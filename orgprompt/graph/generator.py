"""Dynamic role generator utility for the Organizational Knowledge Graph."""

import json
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import networkx as nx

from orgprompt.db.connection import get_connection
from orgprompt.graph.engine import normalize_node_id
from orgprompt.graph.invariants import validate_knowledge_graph
from orgprompt.models import CanonicalRole, RoleGenSpec, RoleGenerationRequest, RoleGenerationResult
from orgprompt.prompts.compiler import PromptCompiler


class RoleSpecificationError(Exception):
    """Raised when role generation parameters are invalid or violate invariants."""


class RoleGenerator:
    """Dynamic generator to synthesize, validate, and persist new canonical roles."""

    def __init__(
        self,
        db_path: Optional[Union[str, Path]] = None,
        conn: Optional[sqlite3.Connection] = None,
        G: Optional[nx.DiGraph] = None,
    ):
        self.db_path = db_path
        self.conn = conn
        self.G = G

    @staticmethod
    def generate_role(
        spec: Union[RoleGenSpec, RoleGenerationRequest, Dict[str, Any]],
        db_path: Optional[Union[str, Path, sqlite3.Connection]] = None,
        conn: Optional[sqlite3.Connection] = None,
        G: Optional[nx.DiGraph] = None,
    ) -> CanonicalRole:
        """Dynamically generates a new valid canonical role, writes to SQLite,
        updates the NetworkX graph, and validates invariants.
        """

        if isinstance(db_path, sqlite3.Connection):
            conn = db_path
            db_path = None

        if isinstance(spec, dict):
            request = RoleGenSpec(**spec)
        else:
            request = spec

        if conn is None:
            conn = get_connection(db_path)

        # 1. Validation & Resolution
        cursor = conn.cursor()
        unit_row = cursor.execute(
            """SELECT u.id, u.slug, u.name, u.division, u.department,
                      o.id, o.slug, o.name, o.signature_mechanisms_summary,
                      i.id, i.slug, i.name
               FROM org_units u
               JOIN exemplar_orgs o ON u.exemplar_org_id = o.id
               JOIN industries i ON o.industry_id = i.id
               WHERE u.slug = ? OR u.id = ?""",
            (request.org_unit_slug, f"unit_{request.org_unit_slug}"),
        ).fetchone()

        if not unit_row:
            clean_token = request.org_unit_slug.replace("unit_", "").replace("-", "_").split("_")[0]
            unit_row = cursor.execute(
                """SELECT u.id, u.slug, u.name, u.division, u.department,
                          o.id, o.slug, o.name, o.signature_mechanisms_summary,
                          i.id, i.slug, i.name
                   FROM org_units u
                   JOIN exemplar_orgs o ON u.exemplar_org_id = o.id
                   JOIN industries i ON o.industry_id = i.id
                   WHERE u.slug LIKE ? OR o.slug LIKE ? OR u.name LIKE ?
                   LIMIT 1""",
                (f"%{clean_token}%", f"%{clean_token}%", f"%{clean_token}%"),
            ).fetchone()

        if not unit_row:
            raise RoleSpecificationError(
                f"Target organizational unit '{request.org_unit_slug}' does not exist in database."
            )

        unit_id, unit_slug, unit_name, unit_div, unit_dept = (
            unit_row[0],
            unit_row[1],
            unit_row[2],
            unit_row[3],
            unit_row[4],
        )
        org_id, org_slug, org_name, org_mech = (
            unit_row[5],
            unit_row[6],
            unit_row[7],
            unit_row[8],
        )
        ind_id, ind_slug, ind_name = unit_row[9], unit_row[10], unit_row[11]

        # Generate slug
        role_slug = re.sub(r"[^a-zA-Z0-9]+", "_", request.name.lower()).strip("_")
        role_id = f"role_{role_slug}"

        # Verify uniqueness
        existing = cursor.execute(
            "SELECT id FROM canonical_roles WHERE slug = ? OR id = ?",
            (role_slug, role_id),
        ).fetchone()
        if existing:
            raise RoleSpecificationError(
                f"Canonical role with slug '{role_slug}' already exists."
            )

        # 2. Hierarchy Linkage Inference (Invariant 2)
        supervisor_slug = request.reports_to_role_slug
        if supervisor_slug:
            # check supervisor exists
            sup_row = cursor.execute(
                "SELECT id, slug FROM canonical_roles WHERE slug = ? OR id = ?",
                (supervisor_slug, f"role_{supervisor_slug}"),
            ).fetchone()
            if not sup_row:
                raise RoleSpecificationError(
                    f"Supervisor role '{supervisor_slug}' not found."
                )
            supervisor_id = sup_row[0]
            supervisor_slug = sup_row[1]
        else:
            # Infer supervisor from org unit or exemplar org leadership
            lead_row = cursor.execute(
                """SELECT id, slug FROM canonical_roles
                   WHERE org_unit_id = ? AND seniority_level IN ('C_SUITE', 'VP', 'DIRECTOR')
                   ORDER BY CASE seniority_level
                       WHEN 'C_SUITE' THEN 1
                       WHEN 'VP' THEN 2
                       WHEN 'DIRECTOR' THEN 3
                       ELSE 4 END
                   LIMIT 1""",
                (unit_id,),
            ).fetchone()
            if not lead_row:
                # search across exemplar org units
                lead_row = cursor.execute(
                    """SELECT r.id, r.slug FROM canonical_roles r
                       JOIN org_units u ON r.org_unit_id = u.id
                       WHERE u.exemplar_org_id = ?
                       ORDER BY CASE r.seniority_level
                           WHEN 'C_SUITE' THEN 1
                           WHEN 'VP' THEN 2
                           WHEN 'DIRECTOR' THEN 3
                           ELSE 4 END
                       LIMIT 1""",
                    (org_id,),
                ).fetchone()

            if not lead_row:
                # Fallback to any role in industry
                lead_row = cursor.execute(
                    """SELECT r.id, r.slug FROM canonical_roles r
                       JOIN org_units u ON r.org_unit_id = u.id
                       JOIN exemplar_orgs o ON u.exemplar_org_id = o.id
                       WHERE o.industry_id = ?
                       LIMIT 1""",
                    (ind_id,),
                ).fetchone()

            supervisor_id = lead_row[0]
            supervisor_slug = lead_row[1]

        # 3. Workflow Linkage Inference (Invariant 3)
        workflow_targets: List[str] = []
        for cslug in request.collaborates_with_role_slugs:
            crow = cursor.execute(
                "SELECT id, slug FROM canonical_roles WHERE slug = ? OR id = ?",
                (cslug, f"role_{cslug}"),
            ).fetchone()
            if not crow:
                raise RoleSpecificationError(
                    f"Collaborator role '{cslug}' not found in canonical roles."
                )
            if crow[1] not in workflow_targets:
                workflow_targets.append(crow[1])

        # Ensure at least 2 distinct workflow targets
        if len(workflow_targets) < 2:
            # Find peers in same unit
            peer_rows = cursor.execute(
                "SELECT slug FROM canonical_roles WHERE org_unit_id = ? AND slug != ? LIMIT 3",
                (unit_id, role_slug),
            ).fetchall()
            for prow in peer_rows:
                pslug = prow[0]
                if pslug not in workflow_targets and pslug != supervisor_slug:
                    workflow_targets.append(pslug)
                if len(workflow_targets) >= 2:
                    break

        if len(workflow_targets) < 2:
            # Find peers in same exemplar org
            peer_rows = cursor.execute(
                """SELECT r.slug FROM canonical_roles r
                   JOIN org_units u ON r.org_unit_id = u.id
                   WHERE u.exemplar_org_id = ? AND r.slug != ? LIMIT 5""",
                (org_id, role_slug),
            ).fetchall()
            for prow in peer_rows:
                pslug = prow[0]
                if pslug not in workflow_targets and pslug != supervisor_slug:
                    workflow_targets.append(pslug)
                if len(workflow_targets) >= 2:
                    break

        # 4. Artifact Creation & Linkage (Invariant 4)
        out_art_name = request.output_artifact_name or f"{request.name} Technical Architecture Specification"
        out_art_slug = re.sub(r"[^a-zA-Z0-9]+", "_", out_art_name.lower()).strip("_")
        out_art_id = f"art_{out_art_slug}"
        out_schema = request.output_artifact_schema or {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": out_art_name,
            "type": "object",
            "required": ["metadata", "architecture_spec", "verification_evidence"],
        }

        # 5. Compile Prompt
        mental_models = request.mental_models or [
            "First-Principles Physical & Logical Decomposition",
            "Zero-Tolerance Invariant Verification",
        ]
        heuristics = [
            f"Enforce {org_name} operational benchmarks and zero-defect quality thresholds.",
            "Eliminate unquantified architectural assumptions prior to handoff.",
        ]
        vocabulary = request.technical_vocabulary or [
            f"{org_name} Engineering Standard",
            "High-Assurance Interface Contract",
        ]
        anti_patterns = request.anti_patterns or [
            "Surface-level facade compliance disguising architectural fragility.",
            "Passing unvalidated data schemas across organizational boundaries.",
        ]
        capabilities = request.capabilities or [
            request.name.lower(),
            request.role_archetype.replace("_", " "),
            org_slug.replace("_", " "),
        ]

        edges_dict = {
            "REPORTS_TO": [supervisor_slug],
            "COLLABORATES_WITH": [workflow_targets[0]] if workflow_targets else [supervisor_slug],
            "HANDS_OFF_TO": [workflow_targets[1]] if len(workflow_targets) > 1 else [supervisor_slug],
        }

        prompt_data = {
            "title": request.name,
            "seniority_tier": request.seniority_level,
            "role_archetype": request.role_archetype,
            "exemplar": org_name,
            "unit": unit_name,
            "mission": request.mission,
            "exemplar_lineage": f"Engineered under {org_name} operational heritage, executing within {unit_name}.",
            "mental_models": mental_models,
            "heuristics": heuristics,
            "vocabulary": vocabulary,
            "anti_patterns": anti_patterns,
            "edges": edges_dict,
            "output_artifact": out_art_name,
            "input_artifact": "Prerequisite_Domain_System_Architecture_Blueprint",
        }
        compiled_prompt = PromptCompiler.compile(prompt_data)
        char_count = len(compiled_prompt)

        # 6. Update and Validate In-Memory Graph if provided
        added_graph_nodes: List[str] = []
        if G is not None:
            r_node = f"role:{role_slug}"
            art_node = f"art:{out_art_slug}"
            if not G.has_node(r_node):
                added_graph_nodes.append(r_node)
            if not G.has_node(art_node):
                added_graph_nodes.append(art_node)

            G.add_node(
                r_node,
                type="CanonicalRole",
                label=request.name,
                slug=role_slug,
                unit_id=unit_id,
                seniority=request.seniority_level,
                archetype=request.role_archetype,
                mission=request.mission,
                char_count=char_count,
                capabilities=capabilities,
                mental_models=mental_models,
                system_prompt=compiled_prompt,
                db_id=role_id,
            )
            # Add artifact node & produces edge
            G.add_node(
                art_node,
                type="Artifact",
                label=out_art_name,
                slug=out_art_slug,
                artifact_type="SPECIFICATION",
                schema_definition=out_schema,
                db_id=out_art_id,
            )
            G.add_edge(r_node, art_node, key="PRODUCES", type="PRODUCES")

            # Add structural edge
            G.add_edge(r_node, f"unit:{unit_slug}", key="BELONGS_TO", type="BELONGS_TO")

            # Add REPORTS_TO
            G.add_edge(
                r_node,
                f"role:{supervisor_slug}",
                key=f"REPORTS_TO_{supervisor_slug}",
                type="REPORTS_TO",
            )
            # Add Workflow edges
            G.add_edge(
                r_node,
                f"role:{workflow_targets[0]}",
                key=f"COLLABORATES_WITH_{workflow_targets[0]}",
                type="COLLABORATES_WITH",
            )
            if len(workflow_targets) > 1:
                G.add_edge(
                    r_node,
                    f"role:{workflow_targets[1]}",
                    key=f"HANDS_OFF_TO_{workflow_targets[1]}",
                    type="HANDS_OFF_TO",
                )

            # If G contains Fortune500Company nodes, link this role to matching companies
            f500_nodes = [
                n for n, d in G.nodes(data=True) if d.get("type") == "Fortune500Company"
            ]
            if f500_nodes:
                matching_f500 = [
                    n for n in f500_nodes if G.nodes[n].get("industry_id") == ind_id
                ]
                if not matching_f500:
                    matching_f500 = f500_nodes[:15]
                for c_node in matching_f500[:25]:
                    G.add_edge(
                        c_node,
                        r_node,
                        key=f"EMPLOYS_{role_slug}",
                        type="EMPLOYS_ROLE",
                        department="Dynamic Operations",
                        priority_tier="CORE",
                    )

            # Validate invariants on G BEFORE committing SQLite!
            report = validate_knowledge_graph(G)
            if not report.is_valid:
                for n in added_graph_nodes:
                    if G.has_node(n):
                        G.remove_node(n)
                raise RoleSpecificationError(
                    f"Generated role broke graph invariants: {report.violations}"
                )

        # 7. Atomic Transaction in SQLite
        try:
            with conn:
                # Insert Artifact
                conn.execute(
                    """INSERT OR REPLACE INTO artifacts (
                        id, slug, name, artifact_type, schema_definition, description, exemplar_context, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        out_art_id,
                        out_art_slug,
                        out_art_name,
                        "SPECIFICATION",
                        json.dumps(out_schema),
                        f"Output deliverable synthesized by {request.name}.",
                        f"Operational context: {org_name}",
                        "{}",
                    ),
                )

                # Insert Canonical Role (Triggers update roles_fts)
                conn.execute(
                    """INSERT INTO canonical_roles (
                        id, org_unit_id, slug, name, seniority_level, role_archetype,
                        mission, system_prompt, character_count, capabilities_json,
                        mental_models_json, domain_heuristics_json, technical_vocabulary_json,
                        anti_patterns_json, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        role_id,
                        unit_id,
                        role_slug,
                        request.name,
                        request.seniority_level,
                        request.role_archetype,
                        request.mission,
                        compiled_prompt,
                        char_count,
                        json.dumps(capabilities),
                        json.dumps(mental_models),
                        json.dumps(heuristics),
                        json.dumps(vocabulary),
                        json.dumps(anti_patterns),
                        "{}",
                    ),
                )

                # Insert Role Artifact Link (PRODUCES)
                conn.execute(
                    """INSERT OR REPLACE INTO role_artifacts (
                        id, role_id, artifact_id, direction, frequency, description, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        f"ra_prod_{role_slug}_{out_art_slug}",
                        role_id,
                        out_art_id,
                        "PRODUCES",
                        "CONTINUOUS",
                        f"Produces {out_art_name}",
                        "{}",
                    ),
                )

                # Insert REPORTS_TO edge
                conn.execute(
                    """INSERT OR REPLACE INTO role_edges (
                        id, source_role_id, target_role_id, edge_type, description, protocol, cadence, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        f"edge_{role_slug}_{supervisor_slug}_reports_to",
                        role_id,
                        supervisor_id,
                        "REPORTS_TO",
                        f"Hierarchical reporting from {request.name} to {supervisor_slug}.",
                        "Weekly 1-on-1 Review",
                        "WEEKLY",
                        "{}",
                    ),
                )

                # Insert Workflow edges
                conn.execute(
                    """INSERT OR REPLACE INTO role_edges (
                        id, source_role_id, target_role_id, edge_type, description, protocol, cadence, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        f"edge_{role_slug}_{workflow_targets[0]}_collaborates",
                        role_id,
                        f"role_{workflow_targets[0]}",
                        "COLLABORATES_WITH",
                        f"Peer collaboration with {workflow_targets[0]}.",
                        "Continuous Sync",
                        "CONTINUOUS",
                        "{}",
                    ),
                )

                if len(workflow_targets) > 1:
                    conn.execute(
                        """INSERT OR REPLACE INTO role_edges (
                            id, source_role_id, target_role_id, edge_type, description, protocol, cadence, metadata_json
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            f"edge_{role_slug}_{workflow_targets[1]}_hands_off",
                            role_id,
                            f"role_{workflow_targets[1]}",
                            "HANDS_OFF_TO",
                            f"Sequential handoff to {workflow_targets[1]}.",
                            "Milestone Delivery Gate",
                            "MILESTONE",
                            "{}",
                        ),
                    )

                # Insert employs_role edges if fortune500_companies and employs_role tables exist
                has_f500_table = cursor.execute(
                    "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='fortune500_companies'"
                ).fetchone()[0] > 0
                has_emp_table = cursor.execute(
                    "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='employs_role'"
                ).fetchone()[0] > 0
                if has_f500_table and has_emp_table:
                    f500_count = cursor.execute("SELECT count(*) FROM fortune500_companies").fetchone()[0]
                    if f500_count > 0:
                        matching_comps = cursor.execute(
                            "SELECT id FROM fortune500_companies WHERE industry_id = ? ORDER BY rank LIMIT 25",
                            (ind_id,),
                        ).fetchall()
                        if not matching_comps:
                            matching_comps = cursor.execute(
                                "SELECT id FROM fortune500_companies ORDER BY rank LIMIT 15"
                            ).fetchall()
                        for comp_row in matching_comps:
                            comp_id = comp_row[0]
                            conn.execute(
                                """INSERT OR REPLACE INTO employs_role (
                                    id, company_id, role_id, department, priority_tier, metadata_json
                                ) VALUES (?, ?, ?, ?, ?, ?)""",
                                (
                                    f"emp_{comp_id}_{role_id}",
                                    comp_id,
                                    role_id,
                                    "Dynamic Operations",
                                    "CORE",
                                    json.dumps({"dynamic": True, "industry_id": ind_id}),
                                ),
                            )
        except Exception as ex:
            if G is not None:
                for n in added_graph_nodes:
                    if G.has_node(n):
                        G.remove_node(n)
            if not isinstance(ex, RoleSpecificationError):
                raise RoleSpecificationError(f"Role generation failed: {ex}") from ex
            raise

        # Build and return CanonicalRole Pydantic instance
        return CanonicalRole(
            id=role_id,
            org_unit_id=unit_id,
            title=request.name,
            slug=role_slug,
            seniority_tier=request.seniority_level,
            role_archetype=request.role_archetype,
            exemplar_lineage=prompt_data["exemplar_lineage"],
            mission=request.mission,
            mental_models=mental_models,
            heuristics=heuristics,
            vocabulary=vocabulary,
            anti_patterns=anti_patterns,
            system_prompt=compiled_prompt,
            capabilities=capabilities,
            output_artifact_ids=[out_art_id],
            input_artifact_ids=[],
        )


generate_role = RoleGenerator().generate_role
