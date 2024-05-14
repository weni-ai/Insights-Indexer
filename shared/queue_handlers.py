import settings
import redis
import time

from datetime import datetime, timedelta

from shared.processors import ObjectETLProcessor

from shared.lua_scripts import (
    add_item_to_sorted_set_with_timestamp,
    pop_item_from_list_then_add_to_sorted_set_with_timestamp,
    pop_old_items_from_sorted_set_then_add_to_list,
)


class RedisQueueHandlerBase:
    def set_connection(self, conn: redis.client.Redis):
        self.conn = conn


def move_from_xset_to_list_when_old_with_lua_script(
    conn: redis.client.Redis, xset_from: str, list_to: str, max_time: int = 120
):
    max_time_timestamp = int((datetime.now() - timedelta(seconds=max_time)).timestamp())
    conn.eval(
        pop_old_items_from_sorted_set_then_add_to_list,
        2,
        xset_from,
        list_to,
        max_time_timestamp,
    )


def get_id_from_list_and_move_to_xset_and_add_timestamp_with_lua_script(
    conn: redis.client.Redis, list_from: str, xset_to: str
):
    obj_id = conn.eval(
        pop_item_from_list_then_add_to_sorted_set_with_timestamp,
        2,
        list_from,
        xset_to,
        int(time.time()),
    )
    return obj_id


def block_get_id_from_list_and_move_to_xset_and_add_timestamp_with_lua_script(
    conn: redis.client.Redis, list_from: str, xset_to: str
):
    """This might not be reliable, if some error occurs after blpop and before eval, the task might will lost"""
    obj_id = conn.blpop(list_from, timeout=settings.REDIS_BLPOP_TIMEOUT)
    conn.eval(
        add_item_to_sorted_set_with_timestamp, 1, xset_to, int(time.time()), obj_id
    )
    return obj_id


class RedisListAndXSetReliableQueue(RedisQueueHandlerBase):
    def __init__(
        self,
        wait_list: str,
        process_list: str,
        data_processor: ObjectETLProcessor,
        max_time: int = 10,
        process_queue_handler: callable = move_from_xset_to_list_when_old_with_lua_script,
        wait_queue_handler: callable = get_id_from_list_and_move_to_xset_and_add_timestamp_with_lua_script,
    ) -> None:
        self.wait_list = wait_list
        self.process_list = process_list
        self.max_time = max_time
        self.data_processor = data_processor
        self.process_queue_handler = process_queue_handler
        self.wait_queue_handler = wait_queue_handler

    def _handle_proc_queue(self):
        self.process_queue_handler(
            conn=self.conn,
            xset_from=self.process_list,
            list_to=self.wait_list,
            max_time=self.max_time,
        )

    def _handle_wait_queue(self):
        return self.wait_queue_handler(self.conn, self.wait_list, self.process_list)

    def _process_obj(self):
        obj_id = self._handle_wait_queue()
        if obj_id is None:
            return
        processor_status = self.data_processor.execute(obj_id)
        if processor_status:
            self.conn.zrem(self.process_list, obj_id)

    def handle(self):
        self._process_obj()
        self._handle_proc_queue()
