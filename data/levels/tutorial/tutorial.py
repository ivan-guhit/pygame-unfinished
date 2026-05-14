import pygame

from pygame import Vector2, Rect
from data.entities.emeny.emeny.emeny import Emeny



BG_COLOUR    = (18,  8, 30)
GROUND_COLOUR = (90, 40, 130)
WORLD_W = 192
WORLD_H = 128

GROUND_Y = 96
GROUND_H = 32

PLAYER_SPAWN_PX = Vector2(48, 64)

DUMMY_OFFSET_X  =  40
BEHIND_OFFSET_X = -40

E_SIZE = Vector2(20, 27)

# All steps except the last are practice (dummy enemy, immortal).
# The last step is a real fight — kill the enemy to proceed.
STEPS = [
    {
        'label'       : 'MOVE: A or D',
        'hint'        : 'Walk left and right',
        'goal'        : lambda t: t.player.current_state == t.player.states['move'],
        'spawn_enemy' : False,
        'need_hit'    : False,
    },
    {
        'label'       : 'JUMP: W',
        'hint'        : '',
        'goal'        : lambda t: t.player.current_state == t.player.states['jump'],
        'spawn_enemy' : False,
        'need_hit'    : False,
    },
    {
        'label'       : 'LIGHT ATTACK: J',
        'hint'        : 'Hit the enemy!',
        'goal'        : lambda t: t._hit_landed,
        'spawn_enemy' : True,
        'need_hit'    : True,
    },
    {
        'label'       : 'HEAVY ATTACK: K',
        'hint'        : 'Hit the enemy!',
        'goal'        : lambda t: t._hit_landed,
        'spawn_enemy' : True,
        'need_hit'    : True,
    },
    {
        'label'       : 'DASH: SPACE',
        'hint'        : 'Invincible while dashing',
        'goal'        : lambda t: t.player.current_state == t.player.states['dash'],
        'spawn_enemy' : False,
        'need_hit'    : False,
    },
    {
        'label'       : 'TURN: E  (enemy behind!)',
        'hint'        : 'Press E to face the other way',
        'goal'        : lambda t: t._turn_done,
        'spawn_enemy' : True,
        'behind'      : True,
        'need_hit'    : False,
    },
    {
        'label'       : 'GRAB: S then J',
        'hint'        : 'Get close and grab the enemy!',
        'goal'        : lambda t: t._hit_landed,
        'spawn_enemy' : True,
        'need_hit'    : True,
    },
    {
        'label'       : 'LOW KICK: S + K',
        'hint'        : 'Knocks the enemy down!',
        'goal'        : lambda t: t._hit_landed,
        'spawn_enemy' : True,
        'need_hit'    : True,
    },
    {
        'label'       : 'BARRAGE (facing right): S D J',
        'hint'        : 'Input S, D, J in sequence',
        'goal'        : lambda t: t._hit_landed,
        'spawn_enemy' : True,
        'need_hit'    : True,
        'behind'      : False,
    },
    {
        'label'       : 'BARRAGE (facing left): S A J',
        'hint'        : 'Turn around first (E), then S, A, J',
        'goal'        : lambda t: t._hit_landed,
        'spawn_enemy' : True,
        'need_hit'    : True,
        'behind'      : True,
    },
    {
        'label'       : 'COMBO: J J K',
        'hint'        : 'Two lights then heavy — must connect!',
        'goal'        : lambda t: t._knockback_finisher_hit,
        'spawn_enemy' : True,
        'need_hit'    : True,
    },
    {
        'label'       : 'COMBO: K K K J',
        'hint'        : 'Three heavies then light finish — must connect!',
        'goal'        : lambda t: t._heavy_finisher_hit,
        'spawn_enemy' : True,
        'need_hit'    : True,
    },
    {
        'label'       : 'COMBO: J J K then SDJ',
        'hint'        : 'J J K then: facing right S D J  |  facing left S A J',
        'goal'        : lambda t: t._knockback_finisher_hit and t._hit_landed,
        'spawn_enemy' : True,
        'need_hit'    : True,
    },
    # ── FINAL STEP: real fight ───────────────────────────────────────────────
    {
        'label'       : 'FINAL TEST: defeat the enemy!',
        'hint'        : 'Use everything you learned',
        'goal'        : lambda t: t._final_enemy_dead,
        'spawn_enemy' : True,
        'final_fight' : True,
        'need_hit'    : False,
    },
]

FINAL_STEP = len(STEPS) - 1


class Tutorial:
    def __init__(self, player, tile_size, actions, game):
        self.player    = player
        self.tile_size = tile_size
        self.actions   = actions
        self.game      = game

        self.size = Vector2(WORLD_W, WORLD_H)

        win_w = game.window.get_width()
        win_h = game.window.get_height()

        self.font_big  = pygame.font.Font('assets/fonts/yosterisland/yoster.ttf', 28)
        self.font_sm   = pygame.font.Font('assets/fonts/yosterisland/yoster.ttf', 16)
        self.font_warn = pygame.font.Font('assets/fonts/yosterisland/yoster.ttf', 36)
        # Bigger font for the "L -> next step" prompt
        self.font_next = pygame.font.Font('assets/fonts/yosterisland/yoster.ttf', 24)

        self._blackout = pygame.Surface((win_w, win_h))
        self._blackout.fill((0, 0, 0))

        self.collisions = [
            Rect(0,            GROUND_Y, WORLD_W,          GROUND_H),
            Rect(-tile_size.x, 0,        int(tile_size.x), WORLD_H),
            Rect(WORLD_W,      0,        int(tile_size.x), WORLD_H),
        ]

        self.step_index        = 0
        self.step_done         = False
        self.waiting           = False
        self._turn_done        = False
        self._final_enemy_dead = False

        # After the final enemy is killed, player must walk to the right edge
        self._final_cleared    = False

        # Hit-tracking flags — reset each step, set by notify_*() methods
        self._hit_landed             = False   # any attack connected
        self._knockback_finisher_hit = False   # J J K finisher connected
        self._heavy_finisher_hit     = False   # K K K J finisher connected

        FADE_DURATION    = 0.4
        self._fading     = False
        self._fade_t     = 0.0
        self._fade_dur   = FADE_DURATION
        self._fade_alpha = 255

        self._outro       = False
        self._outro_t     = 0.0
        self._outro_dur   = 1.2
        self._outro_alpha = 0

        # ── skip-warning overlay ─────────────────────────────────────────────
        self._warn_active       = False
        self._warn_timer        = 0.0
        self._warn_dur          = 2.5      # seconds warning stays visible
        self._warn_fade_in      = 0.3      # seconds to fade in
        self._warn_alpha        = 0
        # Second ENTER press while warning is showing skips immediately
        self._warn_confirm_ready = False

        self.enemies: list = []

        self._start_step(0)

    # ─────────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _spawn_enemy(self, behind=False, real_hp=False):
        offset  = BEHIND_OFFSET_X if behind else DUMMY_OFFSET_X
        spawn_x = max(E_SIZE.x, min(WORLD_W - E_SIZE.x, self.player.pos.x + offset))
        spawn_y = GROUND_Y - E_SIZE.y

        hp = 100 if real_hp else 9999
        e  = Emeny(self.game, hp, self.player, 'emeny',
                   Vector2(spawn_x, spawn_y), E_SIZE, self.tile_size)

        # Flip enemy to face the player:
        #   spawned to the RIGHT of the player → flip=True  (facing left)
        #   spawned to the LEFT  of the player → flip=False (facing right)
        e.flip = spawn_x > self.player.pos.x

        self.enemies.append(e)

    def _start_step(self, index):
        self.step_index              = index
        self.step_done               = False
        self.waiting                 = False
        self._turn_done              = False
        self._final_enemy_dead       = False
        self._final_cleared          = False
        self._hit_landed             = False
        self._knockback_finisher_hit = False
        self._heavy_finisher_hit     = False
        self._fading           = False
        self._fade_t           = 0.0
        self._fade_alpha       = 255
        self.enemies.clear()

        self.player.pos.x    = PLAYER_SPAWN_PX.x
        self.player.pos.y    = PLAYER_SPAWN_PX.y
        self.player.velocity = Vector2(0, 0)
        self.player.health   = 99999
        self.player.change_state('idle')

        step = STEPS[index]
        if step.get('spawn_enemy', False):
            self._spawn_enemy(
                behind=step.get('behind', False),
                real_hp=step.get('final_fight', False),
            )

    def _next_step(self):
        if self.step_index + 1 >= len(STEPS):
            self._outro   = True
            self._outro_t = 0.0
            return
        self._start_step(self.step_index + 1)

    # ─────────────────────────────────────────────────────────────────────────
    # Public input hooks (called from game.py)
    # ─────────────────────────────────────────────────────────────────────────

    def handle_enter(self):
        """ENTER: first press shows the 'game hard' warning.
        Second press while warning is visible skips immediately to level1."""
        if self._warn_active:
            # Second press — skip immediately
            if self._warn_confirm_ready:
                self._warn_active = False
                self._outro       = True
                self._outro_t     = 0.0
        elif not self._outro:
            # First press — show warning
            self._warn_active        = True
            self._warn_timer         = 0.0
            self._warn_alpha         = 0
            self._warn_confirm_ready = False

    def handle_l_advance(self):
        """L: advance to the next step when waiting."""
        if self.waiting:
            self._next_step()

    # Called by player.py when an attack actually lands on an enemy
    def notify_hit(self):
        self._hit_landed = True

    def notify_knockback_finisher_hit(self):
        self._knockback_finisher_hit = True
        self._hit_landed = True

    def notify_heavy_finisher_hit(self):
        self._heavy_finisher_hit = True
        self._hit_landed = True

    # ─────────────────────────────────────────────────────────────────────────
    # Update
    # ─────────────────────────────────────────────────────────────────────────

    def update(self, dt, velocity):
        step     = STEPS[self.step_index]
        is_final = step.get('final_fight', False)

        # ── skip-warning: freeze gameplay while warning is shown ─────────────
        if self._warn_active:
            self._warn_timer += dt
            if self._warn_timer < self._warn_fade_in:
                self._warn_alpha = int(255 * (self._warn_timer / self._warn_fade_in))
            else:
                self._warn_alpha = 255
                self._warn_confirm_ready = True  # ready for second ENTER

            if self._warn_timer >= self._warn_dur:
                # Auto-dismiss after timeout (no skip, just close warning)
                self._warn_active = False
            return

        # ── turn-step detection ──────────────────────────────────────────────
        if step.get('behind') and not self._turn_done:
            if self.player.current_state in (
                    self.player.states['turn_left'],
                    self.player.states['turn_right']):
                self._turn_done = True

        # ── player ───────────────────────────────────────────────────────────
        self.player.update(velocity, self.collisions, dt)

        # ── enemies ──────────────────────────────────────────────────────────
        passive_keys = {'hurt', 'down', 'stand_up', 'death'}

        for e in self.enemies:
            in_passive = any(
                e.current_state == e.states[k]
                for k in passive_keys if k in e.states
            )

            if is_final:
                # Real fight: normal AI (chase + attack)
                e.update(velocity, self.collisions, dt)
                if e.alive:
                    e.attack()
            else:
                # Practice: enemy stands idle and cannot die
                if not in_passive:
                    e.velocity.x = 0
                    if e.current_state != e.states['idle']:
                        e.change_state('idle')

                e.update(velocity, self.collisions, dt)

                if not in_passive and e.current_state != e.states['idle']:
                    e.change_state('idle')

                if e.health <= 0:
                    e.health = 9999
                    if e.alive:
                        e.change_state('idle')

        # ── player attacks ───────────────────────────────────────────────────
        for e in self.enemies:
            if e.alive:
                self.player.attack(e)

        # ── enemy list cleanup & respawn logic ───────────────────────────────
        self.enemies = [e for e in self.enemies if e.alive]

        if is_final:
            # Detect final enemy kill — transition to level1 immediately
            if not self.enemies and not self._final_enemy_dead:
                self._final_enemy_dead = True
                self._final_cleared    = True
                self._outro            = True
                self._outro_t          = 0.0
        else:
            # Respawn dummy if killed somehow
            if step.get('spawn_enemy') and not self.enemies:
                self._spawn_enemy(behind=step.get('behind', False), real_hp=False)

        # ── fade after goal ──────────────────────────────────────────────────
        if self._fading:
            self._fade_t += dt
            progress         = min(self._fade_t / self._fade_dur, 1.0)
            self._fade_alpha = int(255 * (1.0 - progress))
            if progress >= 1.0:
                self._fading = False
                self.waiting = True

        # ── outro ────────────────────────────────────────────────────────────
        if self._outro:
            self._outro_t += dt
            progress          = min(self._outro_t / self._outro_dur, 1.0)
            self._outro_alpha = int(255 * progress)
            if progress >= 1.0:
                self.game.game_state.set_state('level1')
                return

        # ── goal check ───────────────────────────────────────────────────────
        if not self.step_done and not self.waiting and not self._fading:
            if step['goal'](self):
                self.step_done   = True
                self._fading     = True
                self._fade_t     = 0.0
                self._fade_alpha = 255

    # ─────────────────────────────────────────────────────────────────────────
    # Render
    # ─────────────────────────────────────────────────────────────────────────

    def render(self, surface, scroll):
        surface.fill(BG_COLOUR)

        gy = GROUND_Y - int(scroll.y)
        pygame.draw.rect(surface, GROUND_COLOUR, Rect(0, gy, surface.get_width(), GROUND_H))
        pygame.draw.line(surface, (150, 90, 210), (0, gy), (surface.get_width(), gy), 1)

        self.player.render(surface, scroll)
        for e in self.enemies:
            e.render(surface, scroll)


    def render_hud(self, win):
        self._render_guide(win)

    def _render_guide(self, win):
        step = STEPS[self.step_index]
        ww, wh = win.get_size()

        # ── top banner ───────────────────────────────────────────────────────
        banner = pygame.Surface((ww, 64), pygame.SRCALPHA)
        banner.fill((0, 0, 0, 180))
        win.blit(banner, (0, 0))

        counter = self.font_sm.render(
            f'Step {self.step_index + 1} / {len(STEPS)}', True, (120, 140, 160))
        win.blit(counter, (20, 8))

        skip_hint = self.font_sm.render('ENTER -> skip tutorial', True, (100, 100, 120))
        win.blit(skip_hint, (ww - skip_hint.get_width() - 16, 8))

        label_text = step['label']
        label_srf = self.font_big.render(label_text, True, (255, 220, 80))
        if self._fade_alpha < 255:
            label_srf.set_alpha(self._fade_alpha)
        win.blit(label_srf, (ww // 2 - label_srf.get_width() // 2, 10))

        if step['hint']:
            hint_text = step['hint']
            sub = self.font_sm.render(hint_text, True, (160, 200, 160))
            if self._fade_alpha < 255:
                sub.set_alpha(self._fade_alpha)
            win.blit(sub, (ww // 2 - sub.get_width() // 2, 42))

        # ── "L → next step" prompt (bigger font) ─────────────────────────────
        if self.waiting:
            next_prompt = self.font_next.render('L -> next step', True, (80, 255, 140))
            win.blit(next_prompt, (ww - next_prompt.get_width() - 16, wh - 40))


        # ── progress dots ────────────────────────────────────────────────────
        dot_r   = 5
        spacing = 18
        total_w = (len(STEPS) - 1) * spacing + dot_r * 2
        start_x = ww // 2 - total_w // 2
        for i in range(len(STEPS)):
            colour = (255, 220, 80) if i == self.step_index else \
                     (80, 160, 80)  if i < self.step_index  else \
                     (60, 80, 100)
            pygame.draw.circle(win, colour, (start_x + i * spacing, wh - 24), dot_r)

        # ── outro fade ───────────────────────────────────────────────────────
        if self._outro and self._outro_alpha > 0:
            self._blackout.set_alpha(self._outro_alpha)
            win.blit(self._blackout, (0, 0))

        # ── skip-warning overlay ─────────────────────────────────────────────
        if self._warn_active:
            dark = pygame.Surface((ww, wh), pygame.SRCALPHA)
            dark.fill((0, 0, 0, 160))
            dark.set_alpha(self._warn_alpha)
            win.blit(dark, (0, 0))

            w1 = self.font_warn.render('WARNING', True, (255, 60, 60))
            w2 = self.font_big.render('This game is hard!', True, (255, 200, 80))
            w3 = self.font_sm.render(
                'Skipping the tutorial is not recommended...', True, (200, 200, 200))
            # "Press ENTER again" shown once the warning has fully faded in
            w4 = self.font_sm.render('Press ENTER again to skip anyway', True, (255, 140, 140))

            for surf in (w1, w2, w3, w4):
                surf.set_alpha(self._warn_alpha)

            cx = ww // 2
            win.blit(w1, (cx - w1.get_width() // 2, wh // 2 - 80))
            win.blit(w2, (cx - w2.get_width() // 2, wh // 2 - 30))
            win.blit(w3, (cx - w3.get_width() // 2, wh // 2 + 20))
            win.blit(w4, (cx - w4.get_width() // 2, wh // 2 + 55))