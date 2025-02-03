import os

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

NODE_CLASS_MAPPINGS = {
    "Text|LP": Text,
    "String|LP": String,
    "FindValueFromFile|LP": FindValueFromFile,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Text|LP": "Text [LP]",
    "String|LP": "String [LP]",
    "FindValueFromFile|LP": "Find Value From File [LP]",
}