
import flet as ft

from .board_component import BoardComponent
from logic import get_device_icon
from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler
from .ports import Ports
from theme import ThemeManager

TM = ThemeManager()
LMH = LogicModuleHandler()

def create_anchors(location, device_mc, device_class, properties=None, **kwargs):
    in_anchor = AnchorComponent(location, device_mc, device_class, properties,
        anchor_type="in", **kwargs)
    out_anchor = AnchorComponent(location, device_mc, device_class, properties,
        anchor_type="out", **kwargs)
    in_anchor.connect_anchor(out_anchor)
    return [in_anchor, out_anchor]


class AnchorComponent(BoardComponent):
    def __init__(self, location:tuple, device_mc, device_class, properties=None,
                 anchor_type:str="in", **kwargs):
        self.kwargs=kwargs
        self.device_mc = device_mc
        self.device_class = device_class
        self.device_instance = None
        self.anchor_type = anchor_type
        super().__init__(location, 30, 30)
        self.other_anchor = None
        if properties:
            self.device_instance.properties = properties
        self.gesture_detection.content.on_enter = self.handle_on_enter
        self.gesture_detection.content.on_exit = self.handle_on_exit
        self.gesture_detection.content.on_secondary_tap = self.handle_delete

        self.contains = ft.Container(
            top=10,bottom=0,right=10, left=10,
            )
        self._compute_ports()
        self.content=ft.Stack(
            [
             self.header,
             self.gesture_detection, # Must be on top
             self.ports_left,
             self.ports_right,
             self.contains
            ]
            )
        SM = LMH.get_logic(LogicModuleEnum.SIMULATION_MANAGER)
        SM.add_device(self.device_instance)

    def build(self):
        self.content=ft.Stack(
            [
             self.header,
             self.gesture_detection, # Must be on top
             self.ports_left,
             self.ports_right,
             self.contains
            ]
            )
        return self.content

    def connect_anchor(self, anchor):
        SM = LMH.get_logic(LogicModuleEnum.SIMULATION_MANAGER)
        self.device_instance = self.device_class(**self.kwargs)
        SM.add_device(self.device_instance)
        self.other_anchor = anchor
        self._compute_ports()
        anchor._compute_ports()
        anchor.other_anchor = self
        anchor.device_instance=self.device_instance
        self.ports_left.register_device_instance(self.device_instance)
        self.ports_right.register_device_instance(self.device_instance)
        anchor.ports_left.register_device_instance(self.device_instance)
        anchor.ports_right.register_device_instance(self.device_instance)
        
    def _compute_ports(self):
        if self.anchor_type == "in":
            input_ports = [
                (name, port) for name, port in self.device_class.ports.items() if
                port.direction=="input"
                ]
            self.ports_left = Ports(
                height=self.height-10,
                left=0,
                ports=input_ports,
                device_instance=self.device_instance,
                parent=self
            )
            self.ports_right = Ports(
                height=self.height-10,
                right=0,
                ports=[],
                device_instance=self.device_instance,
                parent=self
            )
        elif self.anchor_type == "out":
            output_ports = [
                (name, port) for name, port in self.device_class.ports.items() if
                port.direction=="output"
                ]
            self.ports_left = Ports(
                height=self.height-10,
                right=0,
                ports=[],
                device_instance=self.device_instance,
                parent=self
            )
            self.ports_right = Ports(
                height=self.height-10,
                right=0,
                ports=output_ports,
                device_instance=self.device_instance,
                parent=self
            )


    def handle_on_enter(self, e):
        self.select()
        self.other_anchor.select()
        BM = LMH.get_logic(LogicModuleEnum.BOARD_MANAGER)
        BM.display_info(f"{self.device_class.gui_name}")

    def handle_on_exit(self, e):
        self.deselect()
        self.other_anchor.deselect()
        BM = LMH.get_logic(LogicModuleEnum.BOARD_MANAGER)
        BM.display_info(f"")

    def handle_delete(self, e, propagate=True):
        print("Deleting Anchor")
        CM = LMH.get_logic(LogicModuleEnum.CONNECTION_MANAGER)
        BM = LMH.get_logic(LogicModuleEnum.BOARD_MANAGER)
        SM = LMH.get_logic(LogicModuleEnum.SIMULATION_MANAGER)
        for port in [*self.ports_left.content.controls,
                     *self.ports_right.content.controls]:
            CM.disconnect(port)
        BM.remove_device(self)
        if propagate:
            SM.remove_device(self.device_instance)
            self.other_anchor.handle_delete(e, propagate=False)
        
        
            
        
    
