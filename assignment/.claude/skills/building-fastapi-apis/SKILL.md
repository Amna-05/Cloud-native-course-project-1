---
name: building-fastapi-apis
description: |
  Build production-grade REST APIs with FastAPI, including request validation, CRUD endpoints, error handling, and middleware.
  Use when creating FastAPI applications, designing REST endpoints, implementing validation, or configuring middleware/CORS.
  Use when you need concurrent request handling, automatic API documentation (Swagger), or dependency injection patterns.
  NOT when building GraphQL or async streaming endpoints (separate skills).
---

# FastAPI API Builder

Build fast, type-safe REST APIs with automatic validation, documentation, and async support.

## When to Use This Skill

- "Build FastAPI endpoints for Task Management"
- "Create REST API with request validation"
- "Set up CORS and middleware"
- "Implement dependency injection for database sessions"
- "Design request/response models"

## Quick Start

```bash
uv add fastapi uvicorn sqlmodel pydantic
uv run uvicorn main:app --reload --port 8000
# Visit http://localhost:8000/docs for auto-generated Swagger UI
```

## Core Patterns

### 1. FastAPI App Structure

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

app = FastAPI(
    title="Task Management API",
    description="CRUD operations for tasks",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

### 2. Request/Response Models (Pydantic)

Models use type hints for automatic validation:

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Request model (POST body)
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    completed: bool = False

# Response model (API response)
class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    created_at: datetime
```

**Key pattern**: Separate models for requests (TaskCreate) vs responses (TaskRead).

### 3. CRUD Endpoints

```python
# CREATE
@app.post("/tasks", response_model=TaskRead, status_code=201)
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

# READ (list)
@app.get("/tasks", response_model=list[TaskRead])
def list_tasks(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 10
):
    tasks = session.query(Task).offset(skip).limit(limit).all()
    return tasks

# READ (single)
@app.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

# UPDATE
@app.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_update: TaskCreate,
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# DELETE
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    session.delete(task)
    session.commit()
    return None
```

### 4. Error Handling

```python
from fastapi import HTTPException
from fastapi.responses import JSONResponse

# HTTPException (built-in)
@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    if task_id < 1:
        raise HTTPException(
            status_code=400,
            detail="Invalid task ID"
        )

# Custom exception handler
class TaskNotFound(Exception):
    def __init__(self, task_id: int):
        self.task_id = task_id

@app.exception_handler(TaskNotFound)
async def task_not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {exc.task_id} not found"}
    )
```

### 5. Dependency Injection

**Database session dependency:**

```python
from sqlmodel import Session, create_engine

DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def get_session():
    with Session(engine) as session:
        yield session
```

**Usage in endpoints:**

```python
@app.post("/tasks")
def create_task(task: TaskCreate, session: Session = Depends(get_session)):
    # session is automatically injected
    pass
```

### 6. Query Parameters & Validation

```python
from fastapi import Query

@app.get("/tasks")
def list_tasks(
    session: Session = Depends(get_session),
    skip: int = Query(0, ge=0),  # ≥ 0
    limit: int = Query(10, gt=0, le=100),  # 1-100
    completed: bool = Query(None),  # Optional filter
    title: str = Query(None, min_length=1)  # Optional text search
):
    query = session.query(Task)

    if completed is not None:
        query = query.filter(Task.completed == completed)

    if title:
        query = query.filter(Task.title.contains(title))

    return query.offset(skip).limit(limit).all()
```

## Instructions

### Step 1: Define Models
- Create request models (e.g., TaskCreate)
- Create response models (e.g., TaskRead)
- Use Pydantic Field() for validation

### Step 2: Create Database Dependency
- Set up database engine
- Create get_session() dependency function
- Return Session objects

### Step 3: Build CRUD Endpoints
- POST /items/ → Create
- GET /items/ → List (with pagination)
- GET /items/{id} → Get single
- PUT /items/{id} → Update
- DELETE /items/{id} → Delete

### Step 4: Add Error Handling
- Use HTTPException for known errors
- Return appropriate status codes (201, 400, 404, 500)
- Include error messages in response

### Step 5: Configure Middleware
- Add CORS if needed
- Add logging middleware
- Add request ID tracking

### Step 6: Verify
```bash
python scripts/verify.py
```

## If Verification Fails

1. Run diagnostic: `python scripts/verify.py --verbose`
2. Check: Are all endpoints type-hinted?
3. Check: Does SKILL.md import syntax work?
4. Check: Are models defined with Pydantic?
5. **Stop and report** if issues persist

## Common Patterns

### Pagination

```python
@app.get("/tasks")
def list_tasks(
    session: Session = Depends(get_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    skip = (page - 1) * page_size
    total = session.query(Task).count()
    items = session.query(Task).offset(skip).limit(page_size).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    }
```

### Filtering

```python
@app.get("/tasks")
def list_tasks(
    session: Session = Depends(get_session),
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None)
):
    query = session.query(Task)

    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)

    return query.all()
```

## References

See detailed patterns in `references/fastapi-patterns.md` for:
- JWT authentication
- Async endpoints
- Streaming responses
- Background tasks
- Custom middleware

---

**Learn More**: FastAPI Documentation → https://fastapi.tiangolo.com/
