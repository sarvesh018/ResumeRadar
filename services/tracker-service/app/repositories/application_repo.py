from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.application import Application, StatusEvent


class ApplicationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> Application:
        app = Application(**kwargs)
        self.db.add(app)
        await self.db.flush()
        return app

    async def get_by_id(self, app_id: UUID, user_id: UUID) -> Application | None:
        result = await self.db.execute(
            select(Application)
            .options(selectinload(Application.status_events))
            .where(Application.id == app_id, Application.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(
        self, user_id: UUID, status: str | None = None,
        limit: int = 50, offset: int = 0,
    ) -> list[Application]:
        query = select(Application).where(Application.user_id == user_id)
        if status:
            query = query.where(Application.status == status)
        query = query.order_by(Application.applied_date.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def list_grouped_by_status(self, user_id: UUID) -> dict[str, list[Application]]:
        result = await self.db.execute(
            select(Application).where(Application.user_id == user_id)
            .order_by(Application.applied_date.desc())
        )
        apps = result.scalars().all()
        grouped: dict[str, list[Application]] = {}
        for app in apps:
            if app.status not in grouped:
                grouped[app.status] = []
            grouped[app.status].append(app)
        return grouped

    async def count_by_user(self, user_id: UUID) -> int:
        result = await self.db.execute(
            select(func.count(Application.id)).where(Application.user_id == user_id)
        )
        return result.scalar_one()

    async def update(self, app: Application, data: dict) -> Application:
        for key, value in data.items():
            if hasattr(app, key):
                setattr(app, key, value)
        await self.db.flush()
        await self.db.refresh(app)
        return app

    async def delete(self, app: Application) -> None:
        await self.db.delete(app)
        await self.db.flush()

    async def add_status_event(
        self, application_id: UUID,
        from_status: str | None, to_status: str,
        notes: str | None = None,
    ) -> StatusEvent:
        event = StatusEvent(
            application_id=application_id,
            from_status=from_status,
            to_status=to_status,
            notes=notes,
        )
        self.db.add(event)
        await self.db.flush()
        return event

    async def get_status_events(self, application_id: UUID) -> list[StatusEvent]:
        result = await self.db.execute(
            select(StatusEvent)
            .where(StatusEvent.application_id == application_id)
            .order_by(StatusEvent.created_at)
        )
        return list(result.scalars().all())