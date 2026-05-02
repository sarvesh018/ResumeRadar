from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.match_result import MatchResult


class MatchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> MatchResult:
        result = MatchResult(**kwargs)
        self.db.add(result)
        await self.db.flush()
        return result

    async def get_by_id(self, match_id: UUID, user_id: UUID) -> MatchResult | None:
        result = await self.db.execute(
            select(MatchResult).where(MatchResult.id == match_id, MatchResult.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID, limit: int = 20, offset: int = 0) -> list[MatchResult]:
        result = await self.db.execute(
            select(MatchResult).where(MatchResult.user_id == user_id)
            .order_by(MatchResult.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def list_by_resume(self, user_id: UUID, resume_id: UUID) -> list[MatchResult]:
        result = await self.db.execute(
            select(MatchResult).where(MatchResult.user_id == user_id, MatchResult.resume_id == resume_id)
            .order_by(MatchResult.created_at.desc())
        )
        return list(result.scalars().all())