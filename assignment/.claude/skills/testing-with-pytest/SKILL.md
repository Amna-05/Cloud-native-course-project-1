---
name: testing-with-pytest
description: |
  Write test-driven pytest suites for FastAPI endpoints and database models with fixtures and mocking.
  Use when writing unit tests, integration tests, mocking dependencies, or testing async FastAPI endpoints.
  Use when you need fixtures, parameterized tests, or testing with databases.
  NOT when testing frontend or JavaScript code (use separate skill).
---

# Pytest Test Suite Builder

Write comprehensive tests for FastAPI APIs using pytest fixtures, mocking, and TDD principles.

## When to Use This Skill

- "Write tests for FastAPI endpoints"
- "Set up pytest fixtures"
- "Test database models"
- "Mock external dependencies"
- "Test async FastAPI endpoints"

## Quick Start

```bash
uv add pytest pytest-asyncio httpx
pytest tests/ -v  # Run all tests
pytest tests/test_tasks.py::test_create_task -v  # Run single test
```

## Core Pattern: Arrange-Act-Assert

Every test follows AAA structure:

```python
def test_create_task(client):
    # ARRANGE - set up test data
    task_data = {"title": "Test Task", "completed": False}

    # ACT - perform action
    response = client.post("/tasks/", json=task_data)

    # ASSERT - verify results
    assert response.status_code == 201
    assert response.json()["title"] == "Test Task"
```

## Project Structure

```
project/
├── task_api/
│   ├── main.py
│   ├── models.py
│   └── database.py
├── tests/
│   ├── conftest.py          ← Fixtures
│   ├── test_models.py       ← Model tests
│   └── test_routes.py       ← Endpoint tests
└── pytest.ini               ← Configuration
```

## conftest.py - Shared Fixtures

**Fixtures** are reusable test setup:

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from task_api.main import app
from task_api.database import get_session

@pytest.fixture(scope="session")
def engine():
    """Create test database."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture
def session(engine):
    """Provide test database session."""
    with Session(engine) as session:
        yield session

@pytest.fixture
def client(session):
    """Provide FastAPI test client with overridden database."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_task():
    """Sample task for testing."""
    return {
        "title": "Test Task",
        "description": "A test task",
        "completed": False
    }
```

## Testing Models (Unit Tests)

```python
# tests/test_models.py
from task_api.models import Task, TaskCreate
from datetime import datetime

def test_task_creation():
    """Test creating a task model."""
    task = Task(
        title="Learn Pytest",
        description="Write tests",
        completed=False
    )
    assert task.title == "Learn Pytest"
    assert task.completed is False

def test_task_from_pydantic(sample_task):
    """Test creating task from Pydantic model."""
    task_create = TaskCreate(**sample_task)
    task = Task.model_validate(task_create)
    assert task.title == sample_task["title"]

def test_task_validation():
    """Test Pydantic validation."""
    # Empty title should fail
    try:
        Task(title="", description=None)
        assert False, "Should have raised validation error"
    except ValueError:
        pass  # Expected
```

## Testing Endpoints (Integration Tests)

```python
# tests/test_routes.py
import pytest

def test_create_task(client, sample_task):
    """Test POST /tasks/"""
    response = client.post("/tasks/", json=sample_task)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == sample_task["title"]
    assert "id" in data

def test_list_tasks(client, sample_task):
    """Test GET /tasks/"""
    # Create a task first
    client.post("/tasks/", json=sample_task)

    # List all tasks
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_get_single_task(client, sample_task):
    """Test GET /tasks/{id}"""
    # Create a task
    create_response = client.post("/tasks/", json=sample_task)
    task_id = create_response.json()["id"]

    # Get the task
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id

def test_get_task_not_found(client):
    """Test GET /tasks/{id} with invalid ID"""
    response = client.get("/tasks/99999")
    assert response.status_code == 404

def test_update_task(client, sample_task):
    """Test PUT /tasks/{id}"""
    # Create a task
    create_response = client.post("/tasks/", json=sample_task)
    task_id = create_response.json()["id"]

    # Update it
    update_data = {"title": "Updated Title", "completed": True}
    response = client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["completed"] is True

def test_delete_task(client, sample_task):
    """Test DELETE /tasks/{id}"""
    # Create a task
    create_response = client.post("/tasks/", json=sample_task)
    task_id = create_response.json()["id"]

    # Delete it
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 404
```

## Parameterized Tests

Test multiple scenarios in one test:

```python
import pytest

@pytest.mark.parametrize("title,should_pass", [
    ("Valid Title", True),
    ("", False),  # Empty
    ("x" * 201, False),  # Too long
    ("123 Numbers", True),
])
def test_task_title_validation(title, should_pass):
    """Test various title inputs."""
    if should_pass:
        task = Task(title=title)
        assert task.title == title
    else:
        with pytest.raises(ValueError):
            Task(title=title)
```

## Mocking Dependencies

```python
from unittest.mock import patch, AsyncMock

def test_create_task_with_mock_email(client, sample_task, mocker):
    """Test endpoint without sending actual email."""
    # Mock the email function
    mocker.patch("task_api.services.send_email", return_value=True)

    response = client.post("/tasks/", json=sample_task)
    assert response.status_code == 201
```

## Instructions

### Step 1: Create conftest.py
Define fixtures for database, client, and sample data.

### Step 2: Write Model Tests
Test Pydantic validation and model creation.

### Step 3: Write Endpoint Tests
Use client fixture to test all CRUD endpoints.

### Step 4: Test Error Cases
Test 404, 400, and other error responses.

### Step 5: Add Mocking
Mock external calls (email, external APIs).

### Step 6: Run Tests
```bash
pytest tests/ -v  # Verbose output
pytest --cov=task_api  # Coverage report
```

## If Verification Fails

1. Run diagnostic: `python scripts/verify.py --verbose`
2. Check: Are conftest.py fixtures defined?
3. Check: Does test_routes.py exist?
4. Check: Do tests use TestClient?
5. **Stop and report** if issues persist

## Common Patterns

### Testing with Database Session

```python
def test_task_persists(session, sample_task):
    """Test task is saved to database."""
    task = Task(**sample_task)
    session.add(task)
    session.commit()

    # Verify it's in database
    retrieved = session.get(Task, task.id)
    assert retrieved.title == sample_task["title"]
```

### Async Tests

```python
import pytest

@pytest.mark.asyncio
async def test_async_endpoint(async_client):
    """Test async FastAPI endpoint."""
    response = await async_client.post("/tasks/", json={...})
    assert response.status_code == 201
```

### Fixture Scopes

```python
@pytest.fixture(scope="session")
def test_db_engine():
    """Single engine for entire test session."""
    return create_engine("sqlite://")

@pytest.fixture(scope="function")
def clean_session(test_db_engine):
    """Fresh session for each test."""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()
```

### Testing Pagination

```python
def test_pagination(client, sample_task):
    """Test paginated responses."""
    # Create 25 tasks
    for i in range(25):
        client.post("/tasks/", json={
            "title": f"Task {i}",
            "completed": False
        })

    # Test first page
    response = client.get("/tasks/?skip=0&limit=10")
    assert len(response.json()) == 10

    # Test second page
    response = client.get("/tasks/?skip=10&limit=10")
    assert len(response.json()) == 10
```

## References

See detailed patterns in `references/pytest-patterns.md` for:
- Mocking strategies
- Async testing
- Fixtures with parameters
- Coverage reporting

---

**Learn More**: Pytest Documentation → https://docs.pytest.org/
