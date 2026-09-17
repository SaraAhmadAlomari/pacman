"""Pause menu shown on top of a running game."""

from typing import Dict

import pygame

from ui import (
    BACKGROUND_COLOR,
    DIM_COLOR,
    TITLE_COLOR,
    draw_centered,
    wait_for_key,
)

PAUSE_KEYS: Dict[int, str] = {
    pygame.K_1: "resume",
    pygame.K_KP1: "resume",
    pygame.K_ESCAPE: "resume",
    pygame.K_p: "resume",
    pygame.K_RETURN: "resume",
    pygame.K_2: "main_menu",
    pygame.K_KP2: "main_menu",
}


def show_pause_menu(screen: pygame.Surface) -> str:
    """Display the pause menu until the player makes a choice.

    Args:
        screen: Surface to draw on.

    Returns:
        ``"resume"``, ``"main_menu"`` or ``"quit"``.
    """
    clock = pygame.time.Clock()

    while True:
        screen.fill(BACKGROUND_COLOR)

        draw_centered(screen, "PAUSED", 110, 70, TITLE_COLOR)
        draw_centered(screen, "1. Resume the game", 220, 34)
        draw_centered(screen, "2. Return to the main menu", 265, 34)
        draw_centered(
            screen,
            "the game is frozen while this menu is open",
            330,
            24,
            DIM_COLOR,
        )

        pygame.display.flip()

        action = wait_for_key(PAUSE_KEYS)

        if action is not None:
            return action

        clock.tick(30)
