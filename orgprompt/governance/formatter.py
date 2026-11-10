"""Markdown and JSON formatters for `orgprompt.governance` artifacts and CLI output."""

from __future__ import annotations

import json
from typing import List

from orgprompt.governance.models import (
    BoardSlateRecommendation,
    GovernanceRole,
    SuperhumanGovernancePackage,
)


def format_governance_role_markdown(role: GovernanceRole) -> str:
    """Formats a single `GovernanceRole` into a comprehensive Markdown dossier."""
    lines: List[str] = [
        f"# {role.title}",
        "",
        f"- **Role ID / Slug**: `{role.id}` / `{role.slug}`",
        f"- **Fiduciary Category**: `{role.governance_category}`",
        f"- **Committee / Assurance Seat**: {role.committee_type}",
        f"- **Selected Industries**: {', '.join(role.selected_industries) if role.selected_industries else 'Universal Cross-Industry'}",
        f"- **Prompt Length**: `{len(role.system_prompt):,}` characters",
        "",
        "## Typical Human Background & Credentials",
        role.typical_human_background,
        "",
        "## Fiduciary Mandate & Shareholder Duty",
        role.fiduciary_mandate,
        "",
        "## Quarterly Board / Audit Review Cadence",
    ]
    for step in role.quarterly_review_cadence:
        lines.append(f"- {step}")

    lines.extend(["", "## KPI Value Tree & Capital-Allocation Drivers"])
    for k, v in role.kpi_value_tree.items():
        if isinstance(v, list):
            lines.append(f"- **{k}**: {'; '.join(str(x) for x in v)}")
        else:
            lines.append(f"- **{k}**: {v}")

    lines.extend(["", "## Forensic Red-Flag Triggers"])
    for rf in role.red_flag_triggers:
        lines.append(f"- {rf}")

    lines.extend(["", "## Management Oversight Counterparties (`canonical_roles`)"])
    for tgt in role.oversight_targets:
        lines.append(f"- `{tgt}`")

    lines.extend([
        "",
        "---",
        "",
        "## 7-Section Fiduciary Governance / Audit System Prompt",
        "",
        "```markdown",
        role.system_prompt,
        "```",
        "",
    ])
    return "\n".join(lines)


def format_board_slate_markdown(slate: BoardSlateRecommendation) -> str:
    """Formats an industry- or company-tailored Board & Audit Slate as Markdown."""
    header_target = slate.company_name or slate.industry_name
    lines: List[str] = [
        f"# Fiduciary Board of Directors & Independent Audit Slate: {header_target}",
        "",
        f"- **Resolved Industry**: {slate.industry_name} (`{slate.industry_slug}`)",
        f"- **Company Stage**: `{slate.company_stage}`",
        f"- **Recommended Voting Board Size**: `{slate.board_size}` Directors + `{len(slate.external_auditors)}` Independent External Auditors",
        "",
        "## Board & Audit Charter Summary",
        slate.charter_summary,
        "",
        "## Recommended Board of Directors Seats (`BOARD_DIRECTOR`)",
    ]
    for idx, d in enumerate(slate.board_directors, 1):
        lines.append(
            f"{idx}. **{d.title}** (`{d.slug}`) — *{d.committee_type}*\n"
            f"   - **Mandate**: {d.fiduciary_mandate}\n"
            f"   - **Management Counterparties**: {', '.join(f'`{t}`' for t in d.oversight_targets)}"
        )

    lines.extend(["", "## Independent External & Domain Assurance Panel (`INDEPENDENT_AUDITOR`)"])
    for idx, a in enumerate(slate.external_auditors, 1):
        lines.append(
            f"{idx}. **{a.title}** (`{a.slug}`) — *{a.committee_type}*\n"
            f"   - **Mandate**: {a.fiduciary_mandate}\n"
            f"   - **Management Counterparties**: {', '.join(f'`{t}`' for t in a.oversight_targets)}"
        )

    lines.extend(["", "## Quarterly Boardroom & Audit Committee Agenda"])
    for idx, item in enumerate(slate.quarterly_agenda, 1):
        lines.append(f"{idx}. {item}")

    if slate.oversight_edges:
        lines.extend(["", "## Active Fiduciary Oversight & Audit Edges into Management"])
        for edge in slate.oversight_edges:
            lines.append(
                f"- `{edge.governance_role_slug or edge.governance_role_id}` "
                f"--[**{edge.edge_type}**]--> `{edge.target_management_role_slug}` "
                f"(Artifact: *{edge.review_artifact}*)"
            )
    lines.append("")
    return "\n".join(lines)


def format_superhuman_governance_markdown(pkg: SuperhumanGovernancePackage) -> str:
    """Formats a `SuperhumanGovernancePackage` into an executive Markdown runbook."""
    lines: List[str] = [
        f"# {pkg.title}",
        "",
        f"- **Profile ID / Slug**: `{pkg.id}` / `{pkg.slug}`",
        f"- **Base Governance Seat**: `{pkg.base_governance_role.slug}` ({pkg.base_governance_role.title})",
        f"- **Category**: `{pkg.base_governance_role.governance_category}`",
        f"- **Target Problem / Company Mandate**: {pkg.target_problem_or_company}",
        f"- **Fused Committees & Auditors**: {', '.join(f'`{s}`' for s in pkg.fused_committee_slugs)}",
        f"- **Compiled Deep Prompt Size**: `{pkg.prompt_character_count:,}` characters",
        "",
        "## 1. Doctoral, CPA/CFA/J.D./M.D. & Capital-Allocation Foundations",
        "### Credentials & Degrees",
    ]
    for deg in pkg.academic_and_credential_foundation.degrees_and_certifications:
        lines.append(f"- {deg}")
    lines.append("\n### Capital-Allocation & Accounting Conservation Laws")
    for ax in pkg.academic_and_credential_foundation.capital_and_accounting_axioms:
        lines.append(f"- {ax}")
    lines.append("\n### Statutory & Governance Standards")
    for st in pkg.academic_and_credential_foundation.statutory_and_governance_standards:
        lines.append(f"- {st}")

    lines.extend(["", "## 2. Multi-Cycle Boardroom, Fraud-Detection & Turnaround Crucibles"])
    for idx, ep in enumerate(pkg.boardroom_and_audit_crucibles.crucible_episodes, 1):
        lines.extend([
            f"### Crucible {idx}: {ep.title} ({ep.cycle_and_context})",
            f"- **Management Spin / Hidden Trap**: {ep.management_spin_or_hidden_trap}",
            f"- **Forensic Board / Audit Intervention**: {ep.forensic_board_intervention}",
            f"- **Permanent Fiduciary Scar Tissue**: {ep.permanent_fiduciary_scar_tissue}",
            "",
        ])

    lines.extend([
        "## 3. Fiduciary Independence & Socratic Boardroom Temperament",
        f"- **Independence Posture**: {pkg.fiduciary_temperament.boardroom_independence_posture}",
        f"- **Truth-Over-Harmony Calibration**: {pkg.fiduciary_temperament.truth_over_harmony_calibration}",
    ])
    for trait in pkg.fiduciary_temperament.cognitive_and_conformity_immunities:
        lines.append(f"- **Immunity**: {trait}")

    lines.extend(["", "## 4. Multi-Committee & Management-Seam Adjacency Fusion"])
    for f in pkg.committee_and_seam_fusions:
        lines.append(
            f"- **{f.title}** (`{f.slug}` | `{f.fusion_source_type}` — `{f.edge_or_committee_role}`): "
            f"Eliminates blind spot: *{f.blind_spot_eliminated}*"
        )

    lines.extend(["", "## 5. 5-Stage Unknown-Risk & Management-Spin Falsification Protocol"])
    for stg in pkg.unknown_risk_epistemology.stages:
        lines.extend([
            f"### Stage {stg.stage_number}: {stg.name}",
            f"- **Objective**: {stg.objective}",
            f"- **Fiduciary Gate**: {stg.fiduciary_gate}",
        ])
        for act in stg.forensic_actions:
            lines.append(f"  - {act}")

    if pkg.developer_context:
        lines.extend(["", "## 6. Developer / Shareholder Context", pkg.developer_context])

    lines.extend([
        "",
        "---",
        "",
        "## Compiled 8-Section Deep Superhuman Governance & Audit Prompt",
        "",
        "```markdown",
        pkg.deep_superhuman_governance_prompt,
        "```",
        "",
    ])
    return "\n".join(lines)


def format_superhuman_governance_json(pkg: SuperhumanGovernancePackage, indent: int = 2) -> str:
    """Serializes a `SuperhumanGovernancePackage` into formatted JSON."""
    return json.dumps(pkg.to_dict(), indent=indent)


__all__ = [
    "format_governance_role_markdown",
    "format_board_slate_markdown",
    "format_superhuman_governance_markdown",
    "format_superhuman_governance_json",
]
