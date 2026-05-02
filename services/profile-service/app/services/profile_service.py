import structlog
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.repositories.profile_repo import ProfileRepository
from app.schemas.profile import ProfileResponse, ProfileUpdateRequest

logger = structlog.get_logger()


class ProfileService:
    def __init__(self, db: AsyncSession):
        self.repo = ProfileRepository(db)

    async def get_or_create_profile(self, user_id: UUID) -> ProfileResponse:
        profile = await self.repo.get_by_user_id(user_id)
        if profile is None:
            logger.info("auto_creating_profile", user_id=str(user_id))
            profile = await self.repo.create(user_id=user_id)
        return ProfileResponse.model_validate(profile)

    async def update_profile(self, user_id: UUID, data: ProfileUpdateRequest) -> ProfileResponse:
        profile = await self.repo.get_by_user_id(user_id)
        if profile is None:
            profile = await self.repo.create(user_id=user_id)

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

        profile = await self.repo.update(profile, update_data)
        logger.info("profile_updated", user_id=str(user_id), fields=list(update_data.keys()))
        return ProfileResponse.model_validate(profile)