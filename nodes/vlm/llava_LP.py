import folder_paths
import os
from io import BytesIO
from llama_cpp import Llama
from llama_cpp.llama_chat_format import Llava16ChatHandler
import base64
from torchvision.transforms import ToPILImage
import gc
import torch


supported_LLava_extensions = set(['.gguf'])

try:
    folder_paths.folder_names_and_paths["LLavacheckpoints"] = (folder_paths.folder_names_and_paths["LLavacheckpoints"][0], supported_LLava_extensions)
except:
    if not os.path.isdir(os.path.join(folder_paths.models_dir, "LLavacheckpoints")):
        os.mkdir(os.path.join(folder_paths.models_dir, "LLavacheckpoints"))
        
    folder_paths.folder_names_and_paths["LLavacheckpoints"] = ([os.path.join(folder_paths.models_dir, "LLavacheckpoints")], supported_LLava_extensions)
    
class LLavaLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "ckpt_name": (folder_paths.get_filename_list("LLavacheckpoints"), ),   
                "max_ctx": ("INT", {"default": 4096, "min": 128, "max": 8192, "step": 64}),
                "gpu_layers": ("INT", {"default": 27, "min": 0, "max": 100, "step": 1}),
                "n_threads": ("INT", {"default": 8, "min": 1, "max": 100, "step": 1}),
                "clip": ("CUSTOM", {"default": ""}),
            }
        }
                
    
    RETURN_TYPES = ("CUSTOM",)
    RETURN_NAMES = ("model",)
    FUNCTION = "load_llava_checkpoint"

    CATEGORY = "LevelPixel/VLM"
    def load_llava_checkpoint(self, ckpt_name, max_ctx, gpu_layers, n_threads, clip ):
        ckpt_path = folder_paths.get_full_path("LLavacheckpoints", ckpt_name)
        llm = Llama(model_path = ckpt_path, chat_handler=clip,offload_kqv=True, f16_kv=True, 
                    use_mlock=False, embedding=False, n_batch=1024, last_n_tokens_size=1024, 
                    verbose=True, seed=42, n_ctx = max_ctx, n_gpu_layers=gpu_layers, n_threads=n_threads, 
                    logits_all=True, echo=False) 
        return (llm, ) 
    
class LLavaClipLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {               
                "clip_name": (folder_paths.get_filename_list("LLavacheckpoints"), ), 
            }
        }
    
    RETURN_TYPES = ("CUSTOM", )
    RETURN_NAMES = ("clip", )
    FUNCTION = "load_clip_checkpoint"

    CATEGORY = "LevelPixel/VLM"
    def load_clip_checkpoint(self, clip_name):
        clip_path = folder_paths.get_full_path("LLavacheckpoints", clip_name)
        clip = Llava16ChatHandler(clip_model_path = clip_path, verbose=False)        
        return (clip, ) 

class LLavaSamplerSimple:        
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "model": ("CUSTOM", {"default": ""}),
                "temperature": ("FLOAT", {"default": 0.1, "min": 0.01, "max": 1.0, "step": 0.01}),  
                "prompt": ("STRING",{"multiline": True} ),            
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_text_simple"
    CATEGORY = "LevelPixel/VLM"

    def generate_text_simple(self, image, prompt, model, temperature):

        pil_image = ToPILImage()(image[0].permute(2, 0, 1))

        buffer = BytesIO()
        pil_image.save(buffer, format="PNG")

        image_bytes = buffer.getvalue()

        base64_string = f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('utf-8')}"

        llm = model
        response = llm.create_chat_completion(
            messages = [
                {"role": "system", "content": "You are an assistant who perfectly describes images."},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url" : base64_string}},
                        {"type" : "text", "text": f"{prompt}"}
                    ]
                }
                
            ],
            temperature = temperature,
        )

        return (f"{response['choices'][0]['message']['content']}", )
    
class LLavaSamplerAdvanced:        
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "model": ("CUSTOM", {"default": ""}),
                "max_tokens": ("INT", {"default": 512, "min": 1, "max": 2048, "step": 1}),
                "temperature": ("FLOAT", {"default": 0.1, "min": 0.01, "max": 1.0, "step": 0.01}),
                "top_p": ("FLOAT", {"default": 0.95, "min": 0.1, "max": 1.0, "step": 0.01}),
                "top_k": ("INT", {"default": 40, "step": 1}), 
                "frequency_penalty": ("FLOAT", {"default": 0.0, "step": 0.01}),
                "presence_penalty": ("FLOAT", {"default": 0.0, "step": 0.01}),
                "repeat_penalty": ("FLOAT", {"default": 1.1, "step": 0.01}),
                "seed": ("INT", {"default": 42, "step":1}),
                "prompt": ("STRING",{"multiline": True, "default": ""}),
                "system_msg": ("STRING",{"multiline": True, "default" : "You are an assistant who perfectly describes images."}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_text_advanced"
    CATEGORY = "LevelPixel/VLM"

    def generate_text_advanced(self, image, system_msg, prompt, model, max_tokens, temperature, top_p, 
                               frequency_penalty, presence_penalty, repeat_penalty, top_k,seed):
        

        pil_image = ToPILImage()(image[0].permute(2, 0, 1))

        buffer = BytesIO()
        pil_image.save(buffer, format="PNG")

        image_bytes = buffer.getvalue()

        base64_string = f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('utf-8')}"

        llm = model
        response = llm.create_chat_completion(
            messages = [
                {"role": "system", "content": system_msg},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url" : base64_string}},
                        {"type" : "text", "text": f"{prompt}"}
                    ]
                }

            ],
            max_tokens = max_tokens,
            temperature = temperature,
            top_p = top_p,
            top_k = top_k,
            frequency_penalty = frequency_penalty,
            presence_penalty = presence_penalty,
            repeat_penalty = repeat_penalty,
            seed=seed
        )

        return (f"{response['choices'][0]['message']['content']}", )
    
class LLavaSimple:
    def __init__(self):
        self.llm = None
        self.clip = None

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "ckpt_name": (folder_paths.get_filename_list("LLavacheckpoints"), ),
                "clip_name": (folder_paths.get_filename_list("LLavacheckpoints"), ),
                "max_ctx": ("INT", {"default": 4096, "min": 128, "max": 128000, "step": 64}),
                "gpu_layers": ("INT", {"default": 27, "min": 0, "max": 100, "step": 1}),
                "n_threads": ("INT", {"default": 8, "min": 1, "max": 100, "step": 1}),
                "temperature": ("FLOAT", {"default": 0.1, "min": 0.01, "max": 1.0, "step": 0.01}),
                "unload": ("BOOLEAN", {"default": False}),
                "prompt": ("STRING", {"multiline": True, "forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_text_full_simple"
    CATEGORY = "LevelPixel/VLM"

    def generate_text_full_simple(self, ckpt_name, clip_name, max_ctx, gpu_layers, n_threads, image, prompt, temperature, unload):

        clip_path = folder_paths.get_full_path("LLavacheckpoints", clip_name)
        self.clip = Llava16ChatHandler(clip_model_path=clip_path, verbose=False)

        ckpt_path = folder_paths.get_full_path("LLavacheckpoints", ckpt_name)
        self.llm = Llama(model_path = ckpt_path, chat_handler=self.clip, offload_kqv=True, f16_kv=True, 
                         use_mlock=False, embedding=False, n_batch=1024, last_n_tokens_size=1024, 
                         verbose=True, seed=42, n_ctx = max_ctx, n_gpu_layers=gpu_layers, n_threads=n_threads, 
                         logits_all=True, echo=False)

        pil_image = ToPILImage()(image[0].permute(2, 0, 1))

        buffer = BytesIO()
        pil_image.save(buffer, format="PNG")

        image_bytes = buffer.getvalue()

        base64_string = f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('utf-8')}"

        response = self.llm.create_chat_completion(
            messages=[
                {"role": "system", "content": "You are an assistant who perfectly describes images."},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": base64_string}},
                        {"type": "text", "text": f"{prompt}"}
                    ]
                }
            ],
            temperature=temperature,
        )

        if unload and self.llm is not None:
            self.llm.close()
            del self.llm
            self.llm = None
            gc.collect()
            torch.cuda.empty_cache()
        

        if unload and self.clip is not None:
            self.clip._exit_stack.close() # info https://github.com/abetlen/llama-cpp-python/issues/1746
            del self.clip
            self.clip = None
            gc.collect()
            torch.cuda.empty_cache()
            
        return (f"{response['choices'][0]['message']['content']}", )

class LLavaAdvanced:
    def __init__(self):
        self.llm = None
        self.clip = None

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "ckpt_name": (folder_paths.get_filename_list("LLavacheckpoints"), ),
                "clip_name": (folder_paths.get_filename_list("LLavacheckpoints"), ),
                "max_ctx": ("INT", {"default": 4096, "min": 128, "max": 128000, "step": 64}),
                "gpu_layers": ("INT", {"default": 27, "min": 0, "max": 100, "step": 1}),
                "n_threads": ("INT", {"default": 8, "min": 1, "max": 100, "step": 1}),
                "max_tokens": ("INT", {"default": 512, "min": 1, "max": 2048, "step": 1}),
                "temperature": ("FLOAT", {"default": 0.1, "min": 0.01, "max": 1.0, "step": 0.01}),
                "top_p": ("FLOAT", {"default": 0.95, "min": 0.1, "max": 1.0, "step": 0.01}),
                "top_k": ("INT", {"default": 40, "step": 1}),
                "frequency_penalty": ("FLOAT", {"default": 0.0, "step": 0.01}),
                "presence_penalty": ("FLOAT", {"default": 0.0, "step": 0.01}),
                "repeat_penalty": ("FLOAT", {"default": 1.1, "step": 0.01}),
                "seed": ("INT", {"default": 42, "step": 1}),
                "unload": ("BOOLEAN", {"default": False}),
                "prompt": ("STRING", {"multiline": True,  "default": ""}),
                "system_msg": ("STRING", {"multiline": True, "default": "You are an assistant who perfectly describes images."}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_text_full_advanced"
    CATEGORY = "LevelPixel/VLM"

    def generate_text_full_advanced(self, ckpt_name, clip_name, max_ctx, gpu_layers, n_threads, image, 
                                    system_msg, prompt, max_tokens, temperature, top_p, top_k, frequency_penalty, 
                                    presence_penalty, repeat_penalty, seed, unload):

        clip_path = folder_paths.get_full_path("LLavacheckpoints", clip_name)
        self.clip = Llava16ChatHandler(clip_model_path=clip_path, verbose=False)

        ckpt_path = folder_paths.get_full_path("LLavacheckpoints", ckpt_name)
        self.llm = Llama(model_path = ckpt_path, chat_handler=self.clip, offload_kqv=True, f16_kv=True, 
                         use_mlock=False, embedding=False, n_batch=1024, last_n_tokens_size=1024, 
                         verbose=True, seed=42, n_ctx = max_ctx, n_gpu_layers=gpu_layers, n_threads=n_threads, 
                         logits_all=True, echo=False)

        pil_image = ToPILImage()(image[0].permute(2, 0, 1))

        buffer = BytesIO()
        pil_image.save(buffer, format="PNG")


        image_bytes = buffer.getvalue()

        base64_string = f"data:image/jpeg;base64,{base64.b64encode(image_bytes).decode('utf-8')}"

        response = self.llm.create_chat_completion(
            messages=[
                {"role": "system", "content": system_msg},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": base64_string}},
                        {"type": "text", "text": f"{prompt}"}
                    ]
                }
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            repeat_penalty=repeat_penalty,
            seed=seed,
        )

        if unload and self.llm is not None:
            self.llm.close()
            del self.llm
            self.llm = None
            gc.collect()
            torch.cuda.empty_cache()
        

        if unload and self.clip is not None:
            self.clip._exit_stack.close() # info https://github.com/abetlen/llama-cpp-python/issues/1746
            del self.clip
            self.clip = None
            gc.collect()
            torch.cuda.empty_cache()

        return (f"{response['choices'][0]['message']['content']}", )

NODE_CLASS_MAPPINGS = {
    "LLavaLoader|LP": LLavaLoader,
    "LLavaClipLoader|LP": LLavaClipLoader,
    "LLavaSamplerSimple|LP": LLavaSamplerSimple,
    "LLavaSamplerAdvanced|LP": LLavaSamplerAdvanced,
    "LLavaSimple|LP": LLavaSimple,
    "LLavaAdvanced|LP": LLavaAdvanced,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LLavaLoader|LP": "LLava Loader [LP]",
    "LLavaClipLoader|LP": "LLava Clip Loader [LP]",
    "LLavaSamplerSimple|LP": "LLava Sampler Simple [LP]",
    "LLavaSamplerAdvanced|LP": "LLava Sampler Advanced [LP]",
    "LLavaSimple|LP": "LLava Simple [LP]",
    "LLavaAdvanced|LP": "LLava Advanced [LP]",
}
