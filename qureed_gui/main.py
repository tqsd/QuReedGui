"""
QuReed Gui entry point
"""
import flet as ft

from components import Toolbar, StatusBar
from panels import BoardPanel
from theme import ThemeManager
from logic import KeyboardEventDispatcher

def main(page: ft.Page):
    page.title = "QuReed"
    page.padding = 0
    page.spacing = 0

    KED = KeyboardEventDispatcher()
    page.on_keyboard_event = KED.handle_click

    TM = ThemeManager()

    tabs = ft.Container(
        bgcolor=TM.get_nested_color("bg","base"),
        expand=True,
        content=ft.Tabs(
            selected_index=1,
            animation_duration=100,
            indicator_color="white",
            divider_color="black",
            expand=True,
            tabs=[
                ft.Tab(
                    tab_content=ft.Container(
                        height=20,
                        alignment=ft.alignment.center,
                        content=ft.Text("Board", size=15, color="white"),
                    ),
                    content=BoardPanel(page)
                ),
            ],
        )
    )

    container = ft.Column(
        controls=[
            Toolbar(),
            tabs,
            StatusBar(page)
        ],
        expand=True,
        spacing=0,
    )
    
    # Add container to the page
    page.add(container)

ft.app(main)
