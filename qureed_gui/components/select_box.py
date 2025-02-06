import flet as ft
from components.board_component import BoardComponent
from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler

LMH = LogicModuleHandler()

class SelectBox(ft.Container):
    def __init__(self):
        super().__init__()
        self.visible = False
        self.start_x = None
        self.start_y = None
        self.border = ft.border.all(1, "black")

    def sb_start(self,e):
        self.start_x=e.local_x
        self.start_y=e.local_y

    def sb_update(self, e):
        self.visible = True
        current_x=e.local_x
        current_y=e.local_y
        self.height=abs(self.start_y-current_y)
        self.width=abs(self.start_x-current_x)
        if current_y < self.start_y:
            self.top=current_y
        else:
            self.top=self.start_y
        if current_x < self.start_x:
            self.left = current_x
        else:
            self.left = self.start_x
        self.update()

    def sb_stop(self, e, stack):
        self.visible=False
        self.update()
        if self.top is None or self.height is None:
            return
        top = self.top
        bottom = self.top + self.height
        left = self.left
        right = self.left + self.width
        selection = []
        for element in stack.controls:
            if isinstance(element, BoardComponent):
                if element.top > top and element.top + element.height < bottom:
                    if element.left > left and element.left + element.width < right:
                        selection.append(element)
        SM = LMH.get_logic(LogicModuleEnum.SELECTION_MANAGER)
        SM.new_selection(selection)
