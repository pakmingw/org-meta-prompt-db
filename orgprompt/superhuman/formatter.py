"""8-Section Deep Superhuman Meta-Prompt compiler and Markdown/JSON formatters."""

from __future__ import annotations

import json
from typing import Any, Dict, List

from orgprompt.superhuman.models import SuperhumanRolePackage


def _bullet_lines(items: List[Any], fallback: str = "- None specified") -> str:
    cleaned = [str(x).strip() for x in items if str(x).strip()]
    if not cleaned:
        return fallback
    return "\n".join(f"- {item}" for item in cleaned)


def compile_deep_superhuman_prompt(pkg: SuperhumanRolePackage) -> str:
    """Compiles a >= 6,500-character 8-section Deep Superhuman Meta-Prompt."""
    pr: Dict[str, Any] = pkg.primary_role or {}
    role_title = pr.get("title") or pr.get("name") or pkg.title
    seniority = pr.get("seniority_level") or pr.get("seniority_tier") or "PRINCIPAL_STAFF"
    archetype = pr.get("role_archetype") or "domain_specialist"
    exemplar = pr.get("exemplar_name") or "World-Class Exemplar Organization"
    industry = pr.get("industry_name") or pr.get("industry") or "Enterprise"
    unit_name = pr.get("unit_name") or "Core Operations & Architecture"
    mission = pr.get("mission") or f"Solve mission-critical {industry} challenges from first principles."
    base_prompt = (pr.get("system_prompt") or "").strip()

    company_line = (
        f"Target Enterprise / Operating Environment: {pkg.company_context}"
        if pkg.company_context
        else f"Target Operating Environment: {exemplar} ({industry})"
    )

    # Section 1
    sec1 = (
        f"[SECTION 1] SUPERHUMAN ROLE IDENTITY, EXEMPLAR LINEAGE & TARGET PROBLEM MANDATE\n"
        f"================================================================================\n"
        f"You are operating as **{pkg.title}** (Profile ID: `{pkg.id}`, Input Pathway: `{pkg.input_mode}`).\n"
        f"- Anchor Role Identity: {role_title} (`{pr.get('slug', pkg.slug)}`) | Seniority: `{seniority}` | Archetype: `{archetype}`\n"
        f"- Exemplar Lineage & Functional Unit: {exemplar} — {unit_name} ({industry})\n"
        f"- {company_line}\n"
        f"- Mapped OKG Anchor Role ID: `{pkg.mapped_okg_anchor_role_id or pr.get('id', 'custom_unmapped')}`\n"
        f"- Core Organizational Mission: {mission}\n\n"
        f"TARGET PROBLEM MANDATE:\n"
        f"\"{pkg.problem_statement}\"\n\n"
        f"SUPERHUMAN MANDATE:\n"
        f"You are not a generic assistant summarizing surface-level best practices. You embody the rare 'Perfect Human' "
        f"practitioner who combines rigorous doctoral-level mathematical and physical foundations, 18+ years of high-stakes "
        f"production scar tissue across world-class institutions, internalized polymathic mastery of your upstream, downstream, "
        f"and adversarial audit neighbors in the Organizational Knowledge Graph, and an explicit 5-stage Out-of-Distribution "
        f"(Unknown-to-AI) scientific discovery protocol. Whenever historical priors or memorized templates fail, you drop down "
        f"to conservation laws, structural isomorphism, and falsifiable micro-experiments."
    )

    # Section 2
    af = pkg.academic_foundation
    cruc = pkg.on_the_job_crucibles
    cruc_blocks: List[str] = []
    for idx, ep in enumerate(cruc.crucible_episodes, start=1):
        cruc_blocks.append(
            f"  Crucible {idx}: {ep.title} ({ep.organization_and_era})\n"
            f"    * Broken Assumption & Failure Mode: {ep.failure_mode_and_broken_assumption}\n"
            f"    * Forensic Diagnosis & Stabilization: {ep.recovery_and_forensic_action}\n"
            f"    * Permanent Scar-Tissue Intuition: {ep.tacit_scar_tissue_lesson}"
        )
    sec2 = (
        f"[SECTION 2] PERFECT HUMAN PEDIGREE: UNIVERSITY/DOCTORAL FOUNDATIONS & CRUCIBLE SCAR TISSUE\n"
        f"==========================================================================================\n"
        f"2.1 University, Graduate & Doctoral Rigor:\n"
        f"{_bullet_lines(af.degrees)}\n\n"
        f"2.2 Foundational Mathematical, Scientific & Domain Axioms Mastered:\n"
        f"{_bullet_lines(af.foundational_coursework_and_axioms)}\n\n"
        f"2.3 Seminal Literature, Textbooks & International Standards Internalized:\n"
        f"{_bullet_lines(af.seminal_literature_and_standards)}\n\n"
        f"2.4 Doctoral Thesis & Experimental Lab Methodology:\n"
        f"- {af.doctoral_thesis_and_lab_methodology}\n\n"
        f"2.5 Cross-Disciplinary Minors Bridging Adjacent Organizational Silos:\n"
        f"{_bullet_lines(af.cross_disciplinary_minors)}\n\n"
        f"2.6 Progressive 18-Year Rotational Career Trajectory:\n"
        f"{_bullet_lines(cruc.career_trajectory)}\n\n"
        f"2.7 Cross-Functional Tours of Duty (Operations, Audit, Architecture, Commercial P&L):\n"
        f"{_bullet_lines(cruc.cross_functional_tours_of_duty)}\n\n"
        f"2.8 Survived High-Stakes Production Failures & Adversarial Audits ('Scar Tissue'):\n"
        + "\n".join(cruc_blocks)
        + f"\n\n2.9 Operational Mentorship & Review Rituals:\n{_bullet_lines(cruc.mentorship_and_review_rituals)}"
    )

    # Section 3
    hc = pkg.human_characteristics
    sec3 = (
        f"[SECTION 3] PSYCHOLOGICAL, COGNITIVE & EPISTEMIC CHARACTERISTICS OF THE PERFECT HUMAN\n"
        f"=====================================================================================\n"
        f"3.1 Multi-Scale Cognitive Architecture:\n"
        f"{_bullet_lines(hc.cognitive_architecture)}\n\n"
        f"3.2 Epistemic Calibration & Uncertainty Partitioning:\n"
        f"- {hc.epistemic_calibration}\n\n"
        f"3.3 Explicit Immunity to Cognitive Biases & Organizational Mediocrity:\n"
        f"{_bullet_lines(hc.bias_and_mediocrity_resistances)}\n\n"
        f"3.4 Aesthetic Taste for Simplicity, Parsimony & Extreme Ownership:\n"
        f"{_bullet_lines(hc.aesthetic_and_ownership_traits)}\n\n"
        f"3.5 High-Stress Incident Composure & Socio-Technical Diplomacy:\n"
        f"- {hc.socio_technical_temperament}"
    )

    # Section 4
    adj_blocks: List[str] = []
    for i, adj in enumerate(pkg.adjacent_roles, start=1):
        adj_blocks.append(
            f"  4.{i} [{adj.edge_type} | {adj.direction}] {adj.title} (`{adj.slug}`, {adj.exemplar_org} — {adj.industry})\n"
            f"      - Authentic Graph Edge Description: {adj.edge_description or 'Cross-functional boundary coordination'}\n"
            f"      - Interface & Handoff Protocol: {adj.edge_protocol or adj.protocol_and_cadence or 'Structured artifact verification'}\n"
            f"      - Absorbed Capabilities: {'; '.join(adj.absorbed_capabilities[:3]) or 'Boundary contract enforcement'}\n"
            f"      - Absorbed Mental Models & Heuristics: {'; '.join((adj.absorbed_mental_models + adj.absorbed_heuristics)[:4]) or 'First-principles interface invariants'}\n"
            f"      - Internalized Failure-Gating Checks: {'; '.join(adj.failure_gating_checks[:3]) or 'Zero unvalidated state handoffs'}\n"
            f"      - Shared Boundary Artifacts: {', '.join(adj.output_artifacts[:4]) or 'Verified Specification & Audit Ledger'}\n"
            f"      - Organizational Blind Spot Eliminated: {adj.blind_spot_eliminated}"
        )
    if not adj_blocks:
        adj_blocks.append(
            "  4.1 [CHALLENGES_OR_AUDITS | INCOMING] Independent Principal Risk & Architecture Challenger\n"
            "      - Organizational Blind Spot Eliminated: Eliminates single-silo optimism bias and unverified boundary handoffs."
        )
    team_lines = [
        f"- {tr.get('title') or tr.get('name')} (`{tr.get('slug', '')}`, {tr.get('role_archetype', 'specialist')})"
        for tr in pkg.enterprise_team_roles[:6]
    ]
    sec4 = (
        f"[SECTION 4] POLYMATHIC ORGANIZATIONAL GRAPH FUSION (INTERNALIZED ADJACENT ROLES)\n"
        f"================================================================================\n"
        f"Unlike a siloed specialist who throws artifacts over the wall, you have internalized the mental models, "
        f"handoff protocols, and red-team gates of your adjacent Organizational Knowledge Graph neighbors:\n\n"
        + "\n\n".join(adj_blocks)
        + (
            f"\n\nSupporting Cross-Functional Enterprise Team Topology Available for Delegation:\n"
            + "\n".join(team_lines)
            if team_lines
            else ""
        )
    )

    # Section 5
    caps = pr.get("capabilities") or []
    models = pr.get("mental_models") or []
    heuristics = pr.get("heuristics") or []
    vocab = pr.get("vocabulary") or []
    anti = pr.get("anti_patterns") or []
    tool_lines = [
        f"- {t.get('name') or t.get('tool_name')} [{t.get('category', 'Tool')} / {t.get('archetype', 'Domain')}]: {t.get('primary_purpose') or t.get('description', '')}"
        for t in pkg.tools[:8]
    ]
    swarm_lines = [
        f"- {s.get('subagent_name')} ({s.get('subagent_role')}): HITL Gate = {s.get('hitl_checkpoint', 'Required pre-commit verification')}"
        for s in pkg.subagent_swarm[:6]
    ]
    clipped_base = base_prompt[:1800].rsplit("\n", 1)[0] if len(base_prompt) > 1800 else base_prompt
    base_excerpt = (
        f"\n\n5.8 Inherited Canonical / Custom Agent Operating Prompt Baseline:\n{clipped_base}"
        if clipped_base
        else ""
    )
    sec5 = (
        f"[SECTION 5] CANONICAL ROLE THOUGHT MODEL, DUAL-LAYER TOOLING & 6-AGENT SUBAGENT SWARM\n"
        f"=====================================================================================\n"
        f"5.1 Core Operational Capabilities:\n{_bullet_lines(caps, '- End-to-end architecture, execution, and verification')}\n\n"
        f"5.2 Domain Mental Models:\n{_bullet_lines(models, '- First-principles causal modeling and state-space invariants')}\n\n"
        f"5.3 Battle-Tested Decision Heuristics:\n{_bullet_lines(heuristics, '- Bound worst-case blast radius before optimizing steady-state throughput')}\n\n"
        f"5.4 Precision Technical Vocabulary:\n- {', '.join(str(v) for v in vocab[:15]) if vocab else 'Conservation invariants, tail latency, causal DAGs, blast-radius isolation'}\n\n"
        f"5.5 Strictly Forbidden Anti-Patterns:\n{_bullet_lines(anti, '- Never ship unverified heuristics into high-consequence regimes')}\n\n"
        f"5.6 Dual-Layer Horizontal & Vertical Tooling Stack:\n"
        + ("\n".join(tool_lines) if tool_lines else "- Formal modeling, telemetry analytics, and deterministic verification suite")
        + "\n\n5.7 Personal 6-Agent Subagent Swarm ('Role-in-a-Box' Delegation Topology):\n"
        + ("\n".join(swarm_lines) if swarm_lines else "- Decompose data ingestion, formal verification, simulation, and red-team audit across specialized subagents.")
        + base_excerpt
    )

    # Section 6
    stage_blocks: List[str] = []
    for st in pkg.unknown_problem_epistemology.stages:
        stage_blocks.append(
            f"  [{st.name}]\n"
            f"  * Objective: {st.objective}\n"
            f"  * Triggers / Conservation Axioms:\n"
            + "\n".join(f"    - {t}" for t in st.triggers_or_axioms)
            + "\n  * Mandatory Execution Actions:\n"
            + "\n".join(f"    - {a}" for a in st.concrete_actions)
            + f"\n  * Verification Exit Gate: {st.verification_gate}"
        )
    sec6 = (
        f"[SECTION 6] 5-STAGE OUT-OF-DISTRIBUTION (UNKNOWN-TO-AI) FIRST-PRINCIPLES DISCOVERY PROTOCOL\n"
        f"===========================================================================================\n"
        f"CRITICAL EPISTEMIC RULE: Whenever any aspect of the problem lies outside standard training distributions, "
        f"exhibits novel coupling, or lacks historical precedent, you MUST execute all 5 stages sequentially before "
        f"committing to a final design:\n\n" + "\n\n".join(stage_blocks)
    )

    # Section 7
    dev_ctx = pkg.developer_context.strip()
    dev_verbatim = (
        dev_ctx
        if dev_ctx
        else "No external proprietary developer overrides supplied; enforce strict first-principles physics, statutory compliance, and exemplar security/solvency baselines."
    )
    sec7 = (
        f"[SECTION 7] DEVELOPER-COMPLEMENTED BACKGROUND, PROPRIETARY CONSTRAINTS & CONTEXT OVERRIDES\n"
        f"==========================================================================================\n"
        f"7.1 Verbatim Developer-Injected Domain Background & Hard Constraints:\n"
        f"<<<BEGIN_DEVELOPER_CONTEXT>>>\n"
        f"{dev_verbatim}\n"
        f"<<<END_DEVELOPER_CONTEXT>>>\n\n"
        f"7.2 Precedence & Conflict-Resolution Rules:\n"
        f"- Rule 1 (Local Ground-Truth Supremacy): Every factual architecture constraint, legacy quirk, latency/budget ceiling, "
        f"regulatory jurisdiction, or non-goal inside `BEGIN_DEVELOPER_CONTEXT` overrides generic textbook defaults.\n"
        f"- Rule 2 (Invariant Consistency Check): Cross-check developer constraints against Stage 2 conservation laws; if a "
        f"requested target is mathematically or physically impossible under the stated budget/latency ceiling, prove the "
        f"impossibility quantitatively and present the Pareto-optimal relaxation options.\n"
        f"- Rule 3 (Zero Silent Omission): Trace every constraint from `BEGIN_DEVELOPER_CONTEXT` explicitly into the final verification table."
    )

    # Section 8
    sec8 = (
        f"[SECTION 8] CONCRETE EXECUTION & VERIFICATION OUTPUT CONTRACT\n"
        f"=============================================================\n"
        f"Structure every high-stakes analysis, design, or crisis response using this exact 6-part deliverable contract:\n"
        f"1. **OOD Regime Diagnosis & Pattern-Match Veto Ledger**: What makes this problem hard/novel, which naive textbook/LLM answers are explicitly vetoed, and Known vs. Unknown state partitioning.\n"
        f"2. **First-Principles Conservation & Fermi Feasibility Proof**: Governing equations, capacity/latency/economic bounds, and non-negotiable invariants.\n"
        f"3. **Polymathic Architecture & Cross-Adjacent Mechanism Design**: Concrete solution integrating primary role rigor with upstream/downstream/audit interface contracts from Section 4 and developer constraints from Section 7.\n"
        f"4. **Falsifiable Hypothesis Tree & Minimum-Regret Micro-Experiments**: >= 3 testable hypotheses with exact observable metrics, pass/fail thresholds, canary blast-radius limits, and instant rollback triggers.\n"
        f"5. **Internalized Red-Team Pre-Mortem & Failure-Mode Matrix**: Hostile audit across security, tail-load, data corruption, regulatory compliance, and incentive gaming—paired with deterministic mitigations.\n"
        f"6. **Sequenced Execution Runbook & Subagent Delegation Plan**: Immediate Day-1 containment/validation steps, 30/60/90-day rollout milestones, and concrete verification gates."
    )

    return "\n\n".join([sec1, sec2, sec3, sec4, sec5, sec6, sec7, sec8])


def format_superhuman_json(pkg: SuperhumanRolePackage, indent: int = 2) -> str:
    """Serializes a SuperhumanRolePackage to formatted JSON."""
    return json.dumps(pkg.to_dict(), indent=indent, ensure_ascii=False)


def format_superhuman_markdown(pkg: SuperhumanRolePackage) -> str:
    """Renders a comprehensive Executive & Agentic Markdown Runbook for a SuperhumanRolePackage."""
    pr = pkg.primary_role or {}
    prompt_text = pkg.deep_superhuman_prompt or compile_deep_superhuman_prompt(pkg)

    lines: List[str] = [
        f"# Superhuman Role Blueprint: {pkg.title}",
        "",
        "| Attribute | Value |",
        "| :--- | :--- |",
        f"| **Profile ID** | `{pkg.id}` |",
        f"| **Slug** | `{pkg.slug}` |",
        f"| **Synthesis Input Mode** | `{pkg.input_mode}` |",
        f"| **Primary / Anchor Role** | {pr.get('title') or pr.get('name', pkg.title)} (`{pr.get('slug', '')}`) |",
        f"| **Mapped OKG Anchor ID** | `{pkg.mapped_okg_anchor_role_id or pr.get('id', 'N/A')}` |",
        f"| **Industry / Exemplar** | {pr.get('industry_name') or pr.get('industry', 'Enterprise')} / {pr.get('exemplar_name', 'World-Class Exemplar')} |",
        f"| **Company Context** | {pkg.company_context or 'Generic Cross-Enterprise'} |",
        f"| **Adjacent Roles Fused** | `{len(pkg.adjacent_roles)}` |",
        f"| **Crucible Scar-Tissue Episodes** | `{len(pkg.on_the_job_crucibles.crucible_episodes)}` |",
        f"| **Deep Superhuman Prompt Length** | `{len(prompt_text):,}` characters |",
        "",
        "## 1. Target Problem Mandate",
        f"> {pkg.problem_statement}",
        "",
        "## 2. Polymathic Organizational Graph Adjacency Matrix",
        "| Neighbor Role | Edge Type | Direction | Exemplar / Industry | Blind Spot Eliminated |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for adj in pkg.adjacent_roles:
        lines.append(
            f"| **{adj.title}** (`{adj.slug}`) | `{adj.edge_type}` | `{adj.direction}` | "
            f"{adj.exemplar_org} ({adj.industry}) | {adj.blind_spot_eliminated} |"
        )
    if not pkg.adjacent_roles:
        lines.append("| *Internalized Adversarial Challenger* | `CHALLENGES_OR_AUDITS` | `INCOMING` | Exemplar | Single-silo blind spots |")

    lines.extend([
        "",
        "## 3. Perfect Human Pedigree Summary",
        "### University, Graduate & Doctoral Rigor",
        _bullet_lines(pkg.academic_foundation.degrees),
        "",
        "**Doctoral Thesis & Lab Methodology**:",
        f"- {pkg.academic_foundation.doctoral_thesis_and_lab_methodology}",
        "",
        "### On-the-Job Crucible Episodes ('Scar Tissue')",
    ])
    for idx, ep in enumerate(pkg.on_the_job_crucibles.crucible_episodes, start=1):
        lines.extend([
            f"#### {idx}. {ep.title} (*{ep.organization_and_era}*)",
            f"- **Broken Assumption & Failure Mode**: {ep.failure_mode_and_broken_assumption}",
            f"- **Forensic Recovery Action**: {ep.recovery_and_forensic_action}",
            f"- **Tacit Scar-Tissue Lesson**: {ep.tacit_scar_tissue_lesson}",
            "",
        ])

    lines.extend([
        "## 4. 5-Stage Out-of-Distribution (Unknown-to-AI) Epistemic Protocol",
    ])
    for st in pkg.unknown_problem_epistemology.stages:
        lines.extend([
            f"### {st.name}",
            f"- **Objective**: {st.objective}",
            f"- **Verification Exit Gate**: {st.verification_gate}",
            "",
        ])

    if pkg.developer_context.strip():
        lines.extend([
            "## 5. Developer-Complemented Background & Constraints",
            "```text",
            pkg.developer_context.strip(),
            "```",
            "",
        ])

    lines.extend([
        "## 6. Executable 8-Section Deep Superhuman Meta-Prompt",
        "```markdown",
        prompt_text,
        "```",
        "",
    ])
    return "\n".join(lines)


__all__ = [
    "compile_deep_superhuman_prompt",
    "format_superhuman_json",
    "format_superhuman_markdown",
]
