# Acceptance Test Plan

## Testing Method

The game was tested manually by running the complete application and checking most of the main game cases and features.

## Tested Areas

| Area                           | Test Method                                        | Result |
| ------------------------------ | -------------------------------------------------- | ------ |
| Game launch                    | Run the game with the configuration file           | Pass   |
| Main menu                      | Manual interaction with menu options               | Pass   |
| Game rendering                 | Run the game and check the displayed game elements | Pass   |
| Player input                   | Test movement and controls                         | Pass   |
| Game states                    | Test normal game flow and end states               | Pass   |
| UI elements                    | Check HUD, menus and game screens                  | Pass   |
| Backend / frontend integration | Run the complete game together                     | Pass   |
| Configuration                  | Run the game using the configuration file          | Pass   |
| Packaging                      | Build and test the Linux package                   | Pass   |

## Issue Found

### Maze Generator Integration

During integration, there was a problem connecting the external maze generator with the game code.

The issue was investigated during integration and the maze generator was successfully connected to the game.

## Final Result

The game was manually tested as an integrated application, and the main game cases were checked before the final delivery.
