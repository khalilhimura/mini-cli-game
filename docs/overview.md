# Project Overview

`mini-cli-game` is a simple colony management simulation. The main interface runs in
the terminal using `curses` and allows you to construct buildings, gather
resources and research new technologies. A minimal API powered by FastAPI and a
proof-of-concept web interface are also included.

## Features

- **Turn-based resource generation** handled in `game.py`.
- **Buildings and upgrades** defined in `buildings.py`.
- **Random events** implemented in `events.py`.
- **Research system** defined in `research.py`.
- **Command line interface** in `main.py` for interactive play.
- **HTTP API** served by `web_api.py` to integrate with external clients.
- **Three.js web demo** found in [`web-ui/`](../web-ui) for basic 3D visuals.

## Running the CLI Game

```bash
python main.py
```

This launches the terminal UI where you can manage the colony turn by turn.

## Running the API

```bash
uvicorn web_api:app --reload
```

Requests can then be made to `http://localhost:8000` to query or manipulate the
current game state.

## Running the Web UI

Install Node dependencies in the `web-ui` folder and start the server:

```bash
cd web-ui
npm install
npm start
```

The demo will be available at `http://localhost:3000`.

## Running Tests

All automated tests use `pytest` and can be run from the project root:

```bash
pytest
```
