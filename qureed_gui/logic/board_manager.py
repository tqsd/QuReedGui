from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler
from qureed_project_server import server_pb2

LMH = LogicModuleHandler()

class BoardManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BoardManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.board=None
            self.opened_scheme=None
            self.board_bar=None
            self.board_wrapper=None
            self.board_info=None
            self.board_controls=None
            LMH.register(LogicModuleEnum.BOARD_MANAGER, self)
            self.initialized=True

    @property
    def device_controls(self):
        assert self.board is not None
        return self.board.device_controls

    def register_board_bar(self, board_bar):
        self.board_bar=board_bar

    def register_board_info(self, board_info):
        self.board_info = board_info

    def close_board(self) -> None:
        """
        Clears the board
        """
        self.opened_scheme = ""
        if self.board_bar:
            self.board_bar.update_scheme_name("No Scheme Opened")
        if self.board:
            self.board.clear_board()

    def open_scheme(self, scheme):
        print(f"OPENING {scheme}, currentli {self.opened_scheme} is opened")
        LMH.get_logic(LogicModuleEnum.SELECTION_MANAGER).deselect_all()
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        SvM = LMH.get_logic(LogicModuleEnum.SERVER_MANAGER)
        if self.opened_scheme != scheme:
            self.save_scheme()
            self.board.clear_board()
            scheme_resp = SvM.open_scheme(scheme) 
            print(scheme_resp)
            if scheme_resp.status == "success":
                self.opened_scheme = scheme
                if self.board_bar:
                    self.board_bar.update_scheme_name(self.opened_scheme)
                self.board.load_devices_bulk(scheme_resp.devices)
                self.board.load_connections_bulk(scheme_resp.connections)

    def save_scheme(self):
        from components.board_component import BoardComponent
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        SvM = LMH.get_logic(LogicModuleEnum.SERVER_MANAGER)
        devices = []
        if not self.opened_scheme:
            return
        for device in self.device_controls:
            if not isinstance(device, BoardComponent):
                continue
            device_msg = device.device
            device_msg.location[:] = [device.left, device.top]
            devices.append(device_msg)
        
        response = SvM.save_scheme(
            board=self.opened_scheme,
            devices=devices
            )
        if response.status == "success":
            PM.display_message(f"{self.opened_scheme} succesfully saved")
        else:
            PM.display_message(f"Saving of Scheme {self.opened_scheme} failed: {response.message}")

    def register_board(self, board):
        """
        Register GUI board component, so that we can manage it
        """
        self.board=board

    def register_board_wrapper(self, board_wrapper):
        """
        DEPRECATE
        """
        self.board_wrapper = board_wrapper

    def add_device(self, device:server_pb2.Device):
        print("Attempting to add a device")
        if self.board:
            new_device = server_pb2.Device()
            new_device.CopyFrom(device)
            self.board.add_device(new_device)

    def display_info(self, info:str):
        if self.board_info:
            self.board_info.update_info(info)

    def center_board(self, e):
        self.board.center_board(e)

    def explorer_expansion(self, width):
        if self.board_bar:
            self.board_bar.left=width
            self.board_bar.update()
        if self.board_controls:
            self.board_controls.left=width
            self.board_controls.update()

    def remove_device(self, device):
        SvM = LMH.get_logic(LogicModuleEnum.SERVER_MANAGER)
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        response = SvM.remove_device(device.device.uuid)
        if response.status=="success":
            self.board.board.controls.remove(device)
            self.board.update()
            PM.display_message("Device succesfully removed")
        PM.display_message(f"Device removal failed {response.message}")

