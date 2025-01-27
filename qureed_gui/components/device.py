import flet as ft

from .board_component import BoardComponent
from logic import get_device_icon
from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler
from .ports import Ports
from theme import ThemeManager

TM = ThemeManager()
LMH = LogicModuleHandler()

class Device(BoardComponent):
    def __init__(self, location:tuple, device):
        self.device = device
        super().__init__(location, 50, 75)
        self.bgcolor=TM.get_nested_color("device","bg")
        self.gesture_detection.content.on_enter = self.handle_on_enter
        self.gesture_detection.content.on_exit = self.handle_on_exit
        self.gesture_detection.content.on_secondary_tap = self.handle_delete

        self.contains = ft.Container(
            top=10,bottom=0,right=10, left=10,
            content=ft.Image(src_base64=get_device_icon(device.icon.abs_path))
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
        
    def _compute_ports(self):
        input_ports = [
            (port.label, port) for port in self.device.ports if port.direction == "input"
        ]
        output_ports = [
            (port.label, port) for port in self.device.ports if port.direction == "output"
        ]
        print(input_ports)
        print(output_ports)
        print(self.device.ports)
        self.ports_left = Ports(
            height=self.height-10,
            left=0,
            ports=input_ports,
            parent=self
         )
        self.ports_right = Ports(
            height=self.height-10,
            right=0,
            ports=output_ports,
            parent=self
         )

    def handle_on_enter(self, e):
        BM = LMH.get_logic(LogicModuleEnum.BOARD_MANAGER)
        BM.display_info(self.device.gui_name)

    def handle_on_exit(self, e):
        BM = LMH.get_logic(LogicModuleEnum.BOARD_MANAGER)
        BM.display_info(f"")

    def handle_delete(self, e):
        CM = LMH.get_logic(LogicModuleEnum.CONNECTION_MANAGER)
        BM = LMH.get_logic(LogicModuleEnum.BOARD_MANAGER)
        SM = LMH.get_logic(LogicModuleEnum.SIMULATION_MANAGER)
        for port in [*self.ports_left.content.controls,
                     *self.ports_right.content.controls]:
            CM.disconnect(port)
        BM.remove_device(self)
        SM.remove_device(self.device_instance)
        
            
        
