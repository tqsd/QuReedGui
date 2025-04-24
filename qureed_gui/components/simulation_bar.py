from pathlib import Path

from qureed_gui.logic.logic_module_handler import (
    LogicModuleEnum, LogicModuleHandler
)

import flet as ft

LMH = LogicModuleHandler()

class SimulationBar(ft.Container):
    def __init__(self):
        super().__init__()
        self.height = 70
        self.top = 0
        self.right = 0
        self.bgcolor = "black"
        self.left = 0
        SiM = LMH.get_logic(LogicModuleEnum.SIMULATION_MANAGER)
        SiM.register_simulation_tab(self)
        self.dropdown = ft.Dropdown(
                label="Scheme",
                hint_text="Which scheme will get executed",
                width=300,
                #height=40,
                color="white",
                bgcolor="#594c4c",
                border_color="gray",
                text_size=15,
                label_style=ft.TextStyle(color="white"),
                padding=ft.Padding(0,0,0,0),
                options=[],
                on_change=self.on_scheme_select
            )
        self.content = ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.PLAY_ARROW,
                    icon_color="white",
                    tooltip="Start the Simulation",
                    on_click=self.start_simulation,
                    icon_size=20
                ),
                self.dropdown,
                ft.TextField(
                    label="simulation time (s)",
                    color="white",
                    border_color="grey",
                    label_style=ft.TextStyle(color="white"),
                    on_change=self.update_simulation_time
                )
            ],
            alignment=ft.MainAxisAlignment.START
        )
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        PM.collect_schemes()

    def update_simulation_time(self, e):
        text = e.control.value.strip()

        # Allow empty field (no error)
        if text == "":
            e.control.error_text = None
            e.control.update()
            return

        # Allow intermediate values like "-" or "." temporarily
        if text in ["-", "."]:
            e.control.error_text = None
            e.control.update()
            return

        try:
            float(text)  # ✅ Validate as float
            e.control.error_text = None  # Clear error if valid
            SiM = LMH.get_logic(LogicModuleEnum.SIMULATION_MANAGER)
            SiM.set_simulation_time(float(text))
        except ValueError:
            e.control.error_text = "Invalid number format"  # Show error message

        e.control.update()  # Update UI

    def start_simulation(self, e):
        SiM = LMH.get_logic(LogicModuleEnum.SIMULATION_MANAGER)
        SiM.simulation_start()

    def update_executable_schemes(self, schemes):
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        SiM = LMH.get_logic(LogicModuleEnum.SIMULATION_MANAGER)
        SiM.select_scheme()
        base_path = Path(PM.path)
        self.dropdown.options.clear()
        default_scheme = None
        for scheme in schemes:
            scheme_path =Path(scheme).resolve()

            scheme_name = scheme_path.relative_to(base_path)
            self.dropdown.options.append(
                ft.dropdown.Option(
                    text=scheme_name,
                    key=scheme
                )
            )
            if (scheme_path.parent == base_path and
                scheme_path.name == "main.json"):
                default_scheme = scheme
        if default_scheme:
            self.dropdown.value = default_scheme
            SiM.select_scheme(default_scheme)

        if self.page:
            self.dropdown.update()

    def on_scheme_select(self, e):
        SiM = LMH.get_logic(LogicModuleEnum.SIMULATION_MANAGER)
        SiM.select_scheme(e.data)
