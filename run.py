import sentry_sdk

import logging
import time

import settings

# from db.redis.connection import get_connection as get_redis_connection
from shared.processors import BulkObjectETLProcessor

from flowrun.storage.elasticsearch import FlowRunElasticSearch
from flowrun.storage.postgresql import FlowRunPostgreSQL, OrgPostgreSQL
from flowrun.transformer import (
    bulk_flowrun_sql_to_elasticsearch_transformer,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

BulkFlowRunPGtoES = BulkObjectETLProcessor(
    object_transformer=bulk_flowrun_sql_to_elasticsearch_transformer,
    storage_to=FlowRunElasticSearch(),
    storage_from=FlowRunPostgreSQL(),
    storage_org=OrgPostgreSQL(),
)


def bulk_process():
    while True:
        try:
            BulkFlowRunPGtoES.execute()
        except ConnectionRefusedError as error:
            logging.info(f"[-] Connection error: {error}")
            logging.info("[+] Reconnecting in 10 seconds...")
            time.sleep(settings.WAIT_TIME_RETRY)
            continue

        except KeyboardInterrupt:
            logging.info("[-] Connection closed: Keyboard Interrupt")
            break

        except Exception as error:
            logging.info(f"[-] error on handling events: {type(error)}, {error}")
            time.sleep(settings.WAIT_TIME_RETRY)
            continue

        time.sleep(settings.CONSUMER_MAIN_DELAY)


def main():
    if settings.USE_SENTRY:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            enable_tracing=True,
        )
    # redis = get_redis_connection()
    # batch_position = redis.get(settings.REDIS_BATCH_POSITION)
    # if batch_position
    logging.info("Service running on bulk process single thread mode")
    bulk_process()


if __name__ == "__main__":
    main()
