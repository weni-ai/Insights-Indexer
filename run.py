import redis
import settings
import time
import threading

from datetime import datetime, timedelta

from shared.processors import ObjectETLProcessor

from flowrun.storage.elasticsearch import FlowRunElasticSearch
from flowrun.storage.postgresql import FlowRunPostgreSQL
from flowrun.transformer import flowrun_sql_to_elasticsearch_transformer
from shared.lua_scripts import (
    pop_item_from_list_then_add_to_sorted_set_with_timestamp,
    pop_old_items_from_sorted_set_then_add_to_list,
)

from db.redis.connection import get_connection as get_redis_connection

FlowRunPGtoES = ObjectETLProcessor(
    object_transformer=flowrun_sql_to_elasticsearch_transformer,
    storage_from=FlowRunPostgreSQL(),
    storage_to=FlowRunElasticSearch(),
)


class RedisListAndXSetReliableQueue:
    def __init__(
        self,
        wait_list: str,
        process_list: str,
        max_time: int = 10,
        data_processor: ObjectETLProcessor = FlowRunPGtoES,
    ) -> None:
        self.wait_list = wait_list
        self.process_list = process_list
        self.max_time = max_time
        self.data_processor = data_processor

    def set_connection(self, conn: redis.client.Redis):
        self.conn = conn

    def _handle_proc_queue(self):
        max_time_timestamp = int(
            (datetime.now() - timedelta(seconds=self.max_time)).timestamp()
        )
        self.conn.eval(
            pop_old_items_from_sorted_set_then_add_to_list,
            2,
            self.process_list,
            self.wait_list,
            max_time_timestamp,
        )

    def _handle_wait_queue(self):

        run_id = self.conn.eval(
            pop_item_from_list_then_add_to_sorted_set_with_timestamp,
            2,
            self.wait_list,
            self.process_list,
            int(time.time()),
        )
        if run_id is None:
            return
        processor_status = self.data_processor.execute(run_id)
        if processor_status:
            self.conn.zrem(self.process_list, run_id)

    def handle(self):
        self._handle_wait_queue()
        self._handle_proc_queue()


def start():
    rqc = RedisListAndXSetReliableQueue(
        wait_list=settings.FLOWRUN_WAIT_LIST,
        process_list=settings.FLOWRUN_PROC_LIST,
        max_time=900,
    )

    while True:
        try:
            rqc.set_connection(get_redis_connection())
            rqc.handle()
        except ConnectionRefusedError as error:  # treat redis errors aswell
            print(f"[-] Connection error: {error}")
            print("    [+] Reconnecting in 5 seconds...")
            time.sleep(settings.REDIS_WAIT_TIME_RETRY)

        except KeyboardInterrupt:
            print("[-] Connection closed: Keyboard Interrupt")
            break

        except Exception as error:
            print("[-] error on handling events:", type(error), error)
            time.sleep(settings.REDIS_WAIT_TIME_RETRY)


if __name__ == "__main__":
    for i in range(0, settings.CONSUMER_THREADS):
        thread = threading.Thread(target=start, name=f"indexer-consumer-t{i}")
        thread.start()
        print(f"[+] Started indexer consumer thread {i}")

    while True:
        time.sleep(settings.CONSUMER_MAIN_DELAY)
