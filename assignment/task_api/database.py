import os
from typing import Any, Generator

from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "sqlite:///./tasks.db"
)

# Supabase (and some providers) expose `postgres://` in their dashboard.
# SQLAlchemy 2.x dropped support for this scheme — normalize it here.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args: dict[str, Any]
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}
    engine = create_engine(DATABASE_URL, connect_args=connect_args)
else:
    connect_args = {
        "sslmode": "require",
        "gssencmode": "disable",  # disables GSSAPI, forces plain TCP / IPv4
    }
    # pool_pre_ping=True: SQLAlchemy checks the connection is alive before use.
    # Supabase closes idle connections after ~5 min; without this a stale
    # connection from the pool would cause a 500 on the next request.
    engine = create_engine(
        DATABASE_URL, connect_args=connect_args, pool_pre_ping=True
    )

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session