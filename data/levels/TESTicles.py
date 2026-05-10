
from pygame import Vector2, Rect, draw
class Test():
    def __init__(self, tile_size, player):
        self.player = player

        self.plat_pos = Vector2(1,3).elementwise() * tile_size
        self.plat_rect = {
            'platform' : Rect(self.plat_pos.x, self.plat_pos.y, 200, 64)
        }
    
    def update(self, dt, velocity):
         
         self.player.update(velocity, self.plat_rect.values(), dt)
         self.enemy.update(velocity, self.plat_rect.values(), dt)
    
    def render(self, surface, scroll):
            rect = self.plat_rect['platform']

            self.player.render(surface, scroll)
            self.enemy.render(surface, scroll)
            draw.rect(surface, (51,0,123), Rect(rect.x - scroll.x, rect.y - scroll.y, rect.width, rect.height))