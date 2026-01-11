"""FastAPI Task Management API - Main application."""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from datetime import datetime
from contextlib import asynccontextmanager

from task_api.database import create_db_and_tables, engine, get_session
from task_api.models import Task, TaskCreate, TaskRead, TaskUpdate

# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    create_db_and_tables()
    yield
    # Cleanup on shutdown if needed

# Create FastAPI app with lifespan
app = FastAPI(
    title="Task Management API",
    description="Simple CRUD API for managing tasks",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}

# ==================== CREATE ====================
@app.post("/tasks/", response_model=TaskRead, status_code=201)
def create_task(
    task: TaskCreate,
    session: Session = Depends(get_session)
):
    """Create a new task."""
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

# ==================== READ (LIST) ====================
@app.get("/tasks/", response_model=list[TaskRead])
def list_tasks(
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 10,
    completed: bool = None
):
    """List all tasks with optional filtering."""
    query = select(Task)

    if completed is not None:
        query = query.where(Task.completed == completed)

    query = query.offset(skip).limit(limit)
    tasks = session.exec(query).all()
    return tasks

# ==================== READ (SINGLE) ====================
@app.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    session: Session = Depends(get_session)
):
    """Get a single task by ID."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task

# ==================== UPDATE ====================
@app.put("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    session: Session = Depends(get_session)
):
    """Update a task."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    # Update only provided fields
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.utcnow()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

# ==================== DELETE ====================
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    session: Session = Depends(get_session)
):
    """Delete a task."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    session.delete(task)
    session.commit()
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("task_api.main:app", host="0.0.0.0", port=8000, reload=True)
