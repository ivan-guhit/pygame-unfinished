import pygame


class Cutscene:
    def __init__(self, lines):
        
        self.lines = lines
        self.current_line = 0
        self.active = False
        self.done = False
        self.timer = 0
        self.line_delay = 3.0

        # Reference to the player is set by the level after creation:
        #   self.cutscene.player = self.player
        # If not set, falls back to a fixed screen position.
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
        """Render the current line above the player's head.

        Parameters
        ----------
        surface : pygame.Surface
            The game surface (world-space, before scaling).
        font : pygame.Font
            Font used to render dialogue text (kept for API compat; we use
            our own smaller font internally).
        scroll : pygame.Vector2 | None
            Current camera scroll. Required to convert world-pos to screen-pos.
            If None (or player not set) the text falls back to the bottom bar.
        """
        if not self.active:
            return

        # Use a smaller font for cutscene dialogue (size 8 feels compact and
        # readable on the low-res surface).
        small_font = pygame.font.Font('assets/fonts/yosterisland/yoster.ttf', 8)
        text_surf = small_font.render(self.lines[self.current_line], True, (255, 255, 255))
        text_w = text_surf.get_width()
        text_h = text_surf.get_height()

        # ── Position: above player head ──────────────────────────────────────
        if self.player is not None and scroll is not None:
            # Convert player world-position to surface-space
            px = self.player.pos.x - scroll.x
            py = self.player.pos.y - scroll.y

            text_x = int(px + self.player.size.x / 2 - text_w / 2)
            # Place text just above the player sprite with a small gap
            text_y = int(py - text_h - 6)

            # Clamp so the text stays within the surface
            text_x = max(0, min(text_x, surface.get_width()  - text_w))
            text_y = max(0, min(text_y, surface.get_height() - text_h))
        else:
            # Fallback: bottom of screen
            text_x = surface.get_width() // 2 - text_w // 2
            text_y = surface.get_height() - text_h - 4

        # ── Draw text directly (no background box) ────────────────────────────
        # Thin drop-shadow for legibility against any background
        shadow_surf = small_font.render(self.lines[self.current_line], True, (0, 0, 0))
        surface.blit(shadow_surf, (text_x + 1, text_y + 1))
        surface.blit(text_surf,   (text_x,     text_y))

    def render_hud(self, window, scroll, surface):
        """Render dialogue text directly on the full-resolution window.

        This avoids blurriness caused by drawing small text on the low-res
        surface and then upscaling it.

        Parameters
        ----------
        window  : pygame.Surface  Full-resolution display window.
        scroll  : pygame.Vector2  Current camera scroll (world-space).
        surface : pygame.Surface  The low-res game surface (used to derive scale).
        """
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
            # Convert player world-pos → window-space
            px = (self.player.pos.x - scroll.x) * scale_x
            py = (self.player.pos.y - scroll.y) * scale_y



            text_x = int((px) +  50)
            text_y = int((py) - 2)

            # Clamp within window
            text_x = max(0, min(text_x, window.get_width()  - text_w))
            text_y = max(0, min(text_y, window.get_height() - text_h))
        else:
            text_x = window.get_width()  // 2 - text_w // 2
            text_y = window.get_height() - text_h - 8

        # Drop shadow then text
        window.blit(shadow_surf, (text_x + 1, text_y + 1))
        window.blit(text_surf,   (text_x,     text_y))