from qureed_gui.logic.project_manager import ProjectManager
from qureed_gui.logic.keyboard import KeyboardEventDispatcher
from qureed_gui.logic.board_manager import BoardManager
from qureed_gui.logic.board_helpers import get_device_control, get_device_icon
from qureed_gui.logic.connection_manager import ConnectionManager
from qureed_gui.logic.selection_manager import SelectionManager
from qureed_gui.logic.server_manager import ServeManager

PM = ProjectManager()
KED = KeyboardEventDispatcher()
BM = BoardManager()
CM = ConnectionManager()
SeM = SelectionManager()
SM = ServeManager()
