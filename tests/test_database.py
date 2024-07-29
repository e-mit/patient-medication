"""Tests for the database setup module."""

import os
from unittest.mock import patch
from contextlib import asynccontextmanager

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Database

TEST_DATABASE_FILENAME = "test_database.db"


@asynccontextmanager
async def set_database_url(test_filename: str):
    if os.path.exists(test_filename):
        os.remove(test_filename)
    os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{test_filename}"
    try:
        yield
    finally:
        del os.environ["DATABASE_URL"]
        if os.path.exists(test_filename):
            os.remove(test_filename)


@pytest.mark.asyncio
async def test_get_db():
    with patch('sqlmodel.SQLModel.metadata.create_all'):
        async with set_database_url(TEST_DATABASE_FILENAME):
            await Database.init_db()

    db_gen = Database.get_db()
    # Retrieve the session from the async generator
    session = await db_gen.__anext__()
    assert isinstance(session, AsyncSession)
