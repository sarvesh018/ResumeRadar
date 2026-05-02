from uuid import UUID
from sqlalchemy import select, func, case, cast, Float
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.read_models import ApplicationRead


class AnalyticsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_status_counts(self, user_id: UUID) -> list[dict]:
        result = await self.db.execute(
            select(ApplicationRead.status, func.count(ApplicationRead.id).label("count"))
            .where(ApplicationRead.user_id == user_id)
            .group_by(ApplicationRead.status)
        )
        return [{"status": row.status, "count": row.count} for row in result.all()]

    async def get_total_count(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(ApplicationRead.id)).where(ApplicationRead.user_id == user_id)
        )
        return result.scalar_one()

    async def get_resume_stats(self, user_id: UUID, positive_statuses: list[str]) -> list[dict]:
        total_col = func.count(ApplicationRead.id).label("total_sent")
        positive_col = func.count(
            case((ApplicationRead.status.in_(positive_statuses), ApplicationRead.id))
        ).label("positive_responses")
        avg_score_col = func.avg(ApplicationRead.match_score).label("avg_match_score")

        result = await self.db.execute(
            select(
                cast(ApplicationRead.resume_id, Float).label("resume_id_raw"),
                ApplicationRead.resume_id,
                total_col, positive_col, avg_score_col,
            )
            .where(ApplicationRead.user_id == user_id, ApplicationRead.resume_id.isnot(None))
            .group_by(ApplicationRead.resume_id)
        )
        return [
            {
                "resume_id": str(row.resume_id),
                "total_sent": row.total_sent,
                "positive_responses": row.positive_responses,
                "avg_match_score": round(float(row.avg_match_score), 3) if row.avg_match_score else None,
            }
            for row in result.all()
        ]

    async def get_applications_with_scores(self, user_id: UUID) -> list[dict]:
        result = await self.db.execute(
            select(ApplicationRead.match_score, ApplicationRead.status)
            .where(ApplicationRead.user_id == user_id, ApplicationRead.match_score.isnot(None))
        )
        return [{"match_score": row.match_score, "status": row.status} for row in result.all()]

    async def get_applications_by_period(self, user_id: UUID, positive_statuses: list[str]) -> list[dict]:
        result = await self.db.execute(
            select(ApplicationRead.applied_date, ApplicationRead.status)
            .where(ApplicationRead.user_id == user_id)
            .order_by(ApplicationRead.applied_date)
        )
        return [{"applied_date": row.applied_date, "status": row.status} for row in result.all()]

    async def get_summary_stats(self, user_id: UUID, positive_statuses: list[str]) -> dict:
        result = await self.db.execute(
            select(
                func.count(ApplicationRead.id).label("total"),
                func.count(case((ApplicationRead.status.notin_(["rejected", "withdrawn"]), ApplicationRead.id))).label("active"),
                func.count(case((ApplicationRead.status.in_(positive_statuses), ApplicationRead.id))).label("positive"),
                func.count(case((ApplicationRead.status.in_(["interviewing", "offer"]), ApplicationRead.id))).label("interviews"),
                func.count(case((ApplicationRead.status == "offer", ApplicationRead.id))).label("offers"),
                func.avg(ApplicationRead.match_score).label("avg_score"),
            )
            .where(ApplicationRead.user_id == user_id)
        )
        row = result.one()
        return {
            "total": row.total, "active": row.active, "positive": row.positive,
            "interviews": row.interviews, "offers": row.offers,
            "avg_score": round(float(row.avg_score), 3) if row.avg_score else None,
        }

    async def get_top_companies(self, user_id: UUID, limit: int = 1) -> list[dict]:
        result = await self.db.execute(
            select(ApplicationRead.company, func.count(ApplicationRead.id).label("count"))
            .where(ApplicationRead.user_id == user_id)
            .group_by(ApplicationRead.company)
            .order_by(func.count(ApplicationRead.id).desc())
            .limit(limit)
        )
        return [{"company": row.company, "count": row.count} for row in result.all()]

    async def get_top_roles(self, user_id: UUID, limit: int = 1) -> list[dict]:
        result = await self.db.execute(
            select(ApplicationRead.role_title, func.count(ApplicationRead.id).label("count"))
            .where(ApplicationRead.user_id == user_id)
            .group_by(ApplicationRead.role_title)
            .order_by(func.count(ApplicationRead.id).desc())
            .limit(limit)
        )
        return [{"role_title": row.role_title, "count": row.count} for row in result.all()]