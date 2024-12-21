import flet as ft

from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler
from theme import ThemeManager

TM = ThemeManager()
LMH = LogicModuleHandler()

class NameProperty(ft.Container):
    def __init__(self):
        super().__init__()
        self.content=ft.TextField(
            label="Device Name"
            )

class Setting(ft.Container):
    def __init__(self, device_instance, parameter, label=None):
        super().__init__()
        self.expand=True
        self.content = ft.TextField(
            label=label,
            color=TM.get_nested_color("device_settings", "text"),
            border_color=TM.get_nested_color("device_settings", "input_border_color"),
            label_style=ft.TextStyle(
                color=TM.get_nested_color("device_settings", "text"),
                )
            )
    
class DeviceSettings(ft.Container):
    def __init__(self):
        super().__init__()
        self.top = 50
        self.right = 20
        #self.height = 100
        self.width = 250
        self.bgcolor = TM.get_nested_color("device_settings", "bg")
        self.opacity = 0.9
        self.border_radius = 5
        self.visible = False
        SM = LMH.get_logic(LogicModuleEnum.SELECTION_MANAGER)
        SM.register_device_settings(self)
        self.device = None
        self.title = ft
        self.padding = ft.padding.all(5)
        self.settings = []
        self.content=ft.Column(
            [
             ft.Text(
                 "Device Properties",
                 size=20,
                 color=TM.get_nested_color("device_settings", "text"),
                 text_align=ft.TextAlign.CENTER
             ),
             ft.Divider(),
             *self.settings
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER
            )

    def display_settings(self, device):
        self.device = device
        print(dir(device.device_instance))
        print(self.device.device_instance.properties)
        self.settings = [
            Setting(self.device.device_instance, "name", "Device Name"),
            ]
        self.visible = True
        self.update()

    def hide_settings(self):
        self.device = None
        self.visible = False
        self.update()
