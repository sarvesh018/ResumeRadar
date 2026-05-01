from functools import lru_cache
from resumeradar_common.config.settings import CommonSettings


class AuthSettings(CommonSettings):
    service_name: str = "auth-service"
    db_schema: str = "auth_db"
    bcrypt_rounds: int = 12
    min_password_length: int = 8


@lru_cache()
def get_auth_settings() -> AuthSettings:
    return AuthSettings()