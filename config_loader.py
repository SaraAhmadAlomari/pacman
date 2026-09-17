"""Load, clean and validate the Pac-Man configuration file.

The configuration is JSON with comments. Three comment styles are
accepted and removed before parsing:

* shell style, a line starting with ``#``
* C++ style, ``//`` until the end of the line
* C style, ``/* ... */`` possibly spanning several lines

Every value is validated. An invalid or missing value never stops the
game: it is clamped to a safe default and a clear message is printed.
Unknown keys are ignored.
"""

import json
import os
from typing import Any, Dict, List, Tuple

ConfigDict = Dict[str, Any]

DEFAULT_LEVEL_COUNT = 10
MIN_LEVEL_COUNT = 10
MIN_MAZE_SIZE = 11
MAX_MAZE_SIZE = 41

DEFAULTS: ConfigDict = {
    "highscore_filename": "highscores.json",
    "lives": 3,
    "pacgum": 150,
    "points_per_pacgum": 10,
    "points_per_super_pacgum": 50,
    "points_per_ghost": 200,
    "points_per_level": 500,
    "seed": 42,
    "level_max_time": 90,
    "super_pacgum_duration": 7,
    "ghost_respawn_time": 5,
}


INT_BOUNDS: Dict[str, Tuple[int, int]] = {
    "lives": (1, 99),
    "pacgum": (1, 10000),
    "points_per_pacgum": (0, 100000),
    "points_per_super_pacgum": (0, 100000),
    "points_per_ghost": (0, 100000),
    "points_per_level": (0, 100000),
    "seed": (0, 2**31 - 1),
    "level_max_time": (5, 3600),
    "super_pacgum_duration": (1, 600),
    "ghost_respawn_time": (0, 600),
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

    Characters inside JSON strings are preserved, so a ``#`` used in a
    player name or a file path is never mistaken for a comment.

    Args:
        text: Raw content of the configuration file.

    Returns:
        The same document with every comment replaced by whitespace.
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
                index = length
            else:
                result.append("\n" * text.count("\n", index, end))
                index = end + 2
            continue

        result.append(char)
        index += 1

    return "".join(result)


def _read_int(config: ConfigDict, key: str) -> int:
    """Read one integer setting, clamped inside its allowed range.

    Args:
        config: Raw configuration dictionary.
        key: Name of the setting to read.

    Returns:
        A usable integer value.
    """
    default = int(DEFAULTS[key])
    minimum, maximum = INT_BOUNDS[key]
    raw = config.get(key, default)

    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        _warn(f"'{key}' is not a number, using default {default}.")
        return default

    value = int(raw)

    if value < minimum:
        _warn(f"'{key}' is too small, clamped to {minimum}.")
        return minimum

    if value > maximum:
        _warn(f"'{key}' is too large, clamped to {maximum}.")
        return maximum

    return value


def _read_filename(config: ConfigDict) -> str:
    """Read the highscore filename setting.

    Args:
        config: Raw configuration dictionary.

    Returns:
        A usable filename.
    """
    default = str(DEFAULTS["highscore_filename"])
    raw = config.get("highscore_filename", default)

    if not isinstance(raw, str) or not raw.strip():
        _warn(f"'highscore_filename' is invalid, using '{default}'.")
        return default

    return raw.strip()


def _read_size(level: Dict[str, Any], key: str, index: int) -> int:
    """Read one maze dimension of one level.

    Args:
        level: Raw level description.
        key: Either ``width`` or ``height``.
        index: Zero based index of the level, used in messages.

    Returns:
        A maze dimension inside the supported range.
    """
    raw = level.get(key, 21)

    if isinstance(raw, bool) or not isinstance(raw, (int, float)):
        _warn(f"level {index + 1}: '{key}' is not a number, using 21.")
        return 21

    value = int(raw)

    if value < MIN_MAZE_SIZE:
        _warn(f"level {index + 1}: '{key}' clamped to {MIN_MAZE_SIZE}.")
        return MIN_MAZE_SIZE

    if value > MAX_MAZE_SIZE:
        _warn(f"level {index + 1}: '{key}' clamped to {MAX_MAZE_SIZE}.")
        return MAX_MAZE_SIZE

    return value


def _default_levels() -> List[Dict[str, int]]:
    """Build the fallback list of levels.

    Returns:
        Ten levels of slowly growing size.
    """
    levels: List[Dict[str, int]] = []

    for index in range(DEFAULT_LEVEL_COUNT):
        size = 21 + (index // 2) * 2
        levels.append({"width": size, "height": size})

    return levels


def _read_levels(config: ConfigDict) -> List[Dict[str, int]]:
    """Read and repair the list of levels.

    Args:
        config: Raw configuration dictionary.

    Returns:
        At least ten valid level descriptions.
    """
    raw = config.get("levels", config.get("level"))

    if not isinstance(raw, list) or not raw:
        _warn("'levels' is missing or invalid, using the default levels.")
        return _default_levels()

    levels: List[Dict[str, int]] = []

    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            _warn(f"level {index + 1} is not an object, using 21x21.")
            levels.append({"width": 21, "height": 21})
            continue

        levels.append(
            {
                "width": _read_size(item, "width", index),
                "height": _read_size(item, "height", index),
            }
        )

    if len(levels) < MIN_LEVEL_COUNT:
        _warn(
            f"only {len(levels)} level(s) defined, padding up to "
            f"{MIN_LEVEL_COUNT}."
        )
        while len(levels) < MIN_LEVEL_COUNT:
            levels.append(dict(levels[-1]))

    return levels


def validate_config(config: ConfigDict) -> ConfigDict:
    """Turn a raw configuration into a safe one.

    Args:
        config: Configuration as read from the file.

    Returns:
        A configuration where every key exists and holds a usable value.
    """
    known = set(DEFAULTS) | {"levels", "level"}

    for key in config:
        if key not in known:
            _warn(f"unknown key '{key}' ignored.")

    clean: ConfigDict = {"highscore_filename": _read_filename(config)}

    for key in INT_BOUNDS:
        clean[key] = _read_int(config, key)

    clean["levels"] = _read_levels(config)

    return clean


def load_config(filename: str) -> ConfigDict:
    """Load, clean and validate a configuration file.

    Args:
        filename: Path to the JSON configuration file.

    Returns:
        A validated configuration dictionary.

    Raises:
        ConfigError: If the file cannot be read or parsed.
    """
    if not filename.lower().endswith(".json"):
        raise ConfigError(f"'{filename}' is not a .json file.")

    if not os.path.isfile(filename):
        raise ConfigError(f"configuration file '{filename}' was not found.")

    try:
        with open(filename, "r", encoding="utf-8") as config_file:
            text = config_file.read()
    except OSError as exc:
        raise ConfigError(f"cannot read '{filename}': {exc}") from exc

    try:
        data = json.loads(strip_comments(text))
    except json.JSONDecodeError as exc:
        raise ConfigError(
            f"'{filename}' is not valid JSON (line {exc.lineno}): {exc.msg}"
        ) from exc

    if not isinstance(data, dict):
        raise ConfigError(f"'{filename}' must contain a JSON object.")

    return validate_config(data)
