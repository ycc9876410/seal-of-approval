"""Normal Level Rules"""
import random

from config import (
    COLS as WIDTH, ROWS as HEIGHT, MAX_STEPS, TIRED_MESSAGE,
    ICE_TARGET, LUCKY_HINT, DIRECTIONS,
)
from maps import make_ice

# Nearby means any of the eight tiles around the seal.
def is_nightmare_spawn(seal, penguin, wrap=False):
    # Level 10: check after the penguin is showed on the screen.
    if penguin is None:
        return False
    dx, dy = (abs(seal[0] - penguin[0]), abs(seal[1] - penguin[1]))
    if wrap: # Level 2 can go through the walls.
        dx, dy = (min(dx, WIDTH - dx), min(dy, HEIGHT - dy))
    return (dx != 0 or dy != 0) and dx <= 1 and (dy <= 1)

"""Level Titles and Hints"""
class Level:
    def __init__(self, title, original_hint, simple_hint, rule):
        self.title = title
        self.original_hint = original_hint
        self.simple_hint = simple_hint
        self.rule = rule

LEVELS = [
    Level(
        'An awkward introduction',
        'Attack the penguin from its left. It has a good side.',
        'Stand on the tile immediately LEFT of the penguin, then move RIGHT.',
        'left',
    ),
    Level(
        'Break Through the Wall',
        'Break through the wall. Geography is a suggestion.',
        'Cross any board edge to appear on the opposite side, then catch the penguin.',
        'wrap',
    ),
    Level(
        'Return to sender',
        'Take one step forward. Immediately regret it.',
        'Make a move, then reverse it on your very next move. Then catch the penguin.',
        'reverse',
    ),
    Level(
        'A Warm Welcome',
        'Give your lunch a warm welcome. From every side.',
        'Light every available side of the penguin, then catch it. SPACE turns a fire on or off.',
        'fire',
    ),
    Level(
        'Cold feet',
        'Your lunch is getting warm. Chill a dozen degrees before lunch.',
        'Ice steps add 1; ocean steps subtract 1. Reach a dozen or more to catch.',
        'ice',
    ),
    Level(
        'Formal Lunch',
        'No bow tie, no bite.',
        'Pick up the bow tie before catching the penguin.',
        'formal',
    ),
    Level(
        'The scenic route',
        'Visit all four corners. Leave a one-star review.',
        'Stand on each of the four corner tiles, then catch the penguin.',
        'corners',
    ),
    Level(
        'Seal.exe has stopped working',
        'Your flippers have been installed backwards.',
        'Arrow keys are reversed for this level. Catch the penguin from any side.',
        'backwards',
    ),
    Level(
        'Wash your flippers',
        'Wash your flippers. Lunch has hygiene standards.',
        'Step into ocean water, then use the towel on ice. Stay on ice until you catch.',
        'wash',
    ),
    Level(
        'Whaleabouts Unknown',
        'Ask the biggest gossip in the ocean where your lunch went.',
        'Visit the whale in ocean water to reveal the penguin, then catch it. A whale stranded on ice cannot help.',
        'final',
    ),
]

"""Normal Levels"""
class Puzzle:

    def __init__(self, index=0, rng=None):
        self.index = index
        self.level = LEVELS[index]
        self.simple_hint_visible = False
        self.wrap_around = index == 1
        rng = rng or random
        self.rng = rng
        tiles = [(x, y) for y in range(HEIGHT) for x in range(WIDTH)]
        # Do not put the penguin on a corner.
        corners = {(0, 0), (WIDTH - 1, 0), (0, HEIGHT - 1), (WIDTH - 1, HEIGHT - 1)}
        targets = [tile for tile in tiles if tile not in corners]
        if self.level.rule == 'wash':
            wash_ice = make_ice(index)
            targets = [tile for tile in targets if tile in wash_ice]
        # Leave room on the penguin's left for level 1.
        if index == 0:
            targets = [tile for tile in targets if tile[0] > 0]
        # In level 7, put the penguin within three steps of a corner.
        if self.level.rule == 'corners':
            near_corner = []
            for tile in targets:
                for corner in corners:
                    distance = abs(tile[0] - corner[0]) + abs(tile[1] - corner[1])
                    if distance <= 3:
                        near_corner.append(tile)
                        break
            targets = near_corner
        # In level 10, there is no penguin until the seal visits the whale.
        self.penguin = None if self.level.rule == 'final' else rng.choice(targets)
        starts = [tile for tile in tiles if tile != self.penguin]
        if self.level.rule == 'wash':
            starts = [tile for tile in starts if tile in wash_ice]
        self.player = rng.choice(starts)
        self.whale = (
            rng.choice([tile for tile in tiles if tile not in (self.player, self.penguin)])
            if self.level.rule == 'final'
            else None
        )
        self.whale_stranded = False
        self.penguin_visible = self.whale is None
        self.nightmare_trigger = is_nightmare_spawn(self.player, self.penguin, self.wrap_around)
        self.nightmare_pending = self.nightmare_trigger
        self.surrendered = False
        self.moves = []
        self.previous_vector = None
        self.crossed_border = False
        self.corners_seen = set()
        self.reversed_once = False
        self.fires = set()
        self.won = False
        self.failed = False
        self.ice_score = 0
        self.has_bowtie = False
        self.bowtie_position = (
            rng.choice([tile for tile in tiles if tile not in (self.player, self.penguin)])
            if self.level.rule == 'formal'
            else None
        )
        self.washed = False
        self.dried = False
        self.towel_position = None
        if self.level.rule == 'wash':
            options = [tile for tile in sorted(wash_ice) if tile not in (self.player, self.penguin)]
            self.towel_position = rng.choice(options)
        self.feedback = (
            'A whale might know something. Go say hello.'
            if self.whale
            else 'The penguin has read the hint. It looks concerned.'
        )

    # Switch this level between the original and simple hint.
    def toggle_hint(self):
        self.simple_hint_visible = not self.simple_hint_visible

    def get_hint(self):
        if self.nightmare_pending:
            return LUCKY_HINT
        if self.whale_stranded:
            return "Whale: I'm stranded! I don't know where your lunch went. Retry the level (R)."
        return self.level.simple_hint if self.simple_hint_visible else self.level.original_hint

    # Light the penguin's four sides, leaving out tiles beyond the board.
    def fire_spots(self):
        spots = set()
        if self.penguin is None:
            return spots
        for dx, dy in DIRECTIONS.values():
            tile = (self.penguin[0] + dx, self.penguin[1] + dy)
            if 0 <= tile[0] < WIDTH and 0 <= tile[1] < HEIGHT:
                spots.add(tile)
        return spots

    # Turning a fire on or off does not use a step.
    def toggle_fire(self):
        if self.level.rule != 'fire' or self.won or self.failed or self.nightmare_pending:
            return False
        if self.player not in self.fire_spots():
            return False
        if self.player in self.fires:
            self.fires.remove(self.player)
            self.feedback = 'Flame out. Keep every side warm before catching lunch.'
        else:
            self.fires.add(self.player)
            self.feedback = 'Flame on! A very warm welcome.'
            if self.fires == self.fire_spots():
                self.feedback = 'All sides warmed. Lunch is ready to catch!'
        return True

    # Check the step limit and board edges first.
    def move(self, direction, ice):
        if self.won or self.failed:
            return
        if len(self.moves) >= MAX_STEPS:
            self.moves.append(DIRECTIONS[direction])
            self.failed = True
            self.feedback = TIRED_MESSAGE
            return
        old_position, old_score = (self.player, self.ice_score)
        # Level 8 moves in the opposite direction to the key pressed.
        dx, dy = DIRECTIONS[direction]
        if self.level.rule == 'backwards':
            dx, dy = (-dx, -dy)
        raw = (self.player[0] + dx, self.player[1] + dy)
        if not self.wrap_around and (not (0 <= raw[0] < WIDTH and 0 <= raw[1] < HEIGHT)):
            # Hitting the edge still counts as a step.
            self.moves.append((dx, dy))
            self.previous_vector = None
            self.feedback = 'Bonk! This border has not approved your travel application.'
            return
        if self.index == 4:
            destination = (raw[0] % WIDTH, raw[1] % HEIGHT) if self.wrap_around else raw
            self.ice_score += 1 if destination in ice else -1
        self._move((dx, dy), ice)
        # If the catch is refused, the seal stays on its old tile.
        if self.player == old_position:
            self.ice_score = old_score

    # Move the seal, pick up items and check whether it can catch lunch.
    def _move(self, vector, ice):
        dx, dy = vector
        old = self.player
        raw = (old[0] + dx, old[1] + dy)
        new = (raw[0] % WIDTH, raw[1] % HEIGHT) if self.wrap_around else raw
        wrapped = raw != new
        if wrapped:
            self.crossed_border = True
        if self.previous_vector is not None:
            previous_dx, previous_dy = self.previous_vector
            if vector == (-previous_dx, -previous_dy):
                self.reversed_once = True
        self.moves.append(vector)
        self.previous_vector = vector
        if new in {(0, 0), (WIDTH - 1, 0), (0, HEIGHT - 1), (WIDTH - 1, HEIGHT - 1)}:
            self.corners_seen.add(new)
        # Work out what the seal would collect on the new tile.
        bowtie = self.has_bowtie or new == self.bowtie_position
        washed, dried = (self.washed, self.dried)
        if self.level.rule == 'wash':
            if new not in ice:
                washed, dried = (True, False)
            elif new == self.towel_position and washed:
                dried = True
        # Only check for the nightmare after the penguin appears.
        visiting_whale = new == self.whale and (not self.penguin_visible)
        stranded_whale = visiting_whale and new in ice
        revealed_now = visiting_whale and not stranded_whale
        if revealed_now:
            self.penguin = self.rng.choice(
                [
                    (x, y)
                    for y in range(HEIGHT)
                    for x in range(WIDTH)
                    if (x, y) != new and (x, y) not in {(0, 0), (WIDTH - 1, 0), (0, HEIGHT - 1), (WIDTH - 1, HEIGHT - 1)}
                ],
            )
            self.penguin_visible = True
            self.nightmare_trigger = is_nightmare_spawn(new, self.penguin, self.wrap_around)
            self.nightmare_pending = self.nightmare_trigger
        # Check the catch condition for this level.
        checks = {
            'left': self.level.rule == 'left' and old == ((self.penguin[0] - 1) % WIDTH, self.penguin[1]) and (vector == (1, 0)),
            'wrap': self.crossed_border,
            'reverse': self.reversed_once,
            'fire': self.level.rule == 'fire' and self.fire_spots().issubset(self.fires),
            'ice': self.ice_score >= ICE_TARGET,
            'formal': bowtie,
            'corners': len(self.corners_seen) == 4,
            'backwards': True,
            'wash': washed and dried,
            'final': self.penguin_visible,
        }
        if self.penguin_visible and new == self.penguin:
            self.won = checks[self.level.rule]
            if self.won:
                self.player = new
                self.feedback = 'CATCH APPROVED. The penguin would like to speak to your manager.'
            elif self.level.rule == 'formal':
                self.feedback = 'Lunch rejected. This is a formal lunch. Find your bow tie!'
            elif self.level.rule == 'fire':
                self.feedback = 'Lunch rejected! Light every available side first.'
            elif self.level.rule == 'wash':
                self.feedback = 'Lunch rejected! Wash in ocean water, then dry with the towel.'
            else:
                self.feedback = (
                    'Lunch rejected! You need a dozen degrees of chill.'
                    if self.index == 4
                    else 'Catch rejected! The penguin points at the hint. Try another approach.'
                )
        else:
            self.player = new
            if stranded_whale:
                self.whale_stranded = True
                self.feedback = "This lead has run aground."
            elif revealed_now:
                self.feedback = 'Whale: SECRET DECLASSIFIED! The penguin has appeared. Go catch it!'
            else:
                self.feedback = (
                    'You left reality and arrived on the other side.'
                    if wrapped
                    else 'Waddle waddle. Extremely professional.'
                )
        if self.player == new:
            picked_up = bowtie and (not self.has_bowtie)
            was_washed, was_dried = (self.washed, self.dried)
            self.has_bowtie = bowtie
            if self.has_bowtie:
                self.bowtie_position = None
            self.washed, self.dried = (washed, dried)
            if not self.won:
                if picked_up:
                    self.feedback = 'Dress code approved. Looking dangerously well-dressed!'
                elif self.level.rule == 'wash':
                    if new == self.towel_position and (not washed):
                        self.feedback = 'A towel cannot wash your flippers. Find ocean water first.'
                    elif dried and (not was_dried):
                        self.feedback = 'Flippers dried! Stay on ice until lunch.'
                    elif washed and (not was_washed):
                        self.feedback = 'Flippers washed. Find the towel to dry off.'
                    elif was_dried and (not dried):
                        self.feedback = 'Wet again! Back to the towel before lunch.'
