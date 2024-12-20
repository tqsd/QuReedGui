from pathlib import Path
import os
import sys
import importlib

from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler

LMH = LogicModuleHandler()
    
class ClassLoader:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ClassLoader, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self,"initialized"):
            self.logic_modules={}
            LMH.register(LogicModuleEnum.CLASS_LOADER, self)
            self.initialized=True

    def get_class_from_path(self, class_string):
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        base_path = PM.path

        *module_parts, class_name = class_string.split(".")
        module_path_str = "/".join(module_parts)

        if module_parts[0] == "custom":
            full_path = Path(base_path) / module_path_str
        else:
            site_packages = self.get_project_site_packages_dir()
            full_path = Path(site_packages) / module_path_str

        full_path = full_path.with_suffix(".py")

        if not full_path.exists():
            raise FileNotFoundError(f"Module file not found: {full_path}")

        # Module name
        module_name = ".".join(module_parts)

        # Check if the module is already loaded
        if module_name in sys.modules:
            module = sys.modules[module_name]
        else:
            # Load the module
            spec = importlib.util.spec_from_file_location(module_name, str(full_path))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

        # Retrieve the class
        if hasattr(module, class_name):
            return getattr(module, class_name)
        else:
            raise AttributeError(f"Class '{class_name}' not found in module '{module_name}'.")

    def get_project_site_packages_dir(self):
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        base_path =  PM.venv

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
        return Path(site_packages)

    def get_qureed_devices(self):
        """
        Gets all of the Qureed Devices from the
        existing qureed package in the .venv of the project.

        Returns:
           List[Tuple[class, mc]]
        """
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        if not PM.is_opened:
            return
        site_packages = self.get_project_site_packages_dir()
        print(site_packages)
        qureed_devices = site_packages / "qureed" / "devices"

        excluded_files = {"__init__.py", "port.py", "generic_device.py"}
    
        all_files = [
            path for path in qureed_devices.rglob("*")
            if path.is_file() and 
            path.name not in excluded_files and
            "__pycache__" not in path.parts
        ]

        processed_modules = []
        for path in all_files:
            class_name = ''.join(word.capitalize() for word in str(path.stem).split("_"))
            module_path = str(path.relative_to(site_packages)).replace(".py", "").replace("/", ".")
            mc = f"{module_path}.{class_name}"
            print(mc)
            print(module_path)
            print(class_name)
            try:
                cls = self.get_class_from_path(mc)
            except AttributeError as e:
                print(e)
                continue
            processed_modules.append((cls, mc))

        return processed_modules
