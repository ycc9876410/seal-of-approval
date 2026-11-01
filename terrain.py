"""Ocean Colours and Details"""
import random

import pygame
OCEAN_DARK = (8, 35, 65)
OCEAN_BLUE = (12, 55, 90)
OCEAN_LIGHT = (20, 75, 110)

"""Generate Ocean Details"""
# Make the small water details once when a level starts.
def generate_ocean_details(grid_width, grid_height, tile_size):
    ocean_details = []
    for y in range(grid_height):
        for x in range(grid_width):
            details = []
            for _ in range(7):
                px = random.randint(4, tile_size - 8)
                py = random.randint(4, tile_size - 8)
                size = random.choice([2, 3, 4])
                colour = random.choice([OCEAN_BLUE, OCEAN_LIGHT])
                details.append((px, py, size, colour))
            ocean_details.append((x, y, details))
    return ocean_details

"""Draw Ocean Tile"""
def draw_ocean(screen, x, y, tile_size, details):
    tile_x = x * tile_size
    tile_y = y * tile_size
    pygame.draw.rect(screen, OCEAN_DARK, (tile_x, tile_y, tile_size, tile_size))
    for px, py, size, colour in details:
        pygame.draw.rect(screen, colour, (tile_x + px, tile_y + py, size, size))
