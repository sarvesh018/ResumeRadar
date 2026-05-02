from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.profile import Profile


class ProfileRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_user_id(self, user_id: UUID) -> Profile | None:
        result = await self.db.execute(select(Profile).where(Profile.user_id == user_id))
        return result.scalar_one_or_none()

    async def create(self, user_id: UUID, full_name: str | None = None) -> Profile:
        profile = Profile(user_id=user_id, full_name=full_name)
        self.db.add(profile)
        await self.db.flush()
        return profile

    async def update(self, profile: Profile, data: dict) -> Profile:
        for key, value in data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        await self.db.flush()
        await self.db.refresh(profile)
        return profile