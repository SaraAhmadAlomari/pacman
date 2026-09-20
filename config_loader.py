"""Load, clean and validate the Pac-Man configuration file.

The configuration is JSON with comments. Three comment styles are
accepted and removed before parsing:

* shell style: a line starting with '#'
* C++ style: '//' until the end of the line
* C style: '/* ... */' possibly spanning several lines

Invalid or missing values never stop the game. A safe default is used
and a clear message is printed.
"""

import json
import os
from typing import Any, Dict, List, Tuple


ConfigDict = Dict[str, Any]

DEFAULT_LEVEL_COUNT = 10
DEFAULT_MAZE_SIZE = 29

MIN_MAZE_SIZE = 11
MAX_MAZE_SIZE = 41

DEFAULTS: ConfigDict = {
    "highscore_filename": "highscores.json",
    "lives": 3,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 90,
}


INT_BOUNDS: Dict[str, Tuple[int, int]] = {
    "lives": (1, 99),
    "points_per_pacgum": (0, 100000),
    "points_per_super_pacgum": (0, 100000),
    "points_per_ghost": (0, 100000),
    "seed": (0, 2**31 - 1),
    "level_max_time": (5, 3600),
}


class ConfigError(Exception):
    """Raised when the configuration cannot be read at all."""


def _warn(message: str) -> None:
    """Print a configuration warning.

    Args:
        message: Human readable explanation of the problem.
    """
    print(f"[config] {message}")


def strip_comments(text: str) -> str:
    """Remove comments from a JSON document.

    Characters inside JSON strings are preserved.

    Args:
        text: Raw configuration text.

    Returns:
        Configuration text without comments.
    """
    result: List[str] = []
    index = 0
    length = len(text)
    in_string = False
    escaped = False

    while index < length:
        char = text[index]

        if in_string:
            result.append(char)

            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False

            index += 1
            continue

        if char == '"':
            in_string = True
            result.append(char)
            index += 1
            continue

        two = text[index:index + 2]

        if char == "#" or two == "//":
            while index < length and text[index] != "\n":
                index += 1
            continue

        if two == "/*":
            end = text.find("*/", index + 2)

            if end == -1:
                _warn(
                    "unterminated block comment, ignoring the rest "
                    "of the file."
                )
                break

            result.append(
                "\n" * text.count("\n", index, end)
            )
            index = end + 2
            continue

        result.append(char)
        index += 1

    return "".join(result)


def _read_int(config: ConfigDict, key: str) -> int:
    """Read and validate an integer configuration value.

    Args:
        config: Raw configuration dictionary.
        key: Configuration key.

    Returns:
        A safe integer value.
    """
    default = int(DEFAULTS[key])
    minimum, maximum = INT_BOUNDS[key]

    if key not in config:
        _warn(
            f"'{key}' is missing, using default {default}."
        )
        return default

    raw = config[key]

    if isinstance(raw, bool) or not isinstance(raw, int):
        _warn(
            f"'{key}' is not a valid integer, "
            f"using default {default}."
        )
        return default

    if raw < minimum:
        _warn(
            f"'{key}' is too small, using minimum {minimum}."
        )
        return minimum

    if raw > maximum:
        _warn(
            f"'{key}' is too large, using maximum {maximum}."
        )
        return maximum

    return raw


def _read_filename(config: ConfigDict) -> str:
    """Read and validate the highscore filename.

    Args:
        config: Raw configuration dictionary.

    Returns:
        A safe filename.
    """
    default = str(DEFAULTS["highscore_filename"])

    if "highscore_filename" not in config:
        _warn(
            "'highscore_filename' is missing, "
            f"using default '{default}'."
        )
        return default

    raw = config["highscore_filename"]

    if not isinstance(raw, str) or not raw.strip():
        _warn(
            "'highscore_filename' is invalid, "
            f"using default '{default}'."
        )
        return default

    return raw.strip()


def _read_size(
    level: Dict[str, Any],
    key: str,
) -> int:
    """Read and validate one maze dimension.

    Args:
        level: Level configuration.
        key: 'width' or 'height'.

    Returns:
        A safe maze dimension.
    """
    if key not in level:
        _warn(
            f"level '{key}' is missing, "
            f"using default {DEFAULT_MAZE_SIZE}."
        )
        return DEFAULT_MAZE_SIZE

    raw = level[key]

    if isinstance(raw, bool) or not isinstance(raw, int):
        _warn(
            f"level '{key}' is not a valid integer, "
            f"using default {DEFAULT_MAZE_SIZE}."
        )
        return DEFAULT_MAZE_SIZE

    if raw < MIN_MAZE_SIZE:
        _warn(
            f"level '{key}' is too small, "
            f"using minimum {MIN_MAZE_SIZE}."
        )
        return MIN_MAZE_SIZE

    if raw > MAX_MAZE_SIZE:
        _warn(
            f"level '{key}' is too large, "
            f"using maximum {MAX_MAZE_SIZE}."
        )
        return MAX_MAZE_SIZE

    return raw


def _default_levels() -> List[Dict[str, int]]:
    """Create ten levels with the same maze size.

    Returns:
        Ten 21x21 levels.
    """
    return [
        {
            "width": DEFAULT_MAZE_SIZE,
            "height": DEFAULT_MAZE_SIZE,
        }
        for _ in range(DEFAULT_LEVEL_COUNT)
    ]


def _read_levels(config: ConfigDict) -> List[Dict[str, int]]:
    """Read the maze size and create ten equal-sized levels.

    The configuration only needs one level definition. Its width and
    height are applied to all ten levels.

    Args:
        config: Raw configuration dictionary.

    Returns:
        Ten levels with identical dimensions.
    """
    raw = config.get("levels")

    if raw is None:
        _warn(
            "'levels' is missing, "
            f"using {DEFAULT_MAZE_SIZE}x{DEFAULT_MAZE_SIZE} "
            f"for all {DEFAULT_LEVEL_COUNT} levels."
        )
        return _default_levels()

    if not isinstance(raw, list) or not raw:
        _warn(
            "'levels' is invalid, "
            f"using {DEFAULT_MAZE_SIZE}x{DEFAULT_MAZE_SIZE} "
            f"for all {DEFAULT_LEVEL_COUNT} levels."
        )
        return _default_levels()

    first_level = raw[0]

    if not isinstance(first_level, dict):
        _warn(
            "first level is not an object, "
            f"using {DEFAULT_MAZE_SIZE}x{DEFAULT_MAZE_SIZE} "
            f"for all {DEFAULT_LEVEL_COUNT} levels."
        )
        return _default_levels()

    width = _read_size(first_level, "width")
    height = _read_size(first_level, "height")

    levels: List[Dict[str, int]] = []

    for _ in range(DEFAULT_LEVEL_COUNT):
        levels.append(
            {
                "width": width,
                "height": height,
            }
        )

    if len(raw) > 1:
        _warn(
            "only the first level size is used; "
            "all levels have the same size."
        )

    return levels


def validate_config(config: ConfigDict) -> ConfigDict:
    """Turn raw configuration into a safe configuration.

    Args:
        config: Raw configuration dictionary.

    Returns:
        Validated configuration.
    """
    known_keys = set(DEFAULTS) | {"levels"}

    for key in config:
        if key not in known_keys:
            _warn(
                f"unknown key '{key}' ignored."
            )

    clean: ConfigDict = {}

    clean["highscore_filename"] = _read_filename(config)

    for key in INT_BOUNDS:
        clean[key] = _read_int(config, key)

    clean["levels"] = _read_levels(config)

    return clean


def _default_config() -> ConfigDict:
    """Return a complete default configuration.

    Returns:
        Safe default configuration.
    """
    config: ConfigDict = dict(DEFAULTS)
    config["levels"] = _default_levels()

    return config


def load_config(filename: str) -> ConfigDict:
    """Load and validate the configuration file.

    Any configuration problem is repaired with safe defaults so that
    the game can continue running.

    Args:
        filename: Path to the JSON configuration file.

    Returns:
        A validated configuration dictionary.
    """
    if not filename.lower().endswith(".json"):
        _warn(
            f"'{filename}' is not a .json file, "
            "using default configuration."
        )
        return _default_config()

    if not os.path.isfile(filename):
        _warn(
            f"configuration file '{filename}' was not found, "
            "using default configuration."
        )
        return _default_config()

    try:
        with open(
            filename,
            "r",
            encoding="utf-8",
        ) as config_file:
            text = config_file.read()
    except OSError as exc:
        _warn(
            f"cannot read '{filename}': {exc}. "
            "Using default configuration."
        )
        return _default_config()

    if not text.strip():
        _warn(
            "configuration file is empty, "
            "using default configuration."
        )
        return _default_config()

    cleaned_text = strip_comments(text)

    if not cleaned_text.strip():
        _warn(
            "configuration file contains no data, "
            "using default configuration."
        )
        return _default_config()

    try:
        data = json.loads(cleaned_text)
    except json.JSONDecodeError as exc:
        _warn(
            f"invalid JSON at line {exc.lineno}: {exc.msg}. "
            "Using default configuration."
        )
        return _default_config()

    if not isinstance(data, dict):
        _warn(
            "configuration root must be a JSON object. "
            "Using default configuration."
        )
        return _default_config()

    return validate_config(data)
