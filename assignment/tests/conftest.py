"""Pytest configuration and shared fixtures.

Strategy:
- Each test gets a fresh in-memory SQLite engine (function-scoped).
  This guarantees complete isolation — no rollback tricks, no state leaking
  between tests, and no external services required (CI-safe).
- The FastAPI dependency `get_session` is overridden to inject the test session.
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from task_api.database import get_session
from task_api.main import app


@pytest.fixture(name="engine")
def engine_fixture():
    """Fresh in-memory SQLite engine per test — fully isolated."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="session")
def session_fixture(engine):
    """Database session bound to the test engine."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    """TestClient with the test session injected via dependency override."""

    def _get_session_override():
        return session

    app.dependency_overrides[get_session] = _get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
