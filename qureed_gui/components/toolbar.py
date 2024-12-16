import flet as ft

from theme import ThemeManager
from logic.project import ProjectManager
from .icon_dialog import IconDialog
from .new_device_dialog import NewDeviceDialog

PM = ProjectManager()
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
        self.content=ft.Text("Project",
            color=TM.get_nested_color("toolbar", "text")
            )
        self.controls=[
            ft.MenuItemButton(
                content=ft.Text("New Device"),
                on_click=self.new_device
                ),
            ft.MenuItemButton(
                content=ft.Text("New Device Icon"),
                on_click=self.add_icon
                ),
            ]

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
                 content=ft.Text("New Device")
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
            if project_name:
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
