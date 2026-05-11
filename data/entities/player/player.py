

import pygame
 
from scripts.entities import PhysicsEntity
from scripts.core.animation_player import Animation
from scripts.utils import load_image
from data.entities.player.player_states import Idle, Move, Jump, TurnRight, TurnLeft,LightAttack, LowKick, Barrage, Hurt, Dead, Dash
from pygame import Vector2
 
class Player(PhysicsEntity):
    def __init__(self, game, health, e_type, pos, size, tile_size, actions):
        super().__init__(game, health, e_type, pos, size, tile_size)
 
        self.actions = actions
        self.attack_pos = 0
        self.game = game
        self.friction = 0.32
        self.tile_size = tile_size
 
        self.health = health
        self.alive = True
        self.hitting = False
 

        self.is_sprinting = False
        self.invincible   = False          
 
        self.combo_buffer = []
        self.combo_timer = 0
        self.combo_max_time = 20
 
        self.states = {
            'idle' : Idle(self),
            'move' : Move(self),
            'jump' : Jump(self),
            'turn_left' : TurnLeft(self),
            'turn_right' : TurnRight(self),
            'light_attack' : LightAttack(self),
            'low_kick' : LowKick(self),
            'barrage' : Barrage(self),
            'hurt' : Hurt(self),
            'dead' : Dead(self),
            'dash' : Dash(self),      
        
        }
 
        self.anim = {
 
            'idle' : Animation(0.20, self.pos, 0, self.anim_size, load_image('player/playeranim/idle.png'), 8),
            'move'  : Animation(0.15, self.pos, 0, self.anim_size, load_image('player/playeranim/right.png'), 7),
            'move_b' : Animation(0.15, self.pos, 0, self.anim_size, load_image('player/playeranim/walk-b.png'), 7),
            'jump' : Animation(0.15, self.pos, 0, self.anim_size, load_image('player/playeranim/jump.png'), 6),
            'turn' : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/turn.png'), 7),
            'hurt' : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/hurt.png'), 3),
            'dead' : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/dead.png'), 6, False),
            'light_attack_basic' : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/light_attack_basic.png'), 4),
            'light_attack_1' : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/light_attack_1.png'), 6),
            'light_attack_2' : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/light_attack_2.png'), 5),
            'light_attack_3' : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/light_attack_3.png'), 5),
            'low_kick' : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/light_attack_3.png'), 5),
            'barrage' : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/barrage.png'), 16),
        }
 
        self.basic_attack = [self.anim['light_attack_basic'], self.anim['light_attack_basic'], self.anim['light_attack_1'], self.anim['light_attack_2'],  self.anim['light_attack_3'],]
        
        self.current_anim  = self.anim['idle']
        self.current_state = self.states['idle']
        self.current_state.enter()
 
    def reset(self):
        self.health = 100
        self.alive = True
        self.pos.x = 1 * self.tile_size.x
        self.pos.y = 3 * self.tile_size.y
        self.velocity.x = 0
        self.velocity.y = 0
        self.attack_pos = 0
        self.down = False
        self.is_sprinting = False
        self.invincible   = False
        self.change_state('idle')
 
    def damage(self, hit):

        if self.invincible:
            return
 
        self.health -= hit
 
        if self.health <= 0:
            self.change_state('dead')
 
    def attack(self, enemy):
 
        if self.turn_toggle == False:
            hitrect = pygame.Rect(((self.p_rect.x + self.p_rect.width) - 5), self.p_rect.y, 5, 30)
        elif self.turn_toggle == True:
            hitrect = pygame.Rect((self.p_rect.x + 3), self.p_rect.y, 5, 30)
 
        if self.current_state == self.states['light_attack']:
            
            if 1 <= self.current_anim.frame <= 2:
 
                if hitrect.colliderect(enemy):
 
                    enemy.damage(7)
                    enemy.change_state('hurt')
                    self.hitting = True
                    
                    self.game.hit_pause(5)
                    self.game.screen_shake = 5
 
                    if self.turn_toggle == False:
 
                        if self.attack_pos == len(self.basic_attack) - 1:
                            enemy.knockback(7)       
 
                    if self.turn_toggle == True:
 
                        if self.attack_pos == len(self.basic_attack) - 1:
                            enemy.knockback(-7)
            else:
                enemy.velocity.x *= 0
                            
        
        elif self.current_state == self.states['low_kick']:
 
            if 1 <= self.current_anim.frame <= 3:
 
                if hitrect.colliderect(enemy):
 
                    enemy.damage(4)
                    enemy.change_state('hurt')
                    self.game.hit_pause(4)
                    self.game.screen_shake = 4
 
 
 
        elif self.current_state == self.states['barrage']:
  
            if self.current_anim.frame % 2 == 0:
 
                if hitrect.colliderect(enemy):
 
                    enemy.damage(1)
                    enemy.change_state('hurt')
                    self.game.screen_shake = 10
 
 
    def knockback(self, hit):
        self.velocity.x = hit * self.friction
 
    def register_input(self, key):
 
        self.combo_buffer.append(key)
 
        if len(self.combo_buffer) > 5:
            self.combo_buffer.pop(0)
 
        self.combo_timer = self.combo_max_time
 
        print(self.combo_buffer)
 
    def change_state(self, state_name):
        return super().change_state(state_name)
    
    def update(self, movement, tiles, dt):
        
        super().update(movement, tiles, dt)
 
        self.current_state.update(dt)
 
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo_buffer.clear()