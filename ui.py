"""Small helpers shared by every menu and full-screen panel."""

from typing import Dict, Optional, Tuple

import pygame

BACKGROUND_COLOR = (0, 0, 0)
TITLE_COLOR = (255, 232, 0)
TEXT_COLOR = (235, 235, 235)
DIM_COLOR = (150, 150, 165)
ACCENT_COLOR = (60, 140, 255)

_FONT_CACHE: Dict[int, pygame.font.Font] = {}


def font(size: int) -> pygame.font.Font:
    """Return a cached default font of the requested size.

    Args:
        size: Height of the font in pixels.

    Returns:
        A ready to use font object.
    """
    if size not in _FONT_CACHE:
        _FONT_CACHE[size] = pygame.font.Font(None, size)

    return _FONT_CACHE[size]


def draw_centered(
    screen: pygame.Surface,
    text: str,
    y_position: int,
    size: int = 32,
    color: Tuple[int, int, int] = TEXT_COLOR,
) -> None:
    """Draw one horizontally centred line of text.

    Args:
        screen: Surface to draw on.
        text: Text to display.
        y_position: Vertical centre of the line.
        size: Font size.
        color: Colour of the text.
    """
    surface = font(size).render(text, True, color)
    rect = surface.get_rect(center=(screen.get_width() // 2, y_position))
    screen.blit(surface, rect)


def wait_for_key(keys: Dict[int, str]) -> Optional[str]:
    """Read the event queue and map a pressed key to an action.

    Args:
        keys: Mapping from pygame key codes to action names.

    Returns:
        The matching action, ``"quit"`` when the window is closed, or
        ``None`` when nothing relevant happened.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return "quit"

        if event.type == pygame.KEYDOWN and event.key in keys:
            return keys[event.key]

    return None
