import numpy as np
import os
import sys
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import folder_paths
import random
import json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(__file__)), "comfy"))
from comfy.cli_args import args
   
class SaveImage:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4
        self.downscale_preview = False
        self.size = 512
        self.downscale_mode = True

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to save."}),
                "filename_prefix": ("STRING", {"default": "ComfyUI", "tooltip": "The prefix for the file to save. This may include formatting information such as %date:yyyy-MM-dd% or %Empty Latent Image.width% to include values from nodes."}),
                "downscale_preview": ("BOOLEAN", {"default": True, "label_on": "On", "label_off": "Off"}),
                "size": ("INT", {"default": 512, "min": 1, "max": 8192, "step": 1}),
                "downscale_mode": ("BOOLEAN", {"default": True, "label_on": "max", "label_off": "min"}),
                "compress_level": ("INT", {"default": 1, "min": 0, "max": 9, "step": 1}),
            },
            "hidden": {
                "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("original IMAGE",)
    FUNCTION = "save_images"

    OUTPUT_NODE = False

    CATEGORY = "LevelPixel/IO"
    DESCRIPTION = "Saves the input images to your ComfyUI output directory."

    def save_images(self, images, filename_prefix="ComfyUI", downscale_preview=False, size=512, downscale_mode=True, compress_level=1, prompt=None, extra_pnginfo=None):
        self.downscale_preview = downscale_preview
        self.size = size
        self.downscale_mode = downscale_mode
        self.compress_level = compress_level
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
        results = list()
        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            if self.downscale_preview == True:
                w, h = img.size
                target = max(w, h) if self.downscale_mode else min(w, h)
                if target > self.size:
                    scale = self.size / target
                    new_size = (round(w * scale), round(h * scale))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.png"
            img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=self.compress_level)
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })
            counter += 1

        return { "ui": { "images": results }, "result": (images,) }

class PreviewImageForConditions(SaveImage):
    def __init__(self):
        self.output_dir = folder_paths.get_temp_directory()
        self.type = "temp"
        self.prefix_append = "_temp_" + ''.join(random.choice("abcdefghijklmnopqrstupvxyz") for x in range(5))
        self.compress_level = 0
        self.downscale_preview = True

    @classmethod
    def INPUT_TYPES(s):
        return {"required":{
                        "images": ("IMAGE", ), 
                        "size": ("INT", {"default": 512, "min": 1, "max": 8192, "step": 1}),
                        "downscale_preview": ("BOOLEAN", {"default": True, "label_on": "On", "label_off": "Off"}),
                        "size": ("INT", {"default": 512, "min": 1, "max": 8192, "step": 1}),
                        "downscale_mode": ("BOOLEAN", {"default": True, "label_on": "max", "label_off": "min"}),
                        "compress_level": ("INT", {"default": 0, "min": 0, "max": 9, "step": 1}),
                    },                    
                "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
                }
        
NODE_CLASS_MAPPINGS = {
    "PreviewImageForConditions|LP": PreviewImageForConditions
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "PreviewImageForConditions|LP": "Preview Image Bridge [LP]"
}

