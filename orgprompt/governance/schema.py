"""Dedicated Fiduciary Oversight & Independent Audit SQLite Schema (`orgprompt.governance.schema`).

Keeps all Board of Directors and Independent Auditor tables strictly isolated above and outside
the operating management hierarchy (`canonical_roles` / `fortune500_companies`), using WAL mode
and a 30-second SQLite busy timeout for zero-contention concurrent execution.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional, Union

from orgprompt.db.connection import get_default_db_path


GOVERNANCE_CATEGORIES = ("BOARD_DIRECTOR", "INDEPENDENT_AUDITOR")
COMPANY_STAGES = ("PUBLIC_ENTERPRISE", "VENTURE_OR_BOUTIQUE")
GOVERNANCE_EDGE_TYPES = (
    "OVERSEES_AND_ADVISES",
    "CHALLENGES_CAPITAL_ALLOCATION",
    "ATTESTS_FINANCIAL_CONTROLS",
    "AUDITS_STRATEGIC_AND_AI_PERFORMANCE",
    "GATES_COMPENSATION_AND_SUCCESSION",
)

GOVERNANCE_SCHEMA_DDL = """
CREATE TABLE IF NOT EXISTS governance_roles (
    id TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    governance_category TEXT NOT NULL CHECK(governance_category IN ('BOARD_DIRECTOR', 'INDEPENDENT_AUDITOR')),
    committee_type TEXT NOT NULL,
    selected_industries_json TEXT NOT NULL DEFAULT '[]',
    typical_human_background TEXT NOT NULL,
    fiduciary_mandate TEXT NOT NULL,
    quarterly_review_cadence_json TEXT NOT NULL DEFAULT '[]',
    kpi_value_tree_json TEXT NOT NULL DEFAULT '{}',
    red_flag_triggers_json TEXT NOT NULL DEFAULT '[]',
    oversight_targets_json TEXT NOT NULL DEFAULT '[]',
    system_prompt TEXT NOT NULL,
    character_count INTEGER NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_gov_roles_slug ON governance_roles(slug);
CREATE INDEX IF NOT EXISTS idx_gov_roles_category ON governance_roles(governance_category);
CREATE INDEX IF NOT EXISTS idx_gov_roles_committee ON governance_roles(committee_type);

CREATE TABLE IF NOT EXISTS industry_board_compositions (
    id TEXT PRIMARY KEY,
    industry_slug TEXT NOT NULL,
    industry_name TEXT NOT NULL,
    company_stage TEXT NOT NULL CHECK(company_stage IN ('PUBLIC_ENTERPRISE', 'VENTURE_OR_BOUTIQUE')),
    board_size INTEGER NOT NULL,
    seat_role_slugs_json TEXT NOT NULL DEFAULT '[]',
    external_auditor_slugs_json TEXT NOT NULL DEFAULT '[]',
    charter_summary TEXT NOT NULL,
    quarterly_agenda_json TEXT NOT NULL DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(industry_slug, company_stage)
);

CREATE INDEX IF NOT EXISTS idx_ibc_industry_slug ON industry_board_compositions(industry_slug);
CREATE INDEX IF NOT EXISTS idx_ibc_stage ON industry_board_compositions(company_stage);

CREATE TABLE IF NOT EXISTS governance_oversight_edges (
    id TEXT PRIMARY KEY,
    governance_role_id TEXT NOT NULL REFERENCES governance_roles(id) ON DELETE CASCADE,
    target_management_role_slug TEXT NOT NULL,
    edge_type TEXT NOT NULL CHECK(edge_type IN (
        'OVERSEES_AND_ADVISES',
        'CHALLENGES_CAPITAL_ALLOCATION',
        'ATTESTS_FINANCIAL_CONTROLS',
        'AUDITS_STRATEGIC_AND_AI_PERFORMANCE',
        'GATES_COMPENSATION_AND_SUCCESSION'
    )),
    review_artifact TEXT NOT NULL,
    protocol TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(governance_role_id, target_management_role_slug, edge_type)
);

CREATE INDEX IF NOT EXISTS idx_goe_gov_role ON governance_oversight_edges(governance_role_id);
CREATE INDEX IF NOT EXISTS idx_goe_target_mgmt ON governance_oversight_edges(target_management_role_slug);
CREATE INDEX IF NOT EXISTS idx_goe_edge_type ON governance_oversight_edges(edge_type);

CREATE TABLE IF NOT EXISTS superhuman_governance_profiles (
    id TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    base_governance_role_slug TEXT NOT NULL,
    target_problem_or_company TEXT NOT NULL,
    fused_committee_slugs_json TEXT NOT NULL DEFAULT '[]',
    academic_and_credential_foundation_json TEXT NOT NULL DEFAULT '{}',
    boardroom_and_audit_crucibles_json TEXT NOT NULL DEFAULT '{}',
    fiduciary_temperament_json TEXT NOT NULL DEFAULT '{}',
    unknown_risk_epistemology_json TEXT NOT NULL DEFAULT '{}',
    developer_context TEXT DEFAULT '',
    deep_superhuman_governance_prompt TEXT NOT NULL,
    package_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sgp_slug ON superhuman_governance_profiles(slug);
CREATE INDEX IF NOT EXISTS idx_sgp_base_role ON superhuman_governance_profiles(base_governance_role_slug);
"""


def ensure_governance_schema(
    db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None,
    timeout: float = 30.0,
) -> sqlite3.Connection:
    """Non-destructively ensures the 4 Fiduciary Governance tables exist with WAL + 30s timeout.

    Never deletes from, locks, or modifies `canonical_roles` or `fortune500_companies`.
    """
    busy_ms = int(max(timeout, 30.0) * 1000)
    if isinstance(db_path_or_conn, sqlite3.Connection):
        conn = db_path_or_conn
        conn.execute(f"PRAGMA busy_timeout = {busy_ms};")
        conn.executescript(GOVERNANCE_SCHEMA_DDL)
        conn.commit()
        return conn

    target_path = (
        str(db_path_or_conn)
        if db_path_or_conn is not None
        else str(get_default_db_path())
    )
    if target_path != ":memory:":
        parent = Path(target_path).parent
        if parent:
            parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(target_path, timeout=max(timeout, 30.0))
    conn.execute("PRAGMA foreign_keys = ON;")
    if target_path != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    conn.execute(f"PRAGMA busy_timeout = {busy_ms};")
    conn.executescript(GOVERNANCE_SCHEMA_DDL)
    conn.commit()
    return conn


__all__ = [
    "GOVERNANCE_CATEGORIES",
    "COMPANY_STAGES",
    "GOVERNANCE_EDGE_TYPES",
    "GOVERNANCE_SCHEMA_DDL",
    "ensure_governance_schema",
]
