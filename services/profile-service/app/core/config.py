from functools import lru_cache
from resumeradar_common.config.settings import CommonSettings


class ProfileSettings(CommonSettings):
    service_name: str = "profile-service"
    db_schema: str = "profile_db"
    max_file_size_mb: int = 10
    allowed_extensions: list[str] = ["pdf", "docx"]
    resume_s3_prefix: str = "resumes"
    spacy_model: str = "en_core_web_sm"

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


@lru_cache()
def get_profile_settings() -> ProfileSettings:
    return ProfileSettings()