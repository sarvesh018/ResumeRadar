from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class SkillResponse(BaseModel):
    skill_name: str
    category: str | None
    confidence: float
    model_config = {"from_attributes": True}


class ResumeResponse(BaseModel):
    id: UUID
    user_id: UUID
    version_name: str
    file_type: str
    is_primary: bool
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class ResumeDetailResponse(ResumeResponse):
    skill_count: int = 0
    text_length: int = 0
    skills: list[SkillResponse] = []


class ResumeUploadResponse(BaseModel):
    resume: ResumeDetailResponse
    message: str = "Resume uploaded and parsed successfully"


class ResumeListResponse(BaseModel):
    resumes: list[ResumeResponse]
    total: int