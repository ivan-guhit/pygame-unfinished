import pygame

from scripts.entities import PhysicsEntity
from scripts.core.animation_player import Animation
from scripts.utils import load_image
from data.entities.boss.boss_state import Idle, Chase, Attack, Hurt, Dead


class Invisbol(PhysicsEntity):
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

        print(self.health, self.alive)

        self.states = {
            'idle' : Idle(self),
            'chase' : Chase(self),
            'attack' : Attack(self),
            'hurt' : Hurt(self),
            'death' : Dead(self),
        }

        self.anim = {
            'idle' : Animation(0.20, self.pos, 0, self.anim_size, load_image('enemy/boss/idle.png'), 11),
            'hurt' : Animation(0.25, self.pos, 0, self.anim_size, load_image('enemy/boss/hurt.png'), 5),
            'attack' : Animation(0.25, self.pos, 0, self.anim_size, load_image('enemy/boss/attack.png'), 9),
            'death' : Animation(0.25, self.pos, 0, self.anim_size, load_image('enemy/boss/dead.png'), 4, False),

        }

        self.hurt = [self.anim['hurt'], self.anim['hurt'], self.anim['hurt']]

        self.current_anim = self.anim['idle']
        self.current_state = self.states['idle']
        self.current_state.enter()

    def damage(self, hit):

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

            if 4 <= self.current_anim.frame <= 6:

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