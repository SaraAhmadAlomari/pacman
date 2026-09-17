"""Heads-up display drawn above the maze during gameplay."""

from typing import List

import pygame

from cheat import CheatManager
from models import GameState

HUD_HEIGHT = 50
TEXT_COLOR = (255, 255, 255)
WARNING_COLOR = (255, 80, 80)
CHEAT_COLOR = (0, 230, 140)
MESSAGE_COLOR = (255, 255, 0)


def _active_cheats(cheats: CheatManager) -> str:
    """Build the short label listing the enabled cheats.

    Args:
        cheats: Cheat manager of the session.

    Returns:
        A label such as ``CHEAT: GOD FREEZE``, or an empty string.
    """
    labels: List[str] = []

    if cheats.hidden_mode:
        labels.append("HIDDEN")

    if cheats.ghosts_frozen:
        labels.append("FREEZE")

    if cheats.speed_boost:
        labels.append("SPEED")

    return "CHEAT: " + " ".join(labels) if labels else ""


def draw_hud(
    screen: pygame.Surface,
    state: GameState,
    cheats: CheatManager,
) -> None:
    """Draw score, lives, level, remaining time and cheat status.

    Args:
        screen: Surface to draw on.
        state: Current game state.
        cheats: Cheat manager of the session.
    """
    font = pygame.font.Font(None, 28)

    pygame.draw.rect(
        screen,
        (10, 10, 30),
        (0, 0, screen.get_width(), HUD_HEIGHT),
    )

    time_color = WARNING_COLOR if state.time_left <= 10 else TEXT_COLOR

    entries = [
        (f"Score: {state.score}", TEXT_COLOR),
        (f"Lives: {state.lives}", TEXT_COLOR),
        (f"Level: {state.level}", TEXT_COLOR),
        (f"Time: {int(state.time_left)}", time_color),
    ]

    x_position = 12

    for text, color in entries:
        surface = font.render(text, True, color)
        screen.blit(surface, (x_position, 8))
        x_position += surface.get_width() + 22

    if state.power_timer > 0.0:
        power = font.render(
            f"POWER {state.power_timer:.1f}s",
            True,
            MESSAGE_COLOR,
        )
        screen.blit(power, (12, 28))

    cheat_label = _active_cheats(cheats)

    if cheat_label:
        surface = font.render(cheat_label, True, CHEAT_COLOR)
        screen.blit(
            surface,
            (screen.get_width() - surface.get_width() - 12, 8),
        )

    if state.message_timer > 0.0 and state.message:
        surface = font.render(state.message, True, MESSAGE_COLOR)
        screen.blit(
            surface,
            (
                (screen.get_width() - surface.get_width()) // 2,
                HUD_HEIGHT - 22,
            ),
        )
