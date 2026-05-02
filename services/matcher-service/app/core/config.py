from functools import lru_cache
from resumeradar_common.config.settings import CommonSettings


class MatcherSettings(CommonSettings):
    service_name: str = "matcher-service"
    db_schema: str = "matcher_db"

    # Matching engine weights (must sum to 1.0)
    keyword_weight: float = 0.4
    semantic_weight: float = 0.4
    taxonomy_weight: float = 0.2

    # Semantic model
    embedding_model: str = "all-MiniLM-L6-v2"

    # Fuzzy match threshold (0-100)
    fuzzy_match_threshold: int = 80

    # Semantic similarity threshold (0.0-1.0)
    semantic_similarity_threshold: float = 0.5

    profile_service_url: str = "http://profile-service:8002"


@lru_cache()
def get_matcher_settings() -> MatcherSettings:
    return MatcherSettings()