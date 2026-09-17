"""Persistent highscore table stored as JSON next to the game.

The table is a plain JSON list of ``{"name": ..., "score": ...}``
objects, kept sorted and truncated to the ten best results. Every read is
defensive: a missing, unreadable or corrupted file simply yields an empty
table instead of stopping the game.
"""

import json
import os
from typing import Any, List

from models import HighScore

MAX_ENTRIES = 10
MAX_NAME_LENGTH = 10
DEFAULT_NAME = "PLAYER"


def sanitize_name(name: str) -> str:
    """Keep only the characters allowed in a player name.

    Allowed characters are letters, digits and spaces, and the result is
    limited to ten characters.

    Args:
        name: Raw name typed by the player.

    Returns:
        A valid name, never empty.
    """
    kept = [
        char
        for char in name
        if char.isalnum() or char == " "
    ]

    cleaned = "".join(kept).strip()[:MAX_NAME_LENGTH].strip()

    return cleaned if cleaned else DEFAULT_NAME


def _parse_entry(item: Any) -> HighScore | None:
    """Convert one raw JSON item into a highscore entry.

    Args:
        item: Item read from the highscore file.

    Returns:
        The entry, or ``None`` when the item is unusable.
    """
    if not isinstance(item, dict):
        return None

    name = item.get("name")
    score = item.get("score")

    if not isinstance(name, str):
        return None

    if isinstance(score, bool) or not isinstance(score, int):
        return None

    if score < 0:
        return None

    return HighScore(name=sanitize_name(name), score=score)


def load_highscores(filename: str) -> List[HighScore]:
    """Read the highscore table.

    Args:
        filename: Path to the highscore file.

    Returns:
        At most the ten best entries, sorted by decreasing score.
    """
    if not os.path.isfile(filename):
        return []

    try:
        with open(filename, "r", encoding="utf-8") as score_file:
            data = json.load(score_file)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"[highscore] cannot read '{filename}': {exc}")
        return []

    if not isinstance(data, list):
        print(f"[highscore] '{filename}' is not a list, ignoring it.")
        return []

    entries = [
        entry
        for entry in (_parse_entry(item) for item in data)
        if entry is not None
    ]

    entries.sort(key=lambda entry: entry.score, reverse=True)

    return entries[:MAX_ENTRIES]


def save_highscores(filename: str, entries: List[HighScore]) -> bool:
    """Write the ten best entries to disk.

    Args:
        filename: Path to the highscore file.
        entries: Entries to save.

    Returns:
        True when the file was written.
    """
    best = sorted(entries, key=lambda entry: entry.score, reverse=True)
    best = best[:MAX_ENTRIES]

    try:
        with open(filename, "w", encoding="utf-8") as score_file:
            json.dump(
                [entry.as_dict() for entry in best],
                score_file,
                indent=4,
            )
    except (OSError, TypeError, ValueError) as exc:
        print(f"[highscore] cannot write '{filename}': {exc}")
        return False

    return True


def add_score(filename: str, name: str, score: int) -> List[HighScore]:
    """Add one result to the table and save it.

    Args:
        filename: Path to the highscore file.
        name: Name typed by the player.
        score: Final score of the session.

    Returns:
        The updated table.
    """
    entries = load_highscores(filename)
    entries.append(HighScore(name=sanitize_name(name), score=max(0, score)))

    entries.sort(key=lambda entry: entry.score, reverse=True)
    entries = entries[:MAX_ENTRIES]

    save_highscores(filename, entries)

    return entries
