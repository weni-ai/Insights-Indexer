import logging
import settings
from psycopg import connect

from psycopg_pool import ConnectionPool, NullConnectionPool
from psycopg.rows import dict_row
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

logging.getLogger("psycopg.pool").setLevel(logging.INFO)

PG_URL = settings.PG_URL

db_pool = NullConnectionPool(
    max_size=5,
    conninfo=PG_URL,
    check=ConnectionPool.check_connection,
)


@contextmanager
def get_connection():
    if settings.CONNECTION_TYPE == "pool":
        with db_pool.connection() as conn:
            yield conn
    else:
        with connect(PG_URL) as conn:
            yield conn


@contextmanager
def get_cursor():
    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            yield cur
