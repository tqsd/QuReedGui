import flet as ft

class Ports(ft.Container):
    def __init__(self, height, left=None, right=None):
        super().__init__()
        self.top=10
        self.width=10
        self.height=height

        if left is not None:
            self.left=left
        elif right is not None:
            self.right=right
         
