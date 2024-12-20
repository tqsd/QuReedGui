import flet as ft
from pynput import keyboard
from logic.logic_module_handler import LogicModuleEnum, LogicModuleHandler

LMH = LogicModuleHandler()

class KeyboardEventDispatcher:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(KeyboardEventDispatcher, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.active = True 
            self.focused = True
            self.SHIFT = False
            self.registered_hooks = {}
            LMH.register(LogicModuleEnum.KEYBOARD_DISPATCHER, self)
            self.initialized = True
        
    def handle_click(self, e):
        if not hasattr(e, "press_type"):
            e.press_type = "keydown"
        if e.press_type == "keydown":
            if e.key == "":
                if e.shift:
                    self.SHIFT = True
        if e.press_type == "keyup":
            if e.key == "":
                if e.shift:
                    self.SHIFT = False
        if self.active and self.focused:
            if self.registered_hooks.get(e.key, False):
                for hook in self.registered_hooks[e.key]:
                    if e.ctrl == hook["ctrl"]:
                        hook["hook"](e)
    
    def register_hook(self, key:str, hook, ctrl=False):
        assert len(key)==1
        key = key.upper()
        if self.registered_hooks.get(key, True):
            self.registered_hooks[key]=[]
        self.registered_hooks[key].append(
            {
             "hook":hook,
             "ctrl":ctrl
             }
            )
def pynput_to_flet_event(key, event_type):
    """Convert pynput key event to Flet keyboard event."""
    key_name = None
    if isinstance(key, keyboard.KeyCode):
        key_name = key.char.upper() if key.char else None
    elif isinstance(key, keyboard.Key):
        if key == keyboard.Key.space:
            key_name = " "
        else:
            key_name = ""
    e = ft.KeyboardEvent(
        key=key_name,
        shift=key==keyboard.Key.shift,
        alt=False,
        meta=False,
        ctrl=False
        )
    e.data=""
    e.control=""
    e.press_type=event_type
    return e

        
def start_pynput_listener(ked):
    """Start listening to keyboard events using pynput."""
    KED = KeyboardEventDispatcher()
    def on_press(key):
        if KED.focused:
            event = pynput_to_flet_event(key, "keydown")
            KED.handle_click(event)

    def on_release(key):
        if KED.focused:
            event = pynput_to_flet_event(key, "keyup")
            KED.handle_click(event)

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
