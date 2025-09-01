from comfy import model_management
import gc
import torch
import requests
from comfy.cli_args import args as comfy_args

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

class ModelUnloader:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"source": (any, )},
            "optional": {"model for unload": (any, )},
        }
    
    @classmethod
    def VALIDATE_INPUTS(s, **kwargs):
        return True
    
    RETURN_TYPES = (any, )
    FUNCTION = "unload_model"
    CATEGORY = "LevelPixel/Unloaders"
    OUTPUT_NODE = True
    
    def unload_model(self, **kwargs):
        loaded_models = model_management.loaded_models()
        if kwargs.get("source") in loaded_models:
            loaded_models.remove(kwargs.get("model for unload"))
        else:
            model = kwargs.get("model for unload")
            if type(model) == dict:
                keys = [(key, type(value).__name__) for key, value in model.items()]
                for key, model_type in keys:
                    if key == 'model':
                        print(f"Unloading model of type {model_type}")
                        del model[key]
        model_management.free_memory(1e30, model_management.get_torch_device(), loaded_models)
        model_management.soft_empty_cache(True)
        try:
            gc.collect()
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        except:
            print("Unable to clear cache")
        return (kwargs.get("source"),)
    
class SoftModelUnloader:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
         return {
            "required": {
                "source": (any, {}),
            },
        }

    RETURN_TYPES = (any,)
    FUNCTION = "soft_unload_model"
    OUTPUT_NODE = True
    CATEGORY = "LevelPixel/Unloaders"

    def soft_unload_model(self, **kwargs):
        model_management.soft_empty_cache()
        gc.collect()
        torch.cuda.empty_cache()
        return (kwargs["source"],)

class HardModelUnloader:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"source": (any, )},
        }
    
    @classmethod
    def VALIDATE_INPUTS(s, **kwargs):
        return True
    
    RETURN_TYPES = (any, )
    FUNCTION = "hard_unload_model"
    CATEGORY = "LevelPixel/Unloaders"
    OUTPUT_NODE = True
    
    def hard_unload_model(self, **kwargs):
        print("Unload Models")
        loadedmodels = model_management.current_loaded_models
        for i in range(len(loadedmodels) -1, -1, -1):
            m = loadedmodels.pop(i)
            m.model_unload()
            del m
        
        try:
            gc.collect()
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        except:
            print("Unable to clear cache")

        model_management.unload_all_models()
        model_management.soft_empty_cache(True)

        try:
            gc.collect()
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        except:
            print("Unable to clear cache")
        return (kwargs.get("source"),)

def _server_base_url():
    tls = bool(getattr(comfy_args, "tls_keyfile", None) and getattr(comfy_args, "tls_certfile", None))
    scheme = "https" if tls else "http"

    port = getattr(comfy_args, "port", 8188)
    listen = str(getattr(comfy_args, "listen", "127.0.0.1") or "127.0.0.1")

    hosts = [h.strip() for h in listen.split(",") if h.strip()]
    def is_wildcard(h): return h in ("0.0.0.0", "::")
    host = next((h for h in hosts if not is_wildcard(h)), None) or "127.0.0.1"

    if ":" in host and not host.startswith("["):
        host = f"[{host}]"

    return f"{scheme}://{host}:{port}"

class SoftFullCleanRAMAndVRAM:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "source": (any, {}),
                "free_execution_cache": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = (any,)
    FUNCTION = "soft_free_models"
    CATEGORY = "LevelPixel/Unloaders"
    OUTPUT_NODE = True

    def soft_free_models(self, free_execution_cache, **kwargs):

        url = f"{_server_base_url()}/free"
        if free_execution_cache:
            payload = {"unload_models": True, "free_memory": True}
        else:
            payload = {"unload_models": True}

        res = requests.post(url, json=payload)
        if res.status_code == 200:
            print("Models unloaded (and execution cache cleared)" if free_execution_cache else " Models unloaded")
        else:
            print("Failed to unload models. Maybe outdated ComfyUI version.")
        return (kwargs["source"],)

NODE_CLASS_MAPPINGS = {
    "ModelUnloader|LP": ModelUnloader,
    "SoftModelUnloader|LP": SoftModelUnloader,
    "HardModelUnloader|LP": HardModelUnloader,
    "SoftFullCleanRAMAndVRAM|LP": SoftFullCleanRAMAndVRAM,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ModelUnloader|LP": "Unload Model [LP]",
    "SoftModelUnloader|LP": "Soft Unload Models Data [LP]",
    "HardModelUnloader|LP": "Hard Unload All Models [LP]",
    "SoftFullCleanRAMAndVRAM|LP": "Soft Full Clean RAM and VRAM [LP]",
}

