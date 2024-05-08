import json
from typing import Any


def flowrun_sql_to_elasticsearch_transformer(
    pg_flow_run: dict[str, Any]
) -> dict[str, Any]:
    """
    pg -> {
        id: int
        uuid: uuid
        status: str(1)
        created_on: timestamp
        exited_on: timestamp
        responded: bool
        results: str(json)
        delete_reason: str(1)
        exit_type: str(1)
        contact_uuid: str
        contact_name: str
        contact_urn: str
        flow_uuid: str
        flow_name: str
        project_uuid: uuid
    }
    es -> {
        _id: int
        uuid: str
        status: str
        created_on: timestamp
        exited_on: timestamp
        responded: bool
        delete_reason: str(1)
        exit_type: str(1)
        contact_uuid: str
        contact_name: str
        contact_urn: str
        flow_uuid: str
        flow_name: str
        project_uuid: uuid
        results: str(json) -> {
            x.value: str|int
            x.category: str
            y.value: str|int
            y.category: str
            z.value: str|int
            z.category: str
            (...)
        }

    }
    """
    es_flow_run = {**pg_flow_run, "results": {}}
    results = json.loads(pg_flow_run.get("results", {}))
    result = es_flow_run.get("results", {})

    for k, v in results.items():
        value = v.get("value")
        result[f"{k}.value"] = int(value) if value.isdigit() else value
        result[f"{k}.category"] = v.get("category")
    es_flow_run["results"] = result
    return es_flow_run


def flowrun_in_memory_transformer(flow_run: dict[str, Any]) -> dict[str, Any]:
    return {**flow_run, "transformed": True}
