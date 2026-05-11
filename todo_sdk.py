"""
SDK LAYER: Adapter for external consumers.
Handles serialization, configuration, batch operations, and network-ready dicts.
"""

import json
from typing import List, Dict, Any, Optional
from todo_core import TodoAPI, TodoError, TodoValidationError, TodoNotFoundError

class TodoSDK:
    def __init__(self, db_path: str = "todos.db"):
        self.api = TodoAPI(db_path)

    def add(self, title: str, description: str = "") -> Dict[str, Any]:
        return self.api.create_todo(title, description).to_dict()

    def get(self, todo_id: int) -> Dict[str, Any]:
        return self.api.get_todo(todo_id).to_dict()

    def list(self, completed_only: Optional[bool] = None) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self.api.list_todos(completed_only)]

    def update(self, todo_id: int, **kwargs) -> Dict[str, Any]:
        return self.api.update_todo(todo_id, **kwargs).to_dict()

    def delete(self, todo_id: int) -> bool:
        self.api.delete_todo(todo_id)
        return True

    def export_json(self, filepath: str) -> None:
        with open(filepath, "w") as f:
            json.dump(self.list(), f, indent=2)

    def import_json(self, filepath: str) -> List[Dict[str, Any]]:
        with open(filepath, "r") as f:
            data = json.load(f)
        imported = []
        for item in data:
            try:
                t = self.add(item["title"], item.get("description", ""))
                if item.get("completed"):
                    self.update(t["id"], completed=True)
                imported.append(t)
            except Exception as e:
                print(f"⚠️ Skip import for '{item.get('title', '')}': {e}")
        return imported
