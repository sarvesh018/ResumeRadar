from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from resumeradar_common.database.base_model import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth_db"}

    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"