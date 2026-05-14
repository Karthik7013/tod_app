import os
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from todo_sdk import TodoSDK
from todo_core import TodoNotFoundError, TodoValidationError
from api.models import TodoCreate, TodoUpdate, TodoResponse

app = FastAPI(title="Todo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sdk = TodoSDK(db_path=os.environ.get("TODO_DB_PATH", "todos.db"))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/todos", response_model=list[TodoResponse])
def list_todos(completed: Optional[bool] = Query(None)):
    return [TodoResponse(**t) for t in sdk.list(completed_only=completed)]


@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(data: TodoCreate):
    try:
        return TodoResponse(**sdk.add(data.title, data.description))
    except TodoValidationError as e:
        raise HTTPException(400, str(e))


@app.post("/todos/batch", response_model=list[TodoResponse], status_code=201)
def batch_create_todos(data: list[TodoCreate]):
    results = []
    for item in data:
        try:
            results.append(TodoResponse(**sdk.add(item.title, item.description)))
        except TodoValidationError:
            pass
    return results


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    try:
        return TodoResponse(**sdk.get(todo_id))
    except TodoNotFoundError as e:
        raise HTTPException(404, str(e))


@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, data: TodoUpdate):
    try:
        updates = {k: v for k, v in data.model_dump().items() if v is not None}
        if not updates:
            return TodoResponse(**sdk.get(todo_id))
        return TodoResponse(**sdk.update(todo_id, **updates))
    except TodoNotFoundError as e:
        raise HTTPException(404, str(e))
    except TodoValidationError as e:
        raise HTTPException(400, str(e))


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    try:
        sdk.delete(todo_id)
    except TodoNotFoundError as e:
        raise HTTPException(404, str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
