

class KeyboardEventDispatcher:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(KeyboardEventDispatcher, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.active = True 
            self.registered_hooks = {}
            self.initialized = True
        
    def handle_click(self, e):
        if self.active:
            if self.registered_hooks.get(e.key, False):
                for hook in self.registered_hooks[e.key]:
                    hook(e)
    
    def register_hook(self, key:str, hook):
        if self.registered_hooks.get(key, True):
            self.registered_hooks[key]=[]
        self.registered_hooks[key].append(hook)
        
