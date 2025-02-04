import types
import torch
import comfy.model_management

class OverrideDevice:
    @classmethod
    def INPUT_TYPES(s):
        devices = ["cpu",]
        for k in range(0, torch.cuda.device_count()):
            devices.append(f"cuda:{k}")

        return {
            "required": {
                "device": (devices, {"default":"cpu"}),
            }
        }

    FUNCTION = "patch"
    CATEGORY = "LevelPixel/Unloaders"

    def override(self, model, model_attr, device):
        model.device = device
        patcher = getattr(model, "patcher", model) #.clone()
        for name in ["device", "load_device", "offload_device", "current_device", "output_device"]:
            setattr(patcher, name, device)

        py_model = getattr(model, model_attr)
        py_model.to = types.MethodType(torch.nn.Module.to, py_model)
        py_model.to(device)

        def to(*args, **kwargs):
            pass
        py_model.to = types.MethodType(to, py_model)
        return (model,)

    def patch(self, *args, **kwargs):
        raise NotImplementedError

class OverrideCLIPDevice(OverrideDevice):
    @classmethod
    def INPUT_TYPES(s):
        k = super().INPUT_TYPES()
        k["required"]["clip"] = ("CLIP",)
        return k

    RETURN_TYPES = ("CLIP",)
    CATEGORY = "LevelPixel/Unloaders"

    def patch(self, clip, device):
        return self.override(clip, "cond_stage_model", torch.device(device))

class OverrideVAEDevice(OverrideDevice):
    @classmethod
    def INPUT_TYPES(s):
        k = super().INPUT_TYPES()
        k["required"]["vae"] = ("VAE",)
        return k

    RETURN_TYPES = ("VAE",)
    CATEGORY = "LevelPixel/Unloaders"

    def patch(self, vae, device):
        return self.override(vae, "first_stage_model", torch.device(device))


NODE_CLASS_MAPPINGS = {
    "OverrideCLIPDevice|LP": OverrideCLIPDevice,
    "OverrideVAEDevice|LP": OverrideVAEDevice,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "OverrideCLIPDevice|LP": "Override CLIP Device [LP]",
    "OverrideVAEDevice|LP": "Override VAE Device [LP]",
}
