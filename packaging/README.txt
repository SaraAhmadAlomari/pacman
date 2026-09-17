Pac-Man
=======

Run
---
  ./pacman config.json

The game needs exactly one argument: a JSON configuration file.
config.json ships next to the executable and can be edited freely;
any invalid value is clamped to a safe default at startup.

Controls
--------
  Arrow keys or WASD   move Pac-Man
  P or ESC             pause
  ENTER                confirm in the menus

Cheat mode (for reviewers)
--------------------------
  I  invincibility
  F  freeze the ghosts
  L  one extra life
  N  skip the current level
  B  double speed

Configuration
-------------
  lives                    lives at the start of a game
  pacgum                   wanted number of pacgums per level
  points_per_pacgum        score for a pacgum
  points_per_super_pacgum  score for a super-pacgum
  points_per_ghost         score for an edible ghost
  points_per_level         bonus for finishing a level
  seed                     seed of the first level
  level_max_time           seconds allowed per level
  super_pacgum_duration    seconds the ghosts stay edible
  ghost_respawn_time       seconds before an eaten ghost returns
  levels                   list of { "width": .., "height": .. }
