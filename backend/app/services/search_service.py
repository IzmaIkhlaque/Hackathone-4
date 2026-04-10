"""
Search service — keyword search across chapter content.

Strategy:
  1. Try PostgreSQL full-text search (tsvector/tsquery) against content_metadata
     (title, description, tags).  Fast, no R2 reads needed for metadata matches.
  2. For deeper content matches, search cached R2 chapter text using Python ILIKE.
  3. Return only chapters the requesting user has access to.
  4. Each result includes a 150-character excerpt around the first match.

Phase 2 upgrade path: replace step 2 with a pgvector semantic search.
"""
from __future__ import annotations
import re
from typing import Optional

from app.core.database import get_connection
from app.services.r2_service import get_chapter as r2_get_chapter

_TIER_RANK = {"free": 0, "premium": 1, "pro": 2, "team": 3}
_EXCERPT_RADIUS = 75   # chars on each side of the match keyword


def _user_can_access(user_tier: str, required_tier: str) -> bool:
    return _TIER_RANK.get(user_tier, 0) >= _TIER_RANK.get(required_tier, 0)


def _make_excerpt(text: str, query: str, radius: int = _EXCERPT_RADIUS) -> str:
    """
    Return a ~150-char snippet around the first case-insensitive match of
    `query` in `text`. Falls back to the first 150 chars if not found.
    """
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        return text[:150].strip() + ("…" if len(text) > 150 else "")
    start = max(0, match.start() - radius)
    end   = min(len(text), match.end() + radius)
    snippet = text[start:end].strip()
    if start > 0:
        snippet = "…" + snippet
    if end < len(text):
        snippet = snippet + "…"
    return snippet


async def search_chapters(
    query: str,
    user_tier: str = "free",
    max_results: int = 10,
) -> list[dict]:
    """
    Search chapter content for `query`.

    Returns a list of dicts with keys:
        chapter_id, title, tier_required, order_index, excerpt
    Only returns chapters the user has access to.
    """
    if not query or not query.strip():
        return []

    query = query.strip()

    # ── Step 1: metadata search via PostgreSQL full-text / ILIKE ─────────────
    async with get_connection() as conn:
        # Try tsvector full-text search on title + description + tags
        # Fall back to ILIKE if tsvector gives no results
        rows = await conn.fetch(
            """
            SELECT chapter_id, title, description, tier_required, order_index, tags
            FROM content_metadata
            WHERE
                to_tsvector('english', coalesce(title,'') || ' ' || coalesce(description,''))
                    @@ plainto_tsquery('english', $1)
                OR title       ILIKE $2
                OR description ILIKE $2
                OR EXISTS (
                    SELECT 1 FROM unnest(tags) AS t WHERE t ILIKE $2
                )
            ORDER BY order_index
            """,
            query,
            f"%{query}%",
        )

    accessible = [
        dict(r) for r in rows
        if _user_can_access(user_tier, r["tier_required"])
    ]

    results: list[dict] = []

    # Build results from metadata matches first
    seen: set[str] = set()
    for r in accessible:
        if len(results) >= max_results:
            break
        # Use description as excerpt if it contains the query, else fallback
        desc = r["description"] or r["title"]
        excerpt = _make_excerpt(desc, query)
        results.append({
            "chapter_id":    r["chapter_id"],
            "title":         r["title"],
            "tier_required": r["tier_required"],
            "order_index":   r["order_index"],
            "excerpt":       excerpt,
            "match_source":  "metadata",
        })
        seen.add(r["chapter_id"])

    # ── Step 2: full-content search across R2-cached text ─────────────────────
    if len(results) < max_results:
        # Fetch all accessible chapters not already in results
        async with get_connection() as conn:
            all_rows = await conn.fetch(
                "SELECT chapter_id, title, tier_required, order_index "
                "FROM content_metadata ORDER BY order_index"
            )
        candidates = [
            dict(r) for r in all_rows
            if r["chapter_id"] not in seen
            and _user_can_access(user_tier, r["tier_required"])
        ]

        for c in candidates:
            if len(results) >= max_results:
                break
            content = await r2_get_chapter(c["chapter_id"])
            if content is None:
                continue
            pattern = re.compile(re.escape(query), re.IGNORECASE)
            if pattern.search(content):
                results.append({
                    "chapter_id":    c["chapter_id"],
                    "title":         c["title"],
                    "tier_required": c["tier_required"],
                    "order_index":   c["order_index"],
                    "excerpt":       _make_excerpt(content, query),
                    "match_source":  "content",
                })

    return results
