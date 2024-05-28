import redis
import settings

pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL, max_connections=2, decode_responses=True
)


def get_connection():
    return redis.Redis(connection_pool=pool)
