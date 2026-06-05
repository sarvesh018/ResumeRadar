from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from typing import Optional


class ProfileBase(BaseModel):
    full_name: Optional[str] = None
    headline: Optional[str] = None
    location: Optional[str] = None
    years_experience: Optional[int] = None
    target_roles: Optional[list[str]] = None
    target_locations: Optional[list[str]] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    # NEW
    technical_skills: Optional[list[str]] = None


class ProfileUpdateRequest(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    id: str
    user_id: str
    technical_skills: list[str] = []   # Always return a list, never None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True