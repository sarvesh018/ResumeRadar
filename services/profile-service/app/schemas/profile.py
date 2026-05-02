from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, max_length=255)
    headline: str | None = Field(default=None, max_length=500)
    location: str | None = Field(default=None, max_length=255)
    years_experience: int | None = Field(default=None, ge=0, le=50)
    target_roles: list[str] | None = None
    target_locations: list[str] | None = None
    linkedin_url: str | None = Field(default=None, max_length=500)
    github_url: str | None = Field(default=None, max_length=500)
    portfolio_url: str | None = Field(default=None, max_length=500)


class ProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    full_name: str | None
    headline: str | None
    location: str | None
    years_experience: int | None
    target_roles: list[str] | None
    target_locations: list[str] | None
    linkedin_url: str | None
    github_url: str | None
    portfolio_url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}