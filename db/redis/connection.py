import redis
import settings

pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL, port=6379, max_connections=10, decode_responses=True
)


def get_connection():
    return redis.Redis(connection_pool=pool)
