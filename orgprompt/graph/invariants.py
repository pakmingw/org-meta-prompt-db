"""Structural Invariant Validation for the Organizational Knowledge Graph."""

from typing import List, Set
import networkx as nx

from orgprompt.models import InvariantViolation, ValidationReport

WORKFLOW_EDGE_TYPES: Set[str] = {
    "COLLABORATES_WITH",
    "HANDS_OFF_TO",
    "REVIEWS_AND_GATES",
    "CHALLENGES_OR_AUDITS",
}


def validate_knowledge_graph(g: nx.DiGraph) -> ValidationReport:
    """Validates that all CanonicalRole nodes satisfy all 4 structural invariants.

    Invariants:
    1. Zero Isolated Roles (degree > 0)
    2. Hierarchy Linkage (>= 1 REPORTS_TO edge, either in or out)
    3. Workflow Connectivity (>= 2 workflow/collaboration edges)
    4. Concrete Artifact Linkage (>= 1 PRODUCES edge to an Artifact)
    """
    violations: List[InvariantViolation] = []
    role_nodes = [n for n, d in g.nodes(data=True) if d.get("type") == "CanonicalRole"]

    for role_id in role_nodes:
        attrs = g.nodes[role_id]
        role_name = attrs.get("label", role_id)

        in_edges = list(g.in_edges(role_id, data=True))
        out_edges = list(g.out_edges(role_id, data=True))
        all_edges = in_edges + out_edges

        # Invariant 1: Zero Isolated Roles
        if len(all_edges) == 0:
            violations.append(
                InvariantViolation(
                    role_id=role_id,
                    role_name=role_name,
                    invariant_code="INV-1-ISOLATION",
                    message=f"Role '{role_name}' is completely isolated (degree=0).",
                )
            )
            continue

        # Invariant 2: Hierarchy Linkage (>= 1 REPORTS_TO edge, in or out to a CanonicalRole)
        reports_edges = [
            e
            for e in all_edges
            if (
                e[2].get("type") == "REPORTS_TO"
                or "REPORTS_TO" in e[2].get("edge_types", set())
            )
            and g.nodes[e[0] if e[1] == role_id else e[1]].get("type") == "CanonicalRole"
        ]
        if len(reports_edges) < 1:
            violations.append(
                InvariantViolation(
                    role_id=role_id,
                    role_name=role_name,
                    invariant_code="INV-2-REPORTS-TO",
                    message=f"Role '{role_name}' lacks hierarchy linkage (0 REPORTS_TO edges).",
                )
            )

        # Invariant 3: Workflow Connectivity (>= 2 workflow edges to CanonicalRoles)
        workflow_edges = [
            e
            for e in all_edges
            if (
                (e[2].get("type") in WORKFLOW_EDGE_TYPES)
                or any(t in WORKFLOW_EDGE_TYPES for t in e[2].get("edge_types", set()))
            )
            and g.nodes[e[0] if e[1] == role_id else e[1]].get("type") == "CanonicalRole"
        ]
        if len(workflow_edges) < 2:
            violations.append(
                InvariantViolation(
                    role_id=role_id,
                    role_name=role_name,
                    invariant_code="INV-3-WORKFLOW-EDGES",
                    message=f"Role '{role_name}' has only {len(workflow_edges)} workflow edges (minimum 2 required).",
                )
            )

        # Invariant 4: Concrete Artifact Linkage (>= 1 PRODUCES edge to an Artifact)
        produces_edges = [
            e
            for e in out_edges
            if (e[2].get("type") == "PRODUCES" or "PRODUCES" in e[2].get("edge_types", set()))
            and (g.nodes[e[1]].get("type") == "Artifact")
        ]
        if len(produces_edges) < 1:
            violations.append(
                InvariantViolation(
                    role_id=role_id,
                    role_name=role_name,
                    invariant_code="INV-4-PRODUCES-ARTIFACT",
                    message=f"Role '{role_name}' does not produce any concrete output artifact (0 PRODUCES edges).",
                )
            )

    return ValidationReport(
        is_valid=(len(violations) == 0),
        total_roles=len(role_nodes),
        violations=violations,
    )


def validate_expansion_invariants(g: nx.MultiDiGraph) -> ValidationReport:
    """Validates Fortune 500 enterprise catalog and employment graph invariants.

    Invariants:
    1. >= 500 Fortune500Company nodes (INV-F500-COUNT).
    2. Ranks 1-500 contiguous with no duplicates or missing ranks (INV-F500-RANKS).
    3. >= 500 CanonicalRole nodes (INV-ROLES-COUNT).
    4. >= 15,000 EMPLOYS_ROLE edges (INV-EMPLOYS-EDGES-COUNT).
    5. Zero Orphan Roles: Every CanonicalRole has >= 1 incoming EMPLOYS_ROLE edge (INV-ORPHAN-ROLE).
    6. All standard role invariants 1-4 pass for every CanonicalRole (INV-1 through INV-4).
    """
    violations: List[InvariantViolation] = []

    # 1. Company count
    f500_nodes = [n for n, d in g.nodes(data=True) if d.get("type") == "Fortune500Company"]
    if len(f500_nodes) < 500:
        violations.append(
            InvariantViolation(
                role_id="SYSTEM",
                role_name="Fortune 500 Catalog",
                invariant_code="INV-F500-COUNT",
                message=f"Fortune 500 company count is {len(f500_nodes)}, expected >= 500.",
            )
        )

    # 2. Contiguous ranks 1..500
    ranks = set()
    for n in f500_nodes:
        rank = g.nodes[n].get("rank")
        if rank is not None:
            ranks.add(rank)
    expected_ranks = set(range(1, 501))
    missing_ranks = expected_ranks - ranks
    if missing_ranks:
        violations.append(
            InvariantViolation(
                role_id="SYSTEM",
                role_name="Fortune 500 Ranks",
                invariant_code="INV-F500-RANKS",
                message=f"Missing Fortune 500 ranks: {sorted(list(missing_ranks))[:10]} (total missing: {len(missing_ranks)}).",
            )
        )

    # 3. Canonical roles count
    role_nodes = [n for n, d in g.nodes(data=True) if d.get("type") == "CanonicalRole"]
    if len(role_nodes) < 500:
        violations.append(
            InvariantViolation(
                role_id="SYSTEM",
                role_name="Role Taxonomy",
                invariant_code="INV-ROLES-COUNT",
                message=f"Canonical role count is {len(role_nodes)}, expected >= 500.",
            )
        )

    # 4. Employment edges count
    employs_edges = [
        (u, v, d) for u, v, d in g.edges(data=True) if d.get("type") == "EMPLOYS_ROLE"
    ]
    if len(employs_edges) < 15000:
        violations.append(
            InvariantViolation(
                role_id="SYSTEM",
                role_name="Employment Graph",
                invariant_code="INV-EMPLOYS-EDGES-COUNT",
                message=f"EMPLOYS_ROLE edge count is {len(employs_edges)}, expected >= 15,000.",
            )
        )

    # 5. Zero Orphan Roles: every CanonicalRole must have at least one incoming EMPLOYS_ROLE edge
    for r_node in role_nodes:
        in_employs = [
            e for e in g.in_edges(r_node, data=True) if e[2].get("type") == "EMPLOYS_ROLE"
        ]
        if len(in_employs) == 0:
            attrs = g.nodes[r_node]
            violations.append(
                InvariantViolation(
                    role_id=r_node,
                    role_name=attrs.get("label", r_node),
                    invariant_code="INV-ORPHAN-ROLE",
                    message=f"Role '{attrs.get('label', r_node)}' has 0 employing Fortune 500 companies (orphan role).",
                )
            )

    # 6. Standard 4-point role invariant validation (INV-1 to INV-4)
    base_report = validate_knowledge_graph(g)
    violations.extend(base_report.violations)

    return ValidationReport(
        is_valid=(len(violations) == 0),
        total_roles=len(role_nodes),
        violations=violations,
    )
