# Seal of Approval

**Catch the Penguin. Terms and Conditions Apply.**

One hungry seal. One very picky penguin.

Seal of Approval is a grid-based puzzle game built with Python and Pygame for players who enjoy unexpected rules. Guide a hungry seal through ten levels, decode strange hints, and catch a penguin within 50 movement attempts. Along the way, you'll come across strange rules, ridiculous requests, and Pengushark, a character whose shark hoodie might be more than just a costume.

## Download and play

Download the project ZIP from GitHub and extract it, or clone the repository. Keep the Python files and the `assets` folder together. You will need Python 3 and pygame-ce.

Open a terminal in the project folder and run:

```sh
python3 -m pip install -r requirements.txt
python3 game.py
```

On Windows, use these commands if `python3` is not available:

```sh
py -m pip install -r requirements.txt
py game.py
```

The package is called **pygame-ce**; the program imports it as `pygame`.

## Controls

| Input | Action |
| --- | --- |
| Arrow keys / WASD | Move the seal. |
| H | Switch between original and simple hints, or open the rules during the special challenge. |
| Space | Use the level action when shown on screen. |
| R | Retry the current level. |
| Esc | Return to the menu in normal levels. During the special challenge, follow the on-screen withdrawal rules. |
| Mouse / Enter | Choose a level or activate a result button. |

## Before lunch

- All ten normal levels are available from the menu.
- The seal has up to 50 movement attempts, including blocked moves and rejected catches. Other actions do not count towards the limit.
- Reaching the penguin is not enough: the catch must satisfy the level's condition.
- Press H for a simpler hint if you get stuck.
- Progress resets when you restart the program.
- Complete all ten normal levels to finish the lunch application.

## A change of plans

In **Nightmare Before Lunch**, the seal becomes the prey. Escape Pengushark, watch for icebergs and survive 50 movement attempts. Read the permit before accepting the challenge.

## Behind the game

The program separates game rules from screen display. Player input updates the puzzle state, and the screen shows the result. Different level conditions share the same basic movement controls.

| File | Responsibility |
| --- | --- |
| `game.py` | Starts the game, handles input, changes screens and tracks progress. |
| `rules.py` | Stores normal level definitions and checks movement, items and catches. |
| `special.py` | Controls pursuit, icebergs and survival in the special challenge. |
| `screens.py` | Displays menus, boards, hints and result windows. |
| `maps.py` | Creates ice clusters and keeps level 9's connected map. |
| `artwork.py` | Loads and displays PNG pictures. |
| `terrain.py` | Creates and displays ocean details. |
| `config.py` | Holds shared settings, colours, directions and messages. |

## Artwork

Character, item, stamp and scene artwork was generated and edited with AI image tools and saved as PNG files. Pygame displays these pictures; text, buttons, grid lines and changing game information are drawn by the program.
