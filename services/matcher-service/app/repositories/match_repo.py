import logging
from uuid import UUID
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match_result import MatchResult

logger = logging.getLogger(__name__)


class MatchRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: UUID,
        resume_id: UUID,
        jd_text: str,
        jd_company: str | None,
        jd_role: str | None,
        keyword_score: float,
        semantic_score: float,
        taxonomy_score: float,
        overall_score: float,
        matched_skills: list,
        missing_skills: list,
        suggestions: list,
        resume_skill_count: int = 0,
        jd_skill_count: int = 0,
    ) -> MatchResult:
        result = MatchResult(
            user_id=user_id,
            resume_id=resume_id,
            jd_text=jd_text,
            jd_company=jd_company,
            jd_role=jd_role,
            keyword_score=keyword_score,
            semantic_score=semantic_score,
            taxonomy_score=taxonomy_score,
            overall_score=overall_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            suggestions=suggestions,
        )
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        return result

    async def get_by_id(self, match_id: UUID, user_id: UUID) -> MatchResult | None:
        stmt = select(MatchResult).where(
            MatchResult.id == match_id,
            MatchResult.user_id == user_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_history(
        self,
        user_id: UUID,
        resume_id: UUID | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[MatchResult]:
        stmt = (
            select(MatchResult)
            .where(MatchResult.user_id == user_id)
            .order_by(MatchResult.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if resume_id:
            stmt = stmt.where(MatchResult.resume_id == resume_id)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_resume_skills(self, resume_id: UUID) -> list:
        """
        Fetch skills for a resume from profile_db.resume_skills.
        Both schemas (matcher_db and profile_db) are in the same
        PostgreSQL instance, so rr_admin can query across schemas.
        """
        try:
            stmt = text("""
                SELECT skill_name, category, confidence
                FROM profile_db.resume_skills
                WHERE resume_id = :resume_id
                ORDER BY confidence DESC
            """)
            result = await self.db.execute(stmt, {"resume_id": str(resume_id)})
            rows = result.fetchall()

            # Return simple objects with skill_name attribute
            class SkillRow:
                def __init__(self, skill_name, category, confidence):
                    self.skill_name = skill_name
                    self.category = category
                    self.confidence = confidence

            return [SkillRow(r.skill_name, r.category, r.confidence) for r in rows]

        except Exception as e:
            logger.warning(f"Could not fetch resume skills from profile_db: {e}")
            return []