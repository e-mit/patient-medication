"""Set up the database engine and session."""

import os
from typing import Annotated, AsyncGenerator, Any

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy import event
from sqlmodel import SQLModel
from fastapi import Depends

# Examples:
#
# DATABASE_URL = (f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
#                 f"{POSTGRES_HOST_AND_PORT}/{POSTGRES_DB}")
# or
# DATABASE_URL = f"sqlite+aiosqlite:///{SQLITE_FILE}"
# database_url = os.environ["DATABASE_URL"]


class Database:
    """Non-instantiable class for database connection management."""

    def __init__(self):
        raise RuntimeError("This class cannot be instantiated")

    @classmethod
    async def init_db(cls):
        """Create all database tables."""
        database_url = os.environ["DATABASE_URL"]
        database_echo = bool(os.environ.get("DATABASE_ECHO", 1))
        cls.engine = create_async_engine(database_url,
                                         echo=database_echo)
        cls._setup_event_listeners()
        cls.async_sessionmaker = async_sessionmaker(
            bind=cls.engine,
            expire_on_commit=False,
            autocommit=False
        )

    @classmethod
    async def create_all(cls):
        """Call SQLModel to create the database tables."""
        async with cls.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    @classmethod
    def _setup_event_listeners(cls):
        @event.listens_for(cls.engine.sync_engine, "connect")
        def _enable_foreign_keys(connection, _connection_record):
            """Make SQLite enforce foreign keys; ignored for PostgreSQL."""
            try:
                connection.execute("PRAGMA foreign_keys=ON")
            except Exception:  # pylint: disable=W0718
                print("Foreign key constraint enabling not applicable")

    @classmethod
    async def get_db(cls) -> AsyncGenerator[AsyncSession, Any]:
        """Create a new context-managed database session."""
        async with cls.async_sessionmaker() as session:  # type: ignore
            yield session


DbDependency = Annotated[AsyncSession, Depends(Database.get_db)]
