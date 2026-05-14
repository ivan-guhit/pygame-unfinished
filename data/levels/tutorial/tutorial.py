import pygame

from pygame import Vector2, Rect
from data.entities.emeny.emeny.emeny import Emeny



BG_COLOUR = (18,  8, 30)   
GROUND_COLOUR = (90, 40, 130)   
WORLD_W = 192
WORLD_H = 128

GROUND_Y = 96
GROUND_H = 32

PLAYER_SPAWN_PX = Vector2(48, 64)

DUMMY_OFFSET_X  =  40
BEHIND_OFFSET_X = -40

E_SIZE = Vector2(20, 27)

STEPS = [
    {
        'label'       : 'MOVE: A or D',
        'hint'        : 'Walk left and right',
        'goal'        : lambda t: t.player.current_state == t.player.states['move'],
        'spawn_enemy' : False,
    },
    {
        'label'       : 'JUMP: W',
        'hint'        : '',
        'goal'        : lambda t: t.player.current_state == t.player.states['jump'],
        'spawn_enemy' : False,
    },
    {
        'label'       : 'LIGHT ATTACK: J',
        'hint'        : '',
        'goal'        : lambda t: t.player.current_state == t.player.states['light_attack'],
        'spawn_enemy' : True,
    },
    {
        'label'       : 'HEAVY ATTACK: K',
        'hint'        : '',
        'goal'        : lambda t: t.player.current_state == t.player.states['heavy_attack'],
        'spawn_enemy' : True,
    },
    {
        'label'       : 'DASH: SPACE',
        'hint'        : 'Invincible while dashing',
        'goal'        : lambda t: t.player.current_state == t.player.states['dash'],
        'spawn_enemy' : False,
    },
    {
        'label'       : 'TURN: E  (enemy behind!)',
        'hint'        : 'Press E to face the other way',
        'goal'        : lambda t: t._turn_done,
        'spawn_enemy' : True,
        'behind'      : True,
    },
    {
        'label'       : 'GRAB: S then J',
        'hint'        : 'Press S then J quickly',
        'goal'        : lambda t: t.player.current_state == t.player.states['grab'],
        'spawn_enemy' : True,
    },
    {
        'label'       : 'LOW KICK: S + K',
        'hint'        : 'Knocks the enemy down',
        'goal'        : lambda t: t.player.current_state == t.player.states['low_kick'],
        'spawn_enemy' : True,
    },
    {
        'label'       : 'COMBO: S D J -> BARRAGE',
        'hint'        : 'Input S, D, J in sequence',
        'goal'        : lambda t: t.player.current_state == t.player.states['barrage'],
        'spawn_enemy' : True,
    },
    {
        'label'       : 'COMBO: J J K -> 2L+1H',
        'hint'        : 'Two lights then heavy finisher',
        'goal'        : lambda t: t.player.current_state == t.player.states['light_attack'],
        'spawn_enemy' : True,
    },
    {
        'label'       : 'COMBO: K K K J -> 3H+1L',
        'hint'        : 'Three heavies then light finish',
        'goal'        : lambda t: t.player.current_state == t.player.states['light_attack'],
        'spawn_enemy' : True,
    },
    {
        'label'       : 'COMBO: J J K then SDJ',
        'hint'        : 'knockback then chase with barrage',
        'goal'        : lambda t: t.player.current_state == t.player.states['light_attack'],
        'spawn_enemy' : True,
    },
]


class Tutorial:
    def __init__(self, player, tile_size, actions, game):
        self.player = player
        self.tile_size = tile_size
        self.actions = actions
        self.game = game

        self.size = Vector2(WORLD_W, WORLD_H)


        win_w = game.window.get_width()
        win_h = game.window.get_height()


        self.font_big = pygame.font.Font('assets/fonts/yosterisland/yoster.ttf', 28)
        self.font_sm  = pygame.font.Font('assets/fonts/yosterisland/yoster.ttf', 16)


        self._blackout = pygame.Surface((win_w, win_h))
        self._blackout.fill((0, 0, 0))


        self.collisions = [Rect(0, GROUND_Y, WORLD_W,  GROUND_H), Rect(-tile_size.x, 0, int(tile_size.x), WORLD_H), Rect(WORLD_W, 0, int(tile_size.x), WORLD_H),]

        self.step_index = 0
        self.step_done = False
        self.waiting = False
        self._turn_done = False


        FADE_DURATION = 0.4
        self._fading = False
        self._fade_t = 0.0
        self._fade_dur = FADE_DURATION
        self._fade_alpha = 255

        self._outro = False   
        self._outro_t = 0.0
        self._outro_dur = 1.2     
        self._outro_alpha = 0       

        self.enemies: list = []

        self._start_step(0)

    def _spawn_enemy(self, behind=False):
        offset  = BEHIND_OFFSET_X if behind else DUMMY_OFFSET_X
        spawn_x = max(E_SIZE.x, min(WORLD_W - E_SIZE.x, self.player.pos.x + offset))
        spawn_y = GROUND_Y - E_SIZE.y  
        e = Emeny(self.game, 9999, self.player, 'emeny', Vector2(spawn_x, spawn_y), E_SIZE, self.tile_size,)
        self.enemies.append(e)

    def _start_step(self, index):
        self.step_index = index
        self.step_done = False
        self.waiting = False
        self._turn_done = False
        self._fading = False
        self._fade_t = 0.0
        self._fade_alpha = 255
        self.enemies.clear()

        self.player.pos.x = PLAYER_SPAWN_PX.x
        self.player.pos.y = PLAYER_SPAWN_PX.y
        self.player.velocity = Vector2(0, 0)
        self.player.health = 99999
        self.player.change_state('idle')

        step = STEPS[index]
        if step.get('spawn_enemy', False):
            self._spawn_enemy(behind=step.get('behind', False))

    def _next_step(self):
        if self.step_index + 1 >= len(STEPS):
            self._outro   = True
            self._outro_t = 0.0
            return
        self._start_step(self.step_index + 1)



    def handle_enter(self):
        if self.waiting:
            self._next_step()


    def update(self, dt, velocity):
        step = STEPS[self.step_index]

  
        if step.get('behind') and not self._turn_done:
            if self.player.current_state in (self.player.states['turn_left'],self.player.states['turn_right']):
                self._turn_done = True


        self.player.update(velocity, self.collisions, dt)


        passive_keys = {'hurt', 'down', 'stand_up', 'death'}
        for e in self.enemies:

            in_passive = any(e.current_state == e.states[k] for k in passive_keys if k in e.states)

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


        for e in self.enemies:
            if e.alive:
                self.player.attack(e)

        self.enemies = [e for e in self.enemies if e.alive]
        if step.get('spawn_enemy') and not self.enemies:
            self._spawn_enemy(behind=step.get('behind', False))


        if self._fading:
            self._fade_t += dt
            progress = min(self._fade_t / self._fade_dur, 1.0)
            self._fade_alpha = int(255 * (1.0 - progress))
            if progress >= 1.0:
                self._fading = False
                self.waiting = True  


        if self._outro:
            self._outro_t += dt
            progress = min(self._outro_t / self._outro_dur, 1.0)
            self._outro_alpha = int(255 * progress)
            if progress >= 1.0:
                self.game.game_state.set_state('level1')
                return


        if not self.step_done and not self.waiting and not self._fading:
            if step['goal'](self):
                self.step_done  = True
                self._fading = True   
                self._fade_t = 0.0
                self._fade_alpha = 255


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

        
        banner = pygame.Surface((ww, 64), pygame.SRCALPHA)
        banner.fill((0, 0, 0, 180))
        win.blit(banner, (0, 0))

       
        counter = self.font_sm.render(f'Step {self.step_index + 1} / {len(STEPS)}', True, (120, 140, 160))
        win.blit(counter, (20, 8))

        
        hint_srf = self.font_big.render(step['label'], True, (255, 220, 80))
        if self._fade_alpha < 255:
            hint_srf.set_alpha(self._fade_alpha)
        win.blit(hint_srf, (ww // 2 - hint_srf.get_width() // 2, 10))

        
        if step['hint']:
            sub = self.font_sm.render(step['hint'], True, (160, 200, 160))
            if self._fade_alpha < 255:
                sub.set_alpha(self._fade_alpha)
            win.blit(sub, (ww // 2 - sub.get_width() // 2, 42))

        if self.waiting:
            skip = self.font_sm.render('ENTER -> next step', True, (80, 255, 140))
            win.blit(skip, (ww - skip.get_width() - 16, wh - 24))

   
        dot_r   = 5
        spacing = 18
        total_w = (len(STEPS) - 1) * spacing + dot_r * 2
        start_x = ww // 2 - total_w // 2
        for i in range(len(STEPS)):
            if i == self.step_index:
                colour = (255, 220, 80)
            elif i < self.step_index:
                colour = (80, 160, 80)
            else:
                colour = (60, 80, 100)
            pygame.draw.circle(win, colour, (start_x + i * spacing, wh - 24), dot_r)

        if self._outro and self._outro_alpha > 0:
            self._blackout.set_alpha(self._outro_alpha)
            win.blit(self._blackout, (0, 0))