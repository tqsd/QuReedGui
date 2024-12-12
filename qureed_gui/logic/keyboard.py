

class KeyboardEventDispatcher:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(KeyboardEventDispatcher, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.registered_hooks = {
            }
        
    def handle_click(self, e):
        if self.registered_hooks.get(e.key, False):
            for hook in self.registered_hooks[e.key]:
                hook(e)
    
    def register_hook(self, key:str, hook):
        if self.registered_hooks.get(key, True):
            self.registered_hooks[key]=[]
        self.registered_hooks[key].append(hook)
        
