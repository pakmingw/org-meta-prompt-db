"""Comprehensive Phase 15 test suite for `orgprompt.governance` (`>= 22` tests).

Verifies the dedicated Fiduciary Governance & Independent Audit Taxonomy Tier:
- 18 Board Director & Independent Auditor roles (`governance_roles`) outside management
- 22 Industry & Venture/Creator Board Composition Slates (`industry_board_compositions`)
- 72 Typed Fiduciary Oversight Edges (`governance_oversight_edges`) into `canonical_roles`
- 3 Flagship 8-Section Superhuman Governance Profiles (`superhuman_governance_profiles`)
- CLI (`orgprompt governance ...`) & byte-identical `org-board-and-auditor-governance` skill bundles
"""

from __future__ import annotations

import filecmp
import json
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from orgprompt.cli import cli
from orgprompt.governance import (
    COMPANY_STAGES,
    GOVERNANCE_CATEGORIES,
    GOVERNANCE_EDGE_TYPES,
    SuperhumanGovernanceSynthesizer,
    board_for_company,
    ensure_governance_schema,
    get_governance_role,
    list_governance_roles,
    list_industry_board_compositions,
    seed_flagship_superhuman_governance_profiles,
    seed_governance_taxonomy,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
LIVE_DB = REPO_ROOT / "data" / "org_knowledge_base.db"
GLOBAL_SKILL_DIR = Path("/home/pakmingw/.gemini/config/skills/org-board-and-auditor-governance")
WORKSPACE_SKILL_DIR = REPO_ROOT / ".agents" / "skills" / "org-board-and-auditor-governance"

EXPECTED_18_SLUGS = {
    "gov_lead_independent_board_chair",
    "gov_audit_committee_financial_expert_chair",
    "gov_capital_allocation_value_director",
    "gov_compensation_succession_chair",
    "gov_external_statutory_forensic_auditor",
    "gov_independent_strategic_value_auditor",
    "gov_tech_ai_semiconductor_director",
    "gov_cybersecurity_ai_safety_board_auditor",
    "gov_financial_systemic_risk_chair",
    "gov_biotech_clinical_scientific_director",
    "gov_healthcare_patient_safety_auditor",
    "gov_telco_energy_infra_regulatory_director",
    "gov_aerospace_defense_security_director",
    "gov_industrial_supply_chain_quality_auditor",
    "gov_retail_consumer_brand_director",
    "gov_media_creator_venture_board_partner",
    "gov_esg_climate_labor_governance_auditor",
    "gov_special_committee_mna_turnaround_director",
}


def test_01_isolated_temp_db_schema_and_idempotent_seeding(tmp_path: Path) -> None:
    db_file = tmp_path / "gov_test.db"
    counts_1 = seed_governance_taxonomy(db_file)
    counts_2 = seed_governance_taxonomy(db_file)
    assert counts_1 == {"governance_roles": 18, "industry_board_compositions": 22, "governance_oversight_edges": 72}
    assert counts_2 == counts_1


def test_02_live_db_preserves_management_hierarchy_untouched() -> None:
    conn = sqlite3.connect(LIVE_DB)
    try:
        mgmt_slugs = {r[0] for r in conn.execute("SELECT slug FROM canonical_roles").fetchall()}
        f500_count = conn.execute("SELECT COUNT(*) FROM fortune500_companies").fetchone()[0]
        assert len(mgmt_slugs) >= 559
        assert f500_count >= 507
        assert mgmt_slugs.isdisjoint(EXPECTED_18_SLUGS), "Governance roles must sit strictly outside canonical_roles"
    finally:
        conn.close()


def test_03_all_18_governance_roles_present_and_categorized() -> None:
    roles = list_governance_roles(LIVE_DB)
    assert len(roles) == 18
    assert {r.slug for r in roles} == EXPECTED_18_SLUGS
    cats = {r.governance_category for r in roles}
    assert cats == set(GOVERNANCE_CATEGORIES)
    directors = [r for r in roles if r.governance_category == "BOARD_DIRECTOR"]
    auditors = [r for r in roles if r.governance_category == "INDEPENDENT_AUDITOR"]
    assert len(directors) == 12
    assert len(auditors) == 6


def test_04_every_governance_role_has_rich_7_section_fiduciary_prompt() -> None:
    roles = list_governance_roles(LIVE_DB)
    for r in roles:
        assert r.character_count == len(r.system_prompt)
        assert r.character_count >= 8000, f"{r.slug} prompt too short: {r.character_count}"
        for sec_num in range(1, 8):
            assert f"# SECTION {sec_num}:" in r.system_prompt
        assert len(r.quarterly_review_cadence) >= 4
        assert len(r.kpi_value_tree) >= 4
        assert len(r.red_flag_triggers) >= 4
        assert len(r.oversight_targets) >= 4


def test_05_all_16_macro_industries_have_public_and_venture_compositions() -> None:
    conn = sqlite3.connect(LIVE_DB)
    try:
        macro_slugs = {row[0] for row in conn.execute("SELECT slug FROM industries").fetchall()}
    finally:
        conn.close()
    assert len(macro_slugs) == 16

    all_comps = list_industry_board_compositions(LIVE_DB)
    assert len(all_comps) == 22
    pub_comps = list_industry_board_compositions(LIVE_DB, stage="PUBLIC_ENTERPRISE")
    ven_comps = list_industry_board_compositions(LIVE_DB, stage="VENTURE_OR_BOUTIQUE")
    assert len(pub_comps) == 16
    assert {c.industry_slug for c in pub_comps} == macro_slugs
    assert len(ven_comps) == 6
    assert "creative_media" in {c.industry_slug for c in ven_comps}


def test_06_all_72_oversight_edges_resolve_to_valid_canonical_management_roles() -> None:
    conn = sqlite3.connect(LIVE_DB)
    try:
        total_edges = conn.execute("SELECT COUNT(*) FROM governance_oversight_edges").fetchone()[0]
        assert total_edges == 72
        dangling = conn.execute(
            """
            SELECT target_management_role_slug FROM governance_oversight_edges
            WHERE target_management_role_slug NOT IN (SELECT slug FROM canonical_roles)
            """
        ).fetchall()
        assert dangling == [], f"Dangling management targets: {dangling}"
        used_edge_types = {r[0] for r in conn.execute("SELECT DISTINCT edge_type FROM governance_oversight_edges").fetchall()}
        assert used_edge_types == set(GOVERNANCE_EDGE_TYPES)
    finally:
        conn.close()


def test_07_board_for_company_public_enterprise_orange_france() -> None:
    slate = board_for_company("Orange France", db_path_or_conn=LIVE_DB)
    assert slate.company_name == "Orange France"
    assert slate.industry_slug == "telecommunications"
    assert slate.company_stage == "PUBLIC_ENTERPRISE"
    dir_slugs = {d.slug for d in slate.board_directors}
    aud_slugs = {a.slug for a in slate.external_auditors}
    assert "gov_telco_energy_infra_regulatory_director" in dir_slugs
    assert "gov_capital_allocation_value_director" in dir_slugs
    assert "gov_cybersecurity_ai_safety_board_auditor" in aud_slugs
    assert "gov_esg_climate_labor_governance_auditor" in aud_slugs
    assert len(slate.oversight_edges) >= 20


def test_08_board_for_company_auto_detects_venture_or_boutique_for_indie_and_creator_studios() -> None:
    for studio in ("A24", "Beast Industries", "Kurzgesagt"):
        slate = board_for_company(studio, db_path_or_conn=LIVE_DB)
        assert slate.industry_slug == "creative_media"
        assert slate.company_stage == "VENTURE_OR_BOUTIQUE"
        assert slate.board_size == 5
        dir_slugs = {d.slug for d in slate.board_directors}
        assert "gov_media_creator_venture_board_partner" in dir_slugs
        assert "gov_audit_committee_financial_expert_chair" in dir_slugs


def test_09_board_for_company_direct_industry_slug_and_stage_override(tmp_path: Path) -> None:
    slate = board_for_company("finance_quant", stage="VENTURE_OR_BOUTIQUE", db_path_or_conn=LIVE_DB)
    assert slate.industry_slug == "finance_quant"
    assert slate.company_stage == "VENTURE_OR_BOUTIQUE"
    assert "gov_financial_systemic_risk_chair" in {d.slug for d in slate.board_directors}
    md_out = slate.save(tmp_path / "fintech_slate.md", format="markdown")
    js_out = slate.save(tmp_path / "fintech_slate.json", format="json")
    assert "Fiduciary Board of Directors" in md_out.read_text(encoding="utf-8")
    assert json.loads(js_out.read_text(encoding="utf-8"))["industry_slug"] == "finance_quant"


def test_10_get_governance_role_by_slug_id_and_title() -> None:
    by_slug = get_governance_role("gov_external_statutory_forensic_auditor", LIVE_DB)
    by_id = get_governance_role("gov_role_05", LIVE_DB)
    assert by_slug is not None and by_id is not None
    assert by_slug.slug == by_id.slug
    assert "PCAOB" in by_slug.to_markdown()
    assert json.loads(by_slug.to_json())["id"] == "gov_role_05"


def test_11_filter_governance_roles_by_category_and_industry() -> None:
    auditors = list_governance_roles(LIVE_DB, category="INDEPENDENT_AUDITOR")
    assert len(auditors) == 6
    health_roles = list_governance_roles(LIVE_DB, industry_slug="healthcare_biotech")
    health_slugs = {r.slug for r in health_roles}
    assert "gov_biotech_clinical_scientific_director" in health_slugs
    assert "gov_healthcare_patient_safety_auditor" in health_slugs
    assert "gov_lead_independent_board_chair" in health_slugs


def test_12_three_flagship_superhuman_governance_profiles_persisted_in_live_db() -> None:
    synth = SuperhumanGovernanceSynthesizer(LIVE_DB)
    profiles = synth.list_profiles()
    slugs = {p["slug"] for p in profiles}
    expected = {
        "superhuman_gov_capital_allocation_board_director",
        "superhuman_gov_forensic_strategic_auditor",
        "superhuman_gov_media_creator_board_partner",
    }
    assert expected.issubset(slugs)
    for exp_slug in expected:
        pkg = synth.get_profile(exp_slug)
        assert pkg is not None
        assert pkg.prompt_character_count >= 25000
        assert len(pkg.unknown_risk_epistemology.stages) == 5
        assert len(pkg.boardroom_and_audit_crucibles.crucible_episodes) >= 3
        assert len(pkg.committee_and_seam_fusions) >= 4
        for sec in range(1, 9):
            assert f"## SECTION {sec}:" in pkg.deep_superhuman_governance_prompt


def test_13_flagship_artifacts_exported_on_disk() -> None:
    art_dir = REPO_ROOT / "artifacts" / "governance_roles"
    for slug in (
        "superhuman_gov_capital_allocation_board_director",
        "superhuman_gov_forensic_strategic_auditor",
        "superhuman_gov_media_creator_board_partner",
    ):
        md_path = art_dir / f"{slug}.md"
        js_path = art_dir / f"{slug}.json"
        assert md_path.is_file() and md_path.stat().st_size > 25000
        assert js_path.is_file()
        parsed = json.loads(js_path.read_text(encoding="utf-8"))
        assert parsed["slug"] == slug
        assert parsed["prompt_character_count"] >= 25000


def test_14_superhuman_synthesizer_auto_discovery_and_persist_in_temp_db(tmp_path: Path) -> None:
    db_file = tmp_path / "temp_sh.db"
    synth = SuperhumanGovernanceSynthesizer(db_file)
    pkg = synth.synthesize(
        problem="Audit clinical sepsis AI model for Simpson's Paradox and immunocompromised false negatives",
        developer_context="Enforce ECE < 0.03 across every hospital and demographic stratum.",
        persist=True,
    )
    assert pkg.base_governance_role.slug == "gov_healthcare_patient_safety_auditor"
    assert pkg.prompt_character_count >= 8000
    assert "ECE < 0.03" in pkg.deep_superhuman_governance_prompt
    reloaded = synth.get_profile(pkg.slug)
    assert reloaded is not None and reloaded.id == pkg.id


def test_15_cli_governance_list_roles_json_and_markdown() -> None:
    runner = CliRunner()
    res_json = runner.invoke(cli, ["governance", "list-roles", "--db-path", str(LIVE_DB), "--json"])
    assert res_json.exit_code == 0
    data = json.loads(res_json.output)
    assert len(data) == 18

    res_md = runner.invoke(cli, ["governance", "list-roles", "--db-path", str(LIVE_DB), "--category", "BOARD_DIRECTOR", "--format", "markdown"])
    assert res_md.exit_code == 0
    assert "12 Seats" in res_md.output


def test_16_cli_governance_board_slate_company_and_industry() -> None:
    runner = CliRunner()
    res = runner.invoke(cli, ["governance", "board-slate", "--company", "Orange France", "--db-path", str(LIVE_DB), "--json"])
    assert res.exit_code == 0
    payload = json.loads(res.output)
    assert payload["industry_slug"] == "telecommunications"
    assert len(payload["board_directors"]) >= 5


def test_17_cli_governance_synthesize_superhuman_and_inspect(tmp_path: Path) -> None:
    db_file = tmp_path / "cli_gov.db"
    out_md = tmp_path / "sh_out.md"
    runner = CliRunner()
    res_syn = runner.invoke(
        cli,
        [
            "governance", "synthesize-superhuman",
            "--problem", "Audit ASC 926 digital video capitalization and Shorts vanity views",
            "--role", "gov_media_creator_venture_board_partner",
            "--fuse", "gov_external_statutory_forensic_auditor",
            "--slug", "test_cli_sh_creator_auditor",
            "--persist",
            "--db-path", str(db_file),
            "--output", str(out_md),
        ],
    )
    assert res_syn.exit_code == 0
    assert out_md.is_file()

    res_ins = runner.invoke(cli, ["governance", "inspect", "test_cli_sh_creator_auditor", "--db-path", str(db_file), "--json"])
    assert res_ins.exit_code == 0
    assert json.loads(res_ins.output)["slug"] == "test_cli_sh_creator_auditor"


def test_18_cli_governance_inspect_canonical_seat() -> None:
    runner = CliRunner()
    res = runner.invoke(cli, ["governance", "inspect", "gov_audit_committee_financial_expert_chair", "--db-path", str(LIVE_DB)])
    assert res.exit_code == 0
    assert "SOX Section 407 Financial Expert" in res.output


def test_19_skill_bundles_exist_and_are_byte_identical() -> None:
    for rel in ("SKILL.md", "scripts/run_board_audit.py", "references/industry_board_selection_guide.md"):
        g_file = GLOBAL_SKILL_DIR / rel
        w_file = WORKSPACE_SKILL_DIR / rel
        assert g_file.is_file(), f"Missing global skill file: {g_file}"
        assert w_file.is_file(), f"Missing workspace skill file: {w_file}"
        assert filecmp.cmp(g_file, w_file, shallow=False), f"Skill file mismatch on {rel}"


def test_20_skill_script_run_board_audit_executes_cleanly(tmp_path: Path) -> None:
    out_file = tmp_path / "a24_audit.md"
    proc = subprocess.run(
        [
            sys.executable,
            str(WORKSPACE_SKILL_DIR / "scripts" / "run_board_audit.py"),
            "--company", "A24",
            "--problem", "Evaluate $25M tentpole negative cost vs pre-sales cap",
            "--output", str(out_file),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert proc.returncode == 0
    content = out_file.read_text(encoding="utf-8")
    assert "VENTURE_OR_BOUTIQUE" in content
    assert "SUPERHUMAN GOVERNANCE & ASSURANCE META-PROMPT" in content


def test_21_dict_mixin_ergonomics_on_governance_models() -> None:
    role = get_governance_role("gov_capital_allocation_value_director", LIVE_DB)
    assert role is not None
    assert role["slug"] == "gov_capital_allocation_value_director"
    assert role.get("governance_category") == "BOARD_DIRECTOR"
    assert role.get("nonexistent_key", "fallback") == "fallback"


def test_22_schema_sql_contains_all_four_governance_tables() -> None:
    from orgprompt.db.schema import get_schema_sql

    ddl = get_schema_sql()
    for tbl in (
        "governance_roles",
        "industry_board_compositions",
        "governance_oversight_edges",
        "superhuman_governance_profiles",
    ):
        assert f"CREATE TABLE IF NOT EXISTS {tbl}" in ddl
