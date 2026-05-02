from functools import lru_cache
from resumeradar_common.config.settings import CommonSettings


class AnalyticsSettings(CommonSettings):
    service_name: str = "analytics-service"
    db_schema: str = "analytics_db"
    min_applications_for_stats: int = 3
    positive_statuses: list[str] = ["screening", "interviewing", "offer"]


@lru_cache()
def get_analytics_settings() -> AnalyticsSettings:
    return AnalyticsSettings()