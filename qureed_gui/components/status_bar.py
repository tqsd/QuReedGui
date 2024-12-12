import flet as ft
import threading
from theme import ThemeManager
from logic.project import ProjectManager

PM = ProjectManager()
TM = ThemeManager()
# status_bar.py
import flet as ft
from theme import ThemeManager
from logic.project import ProjectManager

PM = ProjectManager()
TM = ThemeManager()

class StatusBar(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.page = page
        self.height = 25
        self.bgcolor = TM.get_nested_color("toolbar", "bg")
        self.message_timer = None

        # Initialize icons and text
        self.project_status_icon = ft.Icon(
            name=ft.Icons.STOP_CIRCLE_OUTLINED,
            color=TM.get_nested_color("toolbar", "not_ready")
        )
        self.simulation_status_icon = ft.Icon(
            name=ft.Icons.STOP_CIRCLE_OUTLINED,
            color=TM.get_nested_color("toolbar", "not_ready")
        )
        self.message = ft.Text("", color=TM.get_nested_color("toolbar", "text"))

        # Layout
        self.content = ft.Row(
            [
                self.project_status_icon,
                self.message,
                self.simulation_status_icon,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.controls = [self.content]
        self.content_control = self.content

        # Register this StatusBar with ProjectManager
        PM.register_status_bar(self)

    def update_project_status(self, status: int):
        print("UPDATED PROJECT STATUS")

        if status == 1:
            self.project_status_icon.name = ft.Icons.CHECK_CIRCLE_OUTLINED
            self.project_status_icon.color = TM.get_nested_color("toolbar", "ready")
        else:
            self.project_status_icon.name = ft.Icons.STOP_CIRCLE_OUTLINED
            self.project_status_icon.color = TM.get_nested_color("toolbar", "not_ready")

        self.page.update()

    def set_message(self, message: str, timer=True):
        self.message.value = message
        self.page.update()
        if timer:
            self.message_timer = threading.Timer(
                5.0,
                lambda : self.set_message("", timer=False))
            self.message_timer.start()

        

