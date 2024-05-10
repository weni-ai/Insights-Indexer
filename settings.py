import os

PG_URL = os.environ.get("PG_URL", "")
PG_FLOWRUN_TABLE_NAME = os.environ.get("PG_FLOWRUN_TABLE_NAME", "flows_flowrun")
ES_URL = os.environ.get("ES_URL", "")
ES_FLOWRUN_INDEX_NAME = os.environ.get("ES_FLOWRUN_INDEX_NAME", "flowruns_develop")
CONNECTION_TYPE = os.environ.get("CONNECTION_TYPE", "pool")
REDIS_WAIT_TIME_RETRY = os.environ.get("REDIS_WAIT_TIME_RETRY", 5)
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
