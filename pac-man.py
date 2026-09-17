"""Pac-Man - entry point.

Usage:
    python3 pac-man.py config.json

The program takes exactly one argument: a JSON configuration file. Any
problem, from a missing file to a broken maze generator, is reported with
a readable message and never with a Python traceback.
"""

import sys
from typing import Any, Dict, Optional, Tuple

import pygame

from cheat import CheatManager
from config_loader import ConfigError, load_config
from game_over import show_game_over
from game_state import GameEngine
from highscore import add_score
from highscores import show_highscores
from input import read_actions, read_direction
from instructions import show_instructions
from main_menu import show_main_menu
from maze_loader import MazeError
from pause_menu import show_pause_menu
from renderer import draw_frame, window_size

WINDOW_TITLE = "Pac-Man"
MENU_SIZE = (720, 640)
MAX_FPS = 60
USAGE = "usage: python3 pac-man.py <config.json>"


def parse_arguments(argv: list[str]) -> str:
    """Validate the command line and return the configuration path.

    Args:
        argv: Full argument vector, script name included.

    Returns:
        Path to the configuration file.

    Raises:
        ConfigError: If the number of arguments is not exactly one.
    """
    arguments = argv[1:]

    if len(arguments) != 1:
        raise ConfigError(
            f"expected exactly one argument, got {len(arguments)}.\n{USAGE}"
        )

    return arguments[0]


def resize_window(size: Tuple[int, int]) -> pygame.Surface:
    """Create or resize the game window.

    Args:
        size: Wanted window size in pixels.

    Returns:
        The display surface.
    """
    return pygame.display.set_mode(size)


def _apply_cheat(engine: GameEngine, action: str) -> None:
    """Apply one cheat action to the running game.

    Args:
        engine: Engine of the running session.
        action: Cheat action read from the keyboard.
    """
    cheats: CheatManager = engine.cheats

    if action == "hidden_mode":
        engine.notify(cheats.toggle_hidden_mode())
    elif action == "freeze_ghosts":
        engine.notify(cheats.toggle_ghost_freeze())
    elif action == "speed_boost":
        engine.notify(cheats.toggle_speed_boost())
    elif action == "extra_life":
        engine.notify(cheats.add_extra_life(engine.state))
    elif action == "skip_level":
        engine.notify(cheats.clear_level(engine.state))


def run_game(
    screen: pygame.Surface,
    engine: GameEngine,
) -> Tuple[pygame.Surface, str]:
    """Run one full game session.

    Args:
        screen: Current display surface.
        engine: Engine of the session.

    Returns:
        The display surface, which may have been resized, and the result:
        ``"over"`` when the game ended, ``"menu"`` when the player left,
        or ``"quit"`` when the window was closed.
    """
    clock = pygame.time.Clock()
    current_size = window_size(engine.state)
    screen = resize_window(current_size)

    while True:
        delta_time = clock.tick(MAX_FPS) / 1000.0

        for action in read_actions():
            if action == "quit":
                return screen, "quit"

            if action == "pause":
                choice = show_pause_menu(screen)

                if choice == "quit":
                    return screen, "quit"

                if choice == "main_menu":
                    return screen, "menu"

                clock.tick(MAX_FPS)
                continue

            _apply_cheat(engine, action)

        direction = read_direction()

        if direction is not None:
            engine.request_direction(direction)

        engine.update(delta_time)

        if engine.state.status in ("won", "lost"):
            return screen, "over"

        wanted_size = window_size(engine.state)

        if wanted_size != current_size:
            current_size = wanted_size
            screen = resize_window(current_size)

        draw_frame(screen, engine.state, engine.cheats)


def handle_game_end(
    screen: pygame.Surface,
    engine: GameEngine,
    highscore_file: str,
) -> str:
    """Show the final screen and save the score if asked.

    Args:
        screen: Current display surface.
        engine: Finished engine.
        highscore_file: Path to the highscore file.

    Returns:
        ``"menu"`` or ``"quit"``.
    """
    name, action = show_game_over(screen, engine.state)

    if action == "save":
        add_score(highscore_file, name, engine.state.score)

    return "quit" if action == "quit" else "menu"


def start_session(
    screen: pygame.Surface,
    config: Dict[str, Any],
) -> Tuple[pygame.Surface, str]:
    """Create an engine and play one session from start to end.

    Args:
        screen: Current display surface.
        config: Validated configuration.

    Returns:
        The display surface and ``"menu"`` or ``"quit"``.
    """
    try:
        engine = GameEngine(config)
    except MazeError as exc:
        print(f"[maze] {exc}")
        return screen, "menu"

    screen, result = run_game(screen, engine)

    if result == "quit":
        return screen, "quit"

    if result == "over":
        outcome = handle_game_end(
            screen,
            engine,
            str(config["highscore_filename"]),
        )
        return screen, outcome

    return screen, "menu"


def run_application(config: Dict[str, Any]) -> None:
    """Run the menu loop until the player exits.

    Args:
        config: Validated configuration.
    """
    highscore_file = str(config["highscore_filename"])
    screen = resize_window(MENU_SIZE)

    while True:
        screen = resize_window(MENU_SIZE)
        choice = show_main_menu(screen, highscore_file)

        if choice in ("exit", "quit"):
            return

        if choice == "start":
            screen, result = start_session(screen, config)

            if result == "quit":
                return

        elif choice == "highscores":
            if show_highscores(screen, highscore_file) == "quit":
                return

        elif choice == "instructions":
            if show_instructions(screen) == "quit":
                return


def main(argv: Optional[list[str]] = None) -> int:
    """Start Pac-Man.

    Args:
        argv: Argument vector, defaults to ``sys.argv``.

    Returns:
        ``0`` on success, ``1`` when the game could not start.
    """
    try:
        path = parse_arguments(sys.argv if argv is None else argv)
        config = load_config(path)
    except ConfigError as exc:
        print(f"Error: {exc}")
        return 1

    try:
        pygame.init()
        pygame.display.set_caption(WINDOW_TITLE)
        run_application(config)
    except pygame.error as exc:
        print(f"Error: the graphical library failed: {exc}")
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted by the user.")
    finally:
        pygame.quit()

    return 0


if __name__ == "__main__":
    sys.exit(main())
