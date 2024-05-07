import logging
import settings
from psycopg import connect

from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

logging.getLogger("psycopg.pool").setLevel(logging.INFO)

db_pool = ConnectionPool(
    minconn=1,
    maxconn=5,
    conninfo=settings.PG_URL,
    check=ConnectionPool.check_connection,
    open=True if settings.CONNECTION_TYPE == "pool" else False,
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
