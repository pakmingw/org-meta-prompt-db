"""Unit tests for SQLite schema, constraints, cascading foreign keys, FTS5 virtual table, and triggers."""

import sqlite3
import pytest


def test_schema_tables_exist(empty_db: sqlite3.Connection):
    """Verifies all 9 typed relational tables and FTS5 virtual table exist."""
    cursor = empty_db.cursor()
    tables = [
        row[0]
        for row in cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    ]
    expected_tables = [
        "industries",
        "exemplar_orgs",
        "org_units",
        "canonical_roles",
        "artifacts",
        "operating_mechanisms",
        "role_edges",
        "role_artifacts",
        "role_mechanisms",
        "roles_fts",
        "tools",
        "role_use_cases",
        "role_tooling",
        "role_subagent_swarms",
        "role_genai_plans",
    ]
    for tbl in expected_tables:
        assert tbl in tables, f"Expected table '{tbl}' was not created in schema."


def test_foreign_key_enforcement(empty_db: sqlite3.Connection):
    """Verifies foreign key constraints reject orphaned records."""
    cursor = empty_db.cursor()

    # Attempting to insert an exemplar org referencing a non-existent industry
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            """INSERT INTO exemplar_orgs (id, industry_id, slug, name, description, signature_mechanisms_summary)
               VALUES ('org_test', 'ind_nonexistent', 'test_org', 'Test Org', 'Desc', 'Summary')"""
        )

    # Attempting to insert a role referencing a non-existent org unit
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            """INSERT INTO canonical_roles (
                id, org_unit_id, slug, name, seniority_level, role_archetype, mission,
                system_prompt, character_count
            ) VALUES ('role_test', 'unit_nonexistent', 'test_role', 'Test Role', 'PRINCIPAL_STAFF', 'engineering_staff', 'Mission', 'Prompt', 6)"""
        )


def test_check_constraints(empty_db: sqlite3.Connection):
    """Verifies CHECK constraints enforce valid enum values."""
    cursor = empty_db.cursor()

    # Insert prerequisite industry and org
    cursor.execute(
        "INSERT INTO industries (id, slug, name, description, category) VALUES ('ind_t', 't', 'T', 'D', 'C')"
    )
    cursor.execute(
        "INSERT INTO exemplar_orgs (id, industry_id, slug, name, description, signature_mechanisms_summary) VALUES ('org_t', 'ind_t', 'ot', 'OT', 'D', 'S')"
    )

    # Invalid unit_type
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            """INSERT INTO org_units (id, exemplar_org_id, slug, name, division, department, unit_type, description, core_value_loop)
               VALUES ('unit_t', 'org_t', 'ut', 'UT', 'Div', 'Dept', 'INVALID_UNIT_TYPE', 'Desc', 'Loop')"""
        )

    # Valid unit insertion
    cursor.execute(
        """INSERT INTO org_units (id, exemplar_org_id, slug, name, division, department, unit_type, description, core_value_loop)
           VALUES ('unit_t', 'org_t', 'ut', 'UT', 'Div', 'Dept', 'ENGINEERING', 'Desc', 'Loop')"""
    )

    # Invalid seniority_level
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            """INSERT INTO canonical_roles (
                id, org_unit_id, slug, name, seniority_level, role_archetype, mission,
                system_prompt, character_count
            ) VALUES ('role_t', 'unit_t', 'rt', 'RT', 'INVALID_SENIORITY', 'engineering_staff', 'M', 'P', 1)"""
        )

    # Invalid role_archetype
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute(
            """INSERT INTO canonical_roles (
                id, org_unit_id, slug, name, seniority_level, role_archetype, mission,
                system_prompt, character_count
            ) VALUES ('role_t', 'unit_t', 'rt', 'RT', 'PRINCIPAL_STAFF', 'invalid_archetype', 'M', 'P', 1)"""
        )


def test_cascading_deletes(empty_db: sqlite3.Connection):
    """Verifies cascading deletes properly cascade across industries, orgs, units, and roles."""
    cursor = empty_db.cursor()

    cursor.execute("INSERT INTO industries (id, slug, name, description, category) VALUES ('ind_c', 'c', 'C', 'D', 'Cat')")
    cursor.execute("INSERT INTO exemplar_orgs (id, industry_id, slug, name, description, signature_mechanisms_summary) VALUES ('org_c', 'ind_c', 'oc', 'OC', 'D', 'S')")
    cursor.execute("INSERT INTO org_units (id, exemplar_org_id, slug, name, division, department, unit_type, description, core_value_loop) VALUES ('unit_c', 'org_c', 'uc', 'UC', 'Div', 'Dept', 'R_AND_D', 'D', 'L')")
    cursor.execute("""INSERT INTO canonical_roles (
        id, org_unit_id, slug, name, seniority_level, role_archetype, mission, system_prompt, character_count
    ) VALUES ('role_c', 'unit_c', 'rc', 'RC', 'C_SUITE', 'executive_strategy', 'M', 'P', 1)""")

    assert cursor.execute("SELECT count(*) FROM canonical_roles WHERE id='role_c'").fetchone()[0] == 1

    # Deleting industry should cascade all the way down
    cursor.execute("DELETE FROM industries WHERE id='ind_c'")

    assert cursor.execute("SELECT count(*) FROM exemplar_orgs WHERE id='org_c'").fetchone()[0] == 0
    assert cursor.execute("SELECT count(*) FROM org_units WHERE id='unit_c'").fetchone()[0] == 0
    assert cursor.execute("SELECT count(*) FROM canonical_roles WHERE id='role_c'").fetchone()[0] == 0


def test_fts5_triggers_synchronization(empty_db: sqlite3.Connection):
    """Verifies real-time synchronization triggers keep roles_fts in sync on INSERT, UPDATE, DELETE."""
    cursor = empty_db.cursor()

    cursor.execute("INSERT INTO industries (id, slug, name, description, category) VALUES ('ind_f', 'telecom', 'Telecommunications', 'Desc', 'Cat')")
    cursor.execute("INSERT INTO exemplar_orgs (id, industry_id, slug, name, description, signature_mechanisms_summary) VALUES ('org_f', 'ind_f', 'bell_labs', 'Bell Labs', 'Desc', 'Nobel Open-Door')")
    cursor.execute("INSERT INTO org_units (id, exemplar_org_id, slug, name, division, department, unit_type, description, core_value_loop) VALUES ('unit_f', 'org_f', 'phy_res', 'Physical Sciences Lab', 'Div', 'Dept', 'R_AND_D', 'Desc', 'Loop')")

    # 1. Trigger INSERT
    cursor.execute("""INSERT INTO canonical_roles (
        id, org_unit_id, slug, name, seniority_level, role_archetype, mission,
        system_prompt, character_count, capabilities_json, mental_models_json
    ) VALUES (
        'role_f1', 'unit_f', 'quantum_physicist', 'Lead Quantum Physicist', 'PRINCIPAL_STAFF', 'engineering_staff',
        'Lead quantum experiments and microwave resonators', 'Full quantum system prompt text here...', 38,
        '["quantum", "superconducting", "photonics"]', '["Shannon Capacity", "Josephson Junctions"]'
    )""")

    # Verify present in FTS5
    fts_rows = cursor.execute("SELECT role_id, name, industry, org_unit FROM roles_fts WHERE roles_fts MATCH 'quantum'").fetchall()
    assert len(fts_rows) == 1
    assert fts_rows[0][0] == "role_f1"
    assert fts_rows[0][1] == "Lead Quantum Physicist"
    assert fts_rows[0][2] == "Telecommunications"
    assert fts_rows[0][3] == "Physical Sciences Lab"

    # 2. Trigger UPDATE
    cursor.execute("UPDATE canonical_roles SET name='Chief Quantum Architect' WHERE id='role_f1'")
    fts_updated = cursor.execute("SELECT name FROM roles_fts WHERE role_id='role_f1'").fetchone()
    assert fts_updated[0] == "Chief Quantum Architect"

    # 3. Trigger DELETE
    cursor.execute("DELETE FROM canonical_roles WHERE id='role_f1'")
    fts_after_del = cursor.execute("SELECT count(*) FROM roles_fts WHERE role_id='role_f1'").fetchone()
    assert fts_after_del[0] == 0


def test_database_seeding_completeness(seeded_db: sqlite3.Connection):
    """Verifies seed data satisfies all quantitative thresholds and foreign key integrity."""
    cursor = seeded_db.cursor()

    # Check zero foreign key violations
    fk_violations = cursor.execute("PRAGMA foreign_key_check").fetchall()
    assert len(fk_violations) == 0, f"Foreign key integrity violations detected: {fk_violations}"

    # Check Macro Industries threshold (>= 15, expected 16)
    ind_count = cursor.execute("SELECT count(*) FROM industries").fetchone()[0]
    assert ind_count >= 15
    assert ind_count == 16

    # Check Exemplar Organizations threshold (>= 45, expected 48)
    org_count = cursor.execute("SELECT count(*) FROM exemplar_orgs").fetchone()[0]
    assert org_count >= 45
    assert org_count == 48

    # Verify exactly 3 exemplar orgs per industry
    orgs_per_ind = cursor.execute("SELECT industry_id, count(*) FROM exemplar_orgs GROUP BY industry_id").fetchall()
    for row in orgs_per_ind:
        assert row[1] == 3, f"Industry {row[0]} has {row[1]} exemplar orgs instead of 3."

    # Check Operating Units threshold (>= 100, expected 120)
    unit_count = cursor.execute("SELECT count(*) FROM org_units").fetchone()[0]
    assert unit_count >= 100
    assert unit_count == 120

    # Check Canonical Roles threshold (300-500, expected 336)
    role_count = cursor.execute("SELECT count(*) FROM canonical_roles").fetchone()[0]
    assert 300 <= role_count <= 500
    assert role_count == 336

    # Check Artifacts
    art_count = cursor.execute("SELECT count(*) FROM artifacts").fetchone()[0]
    assert art_count >= 300

    # Check Operating Mechanisms
    mech_count = cursor.execute("SELECT count(*) FROM operating_mechanisms").fetchone()[0]
    assert mech_count >= 24

    # Check Role Edges
    edge_count = cursor.execute("SELECT count(*) FROM role_edges").fetchone()[0]
    assert edge_count >= 1000

    # Check Prompts: length >= 1200 characters and 100% uniqueness
    prompts = cursor.execute("SELECT id, system_prompt, character_count FROM canonical_roles").fetchall()
    unique_prompts = set()
    for pid, ptext, ccount in prompts:
        assert len(ptext) >= 1200, f"Role {pid} prompt length {len(ptext)} < 1200"
        assert ccount == len(ptext)
        assert ptext not in unique_prompts, f"Duplicate prompt detected for role {pid}"
        unique_prompts.add(ptext)

    # Check FTS5 index is fully synchronized
    fts_count = cursor.execute("SELECT count(*) FROM roles_fts").fetchone()[0]
    assert fts_count == 336
