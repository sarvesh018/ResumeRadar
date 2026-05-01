import structlog
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenResponse, UserResponse
from resumeradar_common.auth.jwt_handler import create_access_token, create_refresh_token
from resumeradar_common.config.settings import get_settings
from resumeradar_common.events.publisher import publish_event

logger = structlog.get_logger()


class AuthService:
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)
        self.db = db

    async def register(self, email: str, password: str, full_name: str | None = None) -> UserResponse:
        if await self.repo.email_exists(email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        hashed = hash_password(password)
        user = await self.repo.create(email=email, password_hash=hashed, full_name=full_name)

        logger.info("user_registered", user_id=str(user.id), email=email)

        # Publish event (best-effort, don't fail registration if Redis is down)
        try:
            await publish_event("user.registered", {
                "user_id": str(user.id),
                "email": email,
                "full_name": full_name,
            })
        except Exception:
            logger.warning("event_publish_failed", event_type="user.registered")

        return UserResponse.model_validate(user)

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.repo.get_by_email(email)

        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        settings = get_settings()
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        logger.info("user_logged_in", user_id=str(user.id))

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.jwt_access_token_expire_minutes * 60,
        )

    async def get_current_user(self, user_id) -> UserResponse:
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return UserResponse.model_validate(user)