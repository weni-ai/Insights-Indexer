import settings
import time
import threading


from shared.processors import ObjectETLProcessor, BulkObjectETLProcessor
from shared.queue_handlers import RedisListAndXSetReliableQueue

if settings.BLOCK_WAIT_HANDLER is True:
    from shared.queue_handlers import (
        block_get_id_from_list_and_move_to_xset_and_add_timestamp_with_lua_script as wait_queue_handler,
    )
else:
    from shared.queue_handlers import (
        get_id_from_list_and_move_to_xset_and_add_timestamp_with_lua_script as wait_queue_handler,
    )


from flowrun.storage.elasticsearch import FlowRunElasticSearch
from flowrun.storage.postgresql import FlowRunPostgreSQL
from flowrun.transformer import (
    bulk_flowrun_sql_to_elasticsearch_transformer,
    flowrun_sql_to_elasticsearch_transformer,
)

from db.redis.connection import get_connection as get_redis_connection

FlowRunPGtoES = ObjectETLProcessor(
    object_transformer=flowrun_sql_to_elasticsearch_transformer,
    storage_from=FlowRunPostgreSQL(),
    storage_to=FlowRunElasticSearch(),
)

BulkFlowRunPGtoES = BulkObjectETLProcessor(
    object_transformer=bulk_flowrun_sql_to_elasticsearch_transformer,
    storage_from=FlowRunPostgreSQL(),
    storage_to=FlowRunElasticSearch(),
)


def single_process():
    rqc = RedisListAndXSetReliableQueue(
        wait_list=settings.FLOWRUN_WAIT_LIST,
        process_list=settings.FLOWRUN_PROC_LIST,
        max_time=400,
        data_processor=FlowRunPGtoES,
        wait_queue_handler=wait_queue_handler,
    )

    while True:
        try:
            rqc.set_connection(get_redis_connection())
            rqc.handle()
        except ConnectionRefusedError as error:  # treat redis errors aswell
            print(f"\n[-] Connection error: {error}")
            print("\n[+] Reconnecting in 5 seconds...")
            time.sleep(int(settings.REDIS_WAIT_TIME_RETRY))

        except KeyboardInterrupt:
            print("\n[-] Connection closed: Keyboard Interrupt")
            break

        except Exception as error:
            print("\n[-] error on handling events:", type(error), error)
            time.sleep(int(settings.REDIS_WAIT_TIME_RETRY))


def bulk_process():
    while True:
        try:
            BulkFlowRunPGtoES.execute()
        except ConnectionRefusedError as error:
            print(f"\n[-] Connection error: {error}")
            print("\n[+] Reconnecting in 10 seconds...")
            time.sleep(int(settings.REDIS_WAIT_TIME_RETRY))

        except KeyboardInterrupt:
            print("\n[-] Connection closed: Keyboard Interrupt")
            break

        except Exception as error:
            print("\n[-] error on handling events:", type(error), error)
            time.sleep(int(settings.REDIS_WAIT_TIME_RETRY))


def start():
    if settings.PROCESS_TYPE == "BULK":
        bulk_process()
        print("\n[+] Service running on bulk process single thread mode")
    else:
        if settings.USE_THREADS:
            for i in range(0, int(settings.CONSUMER_THREADS)):
                thread = threading.Thread(target=start, name=f"indexer-consumer-t{i}")
                thread.start()
                print(f"\n[+] Started indexer consumer thread {i}")
            while True:
                time.sleep(int(settings.CONSUMER_MAIN_DELAY))
        else:
            start()
            print("\n[+] Service running on single thread mode")


if __name__ == "__main__":
    start()
