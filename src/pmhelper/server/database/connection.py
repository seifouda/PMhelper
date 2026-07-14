"""
Database Connection and Session Management

Supports both PostgreSQL (production) and SQLite (local development).
"""

from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from .models import Base
from ..config import config


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self):
        self.engine = None
        self.async_session_maker = None
        self._initialized = False
        self._is_postgresql = False

    async def initialize(self):
        """Initialize the database engine and create tables."""
        if self._initialized:
            return

        db_url = config.get_database_url()
        self._is_postgresql = db_url.startswith("postgresql")

        # PostgreSQL configuration (Render.com production)
        if self._is_postgresql:
            self.engine = create_async_engine(
                db_url,
                echo=config.DEBUG,
                pool_pre_ping=True,
                pool_size=5,              # Connection pool for PostgreSQL
                max_overflow=10,
                pool_recycle=3600,
                connect_args={
                    "server_settings": {
                        "application_name": "pmhelper"
                    }
                }
            )

        # SQLite configuration (local development)
        else:
            self.engine = create_async_engine(
                db_url,
                echo=config.DEBUG,
                poolclass=StaticPool,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={
                    "check_same_thread": False,
                    "timeout": 30,
                }
            )

        # Create session maker with optimized settings
        self.async_session_maker = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )

        # Create all tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        self._initialized = True

    async def close(self):
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            self._initialized = False

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get an async database session."""
        if not self._initialized:
            await self.initialize()

        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def get_session_dependency(
            self) -> AsyncGenerator[AsyncSession, None]:
        """FastAPI dependency for database sessions."""
        async with self.get_session() as session:
            yield session


# Global database manager instance
db_manager = DatabaseManager()


# FastAPI dependency
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency to get database session."""
    async with db_manager.get_session() as session:
        yield session


# Convenience functions for application lifecycle
async def init_database():
    """Initialize database on startup."""
    await db_manager.initialize()


async def close_database():
    """Close database on shutdown."""
    await db_manager.close()


__all__ = [
    "DatabaseManager",
    "db_manager",
    "get_db_session",
    "init_database",
    "close_database"]
