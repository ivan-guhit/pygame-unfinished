import pygame

from pygame import Vector2

class Animation():
    def __init__(self, speed, pos, starting_frame, size, spriteshet, frame_length, frame_h=0, loop=True):
        self.speed = speed
        self.pos = pos
        self.frame = starting_frame
        self.tile_size = size
        self.frame_speed = speed
        self.frame_length = frame_length
        self.spriteshet = spriteshet
        self.frame_h = frame_h
        self.finished = False
        self.loop = loop
        



    def play(self, surface, offset, flip):
        
        if flip:
            frame = (self.frame_length - 1) - int(self.frame)
        else:
            frame = int(self.frame)

        frame_loc = Vector2(int(frame), int(self.frame_h)).elementwise() * self.tile_size
        frame_point = pygame.Rect(frame_loc.x, frame_loc.y, self.tile_size.x, self.tile_size.y)

        self.frame += self.frame_speed

        if self.frame >= self.frame_length:
            if self.loop:
                self.frame = 0 
            else:
                self.frame = self.frame_length - 0.01 
            self.finished = True
        

        surface.blit(pygame.transform.flip(self.spriteshet, flip, False), (int(self.pos.x - offset.x), int(self.pos.y - offset.y)), frame_point)

    
    def reset(self):
        self.frame = 0
        self.finished = False



        