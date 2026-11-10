"""End-to-end tests for the OrgPrompt Click CLI using CliRunner."""

import json
from pathlib import Path
from click.testing import CliRunner
import pytest

from orgprompt.cli import cli, main


FLAGSHIP_PROBLEM = (
    "Architecting, economically modeling, stress-testing, and governing a next-generation "
    "Sovereign AI + 6G Edge Telecommunications + Real-Time Financial Settlement Infrastructure "
    "under strict regulatory, capital, latency, and adversarial security constraints."
)


@pytest.fixture
def runner() -> CliRunner:
    """Provides a Click CliRunner instance."""
    return CliRunner()


def test_cli_entry_point_aliases():
    """Verifies that `main` and `cli` are aliases for console script entry points."""
    assert main == cli
    assert callable(cli)


def test_cli_help(runner: CliRunner):
    """Verifies top-level help lists all registered command groups."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "team" in result.output
    assert "search" in result.output
    assert "role" in result.output
    assert "benchmark" in result.output


def test_cli_team_synthesize_text(runner: CliRunner):
    """Verifies `team synthesize` command outputs formatted table and DAG overview."""
    result = runner.invoke(
        cli,
        ["team", "synthesize", "--problem", FLAGSHIP_PROBLEM, "--min-roles", "8"],
    )
    assert result.exit_code == 0, f"Command failed with output: {result.output}"
    assert "Dynamic Team Synthesis Complete" in result.output or "Assembled Cross-Functional Team" in result.output
    assert "Execution DAG" in result.output or "Topological Order" in result.output


def test_cli_team_synthesize_json(runner: CliRunner):
    """Verifies `team synthesize --json` outputs structured valid JSON."""
    result = runner.invoke(
        cli,
        ["team", "synthesize", "--problem", FLAGSHIP_PROBLEM, "--min-roles", "8", "--json"],
    )
    assert result.exit_code == 0, f"Command failed with output: {result.output}"
    data = json.loads(result.output)
    assert data["roles_count"] >= 8
    assert data["industries_count"] >= 3
    assert data["is_acyclic"] is True
    assert len(data["roles"]) >= 8
    assert len(data["dag_nodes"]) > 0


def test_cli_team_execute_json(runner: CliRunner, tmp_path: Path):
    """Verifies `team execute --json` executes DAG and saves artifacts to output directory."""
    out_dir = tmp_path / "artifacts"
    result = runner.invoke(
        cli,
        [
            "team",
            "execute",
            "--problem",
            FLAGSHIP_PROBLEM,
            "--output-dir",
            str(out_dir),
            "--min-roles",
            "8",
            "--json",
        ],
    )
    assert result.exit_code == 0, f"Command failed with output: {result.output}"
    data = json.loads(result.output)
    assert data["status"] == "COMPLETED"
    assert len(data["intermediate_artifacts"]) >= 6
    assert len(data["red_team_findings"]) >= 1
    assert len(data["upstream_revisions"]) >= 1
    assert len(data["solution_dossier"].split()) >= 5000

    # Verify files written to disk
    assert out_dir.exists()
    for art in data["intermediate_artifacts"]:
        art_path = out_dir / art
        assert art_path.exists()
        assert art_path.stat().st_size > 0


def test_cli_search_query_text(runner: CliRunner):
    """Verifies `search query` displays formatted results table."""
    result = runner.invoke(cli, ["search", "query", "Shannon capacity O-RAN", "--hybrid"])
    assert result.exit_code == 0, f"Command failed with output: {result.output}"
    assert "Hybrid Search Results" in result.output
    assert "RRF Score" in result.output


def test_cli_search_query_json(runner: CliRunner):
    """Verifies `search query --json` outputs structured candidate rankings with dual scores."""
    result = runner.invoke(
        cli,
        ["search", "query", "Sub-millisecond FPGA trading", "--top-k", "5", "--json"],
    )
    assert result.exit_code == 0, f"Command failed with output: {result.output}"
    data = json.loads(result.output)
    assert data["query"] == "Sub-millisecond FPGA trading"
    assert len(data["results"]) == 5
    first = data["results"][0]
    assert "rrf_score" in first
    assert "sparse_score" in first
    assert "dense_score" in first


def test_cli_search_query_missing_arg(runner: CliRunner):
    """Verifies `search query` requires a query string."""
    result = runner.invoke(cli, ["search", "query"])
    assert result.exit_code != 0
    assert "Error" in result.output or "Usage" in result.output


def test_cli_role_generate_json(runner: CliRunner):
    """Verifies `role generate --json` dynamically synthesizes and validates a role."""
    import uuid
    import sqlite3
    from orgprompt.db.connection import get_default_db_path

    unique_token = uuid.uuid4().hex[:6]
    test_role_name = f"Dynamic Swarm Specialist {unique_token}"
    test_slug = f"dynamic_swarm_specialist_{unique_token}"

    try:
        result = runner.invoke(
            cli,
            [
                "role",
                "generate",
                "--name",
                test_role_name,
                "--industry",
                "Semiconductors & Advanced Manufacturing",
                "--seniority",
                "PRINCIPAL_STAFF",
                "--json",
            ],
        )
        assert result.exit_code == 0, f"Command failed with output: {result.output}"
        data = json.loads(result.output)
        assert data["slug"] == test_slug
        assert data["character_count"] >= 1200
        assert "## 1. Role Identity & Exemplar Lineage" in data["system_prompt"]
        assert "## 6. Concrete Output Artifact Schemas" in data["system_prompt"]
    finally:
        # Clean up database
        conn = sqlite3.connect(get_default_db_path())
        c = conn.cursor()
        c.execute("DELETE FROM canonical_roles WHERE slug = ?", (test_slug,))
        c.execute("DELETE FROM role_edges WHERE source_role_id = ? OR target_role_id = ?", (f"role_{test_slug}", f"role_{test_slug}"))
        conn.commit()
        conn.close()


def test_cli_benchmark_run_json(runner: CliRunner):
    """Verifies `benchmark run --json` evaluates queries and meets target thresholds."""
    result = runner.invoke(cli, ["benchmark", "run", "--k", "10", "--json"])
    assert result.exit_code == 0, f"Command failed with output: {result.output}"
    data = json.loads(result.output)
    assert data["queries_evaluated"] >= 25
    assert data["recall_at_10"] >= 0.85
    assert data["mrr"] >= 0.70
    assert data["dual_contribution_verified"] is True
    assert data["passes"] is True
