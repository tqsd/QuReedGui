import re
import os
import flet as ft

from logic import get_device_icon_absolute_path
from logic import ProjectManager
from logic import QureedInspector
from logic import KeyboardEventDispatcher
from theme import ThemeManager

TM = ThemeManager()
PM = ProjectManager()
QI = QureedInspector()
KED = KeyboardEventDispatcher()

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
        self.expand=True
        self.height=100
        self.custom_icons = PM.get_list_of_all_existing_icons()
        self.qureed_icons = QI.get_qureed_icons()
        self.icons = [
            (f"*{icon}", f"{PM.path}/custom/icons/{icon}.png")
            for icon in self.custom_icons]
        qureed_icons = [os.path.splitext(os.path.basename(path))[0] for path in self.qureed_icons]
        self.icons.extend(
            zip(qureed_icons, self.qureed_icons)
        )
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
        self.image_container.content = ft.Image(
            src_base64=get_device_icon_absolute_path(e.data)
        )
        self.selected_icon = e.data.replace(PM.path, "")
        e.page.update()
        print(self.selected_icon)
        self.image_container.content.update()

    def get_icon(self):
        return self.selected_icon


class NewDeviceDialog(ft.AlertDialog):
    def __init__(self, page):
        super().__init__()
        self.modal = True
        self.existing_icon_list = PM.get_list_of_all_existing_icons()
        self.title = ft.Text("Create a new Device")
        self.actions = [
            ft.TextButton("Confirm", on_click=self.on_confirm),
            ft.TextButton("Cancel", on_click=self.on_cancel)
            ]
        self.device_name = ft.TextField(label="New device name")
        signals = QI.get_qureed_signals()
        self.input_ports = PortCreation("Input Ports", signals)
        self.output_ports = PortCreation("Output Ports", signals)
        self.icon_select = IconSelect()
        self.tags = ft.TextField(label="Tags (comma ',' separated)")
        
        self.column = ft.Column(
            [
                self.device_name,
                self.tags,
                self.icon_select,
                ft.Divider(),
                self.input_ports,
                self.output_ports,
                ft.Divider()
            ],
            scroll=ft.ScrollMode.ADAPTIVE
            )
        self.content = ft.Container(
            height = DIALOG_HEIGHT, width=DIALOG_WIDTH,
            content=self.column,
            )
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
        PM.new_device(
            name=name,
            tags=self.tags.value,
            in_ports=in_ports,
            out_ports=out_ports,
            icon=icon
        )
        KED.active = True
        self.open = False
        e.page.update()

    def on_cancel(self, e):
        self.open = False  # Set the dialog's open property to False
        e.page.update() 
        KED.active = True
        
