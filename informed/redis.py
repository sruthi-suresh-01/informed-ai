from informed.config import RedisConfig
from redis.asyncio import Redis


def init_redis_client(redis_config: RedisConfig) -> Redis:
    redis_client = Redis(
        host=redis_config.host,
        port=redis_config.port,
        db=redis_config.db,
        decode_responses=redis_config.decode_responses,
    )
    return redis_client
