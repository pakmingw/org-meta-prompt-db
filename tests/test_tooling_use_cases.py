"""Tests for Dual-Layer Tooling (Horizontal + Vertical) and Day-to-Day Role Use Cases."""

import json
import sqlite3
import pytest
from orgprompt.db.connection import get_connection, init_db
from orgprompt.db.seed_tooling import (
    HORIZONTAL_TOOLS,
    VERTICAL_TOOLS,
    seed_tools_catalog,
    seed_use_cases_and_tooling,
)
from orgprompt.models import RoleTooling, RoleUseCase, Tool, ToolDefinition


@pytest.fixture
def db_conn() -> sqlite3.Connection:
    """Provides a connection to the active knowledge base database, ensuring seeded state."""
    conn = get_connection()
    cur = conn.cursor()
    cnt = cur.execute("SELECT COUNT(*) FROM role_use_cases").fetchone()[0]
    if cnt < 2000:
        seed_tools_catalog(conn)
        seed_use_cases_and_tooling(conn)
        conn.commit()
    yield conn
    conn.close()


def test_tools_catalog_count_and_categories(db_conn: sqlite3.Connection):
    """Asserts tools table contains >= 45 tools and both horizontal and vertical categories exist."""
    cur = db_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tools")
    total_tools = cur.fetchone()[0]
    assert total_tools >= 45, f"Expected >= 45 tools, found {total_tools}"

    cur.execute("SELECT category, COUNT(*) FROM tools GROUP BY category")
    category_counts = dict(cur.fetchall())
    assert "HORIZONTAL_PRODUCTIVITY" in category_counts
    assert "VERTICAL_DOMAIN" in category_counts

    assert category_counts["HORIZONTAL_PRODUCTIVITY"] >= 6
    assert category_counts["VERTICAL_DOMAIN"] >= 40

    # Ensure all 6 required horizontal archetypes are present
    expected_horizontal = {
        "WORD_PROCESSOR", "SPREADSHEET_PROCESSOR", "SLIDE_PRESENTER",
        "MEETING_NOTE_TAKER", "COMMUNICATION_TRIAGE", "BI_ANALYTICS"
    }
    cur.execute("SELECT archetype FROM tools WHERE category = 'HORIZONTAL_PRODUCTIVITY'")
    present_horizontal = {row[0] for row in cur.fetchall()}
    assert expected_horizontal.issubset(present_horizontal), f"Missing horizontal archetypes: {expected_horizontal - present_horizontal}"


def test_role_use_cases_volume_and_coverage(db_conn: sqlite3.Connection):
    """Asserts role_use_cases count >= 2,000 and every canonical role has >= 4 use cases."""
    cur = db_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM role_use_cases")
    total_use_cases = cur.fetchone()[0]
    assert total_use_cases >= 2000, f"Expected >= 2,000 role use cases, found {total_use_cases}"

    cur.execute("SELECT COUNT(*) FROM canonical_roles")
    total_roles = cur.fetchone()[0]
    assert total_roles >= 500, f"Expected >= 500 canonical roles, found {total_roles}"

    # Verify coverage: zero roles with < 4 use cases
    cur.execute("""
        SELECT r.id, r.name, COUNT(u.id) as uc_count
        FROM canonical_roles r
        LEFT JOIN role_use_cases u ON r.id = u.role_id
        GROUP BY r.id
        HAVING uc_count < 4
    """)
    under_represented = cur.fetchall()
    assert len(under_represented) == 0, f"Found {len(under_represented)} roles with < 4 use cases: {under_represented[:5]}"

    # Verify distinct cadences present
    cur.execute("SELECT DISTINCT cadence FROM role_use_cases")
    cadences = {row[0] for row in cur.fetchall()}
    assert {"DAILY", "WEEKLY", "MONTHLY", "AD_HOC"}.issubset(cadences)


def test_role_use_cases_data_integrity(db_conn: sqlite3.Connection):
    """Asserts all use case fields are non-null, with valid JSON arrays and substantive bottlenecks."""
    cur = db_conn.cursor()
    cur.execute("""
        SELECT id, role_id, title, cadence, trigger_event, inputs_consumed_json,
               horizontal_tools_json, vertical_tools_json, cognitive_bottlenecks, output_artifacts_json
        FROM role_use_cases
        LIMIT 500
    """)
    rows = cur.fetchall()
    assert len(rows) > 0

    valid_cadences = {"DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "AD_HOC", "CONTINUOUS"}

    for row in rows:
        uc_id, role_id, title, cadence, trigger, inps_json, htools_json, vtools_json, bot, outs_json = row

        assert uc_id.startswith("ruc_")
        assert role_id.startswith("role_")
        assert len(title.strip()) >= 5
        assert cadence in valid_cadences
        assert len(trigger.strip()) >= 10
        assert len(bot.strip()) >= 20, f"Cognitive bottleneck too short for {uc_id}"

        # Parse JSON fields
        inputs = json.loads(inps_json)
        assert isinstance(inputs, list) and len(inputs) > 0, f"Inputs empty for {uc_id}"

        htools = json.loads(htools_json)
        assert isinstance(htools, list) and len(htools) > 0, f"Horizontal tools empty for {uc_id}"

        vtools = json.loads(vtools_json)
        assert isinstance(vtools, list) and len(vtools) > 0, f"Vertical tools empty for {uc_id}"

        outputs = json.loads(outs_json)
        assert isinstance(outputs, list) and len(outputs) > 0, f"Outputs empty for {uc_id}"


def test_role_tooling_associations(db_conn: sqlite3.Connection):
    """Asserts role_tooling count >= 2,500 with zero orphan tool IDs or role IDs."""
    cur = db_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM role_tooling")
    total_associations = cur.fetchone()[0]
    assert total_associations >= 2500, f"Expected >= 2,500 role_tooling records, found {total_associations}"

    # Verify every role has at least 3 tools
    cur.execute("""
        SELECT role_id, COUNT(*) as tool_count
        FROM role_tooling
        GROUP BY role_id
        HAVING tool_count < 3
    """)
    under_tooled = cur.fetchall()
    assert len(under_tooled) == 0, f"Found roles with < 3 tools: {under_tooled}"

    # Verify zero orphan tool_id (tools that don't exist in tools table)
    cur.execute("""
        SELECT rt.id, rt.tool_id
        FROM role_tooling rt
        LEFT JOIN tools t ON rt.tool_id = t.id
        WHERE t.id IS NULL
    """)
    orphan_tools = cur.fetchall()
    assert len(orphan_tools) == 0, f"Found orphan tool IDs in role_tooling: {orphan_tools}"

    # Verify zero orphan role_id (roles that don't exist in canonical_roles table)
    cur.execute("""
        SELECT rt.id, rt.role_id
        FROM role_tooling rt
        LEFT JOIN canonical_roles r ON rt.role_id = r.id
        WHERE r.id IS NULL
    """)
    orphan_roles = cur.fetchall()
    assert len(orphan_roles) == 0, f"Found orphan role IDs in role_tooling: {orphan_roles}"


def test_foreign_key_cascade_and_integrity(db_conn: sqlite3.Connection):
    """Asserts PRAGMA foreign_key_check returns zero errors across all tables."""
    cur = db_conn.cursor()
    cur.execute("PRAGMA foreign_key_check")
    violations = cur.fetchall()
    assert len(violations) == 0, f"Foreign key integrity violations detected: {violations}"


def test_pydantic_models_validation(db_conn: sqlite3.Connection):
    """Tests Pydantic models Tool, ToolDefinition, RoleUseCase, and RoleTooling."""
    db_conn.row_factory = sqlite3.Row
    cur = db_conn.cursor()

    # Tool & ToolDefinition
    cur.execute("SELECT * FROM tools WHERE category = 'HORIZONTAL_PRODUCTIVITY' LIMIT 1")
    t_row = dict(cur.fetchone())
    tool = Tool(**t_row)
    assert tool.id == t_row["id"]
    assert tool.layer == "HORIZONTAL_PRODUCTIVITY"
    assert len(tool.vendor_examples) > 0
    assert tool["name"] == tool.name
    assert tool.get("nonexistent", "fallback") == "fallback"

    tool_def = ToolDefinition(**t_row)
    assert tool_def.id == tool.id

    # RoleUseCase
    cur.execute("SELECT * FROM role_use_cases LIMIT 1")
    uc_row = dict(cur.fetchone())
    uc = RoleUseCase(**uc_row)
    assert uc.id == uc_row["id"]
    assert uc.trigger == uc.trigger_event
    assert uc.inputs == uc.inputs_consumed
    assert uc.domain_tools == uc.vertical_tools
    assert uc["title"] == uc.title

    # RoleTooling
    cur.execute("SELECT * FROM role_tooling LIMIT 1")
    rt_row = dict(cur.fetchone())
    rt = RoleTooling(**rt_row)
    assert rt.id == rt_row["id"]
    assert rt.proficiency_level in ("EXPERT", "PROFICIENT", "WORKING_KNOWLEDGE", "BASIC")
    assert rt["primary_purpose"] == rt.primary_purpose


def test_schema_constraints_enforcement():
    """Verifies CHECK and UNIQUE constraints on tools, role_use_cases, and role_tooling."""
    conn = init_db(":memory:")
    cur = conn.cursor()

    # Invalid tool category
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("""
            INSERT INTO tools (id, slug, name, category, archetype, description)
            VALUES ('t_bad', 'bad', 'Bad Tool', 'INVALID_CAT', 'ARCH', 'Desc')
        """)

    # Valid tool
    cur.execute("""
        INSERT INTO tools (id, slug, name, category, archetype, description)
        VALUES ('t_good', 'good', 'Good Tool', 'HORIZONTAL_PRODUCTIVITY', 'ARCH', 'Desc')
    """)

    # Prerequisite industry, org, unit, role for foreign keys
    cur.execute("INSERT INTO industries (id, slug, name, description, category) VALUES ('ind_t', 't', 'T', 'D', 'C')")
    cur.execute("INSERT INTO exemplar_orgs (id, industry_id, slug, name, description, signature_mechanisms_summary) VALUES ('org_t', 'ind_t', 'ot', 'OT', 'D', 'S')")
    cur.execute("INSERT INTO org_units (id, exemplar_org_id, slug, name, division, department, unit_type, description, core_value_loop) VALUES ('unit_t', 'org_t', 'ut', 'UT', 'Div', 'Dept', 'ENGINEERING', 'Desc', 'Loop')")
    cur.execute("INSERT INTO canonical_roles (id, org_unit_id, slug, name, seniority_level, role_archetype, mission, system_prompt, character_count) VALUES ('role_t', 'unit_t', 'rt', 'RT', 'C_SUITE', 'executive_strategy', 'M', 'P', 1)")

    # Invalid cadence
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("""
            INSERT INTO role_use_cases (id, role_id, title, cadence, trigger_event, cognitive_bottlenecks)
            VALUES ('ruc_bad', 'role_t', 'Title', 'INVALID_CADENCE', 'Trig', 'Bot')
        """)

    # Duplicate role_tooling (UNIQUE constraint)
    cur.execute("""
        INSERT INTO role_tooling (id, role_id, tool_id, usage_frequency, proficiency_level, primary_purpose)
        VALUES ('rt_1', 'role_t', 't_good', 'PRIMARY_DAILY', 'EXPERT', 'Purpose')
    """)
    with pytest.raises(sqlite3.IntegrityError):
        cur.execute("""
            INSERT INTO role_tooling (id, role_id, tool_id, usage_frequency, proficiency_level, primary_purpose)
            VALUES ('rt_dup', 'role_t', 't_good', 'PRIMARY_DAILY', 'EXPERT', 'Duplicate')
        """)
    conn.close()
