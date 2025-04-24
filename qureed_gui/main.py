"""
QuReed Gui entry point
"""

import threading
import os

import flet as ft

from qureed_gui.components import Toolbar, StatusBar
from qureed_gui.panels import BoardPanel, SimulationPanel
from qureed_gui.theme import ThemeManager


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
    page.title = "QuReed"
    page.padding = 0
    page.spacing = 0


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
            #on_change=scroll_reset,
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
    page.browser_context_menu.disable()

        

ft.app(target=main, view=ft.WEB_BROWSER) 
#ft.app(main)
