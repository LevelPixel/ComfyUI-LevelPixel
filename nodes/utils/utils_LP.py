import time

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

class Delay:    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input": (any, {"defaultInput": True}),
                "delay_seconds": ("FLOAT", {
                    "default": 1.0,
                    "min": 0.0,
                    "step": 0.1
                }),
            },
        }

    RETURN_TYPES = (any,)
    RETURN_NAMES = ("output",)
    FUNCTION = "add_delay"
    CATEGORY = "LevelPixel/Utils"
    
    def add_delay(self, input, delay_seconds):
        delay_text = f"{delay_seconds:.1f} second{'s' if delay_seconds != 1 else ''}"
        print(f"[Delay Node] Starting delay of {delay_text}")
        time.sleep(delay_seconds)
        print(f"[Delay Node] Delay of {delay_text} completed")
        return (input,)

class PipeOut:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"pipe": ("PIPE_LINE",)},
            }

    RETURN_TYPES = ("PIPE_LINE", "MODEL", "CONDITIONING", "CONDITIONING", "LATENT", "VAE", "CLIP", "CONTROL_NET", "IMAGE", "INT", any, any, any, any, any,)
    RETURN_NAMES = ("pipe", "model", "pos", "neg", "latent", "vae", "clip", "controlnet", "image", "seed", "any1", "any2", "any3", "any4", "any5",)
    FUNCTION = "pipe_out"
    CATEGORY = "LevelPixel/Utils"
    
    def pipe_out(self, pipe):
        model, pos, neg, latent, vae, clip, controlnet, image, seed, any1, any2, any3, any4, any5 = pipe        
        return (pipe, model, pos, neg, latent, vae, clip, controlnet, image, seed, any1, any2, any3, any4, any5, )

class PipeIn:    
    @classmethod
    def INPUT_TYPES(s):
        return {
                "optional": {
                    "pipe": ("PIPE_LINE",),
                    "model": ("MODEL",),
                    "pos": ("CONDITIONING",),
                    "neg": ("CONDITIONING",),
                    "latent": ("LATENT",),
                    "vae": ("VAE",),
                    "clip": ("CLIP",),
                    "controlnet": ("CONTROL_NET",),
                    "image": ("IMAGE",),
                    "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                    "any1": (any, {"defaultInput": True}),
                    "any2": (any, {"defaultInput": True}),
                    "any3": (any, {"defaultInput": True}),
                    "any4": (any, {"defaultInput": True}),
                    "any5": (any, {"defaultInput": True}),
                },
            }

    RETURN_TYPES = ("PIPE_LINE",)
    RETURN_NAMES = ("pipe",)
    FUNCTION = "pipe_in"
    CATEGORY = "LevelPixel/Utils"

    def pipe_in(self, pipe=None, model=None, pos=None, neg=None, latent=None, vae=None, clip=None, controlnet=None, image=None, seed=None, any1=None, any2=None, any3=None, any4=None, any5=None,):
        
        new_model = None 
        new_pos = None 
        new_neg = None 
        new_latent = None 
        new_vae = None 
        new_clip = None 
        new_controlnet = None 
        new_image = None 
        new_seed = None 
        new_any1 = None 
        new_any2 = None 
        new_any3 = None 
        new_any4 = None 
        new_any5 = None 

        if pipe is not None:
            new_model, new_pos, new_neg, new_latent, new_vae, new_clip, new_controlnet, new_image, new_seed, new_any1, new_any2, new_any3, new_any4, new_any5 = pipe

        if model is not None:
            new_model = model
        
        if pos is not None:
            new_pos = pos

        if neg is not None:
            new_neg = neg

        if latent is not None:
            new_latent = latent

        if vae is not None:
            new_vae = vae

        if clip is not None:
            new_clip = clip
            
        if controlnet is not None:
            new_controlnet = controlnet
            
        if image is not None:
            new_image = image
            
        if seed is not None:
            new_seed = seed

        if any1 is not None:
            new_any1 = any1

        if any2 is not None:
            new_any2 = any2

        if any3 is not None:
            new_any3 = any3

        if any4 is not None:
            new_any4 = any4

        if any5 is not None:
            new_any5 = any5
       
        pipe = new_model, new_pos, new_neg, new_latent, new_vae, new_clip, new_controlnet, new_image, new_seed, new_any1, new_any2, new_any3, new_any4, new_any5
       
        return (pipe, )
    
class Pipe:    
    @classmethod
    def INPUT_TYPES(s):
        return {
                "optional": {
                    "pipe": ("PIPE_LINE",),
                    "model": ("MODEL",),
                    "pos": ("CONDITIONING",),
                    "neg": ("CONDITIONING",),
                    "latent": ("LATENT",),
                    "vae": ("VAE",),
                    "clip": ("CLIP",),
                    "controlnet": ("CONTROL_NET",),
                    "image": ("IMAGE",),
                    "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                    "any1": (any, {"defaultInput": True}),
                    "any2": (any, {"defaultInput": True}),
                    "any3": (any, {"defaultInput": True}),
                    "any4": (any, {"defaultInput": True}),
                    "any5": (any, {"defaultInput": True}),
                },
            }

    RETURN_TYPES = ("PIPE_LINE", "MODEL", "CONDITIONING", "CONDITIONING", "LATENT", "VAE", "CLIP", "CONTROL_NET", "IMAGE", "INT", any, any, any, any, any,)
    RETURN_NAMES = ("pipe", "model", "pos", "neg", "latent", "vae", "clip", "controlnet", "image", "seed", "any1", "any2", "any3", "any4", "any5",)
    FUNCTION = "pipe"
    CATEGORY = "LevelPixel/Utils"

    def pipe(self, pipe=None, model=None, pos=None, neg=None, latent=None, vae=None, clip=None, controlnet=None, image=None, seed=None, any1=None, any2=None, any3=None, any4=None, any5=None,):
        
        new_model = None 
        new_pos = None 
        new_neg = None 
        new_latent = None 
        new_vae = None 
        new_clip = None 
        new_controlnet = None 
        new_image = None 
        new_seed = None 
        new_any1 = None 
        new_any2 = None 
        new_any3 = None 
        new_any4 = None 
        new_any5 = None 

        if pipe is not None:
            new_model, new_pos, new_neg, new_latent, new_vae, new_clip, new_controlnet, new_image, new_seed, new_any1, new_any2, new_any3, new_any4, new_any5 = pipe

        if model is not None:
            new_model = model
        
        if pos is not None:
            new_pos = pos

        if neg is not None:
            new_neg = neg

        if latent is not None:
            new_latent = latent

        if vae is not None:
            new_vae = vae

        if clip is not None:
            new_clip = clip
            
        if controlnet is not None:
            new_controlnet = controlnet
            
        if image is not None:
            new_image = image
            
        if seed is not None:
            new_seed = seed

        if any1 is not None:
            new_any1 = any1

        if any2 is not None:
            new_any2 = any2

        if any3 is not None:
            new_any3 = any3

        if any4 is not None:
            new_any4 = any4

        if any5 is not None:
            new_any5 = any5
       
        pipe = new_model, new_pos, new_neg, new_latent, new_vae, new_clip, new_controlnet, new_image, new_seed, new_any1, new_any2, new_any3, new_any4, new_any5
       
        return (pipe, new_model, new_pos, new_neg, new_latent, new_vae, new_clip, new_controlnet, new_image, new_seed, new_any1, new_any2, new_any3, new_any4, new_any5,)

NODE_CLASS_MAPPINGS = {
    "Delay|LP": Delay,
    "PipeOut|LP": PipeOut,
    "PipeIn|LP": PipeIn,
    "Pipe|LP": Pipe,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Delay|LP": "Delay [LP]",
    "PipeOut|LP": "Pipe Out [LP]",
    "PipeIn|LP": "Pipe In [LP]",
    "Pipe|LP": "Pipe [LP]",
}

