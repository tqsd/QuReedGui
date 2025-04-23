"""
QuReed Gui entry point
"""

import threading

import flet as ft

from components import Toolbar, StatusBar
from panels import BoardPanel, SimulationPanel
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

def board_render(self, board):
    board.update()

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
    
    def scroll_reset(e):
        BM = LogicModuleHandler().get_logic(LogicModuleEnum.BOARD_MANAGER)
        BM.reset_scroll()


    tabs = ft.Container(
        bgcolor=TM.get_nested_color("bg","base"),
        expand=True,
        content=ft.Tabs(
            selected_index=0,
            animation_duration=100,
            indicator_color="white",
            divider_color="black",
            expand=True,
            on_change=scroll_reset,
            tabs=[
                ft.Tab(
                    tab_content=ft.Container(
                        height=20,
                        alignment=ft.alignment.center,
                        content=ft.Text("Board", size=15, color="white"),
                    ),
                    content=BoardPanel(page)
                ),
                ft.Tab(
                    tab_content=ft.Container(
                        height=20,
                        alignment=ft.alignment.center,
                        content=ft.Text("Simulation", size=15, color="white")
                    ),
                    content=SimulationPanel(page)
                )
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
    threading.Thread(target=start_pynput_listener, args=(KED,), daemon=True).start()


ft.app(main)
