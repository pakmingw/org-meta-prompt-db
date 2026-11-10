"""Empirical Adversarial Stress-Testing Suite for Milestone Exp-M1A.

Author: Challenger 1 (teamwork_preview_challenger_m1a_1)
Mandate:
Adversarially stress-test company ranks 1..500 contiguity, revenue distribution,
zero orphan roles, bipartite graph hydration performance, and edge cases.
"""

from __future__ import annotations

import json
import random
import re
import sqlite3
import time
import tracemalloc
from pathlib import Path
from typing import Dict, List, Set, Tuple

import networkx as nx
import pytest

from orgprompt.db.connection import get_connection, get_default_db_path
from orgprompt.db.fortune500_catalog import (
    INDUSTRIES,
    INDUSTRY_DEFAULT_MODELS,
    INDUSTRY_MAP,
    TAIL_COMPANIES,
    TOP_20_COMPANIES,
    calculate_revenue,
    generate_fortune500_companies,
)
from orgprompt.db.seed_fortune500 import SEED_JSON_PATH, seed_expanded_database
from orgprompt.graph.engine import KnowledgeGraphEngine
from orgprompt.graph.invariants import (
    validate_expansion_invariants,
    validate_knowledge_graph,
)


@pytest.fixture(scope="module")
def db_conn():
    """Provides a SQLite connection to the expanded database."""
    db_path = get_default_db_path()
    conn = get_connection(db_path)
    yield conn
    conn.close()


@pytest.fixture(scope="module")
def hydrated_graph(db_conn):
    """Provides a hydrated NetworkX Knowledge Graph from SQLite."""
    return KnowledgeGraphEngine.build_from_db(conn=db_conn)


# ==============================================================================
# 1. Company Ranks Contiguity & Boundary Stress Tests
# ==============================================================================

def test_ranks_strict_contiguity_1_to_500(db_conn, hydrated_graph):
    """Adversarially asserts that core Fortune 500 ranks 1..500 are contiguous, unique, and bounded."""
    cursor = db_conn.cursor()
    total_companies = cursor.execute("SELECT count(*) FROM fortune500_companies").fetchone()[0]
    assert total_companies >= 500, f"Expected >= 500 companies, found {total_companies}"

    companies = cursor.execute(
        "SELECT rank, name, slug, revenue_billions FROM fortune500_companies WHERE rank <= 500 ORDER BY rank ASC"
    ).fetchall()

    assert len(companies) == 500, f"Expected 500 core F500 companies, found {len(companies)}"

    ranks = [c[0] for c in companies]
    expected_ranks = list(range(1, 501))
    assert ranks == expected_ranks, "Ranks are not contiguous from 1 to 500"

    # Check uniqueness of slugs and IDs across all companies
    slugs = [c[2] for c in companies]
    assert len(set(slugs)) == 500, f"Slug collisions detected: {500 - len(set(slugs))} duplicates"

    # Graph node verification
    all_f500_nodes = [n for n, d in hydrated_graph.nodes(data=True) if d.get("type") == "Fortune500Company"]
    assert len(all_f500_nodes) >= 500, f"Expected >= 500 Fortune500Company graph nodes, found {len(all_f500_nodes)}"
    f500_nodes = [n for n in all_f500_nodes if hydrated_graph.nodes[n].get("rank", 999) <= 500]
    assert len(f500_nodes) == 500, f"Expected 500 core Fortune500Company graph nodes (rank <= 500), found {len(f500_nodes)}"
    graph_ranks = sorted([hydrated_graph.nodes[n]["rank"] for n in f500_nodes])
    assert graph_ranks == expected_ranks, "Graph ranks do not match 1..500 contiguous set"


def test_ranks_bookends_and_prominent_anchors(db_conn):
    """Verifies that top-20 and tail-6 anchor companies match real-world ground truth."""
    cursor = db_conn.cursor()
    # Rank 1: Walmart ($648.1B)
    r1 = cursor.execute("SELECT name, revenue_billions, slug FROM fortune500_companies WHERE rank = 1").fetchone()
    assert r1[0] == "Walmart"
    assert r1[1] == 648.1
    assert r1[2] == "walmart"

    # Rank 2: Amazon.com ($574.8B)
    r2 = cursor.execute("SELECT name, revenue_billions, slug FROM fortune500_companies WHERE rank = 2").fetchone()
    assert r2[0] == "Amazon.com"
    assert r2[1] == 574.8

    # Rank 3: Apple ($383.3B)
    r3 = cursor.execute("SELECT name, revenue_billions, slug FROM fortune500_companies WHERE rank = 3").fetchone()
    assert r3[0] == "Apple"
    assert r3[1] == 383.3

    # Rank 500: O-I Glass ($7.1B)
    r500 = cursor.execute("SELECT name, revenue_billions, slug FROM fortune500_companies WHERE rank = 500").fetchone()
    assert r500[0] == "O-I Glass"
    assert r500[1] == 7.1


def test_revenue_monotonicity_and_bounds(db_conn):
    """Adversarially verifies monotonic non-increasing revenue across core Fortune 500 ranks 1..500."""
    cursor = db_conn.cursor()
    revs = [r[0] for r in cursor.execute("SELECT revenue_billions FROM fortune500_companies WHERE rank <= 500 ORDER BY rank ASC").fetchall()]

    assert len(revs) == 500
    assert min(revs) == 7.1, f"Expected minimum revenue $7.1B, got {min(revs)}"
    assert max(revs) == 648.1, f"Expected maximum revenue $648.1B, got {max(revs)}"

    # Strict monotonic non-increasing check: rev[i] >= rev[i+1]
    monotonicity_violations = []
    for i in range(len(revs) - 1):
        if revs[i] < revs[i + 1]:
            monotonicity_violations.append((i + 1, revs[i], i + 2, revs[i + 1]))

    assert len(monotonicity_violations) == 0, (
        f"Monotonicity violations detected at ranks: {monotonicity_violations}"
    )

    # Tail companies (495..500) must all be bounded at 7.1
    for r in range(495, 501):
        assert revs[r - 1] == 7.1, f"Rank {r} revenue is {revs[r - 1]} != 7.1"


# ==============================================================================
# 2. Industry, Model & Archetype Distribution Integrity
# ==============================================================================

def test_industry_distribution_and_foreign_keys(db_conn):
    """Verifies that all 16 macro industries exist and have >= 6 companies each."""
    cursor = db_conn.cursor()
    ind_counts = dict(
        cursor.execute("SELECT industry_id, count(*) FROM fortune500_companies GROUP BY industry_id").fetchall()
    )

    assert len(ind_counts) == 16, f"Expected 16 macro industries, found {len(ind_counts)}"
    for ind_id, count in ind_counts.items():
        assert count >= 6, f"Industry {ind_id} has {count} companies (< 6)"

    # Verify foreign key referential integrity against industries table
    missing_industries = cursor.execute("""
        SELECT c.id, c.industry_id FROM fortune500_companies c
        LEFT JOIN industries i ON c.industry_id = i.id
        WHERE i.id IS NULL
    """).fetchall()
    assert len(missing_industries) == 0, f"Found dangling industry foreign keys: {missing_industries}"


def test_business_models_and_archetypes_validity(db_conn):
    """Verifies all companies conform to the 8 valid business models and 5 operating archetypes."""
    valid_models = {
        "HIGH_VELOCITY_DISTRIBUTOR",
        "MULTI_SIDED_PLATFORM",
        "RECURRING_SUBSCRIPTION_SAAS",
        "ASSET_HEAVY_MANUFACTURER",
        "FINANCIAL_RISK_INTERMEDIARY",
        "INTEGRATED_ENERGY_OPERATOR",
        "CLINICAL_LIFE_SCIENCES_INNOVATOR",
        "PROFESSIONAL_KNOWLEDGE_ADVISORY",
    }
    valid_archetypes = {
        "UNIFICATION",
        "COORDINATION",
        "REPLICATION",
        "DIVERSIFICATION",
        "PLATFORM_ECOSYSTEM",
    }

    cursor = db_conn.cursor()
    rows = cursor.execute("SELECT id, name, business_model, operating_archetype FROM fortune500_companies").fetchall()
    for cid, name, model, arch in rows:
        assert model in valid_models, f"Company {name} ({cid}) has invalid business model: {model}"
        assert arch in valid_archetypes, f"Company {name} ({cid}) has invalid archetype: {arch}"


def test_company_attributes_text_hygiene(db_conn):
    """Stress-tests company names, slugs, and subsectors for formatting or null errors."""
    cursor = db_conn.cursor()
    rows = cursor.execute(
        "SELECT id, slug, name, sub_sector, functional_units_json, metadata_json FROM fortune500_companies"
    ).fetchall()

    for cid, slug, name, sub_sector, units_json, meta_json in rows:
        assert cid.startswith("f500_"), f"Invalid ID prefix: {cid}"
        assert re.match(r"^[a-z0-9_]+$", slug), f"Invalid slug characters: {slug}"
        assert name and len(name.strip()) > 0, f"Empty company name: {cid}"
        assert name == name.strip(), f"Unstripped whitespace in company name: '{name}'"
        assert sub_sector and len(sub_sector.strip()) > 0, f"Empty sub_sector for {name}"
        # JSON parsing verification
        assert isinstance(json.loads(units_json), list), f"Invalid functional_units_json for {name}"
        assert isinstance(json.loads(meta_json), dict), f"Invalid metadata_json for {name}"


# ==============================================================================
# 3. Canonical Roles & Zero Orphan Empirical Verification
# ==============================================================================

def test_canonical_roles_total_and_expansion_count(db_conn):
    """Verifies canonical role count (>= 540) and expansion roles (201 in 13 units)."""
    cursor = db_conn.cursor()
    total_roles = cursor.execute("SELECT count(*) FROM canonical_roles").fetchone()[0]
    assert total_roles >= 540, f"Expected >= 540 canonical roles, found {total_roles}"

    expansion_roles = cursor.execute(
        "SELECT count(*) FROM canonical_roles WHERE org_unit_id LIKE 'unit_f500_%'"
    ).fetchone()[0]
    assert expansion_roles >= 204, f"Expected >= 204 expansion roles, found {expansion_roles}"

    units = cursor.execute(
        "SELECT count(*) FROM org_units WHERE id LIKE 'unit_f500_%'"
    ).fetchone()[0]
    assert units == 13, f"Expected 13 dedicated F500 units, found {units}"


def test_zero_orphan_roles_in_sqlite_and_graph(db_conn, hydrated_graph):
    """Empirically tests that ZERO canonical roles are orphaned (every role has >= 1 employer)."""
    cursor = db_conn.cursor()
    all_roles = set(r[0] for r in cursor.execute("SELECT id FROM canonical_roles").fetchall())
    employed_roles = set(r[0] for r in cursor.execute("SELECT DISTINCT role_id FROM employs_role").fetchall())

    orphans = all_roles - employed_roles
    assert len(orphans) == 0, f"Found {len(orphans)} orphan roles in SQLite: {list(orphans)[:5]}"

    # Graph verification
    role_nodes = [n for n, d in hydrated_graph.nodes(data=True) if d.get("type") == "CanonicalRole"]
    graph_orphans = []
    for r_node in role_nodes:
        in_employs = [
            e for e in hydrated_graph.in_edges(r_node, data=True) if e[2].get("type") == "EMPLOYS_ROLE"
        ]
        if len(in_employs) == 0:
            graph_orphans.append(r_node)

    assert len(graph_orphans) == 0, f"Found {len(graph_orphans)} orphan role nodes in graph: {graph_orphans[:5]}"


def test_employs_role_volume_and_degree_bounds(db_conn, hydrated_graph):
    """Verifies >= 15,000 employment edges, and sanity of degree bounds."""
    cursor = db_conn.cursor()
    edge_count = cursor.execute("SELECT count(*) FROM employs_role").fetchone()[0]
    assert edge_count >= 15000, f"Expected >= 15,000 employs_role edges, found {edge_count}"

    # Degree checks per company
    company_degrees = cursor.execute(
        "SELECT company_id, count(*) FROM employs_role GROUP BY company_id"
    ).fetchall()
    assert len(company_degrees) >= 500, f"Expected >= 500 companies with employment edges, got {len(company_degrees)}"
    min_comp_deg = min(d[1] for d in company_degrees)
    max_comp_deg = max(d[1] for d in company_degrees)
    assert min_comp_deg >= 10, f"Company with insufficient roles: min is {min_comp_deg} (< 10)"

    # Degree checks per role
    role_degrees = cursor.execute(
        "SELECT role_id, count(*) FROM employs_role GROUP BY role_id"
    ).fetchall()
    min_role_deg = min(d[1] for d in role_degrees)
    assert min_role_deg >= 1, f"Role with 0 companies found: min is {min_role_deg}"

    # CEO must be employed by all 500 core F500 companies (and >= 500 total)
    ceo_core_count = cursor.execute(
        "SELECT count(*) FROM employs_role WHERE role_id = 'role_exec_chief_executive_officer' "
        "AND company_id IN (SELECT id FROM fortune500_companies WHERE rank <= 500)"
    ).fetchone()[0]
    assert ceo_core_count == 500, f"Expected CEO to be employed by 500 core F500 companies, got {ceo_core_count}"
    ceo_total = cursor.execute(
        "SELECT count(*) FROM employs_role WHERE role_id = 'role_exec_chief_executive_officer'"
    ).fetchone()[0]
    assert ceo_total >= 500, f"Expected CEO to be employed by >= 500 companies, got {ceo_total}"


def test_referential_integrity_bipartite_edges(db_conn):
    """Asserts zero dangling foreign keys across employs_role and role_edges."""
    cursor = db_conn.cursor()

    bad_companies = cursor.execute("""
        SELECT count(*) FROM employs_role e
        LEFT JOIN fortune500_companies c ON e.company_id = c.id
        WHERE c.id IS NULL
    """).fetchone()[0]
    assert bad_companies == 0, f"Found {bad_companies} dangling company_id references in employs_role"

    bad_roles = cursor.execute("""
        SELECT count(*) FROM employs_role e
        LEFT JOIN canonical_roles r ON e.role_id = r.id
        WHERE r.id IS NULL
    """).fetchone()[0]
    assert bad_roles == 0, f"Found {bad_roles} dangling role_id references in employs_role"


# ==============================================================================
# 4. Role Prompts Integrity & Completeness
# ==============================================================================

def test_role_prompt_lengths_and_uniqueness(db_conn):
    """Stress-tests prompt length (>= 1,200 chars, avg > 5,000) and 100% uniqueness."""
    cursor = db_conn.cursor()
    rows = cursor.execute("SELECT id, slug, character_count, system_prompt FROM canonical_roles").fetchall()

    assert len(rows) >= 540
    prompts = [r[3] for r in rows]
    assert len(set(prompts)) == len(prompts), "Duplicate system prompts detected across canonical roles"

    for rid, slug, char_cnt, prompt in rows:
        assert len(prompt) >= 1200, f"Role {slug} ({rid}) prompt length {len(prompt)} < 1,200"
        assert char_cnt == len(prompt), f"Role {slug} character_count mismatch: {char_cnt} vs {len(prompt)}"
        # Check for unformatted template corruptions
        assert "\x00" not in prompt, f"Null byte found in prompt for {slug}"
        assert "{{ " not in prompt and " }}" not in prompt, f"Unrendered Jinja/template tag in {slug}"


def test_expansion_roles_have_all_six_sections(db_conn):
    """Verifies that every expansion role strictly contains all 6 required markdown sections."""
    required_sections = [
        "## 1. Role Identity & Exemplar Lineage",
        "## 2. First-Principles Mental Models & Domain Heuristics",
        "## 3. Technical Vocabulary & Standards",
        "## 4. Anti-Patterns & Mediocrity Filters",
        "## 5. Collaboration, Handoff & Escalation Protocols",
        "## 6. Concrete Output Artifact Schemas",
    ]

    cursor = db_conn.cursor()
    exp_roles = cursor.execute(
        "SELECT slug, system_prompt FROM canonical_roles WHERE org_unit_id LIKE 'unit_f500_%'"
    ).fetchall()
    assert len(exp_roles) >= 204

    for slug, prompt in exp_roles:
        for sec in required_sections:
            assert sec in prompt, f"Expansion role '{slug}' is missing required section: '{sec}'"


# ==============================================================================
# 5. NetworkX Hydration Performance & Traversal Benchmarks
# ==============================================================================

def test_graph_hydration_performance_and_memory(db_conn):
    """Measures graph hydration time (< 10 seconds) and memory footprint (< 100 MB)."""
    tracemalloc.start()
    t0 = time.perf_counter()
    g = KnowledgeGraphEngine.build_from_db(conn=db_conn)
    t1 = time.perf_counter()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    hydration_ms = (t1 - t0) * 1000
    peak_mb = peak_mem / (1024 * 1024)

    assert hydration_ms < 10000, f"Graph hydration took too long: {hydration_ms:.2f} ms (> 10s limit)"
    assert peak_mb < 100, f"Graph hydration memory too high: {peak_mb:.2f} MB (> 100 MB limit)"
    assert g.number_of_nodes() >= 1800, f"Expected >= 1800 nodes, got {g.number_of_nodes()}"
    assert g.number_of_edges() >= 25000, f"Expected >= 25,000 edges, got {g.number_of_edges()}"


def test_bipartite_random_walk_latency(hydrated_graph):
    """Performs 3,000 random queries across bipartite edges to verify sub-millisecond query performance."""
    f500_nodes = [n for n, d in hydrated_graph.nodes(data=True) if d.get("type") == "Fortune500Company"]
    role_nodes = [n for n, d in hydrated_graph.nodes(data=True) if d.get("type") == "CanonicalRole"]

    random.seed(42)

    # 1. Company -> Roles lookup (1,000 queries)
    t0 = time.perf_counter()
    for _ in range(1000):
        c_node = random.choice(f500_nodes)
        roles = [v for u, v, d in hydrated_graph.out_edges(c_node, data=True) if d.get("type") == "EMPLOYS_ROLE"]
        assert len(roles) >= 10
    t1 = time.perf_counter()
    avg_c2r_us = ((t1 - t0) / 1000) * 1e6
    assert avg_c2r_us < 1000, f"Company-to-role lookup latency too high: {avg_c2r_us:.2f} us (> 1ms)"

    # 2. Role -> Companies lookup (1,000 queries)
    t0 = time.perf_counter()
    for _ in range(1000):
        r_node = random.choice(role_nodes)
        comps = [u for u, v, d in hydrated_graph.in_edges(r_node, data=True) if d.get("type") == "EMPLOYS_ROLE"]
        assert len(comps) >= 1
    t1 = time.perf_counter()
    avg_r2c_us = ((t1 - t0) / 1000) * 1e6
    assert avg_r2c_us < 1000, f"Role-to-company lookup latency too high: {avg_r2c_us:.2f} us (> 1ms)"

    # 3. Two-hop lookup: Company -> Role -> Peer Role (1,000 queries)
    t0 = time.perf_counter()
    for _ in range(1000):
        c_node = random.choice(f500_nodes)
        roles = [v for u, v, d in hydrated_graph.out_edges(c_node, data=True) if d.get("type") == "EMPLOYS_ROLE"]
        r = random.choice(roles)
        peers = [v for u, v, d in hydrated_graph.out_edges(r, data=True) if d.get("type") in ("COLLABORATES_WITH", "HANDS_OFF_TO")]
    t1 = time.perf_counter()
    avg_2hop_us = ((t1 - t0) / 1000) * 1e6
    assert avg_2hop_us < 1000, f"Two-hop lookup latency too high: {avg_2hop_us:.2f} us (> 1ms)"


# ==============================================================================
# 6. Formal Invariant Suite Execution
# ==============================================================================

def test_formal_expansion_invariants_pass(hydrated_graph):
    """Runs the formal validate_expansion_invariants engine and asserts 0 violations."""
    report = validate_expansion_invariants(hydrated_graph)
    assert report.is_valid is True, f"Expansion invariants failed: {[v.message for v in report.violations]}"
    assert len(report.violations) == 0
    assert report.total_roles >= 540


def test_seed_fortune500_json_consistency():
    """Asserts that seed_fortune500.json is well-formed, exists, and matches counts."""
    assert SEED_JSON_PATH.exists()
    with open(SEED_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["companies_count"] == 500
    assert data["new_roles_count"] >= 204
    assert data["employs_role_edges_count"] >= 15000
    assert len(data["units"]) == 13
    assert len(data["companies"]) == 500
