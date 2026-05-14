from fastapi import FastAPI, HTTPException, Query
from typing import Optional

from todo_core import TodoAPI, TodoNotFoundError, TodoValidationError
from api.models import TodoCreate, TodoUpdate, TodoResponse


app = FastAPI(title="Todo API", version="1.0.0")

api = TodoAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/todos", response_model=list[TodoResponse])
def list_todos(completed: Optional[bool] = Query(None)):
    todos = api.list_todos(completed_only=completed)
    return [TodoResponse(**t.to_dict()) for t in todos]


@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(data: TodoCreate):
    try:
        todo = api.create_todo(data.title, data.description)
        return TodoResponse(**todo.to_dict())
    except TodoValidationError as e:
        raise HTTPException(400, str(e))


@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    try:
        todo = api.get_todo(todo_id)
        return TodoResponse(**todo.to_dict())
    except TodoNotFoundError as e:
        raise HTTPException(404, str(e))


@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, data: TodoUpdate):
    try:
        updates = {k: v for k, v in data.model_dump().items() if v is not None}
        if not updates:
            return api.get_todo(todo_id)
        todo = api.update_todo(todo_id, **updates)
        return TodoResponse(**todo.to_dict())
    except TodoNotFoundError as e:
        raise HTTPException(404, str(e))
    except TodoValidationError as e:
        raise HTTPException(400, str(e))


@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    try:
        api.delete_todo(todo_id)
    except TodoNotFoundError as e:
        raise HTTPException(404, str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)