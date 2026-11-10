"""Adversarial stress-testing suite for Milestone Exp-M2.

Empirically challenges:
1. Complete null and whitespace scans across all tables.
2. JSON parsing and content validity across all 2,735 use cases and 51 tools.
3. Universal tool ID referential integrity: every tool ID in horizontal/vertical JSON exists in `tools`.
4. Exact cadence distribution across all 547 canonical roles.
5. Query latency benchmarks under diverse workloads (< 5ms threshold).
6. Complex 4-table join performance and correctness.
7. Negative constraint enforcement (foreign keys, check constraints, unique constraints).
"""

import json
import sqlite3
import time
from typing import Dict, List, Set
import pytest
from orgprompt.db.connection import get_connection


@pytest.fixture
def db():
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")
    yield conn
    conn.close()


def test_adv_01_complete_null_and_empty_check(db: sqlite3.Connection):
    """Scan every single column in tools, role_use_cases, and role_tooling for NULL or empty strings."""
    cur = db.cursor()

    # 1. tools table
    cur.execute("SELECT id, slug, name, category, archetype, vendor_examples_json, typical_artifacts_json, description, metadata_json FROM tools")
    tools = cur.fetchall()
    assert len(tools) >= 45, f"Tools count too low: {len(tools)}"
    for row in tools:
        for idx, val in enumerate(row):
            assert val is not None, f"NULL found in tools column {idx} for row {row[0]}"
            if isinstance(val, str):
                assert val.strip() != "", f"Empty string in tools column {idx} for row {row[0]}"

    # 2. role_use_cases table
    total_roles = cur.execute("SELECT COUNT(*) FROM canonical_roles").fetchone()[0]
    cur.execute("""
        SELECT id, role_id, title, cadence, trigger_event, inputs_consumed_json,
               horizontal_tools_json, vertical_tools_json, cognitive_bottlenecks,
               output_artifacts_json, metadata_json
        FROM role_use_cases
    """)
    use_cases = cur.fetchall()
    assert len(use_cases) >= 2735 and len(use_cases) == 5 * total_roles, (
        f"Expected 5 * {total_roles} = {5 * total_roles} use cases (>= 2735), got {len(use_cases)}"
    )
    for row in use_cases:
        for idx, val in enumerate(row):
            assert val is not None, f"NULL found in role_use_cases column {idx} for uc {row[0]}"
            if isinstance(val, str):
                assert val.strip() != "", f"Empty string in role_use_cases column {idx} for uc {row[0]}"

    # 3. role_tooling table
    cur.execute("SELECT id, role_id, tool_id, usage_frequency, proficiency_level, primary_purpose, metadata_json FROM role_tooling")
    role_toolings = cur.fetchall()
    assert len(role_toolings) >= 2500, f"Expected >= 2500 role_toolings, got {len(role_toolings)}"
    for row in role_toolings:
        for idx, val in enumerate(row):
            assert val is not None, f"NULL found in role_tooling column {idx} for rt {row[0]}"
            if isinstance(val, str):
                assert val.strip() != "", f"Empty string in role_tooling column {idx} for rt {row[0]}"


def test_adv_02_json_parse_and_non_empty_arrays(db: sqlite3.Connection):
    """Stress test JSON parsing across all role use cases (>= 2,735) and verify non-empty array elements."""
    cur = db.cursor()
    total_roles = cur.execute("SELECT COUNT(*) FROM canonical_roles").fetchone()[0]
    cur.execute("""
        SELECT id, inputs_consumed_json, horizontal_tools_json, vertical_tools_json,
               output_artifacts_json, metadata_json
        FROM role_use_cases
    """)
    rows = cur.fetchall()
    assert len(rows) >= 2735 and len(rows) == 5 * total_roles

    for uc_id, inps_j, htools_j, vtools_j, outs_j, meta_j in rows:
        # Inputs
        inputs = json.loads(inps_j)
        assert isinstance(inputs, list), f"{uc_id}: inputs not a list"
        assert len(inputs) >= 2, f"{uc_id}: inputs length < 2"
        for item in inputs:
            assert isinstance(item, str) and item.strip() != "", f"{uc_id}: empty input item"

        # Horizontal tools
        htools = json.loads(htools_j)
        assert isinstance(htools, list), f"{uc_id}: horizontal_tools not a list"
        assert len(htools) >= 1, f"{uc_id}: horizontal_tools length < 1"
        for item in htools:
            assert isinstance(item, str) and item.strip() != "", f"{uc_id}: empty htool item"

        # Vertical tools
        vtools = json.loads(vtools_j)
        assert isinstance(vtools, list), f"{uc_id}: vertical_tools not a list"
        assert len(vtools) >= 1, f"{uc_id}: vertical_tools length < 1"
        for item in vtools:
            assert isinstance(item, str) and item.strip() != "", f"{uc_id}: empty vtool item"

        # Output artifacts
        outs = json.loads(outs_j)
        assert isinstance(outs, list), f"{uc_id}: output_artifacts not a list"
        assert len(outs) >= 2, f"{uc_id}: output_artifacts length < 2"
        for item in outs:
            assert isinstance(item, str) and item.strip() != "", f"{uc_id}: empty output item"

        # Metadata
        meta = json.loads(meta_j)
        assert isinstance(meta, dict), f"{uc_id}: metadata not a dict"
        assert "role_seniority" in meta
        assert "industry" in meta


def test_adv_03_tool_id_referential_integrity(db: sqlite3.Connection):
    """Empirically verify that EVERY tool ID referenced in role_use_cases (both horizontal and vertical) exists in tools table."""
    cur = db.cursor()
    cur.execute("SELECT id FROM tools")
    valid_tool_ids = {row[0] for row in cur.fetchall()}
    assert len(valid_tool_ids) >= 45

    cur.execute("SELECT id, horizontal_tools_json, vertical_tools_json FROM role_use_cases")
    all_use_cases = cur.fetchall()

    referenced_tools: Set[str] = set()
    missing_in_tools: Dict[str, List[str]] = {}

    for uc_id, h_json, v_json in all_use_cases:
        h_tools = json.loads(h_json)
        v_tools = json.loads(v_json)

        for tid in h_tools + v_tools:
            referenced_tools.add(tid)
            if tid not in valid_tool_ids:
                missing_in_tools.setdefault(tid, []).append(uc_id)

    assert len(missing_in_tools) == 0, f"Found referenced tools that do not exist in tools table: {missing_in_tools}"

    # Also verify role_tooling
    cur.execute("SELECT DISTINCT tool_id FROM role_tooling")
    rt_tool_ids = {row[0] for row in cur.fetchall()}
    unresolved_rt_tools = rt_tool_ids - valid_tool_ids
    assert len(unresolved_rt_tools) == 0, f"Found unresolved tool IDs in role_tooling: {unresolved_rt_tools}"


def test_adv_04_cadence_distribution_across_roles(db: sqlite3.Connection):
    """Verify cadence distribution across all canonical roles (>= 547): exactly 1 of each (DAILY, WEEKLY, MONTHLY, QUARTERLY, AD_HOC)."""
    cur = db.cursor()
    cur.execute("SELECT id FROM canonical_roles")
    role_ids = [row[0] for row in cur.fetchall()]
    assert len(role_ids) >= 547, f"Expected >= 547 canonical roles, got {len(role_ids)}"

    expected_cadences = {"DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "AD_HOC"}

    cur.execute("SELECT role_id, cadence, COUNT(*) FROM role_use_cases GROUP BY role_id, cadence")
    role_cadence_counts = cur.fetchall()

    role_cadence_map: Dict[str, Set[str]] = {}
    for r_id, cad, count in role_cadence_counts:
        assert count == 1, f"Role {r_id} has duplicate use cases for cadence {cad}: count={count}"
        role_cadence_map.setdefault(r_id, set()).add(cad)

    for r_id in role_ids:
        cads = role_cadence_map.get(r_id, set())
        assert cads == expected_cadences, f"Role {r_id} missing cadences: {expected_cadences - cads}"

    # Overall cadence totals
    cur.execute("SELECT cadence, COUNT(*) FROM role_use_cases GROUP BY cadence")
    totals = dict(cur.fetchall())
    for cad in expected_cadences:
        assert totals.get(cad) == len(role_ids), f"Cadence {cad} count {totals.get(cad)} != {len(role_ids)}"


def test_adv_05_query_latency_benchmarks(db: sqlite3.Connection):
    """Test lookup latency of tools and use cases across diverse roles (< 5ms per lookup threshold)."""
    cur = db.cursor()

    # Select 20 roles across diverse archetypes and seniorities
    cur.execute("""
        SELECT id, name, seniority_level, role_archetype
        FROM canonical_roles
        WHERE seniority_level IN ('C_SUITE', 'VP', 'PRINCIPAL', 'SENIOR_IC', 'MID_LEVEL_IC')
        ORDER BY RANDOM()
        LIMIT 50
    """)
    sampled_roles = cur.fetchall()
    assert len(sampled_roles) >= 30

    latencies_single_lookup: List[float] = []
    latencies_complex_join: List[float] = []

    for r_id, r_name, seniority, archetype in sampled_roles:
        # Benchmark 1: Single role lookup fetching role + use cases
        t0 = time.perf_counter()
        cur.execute("""
            SELECT u.id, u.title, u.cadence, u.trigger_event, u.cognitive_bottlenecks
            FROM role_use_cases u
            WHERE u.role_id = ?
            ORDER BY u.cadence
        """, (r_id,))
        ucs = cur.fetchall()
        t1 = time.perf_counter()
        assert len(ucs) == 5
        latencies_single_lookup.append((t1 - t0) * 1000.0)

        # Benchmark 2: Complex 4-table join
        t0 = time.perf_counter()
        cur.execute("""
            SELECT r.name, r.seniority_level, u.title, u.cadence, t.name, t.category, rt.usage_frequency, rt.proficiency_level
            FROM canonical_roles r
            JOIN role_use_cases u ON r.id = u.role_id
            JOIN role_tooling rt ON r.id = rt.role_id
            JOIN tools t ON rt.tool_id = t.id
            WHERE r.id = ?
        """, (r_id,))
        join_rows = cur.fetchall()
        t1 = time.perf_counter()
        assert len(join_rows) >= 20  # 5 use cases x 6 tools = 30 rows
        latencies_complex_join.append((t1 - t0) * 1000.0)

    avg_single = sum(latencies_single_lookup) / len(latencies_single_lookup)
    p95_single = sorted(latencies_single_lookup)[int(len(latencies_single_lookup) * 0.95)]
    max_single = max(latencies_single_lookup)

    avg_join = sum(latencies_complex_join) / len(latencies_complex_join)
    p95_join = sorted(latencies_complex_join)[int(len(latencies_complex_join) * 0.95)]
    max_join = max(latencies_complex_join)

    print(f"\n[LATENCY BENCHMARK] Single Role Use-Case Lookup (50 samples): avg={avg_single:.3f}ms, p95={p95_single:.3f}ms, max={max_single:.3f}ms")
    print(f"[LATENCY BENCHMARK] Complex 4-Table Join (50 samples): avg={avg_join:.3f}ms, p95={p95_join:.3f}ms, max={max_join:.3f}ms")

    # Invariant: p95 latency must be strictly under 5ms
    assert p95_single < 5.0, f"p95 single lookup latency {p95_single:.2f}ms exceeds 5ms limit!"
    assert p95_join < 5.0, f"p95 complex join latency {p95_join:.2f}ms exceeds 5ms limit!"


def test_adv_06_adversarial_constraint_stress():
    """Verify SQLite constraints on tools, role_use_cases, and role_tooling."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    from orgprompt.db.connection import init_db
    # Initialize full schema
    with open("orgprompt/db/schema.sql") as f:
        conn.executescript(f.read())

    # Insert baseline industry, exemplar org, org unit, canonical role
    cur.execute("INSERT INTO industries (id, slug, name, description, category) VALUES ('ind_test', 'test', 'Test Ind', 'Desc', 'Cat')")
    cur.execute("INSERT INTO exemplar_orgs (id, industry_id, slug, name, description, signature_mechanisms_summary) VALUES ('org_test', 'ind_test', 'ot', 'Org Test', 'Desc', 'Sig')")
    cur.execute("INSERT INTO org_units (id, exemplar_org_id, slug, name, division, department, unit_type, description, core_value_loop) VALUES ('unit_test', 'org_test', 'ut', 'Unit Test', 'Div', 'Dept', 'GOVERNANCE', 'Desc', 'Loop')")
    cur.execute("INSERT INTO canonical_roles (id, org_unit_id, slug, name, seniority_level, role_archetype, mission, system_prompt, character_count) VALUES ('role_test', 'unit_test', 'rt', 'Role Test', 'C_SUITE', 'executive_strategy', 'Mission', 'Prompt', 100)")
    cur.execute("INSERT INTO tools (id, slug, name, category, archetype, description) VALUES ('tool_h1', 'h1', 'H1', 'HORIZONTAL_PRODUCTIVITY', 'WORD_PROCESSOR', 'Desc')")

    # Test 1: Invalid category in tools
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("INSERT INTO tools (id, slug, name, category, archetype, description) VALUES ('tool_bad', 'bad', 'Bad', 'INVALID_CAT', 'WP', 'Desc')")

    # Test 2: Invalid cadence in role_use_cases
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("INSERT INTO role_use_cases (id, role_id, title, cadence, trigger_event, cognitive_bottlenecks) VALUES ('ruc_bad', 'role_test', 'Title', 'HOURLY', 'Trig', 'Bot')")

    # Test 3: Foreign key violation in role_use_cases (non-existent role)
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("INSERT INTO role_use_cases (id, role_id, title, cadence, trigger_event, cognitive_bottlenecks) VALUES ('ruc_bad_fk', 'role_nonexistent', 'Title', 'DAILY', 'Trig', 'Bot')")

    # Test 4: Foreign key violation in role_tooling (non-existent tool)
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("INSERT INTO role_tooling (id, role_id, tool_id, usage_frequency, proficiency_level, primary_purpose) VALUES ('rt_bad_t', 'role_test', 'tool_ghost', 'PRIMARY_DAILY', 'EXPERT', 'Purp')")

    # Test 5: Foreign key violation in role_tooling (non-existent role)
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("INSERT INTO role_tooling (id, role_id, tool_id, usage_frequency, proficiency_level, primary_purpose) VALUES ('rt_bad_r', 'role_ghost', 'tool_h1', 'PRIMARY_DAILY', 'EXPERT', 'Purp')")

    # Test 6: Invalid usage_frequency
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("INSERT INTO role_tooling (id, role_id, tool_id, usage_frequency, proficiency_level, primary_purpose) VALUES ('rt_bad_uf', 'role_test', 'tool_h1', 'RARELY', 'EXPERT', 'Purp')")

    # Test 7: Invalid proficiency_level
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("INSERT INTO role_tooling (id, role_id, tool_id, usage_frequency, proficiency_level, primary_purpose) VALUES ('rt_bad_pl', 'role_test', 'tool_h1', 'PRIMARY_DAILY', 'NOVICE', 'Purp')")

    # Test 8: Duplicate (role_id, tool_id) in role_tooling
    cur.execute("INSERT INTO role_tooling (id, role_id, tool_id, usage_frequency, proficiency_level, primary_purpose) VALUES ('rt_ok', 'role_test', 'tool_h1', 'PRIMARY_DAILY', 'EXPERT', 'Purp')")
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("INSERT INTO role_tooling (id, role_id, tool_id, usage_frequency, proficiency_level, primary_purpose) VALUES ('rt_dup', 'role_test', 'tool_h1', 'FREQUENT_WEEKLY', 'PROFICIENT', 'Purp2')")

    conn.close()


def test_adv_07_cascade_deletion():
    """Verify that deleting a canonical role cleanly cascade-deletes use cases and role_tooling."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    with open("orgprompt/db/schema.sql") as f:
        conn.executescript(f.read())

    cur.execute("INSERT INTO industries (id, slug, name, description, category) VALUES ('ind_t', 't', 'T', 'D', 'C')")
    cur.execute("INSERT INTO exemplar_orgs (id, industry_id, slug, name, description, signature_mechanisms_summary) VALUES ('org_t', 'ind_t', 'ot', 'OT', 'D', 'S')")
    cur.execute("INSERT INTO org_units (id, exemplar_org_id, slug, name, division, department, unit_type, description, core_value_loop) VALUES ('unit_t', 'org_t', 'ut', 'UT', 'Div', 'Dept', 'GOVERNANCE', 'Desc', 'Loop')")
    cur.execute("INSERT INTO canonical_roles (id, org_unit_id, slug, name, seniority_level, role_archetype, mission, system_prompt, character_count) VALUES ('role_del', 'unit_t', 'rd', 'RD', 'C_SUITE', 'executive_strategy', 'M', 'P', 1)")
    cur.execute("INSERT INTO tools (id, slug, name, category, archetype, description) VALUES ('tool_del', 'td', 'TD', 'HORIZONTAL_PRODUCTIVITY', 'WORD_PROCESSOR', 'Desc')")

    cur.execute("INSERT INTO role_use_cases (id, role_id, title, cadence, trigger_event, cognitive_bottlenecks) VALUES ('ruc_del', 'role_del', 'Title', 'DAILY', 'Trig', 'Bot')")
    cur.execute("INSERT INTO role_tooling (id, role_id, tool_id, usage_frequency, proficiency_level, primary_purpose) VALUES ('rt_del', 'role_del', 'tool_del', 'PRIMARY_DAILY', 'EXPERT', 'Purp')")

    assert cur.execute("SELECT COUNT(*) FROM role_use_cases WHERE role_id = 'role_del'").fetchone()[0] == 1
    assert cur.execute("SELECT COUNT(*) FROM role_tooling WHERE role_id = 'role_del'").fetchone()[0] == 1

    # Delete canonical role
    cur.execute("DELETE FROM canonical_roles WHERE id = 'role_del'")
    assert cur.execute("SELECT COUNT(*) FROM role_use_cases WHERE role_id = 'role_del'").fetchone()[0] == 0
    assert cur.execute("SELECT COUNT(*) FROM role_tooling WHERE role_id = 'role_del'").fetchone()[0] == 0
    assert cur.execute("SELECT COUNT(*) FROM tools WHERE id = 'tool_del'").fetchone()[0] == 1

    # Delete tool
    cur.execute("INSERT INTO canonical_roles (id, org_unit_id, slug, name, seniority_level, role_archetype, mission, system_prompt, character_count) VALUES ('role_del2', 'unit_t', 'rd2', 'RD2', 'C_SUITE', 'executive_strategy', 'M', 'P', 1)")
    cur.execute("INSERT INTO role_tooling (id, role_id, tool_id, usage_frequency, proficiency_level, primary_purpose) VALUES ('rt_del2', 'role_del2', 'tool_del', 'PRIMARY_DAILY', 'EXPERT', 'Purp')")
    assert cur.execute("SELECT COUNT(*) FROM role_tooling WHERE tool_id = 'tool_del'").fetchone()[0] == 1
    cur.execute("DELETE FROM tools WHERE id = 'tool_del'")
    assert cur.execute("SELECT COUNT(*) FROM role_tooling WHERE tool_id = 'tool_del'").fetchone()[0] == 0

    conn.close()


def test_adv_08_pydantic_model_edge_cases():
    """Verify Pydantic models with varied deserialization formats and property aliases."""
    from orgprompt.models import Tool, RoleUseCase, RoleTooling
    from pydantic import ValidationError

    # 1. Tool with list inputs vs JSON string inputs
    t_from_list = Tool(
        id="t_test", slug="test", name="Test Tool", category="HORIZONTAL_PRODUCTIVITY",
        archetype="WORD_PROCESSOR", vendor_examples=["Vendor A", "Vendor B"],
        typical_artifacts=["Artifact 1"], description="Description"
    )
    assert t_from_list.vendor_examples == ["Vendor A", "Vendor B"]
    assert t_from_list["slug"] == "test"
    assert t_from_list.get("missing", 42) == 42

    t_from_json = Tool(
        id="t_test2", slug="test2", name="Test Tool 2", category="VERTICAL_DOMAIN",
        archetype="CUSTOM", vendor_examples_json='["Vendor X"]',
        typical_artifacts_json='["Artifact Y"]', description="Description 2"
    )
    assert t_from_json.vendor_examples == ["Vendor X"]
    assert t_from_json.typical_artifacts == ["Artifact Y"]

    # 2. RoleUseCase property aliases
    uc = RoleUseCase(
        id="ruc_test", role_id="role_test", title="Test UC", cadence="DAILY",
        trigger_event="Trigger Alpha", inputs_consumed=["Input 1", "Input 2"],
        horizontal_tools=["tool_wp"], vertical_tools=["tool_erp"],
        cognitive_bottlenecks="Cognitive bottleneck description exceeding minimum",
        output_artifacts=["Output 1"]
    )
    assert uc.trigger == "Trigger Alpha"
    assert uc.inputs == ["Input 1", "Input 2"]
    assert uc.domain_tools == ["tool_erp"]

    # 3. Validation rejection on missing mandatory field
    with pytest.raises(ValidationError):
        RoleUseCase(id="ruc_fail", role_id="role_test", title="Incomplete")


def test_adv_09_codebase_loc_and_hygiene():
    """Verify seed_tooling.py is strictly under 350 lines of code."""
    with open("orgprompt/db/seed_tooling.py") as f:
        lines = f.readlines()
    loc = len(lines)
    assert loc < 350, f"seed_tooling.py exceeds 350 LOC limit: {loc} lines"
    assert loc <= 320, f"seed_tooling.py unexpectedly high LOC: {loc} lines"

