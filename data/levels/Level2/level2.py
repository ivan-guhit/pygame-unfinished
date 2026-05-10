import pygame

from pygame import Vector2, Rect, font
from scripts.utils import load_image
from data.entities.boss.invisbol import Invisbol


class LevelDos():
    def __init__(self, player, tile_size, actions, game):
        
        self.player = player
        self.tile_size = tile_size
        self.actions = actions
        self.game = game
 
        self.e_size = Vector2(20, 27)
 
        self.emeny_pos = Vector2(5, 3).elementwise() * self.tile_size

        self.boss = Invisbol(self.game, 400, self.player,'boss', self.emeny_pos, self.e_size, self.tile_size)
 
 
        self.pos = Vector2(0,0).elementwise() * tile_size
        self.col_pos = Vector2(1,4).elementwise() * tile_size
        
        self.font = font.Font('assets/fonts/yosterisland/yoster.ttf', 32)

        self.nl_size = Vector2(1, 0.3).elementwise() * tile_size
        self.nl_pos = Vector2(5, 0).elementwise() * tile_size
        self.custom_font = pygame.font.Font('assets/fonts/yosterisland/yoster.ttf', 12)

        self.leftwall = Vector2(-1.3, 0).elementwise() * self.tile_size
 
        self.size = Vector2(224, 128)
 
        self.level_complete = False
        
        self.assets = { 

            'wall' : load_image('levels/level2/wall.png'),
            'wall_color' : load_image('levels/level2/wall-color.png'),
            'props' : load_image('levels/level2/tables&shii.png'),
            'ground' : load_image('levels/level2/ground&shi.png'),
            'color' : load_image('levels/level2/color.png'),
            'source_light' : load_image('levels/level2/lightsource&shi.png'),
            'decorlight' : load_image('levels/level2/decorlight&shi.png'),
            'material_light' : load_image('levels/level2/materiallight&shi.png'),
            
        }
        
        self.tilemap = {}
 
        for i in range(4):
            for j in range(7):
                grid_pos = Vector2(j, i)
                self.tilemap[str(0 + i) + str(0 + j)] = {'type': 'ground', 'sprite_offsetX' : j, 'sprite_offsetY': i, 'pos': grid_pos.elementwise() * tile_size}
 
        self.collisions = [Rect(0, -self.tile_size.y, int(self.size.x), self.tile_size.y),
                           Rect(self.leftwall.x, 0, self.tile_size.x, int(self.size.y)),
                           Rect(int(self.size.x), 0, self.tile_size.x, int(self.size.y)),
                           Rect(int(self.col_pos.x - self.tile_size.x), int(self.col_pos.y - self.tile_size.y), int(self.size.x), 32),]
 
    def reset(self):
        self.emeny_pos = Vector2(5, 3).elementwise() * self.tile_size
        self.level_complete = False
        

    def update(self, dt, velocity):

        self.player.update(velocity, self.collisions, dt)
        self.boss.update(velocity, self.collisions, dt)
        
        self.player.attack(self.boss)
        self.boss.attack()

        if self.boss.alive == False:
            self.level_complete = True

        if self.level_complete:
            if 'credits' in self.game.states:
                self.game.game_state.set_state('credits')
            
    
    def render(self, surface, scroll):
        
        pos = (0 - scroll.x, 0 - scroll.y)

        surface.blit(self.assets['wall'], pos)
        surface.blit(self.assets['wall_color'], pos)
        surface.blit(self.assets['props'], pos)

        
        
        for position in self.tilemap:
            tile = self.tilemap[position]
 
            sprite_offset = Vector2(tile['sprite_offsetX'], tile['sprite_offsetY']).elementwise() * self.tile_size
            texture_rect = Rect(int(sprite_offset.x), int(sprite_offset.y), int(self.tile_size.x), int(self.tile_size.y))
            surface.blit(self.assets['ground'], (tile['pos'].x - scroll.x, tile['pos'].y - scroll.y), texture_rect)


        self.player.render(surface, scroll)
        self.boss.render(surface, scroll)
        
        surface.blit(self.assets['color'], pos)
        surface.blit(self.assets['source_light'], pos)
        surface.blit(self.assets['decorlight'], pos)
        surface.blit(self.assets['material_light'], pos)
 