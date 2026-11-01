import pygame

from config import (
    COLS, ROWS, TILE, WIDTH, BOARD_HEIGHT, HEIGHT, MAX_STEPS, SURVIVE_STEPS,
    WHITE, MUTED, GOLD, PAPER, DOCUMENT_INK, DOC_MUTED, DOC_ACCENT, DOC_BORDER,
    DOC_SUCCESS, STAMP_RED,
)
from config import (
    NIGHT_BACKGROUND, NIGHT_PAPER, NIGHT_INK, NIGHT_ACCENT, NIGHT_BORDER,
    NIGHT_WARNING, NIGHT_BUTTON, NIGHT_BUTTON_HOVER,
)
from rules import LEVELS
from terrain import draw_ocean
from artwork import (
    scaled_asset, draw_seal, draw_penguin, draw_pengushark, draw_whale,
    draw_ice, draw_bowtie, draw_towel, draw_drop, draw_funny_stamp,
    draw_lunch_illustration, draw_fire,
)

"""Button Positions"""
def special_start_button():
    return pygame.Rect(78, 674, 310, 58)

def surrender_button():
    return pygame.Rect(418, 674, 284, 58)

def next_level_button(special=False):
    y = 570
    return pygame.Rect(WIDTH // 2 - 115, y, 230, 52)

def retry_button(puzzle):
    return (
        pygame.Rect(WIDTH // 2 - 140, 573, 280, 54)
        if getattr(puzzle, 'surrendered', False)
        else next_level_button()
    )

def level_buttons():
    return [pygame.Rect(40 + i % 2 * 355, 402 + i // 2 * 70, 335, 58) for i in range(len(LEVELS))]

def lunch_button():
    return pygame.Rect(WIDTH // 2 - 130, 690, 260, 54)

"""Text and Panels"""
def wrapped_text(surface, font, text, x, y, colour=WHITE, width=740, centered=False):
    line = ''
    for word in text.split():
        candidate = (line + ' ' + word).strip()
        if font.size(candidate)[0] > width and line:
            label = font.render(line, True, colour)
            position = label.get_rect(midtop=(x + width // 2, y)) if centered else (x, y)
            surface.blit(label, position)
            y += 24
            line = word
        else:
            line = candidate
    label = font.render(line, True, colour)
    position = label.get_rect(midtop=(x + width // 2, y)) if centered else (x, y)
    surface.blit(label, position)
    return y + 24

def draw_document_frame(screen, title, reference, title_font):
    screen.fill(NIGHT_BACKGROUND)
    pygame.draw.rect(screen, (3, 8, 19), (49, 49, WIDTH - 80, HEIGHT - 80), border_radius=4)
    pygame.draw.rect(screen, NIGHT_PAPER, (40, 40, WIDTH - 80, HEIGHT - 80), border_radius=4)
    pygame.draw.rect(screen, NIGHT_BORDER, (40, 40, WIDTH - 80, HEIGHT - 80), 1, border_radius=4)
    small = pygame.font.SysFont(None, 20)
    screen.blit(small.render('ANTARCTIC DEPARTMENT OF LUNCH', True, NIGHT_INK), (65, 59))
    label = small.render(reference, True, NIGHT_WARNING)
    screen.blit(label, label.get_rect(center=(WIDTH - 139, 67)))
    pygame.draw.line(screen, NIGHT_ACCENT, (65, 84), (WIDTH - 65, 84), 1)
    label = title_font.render(title, True, NIGHT_INK)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, 112)))
    pygame.draw.line(screen, NIGHT_BORDER, (65, 145), (WIDTH - 65, 145), 1)

def draw_permit_panel(screen, night=False, level_number=1):
    background = (23, 48, 65) if night else PAPER
    border = (88, 137, 158) if night else DOC_BORDER
    ink = (192, 220, 231) if night else DOC_MUTED
    pygame.draw.rect(screen, background, (0, BOARD_HEIGHT, WIDTH, HEIGHT - BOARD_HEIGHT))
    pygame.draw.line(screen, border, (0, BOARD_HEIGHT), (WIDTH, BOARD_HEIGHT), 2)
    for y in (739, 813):
        pygame.draw.line(screen, border, (20, y), (WIDTH - 20, y), 1)
    small = pygame.font.SysFont(None, 16)
    text = 'FORM HN-50 / DREAM FILE' if night else f'FORM SA-{level_number:02d} / ACTIVE FILE'
    label = small.render(text, True, ink)
    screen.blit(label, label.get_rect(center=(WIDTH - 130, 619)))

# level 9
def draw_hygiene_status(screen, puzzle):
    for x, title, done, icon in ((444, 'WASHED', puzzle.washed, 'water'), (609, 'DRIED', puzzle.dried, 'towel')):
        colour = DOC_SUCCESS if done else DOC_MUTED
        card = pygame.Rect(x, 743, 151, 65)
        pygame.draw.rect(screen, (253, 248, 237), card, border_radius=8)
        pygame.draw.rect(screen, colour, card, 1, border_radius=8)
        if icon == 'water':
            draw_drop(screen, (x + 24, 775), done)
        else:
            draw_towel(screen, (x + 24, 775), size=30)
        small = pygame.font.SysFont(None, 20)
        screen.blit(small.render(title, True, colour), (x + 47, 752))
        screen.blit(small.render('DONE' if done else 'PENDING', True, colour), (x + 47, 778))
        if done:
            pygame.draw.lines(screen, colour, False, [(x + 124, 785), (x + 130, 791), (x + 141, 777)], 2)

"""Level Screens"""
# Draw the ice, water and grid for either game mode.
def draw_board(screen, ice, details, night=False):
    screen.fill((8, 16, 35) if night else (8, 35, 65))
    for y in range(ROWS):
        for x in range(COLS):
            if (x, y) in ice:
                draw_ice(screen, x, y, TILE)
            else:
                draw_ocean(screen, x, y, TILE, details[y * COLS + x][2])
    if night:
        night = pygame.Surface((WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
        night.fill((9, 8, 35, 160))
        screen.blit(night, (0, 0))
    grid_colour = (34, 43, 68) if night else (25, 68, 92)
    for x in range(COLS + 1):
        pygame.draw.line(screen, grid_colour, (x * TILE, 0), (x * TILE, BOARD_HEIGHT))
    for y in range(ROWS + 1):
        pygame.draw.line(screen, grid_colour, (0, y * TILE), (WIDTH, y * TILE))

# Show the normal level and its information below.
def draw_normal_level(screen, font, title_font, puzzle, ice, details, completed):
    draw_board(screen, ice, details)
    if puzzle.level.rule == 'corners':
        for pos in ((0, 0), (COLS - 1, 0), (0, ROWS - 1), (COLS - 1, ROWS - 1)):
            visited = puzzle.corners_seen
            colour = (120, 240, 180) if pos in visited else GOLD
            pygame.draw.rect(screen, colour, (pos[0] * TILE + 5, pos[1] * TILE + 5, 50, 50), 3)
    if puzzle.level.rule == 'fire':
        for x, y in puzzle.fire_spots():
            colour = (255, 172, 82) if (x, y) in puzzle.fires else (149, 114, 79)
            pygame.draw.rect(screen, colour, (x * TILE + 3, y * TILE + 3, TILE - 6, TILE - 6), 2)
    if puzzle.bowtie_position is not None:
        x, y = puzzle.bowtie_position
        draw_bowtie(screen, (x * TILE + 30, y * TILE + 30))
    if puzzle.towel_position is not None:
        x, y = puzzle.towel_position
        draw_towel(screen, (x * TILE + 30, y * TILE + 30))
    if puzzle.whale is not None:
        draw_whale(screen, puzzle.whale)
    if puzzle.penguin_visible:
        draw_penguin(screen, puzzle.penguin)
    draw_seal(screen, puzzle.player)
    if puzzle.has_bowtie:
        draw_bowtie(screen, (puzzle.player[0] * TILE + 30, puzzle.player[1] * TILE + 43), size=18)
    if puzzle.level.rule == 'fire':
        for position in sorted(puzzle.fires):
            draw_fire(screen, position)
    draw_permit_panel(screen, level_number=puzzle.index + 1)
    if puzzle.won:
        stamp_top, stamp_bottom = ('SEAL', 'APPROVED')
    elif puzzle.failed:
        if getattr(puzzle, 'surrendered', False):
            stamp_top, stamp_bottom = ('LUNCH', 'DENIED')
        else:
            stamp_top, stamp_bottom = ('NAP', 'TIME')
    elif puzzle.nightmare_pending:
        stamp_top, stamp_bottom = ('MEAL', 'ALERT')
    else:
        stamp_top, stamp_bottom = ('LUNCH', 'PENDING')
    draw_funny_stamp(screen, (666, 644), stamp_top, stamp_bottom, size=90)
    title = f'{puzzle.index + 1}/{len(LEVELS)}  {puzzle.level.title}'
    y = wrapped_text(screen, title_font, title, 20, 614, DOCUMENT_INK)
    hint = puzzle.get_hint()
    y = wrapped_text(screen, font, hint, 20, y + 6, DOCUMENT_INK, width=625)
    feedback = (
        'Press any key to review your lunch permit. Esc: menu.'
        if puzzle.nightmare_pending
        else puzzle.feedback
    )
    feedback_colour = (
        DOC_SUCCESS
        if puzzle.won
        else (
            STAMP_RED
            if puzzle.failed or 'rejected' in feedback.lower() or feedback.startswith('Bonk')
            else DOC_MUTED
        )
    )
    y = wrapped_text(screen, font, feedback, 20, y + 5, feedback_colour, width=625)
    if puzzle.won:
        text = f'{len(completed)}/10 levels completed. Enter: next unfinished level'
    else:
        text = f"Steps: {len(puzzle.moves)}/{MAX_STEPS}   Borders: {('WRAP' if puzzle.wrap_around else 'SOLID')}"
        if puzzle.level.rule == 'fire':
            text += f'   Flames: {len(puzzle.fires)}/{len(puzzle.fire_spots())}'
        if puzzle.level.rule == 'formal':
            text += '   Dress: ' + ('FORMAL' if puzzle.has_bowtie else 'CASUAL')
        if puzzle.index == 4:
            text += f'   Ice score: {puzzle.ice_score}'
    wrapped_text(
        screen,
        font,
        text,
        20,
        764,
        DOC_ACCENT,
        width=405 if puzzle.level.rule == 'wash' else 740,
    )
    if puzzle.level.rule == 'wash':
        draw_hygiene_status(screen, puzzle)
    controls = (
        'Any key: review the permit     Esc: menu'
        if puzzle.nightmare_pending
        else 'Arrows/WASD: move   H: simple hint   R: retry   ESC: menu'
    )
    if not puzzle.nightmare_pending and puzzle.level.rule == 'fire':
        controls = 'Arrows/WASD: move   SPACE: fire on/off   H: simple hint   R: retry   ESC: menu'
    if not puzzle.nightmare_pending and puzzle.simple_hint_visible:
        controls = controls.replace('H: simple hint', 'H: original hint')
    wrapped_text(screen, font, controls, 20, 822, DOC_MUTED)
    if puzzle.failed:
        draw_failure_popup(screen, font, title_font, puzzle)
    elif puzzle.won:
        draw_completion_popup(screen, font, title_font, puzzle)

# Show the nightmare and the number of steps survived.
def draw_nightmare_level(screen, font, title_font, puzzle, ice, details):
    draw_board(screen, ice, details, night=True)
    for x, y in sorted(puzzle.icebergs):
        px, py = (x * TILE, y * TILE)
        screen.blit(scaled_asset('iceberg.png', TILE, TILE), (px, py))
        if (x, y) == puzzle.last_iceberg:
            pygame.draw.rect(screen, (255, 166, 223), (px + 3, py + 3, 54, 54), 2, border_radius=8)
    pygame.draw.rect(screen, (156, 123, 203), (1, 1, WIDTH - 2, BOARD_HEIGHT - 2), 3)
    draw_seal(screen, puzzle.player)
    draw_pengushark(screen, puzzle.pengushark)
    draw_permit_panel(screen, night=True)
    draw_funny_stamp(screen, (666, 644), 'PREY', 'NOTICE', size=90)
    y = wrapped_text(screen, title_font, 'NIGHTMARE BEFORE LUNCH', 20, 614, (219, 239, 246))
    hint = 'Escape Pengushark. Survive 50 steps.'
    y = wrapped_text(screen, font, hint, 20, y + 7, WHITE, width=625)
    wrapped_text(screen, font, puzzle.feedback, 20, y + 6, (227, 184, 195), width=625)
    text = f'Survival steps: {puzzle.steps}/{SURVIVE_STEPS}   Icebergs: {len(puzzle.icebergs)}'
    wrapped_text(screen, font, text, 20, 754, GOLD)
    next_growth = 5 - puzzle.steps % 5
    wrapped_text(
        screen,
        font,
        f'Next iceberg in {next_growth} steps. Walls solid. Spiky ice blocks ONLY you.',
        20,
        782,
        MUTED,
    )
    wrapped_text(
        screen,
        font,
        'Arrows/WASD: move SEAL   H: rules   R: retry   ESC: surrender',
        20,
        822,
        WHITE,
    )

def draw_special_intro(screen, font, title_font):
    heading = pygame.font.SysFont(None, 46, bold=True)
    draw_document_frame(screen, 'Nightmare Before Lunch', 'FORM HN-50', heading)
    screen.blit(font.render('Applicant: SEAL     Revised role: PREY', True, NIGHT_INK), (71, 162))
    pygame.draw.rect(screen, NIGHT_WARNING, (514, 154, 190, 33), 2)
    stamp = font.render('ROLE REVERSED', True, NIGHT_WARNING)
    screen.blit(stamp, stamp.get_rect(center=(609, 171)))
    draw_seal(screen, (0, 0), size=130, pixel_position=(151, 200))
    draw_pengushark(screen, (0, 0), size=130, pixel_position=(498, 200))
    label = title_font.render('VS', True, NIGHT_WARNING)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, 270)))
    label = title_font.render('Escape Pengushark. Survive 50 steps.', True, NIGHT_INK)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, 359)))
    rules = [
        ('01  MOVEMENT AUTHORISATION', 'Arrows / WASD: move the seal. No waiting.'),
        ('02  PURSUIT CLAUSE', 'Blocked moves count. Pengushark chases after every attempt.'),
        ('03  ICEBERG LIABILITY', 'Every 5 steps: icebergs block you, not Pengushark.'),
    ]
    for i, (heading_text, detail) in enumerate(rules):
        y = 407 + i * 78
        screen.blit(title_font.render(heading_text, True, NIGHT_ACCENT), (75, y))
        wrapped_text(screen, font, detail, 75, y + 32, NIGHT_INK, width=WIDTH - 150)
        pygame.draw.line(screen, NIGHT_BORDER, (75, y + 64), (WIDTH - 75, y + 64), 1)
    start = special_start_button()
    colour = NIGHT_BUTTON_HOVER if start.collidepoint(pygame.mouse.get_pos()) else NIGHT_BUTTON
    pygame.draw.rect(screen, colour, start, border_radius=5)
    pygame.draw.rect(screen, NIGHT_INK, start, 1, border_radius=5)
    label = title_font.render('Accept Challenge', True, NIGHT_INK)
    screen.blit(label, label.get_rect(center=(start.center[0], start.center[1] - 7)))
    label = pygame.font.SysFont(None, 18).render('Click or press Enter', True, NIGHT_INK)
    screen.blit(label, label.get_rect(center=(start.center[0], start.center[1] + 15)))
    button = surrender_button()
    pygame.draw.rect(screen, NIGHT_WARNING, button, 2, border_radius=5)
    label = title_font.render('Be the Daily Special', True, NIGHT_WARNING)
    screen.blit(label, label.get_rect(center=(button.center[0], button.center[1] - 8)))
    label = pygame.font.SysFont(None, 18).render('Surrender (Esc)', True, NIGHT_WARNING)
    screen.blit(label, label.get_rect(center=(button.center[0], button.center[1] + 16)))
    label = font.render('H: full terms     Esc: surrender this level', True, NIGHT_INK)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, 767)))

# Pause the chase while these rules are open.
def draw_special_rules(screen, font, title_font):
    draw_document_frame(screen, 'SURVIVAL TERMS & CONDITIONS', 'ANNEX HN-50', title_font)
    sections = [
        (   '1. Objective', 
            'Escape Pengushark. Survive 50 movement attempts.'
        ),
        (
            '2. Step counting',
            'Arrows / WASD move the seal. Every attempt counts as one step, even if blocked. Pengushark then moves one step.',
        ),
        (
            '3. Border restrictions',
            'You cannot cross the board edges. Flat ice and ocean are walkable. Jagged icebergs block only the seal.',
        ),
        (
            '4. Falling icebergs',
            'Every 5 steps, after Pengushark moves, an iceberg may appear on any of the 8 surrounding tiles or 2 tiles away in a straight line.',
        ),
        (
            '5. Withdrawal clause',
            'Esc or Be the Daily Special makes you lose the original level. Press R to retry during play.',
        ),
    ]
    y = 163
    small = pygame.font.SysFont(None, 22)
    for heading, detail in sections:
        screen.blit(title_font.render(heading, True, NIGHT_ACCENT), (66, y))
        y = wrapped_text(screen, small, detail, 66, y + 29, NIGHT_INK, width=WIDTH - 132) + 13
    pygame.draw.line(screen, NIGHT_BORDER, (66, 741), (WIDTH - 66, 741), 1)
    label = font.render('H: close terms     Esc: surrender', True, NIGHT_WARNING)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, 769)))

def draw_special_tip(screen, font, puzzle):
    if puzzle.tip_text:
        panel = pygame.Rect(20, 18, WIDTH - 40, 76)
        pygame.draw.rect(screen, (18, 36, 53), panel, border_radius=12)
        pygame.draw.rect(screen, GOLD, panel, 1, border_radius=12)
        screen.blit(font.render('SURVIVAL TIP', True, GOLD), (34, 27))
        wrapped_text(screen, font, puzzle.tip_text, 34, 54, WHITE, width=WIDTH - 68)

"""Results and Menu"""
def draw_surrender_failure(screen, font, title_font, puzzle):
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((3, 8, 20, 205))
    screen.blit(shade, (0, 0))
    panel = pygame.Rect(70, 160, WIDTH - 140, 540)
    pygame.draw.rect(screen, PAPER, panel, border_radius=5)
    pygame.draw.rect(screen, STAMP_RED, panel, 2, border_radius=5)
    draw_funny_stamp(screen, (84, 174), 'LUNCH', 'DENIED', size=82)
    title = title_font.render(f'LEVEL {puzzle.index + 1} FAILED', True, STAMP_RED)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 204)))
    label = title_font.render('SURRENDER APPROVED', True, STAMP_RED)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, 251)))
    label = title_font.render("You are today's special.", True, DOCUMENT_INK)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, 291)))
    draw_lunch_illustration(screen, (WIDTH // 2 - 210, 317))
    retry = pygame.Rect(WIDTH // 2 - 140, 573, 280, 54)
    pygame.draw.rect(screen, (235, 222, 197), retry, border_radius=5)
    pygame.draw.rect(screen, DOCUMENT_INK, retry, 1, border_radius=5)
    label = title_font.render('Retry Level', True, DOCUMENT_INK)
    screen.blit(label, label.get_rect(center=retry.center))
    label = font.render('Click / Enter / R: retry     Esc: menu', True, STAMP_RED)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, 662)))

def draw_completion_popup(screen, font, title_font, puzzle):
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((3, 12, 25, 185))
    screen.blit(shade, (0, 0))
    special = getattr(puzzle, 'special', False)
    panel = pygame.Rect(100, 190, WIDTH - 200, 480)
    pygame.draw.rect(screen, PAPER, panel, border_radius=22)
    pygame.draw.rect(screen, DOC_BORDER, panel, width=2, border_radius=22)
    title = 'You survived Nightmare Before Lunch!' if special else 'Level Complete!'
    label = title_font.render(title, True, DOCUMENT_INK)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, panel.top + 47)))
    message = 'You\'re awake! Lunch is back on the menu.' if special else 'The penguin approves. Reluctantly.'
    label = font.render(message, True, DOC_MUTED)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, panel.top + 93)))
    stamp_position = (WIDTH // 2 - 80, 350)
    draw_funny_stamp(screen, stamp_position, 'SEAL', 'APPROVED', size=160)
    button = next_level_button(special)
    hovered = button.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, (229, 207, 166) if hovered else (235, 222, 197), button, border_radius=12)
    label = title_font.render('Level Menu' if special else 'Next Level', True, DOCUMENT_INK)
    screen.blit(label, label.get_rect(center=button.center))
    label = font.render('Click the button or press Enter', True, DOC_MUTED)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, panel.bottom - 25)))

def draw_failure_popup(screen, font, title_font, puzzle=None):
    if getattr(puzzle, 'surrendered', False):
        draw_surrender_failure(screen, font, title_font, puzzle)
        return
    special = getattr(puzzle, 'special', False)
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((3, 12, 25, 190))
    screen.blit(shade, (0, 0))
    panel = pygame.Rect(70, 190, WIDTH - 140, 480)
    pygame.draw.rect(screen, PAPER, panel, border_radius=22)
    pygame.draw.rect(screen, STAMP_RED, panel, 2, border_radius=22)
    label = title_font.render(
        'Caught! You Became the Snack.' if special else 'Level Failed — Nap Time!',
        True,
        STAMP_RED,
    )
    screen.blit(label, label.get_rect(center=(WIDTH // 2, 237)))
    message = (
        'The shark hoodie was not a costume.' if special
        else 'More than 50 steps. The seal is tired. Time for a nap before lunch.'
    )
    wrapped_text(screen, font, message, panel.left + 35, 277,
                 DOCUMENT_INK, width=panel.width - 70, centered=True)
    if special:
        draw_lunch_illustration(screen, (WIDTH // 2 - 210, 338))
    else:
        draw_funny_stamp(screen, (WIDTH // 2 - 80, 350), 'NAP', 'TIME', size=160)
    button = next_level_button()
    hovered = button.collidepoint(pygame.mouse.get_pos())
    pygame.draw.rect(screen, (229, 207, 166) if hovered else (235, 222, 197), button, border_radius=12)
    label = title_font.render('Retry Level', True, DOCUMENT_INK)
    screen.blit(label, label.get_rect(center=button.center))
    label = font.render('Click / Enter / R: retry     Esc: level menu', True, DOC_MUTED)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, panel.bottom - 25)))

def draw_start_screen(screen, font, title_font, selected, completed):
    WHITE, MUTED, GOLD = (DOCUMENT_INK, DOC_MUTED, DOC_ACCENT)
    font = pygame.font.SysFont(None, 22)
    screen.fill(PAPER)
    for y in range(0, HEIGHT, 60):
        pygame.draw.line(screen, (237, 225, 201), (0, y), (WIDTH, y))
    heading = title_font.render('SEAL OF APPROVAL', True, GOLD)
    screen.blit(heading, heading.get_rect(center=(WIDTH // 2, 45)))
    tagline = font.render('Ten puzzles. One hungry seal. Absolutely no common sense.', True, WHITE)
    screen.blit(tagline, tagline.get_rect(center=(WIDTH // 2, 82)))
    draw_seal(screen, (1, 1))
    draw_penguin(screen, (11, 1))
    panel = pygame.Rect(40, 143, WIDTH - 80, 213)
    pygame.draw.rect(screen, (253, 248, 237), panel, border_radius=16)
    screen.blit(title_font.render('FORM SA-01 | LUNCH APPLICATION', True, GOLD), (58, 157))
    instructions = [
        'Applicant: one hungry seal. Lunch: one very picky penguin.',
        'Read the hint. Follow the terms. Catch lunch within 50 steps.',
        'Arrows / WASD: move   H: simple hint',
        'R: retry   Esc: menu   Step 51: mandatory nap.',
    ]
    for row, text in enumerate(instructions):
        screen.blit(font.render(text, True, WHITE if row < 2 else MUTED), (58, 199 + row * 31))
    # Change the menu stamp after all normal levels are complete.
    if len(completed) == len(LEVELS):
        draw_funny_stamp(screen, (597, 199), 'SEAL', 'APPROVED', size=106)
    else:
        draw_funny_stamp(screen, (597, 199), 'LUNCH', 'PENDING', size=106)
    screen.blit(
        title_font.render(f'Choose a level   |   {len(completed)}/10 completed', True, WHITE),
        (40, 369),
    )
    mouse = pygame.mouse.get_pos()
    for i, button in enumerate(level_buttons()):
        active = i == selected or button.collidepoint(mouse)
        pygame.draw.rect(screen, (235, 219, 187) if active else (253, 248, 237), button, border_radius=12)
        pygame.draw.rect(screen, GOLD if active else DOC_BORDER, button, width=2, border_radius=12)
        label = f"{i + 1:02d}{(' *' if i in completed else '  ')} {LEVELS[i].title}"
        screen.blit(font.render(label, True, GOLD if active else WHITE), (button.x + 13, button.y + 17))
    label = font.render('Click any level, or use arrow keys + Enter. All levels are open!', True, MUTED)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, 785)))
    label = font.render('* = completed this session. Esc: quit.', True, MUTED)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, 819)))

def draw_lunch_page(screen, font, title_font):
    WHITE, MUTED, GOLD = (DOCUMENT_INK, DOC_MUTED, DOC_ACCENT)
    screen.fill(PAPER)
    for i in range(45):
        x, y = ((i * 137 + 23) % WIDTH, (i * 83 + 17) % 640)
        pygame.draw.circle(screen, (255, 215, 120) if i % 2 else (133, 220, 238), (x, y), 3)
    title = title_font.render('ALL TEN LEVELS COMPLETE!', True, GOLD)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 85)))
    label = font.render('Lunch is served. It has the seal of approval.', True, WHITE)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, 129)))
    screen.blit(scaled_asset('lunch_scene.png', 780, 430), (0, 200))
    label = title_font.render('Officially approved. Personally delicious.', True, GOLD)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, 649)))
    button = lunch_button()
    colour = (229, 207, 166) if button.collidepoint(pygame.mouse.get_pos()) else (235, 222, 197)
    pygame.draw.rect(screen, colour, button, border_radius=12)
    label = title_font.render('Back to Level Menu', True, DOCUMENT_INK)
    screen.blit(label, label.get_rect(center=button.center))
    label = font.render('Click or press Enter. Esc also returns to the menu.', True, MUTED)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, 785)))
