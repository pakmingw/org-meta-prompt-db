"""Schema helpers and non-destructive auto-migration utilities for OrgPrompt."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional, Union

from orgprompt.db.connection import get_default_db_path, get_schema_sql


SUPERHUMAN_ROLE_PROFILES_DDL = """
CREATE TABLE IF NOT EXISTS superhuman_role_profiles (
    id TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    problem_statement TEXT NOT NULL,
    primary_role_id TEXT,
    adjacent_role_ids_json TEXT NOT NULL DEFAULT '[]',
    academic_foundation_json TEXT NOT NULL DEFAULT '{}',
    on_the_job_crucibles_json TEXT NOT NULL DEFAULT '{}',
    human_characteristics_json TEXT NOT NULL DEFAULT '{}',
    unknown_problem_protocol_json TEXT NOT NULL DEFAULT '{}',
    developer_context TEXT DEFAULT '',
    deep_superhuman_prompt TEXT NOT NULL,
    package_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_srp_slug ON superhuman_role_profiles(slug);
CREATE INDEX IF NOT EXISTS idx_srp_primary_role ON superhuman_role_profiles(primary_role_id);
"""


def ensure_superhuman_schema(
    db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None,
    timeout: float = 30.0,
) -> sqlite3.Connection:
    """Non-destructively ensures `superhuman_role_profiles` exists using WAL + 30s lock timeout.

    Safe to run concurrently against live databases without truncating or modifying
    any existing tables or rows.
    """
    if isinstance(db_path_or_conn, sqlite3.Connection):
        conn = db_path_or_conn
        conn.execute("PRAGMA busy_timeout = 30000;")
        conn.executescript(SUPERHUMAN_ROLE_PROFILES_DDL)
        conn.commit()
        return conn

    target_path = str(db_path_or_conn) if db_path_or_conn is not None else str(get_default_db_path())
    if target_path != ":memory:":
        parent = Path(target_path).parent
        if parent:
            parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(target_path, timeout=timeout)
    conn.execute("PRAGMA foreign_keys = ON;")
    if target_path != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute(f"PRAGMA busy_timeout = {int(timeout * 1000)};")
    conn.executescript(SUPERHUMAN_ROLE_PROFILES_DDL)
    conn.commit()
    return conn


from orgprompt.governance.schema import GOVERNANCE_SCHEMA_DDL, ensure_governance_schema

__all__ = [
    "SUPERHUMAN_ROLE_PROFILES_DDL",
    "GOVERNANCE_SCHEMA_DDL",
    "ensure_superhuman_schema",
    "ensure_governance_schema",
    "get_schema_sql",
]
