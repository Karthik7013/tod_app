import os
import tempfile
import pytest
from fastapi.testclient import TestClient

os.environ["TODO_DB_PATH"] = tempfile.mktemp(suffix=".db")

from api.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


class TestCreateTodo:
    def test_create(self):
        resp = client.post("/todos", json={"title": "Test task"})
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Test task"
        assert data["description"] == ""
        assert data["completed"] is False
        assert "id" in data

    def test_create_with_description(self):
        resp = client.post("/todos", json={"title": "With desc", "description": "A description"})
        assert resp.status_code == 201
        assert resp.json()["description"] == "A description"

    def test_create_empty_title(self):
        resp = client.post("/todos", json={"title": ""})
        assert resp.status_code == 422

    def test_create_blank_title(self):
        resp = client.post("/todos", json={"title": "   "})
        assert resp.status_code == 422


class TestListTodos:
    def test_list_all(self):
        client.post("/todos", json={"title": "A"})
        resp = client.get("/todos")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    def test_list_completed(self):
        resp = client.get("/todos", params={"completed": "true"})
        assert resp.status_code == 200
        assert all(t["completed"] for t in resp.json())

    def test_list_pending(self):
        resp = client.get("/todos", params={"completed": "false"})
        assert resp.status_code == 200
        assert all(not t["completed"] for t in resp.json())


class TestGetTodo:
    def test_get(self):
        created = client.post("/todos", json={"title": "To get"}).json()
        resp = client.get(f"/todos/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "To get"

    def test_get_not_found(self):
        resp = client.get("/todos/99999")
        assert resp.status_code == 404


class TestUpdateTodo:
    def test_update_title(self):
        created = client.post("/todos", json={"title": "Old title"}).json()
        resp = client.put(f"/todos/{created['id']}", json={"title": "New title"})
        assert resp.status_code == 200
        assert resp.json()["title"] == "New title"

    def test_update_completed(self):
        created = client.post("/todos", json={"title": "To complete"}).json()
        resp = client.put(f"/todos/{created['id']}", json={"completed": True})
        assert resp.status_code == 200
        assert resp.json()["completed"] is True

    def test_update_not_found(self):
        resp = client.put("/todos/99999", json={"title": "Nope"})
        assert resp.status_code == 404


class TestDeleteTodo:
    def test_delete(self):
        created = client.post("/todos", json={"title": "To delete"}).json()
        resp = client.delete(f"/todos/{created['id']}")
        assert resp.status_code == 204

    def test_delete_not_found(self):
        resp = client.delete("/todos/99999")
        assert resp.status_code == 404


class TestBatchCreate:
    def test_batch(self):
        items = [
            {"title": "Batch 1"},
            {"title": "Batch 2", "description": "Second item"},
        ]
        resp = client.post("/todos/batch", json=items)
        assert resp.status_code == 201
        data = resp.json()
        assert len(data) == 2
        assert data[0]["title"] == "Batch 1"
        assert data[1]["title"] == "Batch 2"

    def test_batch_reject_invalid(self):
        items = [
            {"title": "Valid"},
            {"title": ""},
        ]
        resp = client.post("/todos/batch", json=items)
        assert resp.status_code == 422
