import pygame

from config import COLS, ROWS, TILE, WIDTH, HEIGHT, SURRENDER_MESSAGE
from maps import make_ice
from terrain import generate_ocean_details
from rules import Puzzle, LEVELS
from special import Nightmare
from artwork import load_images
from screens import (
    special_start_button, surrender_button, next_level_button, retry_button,
    level_buttons, lunch_button, draw_normal_level, draw_nightmare_level,
    draw_special_intro, draw_special_rules, draw_special_tip,
    draw_failure_popup, draw_completion_popup, draw_start_screen, draw_lunch_page,
)

"""Start and Retry Levels"""
# Make the ice and water details when a level starts.
def make_map(index):
    return (make_ice(index), generate_ocean_details(COLS, ROWS, TILE))

# Remember which normal level led to the nightmare.
def new_nightmare_puzzle(source_index=None, rng=None):
    puzzle = Nightmare(rng)
    puzzle.intro_pending = True
    puzzle.source_index = source_index
    return puzzle

# Giving up here means losing the original level.
def surrender_puzzle(puzzle):
    index = menu_return_index(puzzle)
    failed = Puzzle(index)
    failed.nightmare_pending = False
    failed.failed = True
    failed.surrendered = True
    failed.feedback = SURRENDER_MESSAGE
    return failed

# Restart the same level or nightmare with new positions.
def retry_puzzle(puzzle):
    if getattr(puzzle, 'special', False):
        return new_nightmare_puzzle(getattr(puzzle, 'source_index', None))
    return Puzzle(puzzle.index)

def menu_return_index(puzzle):
    if getattr(puzzle, 'special', False):
        return getattr(puzzle, 'source_index', None) or 0
    return puzzle.index

"""Menu and Tips"""
def menu_selection(selected, key):
    if key in (pygame.K_LEFT, pygame.K_RIGHT):
        if selected % 2 == 0:
            return selected + 1
        return selected - 1
    if key == pygame.K_UP:
        return (selected - 2) % len(LEVELS)
    if key == pygame.K_DOWN:
        return (selected + 2) % len(LEVELS)
    return selected

def update_special_tip(puzzle):
    now = pygame.time.get_ticks()
    if puzzle.tip_text is not None and now >= puzzle.tip_until_ms:
        puzzle.tip_text = None
    if puzzle.tip_text is None and puzzle.tutorial_events:
        puzzle.tip_text = puzzle.tutorial_events.pop(0)
        puzzle.tip_until_ms = now + 6000

"""Run the Game"""
# Open the window and run the game.
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    load_images()
    pygame.display.set_caption('Seal of Approval | Catch the Penguin. Terms and Conditions Apply.')
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    title_font = pygame.font.SysFont(None, 30, bold=True)
    puzzle = Puzzle(0)
    ice, details = make_map(0)
    show_rules = False
    running = True
    in_menu = True
    selected_level = 0
    completed = set()  # Start with no completed levels each time.
    in_lunch = False
    key_moves = {
        pygame.K_UP: 'up',
        pygame.K_w: 'up',
        pygame.K_DOWN: 'down',
        pygame.K_s: 'down',
        pygame.K_LEFT: 'left',
        pygame.K_a: 'left',
        pygame.K_RIGHT: 'right',
        pygame.K_d: 'right',
    }
    while running:
        # Check the keyboard and mouse for the current screen.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif in_lunch:
                activate = event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE)
                activate = activate or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and lunch_button().collidepoint(event.pos))
                if activate:
                    in_lunch = False
                    in_menu = True
            elif in_menu:
                chosen = None
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        buttons = level_buttons()
                        for index in range(len(buttons)):
                            if buttons[index].collidepoint(event.pos):
                                chosen = index
                                break
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                        selected_level = menu_selection(selected_level, event.key)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        chosen = selected_level
                if chosen is not None:
                    selected_level = chosen
                    puzzle = Puzzle(chosen)
                    ice, details = make_map(chosen)
                    show_rules = False
                    in_menu = False
            # Esc can still return to the menu before the nightmare permit opens.
            elif getattr(puzzle, 'nightmare_pending', False) and (not puzzle.failed):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        selected_level = puzzle.index
                        in_menu = True
                    else:
                        puzzle = new_nightmare_puzzle(source_index=puzzle.index)
                        ice, details = make_map(puzzle.index)
                    show_rules = False
            # After the permit opens, Esc means giving up.
            elif getattr(puzzle, 'intro_pending', False):
                give_up = event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                give_up = give_up or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and surrender_button().collidepoint(event.pos))
                if give_up:
                    puzzle = surrender_puzzle(puzzle)
                    ice, details = make_map(puzzle.index)
                    show_rules = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                    show_rules = not show_rules
                elif not show_rules:
                    begin = event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER)
                    begin = begin or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and special_start_button().collidepoint(event.pos))
                    if begin:
                        puzzle.intro_pending = False
            elif puzzle.failed:
                retry = event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_r)
                retry = retry or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and retry_button(puzzle).collidepoint(event.pos))
                if retry:
                    puzzle = retry_puzzle(puzzle)
                    ice, details = make_map(puzzle.index)
                    show_rules = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    selected_level = menu_return_index(puzzle)
                    in_menu = True
            # Clicking the button and pressing Enter do the same thing.
            elif puzzle.won:
                advance = event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER)
                advance = advance or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and next_level_button(getattr(puzzle, 'special', False)).collidepoint(event.pos))
                if advance and getattr(puzzle, 'special', False):
                    selected_level = menu_return_index(puzzle)
                    in_menu = True
                elif advance:
                    next_index = (puzzle.index + 1) % len(LEVELS)
                    for step in range(1, len(LEVELS) + 1):
                        candidate = (puzzle.index + step) % len(LEVELS)
                        if candidate not in completed:
                            next_index = candidate
                            break
                    puzzle = Puzzle(next_index)
                    ice, details = make_map(puzzle.index)
                    show_rules = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    selected_level = menu_return_index(puzzle)
                    in_menu = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if getattr(puzzle, 'special', False):
                        puzzle = surrender_puzzle(puzzle)
                        ice, details = make_map(puzzle.index)
                        show_rules = False
                    else:
                        selected_level = menu_return_index(puzzle)
                        in_menu = True
                elif event.key == pygame.K_r:
                    puzzle = retry_puzzle(puzzle)
                    ice, details = make_map(puzzle.index)
                    show_rules = False
                elif event.key == pygame.K_h:
                    if getattr(puzzle, 'special', False):
                        show_rules = not show_rules
                    else:
                        puzzle.toggle_hint()
                elif getattr(puzzle, 'special', False) and show_rules:
                    pass
                elif event.key == pygame.K_SPACE and not getattr(puzzle, 'special', False):
                    puzzle.toggle_fire()
                elif event.key in key_moves:
                    if getattr(puzzle, 'special', False):
                        puzzle.move_seal(key_moves[event.key], delay_chase=True)
                        if puzzle.chase_pending and puzzle.chase_due_ms is None:
                            puzzle.chase_due_ms = pygame.time.get_ticks() + 250
                    else:
                        puzzle.move(key_moves[event.key], ice)
                    if puzzle.won and puzzle.index < len(LEVELS) and (puzzle.index not in completed):
                        completed.add(puzzle.index)
                        if len(completed) == len(LEVELS):
                            in_lunch = True
                            in_menu = False
        # Update the screen after checking the input.
        if in_lunch:
            draw_lunch_page(screen, font, title_font)
        elif in_menu:
            draw_start_screen(screen, font, title_font, selected_level, completed)
        elif getattr(puzzle, 'special', False):
            if getattr(puzzle, 'intro_pending', False):
                draw_special_intro(screen, font, title_font)
                if show_rules:
                    draw_special_rules(screen, font, title_font)
            else:
                if not show_rules and puzzle.chase_pending and (puzzle.chase_due_ms is not None) and (pygame.time.get_ticks() >= puzzle.chase_due_ms):
                    puzzle.move_pengushark()
                draw_nightmare_level(screen, font, title_font, puzzle, ice, details)
                update_special_tip(puzzle)
                draw_special_tip(screen, font, puzzle)
                if show_rules and (not puzzle.failed) and (not puzzle.won):
                    draw_special_rules(screen, font, title_font)
                if puzzle.failed:
                    draw_failure_popup(screen, font, title_font, puzzle)
                elif puzzle.won:
                    draw_completion_popup(screen, font, title_font, puzzle)
        else:
            draw_normal_level(screen, font, title_font, puzzle, ice, details, completed)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()
