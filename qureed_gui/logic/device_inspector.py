import pkgutil
import importlib
import inspect

import qureed.devices

class DeviceInspector:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DeviceInspector, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.find_qureed_gui_devices()


    def find_qureed_gui_devices(self):
        base_module = qureed.devices
        gui_classes = []
        for _, module_name, is_pkg in pkgutil.walk_packages(base_module.__path__, base_module.__name__ + "."):
            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
                print(f"Failed to import {module_name}: {e}")
                continue
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # Check if the class is defined in this module (not imported)
                if obj.__module__ == module_name:
                    # Check if the class has a gui_name property
                    if hasattr(obj, "gui_name"):
                        if isinstance(obj.gui_name, str):
                            gui_classes.append(obj)
        def simple_map(x):
            tags = x.gui_tags if hasattr(x, "gui_tags") else []
            return (x.gui_name, tags, x)
        self.qureed_devices = list(map(simple_map, gui_classes))
