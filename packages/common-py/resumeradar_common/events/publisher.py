import json
from datetime import UTC, datetime

import redis.asyncio as aioredis
import structlog

from resumeradar_common.config.settings import get_settings
from resumeradar_common.middleware.correlation_id import get_correlation_id

logger = structlog.get_logger()

_redis_client = None


async def get_redis_client() -> aioredis.Redis:
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = aioredis.from_url(
            settings.redis_url,
            max_connections=settings.redis_max_connections,
            decode_responses=True,
        )
    return _redis_client


async def publish_event(event_type: str, payload: dict) -> None:
    client = await get_redis_client()
    envelope = {
        "event_type": event_type,
        "timestamp": datetime.now(UTC).isoformat(),
        "correlation_id": get_correlation_id(),
        "payload": payload,
    }
    message = json.dumps(envelope, default=str)
    await client.publish(event_type, message)
    logger.info("event_published", event_type=event_type, correlation_id=get_correlation_id())


async def subscribe_events(*event_types: str):
    client = await get_redis_client()
    pubsub = client.pubsub()
    await pubsub.subscribe(*event_types)
    logger.info("event_subscribed", channels=list(event_types))
    async for message in pubsub.listen():
        if message["type"] == "message":
            try:
                yield json.loads(message["data"])
            except json.JSONDecodeError:
                logger.error("event_parse_error", raw_data=message["data"])