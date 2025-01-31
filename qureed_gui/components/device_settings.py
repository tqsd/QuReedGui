import flet as ft
import traceback
from enum import Enum

from google.protobuf.json_format import MessageToDict

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
    def __init__(self, settings, device, parameter, prop):
        super().__init__()
        print("NEW SETTING")
        self.settings=settings
        self.expand=True
        self.device=device
        self.parameter=parameter
        print(parameter, prop)
        print(self.device.device.device_properties.properties[parameter]["type"])
        properties = MessageToDict(self.device.device.device_properties.properties)
        self.properties = properties
        print(type(properties))
        print(properties)
        if properties[parameter]["type"] == "bool":
            value = properties[parameter].get("value", False)
            print(value)
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
                label=f"{parameter}:{properties[parameter]['type']}",
                color=TM.get_nested_color("device_settings", "text"),
                border_color=TM.get_nested_color("device_settings", "input_border_color"),
                value=properties[parameter].get("value", ""),
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

    def handle_on_change(self, e):
        try:
            value_cast = self.properties[self.parameter]["type"]
            value_cast = type_mapping[value_cast]
            value = value_cast(e.data)
            #self.device_instance.set_property(
            #    self.parameter,
            #    value
            #    )
            self.properties[self.parameter]["value"]=value
            self.device.update_properties(
                self.properties
                )
            self.content.border_color = None
            self.content.error_text = None
        except (ValueError, TypeError) as e:
            traceback.print_exc()
            self.content.border_color = "red"
            self.content.error_text = f"expectes {self.device.device.device_properties.properties[self.parameter]['type']}"
        #self.settings.update_device()
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
        print("Settings")
        print(device.device.device_properties)
        self.device = device
        self.settings = [
            Setting(self, self.device, key, prop) for key,prop in
            self.device.device.device_properties.properties.items()
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
        print(self.device.device_instanc.properties)
        self.device.update()

    def device_disconnect(self):
        CM = LMH.get_logic(LogicModuleEnum.CONNECTION_MANAGER)
        for port in self.device.ports_right.content.controls:
            CM.disconnect(port)
    
