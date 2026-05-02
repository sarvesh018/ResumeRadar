import uuid

from sqlalchemy import Boolean, ForeignKey, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from resumeradar_common.database.base_model import Base


class Resume(Base):
    __tablename__ = "resumes"
    __table_args__ = {"schema": "profile_db"}

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    version_name: Mapped[str] = mapped_column(String(100), nullable=False)
    file_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_type: Mapped[str] = mapped_column(String(10), nullable=False)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    parsed_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    skills: Mapped[list["ResumeSkill"]] = relationship(
        "ResumeSkill", back_populates="resume", cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Resume(id={self.id}, version={self.version_name})>"


class ResumeSkill(Base):
    __tablename__ = "resume_skills"
    __table_args__ = {"schema": "profile_db"}

    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("profile_db.resumes.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    confidence: Mapped[float] = mapped_column(default=1.0)

    resume: Mapped["Resume"] = relationship("Resume", back_populates="skills")

    def __repr__(self) -> str:
        return f"<ResumeSkill(skill={self.skill_name}, confidence={self.confidence})>"