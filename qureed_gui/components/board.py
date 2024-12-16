import flet as ft
import flet.canvas as cv

from theme import ThemeManager
from logic import (
    ProjectManager, KeyboardEventDispatcher,
    BoardManager, get_device_control,
    SimulationManager
    )
from .device_creation import DeviceCreation
from .canvas import Canvas

TM = ThemeManager()
PM = ProjectManager()
KED = KeyboardEventDispatcher()
BM = BoardManager()
OFFSET = -5000

class Board(ft.Container):
    def __init__(self, page:ft.Page):
        super().__init__()
        self.top=0
        self.bottom=0
        self.right=0
        self.left=0
        self.bgcolor = TM.get_nested_color("board", "bg")
        PM.register_board(self)
        BM.register_board(self)
        KED.register_hook(' ', self.handle_new_device)
        self.offset_x, self.offset_y = (0,0)

        self.board_bar = BoardBar()
        self.location = Location()
        self.info = Info()
        self.canvas = Canvas()
        self.board_wrapper = ft.Stack(
                [
                ],
            top=-5000, left=-5000, width=float("inf"), height=float("inf")
            )

        self.stack= ft.Stack(
            [
             #self.canvas_wrapper,
             self.canvas,
             ft.GestureDetector(
                 drag_interval=5,
                 on_vertical_drag_update=self.handle_board_move,
             ),
             self.board_wrapper,
             self.board_bar,
             self.location,
             self.info,
            ],
            width=float("inf"),
            height=float("inf"),
            )
        self.content = ft.Container(
            expand=True,
            content=ft.DragTarget(
                group="device", content=self.stack,
                on_accept=self.drag_accept
            )
            )
        self.device_creation_modal= DeviceCreation()

    def center_board(self):
        self.offset_x = 0
        self.offset_y = 0

        self.board_wrapper.top  = OFFSET
        self.board_wrapper.left = OFFSET
        #self.canvas_wrapper.top  = self.canvas_wrapper.top + e.delta_y
        #self.canvas_wrapper.left = self.canvas_wrapper.left + e.delta_x
        self.canvas.top  = OFFSET
        self.canvas.left = OFFSET
        self.location.update_location(0,0)
        self.update()
        self.page.update()

    def handle_board_move(self, e):
        self.offset_x += e.delta_x
        self.offset_y += e.delta_y

        self.board_wrapper.top  = self.board_wrapper.top + e.delta_y
        self.board_wrapper.left = self.board_wrapper.left + e.delta_x
        #self.canvas_wrapper.top  = self.canvas_wrapper.top + e.delta_y
        #self.canvas_wrapper.left = self.canvas_wrapper.left + e.delta_x
        self.canvas.top  = self.canvas.top + e.delta_y
        self.canvas.left = self.canvas.left + e.delta_x

        self.offset_x = self.offset_x
        self.offset_y = self.offset_y
        self.location.update_location(self.offset_x, self.offset_y)
        self.update()

    def handle_new_device(self, e):
        self.page.open(self.device_creation_modal)

    def add_device(self, device_class, location=None):
        if BM.opened_scheme is None:
            snack_bar = ft.SnackBar(content=ft.Text("No Scheme is opened, open a scheme(.json) in a project")) 
            snack_bar.open = True
            self.page.overlay.append(snack_bar)
            self.page.update()
            try:
                self.page.close(self.device_creation_modal)
            except Exception as e:
                pass
            return
        try:
            self.page.close(self.device_creation_modal)
        except Exception as e:
            pass
        if location == None:
            device_location = (-self.offset_x+400, -self.offset_y+200)
        else:
            device_location = (-self.offset_x+location[0], -self.offset_y+location[1])
        self.board_wrapper.controls.append(
            get_device_control(device_class)(device_location, device_class=device_class)
            )
        self.page.update()

    def display_info(self, info):
        self.info.updade_info(info)

    def drag_accept(self, e):
        print("Drag Accept",e)
        c = self.page.get_control(e.src_id)
        print(c.device_class)
        self.add_device(c.device_class, (e.x-5, e.y-65))

        
class BoardBar(ft.Container):
    def __init__(self):
        super().__init__()
        self.top = 0
        self.right = 0
        self.left = 250
        self.height = 25
        self.bgcolor = TM.get_nested_color("board_bar", "bg")
        self.current_scheme_name = BM.opened_scheme if BM.opened_scheme else "No Scheme Opened"
        self.current_scheme = ft.Text(
            self.current_scheme_name,
            color=TM.get_nested_color("board_bar", "text")
            )
        self.content = ft.Row(
            [self.current_scheme]
        )
        BM.register_board_bar(self)

    def update_scheme_name(self, name):
        self.current_scheme.value = BM.opened_scheme if BM.opened_scheme else "No Scheme Opened"
        print(self.current_scheme_name)
        self.update()

class Location(ft.Container):
    def __init__(self):
        super().__init__()
        self.bottom = 0
        self.right = 5
        self.height = 25
        self.width = 200
        self.location = (0.0,0.0)
        self.on_click = self.handle_on_click
        self.content = ft.Text(
            f"x:{self.location[0]}, y:{self.location[1]}",
            text_align=ft.TextAlign.RIGHT
            )
        
    def update_location(self, x,y):
        self.location = (-float(x),-float(y))
        self.content.value = f"x:{self.location[0]:.0f}, y:{self.location[1]:.0f}"
        self.update()

    def handle_on_click(self,e):
        BM.center_board()

class Info(ft.Container):
    def __init__(self):
        super().__init__()
        self.bottom = 25
        self.right = 5
        self.height = 25
        self.width = 400
        self.content = ft.Text(
            "",
            text_align=ft.TextAlign.RIGHT
            )

    def updade_info(self, info):
        self.content.value = info
        self.update()
