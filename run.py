import settings
import time


from shared.processors import BulkObjectETLProcessor

from flowrun.storage.elasticsearch import FlowRunElasticSearch
from flowrun.storage.postgresql import FlowRunPostgreSQL, OrgPostgreSQL
from flowrun.transformer import (
    bulk_flowrun_sql_to_elasticsearch_transformer,
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
            print(f"\n[-] Connection error: {error}")
            print("\n[+] Reconnecting in 10 seconds...")
            time.sleep(settings.WAIT_TIME_RETRY)
            continue

        except KeyboardInterrupt:
            print("\n[-] Connection closed: Keyboard Interrupt")
            break

        except Exception as error:
            print("\n[-] error on handling events:", type(error), error)
            time.sleep(settings.WAIT_TIME_RETRY)
            continue

        time.sleep(settings.CONSUMER_MAIN_DELAY)


if __name__ == "__main__":
    bulk_process()
    print("\n[+] Service running on bulk process single thread mode")
