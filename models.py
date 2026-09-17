"""Shared data structures used across the Pac-Man modules.

This module only holds plain data containers. It must not import any
other project module, so it can be reused freely without creating
circular imports.
"""

from dataclasses import dataclass
from typing import Dict, List, Literal, Set, Tuple

Position = Tuple[int, int]
Direction = Tuple[int, int]
GameStatus = Literal["menu", "playing", "paused", "won", "lost"]


@dataclass
class Maze:
    """A maze as consumed by the game.

    Attributes:
        width: Number of columns.
        height: Number of rows.
        grid: Wall bitmask for every cell (1=N, 2=E, 4=S, 8=W).
        corridors: Every walkable cell of the maze.
        corners: The four playable cells closest to the corners.
        center: The starting cell of the player.
    """

    width: int
    height: int
    grid: List[List[int]]
    corridors: List[Position]
    corners: List[Position]
    center: Position


@dataclass
class GhostState:
    """State of a single ghost.

    Attributes:
        pos: Current cell of the ghost.
        home: Corner the ghost respawns to after being eaten.
        color: Colour name used by the renderer.
        edible: True while the ghost can be eaten by the player.
        eaten: True while the ghost waits for its respawn delay.
        respawn_timer: Seconds left before the ghost comes back.
    """

    pos: Position
    home: Position
    color: str
    edible: bool = False
    eaten: bool = False
    respawn_timer: float = 0.0


@dataclass
class GameState:
    """Complete state of one game session.

    Attributes:
        score: Current score, never decreasing.
        lives: Remaining lives.
        level: Human readable level number, starting at 1.
        time_left: Seconds left before the level times out.
        maze: Maze of the current level.
        player_pos: Current cell of the player.
        ghosts: Every ghost of the current level.
        pacgums: Cells still holding a regular pacgum.
        super_pacgums: Cells still holding a super-pacgum.
        status: Current status of the session.
        power_timer: Seconds left while ghosts stay edible.
        message: Transient text shown in the HUD.
        message_timer: Seconds left before the message disappears.
    """

    score: int
    lives: int
    level: int
    time_left: float
    maze: Maze
    player_pos: Position
    ghosts: List[GhostState]
    pacgums: Set[Position]
    super_pacgums: Set[Position]
    status: GameStatus
    power_timer: float = 0.0
    message: str = ""
    message_timer: float = 0.0


@dataclass
class HighScore:
    """One entry of the highscore table."""

    name: str
    score: int

    def as_dict(self) -> Dict[str, object]:
        """Return the entry as a JSON serialisable dictionary."""
        return {"name": self.name, "score": self.score}
