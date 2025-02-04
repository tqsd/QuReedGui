import base64
from typing import Union
from pathlib import Path

import flet as ft

from qureed_project_server.server_pb2 import Device

def get_device_control(device: Device) -> ft.Control:
    """
    Based on the given device, return the correct device class

    Parameters:
    -----------
        device (qureed_project_server.server_pb2.Device)

    Resturns:
    ---------
        device_control Union[callable, BoardComponent]
    """
    from components.device import Device
    from components.variable import Variable
    from components.anchor import create_anchors
    if hasattr(device, "gui_tags"):
        if "variable" in device.gui_tags:
            return Variable
        if device.gui_name == "Anchor":
            return create_anchors
    return Device

def get_device_icon(icon_abs_path:str) -> str:
    """
    Converts an image file at the given absolute path to a base64 encoded string. 

    Parameters:
    -----------
    icon_abs_path (str): Absolute path of the image

    Returns:
    --------
    str: The base64 encoded string representation of the image.

    Raises:
    -------
    FileNotFoundError: If the file at the specified path does not exist.
    IOError: If there is an issue reading the file.
    """
    with open(icon_abs_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")