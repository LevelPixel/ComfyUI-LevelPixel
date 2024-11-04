import os
import json
import shutil
import platform
import subprocess
import sys
import importlib.util
import re
import torch
import inspect
import packaging.tags
from requests import get
from server import PromptServer

def get_python_version():
    version_match = re.match(r"3\.(\d+)", platform.python_version())
    if version_match:
        return "3" + version_match.group(1)
    else:
        return None

def get_system_info():
    system_info = {
        'gpu': False,
        'cuda_version': None,
        'python_version': get_python_version(),
        'os': platform.system(),
        'os_bit': platform.architecture()[0].replace("bit", ""),
        'platform_tag': None,
    }

    # Check for NVIDIA GPU and CUDA version
    if importlib.util.find_spec('torch'): 
        system_info['gpu'] = torch.cuda.is_available()
        if system_info['gpu']:
            system_info['cuda_version'] = "cu" + torch.version.cuda.replace(".", "").strip()
    
    # Determine the platform tag
    if importlib.util.find_spec('packaging.tags'):        
        system_info['platform_tag'] = next(packaging.tags.sys_tags()).platform

    return system_info

def latest_lamacpp():
    try:        
        response = get("https://api.github.com/repos/abetlen/llama-cpp-python/releases/latest")
        return response.json()["tag_name"].replace("v", "")
    except Exception:
        return "0.2.20"

def install_package(package_name, custom_command=None):
    if not package_is_installed(package_name):
        print(f"Installing {package_name}...")
        command = [sys.executable, "-m", "pip", "install", package_name, "--no-cache-dir"]
        if custom_command:
            command += custom_command.split()
        subprocess.check_call(command)
    else:
        print(f"{package_name} is already installed.")

def package_is_installed(package_name):
    return importlib.util.find_spec(package_name) is not None

def install_llama(system_info):
    imported = package_is_installed("llama-cpp-python") or package_is_installed("llama_cpp")
    if not imported:
        lcpp_version = latest_lamacpp()
        base_url = "https://github.com/abetlen/llama-cpp-python/releases/download/v"

        if system_info['gpu']:
            cuda_version = system_info['cuda_version']
            custom_command =  f"--force-reinstall --no-deps --index-url=https://abetlen.github.io/llama-cpp-python/whl/{cuda_version}"
        else:
            custom_command = f"{base_url}{lcpp_version}/llama_cpp_python-{lcpp_version}-{system_info['platform_tag']}.whl"
        install_package("llama-cpp-python", custom_command=custom_command)

config = None

def is_logging_enabled():
    config = get_extension_config()
    if "logging" not in config:
        return False
    return config["logging"]

def log(message, type=None, always=False, name=None):
    if not always and not is_logging_enabled():
        return

    if type is not None:
        message = f"[{type}] {message}"

    if name is None:
        name = get_extension_config()["name"]

    print(f"(levelpixel-nodes:{name}) {message}")

def get_ext_dir(subpath=None, mkdir=False):
    dir = os.path.dirname(__file__)
    if subpath is not None:
        dir = os.path.join(dir, subpath)

    dir = os.path.abspath(dir)

    if mkdir and not os.path.exists(dir):
        os.makedirs(dir)
    return dir

def get_extension_config(reload=False):
    global config
    if reload == False and config is not None:
        return config

    config_path = get_ext_dir("levelpixel.json")
    default_config_path = get_ext_dir("levelpixel.default.json")
    if not os.path.exists(config_path):
        if os.path.exists(default_config_path):
            shutil.copy(default_config_path, config_path)
            if not os.path.exists(config_path):
                log(f"Failed to create config at {config_path}", type="ERROR", always=True, name="???")
                print(f"Extension path: {get_ext_dir()}")
                return {"name": "Unknown", "version": -1}
    
        else:
            log("Missing levelpixel.default.json, this extension may not work correctly. Please reinstall the extension.",
                type="ERROR", always=True, name="???")
            print(f"Extension path: {get_ext_dir()}")
            return {"name": "Unknown", "version": -1}

    with open(config_path, "r") as f:
        config = json.loads(f.read())
    return config

def link_js(src, dst):
    src = os.path.abspath(src)
    dst = os.path.abspath(dst)
    if os.name == "nt":
        try:
            import _winapi
            _winapi.CreateJunction(src, dst)
            return True
        except:
            pass
    try:
        os.symlink(src, dst)
        return True
    except:
        import logging
        logging.exception('')
        return False

def is_junction(path):
    if os.name != "nt":
        return False
    try:
        return bool(os.readlink(path))
    except OSError:
        return False

def install_js():
    src_dir = get_ext_dir("web/js")
    if not os.path.exists(src_dir):
        log("No JS")
        return

    should_install = should_install_js()
    if should_install:
        log("it looks like you're running an old version of ComfyUI that requires manual setup of web files, it is recommended you update your installation.", "warning", True)
    dst_dir = get_web_ext_dir()
    linked = os.path.islink(dst_dir) or is_junction(dst_dir)
    if linked or os.path.exists(dst_dir):
        if linked:
            if should_install:
                log("JS already linked")
            else:
                os.unlink(dst_dir)
                log("JS unlinked, PromptServer will serve extension")
        elif not should_install:
            shutil.rmtree(dst_dir)
            log("JS deleted, PromptServer will serve extension")
        return
    
    if not should_install:
        log("JS skipped, PromptServer will serve extension")
        return
    
    if link_js(src_dir, dst_dir):
        log("JS linked")
        return

    log("Copying JS files")
    shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)

def get_web_ext_dir():
    config = get_extension_config()
    name = config["name"]
    dir = get_comfy_dir("web/extensions/levelpixel")
    if not os.path.exists(dir):
        os.makedirs(dir)
    dir = os.path.join(dir, name)
    return dir

def get_comfy_dir(subpath=None, mkdir=False):
    dir = os.path.dirname(inspect.getfile(PromptServer))
    if subpath is not None:
        dir = os.path.join(dir, subpath)

    dir = os.path.abspath(dir)

    if mkdir and not os.path.exists(dir):
        os.makedirs(dir)
    return dir

def should_install_js():
    return not hasattr(PromptServer.instance, "supports") or "custom_nodes_from_web" not in PromptServer.instance.supports


def init(check_imports=None):
    log("Init")

    if check_imports is not None:
        import importlib.util
        for imp in check_imports:
            spec = importlib.util.find_spec(imp)
            if spec is None:
                log(f"{imp} is required, please check requirements are installed.",
                    type="ERROR", always=True)
                return False

    install_js()
    return True
