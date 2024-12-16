
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
            self.initialized=True

    def register_board_bar(self, board_bar):
        self.board_bar=board_bar

    def open_scheme(self, scheme):
        print("Opening scheme", scheme)
        self.opened_scheme = scheme
        if self.board_bar:
            self.board_bar.update_scheme_name(self.opened_scheme)

    def register_board(self, board):
        self.board=board

    def add_device(self, device_class):
        if self.board:
            print(device_class)
            self.board.add_device(device_class)

    def display_info(self, info:str):
        if self.board:
            self.board.display_info(info)

    def center_board(self):
        self.board.center_board()

    def explorer_expansion(self, width):
        if self.board_bar:
            self.board_bar.left=width
            self.board_bar.update()
