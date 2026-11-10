"""NetworkX Knowledge Graph engine for the Organizational Knowledge Graph."""

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
import networkx as nx

from orgprompt.db.connection import get_connection
from orgprompt.graph.invariants import WORKFLOW_EDGE_TYPES, validate_knowledge_graph
from orgprompt.models import ValidationReport


def normalize_node_id(prefix: str, identifier: str) -> str:
    """Normalizes an entity identifier to standard format 'prefix:slug'."""
    slug = identifier
    for p in [
        "role_", "unit_", "org_", "ind_", "art_", "mech_", "f500_", "company_", "tool_",
        "role:", "unit:", "org:", "ind:", "art:", "mech:", "f500:", "company:", "tool:",
    ]:
        if slug.startswith(p):
            slug = slug[len(p):]
            break
    return f"{prefix}:{slug}"


def load_knowledge_graph_from_sqlite(db_connection: sqlite3.Connection) -> nx.MultiDiGraph:
    """Hydrates a heterogeneous NetworkX MultiDiGraph from SQLite."""
    g = nx.MultiDiGraph()
    cursor = db_connection.cursor()

    # 1. Hydrate Industries
    for row in cursor.execute("SELECT id, slug, name, category, description FROM industries"):
        node_id = f"ind:{row[1]}"
        g.add_node(
            node_id,
            type="Industry",
            label=row[2],
            slug=row[1],
            category=row[3],
            description=row[4],
            db_id=row[0],
        )

    # 2. Hydrate Exemplar Orgs
    for row in cursor.execute(
        "SELECT id, slug, name, industry_id, signature_mechanisms_summary, description FROM exemplar_orgs"
    ):
        node_id = f"org:{row[1]}"
        g.add_node(
            node_id,
            type="ExemplarOrg",
            label=row[2],
            slug=row[1],
            industry_id=row[3],
            mechanisms=row[4],
            description=row[5],
            db_id=row[0],
        )

    # 3. Hydrate Org Units
    for row in cursor.execute(
        "SELECT id, slug, name, exemplar_org_id, division, department, unit_type, core_value_loop, description FROM org_units"
    ):
        node_id = f"unit:{row[1]}"
        g.add_node(
            node_id,
            type="OrgUnit",
            label=row[2],
            slug=row[1],
            org_id=row[3],
            division=row[4],
            department=row[5],
            unit_type=row[6],
            value_loop=row[7],
            description=row[8],
            db_id=row[0],
        )

    # 4. Hydrate Canonical Roles
    for row in cursor.execute(
        """SELECT id, slug, name, org_unit_id, seniority_level, role_archetype,
                  mission, character_count, capabilities_json, mental_models_json,
                  system_prompt FROM canonical_roles"""
    ):
        node_id = f"role:{row[1]}"
        caps = json.loads(row[8]) if row[8] else []
        models = json.loads(row[9]) if row[9] else []
        g.add_node(
            node_id,
            type="CanonicalRole",
            label=row[2],
            slug=row[1],
            unit_id=row[3],
            seniority=row[4],
            archetype=row[5],
            mission=row[6],
            char_count=row[7],
            capabilities=caps,
            mental_models=models,
            system_prompt=row[10],
            db_id=row[0],
        )

    # 5. Hydrate Artifacts
    for row in cursor.execute(
        "SELECT id, slug, name, artifact_type, schema_definition, exemplar_context, description FROM artifacts"
    ):
        node_id = f"art:{row[1]}"
        schema_def = json.loads(row[4]) if row[4] else {}
        g.add_node(
            node_id,
            type="Artifact",
            label=row[2],
            slug=row[1],
            artifact_type=row[3],
            schema_definition=schema_def,
            exemplar_context=row[5],
            description=row[6],
            db_id=row[0],
        )

    # 6. Hydrate Operating Mechanisms
    for row in cursor.execute(
        "SELECT id, slug, name, exemplar_org_id, mechanism_type, enforcement_rules, description FROM operating_mechanisms"
    ):
        node_id = f"mech:{row[1]}"
        g.add_node(
            node_id,
            type="OperatingMechanism",
            label=row[2],
            slug=row[1],
            org_id=row[3],
            mechanism_type=row[4],
            enforcement_rules=row[5],
            description=row[6],
            db_id=row[0],
        )

    # 7. Structural Edges: OrgUnit -> ExemplarOrg (PART_OF)
    for row in cursor.execute(
        "SELECT u.slug, o.slug FROM org_units u JOIN exemplar_orgs o ON u.exemplar_org_id = o.id"
    ):
        g.add_edge(f"unit:{row[0]}", f"org:{row[1]}", key="PART_OF", type="PART_OF")

    # 8. Structural Edges: ExemplarOrg -> Industry (PART_OF)
    for row in cursor.execute(
        "SELECT o.slug, i.slug FROM exemplar_orgs o JOIN industries i ON o.industry_id = i.id"
    ):
        g.add_edge(f"org:{row[0]}", f"ind:{row[1]}", key="PART_OF", type="PART_OF")

    # 9. Structural Edges: CanonicalRole -> OrgUnit (BELONGS_TO)
    for row in cursor.execute(
        "SELECT r.slug, u.slug FROM canonical_roles r JOIN org_units u ON r.org_unit_id = u.id"
    ):
        g.add_edge(f"role:{row[0]}", f"unit:{row[1]}", key="BELONGS_TO", type="BELONGS_TO")

    # 10. Role Workflow & Behavioral Edges
    for row in cursor.execute(
        """SELECT s.slug, t.slug, e.edge_type, e.description, e.protocol, e.cadence
           FROM role_edges e
           JOIN canonical_roles s ON e.source_role_id = s.id
           JOIN canonical_roles t ON e.target_role_id = t.id"""
    ):
        s_node = f"role:{row[0]}"
        t_node = f"role:{row[1]}"
        edge_type = row[2]
        key = f"{edge_type}_{row[1]}"
        g.add_edge(
            s_node,
            t_node,
            key=key,
            type=edge_type,
            description=row[3],
            protocol=row[4],
            cadence=row[5],
        )

    # 11. Role Artifact Links (PRODUCES / CONSUMES)
    for row in cursor.execute(
        """SELECT r.slug, a.slug, ra.direction, ra.frequency, ra.description
           FROM role_artifacts ra
           JOIN canonical_roles r ON ra.role_id = r.id
           JOIN artifacts a ON ra.artifact_id = a.id"""
    ):
        r_node = f"role:{row[0]}"
        a_node = f"art:{row[1]}"
        direction = row[2]
        key = f"{direction}_{row[1]}"
        g.add_edge(
            r_node,
            a_node,
            key=key,
            type=direction,
            frequency=row[3],
            description=row[4],
        )

    # 12. Role Mechanism Links (PRACTICES)
    for row in cursor.execute(
        """SELECT r.slug, m.slug, rm.participation_level, rm.description
           FROM role_mechanisms rm
           JOIN canonical_roles r ON rm.role_id = r.id
           JOIN operating_mechanisms m ON rm.mechanism_id = m.id"""
    ):
        r_node = f"role:{row[0]}"
        m_node = f"mech:{row[1]}"
        key = f"PRACTICES_{row[1]}"
        g.add_edge(
            r_node,
            m_node,
            key=key,
            type="PRACTICES",
            participation_level=row[2],
            description=row[3],
        )

    # 13. Hydrate Fortune 500 Companies (if table exists)
    cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='fortune500_companies'")
    if cursor.fetchone()[0] > 0:
        for row in cursor.execute(
            """SELECT id, slug, name, rank, revenue_billions, macro_industry,
                      industry_id, sub_sector, business_model, operating_archetype,
                      functional_units_json, metadata_json FROM fortune500_companies"""
        ):
            node_id = f"f500:{row[1]}"
            units = json.loads(row[10]) if row[10] else []
            meta = json.loads(row[11]) if row[11] else {}
            g.add_node(
                node_id,
                type="Fortune500Company",
                label=row[2],
                slug=row[1],
                rank=row[3],
                revenue=row[4],
                revenue_billions=row[4],
                macro_industry=row[5],
                industry_id=row[6],
                sub_sector=row[7],
                business_model=row[8],
                operating_archetype=row[9],
                functional_units=units,
                metadata=meta,
                db_id=row[0],
            )

    # 14. Hydrate Company Employment Edges: Fortune500Company -> CanonicalRole (EMPLOYS_ROLE)
    cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='employs_role'")
    if cursor.fetchone()[0] > 0:
        for row in cursor.execute(
            """SELECT c.slug, r.slug, e.department, e.priority_tier, e.metadata_json
               FROM employs_role e
               JOIN fortune500_companies c ON e.company_id = c.id
               JOIN canonical_roles r ON e.role_id = r.id"""
        ):
            c_node = f"f500:{row[0]}"
            r_node = f"role:{row[1]}"
            key = f"EMPLOYS_{row[1]}"
            meta = json.loads(row[4]) if row[4] else {}
            g.add_edge(
                c_node,
                r_node,
                key=key,
                type="EMPLOYS_ROLE",
                department=row[2],
                priority_tier=row[3],
                metadata=meta,
            )

    return g


class KnowledgeGraphEngine:
    """Core NetworkX Knowledge Graph builder, validator, and query engine."""

    @classmethod
    def build_from_db(
        cls,
        db_path: Optional[Union[str, Path]] = None,
        conn: Optional[sqlite3.Connection] = None,
    ) -> nx.MultiDiGraph:
        """Builds and hydrates the NetworkX Knowledge Graph from SQLite."""
        if conn is None:
            conn = get_connection(db_path)
        return load_knowledge_graph_from_sqlite(conn)

    @classmethod
    def validate_invariants(cls, G: nx.DiGraph) -> ValidationReport:
        """Runs the 4-point structural invariant audit on the graph."""
        return validate_knowledge_graph(G)

    @classmethod
    def validate_expansion_invariants(cls, G: nx.DiGraph) -> ValidationReport:
        """Runs the expansion structural invariant audit on the graph."""
        from orgprompt.graph.invariants import validate_expansion_invariants
        return validate_expansion_invariants(G)

    @classmethod
    def expand_subgraph(
        cls,
        G: nx.DiGraph,
        anchor_roles: List[str],
        hops: int = 1,
        include_artifacts: bool = True,
        include_units: bool = True,
    ) -> nx.DiGraph:
        """Expands the anchor roles across workflow edges to assemble a cohesive team subgraph.

        Traverses outgoing and incoming workflow edges up to `hops` distance.
        """
        anchor_nodes: Set[str] = set()
        for a in anchor_roles:
            norm = normalize_node_id("role", a)
            if norm in G:
                anchor_nodes.add(norm)
            elif a in G:
                anchor_nodes.add(a)

        selected_nodes: Set[str] = set(anchor_nodes)
        frontier: Set[str] = set(anchor_nodes)

        for _ in range(hops):
            next_frontier: Set[str] = set()
            for u in frontier:
                # Outgoing workflow edges
                for _, v, data in G.out_edges(u, data=True):
                    edge_type = data.get("type", "")
                    if edge_type in WORKFLOW_EDGE_TYPES and G.nodes[v].get("type") == "CanonicalRole":
                        if v not in selected_nodes:
                            selected_nodes.add(v)
                            next_frontier.add(v)
                # Incoming workflow edges
                for v, _, data in G.in_edges(u, data=True):
                    edge_type = data.get("type", "")
                    if edge_type in WORKFLOW_EDGE_TYPES and G.nodes[v].get("type") == "CanonicalRole":
                        if v not in selected_nodes:
                            selected_nodes.add(v)
                            next_frontier.add(v)
            frontier = next_frontier

        # Optionally add connected artifacts and units for selected roles
        extra_nodes: Set[str] = set()
        if include_artifacts or include_units:
            for r in selected_nodes:
                for _, target, data in G.out_edges(r, data=True):
                    ntype = G.nodes[target].get("type", "")
                    if include_artifacts and ntype == "Artifact":
                        extra_nodes.add(target)
                    elif include_units and ntype == "OrgUnit":
                        extra_nodes.add(target)

        all_nodes = selected_nodes | extra_nodes
        # Return induced subgraph
        subgraph = G.subgraph(all_nodes).copy()
        return subgraph
