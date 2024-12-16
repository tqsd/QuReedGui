import importlib.resources as pkg_resources
from pathlib import Path
import base64

from .project import ProjectManager
PM = ProjectManager()

def get_device_control(device_class):
    """
    Based on the given class flet control is returned
    """
    from components.device import Device
    if hasattr(device_class, "gui_tags"):
        if isinstance(device_class.gui_tags, list):
            if "variable" in device_class.gui_tags:
                return None
    return Device

def get_device_icon(device):
    if "venv" in device.gui_icon or "custom" in device.gui_icon:
        print(PM.path)
        print(device.gui_icon)
        path = str(Path(PM.path) / str(device.gui_icon[1:]))
        print(path)
    else:
        path = pkg_resources.files("qureed.gui.assets")
        path = str(path / device.gui_icon)
    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def get_device_icon_absolute_path(path):
    with open(str(path), "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
