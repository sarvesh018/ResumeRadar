from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.analytics import (
    DashboardSummary, FunnelResponse, ResumeComparisonResponse,
    ScoreCallbackResponse, TrendResponse,
)
from app.services.analytics_service import AnalyticsService
from resumeradar_common.auth.dependencies import get_current_user
from resumeradar_common.database.session import get_db

router = APIRouter()


@router.get("/analytics/dashboard", response_model=DashboardSummary)
async def get_dashboard(
    user_id: UUID = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_dashboard_summary(user_id)


@router.get("/analytics/funnel", response_model=FunnelResponse)
async def get_funnel(
    user_id: UUID = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_funnel(user_id)


@router.get("/analytics/resumes", response_model=ResumeComparisonResponse)
async def get_resume_comparison(
    user_id: UUID = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_resume_comparison(user_id)


@router.get("/analytics/score-callback", response_model=ScoreCallbackResponse)
async def get_score_callback(
    user_id: UUID = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_score_vs_callback(user_id)


@router.get("/analytics/trends", response_model=TrendResponse)
async def get_trends(
    period: str = Query(default="weekly", regex="^(weekly|monthly)$"),
    user_id: UUID = Depends(get_current_user), db: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(db)
    return await service.get_trends(user_id, period=period)