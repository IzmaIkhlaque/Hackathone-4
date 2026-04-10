"""
User model — raw asyncpg queries (no ORM).
"""
from __future__ import annotations
from typing import Optional
import asyncpg

from app.core.database import get_connection


async def get_user(user_id: str) -> Optional[asyncpg.Record]:
    async with get_connection() as conn:
        return await conn.fetchrow(
            "SELECT * FROM users WHERE user_id = $1", user_id
        )


async def create_user(user_id: str, email: Optional[str] = None) -> asyncpg.Record:
    async with get_connection() as conn:
        return await conn.fetchrow(
            """
            INSERT INTO users (user_id, email)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE
                SET updated_at = NOW()
            RETURNING *
            """,
            user_id, email,
        )


async def get_or_create_user(
    user_id: str, email: Optional[str] = None
) -> asyncpg.Record:
    async with get_connection() as conn:
        return await conn.fetchrow(
            """
            INSERT INTO users (user_id, email)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE
                SET updated_at = NOW()
            RETURNING *
            """,
            user_id, email,
        )


async def get_user_tier(user_id: str) -> str:
    """Return the user's tier ('free' if user does not exist)."""
    async with get_connection() as conn:
        row = await conn.fetchrow(
            "SELECT tier FROM users WHERE user_id = $1", user_id
        )
        return row["tier"] if row else "free"


async def update_user_tier(user_id: str, tier: str) -> Optional[asyncpg.Record]:
    async with get_connection() as conn:
        return await conn.fetchrow(
            """
            UPDATE users SET tier = $2, updated_at = NOW()
            WHERE user_id = $1
            RETURNING *
            """,
            user_id, tier,
        )
