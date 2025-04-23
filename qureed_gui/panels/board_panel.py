import flet as ft
from qureed_gui.components import ProjectExplorer, BoardContainer
from qureed_gui.components.board import Board
from qureed_gui.theme import ThemeManager

TM = ThemeManager()


class BoardPanel(ft.Stack):
    def __init__(self, page:ft.Page):
        print("RERENDERING BOARD PANEL")
        super().__init__()
        self.page = page
        self.expand = True
        self.controls = [
            BoardContainer(page),
            ProjectExplorer(page),
            ]
