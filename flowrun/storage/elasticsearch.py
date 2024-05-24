from datetime import datetime, timezone, timedelta

import settings

from db.elasticsearch.connection import get_connection
from shared.storage import GenericStorage


class FlowRunElasticSearch(GenericStorage):
    _index_name: str = settings.ES_FLOWRUN_INDEX_NAME

    def get_by_pk(self, identifier: str) -> dict:
        try:
            es_flow_run = get_connection().search(
                index=self._index_name,
                body={"size": 1, "query": {"term": {"uuid": identifier}}},
            )["hits"]["hits"][0]["_source"]
        except (AttributeError, TypeError, IndexError) as err:
            print("[-] <Warning> Elasticsearch Get error: ", type(err), err)
            return None
        return es_flow_run

    def get_last_indexed(self, org):
        try:
            es_flow_run = get_connection().search(
                index=self._index_name,
                body={
                    "size": 1,
                    "sort": {settings.FLOW_LAST_INDEXED_FIELD: "desc"},
                    "query": {"term": {"org_id": org}},
                },
            )["hits"]["hits"][0]["_source"]
        except (AttributeError, TypeError, IndexError) as err:
            print("[-] <Warning> Elasticsearch Get error: ", type(err), err)
            return {}
        return es_flow_run

    def get_last_indexed_timestamp(self, org):
        return self.get_last_indexed(org).get(
            settings.FLOW_LAST_INDEXED_FIELD,
            datetime.now(timezone.utc) - timedelta(minutes=settings.START_RUN_OFFSET),
        )

    def insert(self, new_obj: dict) -> bool:
        es_flow_run = get_connection().index(index=self._index_name, body=new_obj)
        return es_flow_run["result"] == "created"

    def bulk_insert(self, batch) -> bool:
        run_batch = get_connection().bulk(index=self._index_name, body=batch)
        print(
            f"took {run_batch.get('took', 'err')}ms to index {len(run_batch.get('items', batch))} documents"
        )
        return run_batch.get("errors", True)
