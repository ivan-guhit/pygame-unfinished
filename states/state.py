import pygame

class State():
    def __init__(self, entity):
        self.entity = entity
    
    def enter(self):
        pass

    def exit(self):
        pass

    def update(self, dt):
        pass

    def render(self, surface):
        pass

    def change_state(self, state_name):
        self.current_state.exit()
        self.current_state = self.states[state_name]
        self.current_state.enter()

