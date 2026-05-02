from collections import defaultdict
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_analytics_settings
from app.repositories.analytics_repo import AnalyticsRepository
from app.schemas.analytics import (
    DashboardSummary, FunnelResponse, FunnelStage,
    ResumeComparisonResponse, ResumeVersionStats,
    ScoreBucket, ScoreCallbackResponse,
    TrendPoint, TrendResponse,
)

logger = structlog.get_logger()


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.repo = AnalyticsRepository(db)
        self.settings = get_analytics_settings()

    async def get_funnel(self, user_id: UUID) -> FunnelResponse:
        status_counts = await self.repo.get_status_counts(user_id)
        total = await self.repo.get_total_count(user_id)
        count_map = {s["status"]: s["count"] for s in status_counts}

        funnel_order = ["wishlist", "applied", "screening", "interviewing", "offer", "rejected", "withdrawn"]
        stages = []
        for status in funnel_order:
            count = count_map.get(status, 0)
            pct = round((count / total * 100), 1) if total > 0 else 0.0
            stages.append(FunnelStage(status=status, count=count, percentage=pct))

        positive = sum(count_map.get(s, 0) for s in self.settings.positive_statuses)
        interviews = count_map.get("interviewing", 0) + count_map.get("offer", 0)
        offers = count_map.get("offer", 0)

        return FunnelResponse(
            stages=stages, total_applications=total,
            overall_response_rate=round(positive / total, 3) if total > 0 else 0.0,
            interview_rate=round(interviews / total, 3) if total > 0 else 0.0,
            offer_rate=round(offers / total, 3) if total > 0 else 0.0,
        )

    async def get_resume_comparison(self, user_id: UUID) -> ResumeComparisonResponse:
        stats = await self.repo.get_resume_stats(user_id, self.settings.positive_statuses)

        versions = []
        for s in stats:
            rate = round(s["positive_responses"] / s["total_sent"], 3) if s["total_sent"] > 0 else 0.0
            versions.append(ResumeVersionStats(
                resume_id=s["resume_id"], total_sent=s["total_sent"],
                positive_responses=s["positive_responses"],
                response_rate=rate, avg_match_score=s["avg_match_score"],
            ))

        versions.sort(key=lambda v: -v.response_rate)

        best = None
        recommendation = "Upload resumes and track applications to see which version performs best."

        if len(versions) >= 2:
            best = versions[0].resume_id
            top_rate = versions[0].response_rate
            second_rate = versions[1].response_rate
            if top_rate > 0 and second_rate > 0:
                multiplier = round(top_rate / second_rate, 1)
                recommendation = (
                    f"Your best resume has a {top_rate:.0%} response rate, "
                    f"{multiplier}x better than the next version ({second_rate:.0%})."
                )
            elif top_rate > 0:
                recommendation = f"Your best resume has a {top_rate:.0%} response rate."
        elif len(versions) == 1 and versions[0].total_sent >= self.settings.min_applications_for_stats:
            best = versions[0].resume_id
            recommendation = f"You have one resume with a {versions[0].response_rate:.0%} response rate. Try creating a variant to A/B test."

        return ResumeComparisonResponse(versions=versions, best_version=best, recommendation=recommendation)

    async def get_score_vs_callback(self, user_id: UUID) -> ScoreCallbackResponse:
        apps = await self.repo.get_applications_with_scores(user_id)

        buckets_data: dict[int, dict] = {}
        for i in range(10):
            buckets_data[i] = {"total": 0, "positive": 0}

        min_effective = None
        positive_statuses = set(self.settings.positive_statuses)

        for app in apps:
            score = app["match_score"]
            bucket_idx = min(int(score * 10), 9)
            buckets_data[bucket_idx]["total"] += 1
            if app["status"] in positive_statuses:
                buckets_data[bucket_idx]["positive"] += 1
                if min_effective is None or score < min_effective:
                    min_effective = score

        buckets = []
        for i in range(10):
            low = i * 10
            high = (i + 1) * 10
            total = buckets_data[i]["total"]
            positive = buckets_data[i]["positive"]
            rate = round(positive / total, 3) if total > 0 else 0.0
            buckets.append(ScoreBucket(
                range_label=f"{low}-{high}%", min_score=low / 100, max_score=high / 100,
                total_applications=total, positive_responses=positive, response_rate=rate,
            ))

        sweet_spot = "Not enough data yet. Track more applications with match scores."
        high_bucket_rates = [(b.range_label, b.response_rate) for b in buckets if b.total_applications >= 2 and b.response_rate > 0]
        if high_bucket_rates:
            best = max(high_bucket_rates, key=lambda x: x[1])
            sweet_spot = f"Applications in the {best[0]} match score range have the highest callback rate ({best[1]:.0%})."

        return ScoreCallbackResponse(
            buckets=buckets, min_effective_score=round(min_effective, 2) if min_effective else None,
            sweet_spot=sweet_spot,
        )

    async def get_trends(self, user_id: UUID, period: str = "weekly") -> TrendResponse:
        apps = await self.repo.get_applications_by_period(user_id, self.settings.positive_statuses)
        positive_statuses = set(self.settings.positive_statuses)
        period_data: dict[str, dict] = defaultdict(lambda: {"applications": 0, "responses": 0})

        for app in apps:
            d = app["applied_date"]
            if period == "weekly":
                key = f"{d.year}-W{d.isocalendar()[1]:02d}"
            else:
                key = f"{d.year}-{d.month:02d}"
            period_data[key]["applications"] += 1
            if app["status"] in positive_statuses:
                period_data[key]["responses"] += 1

        sorted_periods = sorted(period_data.keys())
        data_points = []
        for p in sorted_periods:
            d = period_data[p]
            rate = round(d["responses"] / d["applications"], 3) if d["applications"] > 0 else 0.0
            data_points.append(TrendPoint(
                period=p, applications=d["applications"],
                responses=d["responses"], response_rate=rate,
            ))

        return TrendResponse(period_type=period, data_points=data_points, total_periods=len(data_points))

    async def get_dashboard_summary(self, user_id: UUID) -> DashboardSummary:
        stats = await self.repo.get_summary_stats(user_id, self.settings.positive_statuses)
        total = stats["total"]

        top_companies = await self.repo.get_top_companies(user_id)
        top_roles = await self.repo.get_top_roles(user_id)

        return DashboardSummary(
            total_applications=total,
            active_applications=stats["active"],
            response_rate=round(stats["positive"] / total, 3) if total > 0 else 0.0,
            interview_rate=round(stats["interviews"] / total, 3) if total > 0 else 0.0,
            offer_rate=round(stats["offers"] / total, 3) if total > 0 else 0.0,
            avg_match_score=stats["avg_score"],
            avg_days_to_response=None,
            most_applied_company=top_companies[0]["company"] if top_companies else None,
            most_applied_role=top_roles[0]["role_title"] if top_roles else None,
        )