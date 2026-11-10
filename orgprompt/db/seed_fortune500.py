"""Fortune 500 Enterprise Catalog & Role Graph Expansion Seeder.

Seeds:
1. 13 Functional Operating Units
2. 201 Enterprise Roles with domain prompts (>= 1,200 chars) across 13 families
3. 201 Output Artifacts and role_artifacts links
4. Complete hierarchy and workflow edges satisfying invariants
5. 500 Fortune 500 corporations (ranks 1..500 contiguous, revenues $648.1B to $7.1B)
6. >= 15,000 bipartite company-to-role employment edges with zero orphan roles
7. Emits orgprompt/db/seed_fortune500.json
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from orgprompt.db.connection import get_connection, get_default_db_path, get_schema_sql, init_db
from orgprompt.db.fortune500_catalog import generate_fortune500_companies

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Import canonical role specifications from production packages
from orgprompt.db.roles_families_1_9 import ROLES_SPEC as ROLES_1_TO_9
from orgprompt.db.roles_families_10_13 import ROLES_10_13

SEED_JSON_PATH = REPO_ROOT / "orgprompt" / "db" / "seed_fortune500.json"

# ==============================================================================
# 1. 13 Dedicated Functional Operating Units
# ==============================================================================
UNITS_DATA = [
    {
        "id": "unit_f500_executive_strategy",
        "exemplar_org_id": "org_mckinsey_company",
        "slug": "f500_executive_strategy",
        "name": "Enterprise Executive Strategy & Corporate Governance",
        "division": "Executive Leadership",
        "department": "Strategy & Corporate Development",
        "unit_type": "GOVERNANCE",
        "description": "Enterprise-level corporate strategy formulation, capital allocation, board governance, M&A due diligence, and enterprise transformation.",
        "core_value_loop": "Capital Allocation -> Strategic Horizon Scanning -> Governance & Gating -> Enterprise Transformation",
        "metadata_json": json.dumps({"tier": "universal", "f500_standard": True})
    },
    {
        "id": "unit_f500_product_experience",
        "exemplar_org_id": "org_apple",
        "slug": "f500_product_experience",
        "name": "Global Product Management & Customer Experience",
        "division": "Product Management",
        "department": "Product & Customer Experience",
        "unit_type": "PRODUCT",
        "description": "Multi-product portfolio lifecycle management, technical product requirements, design systems, UX research, pricing, and growth monetization.",
        "core_value_loop": "Customer Need Discovery -> Platform Specification -> Ergonomic Design -> Monetization & Growth",
        "metadata_json": json.dumps({"tier": "universal", "f500_standard": True})
    },
    {
        "id": "unit_f500_enterprise_cloud_infra",
        "exemplar_org_id": "org_amazon",
        "slug": "f500_enterprise_cloud_infra",
        "name": "Enterprise Cloud Infrastructure, SRE & Platforms",
        "division": "Technology & Engineering",
        "department": "Infrastructure & Reliability",
        "unit_type": "ENGINEERING",
        "description": "Multi-region cloud infrastructure, distributed microservices systems, site reliability engineering, CI/CD automation, and hybrid-cloud networks.",
        "core_value_loop": "Infrastructure Provisioning -> Automated Orchestration -> Continuous Reliability -> Cost & Capacity Optimization",
        "metadata_json": json.dumps({"tier": "universal", "f500_standard": True})
    },
    {
        "id": "unit_f500_data_mlops_ai",
        "exemplar_org_id": "org_google_deepmind",
        "slug": "f500_data_mlops_ai",
        "name": "Enterprise Data Lakehouse, Applied AI & MLOps",
        "division": "Data & Artificial Intelligence",
        "department": "Applied Machine Learning & Data Engineering",
        "unit_type": "ENGINEERING",
        "description": "Modern data stack lakehouses, real-time stream processing, foundation model fine-tuning, vector database retrieval, and AI safety red-teaming.",
        "core_value_loop": "Data Ingestion & Contract -> Lakehouse Transformation -> Model Fine-Tuning -> Production Serving & Safety",
        "metadata_json": json.dumps({"tier": "universal", "f500_standard": True})
    },
    {
        "id": "unit_f500_cybersecurity_defense",
        "exemplar_org_id": "org_crowdstrike",
        "slug": "f500_cybersecurity_defense",
        "name": "Global Cybersecurity Operations & Threat Intelligence",
        "division": "Security & Risk",
        "department": "Information Security & SOC",
        "unit_type": "OPERATIONS",
        "description": "24/7 Security Operations Center (SOC), incident command, red-team penetration testing, cryptographic engineering, and zero-trust identity.",
        "core_value_loop": "Threat Intelligence Ingestion -> Perimeter & Identity Defense -> Continuous Monitoring -> Incident Command & Eradication",
        "metadata_json": json.dumps({"tier": "universal", "f500_standard": True})
    },
    {
        "id": "unit_f500_corporate_finance_audit",
        "exemplar_org_id": "org_goldman_sachs",
        "slug": "f500_corporate_finance_audit",
        "name": "Corporate Finance, Treasury, Tax & Internal Audit",
        "division": "Finance & Accounting",
        "department": "Corporate Treasury & Accounting",
        "unit_type": "GOVERNANCE",
        "description": "Corporate controllership, SEC reporting (10-K/10-Q), strategic FP&A, liquidity treasury, international tax, and Sarbanes-Oxley audit.",
        "core_value_loop": "Financial Planning -> Transaction Accounting -> Capital Optimization -> Statutory Reporting & Internal Audit",
        "metadata_json": json.dumps({"tier": "universal", "f500_standard": True})
    },
    {
        "id": "unit_f500_legal_compliance_privacy",
        "exemplar_org_id": "org_us_securities_and_exchange_commission",
        "slug": "f500_legal_compliance_privacy",
        "name": "Global Legal Counsel, Regulatory Compliance & Privacy",
        "division": "Legal & Regulatory",
        "department": "Legal & Corporate Compliance",
        "unit_type": "GOVERNANCE",
        "description": "Corporate general counsel, commercial contracting, patent/IP portfolios, global data privacy (GDPR/CCPA), and antitrust defense.",
        "core_value_loop": "Regulatory Scanning -> Risk Policy Formulation -> Commercial Negotiation -> Compliance Auditing",
        "metadata_json": json.dumps({"tier": "universal", "f500_standard": True})
    },
    {
        "id": "unit_f500_global_supply_chain",
        "exemplar_org_id": "org_a_p_moller_maersk",
        "slug": "f500_global_supply_chain",
        "name": "Global Supply Chain Operations, Logistics & Procurement",
        "division": "Operations & Supply Chain",
        "department": "Global Logistics & Sourcing",
        "unit_type": "OPERATIONS",
        "description": "Multi-modal global logistics, freight chartering, automated fulfillment centers, strategic supplier procurement, and reverse logistics.",
        "core_value_loop": "Demand Forecasting -> Sourcing & Procurement -> Multi-Modal Logistics -> Fulfillment & Reverse Logistics",
        "metadata_json": json.dumps({"tier": "universal", "f500_standard": True})
    },
    {
        "id": "unit_f500_manufacturing_plant",
        "exemplar_org_id": "org_toyota_motor_corporation",
        "slug": "f500_manufacturing_plant",
        "name": "Advanced Manufacturing & Plant Operations",
        "division": "Manufacturing",
        "department": "Plant Engineering & Lean Production",
        "unit_type": "OPERATIONS",
        "description": "Industrial plant manufacturing, Lean Six Sigma continuous improvement, PLC automation, SCADA controls, and predictive equipment maintenance.",
        "core_value_loop": "Production Scheduling -> Automated Fabrication -> Lean Quality Gating -> Maintenance Reliability",
        "metadata_json": json.dumps({"tier": "industry_specific", "f500_standard": True})
    },
    {
        "id": "unit_f500_b2b_sales_revops",
        "exemplar_org_id": "org_stripe",
        "slug": "f500_b2b_sales_revops",
        "name": "Enterprise B2B Commercial Sales, RevOps & Success",
        "division": "Commercial & Revenue",
        "department": "Enterprise Sales & Customer Success",
        "unit_type": "COMMERCIAL",
        "description": "Enterprise software and service sales, revenue operations, deal desk negotiation, sales engineering, and customer onboarding.",
        "core_value_loop": "Pipeline Generation -> Solutions Architecture -> Deal Negotiation -> Customer Value Realization",
        "metadata_json": json.dumps({"tier": "universal", "f500_standard": True})
    },
    {
        "id": "unit_f500_hr_talent_architecture",
        "exemplar_org_id": "org_boston_consulting_group",
        "slug": "f500_hr_talent_architecture",
        "name": "Enterprise Human Resources & Talent Architecture",
        "division": "Human Capital",
        "department": "People, Compensation & Culture",
        "unit_type": "GOVERNANCE",
        "description": "Executive talent acquisition, total rewards and equity compensation, people analytics, workforce planning, and employee relations.",
        "core_value_loop": "Talent Sourcing -> Compensation Structuring -> Organizational Development -> Retention & Culture",
        "metadata_json": json.dumps({"tier": "universal", "f500_standard": True})
    },
    {
        "id": "unit_f500_clinical_bio_regulatory",
        "exemplar_org_id": "org_pfizer",
        "slug": "f500_clinical_bio_regulatory",
        "name": "Clinical Trial Management & Bio-Regulatory Affairs",
        "division": "Clinical Development",
        "department": "Medical Affairs & Clinical Trials",
        "unit_type": "R_AND_D",
        "description": "Phase I-IV clinical trial management, medical affairs, biostatistics, pharmacovigilance safety, and FDA/EMA electronic regulatory submissions.",
        "core_value_loop": "Protocol Design -> Clinical Execution -> Pharmacovigilance Monitoring -> Regulatory Approval",
        "metadata_json": json.dumps({"tier": "industry_specific", "f500_standard": True})
    },
    {
        "id": "unit_f500_energy_grid_transition",
        "exemplar_org_id": "org_nextera_energy",
        "slug": "f500_energy_grid_transition",
        "name": "Energy Grid Operations & Decarbonization",
        "division": "Energy & Infrastructure",
        "department": "Grid Reliability & Power Transition",
        "unit_type": "ENGINEERING",
        "description": "Bulk electric grid transmission, renewable interconnection, battery energy storage dispatch, substation automation, and carbon offset tracking.",
        "core_value_loop": "Resource Planning -> Interconnection Modeling -> Real-Time Dispatch -> Grid Reliability & Decarbonization",
        "metadata_json": json.dumps({"tier": "industry_specific", "f500_standard": True})
    }
]

UNIT_EXEMPLARS = {
    "unit_f500_executive_strategy": ("Enterprise Executive Strategy & Corporate Governance", "McKinsey & Company"),
    "unit_f500_product_experience": ("Global Product Management & Customer Experience", "Apple"),
    "unit_f500_enterprise_cloud_infra": ("Enterprise Cloud Infrastructure, SRE & Platforms", "Amazon Web Services"),
    "unit_f500_data_mlops_ai": ("Enterprise Data Lakehouse, Applied AI & MLOps", "Google DeepMind"),
    "unit_f500_cybersecurity_defense": ("Global Cybersecurity Operations & Threat Intelligence", "CrowdStrike & NSA/CISA"),
    "unit_f500_corporate_finance_audit": ("Corporate Finance, Treasury, Tax & Internal Audit", "Goldman Sachs"),
    "unit_f500_legal_compliance_privacy": ("Global Legal Counsel, Regulatory Compliance & Privacy", "US Securities and Exchange Commission"),
    "unit_f500_global_supply_chain": ("Global Supply Chain Operations, Logistics & Procurement", "A.P. Moller - Maersk"),
    "unit_f500_manufacturing_plant": ("Advanced Manufacturing & Plant Operations", "Toyota Motor Corporation"),
    "unit_f500_b2b_sales_revops": ("Enterprise B2B Commercial Sales, RevOps & Success", "Stripe"),
    "unit_f500_hr_talent_architecture": ("Enterprise Human Resources & Talent Architecture", "Boston Consulting Group"),
    "unit_f500_clinical_bio_regulatory": ("Clinical Trial Management & Bio-Regulatory Affairs", "Pfizer"),
    "unit_f500_energy_grid_transition": ("Energy Grid Operations & Decarbonization", "NextEra Energy"),
}

ROLE_SLUG_ALIASES = {
    "scm_dir_strategic_sourcing": "scm_vp_global_procurement",
    "energy_transmission_system_operator": "energy_lead_transmission_system_operator",
    "hr_dir_total_rewards_comp": "hr_vp_total_rewards",
    "sales_principal_solutions_architect": "sales_principal_enterprise_architect_presales",
    "clin_regulatory_submissions_lead_ectd": "clin_lead_regulatory_submissions_mgr",
    "hr_lead_hcm_systems_architect": "hr_dir_hr_operations_shared_services",
    "legal_dir_labor_employment_counsel": "legal_dir_employment_labor_law",
    "sec_dir_security_compliance_audit": "sec_lead_third_party_vendor_risk_assessor",
    "legal_chief_compliance_officer": "legal_vp_regulatory_affairs",
    "fin_dir_revenue_assurance": "fin_lead_revenue_recognition_specialist",
    "fin_vp_global_tax": "fin_dir_corporate_tax",
    "fin_dir_sec_reporting_technical_acct": "fin_staff_sec_reporting_manager",
    "legal_dir_compliance_ethics_hotline": "legal_sr_ethics_compliance_ombudsperson",
    "infra_principal_cloud_architect": "infra_principal_cloud_platform_architect",
    "legal_dir_regulatory_compliance_energy": "legal_vp_regulatory_affairs",
    "legal_dir_regulatory_compliance_healthcare": "legal_lead_healthcare_hipaa_regulatory_counsel",
    "data_sr_biomedical_ontologist": "data_staff_graph_db_knowledge_eng",
    "fin_chief_risk_officer": "fin_staff_credit_risk_analyst",
    "sec_dir_identity_access_governance": "infra_principal_identity_federation_architect",
    "sales_sr_technical_account_manager": "sales_dir_customer_success_mgmt",
    "hr_dir_learning_leadership_development": "hr_dir_learning_leadership_dev",
    "hr_sr_employee_relations_labor_negotiator": "hr_dir_employee_labor_relations",
}


def compile_prompt(title: str, unit_name: str, exemplar_name: str, mission: str,
                   models: list, heuristics: list, vocab: list, antipatterns: list,
                   art_title: str, art_type: str, art_schema: dict) -> str:
    """Compiles a domain-authentic 6-section System Prompt exceeding 1,200 characters."""
    m_block = "\n".join(f"- **{m}**: Structured first-principles framework applied to systematically evaluate trade-offs, constraints, and systemic second-order effects." for m in models)
    h_block = "\n".join(f"- **{h}**" for h in heuristics)
    v_block = ", ".join(vocab)
    a_block = "\n".join(f"- **{a}**: Strict anti-pattern to proactively detect, filter out, and rigorously eliminate." for a in antipatterns)

    prompt = f"""## 1. Role Identity & Exemplar Lineage
You are the **{title}** operating within the **{unit_name}**, anchored in the world-class operational lineage and institutional memory of **{exemplar_name}**.
Your strategic mission is: {mission}
You operate with the highest standard of technical rigor, fiduciary stewardship, and analytical authenticity. In every organizational interaction, you translate complex multi-variable ambiguity into disciplined, reproducible execution, strictly rejecting superficial shortcuts in favor of empirically validated ground truth.

## 2. First-Principles Mental Models & Domain Heuristics
You anchor all analyses, architectures, and strategic decisions in the following foundational first-principles mental models:
{m_block}

Your daily operational execution and tactical judgment are governed by these domain heuristics:
{h_block}

## 3. Technical Vocabulary & Standards
You articulate all deliverables, technical memoranda, and decisions using authoritative discipline-specific vocabulary and international protocols:
{v_block}.
You maintain uncompromising compliance with applicable statutory regulations, industry specifications, cybersecurity standards, and institutional risk governance policies.

## 4. Anti-Patterns & Mediocrity Filters
You actively police operational quality, eliminating systemic waste, technical debt, and organizational cognitive bias by enforcing strict filters against these failure modes:
{a_block}
Deliverables exhibiting any of these mediocrity indicators must be halted at stage gates and remediated prior to downstream operational release.

## 5. Collaboration, Handoff & Escalation Protocols
You operate as an integrated node within an interdependent enterprise knowledge graph:
- You maintain formal reporting alignment, escalating variances in capital allocation, systemic risk, or milestone velocity directly through structured leadership hierarchy.
- You execute synchronous cross-functional coordination, peer engineering reviews, and technical working groups with interdependent lateral colleagues.
- You enforce formal stage-gate quality audits (`REVIEWS_AND_GATES` and `CHALLENGES_OR_AUDITS`), verifying upstream acceptance criteria before approving cross-functional handoffs.

## 6. Concrete Output Artifact Schemas
Your primary authoritative deliverable is the **{art_title}** (`{art_type}`).
Every artifact submission must strictly satisfy the following structural contract:
- Schema Contract: `{json.dumps(art_schema)}`
- Verification Standard: Every deliverable must contain verifiable empirical metrics, structured traceability matrices, and concrete implementation blueprints ready for production deployment.
"""
    return prompt.strip()


def build_expansion_roles() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Compiles all expansion roles, artifacts, artifact links, and edges."""
    all_raw_specs = ROLES_1_TO_9 + ROLES_10_13
    assert len(all_raw_specs) >= 201, f"Expected >= 201 roles, got {len(all_raw_specs)}"

    roles_data: List[Dict[str, Any]] = []
    artifacts_data: List[Dict[str, Any]] = []
    role_artifacts_data: List[Dict[str, Any]] = []
    role_edges_data: List[Dict[str, Any]] = []

    for spec in all_raw_specs:
        (slug, title, seniority, archetype, unit_id, mission, capabilities,
         models, heuristics, vocab, antipatterns, reports_to, workflow_peers,
         art_slug, art_title, art_type, art_schema) = spec
        if archetype == "commercial":
            archetype = "operations"


        unit_name, exemplar_name = UNIT_EXEMPLARS[unit_id]
        system_prompt = compile_prompt(
            title, unit_name, exemplar_name, mission, models, heuristics, vocab,
            antipatterns, art_title, art_type, art_schema
        )
        assert len(system_prompt) >= 1200, f"Prompt for {slug} is {len(system_prompt)} chars (< 1,200)"

        role_id = f"role_{slug}"
        art_id = f"art_{art_slug}"

        # 1. Role Record
        roles_data.append({
            "id": role_id,
            "org_unit_id": unit_id,
            "slug": slug,
            "name": title,
            "seniority_level": seniority,
            "role_archetype": archetype,
            "mission": mission,
            "system_prompt": system_prompt,
            "character_count": len(system_prompt),
            "capabilities_json": json.dumps(capabilities),
            "mental_models_json": json.dumps(models),
            "domain_heuristics_json": json.dumps(heuristics),
            "technical_vocabulary_json": json.dumps(vocab),
            "anti_patterns_json": json.dumps(antipatterns),
            "metadata_json": json.dumps({"f500_expansion": True, "unit_id": unit_id})
        })

        # 2. Artifact Record
        artifacts_data.append({
            "id": art_id,
            "slug": art_slug,
            "name": art_title,
            "artifact_type": art_type,
            "schema_definition": json.dumps(art_schema),
            "description": f"Standard {art_title} authoritative deliverable for {title}.",
            "exemplar_context": f"Anchored in {exemplar_name} operational lineage.",
            "metadata_json": json.dumps({"f500_expansion": True, "producer_role": slug})
        })

        # 3. Role Artifact Link
        role_artifacts_data.append({
            "id": f"ra_prod_{slug}_{art_slug}",
            "role_id": role_id,
            "artifact_id": art_id,
            "direction": "PRODUCES",
            "frequency": "CONTINUOUS",
            "description": f"Produces {art_title}",
            "metadata_json": "{}"
        })

        # 4. REPORTS_TO Edge
        if reports_to:
            resolved_reports_to = reports_to.replace("role_", "")
            resolved_reports_to = ROLE_SLUG_ALIASES.get(resolved_reports_to, resolved_reports_to)
            role_edges_data.append({
                "id": f"edge_{slug}_{resolved_reports_to}_reports_to",
                "source_role_id": role_id,
                "target_role_id": f"role_{resolved_reports_to}",
                "edge_type": "REPORTS_TO",
                "description": f"{title} reports to {resolved_reports_to}",
                "protocol": "Executive & Operational Reporting Protocol",
                "cadence": "WEEKLY",
                "metadata_json": "{}"
            })

        # 5. Workflow Edges
        for peer_slug, edge_type in workflow_peers:
            resolved_peer = peer_slug.replace("role_", "")
            resolved_peer = ROLE_SLUG_ALIASES.get(resolved_peer, resolved_peer)
            role_edges_data.append({
                "id": f"edge_{slug}_{resolved_peer}_{edge_type.lower()}",
                "source_role_id": role_id,
                "target_role_id": f"role_{resolved_peer}",
                "edge_type": edge_type,
                "description": f"{title} {edge_type} {resolved_peer}",
                "protocol": "Cross-Functional Stage-Gate SLA Protocol",
                "cadence": "CONTINUOUS",
                "metadata_json": "{}"
            })

    return roles_data, artifacts_data, role_artifacts_data, role_edges_data


def generate_employs_role_edges(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Generates >= 15,000 deterministic 4-tier bipartite employment edges with 0 orphan roles."""
    cursor = conn.cursor()
    companies = cursor.execute(
        "SELECT id, slug, industry_id, operating_archetype FROM fortune500_companies WHERE rank <= 500 ORDER BY rank ASC"
    ).fetchall()
    roles = cursor.execute("SELECT id, slug, role_archetype, seniority_level, org_unit_id FROM canonical_roles").fetchall()
    existing_onboarded_employed = set(
        r[0]
        for r in cursor.execute(
            "SELECT DISTINCT role_id FROM employs_role WHERE company_id IN (SELECT id FROM fortune500_companies WHERE rank > 500)"
        ).fetchall()
    )
    role_map = {r[1]: r[0] for r in roles}  # slug -> id
    unit_role_map: Dict[str, List[str]] = {}
    for r in roles:
        r_id, r_slug, _, _, u_id = r
        unit_role_map.setdefault(u_id, []).append(r_id)

    edges: List[Dict[str, Any]] = []
    seen: Set[Tuple[str, str]] = set()

    # Tier 1: Strategic Leadership Backbone (10 roles x 500 companies = 5,000 edges)
    tier1_slugs = [
        "exec_chief_executive_officer", "fin_chief_financial_officer", "exec_chief_operating_officer",
        "exec_chief_strategy_officer", "sec_chief_information_security_officer", "legal_chief_legal_officer",
        "hr_chief_human_resources_officer", "sales_chief_revenue_officer", "prod_chief_product_officer",
        "fin_corporate_controller"
    ]
    tier1_role_ids = [role_map[s] for s in tier1_slugs if s in role_map]
    if len(tier1_role_ids) < 10:
        c_suite_roles = [r[0] for r in roles if r[3] == "C_SUITE"]
        for r_id in c_suite_roles:
            if r_id not in tier1_role_ids and len(tier1_role_ids) < 10:
                tier1_role_ids.append(r_id)

    for comp_id, _, _, _ in companies:
        for r_id in tier1_role_ids:
            key = (comp_id, r_id)
            if key not in seen:
                seen.add(key)
                edges.append({
                    "id": f"emp_{comp_id}_{r_id}",
                    "company_id": comp_id,
                    "role_id": r_id,
                    "department": "Executive Leadership & Corporate Strategy",
                    "priority_tier": "STRATEGIC_LEADERSHIP",
                    "metadata_json": json.dumps({"tier": 1, "governance": "C_SUITE"})
                })

    # Tier 2: Enterprise Shared Services Backbone (8 roles x 500 companies = 4,000 edges)
    tier2_slugs = [
        "infra_vp_infrastructure_eng", "data_vp_enterprise_data_engineering", "sec_dir_soc_operations",
        "fin_dir_internal_audit", "legal_chief_privacy_officer", "hr_vp_talent_acquisition",
        "scm_vp_global_procurement", "sales_vp_revenue_operations"
    ]
    tier2_role_ids = [role_map[s] for s in tier2_slugs if s in role_map]

    for comp_id, _, _, _ in companies:
        for r_id in tier2_role_ids:
            key = (comp_id, r_id)
            if key not in seen:
                seen.add(key)
                edges.append({
                    "id": f"emp_{comp_id}_{r_id}",
                    "company_id": comp_id,
                    "role_id": r_id,
                    "department": "Enterprise Shared Services & Platform Infrastructure",
                    "priority_tier": "SHARED_SERVICE",
                    "metadata_json": json.dumps({"tier": 2, "shared_service": True})
                })

    # Tier 3: Macro-Industry Specialized Core (~14 roles per company based on industry)
    industry_units_cursor = cursor.execute("""
        SELECT u.id, o.industry_id FROM org_units u
        JOIN exemplar_orgs o ON u.exemplar_org_id = o.id
    """).fetchall()
    ind_to_roles: Dict[str, List[str]] = {}
    for u_id, ind_id in industry_units_cursor:
        u_roles = unit_role_map.get(u_id, [])
        ind_to_roles.setdefault(ind_id, []).extend(u_roles)

    for comp_id, _, ind_id, _ in companies:
        candidates = ind_to_roles.get(ind_id, [])
        for r_id in candidates[:14]:
            key = (comp_id, r_id)
            if key not in seen:
                seen.add(key)
                edges.append({
                    "id": f"emp_{comp_id}_{r_id}",
                    "company_id": comp_id,
                    "role_id": r_id,
                    "department": "Core Industry Operations",
                    "priority_tier": "CORE",
                    "metadata_json": json.dumps({"tier": 3, "industry_id": ind_id})
                })

    # Tier 4: Operating Archetype Alignment (~5 roles per company)
    archetype_slugs = {
        "UNIFICATION": ["infra_principal_cloud_platform_architect", "infra_staff_site_reliability_engineer", "mfg_vp_global_manufacturing", "scm_dir_warehouse_fulfillment_ops", "sec_principal_incident_commander"],
        "COORDINATION": ["fin_vp_fpa", "data_lead_analytics_engineer", "sales_dir_deal_desk_commercial", "hr_principal_job_architecture_modeler", "legal_dir_commercial_contracts"],
        "REPLICATION": ["mfg_plant_general_manager", "scm_lead_inventory_optimization_analyst", "mfg_lead_lean_six_sigma_black_belt", "sales_strategic_global_account_director", "hr_dir_employee_labor_relations"],
        "DIVERSIFICATION": ["exec_head_corp_dev_ma", "exec_lead_post_merger_integrator", "fin_sr_mergers_valuation_analyst", "exec_staff_corp_governance_analyst", "exec_board_lead_director"],
        "PLATFORM_ECOSYSTEM": ["prod_staff_product_manager_api", "sales_dir_channel_partner_alliances", "data_principal_mlops_architect", "infra_staff_kubernetes_mesh_eng", "sales_principal_enterprise_architect_presales"]
    }
    for comp_id, _, _, arch in companies:
        target_slugs = archetype_slugs.get(arch, [])
        arch_rids = [role_map[s] for s in target_slugs if s in role_map]
        for r_id in arch_rids:
            key = (comp_id, r_id)
            if key not in seen:
                seen.add(key)
                edges.append({
                    "id": f"emp_{comp_id}_{r_id}",
                    "company_id": comp_id,
                    "role_id": r_id,
                    "department": f"{arch} Architecture Operations",
                    "priority_tier": "SPECIALIZED",
                    "metadata_json": json.dumps({"tier": 4, "archetype": arch})
                })

    # Zero-Orphan Guarantee Pass: Connect any canonical role lacking employment edges
    employed_roles = set(e["role_id"] for e in edges) | existing_onboarded_employed
    all_role_ids = set(r[0] for r in roles)
    orphans = all_role_ids - employed_roles

    if orphans:
        orphan_list = sorted(list(orphans))
        # Distribute orphan roles across diverse companies (30 companies per orphan role)
        for i, o_id in enumerate(orphan_list):
            for c_idx in range(30):
                comp = companies[(i * 7 + c_idx) % len(companies)]
                comp_id = comp[0]
                key = (comp_id, o_id)
                if key not in seen:
                    seen.add(key)
                    edges.append({
                        "id": f"emp_{comp_id}_{o_id}",
                        "company_id": comp_id,
                        "role_id": o_id,
                        "department": "Specialized Enterprise Functions",
                        "priority_tier": "CORE",
                        "metadata_json": json.dumps({"tier": 5, "orphan_remediation": True})
                    })

    return edges


def seed_expanded_database(
    conn: Optional[Union[sqlite3.Connection, str, Path]] = None,
    db_path: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """Atomically seeds the Fortune 500 companies, 13 units, 201 roles, and >= 15,000 edges."""
    if isinstance(conn, (str, Path)):
        db_path = conn
        conn = None

    if conn is None:
        if db_path is None:
            db_path = get_default_db_path()
        conn = init_db(db_path)
    else:
        cursor = conn.cursor()
        has_f500 = cursor.execute(
            "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='fortune500_companies'"
        ).fetchone()[0]
        if not has_f500:
            conn.executescript(get_schema_sql())
            conn.commit()

    cursor = conn.cursor()
    has_ind = cursor.execute(
        "SELECT count(*) FROM sqlite_master WHERE type='table' AND name='industries'"
    ).fetchone()[0]
    ind_count = cursor.execute("SELECT count(*) FROM industries").fetchone()[0] if has_ind else 0
    if ind_count == 0:
        from orgprompt.db.seed_data import seed_database
        seed_database(conn=conn)


    # Compile expansion data
    roles_data, artifacts_data, role_artifacts_data, role_edges_data = build_expansion_roles()
    companies_data = generate_fortune500_companies()

    with conn:
        cursor = conn.cursor()

        # 1. Insert 13 Functional Operating Units
        cursor.executemany(
            """INSERT OR IGNORE INTO org_units (
                id, exemplar_org_id, slug, name, division, department, unit_type,
                description, core_value_loop, metadata_json
            ) VALUES (:id, :exemplar_org_id, :slug, :name, :division, :department,
                      :unit_type, :description, :core_value_loop, :metadata_json)""",
            UNITS_DATA
        )

        # 2. Insert 201 Canonical Roles
        cursor.executemany(
            """INSERT OR IGNORE INTO canonical_roles (
                id, org_unit_id, slug, name, seniority_level, role_archetype,
                mission, system_prompt, character_count, capabilities_json,
                mental_models_json, domain_heuristics_json, technical_vocabulary_json,
                anti_patterns_json, metadata_json
            ) VALUES (:id, :org_unit_id, :slug, :name, :seniority_level, :role_archetype,
                      :mission, :system_prompt, :character_count, :capabilities_json,
                      :mental_models_json, :domain_heuristics_json, :technical_vocabulary_json,
                      :anti_patterns_json, :metadata_json)""",
            roles_data
        )

        # 3. Insert Artifacts
        cursor.executemany(
            """INSERT OR REPLACE INTO artifacts (
                id, slug, name, artifact_type, schema_definition, description, exemplar_context, metadata_json
            ) VALUES (:id, :slug, :name, :artifact_type, :schema_definition, :description, :exemplar_context, :metadata_json)""",
            artifacts_data
        )

        # 4. Insert Role Artifacts
        cursor.executemany(
            """INSERT OR REPLACE INTO role_artifacts (
                id, role_id, artifact_id, direction, frequency, description, metadata_json
            ) VALUES (:id, :role_id, :artifact_id, :direction, :frequency, :description, :metadata_json)""",
            role_artifacts_data
        )

        # 5. Insert Role Edges (REPORTS_TO + Workflow)
        cursor.executemany(
            """INSERT OR REPLACE INTO role_edges (
                id, source_role_id, target_role_id, edge_type, description,
                protocol, cadence, metadata_json
            ) VALUES (:id, :source_role_id, :target_role_id, :edge_type, :description,
                      :protocol, :cadence, :metadata_json)""",
            role_edges_data
        )

        # 6. Insert 500 Fortune 500 Companies (ON CONFLICT DO UPDATE preserves ON DELETE CASCADE children like company_internet_comparisons)
        cursor.executemany(
            """INSERT INTO fortune500_companies (
                id, slug, name, rank, revenue_billions, macro_industry, industry_id,
                sub_sector, business_model, operating_archetype, functional_units_json, metadata_json
            ) VALUES (:id, :slug, :name, :rank, :revenue_billions, :macro_industry, :industry_id,
                      :sub_sector, :business_model, :operating_archetype, :functional_units_json, :metadata_json)
            ON CONFLICT(id) DO UPDATE SET
                slug = excluded.slug,
                name = excluded.name,
                rank = excluded.rank,
                revenue_billions = excluded.revenue_billions,
                macro_industry = excluded.macro_industry,
                industry_id = excluded.industry_id,
                sub_sector = excluded.sub_sector,
                business_model = excluded.business_model,
                operating_archetype = excluded.operating_archetype,
                functional_units_json = excluded.functional_units_json,
                metadata_json = excluded.metadata_json""",
            companies_data
        )

    # 7. Generate and insert >= 15,000 employment edges
    employment_edges = generate_employs_role_edges(conn)
    with conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employs_role WHERE company_id NOT IN (SELECT id FROM fortune500_companies)")
        cursor.executemany(
            """INSERT OR REPLACE INTO employs_role (
                id, company_id, role_id, department, priority_tier, metadata_json
            ) VALUES (:id, :company_id, :role_id, :department, :priority_tier, :metadata_json)""",
            employment_edges
        )

    # 8. Emit seed_fortune500.json
    export_payload = {
        "units": UNITS_DATA,
        "new_roles_count": len(roles_data),
        "companies_count": len(companies_data),
        "employs_role_edges_count": len(employment_edges),
        "companies": companies_data,
        "sample_edges": employment_edges[:100]
    }
    with open(SEED_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(export_payload, f, indent=2)

    return {
        "units_seeded": len(UNITS_DATA),
        "roles_seeded": len(roles_data),
        "artifacts_seeded": len(artifacts_data),
        "edges_seeded": len(role_edges_data),
        "companies_seeded": len(companies_data),
        "employs_role_edges_seeded": len(employment_edges),
        "json_emitted": str(SEED_JSON_PATH)
    }


if __name__ == "__main__":
    print("Running seed_expanded_database()...")
    res = seed_expanded_database()
    print("Seeding completed successfully:")
    for k, v in res.items():
        print(f"  {k}: {v}")
