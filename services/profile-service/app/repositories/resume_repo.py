from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.resume import Resume, ResumeSkill


class ResumeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: UUID, version_name: str, file_url: str,
                     file_type: str, raw_text: str | None = None,
                     parsed_data: dict | None = None) -> Resume:
        resume = Resume(user_id=user_id, version_name=version_name,
                       file_url=file_url, file_type=file_type,
                       raw_text=raw_text, parsed_data=parsed_data)
        self.db.add(resume)
        await self.db.flush()
        return resume

    async def get_by_id(self, resume_id: UUID, user_id: UUID) -> Resume | None:
        result = await self.db.execute(
            select(Resume).options(selectinload(Resume.skills))
            .where(Resume.id == resume_id, Resume.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: UUID) -> list[Resume]:
        result = await self.db.execute(
            select(Resume).where(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, resume: Resume) -> None:
        await self.db.delete(resume)
        await self.db.flush()

    async def count_by_user(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(Resume.id)).where(Resume.user_id == user_id)
        )
        return result.scalar_one()

    async def add_skills(self, resume_id: UUID, skills: list[dict]) -> list[ResumeSkill]:
        skill_objects = []
        for skill_data in skills:
            skill = ResumeSkill(
                resume_id=resume_id, skill_name=skill_data["skill_name"],
                category=skill_data.get("category"),
                confidence=skill_data.get("confidence", 1.0),
            )
            self.db.add(skill)
            skill_objects.append(skill)
        await self.db.flush()
        return skill_objects

    async def get_skills(self, resume_id: UUID) -> list[ResumeSkill]:
        result = await self.db.execute(
            select(ResumeSkill).where(ResumeSkill.resume_id == resume_id)
            .order_by(ResumeSkill.confidence.desc())
        )
        return list(result.scalars().all())