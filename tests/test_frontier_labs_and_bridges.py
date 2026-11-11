"""Comprehensive Phase 16 test suite for Nov 2026 Frontier AI Labs & Real-World Join Engine (`>= 22` tests).

Verifies:
- 5 Nov 2026 Frontier AI Labs (`frontier_ai_labs`) & 30 Internal Operating Pods (`frontier_lab_pods`)
- 5 Frontier Lab Vertical Tools (`tools` == 60) & 16 `frontier_*` Canonical Roles (`canonical_roles` == 579)
- 512 Onboarded Organizations (`fortune500_companies` ranks 508..512) & 2 Frontier Bridge Superhumans
- 22 Cross-Industry Join Blueprints (`real_world_to_frontier_bridges`) covering 100% of all 16 Macro Industries
- 100% Real-World Role Join Coverage (`role_frontier_joins` >= 1,150 rows across all 563 non-`frontier_*` roles, 0 broken FKs)
- CLI (`orgprompt frontier ...`), SHA-256 parity of `org-frontier-lab-enterprise-bridge` skill & flagship report
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner

from orgprompt.cli import cli
from orgprompt.db.schema import ensure_frontier_schema, get_schema_sql
from orgprompt.frontier import (
    FRONTIER_JOIN_MECHANISMS,
    FRONTIER_POD_CATEGORIES,
    FrontierLabJoinEngine,
    inspect_frontier_lab,
    list_frontier_labs,
    seed_frontier_join_layer,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
LIVE_DB = REPO_ROOT / "data" / "org_knowledge_base.db"
GLOBAL_SKILL_DIR = Path("/home/pakmingw/.gemini/config/skills/org-frontier-lab-enterprise-bridge")
WORKSPACE_SKILL_DIR = REPO_ROOT / ".agents" / "skills" / "org-frontier-lab-enterprise-bridge"
REPO_REPORT = REPO_ROOT / "artifacts" / "frontier_labs" / "frontier_ai_labs_nov2026_and_enterprise_bridge_report.md"
BRAIN_REPORT = Path("/home/pakmingw/.gemini/antigravity/brain/1e96291d-9d64-4bac-9f19-67c0822cf354/frontier_ai_labs_nov2026_and_enterprise_bridge_report.md")

EXPECTED_5_LAB_IDS = {
    "lab_anthropic",
    "lab_openai",
    "lab_google_deepmind",
    "lab_meta_msl",
    "lab_mistral_ai",
}

EXPECTED_5_FRONTIER_TOOLS = {
    "tool_agentic_rl_gym_verifiers",
    "tool_mcp_context_computer_use_runtime",
    "tool_disaggregated_kv_inference_stack",
    "tool_frontier_eval_preparedness_suite",
    "tool_fde_custom_posttraining_forge",
}

EXPECTED_16_FRONTIER_ROLES = {
    "frontier_test_time_compute_reasoning_rl_lead",
    "frontier_agent_post_training_computer_use_lead",
    "frontier_coding_agent_swe_harness_architect",
    "frontier_context_engineering_mcp_architect",
    "frontier_synthetic_data_curriculum_selfplay_lead",
    "frontier_multimodal_world_model_sim_architect",
    "frontier_long_context_moe_architecture_lead",
    "frontier_disaggregated_inference_kv_systems_lead",
    "frontier_gigawatt_cluster_tpu_gpu_codesign_lead",
    "frontier_research_engineer_orchestration_lead",
    "frontier_model_character_spec_alignment_lead",
    "frontier_asl_preparedness_control_evaluator",
    "frontier_eval_science_benchmark_contamination_lead",
    "frontier_forward_deployed_ai_engineer_lead",
    "frontier_enterprise_distillation_forge_lead",
    "frontier_ai_for_science_discovery_lead",
}


def test_01_schema_sql_and_ensure_frontier_schema(tmp_path: Path) -> None:
    ddl = get_schema_sql()
    for tbl in ("frontier_ai_labs", "frontier_lab_pods", "real_world_to_frontier_bridges", "role_frontier_joins"):
        assert f"CREATE TABLE IF NOT EXISTS {tbl}" in ddl
    temp_db = tmp_path / "frontier_empty.db"
    conn = ensure_frontier_schema(temp_db)
    try:
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        assert {"frontier_ai_labs", "frontier_lab_pods", "real_world_to_frontier_bridges", "role_frontier_joins"}.issubset(tables)
    finally:
        conn.close()


def test_02_all_5_frontier_labs_and_30_pods_seeded() -> None:
    labs = list_frontier_labs(LIVE_DB)
    assert len(labs) == 5
    assert {l.id for l in labs} == EXPECTED_5_LAB_IDS
    total_pods = 0
    for lab in labs:
        assert len(lab.pods) == 6, f"{lab.id} must have 6 operating pods"
        assert {p.pod_category for p in lab.pods} == set(FRONTIER_POD_CATEGORIES)
        assert lab.company_id is not None and lab.company_id.startswith("f500_")
        total_pods += len(lab.pods)
    assert total_pods == 30


def test_03_all_30_pods_resolve_cleanly_to_canonical_roles() -> None:
    conn = sqlite3.connect(LIVE_DB)
    try:
        valid_slugs = {r[0] for r in conn.execute("SELECT slug FROM canonical_roles").fetchall()}
    finally:
        conn.close()
    for lab in list_frontier_labs(LIVE_DB):
        for pod in lab.pods:
            assert len(pod.canonical_role_slugs) >= 2
            for slug in pod.canonical_role_slugs:
                assert slug in valid_slugs, f"Pod {pod.id} references unknown role slug {slug}"


def test_04_five_frontier_tools_and_60_total_tools() -> None:
    conn = sqlite3.connect(LIVE_DB)
    try:
        tool_ids = {r[0] for r in conn.execute("SELECT id FROM tools").fetchall()}
        assert len(tool_ids) >= 60
        assert EXPECTED_5_FRONTIER_TOOLS.issubset(tool_ids)
    finally:
        conn.close()


def test_05_sixteen_frontier_canonical_roles_and_579_total_roles() -> None:
    conn = sqlite3.connect(LIVE_DB)
    try:
        rows = conn.execute("SELECT slug, character_count, length(system_prompt) FROM canonical_roles").fetchall()
        slug_map = {r[0]: (r[1], r[2]) for r in rows}
        assert len(slug_map) >= 579
        assert EXPECTED_16_FRONTIER_ROLES.issubset(slug_map.keys())
        for fslug in EXPECTED_16_FRONTIER_ROLES:
            cc, plen = slug_map[fslug]
            assert plen >= 6000 and cc == plen
    finally:
        conn.close()


def test_06_five_frontier_labs_onboarded_in_fortune500_companies_512_total() -> None:
    conn = sqlite3.connect(LIVE_DB)
    try:
        cnt = conn.execute("SELECT COUNT(*) FROM fortune500_companies").fetchone()[0]
        assert cnt >= 512
        cic_cnt = conn.execute("SELECT COUNT(*) FROM company_internet_comparisons").fetchone()[0]
        assert cic_cnt >= 512
        onboarded = {
            r[0] for r in conn.execute("SELECT id FROM fortune500_companies WHERE rank BETWEEN 508 AND 512").fetchall()
        }
        assert onboarded == {
            "f500_anthropic",
            "f500_openai",
            "f500_google_deepmind",
            "f500_meta_superintelligence_labs",
            "f500_mistral_ai",
        }
    finally:
        conn.close()


def test_07_two_frontier_bridge_superhumans_persisted() -> None:
    conn = sqlite3.connect(LIVE_DB)
    try:
        rows = conn.execute(
            "SELECT slug, length(deep_superhuman_prompt) FROM superhuman_role_profiles WHERE slug LIKE 'superhuman_frontier_%'"
        ).fetchall()
        by_slug = dict(rows)
        assert "superhuman_frontier_fde_enterprise_bridge_architect" in by_slug
        assert "superhuman_frontier_post_training_verifier_chief" in by_slug
        for s, plen in by_slug.items():
            assert plen >= 25000, f"{s} prompt too short: {plen}"
    finally:
        conn.close()


def test_08_bridges_cover_all_16_macro_industries_and_zero_dangling_slugs() -> None:
    conn = sqlite3.connect(LIVE_DB)
    try:
        all_industries = {r[0] for r in conn.execute("SELECT id FROM industries").fetchall()}
        valid_roles = {r[0] for r in conn.execute("SELECT slug FROM canonical_roles").fetchall()}
        valid_pods = {r[0] for r in conn.execute("SELECT id FROM frontier_lab_pods").fetchall()}
    finally:
        conn.close()
    assert len(all_industries) == 16

    with FrontierLabJoinEngine(LIVE_DB) as eng:
        bridges = eng.list_bridges()
    assert len(bridges) >= 20
    covered_industries = {b.industry_id for b in bridges}
    assert covered_industries == all_industries, f"Missing industries: {all_industries - covered_industries}"

    for b in bridges:
        assert len(b.real_world_role_slugs) >= 3
        assert len(b.frontier_role_slugs) >= 2
        for rs in b.real_world_role_slugs:
            assert rs in valid_roles, f"Bridge {b.id} has invalid real_world_role {rs}"
        for fs in b.frontier_role_slugs:
            assert fs in valid_roles, f"Bridge {b.id} has invalid frontier_role {fs}"
        for pid in b.frontier_pod_ids:
            assert pid in valid_pods, f"Bridge {b.id} has invalid pod_id {pid}"


def test_09_100_percent_real_world_role_coverage_in_role_frontier_joins() -> None:
    conn = sqlite3.connect(LIVE_DB)
    try:
        total_joins = conn.execute("SELECT COUNT(*) FROM role_frontier_joins").fetchone()[0]
        assert total_joins >= 1150

        non_frontier_roles = {
            r[0] for r in conn.execute("SELECT id FROM canonical_roles WHERE slug NOT LIKE 'frontier_%'").fetchall()
        }
        assert len(non_frontier_roles) >= 563

        joined_counts = dict(
            conn.execute(
                """
                SELECT r.id, COUNT(j.id)
                FROM canonical_roles r
                LEFT JOIN role_frontier_joins j ON j.source_enterprise_role_id = r.id
                WHERE r.slug NOT LIKE 'frontier_%'
                GROUP BY r.id
                """
            ).fetchall()
        )
        uncovered = [rid for rid, cnt in joined_counts.items() if cnt < 2]
        assert uncovered == [], f"Found real-world roles with <2 frontier joins: {uncovered[:5]}"

        self_loops = conn.execute(
            "SELECT COUNT(*) FROM role_frontier_joins WHERE source_enterprise_role_id = target_frontier_role_id"
        ).fetchone()[0]
        assert self_loops == 0

        fk_errors = conn.execute("PRAGMA foreign_key_check;").fetchall()
        assert fk_errors == []

        mechs = {r[0] for r in conn.execute("SELECT DISTINCT join_mechanism FROM role_frontier_joins").fetchall()}
        assert mechs == set(FRONTIER_JOIN_MECHANISMS)

        target_frontier_slugs = {
            r[0]
            for r in conn.execute(
                """
                SELECT DISTINCT r.slug FROM role_frontier_joins j
                JOIN canonical_roles r ON j.target_frontier_role_id = r.id
                WHERE r.slug LIKE 'frontier_%'
                """
            ).fetchall()
        }
        assert target_frontier_slugs == EXPECTED_16_FRONTIER_ROLES
    finally:
        conn.close()


def test_10_idempotent_re_seeding_preserves_exact_counts() -> None:
    c1 = seed_frontier_join_layer(LIVE_DB)
    c2 = seed_frontier_join_layer(LIVE_DB)
    assert c1 == c2
    assert c1["labs"] == 5 and c1["pods"] == 30 and c1["bridges"] >= 20 and c1["role_frontier_joins"] >= 1150


def test_11_inspect_frontier_lab_aliases_and_export(tmp_path: Path) -> None:
    anth = inspect_frontier_lab("anthropic", LIVE_DB)
    gdm = inspect_frontier_lab("deepmind", LIVE_DB)
    msl = inspect_frontier_lab("meta", LIVE_DB)
    mist = inspect_frontier_lab("mistral", LIVE_DB)
    oai = inspect_frontier_lab("openai", LIVE_DB)
    assert {anth.id, gdm.id, msl.id, mist.id, oai.id} == EXPECTED_5_LAB_IDS

    out_md = anth.save(tmp_path / "anthropic.md", format="markdown")
    out_js = anth.save(tmp_path / "anthropic.json", format="json")
    assert "Long-Term Benefit Trust" in out_md.read_text(encoding="utf-8")
    assert len(json.loads(out_js.read_text(encoding="utf-8"))["pods"]) == 6


def test_12_join_role_exact_slug_and_natural_language_query() -> None:
    with FrontierLabJoinEngine(LIVE_DB) as eng:
        r_orange = eng.join_role("principal_ftth_copper_decommissioning_architect_plan_cuivre", company_name_or_slug="Orange France")
        assert r_orange.company_name == "Orange France"
        assert len(r_orange.frontier_joins) == 3
        assert len(r_orange.personal_subagents) == 6
        assert any("telecom" in b.slug for b in r_orange.matching_bridges)

        r_nl = eng.join_role("YouTube retention video editor pacing")
        assert not r_nl.role_slug.startswith("frontier_")
        assert len(r_nl.frontier_joins) >= 2


def test_13_join_company_orange_france_and_beast_industries() -> None:
    with FrontierLabJoinEngine(LIVE_DB) as eng:
        orange = eng.join_company("Orange France")
        assert orange.employed_roles_count >= 20
        assert orange.total_frontier_join_edges >= 60
        assert len(orange.top_frontier_counterparts) >= 5
        assert len(orange.industry_bridges) >= 1

        beast = eng.join_company("Beast Industries")
        assert beast.industry_id == "ind_creative_media"
        assert beast.total_frontier_join_edges >= 20
        assert any("creator" in b.slug or "media" in b.slug for b in beast.industry_bridges)


def test_14_bridge_problem_hybrid_search_to_frontier_pods() -> None:
    with FrontierLabJoinEngine(LIVE_DB) as eng:
        res = eng.bridge_problem(
            "Accelerate FTTH Plan Cuivre copper switch-off and sovereign 5G OSS mediation under SecNumCloud",
            company_name_or_slug="Orange France",
        )
    assert len(res.retrieved_enterprise_roles) >= 4
    assert all(not r["slug"].startswith("frontier_") for r in res.retrieved_enterprise_roles)
    assert len(res.activated_frontier_pods) >= 3
    assert len(res.recommended_labs) >= 2
    assert len(res.co_design_execution_plan) == 4


def test_15_cli_frontier_labs_and_inspect_lab() -> None:
    runner = CliRunner()
    res_labs = runner.invoke(cli, ["frontier", "labs", "--db-path", str(LIVE_DB), "--json"])
    assert res_labs.exit_code == 0
    labs_json = json.loads(res_labs.output)
    assert len(labs_json) == 5

    res_ins = runner.invoke(cli, ["frontier", "inspect-lab", "mistral_ai", "--db-path", str(LIVE_DB)])
    assert res_ins.exit_code == 0
    assert "Mistral Forge" in res_ins.output


def test_16_cli_frontier_join_role_and_join_company(tmp_path: Path) -> None:
    runner = CliRunner()
    res_role = runner.invoke(
        cli,
        ["frontier", "join-role", "creator_solo_founder_one_person_media_studio", "--company", "Kurzgesagt", "--db-path", str(LIVE_DB), "--json"],
    )
    assert res_role.exit_code == 0
    payload = json.loads(res_role.output)
    assert payload["company_name"] == "Kurzgesagt"
    assert len(payload["frontier_joins"]) == 3

    out_md = tmp_path / "orange_join.md"
    res_comp = runner.invoke(
        cli,
        ["frontier", "join-company", "Orange France", "--focus", "ftth", "--db-path", str(LIVE_DB), "--output", str(out_md)],
    )
    assert res_comp.exit_code == 0
    assert out_md.is_file() and "Orange France" in out_md.read_text(encoding="utf-8")


def test_17_cli_frontier_bridge_problem_json_and_markdown() -> None:
    runner = CliRunner()
    res = runner.invoke(
        cli,
        [
            "frontier", "bridge-problem",
            "--problem", "Detect Simpson's paradox subgroup calibration drift in hospital sepsis EHR AI",
            "--db-path", str(LIVE_DB),
            "--json",
        ],
    )
    assert res.exit_code == 0
    data = json.loads(res.output)
    assert len(data["retrieved_enterprise_roles"]) >= 4
    assert len(data["activated_frontier_pods"]) >= 2


def test_18_skill_bundles_exist_and_are_sha256_byte_identical() -> None:
    for rel in ("SKILL.md", "scripts/bridge_frontier_lab.py", "references/nov2026_frontier_labs_matrix.md"):
        g_file = GLOBAL_SKILL_DIR / rel
        w_file = WORKSPACE_SKILL_DIR / rel
        assert g_file.is_file(), f"Missing global skill file: {g_file}"
        assert w_file.is_file(), f"Missing workspace skill file: {w_file}"
        h1 = hashlib.sha256(g_file.read_bytes()).hexdigest()
        h2 = hashlib.sha256(w_file.read_bytes()).hexdigest()
        assert h1 == h2, f"SHA-256 mismatch on skill file {rel}"


def test_19_skill_script_bridge_frontier_lab_executes_cleanly(tmp_path: Path) -> None:
    out_file = tmp_path / "skill_bridge.md"
    proc = subprocess.run(
        [
            sys.executable,
            str(WORKSPACE_SKILL_DIR / "scripts" / "bridge_frontier_lab.py"),
            "--company", "Orange France",
            "--problem", "Automate 5G SA Open RAN slice assurance and Plan Cuivre duct OCR",
            "--output", str(out_file),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert proc.returncode == 0
    txt = out_file.read_text(encoding="utf-8")
    assert "Problem-to-Frontier-Lab Bridge Synthesis" in txt
    assert "Mistral AI" in txt or "Anthropic" in txt


def test_20_flagship_report_sha256_parity_zero_unescaped_dollar_and_mermaid() -> None:
    assert REPO_REPORT.is_file() and BRAIN_REPORT.is_file()
    b1 = REPO_REPORT.read_bytes()
    b2 = BRAIN_REPORT.read_bytes()
    assert hashlib.sha256(b1).hexdigest() == hashlib.sha256(b2).hexdigest()
    txt = b1.decode("utf-8")
    assert len(txt) >= 15000
    unescaped_dollars = re.findall(r"(?<!\\)\$", txt)
    assert unescaped_dollars == [], f"Found unescaped $ signs in report: {unescaped_dollars}"
    assert "```mermaid" in txt
    for mermaid_block in re.findall(r"```mermaid(.*?)```", txt, flags=re.S):
        assert "\\$" not in mermaid_block, "Use USD instead of \\$ inside Mermaid blocks"
    for lab_name in ("Anthropic", "OpenAI", "Google DeepMind", "Meta", "Mistral AI"):
        assert lab_name in txt


def test_21_live_joined_runbook_artifacts_exist_and_clean() -> None:
    for fname in ("orange_france_frontier_lab_bridge.md", "beast_industries_frontier_lab_bridge.md"):
        fpath = REPO_ROOT / "artifacts" / "frontier_labs" / fname
        assert fpath.is_file() and fpath.stat().st_size > 2000
        assert re.findall(r"(?<!\\)\$", fpath.read_text(encoding="utf-8")) == []


def test_22_dict_mixin_ergonomics_on_frontier_models() -> None:
    lab = inspect_frontier_lab("anthropic", LIVE_DB)
    assert lab["slug"] == "anthropic"
    assert lab.get("id") == "lab_anthropic"
    assert lab.get("missing_attr", "default_val") == "default_val"


def test_23_frontier_join_layer_preserves_kg_role_degree_bounds() -> None:
    import statistics
    from orgprompt.graph.engine import KnowledgeGraphEngine

    kg = KnowledgeGraphEngine.build_from_db(LIVE_DB)
    role_nodes = [n for n, d in kg.nodes(data=True) if d.get("type") == "CanonicalRole"]
    assert len(role_nodes) >= 579
    in_degrees = [len(list(kg.in_edges(rn))) for rn in role_nodes]
    avg_in = statistics.mean(in_degrees)
    assert 40.0 <= avg_in <= 70.0, f"avg_in={avg_in:.2f} violated [40.0, 70.0]"
    for rn in role_nodes:
        out_deg = len(list(kg.out_edges(rn)))
        assert 5 <= out_deg <= 15, f"Role {rn} out_degree={out_deg} violated [5, 15]"


def test_24_company_blueprints_exist_for_all_5_onboarded_frontier_labs() -> None:
    bp_dir = REPO_ROOT / "artifacts" / "company_onboarding"
    for slug in ("anthropic", "openai", "google_deepmind", "meta_superintelligence_labs", "mistral_ai"):
        bp = bp_dir / f"{slug}_genai_blueprint.md"
        assert bp.is_file() and bp.stat().st_size > 3000, f"Missing or empty blueprint: {bp}"
