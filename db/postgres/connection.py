import logging
import settings
from psycopg import connect

from psycopg_pool import ConnectionPool, NullConnectionPool
from psycopg.rows import dict_row
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

logging.getLogger("psycopg.pool").setLevel(logging.INFO)

db_pool = NullConnectionPool(
    max_size=5,
    conninfo=settings.PG_URL,
    check=ConnectionPool.check_connection,
)


@contextmanager
def get_connection():
    if settings.CONNECTION_TYPE == "pool":
        with db_pool.connection(row_factory=dict_row) as conn:
            yield conn
    else:
        with connect(settings.PG_URL, row_factory=dict_row) as conn:
            yield conn


@contextmanager
def get_cursor():
    with get_connection() as conn:
        with conn.cursor() as cur:
            yield cur
