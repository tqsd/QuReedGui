import flet as ft
from rapidfuzz import process

from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler
from qureed_project_server import server_pb2

LMH = LogicModuleHandler()

class Device(ft.Container):
    def __init__(self, device:server_pb2.Device):
        super().__init__()
        self.name=device.gui_name if device.gui_name else device.class_name
        self.device=device
        self.device_tags = device.gui_tags
        self.on_click= self.add_device
        self.content=ft.Text(self.name)

    def add_device(self, e):
        BM = LMH.get_logic(LogicModuleEnum.BOARD_MANAGER)
        BM.add_device(self.device)


class DeviceCreation(ft.AlertDialog):
    """
    Modal for inserting devices into the board.
    """
    def __init__(self):
        super().__init__()
        self.modal=False
        self.title=ft.Text("Select a Device")

        self.filtered_devices = []
        self.search_query = ""
        self.devices = []

        self.qureed_devices=ft.ListView(
            self.filtered_devices
            )

        self.content=ft.Column(
            [
             ft.TextField(
                 on_change=self.filter_devices,
                 label="Find a device"
             ),
             ft.Divider(),
             self.qureed_devices,
             ft.Divider(),
             ft.Row(
                 [
                    ]
             )
             ]
            )
        self.actions = [
            ft.TextButton("Close", on_click=self.on_close),
            ]

    def update_dialog(self):
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        SvM = LMH.get_logic(LogicModuleEnum.SERVER_MANAGER)
        all_devices = SvM.get_all_devices()
        PM.display_message("Grabbing Existing Devices")

        self.devices = all_devices.devices
        self.filtered_devices = self.devices
        self.update_device_list()

        KED = LMH.get_logic(LogicModuleEnum.KEYBOARD_DISPATCHER)
        KED.active = False

    def update_device_list(self):
        """Update the ListView based on filtered devices."""
        self.qureed_devices.controls = [
            Device(device)
            for device in self.filtered_devices
        ]
        self.update()

    def filter_devices(self, e):
        """Filter devices based on the search query."""
        query = e.control.value.strip().lower()
        self.search_query = query

        # Perform fuzzy matching on names and tags
        all_device_names = [device.gui_name for device in self.devices]
        print("---------")
        print(all_device_names)
        matches = process.extract(query, all_device_names, limit=len(self.devices))
        print(matches)
        
        # Filter the devices that match the query
        self.filtered_devices = [
            self.devices[idx] for idx, (name, score, idx) in enumerate(matches)
        ]
        if len(self.search_query) == 0:
            self.filtered_devices = self.devices
        self.update_device_list()
            
    def on_close(self, e):
        KED = LMH.get_logic(LogicModuleEnum.KEYBOARD_DISPATCHER)
        KED.active = True
        self.open = False
        e.page.update()
