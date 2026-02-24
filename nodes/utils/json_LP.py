import json
from typing import Tuple

class ParseJSONString:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "json_string": ("STRING", {"multiline": True, "default": "{}"}),
            }
        }
    
    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("json_object",)
    FUNCTION = "parse"
    CATEGORY = "LevelPixel/JSON"
    def parse(self, json_string):
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError:
            print("JSON Parse Error!")
            data = {}
        return (data,)
        
class ModifyJSONObject:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "key": ("STRING", {"default": "new_key"}),
                "value": ("STRING", {"default": "new_value"}),
            },
            "optional": {
                "json_object": ("JSON",), 
            }
        }
    
    RETURN_TYPES = ("JSON", "STRING") 
    RETURN_NAMES = ("json_object", "json_string")
    FUNCTION = "modify"
    CATEGORY = "LevelPixel/JSON"
    def modify(self, key, value, json_object=None):
        if json_object is not None:
            data = json_object.copy()
        else:
            data = {}
        
        if value.isdigit():
            value = int(value)
        elif value.replace('.', '', 1).isdigit() and value.count('.') < 2:
            value = float(value)
            
        data[key] = value
        
        return (data, json.dumps(data, indent=4))
        
class GetJSONValue:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "json_object": ("JSON",),
                "key": ("STRING", {"default": "my_key"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    FUNCTION = "get_value"
    CATEGORY = "LevelPixel/JSON"
    
    def get_value(self, json_object, key):
        normalized_path = key.replace('[', '.').replace(']', '')
        
        parts = [p for p in normalized_path.split('.') if p]
        
        curr = json_object
        
        for part in parts:
            try:
                if isinstance(curr, dict):
                    curr = curr[part]
                elif isinstance(curr, list):
                    idx = int(part)
                    curr = curr[idx]
                else:
                    return ("",)
            except (KeyError, IndexError, ValueError, TypeError):
                return ("",)

        val = "" if curr is None else curr
        return (str(val),)
        
class MergeJSONNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_string_1": ("STRING", {"multiline": True}),
                "json_string_2": ("STRING", {"multiline": True}),
                "merge_strategy": (["override", "preserve", "concat"], {"default": "override"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("json_string",)
    FUNCTION = "merge_json"
    CATEGORY = "LevelPixel/JSON"

    def merge_json(self, json_string_1: str, json_string_2: str, merge_strategy: str) -> tuple[str]:
        try:
            data1 = json.loads(json_string_1)
            data2 = json.loads(json_string_2)
            
            if isinstance(data1, list) and isinstance(data2, list):
                result = data1 + data2
            elif isinstance(data1, dict) and isinstance(data2, dict):
                result = self._merge_dicts(data1, data2, merge_strategy)
            else:
                raise ValueError("Both inputs must be of the same type (either objects or arrays)")
                
            return (json.dumps(result, indent=2),)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON input")

    def _merge_dicts(self, dict1: dict, dict2: dict, strategy: str) -> dict:
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key not in result:
                result[key] = value
            else:
                if strategy == "override":
                    result[key] = value
                elif strategy == "preserve":
                    continue
                elif isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = self._merge_dicts(result[key], value, strategy)
                elif isinstance(result[key], list) and isinstance(value, list):
                    result[key] = result[key] + value
                    
        return result 

class ConvertJsonToString:    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "json_object": ("JSON",),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("json_string",)
    FUNCTION = "convert"
    CATEGORY = "LevelPixel/JSON"

    def convert(self, json_object):
        try:
            string_out = json.dumps(json_object, indent=4, ensure_ascii=False)
            return (string_out,)
        except Exception as e:
            return (f"Error: {str(e)}",)


class ConvertStringToJson:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "json_string": ("STRING", {"default": "{}"}),
            }
        }

    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("json_object",)
    FUNCTION = "convert"
    CATEGORY = "LevelPixel/JSON"

    def convert(self, json_string):
        try:
            json_object = json.loads(json_string)
            return (json_object,)
        except Exception as e:
            print(f"JSON Parse Error: {e}")
            return ({},)
        
class JSONLengthNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_string": ("STRING", {"multiline": True}),
            },
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("length",)
    FUNCTION = "get_length"
    CATEGORY = "LevelPixel/JSON"

    def get_length(self, json_string: str) -> tuple[int]:
        try:
            data = json.loads(json_string)
            if isinstance(data, (list, dict)):
                return (len(data),)
            return (1,)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON input")

class JSONKeyCheckerNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_string": ("STRING", {"multiline": True}),
                "key": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("BOOLEAN", "STRING")
    RETURN_NAMES = ("exists", "value")
    FUNCTION = "check_key"
    CATEGORY = "LevelPixel/JSON"

    def check_key(self, json_string: str, key: str) -> Tuple[bool, str]:
        try:
            data = json.loads(json_string)
            if not isinstance(data, dict):
                return (False, "")
                
            keys = key.split('.')
            current = data
            
            for k in keys:
                if k not in current:
                    return (False, "")
                current = current[k]
                
            if isinstance(current, (dict, list)):
                value = json.dumps(current)
            else:
                value = str(current)
                
            return (True, value)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON input")

class JSONStringifierNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_string": ("STRING", {"multiline": True}),
                "indent": ("INT", {"default": 4, "min": 0, "max": 8}),
                "sort_keys": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("json_string",)
    FUNCTION = "stringify"
    CATEGORY = "LevelPixel/JSON"

    def stringify(self, json_string: str, indent: int, sort_keys: bool) -> tuple[str]:
        try:
            data = json.loads(json_string)
            return (json.dumps(data, indent=indent, sort_keys=sort_keys),)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON input") 

NODE_CLASS_MAPPINGS = {
    "ParseJSONString|LP": ParseJSONString,
    "ModifyJSONObject|LP": ModifyJSONObject,
    "GetJSONValue|LP": GetJSONValue,
    "MergeJSONNode|LP": MergeJSONNode,
    "ConvertJsonToString|LP": ConvertJsonToString,
    "ConvertStringToJson|LP": ConvertStringToJson,
    "JSONLengthNode|LP": JSONLengthNode,
    "JSONKeyCheckerNode|LP": JSONKeyCheckerNode,
    "JSONStringifierNode|LP": JSONStringifierNode
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "ParseJSONString|LP": "Parse JSON String [LP]",
    "ModifyJSONObject|LP": "Modify JSON Object [LP]",
    "GetJSONValue|LP": "Get JSON Value [LP]",
    "MergeJSONNode|LP": "Merge JSON Node [LP]",
    "ConvertJsonToString|LP": "Convert JSON to String [LP]",
    "ConvertStringToJson|LP": "Convert String to JSON [LP]",
    "JSONLengthNode|LP": "Get JSON Length [LP]",
    "JSONKeyCheckerNode|LP": "Check JSON Key [LP]",
    "JSONStringifierNode|LP": "Stringify JSON [LP]"
}