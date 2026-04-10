from __future__ import annotations
from typing import Optional
from pydantic import BaseModel


class ChapterMetadata(BaseModel):
    chapter_id: str
    title: str
    description: Optional[str] = None
    tier_required: str          # 'free' | 'premium' | 'pro'
    order_index: int
    estimated_minutes: Optional[int] = None
    word_count: Optional[int] = None
    tags: list[str] = []

    model_config = {"from_attributes": True}


class ChapterList(BaseModel):
    chapters: list[ChapterMetadata]


class ChapterContent(BaseModel):
    chapter_id: str
    title: str
    tier_required: str
    order_index: int
    estimated_minutes: Optional[int] = None
    content: str                # Full markdown text


class ChapterSummary(BaseModel):
    chapter_id: str
    title: str
    tier_required: str
    preview: str                # First 200 words
