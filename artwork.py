from pathlib import Path

import pygame

from config import TILE

ASSET_ROOT = Path(__file__).resolve().parent / "assets"

"""Load Saved Images"""
original_images = {}
resized_images = {}

# Load the pictures once and make the sizes needed on screen.
def load_images():
    image_sizes = {
        'seal.png': [(TILE, TILE), (130, 130)],
        'penguin.png': [(TILE, TILE)],
        'pengushark.png': [(TILE, TILE), (130, 130)],
        'whale.png': [(TILE, TILE)],
        'ice_tile.png': [(TILE, TILE)],
        'iceberg.png': [(TILE, TILE)],
        'fire.png': [(36, 36)],
        'bowtie.png': [(34, 34), (18, 18)],
        'towel.png': [(38, 38), (30, 30)],
        'drop_done.png': [(36, 36)],
        'drop_pending.png': [(36, 36)],
        'stamp_lunch_pending.png': [(90, 90), (106, 106)],
        'stamp_seal_approved.png': [(90, 90), (88, 88), (106, 106), (160, 160)],
        'stamp_lunch_denied.png': [(90, 90), (88, 88), (82, 82)],
        'stamp_nap_time.png': [(90, 90), (88, 88), (160, 160)],
        'stamp_meal_alert.png': [(90, 90)],
        'stamp_prey_notice.png': [(90, 90)],
        'lunch_scene.png': [(780, 430)],
        'pengushark_lunch.png': [],
    }
    original_images.clear()
    resized_images.clear()
    for name in image_sizes:
        image = pygame.image.load(str(ASSET_ROOT / name)).convert_alpha()
        original_images[name] = image
        for width, height in image_sizes[name]:
            resized_images[(name, width, height)] = pygame.transform.scale(image, (width, height))

    # Fit the lunch picture into the window without stretching it.
    image = original_images['pengushark_lunch.png']
    ratio = min(420 / image.get_width(), 230 / image.get_height())
    width = max(1, round(image.get_width() * ratio))
    height = max(1, round(image.get_height() * ratio))
    resized_images[('pengushark_lunch.png', width, height)] = pygame.transform.scale(image, (width, height))

def get_image(name):
    return original_images[name]

def scaled_asset(name, width, height):
    key = (name, width, height)
    if key in resized_images:
        return resized_images[key]
    return pygame.transform.scale(original_images[name], (width, height))

def draw_saved_picture(surface, name, box):
    image = get_image(name)
    ratio = min(box.w / image.get_width(), box.h / image.get_height())
    size = (max(1, round(image.get_width() * ratio)), max(1, round(image.get_height() * ratio)))
    picture = scaled_asset(name, size[0], size[1])
    surface.blit(picture, picture.get_rect(center=box.center))

"""Display Characters and Items"""
# Turn the tile position into a position on the screen.
def draw_character(surface, position, name, size=TILE, pixel_position=None):
    surface.blit(
        scaled_asset(name, size, size),
        pixel_position if pixel_position is not None else (position[0] * TILE, position[1] * TILE),
    )

def draw_seal(surface, position, size=TILE, pixel_position=None):
    draw_character(surface, position, 'seal.png', size, pixel_position)

def draw_penguin(surface, position, size=TILE, pixel_position=None):
    draw_character(surface, position, 'penguin.png', size, pixel_position)

def draw_pengushark(surface, position, size=TILE, pixel_position=None):
    draw_character(surface, position, 'pengushark.png', size, pixel_position)

def draw_whale(surface, position):
    draw_character(surface, position, 'whale.png')

def draw_ice(surface, x, y, tile_size):
    surface.blit(scaled_asset('ice_tile.png', tile_size, tile_size), (x * tile_size, y * tile_size))

def draw_bowtie(surface, centre, size=34):
    surface.blit(
        scaled_asset('bowtie.png', size, size),
        (round(centre[0] - size / 2), round(centre[1] - size / 2)),
    )

def draw_towel(surface, centre, size=38):
    surface.blit(
        scaled_asset('towel.png', size, size),
        (round(centre[0] - size / 2), round(centre[1] - size / 2)),
    )

def draw_drop(surface, centre, done):
    name = 'drop_done.png' if done else 'drop_pending.png'
    surface.blit(scaled_asset(name, 36, 36), (centre[0] - 18, centre[1] - 18))

# The stamp picture already includes the seal and words.
def draw_funny_stamp(screen, position, top='SEAL', bottom='APPROVED', size=96):
    name = 'stamp_' + top.lower() + '_' + bottom.lower() + '.png'
    screen.blit(scaled_asset(name, size, size), position)

def draw_lunch_illustration(surface, pixel_position, width=420):
    box = pygame.Rect(pixel_position[0], pixel_position[1], width, round(width * 230 / 420))
    draw_saved_picture(surface, 'pengushark_lunch.png', box)

def draw_fire(surface, position):
    centre_x = position[0] * TILE + 44
    centre_y = position[1] * TILE + 40
    surface.blit(scaled_asset('fire.png', 36, 36), (centre_x - 18, centre_y - 18))
