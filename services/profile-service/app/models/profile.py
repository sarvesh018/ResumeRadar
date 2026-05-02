import uuid

from sqlalchemy import JSON, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from resumeradar_common.database.base_model import Base


class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = {"schema": "profile_db"}

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, nullable=False, index=True,
    )
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    headline: Mapped[str | None] = mapped_column(String(500), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    years_experience: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    target_roles: Mapped[list | None] = mapped_column(JSON, nullable=True)
    target_locations: Mapped[list | None] = mapped_column(JSON, nullable=True)
    linkedin_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    portfolio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    preferences: Mapped[dict | None] = mapped_column(JSON, default=dict)

    def __repr__(self) -> str:
        return f"<Profile(user_id={self.user_id}, name={self.full_name})>"