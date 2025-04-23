import flet as ft

from components import (
    SimulationBar, SimulationGraph, SimulationLogs
)
from theme import ThemeManager

class SimulationPanel(ft.Stack):
    """
    Simulation Panel displays the process of the simulation in
    real time
    """
    def __init__(self, page:ft.Page):
        super().__init__()
        self.page = page
        self.expand = True
        self.controls = [
            SimulationBar(),
            ft.Container(
                top=90,
                right=0,
                left=0,
                height=0,
                content=ft.Column(
                    [
                        #SimulationGraph(),
                    ],
                    expand=True,
                    scroll=ft.ScrollMode.ALWAYS
                )
            ),
            SimulationLogs()
            ]


