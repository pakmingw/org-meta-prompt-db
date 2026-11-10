"""Phase 14 integration & regression suite: Indie Film, Scaled YouTube & Solo Creator Studio Expansion."""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path

import networkx as nx
import pytest

from orgprompt.db.connection import get_connection, get_default_db_path
from orgprompt.graph.engine import KnowledgeGraphEngine
from orgprompt.graph.invariants import validate_expansion_invariants
from orgprompt.search.hybrid import HybridSearchEngine

REPO_ROOT = Path(__file__).resolve().parent.parent
BRAIN_PLAYBOOK = Path(
    "/home/pakmingw/.gemini/antigravity/brain/1e96291d-9d64-4bac-9f19-67c0822cf354/social_media_channel_launch_playbook.md"
)
REPO_PLAYBOOK = REPO_ROOT / "artifacts" / "superhuman_roles" / "social_media_channel_launch_playbook.md"

EXPECTED_CREATOR_TOOLS = {
    "tool_davinci_premiere_nle": "davinci_premiere_nle",
    "tool_youtube_studio_analytics": "youtube_studio_analytics",
    "tool_frameio_descript_clipper": "frameio_descript_clipper",
    "tool_studiobinder_moviemagic": "studiobinder_moviemagic",
}

EXPECTED_12_ROLES = [
    "media_indie_film_line_producer_upm",
    "media_film_development_packaging_exec",
    "media_post_production_supervisor_finishing",
    "creator_youtube_head_of_ideation_packaging",
    "creator_retention_scriptwriter_story_producer",
    "creator_lead_retention_video_editor",
    "creator_thumbnail_designer_visual_psychologist",
    "creator_short_form_vertical_producer",
    "creator_channel_showrunner_creative_director",
    "creator_youtube_analytics_strategist",
    "creator_brand_partnerships_monetization_lead",
    "creator_solo_founder_one_person_media_studio",
]

EXPECTED_6_STUDIOS = [
    ("a24", "A24"),
    ("blumhouse_productions", "Blumhouse Productions"),
    ("beast_industries", "Beast Industries"),
    ("mythical_entertainment", "Mythical Entertainment"),
    ("corridor_digital", "Corridor Digital"),
    ("kurzgesagt", "Kurzgesagt"),
]

EXPECTED_2_SUPERHUMANS = [
    ("superhuman_solo_channel_founder_showrunner", "role_creator_solo_founder_one_person_media_studio"),
    ("superhuman_viral_packaging_retention_architect", "role_creator_youtube_head_of_ideation_packaging"),
]


@pytest.fixture(scope="module")
def live_db() -> sqlite3.Connection:
    conn = get_connection(get_default_db_path())
    yield conn
    conn.close()


def test_01_four_creator_film_vertical_tools_exist(live_db: sqlite3.Connection) -> None:
    cur = live_db.cursor()
    for tool_id, slug in EXPECTED_CREATOR_TOOLS.items():
        row = cur.execute(
            "SELECT id, slug, name, category, vendor_examples_json, typical_artifacts_json, description "
            "FROM tools WHERE id = ? AND slug = ?",
            (tool_id, slug),
        ).fetchone()
        assert row is not None, f"Missing vertical creator tool: {tool_id} ({slug})"
        assert row[3] == "VERTICAL_DOMAIN"
        assert len(json.loads(row[4])) >= 2
        assert len(json.loads(row[5])) >= 2
        assert len(row[6].strip()) >= 30


def test_02_twelve_canonical_film_and_creator_roles_complete(live_db: sqlite3.Connection) -> None:
    cur = live_db.cursor()
    for slug in EXPECTED_12_ROLES:
        role_id = f"role_{slug}"
        row = cur.execute(
            "SELECT id, slug, name, system_prompt, character_count FROM canonical_roles WHERE id = ? AND slug = ?",
            (role_id, slug),
        ).fetchone()
        assert row is not None, f"Missing canonical role: {slug}"
        _, _, name, prompt, char_cnt = row
        assert len(prompt) >= 6000, f"Role {slug} prompt length {len(prompt)} < 6,000"
        assert char_cnt >= 6000
        for sec_num in range(1, 8):
            assert f"## {sec_num}." in prompt, f"Role {slug} missing Section {sec_num}"

        # Verify FTS5 index presence
        fts_hit = cur.execute("SELECT COUNT(*) FROM roles_fts WHERE role_id = ?", (role_id,)).fetchone()[0]
        assert fts_hit >= 1, f"Role {slug} missing from roles_fts"

        # Verify 5 day-to-day use cases
        uc_cnt = cur.execute("SELECT COUNT(*) FROM role_use_cases WHERE role_id = ?", (role_id,)).fetchone()[0]
        assert uc_cnt == 5, f"Role {slug} expected 5 use cases, got {uc_cnt}"

        # Verify 11 dual-layer tools (6 horizontal + 5 vertical)
        tool_cats = cur.execute(
            "SELECT t.category, COUNT(*) FROM role_tooling rt JOIN tools t ON rt.tool_id = t.id "
            "WHERE rt.role_id = ? GROUP BY t.category",
            (role_id,),
        ).fetchall()
        cat_map = dict(tool_cats)
        total_tools = sum(cat_map.values())
        assert total_tools == 11, f"Role {slug} expected 11 mapped tools, got {total_tools} ({cat_map})"
        assert cat_map.get("HORIZONTAL_PRODUCTIVITY", 0) == 6
        assert cat_map.get("VERTICAL_DOMAIN", 0) == 5

        # Verify GenAI build plan
        plan_cnt = cur.execute("SELECT COUNT(*) FROM role_genai_plans WHERE role_id = ?", (role_id,)).fetchone()[0]
        assert plan_cnt == 1, f"Role {slug} missing role_genai_plans record"

        # Verify 6 acyclic subagents in Personal Subagent Swarm
        swarms = cur.execute(
            "SELECT subagent_role, interaction_dag_json FROM role_subagent_swarms WHERE role_id = ?",
            (role_id,),
        ).fetchall()
        assert len(swarms) == 6, f"Role {slug} expected 6 subagents, got {len(swarms)}"
        swarm_dag = nx.DiGraph()
        for sa_role, dag_json in swarms:
            dag_spec = json.loads(dag_json)
            swarm_dag.add_node(sa_role)
            for up in dag_spec.get("upstream", []):
                swarm_dag.add_edge(up, sa_role)
            for down in dag_spec.get("downstream", []):
                swarm_dag.add_edge(sa_role, down)
        assert nx.is_directed_acyclic_graph(swarm_dag), f"Swarm DAG for {slug} contains a cycle!"

        # Verify REPORTS_TO and workflow edges
        reports_to = cur.execute(
            "SELECT COUNT(*) FROM role_edges WHERE source_role_id = ? AND edge_type = 'REPORTS_TO'",
            (role_id,),
        ).fetchone()[0]
        assert reports_to >= 1, f"Role {slug} missing REPORTS_TO edge"

        wf_edges = cur.execute(
            "SELECT COUNT(*) FROM role_edges WHERE (source_role_id = ? OR target_role_id = ?) "
            "AND edge_type IN ('COLLABORATES_WITH', 'HANDS_OFF_TO', 'REVIEWS_AND_GATES', 'CHALLENGES_OR_AUDITS')",
            (role_id, role_id),
        ).fetchone()[0]
        assert wf_edges >= 2, f"Role {slug} has < 2 workflow edges ({wf_edges})"


def test_03_six_onboarded_studios_and_graph_invariants(live_db: sqlite3.Connection) -> None:
    cur = live_db.cursor()
    ws_catalog = (
        REPO_ROOT / ".agents" / "skills" / "org-company-deep-onboard" / "references" / "onboarded_companies.md"
    ).read_text(encoding="utf-8")
    global_catalog = Path(
        "/home/pakmingw/.gemini/config/skills/org-company-deep-onboard/references/onboarded_companies.md"
    ).read_text(encoding="utf-8")

    for slug, expected_name in EXPECTED_6_STUDIOS:
        comp_id = f"f500_{slug}"
        c_row = cur.execute(
            "SELECT id, slug, name, rank, revenue_billions FROM fortune500_companies WHERE id = ? AND slug = ?",
            (comp_id, slug),
        ).fetchone()
        assert c_row is not None, f"Onboarded studio missing from fortune500_companies: {slug}"
        assert expected_name in c_row[2]
        assert c_row[3] >= 502

        emp_cnt = cur.execute("SELECT COUNT(*) FROM employs_role WHERE company_id = ?", (comp_id,)).fetchone()[0]
        assert emp_cnt >= 10, f"Studio {slug} employs too few roles: {emp_cnt}"

        cic_cnt = cur.execute(
            "SELECT COUNT(*) FROM company_internet_comparisons WHERE company_id = ?", (comp_id,)
        ).fetchone()[0]
        assert cic_cnt == 1, f"Studio {slug} missing company_internet_comparisons entry"

        bp_path = REPO_ROOT / "artifacts" / "company_onboarding" / f"{slug}_genai_blueprint.md"
        assert bp_path.exists(), f"Missing GenAI blueprint: {bp_path}"
        assert len(bp_path.read_text(encoding="utf-8")) >= 5000

        assert slug in ws_catalog and expected_name in ws_catalog
        assert slug in global_catalog and expected_name in global_catalog

    G = KnowledgeGraphEngine.build_from_db(conn=live_db)
    val = validate_expansion_invariants(G)
    assert val.is_valid is True, f"Knowledge graph invariant violations: {[v.message for v in val.violations]}"


def test_04_hybrid_search_retrieves_creator_and_film_roles_in_top_5() -> None:
    engine = HybridSearchEngine.build_from_db()
    q1 = [r.slug for r in engine.search("YouTube thumbnail CTR retention video editor", top_k=5).results]
    assert set(q1) & {
        "creator_thumbnail_designer_visual_psychologist",
        "creator_lead_retention_video_editor",
        "creator_youtube_head_of_ideation_packaging",
    }, f"Unexpected Top-5 for YouTube CTR/editor query: {q1}"

    q2 = [r.slug for r in engine.search("indie film line producer micro-budget", top_k=5).results]
    assert "media_indie_film_line_producer_upm" in q2, f"Expected indie film line producer in Top-5, got: {q2}"

    q3 = [r.slug for r in engine.search("solo creator social media channel", top_k=5).results]
    assert set(q3) & {
        "creator_solo_founder_one_person_media_studio",
        "creator_channel_showrunner_creative_director",
    }, f"Expected solo creator / channel showrunner in Top-5, got: {q3}"


def test_05_creator_superhumans_and_channel_launch_playbook(live_db: sqlite3.Connection) -> None:
    cur = live_db.cursor()
    for sh_slug, expected_primary_role_id in EXPECTED_2_SUPERHUMANS:
        row = cur.execute(
            "SELECT id, slug, primary_role_id, deep_superhuman_prompt, package_json "
            "FROM superhuman_role_profiles WHERE slug = ?",
            (sh_slug,),
        ).fetchone()
        assert row is not None, f"Missing persisted superhuman profile: {sh_slug}"
        assert row[2] == expected_primary_role_id
        assert len(row[3]) >= 20_000
        pkg = json.loads(row[4])
        assert len(pkg["adjacent_roles"]) >= 4
        assert len(pkg["on_the_job_crucibles"]["crucible_episodes"]) >= 4
        assert len(pkg["unknown_problem_epistemology"]["stages"]) == 5

        md_file = REPO_ROOT / "artifacts" / "superhuman_roles" / f"{sh_slug}.md"
        json_file = REPO_ROOT / "artifacts" / "superhuman_roles" / f"{sh_slug}.json"
        assert md_file.exists() and md_file.stat().st_size >= 20_000
        assert json_file.exists() and json_file.stat().st_size >= 20_000

    assert REPO_PLAYBOOK.exists(), f"Missing repo playbook: {REPO_PLAYBOOK}"
    pb_text = REPO_PLAYBOOK.read_text(encoding="utf-8")
    assert len(pb_text) >= 25_000
    for marker in (
        "## 1. How Production Organizations Actually Work Across 4 Scale Tiers",
        "## 2. The Creator Knowledge Graph: The 12 Core Roles & Artifact Handoff Pipeline",
        "## 3. Starting as an Army of One",
        "## 4. The Creator Hiring Ladder",
        "## 5. Weekly Production Operating System & Quality Gates",
        "## 6. Ready-to-Run CLI Commands & Prompts in Your Database",
        "```mermaid",
        "creator_solo_founder_one_person_media_studio",
        "superhuman_solo_channel_founder_showrunner",
        "superhuman_viral_packaging_retention_architect",
    ):
        assert marker in pb_text, f"Playbook missing required section/marker: {marker}"

    unescaped_dollars = [i + 1 for i, ln in enumerate(pb_text.splitlines()) if re.search(r"(?<!\\)\$", ln)]
    assert len(unescaped_dollars) == 0, f"Unescaped '$' found on playbook lines: {unescaped_dollars}"
    if BRAIN_PLAYBOOK.exists():
        assert BRAIN_PLAYBOOK.read_text(encoding="utf-8") == pb_text
