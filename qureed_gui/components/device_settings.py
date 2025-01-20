import flet as ft
import traceback
from enum import Enum

from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler
from theme import ThemeManager

TM = ThemeManager()
LMH = LogicModuleHandler()

type_mapping = {
    "int": int,
    "float": float,
    "bool": bool,
    "cmplx": complex,
    "str": str,
    "char": lambda v: v if len(v) == 1 else ValueError("Value must be a single character")
}

class Setting(ft.Container):
    def __init__(self, settings, device_instance, parameter, prop):
        super().__init__()
        print("NEW SETTING")
        self.settings=settings
        self.expand=True
        self.device_instance=device_instance
        self.parameter=parameter
        print(self.device_instance.properties[parameter]["type"])
        print(type(self.device_instance.properties[parameter]["type"]))
        try:
            issubclass(self.device_instance.properties[parameter]["type"], Enum)
        except Exception as e:
            print(e)
            print(self.device_instance.properties[parameter]["type"])
            print(type(self.device_instance.properties[parameter]["type"]))
            print("------------------------")
        if issubclass(self.device_instance.properties[parameter]["type"], Enum):
            value = None
            if parameter == "variable_type":
                value = self.device_instance.properties["value"]["type"]
            if value is object:
                value = None
            self.content=ft.Dropdown(
                value=value,
                hint_text = parameter,
                expand = True,
                color = TM.get_nested_color("device_settings","text"),
                bgcolor = TM.get_nested_color("device_settings","bg"),
                border_color = TM.get_nested_color("device_settings", "text"),
                on_change = self.handle_enum_change,
                options = [
                    ft.dropdown.Option(
                        text=str(name),
                        key=name
                           ) for 
                    name, member in
                    self.device_instance.properties[parameter]["type"].__members__.items()
                ]
                )
        elif self.device_instance.properties[parameter]["type"] is bool:
            value = self.device_instance.properties[parameter].get("value", False)
            print(value)
            print(self.device_instance.properties)
            selected = {}
            if value:
                selected = {True}
            else:
                selected = {False}
            print("Should display the BOOL Button", value, selected)
            btn_style=ft.ButtonStyle(
                color={
                    ft.ControlState.SELECTED:"black",
                    ft.ControlState.DEFAULT:"white"
                    }
                )
            self.content=ft.Row(
                controls=[
                    ft.Text(parameter, color=TM.get_nested_color("device_settings", "text")),
                    ft.SegmentedButton(
                        segments=[
                            ft.Segment(
                                value=True,
                                label=ft.Text("True"),
                                ),
                            ft.Segment(
                                value=False,
                                label=ft.Text("False"),
                                  ),
                        ],
                        style=btn_style,
                        selected = selected,
                        allow_multiple_selection=False,
                        on_change=self.handle_bool_change
                    )
                    ]
                )
        else:
            self.content=ft.TextField(
                label=f"{parameter}:{self.device_instance.properties[parameter]['type']}",
                color=TM.get_nested_color("device_settings", "text"),
                border_color=TM.get_nested_color("device_settings", "input_border_color"),
                value=self.device_instance.get_property(parameter),
                label_style=ft.TextStyle(
                    color=TM.get_nested_color("device_settings", "text"),
                    ),
                on_change=self.handle_on_change
                )
    def handle_bool_change(self, e):
        if e.data== '["true"]':
            self.device_instance.set_value(True)
        else:
            self.device_instance.set_value(False)
        self.settings.update_device()

    def handle_enum_change(self, e):
        print(e)
        enum_class = self.device_instance.properties[self.parameter]["type"]
        print(enum_class)
        #enum_class = type(enum_class)
        enum_choice = enum_class[e.data]
        print(enum_choice)
        print(self.device_instance.properties)
        if self.parameter == "variable_type":
            self.device_instance.set_variable_type(enum_choice)
            self.settings.device_disconnect()
        else:
            self.device_instance.set_property(self.parameter, enum_choice)
        print(self.device_instance.properties)
        print(self.settings)
        self.settings.update_device()
        self.settings.update_settings()
        
    
    def handle_on_change(self, e):
        try:
            value_cast = self.device_instance.properties[self.parameter]["type"]
            value = value_cast(e.data)
            self.device_instance.set_property(
                self.parameter,
                value
                )
            self.content.border_color = None
            self.content.error_text = None
        except (ValueError, TypeError) as e:
            traceback.print_exc()
            self.content.border_color = "red"
            self.content.error_text = f"expectes {self.device_instance.properties[self.parameter]}"
        self.settings.update_device()
        self.content.update()

        
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
        self.settings = [
            Setting(self, self.device.device_instance, key, prop) for key,prop in
            self.device.device_instance.properties.items()
            ]
        self.content.controls = [
            ft.Text(
                "Device Properties",
                size=20,
                color=TM.get_nested_color("device_settings", "text"),
                text_align=ft.TextAlign.CENTER
            ),
            ft.Divider(),
            *self.settings
            ]
        self.visible = True
        self.update()

    def hide_settings(self):
        self.device = None
        self.visible = False
        self.update()
       
    def update_settings(self):
        self.display_settings(self.device)
        print(f"Updating  SETTINGS")

    def update_device(self):
        print("UPDATING DEVICE")
        print(self.device.device_instance.properties)
        self.device.update()

    def device_disconnect(self):
        CM = LMH.get_logic(LogicModuleEnum.CONNECTION_MANAGER)
        for port in self.device.ports_right.content.controls:
            CM.disconnect(port)
    
