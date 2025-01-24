from .project import ProjectManager
from .keyboard import KeyboardEventDispatcher
from .board_manager import BoardManager
from .board_helpers import get_device_control, get_device_icon, get_device_icon_absolute_path
from .connection_manager import ConnectionManager
from .simulation_manager import SimulationManager
from .class_loader import ClassLoader
from .selection_manager import SelectionManager
from .server_manager import ServeManager

PM = ProjectManager()
KED = KeyboardEventDispatcher()
BM = BoardManager()
CM = ConnectionManager()
SM = SimulationManager()
CL = ClassLoader()
SeM = SelectionManager()
SvM = ServeManager()
