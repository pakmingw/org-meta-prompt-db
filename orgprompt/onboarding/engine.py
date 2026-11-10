"""Programmatic Company Onboarding Engine for OrgPrompt.

Accepts deep-research findings, registers enterprise companies, wires graph employment
edges, synthesizes bespoke roles with full 7-section prompts, day-to-day use cases,
dual-layer tools, and 6-agent personal swarms, updates skill catalogs, and emits
comprehensive 'Apply Generative AI Everywhere' strategic blueprints.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from orgprompt.db.connection import get_connection, get_default_db_path
from orgprompt.graph.engine import KnowledgeGraphEngine
from orgprompt.graph.generator import RoleGenerator, RoleGenSpec
from orgprompt.graph.invariants import validate_expansion_invariants
from orgprompt.onboarding.blueprint_generator import EnterpriseGenAIBlueprintGenerator
from orgprompt.prompts.compiler import PromptCompiler


VALID_BUSINESS_MODELS = {
    "HIGH_VELOCITY_DISTRIBUTOR",
    "MULTI_SIDED_PLATFORM",
    "RECURRING_SUBSCRIPTION_SAAS",
    "ASSET_HEAVY_MANUFACTURER",
    "FINANCIAL_RISK_INTERMEDIARY",
    "INTEGRATED_ENERGY_OPERATOR",
    "CLINICAL_LIFE_SCIENCES_INNOVATOR",
    "PROFESSIONAL_KNOWLEDGE_ADVISORY",
}

VALID_OPERATING_ARCHETYPES = {
    "UNIFICATION",
    "COORDINATION",
    "REPLICATION",
    "DIVERSIFICATION",
    "PLATFORM_ECOSYSTEM",
}


@dataclass
class OnboardingResult:
    """Result of enterprise company onboarding."""

    company_id: str
    company_slug: str
    company_name: str
    rank: int
    blueprint_path: str
    employed_roles_count: int
    bespoke_roles_count: int
    is_valid: bool
    violations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_id": self.company_id,
            "company_slug": self.company_slug,
            "company_name": self.company_name,
            "rank": self.rank,
            "blueprint_path": self.blueprint_path,
            "employed_roles_count": self.employed_roles_count,
            "bespoke_roles_count": self.bespoke_roles_count,
            "is_valid": self.is_valid,
            "violations": self.violations,
        }


class CompanyOnboardingEngine:
    """Programmatic onboarding engine for Fortune 500 and non-F500 corporations."""

    def __init__(
        self,
        conn: Optional[sqlite3.Connection] = None,
        db_path: Optional[Union[str, Path]] = None,
    ) -> None:
        self.conn = conn or get_connection(db_path or get_default_db_path())
        self._owns_conn = conn is None

    @classmethod
    def build_from_db(
        cls,
        db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None,
    ) -> CompanyOnboardingEngine:
        if isinstance(db_path_or_conn, sqlite3.Connection):
            return cls(conn=db_path_or_conn)
        return cls(db_path=db_path_or_conn)

    def onboard_company(
        self,
        company_data: Union[Dict[str, Any], str, Path],
        output_blueprint_path: Optional[Union[str, Path]] = None,
        validate_graph: bool = True,
    ) -> OnboardingResult:
        """Onboards an enterprise into the knowledge base.

        Args:
            company_data: Dictionary or path to JSON file containing company deep-research findings.
            output_blueprint_path: Optional custom path for the generated GenAI blueprint.
            validate_graph: Whether to run full graph invariant verification.

        Returns:
            OnboardingResult with validation status and blueprint path.
        """
        # 1. Parse company input
        if isinstance(company_data, (str, Path)):
            p = Path(company_data)
            if not p.exists():
                raise FileNotFoundError(f"Company research file '{company_data}' not found.")
            data = json.loads(p.read_text(encoding="utf-8"))
        else:
            data = dict(company_data)

        name = data.get("name")
        if not name:
            raise ValueError("Company onboarding data must contain 'name'.")

        slug = data.get("slug") or name.lower().strip().replace(" ", "_").replace("-", "_")
        company_id = data.get("id") or f"f500_{slug}"
        revenue = float(data.get("revenue_billions", 10.0))
        macro_ind = data.get("macro_industry", "Finance")
        sub_sector = data.get("sub_sector", "Financial Technology & Infrastructure")

        # Resolve model and archetype
        model = data.get("business_model", "MULTI_SIDED_PLATFORM")
        if model not in VALID_BUSINESS_MODELS:
            model = "MULTI_SIDED_PLATFORM"

        archetype = data.get("operating_archetype", "PLATFORM_ECOSYSTEM")
        if archetype not in VALID_OPERATING_ARCHETYPES:
            archetype = "PLATFORM_ECOSYSTEM"

        divisions = data.get("divisions") or data.get("operating_units") or [
            "Global Operations",
            "Core Systems Engineering",
            "Product Architecture",
            "Risk & Regulatory Affairs",
            "Enterprise Commercial Solutions",
        ]

        cursor = self.conn.cursor()

        # 2. Resolve or fallback industry_id
        ind_row = cursor.execute(
            "SELECT id FROM industries WHERE name LIKE ? OR slug LIKE ? LIMIT 1;",
            (f"%{macro_ind}%", f"%{macro_ind.lower()}%"),
        ).fetchone()
        if ind_row:
            industry_id = ind_row[0]
        else:
            default_ind = cursor.execute("SELECT id FROM industries LIMIT 1;").fetchone()
            industry_id = default_ind[0] if default_ind else "ind_finance"

        # 3. Determine unique rank
        existing_rank_row = cursor.execute(
            "SELECT rank FROM fortune500_companies WHERE id = ? OR slug = ?;",
            (company_id, slug),
        ).fetchone()

        if existing_rank_row:
            rank = existing_rank_row[0]
        else:
            max_rank_row = cursor.execute(
                "SELECT COALESCE(MAX(rank), 500) FROM fortune500_companies;"
            ).fetchone()
            rank = max_rank_row[0] + 1

        # 4. Insert or update fortune500_companies
        metadata = {
            "ticker": data.get("ticker", "PRIVATE"),
            "publicly_traded": data.get("is_public", False) or data.get("publicly_traded", False),
            "headquarters": data.get("headquarters", "Global Headquarters"),
            "challenges": data.get("challenges", []),
            "onboarded_at": "2026-11-09T23:50:00Z",
            "source": "Deep-Research Company Onboarding Engine",
        }

        cursor.execute(
            """
            INSERT OR REPLACE INTO fortune500_companies (
                id, slug, name, rank, revenue_billions, macro_industry, industry_id,
                sub_sector, business_model, operating_archetype, functional_units_json,
                metadata_json, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP);
            """,
            (
                company_id,
                slug,
                name,
                rank,
                revenue,
                macro_ind,
                industry_id,
                sub_sector,
                model,
                archetype,
                json.dumps(divisions),
                json.dumps(metadata),
            ),
        )

        # 5. Wire employed canonical roles
        employed_canonical = data.get("employed_canonical_roles") or []
        employed_count = 0

        # If no explicit canonical roles provided, map relevant enterprise roles automatically
        if not employed_canonical:
            sample_roles = cursor.execute(
                """
                SELECT r.id, r.slug FROM canonical_roles r
                JOIN org_units u ON r.org_unit_id = u.id
                JOIN exemplar_orgs o ON u.exemplar_org_id = o.id
                WHERE o.industry_id = ? OR r.role_archetype IN ('executive_strategy', 'engineering_staff')
                LIMIT 20;
                """,
                (industry_id,),
            ).fetchall()
            employed_canonical = [r[1] for r in sample_roles]

        for idx, role_ref in enumerate(employed_canonical):
            # Resolve role ID
            r_row = cursor.execute(
                "SELECT id, slug FROM canonical_roles WHERE id = ? OR slug = ? LIMIT 1;",
                (role_ref, role_ref),
            ).fetchone()
            if r_row:
                r_id, r_slug = r_row
                edge_id = f"er_{slug}_{r_slug}"
                dept = divisions[idx % len(divisions)]
                tier = "CORE" if idx % 2 == 0 else "STRATEGIC_LEADERSHIP"
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO employs_role (
                        id, company_id, role_id, department, priority_tier, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (edge_id, company_id, r_id, dept, tier, json.dumps({"source": "onboarding_mesh"})),
                )
                employed_count += 1

        # 6. Synthesize bespoke roles if provided
        bespoke_roles = data.get("bespoke_roles") or []
        bespoke_count = 0

        for b_role in bespoke_roles:
            b_name = b_role.get("name") or b_role.get("title", f"{name} Specialist")
            b_slug = b_role.get("slug") or f"{slug}_{b_name.lower().replace(' ', '_').replace('-', '_')}"
            b_mission = b_role.get("mission") or f"Direct technical and strategic execution for {b_name} within {name}."
            b_tier = b_role.get("seniority") or b_role.get("seniority_tier", "PRINCIPAL_STAFF")
            b_archetype = b_role.get("archetype") or b_role.get("role_archetype", "domain_specialist")
            b_div = b_role.get("division") or divisions[0]

            # Check if bespoke role already exists in database (idempotent re-run support)
            import re
            clean_token = re.sub(r"[^a-zA-Z0-9]+", "_", b_name.lower()).strip("_")
            existing_role_row = cursor.execute(
                "SELECT id, slug, system_prompt FROM canonical_roles WHERE slug = ? OR name = ? OR slug = ?;",
                (b_slug, b_name, clean_token),
            ).fetchone()

            if existing_role_row:
                new_role_id = existing_role_row[0]
                synth_slug = existing_role_row[1]
                synth_prompt = existing_role_row[2]
                bespoke_count += 1
            else:
                # Generate role via RoleGenerator to ensure graph connectivity and Level-2 prompt headers
                spec = RoleGenSpec(
                    name=b_name,
                    org_unit_slug="physical_research_laboratory",  # standard valid unit anchor
                    seniority_level=b_tier,
                    role_archetype=b_archetype,
                    mission=b_mission,
                    capabilities=[f"{slug}_architecture", "distributed_systems", "operational_excellence"],
                    mental_models=["First-Principles Decomposition", "Zero-Trust Verification"],
                    technical_vocabulary=[name, "Scalability", "SLA", "Throughput"],
                    anti_patterns=["Unverified Presumptions", "Architectural Debt"],
                )

                # Generate role
                synth_role = RoleGenerator.generate_role(spec, conn=self.conn)
                new_role_id = synth_role.id
                synth_slug = synth_role.slug
                synth_prompt = synth_role.system_prompt
                bespoke_count += 1

            # Ensure employs_role edge explicitly connects this bespoke role to the onboarded company!
            er_edge_id = f"er_{slug}_{synth_slug}"
            cursor.execute(
                """
                INSERT OR REPLACE INTO employs_role (
                    id, company_id, role_id, department, priority_tier, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?);
                """,
                (er_edge_id, company_id, new_role_id, b_div, "STRATEGIC_LEADERSHIP", json.dumps({"is_bespoke": True})),
            )
            employed_count += 1

            # Populate 5 Day-to-Day Use Cases
            cadences = ["DAILY", "WEEKLY", "MONTHLY", "QUARTERLY", "AD_HOC"]
            for c_idx, cadence in enumerate(cadences, start=1):
                uc_id = f"ruc_{new_role_id}_{c_idx}"
                uc_title = f"{b_name} Operational Workflow {c_idx} ({cadence})"
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO role_use_cases (
                        id, role_id, title, cadence, trigger_event,
                        inputs_consumed_json, horizontal_tools_json, vertical_tools_json,
                        cognitive_bottlenecks, output_artifacts_json, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        uc_id,
                        new_role_id,
                        uc_title,
                        cadence,
                        f"Operational trigger on {cadence.lower()} cycle",
                        json.dumps(["Production Metrics", "Domain Telemetry", "Peer Pull Requests"]),
                        json.dumps(["tool_word_processor", "tool_spreadsheet_processor", "tool_meeting_note_taker"]),
                        json.dumps(["tool_bi_analytics", "tool_bloomberg_terminal"]),
                        "Multi-variable constraint optimization under low latency",
                        json.dumps([f"{b_name}_{cadence}_Deliverable.md"]),
                        json.dumps({"source": "bespoke_onboarding"}),
                    ),
                )

            # Populate Dual-Layer Tooling
            tool_rows = cursor.execute("SELECT id FROM tools LIMIT 5;").fetchall()
            for t_idx, t_row in enumerate(tool_rows, start=1):
                rt_id = f"rt_{new_role_id}_{t_row[0]}"
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO role_tooling (
                        id, role_id, tool_id, usage_frequency, proficiency_level, primary_purpose, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        rt_id,
                        new_role_id,
                        t_row[0],
                        "PRIMARY_DAILY" if t_idx <= 2 else "FREQUENT_WEEKLY",
                        "EXPERT",
                        f"Core daily execution for {b_name}",
                        json.dumps({"source": "bespoke_onboarding"}),
                    ),
                )

            # Populate 6-Agent Personal Subagent Swarm (strictly acyclic)
            swarm_roles = [
                ("CHIEF_OF_STAFF", "Chief of Staff & Orchestrator", "Tunnels context and delegates subagent execution", {"upstream": ["MEETING_GRAPH"], "downstream": ["DOCUMENT_DRAFTER", "QUANTITATIVE_MODELER"]}),
                ("DOCUMENT_DRAFTER", "Lead Technical Drafter", "Authoritative specification and documentation synthesis", {"upstream": ["CHIEF_OF_STAFF"], "downstream": ["DECK_PRESENTER"]}),
                ("QUANTITATIVE_MODELER", "Quantitative Modeler", "Data validation, formula synthesis, and stress testing", {"upstream": ["CHIEF_OF_STAFF"], "downstream": ["DECK_PRESENTER"]}),
                ("DECK_PRESENTER", "Executive Narrative Presenter", "Slide outline and presentation synthesis", {"upstream": ["DOCUMENT_DRAFTER", "QUANTITATIVE_MODELER"], "downstream": ["QUALITY_CRITIC"]}),
                ("MEETING_GRAPH", "Meeting Knowledge Graph Subagent", "Extracts decisions and action items from syncs", {"upstream": [], "downstream": ["CHIEF_OF_STAFF"]}),
                ("QUALITY_CRITIC", "Quality & Compliance Critic", "Adversarial stress-testing and audit review", {"upstream": ["DECK_PRESENTER"], "downstream": ["HUMAN_PRINCIPAL"]}),
            ]
            for sa_code, sa_name, sa_desc, sa_dag in swarm_roles:
                rss_id = f"rss_{new_role_id}_{sa_code.lower()}"
                sa_prompt = (
                    f"# System Prompt: {sa_name} for {b_name}\n"
                    f"You are the specialized {sa_code} subagent operating within the personal swarm of {b_name}.\n"
                    f"Your objective: {sa_desc}.\n"
                    f"Execute with rigorous first-principles analysis and zero hallucination."
                )
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO role_subagent_swarms (
                        id, role_id, subagent_name, subagent_role, system_prompt,
                        tool_mcp_bindings_json, interaction_dag_json, hitl_checkpoint, metadata_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        rss_id,
                        new_role_id,
                        f"{b_name} {sa_name}",
                        sa_code,
                        sa_prompt,
                        json.dumps(["tools_search", "document_writer", "analytics_engine"]),
                        json.dumps(sa_dag),
                        "Mandatory human sign-off required prior to production execution.",
                        json.dumps({"source": "bespoke_onboarding"}),
                    ),
                )

            # Populate GenAI Plan
            rgp_id = f"rgp_{new_role_id}"
            cursor.execute(
                """
                INSERT OR REPLACE INTO role_genai_plans (
                    id, role_id, horizontal_genai_spec_json, vertical_genai_spec_json,
                    rag_context_architecture, mcp_integrations_json, hitl_guardrails,
                    roi_productivity_impact, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    rgp_id,
                    new_role_id,
                    json.dumps({
                        "word_copilot": "Automated draft synthesis with PRD templates",
                        "excel_modeler": "Deterministic formula checks and cohort stress tests",
                        "slide_presenter": "Executive slide narratives and visual outlines",
                        "meeting_dispatcher": "Structured entity extraction and action routing",
                    }),
                    json.dumps({
                        "domain_system": "Internal Observability & Domain Engine",
                        "capability": "Real-time payment transaction routing, anomaly detection, and automated settlement",
                    }),
                    "Hybrid BM25 + Subword LSA Vector Retrieval with Knowledge Graph Expansion",
                    json.dumps(["mcp_github", "mcp_slack", "mcp_sqlite", "mcp_payment_gateway"]),
                    "Dual-gate approval on external or production modifications.",
                    "35-50% cycle time reduction on routine operational deliverables.",
                    json.dumps({"source": "bespoke_onboarding"}),
                ),
            )

            # Upgrade prompt with Section 7
            sec7_text = (
                f"\n\n## 7. Day-to-Day Tooling, GenAI Build Plan & Personal Subagent Swarm Protocol\n\n"
                f"### 7.1 Operational Tooling Stack\n"
                f"The {b_name} commands both horizontal productivity suites (Word, Sheets, Slides, Notes, Chat) "
                f"and specialized vertical domain software to execute operational workflows with maximum fidelity.\n\n"
                f"### 7.2 Personal Subagent Swarm ('Role-in-a-Box')\n"
                f"Equipped with an acyclic 6-agent swarm: Role Chief of Staff, Document Drafter, Quantitative Modeler, "
                f"Deck Presenter, Meeting Graph Subagent, and Quality Critic, coordinated via strict Human-in-the-Loop gates.\n\n"
                f"### 7.3 Generative AI Engineering Blueprint\n"
                f"Leverages hybrid BM25 + subword vector RAG with MCP integrations to automate 35-50% of routine synthesis."
            )
            if "## 7." not in synth_prompt:
                upgraded_prompt = synth_prompt + sec7_text
                cursor.execute(
                    "UPDATE canonical_roles SET system_prompt = ?, character_count = ? WHERE id = ?;",
                    (upgraded_prompt, len(upgraded_prompt), new_role_id),
                )

        self.conn.commit()

        # 7. Generate Blueprint
        default_bp_path = Path("artifacts/company_onboarding") / f"{slug}_genai_blueprint.md"
        final_bp_path = Path(output_blueprint_path or default_bp_path)
        final_bp_path.parent.mkdir(parents=True, exist_ok=True)

        full_company_profile = {
            "name": name,
            "slug": slug,
            "ticker": metadata.get("ticker", "PRIVATE"),
            "is_public": metadata.get("publicly_traded", False),
            "revenue_billions": revenue,
            "headquarters": metadata.get("headquarters", "Global Headquarters"),
            "macro_industry": macro_ind,
            "sub_sector": sub_sector,
            "business_model": model,
            "operating_archetype": archetype,
            "challenges": metadata.get("challenges", []),
            "divisions": divisions,
            "employed_canonical_roles": employed_canonical,
            "bespoke_roles": bespoke_roles,
        }

        EnterpriseGenAIBlueprintGenerator.generate_blueprint(
            company_data=full_company_profile,
            db_conn=self.conn,
            output_path=final_bp_path,
        )

        # 8. Update Skill Catalogs in both skill directories
        self._update_skill_catalogs(name, slug, metadata.get("ticker", "PRIVATE"), macro_ind, revenue, employed_count, bespoke_count, str(final_bp_path))

        # 9. Graph Validation
        is_valid = True
        violations: List[str] = []
        if validate_graph:
            try:
                g = KnowledgeGraphEngine.build_from_db(conn=self.conn)
                report = validate_expansion_invariants(g)
                is_valid = report.is_valid
                violations = [f"{v.invariant_code}: {v.message}" for v in report.violations]
            except Exception as exc:
                is_valid = False
                violations.append(f"Graph validation exception: {exc}")

        return OnboardingResult(
            company_id=company_id,
            company_slug=slug,
            company_name=name,
            rank=rank,
            blueprint_path=str(final_bp_path),
            employed_roles_count=employed_count,
            bespoke_roles_count=bespoke_count,
            is_valid=is_valid,
            violations=violations,
        )

    def _update_skill_catalogs(
        self,
        name: str,
        slug: str,
        ticker: str,
        industry: str,
        revenue: float,
        employed_count: int,
        bespoke_count: int,
        blueprint_path: str,
    ) -> None:
        """Appends the newly onboarded company to catalog files in both skill locations."""
        catalog_entry = (
            f"| `{slug}` | **{name}** | `{ticker}` | {industry} | "
            f"${revenue:.2f}B | {employed_count} roles ({bespoke_count} bespoke) | "
            f"`{blueprint_path}` | `2026-11-09` |\n"
        )

        catalog_paths = [
            Path("/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/.agents/skills/org-company-deep-onboard/references/onboarded_companies.md"),
            Path("/home/pakmingw/.gemini/config/skills/org-company-deep-onboard/references/onboarded_companies.md"),
            Path("artifacts/company_onboarding/onboarded_companies.md"),
        ]

        header = (
            "# Onboarded Enterprises & GenAI Blueprints Catalog\n\n"
            "Authoritative dynamic registry of enterprise corporations onboarded via `CompanyOnboardingEngine`.\n\n"
            "| Slug | Company Name | Ticker | Industry | Revenue | Employed Roles | Blueprint Artifact | Onboarded Date |\n"
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        )

        for cp in catalog_paths:
            try:
                cp.parent.mkdir(parents=True, exist_ok=True)
                if not cp.exists() or cp.stat().st_size == 0:
                    cp.write_text(header + catalog_entry, encoding="utf-8")
                else:
                    content = cp.read_text(encoding="utf-8")
                    if slug not in content:
                        cp.write_text(content.strip() + "\n" + catalog_entry, encoding="utf-8")
            except Exception:
                pass

    def close(self) -> None:
        if self._owns_conn and self.conn:
            self.conn.close()
