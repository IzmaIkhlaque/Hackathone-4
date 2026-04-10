"""
Quiz attempts model — raw asyncpg queries (no ORM).
"""
from __future__ import annotations
from typing import Any, Optional
import json
import asyncpg

from app.core.database import get_connection


async def save_attempt(
    user_id: str,
    quiz_id: str,
    chapter_id: str,
    score: int,
    total_questions: int,
    correct_answers: int,
    passed: bool,
    answers_json: Optional[Any] = None,
) -> asyncpg.Record:
    async with get_connection() as conn:
        return await conn.fetchrow(
            """
            INSERT INTO quiz_attempts
                (user_id, quiz_id, chapter_id, score,
                 total_questions, correct_answers, passed, answers_json)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb)
            RETURNING *
            """,
            user_id,
            quiz_id,
            chapter_id,
            score,
            total_questions,
            correct_answers,
            passed,
            json.dumps(answers_json) if answers_json is not None else None,
        )


async def get_attempts_for_user(user_id: str) -> list[asyncpg.Record]:
    async with get_connection() as conn:
        return await conn.fetch(
            """
            SELECT quiz_id, chapter_id, score, passed, attempted_at
            FROM quiz_attempts
            WHERE user_id = $1
            ORDER BY attempted_at DESC
            """,
            user_id,
        )


async def get_best_attempt(user_id: str, quiz_id: str) -> Optional[asyncpg.Record]:
    async with get_connection() as conn:
        return await conn.fetchrow(
            """
            SELECT * FROM quiz_attempts
            WHERE user_id = $1 AND quiz_id = $2
            ORDER BY score DESC, attempted_at DESC
            LIMIT 1
            """,
            user_id, quiz_id,
        )


async def get_quiz_id_for_chapter(chapter_id: str) -> Optional[str]:
    """Derive quiz_id from chapter_id (convention: chapter-01 → quiz-01)."""
    # Stored convention: quiz-XX corresponds to chapter-XX
    # We use the naming convention rather than a separate DB lookup in Phase 1
    number = chapter_id.split("-")[-1]  # "01"
    return f"quiz-{number}"
