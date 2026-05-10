from states.state import State
from pygame import mixer

'''player state type shi'''

class Idle(State):

    def enter(self):
        
        if self.entity.velocity.x == 0:
            self.entity.current_anim = self.entity.anim['idle']
            print('im ideling it!')

    def update(self, dt):

        if self.entity.velocity.x > 0 or self.entity.velocity.x < 0:
            self.entity.change_state('move')

        elif self.entity.velocity.y < 0:
            self.entity.change_state('jump')
            
        elif self.entity.actions['light_attack']:
            self.entity.change_state('light_attack')
        
        if self.entity.health <= 0:
            self.entity.change_state('dead')
        

        if self.entity.actions['flipped']:
            self.entity.turn_toggle = not self.entity.turn_toggle

            if self.entity.turn_toggle:
                self.entity.change_state('turn_left')
            else:
                self.entity.change_state('turn_right')
            

class Jump(State):

    def enter(self):

        self.entity.current_anim = self.entity.anim['jump']
        print('jump')

    def update(self, dt):

        if self.entity.down:

            if self.entity.velocity.x > 0 or self.entity.velocity.x < 0:
                self.entity.change_state('move')

            elif not self.entity.velocity.x > 0 and not self.entity.velocity.x < 0:
                self.entity.change_state('idle')
        
        if self.entity.health <= 0:
            self.entity.change_state('dead')


class Move(State):

    def enter(self):
        self.entity.current_anim = self.entity.anim['move']
        self.entity.current_anim.reset()

    def update(self, dt):

        if not self.entity.actions['left'] and not self.entity.actions['right']:
            self.entity.change_state('idle')

        elif self.entity.actions['jump']:
            self.entity.change_state('jump')
        
        if self.entity.actions['flipped']:
            self.entity.turn_toggle = not self.entity.turn_toggle

            if self.entity.turn_toggle:
                self.entity.change_state('turn_left')
            else:
                self.entity.change_state('turn_right')
        
        if self.entity.health <= 0:
            self.entity.change_state('dead')

'''flip type shi'''

class TurnLeft(State):

    def enter(self):
        self.entity.current_anim = self.entity.anim['turn']
        self.entity.flip = True
        self.entity.current_anim.reset()
        print('turned left')
    
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
        print('turned left')
    
    def update(self, dt):

        if self.entity.current_anim.finished:

           self.entity.change_state('idle')
        
        if self.entity.health <= 0:
            self.entity.change_state('dead')
       
class Hurt(State):
    
    def enter(self):
        self.entity.current_anim = self.entity.anim['hurt']
        self.entity.current_anim.reset()

        mixer.music.load('assets/audio/player/punch.mp3')
        mixer.music.play(0, 0.3)
    
    def update(self, dt):
        if self.entity.current_anim.finished:
            self.entity.change_state('idle')
        
        if self.entity.health <= 0:
            self.entity.change_state('dead')
        

'''attack'''

class LightAttack(State):

    def enter(self):

        self.entity.current_anim = self.entity.basic_attack[self.entity.attack_pos]

        self.combo_window = False
        self.next_attack = False

        self.entity.current_anim.reset()

        #print('attacked')

    def update(self, dt):

        combo_open = self.entity.current_anim.frame >= 2

        if combo_open:
            self.combo_window = True

        if self.combo_window and self.entity.actions['light_attack']:
            self.next_attack = True

        if self.entity.current_anim.finished:
            
            if self.next_attack:
                self.entity.attack_pos += 1

                if self.entity.attack_pos >= len(self.entity.basic_attack):
                    self.entity.attack_pos = 0
                    
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
        mixer.music.load('assets/audio/emeny/pain.wav')
        mixer.music.play(0, 0.3)

    def update(self, dt):
        
        if self.entity.current_anim.finished:
            self.entity.alive = False

'''attack combo'''


