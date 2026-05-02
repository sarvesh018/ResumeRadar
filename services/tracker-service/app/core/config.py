from functools import lru_cache
from resumeradar_common.config.settings import CommonSettings


class TrackerSettings(CommonSettings):
    service_name: str = "tracker-service"
    db_schema: str = "tracker_db"
    max_applications_per_user: int = 500
    follow_up_reminder_days: int = 7


@lru_cache()
def get_tracker_settings() -> TrackerSettings:
    return TrackerSettings()