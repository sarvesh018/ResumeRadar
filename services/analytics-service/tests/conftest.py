import asyncio
from collections.abc import AsyncGenerator
from datetime import date
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from resumeradar_common.auth.jwt_handler import create_access_token
from resumeradar_common.database.base_model import Base
from resumeradar_common.database.session import get_db

from app.models.read_models import ApplicationRead  # noqa: F401

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

TEST_USER_ID = uuid4()
RESUME_V1_ID = uuid4()
RESUME_V2_ID = uuid4()


def _strip_schemas(metadata):
    for table in metadata.tables.values():
        table.schema = None


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


async def _seed_test_data(session: AsyncSession):
    """
    10 test applications:
    Resume V1 (4 apps): screening, rejected, applied, interviewing -> 50% response
    Resume V2 (4 apps): offer, interviewing, screening, rejected -> 75% response
    No resume (2 apps): applied, rejected
    """
    test_apps = [
        {"company": "Google", "role_title": "DevOps Engineer", "status": "screening",
         "resume_id": RESUME_V1_ID, "match_score": 0.82, "applied_date": date(2024, 1, 8)},
        {"company": "Meta", "role_title": "SRE", "status": "rejected",
         "resume_id": RESUME_V1_ID, "match_score": 0.45, "applied_date": date(2024, 1, 15)},
        {"company": "Netflix", "role_title": "DevOps Engineer", "status": "applied",
         "resume_id": RESUME_V1_ID, "match_score": 0.68, "applied_date": date(2024, 2, 1)},
        {"company": "Apple", "role_title": "Platform Engineer", "status": "interviewing",
         "resume_id": RESUME_V1_ID, "match_score": 0.75, "applied_date": date(2024, 2, 5)},
        {"company": "Amazon", "role_title": "DevOps Engineer", "status": "offer",
         "resume_id": RESUME_V2_ID, "match_score": 0.95, "applied_date": date(2024, 1, 10)},
        {"company": "Microsoft", "role_title": "SRE", "status": "interviewing",
         "resume_id": RESUME_V2_ID, "match_score": 0.88, "applied_date": date(2024, 1, 20)},
        {"company": "Stripe", "role_title": "DevOps Engineer", "status": "screening",
         "resume_id": RESUME_V2_ID, "match_score": 0.72, "applied_date": date(2024, 2, 1)},
        {"company": "Uber", "role_title": "Platform Engineer", "status": "rejected",
         "resume_id": RESUME_V2_ID, "match_score": 0.35, "applied_date": date(2024, 2, 10)},
        {"company": "Spotify", "role_title": "DevOps Engineer", "status": "applied",
         "resume_id": None, "match_score": None, "applied_date": date(2024, 1, 25)},
        {"company": "Airbnb", "role_title": "SRE", "status": "rejected",
         "resume_id": None, "match_score": 0.30, "applied_date": date(2024, 2, 15)},
    ]

    for app_data in test_apps:
        app = ApplicationRead(
            user_id=TEST_USER_ID,
            company=app_data["company"],
            role_title=app_data["role_title"],
            status=app_data["status"],
            resume_id=app_data["resume_id"],
            match_score=app_data["match_score"],
            applied_date=app_data["applied_date"],
        )
        session.add(app)
    await session.flush()


@pytest_asyncio.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    _strip_schemas(Base.metadata)
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        await _seed_test_data(session)
        await session.commit()
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
    token = create_access_token(TEST_USER_ID)
    return {
        "Authorization": f"Bearer {token}",
        "_user_id": str(TEST_USER_ID),
    }