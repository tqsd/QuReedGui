import importlib.resources as pkg_resources
from pathlib import Path
import base64

from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler
LMH = LogicModuleHandler()

def get_device_control(device_class):
    """
    Based on the given class flet control is returned
    """
    from components.device import Device
    from components.variable import Variable
    from components.anchor import create_anchors
    if hasattr(device_class, "gui_tags"):
        if isinstance(device_class.gui_tags, list):
            if "variable" in device_class.gui_tags:
                return Variable
            if device_class.gui_name == "Anchor":
                print("Creating anchor")
                return create_anchors
    return Device

def get_device_icon(device):
    PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
    CL = LMH.get_logic(LogicModuleEnum.CLASS_LOADER)
    if "venv" in device.gui_icon or "custom" in device.gui_icon:
        path = str(Path(PM.path) / str(device.gui_icon[1:]))
    else:
        path = CL.get_project_site_packages_dir()
        path = path / "qureed" / "assets"
        path = str(path / device.gui_icon)
        print(path)

    with open(path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def get_device_icon_absolute_path(path):
    with open(str(path), "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
