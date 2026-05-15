from states.state import State


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


class Fall(State):

    def enter(self):
        if self.entity.velocity.y > 0:
            self.entity.current_anim = self.entity.anim['fall']

    def update(self, dt):
        if self.entity.velocity.y == 0:
            self.entity.change_state('idle')


class Chase(State):

    def enter(self):
        self.entity.current_anim = self.entity.anim['chase']

    def update(self, dt):
        if self.entity.health == 0:
            self.entity.change_state('death')

        direction = self.entity.game.player.pos - self.entity.pos

        if direction.length() > 18:
            if self.entity.rect().x > (self.entity.game.player.p_rect.x + self.entity.game.player.p_rect.width) - 15:
                self.entity.velocity.x = -0.3
                self.entity.flip = True
            elif self.entity.rect().x + self.entity.rect().width - 10 < self.entity.game.player.p_rect.x:
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

    def update(self, dt):
        if self.entity.current_anim.finished:
            self.entity.hit_count += 1

            if self.entity.hit_count >= len(self.entity.hurt):
                self.entity.hit_count = 0

            if self.entity.interrupted_attack:
                self.entity.interrupted_attack = False
                self.entity.change_state('attack')
            else:
                self.entity.change_state('chase')

        if self.entity.health <= 0:
            self.entity.change_state('death')


class Dead(State):

    def enter(self):
        self.entity.current_anim = self.entity.anim['death']
        self.entity.current_anim.reset()

    def update(self, dt):
        if self.entity.current_anim.finished:
            self.entity.alive = False


class Down(State):
    def enter(self):
        self.entity.current_anim = self.entity.anim['down']
        self.entity.current_anim.reset()
        self.entity.velocity.x = 0
        self.entity.velocity.y = 0

    def update(self, dt):
        if self.entity.current_anim.finished:
            self.entity.change_state('stand_up')

        if self.entity.health <= 0:
            self.entity.change_state('death')


class StandUp(State):

    def enter(self):
        self.entity.current_anim = self.entity.anim['stand_up']
        self.entity.current_anim.reset()

    def update(self, dt):
        if self.entity.current_anim.finished:
            self.entity.change_state('chase')

        if self.entity.health <= 0:
            self.entity.change_state('death')


class Block(State):

    # Combos that trigger a counter-attack (quick_attack state).
    COUNTER_COMBOS = [
        ('light', 'light'),   # J J
        ('light', 'heavy'),   # J K
        ('heavy', 'light'),   # K J
    ]

    # The specific combo that breaks the block entirely.
    # K K K J = three heavy_attack hits (each 'heavy') + HeavyFinisher (also
    # fed as 'heavy' by heavy_damage_combo) → four consecutive 'heavy' entries.
    BREAK_COMBO = ('heavy', 'heavy', 'heavy', 'heavy')  # K K K J

    _MAX_LEN = max(
        max(len(c) for c in COUNTER_COMBOS),
        len(BREAK_COMBO),
    )

    def enter(self):
        self.entity.current_anim = self.entity.anim['block']
        self.entity.current_anim.reset()
        self._hit_sequence = []
        self.entity.velocity.x = 0
        # Remember what the enemy was doing so QuickAttack can return to it.
        prev = self.entity.current_state
        state_map = {v: k for k, v in self.entity.states.items()}
        self.entity._pre_block_state = state_map.get(prev, 'chase')
        # Delayed flip: counts down when player is behind, resets when they move front.
        self._flip_delay = 0
        self._FLIP_DELAY_MAX = 90  # ~1.5 seconds at 60 fps

    def update(self, dt):
        self.entity.velocity.x = 0

        if self.entity.health <= 0:
            self.entity.change_state('death')

        # If the player is behind the enemy, count down and flip to face them.
        if self.entity._player_is_behind():
            self._flip_delay += 1
            if self._flip_delay >= self._FLIP_DELAY_MAX:
                self._flip_delay = 0
                self.entity.flip = not self.entity.flip
        else:
            # Player moved back in front — reset the delay.
            self._flip_delay = 0

    def register_block_hit(self, hit_type='light'):
        # FIX: barrage and low_kick hits are not part of any combo pattern.
        # Letting them into _hit_sequence would corrupt the K K K J break
        # sequence and prevent it from ever matching.
        if hit_type not in ('light', 'heavy'):
            return

        self._hit_sequence.append(hit_type)

        # Keep only as many entries as the longest pattern we need to match.
        if len(self._hit_sequence) > self._MAX_LEN:
            self._hit_sequence = self._hit_sequence[-self._MAX_LEN:]

        # --- Check block-break first (K K K J = four 'heavy' entries) ---
        n_break = len(self.BREAK_COMBO)
        if tuple(self._hit_sequence[-n_break:]) == self.BREAK_COMBO:
            self._hit_sequence = []
            # Deal chip damage so the hurt animation plays correctly.
            self.entity.health -= 5
            self.entity.change_state('hurt')
            return

        # --- Check counter-attack combos (J J / J K / K J) ---
        # Guard: don't fire a counter if the current sequence is a prefix of
        # the break combo (K K K J), so K J doesn't trigger a counter on the
        # 2nd and 3rd heavy of K K K J.
        # FIX: removed duplicate n_break declaration and simplified the
        # is_break_prefix check (the old any(...for _ in [None]) was needlessly
        # convoluted and could evaluate incorrectly).
        is_break_prefix = (
            tuple(self._hit_sequence) == self.BREAK_COMBO[:len(self._hit_sequence)]
        )
        if not is_break_prefix:
            for combo in self.COUNTER_COMBOS:
                n = len(combo)
                if tuple(self._hit_sequence[-n:]) == combo:
                    self._hit_sequence = []
                    self.entity.change_state('quick_attack')
                    return


class QuickAttack(State):

    def enter(self):
        self.entity.current_anim = self.entity.anim['quick_attack']
        self.entity.current_anim.reset()
        self.entity.invincible_during_counter = True
        self.entity.velocity.x = 0

    def update(self, dt):
        self.entity.velocity.x = 0

        # Deal damage on specific frames
        if 3 <= self.entity.current_anim.frame <= 6:
            self.entity._try_hit_player(damage=6, knockback_mag=2)

        if self.entity.current_anim.finished:
            self.entity.invincible_during_counter = False
            self.entity.change_state(getattr(self.entity, '_pre_block_state', 'chase'))

        if self.entity.health <= 0:
            self.entity.invincible_during_counter = False
            self.entity.change_state('death')


class RageBlock(State):

    RAGE_DURATION = 300

    def enter(self):
        self.entity.current_anim = self.entity.anim['block']
        self.entity.current_anim.reset()
        self.rage_timer = self.RAGE_DURATION
        self.entity.velocity.x = 0
        self.entity.rage_block_broken = False
        self._flip_delay = 0
        self._FLIP_DELAY_MAX = 90  # ~1.5 seconds at 60 fps

    def update(self, dt):
        # Pin velocity every frame so knockback can't slide the enemy.
        self.entity.velocity.x = 0

        if self.entity.rage_block_broken:
            self.entity.rage_block_broken = False
            self.entity._rage_exiting = True
            self.entity.change_state('hurt')
            return

        self.rage_timer -= 1

        if self.rage_timer <= 0:
            self.entity._rage_exiting = True
            self.entity.change_state('quick_attack')
            return

        if self.entity.health <= 0:
            self.entity.change_state('death')

        # Delayed flip toward player if they get behind.
        if self.entity._player_is_behind():
            self._flip_delay += 1
            if self._flip_delay >= self._FLIP_DELAY_MAX:
                self._flip_delay = 0
                self.entity.flip = not self.entity.flip
        else:
            self._flip_delay = 0