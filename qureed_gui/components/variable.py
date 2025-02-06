import flet as ft
import uuid
from google.protobuf.json_format import MessageToDict
from .board_component import BoardComponent

from .ports import Ports
from theme import ThemeManager
from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler

TM = ThemeManager()
LMH = LogicModuleHandler()

class Variable(BoardComponent):
    def __init__(self, location:tuple, device):
        self.device = device
        super().__init__(location,50,50)

        self.gesture_detection.content.on_enter = self.handle_on_enter
        self.gesture_detection.content.on_exit = self.handle_on_exit
        self.gesture_detection.content.on_secondary_tap = self.handle_delete

        self.properties = MessageToDict(device.device_properties.properties)
        if "value" not in self.properties["value"]:
            self.properties["value"]["value"] = ""

        self.contains = ft.Container(
            bgcolor="#7ead79",
            top=15,bottom=8,right=10,left=10,
            border_radius=3,
            margin=3,
            padding=3,
            content=ft.Text(
                str(self.properties["value"]["value"]),
                font_family="Courier New",
                size=12
                )
            )

        self.width = 40 + len(self.contains.content.value)*9
        if self.width < 70:
            self.width=70
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
            device=self.device
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

    def update(self):
        self.width = 40 + len(self.contains.content.value)*9
        if self.width < 70:
            self.width=70
        super().update()

    def register_device_with_server(self):
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

    def update_properties_hook(self):
        self.properties = MessageToDict(self.device.device_properties.properties)
        self.contains.content.value=str(self.properties["value"]["value"])
        self.update()
