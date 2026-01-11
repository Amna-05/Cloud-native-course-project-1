"""Database and API models using SQLModel."""
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from pydantic import field_validator

# BASE MODEL - shared fields
class TaskBase(SQLModel):
    """Base task fields shared across models."""
    title: str = Field(min_length=1, max_length=200, index=True)
    description: Optional[str] = None
    completed: bool = Field(default=False)

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v):
        """Ensure title is not just whitespace."""
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()

# DATABASE MODEL - table=True
class Task(TaskBase, table=True):
    """Task database model."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# CREATE MODEL - for POST requests
class TaskCreate(TaskBase):
    """Model for creating tasks (POST)."""
    pass

# UPDATE MODEL - all fields optional
class TaskUpdate(SQLModel):
    """Model for updating tasks (PUT/PATCH)."""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# READ MODEL - for responses
class TaskRead(TaskBase):
    """Model for reading tasks (GET responses)."""
    id: int
    created_at: datetime
    updated_at: datetime
