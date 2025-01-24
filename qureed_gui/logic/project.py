import asyncio
import sys
import inspect
import importlib
from enum import IntEnum
import subprocess
import json
import os
import re
import platform
from pathlib import Path
import threading
import toml
import shutil
from jinja2 import Environment,FileSystemLoader

from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler

LMH = LogicModuleHandler()


class ProjectStatus(IntEnum):
    NOT_READY = 0
    READY = 1

class ProjectManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ProjectManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self,"initialized"):
            self.is_opened = False
            self._status=ProjectStatus.READY
            self.venv = None
            self.path = None
            self.base_path = None
            self.status_bar = None
            self.board = None
            self.device_menu = None
            self.inspector = None
            LMH.register(LogicModuleEnum.PROJECT_MANAGER, self)
            self.initialized=True

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if self.status_bar:
            self.status_bar.update_project_status(value)
        self._status = value

    def register_device_menu(self, device_menu):
        self.device_menu = device_menu

    def register_qureed_inspector(self, inspector):
        self.inspector = inspector

    def serialize_properties(self, properties):
        if isinstance(properties, dict):
            return {k:self.serialize_properties(v) for k,v in properties.items()}
        elif isinstance(properties, type):
            return properties.__name__
        elif isinstance(properties,object):
            return str(properties)
        return properties

    def deserialize_properties(self, properties, custom_type_mapping=None):
        if custom_type_mapping is None:
            custom_type_mapping = {}

        default_type_mapping = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "NoneType": type(None),
        }

        # Combine default and custom type mappings
        type_mapping = {**default_type_mapping, **custom_type_mapping}

        def deserialize_value(value):
            if isinstance(value, dict):
                # Recursively deserialize nested dictionaries
                return {k: deserialize_value(v) for k, v in value.items()}
            elif isinstance(value, str) and value in type_mapping:
                # Convert type name strings back into type objects
                return type_mapping[value]
            return value

        return deserialize_value(properties)

    def save_scheme(self, *args, **kwargs):
        from components.device import Device
        from components.variable import Variable
        from logic import SimulationManager, BoardManager
        from components.board_component import BoardComponent
        SM = SimulationManager()
        BM = BoardManager()
        if not BM.opened_scheme:
            return
        json_descriptor = {
            "devices": [],
            "connections": [],
        }
        for device in BM.device_controls:
            if not isinstance(device, BoardComponent):
                continue
            dev_class = f"{device.device_class.__module__}.{device.device_class.__name__}"
            if isinstance(device, (Device,Variable)):
                properties = self.serialize_properties(device.device_instance.properties)
                print(device.device_mc)

                dev_descriptor = {
                    "device":device.device_mc,
                    "location":(device.left, device.top),
                    "uuid":device.device_instance.ref.uuid,
                    "properties":properties
                    }
            json_descriptor["devices"].append(dev_descriptor)
        for s in SM.signals:
            signal = {
                "signal":f"{type(s).__module__}.{type(s).__name__}",
                "conn":[]
                }
            for p in s.ports:
                port={
                    "device_uuid":p.device.ref.uuid,
                    "port":p.label
                    }
                signal["conn"].append(port)
            json_descriptor["connections"].append(signal)

        with open(f"{self.path}/{BM.opened_scheme}", "w") as json_file:
            json.dump(json_descriptor, json_file, indent=4)

        self.display_message(f"Scheme {BM.opened_scheme} saved")

    def load_scheme(self, scheme):
        BM = LMH.get_logic(LogicModuleEnum.BOARD_MANAGER)
        CL = LMH.get_logic(LogicModuleEnum.CLASS_LOADER)

        # Get the devices from the json
        with open(f"{self.path}/{scheme}", "r") as f:
            data = json.load(f)

        if "devices" not in data.keys():
            return
        devices = []
        for d in data["devices"]:
            device = {
                "class": CL.get_class_from_path(d["device"]),
                "device_mc":d["device"],
                "location":d["location"],
                "properties":self.deserialize_properties(d["properties"]),
                "kwargs":{
                    "uid":d["uuid"],
                      }
                }
            devices.append(device)
        self.board.load_devices_bulk(devices)
        if "connections" in data.keys():
            self.board.load_connections_bulk(data["connections"])

    def get_device_class(self, device_mc):
        device_mc = device_mc.split("/")
        class_name = device_mc[-1]
        device_path = device_mc[:-1]
        if "custom" in device_mc:
            return self.load_class_from_file("/".join(device_path))
        else:
            return self.inspector.load_device_class(".".join(device_mc))
        

    def load_config(self):
        """Load the existing configuration from a TOML file."""
        config_path = Path(self.path) / "config.toml"
        if config_path.exists():
            with open(config_path, "r") as file:
                return toml.load(file)
        return {}

    def update_config(self, updates):
        """
        Update the configuration file with new values.

        Args:
        updates (dict): A dictionary containing configuration updates.
        """

        config_path = Path(self.path) / "config.toml"
        if config_path.is_file():
            # Load existing configuration
            try:
                with config_path.open("r") as f:
                    config = toml.load(f)
            except toml.TomlDecodeError as e:
                config = {}
            except Exception as e:
                config = {}
        else:
            config = {}

        # Update the configuration with new values
        for key, value in updates.items():
            if isinstance(value, list):
                # Ensure no duplicate entries in lists
                existing_items = set(config.get(key, []))
                updated_items = existing_items.union(set(value))
                config[key] = list(updated_items)
            else:
                # Update or add new key-value pairs
                config[key] = value

        # Write the updated configuration back to the file
        with open(config_path, "w") as file:
            toml.dump(config, file)

    def new_project(self, path:str):
        if not path:
            return
        self._status=ProjectStatus.NOT_READY
        self.path = path
        directories = [
            f"{self.path}/custom",
            f"{self.path}/custom/devices",
            f"{self.path}/custom/signals",
            f"{self.path}/custom/icons",
            f"{self.path}/logs",
            f"{self.path}/plots",
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            if "custom" in directory:  # Check if it's a package directory
                init_file_path = os.path.join(directory, "__init__.py")
                with open(init_file_path, "w") as init_file:
                    init_file.write(
                        "# This file is required to make Python treat the directories as containing packages.\n"
                    )

        with open(f"{path}/main.json", "w") as file:
            file.write("{}")  # Empty JSON object as placeholder

        self.update_config({"venv":str(Path(self.path)/".venv")})
        def configure_project_pip():
            self.create_venv()
            (self.path)
            self.install("photon_weave")
            self.install("git+ssh://git@github.com/tqsd/qureed.git@master")
            venv = str(Path(path) / ".venv")
            self.venv = venv


        self.is_opened=True
        if self.device_menu:
            self.device_menu.activate()
        thread = threading.Thread(target=configure_project_pip, daemon=True)
        thread.start()
        if self.project_explorer:
            self.project_explorer.update_project()
        
    def open_project(self, path:str):
        """
        Opens an existing project and
        start a server in the project and connect to it
        """
        CL = LMH.get_logic(LogicModuleEnum.CLASS_LOADER)
        SvM = LMH.get_logic(LogicModuleEnum.SERVER_MANAGER)
        self.path = path
        conf = self.load_config()
        venv = str(Path(path) / ".venv")
        venv = conf.get("venv", venv)
        self.update_config({"venv":venv})
        self.venv = venv
        if not Path(venv).exists():
            self.create_venv()
            self.install()
        else:
            self.status = ProjectStatus.READY

        
        SvM.start()
        SvM.connect_venv()
        return
        self.is_opened = True

        CL.load_module_from_venv("qureed")

        default_scheme = Path(path) / "main.json"
        if not default_scheme.exists():
            with open(str(default_scheme), "w") as file:
                file.write("{}")
        if self.project_explorer:
            self.project_explorer.update_project()

        if self.device_menu:
            self.device_menu.activate()
        
     
    def install(self,*packages:str):
        self.display_message(f"Installing packages {packages}", timer=False)
        self.status=ProjectStatus.NOT_READY
        if not packages:
            config_path = Path(self.path) / "config.toml"
            if config_path.exists():
                config = toml.load(config_path)
                packages = config.get("packages", [])
        else:
            if packages:
                self.update_config({"packages": list(packages)})
        python_executable = (
            Path(self.path) / ".venv" / "bin" / "python"
            if platform.system() != "windows"
            else Path(self.path) / ".venv" / "Scripts" / "python.exe"
        )
        try:
            subprocess.run(
                [
                str(python_executable), "-m",
                "pip", "install", *packages
                ]
            )
            
        except subprocess.CalledProcessError as e:
            print(f"Command failed with return code {e.returncode}")
            print("Error output:")
            print(e.stderr)
        except FileNotFoundError:
            print("Command not found. Please ensure the command is correct and installed.")


        self.display_message(f"Packages installed {packages}")
        self.status=ProjectStatus.READY

    def create_venv(self):
        venv = self.load_config()["venv"]
        self.display_message(f"Creating new virtual env ({venv})", timer=False)
        path = self.path
        self.status=ProjectStatus.NOT_READY
        python_command = "python3" if platform.system() != "Windows" else "python"
        subprocess.run(
            [python_command, "-m", "venv", venv], check=True
        )
        self.status=ProjectStatus.READY
        self.display_message(f"Virtual env created ({venv})")

    def register_status_bar(self, status_bar):
        """
        Register status bar, so the information could be displayd
        """
        self.status_bar = status_bar

    def register_project_explorer(self, project_explorer):
        self.project_explorer = project_explorer

    def register_board(self, board):
        self.board = board

    def display_message(self, message:str, timer=True):
        if self.status_bar:
            self.status_bar.set_message(message, timer)

    def get_file_tree(self):
        """
        Gets the file tree of the project
        """
        def list_files(directory):
            tree = []
            for entry in os.listdir(directory):
                full_path = os.path.join(directory, entry)
                if entry in [
                    "None",
                    "__init__.py",
                    "__pycache__",
                    ".git",
                    ".gitignore",
                    ".venv"
                ]:
                    continue
                if "~" in entry or entry.startswith("."):
                    continue
                if os.path.isdir(full_path):
                    if entry == ".venv":
                        continue
                    relative_path = os.path.relpath(full_path, self.path)
                    tree.append({relative_path: list_files(full_path)})
                else:
                    relative_path = os.path.relpath(full_path, self.path)
                    tree.append(relative_path)
            return tree

        if self.path is None:
            return []
        lst = list_files(self.path)

        def sort_files_folders(items):
            def sort_key(item):
                if isinstance(item, str):
                    return (0, item)  # File
                elif isinstance(item, dict):
                    return (1, next(iter(item)))  # Folder
                return (2, None)  # Fallback case, should not occur

            # Sort items at the current level
            items.sort(key=sort_key)

            # Recursively sort directories
            for item in items:
                if isinstance(item, dict):
                    for key in item:
                        sort_files_folders(item[key])

        sort_files_folders(lst)
        return lst

    def add_icon(self, icon_path, icon_name):
        # Define the destination folder
        destination_folder = Path(self.path) / "custom" / "icons"
        destination_folder.mkdir(parents=True, exist_ok=True)  # Create folder if it doesn't exist
        
        # Extract the file extension from the source file
        file_extension = os.path.splitext(icon_path)[1]  # e.g., ".jpg" or ".png"
        
        # Create the destination file path
        destination_file = destination_folder / f"{icon_name}{file_extension}"
        
        try:
            # Copy the file to the destination
            shutil.copy(icon_path, destination_file)
            if self.project_explorer:
                self.project_explorer.update_project()
            return True, None
        except FileNotFoundError:
            return False, f"Error: Source file not found: {icon_path}"
        except PermissionError:
            return False, f"Error: Permission denied while copying to {destination_folder}"
        except Exception as e:
            return False, f"An unexpected error occurred: {e}"

    def remove_icon(self, icon):
        pass

    def get_list_of_all_existing_icons(self):
        icon_path = Path(self.path) / "custom" / "icons"
        icon_list = os.listdir(icon_path)
        icon_list = [os.path.splitext(icon)[0] for icon in icon_list]
        return icon_list

    def get_all_signals(self):
        pass

    def new_device(self, name, tags, in_ports, out_ports, icon,properties):
        CL = LMH.get_logic(LogicModuleEnum.CLASS_LOADER)
        templates_module= CL.load_module_from_venv("qureed.templates")
        template_dir = os.path.dirname(os.path.abspath(templates_module.__file__))
        print(template_dir)
        template_path = self.inspector.get_new_device_template_path()
        env=Environment(loader=FileSystemLoader(template_path))
        template=env.get_template("device_template.jinja")
        gui_name = name
        class_name = name.title().replace(" ", "")
        file_name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower().replace(" ", "")
        file_name += ".py"
        tags = [tag.strip().lower() for tag in tags.split(",")]
        device=template.render(
            name=name,
            class_name=class_name,
            tags=tags,
            input_ports=in_ports,
            output_ports=out_ports,
            gui_icon=icon,
            properties=properties
            )
        # Save the new device
        file_location = Path(self.path) / "custom" / "devices" / file_name
        print(device)
        with open(str(file_location), "w") as f:
            f.write(device)

        self.display_message(f"Device Created: {file_location}")
        self.project_explorer.update_project()

    def load_class_from_path(self, module_path:str):
        CL = LMH.get_logic(LogicModuleEnum.CLASS_LOADER)
        return CL.get_class_from_path(module_path)

    def load_class_from_file(self, relative_module_path):
        CL = LMH.get_logic(LogicModuleEnum.CLASS_LOADER)
        CL.get_class_from_path(relative_module_path)
        # Construct the full path to the module file
        full_path = Path(self.path) / relative_module_path

        # Resolve the path to ensure it's absolute and normalize any irregular path components
        full_path = full_path.resolve()
        if not full_path.exists():
            raise FileNotFoundError(f"No such file: {full_path}")

        # Debug prints for verification
        if not full_path.is_relative_to(self.path):
            raise ValueError("Attempted to access a file outside of the base directory")
     
        # Convert the full path to a dot-separated module path relative to the base path
        module_str = (
            str(full_path.relative_to(self.path)).replace("/", ".").replace("\\", ".")
        )

        # Only strip the '.py' suffix if it is at the end
        if module_str.endswith(".py"):
            module_str = module_str[:-3]

        class_name = str(Path(full_path).name)[:-3]
        class_name = "".join(x.capitalize() or "_" for x in class_name.split("_"))
        # Dynamically import the module

        base_path = str(Path(self.path).resolve())
        if base_path not in sys.path:
            sys.path.append(base_path)

        module = importlib.import_module(module_str)

        # Inspect the module and return the first found class
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if name == class_name and obj.__module__ == module.__name__:
                return obj
