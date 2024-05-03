from typing import Any


def flowrun_sql_to_elasticsearch_transformer(
    pg_flow_run: dict[str, Any]
) -> dict[str, Any]:
    return {}


def flowrun_in_memory_transformer(flow_run: dict[str, Any]) -> dict[str, Any]:
    return {**flow_run, "transformed": True}
