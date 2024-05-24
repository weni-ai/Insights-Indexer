import logging
import time

import settings

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
            logging.info("[-] error on handling events:", type(error), error)
            time.sleep(settings.WAIT_TIME_RETRY)
            continue

        time.sleep(settings.CONSUMER_MAIN_DELAY)


def main():
    logging.info("Service running on bulk process single thread mode")
    bulk_process()


if __name__ == "__main__":
    main()
