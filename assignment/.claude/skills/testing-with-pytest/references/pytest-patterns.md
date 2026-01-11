# Pytest Advanced Patterns

Deep-dive patterns for sophisticated testing strategies.

## Mocking Strategies

### Mock External API Calls

```python
from unittest.mock import patch, AsyncMock

def test_external_api(client, mocker):
    """Mock external API without making real requests."""
    mock_response = {"id": 123, "status": "success"}

    with patch("task_api.services.external_api", return_value=mock_response):
        response = client.post("/tasks/sync", json={})
        assert response.status_code == 200
```

### Mock Database Queries

```python
from unittest.mock import MagicMock

def test_task_service(mocker):
    """Mock database repository."""
    mock_repo = MagicMock()
    mock_repo.create.return_value = Task(id=1, title="Mocked Task")

    # Use mocked repository
    service = TaskService(repo=mock_repo)
    result = service.create(TaskCreate(title="Test"))

    assert result.id == 1
    mock_repo.create.assert_called_once()
```

## Fixtures with Parameters

```python
@pytest.fixture(params=["sqlite", "postgres"])
def database(request):
    """Run tests against multiple databases."""
    if request.param == "sqlite":
        return create_engine("sqlite://")
    else:
        return create_engine("postgresql://...")

# test_multiple_dbs.py uses multiple databases
def test_task_creation(database):
    """This test runs twice: once for SQLite, once for PostgreSQL."""
    session = Session(database)
    task = Task(title="Test")
    session.add(task)
    session.commit()
    assert task.id is not None
```

## Coverage Reporting

```bash
# Install coverage
uv add pytest-cov

# Generate coverage report
pytest --cov=task_api --cov-report=html

# View report
open htmlcov/index.html

# Enforce minimum coverage
pytest --cov=task_api --cov-fail-under=80
```

## Markers (Skip, Expected Failures, Slow)

```python
import pytest

@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.xfail(reason="Known issue with database")
def test_known_bug():
    assert False  # Expected to fail

@pytest.mark.slow
def test_slow_operation():
    time.sleep(5)

# Run only fast tests
pytest -m "not slow"

# Run only xfail tests
pytest -m xfail
```

## Async Testing

```python
import pytest
from httpx import AsyncClient

@pytest.fixture
async def async_client():
    """Test client for async FastAPI app."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_async_endpoint(async_client):
    """Test async endpoint."""
    response = await async_client.post("/tasks/", json={...})
    assert response.status_code == 201
```

## Dependency Injection in Tests

```python
from dependency_injector import containers, providers

class DIContainer(containers.DeclarativeContainer):
    task_repo = providers.Singleton(TaskRepository)
    task_service = providers.Factory(TaskService, repo=task_repo)

def test_with_di():
    """Test with dependency injection."""
    service = DIContainer.task_service()
    result = service.create(TaskCreate(title="Test"))
    assert result.title == "Test"
```

## Fixture Scope Control

| Scope | Created | Destroyed |
|-------|---------|-----------|
| function | Per test | After test |
| class | Per class | After all tests in class |
| module | Per module | After all tests in module |
| session | Once | At end of session |

```python
@pytest.fixture(scope="session")
def database_engine():
    """Created once per test session."""
    return create_engine("sqlite://")

@pytest.fixture(scope="function")
def session(database_engine):
    """Created per test function."""
    with Session(database_engine) as session:
        yield session
```

## Debugging Tests

```bash
# Run with print statements
pytest -s

# Run with pdb debugger
pytest --pdb

# Run single test with verbose output
pytest tests/test_tasks.py::test_create_task -vv

# Show local variables
pytest -l

# Stop on first failure
pytest -x

# Run last failed test
pytest --lf
```

---

**See Also**: building-fastapi-apis and designing-with-sqlmodel skills for the code being tested.
