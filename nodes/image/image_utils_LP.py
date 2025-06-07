import comfy.utils
import numpy as np
import io
import torch
import nodes
import matplotlib.pyplot as plt
import torchvision.transforms.functional as F
from PIL import Image, ImageOps

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

def pil2tensor(image):
    return torch.from_numpy(np.array(image).astype(np.float32) / 255.0).unsqueeze(0)
    
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b) 

def tensor2pil(image):
    return Image.fromarray(np.clip(255. * image.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))

def rescale_i(samples, width, height, algorithm: str):
    samples = samples.movedim(-1, 1)
    algorithm = getattr(Image, algorithm.upper())  # i.e. Image.BICUBIC
    samples_pil: Image.Image = F.to_pil_image(samples[0].cpu()).resize((width, height), algorithm)
    samples = F.to_tensor(samples_pil).unsqueeze(0)
    samples = samples.movedim(1, -1)
    return samples


def rescale_m(samples, width, height, algorithm: str):
    samples = samples.unsqueeze(1)
    algorithm = getattr(Image, algorithm.upper())  # i.e. Image.BICUBIC
    samples_pil: Image.Image = F.to_pil_image(samples[0].cpu()).resize((width, height), algorithm)
    samples = F.to_tensor(samples_pil).unsqueeze(0)
    samples = samples.squeeze(1)
    return samples


def preresize_imm(downscale_algorithm, upscale_algorithm, preresize_mode, preresize_min_width, preresize_min_height, preresize_max_width, preresize_max_height, image=None, mask=None, optional_context_mask=None):
    current_width, current_height = image.shape[2], image.shape[1]  # Image size [batch, height, width, channels]
    
    if preresize_mode == "ensure minimum resolution":
        if current_width >= preresize_min_width and current_height >= preresize_min_height:
            return image, mask, optional_context_mask

        scale_factor_min_width = preresize_min_width / current_width
        scale_factor_min_height = preresize_min_height / current_height

        scale_factor = max(scale_factor_min_width, scale_factor_min_height)

        target_width = int(current_width * scale_factor)
        target_height = int(current_height * scale_factor)

        if image is not None: image = rescale_i(image, target_width, target_height, upscale_algorithm)
        if mask is not None: mask = rescale_m(mask, target_width, target_height, 'bilinear')
        if optional_context_mask is not None: optional_context_mask = rescale_m(optional_context_mask, target_width, target_height, 'bilinear')
        
        assert target_width >= preresize_min_width and target_height >= preresize_min_height, \
            f"Internal error: After resizing, target size {target_width}x{target_height} is smaller than min size {preresize_min_width}x{preresize_min_height}"

    elif preresize_mode == "ensure minimum and maximum resolution":
        if preresize_min_width <= current_width <= preresize_max_width and preresize_min_height <= current_height <= preresize_max_height:
            return image, mask, optional_context_mask

        scale_factor_min_width = preresize_min_width / current_width
        scale_factor_min_height = preresize_min_height / current_height
        scale_factor_min = max(scale_factor_min_width, scale_factor_min_height)

        scale_factor_max_width = preresize_max_width / current_width
        scale_factor_max_height = preresize_max_height / current_height
        scale_factor_max = min(scale_factor_max_width, scale_factor_max_height)

        if scale_factor_min > 1 and scale_factor_max < 1:
            assert False, "Cannot meet both minimum and maximum resolution requirements with aspect ratio preservation."
        
        if scale_factor_min > 1:  # We're upscaling to meet min resolution
            scale_factor = scale_factor_min
            rescale_algorithm = upscale_algorithm  # Use upscale algorithm for min resolution
        else:  # We're downscaling to meet max resolution
            scale_factor = scale_factor_max
            rescale_algorithm = downscale_algorithm  # Use downscale algorithm for max resolution

        target_width = int(current_width * scale_factor)
        target_height = int(current_height * scale_factor)

        if image is not None: image = rescale_i(image, target_width, target_height, rescale_algorithm)
        if mask is not None: mask = rescale_m(mask, target_width, target_height, 'nearest') # Always nearest for efficiency
        if optional_context_mask is not None: optional_context_mask = rescale_m(optional_context_mask, target_width, target_height, 'nearest') # Always nearest for efficiency
        
        assert preresize_min_width <= target_width <= preresize_max_width, \
            f"Internal error: Target width {target_width} is outside the range {preresize_min_width} - {preresize_max_width}"
        assert preresize_min_height <= target_height <= preresize_max_height, \
            f"Internal error: Target height {target_height} is outside the range {preresize_min_height} - {preresize_max_height}"

    elif preresize_mode == "ensure maximum resolution":
        if current_width <= preresize_max_width and current_height <= preresize_max_height:
            return image, mask, optional_context_mask

        scale_factor_max_width = preresize_max_width / current_width
        scale_factor_max_height = preresize_max_height / current_height
        scale_factor_max = min(scale_factor_max_width, scale_factor_max_height)

        target_width = int(current_width * scale_factor_max)
        target_height = int(current_height * scale_factor_max)

        if image is not None: image = rescale_i(image, target_width, target_height, downscale_algorithm)
        if mask is not None: mask = rescale_m(mask, target_width, target_height, 'nearest')  # Always nearest for efficiency
        if optional_context_mask is not None: optional_context_mask = rescale_m(optional_context_mask, target_width, target_height, 'nearest')  # Always nearest for efficiency

        assert target_width <= preresize_max_width and target_height <= preresize_max_height, \
            f"Internal error: Target size {target_width}x{target_height} is greater than max size {preresize_max_width}x{preresize_max_height}"

    return image, mask, optional_context_mask

def compute_target_size(width, height, target_resolution, aspect_ratio_limit=2):
    ratio = max(1 / aspect_ratio_limit, min(width / height, aspect_ratio_limit))
    height_new = target_resolution * 2 / (ratio + 1)
    width_new = ratio * height_new
    target_size = {
            "target_height": int(round(height_new)),
            "target_width": int(round(width_new)),
        }

    return target_size

def calculate_target_size(mask, target_resolution, aspect_ratio_limit=2):
    B, H, W = mask.shape
    mask = mask.round()

    for b in range(B):
        rows = torch.any(mask[min(b, mask.shape[0]-1)] > 0, dim=1)
        cols = torch.any(mask[min(b, mask.shape[0]-1)] > 0, dim=0)

        row_indices = torch.where(rows)[0]
        col_indices = torch.where(cols)[0]

        if row_indices.numel() == 0 or col_indices.numel() == 0:
            width, height = W, H
        else:
            y_min, y_max = row_indices[[0, -1]]
            x_min, x_max = col_indices[[0, -1]]
            width = (x_max - x_min + 1).item()
            height = (y_max - y_min + 1).item()

        return compute_target_size(width, height, target_resolution, aspect_ratio_limit)

class CalculateTargetSizeByMask:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", ),
                "mask": ("MASK", ),
                "target_size": ("INT", {"default": 1024, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 1}),
                "aspect_ratio_limit": ("FLOAT", {"default": 2, "min": 0, "max": 100, "step": 0.01}),
            },
        }

    RETURN_TYPES = ("INT", "INT",)
    RETURN_NAMES = ("height", "width",)
    FUNCTION = "calculate_target_size"
    CATEGORY = "LevelPixel/Image"
    def calculate_target_size(self, image, mask, target_size=1024, aspect_ratio_limit=2):
        target_size = calculate_target_size(image, mask, target_size, aspect_ratio_limit)
        target_height, target_width = (target_size["target_height"], target_size["target_width"])
        
        return (target_height, target_width, )

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

def calculate_scale_factor(width, height, target_size, mode="max"):
    if mode == "min":
        base_size = min(width, height)
    elif mode == "max":
        base_size = max(width, height)
    elif mode == "avg":
        base_size = (width + height) / 2
    else:
        raise ValueError("Mode must be 'min', 'max', or 'avg'")
    
    scale_factor = target_size / base_size
    return scale_factor

def target_scale_factor(width, height, target_size=9000):
    aspect_ratio = width / height if width > height else height / width
    
    if 0.9 <= aspect_ratio <= 1.1:
        mode = "max"
    elif aspect_ratio > 1.5 or aspect_ratio < 0.67:
        mode = "avg"
    else:
        mode = "max"
    
    scale_factor = calculate_scale_factor(width, height, target_size, mode)
    return scale_factor

def tensor_to_pil(image_tensor):
    if image_tensor.ndimension() == 4:
        image_tensor = image_tensor.squeeze(0)
    if image_tensor.shape[0] in [1, 3]:
        image_tensor = image_tensor.permute(1, 2, 0)
    image_tensor = image_tensor.cpu().numpy()
    image_tensor = (image_tensor * 255).clip(0, 255).astype(np.uint8)
    return Image.fromarray(image_tensor)

def pil_to_tensor(image):
    image = np.array(image).astype(np.float32) / 255.0
    image = torch.tensor(image).permute(2, 0, 1)
    return image

class ResizeImageToTargetSize:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "resize_method": (["LANCZOS", "BICUBIC", "BILINEAR", "NEAREST"],),
                "target_size": ([1000, 2000, 9000],),
            },
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "resize_image_to_target_size"
    CATEGORY = "LevelPixel/Image"
    def resize_image_to_target_size(self, image, resize_method='LANCZOS', target_size=1000):
        size_table = {
            1000: [(640, 1536), (768, 1344), (832, 1216), (896, 1152), (1024, 1024), (1152, 896), (1216, 832), (1344, 768), (1536, 640)],
            2000: [(1280, 3072), (1536, 2688), (1664, 2432), (1792, 2304), (2048, 2048), (2304, 1792), (2432, 1664), (2688, 1536), (3072, 1280)],
            9000: [(5000, 12500), (6000, 10500), (6000, 9000), (7000, 9000), (9000, 9000), (9000, 7000), (9000, 6000), (10500, 6000), (12500, 5000)]
        }

        interpolation_methods = {
            'NEAREST': Image.NEAREST,
            'BILINEAR': Image.BILINEAR,
            'BICUBIC': Image.BICUBIC,
            'LANCZOS': Image.LANCZOS
        }

        img = tensor2pil(image).convert("RGB")
        width, height = img.size

        scale_factor = target_scale_factor(width, height, target_size)
        new_width, new_height = int(width * scale_factor), int(height * scale_factor)
        closest_size = min(size_table[target_size], key=lambda s: abs(s[0] - new_width) + abs(s[1] - new_height))

        aspect_ratio = width / height if width > height else height / width
    
        if 0.9 <= aspect_ratio <= 1.1:
            mode = "max"
        elif aspect_ratio > 1.5 or aspect_ratio < 0.67:
            mode = "avg"
        else:
            mode = "max"

        if mode == "avg":
            target_size = (closest_size[0] + closest_size[1]) / 2
        
        if target_size > 9000:
            target_size = 9000

        scale_factor = target_scale_factor(width, height, target_size)
        new_width, new_height = int(width * scale_factor), int(height * scale_factor)

        while ((new_width < closest_size[0]) | (new_height < closest_size[1])):
            target_size = target_size + 10
            scale_factor = target_scale_factor(width, height, target_size)
            new_width, new_height = int(width * scale_factor), int(height * scale_factor)

        img = img.resize((new_width, new_height), interpolation_methods[resize_method])

        if new_width >= closest_size[0] and new_height >= closest_size[1]:
            left = (new_width - closest_size[0]) // 2
            top = (new_height - closest_size[1]) // 2
            img = img.crop((left, top, left + closest_size[0], top + closest_size[1]))
        
        return (pil2tensor(img),)

class ResizeImageAndMasks:        
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "downscale_algorithm": (["nearest", "bilinear", "bicubic", "lanczos", "box", "hamming"], {"default": "lanczos"}),
                "upscale_algorithm": (["nearest", "bilinear", "bicubic", "lanczos", "box", "hamming"], {"default": "lanczos"}),
                "preresize_mode": (["ensure minimum resolution", "ensure maximum resolution", "ensure minimum and maximum resolution"], {"default": "ensure minimum resolution"}),
                "preresize_min_width": ("INT", {"default": 1024, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 1}),
                "preresize_min_height": ("INT", {"default": 1024, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 1}),
                "preresize_max_width": ("INT", {"default": nodes.MAX_RESOLUTION, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 1}),
                "preresize_max_height": ("INT", {"default": nodes.MAX_RESOLUTION, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 1}),
           },
           "optional": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "optional_context_mask": ("MASK",),
           }
        }

    FUNCTION = "resize_image_and_masks"
    CATEGORY = "LevelPixel/Image"
    DESCRIPTION = "Crops an image around a mask for inpainting, the optional context mask defines an extra area to keep for the context."

    RETURN_TYPES = ("IMAGE", "MASK", "MASK")
    RETURN_NAMES = ("image", "mask", "optional_context_mask")

    def resize_image_and_masks(self, downscale_algorithm, upscale_algorithm, preresize_mode, preresize_min_width, preresize_min_height, preresize_max_width, preresize_max_height, image=None, mask=None, optional_context_mask=None):
        image, mask, optional_context_mask = preresize_imm(downscale_algorithm, upscale_algorithm, preresize_mode, preresize_min_width, preresize_min_height, preresize_max_width, preresize_max_height, image, mask, optional_context_mask,)

        return (image, mask, optional_context_mask)

NODE_CLASS_MAPPINGS = {
    "ImageOverlay|LP": ImageOverlay,
    "FastCheckerPattern|LP": FastCheckerPattern,
    "ResizeImageToTargetSize|LP": ResizeImageToTargetSize,
    "CalculateTargetSizeByMask|LP": CalculateTargetSizeByMask,
    "ResizeImageAndMasks|LP": ResizeImageAndMasks
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageOverlay|LP": "Image Overlay [LP]",
    "FastCheckerPattern|LP": "Fast Checker Pattern [LP]",
    "ResizeImageToTargetSize|LP": "Resize Image To Target Size [LP]",
    "CalculateTargetSizeByMask|LP": "Calculate Target Size By Mask [LP]",
    "ResizeImageAndMasks|LP": "Resize Image and Masks [LP]"
}
