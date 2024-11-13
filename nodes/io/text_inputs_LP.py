

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

NODE_CLASS_MAPPINGS = {
    "Text|LP": Text,
    "String|LP": String,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Text|LP": "Text [LP]",
    "String|LP": "String [LP]",
}