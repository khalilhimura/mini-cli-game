# mini-cli-game

A small colony management game written in Python. It features a curses based
command line interface, a FastAPI driven HTTP API and an optional 3D web demo
implemented with Node and Three.js.

## Setup

1. **Install Python dependencies**

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **(Optional) Install Node dependencies for the web demo**

   ```bash
   cd web-ui
   npm install
   ```

## Usage

- **Launch the CLI game**
  ```bash
  python main.py
  ```

- **Start the API server**
  ```bash
  uvicorn web_api:app --reload
  ```

- **Run the web demo**
  ```bash
  cd web-ui
  npm start
  ```

- **Run tests**
  ```bash
  pytest
  ```

Additional information about project structure and functionality can be found in
[`docs/overview.md`](docs/overview.md).
