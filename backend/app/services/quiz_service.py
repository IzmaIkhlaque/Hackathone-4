"""
Quiz service — deterministic rule-based grading. ZERO LLM calls.

Grade flow:
  1. Load quiz JSON from R2 (answer key is in the JSON, never sent to client)
  2. Compare each submitted answer string to correct_answer string (case-insensitive)
  3. Calculate score = (correct / total) * 100  (integer)
  4. Build per-question feedback list
  5. Return GradeResult dataclass — caller persists it to quiz_attempts table
"""
from __future__ import annotations
from dataclasses import dataclass

from app.services.r2_service import get_quiz as r2_get_quiz
from app.schemas.quiz import AnswerItem, QuestionFeedback, QuizOut, QuizQuestion


# ── Public data types ─────────────────────────────────────────────────────────

@dataclass
class GradeResult:
    quiz_id: str
    chapter_id: str
    user_id: str
    score: int                          # 0-100 integer percentage
    total: int
    correct: int
    passed: bool
    feedback: list[QuestionFeedback]
    answers_payload: list[dict]         # raw answers stored in quiz_attempts.answers_json


# ── Helpers ───────────────────────────────────────────────────────────────────

def _strip_quiz_answers(raw: dict) -> QuizOut:
    """Return a QuizOut (client-safe) with correct_answer stripped from every question."""
    questions = [
        QuizQuestion(
            question_id=q["question_id"],
            question=q["question"],
            options=q["options"],
            type=q.get("type", "mcq"),
            # correct_answer intentionally NOT included
        )
        for q in raw["questions"]
    ]
    return QuizOut(
        quiz_id=raw["quiz_id"],
        chapter_id=raw["chapter_id"],
        title=raw["title"],
        pass_threshold=raw.get("pass_threshold", 70),
        questions=questions,
    )


# ── Public API ────────────────────────────────────────────────────────────────

async def get_quiz_for_client(quiz_id: str) -> QuizOut | None:
    """
    Fetch quiz from R2 and return it with answer keys stripped.
    Returns None if the quiz does not exist in R2.
    """
    raw = await r2_get_quiz(quiz_id)
    if raw is None:
        return None
    return _strip_quiz_answers(raw)


async def grade_quiz(
    quiz_id: str,
    user_id: str,
    submitted_answers: list[AnswerItem],
) -> GradeResult | None:
    """
    Deterministically grade a quiz submission.

    - Loads answer key from R2 (never from client).
    - Compares submitted answer strings case-insensitively.
    - Returns None if the quiz does not exist.
    - ZERO LLM calls — pure string comparison.
    """
    raw = await r2_get_quiz(quiz_id)
    if raw is None:
        return None

    chapter_id    = raw["chapter_id"]
    pass_threshold = raw.get("pass_threshold", 70)

    # Build answer key map: question_id -> {correct_answer, explanation}
    answer_key: dict[str, dict] = {
        q["question_id"]: {
            "correct_answer": q["correct_answer"],
            "explanation":    q.get("explanation", ""),
        }
        for q in raw["questions"]
    }

    total = len(raw["questions"])
    correct_count = 0
    feedback: list[QuestionFeedback] = []

    # Index submitted answers by question_id for O(1) lookup
    submitted_map = {a.question_id: a.answer for a in submitted_answers}

    for q in raw["questions"]:
        qid = q["question_id"]
        key = answer_key[qid]
        submitted = submitted_map.get(qid, "")

        # Case-insensitive, strip whitespace
        is_correct = submitted.strip().upper() == key["correct_answer"].strip().upper()
        if is_correct:
            correct_count += 1

        feedback.append(
            QuestionFeedback(
                question_id=qid,
                correct=is_correct,
                correct_answer=key["correct_answer"],
                explanation=key["explanation"] if not is_correct else None,
            )
        )

    score = round((correct_count / total) * 100) if total > 0 else 0
    passed = score >= pass_threshold

    return GradeResult(
        quiz_id=quiz_id,
        chapter_id=chapter_id,
        user_id=user_id,
        score=score,
        total=total,
        correct=correct_count,
        passed=passed,
        feedback=feedback,
        answers_payload=[a.model_dump() for a in submitted_answers],
    )
