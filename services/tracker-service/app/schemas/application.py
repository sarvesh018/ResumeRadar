from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, Field
from app.core.status_machine import ApplicationStatus


class ApplicationCreateRequest(BaseModel):
    company: str = Field(max_length=255)
    role_title: str = Field(max_length=255)
    resume_id: UUID | None = None
    match_result_id: UUID | None = None
    jd_url: str | None = Field(default=None, max_length=1000)
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    location: str | None = Field(default=None, max_length=255)
    is_remote: bool = False
    applied_date: date | None = None
    match_score: float | None = Field(default=None, ge=0.0, le=1.0)
    notes: str | None = None
    status: ApplicationStatus = ApplicationStatus.APPLIED


class ApplicationUpdateRequest(BaseModel):
    company: str | None = Field(default=None, max_length=255)
    role_title: str | None = Field(default=None, max_length=255)
    jd_url: str | None = Field(default=None, max_length=1000)
    salary_min: int | None = Field(default=None, ge=0)
    salary_max: int | None = Field(default=None, ge=0)
    location: str | None = Field(default=None, max_length=255)
    is_remote: bool | None = None
    notes: str | None = None


class StatusUpdateRequest(BaseModel):
    status: ApplicationStatus
    notes: str | None = None
    response_date: date | None = None


class StatusEventResponse(BaseModel):
    id: UUID
    from_status: str | None
    to_status: str
    notes: str | None
    created_at: datetime
    model_config = {"from_attributes": True}


class ApplicationResponse(BaseModel):
    id: UUID
    user_id: UUID
    company: str
    role_title: str
    resume_id: UUID | None
    match_result_id: UUID | None
    jd_url: str | None
    salary_min: int | None
    salary_max: int | None
    location: str | None
    is_remote: bool
    status: str
    applied_date: date
    response_date: date | None
    match_score: float | None
    notes: str | None
    allowed_transitions: list[str] = []
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class ApplicationDetailResponse(ApplicationResponse):
    status_events: list[StatusEventResponse] = []


class ApplicationListResponse(BaseModel):
    applications: list[ApplicationResponse]
    total: int


class KanbanColumn(BaseModel):
    status: str
    count: int
    applications: list[ApplicationResponse]


class KanbanBoardResponse(BaseModel):
    columns: list[KanbanColumn]
    total: int