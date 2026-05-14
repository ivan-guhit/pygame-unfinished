import pygame


class Cutscene:
    def __init__(self, lines):
        
        self.lines = lines
        self.current_line = 0
        self.active = False
        self.done = False
        self.timer = 0
        self.line_delay = 3.0

        self.player = None

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

    def render(self, surface, font, scroll=None):

        if not self.active:
            return


        small_font = pygame.font.Font('assets/fonts/yosterisland/yoster.ttf', 8)
        text_surf = small_font.render(self.lines[self.current_line], True, (255, 255, 255))
        text_w = text_surf.get_width()
        text_h = text_surf.get_height()


        if self.player is not None and scroll is not None:

            px = self.player.pos.x - scroll.x
            py = self.player.pos.y - scroll.y

            text_x = int(px + self.player.size.x / 2 - text_w / 2)

            text_y = int(py - text_h - 6)

     
            text_x = max(0, min(text_x, surface.get_width()  - text_w))
            text_y = max(0, min(text_y, surface.get_height() - text_h))
        else:

            text_x = surface.get_width() // 2 - text_w // 2
            text_y = surface.get_height() - text_h - 4

        shadow_surf = small_font.render(self.lines[self.current_line], True, (0, 0, 0))
        surface.blit(shadow_surf, (text_x + 1, text_y + 1))
        surface.blit(text_surf,   (text_x,     text_y))

    def render_hud(self, window, scroll, surface):

        if not self.active:
            return

        scale_x = window.get_width()  / surface.get_width()
        scale_y = window.get_height() / surface.get_height()

        # Use a readable font size on the actual window
        hud_font = pygame.font.Font('assets/fonts/yosterisland/yoster.ttf', 28)
        text_surf = hud_font.render(self.lines[self.current_line], True, (255, 255, 255))
        shadow_surf = hud_font.render(self.lines[self.current_line], True, (0, 0, 0))

        text_w = text_surf.get_width()
        text_h = text_surf.get_height()

        if self.player is not None:

            px = (self.player.pos.x - scroll.x) * scale_x
            py = (self.player.pos.y - scroll.y) * scale_y


            text_x = int((px) +  50)
            text_y = int((py) - 2)

            text_x = max(0, min(text_x, window.get_width()  - text_w))
            text_y = max(0, min(text_y, window.get_height() - text_h))
        else:
            text_x = window.get_width()  // 2 - text_w // 2
            text_y = window.get_height() - text_h - 8


        window.blit(shadow_surf, (text_x + 1, text_y + 1))
        window.blit(text_surf,   (text_x,     text_y))