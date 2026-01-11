"""Pytest configuration and shared fixtures."""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from task_api.main import app
from task_api.database import get_session

# Test database
@pytest.fixture(scope="session")
def engine():
    """Create in-memory SQLite test database."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture
def session(engine):
    """Provide test database session with automatic rollback for isolation."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(session):
    """Provide FastAPI test client with mocked database."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_task():
    """Sample task data for testing."""
    return {
        "title": "Test Task",
        "description": "A test task for unit testing",
        "completed": False
    }

@pytest.fixture
def sample_task_completed():
    """Sample completed task for testing."""
    return {
        "title": "Completed Task",
        "description": "A completed task",
        "completed": True
    }
