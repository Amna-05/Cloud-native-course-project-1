# FastAPI Advanced Patterns

Deep-dive patterns for production FastAPI applications.

## JWT Authentication

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx

security = HTTPBearer()

async def verify_token(token: str) -> dict:
    """Verify JWT and return payload."""
    try:
        payload = jwt.decode(
            token,
            "your-secret-key",
            algorithms=["HS256"]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Extract current user from JWT."""
    token = credentials.credentials
    return await verify_token(token)

# Usage in endpoints
@app.post("/tasks")
async def create_task(
    task: TaskCreate,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    # current_user is automatically verified
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()
    return db_task
```

## Async Endpoints

```python
import asyncio
from sqlmodel.ext.asyncio.session import AsyncSession

@app.post("/tasks", response_model=TaskRead)
async def create_task(
    task: TaskCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """Async endpoint for concurrent request handling."""
    db_task = Task.model_validate(task)
    session.add(db_task)
    await session.commit()
    await session.refresh(db_task)
    return db_task

@app.get("/tasks")
async def list_tasks(
    session: AsyncSession = Depends(get_async_session)
):
    """Query with async session."""
    statement = select(Task)
    results = await session.exec(statement)
    return results.all()
```

## Background Tasks

```python
from fastapi import BackgroundTasks
import time

def send_email(email: str, message: str):
    """Background task - runs after response is sent."""
    time.sleep(1)  # Simulate email sending
    print(f"Email sent to {email}: {message}")

@app.post("/tasks")
async def create_task_with_notification(
    task: TaskCreate,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    db_task = Task.model_validate(task)
    session.add(db_task)
    session.commit()

    # Add background task
    background_tasks.add_task(
        send_email,
        email="admin@example.com",
        message=f"New task created: {task.title}"
    )

    return db_task
```

## Custom Middleware

```python
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import uuid
import time

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.time()
        response = await call_next(request)

        process_time = time.time() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)

        return response

# Add to app
app.add_middleware(RequestIDMiddleware)
```

## Streaming Responses

```python
from fastapi.responses import StreamingResponse
import asyncio

async def generate_tasks():
    """Generator for streaming responses."""
    for i in range(100):
        task_data = f'{{"id": {i}, "title": "Task {i}"}}\n'
        yield task_data
        await asyncio.sleep(0.1)

@app.get("/tasks/stream")
async def stream_tasks():
    return StreamingResponse(
        generate_tasks(),
        media_type="application/x-ndjson"
    )
```

## Database Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

# Production: Use connection pooling
engine = create_engine(
    "postgresql://user:pass@host/db",
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,  # Verify connections before use
    echo=False
)

# Test: Use in-memory SQLite
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False}
)
```

## Status Code Reference

| Code | Use Case |
|------|----------|
| 200 | GET successful, no content change |
| 201 | POST successful, resource created |
| 204 | DELETE successful, no content in response |
| 400 | Bad request, validation error |
| 401 | Unauthorized, invalid token |
| 403 | Forbidden, insufficient permissions |
| 404 | Not found |
| 409 | Conflict (e.g., duplicate) |
| 422 | Unprocessable entity (Pydantic validation) |
| 500 | Server error |
| 503 | Service unavailable |

## Common Gotchas

### 1. Returning raw SQLModel objects after commit

After `session.commit()`, the object becomes detached. Always refresh:

```python
session.add(db_task)
session.commit()
session.refresh(db_task)  # Refresh before returning
return db_task
```

### 2. Forgetting response_model

Always specify response model for type safety and validation:

```python
# Good
@app.post("/tasks", response_model=TaskRead)
def create_task(...): pass

# Bad (no validation of response)
@app.post("/tasks")
def create_task(...): pass
```

### 3. Not using status_code

Match HTTP status codes to operation:

```python
# Good
@app.post("/tasks", status_code=201)
def create_task(...): pass

# Bad (200 OK for create looks wrong)
@app.post("/tasks")
def create_task(...): pass
```

---

**See Also**: testing-with-pytest skill for how to test these endpoints.
