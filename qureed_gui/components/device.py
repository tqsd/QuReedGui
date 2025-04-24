import uuid
import flet as ft

from .board_component import BoardComponent
from qureed_gui.logic import get_device_icon
from qureed_gui.logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler
from .ports import Ports
from theme import ThemeManager

from qureed_project_server import server_pb2

TM = ThemeManager()
LMH = LogicModuleHandler()

class Device(BoardComponent):
    def __init__(self, location:tuple, device: server_pb2.Device):
        self.device = server_pb2.Device()
        self.device.CopyFrom(device)
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

    def register_device_with_server(self) -> bool:
        if not self.device.uuid:
            PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
            SvM = LMH.get_logic(LogicModuleEnum.SERVER_MANAGER)

            uid = uuid.uuid4()
            self.device.uuid = str(uid)
            response = SvM.add_device(self.device)
            if response.status == "failure":
                PM.display_message(f"Device (self.device.module_class) not created: {response.message}")
                return False
            return True
            #self.device.uuid = response.device_uuid
        
    def _compute_ports(self):
        input_ports = [
            (port.label, port) for port in self.device.ports if port.direction == "input"
        ]
        output_ports = [
            (port.label, port) for port in self.device.ports if port.direction == "output"
        ]
        max_ports = max(len(input_ports), len(output_ports))
        self.height = max(self.height, max_ports * 20)
        self.ports_left = Ports(
            height=self.height-10,
            left=0,
            ports=input_ports,
            parent=self,
            device=self.device
         )
        self.ports_right = Ports(
            height=self.height-10,
            right=0,
            ports=output_ports,
            parent=self,
            device=self.device,
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
        for port in [*self.ports_left.content.controls,
                     *self.ports_right.content.controls]:
            CM.disconnect(port)
        BM.remove_device(self)
        
            
        
