from qureed_gui.logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler

LMH = LogicModuleHandler()

class SelectionManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SelectionManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self,"initialized"):
            LMH.register(LogicModuleEnum.SELECTION_MANAGER, self)
            self.selected_components = []
            self.device_settings = None
            self.initialized=True

    def register_device_settings(self, device_settings):
        self.device_settings = device_settings

    def new_selection(self, components):
        KED = LMH.get_logic(LogicModuleEnum.KEYBOARD_DISPATCHER)
        if not KED.SHIFT:
            for component in self.selected_components:
                component.deselect()
            self.selected_components = components
            for component in self.selected_components:
                component.select()
        else:
            self.add_to_selection(components)
        if len(self.selected_components)==1:
            self.device_settings.display_settings(self.selected_components[0])
        else:
            self.device_settings.hide_settings()
            
    def add_to_selection(self, components):
        self.selected_components.extend(components)
        for component in self.selected_components:
            component.select()

    def deselect_all(self):
        for component in self.selected_components:
            try:
                component.deselect()
            except Exception:
                print("Component doesn't exist anymore")
        self.selected_components = []
        self.device_settings.hide_settings()
