import sys
from enum import IntEnum
import subprocess
import os
import platform
from pathlib import Path
import threading
import shutil
import toml

from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler
from qureed_project_server import server_pb2

LMH = LogicModuleHandler()


class ProjectStatus(IntEnum):
    """
    Project Status Enum, Maybe we can deprecate this
    """
    NOT_READY = 0
    READY = 1

def get_wheels_path():
    """
    Determine the correct location of the wheels directory, 
    considering both development and bundled contexts.
    """
    if getattr(sys, 'frozen', False):  # Running in a PyInstaller bundle
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(sys.modules["__main__"].__file__).resolve().parent.parent

    wheels_path = base_path / "wheels" / platform.system().lower()
    if not wheels_path.exists():
        raise FileNotFoundError(f"Wheels directory not found: {wheels_path}")
    return wheels_path

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
            self.page = None
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

    def register_page(self, page):
        self.page = page

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

    def save_scheme(self, *_, **__):
        print("Trying to save scheme")
        BM = LMH.get_logic(LogicModuleEnum.BOARD_MANAGER)
        BM.save_scheme()
 

    def load_scheme(self, scheme: server_pb2.OpenBoardResponse):
        """
        Load devices and connections from the given scheme.

        Parameters:
        -----------
            scheme (server_pb2.OpenBoardResponse): The scheme to load
        """
        self.board.load_devices_bulk(scheme.devices)
        self.board.load_connections_bulk(scheme.connections)

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
        """
        New project creation
        """
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
            self.install("qureed_project_server", "qureed")
            venv = str(Path(path) / ".venv")
            self.venv = venv
            self.open_project(path)
            print("Configuration Finished")


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
        print("Opening project")
        SeM = LMH.get_logic(LogicModuleEnum.SELECTION_MANAGER)
        SvM = LMH.get_logic(LogicModuleEnum.SERVER_MANAGER)
        BM = LMH.get_logic(LogicModuleEnum.BOARD_MANAGER)
        if self.path is not None:
            SvM.stop()
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
        SeM.deselect_all()
        BM.close_scheme()
        SvM.start()
        SvM.connect_venv()
        self.is_opened = True
        
        if self.project_explorer:
            self.project_explorer.update_project()

        if self.device_menu:
            self.device_menu.activate()
        
        if self.page:
            self.page.title= f"QuReed - {self.path}"
            self.page.update()

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
            if platform.system() != "Windows"
            else Path(self.path) / ".venv" / "Scripts" / "python.exe"
        )
        print(f"Installing on {platform.system()}")

        # Path to the packaged wheels
        try:
            #wheels_path = files("qureed_gui") / "wheels" / platform.system().lower()
            wheels_path = get_wheels_path()
            print(wheels_path)
        except ModuleNotFoundError:
            wheels_path = None

        wheels_installed = set()
        print("Installing", wheels_path, " with  ", python_executable)
        try:
            # Install wheels first if they match the requested packages
            if wheels_path.exists():
                print(f"{wheels_path} exists")
                for package in packages:
                    # Find the specific wheel file for the package
                    print("Installing" ,package)
                    wheel_files = list(wheels_path.glob(f"{package.replace('-', '_')}*.whl"))
                    print(wheel_files)
                    if wheel_files:
                        self.display_message(f"Installing {package} from {wheel_files[0].name}...")
                        print(" ".join([str(python_executable), "-m",
                                "pip", "install", "--find-links", str(wheels_path), str(wheel_files[0])]))
                        subprocess.run(
                            [
                                str(python_executable), "-m",
                                "pip", "install", "--find-links", str(wheels_path), str(wheel_files[0])
                            ],
                            check=True
                        )
                        print(f"Installed: {package}")
                        wheels_installed.add(package)
            else:
                print(wheels_path)
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

    def get_list_of_all_existing_icons(self):
        """
        DEPRECATED
        """
        raise Exception("DEPRECATED")
        icon_path = Path(self.path) / "custom" / "icons"
        icon_list = os.listdir(icon_path)
        icon_list = [os.path.splitext(icon)[0] for icon in icon_list]
        return icon_list
