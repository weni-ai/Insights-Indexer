import os

PG_URL = os.environ.get("PG_URL", "")
PG_FLOWRUN_TABLE_NAME = os.environ.get("PG_FLOWRUN_TABLE_NAME", "flows_flowrun")
ES_URL = os.environ.get("ES_URL", "")
ES_FLOWRUN_INDEX_NAME = os.environ.get("ES_FLOWRUN_INDEX_NAME", "flowruns")
CONNECTION_TYPE = os.environ.get("CONNECTION_TYPE", "single")
