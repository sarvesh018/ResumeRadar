import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

correlation_id_ctx: ContextVar[str] = ContextVar("correlation_id", default="")
HEADER_NAME = "X-Correlation-ID"


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        incoming_id = request.headers.get(HEADER_NAME)
        request_id = incoming_id or str(uuid.uuid4())
        token = correlation_id_ctx.set(request_id)

        try:
            response = await call_next(request)
            response.headers[HEADER_NAME] = request_id
            return response
        finally:
            correlation_id_ctx.reset(token)


def get_correlation_id() -> str:
    return correlation_id_ctx.get()