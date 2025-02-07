import flet as ft


class PerformanceGraph(ft.Container):
    def __init__(self):
        super().__init__()
        self.height = 200
        self.width = 400
        self.bgcolor = "red"

class MemoryGraph(PerformanceGraph):
    def __init__(self):
        super().__init__()


class CPUGraph(PerformanceGraph):
    def __init__(self):
        super().__init__()



class SimulationGraph(ft.Row):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.height = 200
        self.controls=[
            MemoryGraph(),
            CPUGraph()
        ]
        self.alignment = ft.MainAxisAlignment.SPACE_EVENLY