"""Markdown formatters for the Nov 2026 Frontier AI Lab & Real-World Join Engine (`orgprompt.frontier.formatter`)."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from orgprompt.frontier.models import (
        CompanyFrontierJoinResult,
        FrontierAILab,
        ProblemFrontierBridgeResult,
        RealWorldToFrontierBridge,
        RoleFrontierJoinResult,
    )


def _esc_dollar(text: str) -> str:
    """Escapes unescaped literal currency dollar signs so KaTeX renders cleanly."""
    return re.sub(r"(?<!\\)\$", r"\\$", text or "")


def _format_bridges_section(bridges: List[RealWorldToFrontierBridge]) -> List[str]:
    lines: List[str] = []
    for b in bridges:
        lines.extend([
            f"### {b.domain_name} (`{b.slug}`)",
            f"- **Real-World Goal**: {_esc_dollar(b.real_world_goal)}",
            f"- **Why Naive LLM Wrappers Fail**: {_esc_dollar(b.why_naive_llm_wrappers_fail)}",
            f"- **Lead Frontier Labs**: {', '.join(b.lead_frontier_labs)}",
            f"- **Frontier Technical Recipe**: {_esc_dollar(b.frontier_technical_recipe)}",
            f"- **Joint Enterprise + Lab Pod Topology**: {_esc_dollar(b.joint_enterprise_lab_pod_topology)}",
            "",
        ])
    return lines


def format_lab_markdown(lab: FrontierAILab) -> str:
    lines = [
        f"# Frontier AI Lab Profile: {lab.name} (`{lab.slug}`)",
        "",
        f"- **Lab ID**: `{lab.id}` | **OKG Company ID**: `{lab.company_id or 'N/A'}`",
        f"- **Headquarters & Hubs**: {_esc_dollar(lab.headquarters)}",
        f"- **Corporate & Fiduciary Structure**: {_esc_dollar(lab.corporate_governance_structure)}",
        "",
        "## Leadership & Technical Architecture Anchors",
        *[f"- {_esc_dollar(ldr)}" for ldr in lab.leadership],
        "",
        "## Research-to-Product Velocity Loop",
        _esc_dollar(lab.research_to_product_loop),
        "",
        "## Flagship Model Families & Agent Runtimes",
        *[f"- {_esc_dollar(m)}" for m in lab.flagship_models],
        "",
        "## Safety, Preparedness & Control Framework",
        _esc_dollar(lab.safety_control_framework),
        "",
        "## Enterprise GTM & Forward-Deployed Engineering (FDE) Motion",
        _esc_dollar(lab.enterprise_gtm_fde_motion),
        "",
        "## Compute & Silicon Co-Design Strategy",
        _esc_dollar(lab.compute_and_infra_strategy),
        "",
        f"## Internal Operating Pods ({len(lab.pods)} Pods)",
        "",
    ]
    for pod in lab.pods:
        lines.extend([
            f"### {pod.name} (`{pod.slug}` | `{pod.pod_category}`)",
            f"- **Mandate**: {_esc_dollar(pod.mandate)}",
            f"- **Canonical Lab Roles**: {', '.join(f'`{r}`' for r in pod.canonical_role_slugs)}",
            f"- **Signature Artifacts**: {', '.join(_esc_dollar(a) for a in pod.signature_artifacts)}",
            f"- **Operating Cadence**: {_esc_dollar(pod.operating_cadence)}",
            "",
        ])
    return "\n".join(lines).strip() + "\n"


def format_role_join_markdown(res: RoleFrontierJoinResult) -> str:
    ctx = f" at **{res.company_name}**" if res.company_name else ""
    lines = [
        f"# Real-World <-> Frontier AI Lab Join: {res.role_title}{ctx}",
        "",
        f"- **Enterprise Role**: `{res.role_slug}` (`{res.role_id}`)",
        f"- **Industry**: {res.industry_name or 'Cross-Industry'} (`{res.industry_id or 'horizontal'}`)",
        f"- **Mission**: {_esc_dollar(res.role_mission)}",
    ]
    if res.personal_subagents:
        lines.append(f"- **6-Agent Personal Swarm**: {', '.join(res.personal_subagents)}")
    lines.extend(["", "## Counterpart Frontier AI Lab Roles & Join Mechanisms", ""])
    for j in res.frontier_joins:
        lines.extend([
            f"### {j.priority_rank}. `{j.target_frontier_role_slug}` — {j.target_frontier_role_title} (`{j.join_mechanism}`)",
            f"- **Enterprise Bottleneck**: {_esc_dollar(j.enterprise_pain_point)}",
            f"- **Frontier Lab Capability**: {_esc_dollar(j.frontier_lab_capability)}",
            f"- **Joint Co-Design Artifact**: {_esc_dollar(j.joint_artifact)}",
            f"- **Recommended Frontier Labs**: {', '.join(j.recommended_labs)}",
            "",
        ])
    if res.matching_bridges:
        lines.extend(["## Matching Cross-Industry Frontier Bridge Blueprints", ""])
        lines.extend(_format_bridges_section(res.matching_bridges))
    return "\n".join(lines).strip() + "\n"


def format_company_join_markdown(res: CompanyFrontierJoinResult) -> str:
    focus_str = f" (Focus: `{res.focus}`)" if res.focus else ""
    lines = [
        f"# Enterprise <-> Frontier AI Lab Co-Design Blueprint: {res.company_name}{focus_str}",
        "",
        f"- **Company**: **{res.company_name}** (`{res.company_slug}` | Rank `{res.rank}` | `{res.industry_name}`)",
        f"- **Employed Canonical Roles**: `{res.employed_roles_count}` | **Active Frontier Join Edges**: `{res.total_frontier_join_edges}`",
        f"- **Lead Recommended Frontier Labs**: {', '.join(f'**{l.name}**' for l in res.lead_frontier_labs)}",
        "",
        "## Top Counterpart Frontier Lab Roles Activated Across the Enterprise",
        "| Frontier Lab Role | Slug | Enterprise Roles Joined |",
        "| :--- | :--- | ---: |",
    ]
    for cp in res.top_frontier_counterparts:
        lines.append(f"| {cp['title']} | `{cp['slug']}` | {cp['joined_enterprise_roles_count']} |")
    lines.extend(["", "## Join Mechanism Distribution", ""])
    for mech, cnt in sorted(res.mechanism_distribution.items(), key=lambda x: -x[1]):
        lines.append(f"- **`{mech}`**: `{cnt}` role-to-lab edges")
    if res.industry_bridges:
        lines.extend(["", "## Industry & Horizontal Frontier Bridge Recipes", ""])
        lines.extend(_format_bridges_section(res.industry_bridges))
    lines.extend(["## Sample Role-Level Frontier Co-Design Joins", ""])
    for j in res.sample_role_joins[:10]:
        lines.append(
            f"- **{j.source_enterprise_role_title}** (`{j.source_enterprise_role_slug}`) -> "
            f"**{j.target_frontier_role_title}** (`{j.target_frontier_role_slug}`) via `{j.join_mechanism}` "
            f"[{', '.join(j.recommended_labs[:2])}]"
        )
    return "\n".join(lines).strip() + "\n"


def format_problem_bridge_markdown(res: ProblemFrontierBridgeResult) -> str:
    ctx = f" ({res.company_name})" if res.company_name else ""
    lines = [
        f"# Problem-to-Frontier-Lab Bridge Synthesis{ctx}",
        "",
        f"> **Problem Statement**: {_esc_dollar(res.problem_statement)}",
        "",
        "## 1. Retrieved Real-World Enterprise / Creator Anchor Roles (Hybrid BM25 + Dense RRF)",
    ]
    for r in res.retrieved_enterprise_roles:
        lines.append(f"- **{r['title']}** (`{r['slug']}`) — RRF `{r['rrf_score']}` ({r['industry'] or 'Horizontal'})")
    lines.extend(["", "## 2. Activated Frontier AI Lab Operating Pods", ""])
    for p in res.activated_frontier_pods:
        lines.append(f"- **{p.name}** (`{p.id}` | `{p.pod_category}`) — {_esc_dollar(p.mandate)}")
    lines.extend(["", "## 3. Recommended Frontier AI Labs", ""])
    for l in res.recommended_labs:
        lines.append(f"- **{l.name}** (`{l.slug}`): {_esc_dollar(l.enterprise_gtm_fde_motion)}")
    if res.matching_bridges:
        lines.extend(["", "## 4. Cross-Industry Frontier Technical Recipes", ""])
        lines.extend(_format_bridges_section(res.matching_bridges))
    lines.extend(["## 5. Joint Enterprise Swarm + Frontier Lab Execution Plan", ""])
    for step in res.co_design_execution_plan:
        lines.append(f"- {_esc_dollar(step)}")
    return "\n".join(lines).strip() + "\n"
