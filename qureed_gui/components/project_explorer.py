import flet as ft
from pathlib import Path

from theme import ThemeManager
from logic import ProjectManager, BoardManager

TM = ThemeManager()
PM = ProjectManager()
BM = BoardManager()


class ProjectExplorer(ft.Container):
    """
    Displays the project directory in the board panel
    """

    def __init__(self,page:ft.Page):
        super().__init__()
        self.top = 0
        self.bottom = 0
        self.left = 0
        self.width = 250
        self.bgcolor = TM.get_nested_color("project_explorer", "bg")
        self.color = TM.get_nested_color("project_explorer", "color")
        self.file_list = ft.Column(expand=1, spacing=0, auto_scroll=True)
        self.files = PM.get_file_tree()
        self.content = ft.Stack(
            [
             ft.Container(top=10, right=5, bottom=0, left=5, content=self.file_list),
             ft.Container(
                 top=0, right=0, bottom=0,
                 width=5,
                 bgcolor=ft.Colors.BLACK,
                 on_click=self.toggle_explorer
             ),
             ],
            expand=True
            )
        PM.register_project_explorer(self)

    def update_project(self):
        print("UPDATE FILE EXPLORER")
        self.files = PM.get_file_tree()
        def recursive_tree_update(files):
            elements = []
            for f in files:
                if isinstance(f, str):
                    elements.append(File(path=f))
                elif isinstance(f, dict):
                    for dir_path, contents in f.items():
                        dir_elements = recursive_tree_update(contents)
                        elements.append(Directory(path=dir_path, elements=dir_elements))
            return elements

        self.file_list.controls = recursive_tree_update(self.files)
        self.file_list.update()
        self.page.update()

    def toggle_explorer(self, e):
        if self.width == 250:
            self.width = 5
            self.file_list.visible = False
        else:
            self.width = 250
            self.file_list.visible = True
        BM.explorer_expansion(self.width)
        self.update()
        
        
class Directory(ft.Column):
    def __init__(self, path, elements):
        self.path = path
        self.name = Path(path).name
        super().__init__()
        self.is_visible = False
        self.spacing = 0
        self.elements = ft.Container(
            padding=0,
            margin=ft.margin.only(left=10),
            content=ft.Column(visible=False, controls=elements, spacing=0),
        )
        self.button = ft.TextButton(
            content=ft.Row(
                [
                    ft.Icon(name=ft.Icons.KEYBOARD_ARROW_RIGHT),
                    ft.Text(
                        self.name, size=15, color="#9d9ca0", weight=ft.FontWeight.BOLD
                    ),
                ],
                spacing=2,
            ),
            on_click=self.toggle_visibility,
        )
        self.controls = [self.button, self.elements]

    def toggle_visibility(self, e):
        self.elements.content.visible = not self.elements.content.visible
        if self.elements.content.visible:
            self.button.content.controls[0].name = ft.Icons.KEYBOARD_ARROW_DOWN
        else:
            self.button.content.controls[0].name = ft.Icons.KEYBOARD_ARROW_RIGHT

        self.update()
        e.control.page.update()
        
    def update_project(self, project_path):
        self.path = project_path
        self.update_file_tree()

    def update_file_tree(self):
        pm = ProjectManager()
        self.files = pm.get_file_tree()

        def recursive_tree_update(files):
            elements = []
            for f in files:
                if isinstance(f, str):
                    elements.append(File(path=f))
                elif isinstance(f, dict):
                    for dir_path, contents in f.items():
                        dir_elements = recursive_tree_update(contents)
                        elements.append(Directory(path=dir_path, elements=dir_elements))
            return elements

        self.file_list.controls = recursive_tree_update(self.files)
        self.file_list.update()
        self.page.update()


class DraggableDevice(ft.Draggable):
    """
    Wrapped to carry information to the Board on drag
    """

    def __init__(self, d_cls, group: str, content: ft.Control, content_feedback):
        self.device_class = d_cls["class"]
        super().__init__(
            group=group, content=content, content_feedback=content_feedback
        )

class File(ft.TextButton):
    def __init__(self, path):
        self.path = path
        self.name = Path(path).name
        super().__init__()

        if self.name[-3:] == ".py":
            pm = ProjectManager()
            self.cls = pm.load_class_from_file(self.path)
            self.content = DraggableDevice(
                d_cls={"class": self.cls},
                group="device",
                content_feedback=ft.Container(
                    width=70,
                    height=50,
                    bgcolor="black",
                    opacity=0.3,
                    border_radius=5
                ),
                content=ft.Text(
                    self.cls.gui_name,
                    size=15,
                    weight=ft.FontWeight.BOLD,
                    color="#9d9ca0",
                ),
            )
        else:
            self.content = ft.Text(
                self.name, size=15, weight=ft.FontWeight.BOLD, color="#9d9ca0"
            )
        self.on_click = self.handle_on_click

    def handle_on_click(self, e):
        if self.name[-5:] == ".json":
            BM.open_scheme(self.path)
