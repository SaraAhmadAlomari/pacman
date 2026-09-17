*This activity has been created as part of the 42 curriculum by saalomar, gmagable.*

# Pac-Man

## Description

A complete, playable re-creation of the 1980 Namco arcade game, written in
Python with an object-oriented, modular architecture.

Every maze comes from the external **A-Maze-ing** package assigned to the
group; the game never generates a maze itself. The first level always uses
the seed from the configuration file so it is reproducible, and every later
level is generated randomly.

The player eats pacgums while four ghosts chase them. Super-pacgums sit in
the four corners and turn the ghosts edible for a few seconds. Clearing a
maze moves the player to the next level; losing every life, or a session
ending in victory, opens the name prompt and updates the persistent
highscore table.

Features:

- JSON-with-comments configuration, fully validated and clamped
- no crash: every error path ends with a readable message, never a traceback
- ten levels of growing size, per-level timer, pause and resume
- persistent top-10 highscore table shown on the main menu
- cheat mode for reviewers
- packaging script producing a standalone build for Itch.io

## Instructions

Requirements: Python 3.10 or later.

```bash
make install                  # dependencies + the A-Maze-ing wheel
make run                      # equivalent to: python3 pac-man.py config.json
python3 pac-man.py my.json    # any JSON file works
```

The program takes **exactly one argument**: the configuration file. A
missing argument, a missing file, a wrong extension or broken JSON is
reported as a one-line error and the program exits with status 1.

Other Makefile rules:

| Rule | Effect |
|---|---|
| `make lint` | `flake8 .` and `mypy .` with the mandatory flags |
| `make lint-strict` | `flake8 .` and `mypy . --strict` |
| `make test` | the unit test suite (`pytest`) |
| `make debug` | run the game under `pdb` |
| `make package` | build the standalone binary in `dist/` |
| `make clean` | remove caches and build artefacts |

### Controls

| Key | Action |
|---|---|
| Arrow keys / WASD | move |
| P or ESC | pause |
| 1–4 | main menu entries |
| ENTER | save the score, confirm |

Movement follows the key you hold down. A direction requested while it is
still blocked is remembered and applied as soon as the turn becomes legal,
so turning at a junction is forgiving rather than frame-perfect.

### Cheat mode

Cheats are always available during gameplay so a reviewer can reach every
feature in seconds. The HUD shows which cheats are active.

| Key | Cheat |
|---|---|
| `I` | invincibility, ghosts cannot take a life |
| `F` | freeze the ghosts |
| `L` | one extra life |
| `N` | skip the current level |
| `B` | double the player's speed |

Suggested review path: `N` nine times to reach the victory screen, `I` plus
a super-pacgum to see the edible ghosts and their respawn, `L` and `F` to
check the HUD and the ghost freeze.

## Configuration

The file is JSON plus comments. Three styles are stripped before parsing:
a line starting with `#`, a `//` comment, and a `/* ... */` block. A `#`
inside a JSON string is preserved.

| Key | Default | Range | Meaning |
|---|---|---|---|
| `highscore_filename` | `highscores.json` | non-empty | where the table is stored |
| `lives` | 3 | 1–99 | lives at the start |
| `pacgum` | 150 | 1–10000 | wanted pacgums per level |
| `points_per_pacgum` | 10 | 0–100000 | score per pacgum |
| `points_per_super_pacgum` | 50 | 0–100000 | score per super-pacgum |
| `points_per_ghost` | 200 | 0–100000 | score per edible ghost |
| `points_per_level` | 500 | 0–100000 | bonus for clearing a level |
| `seed` | 42 | ≥ 0 | seed of the **first** level only |
| `level_max_time` | 90 | 5–3600 | seconds per level |
| `super_pacgum_duration` | 7 | 1–600 | seconds the ghosts stay edible |
| `ghost_respawn_time` | 5 | 0–600 | seconds before an eaten ghost returns |
| `levels` | 10 levels | ≥ 10 entries | list of `{ "width", "height" }`, each clamped to 11–41 |

`pacgum` is a target count spread evenly over the corridors of the maze.
When it is greater than the number of corridors, every corridor gets one.

### Faulty configuration handling

`config_loader.validate_config` rebuilds the configuration key by key:

- a value of the wrong type falls back to its default
- a value out of range is clamped to the nearest bound
- a missing or invalid `levels` list falls back to ten default levels, and
  a list shorter than ten entries is padded
- unknown keys are ignored
- every correction prints a `[config] ...` line

Nothing here can stop the game. Only three problems are fatal, and all
three are reported before the window opens: wrong number of arguments,
unreadable file, unparsable JSON.

## Highscore

The table is a JSON list of `{"name": ..., "score": ...}` objects stored in
the file named by `highscore_filename`. It is read when the main menu opens
and written when the player confirms a name on the final screen.

We chose a flat JSON file because it is human-readable, trivially
inspectable during the peer review, and needs no dependency. The cost is
that it is single-user and not concurrency-safe, which does not matter for
a local arcade game.

Robustness is handled on read rather than on write: `load_highscores`
tolerates a missing file, an unreadable file, invalid JSON, a document that
is not a list, entries that are not objects, missing fields, booleans
passed as scores and negative scores. Anything unusable is skipped and the
rest of the table still loads. Names are filtered to letters, digits and
spaces, capped at ten characters, and an empty result becomes `PLAYER`.
The table is sorted by decreasing score and truncated to ten entries.

## Maze Generation

`maze_loader.py` is the only module that touches the external package; it
adapts to the generator's interface and never modifies it.

```python
generator = MazeGenerator(size=(width, height), perfect=False, seed=seed)
grid = generator.maze
```

`perfect=False` makes the generator braid the maze, removing dead ends and
producing the loops Pac-Man needs.

The grid is a wall bitmask per cell: 1 north, 2 east, 4 south, 8 west. A
cell equal to 15 is fully enclosed and is drawn as a solid block, which is
how the generator's decorative "42" appears. The loader turns that grid
into the `Maze` model: the walkable cells, the four ghost corners, and the
player's starting cell. A corner or the centre that happens to fall inside
a block is snapped to the closest walkable cell, so a spawn inside a wall
is impossible.

`can_move` checks both the wall of the cell being left and the facing wall
of the cell being entered, so a wall stored on only one side still blocks.

One trap worth knowing: `MazeGenerator.generate` calls `random.seed()` on
the **global** random module. Anything relying on `random` afterwards
becomes predictable, which would make the "random" levels identical on
every run and the ghosts replay the same moves. The game therefore keeps
its own `random.SystemRandom()` instances in `game_state.py` and
`ghost_ai.py`.

Generator failures raise `MazeError` and are caught: a failure on the first
level returns to the main menu with a message, and the game never crashes.

## Implementation

- **Timers, not frames.** Everything that must feel constant regardless of
  the frame rate is driven by accumulated `delta_time`: the level timer,
  the super-pacgum power, the ghost respawn delays, and the separate step
  clocks of the player (0.10 s) and the ghosts (0.22 s).
- **Ghost lifecycle.** A ghost is normal, edible, or eaten. Eating one sets
  `eaten` and starts `ghost_respawn_time`; when that expires the ghost
  returns to `home`, the corner it started on, and becomes edible again if
  power is still running.
- **Ghost AI.** Greedy Manhattan distance, 75 % of the time towards the
  player and 25 % random so the four of them do not stack into a single
  line; edible ghosts invert the rule and maximise the distance instead.
- **Losing a life** resets positions and the level timer but keeps the maze
  and the pacgums already eaten. The score never decreases.
- **Rendering.** Every entity is positioned through one `_to_pixels`
  helper, so the vertical offset reserved for the HUD is applied once and
  cannot drift between the maze, the ghosts and the player. The window is
  resized whenever a level changes size.
- **Testing.** 19 unit tests cover comment stripping, clamping, spawn
  validity, the power timer, ghost respawn, god mode, the win condition,
  timeouts and the highscore edge cases. They run headless.

## General Software Architecture

```
pac-man.py        entry point: CLI, pygame lifecycle, menu and game loops
config_loader.py  comment stripping, validation, clamping  -> ConfigError
game_state.py     GameEngine: rules, timers, level progression
models.py         dataclasses: Maze, GhostState, GameState, HighScore
maze_loader.py    adapter around the A-Maze-ing package    -> MazeError
ghost_ai.py       ghost movement decisions
cheat.py          CheatManager
input.py          keyboard: held keys for movement, events for actions
highscore.py      persistent table: load, validate, save
renderer.py       maze, pacgums, ghosts, player
hud.py            score, lives, level, time, cheat status
ui.py             shared drawing helpers and font cache
main_menu.py / highscores.py / instructions.py /
pause_menu.py / game_over.py    full-screen panels
tests/            pytest suite
```

Dependencies flow one way:

```
pac-man.py ─> menus / renderer ─> hud ─> models
     │              │
     │              └─> ui
     └─> game_state ─> ghost_ai ─> maze_loader ─> mazegenerator (external)
             └─> cheat ──────────────> models
```

`models.py` imports nothing from the project, so there is no cycle. The
engine never imports pygame, which is why it can be unit tested headless;
the renderer never mutates the state.

## Project packaging

`package.sh`, at the root of the repository, builds a standalone binary
with PyInstaller and assembles `dist/pacman/` with the executable, a
default `config.json` and `packaging/README.txt` (controls, options,
configuration). That folder is uploaded to Itch.io as a free, unlisted
build.

```bash
make package     # or: ./package.sh
```

## Project Management

Planning, progress tracking, risk analysis, task split and the acceptance
test plan live in [`project_management/`](project_management/). We worked
in short iterations: the engine and the maze adapter first, since every
other module depends on their data model, then the UI, then packaging.
Each feature was reviewed by the other member before being merged.

## Resources

- Pac-Man ghost behaviour, *The Pac-Man Dossier* — https://pacman.holenet.info/
- pygame documentation — https://www.pygame.org/docs/
- PEP 257, docstring conventions — https://peps.python.org/pep-0257/
- mypy documentation — https://mypy.readthedocs.io/
- PyInstaller manual — https://pyinstaller.org/en/stable/
- A-Maze-ing subject and the package assigned to us

### Use of AI

AI was used as a reviewer and a rubber duck, not as an author:

- reviewing our first version against the subject, which is how we found
  the missing CLI argument, the absent comment support in the config
  parser and the HUD offset applied to the player only
- explaining why the levels were not random, which led to the discovery
  that the generator reseeds the global `random` module
- suggesting edge cases for the config and highscore tests

Every suggestion was read, rewritten in our own style and tested before
being kept. Nothing was merged that we could not explain.
