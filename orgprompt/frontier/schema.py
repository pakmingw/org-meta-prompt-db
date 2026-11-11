"""Dedicated SQLite Schema for the Nov 2026 Frontier AI Lab & Real-World Join Layer (`orgprompt.frontier.schema`).

Non-destructively defines and auto-migrates the 4 relational join tables:
1. `frontier_ai_labs` (5 Nov 2026 Frontier AI Labs)
2. `frontier_lab_pods` (30 Internal Operating Pods — 6 per Lab)
3. `real_world_to_frontier_bridges` (Cross-Industry & Horizontal Join Blueprints)
4. `role_frontier_joins` (100% Relational Join Coverage across all Canonical Roles)
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional, Union

from orgprompt.db.connection import get_default_db_path


FRONTIER_JOIN_MECHANISMS = (
    "FDE_WORKFLOW_EMBEDDING",
    "RL_VERIFIER_AND_EVAL_HARNESS",
    "MCP_CONTEXT_AND_TOOL_RUNTIME",
    "DOMAIN_DISTILLATION_AND_POST_TRAINING",
    "SAFETY_CONTROL_AND_RED_TEAM_GATE",
    "WORLD_MODEL_AND_SCIENTIFIC_SIM",
)

FRONTIER_POD_CATEGORIES = (
    "PRETRAINING_AND_ARCHITECTURE",
    "REASONING_AND_AGENTIC_POST_TRAINING",
    "ALIGNMENT_CONTROL_AND_EVALS",
    "GIGAWATT_INFRA_AND_INFERENCE",
    "APPLIED_PRODUCT_AND_ORCHESTRATION",
    "FDE_ENTERPRISE_AND_SCIENCE",
)

FRONTIER_SCHEMA_DDL = """
CREATE TABLE IF NOT EXISTS frontier_ai_labs (
    id TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    company_id TEXT,
    headquarters TEXT NOT NULL,
    corporate_governance_structure TEXT NOT NULL,
    leadership_json TEXT NOT NULL DEFAULT '[]',
    research_to_product_loop TEXT NOT NULL,
    flagship_models_json TEXT NOT NULL DEFAULT '[]',
    safety_control_framework TEXT NOT NULL,
    enterprise_gtm_fde_motion TEXT NOT NULL,
    compute_and_infra_strategy TEXT NOT NULL,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_fal_slug ON frontier_ai_labs(slug);
CREATE INDEX IF NOT EXISTS idx_fal_company ON frontier_ai_labs(company_id);

CREATE TABLE IF NOT EXISTS frontier_lab_pods (
    id TEXT PRIMARY KEY,
    lab_id TEXT NOT NULL REFERENCES frontier_ai_labs(id) ON DELETE CASCADE,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    pod_category TEXT NOT NULL CHECK(pod_category IN (
        'PRETRAINING_AND_ARCHITECTURE',
        'REASONING_AND_AGENTIC_POST_TRAINING',
        'ALIGNMENT_CONTROL_AND_EVALS',
        'GIGAWATT_INFRA_AND_INFERENCE',
        'APPLIED_PRODUCT_AND_ORCHESTRATION',
        'FDE_ENTERPRISE_AND_SCIENCE'
    )),
    mandate TEXT NOT NULL,
    canonical_role_slugs_json TEXT NOT NULL DEFAULT '[]',
    signature_artifacts_json TEXT NOT NULL DEFAULT '[]',
    operating_cadence TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_flp_lab ON frontier_lab_pods(lab_id);
CREATE INDEX IF NOT EXISTS idx_flp_category ON frontier_lab_pods(pod_category);

CREATE TABLE IF NOT EXISTS real_world_to_frontier_bridges (
    id TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    industry_id TEXT NOT NULL REFERENCES industries(id) ON DELETE CASCADE,
    domain_name TEXT NOT NULL,
    real_world_goal TEXT NOT NULL,
    real_world_role_slugs_json TEXT NOT NULL DEFAULT '[]',
    real_world_bottlenecks_json TEXT NOT NULL DEFAULT '[]',
    why_naive_llm_wrappers_fail TEXT NOT NULL,
    lead_frontier_labs_json TEXT NOT NULL DEFAULT '[]',
    frontier_pod_ids_json TEXT NOT NULL DEFAULT '[]',
    frontier_role_slugs_json TEXT NOT NULL DEFAULT '[]',
    frontier_technical_recipe TEXT NOT NULL,
    joint_enterprise_lab_pod_topology TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_rwfb_industry ON real_world_to_frontier_bridges(industry_id);
CREATE INDEX IF NOT EXISTS idx_rwfb_slug ON real_world_to_frontier_bridges(slug);

CREATE TABLE IF NOT EXISTS role_frontier_joins (
    id TEXT PRIMARY KEY,
    source_enterprise_role_id TEXT NOT NULL REFERENCES canonical_roles(id) ON DELETE CASCADE,
    target_frontier_role_id TEXT NOT NULL REFERENCES canonical_roles(id) ON DELETE CASCADE,
    join_mechanism TEXT NOT NULL CHECK(join_mechanism IN (
        'FDE_WORKFLOW_EMBEDDING',
        'RL_VERIFIER_AND_EVAL_HARNESS',
        'MCP_CONTEXT_AND_TOOL_RUNTIME',
        'DOMAIN_DISTILLATION_AND_POST_TRAINING',
        'SAFETY_CONTROL_AND_RED_TEAM_GATE',
        'WORLD_MODEL_AND_SCIENTIFIC_SIM'
    )),
    enterprise_pain_point TEXT NOT NULL,
    frontier_lab_capability TEXT NOT NULL,
    joint_artifact TEXT NOT NULL,
    recommended_labs_json TEXT NOT NULL DEFAULT '[]',
    priority_rank INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_enterprise_role_id, target_frontier_role_id, join_mechanism)
);

CREATE INDEX IF NOT EXISTS idx_rfj_source ON role_frontier_joins(source_enterprise_role_id);
CREATE INDEX IF NOT EXISTS idx_rfj_target ON role_frontier_joins(target_frontier_role_id);
CREATE INDEX IF NOT EXISTS idx_rfj_mechanism ON role_frontier_joins(join_mechanism);
"""


def ensure_frontier_schema(
    db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None,
    timeout: float = 30.0,
) -> sqlite3.Connection:
    """Non-destructively ensures the 4 Frontier Lab & Join tables exist with WAL + 30s timeout."""
    busy_ms = int(max(timeout, 30.0) * 1000)
    if isinstance(db_path_or_conn, sqlite3.Connection):
        conn = db_path_or_conn
        conn.execute(f"PRAGMA busy_timeout = {busy_ms};")
        conn.executescript(FRONTIER_SCHEMA_DDL)
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
    conn.executescript(FRONTIER_SCHEMA_DDL)
    conn.commit()
    return conn


__all__ = [
    "FRONTIER_JOIN_MECHANISMS",
    "FRONTIER_POD_CATEGORIES",
    "FRONTIER_SCHEMA_DDL",
    "ensure_frontier_schema",
]
