import os
import pkg_resources
import sys
import subprocess
import importlib

def check_requirements_installed(requirements_path):
    with open(requirements_path, 'r') as f:
        requirements = [pkg_resources.Requirement.parse(line.strip()) for line in f if line.strip()]

    installed_packages = {pkg.key: pkg for pkg in pkg_resources.working_set}
    installed_packages_set = set(installed_packages.keys())
    missing_packages = []
    for requirement in requirements:
        if requirement.key not in installed_packages_set or not installed_packages[requirement.key] in requirement:
            missing_packages.append(str(requirement))

    if missing_packages:
        print(f"Missing or outdated packages: {', '.join(missing_packages)}")
        print("Installing/Updating missing packages...")
        subprocess.check_call([sys.executable, '-s', '-m', 'pip', 'install', *missing_packages])

requirements_path  = os.path.join(os.path.dirname(os.path.realpath(__file__)), "requirements.txt")
check_requirements_installed(requirements_path)

from .install_init import init, get_system_info, install_llama

system_info = get_system_info()
install_llama(system_info)
llama_cpp_agent_path  = os.path.join(os.path.dirname(os.path.realpath(__file__)), "cpp_agent_req.txt")
check_requirements_installed(llama_cpp_agent_path)

init()

node_list = [
    "convert.convert_LP",
    "image.image_utils_LP",
    "io.folder_workers_LP",
    "io.image_loaders_LP",
    "io.image_outputs_LP",
    "io.lora_tag_loader_LP",
    "io.numbers_utils_LP",
    "io.text_inputs_LP",
    "io.text_outputs_LP",
    "llm.llm_LP",
    "tags.tags_utils_LP",
    "text.text_utils_LP",
    "unloaders.model_unloaders_LP",
    "vlm.autotagger_LP",
    "unloaders.override_device_LP",
    "utils.utils_LP",
    "vlm.llava_LP",    
]

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

for module_name in node_list:
    imported_module = importlib.import_module(f".nodes.{module_name}", __name__)

    NODE_CLASS_MAPPINGS = {**NODE_CLASS_MAPPINGS, **imported_module.NODE_CLASS_MAPPINGS}
    NODE_DISPLAY_NAME_MAPPINGS = {**NODE_DISPLAY_NAME_MAPPINGS, **imported_module.NODE_DISPLAY_NAME_MAPPINGS}

WEB_DIRECTORY = "./web"
__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]