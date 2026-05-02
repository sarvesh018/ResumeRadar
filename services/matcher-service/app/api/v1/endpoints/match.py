from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.match import MatchHistoryResponse, MatchRequest, MatchResponse
from app.services.matcher_service import MatcherService
from resumeradar_common.auth.dependencies import get_current_user
from resumeradar_common.database.session import get_db

router = APIRouter()


@router.post("/match", response_model=MatchResponse, status_code=201)
async def run_match(
    request: MatchRequest,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MatcherService(db)
    return await service.match_resume_to_jd(
        user_id=user_id, resume_id=request.resume_id,
        jd_text=request.jd_text, jd_company=request.jd_company,
        jd_role=request.jd_role,
    )


@router.get("/match/history", response_model=MatchHistoryResponse)
async def get_match_history(
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MatcherService(db)
    return await service.get_history(user_id)


@router.get("/match/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MatcherService(db)
    return await service.get_match(match_id, user_id)