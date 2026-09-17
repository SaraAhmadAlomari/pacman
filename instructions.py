"""Instructions screen listing the controls and the rules."""

from typing import Dict, List, Tuple

import pygame

from ui import (
    ACCENT_COLOR,
    BACKGROUND_COLOR,
    DIM_COLOR,
    TEXT_COLOR,
    TITLE_COLOR,
    draw_centered,
    wait_for_key,
)

BACK_KEYS: Dict[int, str] = {
    pygame.K_ESCAPE: "menu",
    pygame.K_RETURN: "menu",
    pygame.K_SPACE: "menu",
    pygame.K_BACKSPACE: "menu",
}

LINES: List[Tuple[str, Tuple[int, int, int]]] = [
    ("CONTROLS", ACCENT_COLOR),
    ("Arrow keys or WASD - move Pac-Man", TEXT_COLOR),
    ("P or ESC - pause the game", TEXT_COLOR),
    ("", TEXT_COLOR),
    ("RULES", ACCENT_COLOR),
    ("Eat every pacgum to finish a level", TEXT_COLOR),
    ("Super-pacgums sit in the four corners", TEXT_COLOR),
    ("They make the ghosts edible for a few seconds", TEXT_COLOR),
    ("An eaten ghost returns to its corner after a delay", TEXT_COLOR),
    ("A ghost that touches you costs one life", TEXT_COLOR),
    ("Running out of time also costs one life", TEXT_COLOR),
    ("", TEXT_COLOR),
    ("CHEAT MODE (for the peer review)", ACCENT_COLOR),
    ("I - invincibility        F - freeze the ghosts", TEXT_COLOR),
    ("L - one extra life       N - skip the level", TEXT_COLOR),
    ("B - double speed", TEXT_COLOR),
]


def show_instructions(screen: pygame.Surface) -> str:
    """Display the controls and rules until the player goes back.

    Args:
        screen: Surface to draw on.

    Returns:
        ``"menu"`` to go back, or ``"quit"`` if the window was closed.
    """
    clock = pygame.time.Clock()

    while True:
        screen.fill(BACKGROUND_COLOR)

        draw_centered(screen, "INSTRUCTIONS", 55, 54, TITLE_COLOR)

        for index, (text, color) in enumerate(LINES):
            if text:
                draw_centered(screen, text, 115 + index * 27, 26, color)

        draw_centered(
            screen,
            "ESC / ENTER: back to menu",
            screen.get_height() - 35,
            26,
            DIM_COLOR,
        )

        pygame.display.flip()

        action = wait_for_key(BACK_KEYS)

        if action is not None:
            return action

        clock.tick(30)
