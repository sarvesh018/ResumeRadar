from datetime import date
from uuid import UUID

import structlog
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_tracker_settings
from app.core.status_machine import (
    ApplicationStatus, get_allowed_transitions, is_valid_transition,
)
from app.repositories.application_repo import ApplicationRepository
from app.schemas.application import (
    ApplicationCreateRequest, ApplicationDetailResponse,
    ApplicationListResponse, ApplicationResponse,
    ApplicationUpdateRequest, KanbanBoardResponse, KanbanColumn,
    StatusEventResponse, StatusUpdateRequest,
)

logger = structlog.get_logger()


class TrackerService:
    def __init__(self, db: AsyncSession):
        self.repo = ApplicationRepository(db)
        self.settings = get_tracker_settings()

    async def create_application(
        self, user_id: UUID, data: ApplicationCreateRequest,
    ) -> ApplicationResponse:
        count = await self.repo.count_by_user(user_id)
        if count >= self.settings.max_applications_per_user:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Maximum {self.settings.max_applications_per_user} applications reached",
            )

        applied_date = data.applied_date or date.today()

        app = await self.repo.create(
            user_id=user_id, company=data.company, role_title=data.role_title,
            resume_id=data.resume_id, match_result_id=data.match_result_id,
            jd_url=data.jd_url, salary_min=data.salary_min, salary_max=data.salary_max,
            location=data.location, is_remote=data.is_remote,
            status=data.status.value, applied_date=applied_date,
            match_score=data.match_score, notes=data.notes,
        )

        await self.repo.add_status_event(
            application_id=app.id, from_status=None,
            to_status=data.status.value, notes="Application created",
        )

        logger.info("application_created", user_id=str(user_id), app_id=str(app.id),
                     company=data.company, role=data.role_title)

        try:
            from resumeradar_common.events.publisher import publish_event
            await publish_event("application.created", {
                "user_id": str(user_id), "application_id": str(app.id),
                "company": data.company, "role_title": data.role_title,
                "status": data.status.value,
            })
        except Exception:
            logger.warning("event_publish_failed", event_type="application.created")

        return self._to_response(app)

    async def get_application(self, app_id: UUID, user_id: UUID) -> ApplicationDetailResponse:
        app = await self.repo.get_by_id(app_id, user_id)
        if app is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

        events_raw = await self.repo.get_status_events(app_id)
        events = [StatusEventResponse.model_validate(e) for e in events_raw]
        return ApplicationDetailResponse(**self._to_response(app).model_dump(), status_events=events)

    async def list_applications(
        self, user_id: UUID, status_filter: str | None = None,
    ) -> ApplicationListResponse:
        apps = await self.repo.list_by_user(user_id, status=status_filter)
        responses = [self._to_response(a) for a in apps]
        return ApplicationListResponse(applications=responses, total=len(responses))

    async def get_kanban_board(self, user_id: UUID) -> KanbanBoardResponse:
        grouped = await self.repo.list_grouped_by_status(user_id)
        column_order = [s.value for s in ApplicationStatus]
        columns = []
        total = 0
        for status_val in column_order:
            apps = grouped.get(status_val, [])
            columns.append(KanbanColumn(
                status=status_val, count=len(apps),
                applications=[self._to_response(a) for a in apps],
            ))
            total += len(apps)
        return KanbanBoardResponse(columns=columns, total=total)

    async def update_application(
        self, app_id: UUID, user_id: UUID, data: ApplicationUpdateRequest,
    ) -> ApplicationResponse:
        app = await self.repo.get_by_id(app_id, user_id)
        if app is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

        app = await self.repo.update(app, update_data)
        logger.info("application_updated", app_id=str(app_id), fields=list(update_data.keys()))
        return self._to_response(app)

    async def update_status(
        self, app_id: UUID, user_id: UUID, data: StatusUpdateRequest,
    ) -> ApplicationDetailResponse:
        app = await self.repo.get_by_id(app_id, user_id)
        if app is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")

        current = ApplicationStatus(app.status)
        target = data.status

        if not is_valid_transition(current, target):
            allowed = get_allowed_transitions(current)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot transition from '{current.value}' to '{target.value}'. "
                       f"Allowed transitions: {allowed}",
            )

        old_status = app.status
        update_data = {"status": target.value}
        if data.response_date:
            update_data["response_date"] = data.response_date
        app = await self.repo.update(app, update_data)

        await self.repo.add_status_event(
            application_id=app.id, from_status=old_status,
            to_status=target.value, notes=data.notes,
        )

        logger.info("application_status_changed", app_id=str(app_id),
                     from_status=old_status, to_status=target.value)

        try:
            from resumeradar_common.events.publisher import publish_event
            await publish_event("application.status_changed", {
                "user_id": str(user_id), "application_id": str(app_id),
                "from_status": old_status, "to_status": target.value,
            })
        except Exception:
            logger.warning("event_publish_failed", event_type="application.status_changed")

        events_raw = await self.repo.get_status_events(app_id)
        events = [StatusEventResponse.model_validate(e) for e in events_raw]
        return ApplicationDetailResponse(**self._to_response(app).model_dump(), status_events=events)

    async def delete_application(self, app_id: UUID, user_id: UUID) -> None:
        app = await self.repo.get_by_id(app_id, user_id)
        if app is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
        await self.repo.delete(app)
        logger.info("application_deleted", app_id=str(app_id))

    def _to_response(self, app) -> ApplicationResponse:
        try:
            current = ApplicationStatus(app.status)
            allowed = get_allowed_transitions(current)
        except ValueError:
            allowed = []

        return ApplicationResponse(
            id=app.id, user_id=app.user_id, company=app.company,
            role_title=app.role_title, resume_id=app.resume_id,
            match_result_id=app.match_result_id, jd_url=app.jd_url,
            salary_min=app.salary_min, salary_max=app.salary_max,
            location=app.location, is_remote=app.is_remote,
            status=app.status, applied_date=app.applied_date,
            response_date=app.response_date, match_score=app.match_score,
            notes=app.notes, allowed_transitions=allowed,
            created_at=app.created_at, updated_at=app.updated_at,
        )