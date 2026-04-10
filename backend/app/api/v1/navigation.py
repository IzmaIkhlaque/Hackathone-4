"""
Navigation API — Section 6.2 of PHASE_1_PROMPT.md

Routes:
  GET  /navigation/chapters/{chapter_id}/next  → next chapter metadata
  GET  /navigation/chapters/{chapter_id}/prev  → previous chapter metadata
  GET  /navigation/chapters/sequence           → full ordered list (table of contents)
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_connection

router = APIRouter()


# ── Response schemas (lightweight, navigation-specific) ───────────────────────

class ChapterNavItem(BaseModel):
    chapter_id: str
    title: str
    tier_required: str
    order_index: int


class SequenceResponse(BaseModel):
    chapters: list[ChapterNavItem]


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_ordered_chapters() -> list[dict]:
    async with get_connection() as conn:
        rows = await conn.fetch(
            "SELECT chapter_id, title, tier_required, order_index "
            "FROM content_metadata ORDER BY order_index"
        )
    return [dict(r) for r in rows]


async def _get_adjacent(chapter_id: str, direction: str) -> Optional[dict]:
    """
    Return the next (direction='next') or previous (direction='prev') chapter.
    Uses order_index arithmetic directly in SQL for efficiency.
    """
    operator = ">" if direction == "next" else "<"
    order    = "ASC" if direction == "next" else "DESC"

    async with get_connection() as conn:
        current = await conn.fetchrow(
            "SELECT order_index FROM content_metadata WHERE chapter_id = $1",
            chapter_id,
        )
        if current is None:
            return None

        row = await conn.fetchrow(
            f"""
            SELECT chapter_id, title, tier_required, order_index
            FROM content_metadata
            WHERE order_index {operator} $1
            ORDER BY order_index {order}
            LIMIT 1
            """,
            current["order_index"],
        )
    return dict(row) if row else None


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/chapters/sequence", response_model=SequenceResponse)
async def get_sequence():
    """
    Returns the full ordered chapter list — suitable for building a table of contents.
    """
    rows = await _get_ordered_chapters()
    chapters = [ChapterNavItem(**r) for r in rows]
    return SequenceResponse(chapters=chapters)


@router.get("/chapters/{chapter_id}/next", response_model=ChapterNavItem)
async def get_next_chapter(chapter_id: str):
    """
    Returns metadata for the chapter that follows `chapter_id` (by order_index).
    404 if `chapter_id` is the last chapter or does not exist.
    """
    chapter = await _get_adjacent(chapter_id, "next")
    if chapter is None:
        raise HTTPException(
            status_code=404,
            detail=f"No next chapter after '{chapter_id}'. This may be the last chapter.",
        )
    return ChapterNavItem(**chapter)


@router.get("/chapters/{chapter_id}/prev", response_model=ChapterNavItem)
async def get_prev_chapter(chapter_id: str):
    """
    Returns metadata for the chapter that precedes `chapter_id` (by order_index).
    404 if `chapter_id` is the first chapter or does not exist.
    """
    chapter = await _get_adjacent(chapter_id, "prev")
    if chapter is None:
        raise HTTPException(
            status_code=404,
            detail=f"No previous chapter before '{chapter_id}'. This may be the first chapter.",
        )
    return ChapterNavItem(**chapter)
