"""Nightmare Before Lunch Rules"""
import random

from config import SURVIVE_STEPS, DIRECTIONS, COLS as WIDTH, ROWS as HEIGHT
from rules import LEVELS
SPECIAL_INDEX = len(LEVELS)

class Nightmare:

    def __init__(self, rng=None):
        self.rng = rng or random.Random()
        self.index = SPECIAL_INDEX
        self.special = True
        self.player = self.rng.choice([(x, y) for x in range(1, WIDTH - 1) for y in range(1, HEIGHT - 1)])
        # Keep Pengushark at least 8 steps away, counting horizontal and vertical distance together.
        positions = []
        for x in range(WIDTH):
            for y in range(HEIGHT):
                distance = abs(x - self.player[0]) + abs(y - self.player[1])
                if distance >= 8:
                    positions.append((x, y))
        self.pengushark = self.rng.choice(positions)

        self.won = False
        self.failed = False
        self.steps = 0
        self.chase_pending = False
        self.chase_due_ms = None
        self.last_blocked = False
        self.icebergs = set()
        self.last_iceberg = None
        self.tutorial_events = []
        self.tutorial_seen = set()
        self.tip_text = None
        self.tip_until_ms = 0
        self.feedback = 'YOU control the seal. Pengushark chases automatically. Escape!'

    def tutorial_once(self, key, message):
        if key not in self.tutorial_seen:
            self.tutorial_seen.add(key)
            self.tutorial_events.append(message)

    def inside(self, tile):
        return 0 <= tile[0] < WIDTH and 0 <= tile[1] < HEIGHT

    def neighbours(self, tile):
        return {(tile[0] + dx, tile[1] + dy) for dx, dy in DIRECTIONS.values() if self.inside((tile[0] + dx, tile[1] + dy))}

    def grow_iceberg(self):
        # Do not drop ice on either character.
        # Leave two ways out if possible. If there are fewer, keep them open.
        # Skip this iceberg if there is nowhere safe to put it.
        neighbours = self.neighbours(self.player)
        free_exits = neighbours - self.icebergs - {self.pengushark}
        candidates = []
        for x in range(WIDTH):
            for y in range(HEIGHT):
                tile = (x, y)
                distance = abs(x - self.player[0]) + abs(y - self.player[1])
                if not 1 <= distance <= 2 or tile in self.icebergs or tile in (self.player, self.pengushark):
                    continue
                if len(free_exits - {tile}) >= min(2, len(free_exits)):
                    candidates.append(tile)
        if not candidates:
            self.last_iceberg = None
            return None
        tile = self.rng.choice(sorted(candidates))
        self.icebergs.add(tile)
        self.last_iceberg = tile
        self.tutorial_once('iceberg', 'Iceberg incoming! Go around it. Pengushark does not have to.')
        return tile

    def move_seal(self, direction, delay_chase=False):
        self.take_step(DIRECTIONS[direction], delay_chase=delay_chase)

    def take_step(self, vector, delay_chase=False):
        if self.won or self.failed or self.chase_pending or vector == (0, 0):
            return
        self.last_iceberg = None
        target = (self.player[0] + vector[0], self.player[1] + vector[1])
        self.last_blocked = not self.inside(target) or target in self.icebergs
        if not self.inside(target):
            self.tutorial_once('wall', 'Bonk! You stayed still, but Pengushark still gets a step.')
        if not self.last_blocked:
            self.player = target
        # Hitting a wall or iceberg still counts as a step.
        # This lets the seal stay still while Pengushark moves, creating a chance to escape.
        # This is intentional.
        self.steps += 1
        if self.player == self.pengushark:
            self.caught()
            return
        self.chase_pending = True
        if delay_chase:
            self.feedback = 'Seal step finished. Pengushark moves automatically next...'
        else:
            self.move_pengushark()

    def move_pengushark(self):
        if not self.chase_pending or self.won or self.failed:
            return
        self.chase_pending = False
        self.chase_due_ms = None
        # Move along the bigger gap. If both gaps are equal, alternate directions.
        dx, dy = (self.player[0] - self.pengushark[0], self.player[1] - self.pengushark[1])
        horizontal = abs(dx) > abs(dy) or (abs(dx) == abs(dy) and self.steps % 2 == 1)
        step = (1 if dx > 0 else -1, 0) if horizontal else (0, 1 if dy > 0 else -1)
        # Icebergs do not stop Pengushark.
        self.pengushark = (self.pengushark[0] + step[0], self.pengushark[1] + step[1])
        if self.player == self.pengushark:
            self.caught()
            return
        # Getting caught on step 50 still means losing.
        grown = self.grow_iceberg() if self.steps % 5 == 0 else None
        if self.steps >= SURVIVE_STEPS:
            self.won = True
            self.feedback = "You're awake! You survived without becoming lunch."
        elif grown:
            self.feedback = 'CRACK! An iceberg appeared nearby. Pengushark can walk through it.'
        elif self.last_blocked:
            self.feedback = 'Bonk! Solid walls and spiky icebergs stop you. Pengushark still moves.'
        else:
            self.feedback = "One step closer to waking up. Try not to become Pengushark's lunch."
    
    def caught(self):
        self.chase_pending = False
        self.chase_due_ms = None
        self.failed = True
        self.feedback = 'You got caught! The shark hoodie was not a costume.'
