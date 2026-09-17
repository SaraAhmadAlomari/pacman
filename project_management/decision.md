# Project Decisions

## Team Division

The project was divided into two main parts:

* Backend and game logic
* Frontend, rendering and input

This allowed both team members to work on their parts in parallel.

## Shared Game State

A shared game state was used to connect the backend with the frontend.

The backend updates the game state, while the frontend uses it for rendering and UI.

## External Maze Generator

The provided external maze generator was used for maze generation and integrated through `maze_loader.py`.

## Integration

After implementing the separate parts, the frontend and backend were connected and tested together.
