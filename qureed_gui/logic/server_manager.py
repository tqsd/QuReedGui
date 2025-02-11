"""
This module impements server management class, which 
also manages the communication with the server
"""
import inspect
import uuid
import asyncio
import time
import socket
import subprocess
import sys
import threading
from pathlib import Path
from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler
import qureed_project_server.server_pb2 as MSG
from qureed_project_server.client import GrpcClient


LMH = LogicModuleHandler()

def is_port_free(port):
    """
    Bind temporarily to a port to check if it's free.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f"Testing availability 127.0.0.1:{port}")
            return s.connect_ex(("127.0.0.1", port)) != 0
    except OSError:
        return False

def find_unused_port(start=50000, end=60000):
    """
    Find an unused port in the specified range.
    
    Parameters:
    - start (int): Starting port number.
    - end (int): Ending port number.
    
    Returns:
    - int: An unused port.
    """
    for port in range(start, end):
        if is_port_free(port):
            print(f"Availability confirmed 127.0.0.1:{port}")
            return port  # Return the reserved port
    raise RuntimeError("No unused port found in the specified range.")


class ServeManager:
    """
    ServerManager (Singleton) manages the project server and the
    communication with it. The created server is listening on the
    localhost (127.0.0.1) interface.

    Attributes:
    -----------
    server_process (Optional[Subprocess]): Server subprocess after it was
       created
    port (int): The port over which server and main process communicate
    client (GrpcClient): The Grpc Client, which is managing the gRPC protocol
    loop (asyncion event loop): The asyncio event loop, so that we 
        can work with asynchronous tasks
    grpc_thread (Thread): thread running the loop (asyncio)
    initialized (bool): Initialization flag for the Singleton Pattern

    Methods:
    --------
    is_server_ready(): Checks if the server is ready
    poll_server_output(): Polls and displays stdout and stderr of the server
        subprocess
    start(): Starts the server and related processes
    run_in_loop(): Asyncio utility method
    interrupt_signal_hook(): Hook to stop the server
    ... the rest are the communication calls
    
    Examples:
    ---------
    Example of using this class in the project:
        >>> from qureed_gui.logic.logic_module_hangler import (
        >>>     LogicModuleHandler, LogicModuleEnum
        >>> )
        >>> SM = LogicModuleHandler().get_logic(
        >>>     LogicModuleEnum.SERVER_MANAGER
        >>> )
    
    Notes:
    ------
    This Singleton instance is initiated once in the `logic/__init__.py`
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ServeManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self,"initialized"):
            self.server_process = None
            self.port = None
            self.client = None
            self.loop = None
            self.grpc_thread = None
            LMH.register(LogicModuleEnum.SERVER_MANAGER, self)
            self.initialized=True

    def is_server_ready(self) -> bool:
        """
        Check if the server is ready to accept connections.

        Returns:
        bool: True if the server was succesfully created
        """
        try:
            with socket.create_connection(("localhost", self.port), timeout=1):
                return True
        except OSError:
            return False

    def poll_server_output(self):
        """
        Method that polls the server ouput and displays it in the
        stdout of the gui process.
        """
        if self.server_process:
            def poll(process):
                for line in iter(process.stdout.readline, ""):
                    print(f"[SERVER STDOUT] {line.strip()}")
                for line in iter(process.stderr.readline, ""):
                    print(f"[SERVER STDERR] {line.strip()}")

            output_thread = threading.Thread(target=poll, args=(self.server_process,), daemon=True)
            output_thread.start()

    def start(self) -> None:
        """
        Starts the project specific server as a subprocess.
        Then it starts the thread which polls the server stdout
        and stderr. After the connection to the server can be
        established it starts grpc thread.

        """
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)

        python_executable = Path(PM.venv) / "bin" / "python" if sys.platform != "win32" else Path(PM.venv) / "Scripts" / "python.exe"
        python_executable = Path(PM.venv) / (
            "bin/python" if sys.platform != "win32" else "Scripts/python.exe"
        )


        if not python_executable.exists():
            raise FileNotFoundError(
                f"Python executable not found in virtual environment: {python_executable}"
                )

        # Find an unused port
        self.port = find_unused_port()
        # self.port = 60000

        # Command to start the server
        command = [str(python_executable), "-u", "-m", 
                   "qureed_project_server.server", "--port", str(self.port)]
        PM.display_message("Starting server:" + " ".join(command))
        try:
            # Start the server process
            self.server_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                encoding="utf-8"
                )
            print(f"Server started with PID {self.server_process.pid} on interface 127.0.0.1:{self.port},  {self.server_process.poll()}")
            self.poll_server_output()


            # Poll for readiness
            for _ in range(20):  # Wait up to 10 seconds
                time.sleep(0.5)
                if self.is_server_ready():
                    break
            else:
                raise TimeoutError("Server did not become ready in time.")
            
        except Exception as e:
            PM.display_message("Failed to start the server: {e}")
            return

        PM.display_message(f"Project server started succesfully on port: {self.port}")
        # Define a function to start the asyncio event loop in a new thread
        def grpc_thread_func():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()

        # Start the gRPC thread if not already running
        if self.grpc_thread is None:
            self.grpc_thread = threading.Thread(target=grpc_thread_func, daemon=True)
            self.grpc_thread.start()

        # Wait for the event loop to initialize
        while self.loop is None:
            pass

        # Initialize the gRPC client asynchronously
        async def init_client():
            self.client = GrpcClient(f"localhost:{self.port}")

        # Submit the init_client coroutine to the running event loop
        future = asyncio.run_coroutine_threadsafe(init_client(), self.loop)
        try:
            # Wait for the client initialization to complete
            future.result()
        except Exception as e:
            print(f"Error initializing gRPC client: {e}")

    def run_in_loop(self, coro):
        """
        Utility method to run a coroutine in the correct event loop.

        Args:
            coro (coroutine): The coroutine to execute.

        Returns:
            Any: The result of the coroutine.

        Raises:
            Exception: Any exception raised by the coroutine is propagated.
        """
        if self.loop is None:
            raise RuntimeError("Event loop is not initialized. Did you call start()?")

        # Submit the coroutine to the loop and wait for the result
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()

    def interrupt_signal_hook(self, *_, **__):
        """
        Interrupt signal hook, stops the server when 
        activated. Must be registered.
        """
        print("Interrupt received! Stopping the server...")
        self.stop()
        sys.exit(0)

    def connect_venv(self):
        """
        Connect to the virtual environment using the gRPC client.
        """
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)

        async def connect():
            response = await self.client.call(
                self.client.venv_stub.Connect,
                MSG.VenvConnectRequest(venv_path=str(PM.venv))
            )
        self.run_in_loop(connect())

    def open_scheme(self, scheme):
        """
        Request to open a scheme, receives the scheme elements.
        """
        async def load_scheme():
            response = await self.client.call(
                self.client.qm_stub.OpenBoard,
                MSG.OpenBoardRequest(board=scheme)
                )
            return response
        return self.run_in_loop(load_scheme())

    def get_device(self, path: str):
        """
        Get the module class string given a path of the module
        """
        async def get_device():
            response = await self.client.call(
                self.client.qm_stub.GetDevice,
                MSG.GetDeviceRequest(module_path=path)
                )
            return response
        return self.run_in_loop(get_device())

    def save_scheme(self, board, devices=[], connections=[]):
        """
        Requests the saving of the scheme
        """
        async def save_scheme():
            response = await self.client.call(
                self.client.qm_stub.SaveBoard,
                MSG.SaveBoardRequest(
                    board=board,
                    devices=devices,
                    connections=connections
                    )
                )
            return response
        return self.run_in_loop(save_scheme())

    def update_device(self, device):
        """
        TODO
        """

    def connect_devices(self, device_uuid_1, device_port_1, device_uuid_2, device_port_2):
        async def connect_devices():
            response = await self.client.call(
                self.client.qm_stub.ConnectDevices,
                MSG.ConnectDevicesRequest(
                    device_uuid_1=device_uuid_1,
                    device_port_1=device_port_1,
                    device_uuid_2=device_uuid_2,
                    device_port_2=device_port_2
                    )
                )
            return response
        return self.run_in_loop(connect_devices())

    def disconnect_devices(self, device_uuid_1, device_port_1, device_uuid_2, device_port_2):
        async def disconnect_devices():
            response = await self.client.call(
                self.client.qm_stub.DisconnectDevices,
                MSG.DisconnectDevicesRequest(
                    device_uuid_1=device_uuid_1,
                    device_port_1=device_port_1,
                    device_uuid_2=device_uuid_2,
                    device_port_2=device_port_2
                    )
                )
            return response
        return self.run_in_loop(disconnect_devices())

    def add_device(self, device):
        async def get_device():
            response = await self.client.call(
                self.client.qm_stub.AddDevice,
                MSG.AddDeviceRequest(device=device)
                )
            return response
        return self.run_in_loop(get_device())

    def remove_device(self, device_uuid):
        async def remove_device():
            response = await self.client.call(
                self.client.qm_stub.RemoveDevice,
                MSG.RemoveDeviceRequest(device_uuid=device_uuid)
                )
            return response
        return self.run_in_loop(remove_device())

    def get_all_devices(self):
        async def get_all_devices():
            response = await self.client.call(
                self.client.qm_stub.GetDevices,
                MSG.GetDevicesRequest()
                )
            return response
        return self.run_in_loop(get_all_devices())

    def get_all_icons(self):
        async def get_all_icons():
            response = await self.client.call(
                self.client.qm_stub.GetIcons,
                MSG.GetIconRequest()
                )
            return response
        return self.run_in_loop(get_all_icons())

    def get_all_signals(self):
        async def get_all_signals():
            response = await self.client.call(
                self.client.qm_stub.GetSignals,
                MSG.GetSignalsRequest()
                )
            return response
        return self.run_in_loop(get_all_signals())

    def generate_new_device(self, device):
        async def generate_new_device():
            response = await self.client.call(
                self.client.qm_stub.GenerateDevices,
                MSG.GenerateDeviceRequest(device=device)
                )
            return response
        return self.run_in_loop(generate_new_device())

    def update_device_properties(self, device:MSG.Device):
        async def update_device_properties():
            response = await self.client.call(
                self.client.qm_stub.UpdateDeviceProperties,
                MSG.UpdateDevicePropertiesRequest(
                    device=device))
            return response
        return self.run_in_loop(update_device_properties())

    def stop(self, timeout=5):
        """
        Stops the server process gracefully and forces termination if it doesn't stop within the timeout.

        Args:
            timeout (int): Time in seconds to wait for the server to terminate gracefully.
        """
        if self.server_process is None:
            return
        async def terminate():
            response = await self.client.call(
                self.client.server_stub.Terminate,
                MSG.TerminateRequest()
            )
            return response

        try:
            # Attempt to terminate the server gracefully
            response = self.run_in_loop(terminate())
            print(f"Server termination response: {response}")
        except Exception as e:
            print(f"Error during graceful termination request: {e}")

        # Wait for the process to terminate gracefully
        if self.server_process and self.server_process.poll() is None:  # Check if process is still running
            print(f"Waiting up to {timeout} seconds for the server to stop...")
            for _ in range(timeout * 10):  # Check every 100ms
                if self.server_process.poll() is not None:
                    print("Server terminated gracefully.")
                    break
                time.sleep(0.1)
            else:
                # Force termination if the server is still running after timeout
                print("Server did not terminate in time. Forcing termination...")
                self.server_process.terminate()

        # Ensure the process is fully terminated
        self.server_process.wait()
        print("Server stopped.")

    def start_simulation(self, scheme:str, simulation_id):
        async def start_simulation():
            response = await self.client.call(
                self.client.simulation_stub.StartSimulation,
                MSG.StartSimulationRequest(
                    scheme_path=str(scheme),
                    simulation_id=str(simulation_id)
                )
            )
            return response

        if self.loop is not None:
            self.loop.call_soon_threadsafe(
                asyncio.create_task, 
                self.subscribe_to_logs(simulation_id=simulation_id)
            )
        
        return self.run_in_loop(start_simulation())

    async def subscribe_to_logs(self, simulation_id):
        request = MSG.SimulationLogStreamRequest()
        print("SUBSCRIBING TO THE LOGS")
        try:
            async for response in self.client.simulation_stub.SimulationLogStream(request):
                print("ANYTHING?")
                print("Received log", response.log)
        except Exception as e:
            print(e)
        print("OVER")
