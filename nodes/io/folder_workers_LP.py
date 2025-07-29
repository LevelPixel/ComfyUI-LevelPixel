import folder_paths
import glob
import os

class FileCounter:
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

    OUTPUT_NODE = True
    CATEGORY = "LevelPixel/IO"

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

class GetComfyUIFolderPath:
    @classmethod
    def INPUT_TYPES(cls):
        try:
            folder_names = list(folder_paths.folder_names_and_paths.keys())
        except Exception:
            folder_names = []
        standard_folders = ["base", "model", "output", "temp", "input"]
        for name in standard_folders:
            if name not in folder_names:
                folder_names.append(name)
        return {
            "required": {
                "folder_name": (folder_names, {"default": folder_names[0] if folder_names else "input"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("folder_path",)

    CATEGORY = "LevelPixel/IO"
    FUNCTION = "get_comfyui_folder_path"

    def get_comfyui_folder_path(self, folder_name):
        try:
            if folder_name == "base":
                return (str(folder_paths.base_path),)
            elif folder_name == "model":
                return (str(folder_paths.models_dir),)
            elif folder_name == "output":
                return (str(folder_paths.get_output_directory()),)
            elif folder_name == "temp":
                return (str(folder_paths.get_temp_directory()),)
            elif folder_name == "input":
                return (str(folder_paths.get_input_directory()),)
            path = folder_paths.get_folder_paths(folder_name)
            if isinstance(path, list):
                return (path[0],)
            return (str(path),)
        except Exception as e:
            return (f"Error: {e}",)
        
class GetComfyUIHttpFolderPath:
    @classmethod
    def INPUT_TYPES(cls):
        folder_names = ["output", "temp", "input"]
        return {
            "required": {
                "folder_name": (folder_names, {"default": folder_names[0]}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("folder_path",)

    CATEGORY = "LevelPixel/IO"
    FUNCTION = "get_comfyui_http_folder_path"

    def get_comfyui_http_folder_path(self, folder_name):
        try:
            path = folder_paths.get_directory_by_type(folder_name)
            if path is not None:
                return (str(path),)
            return (f"Not allowed or unknown folder: {folder_name}",)
        except Exception as e:
            return (f"Error: {e}",)
        

class GetFilenameByIndexInFolder:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "folder_path": ("STRING", {"default": "", "multiline": False}),
                "file_index": ("INT", {"default": 0, "min": 0, "step": 1}),
                "patterns": ("STRING", {"default": "*", "multiline": False}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("full_filename", "filename", "extension")

    CATEGORY = "LevelPixel/IO"
    FUNCTION = "get_filename_by_index_in_folder"

    def get_filename_by_index_in_folder(self, folder_path, file_index, patterns):
        if not os.path.isdir(folder_path):
            return ("Error: not a directory", "", "")
        files = []
        for pattern in patterns.split("|"):
            files.extend(glob.glob(os.path.join(folder_path, pattern)))
        if not files:
            return ("Error: no files found", "", "")
        files.sort(key=lambda x: os.path.getctime(x))
        if file_index < 0 or file_index >= len(files):
            return (f"Error: index {file_index} out of range (found {len(files)} files)", "", "")
        full_filename = os.path.basename(files[file_index])
        filename, extension = os.path.splitext(full_filename)
        extension = extension[1:] if extension.startswith(".") else extension
        return (full_filename, filename, extension)

NODE_CLASS_MAPPINGS = {
    "FileCounter|LP": FileCounter,
    "GetComfyUIFolderPath|LP": GetComfyUIFolderPath,
    "GetComfyUIHttpFolderPath|LP": GetComfyUIHttpFolderPath,
    "GetFilenameByIndexInFolder|LP": GetFilenameByIndexInFolder,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FileCounter|LP": "File Counter [LP]",
    "GetComfyUIFolderPath|LP": "Get ComfyUI Folder Path [LP]",
    "GetComfyUIHttpFolderPath|LP": "Get ComfyUI HTTP Folder Path [LP]",
    "GetFilenameByIndexInFolder|LP": "Get Filename By Index In Folder [LP]",
}

