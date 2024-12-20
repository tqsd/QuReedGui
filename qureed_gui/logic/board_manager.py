from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler

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

    def open_scheme(self, scheme):
        SM = LMH.get_logic(LogicModuleEnum.SIMULATION_MANAGER)
        PM = LMH.get_logic(LogicModuleEnum.PROJECT_MANAGER)
        if self.opened_scheme != scheme:
            PM.save_scheme()
            SM.clear_simulation()
            self.board.clear_board()
            self.opened_scheme = scheme
            if self.board_bar:
                self.board_bar.update_scheme_name(self.opened_scheme)
            PM.load_scheme(scheme)


    def register_board(self, board):
        self.board=board

    def register_board_wrapper(self, board_wrapper):
        self.board_wrapper = board_wrapper

    def add_device(self, device_class, device_mc):
        if self.board:
            self.board.add_device(device_class, device_mc)

    def display_info(self, info:str):
        if self.board_info:
            self.board_info.update_info(info)

    def center_board(self, e):
        self.board.center_board(e)

    def explorer_expansion(self, width):
        if self.board_bar:
            self.board_bar.left=width
            self.board_bar.update()

    def remove_device(self, device):
        self.board.board.controls.remove(device)
        self.board.update()
        
