"""
Manages the connections between the ports
"""
import traceback

from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler
from .simulation_manager import SimulationManager
from components.connection import Connection

LMH = LogicModuleHandler()

class ConnectionManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConnectionManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.first_port = None
            self.canvas = None
            self.canvas_connections = {}
            self.all_connections = {}
            LMH.register(LogicModuleEnum.CONNECTION_MANAGER, self)
            self.initialized = True

    def register_canvas(self, canvas):
        self.canvas = canvas

    def clear(self):
        if self.first_port:
            self.first_port[2].set_connection()
            self.first_port = None

    def connect_action_interrupt(self):
        self.first_port = None

    def get_signal_class(self, signal_mc):
        self.pro

    def connect_action(self, e, port_label, device_instance, port):
        SM = LMH.get_logic(LogicModuleEnum.SIMULATION_MANAGER)
        connection = None
        if self.first_port is None:
            self.first_port = (device_instance,port_label, port)
            return True
        else:
            sig_cls_1 = self.first_port[0].ports[self.first_port[1]].signal_type
            sig_cls_2 = device_instance.ports[port_label].signal_type

            # We select the signal which is higher in the inheritance chain
            try:
                sig = SM.create_connection(sig_cls, self.first_port[0], self.first_port[1],
                                     device_instance, port_label)
                connection=Connection(self.first_port[2], port, self.canvas.canvas, sig)
                self.first_port[2].set_connection(connection)
                port.set_connection(connection)
                connection.draw()
            except Exception as e:
                print("ERROR", e)
                err=traceback.format_exc()
                SM.display_message("ERROR: " + str(e))
                print(err)
                self.clear()
                return False

            self.register_connection(port, self.first_port[2], connection)
            self.first_port = None
            return True

    def load_connection(self, port1, port2):
        """
        Renders the connection, which already exist in the backend
        """
        connection = Connection(port1, port2, self.canvas.canvas)
        port1.set_connection(connection)
        port2.set_connection(connection)
        self.register_connection(port1, port2, connection)
        connection.draw()
            
    def register_connection(self, port1, port2, connection):
        if port1 not in self.all_connections.keys():
            self.all_connections[port1] = []
        if port2 not in self.all_connections.keys():
            self.all_connections[port2] = []
        self.all_connections[port1].append((port2, connection))
        self.all_connections[port2].append((port1, connection))
        
    def disconnect(self, port):
        SM = LMH.get_logic(LogicModuleEnum.SIMULATION_MANAGER)
        port.set_connection()
        if port not in self.all_connections.keys():
            return
        if len(self.all_connections[port]) == 0:
            return
        
        connection = self.all_connections[port][0][1]
        connection.remove()
        for other_port in self.all_connections[port]:
            SM.remove_connection(connection.signal)
            other_port[0].set_connection()
            self.all_connections[other_port[0]] = []
        self.all_connections[port] = []
        
        
