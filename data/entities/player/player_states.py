from states.state import State
 

 
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

        elif self.entity.combo_buffer[-3:] == ["J", "J", "K"]:
            self.entity.combo_buffer.clear()
            self.entity.change_state("barrage")

        elif self.entity.actions['light_attack']:
            self.entity.change_state('light_attack')

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
        self.combo_window = False
        self.next_attack = False
        self.entity.current_anim.reset()
    def update(self, dt):

        if self.entity.current_anim.frame >= 2:
            self.combo_window = True

        if self.combo_window and self.entity.actions['light_attack']:
            self.next_attack = True

        if self.entity.current_anim.finished:

            if self.next_attack:
                self.entity.attack_pos = (self.entity.attack_pos + 1) % len(self.entity.basic_attack)
                self.entity.change_state('light_attack')
            else:
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
        self.entity.change_state('grab')
    def update(self, dt):
        pass
 
class Grab(State):

    GRAB_RANGE = 25
    GRAB_DAMAGE = 10
    SHOVE_POWER = 8
    SHOVE_DURATION = 4

    def enter(self):

        self.entity.current_anim = self.entity.anim['grab']
        self.entity.current_anim.reset()
        self.entity.velocity.x = 0
        self.grabbed = False
        self.target_enemy = None
        self.shove_timer = 0 

    def update(self, dt):

        if self.grabbed and self.target_enemy and self.shove_timer == 0:

            if not self.entity.flip:
                hold_offset = 12
            else:
                hold_offset = -12

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

    def enter(self):

        self.entity.current_anim = self.entity.anim['barrage']
        self.entity.current_anim.reset()

    def update(self, dt):

        if self.entity.current_anim.finished:
            self.entity.change_state('idle')
 
class Dash(State):

    DASH_DURATION = 6
    DASH_SPEED = 2.4
    DASH_COOLDOWN = 45

    def enter(self):

        self.entity.current_anim = self.entity.anim['jump']
        self.entity.current_anim.reset()

        self.timer = self.DASH_DURATION

        if self.entity.flip:
            self.dash_dir = -1
        else:
            self.dash_dir = 1


        self.entity.velocity.x = self.dash_dir * self.DASH_SPEED

        self.entity.dash_cooldown = self.DASH_COOLDOWN
        self.entity.invincible = True

    def update(self, dt):

        self.entity.velocity.x = self.dash_dir * self.DASH_SPEED

        self.timer -= 1

        if self.timer <= 0:

            self.entity.velocity.x = 0

            self.entity.change_state(
                'move'
                if (self.entity.actions['left'] or self.entity.actions['right'])
                else 'idle'
            )

    def exit(self):
        self.entity.invincible = False