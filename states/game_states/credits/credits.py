
from pygame import Vector2, font

class Credits():
    def __init__(self, tile_size, surface, game_state, game):
        self.surface = surface
        self.game_state = game_state
        self.tile_size = tile_size
        self.game = game
        self.size = Vector2(192, 128).elementwise() * self.tile_size
        self.pos = Vector2(0,0)

        self.font = font.Font('assets/fonts/yosterisland/yoster.ttf', 12)
        
        self.cutscene_complete = False
        self.timer = 4.0  

        self.flip = False

    def update(self, delta, velocity):
        if self.timer > 0:
            self.timer -= delta
        else:
            self.cutscene_complete = True
            self.timer = 4.0  # reset for next time
            if 'title_screen' in self.game.states:
                self.game.game_state.set_state('title_screen')

    def render(self, surface, offset):
        surface.fill((0, 0, 0))

        gg_text = self.font.render('You Win!', True, (255, 255, 255))
        text_rect = gg_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
        surface.blit(gg_text, text_rect)
        

  