"""Ice Layouts"""
import random

from config import COLS as WIDTH, ROWS as HEIGHT

# Keep level 9 fixed. Make a new map for every other level.
def make_ice(index):
    rng = random.Random(9001 + index) if index == 8 else random.Random()
    ice = set()
    # Pick eight centres and scatter ice around each one.
    for _ in range(8):
        cx, cy = (rng.randrange(WIDTH), rng.randrange(HEIGHT))
        for y in range(max(0, cy - 1), min(HEIGHT, cy + 2)):
            for x in range(max(0, cx - 2), min(WIDTH, cx + 3)):
                if rng.random() < 0.72:
                    ice.add((x, y))
    if index == 8:
        # Keep the original level-9 ice and add two connecting tiles.
        ice.update({(3, 5), (4, 5), (5, 5), (10, 5), (6, 6)})
    return ice

