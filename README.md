# Todo App (Core + SDK + CLI + GUI)

A production-ready, layered Todo application built with Python standard library only.

## 📦 Structure
- `todo_core.py` → Business logic & SQLite (DO NOT MODIFY)
- `todo_sdk.py` → Serialization, import/export, dict adapter
- `todo_cli.py` → Terminal interface
- `todo_gui.py` → Desktop GUI (Tkinter)

## 🚀 Quick Start
```bash
cd todo_app
python todo_cli.py add "Learn Python" -d "Master layered architecture"
python todo_cli.py list
python todo_gui.py
```

## 🛡️ Architecture
- **Core**: Pure business rules + DB access. Zero dependencies.
- **SDK**: Network/serialization ready. Single entry point for all consumers.
- **CLI/GUI**: UI only. Never touch `sqlite3` or validation logic.
