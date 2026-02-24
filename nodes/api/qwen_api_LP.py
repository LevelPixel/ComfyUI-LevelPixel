import base64
import io
import json
import os
from pathlib import Path

import numpy as np
import requests
import torch
from dotenv import load_dotenv
from PIL import Image

def _get_api_key() -> str:
    env_path = Path(__file__).parent / ".env"
    if env_path.is_file():
        load_dotenv(env_path, override=False)

    key = os.environ.get("DASHSCOPE_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "DASHSCOPE_API_KEY not found. "
            "Set it in a .env file next to this node or as a system environment variable (DASHSCOPE_API_KEY)."
        )
    return key

API_URL = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"

def _tensor_to_base64(image_tensor: torch.Tensor) -> str:
    """Convert a single ComfyUI IMAGE tensor (H, W, C) float32 [0,1] → base64 PNG string."""
    arr = image_tensor.cpu().numpy()
    arr = (np.clip(arr, 0.0, 1.0) * 255.0).astype(np.uint8)
    pil_img = Image.fromarray(arr, mode="RGB")

    buffer = io.BytesIO()
    pil_img.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def _download_image_as_tensor(url: str) -> torch.Tensor:
    """Download an image from *url* and return a ComfyUI IMAGE tensor (H, W, C) float32 [0,1]."""
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()

    pil_img = Image.open(io.BytesIO(resp.content)).convert("RGB")
    arr = np.array(pil_img, dtype=np.float32) / 255.0
    return torch.from_numpy(arr)

class QwenImageEditNode:

    CATEGORY = "LevelPixel/API/Qwen"
    FUNCTION = "execute"
    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("images", "json_response")
    OUTPUT_NODE = False

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image1": ("IMAGE",),
                "positive_prompt": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "placeholder": "Describe the desired edit…",
                }),
            },
            "optional": {
                "image2": ("IMAGE",),
                "image3": ("IMAGE",),
                "negative_prompt": ("STRING", {
                    "multiline": True,
                    "default": "",
                    "placeholder": "What to avoid…",
                }),
                "n": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 6,
                    "step": 1,
                    "display": "number",
                }),
                "width": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 2048,
                    "step": 16,
                    "display": "number",
                    "tooltip": "Output width in px (512-2048). 0 = auto.",
                }),
                "height": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 2048,
                    "step": 16,
                    "display": "number",
                    "tooltip": "Output height in px (512-2048). 0 = auto.",
                }),
                "prompt_extend": ("BOOLEAN", {"default": True}),
                "watermark": ("BOOLEAN", {"default": False}),
                "seed": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 2147483647,
                    "step": 1,
                    "display": "number",
                    "tooltip": "Random seed. 0 = do not send (server picks).",
                }),
            },
        }
    def execute(
        self,
        image1: torch.Tensor,
        positive_prompt: str,
        image2: torch.Tensor | None = None,
        image3: torch.Tensor | None = None,
        negative_prompt: str = "",
        n: int = 1,
        width: int = 0,
        height: int = 0,
        prompt_extend: bool = True,
        watermark: bool = False,
        seed: int = 0,
    ):
        api_key = _get_api_key()

        content: list[dict] = []

        content.append({"image": _tensor_to_base64(image1[0])})

        if image2 is not None:
            content.append({"image": _tensor_to_base64(image2[0])})
        if image3 is not None:
            content.append({"image": _tensor_to_base64(image3[0])})

        content.append({"text": positive_prompt})

        parameters: dict = {
            "n": n,
            "prompt_extend": prompt_extend,
            "watermark": watermark,
        }

        if negative_prompt.strip():
            parameters["negative_prompt"] = negative_prompt.strip()

        if width > 0 and height > 0:
            parameters["size"] = f"{width}*{height}"

        if seed > 0:
            parameters["seed"] = seed

        body = {
            "model": "qwen-image-edit-max",
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": content,
                    }
                ]
            },
            "parameters": parameters,
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        print("[QwenImageEdit] Sending request to DashScope API…")
        response = requests.post(API_URL, headers=headers, json=body, timeout=300)

        response_json = response.json()
        json_str = json.dumps(response_json, indent=2, ensure_ascii=False)

        if response.status_code != 200:
            error_msg = response_json.get("message", response.text)
            error_code = response_json.get("code", response.status_code)
            raise RuntimeError(
                f"[QwenImageEdit] API error {error_code}: {error_msg}\n"
                f"Full response:\n{json_str}"
            )

        try:
            choices = response_json["output"]["choices"]
            image_urls: list[str] = []
            for choice in choices:
                for item in choice["message"]["content"]:
                    if "image" in item:
                        image_urls.append(item["image"])
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(
                f"[QwenImageEdit] Unexpected API response structure: {exc}\n"
                f"Full response:\n{json_str}"
            ) from exc

        if not image_urls:
            raise RuntimeError(
                f"[QwenImageEdit] No images returned by API.\n"
                f"Full response:\n{json_str}"
            )

        print(f"[QwenImageEdit] Downloading {len(image_urls)} image(s)…")
        tensors: list[torch.Tensor] = []
        for url in image_urls:
            tensors.append(_download_image_as_tensor(url))

        images_batch = torch.stack(tensors, dim=0)

        print("[QwenImageEdit] Done.")
        return (images_batch, json_str)


NODE_CLASS_MAPPINGS = {
    "QwenImageEdit|LP": QwenImageEditNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenImageEdit|LP": "Qwen Image Edit (API) [LP]",
}