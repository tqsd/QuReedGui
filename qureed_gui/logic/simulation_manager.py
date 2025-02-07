
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
            self.scheme = None
            self.initialized=True

    def register_simulation_tab(self, simulation_tab) -> None:
        self.simulation_tab = simulation_tab

    def update_executable_schemes(self, schemes) -> None:
        if self.simulation_tab:
            self.simulation_tab.update_executable_schemes(schemes)

    def select_scheme(self, scheme=None):
        self.scheme = scheme
        print(f"Selected a new scheme {self.scheme}")

    def simulation_start(self):
        SeM = LMH.get_logic(LogicModuleEnum.SERVER_MANAGER)
        if self.scheme:
            response = SeM.start_simulation(self.scheme)
            print(response)
        
