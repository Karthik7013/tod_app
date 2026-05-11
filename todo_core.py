"""
CORE LAYER: Business logic & data access.
This file remains untouched when building SDK, CLI, or GUI.
"""

import sqlite3
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class TodoError(Exception):
    pass
class TodoNotFoundError(TodoError):
    pass
class TodoValidationError(TodoError):
    pass
class TodoDatabaseError(TodoError):
    pass


@dataclass
class Todo:
    id: Optional[int] = None
    title: str = ""
    description: str = ""
    completed: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TodoRepository:
    """Handles SQLite operations. Keeps SQL away from business rules."""
    def __init__(self, db_path: str = "todos.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        try:
            yield conn
            conn.commit()
        except TodoError:
            conn.rollback()
            raise
        except Exception as e:
            conn.rollback()
            raise TodoDatabaseError(f"DB error: {e}") from e
        finally:
            conn.close()

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL CHECK(LENGTH(TRIM(title)) > 0),
                    description TEXT DEFAULT '',
                    completed BOOLEAN NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

    def create(self, todo: Todo) -> Todo:
        now = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            cur = conn.execute(
                "INSERT INTO todos (title, description, completed, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (todo.title, todo.description, todo.completed, now, now)
            )
            todo.id = cur.lastrowid
            todo.created_at = now
            todo.updated_at = now
            return todo

    def get_by_id(self, todo_id: int) -> Todo:
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM todos WHERE id = ?", (todo_id,)).fetchone()
            if not row:
                raise TodoNotFoundError(f"Todo #{todo_id} not found")
            return Todo(**dict(row))

    def get_all(self, completed_only: Optional[bool] = None) -> List[Todo]:
        with self._get_connection() as conn:
            if completed_only is None:
                rows = conn.execute("SELECT * FROM todos ORDER BY created_at DESC").fetchall()
            else:
                rows = conn.execute("SELECT * FROM todos WHERE completed = ? ORDER BY created_at DESC", (completed_only,)).fetchall()
            return [Todo(**dict(r)) for r in rows]

    def update(self, todo_id: int, updates: Dict[str, Any]) -> Todo:
        allowed = {"title", "description", "completed"}
        invalid = set(updates.keys()) - allowed
        if invalid:
            raise TodoValidationError(f"Invalid fields: {invalid}")
        if not updates:
            return self.get_by_id(todo_id)

        now = datetime.now(timezone.utc).isoformat()
        updates["updated_at"] = now
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [todo_id]

        with self._get_connection() as conn:
            cur = conn.execute(f"UPDATE todos SET {set_clause} WHERE id = ?", values)
            if cur.rowcount == 0:
                raise TodoNotFoundError(f"Todo #{todo_id} not found")
            return self.get_by_id(todo_id)

    def delete(self, todo_id: int) -> None:
        with self._get_connection() as conn:
            cur = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
            if cur.rowcount == 0:
                raise TodoNotFoundError(f"Todo #{todo_id} not found")


class TodoAPI:
    """Public business interface. Validates input, delegates to Repository."""
    def __init__(self, db_path: str = "todos.db"):
        self._repo = TodoRepository(db_path)

    def create_todo(self, title: str, description: str = "") -> Todo:
        title = title.strip()
        if not title:
            raise TodoValidationError("Title cannot be empty.")
        return self._repo.create(Todo(title=title, description=description.strip()))

    def get_todo(self, todo_id: int) -> Todo:
        return self._repo.get_by_id(todo_id)
    def list_todos(self, completed_only: Optional[bool] = None) -> List[Todo]:
        return self._repo.get_all(completed_only)
    def update_todo(self, todo_id: int, **kwargs) -> Todo:
        return self._repo.update(todo_id, kwargs)
    def delete_todo(self, todo_id: int) -> None:
        self._repo.delete(todo_id)
