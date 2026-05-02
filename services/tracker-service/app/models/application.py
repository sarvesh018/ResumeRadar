import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from resumeradar_common.database.base_model import Base


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = {"schema": "tracker_db"}

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    resume_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    match_result_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)

    company: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role_title: Mapped[str] = mapped_column(String(255), nullable=False)
    jd_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    salary_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_remote: Mapped[bool] = mapped_column(Boolean, default=False)

    status: Mapped[str] = mapped_column(String(20), default="applied", index=True)

    applied_date: Mapped[date] = mapped_column(Date, nullable=False)
    response_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    match_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    status_events: Mapped[list["StatusEvent"]] = relationship(
        "StatusEvent", back_populates="application",
        cascade="all, delete-orphan",
        order_by="StatusEvent.created_at",
    )

    def __repr__(self) -> str:
        return f"<Application(company={self.company}, role={self.role_title}, status={self.status})>"


class StatusEvent(Base):
    __tablename__ = "status_events"
    __table_args__ = {"schema": "tracker_db"}

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tracker_db.applications.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    from_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    to_status: Mapped[str] = mapped_column(String(20), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    application: Mapped["Application"] = relationship("Application", back_populates="status_events")

    def __repr__(self) -> str:
        return f"<StatusEvent({self.from_status} -> {self.to_status})>"