import flet as ft

from qureed_gui.logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler
from qureed_project_server.utils import tensor_from_message
from qureed_gui.logic.board_helpers import get_device_icon

LMH = LogicModuleHandler()

class SimulationLogLine(ft.Container):
    """
    Individual Log Line renders one log line. It understands, what kind
    of log it should display. It can display general logs, tensor logs or 
    plot (picture) logs.

    Attributes:
    -----------
    log: the log message to be generated and displayed
    expanded: expansion flag, used for plot or tensor logging
    tensor_data: Optional tensor data
    plot_path: The path to the plot

    """
    def __init__(self, log):
        super().__init__()
        self.log = log
        self.spacing = 2
        self.bgcolor = "black"
        font_family = "Courier New"
        self.expanded = False
        controls = [
            ft.Text(
                f"[ {float(log.simulation_timestamp):<5} ]", 
                color="#f1f1f1",
                font_family=font_family),
            ft.Text(
                f"[ {log.log_type[:3]:<3} ]", 
                color="#d3f2b1",
                font_family=font_family)
        ]
        if hasattr(log, "device_name"):
            controls.append(
                ft.Text(
                    f"{log.device_name[:15]:<15}", 
                    color="#f2a797",
                    font_family=font_family)
            )
        if hasattr(log, "device_type"):
            controls.append(
                ft.Text(
                    f" {log.device_type:<20} ", 
                    color="white", 
                    font_family=font_family)
            )
        controls.append(
            ft.Text(
                " : ",
                color="#797979", 
                font_family=font_family),
        )
        controls.append(
            ft.Text(
                log.message, 
                color="white", 
                font_family=font_family),
        )
        self.tensor_data = None
        self.tensor_display = None
        self.plot_display = None

        if log.figure:
            self.plot_path = log.figure
            self.expand_button = ft.IconButton(
                icon=ft.icons.EXPAND_MORE,
                on_click=self.toggle_plot_display,
                icon_color="white",
                icon_size=10,
            )
            controls.append(self.expand_button)  # Add the button at the start

        if log.tensor.real_values:
            self.tensor_data = tensor_from_message(log.tensor)  # Convert tensor to NumPy array
            self.expand_button = ft.IconButton(
                icon=ft.icons.EXPAND_MORE,
                on_click=self.toggle_tensor_display,
                icon_color="white",
                icon_size=10
            )
            controls.append(self.expand_button)  # Add the button at the start

        self.main_row = ft.Row(controls)
        self.content = ft.Column([self.main_row])

        self.on_hover = self.on_hover_handler

    def toggle_tensor_display(self, e):
        """ Expands or collapses the tensor display """
        if self.expanded:
            self.content.controls.remove(self.tensor_display)  # Hide tensor
            self.expand_button.icon = ft.icons.EXPAND_MORE  # Update button icon
        else:
            self.tensor_display = self.create_tensor_display()
            self.content.controls.append(self.tensor_display)  # Show tensor
            self.expand_button.icon = ft.icons.EXPAND_LESS  # Update button icon

        self.expanded = not self.expanded
        self.update()

    def toggle_plot_display(self, e):
        if self.expanded:
            self.content.controls.remove(self.plot_display)
            self.expand_button.icon = ft.icons.EXPAND_MORE  # Update button icon
        else:
            self.plot_display = self.create_plot_display()
            self.content.controls.append(self.plot_display)  # Show tensor
            self.expand_button.icon = ft.icons.EXPAND_LESS  # Update button icon

        self.expanded = not self.expanded
        self.update()
        print(self.plot_path)

    def create_plot_display(self):
        """Creates plot display"""
        plot_img = get_device_icon(self.plot_path)
        return ft.Container(
            content=ft.Image(src_base64=plot_img),
            padding=ft.padding.all(10)
        )


    def create_tensor_grid(self):
        """ Creates a formatted display of the tensor """
        tensor_str = str(self.tensor_data)  # Convert NumPy array to string
        return ft.Container(
            content=ft.Text(tensor_str, font_family="Courier New", color="white"),
            padding=ft.padding.all(10),
            bgcolor="#222222",
            border_radius=5
        )

    def create_tensor_display(self):
        """ Creates a DataTable for a 2D tensor """
        return self.create_tensor_grid()

    def on_hover_handler(self, e):
        if e.data == "true":
            self.bgcolor="#424242"
        else:
            self.bgcolor = "black"
        self.update()



class SimulationLogs(ft.Container):
    def __init__(self):
        super().__init__()
        self.top=150
        self.left=20
        self.right=20
        self.bottom=10
        SiM = LMH.get_logic(LogicModuleEnum.SIMULATION_MANAGER)
        SiM.register_log_component(self)
        self.content = ft.Column(
            expand=True,
            scroll=True,
            spacing=0,
        )

    def submit_log(self, log):
        self.content.controls.append(SimulationLogLine(log))
        if hasattr(log, "tensor") and log.tensor.real_values:
            print(tensor_from_message(log.tensor))
        self.content.controls.sort(
            key=lambda lc: float(lc.log.simulation_timestamp)
        )
        self.update()

    def clear_logs(self):
        self.content.controls = []
        self.update()
