"""
A base component, which is the base for the other components
"""

import flet as ft

from qureed_project_server import server_pb2

from .ports import Ports
from theme import ThemeManager
from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler

TM = ThemeManager()
LMH = LogicModuleHandler()

class BoardComponent(ft.Container):
    def __init__(self, location:tuple, height, width):
        super().__init__()
        self.top=location[1]
        self.left=location[0]
        self.height = height
        self.width = width
        self.border_radius=4
        self.bgcolor=TM.get_nested_color("board_component", "bg")
        self._compute_ports()
        self.contains = ft.Container(
            top=10,bottom=0,right=10, left=10,
            )
        

        self.header = ft.Container(
            top=0, right=0, left=0, height=10,
            bgcolor=TM.get_nested_color("device", "header")
            )
        self.gesture_detection = ft.Container(
            top=0, right=0, left=0, height=10,
            content = ft.GestureDetector(
                drag_interval=1,
                on_vertical_drag_update=self.handle_device_move,
                on_tap=self.handle_select,
                )
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
        self.ports_left = Ports(height = self.height-10, left=0, parent=self)
        self.ports_right = Ports(height = self.height-10, right=0, parent=self)

    def device_move(self, e):
        self.top += e.delta_y
        self.left += e.delta_x
        self.top = max(self.top, 0)
        self.left = max(self.left, 0)
        for port in [*self.ports_left.content.controls, *self.ports_right.content.controls]:
            if port.connection:
                port.connection.move(port, e.delta_x, e.delta_y)
        self.update()

    def handle_device_move(self, e):
        SM = LMH.get_logic(LogicModuleEnum.SELECTION_MANAGER)
        if self not in SM.selected_components:
            SM.deselect_all()
        if SM.selected_components == []:
            self.device_move(e)
        for bc in SM.selected_components:
            bc.device_move(e)

    def handle_select(self, e):
        SM = LMH.get_logic(LogicModuleEnum.SELECTION_MANAGER)
        SM.new_selection([self])
        self.select()

    def select(self):
        self.border=ft.border.all(1, "yellow")
        self.update()

    def deselect(self):
        self.border = None
        self.update()


    def update_properties(self, properties:dict[str, dict]):
        if hasattr(self, "device"):
            device_copy = type(self.device)()
            device_copy.CopyFrom(self.device)
            properties_msg = server_pb2.DeviceProperties(
                properties=properties
                )
            device_copy.device_properties.CopyFrom(properties_msg)
            SvM = LMH.get_logic(LogicModuleEnum.SERVER_MANAGER)
            response = SvM.update_device_properties(device_copy)
            print(response)
            if response.status == "success":
                self.device = device_copy
            if hasattr(self, "update_properties_hook"):
                self.update_properties_hook()

            
