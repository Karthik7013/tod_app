from pydantic import BaseModel, Field, field_validator
from typing import Optional


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = ""

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    completed: Optional[bool] = None

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    created_at: str
    updated_at: str
