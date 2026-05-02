from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.application import (
    ApplicationCreateRequest, ApplicationDetailResponse,
    ApplicationListResponse, ApplicationResponse,
    ApplicationUpdateRequest, KanbanBoardResponse, StatusUpdateRequest,
)
from app.services.tracker_service import TrackerService
from resumeradar_common.auth.dependencies import get_current_user
from resumeradar_common.database.session import get_db
from resumeradar_common.schemas.pagination import MessageResponse

router = APIRouter()


@router.post("/applications", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    data: ApplicationCreateRequest,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TrackerService(db)
    return await service.create_application(user_id, data)


@router.get("/applications", response_model=ApplicationListResponse)
async def list_applications(
    status_filter: str | None = Query(default=None, alias="status"),
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TrackerService(db)
    return await service.list_applications(user_id, status_filter=status_filter)


@router.get("/applications/board", response_model=KanbanBoardResponse)
async def get_kanban_board(
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TrackerService(db)
    return await service.get_kanban_board(user_id)


@router.get("/applications/{app_id}", response_model=ApplicationDetailResponse)
async def get_application(
    app_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TrackerService(db)
    return await service.get_application(app_id, user_id)


@router.put("/applications/{app_id}", response_model=ApplicationResponse)
async def update_application(
    app_id: UUID, data: ApplicationUpdateRequest,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TrackerService(db)
    return await service.update_application(app_id, user_id, data)


@router.patch("/applications/{app_id}/status", response_model=ApplicationDetailResponse)
async def update_status(
    app_id: UUID, data: StatusUpdateRequest,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TrackerService(db)
    return await service.update_status(app_id, user_id, data)


@router.delete("/applications/{app_id}", response_model=MessageResponse)
async def delete_application(
    app_id: UUID,
    user_id: UUID = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = TrackerService(db)
    await service.delete_application(app_id, user_id)
    return MessageResponse(message="Application deleted successfully")