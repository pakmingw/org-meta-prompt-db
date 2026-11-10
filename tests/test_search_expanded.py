"""Tests for upgraded HybridSearchEngine and expanded >=35-query benchmark."""

import json
import pytest
from click.testing import CliRunner

from orgprompt.cli import cli
from orgprompt.db.connection import get_default_db_path
from orgprompt.search.benchmark import DEFAULT_BENCHMARK_QUERIES, RetrievalBenchmark
from orgprompt.search.hybrid import HybridSearchEngine


@pytest.fixture
def search_engine():
    return HybridSearchEngine.build_from_db(get_default_db_path())


def test_benchmark_query_suite_size():
    assert len(DEFAULT_BENCHMARK_QUERIES) >= 35
    assert len(DEFAULT_BENCHMARK_QUERIES) == 36


def test_hybrid_search_expanded_benchmark(search_engine):
    report = RetrievalBenchmark.run_benchmark(search_engine, k=10)

    assert report.queries_evaluated >= 35
    assert report.recall_at_10 >= 0.85, f"Recall@10 {report.recall_at_10:.4f} is below 0.85"
    assert report.mrr >= 0.70, f"MRR {report.mrr:.4f} is below 0.70"
    assert report.dual_contribution_verified is True
    assert report.sparse_contributions > 0
    assert report.dense_contributions > 0
    assert report.passes is True


def test_hybrid_search_tools_and_use_cases(search_engine):
    # Query matching specific enterprise tool
    res_tool = search_engine.search("SAP S/4HANA supply chain enterprise ERP", top_k=5)
    assert len(res_tool.results) > 0
    # At least one result must have dual score attribution
    assert any(r.has_sparse_contribution or r.has_dense_contribution for r in res_tool.results)

    # Query matching subagent swarm role
    res_swarm = search_engine.search("Quantitative Modeler Monte Carlo simulation subagent", top_k=5)
    assert len(res_swarm.results) > 0


def test_cli_benchmark_run_json():
    runner = CliRunner()
    res = runner.invoke(cli, ["benchmark", "run", "--json"])

    assert res.exit_code == 0
    data = json.loads(res.output)
    assert data["queries_evaluated"] >= 35
    assert data["recall_at_10"] >= 0.85
    assert data["mrr"] >= 0.70
    assert data["dual_contribution_verified"] is True
    assert data["passes"] is True
