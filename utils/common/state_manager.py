class EnvStateManager:
    def __init__(self):
        self.state = {}

    def get(self, key, default=None):
        return self.state.get(key, default)

    def update(self, key, value):
        self.state[key] = value
    @property
    def get_full_state(self):
        return self.state
    
class PhaseStateManager:
    def __init__(self):
        self.state = {}

    def initialize(self, task):
        self.state["task"] = task

    def update(self, key, value):
        self.state[key] = value

    def get(self, key, default=None):
        return self.state.get(key, default)
    @property
    def get_full_state(self):
        return self.state