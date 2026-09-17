"""Game engine: rules, timers and level progression.

The engine owns the whole simulation and knows nothing about pygame.
"""

import random
from typing import Any, Dict, List, Optional, Set

from cheat import CheatManager
from ghost_ai import update_ghosts
from maze_loader import MazeError, can_move, load_maze
from models import Direction, GameState, GhostState, Position

PLAYER_STEP_TIME = 0.10
GHOST_STEP_TIME = 0.22
MESSAGE_TIME = 2.0
GHOST_COLORS = ["red", "pink", "cyan", "orange"]

_RNG = random.SystemRandom()


class GameEngine:
    """Drive one game session from the first level to the last."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Create an engine and build the first level.

        Args:
            config: Validated configuration dictionary.

        Raises:
            MazeError: If the first maze cannot be generated.
        """
        self.config = config
        self.levels: List[Dict[str, int]] = config["levels"]
        self.cheats = CheatManager()

        self.level_index = 0
        self.score = 0
        self.lives = int(config["lives"])
        self.direction: Optional[Direction] = None
        self.next_direction: Optional[Direction] = None
        self.player_timer = 0.0
        self.ghost_timer = 0.0

        self.state = self._build_level(0)

    def _level_seed(self, level_index: int) -> Optional[int]:
        """Return the seed used for one level.

        The first level always uses the seed from the configuration so it
        is reproducible. Every later level is generated randomly.

        Args:
            level_index: Zero based index of the level.

        Returns:
            The seed, or ``None`` to let the generator randomise.
        """
        if level_index == 0:
            return int(self.config["seed"])

        return _RNG.randint(1, 2**31 - 1)

    def _place_pacgums(self, corridors: List[Position]) -> Set[Position]:
        """Spread pacgums over the corridors of a maze.

        The pacgum setting is the wanted number of pacgums. When it is
        greater than the number of corridors, every corridor gets one.

        Args:
            corridors: Every walkable cell of the maze.

        Returns:
            The cells holding a pacgum.
        """
        wanted = int(self.config["pacgum"])

        if wanted >= len(corridors):
            return set(corridors)

        step = len(corridors) / wanted

        return {corridors[int(index * step)] for index in range(wanted)}

    def _build_level(self, level_index: int) -> GameState:
        """Build the state of one level.

        Args:
            level_index: Zero based index of the level.

        Returns:
            A fresh game state keeping the current score and lives.

        Raises:
            MazeError: If the maze cannot be generated.
        """
        level = self.levels[level_index]
        maze = load_maze(
            level["width"],
            level["height"],
            self._level_seed(level_index),
        )

        ghosts = [
            GhostState(pos=corner, home=corner, color=color)
            for corner, color in zip(maze.corners, GHOST_COLORS)
        ]

        pacgums = self._place_pacgums(maze.corridors)
        pacgums.discard(maze.center)

        super_pacgums: Set[Position] = set()

        for corner in maze.corners:
            pacgums.discard(corner)
            super_pacgums.add(corner)

        self.direction = None
        self.next_direction = None
        self.player_timer = 0.0
        self.ghost_timer = 0.0

        return GameState(
            score=self.score,
            lives=self.lives,
            level=level_index + 1,
            time_left=float(self.config["level_max_time"]),
            maze=maze,
            player_pos=maze.center,
            ghosts=ghosts,
            pacgums=pacgums,
            super_pacgums=super_pacgums,
            status="playing",
        )

    def request_direction(self, direction: Direction) -> None:
        """Store the direction the player wants to take.

        The direction is applied as soon as it becomes legal, which makes
        turning at a junction forgiving instead of frame perfect.

        Args:
            direction: Row and column step requested by the player.
        """
        self.next_direction = direction

    def notify(self, message: str) -> None:
        """Show a short message in the HUD.

        Args:
            message: Text to display.
        """
        self.state.message = message
        self.state.message_timer = MESSAGE_TIME

    def update(self, delta_time: float) -> None:
        """Advance the simulation by one frame.

        Args:
            delta_time: Seconds elapsed since the previous frame.
        """
        if self.state.status != "playing":
            return

        self._update_timers(delta_time)

        if self.state.status != "playing":
            return

        self._update_player(delta_time)
        self._update_ghosts(delta_time)
        self._check_collisions()
        self._check_level_complete()

    def _update_timers(self, delta_time: float) -> None:
        """Update the level, power and respawn timers.

        Args:
            delta_time: Seconds elapsed since the previous frame.
        """
        if self.state.message_timer > 0.0:
            self.state.message_timer -= delta_time

        if self.state.power_timer > 0.0:
            self.state.power_timer -= delta_time

            if self.state.power_timer <= 0.0:
                self.state.power_timer = 0.0
                for ghost in self.state.ghosts:
                    ghost.edible = False

        for ghost in self.state.ghosts:
            if not ghost.eaten:
                continue

            ghost.respawn_timer -= delta_time

            if ghost.respawn_timer <= 0.0:
                ghost.eaten = False
                ghost.edible = self.state.power_timer > 0.0
                ghost.respawn_timer = 0.0
                ghost.pos = ghost.home

        self.state.time_left -= delta_time

        if self.state.time_left <= 0.0:
            self.state.time_left = 0.0
            self._lose_life(timeout=True)

    def _step_target(self, direction: Direction) -> Position:
        """Return the cell reached by one step in a direction.

        Args:
            direction: Row and column step.

        Returns:
            The target cell.
        """
        row, col = self.state.player_pos
        return (row + direction[0], col + direction[1])

    def _update_player(self, delta_time: float) -> None:
        """Move the player at a constant speed.

        Args:
            delta_time: Seconds elapsed since the previous frame.
        """
        self.player_timer += delta_time * self.cheats.speed_factor

        if self.player_timer < PLAYER_STEP_TIME:
            return

        self.player_timer = 0.0

        if self.next_direction is not None:
            target = self._step_target(self.next_direction)
            if can_move(self.state.maze, self.state.player_pos, target):
                self.direction = self.next_direction
                self.next_direction = None

        if self.direction is None:
            return

        target = self._step_target(self.direction)

        if not can_move(self.state.maze, self.state.player_pos, target):
            self.direction = None
            return

        self.state.player_pos = target

    def _update_ghosts(self, delta_time: float) -> None:
        """Move the ghosts on their own, slower, clock.

        Args:
            delta_time: Seconds elapsed since the previous frame.
        """
        self.ghost_timer += delta_time

        if self.ghost_timer < GHOST_STEP_TIME:
            return

        self.ghost_timer = 0.0

        update_ghosts(
            self.state.ghosts,
            self.state.player_pos,
            self.state.maze,
            frozen=self.cheats.ghosts_frozen,
        )

    def _eat_pacgums(self) -> None:
        """Collect the pacgum or super-pacgum under the player."""
        position = self.state.player_pos

        if position in self.state.pacgums:
            self.state.pacgums.discard(position)
            self._add_score(int(self.config["points_per_pacgum"]))

        if position in self.state.super_pacgums:
            self.state.super_pacgums.discard(position)
            self._add_score(int(self.config["points_per_super_pacgum"]))
            self.state.power_timer = float(
                self.config["super_pacgum_duration"]
            )

            for ghost in self.state.ghosts:
                if not ghost.eaten:
                    ghost.edible = True

    def _add_score(self, points: int) -> None:
        """Increase the score, which never decreases.

        Args:
            points: Points to add.
        """
        self.score += max(0, points)
        self.state.score = self.score

    def _check_collisions(self) -> None:
        """Resolve everything standing on the player's cell."""
        self._eat_pacgums()

        for ghost in self.state.ghosts:
            if ghost.eaten or ghost.pos != self.state.player_pos:
                continue

            if ghost.edible:
                self._eat_ghost(ghost)
            elif not self.cheats.hidden_mode:
                self._lose_life()
                return

    def _eat_ghost(self, ghost: GhostState) -> None:
        """Eat one edible ghost and send it home.

        Args:
            ghost: The ghost standing on the player.
        """
        self._add_score(int(self.config["points_per_ghost"]))
        ghost.eaten = True
        ghost.edible = False
        ghost.respawn_timer = float(self.config["ghost_respawn_time"])

    def _lose_life(self, timeout: bool = False) -> None:
        """Take one life and restart the level layout.

        Args:
            timeout: True when the life is lost because the level timer
                reached zero.
        """
        self.lives -= 1
        self.state.lives = self.lives

        if self.lives <= 0:
            self.state.status = "lost"
            return

        self.state.time_left = float(self.config["level_max_time"])
        self.state.power_timer = 0.0
        self.state.player_pos = self.state.maze.center
        self.direction = None
        self.next_direction = None

        for ghost in self.state.ghosts:
            ghost.pos = ghost.home
            ghost.edible = False
            ghost.eaten = False
            ghost.respawn_timer = 0.0

        self.notify("Time is up!" if timeout else "Ouch! One life lost")

    def _check_level_complete(self) -> None:
        """Move to the next level, or win the game, once the maze is clear."""
        if self.state.pacgums or self.state.super_pacgums:
            return

        self._add_score(int(self.config["points_per_level"]))
        self.level_index += 1

        if self.level_index >= len(self.levels):
            self.state.status = "won"
            return

        try:
            self.state = self._build_level(self.level_index)
        except MazeError as exc:
            print(f"[maze] {exc}")
            self.state.status = "won"
            return

        self.notify(f"Level {self.state.level}")
