"""
Progress and streaks model — raw asyncpg queries (no ORM).
"""
from __future__ import annotations
from datetime import date
from typing import Optional
import asyncpg

from app.core.database import get_connection


# ── Chapter progress ──────────────────────────────────────────────────────────

async def get_chapter_progress(
    user_id: str, chapter_id: str
) -> Optional[asyncpg.Record]:
    async with get_connection() as conn:
        return await conn.fetchrow(
            "SELECT * FROM progress WHERE user_id = $1 AND chapter_id = $2",
            user_id, chapter_id,
        )


async def get_all_progress(user_id: str) -> list[asyncpg.Record]:
    async with get_connection() as conn:
        return await conn.fetch(
            "SELECT * FROM progress WHERE user_id = $1 ORDER BY updated_at DESC",
            user_id,
        )


async def upsert_progress(
    user_id: str,
    chapter_id: str,
    completed: bool,
    completion_percentage: int,
) -> asyncpg.Record:
    async with get_connection() as conn:
        return await conn.fetchrow(
            """
            INSERT INTO progress
                (user_id, chapter_id, completed, completion_percentage, last_read_at, updated_at)
            VALUES ($1, $2, $3, $4, NOW(), NOW())
            ON CONFLICT (user_id, chapter_id) DO UPDATE SET
                completed             = EXCLUDED.completed,
                completion_percentage = EXCLUDED.completion_percentage,
                last_read_at          = NOW(),
                updated_at            = NOW()
            RETURNING *
            """,
            user_id, chapter_id, completed, completion_percentage,
        )


async def mark_last_read(user_id: str, chapter_id: str) -> None:
    """Lightweight update — just records that the user read this chapter now."""
    async with get_connection() as conn:
        await conn.execute(
            """
            INSERT INTO progress
                (user_id, chapter_id, last_read_at, updated_at)
            VALUES ($1, $2, NOW(), NOW())
            ON CONFLICT (user_id, chapter_id) DO UPDATE SET
                last_read_at = NOW(),
                updated_at   = NOW()
            """,
            user_id, chapter_id,
        )


# ── Streaks ───────────────────────────────────────────────────────────────────

async def get_streak(user_id: str) -> Optional[asyncpg.Record]:
    async with get_connection() as conn:
        return await conn.fetchrow(
            "SELECT * FROM streaks WHERE user_id = $1", user_id
        )


async def update_streak(user_id: str) -> asyncpg.Record:
    """
    Recalculate and persist the streak for a user.

    Rules:
    - If last_activity_date == today  → no change
    - If last_activity_date == yesterday → current_streak += 1
    - Otherwise → current_streak resets to 1
    - longest_streak = max(longest_streak, current_streak)
    - total_study_days always increments when last_activity_date != today
    """
    today = date.today()
    async with get_connection() as conn:
        existing = await conn.fetchrow(
            "SELECT * FROM streaks WHERE user_id = $1", user_id
        )

        if existing is None:
            # First ever activity
            return await conn.fetchrow(
                """
                INSERT INTO streaks
                    (user_id, current_streak, longest_streak,
                     last_activity_date, total_study_days, updated_at)
                VALUES ($1, 1, 1, $2, 1, NOW())
                RETURNING *
                """,
                user_id, today,
            )

        last = existing["last_activity_date"]

        if last == today:
            # Already updated today — return as-is
            return existing

        from datetime import timedelta
        yesterday = today - timedelta(days=1)

        if last == yesterday:
            new_streak = existing["current_streak"] + 1
        else:
            new_streak = 1

        new_longest = max(existing["longest_streak"], new_streak)
        new_total   = existing["total_study_days"] + 1

        return await conn.fetchrow(
            """
            UPDATE streaks SET
                current_streak     = $2,
                longest_streak     = $3,
                last_activity_date = $4,
                total_study_days   = $5,
                updated_at         = NOW()
            WHERE user_id = $1
            RETURNING *
            """,
            user_id, new_streak, new_longest, today, new_total,
        )
