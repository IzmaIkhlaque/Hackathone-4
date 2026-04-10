"""
Progress API — Section 6.4 of PHASE_1_PROMPT.md

Routes:
  GET  /progress/{user_id}                          → full progress summary
  PUT  /progress/{user_id}/chapter/{chapter_id}     → update chapter progress + streak
  GET  /progress/{user_id}/streak                   → streak info only
"""
from fastapi import APIRouter, HTTPException

from app.models.user import get_or_create_user
from app.services import progress_service
from app.schemas.progress import UserProgress, ProgressUpdate, ChapterProgressOut, StreakInfo

router = APIRouter()


@router.get("/{user_id}", response_model=UserProgress)
async def get_progress(user_id: str):
    """
    Return full progress summary for a user:
    completed chapters, overall %, streak, quiz scores.
    Auto-creates the user record if it doesn't exist yet.
    """
    await get_or_create_user(user_id)
    return await progress_service.get_full_progress(user_id)


@router.put("/{user_id}/chapter/{chapter_id}", response_model=ChapterProgressOut)
async def update_progress(
    user_id: str,
    chapter_id: str,
    body: ProgressUpdate,
):
    """
    Update progress for a specific chapter.
    - Upserts progress row (completed + completion_percentage)
    - Recalculates streak automatically
    Returns the updated progress row.
    """
    await get_or_create_user(user_id)

    row = await progress_service.update_chapter_progress(
        user_id=user_id,
        chapter_id=chapter_id,
        completed=body.completed,
        completion_percentage=body.completion_percentage,
    )

    return ChapterProgressOut(
        user_id=user_id,
        chapter_id=chapter_id,
        completed=row["completed"],
        completion_percentage=row["completion_percentage"],
        last_read_at=row.get("last_read_at"),
        updated_at=row.get("updated_at"),
    )


@router.get("/{user_id}/streak", response_model=StreakInfo)
async def get_streak(user_id: str):
    """
    Return streak information only (faster than full progress).
    Returns zeros if the user has no activity recorded yet.
    """
    await get_or_create_user(user_id)
    return await progress_service.get_streak_info(user_id)
