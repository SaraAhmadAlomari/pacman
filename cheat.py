"""Cheat mode, provided so a reviewer can test every feature quickly."""

from dataclasses import dataclass

from models import GameState

SPEED_MULTIPLIER = 2.0


@dataclass
class CheatManager:
    """Hold and apply the cheats enabled during a session.

    Attributes:
        hidden_mode: The player cannot lose a life.
        ghosts_frozen: Ghosts stop moving.
        speed_boost: The player moves twice as fast.
    """

    hidden_mode: bool = False
    ghosts_frozen: bool = False
    speed_boost: bool = False

    @property
    def speed_factor(self) -> float:
        """Return the multiplier applied to the player's speed."""
        return SPEED_MULTIPLIER if self.speed_boost else 1.0

    def toggle_hidden_mode(self) -> str:
        """Toggle invincibility.

        Returns:
            A message describing the new state.
        """
        self.hidden_mode = not self.hidden_mode
        return f"Hidden mode: {'ON' if self.hidden_mode else 'OFF'}"

    def toggle_ghost_freeze(self) -> str:
        """Toggle the ghost freeze.

        Returns:
            A message describing the new state.
        """
        self.ghosts_frozen = not self.ghosts_frozen
        return f"Ghost freeze: {'ON' if self.ghosts_frozen else 'OFF'}"

    def toggle_speed_boost(self) -> str:
        """Toggle the speed boost.

        Returns:
            A message describing the new state.
        """
        self.speed_boost = not self.speed_boost
        return f"Speed boost: {'ON' if self.speed_boost else 'OFF'}"

    def add_extra_life(self, state: GameState) -> str:
        """Give one extra life to the player.

        Args:
            state: Current game state.

        Returns:
            A message describing the new state.
        """
        state.lives += 1
        return f"Extra life granted (lives: {state.lives})"

    def clear_level(self, state: GameState) -> str:
        """Eat every remaining pacgum so the level is won at once.

        Args:
            state: Current game state.

        Returns:
            A message describing the action.
        """
        state.pacgums.clear()
        state.super_pacgums.clear()
        return "Level skipped"
