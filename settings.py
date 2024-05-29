import os

PG_URL = os.environ.get("PG_URL", "")
PG_FLOWRUN_TABLE_NAME = os.environ.get("PG_FLOWRUN_TABLE_NAME", "flows_flowrun")
FLOWRUN_USE_ORG = bool(int(os.environ.get("FLOWRUN_USE_ORG", "1")))

ES_URL = os.environ.get("ES_URL", "")
ES_FLOWRUN_INDEX_NAME = os.environ.get("ES_FLOWRUN_INDEX_NAME", "flowruns")
FLOW_RUN_BATCH_LIMIT = int(os.environ.get("FLOW_RUN_BATCH_LIMIT", 100))
EMPTY_ORG_SLEEP = float(os.environ.get("EMPTY_ORG_SLEEP", 0.1))
BATCH_PROCESSING_TIME_LIMIT = int(os.environ.get("BATCH_PROCESSING_TIME_LIMIT", 30))
START_RUN_OFFSET = int(os.environ.get("START_RUN_OFFSET", 60))
FLOW_LAST_INDEXED_FIELD = os.environ.get("FLOW_LAST_INDEXED_FIELD", "modified_on")
ORG_RANGE_FROM = int(os.environ.get("ORG_RANGE_FROM", 0))
ORG_RANGE_TO = int(os.environ.get("ORG_RANGE_TO", 2000))
IS_LAST_ORG_BATCH = bool(int(os.environ.get("IS_LAST_ORG_BATCH", "0")))

if os.environ.get("ALLOWED_ORGS", "") != "":
    ALLOWED_ORGS = list(int(org) for org in os.environ.get("ALLOWED_ORGS").split(","))
else:
    ALLOWED_ORGS = []

if os.environ.get("ALLOWED_PROJECTS", "") != "":
    ALLOWED_PROJECTS = list(
        proj for proj in os.environ.get("ALLOWED_PROJECTS").split(",")
    )
else:
    ALLOWED_PROJECTS = []

CONNECTION_TYPE = os.environ.get("CONNECTION_TYPE", "pool")
WAIT_TIME_RETRY = int(os.environ.get("WAIT_TIME_RETRY", 10))

PROCESS_TYPE = os.environ.get("PROCESS_TYPE", "BULK")
CONSUMER_MAIN_DELAY = int(os.environ.get("CONSUMER_MAIN_DELAY", 1000))

USE_SENTRY = bool(int(os.environ.get("USE_SENTRY", "0")))
SENTRY_DSN = os.environ.get("SENTRY_DSN", None)
