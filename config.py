"""Board Settings"""
COLS = 13
ROWS = 10
TILE = 60
WIDTH = COLS * TILE
BOARD_HEIGHT = ROWS * TILE
HEIGHT = 860
MAX_STEPS = 50
ICE_TARGET = 12
SURVIVE_STEPS = 50
DIRECTIONS = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}

"""Interface Colours"""
WHITE = (240, 251, 255)
MUTED = (157, 193, 210)
GOLD = (145, 201, 218)
PAPER = (247, 239, 222)
DOCUMENT_INK = (70, 55, 43)
DOC_MUTED = (116, 96, 77)
DOC_ACCENT = (143, 103, 68)
DOC_BORDER = (202, 181, 149)
DOC_SUCCESS = (89, 119, 79)
STAMP_RED = (165, 70, 62)

"""Shared Messages"""
TIRED_MESSAGE = "The seal is tired. Time for a nap before lunch."
LUCKY_HINT = "What a stroke of lunch! Your meal is within flipper's reach."
SURRENDER_MESSAGE = "Surrender approved. You are today's special."

"""Night Documents"""
NIGHT_BACKGROUND = (8, 16, 35)
NIGHT_PAPER = (18, 34, 54)
NIGHT_INK = (225, 239, 247)
NIGHT_ACCENT = (129, 211, 225)
NIGHT_BORDER = (72, 113, 145)
NIGHT_WARNING = (236, 151, 174)
NIGHT_BUTTON = (39, 78, 102)
NIGHT_BUTTON_HOVER = (53, 102, 125)
