import flet as ft
from rapidfuzz import process

from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler

LMH = LogicModuleHandler()

class Device(ft.Container):
    def __init__(self, name, device_class, device_mc):
        super().__init__()
        self.value=name
        self.device_mc=device_mc
        self.device_class=device_class
        self.device_tags = device_class.gui_tags
        self.on_click= self.add_device
        self.content=ft.Text(name)

    def add_device(self, e):
        BM = LMH.get_logic(LogicModuleEnum.BOARD_MANAGER)
        BM.add_device(self.device_class, self.device_mc)
        
        

class DeviceCreation(ft.AlertDialog):
    def __init__(self):
        super().__init__()
        self.modal=False
        self.title=ft.Text("Select a Device")
        CL = LMH.get_logic(LogicModuleEnum.CLASS_LOADER)
        print("SHOULD GET THE VENV")
        CL.get_qureed_devices()

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
        CL = LMH.get_logic(LogicModuleEnum.CLASS_LOADER)
        devices = CL.get_qureed_devices()
        
        if not devices:
            return

        self.devices = [
            {
                "name": device[0].gui_name,
                "tags": device[0].gui_tags,
                "class": device[0],
                "mc": device[1],
            }
            for device in devices if hasattr(device[0], "gui_name") and hasattr(device[0], "gui_tags")
        ]

        self.filtered_devices = self.devices
        self.update_device_list()

        #self.qureed_devices.controls = []
        #for device in devices:
        #    d_cls = device[0]
        #    if not hasattr(d_cls, "gui_name"):
        #        continue
        #    d_name = d_cls.gui_name
        #    device_component = Device(d_name, d_cls, device[1])
        #    self.qureed_devices.controls.append(device_component)
        KED = LMH.get_logic(LogicModuleEnum.KEYBOARD_DISPATCHER)
        KED.active = False

    def update_device_list(self):
        """Update the ListView based on filtered devices."""
        self.qureed_devices.controls = [
            Device(device["name"], device["class"], device["mc"])
            for device in self.filtered_devices
        ]
        self.update()

    def filter_devices(self, e):
        """Filter devices based on the search query."""
        query = e.control.value.strip().lower()
        self.search_query = query

        # Perform fuzzy matching on names and tags
        all_device_names = [device["name"] for device in self.devices]
        matches = process.extract(query, all_device_names, limit=len(self.devices))
        
        # Filter the devices that match the query
        self.filtered_devices = [
            self.devices[idx] for idx, (name, score, idx) in enumerate(matches) if score > 50
        ]
        print("HESE")
        if len(self.search_query) == 0:
            print("should show all")
            self.filter_devices = self.devices
        self.update_device_list()
            
    def on_close(self, e):
        KED = LMH.get_logic(LogicModuleEnum.KEYBOARD_DISPATCHER)
        KED.active = True
        self.open = False
        e.page.update()
