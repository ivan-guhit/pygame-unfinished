import pygame
 
 
class ControlsScreen:
 
    CONTROLS = [
        ("Move",         "A  or  D"),
        ("Jump",         "W"),
        ("Turn",         "E"),
        ("Light Attack", "J"),
        ("Heavy Attack", "K"),
        ("Dash",         "SPACE"),
        ("Grab",         "S + J"),
        ("Barrage",      "J + J + K"),
    ]
 
    FADE_IN_SPEED  = 10
    FADE_OUT_SPEED = 2
 
    def __init__(self, tile_size, surface, game_state, game):
        self.tile_size  = tile_size
        self.surface    = surface
        self.game_state = game_state
        self.game       = game
 
        self.alpha      = 0
        self.fading_out = False
        self.fade_out_alpha = 0
 
        self.win_w = game.window.get_width()
        self.win_h = game.window.get_height()
 
        try:
            self.font_title = pygame.font.Font('assets/fonts/yosterisland/yoster.ttf', 48)
            self.font_body  = pygame.font.Font('assets/fonts/yosterisland/yoster.ttf', 28)
            self.font_hint  = pygame.font.Font('assets/fonts/yosterisland/yoster.ttf', 22)
        except Exception:
            self.font_title = pygame.font.SysFont('Arial', 48)
            self.font_body  = pygame.font.SysFont('Arial', 28)
            self.font_hint  = pygame.font.SysFont('Arial', 22)
 
        self._overlay   = pygame.Surface((self.win_w, self.win_h), pygame.SRCALPHA)
        self._blackout  = pygame.Surface((self.win_w, self.win_h))
        self._blackout.fill((0, 0, 0))
 
        self._build_overlay()
 
    def _build_overlay(self):
        ov = self._overlay
        ov.fill((0, 0, 0, 210))
 
        pad_x  = 80
        col2_x = self.win_w // 2 + 40
 
        title = self.font_title.render("CONTROLS", True, (255, 215, 50))
        ov.blit(title, (self.win_w // 2 - title.get_width() // 2, 48))
 
        pygame.draw.line(ov, (255, 215, 50), (pad_x, 112), (self.win_w - pad_x, 112), 2)
 
        row_h   = 52
        start_y = 136
 
        for i, (action, keys) in enumerate(self.CONTROLS):
            y = start_y + i * row_h
 
            if action == "Grab":
                pygame.draw.rect(ov, (90, 50, 0, 180),
                                 (pad_x - 12, y - 6, self.win_w - (pad_x - 12) * 2, row_h - 4))
 
            col_surf = self.font_body.render(action, True, (180, 180, 180))
            val_surf = self.font_body.render(keys,   True, (255, 255, 255))
            ov.blit(col_surf, (pad_x, y))
            ov.blit(val_surf, (col2_x, y))
 
        hint = self.font_hint.render("Press  ENTER  to play", True, (140, 140, 140))
        ov.blit(hint, (self.win_w // 2 - hint.get_width() // 2, self.win_h - 60))
 
    def confirm(self):
        if not self.fading_out:
            self.fading_out = True
 
    def update(self, dt, velocity=None):
        if not self.fading_out:
            if self.alpha < 255:
                self.alpha = min(255, self.alpha + self.FADE_IN_SPEED)
        else:
            self.fade_out_alpha = min(255, self.fade_out_alpha + self.FADE_OUT_SPEED)
            if self.fade_out_alpha >= 255:
                self.game_state.set_state('level1')
 
    def render(self, surface, scroll):
        win = self.game.window
 
        win.fill((10, 10, 20))
 
        self._overlay.set_alpha(self.alpha)
        win.blit(self._overlay, (0, 0))
 
        if self.fading_out:
            self._blackout.set_alpha(self.fade_out_alpha)
            win.blit(self._blackout, (0, 0))
 