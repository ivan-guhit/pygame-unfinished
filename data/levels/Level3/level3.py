
from pygame import Vector2, Rect
from scripts.utils import load_image

class LevelTres():
    def __init__(self, surface, scroll):
        self.collisions = {
            'ground' : {'grid_pos' : Vector2(), 'rect' : Rect()},
            'fence_left' : {'grid_pos' : Vector2(), 'rect' : Rect()},
            'fence_right' : {'grid_pos' : Vector2(), 'rect' : Rect()},
        }
    
    def render(self):
        pass