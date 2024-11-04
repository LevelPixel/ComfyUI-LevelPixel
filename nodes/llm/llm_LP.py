import folder_paths
import os
from llama_cpp import Llama
import gc
import torch


supported_LLava_extensions = set(['.gguf'])

try:
    folder_paths.folder_names_and_paths["LLavacheckpoints"] = (folder_paths.folder_names_and_paths["LLavacheckpoints"][0], supported_LLava_extensions)
except:
    if not os.path.isdir(os.path.join(folder_paths.models_dir, "LLavacheckpoints")):
        os.mkdir(os.path.join(folder_paths.models_dir, "LLavacheckpoints"))
        
    folder_paths.folder_names_and_paths["LLavacheckpoints"] = ([os.path.join(folder_paths.models_dir, "LLavacheckpoints")], supported_LLava_extensions)
    
class LLMLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": { 
                "ckpt_name": (folder_paths.get_filename_list("LLavacheckpoints"), ),   
                "max_ctx": ("INT", {"default": 2048, "min": 128, "max": 128000, "step": 64}),
                "gpu_layers": ("INT", {"default": 27, "min": 0, "max": 100, "step": 1}),
                "n_threads": ("INT", {"default": 8, "min": 1, "max": 100, "step": 1}),
            }
        }
                
    
    RETURN_TYPES = ("CUSTOM",)
    RETURN_NAMES = ("model",)
    FUNCTION = "load_llm_checkpoint"

    CATEGORY = "LevelPixel/LLM"
    def load_llm_checkpoint(self, ckpt_name, max_ctx, gpu_layers, n_threads):
        ckpt_path = folder_paths.get_full_path("LLavacheckpoints", ckpt_name)
        llm = Llama(model_path = ckpt_path, chat_format="chatml", offload_kqv=True, 
                    f16_kv=True, use_mlock=False, embedding=False, n_batch=1024, 
                    last_n_tokens_size=1024, verbose=True, seed=42, n_ctx = max_ctx, 
                    n_gpu_layers=gpu_layers, n_threads=n_threads,) 
        return (llm, ) 
    
class LLMSampler:        
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("CUSTOM", {"default": ""}),
                "max_tokens": ("INT", {"default": 512, "min": 1, "max": 2048, "step": 1}),
                "temperature": ("FLOAT", {"default": 0.2, "min": 0.01, "max": 1.0, "step": 0.01}),
                "top_p": ("FLOAT", {"default": 0.95, "min": 0.1, "max": 1.0, "step": 0.01}),
                "top_k": ("INT", {"default": 40, "step": 1}), 
                "frequency_penalty": ("FLOAT", {"default": 0.0, "step": 0.01}),
                "presence_penalty": ("FLOAT", {"default": 0.0, "step": 0.01}),
                "repeat_penalty": ("FLOAT", {"default": 1.1, "step": 0.01}),
		        "seed": ("INT", {"default": 42, "step": 1}),
                "prompt": ("STRING",{"multiline": True, "default": ""}),
                "system_msg": ("STRING",{ "multiline": True, "default" : "You are an assistant who perfectly describes images."}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_text_sampler"
    CATEGORY = "LevelPixel/LLM"

    def generate_text_sampler(self, system_msg, prompt, model, max_tokens, 
                              temperature, top_p, top_k, frequency_penalty, 
                              presence_penalty, repeat_penalty, seed):
        llm = model
        response = llm.create_chat_completion(messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": prompt + " Assistant:"},
        ],
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            repeat_penalty=repeat_penalty,
	    seed=seed
            
        )
        return (f"{response['choices'][0]['message']['content']}", )


class LLMAdvanced:
    def __init__(self):
        self.llm = None

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "ckpt_name": (folder_paths.get_filename_list("LLavacheckpoints"), ),
                "max_ctx": ("INT", {"default": 2048, "min": 300, "max": 100000, "step": 64}),
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
                "prompt": ("STRING", {"multiline": True, "default": ""}),
                "system_msg": ("STRING", {"multiline": True, "default": "You are an assistant who perfectly describes images."}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate_text_advanced"
    CATEGORY = "LevelPixel/LLM"

    def generate_text_advanced(self, ckpt_name, max_ctx, gpu_layers, n_threads, 
                               system_msg, prompt, max_tokens, temperature, top_p, 
                               top_k, frequency_penalty, presence_penalty, repeat_penalty, seed, unload):

        ckpt_path = folder_paths.get_full_path("LLavacheckpoints", ckpt_name)
        self.llm = Llama(model_path = ckpt_path, offload_kqv=True, f16_kv=True, 
                         use_mlock=False, embedding=False, n_batch=1024, last_n_tokens_size=1024, 
                         verbose=True, seed=42, n_ctx = max_ctx, n_gpu_layers=gpu_layers, 
                         n_threads=n_threads, logits_all=True, echo=False)

        response = self.llm.create_chat_completion(messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt},
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

        return (f"{response['choices'][0]['message']['content']}", )

NODE_CLASS_MAPPINGS = {
    "LLMLoader|LP": LLMLoader,
    "LLMSampler|LP": LLMSampler,
    "LLMAdvanced|LP": LLMAdvanced,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LLMLoader|LP": "LLM Loader [LP]",
    "LLMSampler|LP": "LLM Sampler [LP]",
    "LLMAdvanced|LP": "LLM Advanced [LP]"
}
