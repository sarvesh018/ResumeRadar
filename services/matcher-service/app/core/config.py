from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class MatcherSettings(BaseSettings):
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    db_schema: str = "matcher_db"
    environment: str = "development"
    log_level: str = "INFO"
    service_name: str = "matcher-service" 

    # Profile service URL (to fetch user profile skills)
    profile_service_url: str = "http://profile-service:8002"

    # Groq API key (optional — falls back to spaCy if not set)
    # Get free key at: https://console.groq.com (no credit card needed)
    groq_api_key: Optional[str] = None
    groq_model: str = "llama3-8b-8192"

    # Scoring weights (must sum to 1.0)
    weight_keyword: float = 0.50
    weight_semantic: float = 0.30
    weight_taxonomy: float = 0.20

    # Only count semantic match if similarity exceeds this
    semantic_match_threshold: float = 0.65

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_matcher_settings() -> MatcherSettings:
    return MatcherSettings()


# Module-level instance for direct import (used in matcher_service.py)
settings = get_matcher_settings()