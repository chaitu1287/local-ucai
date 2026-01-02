"""Database configuration and connection management."""

import functools
import os
import sqlalchemy.engine.url
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool
from src.database.models import Base


class Database:
    """Database connection and session management."""

    def __init__(self):
        """Initialize database with environment variables."""
        db_url = os.getenv("DATABASE_URL")

        if not db_url:
            raise ValueError("DATABASE_URL environment variable is required.")

        db_url = sqlalchemy.engine.url.make_url(db_url)

        self.async_url = db_url.set(drivername="postgresql+asyncpg")
        self.async_engine = create_async_engine(
            self.async_url, echo=False, poolclass=NullPool
        )
        self.AsyncSessionLocal = async_sessionmaker(
            self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

    async def async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session with automatic commit/rollback."""
        session = self.AsyncSessionLocal()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def init(self):
        """Initialize the database."""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop(self):
        """Drop the database."""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@functools.lru_cache(maxsize=1)
def get_db() -> Database:
    """Get Database singleton."""
    return Database()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session with automatic commit/rollback."""
    async for session in get_db().async_session():
        yield session
