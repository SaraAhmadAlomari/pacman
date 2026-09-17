"""Keyboard handling for the gameplay screen.

Movement uses the keys currently held down, which gives the continuous
motion of the original game, while one-shot actions such as pause or the
cheats are read from the event queue.
"""

from typing import Dict, List, Literal, Optional

import pygame

from models import Direction

Action = Literal[
    "quit",
    "pause",
    "main_menu",
    "hidden_mode",
    "freeze_ghosts",
    "extra_life",
    "skip_level",
    "speed_boost",
]

MOVE_KEYS: Dict[int, Direction] = {
    pygame.K_UP: (-1, 0),
    pygame.K_w: (-1, 0),
    pygame.K_DOWN: (1, 0),
    pygame.K_s: (1, 0),
    pygame.K_LEFT: (0, -1),
    pygame.K_a: (0, -1),
    pygame.K_RIGHT: (0, 1),
    pygame.K_d: (0, 1),
}

ACTION_KEYS: Dict[int, Action] = {
    pygame.K_p: "pause",
    pygame.K_ESCAPE: "pause",
    pygame.K_i: "hidden_mode",
    pygame.K_f: "freeze_ghosts",
    pygame.K_l: "extra_life",
    pygame.K_n: "skip_level",
    pygame.K_b: "speed_boost",
}


def read_actions() -> List[Action]:
    """Drain the event queue and return the one-shot actions.

    Returns:
        Every action requested since the previous frame, in order.
    """
    actions: List[Action] = []

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            actions.append("quit")
        elif event.type == pygame.KEYDOWN and event.key in ACTION_KEYS:
            actions.append(ACTION_KEYS[event.key])

    return actions


def read_direction() -> Optional[Direction]:
    """Return the direction matching the keys held down.

    Returns:
        The requested direction, or ``None`` when no movement key is
        pressed.
    """
    pressed = pygame.key.get_pressed()

    for key, direction in MOVE_KEYS.items():
        if pressed[key]:
            return direction

    return None
