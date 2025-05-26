import os

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

class Text:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "TEXT": ("STRING", {"default": "", "multiline": True, "placeholder": "Text"}),}
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("TEXT",)
    FUNCTION = "text"

    CATEGORY = "LevelPixel/IO"

    @staticmethod
    def text(TEXT):
        return TEXT,

class String:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "STRING": ("STRING", {"default": "", "multiline": False, "placeholder": "String"}),}
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "string"

    CATEGORY = "LevelPixel/IO"

    @staticmethod
    def string(STRING):
        return STRING,

class FindValueFromFile:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
   
        return {"required": {
                    "key": ("STRING", {"default": '', "multiline": False}),
                    "input_path": ("STRING", {"default": '', "multiline": False})
            }
        }

    RETURN_TYPES = ("STRING", "BOOLEAN")
    RETURN_NAMES = ("Value STRING", "Value received BOOL")
    
    FUNCTION = "find_value_from_file"
    CATEGORY = "LevelPixel/IO"

    def find_value_from_file(self, key, input_path=None):
        valueString = ""
        boolResult = True
        log = []
        log.append("")
        try:
            with open(os.path.normpath(input_path), 'r', encoding='utf-8') as file:
                for line in file:
                    line = line.strip()

                    if "-->" in line:
                        keyLine, valueLine = line.split("-->", 1)
                        if keyLine.strip() == key:
                            valueString = valueLine.strip()
                            break
        except FileNotFoundError:
            log[0] = log[0] + f"Error: File not found at {input_path}"
            boolResult = False
        except Exception as e:
            log[0] = log[0] + f"Error: {e}"
            boolResult = False

        if valueString == "":
            boolResult = False
        
        return {"ui": {"text": valueString, "log": log,}, "result": (valueString, boolResult,)}

class StringCycler:
    
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
            "text": ("STRING", {"multiline": True, "default": ""}),
            "repeats": ("INT", {"default": 1, "min": 1, "max": 99999}),
            "loops": ("INT", {"default": 1, "min": 1, "max": 99999}),
            }
        }

    RETURN_TYPES = (any,)
    RETURN_NAMES = ("STRING",)
    OUTPUT_IS_LIST = (True,)
    FUNCTION = "string_cycle"
    CATEGORY = "LevelPixel/IO"  

    def string_cycle(self, text, repeats, loops=1):

        lines = text.split('\n')
        list_out = []

        for i in range(loops):
            for text_item in lines:
                for _ in range(repeats):
                    list_out.append(text_item)
        
        return (list_out, )

NODE_CLASS_MAPPINGS = {
    "Text|LP": Text,
    "String|LP": String,
    "FindValueFromFile|LP": FindValueFromFile,
    "StringCycler|LP": StringCycler,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Text|LP": "Text [LP]",
    "String|LP": "String [LP]",
    "FindValueFromFile|LP": "Find Value From File [LP]",
    "StringCycler|LP": "String Cycler [LP]",
}