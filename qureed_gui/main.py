"""
QuReed Gui entry point
"""

import threading

import flet as ft

from components import Toolbar, StatusBar
from panels import BoardPanel
from theme import ThemeManager

from logic.keyboard import KeyboardEventDispatcher, start_pynput_listener
from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler

def window_focus(e) -> None:
    """
    Window focus hook

    Parameters:
    -----------
    e (ft.Event): Event created at the focusing
    """
    KED = KeyboardEventDispatcher()
    if e.type == ft.WindowEventType.BLUR:
        KED.focused = False
    elif e.type == ft.WindowEventType.FOCUS:
        KED.focused = True

def main(page: ft.Page) -> None:
    """
    Main function

    This function starts the gui process

    Parameters:
    -----------
    page (ft.Page): flet Page instance
    """
    PM = LogicModuleHandler().get_logic(LogicModuleEnum.PROJECT_MANAGER)
    PM.register_page(page)
    page.title = "QuReed"
    page.padding = 0
    page.spacing = 0

    KED = KeyboardEventDispatcher()
    #page.on_keyboard_event = KED.handle_click

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
    page.window.on_event=window_focus
    print(page.window.height)
    threading.Thread(target=start_pynput_listener, args=(KED,), daemon=True).start()

ft.app(main)
