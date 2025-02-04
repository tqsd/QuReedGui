from .project import ProjectManager
from .keyboard import KeyboardEventDispatcher
from .board_manager import BoardManager
from .board_helpers import get_device_control, get_device_icon
from .connection_manager import ConnectionManager
from .class_loader import ClassLoader
from .selection_manager import SelectionManager
from .server_manager import ServeManager

PM = ProjectManager()
KED = KeyboardEventDispatcher()
BM = BoardManager()
CM = ConnectionManager()
CL = ClassLoader()
SeM = SelectionManager()
SM = ServeManager()
