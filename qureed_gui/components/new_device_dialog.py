import re
import os
import flet as ft

from logic import get_device_icon_absolute_path
from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler
from theme import ThemeManager

LMH = LogicModuleHandler()
TM = ThemeManager()

DIALOG_HEIGHT = 500
DIALOG_WIDTH = 700
BUTTON_HEIGHT = 30
IMAGE_PREVIEW_SIZE = 50

class NewPort(ft.Row):
    def __init__(self, parent, signals):
        self.parent=parent
        super().__init__()
        self.signals=signals
        self.controls = [
            ft.TextField(label="Port Name"),
            ft.Dropdown(
                label="Port Type",
                options=
                [ft.dropdown.Option(
                    sig[0]
                ) for sig in self.signals]
            ),
            ft.TextButton(icon=ft.Icons.REMOVE, on_click=self.remove_port)
            ]

    def remove_port(self, e):
        # Remove this port from its parent
        parent = self.parent
        if parent:
            parent.controls.remove(self)
            parent.update()  # Update the parent to refresh the UI

class PortCreation(ft.Column):
    def __init__(self, label, signals):
        super().__init__()
        self.signals = signals
        self.controls=[
            ft.Row(
                controls=[
                    ft.Text(label),
                    ft.TextButton(icon=ft.Icons.ADD, on_click=self.add_port)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
             )
            ]

    def add_port(self, e):
        new_port = NewPort(self, self.signals)
        self.controls.append(new_port)
        self.update()
        e.control.update()

    def get_ports(self):
        ports = {}
        for p in self.controls[1:]:
            name = p.controls[0].value
            ptype = p.controls[1].value
            ports[name]=ptype
        return ports

class IconSelect(ft.Container):
    def __init__(self):
        super().__init__()
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        CL = LMH.get_logic(LogicModuleEnum.CLASS_LOADER)
        self.expand=True
        self.height=100
        self.custom_icons = PM.get_list_of_all_existing_icons()
        #self.qureed_icons = QI.get_qureed_icons()
        self.icons = [
            (f"*{icon}", f"{PM.path}/custom/icons/{icon}.png")
            for icon in self.custom_icons]
        icon_list = CL.load_module_from_venv("qureed.assets.icon_list")
        all_icon_list_attributes = dir(icon_list)

        qureed_icons = [
            (name, f"{os.path.dirname(os.path.abspath(icon_list.__file__))}/{getattr(icon_list, name)}")
            for name in all_icon_list_attributes
            if name.isupper() and not callable(getattr(icon_list, name))
        ]
        
        self.icons.extend(qureed_icons)
        self.image_container = ft.Container(
            width=IMAGE_PREVIEW_SIZE, height=IMAGE_PREVIEW_SIZE, 
            border_radius=5,
            bgcolor=TM.get_nested_color("device", "bg"),
            )
        self.content=ft.Column(
            controls=[
                ft.Dropdown(
                    label="Select Icon",
                    on_change=self.on_select,
                    options=[
                        ft.dropdown.Option(text=ic[0], key=ic[1])
                        for ic in self.icons
                    ]
                ),
                self.image_container
            ]
        )

    def on_select(self, e):
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        self.image_container.content = ft.Image(
            src_base64=get_device_icon_absolute_path(e.data)
        )
        self.selected_icon = e.data.replace(PM.path, "")
        e.page.update()
        print(self.selected_icon)
        self.image_container.content.update()

    def get_icon(self):
        return self.selected_icon

class Properties(ft.Column):
    def __init__(self):
        super().__init__()
        self.controls=[
            ft.Row(
                controls=[
                    ft.Text("Properties"),
                    ft.TextButton(icon=ft.Icons.ADD, on_click=self.add_property)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
             )
            ]
    def add_property(self, e):
        new_property = NewProperty(self)
        self.controls.append(new_property)
        self.update()
        e.control.update()
        print(e)

    def get_properties(self):
        properties = {}
        for new_property in self.controls[1:]:
            prop = new_property.get_property()
            properties[prop[0]]=prop[1]
        return properties

class NewProperty(ft.Row):
    def __init__(self,parent):
        super().__init__()
        self.parent = parent
        property_types = ["str", "float", "int", "cmplx", "bool"]
        self.controls=[
            ft.TextField(label="Property Name", on_change=self.on_label_change),
            ft.Dropdown(
                options=[ft.dropdown.Option(val) for val in property_types],
                hint_text="Select a type"
            ),
            ft.TextButton(icon=ft.Icons.REMOVE, on_click=self.remove_property)
        ]
        self.alignment=ft.MainAxisAlignment.SPACE_BETWEEN

    def on_label_change(self, e):
        if not re.match(r'^[a-zA-Z0-9 ]*$', e.control.value):
            # Remove invalid characters
            e.control.error_text = "Only alphanumeric characters and spaces are allowed"
            e.control.update()
        else:
            # Clear the error if the input is valid
            e.control.error_text = None
            e.control.update()

    def remove_property(self, e):
        # Remove this port from its parent
        parent = self.parent
        if parent:
            parent.controls.remove(self)
            parent.update()  # Update the parent to refresh the UI

    def get_property(self):
        prop = {
            "type": self.controls[1].value
        }
        return self.controls[0].value, prop

class NewDeviceDialog(ft.AlertDialog):
    def __init__(self, page):
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        super().__init__()
        self.modal = True
        self.existing_icon_list = PM.get_list_of_all_existing_icons()
        self.title = ft.Text("Create a new Device")
        self.actions = [
            ft.TextButton("Confirm", on_click=self.on_confirm),
            ft.TextButton("Cancel", on_click=self.on_cancel)
            ]
        self.device_name = ft.TextField(label="New device name")
        #signals = QI.get_qureed_signals()
        signals = []
        self.input_ports = PortCreation("Input Ports", signals)
        self.output_ports = PortCreation("Output Ports", signals)
        self.icon_select = IconSelect()
        self.tags = ft.TextField(label="Tags (comma ',' separated)")
        self.properties = Properties()
        
        self.column = ft.Column(
            [
                self.device_name,
                self.tags,
                self.icon_select,
                ft.Divider(),
                self.input_ports,
                self.output_ports,
                ft.Divider(),
                self.properties
            ],
            scroll=ft.ScrollMode.ADAPTIVE
            )
        self.content = ft.Container(
            height = DIALOG_HEIGHT, width=DIALOG_WIDTH,
            content=self.column,
            )
        KED = LMH.get_logic(LogicModuleEnum.KEYBOARD_DISPATCHER)
        KED.active = False

    def on_confirm(self, e):
        if self.device_name.value == "":
            snack_bar = ft.SnackBar(content=ft.Text("No Device Name Given")) 
            snack_bar.open = True
            e.page.overlay.append(snack_bar)
            e.page.update()
            return
        if not self.icon_select.content.controls[0].value:
            snack_bar = ft.SnackBar(content=ft.Text("No Icon Selected")) 
            snack_bar.open = True
            e.page.overlay.append(snack_bar)
            e.page.update()
            return
        name = self.device_name.value
        in_ports = self.input_ports.get_ports()
        out_ports = self.output_ports.get_ports()
        for ports in [in_ports, out_ports]:
            for key, value in ports.items():
                if key=="" or value is None:
                    snack_bar = ft.SnackBar(content=ft.Text("Port not fully specified")) 
                    snack_bar.open = True
                    e.page.overlay.append(snack_bar)
                    e.page.update()
                    return
                    
        icon = self.icon_select.get_icon()
        print(self.properties.get_properties())
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        PM.new_device(
            name=name,
            tags=self.tags.value,
            in_ports=in_ports,
            out_ports=out_ports,
            icon=icon,
            properties=self.properties.get_properties()
        )
        KED = LMH.get_logic(LogicModuleEnum.KEYBOARD_DISPATCHER)
        KED.active = True
        self.open = False
        e.page.update()

    def on_cancel(self, e):
        self.open = False  # Set the dialog's open property to False
        e.page.update() 
        KED = LMH.get_logic(LogicModuleEnum.KEYBOARD_DISPATCHER)
        KED.active = True
        
