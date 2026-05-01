from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from resumeradar_common.config.settings import get_settings


def create_engine_from_settings(settings=None, use_pool: bool = True):
    if settings is None:
        settings = get_settings()

    engine_kwargs = {
        "echo": settings.is_development,
    }

    if use_pool:
        engine_kwargs.update({
            "pool_size": settings.db_pool_size,
            "max_overflow": settings.db_pool_max_overflow,
            "pool_pre_ping": True,
            "pool_recycle": 300,
        })
    else:
        engine_kwargs["poolclass"] = NullPool

    return create_async_engine(settings.database_url, **engine_kwargs)


_engine = None
_session_factory = None


def get_session_factory():
    global _engine, _session_factory
    if _session_factory is None:
        _engine = create_engine_from_settings()
        _session_factory = async_sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise