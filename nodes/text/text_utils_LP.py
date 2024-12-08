import re
import random
import time
from deep_translator import GoogleTranslator
from langdetect import detect

class TextChoiceParser:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "dynamicPrompts": False}),
            },
            "optional": {
                "variables": ("STRING", {"multiline": True, "dynamicPrompts": False}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "text_choice_parser"
    OUTPUT_NODE = True
    CATEGORY = "LevelPixel/Text"
    
    def text_choice_parser(self, text, variables="", seed=None):
        if len(text) > 10000:
            return ("Text too large to process at once",)
        
        if seed is None or seed == 0:
            seed = int(time.time() * 1000)
        random.seed(seed)
        
        var_dict = {}
        for line in variables.split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                var_dict[key.strip()] = value.strip()

        for key, value in var_dict.items():
            text = text.replace(f"[{key}]", value)

        pattern = r'\{([^}]+)\}'
        
        def replace_random(match):
            return random.choice(match.group(1).split('|'))

        result = re.sub(pattern, replace_random, text)
        
        return (result,)

    @classmethod
    def IS_CHANGED(s, text, variables="", seed=None):
        return (text, variables, seed)

class CLIPTextEncodeTranslate:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"text": ("STRING", {"multiline": True, "dynamicPrompts": True}), "clip": ("CLIP", )}}
    RETURN_TYPES = ("CONDITIONING",)
    FUNCTION = "clip_text_encode_translate"
    CATEGORY = "LevelPixel/Text"

    def clip_text_encode_translate(self, clip, text):
        if text.strip():
            detected_lang = detect(text)
            if detected_lang != 'en':
                try:
                    translator = GoogleTranslator(source='auto', target='en')
                    text = translator.translate(text)
                except Exception as e:
                    print(f"Translation error: {e}")
        tokens = clip.tokenize(text)
        cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)
        return ([[cond, {"pooled_output": pooled}]], )

class TextTranslate:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"text": ("STRING", {"default": "text", "multiline": True})}}
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "text_translate"
    CATEGORY = "LevelPixel/Text"

    def text_translate(self, prompt):
        if prompt.strip():
            detected_lang = detect(prompt)
            if detected_lang != 'en':
                try:
                    translator = GoogleTranslator(source='auto', target='en')
                    prompt = translator.translate(prompt)
                except Exception as e:
                    print(f"Translation error: {e}")
        return (prompt,)

NODE_CLASS_MAPPINGS = {
    "TextChoiceParser|LP": TextChoiceParser,
    "CLIPTextEncodeTranslate|LP": CLIPTextEncodeTranslate,
    "TextTranslate|LP": TextTranslate,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextChoiceParser|LP": "Text Choice Parser [LP]",
    "CLIPTextEncodeTranslate|LP": "CLIP Text Encode Translate [LP]",
    "TextTranslate|LP": "Text Translate [LP]",
}