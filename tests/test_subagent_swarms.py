"""Tests for Personal Subagent Swarms ("Role-in-a-Box") & GenAI Tooling Build Plans."""

import json
import re
import sqlite3
import networkx as nx
import pydantic
import pytest
from orgprompt.db.connection import get_connection, init_db
from orgprompt.db.seed_swarms_plans import (
    seed_swarms_and_plans,
    fetch_roles_with_context,
    build_swarms_and_plans,
)
from orgprompt.models import (
    RoleSubagentSwarm,
    RoleGenAIPlan,
    SubagentSpec,
    GenAIPlan,
    VALID_SUBAGENT_ROLES,
)


@pytest.fixture
def db_conn() -> sqlite3.Connection:
    """Provides a connection to the active knowledge base database, ensuring seeded swarms state."""
    conn = get_connection()
    cur = conn.cursor()
    cnt = cur.execute("SELECT COUNT(*) FROM role_subagent_swarms").fetchone()[0]
    if cnt < 2500:
        seed_swarms_and_plans(conn)
        conn.commit()
    yield conn
    conn.close()


def test_subagent_swarms_volume_and_coverage(db_conn: sqlite3.Connection):
    """Asserts role_subagent_swarms count >= 2,500 and every canonical role has 4-7 subagents."""
    cur = db_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM role_subagent_swarms")
    total_swarms = cur.fetchone()[0]
    assert total_swarms >= 2500, f"Expected >= 2,500 subagents, found {total_swarms}"

    cur.execute("SELECT COUNT(*) FROM canonical_roles")
    total_roles = cur.fetchone()[0]
    assert total_roles >= 500, f"Expected >= 500 canonical roles, found {total_roles}"

    # Verify coverage: zero roles with < 4 subagents, every role between 4 and 7 subagents
    cur.execute("""
        SELECT r.id, r.name, COUNT(s.id) as swarm_count
        FROM canonical_roles r
        LEFT JOIN role_subagent_swarms s ON r.id = s.role_id
        GROUP BY r.id
        HAVING swarm_count < 4 OR swarm_count > 7
    """)
    out_of_bounds = cur.fetchall()
    assert len(out_of_bounds) == 0, f"Found roles with out-of-bounds subagents: {out_of_bounds[:5]}"

    # Verify all expected subagent roles exist
    valid_roles = {
        "CHIEF_OF_STAFF", "DOCUMENT_DRAFTER", "QUANTITATIVE_MODELER",
        "DECK_PRESENTER", "MEETING_GRAPH", "DOMAIN_SPECIALIST", "QUALITY_CRITIC"
    }
    cur.execute("SELECT DISTINCT subagent_role FROM role_subagent_swarms")
    found_roles = {row[0] for row in cur.fetchall()}
    assert found_roles.issubset(valid_roles), f"Found invalid subagent roles: {found_roles - valid_roles}"
    assert {"CHIEF_OF_STAFF", "DOCUMENT_DRAFTER", "QUANTITATIVE_MODELER", "DECK_PRESENTER", "MEETING_GRAPH"}.issubset(found_roles)


def test_genai_plans_count_and_completeness(db_conn: sqlite3.Connection):
    """Asserts role_genai_plans count == 547, non-null fields, and valid JSON specs."""
    cur = db_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM canonical_roles")
    expected_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM role_genai_plans")
    plans_count = cur.fetchone()[0]
    assert plans_count == expected_count, f"Expected {expected_count} GenAI plans, found {plans_count}"

    # Verify field integrity on all plans
    cur.execute("""
        SELECT id, role_id, horizontal_genai_spec_json, vertical_genai_spec_json,
               rag_context_architecture, mcp_integrations_json, hitl_guardrails,
               roi_productivity_impact
        FROM role_genai_plans
    """)
    rows = cur.fetchall()
    assert len(rows) == expected_count

    for row in rows:
        pid, rid, h_json, v_json, rag, mcp_json, hitl, roi = row
        assert pid.startswith("rgp_"), f"Invalid plan id: {pid}"
        assert rid, "Empty role_id"
        assert rag and len(rag) > 20, f"RAG architecture too short in plan {pid}"
        assert hitl and len(hitl) > 20, f"HITL guardrails too short in plan {pid}"
        assert roi and len(roi) > 10, f"ROI impact too short in plan {pid}"

        h_spec = json.loads(h_json)
        assert "word_copilot" in h_spec
        assert "excel_modeler" in h_spec
        assert "slide_presenter" in h_spec
        assert "meeting_dispatcher" in h_spec

        v_spec = json.loads(v_json)
        assert "domain_system" in v_spec
        assert "capability" in v_spec

        mcp_list = json.loads(mcp_json)
        assert isinstance(mcp_list, list) and len(mcp_list) >= 3


def test_canonical_roles_prompt_upgrade_section_7(db_conn: sqlite3.Connection):
    """Asserts every role in canonical_roles contains Section 7 header and content."""
    cur = db_conn.cursor()
    cur.execute("SELECT id, name, system_prompt FROM canonical_roles")
    roles = cur.fetchall()

    target_header = "## 7. Day-to-Day Tooling, GenAI Build Plan & Personal Subagent Swarm Protocol"

    for r_id, r_name, prompt in roles:
        assert target_header in prompt, f"Role {r_id} ({r_name}) missing Section 7 header"
        # Check all 7 headers exist
        headers = re.findall(r"## [1-7]\..*", prompt)
        assert len(headers) == 7, f"Role {r_id} has {len(headers)} numbered headers instead of 7: {headers}"


def test_canonical_roles_prompt_length_and_uniqueness(db_conn: sqlite3.Connection):
    """Asserts character_count >= 3000 and len(prompt) >= 3000 for all roles, 100% unique, zero stubs."""
    cur = db_conn.cursor()
    cur.execute("SELECT id, name, system_prompt, character_count FROM canonical_roles")
    roles = cur.fetchall()
    assert len(roles) >= 500

    unique_prompts = set()
    stub_regex = re.compile(r"\b(TODO|FIXME|STUB|placeholder|TBD|see above)\b")

    for r_id, r_name, prompt, ccount in roles:
        assert len(prompt) >= 3000, f"Role {r_id} prompt length {len(prompt)} < 3000"
        assert ccount >= 3000, f"Role {r_id} character_count {ccount} < 3000"
        assert ccount == len(prompt), f"Role {r_id} character_count mismatch: {ccount} != {len(prompt)}"
        assert prompt not in unique_prompts, f"Duplicate prompt detected for role {r_id}"
        unique_prompts.add(prompt)

        stubs = stub_regex.findall(prompt)
        assert len(stubs) == 0, f"Role {r_id} contains placeholder stubs: {stubs}"

    assert len(unique_prompts) == len(roles), "Not all prompts are 100% unique"


def test_foreign_key_cascade_and_integrity(db_conn: sqlite3.Connection):
    """Verifies foreign key constraints, unique constraints, and CASCADE deletion."""
    cur = db_conn.cursor()

    # 1. Clean PRAGMA foreign_key_check
    cur.execute("PRAGMA foreign_key_check")
    violations = cur.fetchall()
    assert violations == [], f"Foreign key check failed: {violations}"

    # 2. Unique constraint on role_genai_plans(role_id)
    cur.execute("SELECT id FROM canonical_roles LIMIT 1")
    sample_role_id = cur.fetchone()[0]

    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("""
            INSERT INTO role_genai_plans (
                id, role_id, horizontal_genai_spec_json, vertical_genai_spec_json,
                rag_context_architecture, mcp_integrations_json, hitl_guardrails,
                roi_productivity_impact
            ) VALUES ('rgp_duplicate_test', ?, '{}', '{}', 'rag', '[]', 'hitl', 'roi')
        """, (sample_role_id,))

    # 3. Unique constraint on role_subagent_swarms(role_id, subagent_role)
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("""
            INSERT INTO role_subagent_swarms (
                id, role_id, subagent_name, subagent_role, system_prompt,
                tool_mcp_bindings_json, interaction_dag_json, hitl_checkpoint
            ) VALUES ('rss_duplicate_test', ?, 'Duplicate CoS', 'CHIEF_OF_STAFF', 'Prompt', '[]', '{}', 'HITL')
        """, (sample_role_id,))

    # 4. Foreign key cascade deletion
    sample_unit_id = cur.execute("SELECT id FROM org_units LIMIT 1").fetchone()[0]
    cur.execute("""
        INSERT INTO canonical_roles (
            id, org_unit_id, slug, name, seniority_level, role_archetype, mission,
            system_prompt, character_count
        ) VALUES (
            'role_cascade_test', ?, 'cascade_test', 'Cascade Tester',
            'PRINCIPAL_STAFF', 'engineering_staff', 'Test cascade deletion',
            'Test prompt with at least required length ' || hex(randomblob(1600)), 3200
        )
    """, (sample_unit_id,))

    cur.execute("""
        INSERT INTO role_subagent_swarms (
            id, role_id, subagent_name, subagent_role, system_prompt, hitl_checkpoint
        ) VALUES ('rss_cascade_test_cos', 'role_cascade_test', 'Tester CoS', 'CHIEF_OF_STAFF', 'Prompt', 'HITL')
    """)

    cur.execute("""
        INSERT INTO role_genai_plans (
            id, role_id, rag_context_architecture, hitl_guardrails, roi_productivity_impact
        ) VALUES ('rgp_cascade_test', 'role_cascade_test', 'RAG arch', 'HITL', 'ROI')
    """)

    # Verify rows exist
    cur.execute("SELECT COUNT(*) FROM role_subagent_swarms WHERE role_id = 'role_cascade_test'")
    assert cur.fetchone()[0] == 1
    cur.execute("SELECT COUNT(*) FROM role_genai_plans WHERE role_id = 'role_cascade_test'")
    assert cur.fetchone()[0] == 1

    # Delete parent role and verify cascade
    cur.execute("DELETE FROM canonical_roles WHERE id = 'role_cascade_test'")
    cur.execute("SELECT COUNT(*) FROM role_subagent_swarms WHERE role_id = 'role_cascade_test'")
    assert cur.fetchone()[0] == 0
    cur.execute("SELECT COUNT(*) FROM role_genai_plans WHERE role_id = 'role_cascade_test'")
    assert cur.fetchone()[0] == 0


def test_pydantic_models_and_properties():
    """Verifies RoleSubagentSwarm and RoleGenAIPlan Pydantic models and aliases."""
    raw_swarm = {
        "id": "rss_sample_role_chief_of_staff",
        "role_id": "sample_role",
        "subagent_name": "Chief of Staff Subagent",
        "subagent_role": "CHIEF_OF_STAFF",
        "system_prompt": "You are the Chief of Staff orchestrating workflows.",
        "tool_mcp_bindings_json": '["mcp://filesystem", "mcp://slack"]',
        "interaction_dag_json": '{"upstream": ["PRINCIPAL"], "downstream": ["DRAFTER"]}',
        "hitl_checkpoint": "Sign-off required.",
    }

    swarm = RoleSubagentSwarm.model_validate(raw_swarm)
    assert swarm.id == "rss_sample_role_chief_of_staff"
    assert swarm.archetype == "CHIEF_OF_STAFF"
    assert swarm.mcp_tools == ["mcp://filesystem", "mcp://slack"]
    assert swarm.upstream_subagents == ["PRINCIPAL"]
    assert swarm.downstream_subagents == ["DRAFTER"]
    assert swarm["subagent_name"] == "Chief of Staff Subagent"
    assert swarm.get("nonexistent", "default") == "default"

    # Alias SubagentSpec
    assert SubagentSpec is RoleSubagentSwarm

    raw_plan = {
        "id": "rgp_sample_role",
        "role_id": "sample_role",
        "horizontal_genai_spec_json": '{"word_copilot": {"capability": "Drafting RFCs"}}',
        "vertical_genai_spec_json": '{"domain_system": "Bloomberg"}',
        "rag_context_architecture": "Dense + sparse RRF",
        "mcp_integrations_json": '["mcp://kb", "mcp://bloomberg"]',
        "hitl_guardrails": "Risk limit approval",
        "roi_productivity_impact": "50% time saved",
    }

    plan = RoleGenAIPlan.model_validate(raw_plan)
    assert plan.id == "rgp_sample_role"
    assert plan.context_rag_architecture == "Dense + sparse RRF"
    assert plan.quantified_roi_impact == "50% time saved"
    assert plan.mcp_integrations == ["mcp://kb", "mcp://bloomberg"]
    assert plan.horizontal_genai_spec["word_copilot"]["capability"] == "Drafting RFCs"
    assert plan["hitl_guardrails"] == "Risk limit approval"

    # Alias GenAIPlan
    assert GenAIPlan is RoleGenAIPlan


def test_fts5_synchronization_with_section_7(db_conn: sqlite3.Connection):
    """Verifies roles_fts table indexes Section 7 content for fast full-text retrieval."""
    cur = db_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM roles_fts")
    fts_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM canonical_roles")
    roles_count = cur.fetchone()[0]
    assert fts_count == roles_count, f"FTS count {fts_count} != roles count {roles_count}"

    # Search for Section 7 tokens
    cur.execute("SELECT COUNT(*) FROM roles_fts WHERE roles_fts MATCH ?", ('"Personal Subagent Swarm"',))
    match_count = cur.fetchone()[0]
    assert match_count == roles_count, f"Expected all {roles_count} roles to match 'Personal Subagent Swarm', found {match_count}"


def test_all_swarms_are_acyclic_dags(db_conn: sqlite3.Connection):
    """Asserts across all roles that their subagent swarm internal edges form a strictly acyclic DAG."""
    cur = db_conn.cursor()
    cur.execute("SELECT DISTINCT role_id FROM role_subagent_swarms")
    roles = cur.fetchall()
    assert len(roles) >= 500, f"Expected >= 500 roles in swarms, found {len(roles)}"

    for (r_id,) in roles:
        cur.execute(
            "SELECT subagent_role, interaction_dag_json FROM role_subagent_swarms WHERE role_id = ?",
            (r_id,),
        )
        rows = cur.fetchall()
        swarm_roles = set(r[0] for r in rows)
        G = nx.DiGraph()
        for s_role, dag_str in rows:
            G.add_node(s_role)
            dag = json.loads(dag_str)
            for ds in dag.get("downstream", []):
                if ds in swarm_roles:
                    G.add_edge(s_role, ds)

        assert nx.is_directed_acyclic_graph(G), (
            f"Role {r_id} swarm is not a DAG! Cycles detected: {list(nx.simple_cycles(G))}"
        )
        topo_order = list(nx.topological_sort(G))
        assert len(topo_order) == len(swarm_roles), (
            f"Topological sort length {len(topo_order)} != swarm size {len(swarm_roles)} for {r_id}"
        )


def test_subagent_role_enum_validation():
    """Asserts that RoleSubagentSwarm strictly validates subagent_role via Literal enum."""
    # 1. Invalid subagent_role raises ValidationError directly
    with pytest.raises(pydantic.ValidationError):
        RoleSubagentSwarm(
            role_id="role_sample",
            subagent_name="Invalid Role Agent",
            subagent_role="INVALID_ROLE_XYZ",  # type: ignore[arg-type]
            system_prompt="System prompt text",
            hitl_checkpoint="Sign-off",
        )

    # 2. Invalid archetype in dict validation raises ValidationError
    with pytest.raises(pydantic.ValidationError):
        RoleSubagentSwarm.model_validate({
            "role_id": "role_sample",
            "subagent_name": "Invalid Role Agent",
            "archetype": "UNSUPPORTED_ROLE_TYPE",
            "system_prompt": "System prompt text",
            "hitl_checkpoint": "Sign-off",
        })

    # 3. All 7 valid roles succeed
    expected_valid_roles = [
        "CHIEF_OF_STAFF",
        "DOCUMENT_DRAFTER",
        "QUANTITATIVE_MODELER",
        "DECK_PRESENTER",
        "MEETING_GRAPH",
        "DOMAIN_SPECIALIST",
        "QUALITY_CRITIC",
    ]
    for valid_role in expected_valid_roles:
        swarm = RoleSubagentSwarm(
            role_id="role_sample",
            subagent_name=f"{valid_role} Agent",
            subagent_role=valid_role,  # type: ignore[arg-type]
            system_prompt="System prompt text",
            hitl_checkpoint="Sign-off",
        )
        assert swarm.subagent_role == valid_role
        assert swarm.archetype == valid_role

