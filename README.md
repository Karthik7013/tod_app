# Todo App (Core + SDK + API + CLI + GUI)

A production-ready, layered Todo application built with Python.

## Structure
- `todo_core.py` → Business logic & SQLite (DO NOT MODIFY)
- `todo_sdk.py` → Serialization, import/export, dict adapter
- `api/` → FastAPI REST server
- `todo_cli.py` → Terminal interface (HTTP client)
- `todo_gui.py` → Desktop GUI (Tkinter, HTTP client)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the API server
python -m uvicorn api.main:app --reload

# In another terminal:
python todo_cli.py add "Learn Python" -d "Master layered architecture"
python todo_cli.py list
python todo_gui.py
```

## API Endpoints

| Method | Path              | Description         |
|--------|-------------------|---------------------|
| GET    | /health           | Health check        |
| GET    | /todos            | List todos          |
| POST   | /todos            | Create todo         |
| POST   | /todos/batch      | Batch create todos  |
| GET    | /todos/{id}       | Get todo by ID      |
| PUT    | /todos/{id}       | Update todo         |
| DELETE | /todos/{id}       | Delete todo         |

## Architecture
- **Core**: Pure business rules + DB access. Zero dependencies.
- **SDK**: Network/serialization ready. Single entry point for all consumers.
- **API**: FastAPI REST layer wrapping the SDK.
- **CLI/GUI**: UI only. Communicate via HTTP. Never touch sqlite3 or validation logic.

## Environment Variables
- `TODO_DB_PATH`: Path to SQLite database (default: `todos.db`)
