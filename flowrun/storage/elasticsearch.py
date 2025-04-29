import logging
from datetime import datetime, timezone, timedelta
import time

import settings

from db.elasticsearch.connection import get_connection
from shared.storage import GenericStorage

logger = logging.getLogger(__name__)

class FlowRunElasticSearch(GenericStorage):
    _index_name: str = settings.ES_FLOWRUN_INDEX_NAME

    def get_by_pk(self, identifier: str) -> dict:
        start_time = time.time()
        try:
            es_flow_run = get_connection().search(
                index=self._index_name,
                body={"size": 1, "query": {"term": {"uuid": identifier}}},
            )["hits"]["hits"][0]["_source"]
        except (AttributeError, TypeError, IndexError) as err:
            logging.warning(f"Elasticsearch Get error: {type(err)} {err}")
            return None
        finally:
            elapsed_time = time.time() - start_time
            logging.info(f"get_by_pk executed in {elapsed_time:.2f} seconds")
        return es_flow_run

    def get_last_indexed(self, project_uuid):
        start_time = time.time()
        try:
            es_flow_run = get_connection().search(
                index=self._index_name,
                body={
                    "size": 1,
                    "sort": {settings.FLOW_LAST_INDEXED_FIELD: "desc"},
                    "query": {"term": {"project_uuid": project_uuid}},
                },
            )["hits"]["hits"][0]["_source"]
        except (AttributeError, TypeError, IndexError) as err:
            logging.warning(f"While listing flowruns: {type(err)} {err}")
            return {}
        finally:
            elapsed_time = time.time() - start_time
            logging.info(f"get_last_indexed executed in {elapsed_time:.2f} seconds")
        return es_flow_run

    def get_last_indexed_timestamp(self, project_uuid):
        start_time = time.time()
        try:
            result = self.get_last_indexed(project_uuid).get(
                settings.FLOW_LAST_INDEXED_FIELD,
                datetime.now(timezone.utc) - timedelta(minutes=settings.START_RUN_OFFSET),
            )
        finally:
            elapsed_time = time.time() - start_time
            logging.info(f"get_last_indexed_timestamp executed in {elapsed_time:.2f} seconds")
        return result

    def insert(self, new_obj: dict) -> bool:
        start_time = time.time()
        try:
            es_flow_run = get_connection().index(index=self._index_name, body=new_obj)
        finally:
            elapsed_time = time.time() - start_time
            logging.info(f"insert executed in {elapsed_time:.2f} seconds")
        return es_flow_run["result"] == "created"

    def bulk_insert(self, batch) -> bool:
        start_time = time.time()
        try:
            run_batch = get_connection().bulk(index=self._index_name, body=batch)
            logging.info(
                f"took {run_batch.get('took', 'err')}ms to index {len(run_batch.get('items', batch))} documents"
            )
        finally:
            elapsed_time = time.time() - start_time
            logging.info(f"bulk_insert executed in {elapsed_time:.2f} seconds")
