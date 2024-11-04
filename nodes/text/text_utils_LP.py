import re
import random
import time

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

NODE_CLASS_MAPPINGS = {
    "TextChoiceParser|LP": TextChoiceParser,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextChoiceParser|LP": "Text Choice Parser [LP]",
}

