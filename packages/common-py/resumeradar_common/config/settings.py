from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    environment: str = "development"
    log_level: str = "INFO"
    service_name: str = "unknown"

    # Database
    database_url: str = "postgresql+asyncpg://rr_admin:localdev@localhost:5432/resumeradar"
    db_schema: str = "public"
    db_pool_size: int = 5
    db_pool_max_overflow: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 10

    # JWT Auth
    jwt_secret: str = "change-this-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # AWS
    aws_region: str = "ap-south-1"
    aws_s3_bucket: str = "resumeradar-resumes-dev"

    # Inter-Service URLs
    auth_service_url: str = "http://auth-service:8001"
    profile_service_url: str = "http://profile-service:8002"
    matcher_service_url: str = "http://matcher-service:8003"
    tracker_service_url: str = "http://tracker-service:8004"
    analytics_service_url: str = "http://analytics-service:8005"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache()
def get_settings() -> CommonSettings:
    return CommonSettings()