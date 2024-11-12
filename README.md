## Level Pixel nodes for ComfyUI

![banner_LevelPixel_with_logo](https://github.com/user-attachments/assets/ef79f2c9-04fb-485f-aba5-6cd00cb14d8c)

In this Level Pixel node pack you will find:

LLM nodes, LLaVa nodes, Image Remove Background based on RemBG, Tag Category Filter nodes, Model Unloader nodes, Autotagger, File Counter, Image Loader From Path, Load Image, Fast Checker Pattern, Simple Float Slider.

## Contacts:

For cooperation, suggestions and ideas you can write to email:
levelpixel.dev@gmail.com

# Installation:

## Installation Using ComfyUI Manager (recommended):

Install [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager) and do steps introduced there to install this repo 'ComfyUI-LevelPixel'.
The nodes of the current package will be updated automatically when you click "Update ALL" in ComfyUI Manager.

## Alternative installation:

Clone the repository:
`git clone https://github.com/LevelPixel/ComfyUI-LevelPixel.git`
to your ComfyUI `custom_nodes` directory

The script will then automatically install all custom scripts and nodes.
It will attempt to use symlinks and junctions to prevent having to copy files and keep them up to date.

- For uninstallation:
  - Delete the cloned repo in `custom_nodes`
  - Ensure `web/extensions/levelpixel` has also been removed
- For manual update:
  - Navigate to the cloned repo e.g. `custom_nodes/ComfyUI-LevelPixel`
  - `git pull`

# Features

All nodes Level Pixel:

<img width="1173" alt="level-pixel-nodes" src="https://github.com/user-attachments/assets/60623f84-b02a-4749-9e2c-4ab60431b383">

## LLM nodes

A node that generates text using the LLM model with subsequent unloading of the model from memory. Useful in those workflows where there is constant switching between different models and technologies under conditions of insufficient RAM of the video processor.

Our LLM nodes support the latest LLM and CLIP models, and should support future ones (please let us know if any models stop working).

The core functionality is taken from [ComfyUI_VLM_nodes](https://github.com/gokayfem/ComfyUI_VLM_nodes) and belongs to its authors.

## LLaVa nodes

A node that generates text using the LLM model and CLIP by image and prompt with subsequent unloading of the model from memory.

Our LLava nodes support the latest LLM models, and should support future ones (please let us know if any models stop working).

The core functionality is taken from [ComfyUI_VLM_nodes](https://github.com/gokayfem/ComfyUI_VLM_nodes) and belongs to its authors.

## Image Remove Background based on RemBG

A more improved version of rembg nodes for ComfyUI with an extended list of models.

The core functionality is taken from [RemBG nodes for ComfyUI](https://github.com/Loewen-Hob/rembg-comfyui-node-better) and belongs to its authors.

## Autotagger

An image autotagger that creates highly relevant tags using fast and ultra-accurate, highly specialized models. More diverse models are planned to be added to the list of models in the future.

This node allows it to be used in cycles and conditions (in places where it is not necessary to execute this node according to the specified conditions), since it is not a node with mandatory execution.

The core functionality is taken from [ComfyUI-WD14-Tagger](https://github.com/pythongosssss/ComfyUI-WD14-Tagger) and belongs to its authors.

## Tag Category Filter nodes

A set of nodes that allow you to filter tags by category. There is an option to remove or leave certain categories of tags, there is a function for defining categories of all tags, there is a function for removing certain tags.

Nodes are very convenient because you can use them to remove unnecessary tags by certain categories, for example, to clean up tags and prepare them for use. You can use this to get certain prompts from an image (for example, if you need a description of only the background from an image - you can get this category of tags if you set the "background" category in Tag Category Keeper).

The core functionality is taken from [comfyui_tag_fillter](https://github.com/sugarkwork/comfyui_tag_fillter) and belongs to its authors.

## Model Unloader nodes

A node that automatically unloads all checkpoints from memory. It must be added to a sequential chain of nodes in the workflow. There are three versions of this node: Hard (complete unloading of all checkpoints from memory, except for GGUF (not supported yet)), Middle (the same as Hard, but in the future I plan to add widgets with the ability to select a mode), Soft (without unloading checkpoints from memory, just soft cleaning of memory from garbage).

## File Counter

A simple counter of files in a given folder. Convenient when you need to count the number of files in a certain format (for example, for subsequent use in loops or conditions).

## Image Loader From Path

Loads images from a specific folder or path. It is convenient because you can specify both absolute paths and local paths (from the input folder), as well as the ability to sequentially receive images into the workflow at each step of the cycle by number. In addition, you can load images in batches with a certain number of loaded images in a batch. And the cherry on the cake - you can get a list of image file names at the output.

## Load Image

This is a new image loading node that can retrieve the name of the files you load into your workflow.

## Fast Checker Pattern

Quickly creates a background image with a checkerboard pattern according to the specified parameters for subsequent testing of images with a transparent background. You need to combine the resulting background image with your image with a transparent background in other ComfyUI nodes (at the moment there is no universal node, but perhaps we will make one in the future).

## Simple Float Slider

Simple Float Slider is a handy slider from 0.0 to 1.0 to conveniently manage variables in your workflow. The min and max values cannot be changed on the interface (but you can change these values inside Python if you really need to).
The pack contains two additional sliders - "Simple Float Slider - Tenths Step" and "Simple Float Slider - Hundredths Step" for working with more precisely defined values in tenths and hundredths (work correctly only if you have not changed the value of "Float widget rounding decimal places" in the ComfyUI settings. If you have changed it, then return the value to 0).

The core functionality is taken from [comfyui-mixlab-nodes](https://github.com/shadowcz007/comfyui-mixlab-nodes) and belongs to its authors.

## Other nodes

There are a few more nodes in this package that have some unusual uses:

* Preview Image Bridge - only output an image to the screen if there is a connection to the output node. Useful in loops and conditions where the execution of this node is not required due to current conditions (variables).
* Show Text Bridge - only output text to the screen if there is a connection to the output node. Useful in loops and conditions where the execution of this node is not required due to current conditions (variables).
* Show Text - output text to the screen with mandatory execution. The node is executed in any case, whether the output is connected or not.

# Credits

ComfyUI/[ComfyUI](https://github.com/comfyanonymous/ComfyUI) - A powerful and modular stable diffusion GUI.

VLM nodes for ComfyUI/[ComfyUI_VLM_nodes](https://github.com/gokayfem/ComfyUI_VLM_nodes) - Best VLM nodes for ComfyUI.

Tag Filter nodes for ComfyUI/[comfyui_tag_fillter](https://github.com/sugarkwork/comfyui_tag_fillter) - Best tag filter by category nodes for ComfyUI.

RemBG nodes for ComfyUI/[rembg-comfyui-node](https://github.com/Loewen-Hob/rembg-comfyui-node-better) - RemBG nodes for ComfyUI.

RemBG software package/[rembg](https://github.com/danielgatis/rembg) - Best software to remove background for any object in the picture.

# License

Copyright (c) 2024-present Level Pixel

Licensed under Apache License
