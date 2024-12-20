import flet as ft

from .board_component import BoardComponent
from logic import get_device_icon
from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler
from .ports import Ports
from theme import ThemeManager

TM = ThemeManager()
LMH = LogicModuleHandler()

class Device(BoardComponent):
    def __init__(self, location:tuple, device_mc, device_class, **kwargs):
        self.device_mc = device_mc
        self.device_class = device_class
        self.device_instance = self.device_class(**kwargs)
        super().__init__(location)
        self.bgcolor=TM.get_nested_color("device","bg")
        self.gesture_detection.content.on_enter = self.handle_on_enter
        self.gesture_detection.content.on_exit = self.handle_on_exit
        self.gesture_detection.content.on_secondary_tap = self.handle_delete

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
        SM = LMH.get_logic(LogicModuleEnum.SIMULATION_MANAGER)
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

    def handle_on_enter(self, e):
        BM = LMH.get_logic(LogicModuleEnum.BOARD_MANAGER)
        BM.display_info(f"{self.device_class.gui_name}")

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
        
            
        
