import flet as ft

from .board_component import BoardComponent
from logic import get_device_icon, SimulationManager
from .ports import Ports
from theme import ThemeManager

TM = ThemeManager()
SM = SimulationManager()


class Device(BoardComponent):
    def __init__(self, location:tuple, **kwargs):
        self.device_class = kwargs["device_class"]
        self.device_instance = self.device_class()
        super().__init__(location)
        self.bgcolor=TM.get_nested_color("device","bg")

        self.contains = ft.Container(
            top=10,bottom=0,right=10, left=10,
            content=ft.Image(src_base64=get_device_icon(self.device_class))
            )
        self.content=ft.Stack(
            [
             self.header,
             self.gesture_detection, # Must be on top
             self.ports_left,
             self.ports_right,
             self.contains
            ]
            )
        SM.add_device(self.device_instance)
        
    def _compute_ports(self):
        input_ports = [
            (name, port) for name, port in self.device_class.ports.items() if
            port.direction=="input"
            ]
        output_ports = [
            (name, port) for name, port in self.device_class.ports.items() if
            port.direction=="output"
            ]
        self.ports_left = Ports(
            height=self.height-10,
            left=0,
            ports=input_ports,
            device_instance=self.device_instance,
            parent=self
         )
        self.ports_right = Ports(
            height=self.height-10,
            right=0,
            ports=output_ports,
            device_instance=self.device_instance,
            parent=self
         )
