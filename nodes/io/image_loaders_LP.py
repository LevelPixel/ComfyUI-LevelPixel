import numpy as np
import os
from PIL import Image, ImageOps, ImageSequence
import folder_paths
import re
import torch
import node_helpers
import hashlib

class ImageLoaderFromPath:

    @classmethod
    def INPUT_TYPES(s):
    
        input_dir = folder_paths.input_directory
        image_folder = [name for name in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir,name))]
        image_folder.append("")
    
        return {"required": {"input_folder": (sorted(image_folder), ),
                             "start_index": ("INT", {"default": 0, "min": 0, "max": 9999}),
                             "max_images": ("INT", {"default": 1, "min": 1, "max": 9999}),
                             "white_bg": (["disable","enable"],),
                             "patterns": ("STRING", {"default": '*.jpg|*.png|*.jpeg', "multiline": False}),
               },
               "optional": {"input_path": ("STRING", {"default": '', "multiline": False}),     
               }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING" )
    RETURN_NAMES = ("IMAGE", "MASK", "Filename STRING" )
    OUTPUT_IS_LIST = (True, True, True)
    FUNCTION = "loader_images"
    CATEGORY = "LevelPixel/IO"

    def loader_images(self, start_index, max_images, white_bg, patterns, input_folder="", input_path=None):

        if input_path != '' and input_path is not None:
            if not os.path.exists(input_path):
                print(f"[Warning] Image Loader From Path: The input_path `{input_path}` does not exist")
                return ("",)  
            in_path = input_path
        else:
            input_dir = folder_paths.input_directory
            in_path = os.path.join(input_dir, input_folder)

        if not os.listdir(in_path):
            print(f"[Warning] Image Loader From Path: The folder `{in_path}` is empty")
            return None

        file_list = sorted(os.listdir(in_path), key=lambda s: sum(((s, int(n)) for s, n in re.findall(r'(\D+)(\d+)', 'a%s0' % s)), ()))
        extensions = tuple(patterns.replace('*', '').split('|'))
        file_list = [f for f in file_list if f.lower().endswith(extensions)]
        
        image_list = []
        mask_list = []
        filename_list = []
        
        start_index = max(0, start_index)
        end_index = min(start_index + max_images, len(file_list))
                    
        for num in range(start_index, end_index):
            img = Image.open(os.path.join(in_path, file_list[num]))

            image = img.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            if 'A' in img.getbands():
                mask = np.array(img.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
                if white_bg=="enable":
                    nw = mask.unsqueeze(0).unsqueeze(-1).repeat(1, 1, 1, 3)
                    image[nw == 1] = 1.0
            else:
                mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
                
            image_list.append(image)
            mask_list.append(mask)
            filename_list.append(file_list[num])
        
        if not image_list:
            print("Image Loader From Path: No images found.")
            return None

        return (image_list, mask_list, filename_list)
    
class LoadImage:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {"required":
                    {"image": (sorted(files), {"image_upload": True})},
                }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING" )
    RETURN_NAMES = ("IMAGE", "MASK", "Filename STRING")

    FUNCTION = "load_image"

    CATEGORY = "LevelPixel/IO"

    def load_image(self, image):
        image_path = folder_paths.get_annotated_filepath(image)
        file_name = os.path.basename(image_path)
        
        img = node_helpers.pillow(Image.open, image_path)
        
        output_images = []
        output_masks = []
        output_filenames = []
        w, h = None, None

        excluded_formats = ['MPO']
        
        for i in ImageSequence.Iterator(img):
            i = node_helpers.pillow(ImageOps.exif_transpose, i)

            if i.mode == 'I':
                i = i.point(lambda i: i * (1 / 255))
            image = i.convert("RGB")

            if len(output_images) == 0:
                w = image.size[0]
                h = image.size[1]
            
            if image.size[0] != w or image.size[1] != h:
                continue
            
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
            output_images.append(image)
            output_masks.append(mask.unsqueeze(0))
            output_filenames.append(file_name)

        if len(output_images) > 1 and img.format not in excluded_formats:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]
            output_filename = output_filenames[0]

        return (output_image, output_mask, output_filename)

    @classmethod
    def IS_CHANGED(s, image):
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, 'rb') as f:
            m.update(f.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(s, image):
        if not folder_paths.exists_annotated_filepath(image):
            return "Invalid image file: {}".format(image)

        return True
        
NODE_CLASS_MAPPINGS = {
    "ImageLoaderFromPath|LP": ImageLoaderFromPath,
    "LoadImage|LP": LoadImage,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageLoaderFromPath|LP": "Image Loader From Path [LP]",
    "LoadImage|LP": "Load Image [LP]",
}

