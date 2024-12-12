import flet as ft
import flet.canvas as cv

from theme import ThemeManager
from logic import ProjectManager, KeyboardEventDispatcher, BoardManager
from .device_creation import DeviceCreation

# For testing
from .board_component import BoardComponent

TM = ThemeManager()
PM = ProjectManager()
KED = KeyboardEventDispatcher()
BM = BoardManager()

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
        stroke_paint = ft.Paint(stroke_width=2, style=ft.PaintingStyle.STROKE)
        self.canvas = cv.Canvas(
            [cv.Circle(500,500, 200, stroke_paint)]
            )
        self.canvas_wrapper = ft.Container(
            top=0, left=0,
            content=self.canvas)
        self.board_wrapper = ft.Stack(
                [
                 ft.Container(top=400,left=500,height=100, width=100, bgcolor="black"),
                 ft.Container(top=500,left=800,height=100, width=100, bgcolor="RED"),
                 BoardComponent((600,600))
                ],
            top=0, left=0, width=float("inf"), height=float("inf")
            )

        self.content = ft.Stack(
            [
             self.canvas_wrapper,
             ft.GestureDetector(
                 drag_interval=1,
                 on_vertical_drag_update=self.handle_board_move,
             ),
             self.board_wrapper,
             self.board_bar,
             self.location,
            ]
            )
        self.device_creation_modal= DeviceCreation()

    def handle_board_move(self, e):
        self.offset_x += e.delta_x
        self.offset_y += e.delta_y

        self.board_wrapper.top  = self.board_wrapper.top + e.delta_y
        self.board_wrapper.left = self.board_wrapper.left + e.delta_x
        self.canvas_wrapper.top  = self.canvas_wrapper.top + e.delta_y
        self.canvas_wrapper.left = self.canvas_wrapper.left + e.delta_x

        self.offset_x = self.offset_x
        self.offset_y = self.offset_y
        self.location.update_location(self.offset_x, self.offset_y)
        self.update()
        e.page.update()

    def handle_new_device(self, e):
        self.page.open(self.device_creation_modal)

    def add_device(self, device_class):
        self.page.close(self.device_creation_modal)
        print(device_class)

        
class BoardBar(ft.Container):
    def __init__(self):
        super().__init__()
        self.top = 0
        self.right = 0
        self.left = 0
        self.height = 25
        self.bgcolor = "white"
        
class Location(ft.Container):
    def __init__(self):
        super().__init__()
        self.bottom = 0
        self.right = 5
        self.height = 25
        self.width = 200
        self.location = (0.0,0.0)
        self.content = ft.Text(
            f"x:{self.location[0]}, y:{self.location[1]}",
            text_align=ft.TextAlign.RIGHT
            )
        
    def update_location(self, x,y):
        self.location = (float(x),float(y))
        self.content.value = f"x:{self.location[0]:.0f}, y:{self.location[1]:.0f}"
        self.update()

