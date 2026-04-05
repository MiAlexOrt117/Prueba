# Project Guidelines

## Code Style
- Follow existing Python style in this repository: clear class-based modules, `snake_case` methods/functions, and concise docstrings in Spanish where already used.
- Keep module responsibilities separated as they are today: UI logic in `ui.py`, synchronization and thread behavior in simulation/philosopher modules, shared constants and data types in `utils.py`.
- Prefer standard library solutions first. This project intentionally has no external Python dependencies.

## Architecture
- The app has two simulation modes exposed through `main.py`:
  - Naive mode in `simulation_naive.py` (deadlock-prone by design for demonstration).
  - Corrected mode in `simulation_corrected.py` (monitor + FIFO queue to avoid deadlock/starvation).
- Core concurrency entities:
  - `Fork` in `fork.py` wraps lock-based fork ownership.
  - Philosopher thread implementations live in `philosopher.py`.
  - Shared enums/constants/statistics/events are in `utils.py`.
- UI and rendering are Tkinter-based in `ui.py`; avoid coupling UI state updates directly to synchronization internals.
- For deeper details, link to existing docs instead of duplicating:
  - `ARQUITECTURA.md`
  - `README_PHILOSOPHERS.md`

## Build and Test
- Environment checks:
  - `python --version` (Python 3.6+)
  - `python -m tkinter` (Tkinter available)
  - Optional: `python check_install.py`
- Run app:
  - `python main.py` (primary entry point)
  - `python run.py` (wrapper script)
- Run logic verification script:
  - `python test_simulation.py`

## Conventions
- Preserve educational intent:
  - Naive mode must remain capable of reaching deadlock.
  - Corrected mode must preserve deadlock avoidance and fairness behavior.
- Keep philosopher and fork counts consistent with `NUM_PHILOSOPHERS` from `utils.py` unless a task explicitly changes simulation scale.
- When changing concurrency behavior, avoid introducing blocking/UI operations that can freeze Tkinter mainloop.
- Keep terminology and state names consistent with the existing Spanish labels used in enums/UI.

## Key References
- Quick usage guide: `GUIA_RAPIDA.md`
- Architecture and module boundaries: `ARQUITECTURA.md`
- Full problem and algorithm explanation: `README_PHILOSOPHERS.md`
- Project file map: `INDICE.md`