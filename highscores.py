"""Full screen highscore table reachable from the main menu."""

from typing import Dict

import pygame

from highscore import load_highscores
from ui import (
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


def show_highscores(screen: pygame.Surface, filename: str) -> str:
    """Display the ten best scores.

    Args:
        screen: Surface to draw on.
        filename: Path to the highscore file.

    Returns:
        ``"menu"`` to go back, or ``"quit"`` if the window was closed.
    """
    entries = load_highscores(filename)
    clock = pygame.time.Clock()

    while True:
        screen.fill(BACKGROUND_COLOR)

        draw_centered(screen, "HIGHSCORES", 70, 60, TITLE_COLOR)

        if not entries:
            draw_centered(screen, "No score yet.", 170, 30, DIM_COLOR)
        else:
            for index, entry in enumerate(entries):
                draw_centered(
                    screen,
                    f"{index + 1:2d}. {entry.name:<10} {entry.score:>7} pts",
                    140 + index * 32,
                    30,
                    TEXT_COLOR,
                )

        draw_centered(
            screen,
            "ESC / ENTER: back to menu",
            screen.get_height() - 40,
            26,
            DIM_COLOR,
        )

        pygame.display.flip()

        action = wait_for_key(BACK_KEYS)

        if action is not None:
            return action

        clock.tick(30)
