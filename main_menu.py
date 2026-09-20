"""Main menu, including the highscore preview required by the subject."""

from typing import Dict, List

import pygame

from highscore import load_highscores
from models import HighScore
from ui import (
    ACCENT_COLOR,
    BACKGROUND_COLOR,
    DIM_COLOR,
    TEXT_COLOR,
    TITLE_COLOR,
    draw_centered,
    wait_for_key,
)

PREVIEW_SIZE = 10

MENU_KEYS: Dict[int, str] = {
    pygame.K_1: "start",
    pygame.K_KP1: "start",
    pygame.K_SPACE: "start",
    pygame.K_RETURN: "start",
    pygame.K_2: "highscores",
    pygame.K_KP2: "highscores",
    pygame.K_3: "instructions",
    pygame.K_KP3: "instructions",
    pygame.K_4: "exit",
    pygame.K_KP4: "exit",
    pygame.K_ESCAPE: "exit",
}

OPTIONS = [
    "1. Start game",
    "2. Highscores",
    "3. Instructions",
    "4. Exit",
]


def _draw_preview(
    screen: pygame.Surface,
    entries: List[HighScore],
    y_position: int,
) -> None:
    """Draw the first highscores directly on the main menu.

    Args:
        screen: Surface to draw on.
        entries: Highscore table.
        y_position: Vertical position of the section title.
    """
    draw_centered(screen, "highscores:", y_position, 28, ACCENT_COLOR)

    if not entries:
        draw_centered(
            screen,
            "no score yet",
            y_position + 30,
            26,
            DIM_COLOR,
        )
        return

    for index, entry in enumerate(entries[:PREVIEW_SIZE]):
        draw_centered(
            screen,
            f"{index + 1}. {entry.name} - {entry.score} pts",
            y_position + 30 + index * 22,
            26,
            TEXT_COLOR,
        )


def show_main_menu(screen: pygame.Surface, highscore_file: str) -> str:
    """Display the main menu until the player chooses an entry.

    Args:
        screen: Surface to draw on.
        highscore_file: Path to the highscore file.

    Returns:
        One of ``start``, ``highscores``, ``instructions``, ``exit`` or
        ``quit``.
    """
    entries = load_highscores(highscore_file)
    clock = pygame.time.Clock()

    while True:
        screen.fill(BACKGROUND_COLOR)

        draw_centered(screen, "PAC-MAN", 80, 84, TITLE_COLOR)
        draw_centered(screen, "Ghosts! More ghosts!", 130, 26, DIM_COLOR)

        for index, option in enumerate(OPTIONS):
            draw_centered(screen, option, 200 + index * 38, 32)

        _draw_preview(screen, entries, 380)

        pygame.display.flip()

        action = wait_for_key(MENU_KEYS)

        if action is not None:
            return action

        clock.tick(30)
