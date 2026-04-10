"""
Search API — Section 6.5 of PHASE_1_PROMPT.md

Route:
  GET /search?q={query}&user_id={user_id}
"""
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional

from app.models.user import get_user_tier
from app.services.search_service import search_chapters

router = APIRouter()


class SearchResult(BaseModel):
    chapter_id: str
    title: str
    tier_required: str
    order_index: int
    excerpt: str


class SearchResponse(BaseModel):
    query: str
    user_id: str
    total: int
    results: list[SearchResult]


@router.get("", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="Search keyword or phrase"),
    user_id: Optional[str] = Query(default=None, description="User ID for access filtering"),
):
    """
    Keyword search across course content.
    - Searches chapter titles, descriptions, tags (PostgreSQL full-text / ILIKE)
    - Falls back to scanning full chapter text from R2 (cached)
    - Only returns chapters the requesting user has access to
    - Each result includes a 150-character excerpt around the first match
    """
    uid = user_id or "anonymous"
    user_tier = await get_user_tier(uid)

    hits = await search_chapters(query=q, user_tier=user_tier)

    results = [
        SearchResult(
            chapter_id=h["chapter_id"],
            title=h["title"],
            tier_required=h["tier_required"],
            order_index=h["order_index"],
            excerpt=h["excerpt"],
        )
        for h in hits
    ]

    return SearchResponse(
        query=q,
        user_id=uid,
        total=len(results),
        results=results,
    )
