"""Ghost behaviour.

Ghosts chase the player with a greedy Manhattan distance heuristic, with
a small amount of randomness so the four of them do not walk in a single
line. When they are edible they use the opposite rule and run away.
"""

import random
from typing import List

from maze_loader import can_move
from models import GhostState, Maze, Position

CHASE_PROBABILITY = 0.75
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

_RNG = random.SystemRandom()


def _distance(first: Position, second: Position) -> int:
    """Return the Manhattan distance between two cells.

    Args:
        first: First cell.
        second: Second cell.

    Returns:
        The distance in cells.
    """
    return abs(first[0] - second[0]) + abs(first[1] - second[1])


def available_moves(maze: Maze, position: Position) -> List[Position]:
    """List every cell reachable from a position in one step.

    Args:
        maze: Maze being played.
        position: Cell to start from.

    Returns:
        Reachable neighbouring cells.
    """
    row, col = position
    moves: List[Position] = []

    for row_step, col_step in DIRECTIONS:
        target = (row + row_step, col + col_step)
        if can_move(maze, position, target):
            moves.append(target)

    return moves


def next_position(
    ghost: GhostState,
    player_pos: Position,
    maze: Maze,
) -> Position:
    """Choose the next cell of one ghost.

    Args:
        ghost: Ghost to move.
        player_pos: Current cell of the player.
        maze: Maze being played.

    Returns:
        The cell the ghost should move to.
    """
    moves = available_moves(maze, ghost.pos)

    if not moves:
        return ghost.pos

    if ghost.edible:
        return max(moves, key=lambda cell: _distance(cell, player_pos))

    if _RNG.random() < CHASE_PROBABILITY:
        return min(moves, key=lambda cell: _distance(cell, player_pos))

    return _RNG.choice(moves)


def update_ghosts(
    ghosts: List[GhostState],
    player_pos: Position,
    maze: Maze,
    frozen: bool = False,
) -> None:
    """Move every active ghost by one cell.

    Ghosts that have been eaten stay where they are until their respawn
    timer brings them back, so they are skipped here.

    Args:
        ghosts: Ghosts of the current level, modified in place.
        player_pos: Current cell of the player.
        maze: Maze being played.
        frozen: True when the ghost freeze cheat is enabled.
    """
    if frozen:
        return

    for ghost in ghosts:
        if ghost.eaten:
            continue

        ghost.pos = next_position(ghost, player_pos, maze)
