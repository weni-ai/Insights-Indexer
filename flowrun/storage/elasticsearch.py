import settings

from db.elasticsearch.connection import get_connection
from shared.storage import GenericStorage
from flowrun.dtos import FlowRunElasticSearchDTO


class FlowRunElasticSearch(GenericStorage):
    _index_name: str = settings.ES_FLOWRUN_INDEX_NAME

    def get_by_pk(self, identifier: str) -> FlowRunElasticSearchDTO:
        try:
            es_flow_run = get_connection().get(index=self._index_name, uuid=identifier)[
                "_source"
            ]
        except (AttributeError, TypeError) as err:
            print("[-] Elasticsearch Get error: ", type(err), err)
            return None
        return es_flow_run  # FlowRunElasticSearchDTO.from_dict(es_flow_run)

    def insert(self, new_obj: dict) -> bool:
        es_flow_run = get_connection().index(
            index=self._index_name, body=new_obj.to_dict()
        )
        return es_flow_run.get("ok")
