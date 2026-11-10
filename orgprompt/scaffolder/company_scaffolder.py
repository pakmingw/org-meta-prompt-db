"""Company Scaffolder API: Synthesizes enterprise operational runbooks and role staffing swarms."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from orgprompt.db.connection import get_connection, get_default_db_path
from orgprompt.scaffolder.formatter import format_company_json, format_company_markdown


@dataclass
class CompanyScaffoldingPackage:
    """Complete enterprise scaffolding package for a corporation."""

    company: Dict[str, Any]
    divisions: List[str] = field(default_factory=list)
    employed_roles: List[Dict[str, Any]] = field(default_factory=list)
    tools: List[Dict[str, Any]] = field(default_factory=list)
    swarms: List[Dict[str, Any]] = field(default_factory=list)
    comparison: Optional[Dict[str, Any]] = None
    problem_statement: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converts package to native Python dictionary."""
        return {
            "company": self.company,
            "problem_statement": self.problem_statement,
            "divisions": self.divisions,
            "employed_roles": self.employed_roles,
            "tools": self.tools,
            "swarms": self.swarms,
            "comparison": self.comparison,
        }

    def to_json(self, indent: int = 2) -> str:
        """Exports package as formatted JSON string."""
        return format_company_json(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        """Exports package as comprehensive executive Markdown runbook."""
        return format_company_markdown(self.to_dict())

    def save(self, path: Union[str, Path], format: str = "json") -> Path:
        """Saves package to disk in specified format ('json' or 'markdown')."""
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if format.lower() in ("markdown", "md"):
            out_path.write_text(self.to_markdown(), encoding="utf-8")
        else:
            out_path.write_text(self.to_json(), encoding="utf-8")
        return out_path


class CompanyScaffolder:
    """Loads enterprise data and packages divisions, employed roles, tools, and swarms."""

    def __init__(
        self,
        conn: Optional[sqlite3.Connection] = None,
        db_path: Optional[Union[str, Path]] = None,
    ) -> None:
        self.conn = conn or get_connection(db_path or get_default_db_path())
        self._owns_conn = conn is None

    def __enter__(self) -> CompanyScaffolder:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    @classmethod
    def build_from_db(
        cls,
        db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None,
    ) -> CompanyScaffolder:
        """Factory constructor using connection or file path."""
        if isinstance(db_path_or_conn, sqlite3.Connection):
            return cls(conn=db_path_or_conn)
        return cls(db_path=db_path_or_conn)

    def scaffold_company(
        self,
        company_name: str,
        division: Optional[str] = None,
        business_problem: Optional[str] = None,
    ) -> CompanyScaffoldingPackage:
        """Scaffolds a complete enterprise package from the knowledge base.

        Args:
            company_name: Company name, ticker, or slug.
            division: Optional division/department filter.
            business_problem: Optional executive challenge statement.

        Returns:
            CompanyScaffoldingPackage ready for export.
        """
        if not company_name or not company_name.strip():
            raise KeyError("Empty or whitespace-only company identifier provided")

        cursor = self.conn.cursor()

        # 1. Resolve company
        query_company = """
            SELECT
                id, slug, name, rank, revenue_billions, macro_industry, industry_id,
                sub_sector, business_model, operating_archetype, functional_units_json,
                metadata_json
            FROM fortune500_companies
            WHERE id = ? OR slug = ? OR name = ?
            LIMIT 1;
        """
        row = cursor.execute(query_company, (company_name, company_name, company_name)).fetchone()

        if not row:
            clean = company_name.lower().strip().replace("-", "_").replace(" ", "_")
            if not clean.startswith("f500_"):
                slug_prefix = f"f500_{clean}"
            else:
                slug_prefix = clean

            query_loose = """
                SELECT
                    id, slug, name, rank, revenue_billions, macro_industry, industry_id,
                    sub_sector, business_model, operating_archetype, functional_units_json,
                    metadata_json
                FROM fortune500_companies
                WHERE slug = ? OR id = ? OR LOWER(name) = LOWER(?)
                   OR metadata_json LIKE ? OR name LIKE ? OR slug LIKE ?
                LIMIT 1;
            """
            row = cursor.execute(
                query_loose,
                (clean, slug_prefix, company_name, f'%"ticker": "{company_name.upper()}"%', f"%{company_name}%", f"%{clean}%"),
            ).fetchone()

        if not row:
            raise KeyError(f"Enterprise company '{company_name}' not found in knowledge base.")

        company_id = row[0]
        meta = json.loads(row[11]) if row[11] else {}
        functional_units = json.loads(row[10]) if row[10] else []

        company_dict = {
            "id": row[0],
            "slug": row[1],
            "name": row[2],
            "rank": row[3],
            "revenue_billions": row[4],
            "macro_industry": row[5],
            "industry_id": row[6],
            "sub_sector": row[7],
            "business_model": row[8],
            "operating_archetype": row[9],
            "metadata": meta,
        }

        # 2. Fetch employed roles
        query_roles = """
            SELECT
                er.id, er.company_id, er.role_id, er.department, er.priority_tier,
                r.slug, r.name, r.seniority_level, r.role_archetype, r.mission
            FROM employs_role er
            JOIN canonical_roles r ON er.role_id = r.id
            WHERE er.company_id = ?
        """
        params: List[Any] = [company_id]
        if division:
            query_roles += " AND (LOWER(er.department) LIKE ? OR LOWER(er.department) = ?)"
            params.extend([f"%{division.lower()}%", division.lower()])

        query_roles += " ORDER BY er.department ASC, r.name ASC;"

        cursor.execute(query_roles, params)
        employed_roles: List[Dict[str, Any]] = []
        departments_seen = set()
        role_ids: List[str] = []

        for r_row in cursor.fetchall():
            employed_roles.append({
                "id": r_row[0],
                "company_id": r_row[1],
                "role_id": r_row[2],
                "department": r_row[3],
                "priority_tier": r_row[4],
                "slug": r_row[5],
                "name": r_row[6],
                "title": r_row[6],
                "seniority_level": r_row[7],
                "role_archetype": r_row[8],
                "mission": r_row[9],
            })
            departments_seen.add(r_row[3])
            role_ids.append(r_row[2])

        divisions = functional_units if functional_units else sorted(list(departments_seen))

        # 3. Fetch unique tools used across company roles
        tools: List[Dict[str, Any]] = []
        if role_ids:
            placeholders = ",".join("?" for _ in role_ids)
            query_tools = f"""
                SELECT DISTINCT
                    t.id, t.slug, t.name, t.category, t.archetype,
                    t.vendor_examples_json, t.typical_artifacts_json, t.description
                FROM role_tooling rt
                JOIN tools t ON rt.tool_id = t.id
                WHERE rt.role_id IN ({placeholders})
                ORDER BY t.category ASC, t.name ASC;
            """
            cursor.execute(query_tools, role_ids)
            for t_row in cursor.fetchall():
                tools.append({
                    "id": t_row[0],
                    "slug": t_row[1],
                    "name": t_row[2],
                    "category": t_row[3],
                    "archetype": t_row[4],
                    "vendor_examples": json.loads(t_row[5]) if t_row[5] else [],
                    "typical_artifacts": json.loads(t_row[6]) if t_row[6] else [],
                    "description": t_row[7],
                })

        # 4. Fetch personal swarms for key employed roles (limit to top 15 strategic roles)
        swarms: List[Dict[str, Any]] = []
        target_roles = [r for r in employed_roles if r.get("priority_tier") in ("STRATEGIC_LEADERSHIP", "CORE", "SPECIALIZED")]
        if not target_roles:
            target_roles = employed_roles[:15]
        else:
            target_roles = target_roles[:15]

        for tr in target_roles:
            cursor.execute(
                """
                SELECT subagent_name, subagent_role, system_prompt, tool_mcp_bindings_json, hitl_checkpoint
                FROM role_subagent_swarms
                WHERE role_id = ?
                ORDER BY id ASC;
                """,
                (tr["role_id"],),
            )
            subagents: List[Dict[str, Any]] = []
            for sa_row in cursor.fetchall():
                subagents.append({
                    "subagent_name": sa_row[0],
                    "subagent_role": sa_row[1],
                    "system_prompt": sa_row[2],
                    "tool_mcp_bindings": json.loads(sa_row[3]) if sa_row[3] else [],
                    "hitl_checkpoint": sa_row[4],
                })
            if subagents:
                swarms.append({
                    "role_id": tr["role_id"],
                    "role_name": tr["name"],
                    "role_slug": tr["slug"],
                    "department": tr["department"],
                    "priority_tier": tr["priority_tier"],
                    "subagents": subagents,
                })

        # 5. Fetch comparison data if available
        cursor.execute(
            """
            SELECT
                f500_rank, company_name, internet_divisions_json, internet_bespoke_roles_json,
                db_mapped_roles_count, alignment_score, delta_analysis_md, tailored_swarm_recommendation_md
            FROM company_internet_comparisons
            WHERE company_id = ?
            LIMIT 1;
            """,
            (company_id,),
        )
        c_row = cursor.fetchone()
        comparison = None
        if c_row:
            comparison = {
                "f500_rank": c_row[0],
                "company_name": c_row[1],
                "internet_divisions": json.loads(c_row[2]) if c_row[2] else [],
                "internet_bespoke_roles": json.loads(c_row[3]) if c_row[3] else [],
                "db_mapped_roles_count": c_row[4],
                "alignment_score": c_row[5],
                "delta_analysis_md": c_row[6],
                "tailored_swarm_recommendation_md": c_row[7],
            }

        return CompanyScaffoldingPackage(
            company=company_dict,
            divisions=divisions,
            employed_roles=employed_roles,
            tools=tools,
            swarms=swarms,
            comparison=comparison,
            problem_statement=business_problem,
        )

    def close(self) -> None:
        """Closes the database connection if owned."""
        if self._owns_conn and self.conn:
            self.conn.close()
