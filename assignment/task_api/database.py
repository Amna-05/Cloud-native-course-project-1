"""Database configuration and session management."""
from sqlmodel import SQLModel, create_engine, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///tasks.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency for injecting database session."""
    with Session(engine) as session:
        yield session
