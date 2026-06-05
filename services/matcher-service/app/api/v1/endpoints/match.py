import asyncio
import logging
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.match import MatchRequest, MatchResponse
from app.services.matcher_service import MatcherService
from resumeradar_common.auth.dependencies import get_current_user
from resumeradar_common.database.session import get_db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
async def run_match(
    request: MatchRequest,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        service = MatcherService(db)
        result = await asyncio.wait_for(
            service.match_resume_to_jd(
                user_id=user_id,
                request=request,         # ← pass the whole request object
            ),
            timeout=60.0,
        )
        return result
    except asyncio.TimeoutError:
        logger.error("Match analysis timed out")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Match analysis timed out. Please try again in 30 seconds.",
        )
    except Exception as e:
        logger.error(f"Match analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Match analysis failed: {str(e)}",
        )


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(
    match_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        service = MatcherService(db)
        repo = service.repo
        result = await repo.get_by_id(match_id, user_id)
        if not result:
            raise HTTPException(status_code=404, detail="Match result not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get match failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))