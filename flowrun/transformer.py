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
        values: list(dict) ->
        [
            {
                name: str
                value: str
                value_number: float
                category: str
            },
            {
                name: str
                value: str
                value_number: float
                category: str
            },
            {...}
        ]
    }
    """
    es_flow_run = {**pg_flow_run}
    results = json.loads(pg_flow_run.get("results", {}))
    new_results = []

    for k, v in results.items():
        new_obj = {}
        new_obj["name"] = k
        new_obj["category"] = v.get("category")

        value = v.get("value")
        new_obj["value"] = value

        if value.isdigit():
            new_obj["value_number"] = float(value)

        new_results.append(new_obj)
    es_flow_run.pop("results", None)
    es_flow_run["values"] = new_results
    return es_flow_run


def bulk_flowrun_sql_to_elasticsearch_transformer(pg_flow_run: list[dict]):
    obj = flowrun_sql_to_elasticsearch_transformer(pg_flow_run)
    _id = obj.pop("id")
    return [{"index": {"_id": _id}}, obj]


def flowrun_in_memory_transformer(flow_run: dict[str, Any]) -> dict[str, Any]:
    return {**flow_run, "transformed": True}
