# Team Organization

## Team

The project was developed by two team members:

* **saalomar — Person B**
* **gmagable — Person A**

## Person A — Backend

Person A was responsible for:

* Config loader — `config.py`
* Maze generator integration — `maze_loader.py`
* Highscore system — `highscore.py`
* Core game logic — `game_state.py`
* Ghost AI — `ghost_ai.py`
* Cheat logic — `cheat.py`
* Testing and tooling

## Person B — Frontend / UI

Person B was responsible for:

* Graphics setup
* Maze and entity rendering — `renderer.py`
* Input handling
* Main menu — `main_menu.py`
* In-game HUD — `hud.py`
* Pause menu — `pause_menu.py`
* Game Over / Victory screens — `game_over.py`
* General frontend/UI work
* Connecting the frontend with the backend

## Collaboration

The two team members worked on their assigned parts and then integrated them together.

The shared game structure and interfaces were used to connect the backend game state with the frontend and rendering components.
