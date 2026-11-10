"""Unit tests for NetworkX Knowledge Graph hydration, traversal, and structural invariant validation."""

import networkx as nx
import pytest

from orgprompt.graph.engine import KnowledgeGraphEngine
from orgprompt.graph.invariants import validate_knowledge_graph


def test_graph_hydration_node_types_and_counts(populated_graph: nx.MultiDiGraph):
    """Verifies all node types exist with correct counts."""
    type_counts = {}
    for _, data in populated_graph.nodes(data=True):
        ntype = data.get("type")
        type_counts[ntype] = type_counts.get(ntype, 0) + 1

    assert type_counts.get("Industry") == 16
    assert type_counts.get("ExemplarOrg") == 48
    assert type_counts.get("OrgUnit") == 120
    assert type_counts.get("CanonicalRole") == 336
    assert type_counts.get("Artifact", 0) >= 300
    assert type_counts.get("OperatingMechanism", 0) >= 48


def test_graph_hydration_edge_types(populated_graph: nx.MultiDiGraph):
    """Verifies all structural and workflow edge types are present in the graph."""
    edge_types = {data.get("type") for _, _, data in populated_graph.edges(data=True)}
    expected_types = {
        "PART_OF",
        "BELONGS_TO",
        "PRODUCES",
        "CONSUMES",
        "PRACTICES",
        "REPORTS_TO",
        "COLLABORATES_WITH",
        "HANDS_OFF_TO",
        "REVIEWS_AND_GATES",
        "CHALLENGES_OR_AUDITS",
    }
    for et in expected_types:
        assert et in edge_types, f"Edge type '{et}' missing from hydrated Knowledge Graph."


def test_all_336_roles_satisfy_invariants(populated_graph: nx.MultiDiGraph):
    """Verifies all 336 canonical roles strictly satisfy all 4 structural invariants."""
    report = KnowledgeGraphEngine.validate_invariants(populated_graph)
    assert report.is_valid is True, f"Invariant audit failed with violations: {report.violations}"
    assert report.total_roles == 336
    assert report.violation_count == 0


def test_invariant_violation_synthetic_isolated_role(populated_graph: nx.MultiDiGraph):
    """Verifies invariant auditor catches isolated roles (Invariant 1)."""
    G = populated_graph.copy()
    # Add an isolated role
    isolated_id = "role:isolated_test_role"
    G.add_node(isolated_id, type="CanonicalRole", label="Isolated Role")

    report = validate_knowledge_graph(G)
    assert report.is_valid is False
    inv1_violations = [v for v in report.violations if v.invariant_code == "INV-1-ISOLATION"]
    assert len(inv1_violations) == 1
    assert inv1_violations[0].role_id == isolated_id


def test_invariant_violation_synthetic_no_reports_to(populated_graph: nx.MultiDiGraph):
    """Verifies invariant auditor catches roles lacking hierarchy linkage (Invariant 2)."""
    G = populated_graph.copy()
    # Pick a non-executive role and remove all its REPORTS_TO edges
    test_role = "role:telecom_oran_integration_engineer"
    edges_to_remove = [
        (u, v, k)
        for u, v, k, d in G.edges(keys=True, data=True)
        if (u == test_role or v == test_role) and d.get("type") == "REPORTS_TO"
    ]
    for u, v, k in edges_to_remove:
        G.remove_edge(u, v, key=k)

    report = validate_knowledge_graph(G)
    assert report.is_valid is False
    inv2_violations = [
        v for v in report.violations if v.role_id == test_role and v.invariant_code == "INV-2-REPORTS-TO"
    ]
    assert len(inv2_violations) == 1


def test_invariant_violation_synthetic_insufficient_workflow(populated_graph: nx.MultiDiGraph):
    """Verifies invariant auditor catches roles with <2 workflow edges (Invariant 3)."""
    G = populated_graph.copy()
    test_role = "role:telecom_oran_integration_engineer"
    workflow_types = {"COLLABORATES_WITH", "HANDS_OFF_TO", "REVIEWS_AND_GATES", "CHALLENGES_OR_AUDITS"}
    # Remove all workflow edges for this role
    edges_to_remove = [
        (u, v, k)
        for u, v, k, d in G.edges(keys=True, data=True)
        if (u == test_role or v == test_role) and d.get("type") in workflow_types
    ]
    for u, v, k in edges_to_remove:
        G.remove_edge(u, v, key=k)

    report = validate_knowledge_graph(G)
    assert report.is_valid is False
    inv3_violations = [
        v for v in report.violations if v.role_id == test_role and v.invariant_code == "INV-3-WORKFLOW-EDGES"
    ]
    assert len(inv3_violations) == 1


def test_invariant_violation_synthetic_no_output_artifact(populated_graph: nx.MultiDiGraph):
    """Verifies invariant auditor catches roles without a PRODUCES artifact edge (Invariant 4)."""
    G = populated_graph.copy()
    test_role = "role:telecom_oran_integration_engineer"
    # Remove PRODUCES edges
    edges_to_remove = [
        (u, v, k)
        for u, v, k, d in G.out_edges(test_role, keys=True, data=True)
        if d.get("type") == "PRODUCES"
    ]
    for u, v, k in edges_to_remove:
        G.remove_edge(u, v, key=k)

    report = validate_knowledge_graph(G)
    assert report.is_valid is False
    inv4_violations = [
        v for v in report.violations if v.role_id == test_role and v.invariant_code == "INV-4-PRODUCES-ARTIFACT"
    ]
    assert len(inv4_violations) == 1


def test_expand_subgraph(populated_graph: nx.MultiDiGraph):
    """Verifies knowledge graph expansion across workflow edges."""
    anchor = "telecom_chief_network_architect"
    sub_1hop = KnowledgeGraphEngine.expand_subgraph(populated_graph, [anchor], hops=1)

    assert sub_1hop.number_of_nodes() > 1
    # Check anchor role is in subgraph
    assert f"role:{anchor}" in sub_1hop

    # Check connected workflow peers are in subgraph
    role_nodes = [n for n, d in sub_1hop.nodes(data=True) if d.get("type") == "CanonicalRole"]
    assert len(role_nodes) >= 3

    # Check 2-hop expansion includes more nodes
    sub_2hop = KnowledgeGraphEngine.expand_subgraph(populated_graph, [anchor], hops=2)
    assert sub_2hop.number_of_nodes() >= sub_1hop.number_of_nodes()


def test_invariant_violation_synthetic_endpoint_not_canonical_role(populated_graph: nx.MultiDiGraph):
    """Verifies invariant auditor enforces that REPORTS_TO and workflow edge endpoints must be CanonicalRole."""
    G = populated_graph.copy()
    test_role = "role:telecom_oran_integration_engineer"

    # 1. Test Invariant 2: Replace REPORTS_TO target with an OrgUnit
    edges_to_remove = [
        (u, v, k)
        for u, v, k, d in G.edges(keys=True, data=True)
        if (u == test_role or v == test_role) and d.get("type") == "REPORTS_TO"
    ]
    for u, v, k in edges_to_remove:
        G.remove_edge(u, v, key=k)

    # Add invalid REPORTS_TO pointing to an OrgUnit
    G.add_edge(test_role, "unit:bell_labs_rf_lab", key="REPORTS_TO_INVALID", type="REPORTS_TO")

    report = validate_knowledge_graph(G)
    assert report.is_valid is False
    inv2_violations = [
        v for v in report.violations if v.role_id == test_role and v.invariant_code == "INV-2-REPORTS-TO"
    ]
    assert len(inv2_violations) == 1, "Expected INV-2 violation when REPORTS_TO endpoint is OrgUnit"

    # Restore valid REPORTS_TO edge and test Invariant 3
    G.remove_edge(test_role, "unit:bell_labs_rf_lab", key="REPORTS_TO_INVALID")
    G.add_edge(test_role, "role:telecom_chief_network_architect", key="REPORTS_TO_RESTORED", type="REPORTS_TO")

    # Remove all workflow edges and add edges pointing to an Artifact instead of a CanonicalRole
    workflow_types = {"COLLABORATES_WITH", "HANDS_OFF_TO", "REVIEWS_AND_GATES", "CHALLENGES_OR_AUDITS"}
    wf_edges = [
        (u, v, k)
        for u, v, k, d in G.edges(keys=True, data=True)
        if (u == test_role or v == test_role) and d.get("type") in workflow_types
    ]
    for u, v, k in wf_edges:
        G.remove_edge(u, v, key=k)

    # Add 2 invalid workflow edges pointing to an Artifact node
    G.add_edge(test_role, "art:rf_spec", key="COLLAB_INVALID_1", type="COLLABORATES_WITH")
    G.add_edge(test_role, "art:oran_spec", key="COLLAB_INVALID_2", type="HANDS_OFF_TO")

    report2 = validate_knowledge_graph(G)
    assert report2.is_valid is False
    inv3_violations = [
        v for v in report2.violations if v.role_id == test_role and v.invariant_code == "INV-3-WORKFLOW-EDGES"
    ]
    assert len(inv3_violations) == 1, "Expected INV-3 violation when workflow endpoints are Artifacts"
