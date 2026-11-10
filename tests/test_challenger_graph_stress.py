"""Empirical Challenger 2 Stress-Testing Suite for Milestone Exp-M1A.

Audits and stress-tests:
1. Hydration Latency: Strictly < 5.0 seconds across repeated runs from SQLite.
2. Scale & Edge Distribution: >= 1,800 nodes, >= 30,000 edges, >= 15,000 EMPLOYS_ROLE edges.
3. Role Degree Distributions: Minimum, maximum, and average in-degrees across all canonical roles.
4. Subgraph Expansion Performance & Convergence: 1-hop to 10-hop traversals across roles and companies.
5. Adversarial Input Robustness: Non-existent IDs, bare slugs, malformed inputs, company nodes.
6. Dynamic Role Invariant Boundary: Proves RoleGenerator boundary vs validate_expansion_invariants.
"""

import random
import statistics
import time
import pytest
import networkx as nx

from orgprompt.db.connection import get_default_db_path
from orgprompt.graph.engine import KnowledgeGraphEngine
from orgprompt.graph.invariants import (
    WORKFLOW_EDGE_TYPES,
    validate_expansion_invariants,
    validate_knowledge_graph,
)
from orgprompt.models import RoleGenSpec
from orgprompt.graph.generator import RoleGenerator


@pytest.fixture(scope="module")
def persistent_graph():
    """Builds the full heterogeneous knowledge graph once from the persistent SQLite database."""
    db_path = get_default_db_path()
    return KnowledgeGraphEngine.build_from_db(db_path)


def test_hydration_latency_under_5s():
    """Empirically tests that graph hydration completes strictly under 5.0 seconds over 5 runs."""
    db_path = get_default_db_path()
    latencies = []
    for _ in range(5):
        t0 = time.perf_counter()
        g = KnowledgeGraphEngine.build_from_db(db_path)
        elapsed = time.perf_counter() - t0
        latencies.append(elapsed)
        assert g.number_of_nodes() >= 1800
        assert g.number_of_edges() >= 30000

    max_lat = max(latencies)
    mean_lat = statistics.mean(latencies)
    assert max_lat < 5.0, f"Max hydration latency {max_lat:.3f}s exceeded 5.0s threshold"
    assert mean_lat < 2.0, f"Mean hydration latency {mean_lat:.3f}s is abnormally high"


def test_graph_scale_and_edge_types(persistent_graph: nx.MultiDiGraph):
    """Verifies graph node scale, company count, role count, and edge distributions."""
    g = persistent_graph

    # Node checks
    roles = [n for n, d in g.nodes(data=True) if d.get("type") == "CanonicalRole"]
    f500_cos = [n for n, d in g.nodes(data=True) if d.get("type") == "Fortune500Company"]
    units = [n for n, d in g.nodes(data=True) if d.get("type") == "OrgUnit"]
    industries = [n for n, d in g.nodes(data=True) if d.get("type") == "Industry"]

    assert len(roles) >= 540, f"Expected >= 540 roles, got {len(roles)}"
    assert len(f500_cos) >= 500, f"Expected >= 500 F500 companies, got {len(f500_cos)}"
    core_f500_cos = [n for n in f500_cos if g.nodes[n].get("rank", 999) <= 500]
    assert len(core_f500_cos) == 500, f"Expected exactly 500 core F500 companies (rank <= 500), got {len(core_f500_cos)}"
    assert len(units) >= 130, f"Expected >= 130 org units, got {len(units)}"
    assert len(industries) == 16, f"Expected 16 industries, got {len(industries)}"

    # Edge checks
    employs_edges = [e for e in g.edges(data=True) if e[2].get("type") == "EMPLOYS_ROLE"]
    workflow_edges = [
        e for e in g.edges(data=True) if e[2].get("type") in WORKFLOW_EDGE_TYPES
    ]
    reports_edges = [e for e in g.edges(data=True) if e[2].get("type") == "REPORTS_TO"]
    produces_edges = [e for e in g.edges(data=True) if e[2].get("type") == "PRODUCES"]

    assert len(employs_edges) >= 15000, f"Expected >= 15,000 EMPLOYS_ROLE edges, got {len(employs_edges)}"
    assert len(workflow_edges) >= 1600, f"Expected >= 1,600 workflow edges, got {len(workflow_edges)}"
    assert len(reports_edges) >= 500, f"Expected >= 500 REPORTS_TO edges, got {len(reports_edges)}"
    assert len(produces_edges) >= 540, f"Expected >= 540 PRODUCES edges, got {len(produces_edges)}"


def test_role_degree_distribution_metrics(persistent_graph: nx.MultiDiGraph):
    """Empirically validates degree distributions across all canonical roles."""
    g = persistent_graph
    role_nodes = [n for n, d in g.nodes(data=True) if d.get("type") == "CanonicalRole"]

    in_degrees = []
    employs_in_degrees = []
    workflow_in_degrees = []

    for r in role_nodes:
        in_e = list(g.in_edges(r, data=True))
        in_degrees.append(len(in_e))

        emp_in = sum(1 for e in in_e if e[2].get("type") == "EMPLOYS_ROLE")
        wf_in = sum(1 for e in in_e if e[2].get("type") in WORKFLOW_EDGE_TYPES)
        employs_in_degrees.append(emp_in)
        workflow_in_degrees.append(wf_in)

    # 1. Zero-orphan verification: all roles must have in-degree > 0 (bespoke single-company roles >= 1, core F500 roles >= 6)
    min_in = min(in_degrees)
    assert min_in >= 1, f"Expected minimum in-degree >= 1, found {min_in}"
    core_in_degrees = [
        len(list(g.in_edges(r, data=True)))
        for r in role_nodes
        if any(
            g.nodes[u].get("rank", 999) <= 500
            for u, _, d in g.in_edges(r, data=True)
            if d.get("type") == "EMPLOYS_ROLE"
        )
    ]
    assert min(core_in_degrees) >= 6, f"Expected minimum core F500 role in-degree >= 6, found {min(core_in_degrees)}"

    # 2. Maximum in-degree: C-suite / corporate leadership roles should have in-degree >= 500
    max_in = max(in_degrees)
    assert max_in >= 500, f"Expected maximum in-degree >= 500, found {max_in}"

    # 3. Average in-degree: total ~26.9k employs + ~1.6k workflow + ~500 reports / ~547 roles ~= 53
    avg_in = statistics.mean(in_degrees)
    assert 40.0 <= avg_in <= 70.0, f"Expected average in-degree between 40 and 70, got {avg_in:.2f}"

    # 4. Out-degree invariants
    out_degrees = [len(list(g.out_edges(r))) for r in role_nodes]
    assert min(out_degrees) >= 5, "Every role must have at least 5 outgoing edges"
    assert max(out_degrees) <= 15, "Outgoing edges must be bounded (<= 15) to prevent fanout bloat"


def test_canonical_role_subgraph_expansion_performance(persistent_graph: nx.MultiDiGraph):
    """Stress-tests multi-hop subgraph expansion across random canonical roles."""
    g = persistent_graph
    role_nodes = [n for n, d in g.nodes(data=True) if d.get("type") == "CanonicalRole"]

    random.seed(999)
    sampled = random.sample(role_nodes, 10)

    for r in sampled:
        # Hop 1
        t0 = time.perf_counter()
        sub1 = KnowledgeGraphEngine.expand_subgraph(g, [r], hops=1)
        dur1 = (time.perf_counter() - t0) * 1000
        assert sub1.number_of_nodes() >= 3
        assert dur1 < 50.0, f"1-hop expansion took too long: {dur1:.2f}ms"

        # Hop 2
        t0 = time.perf_counter()
        sub2 = KnowledgeGraphEngine.expand_subgraph(g, [r], hops=2)
        dur2 = (time.perf_counter() - t0) * 1000
        assert sub2.number_of_nodes() >= sub1.number_of_nodes()
        assert dur2 < 150.0, f"2-hop expansion took too long: {dur2:.2f}ms"


def test_deep_subgraph_expansion_convergence(persistent_graph: nx.MultiDiGraph):
    """Verifies that deep hops (up to 10) on a high-degree anchor role converge cleanly."""
    g = persistent_graph
    anchor = "role:exec_chief_executive_officer"

    t0 = time.perf_counter()
    sub_10 = KnowledgeGraphEngine.expand_subgraph(g, [anchor], hops=10)
    dur = (time.perf_counter() - t0) * 1000

    assert dur < 250.0, f"10-hop expansion exceeded 250ms: {dur:.2f}ms"
    assert sub_10.number_of_nodes() >= 200
    assert nx.is_directed_acyclic_graph(sub_10) is False  # Contains mutual collaboration cycles


def test_adversarial_subgraph_expansion_edge_cases(persistent_graph: nx.MultiDiGraph):
    """Tests edge cases: non-existent roles, empty inputs, prefix variations, company nodes."""
    g = persistent_graph

    # Non-existent role
    sub_none = KnowledgeGraphEngine.expand_subgraph(g, ["role:fictional_non_existent_role"])
    assert sub_none.number_of_nodes() == 0

    # Empty list
    sub_empty = KnowledgeGraphEngine.expand_subgraph(g, [])
    assert sub_empty.number_of_nodes() == 0

    # Prefix normalization tolerance: "role_exec_chief_executive_officer", "exec_chief_executive_officer", "role:exec_chief_executive_officer"
    sub_a = KnowledgeGraphEngine.expand_subgraph(g, ["role:exec_chief_executive_officer"], hops=1)
    sub_b = KnowledgeGraphEngine.expand_subgraph(g, ["role_exec_chief_executive_officer"], hops=1)
    sub_c = KnowledgeGraphEngine.expand_subgraph(g, ["exec_chief_executive_officer"], hops=1)

    assert set(sub_a.nodes()) == set(sub_b.nodes()) == set(sub_c.nodes())

    # Company node passed to expand_subgraph:
    # expand_subgraph is designed for workflow roles; passing a company node must not crash,
    # and returns an induced subgraph containing the company node without error.
    sub_co = KnowledgeGraphEngine.expand_subgraph(g, ["f500:walmart"], hops=1)
    assert "f500:walmart" in sub_co
    assert sub_co.number_of_nodes() == 1


def test_company_role_multihop_traversal_speed(persistent_graph: nx.MultiDiGraph):
    """Verifies that direct company-to-role and role-to-company queries execute in < 5ms."""
    g = persistent_graph
    f500_nodes = [n for n, d in g.nodes(data=True) if d.get("type") == "Fortune500Company"]
    role_nodes = [n for n, d in g.nodes(data=True) if d.get("type") == "CanonicalRole"]

    random.seed(777)
    for c in random.sample(f500_nodes, 10):
        t0 = time.perf_counter()
        employed = [v for _, v, d in g.out_edges(c, data=True) if d.get("type") == "EMPLOYS_ROLE"]
        dur = (time.perf_counter() - t0) * 1000
        assert len(employed) >= 15
        assert dur < 5.0, f"Company traversal took {dur:.2f}ms (> 5.0ms)"

    for r in random.sample(role_nodes, 10):
        t0 = time.perf_counter()
        employers = [u for u, _, d in g.in_edges(r, data=True) if d.get("type") == "EMPLOYS_ROLE"]
        dur = (time.perf_counter() - t0) * 1000
        assert len(employers) >= 1
        assert dur < 5.0, f"Role traversal took {dur:.2f}ms (> 5.0ms)"


def test_validate_expansion_invariants_passes_on_current_db(persistent_graph: nx.MultiDiGraph):
    """Verifies that the current hydrated knowledge graph satisfies 100% of expansion invariants."""
    report = validate_expansion_invariants(persistent_graph)
    assert report.is_valid is True, f"Expansion invariants failed: {[v.message for v in report.violations]}"
    assert len(report.violations) == 0


def test_generator_orphan_boundary_adversarial_proof(persistent_graph: nx.MultiDiGraph):
    """Empirical proof of generator boundary:

    RoleGenerator generates a role that satisfies base invariants (INV-1..4)
    but lacks EMPLOYS_ROLE edges until remediated by seed_expanded_database.
    """
    import sqlite3
    from orgprompt.db.seed_data import seed_database

    mem_conn = seed_database(":memory:")
    # Build base graph from in-memory DB
    g = KnowledgeGraphEngine.build_from_db(conn=mem_conn)

    spec = RoleGenSpec(
        name="Adversarial Audit Target Specialist",
        org_unit_slug="telecom_bell_labs_physical_research",
        seniority_level="SENIOR_SPECIALIST",
        role_archetype="domain_specialist",
        mission="Audit boundaries and invariants under adversarial challenge.",
        output_artifact_name="Adversarial Audit Finding Log",
    )

    new_role = RoleGenerator.generate_role(spec, conn=mem_conn, G=g)
    assert new_role.id is not None

    # Base invariants pass
    base_report = validate_knowledge_graph(g)
    assert base_report.is_valid is True, "Base invariants must pass for newly generated role"

    # Expansion invariants fail because 0 companies employ this new role
    exp_report = validate_expansion_invariants(g)
    assert exp_report.is_valid is False
    assert any(v.invariant_code == "INV-ORPHAN-ROLE" for v in exp_report.violations)
