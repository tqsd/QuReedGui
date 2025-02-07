import flet as ft


class SimulationLogs(ft.Container):
    def __init__(self):
        super().__init__()
        self.top=250
        self.left=0
        self.right=0
        self.bottom=0
        self.bgcolor = "blue"