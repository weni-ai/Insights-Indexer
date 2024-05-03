import redis
import redis.client
from time import sleep, time
from datetime import datetime, timedelta

from shared.processors import ObjectETLProcessor

from flowrun.storage.elasticsearch import FlowRunElasticSearch
from flowrun.storage.postgresql import FlowRunPostgreSQL
from flowrun.transformer import flowrun_sql_to_elasticsearch_transformer
from shared.lua_scripts import (
    pop_item_from_list_then_add_to_sorted_set_with_timestamp,
    pop_old_items_from_sorted_set_then_add_to_list,
)

FlowRunPGtoES = ObjectETLProcessor(
    object_transformer=flowrun_sql_to_elasticsearch_transformer,
    storage_from=FlowRunPostgreSQL(),
    storage_to=FlowRunElasticSearch(),
)


pool = redis.ConnectionPool(
    host="localhost", port=6379, max_connections=10, decode_responses=True
)

wait_list = "flowruns:wait"
process_list = "flowruns:proc"


def handle_proc_queue(
    conn: redis.client.Redis, wait_list: str, process_list: str, calc_time: int = 10
):
    max_time = int((datetime.now() - timedelta(seconds=calc_time)).timestamp())
    conn.eval(
        pop_old_items_from_sorted_set_then_add_to_list,
        2,
        process_list,
        wait_list,
        max_time,
    )


while True:
    r = redis.Redis(connection_pool=pool)
    run_id = r.eval(
        pop_item_from_list_then_add_to_sorted_set_with_timestamp,
        2,
        wait_list,
        process_list,
        int(time()),
    )
    # run_id = r.blmove("flowruns:wait", "flowruns:proc", timeout=10)
    if run_id is None:
        continue
    handler_status = FlowRunPGtoES.execute(run_id)
    if handler_status:
        # r.lrem(name="flowruns:proc", count=0, value=run_id)
        r.zrem("flowruns:proc", run_id)

    handle_proc_queue(
        conn=r,
        wait_list=wait_list,
        process_list=process_list,
    )  # checa se há runs a mais de 15min em processamento, se sim, devolve-as para a fila de espera
