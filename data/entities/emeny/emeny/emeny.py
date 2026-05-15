import pygame

from pygame import mixer
from scripts.entities import PhysicsEntity
from scripts.core.animation_player import Animation
from scripts.utils import load_image
from data.entities.emeny.emeny.emeny_states import Idle, Chase, Attack, Hurt, Dead, Fall, Down, StandUp, Block, QuickAttack, RageBlock



class Emeny(PhysicsEntity):
    def __init__(self, game, health, player, e_type, pos, size, tile_size):
        super().__init__(game, health, e_type, pos, size, tile_size)

        self.pos = pos
        self.timer  = 0
        self.friction = 0.32
        self.hit_count = 0
        self.next_anim = True
        self.player = player

        self.health = health
        self.alive = True

        self.rage_range = 40
        self.rage_duration = 3.0
        self.rage_start_time = 0

        self.interrupted_attack = False

        self.invincible_during_counter = False

        self.rage_triggered = False
        self.rage_block_broken = False

        self._hit_timestamps = []
        self._frame_counter = 0

        self._block_hit_thresh = 1
        self._block_window = 90
        self._block_cooldown = 0
        self._BLOCK_COOLDOWN_MAX = 180


        self.states = {
            'idle' : Idle(self),
            'chase' : Chase(self),
            'attack' : Attack(self),
            'hurt' : Hurt(self),
            'death' : Dead(self),
            'fall' : Fall(self),
            'down' : Down(self),
            'stand_up' : StandUp(self),
            'block' : Block(self),
            'quick_attack' : QuickAttack(self),
            'rage_block' : RageBlock(self),
        }

        self.anim = {
            'idle' : Animation(0.20, self.pos, 0, self.anim_size, load_image('enemy/fentanyl/idle.png'), 8),
            'chase' : Animation(0.15, self.pos, 0, self.anim_size, load_image('enemy/fentanyl/move.png'), 10),
            'hurt1' : Animation(0.25, self.pos, 0, self.anim_size, load_image('enemy/fentanyl/hurt1.png'), 3),
            'hurt2' : Animation(0.25, self.pos, 0, self.anim_size, load_image('enemy/fentanyl/hurt2.png'), 3),
            'attack' : Animation(0.25, self.pos, 0, self.anim_size, load_image('enemy/fentanyl/attack.png'), 25),
            'death' : Animation(0.25, self.pos, 0, self.anim_size, load_image('enemy/fentanyl/dead.png'), 8, False),
            'fall' : Animation(0.25, self.pos, 0, self.anim_size, load_image('enemy/fentanyl/fall.png'), 0),

            'block' : Animation(0.25, self.pos, 0, self.anim_size, load_image('enemy/fentanyl/block.png'), 8, 0, False),
            'quick_attack' : Animation(0.25, self.pos, 17, self.anim_size, load_image('enemy/fentanyl/attack.png'), 9),
            'down' : Animation(0.25, self.pos, 0, self.anim_size, load_image('enemy/fentanyl/down.png'), 11, 0, False),
            'stand_up' : Animation(0.25, self.pos, 0, self.anim_size, load_image('enemy/fentanyl/stand_up.png'), 8),
        }

        self.hurt = [self.anim['hurt1'], self.anim['hurt2'], self.anim['hurt1']]

        self.current_anim  = self.anim['idle']
        self.current_state = self.states['idle']
        self.current_state.enter()

    def _is_blocking(self):
        """Return True when the enemy is in any blocking state."""
        return (self.current_state == self.states.get('block') or
                self.current_state == self.states.get('rage_block'))

    def _player_is_behind(self):
        """Return True if the player is on the enemy's unguarded (back) side."""
        # Enemy faces left (flip=True)  → guarded side is left  → behind is right
        # Enemy faces right (flip=False) → guarded side is right → behind is left
        if self.flip:
            return self.player.pos.x > self.pos.x
        else:
            return self.player.pos.x < self.pos.x

    def damage(self, hit, hit_type='light'):
        # hit_type values: 'light' (J), 'heavy' (K), 'barrage' (S+D/A+J), 'low_kick' (S+K)
        # Returns True if the hit was absorbed (blocked), False if it landed normally.
        if self.invincible_during_counter:
            return True

        # Both block states absorb ALL hit types — unless the player is behind
        # the enemy, in which case the block is bypassed entirely.
        if self._is_blocking() and not self._player_is_behind():
            if self.current_state == self.states['rage_block']:
                return True
            if self.current_state == self.states['block']:
                # Only light/heavy hits are fed into the combo tracker (barrage ignored).
                self.states['block'].register_block_hit(hit_type)
                return True  # absorbed — no health reduction

        # Record timestamp for should_block() tracking (only for hits that land).
        self._hit_timestamps.append(self._frame_counter)
        self._hit_timestamps = [
            t for t in self._hit_timestamps
            if self._frame_counter - t <= self._block_window
        ]

        self.interrupted_attack = (self.current_state == self.states['attack'])

        self.health -= hit

        self.velocity.x = 0

        if self.health <= 0:
            self.change_state('death')
            return False
        elif not self.rage_triggered and self.health <= 35:
            # Drop into block the moment health crosses the threshold.
            # The caller must not override this state.
            self.rage_triggered = True
            self.change_state('block')
            return True
        elif self.current_state != self.states['hurt']:
            self.change_state('hurt')

        return False

    def should_block(self):
        if self._block_cooldown > 0:
            return False
        recent = [
            t for t in self._hit_timestamps
            if self._frame_counter - t <= self._block_window
        ]
        return len(recent) >= self._block_hit_thresh

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

    def _try_hit_player(self, damage, knockback_mag):
        if self.flip == False:
            hit = pygame.Rect(self.rect().centerx + self.rect().width, self.rect().y, 20, 30)
        else:
            hit = pygame.Rect((self.rect().x - 10), self.rect().y, 20, 30)

        if hit.colliderect(self.player.rect()):
            self.game.screen_shake = 4
            self.player.damage(damage)
            self.player.change_state('hurt')
            if self.flip == False:
                self.player.knockback(knockback_mag)
            else:
                self.player.knockback(-knockback_mag)

    def knockback(self, hit):
        # While blocking, no knockback — enemy holds its ground completely.
        if self._is_blocking():
            return
        self.velocity.x = hit * self.friction

    def rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)

    def change_state(self, state_name):
        # rage_block can only be exited via death, hurt (break), or quick_attack (timer).
        if (self.current_state == self.states.get('rage_block')
                and not getattr(self, '_rage_exiting', False)
                and state_name != 'death'
                and state_name != 'hurt'):
            return
        # regular block can only be exited via death, hurt (break), or quick_attack (counter).
        if (self.current_state == self.states.get('block')
                and state_name not in ('death', 'hurt', 'quick_attack')):
            return
        self._rage_exiting = False
        if self.current_state == self.states.get('block') and state_name != 'block':
            if state_name == 'quick_attack':
                # Counter — no cooldown, enemy can block again right away.
                self._block_cooldown = 0
            elif state_name == 'hurt':
                # Block was broken by K K K J — short cooldown.
                self._block_cooldown = 60
            else:
                self._block_cooldown = self._BLOCK_COOLDOWN_MAX
            self._hit_timestamps = []
        return super().change_state(state_name)

    def update(self, movement, tiles, dt):
        self._frame_counter += 1
        if self._block_cooldown > 0:
            self._block_cooldown -= 1
        self.current_state.update(dt)
        return super().update(movement, tiles, dt)