"""Create a SQLite database for testing with pytest."""

import os

import pytest
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

DATABASE_FILE = "sqlite.db"


@pytest.fixture(scope="function")
def session():
    """Create a new SQLite database, SQLModel tables, and return a session."""
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)
    engine = create_engine(f"sqlite:///{DATABASE_FILE}")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    # Tear down
    SQLModel.metadata.drop_all(engine)
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)


@pytest.fixture(scope="function")
async def async_session():
    """Create an SQLite database, SQLModel tables; return an AsyncSession."""
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)
    engine = create_async_engine(f"sqlite+aiosqlite:///{DATABASE_FILE}")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    async with AsyncSession(engine) as session:
        yield session
    # Tear down
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)
