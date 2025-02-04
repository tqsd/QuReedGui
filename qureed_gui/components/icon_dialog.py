import re
import flet as ft

from logic import get_device_icon
from logic import ProjectManager
from theme import ThemeManager

TM = ThemeManager()
PM = ProjectManager()

DIALOG_HEIGHT = 300
DIALOG_WIDTH = 600
BUTTON_HEIGHT = 30
IMAGE_PREVIEW_SIZE = 100


class IconDialog(ft.AlertDialog):
    def __init__(self, page):
        super().__init__()
        self.image_path = ""  # Store the selected image path
        self.existing_icon_list = PM.get_list_of_all_existing_icons()
        self.title = ft.Text("Add a new Device icon")
        self.actions = [
            ft.TextButton("Confirm", on_click=self.on_confirm),
            ft.TextButton("Cancel", on_click=self.on_cancel)
            ]

        # FilePicker instance
        self.file_picker = ft.FilePicker(
            on_result=self.process_icon
        )
        page.overlay.append(self.file_picker)  # Add FilePicker to the page overlay

        # Button to open the FilePicker
        self.find_icon_button = ft.Container(
            height=30,
            content=ft.TextButton(
                text="Find an image",  # Updated the content
                on_click=self.open_file_explorer
            )
        )

        self.image_name_container = ft.Container(
            content=ft.TextField(
                label="Image Name",
                on_change=self.on_image_name_change,
                error_text=""
                )
            )

        # Display the selected image path
        self.image_path_text = ft.Text(self.image_path)

        # Display selected image
        self.image_container = ft.Container(
            width=IMAGE_PREVIEW_SIZE, height=IMAGE_PREVIEW_SIZE, 
            border_radius=5,
            bgcolor=TM.get_nested_color("device", "bg"),
            )
        self.image_path_container = ft.Container(
            height=30,
            content=self.image_path_text  # Use a Text control
        )

        # Stack containing the button and the path display
        self.stack = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.find_icon_button,
                self.image_path_container,
                self.image_container,
                self.image_name_container,
                ]
        )

        # Dialog content
        self.content = ft.Container(
            height=DIALOG_HEIGHT, width=DIALOG_WIDTH,  # Increased width for better layot
            content=self.stack
        )

    def process_icon(self, e):
        """Handle the result of the file picker."""
        if e.files:
            self.image_path = e.files[0].path  # Get the first file's path
            self.image_path_text.value = self.image_path  # Update the Text control
            self.image_container.content = ft.Image(
                src_base64=get_device_icon(self.image_path)
                )
            e.page.update()
            self.image_container.content.update()
            self.image_path_text.update()  # Refresh the display
        else:
            print("No file selected.")

    def open_file_explorer(self, e):
        """Open the file picker dialog."""
        self.file_picker.pick_files(
            dialog_title="Device Icon",
            file_type=ft.FilePickerFileType.IMAGE,
            allowed_extensions=["jpg", "png"],
            allow_multiple=False  # Restrict to single file selection
        )

    def on_image_name_change(self,e):
        name = e.control.value  # Get the current value of the text field

        # Allow only letters, numbers, dashes, and underscores
        if not re.match(r"^[a-zA-Z0-9_-]*$", name):
            e.control.error_text = "Only letters, numbers, '-', and '_' are allowed."
        elif name in self.existing_icon_list:
            e.control.error_text = "An icon with this name already exists."
        else:
            e.control.error_text = None # Clear any previous error message

        e.control.update()  # Update the TextField with changes
        e.page.update()

    def on_confirm(self, e):
        if self.image_path == "":
            snack_bar = ft.SnackBar(content=ft.Text("No icon file selected."))
            snack_bar.open = True
            e.page.overlay.append(snack_bar)
            e.page.update()
            return
        if not self.image_name_container.content.error_text == "":
            snack_bar = ft.SnackBar(content=ft.Text("Choose another name"))
            snack_bar.open = True
            e.page.overlay.append(snack_bar)
            e.page.update()
            return
        success, message = PM.add_icon(self.image_path, self.image_name_container.content.value)
        if success:
            self.on_cancel(e)
        else:
            snack_bar = ft.SnackBar(content=ft.Text(message))
            snack_bar.open = True
            e.page.overlay.append(snack_bar)
            e.page.update() 
            

    def on_cancel(self, e):
        self.open = False  # Set the dialog's open property to False
        e.page.update() 
