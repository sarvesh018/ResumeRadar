from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class MatchRequest(BaseModel):
    resume_id: UUID
    jd_text: str = Field(min_length=50, max_length=50000)
    jd_company: str | None = Field(default=None, max_length=255)
    jd_role: str | None = Field(default=None, max_length=255)


class SkillMatchDetail(BaseModel):
    skill: str
    match_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    found_in_resume: bool
    jd_required: bool = True


class MissingSkillDetail(BaseModel):
    skill: str
    category: str | None = None
    importance: str = "required"
    suggestion: str | None = None


class SuggestionDetail(BaseModel):
    section: str
    action: str
    text: str


class MatchResponse(BaseModel):
    id: UUID
    resume_id: UUID
    jd_company: str | None
    jd_role: str | None
    overall_score: float = Field(ge=0.0, le=1.0)
    keyword_score: float = Field(ge=0.0, le=1.0)
    semantic_score: float = Field(ge=0.0, le=1.0)
    taxonomy_score: float = Field(ge=0.0, le=1.0)
    matched_skills: list[SkillMatchDetail]
    missing_skills: list[MissingSkillDetail]
    suggestions: list[SuggestionDetail]
    resume_skill_count: int
    jd_skill_count: int
    created_at: datetime
    model_config = {"from_attributes": True}


class MatchSummaryResponse(BaseModel):
    id: UUID
    resume_id: UUID
    jd_company: str | None
    jd_role: str | None
    overall_score: float
    created_at: datetime
    model_config = {"from_attributes": True}


class MatchHistoryResponse(BaseModel):
    results: list[MatchSummaryResponse]
    total: int