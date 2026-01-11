---
name: designing-with-sqlmodel
description: |
  Design and implement type-safe database schemas with SQLModel, combining SQLAlchemy power with Pydantic validation.
  Use when defining database models, designing table relationships, creating API request/response schemas, or connecting to PostgreSQL/SQLite.
  Use when you need a single model definition for both database and API validation.
  NOT when designing complex database migrations (use alembic-migrations skill).
---

# SQLModel Schema Designer

Build type-safe database models that work as both ORM entities and API schemas.

## When to Use This Skill

- "Define Task model for database and API"
- "Create relationships between tables"
- "Design request/response schemas"
- "Set up SQLModel with async database"
- "Add validation to database models"

## Quick Start

```bash
uv add sqlmodel sqlalchemy
```

## Core Concepts

SQLModel combines **SQLAlchemy** (database) + **Pydantic** (validation) = single model.

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# One definition: Database + API schema + Validation
class Task(SQLModel, table=True):  # table=True = database model
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)  # Indexed for fast queries
    description: Optional[str] = None
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Key Pattern: Model Hierarchy

**Don't use a single model for everything.** Use inheritance:

```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# 1. BASE MODEL - shared fields, no table
class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    completed: bool = False

# 2. DATABASE MODEL - has table=True
class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# 3. CREATE MODEL - for POST requests
class TaskCreate(TaskBase):
    pass  # Inherits all base fields

# 4. UPDATE MODEL - all fields optional (PATCH)
class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

# 5. READ MODEL - for responses (matches table schema)
class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
```

**Why this pattern?**
- TaskCreate: Clients POST this (no id, no timestamps)
- TaskUpdate: Clients PATCH this (all optional)
- TaskRead: API returns this (includes id and timestamps)
- Task: Database table (production schema)

## Database Models

### Basic Model

```python
class Task(SQLModel, table=True):
    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)

    # String field with validation
    title: str = Field(
        min_length=1,
        max_length=200,
        index=True,  # Create database index
    )

    # Optional field
    description: Optional[str] = None

    # Boolean field with default
    completed: bool = Field(default=False)

    # Enum field
    status: Literal["pending", "in_progress", "completed"] = "pending"

    # Timestamp with auto-generation
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Relationships (One-to-Many)

```python
from sqlmodel import Relationship

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    # One project has many tasks
    tasks: list["Task"] = Relationship(back_populates="project")

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    # Each task belongs to one project
    project: Optional[Project] = Relationship(back_populates="tasks")
```

### Relationships (Many-to-Many)

```python
class TaskWorkerLink(SQLModel, table=True):
    """Join table for many-to-many relationship."""
    task_id: Optional[int] = Field(default=None, foreign_key="task.id", primary_key=True)
    worker_id: Optional[str] = Field(default=None, foreign_key="worker.id", primary_key=True)

class Worker(SQLModel, table=True):
    id: str = Field(primary_key=True)
    name: str
    # One worker can have many tasks
    tasks: list["Task"] = Relationship(
        back_populates="workers",
        link_model=TaskWorkerLink
    )

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    # One task can have many workers
    workers: list[Worker] = Relationship(
        back_populates="tasks",
        link_model=TaskWorkerLink
    )
```

## Database Connection

### SQLite (Development)

```python
from sqlmodel import create_engine, SQLModel, Session

DATABASE_URL = "sqlite:///database.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True  # Log SQL statements (disable in production)
)

def create_db_and_tables():
    """Create all tables from models."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for injecting database session."""
    with Session(engine) as session:
        yield session
```

### PostgreSQL (Production)

```python
from sqlmodel import create_engine, SQLModel
import os

DATABASE_URL = os.getenv("DATABASE_URL")  # postgresql://user:pass@host/db

engine = create_engine(
    DATABASE_URL,
    echo=False,  # Disable SQL logging in production
    pool_size=20,  # Connection pool size
    max_overflow=40  # Additional connections if pool exhausted
)

async def create_db_and_tables():
    """Async version for Alembic migrations."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

## Validation Patterns

### Field Constraints

```python
from pydantic import field_validator

class Task(SQLModel, table=True):
    title: str = Field(
        min_length=1,       # At least 1 character
        max_length=200,     # Max 200 characters
        regex=r"^[a-zA-Z]"  # Must start with letter
    )

    priority: Literal["low", "medium", "high"] = "medium"  # Enum validation

    progress: int = Field(
        default=0,
        ge=0,   # Greater than or equal to 0
        le=100  # Less than or equal to 100
    )

    # Custom validation
    @field_validator("title")
    @classmethod
    def title_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Title cannot be whitespace only")
        return v.strip()
```

## Instructions

### Step 1: Define Base Model
Create TaskBase with all user-editable fields.

### Step 2: Extend for Database
Create Task(TaskBase, table=True) with id + timestamps.

### Step 3: Create Request Models
Create TaskCreate and TaskUpdate for API.

### Step 4: Create Response Model
Create TaskRead with all fields (including id).

### Step 5: Set Up Database
- Create engine with DATABASE_URL
- Create get_session() dependency
- Call SQLModel.metadata.create_all()

### Step 6: Verify
```bash
python scripts/verify.py
```

## If Verification Fails

1. Run diagnostic: `python scripts/verify.py --verbose`
2. Check: Are models using SQLModel base class?
3. Check: Does Task model have table=True?
4. Check: Are relationships defined with Relationship()?
5. **Stop and report** if issues persist

## Common Patterns

### Soft Deletes (Logical Delete)

```python
from datetime import datetime

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    deleted_at: Optional[datetime] = None  # NULL = not deleted

# Don't delete, set deleted_at instead
task.deleted_at = datetime.utcnow()
session.add(task)
session.commit()

# Query only active tasks
from sqlmodel import select
statement = select(Task).where(Task.deleted_at == None)
results = session.exec(statement).all()
```

### Audit Trail

```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str  # User who created
    updated_by: Optional[str] = None  # User who updated

# Update and track
task.title = "New title"
task.updated_at = datetime.utcnow()
task.updated_by = current_user_id
session.add(task)
session.commit()
```

## References

See detailed patterns in `references/sqlmodel-patterns.md` for:
- Async database connections
- Complex query patterns
- Migration strategies
- Relationship best practices

---

**Learn More**: SQLModel Documentation → https://sqlmodel.tiangolo.com/
