import pygame
 
from scripts.entities import PhysicsEntity
from scripts.core.animation_player import Animation
from scripts.utils import load_image
from data.entities.player.player_states import  Idle, Move, Jump, TurnRight, TurnLeft, LightAttack, HeavyAttack, KnockbackFinisher, HeavyFinisher, LowKick, Grab, Barrage, Hurt, Dead, Dash, ChaseForBarrage, PostKnockback
 
 
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

        # Tracks whether the current attack state has already landed a hit
        # on a specific enemy this swing — reset when state changes.
        self._attack_hit_this_swing = set()
 
        self.invincible = False
        self.dash_cooldown = 0
        self.barrage_cooldown = 0          
 
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
            'heavy_attack' :  HeavyAttack(self),
            'knockback_finisher' : KnockbackFinisher(self),   
            'heavy_finisher' : HeavyFinisher(self),       
            'low_kick' : LowKick(self),
            'grab' : Grab(self),
            'barrage' : Barrage(self),
            'hurt' : Hurt(self),
            'dead' : Dead(self),
            'dash' : Dash(self),
            'chase_for_barrage' : ChaseForBarrage(self),
            'post_knockback' : PostKnockback(self),
        }
 
        self.anim = {
            'idle': Animation(0.20, self.pos, 0, self.anim_size, load_image('player/playeranim/idle.png'), 8),
            'move' : Animation(0.15, self.pos, 0, self.anim_size, load_image('player/playeranim/right.png'), 7),
            'move_b' : Animation(0.15, self.pos, 0, self.anim_size, load_image('player/playeranim/walk-b.png'), 7),
            'jump' : Animation(0.15, self.pos, 0, self.anim_size, load_image('player/playeranim/jump.png'), 6),
            'turn' : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/turn.png'), 7),
            'hurt' : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/hurt.png'), 3),
            'dead' : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/dead.png'), 6, 0, False),
 
            'light_attack_1' : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/light_attack_1.png'), 4),
            'light_attack_2' : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/light_attack_2.png'), 6),
 
            'low_kick' : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/low_kick.png'), 7),
 
            'heavy_attack_1' : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/heavy_attack_1.png'), 8),
            'heavy_attack_2' : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/heavy_attack_2.png'), 7),
            'heavy_attack_3' : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/heavy_attack_3.png'), 5),
 
            'grab'    : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/grab.png'), 9),
            'barrage' : Animation(0.25, self.pos, 0, self.anim_size, load_image('player/playeranim/barrage.png'), 16),
        }
 
        self.basic_attack = [
            self.anim['light_attack_1'],
            self.anim['light_attack_1'],
            self.anim['light_attack_2'],
        ]
 
        self.heavy_attack = [
            self.anim['heavy_attack_2'],
            self.anim['heavy_attack_3'],
            self.anim['heavy_attack_1'],
        ]
 
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
        self.invincible = False
        self.flip = False
        self.dash_cooldown = 0
        self.barrage_cooldown = 0
        self._attack_hit_this_swing = set()
        self.change_state('idle')
 
 
    def damage(self, hit):
        if self.invincible:
            return
        self.health -= hit
        if self.health <= 0:
            self.change_state('dead')
 
    def knockback(self, hit):
        self.velocity.x = hit * self.friction
 
    def _nearby_enemies(self, reach=40):
        enemies = []
        state = self.game.game_state.get_state()
        level = self.game.states.get(state)
        if level is None or not hasattr(level, 'enemies'):
            return enemies
        for enemy in level.enemies:
            if not enemy.alive:
                continue
            if self.p_rect.inflate(reach * 2, 0).colliderect(enemy.p_rect):
                enemies.append(enemy)
        return enemies
 
    def _finisher_target(self, reach=20):
        """Return the single closest enemy within the finisher hitbox
        AND in front of the player. Returns None if no valid target."""
        if self.flip:
            hit_rect = pygame.Rect(self.p_rect.left - reach, self.p_rect.y, reach, self.p_rect.height)
        else:
            hit_rect = pygame.Rect(self.p_rect.right, self.p_rect.y, reach, self.p_rect.height)

        state = self.game.game_state.get_state()
        level = self.game.states.get(state)
        if level is None or not hasattr(level, 'enemies'):
            return None

        closest = None
        closest_dist = float('inf')
        for enemy in level.enemies:
            if not enemy.alive:
                continue
            if not hit_rect.colliderect(enemy.p_rect):
                continue
            dist = abs(enemy.pos.x - self.pos.x)
            if dist < closest_dist:
                closest_dist = dist
                closest = enemy
        return closest

    def knockback_combo(self, power):
        direction = -1 if self.flip else 1
        target = self._finisher_target()
        if target is not None:
            target.velocity.x = direction * power
            target.change_state('hurt')
            self._notify_tutorial('knockback_finisher')

    def heavy_damage_combo(self, bonus_damage):
        target = self._finisher_target()
        if target is not None:
            target.damage(bonus_damage)
            target.change_state('hurt')
            self.game.hit_pause(8)
            self._notify_tutorial('heavy_finisher')
 
    def low_kick_hit(self, reach=30):
 
        hit_rect = self.p_rect.inflate(reach * 2, 0)
 
        state = self.game.game_state.get_state()
        level = self.game.states.get(state)
        if level is None or not hasattr(level, 'enemies'):
            return
 
        closest = None
        closest_dist = float('inf')
        for enemy in level.enemies:
            if not enemy.alive:
                continue
            if not hit_rect.colliderect(enemy.p_rect):
                continue
            dist = abs(enemy.pos.x - self.pos.x)
            if dist < closest_dist:
                closest_dist = dist
                closest      = enemy
 
        if closest is None:
            return
 
        closest.damage(5)
        self.hitting = True
        self.game.hit_pause(5)
        self.game.screen_shake = 8
        self._notify_tutorial('hit')
 
        if hasattr(closest, 'states') and 'down' in closest.states:
            closest.change_state('down')
        else:
            closest.change_state('hurt')
 
    def attack(self, enemy):
        if self.turn_toggle == False:
            hitrect = pygame.Rect(((self.p_rect.x + self.p_rect.width) - 5), self.p_rect.y, 5, 30)
        elif self.turn_toggle == True:
            hitrect = pygame.Rect((self.p_rect.x + 3), self.p_rect.y, 5, 30)

        enemy_id = id(enemy)
 
        if self.current_state == self.states['light_attack']:
 
            if 1 <= self.current_anim.frame <= 2:
                if hitrect.colliderect(enemy) and enemy_id not in self._attack_hit_this_swing:
                    self._attack_hit_this_swing.add(enemy_id)
                    enemy.damage(7)
                    enemy.change_state('hurt')
                    self.hitting = True
                    self.game.hit_pause(5)
                    self.game.screen_shake = 5
                    self._notify_tutorial('hit')
            else:
                enemy.velocity.x *= 0.5
 
        elif self.current_state == self.states['heavy_attack']:
            if 1 <= self.current_anim.frame <= 2:
                if hitrect.colliderect(enemy) and enemy_id not in self._attack_hit_this_swing:
                    self._attack_hit_this_swing.add(enemy_id)
                    enemy.damage(7)
                    enemy.change_state('hurt')
                    self.hitting = True
                    self.game.hit_pause(5)
                    self.game.screen_shake = 5
                    self._notify_tutorial('hit')
            else:
                enemy.velocity.x *= 0.5
 
        elif self.current_state == self.states['grab']:
            grab_state = self.states['grab']
            if not grab_state.grabbed and 1 <= self.current_anim.frame <= 3:
                if self.turn_toggle == False:
                    grab_rect = pygame.Rect(self.p_rect.right, self.p_rect.y, grab_state.GRAB_RANGE, 30)
                else:
                    grab_rect = pygame.Rect(self.p_rect.left - grab_state.GRAB_RANGE, self.p_rect.y, grab_state.GRAB_RANGE, 30)
 
                if grab_rect.colliderect(enemy.p_rect):
                    grab_state.grabbed = True
                    grab_state.target_enemy = enemy
                    enemy.change_state('hurt')
                    self.game.hit_pause(5)
                    self._notify_tutorial('hit')
 
        elif self.current_state == self.states['barrage']:
            if self.current_anim.frame % 2 == 0:
                if hitrect.colliderect(enemy):
                    enemy.damage(14)
                    enemy.change_state('hurt')
                    self.game.screen_shake = 5
                    self._notify_tutorial('hit')
 
 
    def register_input(self, key):
        self.combo_buffer.append(key)
        if len(self.combo_buffer) > 5:
            self.combo_buffer.pop(0)
        self.combo_timer = self.combo_max_time
 
    def _notify_tutorial(self, kind='hit'):

        state = self.game.game_state.get_state()
        tut = self.game.states.get(state)
        if tut is None or not hasattr(tut, 'notify_hit'):
            return
        if kind == 'knockback_finisher':
            tut.notify_knockback_finisher_hit()
        elif kind == 'heavy_finisher':
            tut.notify_heavy_finisher_hit()
        else:
            tut.notify_hit()

    def change_state(self, state_name):

        if state_name in ('light_attack', 'heavy_attack', 'grab', 'barrage', 'knockback_finisher', 'heavy_finisher', 'low_kick'):
            self._attack_hit_this_swing = set()
        return super().change_state(state_name)
 
 
    def update(self, movement, tiles, dt):
        super().update(movement, tiles, dt)
        self.current_state.update(dt)
 
        if self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo_buffer.clear()
 
        if self.dash_cooldown > 0:
            self.dash_cooldown -= 1
 
        if self.barrage_cooldown > 0:          
            self.barrage_cooldown -= 1