"""
Quiz API — Section 6.3 of PHASE_1_PROMPT.md

Routes:
  GET  /quiz/chapter/{chapter_id}     → quiz_id for a chapter
  GET  /quiz/{quiz_id}                → questions WITHOUT answer keys
  POST /quiz/{quiz_id}/submit         → deterministic grading + store attempt
"""
from fastapi import APIRouter, HTTPException

from app.services import quiz_service
from app.models import quiz_attempt as attempt_model
from app.schemas.quiz import QuizOut, QuizSubmission, QuizResult

router = APIRouter()


# ── NOTE: /quiz/chapter/{chapter_id} MUST be registered before /quiz/{quiz_id}
# so FastAPI doesn't try to match "chapter" as a quiz_id literal.


@router.get("/chapter/{chapter_id}")
async def get_quiz_id_for_chapter(chapter_id: str):
    """
    Return the quiz_id that corresponds to a given chapter_id.
    Convention: chapter-01 → quiz-01.
    """
    quiz_id = await attempt_model.get_quiz_id_for_chapter(chapter_id)
    if quiz_id is None:
        raise HTTPException(
            status_code=404,
            detail=f"No quiz found for chapter '{chapter_id}'.",
        )
    return {"chapter_id": chapter_id, "quiz_id": quiz_id}


@router.get("/{quiz_id}", response_model=QuizOut)
async def get_quiz(quiz_id: str):
    """
    Return quiz questions WITHOUT correct answers (safe for client).
    404 if the quiz does not exist in R2.
    """
    quiz = await quiz_service.get_quiz_for_client(quiz_id)
    if quiz is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Quiz '{quiz_id}' not found. "
                "Ensure quiz JSON files have been uploaded to R2."
            ),
        )
    return quiz


@router.post("/{quiz_id}/submit", response_model=QuizResult)
async def submit_quiz(quiz_id: str, body: QuizSubmission):
    """
    Grade a quiz submission deterministically (no LLM).
    - Loads answer key from R2
    - Compares each answer string (case-insensitive)
    - Stores attempt in quiz_attempts table
    - Returns score, pass/fail, and per-question feedback
    """
    result = await quiz_service.grade_quiz(
        quiz_id=quiz_id,
        user_id=body.user_id,
        submitted_answers=body.answers,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Quiz '{quiz_id}' not found. "
                "Ensure quiz JSON files have been uploaded to R2."
            ),
        )

    # Persist attempt (non-critical — don't fail the grade response if DB is down)
    try:
        await attempt_model.save_attempt(
            user_id=result.user_id,
            quiz_id=result.quiz_id,
            chapter_id=result.chapter_id,
            score=result.score,
            total_questions=result.total,
            correct_answers=result.correct,
            passed=result.passed,
            answers_json=result.answers_payload,
        )
    except Exception:
        pass  # Grade is still returned even if DB write fails

    return QuizResult(
        quiz_id=quiz_id,
        user_id=body.user_id,
        score=result.score,
        total=result.total,
        correct=result.correct,
        passed=result.passed,
        feedback=result.feedback,
    )
