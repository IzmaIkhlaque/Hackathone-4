"""
Access Control API — Section 6.6 of PHASE_1_PROMPT.md

Routes:
  GET  /access/check/{user_id}/{chapter_id}   → freemium gate check
  POST /access/users                          → create or get user (upsert)
  GET  /access/users/{user_id}/tier           → return user tier
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_connection
from app.models.user import get_or_create_user, get_user_tier, get_user

router = APIRouter()

_TIER_RANK = {"free": 0, "premium": 1, "pro": 2, "team": 3}


def _can_access(user_tier: str, required_tier: str) -> bool:
    return _TIER_RANK.get(user_tier, 0) >= _TIER_RANK.get(required_tier, 0)


# ── Request / Response schemas (access-specific, lightweight) ─────────────────

class CreateUserRequest(BaseModel):
    user_id: str
    email: Optional[str] = None


class UserOut(BaseModel):
    user_id: str
    email: Optional[str] = None
    tier: str
    created_at: Optional[str] = None


class AccessCheckResponse(BaseModel):
    has_access: bool
    tier_required: str
    user_tier: str
    chapter_id: str
    user_id: str


class TierResponse(BaseModel):
    user_id: str
    tier: str


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/check/{user_id}/{chapter_id}", response_model=AccessCheckResponse)
async def check_access(user_id: str, chapter_id: str):
    """
    Check whether a user can access a specific chapter based on their tier.

    Logic:
    - tier_required == 'free'    → always True
    - tier_required == 'premium' → user.tier must be premium, pro, or team
    - tier_required == 'pro'     → user.tier must be pro or team
    """
    # Get chapter tier requirement
    async with get_connection() as conn:
        row = await conn.fetchrow(
            "SELECT tier_required FROM content_metadata WHERE chapter_id = $1",
            chapter_id,
        )

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Chapter '{chapter_id}' not found.",
        )

    required_tier = row["tier_required"]
    user_tier = await get_user_tier(user_id)   # returns 'free' if user not in DB
    has_access = _can_access(user_tier, required_tier)

    return AccessCheckResponse(
        has_access=has_access,
        tier_required=required_tier,
        user_tier=user_tier,
        chapter_id=chapter_id,
        user_id=user_id,
    )


@router.post("/users", response_model=UserOut, status_code=200)
async def create_or_get_user(body: CreateUserRequest):
    """
    Create a new user or return the existing one (upsert by user_id).
    Used by ChatGPT App on first interaction to register the user.
    """
    row = await get_or_create_user(user_id=body.user_id, email=body.email)
    return UserOut(
        user_id=row["user_id"],
        email=row["email"],
        tier=row["tier"],
        created_at=str(row["created_at"]) if row["created_at"] else None,
    )


@router.get("/users/{user_id}/tier", response_model=TierResponse)
async def get_tier(user_id: str):
    """
    Return the tier for a given user_id.
    Returns 'free' if the user does not exist in the database.
    """
    tier = await get_user_tier(user_id)
    return TierResponse(user_id=user_id, tier=tier)
