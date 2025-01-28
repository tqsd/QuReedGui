import inspect
import flet as ft


import flet.canvas as cv

from theme import ThemeManager
from logic.logic_module_handler import LogicModuleHandler, LogicModuleEnum
from logic.board_helpers import get_device_control
from .device_creation import DeviceCreation
from .canvas import Canvas
from .select_box import SelectBox
from .device_settings import DeviceSettings

LMH = LogicModuleHandler()
TM = ThemeManager()
OFFSET = 0
BOARD_SIZE = 10000

class Board(ft.Container):
    def __init__(self,page, location_widget):
        super().__init__()
        BM = LMH.get_logic(LogicModuleEnum.BOARD_MANAGER)
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        PM.register_board(self)
        BM.register_board(self)
        self.page = page
        self.location_widget = location_widget
        self.top = 0
        self.left = 0
        self.bottom = 0
        self.board_offset = [BOARD_SIZE / 2, BOARD_SIZE / 2]
        self.right = 0
        self.transform=ft.transform.Scale
        self.canvas = Canvas()

        self.select_box = SelectBox()

        SeM = LMH.get_logic(LogicModuleEnum.SELECTION_MANAGER)
        self.gesture_detection = ft.GestureDetector(
            on_tap=lambda e: SeM.deselect_all(),
            on_horizontal_drag_start=self.select_box.sb_start,
            on_horizontal_drag_update=self.select_box.sb_update,
            on_horizontal_drag_end=lambda e: self.select_box.sb_stop(e,self.board)
        )
        
        self.board = ft.Stack(
            expand=True,
            controls=[
                self.canvas,
                self.select_box,
                self.gesture_detection
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
    def device_controls(self):
        return self.board.controls[1:]

    @property
    def location(self):
        return [ o - BOARD_SIZE/2 for o in self.board_offset ]
        
    @location.setter
    def location(self, location):
        self.board_offset = [ max(l + BOARD_SIZE/2,0) for l in location ]
        self.location_widget.update_location(*self.location)

    def clear_board(self):
        self.canvas.clear_canvas()
        self.board.controls = [
            self.canvas,
            self.select_box,
            self.gesture_detection]
        self.center_board()
        

    def on_scroll_handle(self, e, direction):
        if direction == 'x':
            self.board_offset[0] = e.pixels
        elif direction == 'y':
            self.board_offset[1] = e.pixels
        
        self.location_widget.update_location(*self.location)
            
    def move_board(self, e):
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

        
    def add_device(self, device, location=None):
        if not location:
            location = [o+500 for o in self.board_offset]
        else:
            location[0] += self.board_offset[0]
            location[1] += self.board_offset[1] - 55
            

        device_location = location
        result = get_device_control(device)(location, device)
        result.register_device_with_server()
        if isinstance(result, list):
            self.board.controls.extend(result)
        else:
            self.board.controls.append(result)
        self.board.update()

    def load_devices_bulk(self, device_list):
        device_controls = []
        for device in device_list:
            print(device)
            result = get_device_control(device)(device.location, device)
            if isinstance(result, list):
                self.board.controls.extend(result)
            else:
                self.board.controls.append(result)
        self.board.update()

    def load_connections_bulk(self, connections):
        CM = LMH.get_logic(LogicModuleEnum.CONNECTION_MANAGER)
        for connection in connections:
            port1 = self.get_port(connection.device_one_uuid, connection.device_one_port_label)
            port2 = self.get_port(connection.device_two_uuid, connection.device_two_port_label)
            print(port1)
            print(type(port1))
            CM.load_connection(port1, port2)
            

    def get_device(self, uuid):
        from components.board_component import BoardComponent
        for device in self.board.controls:
            if not isinstance(device, BoardComponent):
                continue
            if device.device.uuid == uuid:
                return device

    def get_port(self, device_uuid, port_label):
        device = self.get_device(device_uuid)
        for p in device.device.ports:
            if p.label == port_label:
                port = p

        if port.direction=="input":
            ports = device.ports_left
        elif port.direction=="output":
            ports = device.ports_right

        for p in ports.content.controls:
            if p.port_label == port.label:
                return p


        
class BoardContainer(ft.Container):
    def __init__(self, page:ft.Page):
        super().__init__()
        self.top=0
        self.bottom=0
        self.right=0
        self.left=0
        self.bgcolor = TM.get_nested_color("board", "bg")
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        KED = LMH.get_logic(LogicModuleEnum.KEYBOARD_DISPATCHER)
        KED.register_hook(' ', self.handle_new_device)
        KED.register_hook('s', PM.save_scheme, ctrl=True)
        self.offset_x, self.offset_y = (0,0)

        self.device_creation_modal= DeviceCreation()
        self.board_bar = BoardBar()
        self.location = Location()
        self.info = Info()
        self.board = Board(page, self.location)
        self.device_settings = DeviceSettings()
        self.controls = Controls(self.device_creation_modal)
        self.stack= ft.Stack(
            [
             self.board,
             self.board_bar,
             self.location,
             self.info,
             self.device_settings,
             self.controls
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

    def handle_new_device(self, e):
        self.page.open(self.device_creation_modal)
        self.device_creation_modal.update_dialog()

    def drag_accept(self, e):
        SvM = LMH.get_logic(LogicModuleEnum.SERVER_MANAGER)
        c = self.page.get_control(e.src_id)
        self.board.add_device(c.device, [e.x, e.y])

        
class BoardBar(ft.Container):
    def __init__(self):
        super().__init__()
        BM = LMH.get_logic(LogicModuleEnum.BOARD_MANAGER)
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
        BM = LMH.get_logic(LogicModuleEnum.BOARD_MANAGER)
        self.current_scheme.value = BM.opened_scheme if BM.opened_scheme else "No Scheme Opened"
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
        BM = LMH.get_logic(LogicModuleEnum.BOARD_MANAGER)
        BM.center_board(e)

class Info(ft.Container):
    def __init__(self):
        super().__init__()
        self.bottom = 25
        self.right = 5
        self.height = 25
        self.width = 400
        BM = LMH.get_logic(LogicModuleEnum.BOARD_MANAGER)
        BM.register_board_info(self)
        self.content = ft.Text(
            "",
            text_align=ft.TextAlign.RIGHT
            )

    def update_info(self, info):
        self.content.value = info
        self.update()


class Controls(ft.Container):
    def __init__(self, device_creation_modal):
        super().__init__()
        self.device_creation_modal = device_creation_modal
        self.top = 30
        self.height = 100
        self.width = 50
        self.left = 250
        self.content = ft.Column(
            controls=[
                ft.TextButton(
                    text="",
                    icon=ft.Icons.ADD_ROUNDED,
                    on_click=self.add_device
                      )
            ]
            )
        BM = LMH.get_logic(LogicModuleEnum.BOARD_MANAGER)
        BM.board_controls = self

    def add_device(self,e):
        self.page.open(self.device_creation_modal)
        self.device_creation_modal.update_dialog()
