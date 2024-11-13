import numpy as np
import io
import torch
from PIL import Image, ImageOps
import matplotlib.pyplot as plt
from rembg import new_session, remove
import comfy.sd
import comfy.utils
    
color_mapping = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "yellow": (255, 255, 0),
    "cyan": (0, 255, 255),
    "magenta": (255, 0, 255),
    "orange": (255, 165, 0),
    "purple": (128, 0, 128),
    "pink": (255, 192, 203),
    "brown": (165, 42, 42),
    "gray": (128, 128, 128),
    "lightgray": (211, 211, 211),
    "darkgray": (169, 169, 169),
    "olive": (128, 128, 0),
    "lime": (0, 128, 0),
    "teal": (0, 128, 128),
    "navy": (0, 0, 128),
    "maroon": (128, 0, 0),
    "fuchsia": (255, 0, 128),
    "aqua": (0, 255, 128),
    "silver": (192, 192, 192),
    "gold": (255, 215, 0),
    "turquoise": (64, 224, 208),
    "lavender": (230, 230, 250),
    "violet": (238, 130, 238),
    "coral": (255, 127, 80),
    "indigo": (75, 0, 130),    
}

COLORS = ["custom", "white", "black", "red", "green", "blue", "yellow",
          "cyan", "magenta", "orange", "purple", "pink", "brown", "gray",
          "lightgray", "darkgray", "olive", "lime", "teal", "navy", "maroon",
          "fuchsia", "aqua", "silver", "gold", "turquoise", "lavender",
          "violet", "coral", "indigo"]

model_list = [
'birefnet-massive', # BEST! Recommended! A pre-trained model with massive dataset. Source - https://github.com/ZhengPeng7/BiRefNet
'birefnet-general', # A pre-trained model for general use cases. Source - https://github.com/ZhengPeng7/BiRefNet
'birefnet-general-lite', # A light pre-trained model for general use cases. Source - https://github.com/ZhengPeng7/BiRefNet
'birefnet-portrait', # A pre-trained model for human portraits. Source - https://github.com/ZhengPeng7/BiRefNet
'birefnet-dis', # A pre-trained model for dichotomous image segmentation (DIS). Source - https://github.com/ZhengPeng7/BiRefNet
'birefnet-hrsod', # A pre-trained model for high-resolution salient object detection (HRSOD). Source - https://github.com/ZhengPeng7/BiRefNet
'birefnet-cod', # A pre-trained model for concealed object detection (COD). Source - https://github.com/ZhengPeng7/BiRefNet
'u2net', # A pre-trained model for general use cases. Source - https://github.com/xuebinqin/U-2-Net
'u2netp', # A lightweight version of u2net model. Source - https://github.com/xuebinqin/U-2-Net
'u2net_human_seg', # A pre-trained model for human segmentation. Source - https://github.com/xuebinqin/U-2-Net
'u2net_cloth_seg', # A pre-trained model for Cloths Parsing from human portrait. Here clothes are parsed into 3 category: Upper body, Lower body and Full body. Source - https://github.com/levindabhi/cloth-segmentation
'silueta', # Same as u2net but the size is reduced to 43Mb. Source - https://github.com/xuebinqin/U-2-Net/issues/295
'isnet-general-use', # A new pre-trained model for general use cases. Source - https://github.com/xuebinqin/DIS
'isnet-anime', # A high-accuracy segmentation for anime character. Source - https://github.com/SkyTNT/anime-segmentation
'sam' # A pre-trained model for any use cases. Source - https://github.com/danielgatis/rembg/releases/download/v0.0.0/vit_b-decoder-quant.onnx
]

def pil2tensor(image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)

    
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b) 

class FastCheckerPattern:

    @classmethod
    def INPUT_TYPES(s):        
        return {"required": {
                    "width": ("INT", {"default": 512, "min": 64, "max": 4096}),
                    "height": ("INT", {"default": 512, "min": 64, "max": 4096}),
                    "color_1": (COLORS,),
                    "color_2": (COLORS,), 
                    "grid_frequency": ("INT", {"default": 50, "min": 1, "max": 200, "step": 1}),
                },
                "optional": {
                    "color1_hex": ("STRING", {"multiline": False, "default": "#C0C0C0"}),
                    "color2_hex": ("STRING", {"multiline": False, "default": "#808080"}),
                }        
    }

    RETURN_TYPES = ("IMAGE", )
    RETURN_NAMES = ("IMAGE", )
    FUNCTION = "draw"
    CATEGORY = "LevelPixel/Image"

    def draw(self, width, height, color_1, color_2,
            grid_frequency, color1_hex='#C0C0C0', color2_hex='#808080'):
            
        if color_1 == "custom":
            color1_rgb = hex_to_rgb(color1_hex)
        else:
            color1_rgb = color_mapping.get(color_1, (255, 255, 255))

        if color_2 == "custom":
            color2_rgb = hex_to_rgb(color2_hex)
        else:
            color2_rgb = color_mapping.get(color_2, (0, 0, 0))

        canvas = np.zeros((height, width, 3), dtype=np.uint8)
        
        grid_size = width // grid_frequency

        x_indices = np.arange(width) // grid_size
        y_indices = np.arange(height) // grid_size

        x_grid, y_grid = np.meshgrid(x_indices, y_indices)

        checker_pattern = (x_grid + y_grid) % 2

        canvas[checker_pattern == 0] = color1_rgb
        canvas[checker_pattern == 1] = color2_rgb

        fig, ax = plt.subplots(figsize=(width/100, height/100))
        ax.imshow(canvas)

        plt.axis('off')
        plt.tight_layout(pad=0, w_pad=0, h_pad=0)
        plt.autoscale(tight=True)

        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        img = Image.open(img_buf)

        image_out = pil2tensor(img.convert("RGB"))

        return (image_out,)
        

def tensor2pil(image):
    return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))

def list_model():
    return model_list


class ImageRemoveBackground:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model_name": (list_model(), ),
                "image": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "remove_background"
    CATEGORY = "LevelPixel/Image"

    def remove_background(self, image, model_name):
        session = new_session(model_name)
        image = pil2tensor(remove(tensor2pil(image), session = session))
        return (image,)


class ImageOverlay:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_image": ("IMAGE",),
                "overlay_image": ("IMAGE",),
                "overlay_resize": (["None", "Fit", "Resize by rescale_factor", "Resize to width & heigth"],),
                "resize_method": (["nearest-exact", "bilinear", "area"],),
                "rescale_factor": ("FLOAT", {"default": 1, "min": 0.01, "max": 16.0, "step": 0.1}),
                "width": ("INT", {"default": 1024, "min": 0, "max": 32768, "step": 64}),
                "height": ("INT", {"default": 1024, "min": 0, "max": 32768, "step": 64}),
                "x_offset": ("INT", {"default": 0, "min": -48000, "max": 48000, "step": 10}),
                "y_offset": ("INT", {"default": 0, "min": -48000, "max": 48000, "step": 10}),
                "rotation": ("INT", {"default": 0, "min": -180, "max": 180, "step": 5}),
                "opacity": ("FLOAT", {"default": 0, "min": 0, "max": 100, "step": 5}),
            },
            "optional": {"optional_mask": ("MASK",),}
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "apply_overlay_image"
    CATEGORY = "LevelPixel/Image"

    def apply_overlay_image(self, base_image, overlay_image, overlay_resize, resize_method, rescale_factor,
                            width, height, x_offset, y_offset, rotation, opacity, optional_mask=None):

        # Pack tuples and assign variables
        size = width, height
        location = x_offset, y_offset
        mask = optional_mask

        # Check for different sizing options
        if overlay_resize != "None":
            #Extract overlay_image size and store in Tuple "overlay_image_size" (WxH)
            overlay_image_size = overlay_image.size()
            overlay_image_size = (overlay_image_size[2], overlay_image_size[1])
            if overlay_resize == "Fit":
                h_ratio = base_image.size()[1] / overlay_image_size[1]
                w_ratio = base_image.size()[2] / overlay_image_size[0]
                ratio = min(h_ratio, w_ratio)
                overlay_image_size = tuple(round(dimension * ratio) for dimension in overlay_image_size)
            elif overlay_resize == "Resize by rescale_factor":
                overlay_image_size = tuple(int(dimension * rescale_factor) for dimension in overlay_image_size)
            elif overlay_resize == "Resize to width & heigth":
                overlay_image_size = (size[0], size[1])

            samples = overlay_image.movedim(-1, 1)
            overlay_image = comfy.utils.common_upscale(samples, overlay_image_size[0], overlay_image_size[1], resize_method, False)
            overlay_image = overlay_image.movedim(1, -1)
            
        overlay_image = tensor2pil(overlay_image)

         # Add Alpha channel to overlay
        overlay_image = overlay_image.convert('RGBA')
        overlay_image.putalpha(Image.new("L", overlay_image.size, 255))

        # If mask connected, check if the overlay_image image has an alpha channel
        if mask is not None:
            # Convert mask to pil and resize
            mask = tensor2pil(mask)
            mask = mask.resize(overlay_image.size)
            # Apply mask as overlay's alpha
            overlay_image.putalpha(ImageOps.invert(mask))

        # Rotate the overlay image
        overlay_image = overlay_image.rotate(rotation, expand=True)

        # Apply opacity on overlay image
        r, g, b, a = overlay_image.split()
        a = a.point(lambda x: max(0, int(x * (1 - opacity / 100))))
        overlay_image.putalpha(a)

        # Split the base_image tensor along the first dimension to get a list of tensors
        base_image_list = torch.unbind(base_image, dim=0)

        # Convert each tensor to a PIL image, apply the overlay, and then convert it back to a tensor
        processed_base_image_list = []
        for tensor in base_image_list:
            # Convert tensor to PIL Image
            image = tensor2pil(tensor)

            # Paste the overlay image onto the base image
            if mask is None:
                image.paste(overlay_image, location)
            else:
                image.paste(overlay_image, location, overlay_image)

            # Convert PIL Image back to tensor
            processed_tensor = pil2tensor(image)

            # Append to list
            processed_base_image_list.append(processed_tensor)

        # Combine the processed images back into a single tensor
        base_image = torch.stack([tensor.squeeze() for tensor in processed_base_image_list])

        # Return the edited base image
        return (base_image,)



NODE_CLASS_MAPPINGS = {
    "ImageOverlay|LP": ImageOverlay,
    "FastCheckerPattern|LP": FastCheckerPattern,
    "ImageRemoveBackground|LP": ImageRemoveBackground,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageOverlay|LP": "Image Overlay [LP]",
    "FastCheckerPattern|LP": "Fast Checker Pattern [LP]",
    "ImageRemoveBackground|LP": "Image Remove Background [LP]",
}
