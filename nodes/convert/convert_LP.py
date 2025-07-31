import sys

class AnyType(str):
    def __ne__(self, __value: object) -> bool:
        return False

any = AnyType("*")

class StringToFloat:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "string": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "string_to_float"
    CATEGORY = "LevelPixel/Conversion"

    def string_to_float(self, string):
        return (float(string),)

class StringToInt:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "string": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "string_to_int"
    CATEGORY = "LevelPixel/Conversion"

    def string_to_int(self, string):
        return (int(string),)

class StringToBool:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"multiline": False, "default": ""}),
            },
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("BOOLEAN",)
    FUNCTION = "string_to_bool"
    CATEGORY = "LevelPixel/Conversion"

    def string_to_bool(self, string):

        if string == "True" or string == "true" or string == "yes" or string == "1":
            boolean_out = True
        if string == "False" or string == "false" or string == "no" or string == "0":
            boolean_out = False
        else:
            if string.startswith('-') and string[1:].replace('.','',1).isdigit():
                float_out = -float(string[1:])
                if float_out > 0:
                    boolean_out = True
                if float_out <= 0:
                    boolean_out = False
            else:
                if string.replace('.','',1).isdigit():
                    float_out = float(string)
                    if float_out > 0:
                        boolean_out = True
                    if float_out <= 0:
                        boolean_out = False
                else:
                    pass

        return (boolean_out,)
    
class StringToNumber: 
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"string": ("STRING", {"multiline": False, "default": ""}),
                "round_integer": (["round", "round down","round up"],),
                },
        }

    RETURN_TYPES = ("INT", "FLOAT",)
    RETURN_NAMES = ("INT", "FLOAT",)
    FUNCTION = "string_to_number"
    CATEGORY = "LevelPixel/Conversion"

    def string_to_number(self, string, round_integer):
        if string.startswith('-') and string[1:].replace('.','',1).isdigit():
            float_out = -float(string[1:])
        else:
            if string.replace('.','',1).isdigit():
                float_out = float(string)
            else:
                print(f"[Error] String To Number. Not a number.")
                return {}

        if round_integer == "round up":
            if string.startswith('-'):
                int_out = int(float_out)
            else:
                int_out = int(float_out) + 1
        elif round_integer == "round down": 
            if string.startswith('-'):
                int_out = int(float_out) - 1
            else:
                int_out = int(float_out)
        else:
            int_out = round(float_out)
        
        return (int_out, float_out,)

class StringToCombo:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING", {"multiline": False, "default": ""}),
            },
        }

    RETURN_TYPES = (any,)
    RETURN_NAMES = ("any",)
    FUNCTION = "string_to_combo"
    CATEGORY = "LevelPixel/Conversion"

    def string_to_combo(self, string):
        text_list = list()
        if string != "":
            values = string.split(',')
            text_list = values[0]
            print(text_list)

        return (text_list,)

class IntToString:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"int": ("INT", {"default": 0, "min": -0xffffffffffffffff, "max": 0xffffffffffffffff, }),
                }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = 'int_to_string'
    CATEGORY = "LevelPixel/Conversion"

    def int_to_string(self, int):
        return (f'{int}', )

class FloatToString:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"float": ("FLOAT", {"default": 0.0, "min": -0xffffffffffffffff, "max": 0xffffffffffffffff, }),
                }        
        }

    RETURN_TYPES = ('STRING', )
    RETURN_NAMES = ('STRING', )
    FUNCTION = 'float_to_string'
    CATEGORY = "LevelPixel/Conversion"

    def float_to_string(self, float):
        return (f'{float}', )
    
class BoolToString:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"bool": ("BOOLEAN", {"default": False,}),
                }        
        }

    RETURN_TYPES = ('STRING', )
    RETURN_NAMES = ('STRING', )
    FUNCTION = 'bool_to_string'
    CATEGORY = "LevelPixel/Conversion"

    def bool_to_string(self, bool):
        return (f'{bool}', )

class FloatToInt:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"float": ("FLOAT", {"default": 0.0, "min": -0xffffffffffffffff, "max": 0xffffffffffffffff, }),
                "round_integer": (["round", "round down","round up"],),
                }
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("INT",)
    FUNCTION = "float_to_int"
    CATEGORY = "LevelPixel/Conversion"

    def float_to_int(self, float, round_integer):
        if round_integer == "round up":
            if float < 0.0:
                int_out = int(float)
            else:
                int_out = int(float) + 1
        elif round_integer == "round down": 
            if float < 0.0:
                int_out = int(float) - 1
            else:
                int_out = int(float)
        else:
            int_out = round(float)
        return (int_out,)
    
class IntToFloat:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"int": ("INT", {"default": 0, "min": -0xffffffffffffffff, "max": 0xffffffffffffffff, }),
                }
        }

    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("FLOAT",)
    FUNCTION = "int_to_float"
    CATEGORY = "LevelPixel/Conversion"

    def int_to_float(self, int):
        return (float(int),)
    
class IntToBool:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "int": ("INT", {"default": 0, "min": -0xffffffffffffffff, "max": 0xffffffffffffffff, }),
            },
        }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("BOOLEAN",)
    FUNCTION = "int_to_bool"
    CATEGORY = "LevelPixel/Conversion"

    def int_to_bool(self, int):
        if int > 0:
            boolean_out = True
        if int < 1:
            boolean_out = False
        else:
            pass

        return (boolean_out,)

class BoolToInt:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "bool": ("BOOLEAN", {"multiline": False, "default": False}),
            },
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("INT",)
    FUNCTION = "bool_to_int"
    CATEGORY = "LevelPixel/Conversion"

    def bool_to_int(self, bool):
        if bool == True:
            int_out = 1
        if bool == False:
            int_out = 0
        else:
            pass

        return (int_out,)

class ComboToText:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "combo_list": ("COMBO",),
                "delimiter": ("STRING", {"default": ", ", "multiline": False}),
                "as_json": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "combo_to_text"
    CATEGORY = "LevelPixel/Conversion"

    def combo_to_text(self, combo_list, delimiter, as_json):
        import json
        if as_json:
            try:
                text = json.dumps(combo_list, ensure_ascii=False, indent=2)
            except Exception as e:
                text = f"Error: {e}"
        else:
            lines = []
            for item in combo_list:
                if isinstance(item, dict):
                    line = delimiter.join(f"{k}: {v}" for k, v in item.items())
                else:
                    line = str(item)
                lines.append(line)
            text = "\n".join(lines)
        return (text,)

class AnyToText:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "any_value": (any, {"defaultInput": True}),
                "as_json": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "any_to_text"
    CATEGORY = "LevelPixel/Conversion"

    def any_to_text(self, any_value, as_json):
        import json
        if as_json:
            try:
                text = json.dumps(any_value, ensure_ascii=False, indent=2)
            except Exception as e:
                text = f"Error: {e}"
        else:
            text = str(any_value)
        return (text,)


NODE_CLASS_MAPPINGS = {
    "StringToInt|LP": StringToInt,
    "StringToFloat|LP": StringToFloat,
    "StringToBool|LP": StringToBool,
    "StringToNumber|LP": StringToNumber,
    "StringToCombo|LP": StringToCombo,
    "IntToString|LP": IntToString,
    "FloatToString|LP": FloatToString,
    "BoolToString|LP": BoolToString,
    "FloatToInt|LP": FloatToInt,
    "IntToFloat|LP": IntToFloat,
    "IntToBool|LP": IntToBool,
    "BoolToInt|LP": BoolToInt,
    "ComboToText|LP": ComboToText,
    "AnyToText|LP": AnyToText,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "StringToInt|LP": "Convert String To Int [LP]",
    "StringToFloat|LP": "Convert String To Float [LP]",
    "StringToBool|LP": "Convert String To Bool [LP]",
    "StringToNumber|LP": "Convert String To Number [LP]",
    "StringToCombo|LP": "Convert String To Combo [LP]",
    "IntToString|LP": "Convert Int To String [LP]",
    "FloatToString|LP": "Convert Float To String [LP]",
    "BoolToString|LP": "Convert Bool To String [LP]",
    "FloatToInt|LP": "Convert Float To Int [LP]",
    "IntToFloat|LP": "Convert Int To Float [LP]",
    "IntToBool|LP": "Convert Int To Bool [LP]",
    "BoolToInt|LP": "Convert Bool To Int [LP]",
    "ComboToText|LP": "Convert Combo To Text [LP]",
    "AnyToText|LP": "Convert Any To Text [LP]",
}