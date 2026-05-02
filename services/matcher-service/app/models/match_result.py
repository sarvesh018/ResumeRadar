import uuid

from sqlalchemy import Float, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from resumeradar_common.database.base_model import Base


class MatchResult(Base):
    __tablename__ = "match_results"
    __table_args__ = {"schema": "matcher_db"}

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    jd_text: Mapped[str] = mapped_column(Text, nullable=False)
    jd_company: Mapped[str | None] = mapped_column(String(255), nullable=True)
    jd_role: Mapped[str | None] = mapped_column(String(255), nullable=True)

    keyword_score: Mapped[float] = mapped_column(Float, nullable=False)
    semantic_score: Mapped[float] = mapped_column(Float, nullable=False)
    taxonomy_score: Mapped[float] = mapped_column(Float, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)

    matched_skills: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    missing_skills: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    suggestions: Mapped[list | None] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<MatchResult(id={self.id}, score={self.overall_score:.0%})>"