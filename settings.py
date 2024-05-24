import os

PG_URL = os.environ.get("PG_URL", "")
PG_FLOWRUN_TABLE_NAME = os.environ.get("PG_FLOWRUN_TABLE_NAME", "flows_flowrun")
FLOWRUN_USE_ORG = bool(int(os.environ.get("FLOWRUN_USE_ORG", "1")))

ES_URL = os.environ.get("ES_URL", "")
ES_FLOWRUN_INDEX_NAME = os.environ.get("ES_FLOWRUN_INDEX_NAME", "flowruns")
FLOW_RUN_BATCH_LIMIT = int(os.environ.get("FLOW_RUN_BATCH_LIMIT", 100))
BATCH_PROCESSING_TIME_LIMIT = int(os.environ.get("BATCH_PROCESSING_TIME_LIMIT", 30))
FLOW_LAST_INDEXED_FIELD = os.environ.get("FLOW_LAST_INDEXED_FIELD", "modified_on")

CONNECTION_TYPE = os.environ.get("CONNECTION_TYPE", "pool")
REDIS_WAIT_TIME_RETRY = int(os.environ.get("REDIS_WAIT_TIME_RETRY", 10))
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

PROCESS_TYPE = os.environ.get("PROCESS_TYPE", "BULK")
USE_THREADS = os.environ.get("USE_THREADS", True)
CONSUMER_THREADS = int(os.environ.get("CONSUMER_THREADS", 3))
CONSUMER_MAIN_DELAY = int(os.environ.get("CONSUMER_MAIN_DELAY", 1000))
REDIS_BLPOP_TIMEOUT = int(os.environ.get("REDIS_BLPOP_TIMEOUT", 600))
BLOCK_WAIT_HANDLER = os.environ.get("BLOCK_WAIT_HANDLER", True)

FLOWRUN_PROC_LIST = os.environ.get("FLOWRUN_PROC_LIST", "flowruns:proc")
FLOWRUN_WAIT_LIST = os.environ.get("FLOWRUN_WAIT_LIST", "flowruns:wait")
