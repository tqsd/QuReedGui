import flet as ft
from flet.core.adaptive_control import AdaptiveControl

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
OFFSET = 0
BOARD_SIZE = 10000

class Board(ft.Container):
    def __init__(self,page, location_widget):
        super().__init__()
        self.page = page
        self.location_widget = location_widget
        self.top = 0
        self.left = 0
        self.bottom = 0
        self.board_offset = [BOARD_SIZE / 2, BOARD_SIZE / 2]
        BM.register_board(self)
        self.right = 0
        self.canvas = Canvas()
        self.board = ft.Stack(
            expand=True,
            controls=[
                self.canvas
            ]
        )
        self.board_wrapper = ft.Container(
            height=BOARD_SIZE,
            width=BOARD_SIZE,
            content = self.board
            )
        self.content = ft.Row(
            expand=True,
            scroll=ft.ScrollMode.ALWAYS,
            on_scroll= lambda e: self.on_scroll_handle(e, 'x'),
            controls=[ft.Column(
                scroll=ft.ScrollMode.HIDDEN,
                on_scroll= lambda e: self.on_scroll_handle(e, 'y'),
                expand=True,
                controls=[self.board_wrapper]
                )]
            )

    @property
    def location(self):
        return [ o - BOARD_SIZE/2 for o in self.board_offset ]
        
    @location.setter
    def location(self, location):
        self.board_offset = [ max(l + BOARD_SIZE/2,0) for l in location ]
        self.location_widget.update_location(*self.location)

    def clear_board(self):
        self.canvas.clear_canvas()
        self.board.controls = [self.canvas]
        self.center_board()
        

    def on_scroll_handle(self, e, direction):
        if direction == 'x':
            self.board_offset[0] = e.pixels
        elif direction == 'y':
            self.board_offset[1] = e.pixels
        
        self.location_widget.update_location(*self.location)
            
    def move_board(self, e):
        print("Moving the board", e)
        location = self.location
        location[0] -= e.delta_x
        location[1] -= e.delta_y
        self.location = location

    def on_click_handle(self, e):
        print("CLICK")

    def did_mount(self):
        row = self.content# This is the Row
        col = row.controls[0]  # This is the Column inside the Row

        row.scroll_to(self.board_offset[0])

        col.scroll_to(self.board_offset[1])
        self.location_widget.update_location(*self.location)

    def center_board(self, e=None):
        self.location = [0,0]
        self.content.scroll_to(offset=self.board_offset[0])
        self.content.controls[0].scroll_to(self.board_offset[1])
        self.location_widget.update_location(*self.location)

        
    def add_device(self, device_class, location=None):
        if not location:
            location = [o+500 for o in self.board_offset]
        else:
            location[0] += self.board_offset[0]
            location[1] += self.board_offset[1] - 55
            

        device_location = location
        print(device_location)
        self.board.controls.append(
            get_device_control(device_class)(device_location, device_class=device_class)
            )
        self.board.update()

class BoardContainer(ft.Container):
    def __init__(self, page:ft.Page):
        super().__init__()
        self.top=0
        self.bottom=0
        self.right=0
        self.left=0
        self.bgcolor = TM.get_nested_color("board", "bg")
        PM.register_board(self)
        KED.register_hook(' ', self.handle_new_device)
        self.offset_x, self.offset_y = (0,0)

        self.board_bar = BoardBar()
        self.location = Location()
        self.info = Info()
        self.board = Board(page, self.location)
        self.stack= ft.Stack(
            [
             self.board,
             self.board_bar,
             self.location,
             self.info,
            ],
            #width=float("inf"),
            #height=float("inf"),
            )
        self.content = ft.Container(
            expand=True,
            content=ft.DragTarget(
                group="device", content=self.stack,
                on_accept=self.drag_accept
            )
            )
        self.device_creation_modal= DeviceCreation()

    def handle_new_device(self, e):
        self.page.open(self.device_creation_modal)

    def drag_accept(self, e):
        c = self.page.get_control(e.src_id)
        self.board.add_device(c.device_class, [e.x, e.y])

        
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
        BM.center_board(e)

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
