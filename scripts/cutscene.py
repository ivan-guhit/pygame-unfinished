import pygame

class Cutscene:
    def __init__(self, lines):
        
        self.lines = lines
        self.current_line = 0
        self.active = False
        self.done = False
        self.timer = 0
        self.line_delay = 3.0  

    def start(self):

        self.active = True
        self.current_line = 0
        self.done = False

    def update(self, delta):
        if not self.active:
            return
        self.timer += delta
        if self.timer >= self.line_delay:
            self.timer = 0
            self.current_line += 1
            if self.current_line >= len(self.lines):
                self.active = False
                self.done = True

    def render(self, surface, font):
        if not self.active:
            return

        box = pygame.Surface((surface.get_width(), 30), pygame.SRCALPHA)
        box.fill((0, 0, 0, 180))
        surface.blit(box, (0, surface.get_height() - 30))

        text = font.render(self.lines[self.current_line], True, (255, 255, 255))
        surface.blit(text, (4, surface.get_height() - 26))