import asyncio
import time
import socket
import subprocess
import sys
import threading
from pathlib import Path
from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler
import qureed_project_server.server_pb2 as MSG
import qureed_project_server.server_pb2_grpc
from qureed_project_server.client import GrpcClient


LMH = LogicModuleHandler()

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
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))  # Bind to the port to check if it's available
                return port
            except OSError:
                continue
    raise RuntimeError("No unused port found in the specified range.")


class ServeManager:
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

    def is_server_ready(self):
        """
        Check if the server is ready to accept connections.
        """
        try:
            with socket.create_connection(("localhost", self.port), timeout=1):
                return True
        except OSError:
            return False

    def start(self):
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)

        python_executable = Path(PM.venv) / "bin" / "python" if sys.platform != "win32" else Path(PM.venv) / "Scripts" / "python.exe"

        if not python_executable.exists():
            raise FileNotFoundError(f"Python executable not found in virtual environment: {python_executable}")

        # Find an unused port
        port = find_unused_port()
        self.port = port

        # Command to start the server
        command = [str(python_executable), "-m", "qureed_project_server.server", "--port", str(port)]
        print(" ".join(command))
        try:
            # Start the server process
            self.server_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Server started with PID {self.server_process.pid} on port {self.port}")

            # Poll for readiness
            for _ in range(20):  # Wait up to 10 seconds
                time.sleep(0.5)
                if self.is_server_ready():
                    break
            else:
                raise TimeoutError("Server did not become ready in time.")
        except Exception as e:
            print(f"Failed to start server: {e}")
            return

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
            print(f"Connect Venv Response: {response}")

        # Use the helper method to run the coroutine
        self.run_in_loop(connect())
        

    def stop(start):
        pass
