"""
Progress service — aggregates progress, quiz scores, and streak data for a user.
Pure business logic; all DB access goes through the models layer.
ZERO LLM calls.
"""
from __future__ import annotations

from app.core.database import get_connection
from app.models import progress as progress_model
from app.models import quiz_attempt as attempt_model
from app.schemas.progress import UserProgress, QuizScore, StreakInfo


# Total chapters in the course (free + premium + pro).
# Used to compute overall completion %.  Phase 2 can make this dynamic.
_TOTAL_CHAPTERS = 6


async def get_full_progress(user_id: str) -> UserProgress:
    """
    Aggregate all progress data for a user into a single UserProgress object.

    Composition:
    - completed_chapters  : chapters where progress.completed = True
    - completion_percentage: (completed / TOTAL) * 100
    - streak data          : from streaks table (0s if no row yet)
    - quiz_scores          : latest best score per quiz from quiz_attempts
    """
    # ── Chapter progress ──────────────────────────────────────────────────────
    prog_rows = await progress_model.get_all_progress(user_id)
    completed_chapters = [
        r["chapter_id"] for r in prog_rows if r["completed"]
    ]
    completion_pct = round(len(completed_chapters) / _TOTAL_CHAPTERS * 100)

    # ── Streak ────────────────────────────────────────────────────────────────
    streak_row = await progress_model.get_streak(user_id)
    current_streak  = streak_row["current_streak"]  if streak_row else 0
    longest_streak  = streak_row["longest_streak"]  if streak_row else 0
    total_study_days = streak_row["total_study_days"] if streak_row else 0

    # ── Quiz scores (best attempt per quiz) ───────────────────────────────────
    attempt_rows = await attempt_model.get_attempts_for_user(user_id)

    # Deduplicate: keep best score per quiz_id
    best: dict[str, dict] = {}
    for row in attempt_rows:
        qid = row["quiz_id"]
        if qid not in best or row["score"] > best[qid]["score"]:
            best[qid] = {
                "quiz_id":      qid,
                "score":        row["score"],
                "passed":       row["passed"],
                "attempted_at": row["attempted_at"],
            }

    quiz_scores = [QuizScore(**v) for v in best.values()]

    return UserProgress(
        user_id=user_id,
        completed_chapters=completed_chapters,
        completion_percentage=completion_pct,
        current_streak=current_streak,
        longest_streak=longest_streak,
        total_study_days=total_study_days,
        quiz_scores=quiz_scores,
    )


async def update_chapter_progress(
    user_id: str,
    chapter_id: str,
    completed: bool,
    completion_percentage: int,
) -> dict:
    """
    Persist chapter progress and recalculate streak.
    Returns the updated progress row as a dict.
    """
    # Upsert progress row
    row = await progress_model.upsert_progress(
        user_id=user_id,
        chapter_id=chapter_id,
        completed=completed,
        completion_percentage=completion_percentage,
    )

    # Recalculate streak (only when marking meaningful progress)
    if completion_percentage > 0 or completed:
        try:
            await progress_model.update_streak(user_id)
        except Exception:
            pass  # streak is non-critical; don't fail the update

    return dict(row)


async def get_streak_info(user_id: str) -> StreakInfo:
    row = await progress_model.get_streak(user_id)
    if row is None:
        return StreakInfo(
            user_id=user_id,
            current_streak=0,
            longest_streak=0,
            last_activity_date=None,
            total_study_days=0,
        )
    return StreakInfo(
        user_id=user_id,
        current_streak=row["current_streak"],
        longest_streak=row["longest_streak"],
        last_activity_date=row["last_activity_date"],
        total_study_days=row["total_study_days"],
    )
