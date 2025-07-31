import importlib
from .install_init import init

init()

node_list = [
    "convert.convert_LP",
    "image.image_utils_LP",
    "image.inpaint_crop_stitch_LP",
    "io.iterators_LP",
    "io.folder_workers_LP",
    "io.image_loaders_LP",
    "io.image_outputs_LP",
    "io.lora_tag_loader_LP",
    "io.numbers_utils_LP",
    "io.text_inputs_LP",
    "io.text_outputs_LP",
    "tags.tags_utils_LP",
    "text.text_utils_LP",
    "unloaders.model_unloaders_LP",
    "unloaders.override_device_LP",
    "utils.utils_LP",
]

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

for module_name in node_list:
    imported_module = importlib.import_module(f".nodes.{module_name}", __name__)

    NODE_CLASS_MAPPINGS = {**NODE_CLASS_MAPPINGS, **imported_module.NODE_CLASS_MAPPINGS}
    NODE_DISPLAY_NAME_MAPPINGS = {**NODE_DISPLAY_NAME_MAPPINGS, **imported_module.NODE_DISPLAY_NAME_MAPPINGS}

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]