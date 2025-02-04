import flet as ft

from theme import ThemeManager
from logic.project import ProjectManager
from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler
from .icon_dialog import IconDialog
from .new_device_dialog import NewDeviceDialog

PM = ProjectManager()
LMH = LogicModuleHandler()
TM = ThemeManager()


class Toolbar(ft.Container):
    """
    Toolbar appears always on the top
    """
    def __init__(self):
        super().__init__()
        self.height=20
        self.bgcolor=TM.get_nested_color("toolbar","bg")
        self.content=ft.Row(
            [
             FileMenu(),
             ProjectMenu()
            ]
        )

class ProjectMenu(ft.SubmenuButton):
    def __init__(self):
        super().__init__()
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        PM.register_device_menu(self)
        self.content=ft.Text("Devices",
            color=TM.get_nested_color("toolbar", "text")
            )
        self.controls=[
            ft.MenuItemButton(
                content=ft.Text("Create New Device"),
                on_click=None
                ),
            ft.MenuItemButton(
                content=ft.Text("Add New Device Icon"),
                on_click=None
                ),
            ]

    def toggle_menu(self):
        self.is_menu_open = not self.is_menu_open

    def activate(self):
        self.controls[0].on_click = self.new_device
        self.controls[1].on_click = self.add_icon

    def deactivate(self):
        self.controls[0].on_click = None
        self.controls[1].on_click = None


    def add_icon(self, e):
        ic = IconDialog(e.page)
        e.page.overlay.append(ic)
        ic.open = True
        e.page.update()

    def new_device(self, e):
        ndd = NewDeviceDialog(e.page)
        e.page.overlay.append(ndd)
        ndd.open = True
        e.page.update()

        
    

class FileMenu(ft.SubmenuButton):
    def __init__(self):
        super().__init__(
        content=ft.Text(
            "File",
            color=TM.get_nested_color("toolbar","text")
        ),
        controls=[
             ft.MenuItemButton(
                 content=ft.Text("New Project"),
                 on_click=lambda e: self.pick_dir(self.new_project, e)
             ),
             ft.MenuItemButton(
                 content=ft.Text("Open Project"),
                 on_click= lambda e: self.pick_dir(self.open_project, e)
             ),
             ft.MenuItemButton(
                 content=ft.Text("Save Scheme"),
                 on_click=self.save_scheme
             ),
            ]
        )

    def pick_dir(self, callback, e: ft.ControlEvent):
        fp = ft.FilePicker(on_result=callback)

        e.page.overlay.append(fp)
        e.page.update()
        fp.get_directory_path()

    def new_project(self, e):
        # Create a TextField for user input
        if not e.path:
            return
        name_prompt = ft.TextField(label=f"{e.path}/")

        # Define the on_click handler for the Cancel button first
        def close_dialog(click_event):
            dialog.open = False  # Close the dialog
            e.page.close(dialog)

        # Define the on_click handler for the Confirm button
        def on_confirm(click_event):
            project_name = name_prompt.value.strip()
            if not project_name:
                name_prompt.error_text= "Project Name cannot be empty!"
                e.page.update()
                return
            else:
                name_prompt.error_text= None
                e.page.update()
                PM.new_project(f"{e.path}/{project_name}")
                dialog.open = False
                e.page.close(dialog)
                e.page.update()

        # Create the AlertDialog with proper handlers
        dialog = ft.AlertDialog(
            title=ft.Text("New Project Name"),
            content=name_prompt,
            actions=[
                ft.TextButton("Confirm", on_click=on_confirm),
                ft.TextButton("Cancel", on_click=close_dialog)
            ],
            modal=True  # Makes the dialog modal (prevents interaction with other UI elements)
        )

        # Add the dialog to the page's overlay
        e.page.overlay.append(dialog)

        # Open the dialog
        dialog.open = True

        # Update the page to reflect changes
        e.page.update()

    def open_project(self, e):
        PM.open_project(e.path)
        e.page.update()

    def save_scheme(self, e):
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        PM.save_scheme()
