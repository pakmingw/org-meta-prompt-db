"""Seed data loader and database seeding functions."""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional, Union

from orgprompt.db.connection import get_connection, init_db

SEED_DATA_JSON_PATH = Path(__file__).resolve().parent / "seed_data.json"


def get_seed_data() -> Dict[str, Any]:
    """Loads and returns the compiled seed data dictionary."""
    if not SEED_DATA_JSON_PATH.exists():
        raise FileNotFoundError(f"Seed data file not found at {SEED_DATA_JSON_PATH}")
    with open(SEED_DATA_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def seed_database(
    conn: Optional[Union[sqlite3.Connection, str, Path]] = None, db_path: Optional[str | Path] = None
) -> sqlite3.Connection:
    """Populates the SQLite database with 16 industries, 48 exemplar orgs,
    120 functional operating units, 336 canonical roles, artifacts, mechanisms,
    and edges. Ensures idempotent execution within an atomic transaction.
    """
    if isinstance(conn, (str, Path)):
        db_path = conn
        conn = None

    if conn is None:
        conn = init_db(db_path)
    else:
        cursor = conn.cursor()
        has_table = cursor.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='industries'"
        ).fetchone()[0]
        if not has_table:
            from orgprompt.db.connection import get_schema_sql
            conn.executescript(get_schema_sql())
            conn.commit()

    data = get_seed_data()

    with conn:
        # 1. Industries
        conn.executemany(
            """INSERT OR REPLACE INTO industries (
                id, slug, name, description, category, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?)""",
            [
                (
                    ind["id"],
                    ind["slug"],
                    ind["name"],
                    ind["description"],
                    ind["category"],
                    ind.get("metadata_json", "{}"),
                )
                for ind in data["industries"]
            ],
        )

        # 2. Exemplar Orgs
        conn.executemany(
            """INSERT OR REPLACE INTO exemplar_orgs (
                id, industry_id, slug, name, description, signature_mechanisms_summary, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    org["id"],
                    org["industry_id"],
                    org["slug"],
                    org["name"],
                    org["description"],
                    org["signature_mechanisms_summary"],
                    org.get("metadata_json", "{}"),
                )
                for org in data["exemplar_orgs"]
            ],
        )

        # 3. Org Units
        conn.executemany(
            """INSERT OR REPLACE INTO org_units (
                id, exemplar_org_id, slug, name, division, department, unit_type, description, core_value_loop, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    u["id"],
                    u["exemplar_org_id"],
                    u["slug"],
                    u["name"],
                    u["division"],
                    u["department"],
                    u["unit_type"],
                    u["description"],
                    u["core_value_loop"],
                    u.get("metadata_json", "{}"),
                )
                for u in data["org_units"]
            ],
        )

        # 4. Artifacts
        conn.executemany(
            """INSERT OR REPLACE INTO artifacts (
                id, slug, name, artifact_type, schema_definition, description, exemplar_context, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    a["id"],
                    a["slug"],
                    a["name"],
                    a["artifact_type"],
                    a["schema_definition"],
                    a["description"],
                    a["exemplar_context"],
                    a.get("metadata_json", "{}"),
                )
                for a in data["artifacts"]
            ],
        )

        # 5. Operating Mechanisms
        conn.executemany(
            """INSERT OR REPLACE INTO operating_mechanisms (
                id, exemplar_org_id, slug, name, mechanism_type, description, execution_steps_json, enforcement_rules, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    m["id"],
                    m["exemplar_org_id"],
                    m["slug"],
                    m["name"],
                    m["mechanism_type"],
                    m["description"],
                    m["execution_steps_json"],
                    m["enforcement_rules"],
                    m.get("metadata_json", "{}"),
                )
                for m in data["operating_mechanisms"]
            ],
        )

        # 6. Canonical Roles (triggers populate roles_fts)
        conn.executemany(
            """INSERT OR REPLACE INTO canonical_roles (
                id, org_unit_id, slug, name, seniority_level, role_archetype, mission,
                system_prompt, character_count, capabilities_json, mental_models_json,
                domain_heuristics_json, technical_vocabulary_json, anti_patterns_json, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    r["id"],
                    r["org_unit_id"],
                    r["slug"],
                    r["name"],
                    r["seniority_level"],
                    r["role_archetype"],
                    r["mission"],
                    r["system_prompt"],
                    r["character_count"],
                    r["capabilities_json"],
                    r["mental_models_json"],
                    r["domain_heuristics_json"],
                    r["technical_vocabulary_json"],
                    r["anti_patterns_json"],
                    r.get("metadata_json", "{}"),
                )
                for r in data["canonical_roles"]
            ],
        )

        # 7. Role Edges
        conn.executemany(
            """INSERT OR REPLACE INTO role_edges (
                id, source_role_id, target_role_id, edge_type, description, protocol, cadence, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    e["id"],
                    e["source_role_id"],
                    e["target_role_id"],
                    e["edge_type"],
                    e["description"],
                    e.get("protocol", ""),
                    e.get("cadence", "CONTINUOUS"),
                    e.get("metadata_json", "{}"),
                )
                for e in data["role_edges"]
            ],
        )

        # 8. Role Artifacts
        conn.executemany(
            """INSERT OR REPLACE INTO role_artifacts (
                id, role_id, artifact_id, direction, frequency, description, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    ra["id"],
                    ra["role_id"],
                    ra["artifact_id"],
                    ra["direction"],
                    ra.get("frequency", "CONTINUOUS"),
                    ra["description"],
                    ra.get("metadata_json", "{}"),
                )
                for ra in data["role_artifacts"]
            ],
        )

        # 9. Role Mechanisms
        conn.executemany(
            """INSERT OR REPLACE INTO role_mechanisms (
                id, role_id, mechanism_id, participation_level, description, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?)""",
            [
                (
                    rm["id"],
                    rm["role_id"],
                    rm["mechanism_id"],
                    rm["participation_level"],
                    rm["description"],
                    rm.get("metadata_json", "{}"),
                )
                for rm in data["role_mechanisms"]
            ],
        )

    return conn
