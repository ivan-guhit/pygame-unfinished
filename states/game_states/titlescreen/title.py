import pygame

from scripts.core.animation_player import Animation
from scripts.utils import load_image
from pygame import Vector2, mixer

class TitleScreen():
    def __init__(self, tile_size, surface, game_state):
        self.surface = surface
        self.game_state = game_state
        self.tile_size = tile_size
        self.size = Vector2(192, 128)
        self.pos = Vector2(0,0)
        self.title_screen_anim = Animation(0.15, self.pos, 0, self.size, load_image('ui/title_screen/title_screen.png'), 8)

        self.font = pygame.font.Font('assets/fonts/yosterisland/yoster.ttf', 12)
        
        self.font_size = Vector2(5,0.5).elementwise() * tile_size
        self.font_pos = Vector2(0.5, 0.2).elementwise() * tile_size


        self.start_size = Vector2(4,0.4).elementwise() * tile_size
        self.start_pos = Vector2(1, 3.3).elementwise() * tile_size
        self.flip = False


    def update(self, delta, velocity):
        pass

    def render(self, surface, offset):
        
        title_text = "Thugs Invasion Thugs Evasion"
        current_x = self.font_pos.x

        for char in title_text:

            if char.isupper():
                color = (255, 0, 0) 
            else:
                color = (255, 255, 255)

            char_surf = self.font.render(char, True, color)
        
            char_width = char_surf.get_width() * (self.font_size.x / self.font.size(title_text)[0])
            scaled_char = pygame.transform.scale(char_surf, (int(char_width), int(self.font_size.y)))

            surface.blit(scaled_char, (current_x, self.font_pos.y))
            current_x += char_width


        start = self.font.render("Press \"Enter\" to start", True, (255, 255, 255))
        surface.blit(pygame.transform.scale(start, (self.start_size.x, self.start_size.y)), (self.start_pos.x, self.start_pos.y))
        self.title_screen_anim.play(surface, offset, self.flip)

  