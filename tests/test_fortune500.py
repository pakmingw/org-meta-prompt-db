"""Tests for Fortune 500 Enterprise Catalog & Role Graph Expansion (Exp-M1A)."""

import json
import sqlite3
from pathlib import Path
import pytest
import networkx as nx

from orgprompt.db.connection import get_default_db_path
from orgprompt.db.seed_data import seed_database
from orgprompt.db.seed_fortune500 import seed_expanded_database, SEED_JSON_PATH
from orgprompt.graph.engine import KnowledgeGraphEngine
from orgprompt.graph.invariants import validate_expansion_invariants, validate_knowledge_graph


@pytest.fixture(scope="module")
def expansion_db_conn():
    """Provides a SQLite connection to the expanded Fortune 500 database."""
    from orgprompt.db.connection import get_connection
    db_path = get_default_db_path()
    seed_expanded_database(db_path=db_path)
    conn = get_connection(db_path)
    yield conn
    conn.close()


@pytest.fixture(scope="module")
def expansion_graph(expansion_db_conn):
    """Provides a hydrated NetworkX Knowledge Graph from the expanded in-memory database."""
    return KnowledgeGraphEngine.build_from_db(conn=expansion_db_conn)


def test_fortune500_companies_count_and_ranks(expansion_db_conn, expansion_graph):
    """Verifies exactly 500 companies with contiguous ranks 1..500 in SQLite and NetworkX."""
    cursor = expansion_db_conn.cursor()
    companies = cursor.execute(
        "SELECT rank, name, slug, revenue_billions FROM fortune500_companies ORDER BY rank ASC"
    ).fetchall()

    assert len(companies) == 500, f"Expected 500 companies in SQLite, got {len(companies)}"
    ranks = [c[0] for c in companies]
    assert ranks == list(range(1, 501)), "Ranks must be strictly contiguous from 1 to 500 without gaps"

    # NetworkX verification
    f500_nodes = [n for n, d in expansion_graph.nodes(data=True) if d.get("type") == "Fortune500Company"]
    assert len(f500_nodes) == 500, f"Expected 500 Fortune500Company nodes in graph, got {len(f500_nodes)}"
    graph_ranks = sorted([expansion_graph.nodes[n].get("rank") for n in f500_nodes])
    assert graph_ranks == list(range(1, 501)), "Graph node ranks must be strictly contiguous 1..500"


def test_fortune500_revenue_sanity(expansion_db_conn):
    """Verifies revenue bookends and monotonicity."""
    cursor = expansion_db_conn.cursor()
    c1 = cursor.execute("SELECT name, revenue_billions FROM fortune500_companies WHERE rank = 1").fetchone()
    c500 = cursor.execute("SELECT name, revenue_billions FROM fortune500_companies WHERE rank = 500").fetchone()

    assert c1[0] == "Walmart"
    assert c1[1] == 648.1
    assert c500[0] == "O-I Glass"
    assert c500[1] == 7.1

    all_revs = [r[0] for r in cursor.execute("SELECT revenue_billions FROM fortune500_companies ORDER BY rank ASC").fetchall()]
    assert all(rev > 0 for rev in all_revs), "All revenues must be positive"
    for i in range(len(all_revs) - 1):
        assert all_revs[i] >= all_revs[i + 1], f"Revenue out of order at rank {i+1}: {all_revs[i]} < {all_revs[i+1]}"


def test_fortune500_industry_distribution(expansion_db_conn):
    """Verifies that all 16 macro industries are represented with >= 6 companies each."""
    cursor = expansion_db_conn.cursor()
    ind_counts = cursor.execute(
        "SELECT industry_id, count(*) FROM fortune500_companies GROUP BY industry_id"
    ).fetchall()
    ind_map = dict(ind_counts)

    assert len(ind_map) == 16, f"Expected 16 macro industries, got {len(ind_map)}"
    for ind_id, count in ind_map.items():
        assert count >= 6, f"Industry {ind_id} has {count} companies (< 6)"


def test_fortune500_archetypes_and_models(expansion_db_conn):
    """Verifies valid operating archetypes (5) and business models (8)."""
    valid_models = {
        'HIGH_VELOCITY_DISTRIBUTOR', 'MULTI_SIDED_PLATFORM', 'RECURRING_SUBSCRIPTION_SAAS',
        'ASSET_HEAVY_MANUFACTURER', 'FINANCIAL_RISK_INTERMEDIARY', 'INTEGRATED_ENERGY_OPERATOR',
        'CLINICAL_LIFE_SCIENCES_INNOVATOR', 'PROFESSIONAL_KNOWLEDGE_ADVISORY'
    }
    valid_archetypes = {
        'UNIFICATION', 'COORDINATION', 'REPLICATION', 'DIVERSIFICATION', 'PLATFORM_ECOSYSTEM'
    }
    cursor = expansion_db_conn.cursor()
    rows = cursor.execute("SELECT business_model, operating_archetype FROM fortune500_companies").fetchall()
    for model, arch in rows:
        assert model in valid_models, f"Invalid business model: {model}"
        assert arch in valid_archetypes, f"Invalid operating archetype: {arch}"


def test_expansion_units_count(expansion_db_conn):
    """Verifies 13 dedicated functional operating units and referential integrity."""
    cursor = expansion_db_conn.cursor()
    units = cursor.execute("SELECT id, exemplar_org_id, name FROM org_units WHERE id LIKE 'unit_f500_%'").fetchall()
    assert len(units) == 13, f"Expected 13 dedicated units, got {len(units)}"

    # Check exemplar existence
    for _, exemplar_id, _ in units:
        org = cursor.execute("SELECT id FROM exemplar_orgs WHERE id = ?", (exemplar_id,)).fetchone()
        assert org is not None, f"Exemplar {exemplar_id} not found in exemplar_orgs"


def test_canonical_roles_expansion_count(expansion_db_conn):
    """Verifies >= 540 canonical roles (547 total) with authentic 6-section prompts (>= 1,200 chars)."""
    cursor = expansion_db_conn.cursor()
    total_roles = cursor.execute("SELECT count(*) FROM canonical_roles").fetchone()[0]
    assert total_roles >= 540, f"Expected >= 540 canonical roles, got {total_roles}"

    # Verify expansion roles prompt quality
    expansion_roles = cursor.execute(
        "SELECT slug, character_count, system_prompt FROM canonical_roles WHERE org_unit_id LIKE 'unit_f500_%'"
    ).fetchall()
    assert len(expansion_roles) >= 204, f"Expected >= 204 expansion roles, got {len(expansion_roles)}"

    required_sections = [
        "## 1. Role Identity & Exemplar Lineage",
        "## 2. First-Principles Mental Models & Domain Heuristics",
        "## 3. Technical Vocabulary & Standards",
        "## 4. Anti-Patterns & Mediocrity Filters",
        "## 5. Collaboration, Handoff & Escalation Protocols",
        "## 6. Concrete Output Artifact Schemas"
    ]
    for slug, char_count, prompt in expansion_roles:
        assert char_count >= 1200, f"Role {slug} character count is {char_count} (< 1,200)"
        assert len(prompt) >= 1200, f"Role {slug} prompt length is {len(prompt)} (< 1,200)"
        for section in required_sections:
            assert section in prompt, f"Role {slug} missing section '{section}'"


def test_employs_role_edge_count(expansion_db_conn, expansion_graph):
    """Verifies >= 15,000 employs_role edges in SQLite and NetworkX."""
    cursor = expansion_db_conn.cursor()
    edge_count = cursor.execute("SELECT count(*) FROM employs_role").fetchone()[0]
    assert edge_count >= 15000, f"Expected >= 15,000 employs_role edges in SQLite, got {edge_count}"

    graph_employs = [
        (u, v, d) for u, v, d in expansion_graph.edges(data=True) if d.get("type") == "EMPLOYS_ROLE"
    ]
    assert len(graph_employs) >= 15000, f"Expected >= 15,000 EMPLOYS_ROLE edges in graph, got {len(graph_employs)}"


def test_zero_orphan_roles(expansion_db_conn, expansion_graph):
    """Verifies that every canonical role has degree > 0 and >= 1 employing Fortune 500 company."""
    cursor = expansion_db_conn.cursor()
    all_role_ids = set(r[0] for r in cursor.execute("SELECT id FROM canonical_roles").fetchall())
    employed_role_ids = set(r[0] for r in cursor.execute("SELECT DISTINCT role_id FROM employs_role").fetchall())

    orphans_sql = all_role_ids - employed_role_ids
    assert len(orphans_sql) == 0, f"Found {len(orphans_sql)} orphan roles in SQLite: {list(orphans_sql)[:5]}"

    # Graph check
    role_nodes = [n for n, d in expansion_graph.nodes(data=True) if d.get("type") == "CanonicalRole"]
    orphans_graph = []
    for r_node in role_nodes:
        in_employs = [
            e for e in expansion_graph.in_edges(r_node, data=True) if e[2].get("type") == "EMPLOYS_ROLE"
        ]
        if len(in_employs) == 0:
            orphans_graph.append(r_node)

    assert len(orphans_graph) == 0, f"Found {len(orphans_graph)} orphan roles in graph: {orphans_graph[:5]}"


def test_validate_expansion_invariants(expansion_graph):
    """Runs the formal validate_expansion_invariants suite and asserts 0 violations."""
    report = validate_expansion_invariants(expansion_graph)
    assert report.is_valid is True, f"Invariant validation failed: {[v.message for v in report.violations]}"
    assert len(report.violations) == 0, f"Found {len(report.violations)} invariant violations"
    assert report.total_roles >= 540


def test_company_role_graph_traversal(expansion_graph):
    """Verifies NetworkX multi-hop neighborhood queries between Fortune 500 companies and roles."""
    walmart_node = "f500:walmart"
    assert walmart_node in expansion_graph.nodes, "f500:walmart node missing from graph"

    # Outgoing edges from company to employed roles
    out_edges = expansion_graph.out_edges(walmart_node, data=True)
    employed_roles = [v for u, v, d in out_edges if d.get("type") == "EMPLOYS_ROLE"]
    assert len(employed_roles) >= 18, f"Walmart employs {len(employed_roles)} roles (< 18)"

    # Predecessors of CEO role
    ceo_node = "role:exec_chief_executive_officer"
    assert ceo_node in expansion_graph.nodes, "CEO role node missing from graph"
    employing_companies = [
        u for u, v, d in expansion_graph.in_edges(ceo_node, data=True) if d.get("type") == "EMPLOYS_ROLE"
    ]
    assert len(employing_companies) == 500, f"Expected 500 companies employing CEO, got {len(employing_companies)}"


def test_seed_fortune500_json_validity():
    """Verifies that seed_fortune500.json was generated, is valid, and matches counts."""
    assert SEED_JSON_PATH.exists(), f"seed_fortune500.json not found at {SEED_JSON_PATH}"
    with open(SEED_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert len(data["units"]) == 13
    assert data["new_roles_count"] >= 204
    assert data["companies_count"] == 500
    assert data["employs_role_edges_count"] >= 15000
    assert len(data["companies"]) == 500
    assert data["companies"][0]["name"] == "Walmart"
    assert data["companies"][-1]["name"] == "O-I Glass"
