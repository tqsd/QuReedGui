"""
Manages the connections between the ports
"""
from .simulation_manager import SimulationManager
from components.connection import Connection

SM = SimulationManager()

class ConnectionManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConnectionManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.initialized = True
            self.first_port = None
            self.canvas = None
            self.canvas_connections = {}
            self.all_connections = {}

    def register_canvas(self, canvas):
        self.canvas = canvas

    def clear(self):
        if self.first_port:
            self.first_port[2].set_connection()
            self.first_port = None

    def connect_action_interrupt(self):
        self.first_port = None

    def connect_action(self, e, port_label, device_instance, port):
        connection = None
        if self.first_port is None:
            self.first_port = (device_instance,port_label, port)
            return True
        else:
            sig_cls_1 = self.first_port[0].ports[self.first_port[1]].signal_type
            sig_cls_2 = device_instance.ports[port_label].signal_type

            # We select the signal which is higher in the inheritance chain
            sig_cls = None
            if issubclass(sig_cls_1, sig_cls_2):
                sig_cls = sig_cls_2
            else:
                sig_cls = sig_cls_1

            try:
                sig = SM.create_connection(sig_cls, self.first_port[0], self.first_port[1],
                                     device_instance, port_label)
                connection=Connection(self.first_port[2], port, self.canvas.canvas, sig)
                self.first_port[2].set_connection(connection)
                port.set_connection(connection)
                connection.draw()
            except Exception as e:
                print("ERROR", e)
                SM.display_message("ERROR: " + str(e))
                self.clear()
                return False
            if port not in self.all_connections.keys():
                self.all_connections[port] = []
            if self.first_port[1] not in self.all_connections.keys():
                self.all_connections[self.first_port[2]] = []
            self.all_connections[port].append((self.first_port[2], connection))
            self.all_connections[self.first_port[2]].append((port, connection))
            print("Something should be in the dictionary")
            print(self.all_connections)
            self.first_port = None
            return True
        
    def disconnect(self, port):
        port.set_connection()
        print("WHAT DO WE HAVE HERE")
        print(self.all_connections)
        connection = self.all_connections[port][0][1]
        connection.remove()
        for other_port in self.all_connections[port]:
            SM.remove_connection(connection.signal)
            print(other_port)
            other_port[0].set_connection()
            self.all_connections[other_port[0]] = []
        self.all_connections[port] = []
        
        
