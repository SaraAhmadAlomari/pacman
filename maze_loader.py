"""Adapt the external A-Maze-ing package to the game's Maze model.

The generator is used as-is: the game only reads ``MazeGenerator.maze``
and converts it into the :class:`models.Maze` structure the rest of the
game understands. Nothing here modifies the package.

Cell values are wall bitmasks: 1 = north, 2 = east, 4 = south, 8 = west.
A cell whose value is 15 is fully enclosed, so it is a solid block and
never walkable.
"""

from typing import List, Optional, Tuple

from mazegenerator import MazeGenerator

from models import Maze, Position

BLOCK = 15


class MazeError(RuntimeError):
    """Raised when the external generator cannot produce a usable maze."""


def _nearest_corridor(
    corridors: List[Position],
    target: Position,
) -> Position:
    """Find the walkable cell closest to a target cell.

    Args:
        corridors: Every walkable cell of the maze.
        target: Cell we would like to use.

    Returns:
        ``target`` itself when it is walkable, otherwise the closest
        walkable cell.
    """
    if target in corridors:
        return target

    return min(
        corridors,
        key=lambda cell: (
            abs(cell[0] - target[0]) + abs(cell[1] - target[1])
        ),
    )


def extract_corridors(grid: List[List[int]]) -> List[Position]:
    """List every walkable cell of a generated grid.

    Args:
        grid: Raw grid returned by the generator.

    Returns:
        Walkable cells as ``(row, column)`` pairs.
    """
    corridors: List[Position] = []

    for row, line in enumerate(grid):
        for col, value in enumerate(line):
            if value != BLOCK:
                corridors.append((row, col))

    return corridors


def pick_corners(
    corridors: List[Position],
    height: int,
    width: int,
) -> List[Position]:
    """Choose the four ghost corners of a maze.

    Args:
        corridors: Every walkable cell of the maze.
        height: Number of rows.
        width: Number of columns.

    Returns:
        Four distinct walkable cells, one per corner.
    """
    wanted = [
        (0, 0),
        (0, width - 1),
        (height - 1, 0),
        (height - 1, width - 1),
    ]

    corners: List[Position] = []
    remaining = list(corridors)

    for target in wanted:
        cell = _nearest_corridor(remaining, target)
        corners.append(cell)
        if len(remaining) > 1:
            remaining.remove(cell)

    return corners


def load_maze(
    width: int,
    height: int,
    seed: Optional[int] = None,
) -> Maze:
    """Generate one maze with the assigned A-Maze-ing package.

    Args:
        width: Requested number of columns.
        height: Requested number of rows.
        seed: Seed given to the generator. ``None`` lets the generator
            pick its own, which produces a random maze.

    Returns:
        A maze ready to be played.

    Raises:
        MazeError: If the generator fails or returns an unusable grid.
    """
    try:
        generator = MazeGenerator(
            size=(width, height),
            perfect=False,
            seed=seed if seed is not None else 0,
        )
        raw_grid: List[List[int]] = generator.maze
    except Exception as exc:
        raise MazeError(
            f"the maze generator failed for {width}x{height}: {exc}"
        ) from exc

    if not raw_grid or not raw_grid[0]:
        raise MazeError("the maze generator returned an empty maze.")

    grid: List[List[int]] = [[int(cell) for cell in row] for row in raw_grid]
    real_height = len(grid)
    real_width = len(grid[0])

    corridors = extract_corridors(grid)

    if len(corridors) < 8:
        raise MazeError("the generated maze has almost no corridor.")

    corners = pick_corners(corridors, real_height, real_width)
    center = _nearest_corridor(
        corridors,
        (real_height // 2, real_width // 2),
    )

    return Maze(
        width=real_width,
        height=real_height,
        grid=grid,
        corridors=corridors,
        corners=corners,
        center=center,
    )


def can_move(maze: Maze, current: Position, target: Position) -> bool:
    """Tell whether a move between two adjacent cells is legal.

    Both the wall of the current cell and the facing wall of the target
    cell are checked, so a move is refused as soon as one of them exists.

    Args:
        maze: Maze being played.
        current: Cell the entity stands on.
        target: Cell the entity wants to reach.

    Returns:
        True when the move crosses no wall.
    """
    row, col = current
    target_row, target_col = target

    if not 0 <= target_row < maze.height:
        return False

    if not 0 <= target_col < maze.width:
        return False

    if maze.grid[target_row][target_col] == BLOCK:
        return False

    walls: Tuple[int, int]

    if target == (row - 1, col):
        walls = (1, 4)
    elif target == (row, col + 1):
        walls = (2, 8)
    elif target == (row + 1, col):
        walls = (4, 1)
    elif target == (row, col - 1):
        walls = (8, 2)
    else:
        return False

    if maze.grid[row][col] & walls[0]:
        return False

    return not maze.grid[target_row][target_col] & walls[1]
