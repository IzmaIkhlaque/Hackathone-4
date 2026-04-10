from __future__ import annotations
from typing import Any, Optional
from pydantic import BaseModel


class QuizOption(BaseModel):
    """A single answer option (A/B/C/D)."""
    key: str
    text: str


class QuizQuestion(BaseModel):
    question_id: str
    question: str
    options: dict[str, str]     # {"A": "text", "B": "text", ...}
    type: str = "mcq"
    # NOTE: correct_answer is intentionally absent — never sent to the client


class QuizOut(BaseModel):
    """Quiz returned to the client — no answer keys."""
    quiz_id: str
    chapter_id: str
    title: str
    pass_threshold: int
    questions: list[QuizQuestion]


class AnswerItem(BaseModel):
    question_id: str
    answer: str                 # "A" | "B" | "C" | "D"


class QuizSubmission(BaseModel):
    user_id: str
    answers: list[AnswerItem]


class QuestionFeedback(BaseModel):
    question_id: str
    correct: bool
    correct_answer: str
    explanation: Optional[str] = None


class QuizResult(BaseModel):
    quiz_id: str
    user_id: str
    score: int                  # 0-100 percentage
    total: int
    correct: int
    passed: bool
    feedback: list[QuestionFeedback]
