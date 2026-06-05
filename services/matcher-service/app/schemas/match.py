from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class MatchRequest(BaseModel):
    resume_id: UUID
    jd_text: str = Field(..., min_length=50)
    jd_company: Optional[str] = None
    jd_role: Optional[str] = None


class SkillMatchDetail(BaseModel):
    skill: str
    matched_with: Optional[str] = None
    match_type: str
    confidence: float
    found_in_resume: bool
    jd_required: bool


class MissingSkill(BaseModel):
    skill: str
    category: Optional[str] = None
    importance: str
    suggestion: Optional[str] = None


class Suggestion(BaseModel):
    section: str
    action: str
    text: str


class MatchResponse(BaseModel):
    id: UUID
    resume_id: UUID
    jd_company: Optional[str] = None
    jd_role: Optional[str] = None
    overall_score: float
    keyword_score: float
    semantic_score: float
    taxonomy_score: float
    matched_skills: list
    missing_skills: list
    suggestions: list
    resume_skill_count: int = 0
    jd_skill_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True