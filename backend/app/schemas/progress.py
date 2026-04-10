from __future__ import annotations
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class QuizScore(BaseModel):
    quiz_id: str
    score: int
    passed: bool
    attempted_at: Optional[datetime] = None


class UserProgress(BaseModel):
    user_id: str
    completed_chapters: list[str]
    completion_percentage: int      # 0-100 across all free chapters
    current_streak: int
    longest_streak: int
    total_study_days: int
    quiz_scores: list[QuizScore]


class ProgressUpdate(BaseModel):
    completed: bool = False
    completion_percentage: int = 0  # 0-100


class ChapterProgressOut(BaseModel):
    user_id: str
    chapter_id: str
    completed: bool
    completion_percentage: int
    last_read_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class StreakInfo(BaseModel):
    user_id: str
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[date] = None
    total_study_days: int
