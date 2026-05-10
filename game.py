import pygame
import os
import random

os.environ['SDL_VIDEO_CENTERED'] = '1'

from pygame import Vector2
from data.entities.player.player import Player
from states.game_states.titlescreen.title import TitleScreen
from states.game_states.credits.credits import Credits
from states.game_states.game_states import GameState
from data.levels.Level1.level1 import LevelUno
from data.levels.Level2.level2 import LevelDos



from data.levels.TESTicles import Test

class Game():
    def __init__(self):
        
        pygame.init()

        self.delta = 0
        self.cell_size = Vector2(64, 64)
        self.tile_size = Vector2(32, 32)
        self.tile_layout = Vector2(6,4).elementwise() * self.tile_size
        self.window_size = Vector2(16, 10).elementwise() * self.cell_size
        self.window = pygame.display.set_mode((int(self.window_size.x), int(self.window_size.y)))
        self.surface = pygame.Surface((int(self.tile_layout.x), int(self.tile_layout.y)))
        
        pygame.display.set_caption('Thugs Invasion Thugs Evasion (TITE)')

        self.gameloop = True
        self.clock = pygame.time.Clock()
        self.p_size = Vector2(25, 27)
        

        self.screen_shake = 0
        if self.screen_shake >= 0:
            self.screen_shake -= 1

        self.hitpause = 0
        self.freeze = False

        self.actions = {

            'jump' : False, 
            'down' : False, 
            'left' : False, 
            'right' : False,
            'light_attack' : False,
            'heavy_attack' : False,
            'flipped' : False,
            'dodge' : False,

        }

        self.player_pos = Vector2(1, 1).elementwise() * self.tile_size
        self.player = Player(self, 100, 'player', self.player_pos, self.p_size, self.tile_size, self.actions)
        self.velocity = Vector2(0,0)
        self.scroll = Vector2(0,0)

        self.previous_state = 'title_screen'
        self.game_state = GameState('title_screen')

        self.states = {

            'test_world' : Test(self.tile_size, self.player),
            'title_screen' : TitleScreen(self.tile_size, self.surface, self.game_state),
            'level1' : LevelUno(self.player, self.tile_size, self.actions, self),
            'level2' : LevelDos(self.player, self.tile_size, self.actions, self),
            'credits' : Credits(self.tile_size, self.surface, self.game_state, self)
            
        }


    def run(self):
        while self.gameloop:
            
            self.input_handle()
            self.update()
            self.render()
            self.delta = self.clock.tick(60) / 1000.00
            
   
    def hit_pause(self, duration):
        self.hitpause = duration
        self.freeze = False


    def input_handle(self):
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.gameloop = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.gameloop = False
                    break
                if event.key == pygame.K_d:
                    self.actions['right'] = True
                    self.player.velocity.x = 0.5
                if event.key == pygame.K_a:
                    self.actions['left'] = True
                    self.player.velocity.x = -0.5 
                if event.key == pygame.K_w:
                    if self.player.down:
                        self.actions['jump'] = True
                        self.player.velocity.y = -4
                if event.key == pygame.K_e:
                    self.actions['flipped'] = True
                if event.key == pygame.K_j:
                    self.actions['light_attack'] = True
                if event.key == pygame.K_RETURN:
                    self.game_state.set_state('level1')
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    self.actions['jump'] = False
                if event.key == pygame.K_d:
                    self.actions['right'] = False
                    self.player.velocity.x = 0
                if event.key == pygame.K_a:
                    self.actions['left'] = False
                    self.player.velocity.x = 0
                if event.key == pygame.K_j:
                    self.actions['light_attack'] = False
                    print(self.player.attack_pos)
                if event.key == pygame.K_e:
                    self.actions['flipped'] = False

        #print(self.velocity)

    def update(self):
        
        current_state = self.game_state.get_state()

        if self.freeze:
            self.hitpause -= 1
            if self.hitpause <= 0:
                self.freeze = False
        else:
            if current_state != self.previous_state:
                self.scroll = Vector2(0, 0)
                self.player.reset()
                self.player.velocity = Vector2(0, 0)                            
                self.previous_state = current_state
        
            self.states[current_state].update(self.delta, self.velocity)

        if self.player.alive == False:
            self.player.reset()
            self.states['level1'].reset()
            self.states['level2'].reset()
            self.game_state.set_state('title_screen')

        if self.player.velocity.x > 0:
            self.scroll.x += int(((self.player.rect().centerx - self.surface.get_width() / 2 - self.scroll.x) / 5) + 2)
        elif self.player.velocity.x < 0:
            self.scroll.x += int(((self.player.rect().centerx - self.surface.get_width() / 2 - self.scroll.x) / 5) - 2)
        else:
            self.scroll.x += int(((self.player.rect().centerx - self.surface.get_width() / 2 - self.scroll.x) / 5))

        self.scroll.y = int(((self.player.rect().centery - self.surface.get_height() / 2 - self.scroll.y) / 5))

        if current_state == 'level2':
            level_width = 224
            level_height = 128
        else:
            level_width = 384
            level_height = 128
    
        self.scroll.x = max(0, min(self.scroll.x, level_width - self.surface.get_width()))
        self.scroll.y = max(0, min(self.scroll.y, level_height - self.surface.get_height()))


    def render(self):

        self.surface.fill((0,0,0))

        self.states[self.game_state.get_state()].render(self.surface, self.scroll)

        shake = Vector2(random.uniform(-self.screen_shake, self.screen_shake), random.uniform(-self.screen_shake, self.screen_shake))

        if self.screen_shake > 0:
            self.screen_shake -= 1

        self.window.blit(pygame.transform.scale(self.surface, self.window.get_size()), (shake.x, shake.y))
        pygame.display.flip()
    
    



game = Game()

game.run()

pygame.quit()