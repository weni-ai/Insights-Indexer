import pytest

from .transformer import flow_run_pg_to_es_transformer


def test_flow_run_format():
    raw_data = {}
    treated_flowrun = flow_run_pg_to_es_transformer(raw_data)
    assert treated_flowrun == {}
