# TypeStorm

A fast-paced typing arcade game for the desktop. Words fall from the sky like
meteors - type them letter by letter to blow them up before they hit the
firewall. Every level the storm gets faster, the words get longer, and the
pressure builds.

Built with pure Python and `tkinter`. No third-party packages needed.

## Play online

**[Play TypeStorm in your browser](https://subhangam-sharma.github.io/Typestorm/)** - no install needed.
Works on desktop with a keyboard, and on phones and tablets (tap the screen to
open the keyboard). A browser version of the game lives in [`index.html`](index.html).

Prefer the desktop version? [Download the ZIP](https://github.com/Subhangam-sharma/Typestorm/archive/refs/heads/main.zip),
extract it and follow the steps under **Run it** below.

<!-- Add a screenshot or GIF here once you have one:
![TypeStorm gameplay](docs/screenshot.png)
-->

## Features

- **Accelerating difficulty** - fall speed grows 20% every level (up to a cap)
  while meteors spawn more often and words get longer
- **Three difficulty modes** - Easy, Normal and Hard, each with its own high score
- **Power words** - `FREEZE` slows time, `BOMB` clears the sky, `+LIFE` heals
- **Boss words** - every 4th level a huge word drops, worth triple points
  (and costs two lives if it lands)
- **Combo system** - every five correct words in a row add +0.5x to your score
- **Swaying meteors** from level 5 onward make targets harder to track
- **Live stats** - accuracy, words per minute, best combo and level reached
- **Persistent high scores** saved per difficulty
- Polished dark UI: gradient sky, glowing word chips with comet trails, rounded
  panels, animated firewall, heart lives and a level progress bar
- Particle explosions, screen shake, parallax starfield and sound effects
  (sound on Windows)

## Requirements

- Python 3.9 or newer
- `tkinter` (included with the standard Python installers for Windows and macOS;
  on Debian/Ubuntu install it with `sudo apt install python3-tk`)

## Run it

```bash
git clone https://github.com/<your-username>/TypeStorm.git
cd TypeStorm
python main.py
```

On Windows you can also double-click `main.py`, or run `py main.py`.
You can start it as a module too: `python -m typestorm`.

## How to play

| Key            | Action                                  |
| -------------- | --------------------------------------- |
| Letters        | Type the word on a meteor               |
| `Enter`        | Start / play again                      |
| `Left` `Right` | Change difficulty on the menu           |
| `Esc`          | Drop the word you are currently typing  |
| `Tab`          | Pause / resume                          |
| `F1`           | Sound on / off                          |

The first letter you type locks onto the matching meteor closest to the
ground. A wrong key resets your combo. Meteors that reach the firewall cost a
life, and you lose when all lives are gone.

### Scoring

```
points = word length x 10 x combo multiplier   (x3 for boss words)
combo multiplier = 1 + 0.5 for every 5 words in a row
```

### Difficulty curve

| Level | Fall speed (px/frame, Normal) |
| ----- | ----------------------------- |
| 1     | 0.60                          |
| 3     | 0.86                          |
| 5     | 1.24                          |
| 8     | 2.15                          |
| 10    | 3.10                          |
| 12    | 4.46                          |

All tuning values live in [`typestorm/rules.py`](typestorm/rules.py).

## Project structure

```
TypeStorm/
├── index.html           # browser version (HTML + JavaScript, no build step)
├── main.py              # desktop entry point
├── typestorm/
│   ├── game.py          # game state, input handling, update loop
│   ├── renderer.py      # all drawing: HUD, word chips, menus, game over screen
│   ├── theme.py         # window size, colour palette, colour helpers
│   ├── rules.py         # speed curve, spawn rate, scoring, stats formulas
│   ├── words.py         # word lists and word selection
│   ├── entities.py      # Meteor, Particle, FloatText data classes
│   ├── storage.py       # high score and lifetime stats (JSON)
│   └── sound.py         # sound effects
└── tests/               # unit tests for the game logic
```

The game logic (`rules`, `words`, `storage`, `theme`) is kept separate from the
GUI so it can be tested without opening a window. All fonts are sized in pixels,
so the layout looks the same on every screen scaling.

## Run the tests

```bash
python -m unittest discover -v
```

## Ideas for the future

- Custom word lists (load your own vocabulary from a text file)
- Online leaderboard
- Themes and skins
- Multiplayer race mode

## License

Released under the [MIT License](LICENSE).
