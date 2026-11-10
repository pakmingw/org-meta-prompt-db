"""Knowledge Graph Traversal Expansion for Cross-Functional Team Assembly.

Given top-k anchor roles discovered by Reciprocal Rank Fusion, traverses behavioral
and workflow edges (COLLABORATES_WITH, HANDS_OFF_TO, REVIEWS_AND_GATES, CHALLENGES_OR_AUDITS,
REPORTS_TO) across the NetworkX Knowledge Graph to assemble a cohesive, functionally
balanced multi-agent team subgraph.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple
import networkx as nx

from orgprompt.models import CanonicalRole


EDGE_PRIORITY: Dict[str, float] = {
    "CHALLENGES_OR_AUDITS": 1.00,  # Critical for adversarial review & red-teaming
    "REVIEWS_AND_GATES": 0.90,     # Critical for quality gating & sign-offs
    "HANDS_OFF_TO": 0.85,         # Critical for workflow continuity & artifact pipelines
    "COLLABORATES_WITH": 0.80,    # Peer cross-functional collaboration
    "REPORTS_TO": 0.70,           # Executive sponsorship & organizational hierarchy
}

TARGET_ARCHETYPES = {
    "executive_strategy": 1,
    "engineering_staff": 2,
    "domain_specialist": 2,
    "operations": 1,
    "risk_compliance": 2,
}


def _normalize_node_id(graph: nx.Graph, role_identifier: str) -> Optional[str]:
    """Resolves a role slug, role ID, or graph key into the canonical graph node ID."""
    if graph.has_node(role_identifier):
        return role_identifier

    # Try standard prefixes
    candidates = [
        f"role:{role_identifier.replace('role_', '').replace('role:', '')}",
        f"role_{role_identifier.replace('role:', '').replace('role_', '')}",
        role_identifier.replace("role:", "").replace("role_", ""),
    ]
    for c in candidates:
        if graph.has_node(c):
            return c

    # Search by slug attribute
    clean_slug = role_identifier.replace("role:", "").replace("role_", "")
    for n, d in graph.nodes(data=True):
        if d.get("type") == "CanonicalRole":
            if d.get("slug") == clean_slug or n.endswith(f":{clean_slug}"):
                return n

    return None


def expand_team_subgraph(
    graph: nx.Graph,
    anchor_role_ids: List[str],
    min_roles: int = 8,
    max_roles: int = 12,
    roles_by_id: Optional[Dict[str, CanonicalRole]] = None,
) -> Dict[str, Any]:
    """Expands anchor roles across behavioral edges to assemble a cross-functional team.

    Args:
        graph: NetworkX Knowledge Graph (DiGraph or MultiDiGraph).
        anchor_role_ids: List of seed anchor role identifiers.
        min_roles: Minimum number of roles in the expanded team.
        max_roles: Maximum number of roles in the expanded team.
        roles_by_id: Optional dictionary of hydrated CanonicalRole models.

    Returns:
        Dict containing:
            - 'team_role_ids': Graph node IDs of assembled team roles.
            - 'team_slugs': Clean URL-safe slugs of assembled roles.
            - 'team_size': Number of roles in the assembled team.
            - 'subgraph': Induced NetworkX subgraph connecting the team.
            - 'edges': List of interconnecting edges with metadata.
            - 'archetypes': Mapping of archetype category to role IDs.
            - 'roles': List of CanonicalRole instances (if roles_by_id provided).
    """
    if not graph or graph.number_of_nodes() == 0:
        return {
            "team_role_ids": list(anchor_role_ids),
            "team_slugs": [r.replace("role:", "").replace("role_", "") for r in anchor_role_ids],
            "team_size": len(anchor_role_ids),
            "subgraph": nx.DiGraph(),
            "edges": [],
            "archetypes": {},
            "roles": [],
        }

    # Resolve and validate anchor nodes
    resolved_anchors: List[str] = []
    for anchor in anchor_role_ids:
        node_id = _normalize_node_id(graph, anchor)
        if node_id and node_id not in resolved_anchors:
            resolved_anchors.append(node_id)

    team_nodes: Set[str] = set(resolved_anchors)
    candidate_scores: Dict[str, float] = {}

    # Multi-hop neighborhood search: traverse both outgoing and incoming edges
    for anchor in resolved_anchors:
        # Outgoing edges (anchor hands off to, reports to, collaborates with, audits)
        for _, target, data in graph.out_edges(anchor, data=True):
            target_data = graph.nodes[target]
            if target_data.get("type") == "CanonicalRole" and target not in team_nodes:
                edge_t = data.get("type", "")
                weight = EDGE_PRIORITY.get(edge_t, 0.5)
                candidate_scores[target] = candidate_scores.get(target, 0.0) + weight

        # Incoming edges (auditors auditing the anchor, supervisors overseeing the anchor)
        for source, _, data in graph.in_edges(anchor, data=True):
            source_data = graph.nodes[source]
            if source_data.get("type") == "CanonicalRole" and source not in team_nodes:
                edge_t = data.get("type", "")
                weight = EDGE_PRIORITY.get(edge_t, 0.5)
                candidate_scores[source] = candidate_scores.get(source, 0.0) + weight

    # If first hop doesn't provide enough candidates, expand second hop from top candidates
    if len(team_nodes) + len(candidate_scores) < min_roles:
        first_hop_top = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        for node, base_w in first_hop_top:
            for _, target, data in graph.out_edges(node, data=True):
                if graph.nodes[target].get("type") == "CanonicalRole" and target not in team_nodes:
                    w = EDGE_PRIORITY.get(data.get("type", ""), 0.5) * 0.7  # Hop attenuation
                    candidate_scores[target] = candidate_scores.get(target, 0.0) + w

    # Priority sort candidates by graph centrality / workflow relevance score
    sorted_candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)

    # Diversity Quota Balancing: prioritize archetypes under-represented in anchors
    present_archetypes: Dict[str, int] = {}
    for node in team_nodes:
        arch = graph.nodes[node].get("archetype", "engineering_staff")
        present_archetypes[arch] = present_archetypes.get(arch, 0) + 1

    # First pass: add candidates that satisfy missing target archetypes
    for cand, _ in sorted_candidates:
        if len(team_nodes) >= max_roles:
            break
        cand_arch = graph.nodes[cand].get("archetype", "engineering_staff")
        target_count = TARGET_ARCHETYPES.get(cand_arch, 1)
        if present_archetypes.get(cand_arch, 0) < target_count:
            team_nodes.add(cand)
            present_archetypes[cand_arch] = present_archetypes.get(cand_arch, 0) + 1

    # Second pass: fill remaining capacity up to max_roles or at least min_roles
    for cand, _ in sorted_candidates:
        if len(team_nodes) >= max_roles:
            break
        if cand not in team_nodes:
            team_nodes.add(cand)
            cand_arch = graph.nodes[cand].get("archetype", "engineering_staff")
            present_archetypes[cand_arch] = present_archetypes.get(cand_arch, 0) + 1

    # Extract induced subgraph containing all interconnecting workflow edges
    induced_subgraph = graph.subgraph(team_nodes).copy()

    # Format output manifest
    team_role_ids = list(team_nodes)
    team_slugs = [
        graph.nodes[nid].get("slug", nid.replace("role:", "").replace("role_", ""))
        for nid in team_role_ids
    ]

    archetype_map: Dict[str, List[str]] = {}
    for nid in team_role_ids:
        arch = graph.nodes[nid].get("archetype", "engineering_staff")
        if arch not in archetype_map:
            archetype_map[arch] = []
        archetype_map[arch].append(nid)

    assembled_roles: List[CanonicalRole] = []
    if roles_by_id:
        for nid in team_role_ids:
            clean_id = f"role_{nid.replace('role:', '').replace('role_', '')}"
            if clean_id in roles_by_id:
                assembled_roles.append(roles_by_id[clean_id])
            elif nid in roles_by_id:
                assembled_roles.append(roles_by_id[nid])

    return {
        "team_role_ids": team_role_ids,
        "team_slugs": team_slugs,
        "team_size": len(team_nodes),
        "subgraph": induced_subgraph,
        "edges": list(induced_subgraph.edges(data=True)),
        "archetypes": archetype_map,
        "roles": assembled_roles,
    }
