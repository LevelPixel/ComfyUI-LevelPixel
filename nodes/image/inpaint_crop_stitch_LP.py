import comfy.utils
import math
import nodes
import numpy as np
import torch
from scipy.ndimage import gaussian_filter, grey_dilation, binary_closing, binary_fill_holes
import torchvision.transforms.functional as F
from PIL import Image

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

def fillholes_iterative_hipass_fill_m(samples):
    thresholds = [1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1]

    mask_np = samples.squeeze(0).cpu().numpy()

    for threshold in thresholds:
        thresholded_mask = mask_np >= threshold
        closed_mask = binary_closing(thresholded_mask, structure=np.ones((3, 3)), border_value=1)
        filled_mask = binary_fill_holes(closed_mask)
        mask_np = np.maximum(mask_np, np.where(filled_mask != 0, threshold, 0))

    final_mask = torch.from_numpy(mask_np.astype(np.float32)).unsqueeze(0)

    return final_mask


def hipassfilter_m(samples, threshold):
    filtered_mask = samples.clone()
    filtered_mask[filtered_mask < threshold] = 0
    return filtered_mask


def expand_m(mask, pixels):
    sigma = pixels / 4
    mask_np = mask.squeeze(0).cpu().numpy()
    kernel_size = math.ceil(sigma * 1.5 + 1)
    kernel = np.ones((kernel_size, kernel_size), dtype=np.uint8)
    dilated_mask = grey_dilation(mask_np, footprint=kernel)
    dilated_mask = dilated_mask.astype(np.float32)
    dilated_mask = torch.from_numpy(dilated_mask)
    dilated_mask = torch.clamp(dilated_mask, 0.0, 1.0)
    return dilated_mask.unsqueeze(0)


def invert_m(samples):
    inverted_mask = samples.clone()
    inverted_mask = 1.0 - inverted_mask
    return inverted_mask


def blur_m(samples, pixels):
    mask = samples.squeeze(0)
    sigma = pixels / 4 
    mask_np = mask.cpu().numpy()
    blurred_mask = gaussian_filter(mask_np, sigma=sigma)
    blurred_mask = torch.from_numpy(blurred_mask).float()
    blurred_mask = torch.clamp(blurred_mask, 0.0, 1.0)
    return blurred_mask.unsqueeze(0)


def extend_imm(image, mask, optional_context_mask, extend_up_factor, extend_down_factor, extend_left_factor, extend_right_factor):
    B, H, W, C = image.shape

    new_H = int(H * (1.0 + extend_up_factor - 1.0 + extend_down_factor - 1.0))
    new_W = int(W * (1.0 + extend_left_factor - 1.0 + extend_right_factor - 1.0))

    assert new_H >= 0, f"Error: Trying to crop too much, height ({new_H}) must be >= 0"
    assert new_W >= 0, f"Error: Trying to crop too much, width ({new_W}) must be >= 0"

    expanded_image = torch.zeros(1, new_H, new_W, C, device=image.device)
    expanded_mask = torch.ones(1, new_H, new_W, device=mask.device)
    expanded_optional_context_mask = torch.zeros(1, new_H, new_W, device=optional_context_mask.device)

    up_padding = int(H * (extend_up_factor - 1.0))
    down_padding = new_H - H - up_padding
    left_padding = int(W * (extend_left_factor - 1.0))
    right_padding = new_W - W - left_padding

    slice_target_up = max(0, up_padding)
    slice_target_down = min(new_H, up_padding + H)
    slice_target_left = max(0, left_padding)
    slice_target_right = min(new_W, left_padding + W)

    slice_source_up = max(0, -up_padding)
    slice_source_down = min(H, new_H - up_padding)
    slice_source_left = max(0, -left_padding)
    slice_source_right = min(W, new_W - left_padding)

    image = image.permute(0, 3, 1, 2)  # [B, H, W, C] -> [B, C, H, W]
    expanded_image = expanded_image.permute(0, 3, 1, 2)  # [B, H, W, C] -> [B, C, H, W]

    expanded_image[:, :, slice_target_up:slice_target_down, slice_target_left:slice_target_right] = image[:, :, slice_source_up:slice_source_down, slice_source_left:slice_source_right]
    if up_padding > 0:
        expanded_image[:, :, :up_padding, slice_target_left:slice_target_right] = image[:, :, 0:1, slice_source_left:slice_source_right].repeat(1, 1, up_padding, 1)
    if down_padding > 0:
        expanded_image[:, :, -down_padding:, slice_target_left:slice_target_right] = image[:, :, -1:, slice_source_left:slice_source_right].repeat(1, 1, down_padding, 1)
    if left_padding > 0:
        expanded_image[:, :, :, :left_padding] = expanded_image[:, :, :, left_padding:left_padding+1].repeat(1, 1, 1, left_padding)
    if right_padding > 0:
        expanded_image[:, :, :, -right_padding:] = expanded_image[:, :, :, -right_padding-1:-right_padding].repeat(1, 1, 1, right_padding)

    expanded_mask[:, slice_target_up:slice_target_down, slice_target_left:slice_target_right] = mask[:, slice_source_up:slice_source_down, slice_source_left:slice_source_right]
    expanded_optional_context_mask[:, slice_target_up:slice_target_down, slice_target_left:slice_target_right] = optional_context_mask[:, slice_source_up:slice_source_down, slice_source_left:slice_source_right]

    expanded_image = expanded_image.permute(0, 2, 3, 1)  # [B, C, H, W] -> [B, H, W, C]
    image = image.permute(0, 2, 3, 1)  # [B, C, H, W] -> [B, H, W, C]

    return expanded_image, expanded_mask, expanded_optional_context_mask


def findcontextarea_m(mask):
    mask_squeezed = mask[0]  # Now shape is [H, W]
    non_zero_indices = torch.nonzero(mask_squeezed)

    H, W = mask_squeezed.shape

    if non_zero_indices.numel() == 0:
        x, y = -1, -1
        w, h = -1, -1
    else:
        y = torch.min(non_zero_indices[:, 0]).item()
        x = torch.min(non_zero_indices[:, 1]).item()
        y_max = torch.max(non_zero_indices[:, 0]).item()
        x_max = torch.max(non_zero_indices[:, 1]).item()
        w = x_max - x + 1  # +1 to include the max index
        h = y_max - y + 1  # +1 to include the max index

    context = mask[:, y:y+h, x:x+w]
    return context, x, y, w, h


def growcontextarea_m(context, mask, x, y, w, h, extend_factor):
    img_h, img_w = mask.shape[1], mask.shape[2]

    # Compute intended growth in each direction
    grow_left = int(round(w * (extend_factor-1.0) / 2.0))
    grow_right = int(round(w * (extend_factor-1.0) / 2.0))
    grow_up = int(round(h * (extend_factor-1.0) / 2.0))
    grow_down = int(round(h * (extend_factor-1.0) / 2.0))

    # Try to grow left, but clamp at 0
    new_x = x - grow_left
    if new_x < 0:
        new_x = 0

    # Try to grow up, but clamp at 0
    new_y = y - grow_up
    if new_y < 0:
        new_y = 0

    # Right edge
    new_x2 = x + w + grow_right
    if new_x2 > img_w:
        new_x2 = img_w

    # Bottom edge
    new_y2 = y + h + grow_down
    if new_y2 > img_h:
        new_y2 = img_h

    # New width and height
    new_w = new_x2 - new_x
    new_h = new_y2 - new_y

    # Extract the context
    new_context = mask[:, new_y:new_y+new_h, new_x:new_x+new_w]

    if new_h < 0 or new_w < 0:
        new_x = 0
        new_y = 0
        new_w = mask.shape[2]
        new_h = mask.shape[1]

    return new_context, new_x, new_y, new_w, new_h


def combinecontextmask_m(context, mask, x, y, w, h, optional_context_mask):
    _, x_opt, y_opt, w_opt, h_opt = findcontextarea_m(optional_context_mask)
    if x == -1:
        x, y, w, h = x_opt, y_opt, w_opt, h_opt
    if x_opt == -1:
        x_opt, y_opt, w_opt, h_opt = x, y, w, h
    if x == -1:
        return torch.zeros(1, 0, 0, device=mask.device), -1, -1, -1, -1
    new_x = min(x, x_opt)
    new_y = min(y, y_opt)
    new_x_max = max(x + w, x_opt + w_opt)
    new_y_max = max(y + h, y_opt + h_opt)
    new_w = new_x_max - new_x
    new_h = new_y_max - new_y
    combined_context = mask[:, new_y:new_y+new_h, new_x:new_x+new_w]
    return combined_context, new_x, new_y, new_w, new_h


def pad_to_multiple(value, multiple):
    return int(math.ceil(value / multiple) * multiple)


def crop_magic_im(image, mask, x, y, w, h, target_w, target_h, padding, downscale_algorithm, upscale_algorithm):
    image = image.clone()
    mask = mask.clone()
    
    # Ok this is the most complex function in this node. The one that does the magic after all the preparation done by the other nodes.
    # Basically this function determines the right context area that encompasses the whole context area (mask+optional_context_mask),
    # that is ideally within the bounds of the original image, and that has the right aspect ratio to match target width and height.
    # It may grow the image if the aspect ratio wouldn't fit in the original image.
    # It keeps track of that growing to then be able to crop the image in the stitch node.
    # Finally, it crops the context area and resizes it to be exactly target_w and target_h.
    # It keeps track of that resize to be able to revert it in the stitch node.

    # Check for invalid inputs
    if target_w <= 0 or target_h <= 0 or w == 0 or h == 0:
        return image, 0, 0, image.shape[2], image.shape[1], image, mask, 0, 0, image.shape[2], image.shape[1]

    # Step 1: Pad target dimensions to be multiples of padding
    if padding != 0:
        target_w = pad_to_multiple(target_w, padding)
        target_h = pad_to_multiple(target_h, padding)

    # Step 2: Calculate target aspect ratio
    target_aspect_ratio = target_w / target_h

    # Step 3: Grow current context area to meet the target aspect ratio
    B, image_h, image_w, C = image.shape
    context_aspect_ratio = w / h
    if context_aspect_ratio < target_aspect_ratio:
        # Grow width to meet aspect ratio
        new_w = int(h * target_aspect_ratio)
        new_h = h
        new_x = x - (new_w - w) // 2
        new_y = y

        # Adjust new_x to keep within bounds
        if new_x < 0:
            shift = -new_x
            if new_x + new_w + shift <= image_w:
                new_x += shift
            else:
                overflow = (new_w - image_w) // 2
                new_x = -overflow
        elif new_x + new_w > image_w:
            overflow = new_x + new_w - image_w
            if new_x - overflow >= 0:
                new_x -= overflow
            else:
                overflow = (new_w - image_w) // 2
                new_x = -overflow

    else:
        # Grow height to meet aspect ratio
        new_w = w
        new_h = int(w / target_aspect_ratio)
        new_x = x
        new_y = y - (new_h - h) // 2

        # Adjust new_y to keep within bounds
        if new_y < 0:
            shift = -new_y
            if new_y + new_h + shift <= image_h:
                new_y += shift
            else:
                overflow = (new_h - image_h) // 2
                new_y = -overflow
        elif new_y + new_h > image_h:
            overflow = new_y + new_h - image_h
            if new_y - overflow >= 0:
                new_y -= overflow
            else:
                overflow = (new_h - image_h) // 2
                new_y = -overflow

    # Step 4: Grow the image to accommodate the new context area
    up_padding, down_padding, left_padding, right_padding = 0, 0, 0, 0

    expanded_image_w = image_w
    expanded_image_h = image_h

    # Adjust width for left overflow (x < 0) and right overflow (x + w > image_w)
    if new_x < 0:
        left_padding = -new_x
        expanded_image_w += left_padding
    if new_x + new_w > image_w:
        right_padding = (new_x + new_w - image_w)
        expanded_image_w += right_padding
    # Adjust height for top overflow (y < 0) and bottom overflow (y + h > image_h)
    if new_y < 0:
        up_padding = -new_y
        expanded_image_h += up_padding 
    if new_y + new_h > image_h:
        down_padding = (new_y + new_h - image_h)
        expanded_image_h += down_padding

    # Step 5: Create the new image and mask
    expanded_image = torch.zeros((image.shape[0], expanded_image_h, expanded_image_w, image.shape[3]), device=image.device)
    expanded_mask = torch.ones((mask.shape[0], expanded_image_h, expanded_image_w), device=mask.device)

    # Reorder the tensors to match the required dimension format for padding
    image = image.permute(0, 3, 1, 2)  # [B, H, W, C] -> [B, C, H, W]
    expanded_image = expanded_image.permute(0, 3, 1, 2)  # [B, H, W, C] -> [B, C, H, W]

    # Ensure the expanded image has enough room to hold the padded version of the original image
    expanded_image[:, :, up_padding:up_padding + image_h, left_padding:left_padding + image_w] = image

    # Fill the new extended areas with the edge values of the image
    if up_padding > 0:
        expanded_image[:, :, :up_padding, left_padding:left_padding + image_w] = image[:, :, 0:1, left_padding:left_padding + image_w].repeat(1, 1, up_padding, 1)
    if down_padding > 0:
        expanded_image[:, :, -down_padding:, left_padding:left_padding + image_w] = image[:, :, -1:, left_padding:left_padding + image_w].repeat(1, 1, down_padding, 1)
    if left_padding > 0:
        expanded_image[:, :, up_padding:up_padding + image_h, :left_padding] = expanded_image[:, :, up_padding:up_padding + image_h, left_padding:left_padding+1].repeat(1, 1, 1, left_padding)
    if right_padding > 0:
        expanded_image[:, :, up_padding:up_padding + image_h, -right_padding:] = expanded_image[:, :, up_padding:up_padding + image_h, -right_padding-1:-right_padding].repeat(1, 1, 1, right_padding)

    # Reorder the tensors back to [B, H, W, C] format
    expanded_image = expanded_image.permute(0, 2, 3, 1)  # [B, C, H, W] -> [B, H, W, C]
    image = image.permute(0, 2, 3, 1)  # [B, C, H, W] -> [B, H, W, C]

    # Same for the mask
    expanded_mask[:, up_padding:up_padding + image_h, left_padding:left_padding + image_w] = mask

    # Record the cto values (canvas to original)
    cto_x = left_padding
    cto_y = up_padding
    cto_w = image_w
    cto_h = image_h

    # The final expanded image and mask
    canvas_image = expanded_image
    canvas_mask = expanded_mask

    # Step 6: Crop the image and mask around x, y, w, h
    ctc_x = new_x+left_padding
    ctc_y = new_y+up_padding
    ctc_w = new_w
    ctc_h = new_h

    # Crop the image and mask
    cropped_image = canvas_image[:, ctc_y:ctc_y + ctc_h, ctc_x:ctc_x + ctc_w]
    cropped_mask = canvas_mask[:, ctc_y:ctc_y + ctc_h, ctc_x:ctc_x + ctc_w]

    # Step 7: Resize image and mask to the target width and height
    # Decide which algorithm to use based on the scaling direction
    if target_w > ctc_w or target_h > ctc_h:  # Upscaling
        cropped_image = rescale_i(cropped_image, target_w, target_h, upscale_algorithm)
        cropped_mask = rescale_m(cropped_mask, target_w, target_h, upscale_algorithm)
    else:  # Downscaling
        cropped_image = rescale_i(cropped_image, target_w, target_h, downscale_algorithm)
        cropped_mask = rescale_m(cropped_mask, target_w, target_h, downscale_algorithm)

    return canvas_image, cto_x, cto_y, cto_w, cto_h, cropped_image, cropped_mask, ctc_x, ctc_y, ctc_w, ctc_h


def stitch_magic_im(canvas_image, inpainted_image, mask, ctc_x, ctc_y, ctc_w, ctc_h, cto_x, cto_y, cto_w, cto_h, downscale_algorithm, upscale_algorithm):
    canvas_image = canvas_image.clone()
    inpainted_image = inpainted_image.clone()
    mask = mask.clone()

    # Resize inpainted image and mask to match the context size
    _, h, w, _ = inpainted_image.shape
    if ctc_w > w or ctc_h > h:  # Upscaling
        resized_image = rescale_i(inpainted_image, ctc_w, ctc_h, upscale_algorithm)
        resized_mask = rescale_m(mask, ctc_w, ctc_h, upscale_algorithm)
    else:  # Downscaling
        resized_image = rescale_i(inpainted_image, ctc_w, ctc_h, downscale_algorithm)
        resized_mask = rescale_m(mask, ctc_w, ctc_h, downscale_algorithm)

    # Clamp mask to [0, 1] and expand to match image channels
    resized_mask = resized_mask.clamp(0, 1).unsqueeze(-1)  # shape: [1, H, W, 1]

    # Extract the canvas region we're about to overwrite
    canvas_crop = canvas_image[:, ctc_y:ctc_y + ctc_h, ctc_x:ctc_x + ctc_w]

    # Blend: new = mask * inpainted + (1 - mask) * canvas
    blended = resized_mask * resized_image + (1.0 - resized_mask) * canvas_crop

    # Paste the blended region back onto the canvas
    canvas_image[:, ctc_y:ctc_y + ctc_h, ctc_x:ctc_x + ctc_w] = blended

    # Final crop to get back the original image area
    output_image = canvas_image[:, cto_y:cto_y + cto_h, cto_x:cto_x + cto_w]

    return output_image


class InpaintCrop:
    """
    ComfyUI-LevelPixel
    https://github.com/LevelPixel/ComfyUI-LevelPixel

    ComfyUI-Inpaint-CropAndStitch
    https://github.com/lquesada/ComfyUI-Inpaint-CropAndStitch
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # Required inputs
                "image": ("IMAGE",),

                # Resize algorithms
                "downscale_algorithm": (["nearest", "bilinear", "bicubic", "lanczos", "box", "hamming"], {"default": "bilinear"}),
                "upscale_algorithm": (["nearest", "bilinear", "bicubic", "lanczos", "box", "hamming"], {"default": "bicubic"}),

                # Mask manipulation
                "mask_fill_holes": ("BOOLEAN", {"default": True, "tooltip": "Mark as masked any areas fully enclosed by mask."}),
                "mask_expand_pixels": ("INT", {"default": 0, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 1, "tooltip": "Expand the mask by a certain amount of pixels before processing."}),
                "mask_invert": ("BOOLEAN", {"default": False,"tooltip": "Invert mask so that anything masked will be kept."}),
                "mask_blend_pixels": ("INT", {"default": 32, "min": 0, "max": 64, "step": 1, "tooltip": "How many pixels to blend into the original image."}),
                "mask_hipass_filter": ("FLOAT", {"default": 0.1, "min": 0, "max": 1, "step": 0.01, "tooltip": "Ignore mask values lower than this value."}),

                # Context
                "context_from_mask_extend_factor": ("FLOAT", {"default": 1.2, "min": 1.0, "max": 100.0, "step": 0.01, "tooltip": "Grow the context area from the mask by a certain factor in every direction. For example, 1.5 grabs extra 50% up, down, left, and right as context."}),
                "output_padding": (["0", "8", "16", "32", "64", "128", "256", "512"], {"default": "32"}),

                # Output cropped image size
                "mode": (["none", "input size parameters", "forced size", "aspect size"], {"default": "aspect size"}),
                "target_size": ("INT", {"default": 1024, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 1}),
                "aspect_ratio_limit": ("FLOAT", {"default": 2, "min": 1, "max": 100, "step": 0.01}),
                "force_width": ("INT", {"default": 1024, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 1}),
                "force_height": ("INT", {"default": 1024, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 1})             
           },
           "optional": {
                # Optional inputs
                "mask": ("MASK",),
                "optional_context_mask": ("MASK",),

                # Custom Parameters
                "extend_factor_parameters": ("EXTENDFACTORDATA", ),
                "cropped_size_parameters": ("CROPPEDSIZEDATA", ),
           }
        }

    FUNCTION = "inpaint_crop"
    CATEGORY = "LevelPixel/Inpaint"
    DESCRIPTION = "Crops an image around a mask for inpainting, the optional context mask defines an extra area to keep for the context."

    RETURN_TYPES = ("CROPDATA", "IMAGE", "MASK")
    RETURN_NAMES = ("crop_data", "cropped_image", "cropped_mask")
 
    def inpaint_crop(self, image, downscale_algorithm, upscale_algorithm, mask_hipass_filter, mask_fill_holes, mask_expand_pixels, mask_invert, mask_blend_pixels, context_from_mask_extend_factor, output_padding, mode, target_size, aspect_ratio_limit, force_width, force_height, mask=None, optional_context_mask=None, extend_factor_parameters=None, cropped_size_parameters=None):
        if mode == "input size parameters":
            if cropped_size_parameters is not None:
                target_width, target_height, batch_mode = (
                    cropped_size_parameters["target_width"],
                    cropped_size_parameters["target_height"],
                    cropped_size_parameters["batch_mode"]
                )
                output_resize_to_target_size = True
            else:
                output_resize_to_target_size = False
                target_width = None
                target_height = None
                batch_mode = False
        elif mode == "forced size":
            output_resize_to_target_size = True
            target_width = force_width
            target_height = force_height
            batch_mode = True
        elif mode == "aspect size":
            output_resize_to_target_size = True
            new_mask = mask
            if optional_context_mask is not None:
                assert optional_context_mask.shape[1:] == new_mask.shape[1:3], f"optional_context_mask dimensions do not match mask dimensions. Expected {new_mask.shape[1:3]}, got {optional_context_mask.shape[1:]}"
                context_mask = optional_context_mask.squeeze(-1)
                new_mask = ((new_mask > 0) | (context_mask > 0)).float()     
            aspect_target_size = calculate_target_size(new_mask, target_size, aspect_ratio_limit)
            target_width, target_height = (
                    aspect_target_size["target_width"],
                    aspect_target_size["target_height"]
                )
            batch_mode = False
        else:
            output_resize_to_target_size = False
            target_width = None
            target_height = None
            batch_mode = False

        if extend_factor_parameters is not None:
            extend_up_factor, extend_down_factor, extend_left_factor, extend_right_factor = (
                extend_factor_parameters["extend_up_factor"],
                extend_factor_parameters["extend_down_factor"],
                extend_factor_parameters["extend_left_factor"],
                extend_factor_parameters["extend_right_factor"]
            )
            extend_for_outpainting = True
        else:
            extend_for_outpainting = False
            extend_up_factor = 1.0
            extend_down_factor = 1.0
            extend_left_factor = 1.0
            extend_right_factor = 1.0

        image = image.clone()
        if mask is not None:
            mask = mask.clone()
        if optional_context_mask is not None:
            optional_context_mask = optional_context_mask.clone()

        output_padding = int(output_padding)

        if image.shape[0] > 1:
            assert batch_mode, "for batch of images use Inpaint Crop only with Cropped Forsed Size Parameters node or with Forsed mode, given all images in the batch output have to be the same size"

        # When a LoadImage node passes a mask without user editing, it may be the wrong shape.
        # Detect and fix that to avoid shape mismatch errors.
        if mask is not None and (image.shape[0] == 1 or mask.shape[0] == 1 or mask.shape[0] == image.shape[0]):
            if mask.shape[1] != image.shape[1] or mask.shape[2] != image.shape[2]:
                if torch.count_nonzero(mask) == 0:
                    mask = torch.zeros((mask.shape[0], image.shape[1], image.shape[2]), device=image.device, dtype=image.dtype)

        if optional_context_mask is not None and (image.shape[0] == 1 or optional_context_mask.shape[0] == 1 or optional_context_mask.shape[0] == image.shape[0]):
            if optional_context_mask.shape[1] != image.shape[1] or optional_context_mask.shape[2] != image.shape[2]:
                if torch.count_nonzero(optional_context_mask) == 0:
                    optional_context_mask = torch.zeros((optional_context_mask.shape[0], image.shape[1], image.shape[2]), device=image.device, dtype=image.dtype)

        # If no mask is provided, create one with the shape of the image
        if mask is None:
            mask = torch.zeros_like(image[:, :, :, 0])
    
        # If there is only one image for many masks, replicate it for all masks
        if mask.shape[0] > 1 and image.shape[0] == 1:
            assert image.dim() == 4, f"Expected 4D BHWC image tensor, got {image.shape}"
            image = image.expand(mask.shape[0], -1, -1, -1).clone()

        # If there is only one mask for many images, replicate it for all images
        if image.shape[0] > 1 and mask.shape[0] == 1:
            assert mask.dim() == 3, f"Expected 3D BHW mask tensor, got {mask.shape}"
            mask = mask.expand(image.shape[0], -1, -1).clone()

        # If no optional_context_mask is provided, create one with the shape of the image
        if optional_context_mask is None:
            optional_context_mask = torch.zeros_like(image[:, :, :, 0])

        # If there is only one optional_context_mask for many images, replicate it for all images
        if image.shape[0] > 1 and optional_context_mask.shape[0] == 1:
            assert optional_context_mask.dim() == 3, f"Expected 3D BHW optional_context_mask tensor, got {optional_context_mask.shape}"
            optional_context_mask = optional_context_mask.expand(image.shape[0], -1, -1).clone()

         # Validate data
        assert image.ndimension() == 4, f"Expected 4 dimensions for image, got {image.ndimension()}"
        assert mask.ndimension() == 3, f"Expected 3 dimensions for mask, got {mask.ndimension()}"
        assert optional_context_mask.ndimension() == 3, f"Expected 3 dimensions for optional_context_mask, got {optional_context_mask.ndimension()}"
        assert mask.shape[1:] == image.shape[1:3], f"Mask dimensions do not match image dimensions. Expected {image.shape[1:3]}, got {mask.shape[1:]}"
        assert optional_context_mask.shape[1:] == image.shape[1:3], f"optional_context_mask dimensions do not match image dimensions. Expected {image.shape[1:3]}, got {optional_context_mask.shape[1:]}"
        assert mask.shape[0] == image.shape[0], f"Mask batch does not match image batch. Expected {image.shape[0]}, got {mask.shape[0]}"
        assert optional_context_mask.shape[0] == image.shape[0], f"Optional context mask batch does not match image batch. Expected {image.shape[0]}, got {optional_context_mask.shape[0]}"

        # Run for each image separately
        result_stitcher = {
            'downscale_algorithm': downscale_algorithm,
            'upscale_algorithm': upscale_algorithm,
            'blend_pixels': mask_blend_pixels,
            'canvas_to_orig_x': [],
            'canvas_to_orig_y': [],
            'canvas_to_orig_w': [],
            'canvas_to_orig_h': [],
            'canvas_image': [],
            'cropped_to_canvas_x': [],
            'cropped_to_canvas_y': [],
            'cropped_to_canvas_w': [],
            'cropped_to_canvas_h': [],
            'cropped_mask_for_blend': [],
        }
        
        result_image = []
        result_mask = []

        batch_size = image.shape[0]
        for b in range(batch_size):
            one_image = image[b].unsqueeze(0)
            one_mask = mask[b].unsqueeze(0)
            one_optional_context_mask = optional_context_mask[b].unsqueeze(0)

            outputs = self.inpaint_crop_single_image(
                one_image, downscale_algorithm, upscale_algorithm, extend_for_outpainting, extend_up_factor, 
                extend_down_factor, extend_left_factor, extend_right_factor,mask_hipass_filter, 
                mask_fill_holes, mask_expand_pixels, mask_invert, mask_blend_pixels,
                context_from_mask_extend_factor, output_resize_to_target_size, target_width, target_height,
                output_padding, one_mask, one_optional_context_mask)

            stitcher, cropped_image, cropped_mask = outputs[:3]
            for key in ['canvas_to_orig_x', 'canvas_to_orig_y', 'canvas_to_orig_w', 'canvas_to_orig_h', 'canvas_image', 'cropped_to_canvas_x', 'cropped_to_canvas_y', 'cropped_to_canvas_w', 'cropped_to_canvas_h', 'cropped_mask_for_blend']:
                result_stitcher[key].append(stitcher[key])

            cropped_image = cropped_image.clone().squeeze(0)
            result_image.append(cropped_image)
            cropped_mask = cropped_mask.clone().squeeze(0)
            result_mask.append(cropped_mask)

        result_image = torch.stack(result_image, dim=0)
        result_mask = torch.stack(result_mask, dim=0)

        return result_stitcher, result_image, result_mask,


    def inpaint_crop_single_image(self, image, downscale_algorithm, upscale_algorithm, extend_for_outpainting, extend_up_factor, extend_down_factor, extend_left_factor, extend_right_factor, mask_hipass_filter, mask_fill_holes, mask_expand_pixels, mask_invert, mask_blend_pixels, context_from_mask_extend_factor, output_resize_to_target_size, output_target_width, output_target_height, output_padding, mask, optional_context_mask):
        if mask_fill_holes:
           mask = fillholes_iterative_hipass_fill_m(mask)

        if mask_expand_pixels > 0:
            mask = expand_m(mask, mask_expand_pixels)

        if mask_invert:
            mask = invert_m(mask)

        if mask_blend_pixels > 0:
            mask = expand_m(mask, mask_blend_pixels)
            mask = blur_m(mask, mask_blend_pixels*0.5)

        if mask_hipass_filter >= 0.01:
            mask = hipassfilter_m(mask, mask_hipass_filter)
            optional_context_mask = hipassfilter_m(optional_context_mask, mask_hipass_filter)

        if extend_for_outpainting:
            image, mask, optional_context_mask = extend_imm(image, mask, optional_context_mask, extend_up_factor, extend_down_factor, extend_left_factor, extend_right_factor)

        context, x, y, w, h = findcontextarea_m(mask)
        # If no mask, mask everything for some inpainting.
        if x == -1 or w == -1 or h == -1 or y == -1:
            x, y, w, h = 0, 0, image.shape[2], image.shape[1]
            context = mask[:, y:y+h, x:x+w]

        if context_from_mask_extend_factor >= 1.01:
            context, x, y, w, h = growcontextarea_m(context, mask, x, y, w, h, context_from_mask_extend_factor)
        # If no mask, mask everything for some inpainting.
        if x == -1 or w == -1 or h == -1 or y == -1:
            x, y, w, h = 0, 0, image.shape[2], image.shape[1]
            context = mask[:, y:y+h, x:x+w]

        context, x, y, w, h = combinecontextmask_m(context, mask, x, y, w, h, optional_context_mask)
        # If no mask, mask everything for some inpainting.
        if x == -1 or w == -1 or h == -1 or y == -1:
            x, y, w, h = 0, 0, image.shape[2], image.shape[1]
            context = mask[:, y:y+h, x:x+w]

        if not output_resize_to_target_size:
            canvas_image, cto_x, cto_y, cto_w, cto_h, cropped_image, cropped_mask, ctc_x, ctc_y, ctc_w, ctc_h = crop_magic_im(image, mask, x, y, w, h, w, h, output_padding, downscale_algorithm, upscale_algorithm)
        else: # if output_resize_to_target_size:
            canvas_image, cto_x, cto_y, cto_w, cto_h, cropped_image, cropped_mask, ctc_x, ctc_y, ctc_w, ctc_h = crop_magic_im(image, mask, x, y, w, h, output_target_width, output_target_height, output_padding, downscale_algorithm, upscale_algorithm)

        # For blending, grow the mask even further and make it blurrier.
        cropped_mask_blend = cropped_mask.clone()
        if mask_blend_pixels > 0:
           cropped_mask_blend = blur_m(cropped_mask_blend, mask_blend_pixels*0.5)

        stitcher = {
            'canvas_to_orig_x': cto_x,
            'canvas_to_orig_y': cto_y,
            'canvas_to_orig_w': cto_w,
            'canvas_to_orig_h': cto_h,
            'canvas_image': canvas_image,
            'cropped_to_canvas_x': ctc_x,
            'cropped_to_canvas_y': ctc_y,
            'cropped_to_canvas_w': ctc_w,
            'cropped_to_canvas_h': ctc_h,
            'cropped_mask_for_blend': cropped_mask_blend,
        }

        return stitcher, cropped_image, cropped_mask


class InpaintStitch:
    """
    ComfyUI-LevelPixel
    https://github.com/LevelPixel/ComfyUI-LevelPixel

    ComfyUI-Inpaint-CropAndStitch
    https://github.com/lquesada/ComfyUI-Inpaint-CropAndStitch

    This node stitches the inpainted image without altering unmasked areas.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "crop_data": ("CROPDATA",),
                "inpainted_image": ("IMAGE",),
            }
        }

    CATEGORY = "LevelPixel/Inpaint"
    DESCRIPTION = "Stitches an image cropped with Inpaint Crop back into the original image"

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    FUNCTION = "inpaint_stitch"

    def inpaint_stitch(self, crop_data, inpainted_image):
        inpainted_image = inpainted_image.clone()
        results = []

        batch_size = inpainted_image.shape[0]
        assert len(crop_data['cropped_to_canvas_x']) == batch_size or len(crop_data['cropped_to_canvas_x']) == 1, "Stitch batch size doesn't match image batch size"
        override = False
        if len(crop_data['cropped_to_canvas_x']) != batch_size and len(crop_data['cropped_to_canvas_x']) == 1:
            override = True
        for b in range(batch_size):
            one_image = inpainted_image[b]
            one_stitcher = {}
            for key in ['downscale_algorithm', 'upscale_algorithm', 'blend_pixels']:
                one_stitcher[key] = crop_data[key]
            for key in ['canvas_to_orig_x', 'canvas_to_orig_y', 'canvas_to_orig_w', 'canvas_to_orig_h', 'canvas_image', 'cropped_to_canvas_x', 'cropped_to_canvas_y', 'cropped_to_canvas_w', 'cropped_to_canvas_h', 'cropped_mask_for_blend']:
                if override:
                    one_stitcher[key] = crop_data[key][0]
                else:
                    one_stitcher[key] = crop_data[key][b]
            one_image = one_image.unsqueeze(0)
            one_image, = self.inpaint_stitch_single_image(one_stitcher, one_image)
            one_image = one_image.squeeze(0)
            one_image = one_image.clone()
            results.append(one_image)

        result_batch = torch.stack(results, dim=0)

        return (result_batch,)

    def inpaint_stitch_single_image(self, stitcher, inpainted_image):
        downscale_algorithm = stitcher['downscale_algorithm']
        upscale_algorithm = stitcher['upscale_algorithm']
        canvas_image = stitcher['canvas_image']

        ctc_x = stitcher['cropped_to_canvas_x']
        ctc_y = stitcher['cropped_to_canvas_y']
        ctc_w = stitcher['cropped_to_canvas_w']
        ctc_h = stitcher['cropped_to_canvas_h']

        cto_x = stitcher['canvas_to_orig_x']
        cto_y = stitcher['canvas_to_orig_y']
        cto_w = stitcher['canvas_to_orig_w']
        cto_h = stitcher['canvas_to_orig_h']

        mask = stitcher['cropped_mask_for_blend']

        output_image = stitch_magic_im(canvas_image, inpainted_image, mask, ctc_x, ctc_y, ctc_w, ctc_h, cto_x, cto_y, cto_w, cto_h, downscale_algorithm, upscale_algorithm)

        return (output_image,)


class ExtendFactorParameters:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "extend_up_factor": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 100.0, "step": 0.01}),
                "extend_down_factor": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 100.0, "step": 0.01}),
                "extend_left_factor": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 100.0, "step": 0.01}),
                "extend_right_factor": ("FLOAT", {"default": 1.0, "min": 0.01, "max": 100.0, "step": 0.01}),
            },
        }

    RETURN_TYPES = ("EXTENDFACTORDATA",)
    RETURN_NAMES = ("extend_factor_data",)
    FUNCTION = "extend_factor_parameters"
    CATEGORY = "LevelPixel/Inpaint"
    def extend_factor_parameters(self, extend_up_factor, extend_down_factor, extend_left_factor, extend_right_factor):
        extend_factor_data = {
            "extend_up_factor": extend_up_factor,
            "extend_down_factor": extend_down_factor,
            "extend_left_factor": extend_left_factor,
            "extend_right_factor": extend_right_factor
        }
        return (extend_factor_data, )


class CroppedAspectSizeParameters:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK", ),
                "target_size": ("INT", {"default": 1024, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 1}),
                "aspect_ratio_limit": ("FLOAT", {"default": 2, "min": 1, "max": 100, "step": 0.01}),
            },
            "optional": {
                "optional_context_mask": ("MASK", ),
            }
        }

    RETURN_TYPES = ("CROPPEDSIZEDATA",)
    RETURN_NAMES = ("cropped_size_parameters",)
    FUNCTION = "cropped_aspect_size_parameters"
    CATEGORY = "LevelPixel/Inpaint"
    def cropped_aspect_size_parameters(self, mask, target_size=1024, aspect_ratio_limit=2, optional_context_mask=None):
        if optional_context_mask is not None:
            assert optional_context_mask.shape[1:] == mask.shape[1:3], f"optional_context_mask dimensions do not match mask dimensions. Expected {mask.shape[1:3]}, got {optional_context_mask.shape[1:]}"
            context_mask = optional_context_mask.squeeze(-1)
            mask = ((mask > 0) | (context_mask > 0)).float()        
        cropped_size_parameters = calculate_target_size(mask, target_size, aspect_ratio_limit)
        cropped_size_parameters["batch_mode"] = False

        return (cropped_size_parameters, )


class CroppedForsedSizeParameters:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "cropped_width": ("INT", {"default": 1024, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 1}),
                "cropped_height": ("INT", {"default": 1024, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 1}),                
            },
        }

    RETURN_TYPES = ("CROPPEDSIZEDATA",)
    RETURN_NAMES = ("cropped_size_parameters",)
    FUNCTION = "cropped_forsed_size_parameters"
    CATEGORY = "LevelPixel/Inpaint"
    def cropped_forsed_size_parameters(self, cropped_height, cropped_width):        
        target_height = cropped_height
        target_width = cropped_width
        cropped_size_parameters = {            
            "target_height": target_height,
            "target_width": target_width,
            "batch_mode": True
        }
        return (cropped_size_parameters, )


class CroppedRangedSizeParameters:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK", ),
                "min_width": ("INT", {"default": 832, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 1}),
                "min_height": ("INT", {"default": 832, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 1}),
                "max_width": ("INT", {"default": 1216, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 1}),
                "max_height": ("INT", {"default": 1216, "min": 0, "max": nodes.MAX_RESOLUTION, "step": 1})
            },
            "optional": {
                "optional_context_mask": ("MASK", ),
            }
        }

    RETURN_TYPES = ("CROPPEDSIZEDATA",)
    RETURN_NAMES = ("cropped_size_parameters",)
    FUNCTION = "cropped_ranged_size_parameters"
    CATEGORY = "LevelPixel/Inpaint"
    def cropped_ranged_size_parameters(self, mask, min_width, min_height, max_width, max_height, optional_context_mask=None):
        assert max_width >= min_width, "max_width must be greater than or equal to min_width"
        assert max_height >= min_height, "max_height must be greater than or equal to min_height"

        if optional_context_mask is not None:
            assert optional_context_mask.shape[1:] == mask.shape[1:3], f"optional_context_mask dimensions do not match mask dimensions. Expected {mask.shape[1:3]}, got {optional_context_mask.shape[1:]}"
            context_mask = optional_context_mask.squeeze(-1)
            mask = ((mask > 0) | (context_mask > 0)).float()  

        mask_height = mask.shape[1]
        mask_width = mask.shape[2]

        scale_w_min = min_width / mask_width
        scale_h_min = min_height / mask_height
        scale_w_max = max_width / mask_width
        scale_h_max = max_height / mask_height

        scale_w = (scale_w_min + scale_w_max) / 2
        scale_h = (scale_h_min + scale_h_max) / 2

        scale_w = min(scale_w_max, max(scale_w_min, scale_w))
        scale_h = min(scale_h_max, max(scale_h_min, scale_h))

        new_width = int(mask_width * scale_w)
        new_height = int(mask_height * scale_h)

        cropped_size_parameters = {            
            "target_height": new_height,
            "target_width": new_width,
            "batch_mode": False
        }
        return (cropped_size_parameters, )


class CroppedFreeSizeParameters:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mask": ("MASK", ),
                "rescale_factor": ("FLOAT", {"default": 2.00, "min": 0.01, "max": 100.0, "step": 0.01})
            },
            "optional": {
                "optional_context_mask": ("MASK", ),
            }
        }

    RETURN_TYPES = ("CROPPEDSIZEDATA",)
    RETURN_NAMES = ("cropped_size_parameters",)
    FUNCTION = "cropped_free_size_parameters"
    CATEGORY = "LevelPixel/Inpaint"
    def cropped_free_size_parameters(self, mask, rescale_factor, optional_context_mask=None):
        if optional_context_mask is not None:
            assert optional_context_mask.shape[1:] == mask.shape[1:3], f"optional_context_mask dimensions do not match mask dimensions. Expected {mask.shape[1:3]}, got {optional_context_mask.shape[1:]}"
            context_mask = optional_context_mask.squeeze(-1)
            mask = ((mask > 0) | (context_mask > 0)).float()  

        height = int(mask.shape[1] * rescale_factor)
        width = int(mask.shape[2] * rescale_factor)

        cropped_size_parameters = {            
            "target_height": height,
            "target_width": width,
            "batch_mode": False
        }
        return (cropped_size_parameters, )

NODE_CLASS_MAPPINGS = {
    "InpaintCrop|LP": InpaintCrop,
    "InpaintStitch|LP": InpaintStitch,
    "ExtendFactorParameters|LP": ExtendFactorParameters,
    "CroppedAspectSizeParameters|LP": CroppedAspectSizeParameters,
    "CroppedForsedSizeParameters|LP": CroppedForsedSizeParameters,
    "CroppedRangedSizeParameters|LP": CroppedRangedSizeParameters,
    "CroppedFreeSizeParameters|LP": CroppedFreeSizeParameters
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "InpaintCrop|LP": "Inpaint Crop [LP]",
    "InpaintStitch|LP": "Inpaint Stitch [LP]",
    "ExtendFactorParameters|LP": "Extend Factor Parameters [LP]",
    "CroppedAspectSizeParameters|LP": "Cropped Aspect Size Parameters [LP]",
    "CroppedForsedSizeParameters|LP": "Cropped Forsed Size Parameters [LP]",
    "CroppedRangedSizeParameters|LP": "Cropped Ranged Size Parameters [LP]",
    "CroppedFreeSizeParameters|LP": "Cropped Free Size Parameters [LP]"
}