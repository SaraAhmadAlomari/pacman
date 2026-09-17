"""Drawing of the maze, the player and the ghosts.

Every game element is drawn through the same ``_to_pixels`` helper, so
the vertical offset reserved for the HUD is applied once and cannot drift
between entities.
"""

from typing import Dict, Tuple

import pygame

from cheat import CheatManager
from hud import HUD_HEIGHT, draw_hud
from maze_loader import BLOCK
from models import GameState, Position

CELL_SIZE = 26
WALL_WIDTH = 2

BACKGROUND_COLOR = (0, 0, 0)
WALL_COLOR = (40, 60, 220)
BLOCK_COLOR = (0, 90, 200)
PACGUM_COLOR = (255, 230, 180)
SUPER_PACGUM_COLOR = (255, 255, 255)
PLAYER_COLOR = (255, 232, 0)
HIDDEN_MODE_COLOR = (0, 230, 140)
EDIBLE_GHOST_COLOR = (60, 90, 255)
EATEN_GHOST_COLOR = (90, 90, 110)

GHOST_COLORS: Dict[str, Tuple[int, int, int]] = {
    "red": (255, 40, 40),
    "pink": (255, 140, 200),
    "cyan": (0, 230, 230),
    "orange": (255, 165, 40),
}


def window_size(state: GameState) -> Tuple[int, int]:
    """Return the window size needed to display a level.

    Args:
        state: Game state holding the maze.

    Returns:
        Width and height in pixels, HUD included.
    """
    return (
        state.maze.width * CELL_SIZE,
        state.maze.height * CELL_SIZE + HUD_HEIGHT,
    )


def _to_pixels(cell: Position) -> Tuple[int, int]:
    """Convert a maze cell into the pixel centre of that cell.

    Args:
        cell: Row and column of the cell.

    Returns:
        Pixel coordinates of the centre of the cell.
    """
    row, col = cell

    return (
        col * CELL_SIZE + CELL_SIZE // 2,
        row * CELL_SIZE + CELL_SIZE // 2 + HUD_HEIGHT,
    )


def _draw_cell_walls(
    screen: pygame.Surface,
    value: int,
    x: int,
    y: int,
) -> None:
    """Draw the walls of one maze cell.

    Args:
        screen: Surface to draw on.
        value: Wall bitmask of the cell.
        x: Left pixel coordinate of the cell.
        y: Top pixel coordinate of the cell.
    """
    corners = {
        1: ((x, y), (x + CELL_SIZE, y)),
        2: ((x + CELL_SIZE, y), (x + CELL_SIZE, y + CELL_SIZE)),
        4: ((x, y + CELL_SIZE), (x + CELL_SIZE, y + CELL_SIZE)),
        8: ((x, y), (x, y + CELL_SIZE)),
    }

    for bit, (start, end) in corners.items():
        if value & bit:
            pygame.draw.line(screen, WALL_COLOR, start, end, WALL_WIDTH)


def _draw_maze(screen: pygame.Surface, state: GameState) -> None:
    """Draw walls and solid blocks of the maze.

    Args:
        screen: Surface to draw on.
        state: Current game state.
    """
    for row, line in enumerate(state.maze.grid):
        for col, value in enumerate(line):
            x = col * CELL_SIZE
            y = row * CELL_SIZE + HUD_HEIGHT

            if value == BLOCK:
                pygame.draw.rect(
                    screen,
                    BLOCK_COLOR,
                    (x, y, CELL_SIZE, CELL_SIZE),
                )
                continue

            _draw_cell_walls(screen, value, x, y)


def _draw_pacgums(screen: pygame.Surface, state: GameState) -> None:
    """Draw the remaining pacgums and super-pacgums.

    Args:
        screen: Surface to draw on.
        state: Current game state.
    """
    for cell in state.pacgums:
        pygame.draw.circle(screen, PACGUM_COLOR, _to_pixels(cell), 3)

    for cell in state.super_pacgums:
        pygame.draw.circle(screen, SUPER_PACGUM_COLOR, _to_pixels(cell), 7)


def _draw_player(
    screen: pygame.Surface,
    state: GameState,
    hidden_mode: bool,
) -> None:
    """Draw Pac-Man.

    Args:
        screen: Surface to draw on.
        state: Current game state.
        hidden_mode: True when the player is in hidden mode.
    """
    color = HIDDEN_MODE_COLOR if hidden_mode else PLAYER_COLOR
    radius = CELL_SIZE // 2 - 2

    pygame.draw.circle(screen, color, _to_pixels(state.player_pos), radius)

    if hidden_mode:
        pygame.draw.circle(
            screen,
            (255, 255, 255),
            _to_pixels(state.player_pos),
            radius,
            2,
        )


def _draw_ghosts(screen: pygame.Surface, state: GameState) -> None:
    """Draw every ghost of the level.

    Args:
        screen: Surface to draw on.
        state: Current game state.
    """
    radius = CELL_SIZE // 2 - 3

    for ghost in state.ghosts:
        if ghost.eaten:
            color = EATEN_GHOST_COLOR
        elif ghost.edible:
            color = EDIBLE_GHOST_COLOR
        else:
            color = GHOST_COLORS.get(ghost.color, (255, 255, 255))

        center = _to_pixels(ghost.pos)

        if ghost.eaten:
            pygame.draw.circle(screen, color, center, radius, 2)
            continue

        pygame.draw.circle(screen, color, center, radius)


def draw_frame(
    screen: pygame.Surface,
    state: GameState,
    cheats: CheatManager,
) -> None:
    """Draw one complete frame of the gameplay screen.

    Args:
        screen: Surface to draw on.
        state: Current game state.
        cheats: Cheat manager of the session.
    """
    screen.fill(BACKGROUND_COLOR)

    _draw_maze(screen, state)
    _draw_pacgums(screen, state)
    _draw_ghosts(screen, state)
    _draw_player(screen, state, cheats.hidden_mode)

    draw_hud(screen, state, cheats)

    pygame.display.flip()
