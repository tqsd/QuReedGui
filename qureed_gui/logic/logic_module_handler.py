import sys
from enum import StrEnum
import traceback
import os
print(f"[LMH] PID: {os.getpid()}, FILE: {__file__}")

class LogicModuleEnum(StrEnum):
    """
    LogicModuleEnum enums all of the 
    logic modules
    """
    PROJECT_MANAGER = "project_manager"
    BOARD_MANAGER = "board_manager"
    KEYBOARD_DISPATCHER = "board_dispatcher"
    CONNECTION_MANAGER = "connection_manager"
    SELECTION_MANAGER = "selection_manager"
    SIMULATION_MANAGER = "simulation_manager"
    SERVER_MANAGER = "server_manager"

class LogicModuleHandler:
    """
    LogicModuleHandler (Singleton) keeps track of the logic modules and
    passes the reference to the correct logic through the
    get_logic method

    Attributes:
    -----------
    modules (dict): Dictionary of all registered modules
    initialized (bool): Initialization flag for the Singleton Pattern

    Methods:
    --------
    register: Registers the module
    get_logic: Gets the logic

    Example:
    --------
        >>> SM = LogicModuleHangler().get_logic(
        >>>     LogicModuleEnum.SERVER_MANAGER
        >>> )

    Notes:
    ------
    Individual logic modules are registered individually in their 
    initialization methods.
    """

    def __new__(cls, *args, **kwargs):
        if hasattr(cls, "_instance"):
            return cls._instance

        key = "qureed_gui.logic.logic_module_handler._singleton"
        if key in sys.modules:
            cls._instance = sys.modules[key]
        else:
            cls._instance = super().__new__(cls)
            sys.modules[key] = cls._instance
            cls._instance.modules = {}
            cls._instance.initialized = True
            print("Initialized singleton LogicModuleHandler")
            traceback.print_stack()

        return cls._instance
    def __init__(self):
        pass

    def register(self, module_type:LogicModuleEnum, module:type):
        """
        Register the module with the LogicModuleHandler.
        This should be called from within the __init__ method
        of the individual Logic units

        Parameters:
        -----------
        module_type (LogicModuleEnum): The type of the module being registered
        module (type): Actual instance of the module
        """
        self.modules[module_type]=module

    def get_logic(self, module_type:LogicModuleEnum):
        """
        Gets the instance of the specific logic module.

        Parameters:
        -----------
        module_type (LogicModuleEnum): Requested logic module
        """
        try:
            return self.modules[module_type]
        except Exception as e:
            print(self)
            
        
