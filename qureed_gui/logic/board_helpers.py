import flet as ft
import importlib.resources as pkg_resources
from pathlib import Path
import base64

from qureed_project_server.server_pb2 import Device


from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler
LMH = LogicModuleHandler()

def get_device_control(device: Device) -> ft.Control:
    """
    Based on the given device, return the correct device class

    Parameters:
    -----------
        device (qureed_project_server.server_pb2.Device)

    Resturns 
    """
    from components.device import Device
    from components.variable import Variable
    from components.anchor import create_anchors
    if hasattr(device, "gui_tags"):
        if "variable" in device.gui_tags:
            return Variable
        if device.gui_name == "Anchor":
            print("Creating anchor")
            return create_anchors
    return Device

def get_device_icon(icon_abs_path):
    with open(icon_abs_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def get_device_icon_absolute_path(path):
    with open(str(path), "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
