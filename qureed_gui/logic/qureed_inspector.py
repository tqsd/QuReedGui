import pkgutil
from pathlib import Path
import sys
import os
import importlib
import inspect

import qureed.devices

from .project import ProjectManager

PM = ProjectManager()

class QureedInspector:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(QureedInspector, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.find_qureed_gui_devices()
            PM.register_qureed_inspector(self)
            self.initialized = True

    def load_device_class(self, device_mc):
        if os.name == "nt":
            site_packages = os.join(PM.venv, "Lib", "site-packages")
        else:
            lib_path = os.path.join(PM.venv, "lib")
            python_versions = [folder for folder in os.listdir(lib_path) if folder.startswith("python")
                ]
            if not python_versions:
                raise FileNotFoundError("No Python Versions found")
            latest_version=sorted(python_versions, reverse=True)[0]
            site_packages=os.path.join(lib_path, latest_version, "site-packages")
        if not os.path.exists(site_packages):
            raise FileNotFoundError(f"site-packages directory not found in the virtual environment:{site_packages}")

        if site_packages not in sys.path:
            sys.path.insert(0, site_packages)

        spec = importlib.util.find_spec("qureed")
        if not spec:
            raise ImportError("Module qureed not found in the virtual environment") 

        print(device_mc)
        module_name = ".".join(device_mc.split(".")[:-1])
        print(module_name)
        print("------------------------")
        module = importlib.import_module(module_name)

        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module_name:
                return obj

    def find_qureed_gui_devices(self):
        base_module = qureed.devices
        gui_classes = []
        for _, module_name, is_pkg in pkgutil.walk_packages(base_module.__path__, base_module.__name__ + "."):
            try:
                module = importlib.import_module(module_name)
            except ImportError as e:
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

    def get_qureed_signals(self):
        if os.name == "nt":
            site_packages = os.join(PM.venv, "Lib", "site-packages")
        else:
            lib_path = os.path.join(PM.venv, "lib")
            python_versions = [folder for folder in os.listdir(lib_path) if folder.startswith("python")
                ]
            if not python_versions:
                raise FileNotFoundError("No Python Versions found")
            latest_version=sorted(python_versions, reverse=True)[0]
            site_packages=os.path.join(lib_path, latest_version, "site-packages")
        if not os.path.exists(site_packages):
            raise FileNotFoundError(f"site-packages directory not found in the virtual environment:{site_packages}")

        if site_packages not in sys.path:
            sys.path.insert(0, site_packages)

        spec = importlib.util.find_spec("qureed")
        if not spec:
            raise ImportError("Module qureed not found in the virtual environment")

        signals_module = importlib.import_module("qureed.signals")

        signal_classes = inspect.getmembers(signals_module, inspect.isclass)
        return signal_classes


    def get_qureed_icons(self):
        if os.name == "nt":
            site_packages = os.join(PM.venv, "Lib", "site-packages")
        else:
            lib_path = os.path.join(PM.venv, "lib")
            python_versions = [folder for folder in os.listdir(lib_path) if folder.startswith("python")
                ]
            if not python_versions:
                raise FileNotFoundError("No Python Versions found")
            latest_version=sorted(python_versions, reverse=True)[0]
            site_packages=os.path.join(lib_path, latest_version, "site-packages")
        if not os.path.exists(site_packages):
            raise FileNotFoundError(f"site-packages directory not found in the virtual environment:{site_packages}")
        icon_path = Path(site_packages) / "qureed" / "gui" / "assets"
        return [str(file) for file in icon_path.glob("*.png")]

        
    def get_new_device_template_path(self):
        if os.name == "nt":
            site_packages = os.join(PM.venv, "Lib", "site-packages")
        else:
            lib_path = os.path.join(PM.venv, "lib")
            python_versions = [folder for folder in os.listdir(lib_path) if folder.startswith("python")
                ]
            if not python_versions:
                raise FileNotFoundError("No Python Versions found")
            latest_version=sorted(python_versions, reverse=True)[0]
            site_packages=os.path.join(lib_path, latest_version, "site-packages")
        if not os.path.exists(site_packages):
            raise FileNotFoundError(f"site-packages directory not found in the virtual environment:{site_packages}")
        template_path = Path(site_packages) / "qureed" / "templates"
        return template_path
