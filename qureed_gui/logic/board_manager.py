
class BoardManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BoardManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.board=None

    def register_board(self, board):
        self.board=board

    def add_device(self, device_class):
        if self.board:
            print(device_class)
            self.board.add_device(device_class)
