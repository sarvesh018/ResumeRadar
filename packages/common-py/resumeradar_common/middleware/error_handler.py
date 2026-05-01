import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from resumeradar_common.config.settings import get_settings
from resumeradar_common.middleware.correlation_id import get_correlation_id

logger = structlog.get_logger()


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "type": "http_error",
                "title": exc.detail if isinstance(exc.detail, str) else "Error",
                "status": exc.status_code,
                "correlation_id": get_correlation_id(),
            },
        )

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "type": "validation_error",
                "title": "Request validation failed",
                "status": 422,
                "detail": exc.errors(),
                "correlation_id": get_correlation_id(),
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        settings = get_settings()

        logger.error(
            "unhandled_exception",
            error_type=type(exc).__name__,
            error_message=str(exc),
            path=str(request.url.path),
            correlation_id=get_correlation_id(),
        )

        detail = str(exc) if settings.is_development else "An unexpected error occurred"

        return JSONResponse(
            status_code=500,
            content={
                "type": "server_error",
                "title": "Internal Server Error",
                "status": 500,
                "detail": detail,
                "correlation_id": get_correlation_id(),
            },
        )