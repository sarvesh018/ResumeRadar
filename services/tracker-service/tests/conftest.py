import asyncio
from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from resumeradar_common.auth.jwt_handler import create_access_token
from resumeradar_common.database.base_model import Base
from resumeradar_common.database.session import get_db

from app.models.application import Application, StatusEvent  # noqa: F401

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


def _strip_schemas(metadata):
    for table in metadata.tables.values():
        table.schema = None


def _fix_foreign_keys(metadata):
    for table in metadata.tables.values():
        for fk in table.foreign_keys:
            if "." in fk._colspec and fk._colspec.count(".") == 2:
                parts = fk._colspec.split(".")
                fk._colspec = f"{parts[1]}.{parts[2]}"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    _strip_schemas(Base.metadata)
    _fix_foreign_keys(Base.metadata)
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def client(test_db: AsyncSession) -> TestClient:
    from app.main import app

    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> dict:
    test_user_id = uuid4()
    token = create_access_token(test_user_id)
    return {
        "Authorization": f"Bearer {token}",
        "_user_id": str(test_user_id),
    }