"""Ghost behaviour.

The first two ghosts chase the player using real shortest-path distance.
The other two ghosts move randomly through available cells.
"""

import random
from collections import deque
from typing import Dict, List

from maze_loader import can_move
from models import GhostState, Maze, Position


DIRECTIONS = [
    (-1, 0),
    (1, 0),
    (0, -1),
    (0, 1),
]

_RNG = random.SystemRandom()


def available_moves(
    maze: Maze,
    position: Position,
) -> List[Position]:
    """Return every walkable neighbouring cell."""
    row, col = position
    moves: List[Position] = []

    for row_step, col_step in DIRECTIONS:
        target = (row + row_step, col + col_step)

        if can_move(maze, position, target):
            moves.append(target)

    return moves


def _bfs_distances(maze: Maze, start: Position) -> Dict[Position, int]:
    """
    Compute the real shortest-path distance from start to every
    reachable cell.
    """
    distances: Dict[Position, int] = {start: 0}
    queue = deque([start])

    while queue:
        current = queue.popleft()
        for neighbour in available_moves(maze, current):
            if neighbour not in distances:
                distances[neighbour] = distances[current] + 1
                queue.append(neighbour)

    return distances


def _chase_player(
    ghost: GhostState,
    player_pos: Position,
    maze: Maze,
) -> Position:
    """Move the ghost toward the player using shortest-path distance."""
    moves = available_moves(maze, ghost.pos)

    if not moves:
        return ghost.pos

    distances = _bfs_distances(maze, player_pos)
    unreachable_penalty = len(distances) + 1

    def dist_to_player(cell: Position) -> int:
        return distances.get(cell, unreachable_penalty)

    if ghost.edible:
        return max(moves, key=dist_to_player)

    return min(moves, key=dist_to_player)


def _random_move(
    ghost: GhostState,
    maze: Maze,
) -> Position:
    """Choose a random walkable neighbouring cell."""
    moves = available_moves(maze, ghost.pos)

    if not moves:
        return ghost.pos

    return _RNG.choice(moves)


def next_position(
    ghost: GhostState,
    player_pos: Position,
    maze: Maze,
    chase: bool,
) -> Position:
    """Choose the next position for a ghost."""
    if chase:
        return _chase_player(
            ghost,
            player_pos,
            maze,
        )

    return _random_move(
        ghost,
        maze,
    )


def update_ghosts(
    ghosts: List[GhostState],
    player_pos: Position,
    maze: Maze,
    frozen: bool = False,
) -> None:
    """Move every active ghost."""
    if frozen:
        return

    for index, ghost in enumerate(ghosts):
        if ghost.eaten:
            continue

        chase = index < 2

        ghost.pos = next_position(
            ghost,
            player_pos,
            maze,
            chase,
        )
