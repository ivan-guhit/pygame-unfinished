import pygame


from scripts.core.animation_player import Animation
from scripts.cutscene import Cutscene
from pygame import Vector2, Rect, font, mixer, draw
from data.entities.emeny.emeny.emeny import Emeny
from scripts.utils import load_image
 
 
class LevelUno():
    def __init__(self, player, tile_size, actions, game):
        
        self.player = player
        self.tile_size = tile_size
        self.actions = actions
        self.game = game


        self.cutscene = Cutscene([
            "hello?",
            "i've runned out of gas",
            "can you help me?",
            "...",
            "oh god pls no!",
        ])

        self.cutscene_triggered = True
        self.cutscene.start()

        self.loc_guide = Vector2(0,0).elementwise() * tile_size
 
        self.e_size = Vector2(20, 27)

        self.dang = pygame.font.SysFont('Arial', 10)
 
        self.pos = Vector2(0,0).elementwise() * tile_size
        self.col_pos = Vector2(1,4).elementwise() * tile_size
        self.leftwall = Vector2(-1.3, 0).elementwise() * self.tile_size
        
        self.font = font.Font('assets/fonts/yosterisland/yoster.ttf', 32)

        self.nl_size = Vector2(1, 0.3).elementwise() * tile_size
        self.nl_pos = Vector2(5, 0).elementwise() * tile_size
        self.custom_font = pygame.font.Font('assets/fonts/yosterisland/yoster.ttf', 12)
 
        self.size = Vector2(384, 128)
 
        self.flanked = False
        self.level_complete = False
  
 
        self.enemies = [Emeny(self.game, 100, self.player,' emeny', Vector2(3.3, 2).elementwise() * self.tile_size, self.e_size, self.tile_size), 
                        Emeny(self.game, 100, self.player,' emeny', Vector2(7, 3).elementwise() * self.tile_size, self.e_size, self.tile_size),
                        Emeny(self.game, 100, self.player,' emeny', Vector2(9, 3).elementwise() * self.tile_size, self.e_size, self.tile_size),
                        Emeny(self.game, 100, self.player,' emeny', Vector2(11, 3).elementwise() * self.tile_size, self.e_size, self.tile_size),]
 
        
        self.assets = {
            'bg' : load_image('levels/level1/bg.png'),
            'color' : load_image('levels/level1/color.png'),
            'fog' : load_image('levels/level1/fog.png'),
 
            'ground' : load_image('levels/level1/ground.png'),
            'ground_top' : load_image('levels/level1/g_top.png'),
 
            'treebg' : load_image('levels/level1/treebg.png'),
            'treemg' : load_image('levels/level1/treemg.png'),
            'treefg' : load_image('levels/level1/treefg.png'),
            't&b_sfg' : load_image('levels/level1/t&b_sfg.png'),
 
            'bushbg' : load_image('levels/level1/bushbg.png'),
            'bushmg' : load_image('levels/level1/bushmg.png'),
            'bushfg' : load_image('levels/level1/bushfg.png'),
            
            'rain' : Animation(0.45, self.pos, 0, self.size, load_image('levels/level1/rain.png'), 10),
            'rain-mg' : Animation(0.45, self.pos, 0, self.size, load_image('levels/level1/rain-mg.png'), 10),
 
        }
        
        self.tilemap = {}
 
        for i in range(4):
            for j in range(15):
                grid_pos = Vector2(j, i)
                self.tilemap[str(0 + i) + str(0 + j)] = {'type': 'ground', 'sprite_offsetX' : j, 'sprite_offsetY': i, 'pos': grid_pos.elementwise() * tile_size}
 
        self.collisions = [Rect(int(self.col_pos.x - self.tile_size.x), int(self.col_pos.y - self.tile_size.y), int(self.size.x), 32), 
                           Rect(self.leftwall.x, 0, self.tile_size.x, int(self.size.y)),]
        
    def spawn_enemy(self):
        new_enemy = type(self.enemies[0])(self.player.game, 100, self.player, 'emeny', Vector2(500, 200), self.player.game.e_size, self.tile_size)  
        self.enemies.append(new_enemy)
    
    def spawn_flanking(self):
        spawn_y = 0  
        offset = 60
 
        left_x  = max(self.e_size.x, self.player.pos.x - offset)
        right_x = min(self.size.x - self.e_size.x, self.player.pos.x + offset)
 
        self.enemies.append(Emeny(self.game, 100, self.player, 'emeny', Vector2(left_x,  spawn_y), self.e_size, self.tile_size))
        self.enemies.append(Emeny(self.game, 100, self.player, 'emeny', Vector2(right_x, spawn_y), self.e_size, self.tile_size))
        self.flanked = True


    
    def update(self, dt, velocity):

        if self.cutscene.active:
            self.player.velocity.x = 0
            self.player.update(velocity, self.collisions, dt)
            self.cutscene.update(dt)


            for enemy in self.enemies:
                enemy.update(velocity, self.collisions, dt)
                if enemy.current_state != enemy.states['idle']:
                    enemy.change_state('idle')  
                

            return 


        self.player.update(velocity, self.collisions, dt)
        
        for enemy in self.enemies:
            enemy.update(velocity, self.collisions, dt)
 
        for enemy in self.enemies:
            if enemy.alive:
                self.player.attack(enemy)
 
        for enemy in self.enemies:
            if enemy.alive:
                enemy.attack()
        
        self.enemies = [enemy for enemy in self.enemies if enemy.alive]
 
        if len(self.enemies) <= 2 and not self.flanked:
            self.spawn_flanking()

        if len(self.enemies) == 0 and self.flanked and not self.level_complete:
            self.level_complete = True
 
        if self.level_complete:
            if self.player.pos.x > self.size.x:
                if 'level2' in self.game.states:
                    self.game.game_state.set_state('level2')
            
    



    def render(self, surface, scroll):
        
        bg1 =  scroll * -0.1
        bg2 = scroll * -0.2
        bg3 = scroll * -0.3
 
        mg1 =  scroll * -0.5
        mg2 =  scroll * -0.7
        fg1 =  scroll * -0.8
        fg2 = scroll * -0.9
        main = scroll * -1.0
 
 
        for i in range(5):
            surface.blit(self.assets['bg'], (bg1.x + i * self.assets['bg'].get_width(), bg1.y))
            surface.blit(self.assets['treebg'], (bg2.x + i * self.assets['treebg'].get_width(), bg2.y))
            surface.blit(self.assets['bushbg'], (bg3.x + i * self.assets['bushbg'].get_width(), bg3.y))
            surface.blit(self.assets['treemg'], (mg1.x + i * self.assets['treemg'].get_width(), mg1.y))
 
        self.assets['rain-mg'].play(surface, scroll, False)
        
        for i in range(5):
            surface.blit(self.assets['treefg'], (fg1.x + i * self.assets['treefg'].get_width(), mg1.y))
            surface.blit(self.assets['bushmg'], (fg2.x + i * self.assets['bushmg'].get_width(), fg2.y))
            surface.blit(self.assets['fog'], (mg2.x + i * self.assets['fog'].get_width(), mg2.y))
            surface.blit(self.assets['ground_top'], (main.x + i * self.assets['ground_top'].get_width(), main.y))
        
        self.player.render(surface, scroll)
 
        for enemy in self.enemies:
            enemy.render(surface, scroll)
 
        for i in range(5):
            surface.blit(self.assets['color'], (main.x + i * self.assets['color'].get_width(), main.y))
            
 
        self.assets['rain'].play(surface, scroll, False)
 
        for position in self.tilemap:
            tile = self.tilemap[position]
 
            sprite_offset = Vector2(tile['sprite_offsetX'], tile['sprite_offsetY']).elementwise() * self.tile_size
            texture_rect = Rect(int(sprite_offset.x), int(sprite_offset.y), int(self.tile_size.x), int(self.tile_size.y))
            surface.blit(self.assets['ground'], (tile['pos'].x - scroll.x, tile['pos'].y - scroll.y), texture_rect)
 
 
        for i in range(2):
            surface.blit(self.assets['t&b_sfg'], (fg1.x + i * self.assets['t&b_sfg'].get_width(), fg1.y))
 
        if self.level_complete:
            text = self.custom_font.render('Go! >', True, (255, 255, 255))

            surface.blit(pygame.transform.scale(text, (self.nl_size.x, self.nl_size.y)), (self.nl_pos.x, self.nl_pos.y))
        
        self.cutscene.render(surface, self.custom_font)



        