In this Level Pixel node pack you will find:

LLM nodes - A node that generates text using the LLM model with subsequent unloading of the model from memory. Useful in those workflows where there is constant switching between different models and technologies under conditions of insufficient RAM of the video processor. 
Our LLM nodes support the latest LLM and CLIP models, and should support future ones (please let us know if any models stop working).
Most of the functionality is taken from this package - https://github.com/gokayfem/ComfyUI_VLM_nodes

LLaVa nodes - A node that generates text using the LLM model and CLIP by image and prompt with subsequent unloading of the model from memory. 
Our LLava nodes support the latest LLM models, and should support future ones (please let us know if any models stop working).
Most of the functionality is taken from this package - https://github.com/gokayfem/ComfyUI_VLM_nodes

Tag Category Filter nodes - a set of nodes that allow you to filter tags by category. There is an option to remove or leave certain categories of tags, there is a function for defining categories of all tags, there is a function for removing certain tags.
Nodes are very convenient because you can use them to remove unnecessary tags by certain categories, for example, to clean up tags and prepare them for use. You can use this to get certain prompts from an image (for example, if you need a description of only the background from an image - you can get this category of tags if you set the "background" category in Tag Category Keeper).
Most of the functionality is taken from this package - https://github.com/sugarkwork/comfyui_tag_fillter

Model Unloader nodes - a node that automatically unloads all checkpoints from memory. It must be added to a sequential chain of nodes in the workflow. There are three versions of this node: Hard (complete unloading of all checkpoints from memory, except for GGUF (not supported yet)), Middle (the same as Hard, but in the future I plan to add widgets with the ability to select a mode), Soft (without unloading checkpoints from memory, just soft cleaning of memory from garbage).

File Counter - A simple counter of files in a given folder. Convenient when you need to count the number of files in a certain format (for example, for subsequent use in loops or conditions).

Image Loader From Path - Loads images from a specific folder or path. It is convenient because you can specify both absolute paths and local paths (from the input folder), as well as the ability to sequentially receive images into the workflow at each step of the cycle by number. In addition, you can load images in batches with a certain number of loaded images in a batch. And the cherry on the cake - you can get a list of image file names at the output.

Load Image - This is a new image loading node that can retrieve the name of the files you load into your workflow.

Fast Checker Pattern - Quickly creates a background image with a checkerboard pattern according to the specified parameters for subsequent testing of images with a transparent background. You need to combine the resulting background image with your image with a transparent background in other ComfyUI nodes (at the moment there is no universal node, but perhaps we will make one in the future).

Simple Float Slider - Simple Float Slider is a handy slider from 0.0001 to 1.0000 to conveniently manage variables in your workflow. The min and max values ​​cannot be changed on the interface (but you can change these values ​​inside Python if you really need to).


(C) Level Pixel