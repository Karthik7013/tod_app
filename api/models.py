from pydantic import BaseModel, Field
from typing import Optional


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, strip_whitespace=True)
    description: str = ""


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, strip_whitespace=True)
    description: Optional[str] = None
    completed: Optional[bool] = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at: str
    updated_at: str