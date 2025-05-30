## Level Pixel nodes for ComfyUI

![banner_LevelPixel_with_logo](https://github.com/user-attachments/assets/ef79f2c9-04fb-485f-aba5-6cd00cb14d8c)

The purpose of this package is to collect the most necessary and atomic nodes for working with any tasks, adapted for use in cycles and conditions. The package of nodes is aimed at those users who need all the basic things to create multitasking complex workflows using multimodal neural models and software solutions.

*Our dream is to see object-oriented programming in ComfyUI. We will try to get closer to it.*

**In this Level Pixel node pack you will find:**
Image Remove Background based on RemBG, Tag Category Filter nodes, Model Unloader nodes, File Counter, Image Loader From Path, Load Image, Fast Checker Pattern, Float Slider, Load LoRA Tag, Image Overlay, Conversion nodes.

Recommend that you install the advanced node package from Level Pixel Advanced for Multimodal Generators, Qwen2.5-VL gguf, LLM, VLM, RAM, Autotaggers, RemBG nodes:\
[https://github.com/LevelPixel/ComfyUI-LevelPixel-Advanced](https://github.com/LevelPixel/ComfyUI-LevelPixel-Advanced)

The official repository of the current node package is located at this link:\
[https://github.com/LevelPixel/ComfyUI-LevelPixel](https://github.com/LevelPixel/ComfyUI-LevelPixel)

## Contacts:

For cooperation, suggestions and ideas you can write to email:
levelpixel.dev@gmail.com

# Installation:

## Installation package using ComfyUI Manager (recommended):

Install [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager) and do steps introduced there to install this repo 'ComfyUI-LevelPixel'.
The nodes of the current package will be updated automatically when you click "Update ALL" in ComfyUI Manager.

## Alternative installation package:

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

All nodes Level Pixel in this package:

<img width="1171" alt="level-pixel-nodes_1" src="https://github.com/user-attachments/assets/10fa67be-766c-4936-9fbd-fdf3830cd290">
<img width="1171" alt="level-pixel-nodes_2" src="https://github.com/user-attachments/assets/f9c1e2ab-1bfc-4f4d-9fd5-b4c8c00e4423">

## Tag Category Filter nodes

A set of nodes that allow you to filter tags by category. There is an option to remove or leave certain categories of tags, there is a function for defining categories of all tags, there is a function for removing certain tags.

Nodes are very convenient because you can use them to remove unnecessary tags by certain categories, for example, to clean up tags and prepare them for use. You can use this to get certain prompts from an image (for example, if you need a description of only the background from an image - you can get this category of tags if you set the "background" category in Tag Category Keeper).

The core functionality is taken from [comfyui_tag_fillter](https://github.com/sugarkwork/comfyui_tag_fillter) and belongs to its authors.

## Load LoRA Tag

LoRA loader from text in the style of Automatic1111 and Forge WebUI. For this version of loader, text output for errors when loading LoRA has been added as widget on node.

The core functionality is taken from [comfyui_lora_tag_loader](https://github.com/badjeff/comfyui_lora_tag_loader) and belongs to its authors.

## Model Unloader nodes

A node that automatically unloads all checkpoints from memory. It must be added to a sequential chain of nodes in the workflow. There are three versions of this node: Hard (complete unloading of all checkpoints from memory, except for GGUF (not supported yet)), Middle (the same as Hard, but in the future I plan to add widgets with the ability to select a mode), Soft (without unloading checkpoints from memory, just soft cleaning of memory from garbage).

## File Counter

A simple counter of files in a given folder. Convenient when you need to count the number of files in a certain format (for example, for subsequent use in loops or conditions).

## Image Loader From Path

Loads images from a specific folder or path. It is convenient because you can specify both absolute paths and local paths (from the input folder), as well as the ability to sequentially receive images into the workflow at each step of the cycle by number. In addition, you can load images in batches with a certain number of loaded images in a batch. And the cherry on the cake - you can get a list of image file names at the output.

## Load Image

This is a new image loading node that can retrieve the name of the files you load into your workflow.

## Image Overlay

A node that allows you to overlay one image on another with the ability to specify a mask. In this package, Image Overlay has an extended range of specified sizes for the final image, and also has another standard image size.

The core functionality is taken from [efficiency-nodes-comfyui](https://github.com/jags111/efficiency-nodes-comfyui) and belongs to its authors.

## Fast Checker Pattern

Quickly creates a background image with a checkerboard pattern according to the specified parameters for subsequent testing of images with a transparent background. You need to combine the resulting background image with your image with a transparent background in other ComfyUI nodes (at the moment there is no universal node, but perhaps we will make one in the future).

## Simple Float Slider

Simple Float Slider is a handy slider from 0.0 to 1.0 to conveniently manage variables in your workflow. The min and max values cannot be changed on the interface (but you can change these values inside Python if you really need to).
The pack contains two additional sliders - "Simple Float Slider - Tenths Step" and "Simple Float Slider - Hundredths Step" for working with more precisely defined values in tenths and hundredths (work correctly only if you have not changed the value of "Float widget rounding decimal places" in the ComfyUI settings. If you have changed it, then return the value to 0).

The core functionality is taken from [comfyui-mixlab-nodes](https://github.com/shadowcz007/comfyui-mixlab-nodes) and belongs to its authors.

## Other nodes

There are a few more nodes in this package that have some unusual uses:

* Google Translate
* Count Objects - counts the number of objects that were fed to the input (this can be a list or one single object). Accepts any type of input.
* Preview Image Bridge - only output an image to the screen if there is a connection to the output node. Useful in loops and conditions where the execution of this node is not required due to current conditions (variables).
* Show Text Bridge - only output text to the screen if there is a connection to the output node. Useful in loops and conditions where the execution of this node is not required due to current conditions (variables).
* Show Text - output text to the screen with mandatory execution. The node is executed in any case, whether the output is connected or not.
* Text - a simple node for entering multi-line text (similar to Prompt from other node packages).
* String - a simple node for entering single-line text (similar to String from other node packages).
* Conversion nodes - a variety of different nodes that allow you to transform different types of variables into other variables. The big difference from other current node packages is that they cover a larger number of variable types. Conversion nodes: StringToFloat, StringToInt, StringToBool, StringToNumber, StringToCombo, IntToString, FloatToString, BoolToString, FloatToInt, IntToFloat, IntToBool, BoolToInt.
* Pipe - extremely useful and extremely easy to use node for building a beautiful pipeline. One Pipe node is both an input and an output, so I recommend using it where it is absolutely necessary. In addition, there are standard Pipe In and Pipe Out, if you want aesthetics.

## About LLM, LLaVa, VLM, Autotagger, RAM nodes

All LLM nodes have been moved to a separate ComfyUI Level Pixel Advanced node package, as such nodes require the skill of configuring programs, drivers and libraries for correct use, as well as due to constant changes and other frequent changes that may affect all other functionality of the current node package. In addition, some technologies based on neural networks tend to quickly become obsolete (currently in 1-2 years), so they will be in a separate ComfyUI Level Pixel Advanced package.

Link to Level Pixel Advanced nodes with LLM nodes:\ [https://github.com/LevelPixel/ComfyUI-LevelPixel-Advanced](https://github.com/LevelPixel/ComfyUI-LevelPixel-Advanced)

# Update History

27-05-2025 - The node package is divided into two independent packages - a package with logical nodes [ComfyUI-LevelPixel](https://github.com/LevelPixel/ComfyUI-LevelPixel) and a package with wrapper-nodes for neural models [ComfyUI-LevelPixel-Advanced](https://github.com/LevelPixel/ComfyUI-LevelPixel-Advanced)

The license for this package has been changed from Apache 2.0 to GNU GPLv3

# Credits

ComfyUI/[ComfyUI](https://github.com/comfyanonymous/ComfyUI) - A powerful and modular stable diffusion GUI.

Tag Filter nodes for ComfyUI/[comfyui_tag_fillter](https://github.com/sugarkwork/comfyui_tag_fillter) - Best tag filter by category nodes for ComfyUI.

Load LoRA Tag node for ComfyUI/[comfyui_lora_tag_loader](https://github.com/badjeff/comfyui_lora_tag_loader) - Thanks to the author for this great node for LoRAs!

Efficiency-nodes-comfyui/[efficiency-nodes-comfyui](https://github.com/jags111/efficiency-nodes-comfyui) - Thanks for Image Overlay!

# License

Copyright (c) 2024-present [Level Pixel](https://github.com/LevelPixel)

Licensed under GNU GPLv3
