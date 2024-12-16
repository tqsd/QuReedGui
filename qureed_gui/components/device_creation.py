import flet as ft

from logic import QureedInspector, BoardManager

QI = QureedInspector()
BM = BoardManager()

class Device(ft.Container):
    def __init__(self, name, device_class):
        super().__init__()
        self.value=name
        self.device_class=device_class
        self.on_click= self.add_device
        self.content=ft.Text(name)

    def add_device(self, e):
        print("Here")
        BM.add_device(self.device_class)
        
        

class DeviceCreation(ft.AlertDialog):
    def __init__(self):
        super().__init__()
        self.modal=False
        self.title=ft.Text("Select a Device")
        self.qureed_devices=ft.ListView(
            [Device(d[0],d[2]) for d in QI.qureed_devices]
            )
        
        self.content=ft.Column(
            [
             ft.TextField(),
             ft.Divider(),
             self.qureed_devices,
             ft.Divider(),
             ft.Row(
                 [
                  ft.TextButton("Ok"),
                  ft.TextButton("Cancel")
                    ]
             )
             ]
            )
        

        
        
