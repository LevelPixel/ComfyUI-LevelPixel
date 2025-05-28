import os
import json
import shutil
import inspect
from server import PromptServer
import subprocess
import sys
from importlib import metadata

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

def get_comfy_dir(subpath=None, mkdir=False):
    dir = os.path.dirname(inspect.getfile(PromptServer))
    if subpath is not None:
        dir = os.path.join(dir, subpath)

    dir = os.path.abspath(dir)

    if mkdir and not os.path.exists(dir):
        os.makedirs(dir)
    return dir

def get_web_ext_dir():
    config = get_extension_config()
    name = config["name"]
    dir = get_comfy_dir("web/extensions/levelpixel")
    if not os.path.exists(dir):
        os.makedirs(dir)
    dir = os.path.join(dir, name)
    return dir

def is_junction(path):
    if os.name != "nt":
        return False
    try:
        return bool(os.readlink(path))
    except OSError:
        return False

def should_install_js():
    return not hasattr(PromptServer.instance, "supports") or "custom_nodes_from_web" not in PromptServer.instance.supports

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

def has_nvidia_cuda():
    try:
        output = subprocess.check_output(
            ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
            stderr=subprocess.DEVNULL,
            encoding='utf-8'
        ).strip()
        return bool(output)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def is_installed(pkg_name: str, min_version: str = '') -> bool:
    try:
        ver = metadata.version(pkg_name)
        if min_version:
            return tuple(map(int, ver.split('.'))) >= tuple(map(int, min_version.split('.')))
        return True
    except metadata.PackageNotFoundError:
        return False

def install(pkg_spec: str):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg_spec])

def uninstall(pkg: str):
    subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', '-y', pkg])

def install_onnxruntime_and_rembg():
    gpu = has_nvidia_cuda()
    print(f"Found NVIDIA GPU: {gpu}")
    if gpu:
        if is_installed('onnxruntime'):
            #uninstall("onnxruntime")
            print(f"LP >>> Your python has the 'onnxruntime' library installed, although your computer supports 'onnxruntime-gpu'.")
            print(f"LP >>> Solution: If other node packages do not use the 'onnxruntime' library, then remove the 'onnxruntime' library for your python.")
            print(f"LP >>> Otherwise the Image Remove Background node will not work effectively (the node will use the CPU instead of the GPU).")
            print(f"LP >>> Close ComfyUI and run the script at .\\ComfyUI\\custom_nodes\\ComfyUI-LevelPixel\\scripts\\remove_onnxruntime.bat")
        if not is_installed('onnxruntime-gpu'):
            install("onnxruntime-gpu>=1.22")
    else:
        if is_installed('onnxruntime-gpu'):
            #uninstall("onnxruntime-gpu")
            print(f"LP >>> Your python has the 'onnxruntime-gpu' library installed, but you don't have a GPU.")
            print(f"LP >>> Solution: If other node packages do not use the 'onnxruntime-gpu' library, then remove the 'onnxruntime-gpu' library for your python.")
            print(f"LP >>> Close ComfyUI and run the script at .\\ComfyUI\\custom_nodes\\ComfyUI-LevelPixel\\scripts\\remove_onnxruntime.bat")
        if not is_installed('onnxruntime'):
            install("onnxruntime>=1.22")

    rembg_pkg = 'rembg[gpu]' if gpu else 'rembg[cpu]'

    if not is_installed('rembg', '2.0.66'):
        install(f'{rembg_pkg}>={'2.0.66'}')

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
    install_onnxruntime_and_rembg()
    return True
