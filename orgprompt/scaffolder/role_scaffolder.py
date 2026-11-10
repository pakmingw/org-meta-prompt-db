"""Role Scaffolder API: Extracts and packages complete operational blueprints for canonical roles."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from orgprompt.db.connection import get_connection, get_default_db_path
from orgprompt.scaffolder.formatter import format_role_json, format_role_markdown


@dataclass
class RoleScaffoldingPackage:
    """Complete executable scaffolding package for a canonical role."""

    role: Dict[str, Any]
    use_cases: List[Dict[str, Any]] = field(default_factory=list)
    tools: List[Dict[str, Any]] = field(default_factory=list)
    subagent_swarm: List[Dict[str, Any]] = field(default_factory=list)
    genai_plan: Optional[Dict[str, Any]] = None
    company_context: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts package to native Python dictionary."""
        return {
            "role": self.role,
            "company_context": self.company_context,
            "use_cases": self.use_cases,
            "tools": self.tools,
            "subagent_swarm": self.subagent_swarm,
            "genai_plan": self.genai_plan,
        }

    def to_json(self, indent: int = 2) -> str:
        """Exports package as formatted JSON string."""
        return format_role_json(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        """Exports package as comprehensive executive Markdown runbook."""
        return format_role_markdown(self.to_dict())

    def save(self, path: Union[str, Path], format: str = "json") -> Path:
        """Saves package to disk in specified format ('json' or 'markdown')."""
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if format.lower() in ("markdown", "md"):
            out_path.write_text(self.to_markdown(), encoding="utf-8")
        else:
            out_path.write_text(self.to_json(), encoding="utf-8")
        return out_path


class RoleScaffolder:
    """Loads canonical roles and packages use cases, tools, swarms, and GenAI plans."""

    def __init__(
        self,
        conn: Optional[sqlite3.Connection] = None,
        db_path: Optional[Union[str, Path]] = None,
    ) -> None:
        self.conn = conn or get_connection(db_path or get_default_db_path())
        self._owns_conn = conn is None

    def __enter__(self) -> RoleScaffolder:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    @classmethod
    def build_from_db(
        cls,
        db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None,
    ) -> RoleScaffolder:
        """Factory constructor using connection or file path."""
        if isinstance(db_path_or_conn, sqlite3.Connection):
            return cls(conn=db_path_or_conn)
        return cls(db_path=db_path_or_conn)

    def scaffold_role(
        self,
        role_id_or_title: str,
        company_name: Optional[str] = None,
    ) -> RoleScaffoldingPackage:
        """Scaffolds a complete role package from the knowledge base.

        Args:
            role_id_or_title: Role ID (e.g. 'role_fin_chief_investment_officer'),
                slug (e.g. 'fin_chief_investment_officer'), or title substring.
            company_name: Optional company context to attach.

        Returns:
            RoleScaffoldingPackage ready for export.
        """
        if not role_id_or_title or not role_id_or_title.strip():
            raise KeyError("Empty or whitespace-only role identifier provided")

        cursor = self.conn.cursor()

        # 1. Resolve role record
        query_role = """
            SELECT
                r.id, r.org_unit_id, r.slug, r.name, r.seniority_level, r.role_archetype,
                r.mission, r.system_prompt, r.character_count, r.capabilities_json,
                r.mental_models_json, r.domain_heuristics_json, r.technical_vocabulary_json,
                r.anti_patterns_json, r.metadata_json,
                u.name as unit_name, o.name as exemplar_name, i.name as industry_name
            FROM canonical_roles r
            LEFT JOIN org_units u ON r.org_unit_id = u.id
            LEFT JOIN exemplar_orgs o ON u.exemplar_org_id = o.id
            LEFT JOIN industries i ON o.industry_id = i.id
            WHERE r.id = ? OR r.slug = ? OR r.name = ?
            LIMIT 1;
        """
        row = cursor.execute(query_role, (role_id_or_title, role_id_or_title, role_id_or_title)).fetchone()

        if not row:
            # Try case-insensitive and slug normalization
            clean_slug = role_id_or_title.lower().strip().replace("-", "_").replace(" ", "_")
            if not clean_slug.startswith("role_"):
                slug_with_prefix = f"role_{clean_slug}"
            else:
                slug_with_prefix = clean_slug

            query_loose = """
                SELECT
                    r.id, r.org_unit_id, r.slug, r.name, r.seniority_level, r.role_archetype,
                    r.mission, r.system_prompt, r.character_count, r.capabilities_json,
                    r.mental_models_json, r.domain_heuristics_json, r.technical_vocabulary_json,
                    r.anti_patterns_json, r.metadata_json,
                    u.name as unit_name, o.name as exemplar_name, i.name as industry_name
                FROM canonical_roles r
                LEFT JOIN org_units u ON r.org_unit_id = u.id
                LEFT JOIN exemplar_orgs o ON u.exemplar_org_id = o.id
                LEFT JOIN industries i ON o.industry_id = i.id
                WHERE r.slug = ? OR r.id = ? OR LOWER(r.name) = LOWER(?) OR r.slug LIKE ? OR r.name LIKE ?
                LIMIT 1;
            """
            row = cursor.execute(
                query_loose,
                (clean_slug, slug_with_prefix, role_id_or_title, f"%{clean_slug}%", f"%{role_id_or_title}%"),
            ).fetchone()

        if not row:
            raise KeyError(f"Canonical role '{role_id_or_title}' not found in knowledge base.")

        role_id = row[0]
        role_dict = {
            "id": row[0],
            "org_unit_id": row[1],
            "slug": row[2],
            "name": row[3],
            "title": row[3],
            "seniority_level": row[4],
            "seniority_tier": row[4],
            "role_archetype": row[5],
            "mission": row[6],
            "system_prompt": row[7],
            "character_count": row[8],
            "capabilities": json.loads(row[9]) if row[9] else [],
            "mental_models": json.loads(row[10]) if row[10] else [],
            "heuristics": json.loads(row[11]) if row[11] else [],
            "vocabulary": json.loads(row[12]) if row[12] else [],
            "anti_patterns": json.loads(row[13]) if row[13] else [],
            "metadata": json.loads(row[14]) if row[14] else {},
            "unit_name": row[15] or "Operations",
            "exemplar_name": row[16] or "Exemplar Org",
            "industry_name": row[17] or "Enterprise",
        }

        # 2. Fetch use cases
        cursor.execute(
            """
            SELECT
                id, role_id, title, cadence, trigger_event,
                inputs_consumed_json, horizontal_tools_json, vertical_tools_json,
                cognitive_bottlenecks, output_artifacts_json, metadata_json
            FROM role_use_cases
            WHERE role_id = ?
            ORDER BY id ASC;
            """,
            (role_id,),
        )
        use_cases: List[Dict[str, Any]] = []
        for uc_row in cursor.fetchall():
            use_cases.append({
                "id": uc_row[0],
                "role_id": uc_row[1],
                "title": uc_row[2],
                "cadence": uc_row[3],
                "trigger_event": uc_row[4],
                "trigger": uc_row[4],
                "inputs_consumed": json.loads(uc_row[5]) if uc_row[5] else [],
                "inputs": json.loads(uc_row[5]) if uc_row[5] else [],
                "horizontal_tools": json.loads(uc_row[6]) if uc_row[6] else [],
                "vertical_tools": json.loads(uc_row[7]) if uc_row[7] else [],
                "domain_tools": json.loads(uc_row[7]) if uc_row[7] else [],
                "cognitive_bottlenecks": uc_row[8],
                "output_artifacts": json.loads(uc_row[9]) if uc_row[9] else [],
                "metadata": json.loads(uc_row[10]) if uc_row[10] else {},
            })

        # 3. Fetch role tooling
        cursor.execute(
            """
            SELECT
                rt.id, rt.role_id, rt.tool_id, rt.usage_frequency, rt.proficiency_level,
                rt.primary_purpose, t.name as tool_name, t.slug as tool_slug,
                t.category, t.archetype, t.vendor_examples_json, t.typical_artifacts_json,
                t.description
            FROM role_tooling rt
            JOIN tools t ON rt.tool_id = t.id
            WHERE rt.role_id = ?
            ORDER BY rt.id ASC;
            """,
            (role_id,),
        )
        tools: List[Dict[str, Any]] = []
        for t_row in cursor.fetchall():
            tools.append({
                "id": t_row[0],
                "role_id": t_row[1],
                "tool_id": t_row[2],
                "usage_frequency": t_row[3],
                "proficiency_level": t_row[4],
                "primary_purpose": t_row[5],
                "name": t_row[6],
                "tool_name": t_row[6],
                "slug": t_row[7],
                "category": t_row[8],
                "archetype": t_row[9],
                "vendor_examples": json.loads(t_row[10]) if t_row[10] else [],
                "typical_artifacts": json.loads(t_row[11]) if t_row[11] else [],
                "description": t_row[12],
            })

        # 4. Fetch subagent swarm
        cursor.execute(
            """
            SELECT
                id, role_id, subagent_name, subagent_role, system_prompt,
                tool_mcp_bindings_json, interaction_dag_json, hitl_checkpoint, metadata_json
            FROM role_subagent_swarms
            WHERE role_id = ?
            ORDER BY id ASC;
            """,
            (role_id,),
        )
        swarm: List[Dict[str, Any]] = []
        for s_row in cursor.fetchall():
            swarm.append({
                "id": s_row[0],
                "role_id": s_row[1],
                "subagent_name": s_row[2],
                "subagent_role": s_row[3],
                "system_prompt": s_row[4],
                "tool_mcp_bindings": json.loads(s_row[5]) if s_row[5] else [],
                "mcp_tools": json.loads(s_row[5]) if s_row[5] else [],
                "interaction_dag": json.loads(s_row[6]) if s_row[6] else {},
                "hitl_checkpoint": s_row[7],
                "metadata": json.loads(s_row[8]) if s_row[8] else {},
            })

        # 5. Fetch GenAI plan
        cursor.execute(
            """
            SELECT
                id, role_id, horizontal_genai_spec_json, vertical_genai_spec_json,
                rag_context_architecture, mcp_integrations_json, hitl_guardrails,
                roi_productivity_impact, metadata_json
            FROM role_genai_plans
            WHERE role_id = ?
            LIMIT 1;
            """,
            (role_id,),
        )
        g_row = cursor.fetchone()
        genai_plan = None
        if g_row:
            genai_plan = {
                "id": g_row[0],
                "role_id": g_row[1],
                "horizontal_genai_spec": json.loads(g_row[2]) if g_row[2] else {},
                "vertical_genai_spec": json.loads(g_row[3]) if g_row[3] else {},
                "rag_context_architecture": g_row[4],
                "mcp_integrations": json.loads(g_row[5]) if g_row[5] else [],
                "hitl_guardrails": g_row[6],
                "roi_productivity_impact": g_row[7],
                "metadata": json.loads(g_row[8]) if g_row[8] else {},
            }

        return RoleScaffoldingPackage(
            role=role_dict,
            use_cases=use_cases,
            tools=tools,
            subagent_swarm=swarm,
            genai_plan=genai_plan,
            company_context=company_name,
        )

    def close(self) -> None:
        """Closes the database connection if owned."""
        if self._owns_conn and self.conn:
            self.conn.close()
