from uuid import uuid4
from sqlalchemy import Column, String, Integer, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from resumeradar_common.database.base_model import Base


class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = {"schema": "profile_db"}

    id = Column(PGUUID, primary_key=True, default=uuid4)
    user_id = Column(PGUUID, unique=True, nullable=False)
    full_name = Column(String(255))
    headline = Column(String(500))
    location = Column(String(255))
    years_experience = Column(Integer)
    target_roles = Column(JSON)
    target_locations = Column(JSON)
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    portfolio_url = Column(String(500))
    preferences = Column(JSON, default={})

    # NEW: user-defined technical skills list
    # Example: ["Python", "Docker", "AWS", "Kubernetes"]
    technical_skills = Column(JSON, default=list)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())