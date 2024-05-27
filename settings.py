import os

PG_URL = os.environ.get("PG_URL", "")
PG_FLOWRUN_TABLE_NAME = os.environ.get("PG_FLOWRUN_TABLE_NAME", "flows_flowrun")
FLOWRUN_USE_ORG = bool(int(os.environ.get("FLOWRUN_USE_ORG", "1")))

ES_URL = os.environ.get("ES_URL", "")
ES_FLOWRUN_INDEX_NAME = os.environ.get("ES_FLOWRUN_INDEX_NAME", "flowruns")
FLOW_RUN_BATCH_LIMIT = int(os.environ.get("FLOW_RUN_BATCH_LIMIT", 100))
EMPTY_ORG_SLEEP = float(os.environ.get("EMPTY_ORG_SLEEP", 0.1))
BATCH_PROCESSING_TIME_LIMIT = int(os.environ.get("BATCH_PROCESSING_TIME_LIMIT", 30))
START_RUN_OFFSET = int(os.environ.get("START_RUN_OFFSET", 30))
FLOW_LAST_INDEXED_FIELD = os.environ.get("FLOW_LAST_INDEXED_FIELD", "modified_on")

CONNECTION_TYPE = os.environ.get("CONNECTION_TYPE", "pool")
WAIT_TIME_RETRY = int(os.environ.get("WAIT_TIME_RETRY", 10))

PROCESS_TYPE = os.environ.get("PROCESS_TYPE", "BULK")
CONSUMER_MAIN_DELAY = int(os.environ.get("CONSUMER_MAIN_DELAY", 1000))

USE_SENTRY = bool(int(os.environ.get("USE_SENTRY", "0")))
SENTRY_DSN = os.environ.get("SENTRY_DSN", None)
