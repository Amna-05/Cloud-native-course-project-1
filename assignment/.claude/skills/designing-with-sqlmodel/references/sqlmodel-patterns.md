# SQLModel Advanced Patterns

Deep-dive patterns for complex database schemas.

## Async Database Connections

```python
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL")

# Convert sync URL to async
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+asyncpg://",
        1
    )

async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10
)

async def create_db_and_tables():
    """Create all tables asynchronously."""
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_async_session() -> AsyncSession:
    """Async session dependency for FastAPI."""
    async with AsyncSession(async_engine) as session:
        yield session
```

## Complex Query Patterns

```python
from sqlmodel import select, or_, and_
from sqlalchemy.orm import selectinload

# Basic where clause
statement = select(Task).where(Task.status == "pending")

# Multiple conditions (AND)
statement = select(Task).where(
    Task.status == "pending",
    Task.priority == "high"
)

# OR conditions
statement = select(Task).where(
    or_(Task.status == "pending", Task.status == "in_progress")
)

# AND + OR combined
statement = select(Task).where(
    and_(
        Task.completed == False,
        or_(Task.priority == "high", Task.priority == "critical")
    )
)

# Ordering and pagination
statement = (
    select(Task)
    .order_by(Task.created_at.desc())
    .offset(20)
    .limit(10)
)

# Eager load relationships (prevent N+1 queries)
statement = select(Task).options(selectinload(Task.project))
results = await session.exec(statement)

# Count
statement = select(func.count(Task.id))
total = await session.scalar(statement)
```

## Lazy vs Eager Loading

### Problem: N+1 Query

```python
# BAD - causes N+1 queries
tasks = await session.exec(select(Task))
for task in tasks:
    print(task.project.name)  # N+1 queries!
```

### Solution: Eager Load

```python
from sqlalchemy.orm import selectinload

# GOOD - single query with join
statement = select(Task).options(selectinload(Task.project))
tasks = await session.exec(statement)
for task in tasks:
    print(task.project.name)  # No extra queries!
```

## Indexes for Performance

```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Simple index
    title: str = Field(index=True)

    # Composite index
    status: str = Field(index=True)
    created_at: datetime = Field(index=True)

    # Unique constraint
    email: str = Field(unique=True)
```

## Soft Deletes

Instead of DELETE, mark as deleted:

```python
from datetime import datetime
from sqlmodel import select

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    deleted_at: Optional[datetime] = None

# Soft delete
task.deleted_at = datetime.utcnow()
session.add(task)
session.commit()

# Query only active records
statement = select(Task).where(Task.deleted_at == None)
active_tasks = await session.exec(statement)
```

## Audit Logging

Track who changed what and when:

```python
from datetime import datetime

class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    entity_type: str  # "Task", "Project", etc
    entity_id: int    # Which record
    action: str       # "created", "updated", "deleted"
    changed_by: str   # User ID
    changed_at: datetime = Field(default_factory=datetime.utcnow)
    old_value: Optional[dict] = None
    new_value: Optional[dict] = None

def log_change(
    session: Session,
    entity_type: str,
    entity_id: int,
    action: str,
    changed_by: str,
    old_value: dict = None,
    new_value: dict = None
):
    """Log an audit event."""
    log = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        changed_by=changed_by,
        old_value=old_value,
        new_value=new_value
    )
    session.add(log)
    session.commit()
```

## Polymorphic Models

Handle different entity types in one table:

```python
from sqlalchemy import Column, String

class Entity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str = Field(discriminator="type")
    name: str

class Task(Entity, table=False):
    type: str = "task"
    priority: str = "medium"

class Project(Entity, table=False):
    type: str = "project"
    deadline: Optional[datetime] = None
```

## Bulk Operations

For performance with many records:

```python
from sqlalchemy import update, delete

# Bulk update
statement = (
    update(Task)
    .where(Task.status == "pending")
    .values(status="in_progress")
)
await session.execute(statement)
await session.commit()

# Bulk delete
statement = delete(Task).where(Task.completed == True)
await session.execute(statement)
await session.commit()
```

---

**See Also**: building-fastapi-apis skill for how to use these models in endpoints.
