import re
import random
import time
import wordninja
import string
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

    def text_translate(self, text):
        if text.strip():
            detected_lang = detect(text)
            if detected_lang != 'en':
                try:
                    translator = GoogleTranslator(source='auto', target='en')
                    text = translator.translate(text)
                except Exception as e:
                    print(f"Translation error: {e}")
        return (text,)

class TextToList:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
            },
            "optional": {
                "delimiter": ("STRING", {"default": " "}),
                "text_1": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "text_2": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "text_3": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "text_4": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "text_5": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "text_6": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "text_7": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "text_8": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "text_9": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
                "text_10": ("STRING", {"multiline": True, "default": "", "forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING", "LIST",)
    RETURN_NAMES = ("concatenated STRING", "text LIST")
    OUTPUT_IS_LIST = (False, True, )
    FUNCTION = "text_to_list"

    CATEGORY = "LevelPixel/Text"

    def text_to_list(self,
                delimiter="",
                text_1=None,
                text_2=None,
                text_3=None,
                text_4=None,
                text_5=None,
                text_6=None,
                text_7=None,
                text_8=None,
                text_9=None,
                text_10=None):

        list_str = []

        if text_1 is not None and text_1 != "":
            list_str.append(text_1)
        if text_2 is not None and text_2 != "":
            list_str.append(text_2)
        if text_3 is not None and text_3 != "":
            list_str.append(text_3)
        if text_4 is not None and text_4 != "":
            list_str.append(text_4)
        if text_5 is not None and text_5 != "":
            list_str.append(text_5)
        if text_6 is not None and text_6 != "":
            list_str.append(text_6)
        if text_7 is not None and text_7 != "":
            list_str.append(text_7)
        if text_8 is not None and text_8 != "":
            list_str.append(text_8)
        if text_9 is not None and text_9 != "":
            list_str.append(text_9)
        if text_10 is not None and text_10 != "":
            list_str.append(text_10)

        return delimiter.join(list_str), [list_str]
    
class SplitCompoundText:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "forceInput": True})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text TEXT",)

    FUNCTION = "split_compound_text"

    CATEGORY = "LevelPixel/Text"

    def split_compound_text(self, text):
        has_trailing_comma = text.rstrip().endswith(',')
        
        tokens = text.split(',')
        result_tokens = []
        
        for token in tokens:
            token = token.strip()
            if token:
                splitted_words = wordninja.split(token)
                result_tokens.append(" ".join(splitted_words))
        
        result = ", ".join(result_tokens)
        if has_trailing_comma:
            result += ","
        
        return (result,)

def is_english_core(core: str) -> bool:
    for ch in core:
        if ch.isalpha() and ch not in string.ascii_letters:
            return False
    return True

def process_token(token: str) -> str:
    core = token.strip(string.punctuation)
    if core == "":
        return token
    if is_english_core(core):
        return token
    else:
        return ""

class KeepOnlyEnglishWords:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "forceInput": True})
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text TEXT",)

    FUNCTION = "keep_only_english_words"

    CATEGORY = "LevelPixel/Text"
    
    def keep_only_english_words(self, text):
        tokens = text.split()
        processed_tokens = []
        for token in tokens:
            filtered = process_token(token)
            if filtered:
                processed_tokens.append(filtered)
        result = " ".join(processed_tokens)

        result = re.sub(r'\s+([,.?!:;])', r'\1', result)

        text = text.rstrip()
        if text and text[-1] in ".!?" and (not result or result[-1] not in ".!?"):
            result += text[-1]

        return (result,)

NODE_CLASS_MAPPINGS = {
    "TextChoiceParser|LP": TextChoiceParser,
    "CLIPTextEncodeTranslate|LP": CLIPTextEncodeTranslate,
    "TextTranslate|LP": TextTranslate,
    "TextToList|LP": TextToList,
    "SplitCompoundText|LP": SplitCompoundText,
    "KeepOnlyEnglishWords|LP": KeepOnlyEnglishWords,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextChoiceParser|LP": "Text Choice Parser [LP]",
    "CLIPTextEncodeTranslate|LP": "CLIP Text Encode Translate [LP]",
    "TextTranslate|LP": "Text Translate [LP]",
    "TextToList|LP": "Text To List [LP]",
    "SplitCompoundText|LP": "Split Compound Text [LP]",
    "KeepOnlyEnglishWords|LP": "Keep Only English Words [LP]",
}