import flet as ft
from components import ProjectExplorer, Board
from theme import ThemeManager

TM = ThemeManager()


class BoardPanel(ft.Stack):
    def __init__(self, page:ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.controls = [
            Board(page),
            ProjectExplorer(page),
            ]
