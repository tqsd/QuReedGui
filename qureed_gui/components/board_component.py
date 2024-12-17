"""
A base component, which is the base for the other components
"""

import flet as ft

from .ports import Ports
from theme import ThemeManager

TM = ThemeManager()

class BoardComponent(ft.Container):
    def __init__(self, location:tuple):
        super().__init__()
        self.top=location[1]
        self.left=location[0]
        self.height=50
        self.width=75
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
                on_vertical_drag_update=self.handle_device_move
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

    def handle_device_move(self, e):
        self.top += e.delta_y
        self.left += e.delta_x
        self.top = max(self.top, 0)
        self.left = max(self.left, 0)
        for port in [*self.ports_left.content.controls, *self.ports_right.content.controls]:
            if port.connection:
                port.connection.move(port, e.delta_x, e.delta_y)
        self.update()
