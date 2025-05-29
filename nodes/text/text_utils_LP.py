import re
import random
import time
import wordninja
import string
from deep_translator import GoogleTranslator, MyMemoryTranslator
from langdetect import detect

translators = ['GoogleTranslator', 'MyMemoryTranslator']

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

def split_text(text, limit=499):
    if len(text) <= limit:
        return [text]

    parts = []

    if '\n' in text:
        for line in text.split('\n'):
            if not line:
                parts.append('')
            elif len(line) <= limit:
                parts.append(line)
            else:
                parts.extend(split_text(line, limit))
        return parts

    sentences = re.findall(r'.*?[\.!?]|.+$', text)

    chunk = ''
    for s in (s.strip() for s in sentences if s.strip()):
        if not chunk:
            chunk = s
        elif len(chunk) + 1 + len(s) <= limit:
            chunk += ' ' + s
        else:
            parts.append(chunk)
            chunk = s
    if chunk:
        parts.append(chunk)

    return parts

def join_text(parts):
    return '\n\n'.join(parts)

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
        return {"required": {"text": ("STRING", {"default": "text", "multiline": True}),
                            "translator": (translators, {"default":"GoogleTranslator"})
                         }
                }
        
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("english TEXT",)
    FUNCTION = "text_translate"
    CATEGORY = "LevelPixel/Text"

    def text_translate(self, text, translator='GoogleTranslator'):
        if text.strip():
            detected_lang = detect(text)
            if detected_lang != 'en':
                try:
                    if translator == 'MyMemoryTranslator':
                        sentences = split_text(text, 499)
                        translator = MyMemoryTranslator(source='auto', target='en-US')                        
                        texts = translator.translate_batch(sentences)
                        text = join_text(texts)
                    else:
                        sentences = split_text(text, 4999)
                        translator = GoogleTranslator(source='auto', target='en')
                        texts = translator.translate_batch(sentences)
                        text = join_text(texts)
                except Exception as e:
                    print(f"Translation error: {e}")
        return (text,)
    
class TextTranslateManualAll:
    @classmethod
    def INPUT_TYPES(s):
        source_language_codes = [
            'auto', 'af', 'am', 'ar', 'az', 'be', 'bg', 'bn', 'bs', 'ca', 'ceb', 'co', 
            'cs', 'cy', 'da', 'de', 'el', 'en', 'eo', 'es', 'et', 'eu', 'fa', 'fi', 
            'fr', 'fy', 'ga', 'gd', 'gl', 'gu', 'ha', 'haw', 'he', 'hi', 'hmn', 'hr', 
            'ht', 'hu', 'hy', 'id', 'ig', 'is', 'it', 'ja', 'jv', 'ka', 'kk', 'km', 
            'kn', 'ko', 'ku', 'ky', 'la', 'lb', 'lo', 'lt', 'lv', 'mg', 'mi', 'mk', 
            'ml', 'mn', 'mr', 'ms', 'mt', 'my', 'ne', 'nl', 'no', 'ny', 'pa', 'pl', 
            'ps', 'pt', 'ro', 'ru', 'rw', 'sd', 'si', 'sk', 'sl', 'sm', 'sn', 'so', 
            'sq', 'sr', 'st', 'su', 'sv', 'sw', 'ta', 'te', 'tg', 'th', 'tk', 'tl', 'tr', 
            'tt', 'ug', 'uk', 'ur', 'uz', 'vi', 'xh', 'yi', 'yo', 'zh-CN', 'zh-TW', 'zu'
        ]
        target_language_codes = [code for code in source_language_codes if code != 'auto']
        return {
            "required": {"text": ("STRING", {"default": "text", "multiline": True}),
                         "source_lang": (source_language_codes, {"default":"auto"}),
                         "target_lang": (target_language_codes, {"default":"en"}),
                         "translator": (translators, {"default":"GoogleTranslator"})
                         }
                }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "text_translate_manual_all"
    CATEGORY = "LevelPixel/Text"

    def text_translate_manual_all(self, text, source_lang='auto', target_lang='en', translator='GoogleTranslator'):
        if text.strip():
            try:
                if translator == 'MyMemoryTranslator':
                    sentences = split_text(text, 499)
                    translator = MyMemoryTranslator(source=source_lang, target=target_lang)                    
                    texts = translator.translate_batch(sentences)
                    text = join_text(texts)
                else:
                    sentences = split_text(text, 4999)
                    translator = GoogleTranslator(source=source_lang, target=target_lang)
                    texts = translator.translate_batch(sentences)
                    text = join_text(texts)
            except Exception as e:
                print(f"Translation error: {e}")
        return (text,)
    
class TextTranslateManual:
    @classmethod
    def INPUT_TYPES(s):
        source_language_codes = [
            'auto',
            'English',
            'Русский',
            'Deutsch',
            'Français',
            'Italiano',
            'Polski',
            'Українська',
            'Nederlands',
            'Español',
            '简体中文',
            '繁體中文',
            '日本語',
            'हिन्दी',
            'العربية',
            'Português',
            'বাংলা'
        ]
        target_language_codes = [code for code in source_language_codes if code != 'auto']
        return {
            "required": {"text": ("STRING", {"default": "text", "multiline": True}),
                         "source_lang": (source_language_codes, {"default":"auto"}),
                         "target_lang": (target_language_codes, {"default":"English"}),
                         "translator": (translators, {"default":"GoogleTranslator"})
                         }
                }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "text_translate_manual"
    CATEGORY = "LevelPixel/Text"

    def text_translate_manual(self, text, source_lang='auto', target_lang='English', translator='GoogleTranslator'):
        google_language_name_to_code = {
            'auto': 'auto',
            'English': 'en',
            'Русский': 'ru',
            'Deutsch': 'de',
            'Français': 'fr',
            'Italiano': 'it',
            'Polski': 'pl',
            'Українська': 'uk',
            'Nederlands': 'nl',
            'Español': 'es',
            '简体中文': 'zh-CN',
            '繁體中文': 'zh-TW',
            '日本語': 'ja',
            'हिन्दी': 'hi',
            'العربية': 'ar',
            'Português': 'pt',
            'বাংলা': 'bn',
        }

        mymemory_language_name_to_code = {
            'auto': 'auto',
            'English': 'en-US',
            'Русский': 'ru-RU',
            'Deutsch': 'de-DE',
            'Français': 'fr-FR',
            'Italiano': 'it-IT',
            'Polski': 'pl-PL',
            'Українська': 'uk-UA',
            'Nederlands': 'nl-NL',
            'Español': 'es-ES',
            '简体中文': 'zh-CN',
            '繁體中文': 'zh-TW',
            '日本語': 'ja-JP',
            'हिन्दी': 'hi-IN',
            'العربية': 'ar-SA',
            'Português': 'pt-PT',
            'বাংলা': 'bn-IN',
        }

        if text.strip():
            try:
                if translator == 'MyMemoryTranslator':
                    source_lang_code = mymemory_language_name_to_code.get(source_lang)
                    target_lang_code = mymemory_language_name_to_code.get(target_lang)
                    sentences = split_text(text, 499)
                    translator = MyMemoryTranslator(source=source_lang_code, target=target_lang_code)                    
                    texts = translator.translate_batch(sentences)
                    text = join_text(texts)
                else:
                    source_lang_code = google_language_name_to_code.get(source_lang)
                    target_lang_code = google_language_name_to_code.get(target_lang)
                    sentences = split_text(text, 4999)
                    translator = GoogleTranslator(source=source_lang_code, target=target_lang_code)
                    texts = translator.translate_batch(sentences)
                    text = join_text(texts)
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

class TextReplace:

    @ classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "forceInput": True}),            
                },
            "optional": {
                "find1": ("STRING", {"multiline": False, "default": ""}),
                "replace1": ("STRING", {"multiline": False, "default": ""}),
                "find2": ("STRING", {"multiline": False, "default": ""}),
                "replace2": ("STRING", {"multiline": False, "default": ""}),
                "find3": ("STRING", {"multiline": False, "default": ""}),
                "replace3": ("STRING", {"multiline": False, "default": ""}),
                "find4": ("STRING", {"multiline": False, "default": ""}),
                "replace4": ("STRING", {"multiline": False, "default": ""}),
                "find5": ("STRING", {"multiline": False, "default": ""}),
                "replace5": ("STRING", {"multiline": False, "default": ""}),
                "find6": ("STRING", {"multiline": False, "default": ""}),
                "replace6": ("STRING", {"multiline": False, "default": ""}),
                "find7": ("STRING", {"multiline": False, "default": ""}),
                "replace7": ("STRING", {"multiline": False, "default": ""}),
                "find8": ("STRING", {"multiline": False, "default": ""}),
                "replace8": ("STRING", {"multiline": False, "default": ""}),
                "find9": ("STRING", {"multiline": False, "default": ""}),
                "replace9": ("STRING", {"multiline": False, "default": ""}),
            },
        }

    RETURN_TYPES = (any, )
    RETURN_NAMES = ("text TEXT", )
    FUNCTION = "replace_text"
    CATEGORY = "LevelPixel/Text"

    def replace_text(self, text, find1="", replace1="", find2="", replace2="", find3="", replace3="", find4="", replace4="", find5="", replace5="", find6="", replace6="", find7="", replace7="", find8="", replace8="", find9="", replace9=""):
           
        text = text.replace(find1, replace1)
        text = text.replace(find2, replace2)
        text = text.replace(find3, replace3)
        text = text.replace(find4, replace4)
        text = text.replace(find5, replace5)
        text = text.replace(find6, replace6)
        text = text.replace(find7, replace7)
        text = text.replace(find8, replace8)
        text = text.replace(find9, replace9)
        
        return (text,)   

NODE_CLASS_MAPPINGS = {
    "TextChoiceParser|LP": TextChoiceParser,
    "CLIPTextEncodeTranslate|LP": CLIPTextEncodeTranslate,
    "TextTranslate|LP": TextTranslate,
    "TextTranslateManualAll|LP": TextTranslateManualAll,
    "TextTranslateManual|LP": TextTranslateManual,
    "TextToList|LP": TextToList,
    "SplitCompoundText|LP": SplitCompoundText,
    "KeepOnlyEnglishWords|LP": KeepOnlyEnglishWords,
    "TextReplace|LP": TextReplace,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "TextChoiceParser|LP": "Text Choice Parser [LP]",
    "CLIPTextEncodeTranslate|LP": "CLIP Text Encode Translate [LP]",
    "TextTranslate|LP": "Text Translate [LP]",
    "TextTranslateManualAll|LP": "Text Translate Manual (All langs) [LP]",
    "TextTranslateManual|LP": "Text Translate Manual [LP]",
    "TextToList|LP": "Text To List [LP]",
    "SplitCompoundText|LP": "Split Compound Text [LP]",
    "KeepOnlyEnglishWords|LP": "Keep Only English Words [LP]",
    "TextReplace|LP": "Text Replace [LP]",
}