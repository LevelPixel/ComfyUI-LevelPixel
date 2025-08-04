import os
import glob
import cv2

class GetIteratorDataVideos:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory_path": ("STRING", {"default": '', "multiline": False}),
                "patterns": ("STRING", {"default": '*.mp4|*.avi|*.mov|*.mkv', "multiline": False}),
                "rescan_each_queue": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("ITERATOR_DATA", "INT", "INT")
    RETURN_NAMES = ("iterator_data", "video_count", "frame_count")
    FUNCTION = "prepare_iterator_data_from_videos"
    CATEGORY = "LevelPixel/Iterators"

    @classmethod
    def IS_CHANGED(cls, directory_path, patterns, rescan_each_queue, *v):
        if rescan_each_queue == True:
            return float("NaN")
        else:
            return False

    def prepare_iterator_data_from_videos(self, directory_path, patterns, rescan_each_queue):
        if not os.path.isdir(directory_path):
            return ([], 0, 0)
        iterator_data = []
        video_files = []
        for pattern in patterns.split("|"):
            video_files.extend(glob.glob(os.path.join(directory_path, pattern)))
        video_files = sorted(video_files)
        total_frames = 0
        for idx, video_path in enumerate(video_files):
            name = os.path.basename(video_path)
            try:
                cap = cv2.VideoCapture(video_path)
                count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                cap.release()
            except Exception:
                count = 0
            iterator_data.append({"index": idx, "name": name, "count": count})
            total_frames += count
        return (iterator_data, len(video_files), total_frames)


class GetIteratorDataImageFolders:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "directory_path": ("STRING", {"default": '', "multiline": False}),
                "patterns": ("STRING", {"default": '*.jpg|*.png|*.jpeg', "multiline": False}),
                "subfolder": ("STRING", {"default": '', "multiline": False}),
                "rescan_each_queue": ("BOOLEAN", {"default": True}),
            },
        }

    RETURN_TYPES = ("ITERATOR_DATA", "INT", "INT")
    RETURN_NAMES = ("iterator_data", "folder_count", "image_count")
    FUNCTION = "prepare_iterator_data_from_image_folders"
    CATEGORY = "LevelPixel/Iterators"

    @classmethod
    def IS_CHANGED(cls, directory_path, patterns, subfolder, rescan_each_queue, *v):
        if rescan_each_queue == True:
            return float("NaN")
        else:
            return False

    def prepare_iterator_data_from_image_folders(self, directory_path, patterns, subfolder, rescan_each_queue):
        if not os.path.isdir(directory_path):
            return ([], 0, 0)
        iterator_data = []
        folders = [f for f in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, f))]
        total_images = 0
        for idx, folder in enumerate(sorted(folders)):
            if subfolder:
                search_path = os.path.join(directory_path, folder, subfolder)
            else:
                search_path = os.path.join(directory_path, folder)
            count = 0
            if os.path.isdir(search_path):
                for pattern in patterns.split("|"):
                    count += len(glob.glob(os.path.join(search_path, pattern)))
            iterator_data.append({"index": idx, "name": folder, "count": count})
            total_images += count
        return (iterator_data, len(folders), total_images)

class ImageDataIterator:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "iterator_data": ("ITERATOR_DATA",),
                "global_index": ("INT", {"default": 0, "min": 0, "control_after_generate": True}),
            }
        }

    RETURN_TYPES = ("INT", "INT", "STRING", "INT")
    RETURN_NAMES = ("item_index", "set_index", "set_name", "global_index")
    FUNCTION = "iterate"
    CATEGORY = "LevelPixel/Iterators"

    def iterate(self, iterator_data, global_index):
        total = 0
        total_frames = sum(item["count"] for item in iterator_data)
        if global_index >= total_frames:
            raise RuntimeError("Image iteration finished")
        for i, item in enumerate(iterator_data):
            count = item["count"]
            if global_index < total + count:
                item_index = global_index - total
                set_index = item["index"]
                set_name = item["name"]
                return (item_index, set_index, set_name, global_index)
            total += count
        return (0, 0, '', global_index)
    
class Iterator:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "index": ("INT", {"default": 0, "min": 0, "max": 999999, "control_after_generate": True}),
                "limit": ("INT", {"default": 0, "min": 0, "max": 999999}),
                "mode": ([
                    "Greater (index > limit)",
                    "Less (index < limit)",
                    "Equal (index == limit)",
                    "Greater or Equal (index >= limit)",
                    "Less or Equal (index <= limit)"
                ], {"default": "Greater (index > limit)"}),
            },
        }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("index",)
    FUNCTION = "indexate"
    CATEGORY = "LevelPixel/Iterators"

    def indexate(self, index, limit, mode):
        if mode == "Greater (index > limit)":
            if index > limit:
                raise RuntimeError("Iteration finished (index > limit)")
        elif mode == "Less (index < limit)":
            if index < limit:
                raise RuntimeError("Iteration finished (index < limit)")
        elif mode == "Equal (index == limit)":
            if index == limit:
                raise RuntimeError("Iteration finished (index == limit)")
        elif mode == "Greater or Equal (index >= limit)":
            if index >= limit:
                raise RuntimeError("Iteration finished (index >= limit)")
        elif mode == "Less or Equal (index <= limit)":
            if index <= limit:
                raise RuntimeError("Iteration finished (index <= limit)")
        return (index,)

NODE_CLASS_MAPPINGS = {
    "GetIteratorDataVideos|LP": GetIteratorDataVideos,
    "GetIteratorDataImageFolders|LP": GetIteratorDataImageFolders,
    "ImageDataIterator|LP": ImageDataIterator,
    "Iterator|LP": Iterator,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GetIteratorDataVideos|LP": "Get Iterator Data From Videos [LP]",
    "GetIteratorDataImageFolders|LP": "Get Iterator Data From Image Folders [LP]",
    "ImageDataIterator|LP": "Image Data Iterator [LP]",
    "Iterator|LP": "Iterator [LP]",
}
