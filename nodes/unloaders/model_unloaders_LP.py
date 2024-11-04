from comfy import model_management
import gc
import torch

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

class ModelUnloader:
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

    FUNCTION = "unload_model"

    OUTPUT_NODE = True

    CATEGORY = "LevelPixel/Unloaders"

    def unload_model(self, **kwargs):
        loadedmodels=model_management.current_loaded_models
        unloaded_model = False
        for i in range(len(loadedmodels) -1, -1, -1):
            m = loadedmodels.pop(i)
            m.model_unload()
            del m
            unloaded_model = True
        if unloaded_model:
            model_management.soft_empty_cache()
        gc.collect()
        torch.cuda.empty_cache()
        return (kwargs["source"],)
    
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
    def INPUT_TYPES(s):
         return {
            "required": {
                "source": (any, {}),
            },
        }

    RETURN_TYPES = (any,)

    FUNCTION = "hard_unload_model"

    OUTPUT_NODE = True

    CATEGORY = "LevelPixel/Unloaders"

    def hard_unload_model(self, **kwargs):
        loadedmodels=model_management.current_loaded_models
        unloaded_model = False
        for i in range(len(loadedmodels) -1, -1, -1):
            m = loadedmodels.pop(i)
            m.model_unload()
            del m
            unloaded_model = True
        if unloaded_model:
            model_management.soft_empty_cache()
        gc.collect()
        torch.cuda.empty_cache()
        return (kwargs["source"],)

NODE_CLASS_MAPPINGS = {
    "ModelUnloader|LP": ModelUnloader,
    "SoftModelUnloader|LP": SoftModelUnloader,
    "HardModelUnloader|LP": HardModelUnloader,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ModelUnloader|LP": "Model Unloader [LP]",
    "SoftModelUnloader|LP": "Soft Model Unloader [LP]",
    "HardModelUnloader|LP": "Hard Model Unloader [LP]",
}

