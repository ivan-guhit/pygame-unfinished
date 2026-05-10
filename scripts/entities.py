import pygame


from pygame import Vector2, draw
from scripts.utils import load_image

class PhysicsEntity():
    def __init__(self, game, health, e_type, pos, size, tile_size):
        self.game = game
        self.e_type = e_type
        self.pos = pos
        self.size = size
        self.anim_size = tile_size

        self.down = False
        self.midair = False

        self.velocity = Vector2(0,0)
        self.crop_img = pygame.Rect(0,0, 32, 32)

        self.turn_toggle = False
        self.flip = False

        self.health = health

    def rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
        
    def damage(self, hit):
        self.health -= hit
        print(self.health)

    def update(self, movement, tiles, dt):

        self.down = False
        self.midair = False

        rects = tiles

        frame_movementX = movement.x + self.velocity.x
        frame_movementY = movement.y + self.velocity.y

        self.pos.x += frame_movementX 

        self.p_rect = self.rect()
        
        for tile in rects:
            if self.p_rect.colliderect(tile):
                if frame_movementX > 0:
                    self.p_rect.right = tile.left
                    #print('collisioning')
                if frame_movementX < 0:
                    self.p_rect.left = tile.right
                    #print('collisioning')
                self.pos.x = self.p_rect.x

        self.pos.y += frame_movementY 
        
        self.p_rect = self.rect()
        
        for tile in rects:
            if self.p_rect.colliderect(tile):
                if frame_movementY > 0:
                    self.p_rect.bottom = tile.top
                    self.down = True
                    #print('collisioning')
                if frame_movementY < 0:
                    self.p_rect.top = tile.bottom
                    self.midair = True
                    #print('collisioning')
                self.pos.y = self.p_rect.y

        self.velocity.y = min(5, self.velocity.y + 0.4)

        if self.down:
            frame_movementY = 0
            self.game.actions['jump'] = False
        
        if self.midair:
            self.velocity.y = 0

    def change_state(self, state_name):
        self.current_state.exit()
        self.current_state = self.states[state_name]
        self.current_state.enter()
        
    def render(self, surface, offset):
        if self.current_anim:
            self.current_anim.play(surface, offset, self.flip)
            

    

    
    
    

        

        


