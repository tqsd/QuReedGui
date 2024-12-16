import inspect

import flet as ft

from theme import ThemeManager
from logic import BoardManager, ConnectionManager

TM = ThemeManager()
BM = BoardManager()
CM = ConnectionManager()

class Ports(ft.Container):
    def __init__(self, height, left=None, right=None, ports=None, device_instance=None, parent=None):
        super().__init__()
        self._parent = parent
        self.top=10
        self.width=10
        self.height=height
        self.ports = ports if ports else []
        self.device_instance=device_instance

        if left is not None:
            self.left=left
            self.direction="IN"
        elif right is not None:
            self.right=right
            self.direction="OUT"

        spacing = (self.height - len(self.ports)*10)/max(len(self.ports)*2,1)
        controls = []
        for i,port in enumerate(self.ports):
            controls.append(Port(
                top=i*(10+2*spacing) + spacing,
                port=port,
                ports=self,
                direction=self.direction,
                device_instance=self.device_instance,
            ))
        
        self.content = ft.Stack(
            controls=controls)

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        pass

    @property
    def location(self):
        y=self.parent.top + 10
        if self.direction == "IN":
            x=self.parent.left + 5
        else:
            x=self.parent.left + self.parent.width-5
        return (x,y)

class Port(ft.Container):
    def __init__(self, top, port, ports, direction, device_instance):
        super().__init__()
        self.top = top
        self.left = 0
        self.width = 10
        self.height = 10
        self.ports = ports
        self.port_label = port[0]
        self.port_type = port[1]
        self.device_instance = device_instance
        self.connected = False
        self.connection = None
        self.hover = False

        if direction=="IN":
            self.right_radius = 5
            self.left_radius = 0
        else:
            self.right_radius = 0
            self.left_radius = 5
        border_radius = ft.border_radius.horizontal(
            left=self.left_radius,
            right=self.right_radius)

        self.content=ft.Stack(
            [
             ft.Container(
                 top=0, right=0, left=0, bottom=0,
                 bgcolor=self.choose_bg_color(),
                 border_radius=border_radius
             ),
             ft.GestureDetector(
                 on_enter=self.handle_on_enter,
                 on_exit=self.handle_on_exit,
                 on_tap=self.handle_on_tap,
                 on_secondary_tap=self.handle_on_secondary
             )
            ]
            )

    def choose_bg_color(self):
        if self.hover:
            return TM.get_nested_color("port", "bg_hover")
        elif self.connected:
            return TM.get_nested_color("port", "bg_connected")
        return TM.get_nested_color("port", "bg")

    def update_bg_color(self):
        self.content.controls[0].bgcolor = self.choose_bg_color()
        self.update()

    @property
    def location(self):
        ports_location = self.ports.location
        x = ports_location[0] + 5
        y = ports_location[1] + self.top + 5
        return (x,y)
        

    def handle_on_enter(self, e):
        BM.display_info(f"{self.port_label}:{self.port_type.signal_type.__name__}")
        self.hover = True
        self.update_bg_color()
        #self.content.controls[0].bgcolor = TM.get_nested_color("port","bg_hover")

    def handle_on_exit(self, e):
        BM.display_info(f"")
        self.hover = False
        self.update_bg_color()

    def handle_on_tap(self,e):
        success = CM.connect_action(e,self.port_label, self.device_instance, self)
        if not self.connected:
            self.connected = success

    def handle_on_secondary(self, e):
        CM.disconnect(self)

    def set_connection(self, connection=None) -> None:
        self.connection = connection
        if connection:
            self.connected = True
        else:
            self.connected = False
        self.update_bg_color()
