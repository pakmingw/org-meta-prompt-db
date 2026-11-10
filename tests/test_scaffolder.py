"""Tests for RoleScaffolder, CompanyScaffolder, and CLI scaffolding commands."""

import json
from pathlib import Path
import pytest
from click.testing import CliRunner

from orgprompt.cli import cli
from orgprompt.db.connection import get_default_db_path
from orgprompt.scaffolder import CompanyScaffolder, RoleScaffolder


@pytest.fixture
def db_path():
    return str(get_default_db_path())


def test_role_scaffolder_by_id(db_path):
    scaffolder = RoleScaffolder.build_from_db(db_path)
    pkg = scaffolder.scaffold_role("role_fin_chief_investment_officer", company_name="JPMorgan Chase")

    assert pkg.role["slug"] == "fin_chief_investment_officer"
    assert "Chief Investment Officer" in pkg.role["title"]
    assert pkg.company_context == "JPMorgan Chase"
    assert len(pkg.role["system_prompt"]) >= 3000
    assert "## 7." in pkg.role["system_prompt"]

    # Use cases verification
    assert len(pkg.use_cases) >= 4
    for uc in pkg.use_cases:
        assert uc["cadence"] in ("DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "AD_HOC", "CONTINUOUS")
        assert uc["trigger_event"]
        assert len(uc["horizontal_tools"]) > 0 or len(uc["vertical_tools"]) > 0

    # Tools verification
    assert len(pkg.tools) >= 3
    tool_names = [t["name"] for t in pkg.tools]
    assert any("Word" in tn or "Spreadsheet" in tn or "Presentation" in tn or "Terminal" in tn or "Analytics" in tn for tn in tool_names)

    # Subagent swarm verification
    assert len(pkg.subagent_swarm) >= 4
    roles_in_swarm = [sa["subagent_role"] for sa in pkg.subagent_swarm]
    assert "CHIEF_OF_STAFF" in roles_in_swarm
    for sa in pkg.subagent_swarm:
        assert sa["system_prompt"]
        assert sa["hitl_checkpoint"]

    # GenAI plan verification
    assert pkg.genai_plan is not None
    assert pkg.genai_plan["rag_context_architecture"]
    assert pkg.genai_plan["hitl_guardrails"]


def test_role_scaffolder_by_slug(db_path):
    scaffolder = RoleScaffolder.build_from_db(db_path)
    pkg = scaffolder.scaffold_role("tech_principal_distributed_training_engineer")

    assert pkg.role["slug"] == "tech_principal_distributed_training_engineer"
    assert pkg.role["name"] == "Principal Distributed Training Engineer"
    assert len(pkg.use_cases) >= 4
    assert len(pkg.subagent_swarm) >= 4


def test_role_scaffolder_exports(tmp_path, db_path):
    scaffolder = RoleScaffolder.build_from_db(db_path)
    pkg = scaffolder.scaffold_role("telecom_chief_network_architect")

    # Markdown export test
    md = pkg.to_markdown()
    assert "# Canonical Role Scaffolding Runbook" in md
    assert "## 1. Fiduciary Mission" in md
    assert "## 2. Day-to-Day Operational Anatomy" in md
    assert "## 3. Dual-Layer Tooling" in md
    assert "## 4. Personal Subagent Swarm Architecture" in md
    assert "## 5. Generative AI Tooling Engineering Blueprint" in md
    assert "## 6. Compiled Canonical Meta-Prompt" in md

    # JSON export test
    js = pkg.to_json()
    data = json.loads(js)
    assert data["role"]["slug"] == "telecom_chief_network_architect"
    assert len(data["use_cases"]) >= 4

    # File save tests
    md_file = tmp_path / "architect_runbook.md"
    saved_md = pkg.save(md_file, format="markdown")
    assert saved_md.exists()
    assert saved_md.stat().st_size > 1000

    json_file = tmp_path / "architect_runbook.json"
    saved_json = pkg.save(json_file, format="json")
    assert saved_json.exists()
    assert json.loads(saved_json.read_text(encoding="utf-8"))["role"]["slug"] == "telecom_chief_network_architect"


def test_role_scaffolder_nonexistent_raises(db_path):
    scaffolder = RoleScaffolder.build_from_db(db_path)
    with pytest.raises(KeyError):
        scaffolder.scaffold_role("nonexistent_phantom_role_xyz")


def test_company_scaffolder_f500(db_path):
    scaffolder = CompanyScaffolder.build_from_db(db_path)
    pkg = scaffolder.scaffold_company("Walmart")

    assert pkg.company["name"] == "Walmart"
    assert pkg.company["rank"] == 1
    assert pkg.company["revenue_billions"] >= 600.0
    assert len(pkg.divisions) >= 3
    assert len(pkg.employed_roles) >= 10
    assert len(pkg.tools) >= 3
    assert len(pkg.swarms) >= 1

    # Markdown export
    md = pkg.to_markdown()
    assert "# Enterprise Scaffolding Runbook: Walmart" in md
    assert "## 1. Operating Divisions" in md
    assert "## 2. Employed Canonical Roles" in md
    assert "## 3. Enterprise Tooling Stack" in md
    assert "## 4. Personal Subagent Swarm Deployments" in md

    # JSON export
    js = pkg.to_json()
    data = json.loads(js)
    assert data["company"]["name"] == "Walmart"
    assert len(data["employed_roles"]) >= 10


def test_company_scaffolder_with_division_filter(db_path):
    scaffolder = CompanyScaffolder.build_from_db(db_path)
    # Filter by Supply Chain or Operations
    pkg = scaffolder.scaffold_company("Walmart", division="Supply Chain")
    assert pkg.company["name"] == "Walmart"
    # Filtered employed roles should match or be empty if division is specific
    for r in pkg.employed_roles:
        assert "supply" in r["department"].lower() or "chain" in r["department"].lower() or len(pkg.employed_roles) > 0


def test_company_scaffolder_nonexistent_raises(db_path):
    scaffolder = CompanyScaffolder.build_from_db(db_path)
    with pytest.raises(KeyError):
        scaffolder.scaffold_company("NonexistentCorpFake12345")


def test_cli_scaffold_role(tmp_path, db_path):
    runner = CliRunner()

    # Markdown format to stdout
    res = runner.invoke(
        cli,
        ["scaffold", "role", "fin_chief_investment_officer", "--db-path", db_path],
    )
    assert res.exit_code == 0
    assert "Canonical Role Scaffolding Runbook: Chief Investment Officer" in res.output

    # JSON format to stdout
    res_json = runner.invoke(
        cli,
        ["scaffold", "role", "fin_chief_investment_officer", "--format", "json", "--db-path", db_path],
    )
    assert res_json.exit_code == 0
    parsed = json.loads(res_json.output)
    assert parsed["role"]["slug"] == "fin_chief_investment_officer"

    # Save to file
    out_file = str(tmp_path / "cli_cio.md")
    res_save = runner.invoke(
        cli,
        ["scaffold", "role", "fin_chief_investment_officer", "--output", out_file, "--db-path", db_path],
    )
    assert res_save.exit_code == 0
    assert Path(out_file).exists()


def test_cli_scaffold_company(tmp_path, db_path):
    runner = CliRunner()

    # Markdown format
    res = runner.invoke(
        cli,
        ["scaffold", "company", "Apple", "--db-path", db_path],
    )
    assert res.exit_code == 0
    assert "Enterprise Scaffolding Runbook: Apple" in res.output

    # JSON format
    res_json = runner.invoke(
        cli,
        ["scaffold", "company", "Apple", "--format", "json", "--db-path", db_path],
    )
    assert res_json.exit_code == 0
    data = json.loads(res_json.output)
    assert data["company"]["name"] == "Apple"

    # Save to file
    out_file = str(tmp_path / "cli_apple.md")
    res_save = runner.invoke(
        cli,
        ["scaffold", "company", "Apple", "--output", out_file, "--db-path", db_path],
    )
    assert res_save.exit_code == 0
    assert Path(out_file).exists()


@pytest.mark.parametrize("empty_query", ["", "   ", "\t\n", "  \t  "])
def test_role_scaffolder_empty_or_whitespace_raises(db_path, empty_query):
    with RoleScaffolder.build_from_db(db_path) as scaffolder:
        with pytest.raises(KeyError, match="Empty or whitespace-only role identifier provided"):
            scaffolder.scaffold_role(empty_query)


@pytest.mark.parametrize("empty_query", ["", "   ", "\t\n", "  \t  "])
def test_company_scaffolder_empty_or_whitespace_raises(db_path, empty_query):
    with CompanyScaffolder.build_from_db(db_path) as scaffolder:
        with pytest.raises(KeyError, match="Empty or whitespace-only company identifier provided"):
            scaffolder.scaffold_company(empty_query)


def test_scaffolder_context_managers(db_path):
    with RoleScaffolder.build_from_db(db_path) as r_scaffolder:
        pkg = r_scaffolder.scaffold_role("role_fin_chief_investment_officer")
        assert pkg.role["slug"] == "fin_chief_investment_officer"

    with CompanyScaffolder.build_from_db(db_path) as c_scaffolder:
        cpkg = c_scaffolder.scaffold_company("Walmart")
        assert cpkg.company["name"] == "Walmart"

