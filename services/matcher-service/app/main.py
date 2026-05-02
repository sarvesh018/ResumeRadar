from fastapi import FastAPI
from app.api.v1.router import router as v1_router
from app.core.config import get_matcher_settings
from resumeradar_common.database.health import health_router
from resumeradar_common.middleware.correlation_id import CorrelationIdMiddleware
from resumeradar_common.middleware.error_handler import register_error_handlers
from resumeradar_common.middleware.request_logger import RequestLoggerMiddleware
from resumeradar_common.observability.logging import setup_logging
from resumeradar_common.observability.metrics import setup_prometheus


def create_app() -> FastAPI:
    settings = get_matcher_settings()
    setup_logging(service_name=settings.service_name, log_level=settings.log_level)

    app = FastAPI(
        title="ResumeRadar Matcher Service",
        version="1.0.0",
        docs_url="/api/v1/match/docs",
        openapi_url="/api/v1/match/openapi.json",
    )

    app.add_middleware(RequestLoggerMiddleware)
    app.add_middleware(CorrelationIdMiddleware)
    register_error_handlers(app)
    setup_prometheus(app, service_name=settings.service_name)

    app.include_router(health_router, prefix="/health", tags=["health"])
    app.include_router(v1_router, prefix="/api/v1", tags=["match"])

    return app


app = create_app()