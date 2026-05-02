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

from app.models.match_result import MatchResult  # noqa: F401

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


def _strip_schemas(metadata):
    for table in metadata.tables.values():
        table.schema = None


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    _strip_schemas(Base.metadata)
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


@pytest.fixture
def sample_resume_skills() -> list[dict]:
    return [
        {"skill_name": "python", "category": "programming_language", "confidence": 1.0},
        {"skill_name": "bash", "category": "programming_language", "confidence": 1.0},
        {"skill_name": "javascript", "category": "programming_language", "confidence": 1.0},
        {"skill_name": "docker", "category": "containerization", "confidence": 1.0},
        {"skill_name": "kubernetes", "category": "container_orchestration", "confidence": 1.0},
        {"skill_name": "helm", "category": "container_orchestration", "confidence": 1.0},
        {"skill_name": "jenkins", "category": "ci_cd", "confidence": 1.0},
        {"skill_name": "github_actions", "category": "ci_cd", "confidence": 1.0},
        {"skill_name": "aws", "category": "cloud_platform", "confidence": 1.0},
        {"skill_name": "aws_ec2", "category": "cloud_compute", "confidence": 1.0},
        {"skill_name": "aws_s3", "category": "cloud_storage", "confidence": 1.0},
        {"skill_name": "terraform", "category": "infrastructure_as_code", "confidence": 1.0},
        {"skill_name": "grafana", "category": "monitoring", "confidence": 1.0},
        {"skill_name": "prometheus", "category": "monitoring", "confidence": 1.0},
        {"skill_name": "postgresql", "category": "database", "confidence": 1.0},
        {"skill_name": "redis", "category": "database", "confidence": 1.0},
        {"skill_name": "linux", "category": "operating_system", "confidence": 1.0},
        {"skill_name": "git", "category": "version_control", "confidence": 1.0},
    ]


@pytest.fixture
def sample_jd_text() -> str:
    return """
    Senior DevOps Engineer - TechCorp

    We are looking for a Senior DevOps Engineer to join our infrastructure team.

    Required Skills:
    - Strong experience with Python and Bash scripting
    - Expertise in Docker and Kubernetes for container orchestration
    - Experience with CI/CD tools such as Jenkins or GitLab CI
    - AWS cloud experience (EC2, S3, IAM, Lambda)
    - Infrastructure as Code using Terraform or CloudFormation
    - Monitoring with Grafana, Prometheus, and Alertmanager
    - Strong Linux administration skills
    - Experience with PostgreSQL and Redis

    Nice to Have:
    - Experience with Golang or Rust
    - ArgoCD or FluxCD for GitOps
    - Service mesh experience (Istio or Linkerd)
    - Kafka or RabbitMQ for event streaming

    Requirements:
    - 3+ years of DevOps/SRE experience
    - Bachelor's degree in Computer Science or related field
    """