"""Game over and victory screen, including the name entry field."""

from typing import Tuple

import pygame

from highscore import MAX_NAME_LENGTH
from models import GameState
from ui import (
    ACCENT_COLOR,
    BACKGROUND_COLOR,
    DIM_COLOR,
    TEXT_COLOR,
    TITLE_COLOR,
    draw_centered,
)


def _handle_events(name: str) -> Tuple[str, str]:
    """Read the event queue while the player types a name.

    Only letters, digits and spaces are accepted, and the name is capped
    at ten characters, which matches the highscore rules.

    Args:
        name: Name typed so far.

    Returns:
        A tuple with the updated name and the chosen action. The action
        is empty while the player is still typing.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return name, "quit"

        if event.type == pygame.TEXTINPUT:
            for char in event.text:
                if len(name) >= MAX_NAME_LENGTH:
                    break
                if char.isalnum() or char == " ":
                    name += char
            continue

        if event.type != pygame.KEYDOWN:
            continue

        if event.key == pygame.K_ESCAPE:
            return name, "skip"

        if event.key == pygame.K_BACKSPACE:
            name = name[:-1]
            continue

        if event.key == pygame.K_RETURN and name.strip():
            return name.strip(), "save"

    return name, ""


def _draw(screen: pygame.Surface, state: GameState, name: str) -> None:
    """Draw the final screen.

    Args:
        screen: Surface to draw on.
        state: Final game state.
        name: Name typed so far.
    """
    screen.fill(BACKGROUND_COLOR)

    won = state.status == "won"

    draw_centered(
        screen,
        "YOU WIN!" if won else "GAME OVER",
        90,
        70,
        TITLE_COLOR,
    )

    if won:
        draw_centered(
            screen,
            "Every level cleared. Waka-waka!",
            140,
            28,
            ACCENT_COLOR,
        )

    draw_centered(screen, f"Final score: {state.score}", 195, 36)
    draw_centered(screen, f"Level reached: {state.level}", 232, 28, DIM_COLOR)

    draw_centered(screen, "Enter your name:", 300, 30)
    draw_centered(screen, name + "_", 340, 34, TEXT_COLOR)
    draw_centered(
        screen,
        "letters, digits and spaces, 10 characters max",
        370,
        22,
        DIM_COLOR,
    )

    draw_centered(
        screen,
        "ENTER: save score        ESC: skip",
        420,
        26,
        DIM_COLOR,
    )

    pygame.display.flip()


def show_game_over(
    screen: pygame.Surface,
    state: GameState,
) -> Tuple[str, str]:
    """Show the final screen and collect the player's name.

    Args:
        screen: Surface to draw on.
        state: Final game state.

    Returns:
        A tuple with the name and one of ``save``, ``skip`` or ``quit``.
    """
    name = ""
    clock = pygame.time.Clock()

    pygame.key.start_text_input()

    try:
        while True:
            _draw(screen, state, name)

            name, action = _handle_events(name)

            if action:
                return name, action

            clock.tick(30)
    finally:
        pygame.key.stop_text_input()
