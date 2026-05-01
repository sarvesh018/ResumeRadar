from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt

from resumeradar_common.config.settings import get_settings


class TokenError(Exception):
    pass


def create_access_token(user_id: UUID, settings=None) -> str:
    if settings is None:
        settings = get_settings()

    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_refresh_token(user_id: UUID, settings=None) -> str:
    if settings is None:
        settings = get_settings()

    expire = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_token_expire_days)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(UTC),
        "type": "refresh",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(token: str, expected_type: str = "access", settings=None) -> dict:
    if settings is None:
        settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as e:
        raise TokenError(f"Invalid token: {e}") from e

    if payload.get("type") != expected_type:
        raise TokenError(f"Expected {expected_type} token, got {payload.get('type')}")

    return payload


def get_user_id_from_token(token: str, settings=None) -> UUID:
    payload = verify_token(token, expected_type="access", settings=settings)
    try:
        return UUID(payload["sub"])
    except (KeyError, ValueError) as e:
        raise TokenError(f"Token missing valid 'sub' claim: {e}") from e