import glob
import os

class FileCounter:
    FUNCTION = "file_counter"
    OUTPUT_NODE = True
    CATEGORY = "LevelPixel/IO"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory_path": ("STRING", {"default": '', "multiline": False}),
                "patterns": ("STRING", {"default": '*.jpg|*.png|*.jpeg', "multiline": False}),
            },
        }

    RETURN_TYPES = ("INT","STRING")
    RETURN_NAMES = ("Total INT","Total STRING")
    FUNCTION = "file_counter"

    @classmethod
    def IS_CHANGED(cls, *v):
        return ALWAYS_CHANGED_FLAG

    def file_counter(self, directory_path, patterns):
        if not os.path.isdir(directory_path):
            return (0,)
        total_int = 0
        for pattern in patterns.split("|"):
            files = list(glob.glob(pattern, root_dir=directory_path))
            total_int += len(files)
        total_string = str(total_int)
        print("total " + str(total_int))
        return (total_int, total_string)

NODE_CLASS_MAPPINGS = {
    "FileCounter|LP": FileCounter,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FileCounter|LP": "File Counter [LP]",
}

