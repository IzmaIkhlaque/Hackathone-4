"""
Content API — Section 6.1 of PHASE_1_PROMPT.md

Routes:
  GET  /content/chapters                       → list all chapters (metadata only)
  GET  /content/chapters/{chapter_id}          → full markdown (access-gated, updates progress)
  GET  /content/chapters/{chapter_id}/summary  → first 200 words (available to all tiers)
"""
from fastapi import APIRouter, Header, HTTPException
from typing import Optional

from app.core.database import get_connection
from app.services.r2_service import get_chapter as r2_get_chapter
from app.models import progress as progress_model
from app.models import user as user_model
from app.schemas.content import ChapterList, ChapterMetadata, ChapterContent, ChapterSummary

router = APIRouter()

# ── Tier access ordering ───────────────────────────────────────────────────────
_TIER_RANK = {"free": 0, "premium": 1, "pro": 2, "team": 3}


def _user_can_access(user_tier: str, required_tier: str) -> bool:
    return _TIER_RANK.get(user_tier, 0) >= _TIER_RANK.get(required_tier, 0)


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_all_metadata() -> list[dict]:
    async with get_connection() as conn:
        rows = await conn.fetch(
            """
            SELECT chapter_id, title, description, order_index,
                   tier_required, estimated_minutes, word_count, tags
            FROM content_metadata
            ORDER BY order_index
            """
        )
    return [dict(r) for r in rows]


async def _get_chapter_meta(chapter_id: str) -> Optional[dict]:
    async with get_connection() as conn:
        row = await conn.fetchrow(
            """
            SELECT chapter_id, title, description, order_index,
                   tier_required, estimated_minutes, word_count, tags
            FROM content_metadata
            WHERE chapter_id = $1
            """,
            chapter_id,
        )
    return dict(row) if row else None


def _first_n_words(text: str, n: int = 200) -> str:
    """Return the first `n` words of a string, stripping YAML frontmatter."""
    lines = text.splitlines()
    # Skip YAML frontmatter (between --- delimiters)
    if lines and lines[0].strip() == "---":
        try:
            end = lines.index("---", 1)
            lines = lines[end + 1:]
        except ValueError:
            pass
    body = " ".join(lines)
    words = body.split()
    return " ".join(words[:n])


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/chapters", response_model=ChapterList)
async def list_chapters():
    """
    Returns all chapter metadata (no content, no access restriction).
    """
    rows = await _get_all_metadata()
    chapters = [
        ChapterMetadata(
            chapter_id=r["chapter_id"],
            title=r["title"],
            description=r["description"],
            tier_required=r["tier_required"],
            order_index=r["order_index"],
            estimated_minutes=r["estimated_minutes"],
            word_count=r["word_count"],
            tags=r["tags"] or [],
        )
        for r in rows
    ]
    return ChapterList(chapters=chapters)


@router.get("/chapters/{chapter_id}/summary", response_model=ChapterSummary)
async def get_chapter_summary(chapter_id: str):
    """
    Returns the first 200 words of a chapter (preview for locked content).
    Available to all tiers — no access check.
    """
    meta = await _get_chapter_meta(chapter_id)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Chapter '{chapter_id}' not found")

    content = await r2_get_chapter(chapter_id)
    if content is None:
        # Fall back: show title + placeholder when R2 is not yet seeded
        preview = f"Preview not available yet. Upload content to R2 to enable previews."
    else:
        preview = _first_n_words(content, 200)

    return ChapterSummary(
        chapter_id=chapter_id,
        title=meta["title"],
        tier_required=meta["tier_required"],
        preview=preview,
    )


@router.get("/chapters/{chapter_id}", response_model=ChapterContent)
async def get_chapter(
    chapter_id: str,
    x_user_id: Optional[str] = Header(default=None, alias="X-User-ID"),
):
    """
    Returns full chapter markdown.
    - Checks freemium gate: 403 if user tier is below required tier.
    - After serving, marks chapter as last_read in progress table.
    - user_id comes from X-User-ID header (anonymous access treated as 'free').
    """
    meta = await _get_chapter_meta(chapter_id)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Chapter '{chapter_id}' not found")

    # Determine user tier
    user_id = x_user_id or "anonymous"
    user_tier = await user_model.get_user_tier(user_id)

    if not _user_can_access(user_tier, meta["tier_required"]):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "premium_required",
                "upgrade_message": (
                    f"This chapter requires {meta['tier_required'].capitalize()} tier. "
                    f"Your current tier is {user_tier}."
                ),
                "tier_required": meta["tier_required"],
                "user_tier": user_tier,
            },
        )

    content = r2_get_chapter(chapter_id)
    if content is None:
        raise HTTPException(
            status_code=503,
            detail="Chapter content not available. Content may not have been uploaded to R2 yet.",
        )

    # Fire-and-forget: update progress (do not fail the request if this errors)
    if user_id != "anonymous":
        try:
            await progress_model.mark_last_read(user_id, chapter_id)
        except Exception:
            pass  # Non-critical — don't fail the content request

    return ChapterContent(
        chapter_id=chapter_id,
        title=meta["title"],
        tier_required=meta["tier_required"],
        order_index=meta["order_index"],
        estimated_minutes=meta["estimated_minutes"],
        content=content,
    )
