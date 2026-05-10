from states.state import State
from pygame import mixer

class Idle(State):
    
    def enter(self):
        if self.entity.velocity.x == 0:
            self.entity.current_anim = self.entity.anim['idle']
    
    def update(self, dt):
        direction = self.entity.game.player.pos - self.entity.pos

        if direction.length() <= 100:
            self.entity.change_state('chase')
        
        if self.entity.health <= 0:
            self.entity.change_state('death')

class Chase(State):

    def enter(self):
        self.entity.current_anim = self.entity.anim['idle']
    
    def update(self, dt):
        
        if self.entity.health == 0:
            self.entity.change_state('death')
        direction = self.entity.game.player.pos - self.entity.pos

        if direction.length() > 18:

            if self.entity.rect().x > (self.entity.game.player.p_rect.x + self.entity.game.player.p_rect.width) - 15:
                self.entity.velocity.x = -0.3
                self.entity.flip = True
            elif self.entity.rect().x + self.entity.rect().width - 10 < self.entity.game.player.p_rect.x :
                self.entity.velocity.x = 0.3
                self.entity.flip = False
        else:
            self.entity.velocity.x = 0
            self.entity.change_state('attack')

class Attack(State):

    def enter(self):
        self.entity.current_anim = self.entity.anim['attack']
        self.entity.current_anim.reset()
        
    
    def update(self, dt):

        if not self.entity.alive:
            return

        if self.entity.current_anim.finished:
            self.entity.game.player.velocity.x = 0
            self.entity.change_state('chase')
        
        if self.entity.health <= 0:
            self.entity.change_state('death')



class Hurt(State):

    def enter(self):
        self.entity.current_anim = self.entity.hurt[self.entity.hit_count]
        self.entity.current_anim.reset()
        mixer.music.load('assets/audio/player/punch.mp3')
        mixer.music.play(0, 0.3)

    def update(self, dt):
        if self.entity.current_anim.finished:
            self.entity.hit_count += 1

            if self.entity.hit_count >= len(self.entity.hurt):
                self.entity.hit_count = 0

            self.entity.change_state('chase')
        
        if self.entity.health <= 0:
            self.entity.change_state('death')

class Dead(State):

    def enter(self):
        self.entity.current_anim = self.entity.anim['death']
        self.entity.current_anim.reset()
        mixer.music.load('assets/audio/emeny/pain.wav')
        mixer.music.play(0, 0.3)


    def update(self, dt):
    
        if self.entity.current_anim.finished:
            self.entity.alive = False