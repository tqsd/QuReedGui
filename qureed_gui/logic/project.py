import asyncio
from enum import IntEnum
import subprocess
import os
import platform
from pathlib import Path
import threading
import toml


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
        self._status=ProjectStatus.READY
        self.venv = None
        self.path = None
        self.base_path = None
        self.status_bar = None
        self.board = None

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if self.status_bar:
            self.status_bar.update_project_status(value)
        self._status = value

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
        print("New Project")
        print(path)
        directories = [
            f"{self.path}/custom",
            f"{self.path}/custom/devices",
            f"{self.path}/custom/signals",
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


        thread = threading.Thread(target=configure_project_pip, daemon=True)
        thread.start()
        if self.project_explorer:
            self.project_explorer.update_project()
        
    def open_project(self, path:str):
        print("Opening project")
        self.path = path
        conf = self.load_config()
        venv = str(Path(path) / ".venv")
        venv = conf.get("venv", venv)
        self.update_config({"venv":venv})
        print(venv)
        print(Path(venv).exists())
        if not Path(venv).exists():
            print("WHAT")
            self.create_venv()
            self.install()
        else:
            self.status = ProjectStatus.READY

        default_scheme = Path(path) / "main.json"
        if not default_scheme.exists():
            with open(str(default_scheme), "w") as file:
                file.write("{}")
        if self.project_explorer:
            self.project_explorer.update_project()
     
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
        print("VENV CREATION")
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
        print("Getting file tree")

        def list_files(directory):
            tree = []
            for entry in os.listdir(directory):
                full_path = os.path.join(directory, entry)
                print(entry)
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
            print(self.path)
            return []
        lst = list_files(self.path)
        print(lst)

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
