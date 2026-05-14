from states.state import State
 
 
ATTACK_MOVE_SPEED = 0.15   
 
 
class Idle(State):
 
    def enter(self):
        if self.entity.velocity.x == 0:
            self.entity.current_anim = self.entity.anim['idle']
 
    def update(self, dt):
 
        if self.entity.velocity.x != 0:
            self.entity.change_state('move')
 
        elif self.entity.velocity.y < 0:
            self.entity.change_state('jump')
 
        if self.entity.combo_buffer[-1:] == ["SPACE"] and self.entity.dash_cooldown <= 0:
            self.entity.combo_buffer.clear()
            self.entity.change_state('dash')
 
 
        if self.entity.combo_buffer[-2:] == ["S", "J"]:
            self.entity.combo_buffer.clear()
            self.entity.change_state("grab")
 
 
        elif self.entity.combo_buffer[-2:] == ["S", "K"]:
            self.entity.combo_buffer.clear()
            self.entity.change_state("low_kick")
 
   

        elif self.entity.combo_buffer[-3:] == (["S", "A", "J"] if self.entity.flip else ["S", "D", "J"]):
            self.entity.combo_buffer.clear()
            self.entity.change_state("barrage")
 
        elif self.entity.actions['light_attack']:
            self.entity.change_state('light_attack')
 
        elif self.entity.actions['heavy_attack']:
            self.entity.change_state('heavy_attack')
 
        if self.entity.health <= 0:
            self.entity.change_state('dead')
 
        if self.entity.actions['flipped']:
            self.entity.turn_toggle = not self.entity.turn_toggle
            self.entity.change_state('turn_left' if self.entity.turn_toggle else 'turn_right')
 
 
class Jump(State):
 
    def enter(self):
        self.entity.current_anim = self.entity.anim['jump']
 
    def update(self, dt):
        if self.entity.down:
            self.entity.change_state('move' if self.entity.velocity.x != 0 else 'idle')
        if self.entity.health <= 0:
            self.entity.change_state('dead')
 
 
class Move(State):
 
    def enter(self):
        if self.entity.flip:
            self.entity.current_anim = self.entity.anim["move"] if self.entity.velocity.x < 0 else self.entity.anim["move_b"]
        else:
            self.entity.current_anim = self.entity.anim["move"] if self.entity.velocity.x > 0 else self.entity.anim["move_b"]
        self.entity.current_anim.reset()
 
    def update(self, dt):

        if not self.entity.actions['left'] and not self.entity.actions['right']:
            self.entity.change_state('idle')
 
        elif self.entity.actions['jump']:
            self.entity.change_state('jump')
 
        if self.entity.combo_buffer[-1:] == ["SPACE"] and self.entity.dash_cooldown <= 0:
            self.entity.combo_buffer.clear()
            self.entity.change_state('dash')
        
        if self.entity.combo_buffer[-2:] == ["S", "J"]:
            self.entity.combo_buffer.clear()
            self.entity.change_state("grab")
 
        elif self.entity.combo_buffer[-2:] == ["S", "K"]:
            self.entity.combo_buffer.clear()
            self.entity.change_state("low_kick")
   
            
        elif self.entity.combo_buffer[-3:] == (["S", "A", "J"] if self.entity.flip else ["S", "D", "J"]):
            self.entity.combo_buffer.clear()
            self.entity.change_state("barrage")
 
        elif self.entity.actions['light_attack']:
            self.entity.change_state('light_attack')
 
        elif self.entity.actions['heavy_attack']:
            self.entity.change_state('heavy_attack')
 
        if self.entity.actions['flipped']:
            self.entity.turn_toggle = not self.entity.turn_toggle
            self.entity.change_state('turn_left' if self.entity.turn_toggle else 'turn_right')
 
        if self.entity.health <= 0:
            self.entity.change_state('dead')
 
 
class TurnLeft(State):
    def enter(self):
        self.entity.current_anim = self.entity.anim['turn']
        self.entity.flip = True
        self.entity.current_anim.reset()
 
    def update(self, dt):
        if self.entity.current_anim.finished:
            self.entity.change_state('idle')
        if self.entity.health <= 0:
            self.entity.change_state('dead')
 
 
class TurnRight(State):
    def enter(self):
        self.entity.current_anim = self.entity.anim['turn']
        self.entity.flip = False
        self.entity.current_anim.reset()
 
    def update(self, dt):
        if self.entity.current_anim.finished:
            self.entity.change_state('idle')
        if self.entity.health <= 0:
            self.entity.change_state('dead')
 
 
class Hurt(State):
 
    def enter(self):
        self.entity.current_anim = self.entity.anim['hurt']
        self.entity.current_anim.reset()
 
    def update(self, dt):
        if self.entity.current_anim.finished:
            self.entity.change_state('idle')
        if self.entity.health <= 0:
            self.entity.change_state('dead')
 
 

 
class LightAttack(State):
 
    def enter(self):
        self.entity.current_anim = self.entity.basic_attack[self.entity.attack_pos]
        self.combo_window  = False
        self.next_attack   = False
        self.wants_heavy   = False
        self.entity.current_anim.reset()
 
    def update(self, dt):
 
        if self.entity.current_anim.frame >= 2:
            self.combo_window = True
 
        if self.combo_window:
            if self.entity.actions['light_attack']:
                self.next_attack = True
                self.wants_heavy = False
            if self.entity.actions['heavy_attack']:
                self.wants_heavy = True
 
        if self.entity.current_anim.finished:
            chain_len = self.entity.attack_pos + 1   
 
            if self.wants_heavy and chain_len >= 2:
                self.entity.attack_pos = 0
                self.entity.change_state('knockback_finisher')
            elif self.next_attack:
                self.entity.attack_pos = (self.entity.attack_pos + 1) % len(self.entity.basic_attack)
                self.entity.change_state('light_attack')
            else:
                self.entity.attack_pos = 0
                self.entity.change_state('idle')
 
        if self.entity.health <= 0:
            self.entity.change_state('dead')
 
 
class HeavyAttack(State):
 
    def enter(self):
        self.entity.current_anim = self.entity.heavy_attack[self.entity.attack_pos]
        self.combo_window  = False
        self.next_attack   = False
        self.wants_light   = False
        self.entity.current_anim.reset()
 
    def update(self, dt):
 
        if self.entity.current_anim.frame >= 2:
            self.combo_window = True
 
        if self.combo_window:
            if self.entity.actions['heavy_attack']:
                self.next_attack = True
                self.wants_light = False
            if self.entity.actions['light_attack']:
                self.wants_light = True
 
        if self.entity.current_anim.finished:
            chain_len = self.entity.attack_pos + 1
 
            if self.wants_light and chain_len >= 2:
                self.entity.attack_pos = 0
                self.entity.change_state('heavy_finisher')
            elif self.next_attack:
                self.entity.attack_pos = (self.entity.attack_pos + 1) % len(self.entity.heavy_attack)
                self.entity.change_state('heavy_attack')
            else:
                self.entity.attack_pos = 0
                self.entity.change_state('idle')
 
        if self.entity.health <= 0:
            self.entity.change_state('dead')
 
 
class KnockbackFinisher(State):
 
    KNOCKBACK_POWER = 2
 
    def enter(self):
        self.entity.current_anim = self.entity.anim['heavy_attack_3']
        self.entity.current_anim.reset()
        self.applied       = False
        self.wants_barrage = False
 
    def update(self, dt):
 
        if not self.applied and self.entity.current_anim.frame >= 3:
            self.entity.knockback_combo(self.KNOCKBACK_POWER)
            self.applied = True
            self.entity.game.screen_shake = 8
 
        _barrage_combo = ["S", "A", "J"] if self.entity.flip else ["S", "D", "J"]
        if self.applied and self.entity.combo_buffer[-3:] == _barrage_combo:
            self.wants_barrage = True
            self.entity.combo_buffer.clear()
 
        if self.entity.current_anim.finished:
            self.entity.attack_pos = 0
            if self.entity.current_anim.finished:
                self.entity.attack_pos = 0
                self.entity.change_state('post_knockback')
 
        if self.entity.health <= 0:
            self.entity.change_state('dead')
 
 
class HeavyFinisher(State):
 
    BONUS_DAMAGE = 20
 
    def enter(self):
        self.entity.current_anim = self.entity.anim['light_attack_2']
        self.entity.current_anim.reset()
        self.applied = False
 
    def update(self, dt):

 
        if not self.applied and self.entity.current_anim.frame >= 2:
            self.entity.heavy_damage_combo(self.BONUS_DAMAGE)
            self.applied = True
            self.entity.game.screen_shake = 17
 
        if self.entity.current_anim.finished:
            self.entity.attack_pos = 0
            self.entity.change_state('idle')
 
        if self.entity.health <= 0:
            self.entity.change_state('dead')
 
 
class Dead(State):
 
    def enter(self):
        self.entity.current_anim = self.entity.anim['dead']
        self.entity.current_anim.reset()
 
    def update(self, dt):
        if self.entity.current_anim.finished:
            self.entity.alive = False
 
 
class LowKick(State):
 
    def enter(self):
        self.entity.current_anim = self.entity.anim['low_kick']
        self.entity.current_anim.reset()
        self.applied = False
 
    def update(self, dt):

 
        if not self.applied and self.entity.current_anim.frame >= 2:
            self.entity.low_kick_hit()
            self.applied = True

 
        if self.entity.current_anim.finished:
            self.entity.change_state('idle')
 
        if self.entity.health <= 0:
            self.entity.change_state('dead')


class PostKnockback(State):

    WAIT_FRAMES = 30  

    def enter(self):
        self.entity.current_anim = self.entity.anim['idle']
        self.entity.current_anim.reset()
        self.timer = self.WAIT_FRAMES

    def update(self, dt):
        self.timer -= 1

        _barrage_combo = ["S", "A", "J"] if self.entity.flip else ["S", "D", "J"]
        if self.entity.combo_buffer[-3:] == _barrage_combo:
            self.entity.combo_buffer.clear()
            self.entity.change_state('chase_for_barrage')
            return

        if self.timer <= 0:
            self.entity.change_state('idle')

        if self.entity.health <= 0:
            self.entity.change_state('dead')

 
class ChaseForBarrage(State):
 
    CHASE_SPEED = 5
    CLOSE_ENOUGH = 15
 
    def enter(self):
        self.entity.current_anim = self.entity.anim['move']
        self.entity.current_anim.reset()
 
    def update(self, dt):
        enemies = self.entity._nearby_enemies(reach=200)
 
        if not enemies:
            self.entity.velocity.x = 0
            self.entity.change_state('idle')
            return
 
        closest = min(enemies, key=lambda e: abs(e.pos.x - self.entity.pos.x))
        dist = abs(closest.pos.x - self.entity.pos.x)
 
        if dist <= self.CLOSE_ENOUGH:
            self.entity.velocity.x = 0
            self.entity.change_state('barrage')
            return
 
        if closest.pos.x > self.entity.pos.x:
            self.entity.velocity.x = self.CHASE_SPEED
            self.entity.flip = False
            self.entity.turn_toggle = False
        else:
            self.entity.velocity.x = -self.CHASE_SPEED
            self.entity.flip = True
            self.entity.turn_toggle = True
 
        if self.entity.health <= 0:
            self.entity.change_state('dead')
 
 
class Grab(State):
 
    GRAB_RANGE = 5
    GRAB_DAMAGE = 0
    SHOVE_POWER = 7
    SHOVE_DURATION = 4
 
    def enter(self):
        self.entity.current_anim = self.entity.anim['grab']
        self.entity.current_anim.reset()
        self.entity.velocity.x = 0
        self.grabbed = False
        self.target_enemy = None
        self.shove_timer  = 0
 
    def update(self, dt):
 
        if self.grabbed and self.target_enemy and self.shove_timer == 0:
            hold_offset = 12 if not self.entity.flip else -12
            self.target_enemy.pos.x = self.entity.pos.x + hold_offset
            self.target_enemy.velocity.x = 0
            self.target_enemy.velocity.y = 0
 
        if self.entity.current_anim.finished and self.grabbed and self.shove_timer == 0:
            self.shove_timer = self.SHOVE_DURATION
            self.target_enemy.damage(self.GRAB_DAMAGE)
 
            shove_dir = 1 if self.entity.flip else -1
            self.target_enemy.velocity.x = shove_dir * self.SHOVE_POWER
 
            self.entity.flip = not self.entity.flip
            self.entity.turn_toggle = self.entity.flip
 
        if self.shove_timer > 0:
            self.shove_timer -= 1
            if self.shove_timer <= 0:
                if self.target_enemy:
                    self.target_enemy.velocity.x = 0
                self.entity.change_state('idle')
 
        elif self.entity.current_anim.finished and not self.grabbed:
            self.entity.change_state('idle')
 
        if self.entity.health <= 0:
            self.entity.change_state('dead')
 
 
class Barrage(State):
 
    BARRAGE_COOLDOWN = 180   
 
    def enter(self):
        if self.entity.barrage_cooldown > 0:
            self.entity.change_state('heavy_attack')
            return
 
        self.entity.current_anim = self.entity.anim['barrage']
        self.entity.current_anim.reset()
 
    def update(self, dt):
 
        if self.entity.current_anim.finished:
            self.entity.barrage_cooldown = self.BARRAGE_COOLDOWN
            self.entity.change_state('idle')
 
 
class Dash(State):
 
    DASH_DURATION = 6
    DASH_SPEED = 2.4
    DASH_COOLDOWN = 45
 
    def enter(self):
        self.entity.current_anim = self.entity.anim['jump']
        self.entity.current_anim.reset()
 
        self.timer = self.DASH_DURATION
        self.dash_dir = -1 if self.entity.flip else 1
 
        self.entity.velocity.x = self.dash_dir * self.DASH_SPEED
        self.entity.dash_cooldown = self.DASH_COOLDOWN
        self.entity.invincible = True
 
    def update(self, dt):
        self.entity.velocity.x = self.dash_dir * self.DASH_SPEED
        self.timer -= 1


        if self.entity.actions['flipped']:
            self.entity.turn_toggle = not self.entity.turn_toggle
            self.entity.flip = self.entity.turn_toggle
            self.dash_dir = -1 if self.entity.flip else 1
            self.entity.actions['flipped'] = False


        if self.entity.actions['light_attack']:
            self.entity.change_state('light_attack')
            return
        if self.entity.actions['heavy_attack']:
            self.entity.change_state('heavy_attack')
            return

        if self.timer <= 0:
            self.entity.velocity.x = 0
            self.entity.change_state(
                'move' if (self.entity.actions['left'] or self.entity.actions['right'])
                else 'idle'
            )

    def exit(self):
        self.entity.invincible = False