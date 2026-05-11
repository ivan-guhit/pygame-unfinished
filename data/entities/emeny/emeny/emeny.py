import pygame
 
from pygame import mixer
from scripts.entities import PhysicsEntity
from scripts.core.animation_player import Animation
from scripts.utils import load_image
from data.entities.emeny.emeny.emeny_states import Idle, Chase, Attack, Hurt, Dead, Fall
 
 
class Emeny(PhysicsEntity):
    def __init__(self, game, health, player, e_type, pos, size, tile_size):
        super().__init__(game, health, e_type, pos, size, tile_size)
        
        self.pos = pos
 
        self.timer = 0
        self.friction = 0.32
        self.hit_count = 0
        self.next_anim = True
        self.player = player
 
        self.health = health
       
        self.alive = True
 
        self.rage_range = 40
        self.rage_duration = 3.0
        self.rage_start_time = 0
 
        # Track whether the enemy was mid-attack when hurt interrupted them
        self.interrupted_attack = False
 
        print(self.health, self.alive)
 
        self.states = {
            'idle'   : Idle(self),
            'chase'  : Chase(self),
            'attack' : Attack(self),
            'hurt'   : Hurt(self),
            'death'  : Dead(self),
            'fall'   : Fall(self),
        }
 
        self.anim = {
            'idle'   : Animation(0.20, self.pos, 0, self.anim_size, load_image('enemy/fentanyl/idle.png'), 8),
            'chase'  : Animation(0.15, self.pos, 0, self.anim_size, load_image('enemy/fentanyl/move.png'), 10),
            'hurt1'  : Animation(0.25, self.pos, 0, self.anim_size, load_image('enemy/fentanyl/hurt1.png'), 3),
            'hurt2'  : Animation(0.25, self.pos, 0, self.anim_size, load_image('enemy/fentanyl/hurt2.png'), 3),
            'attack' : Animation(0.25, self.pos, 0, self.anim_size, load_image('enemy/fentanyl/attack.png'), 25),
            'death'  : Animation(0.25, self.pos, 0, self.anim_size, load_image('enemy/fentanyl/dead.png'), 8, False),
            'fall'   : Animation(0.25, self.pos, 0, self.anim_size, load_image('enemy/fentanyl/fall.png'), 0),
        }
 
        self.hurt = [self.anim['hurt1'], self.anim['hurt2'], self.anim['hurt1']]
 
        self.current_anim  = self.anim['idle']
        self.current_state = self.states['idle']
        self.current_state.enter()
 
    def damage(self, hit):
        if self.current_state == self.states['hurt']:
            return
 

        self.interrupted_attack = (self.current_state == self.states['attack'])
 
        self.health -= hit
        print(self.health)
 
        if self.health <= 0:
            self.change_state('death')
            
    def attack(self):
 
        if self.flip == False:
            hit = pygame.Rect(self.rect().centerx + self.rect().width, self.rect().y, 15, 30)
        else:
            hit = pygame.Rect((self.rect().x - 10), self.rect().y, 15, 30)
 
        if self.current_state == self.states['attack']:
 
            if 20 <= self.current_anim.frame <= 23:
 
                if hit.colliderect(self.player.rect()):
                    
                    self.game.screen_shake = 5
                    self.player.damage(4)
                    self.player.change_state('hurt')
                    
                    if self.flip == False:
                        self.player.knockback(3)
                    elif self.flip == True:
                        self.player.knockback(-3)
 
                                                        
    def knockback(self, hit):
        self.velocity.x = hit * self.friction
 
    def rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
    
    def change_state(self, state_name):
        return super().change_state(state_name)
    
 
    def update(self, movement, tiles, dt):
        self.current_state.update(dt)
        return super().update(movement, tiles, dt)