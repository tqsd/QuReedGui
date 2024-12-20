"""
Manages the simulation
"""
from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler

LMH = LogicModuleHandler()

class SimulationManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SimulationManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.status_bar = None
            self.devices = []
            self.signals = []
            LMH.register(LogicModuleEnum.SIMULATION_MANAGER, self)
            self.initialized = True

    def clear_simulation(self):
        self.devices = []
        self.signals = []
        
    def register_status_bar(self, status_bar):
        self.status_bar = status_bar

    def add_device(self, device):
        self.devices.append(device)
        self.display_message(f"Added a device: {device.__class__.__name__}")

    def remove_device(self, device):
        self.devices.remove(device)
        self.display_message(f"Removed a device: {device.__class__.__name__}")

    def create_connection(self, sig_cls, dev1, port_label_1, dev2, port_label_2):
        sig = sig_cls()
        if dev1 is dev2:
            raise ValueError("Cannot connect to self")
        print(dev1.ports[port_label_1], sig)
        dev1.register_signal(signal=sig, port_label=port_label_1)
        dev2.register_signal(signal=sig, port_label=port_label_2)
        self.signals.append(sig)
        name = lambda dev: dev.name if dev.name else dev.__class__.__name__
        self.display_message(
            f"Connection Created {name(dev1)}:{port_label_1}-{sig_cls.__name__}-{name(dev2)}:{port_label_2}")
        return sig

    def remove_connection(self, sig):
        print("removing connection")
        for p in sig.ports:
            p.signal = None
        self.signals.remove(sig)

    def display_message(self, message:str, timer=True):
        if self.status_bar:
            self.status_bar.set_message(message, timer)

    def get_device(self, uuid):
        return [d for d in self.devices if d.ref.uuid == uuid][0]
