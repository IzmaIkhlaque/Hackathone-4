import asyncpg
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.core.config import settings

# Global connection pool — created on startup, closed on shutdown
_pool: asyncpg.Pool | None = None


async def create_pool() -> asyncpg.Pool:
    """Create the asyncpg connection pool to Neon PostgreSQL."""
    # Neon requires SSL; asyncpg uses ssl="require" by default for postgres:// URLs
    # that include ?sslmode=require, but we enforce it explicitly here.
    pool = await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=1,
        max_size=10,
        command_timeout=30,
        ssl="require",
    )
    return pool


async def get_pool() -> asyncpg.Pool:
    """Return the active pool. Raises HTTPException 503 if DB is not connected."""
    if _pool is None:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=503,
            detail="Database not connected. Check DATABASE_URL environment variable.",
        )
    return _pool


@asynccontextmanager
async def get_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """Async context manager that yields a single connection from the pool."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn


async def startup_db() -> None:
    """Called once on application startup to initialise the pool."""
    global _pool
    import logging
    logger = logging.getLogger(__name__)
    try:
        _pool = await create_pool()
        logger.info("Database pool created successfully.")
    except Exception as exc:
        logger.warning(
            "Could not connect to database at startup: %s. "
            "Data endpoints will return 503 until DB is reachable.",
            exc,
        )
        _pool = None


async def shutdown_db() -> None:
    """Called once on application shutdown to close the pool gracefully."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
