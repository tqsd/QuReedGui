"""
Manages the connections between the ports
"""
from __future__ import annotations
import typing
from qureed_gui.logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler

if typing.TYPE_CHECKING:
    from qureed_gui.components.ports import Port

LMH = LogicModuleHandler()


class ConnectionManager:
    """
    Connection Manger, manages the connecting and disconnecting of
    the devices currently on the board.
    """
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
        pass

    def connect_action(self, port) -> bool:
        """
        Connect action saves the parameters of the clicked port,
        if another port was clicked before than it attempts to
        connect the ports.

        Parameters:
        -----------
        port
        """
        if self.first_port is None:
            self.first_port = port
            return True
        else:
            SvM = LMH.get_logic(LogicModuleEnum.SERVER_MANAGER)
            response = SvM.connect_devices(
                device_uuid_1=self.first_port.device.uuid,
                device_port_1=self.first_port.port_label,
                device_uuid_2=port.device.uuid,
                device_port_2=port.port_label
                )

            first_port = self.first_port
            self.first_port = None
            if response.status == "success":
                self.load_connection(first_port, port)
                return True
            return False

    def load_connection(self, port1, port2):
        """
        Renders the connection, which already exist in the backend
        """
        from components.connection import Connection
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
    
    def deregister_connection(self, connection):
        try:
            self.all_connections[connection.port_a].remove((connection.port_b, connection))
            self.all_connections[connection.port_b].remove((connection.port_a, connection))
        except Exception as e:
            print("Error in degeristering connection", e)
        
    def disconnect(self, port:Port):
        """
        Disconnects all signals from the given port
        """
        SvM = LMH.get_logic(LogicModuleEnum.SERVER_MANAGER)

        if port not in self.all_connections.keys():
            return
        if len(self.all_connections[port]) == 0:
            return

        connections_to_remove = [
            conn for p,conn in self.all_connections[port]
            ]

        for conn in connections_to_remove:
            response = SvM.disconnect_devices(
                conn.port_a.device.uuid,
                conn.port_a.port_label,
                conn.port_b.device.uuid,
                conn.port_b.port_label,
                )
            if response.status == "success":
                conn.remove()
                conn.port_a.set_connection()
                conn.port_b.set_connection()
                self.deregister_connection(conn)
