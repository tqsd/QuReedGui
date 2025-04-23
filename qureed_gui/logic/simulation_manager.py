import asyncio
import uuid 
from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler

LMH = LogicModuleHandler()

class SimulationManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SimulationManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self,"initialized"):
            LMH.register(LogicModuleEnum.SIMULATION_MANAGER, self)
            self.simulation_tab=None
            self.log_component=None
            self.simulation_time=None
            self.scheme = None
            self.initialized=True

    def set_simulation_time(self, simulation_time:float) -> None:
        self.simulation_time = simulation_time
        print(self.simulation_time)

    def register_simulation_tab(self, simulation_tab) -> None:
        self.simulation_tab = simulation_tab

    def register_log_component(self, log_component) -> None:
        self.log_component = log_component

    def update_executable_schemes(self, schemes) -> None:
        if self.simulation_tab:
            self.simulation_tab.update_executable_schemes(schemes)

    def select_scheme(self, scheme=None):
        self.scheme = scheme
        print(f"Selected a new scheme {self.scheme}")

    def clear_logs(self):
        if self.log_component:
            self.log_component.clear_logs()

    def simulation_start(self):
        self.clear_logs()
        SeM = LMH.get_logic(LogicModuleEnum.SERVER_MANAGER)
        self.simulation_id = uuid.uuid4()
        if self.scheme:
            response = SeM.start_simulation(
                self.scheme,
                self.simulation_id,
                self.simulation_time)

    def handle_logs(self, response):
        if self.log_component:
            self.log_component.submit_log(response.log)
        else:
            print("COMPONENT NOT REGISTERED")

    def handle_simulation_end(self):
        self.simulation_id = None
