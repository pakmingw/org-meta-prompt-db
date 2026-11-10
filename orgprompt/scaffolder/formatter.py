"""Formatters for JSON and Markdown runbook exports in OrgPrompt Scaffolder."""

from __future__ import annotations

import json
from typing import Any, Dict, List


def format_role_markdown(pkg_data: Dict[str, Any]) -> str:
    """Formats a role scaffolding package into an executive Markdown runbook."""
    role = pkg_data.get("role", {})
    company_name = pkg_data.get("company_context") or "Enterprise Standard"
    use_cases = pkg_data.get("use_cases", [])
    tools = pkg_data.get("tools", [])
    swarm = pkg_data.get("subagent_swarm", [])
    genai_plan = pkg_data.get("genai_plan", {})
    prompt = role.get("system_prompt", "")

    lines: List[str] = [
        f"# Canonical Role Scaffolding Runbook: {role.get('name', 'Role')}",
        "",
        f"**Enterprise Context:** {company_name}",
        f"**Role ID:** `{role.get('id', '')}`  |  **Slug:** `{role.get('slug', '')}`",
        f"**Seniority Tier:** `{role.get('seniority_tier', role.get('seniority_level', 'PRINCIPAL_STAFF'))}`  |  **Archetype:** `{role.get('role_archetype', 'domain_specialist')}`",
        f"**Operating Unit:** {role.get('unit_name', 'Operations')}  |  **Exemplar:** {role.get('exemplar_name', 'Exemplar Org')}  |  **Industry:** {role.get('industry_name', 'Enterprise')}",
        "",
        "---",
        "",
        "## 1. Fiduciary Mission & Core Responsibilities",
        "",
        f"> {role.get('mission', '')}",
        "",
        "### Key Capabilities",
    ]

    caps = role.get("capabilities", [])
    if isinstance(caps, str):
        try:
            caps = json.loads(caps)
        except Exception:
            caps = [caps]
    for cap in caps:
        lines.append(f"- **{cap.replace('_', ' ').title() if isinstance(cap, str) else str(cap)}**")

    lines.extend([
        "",
        "### Mental Models & Governing Heuristics",
    ])
    mentals = role.get("mental_models", [])
    if isinstance(mentals, str):
        try:
            mentals = json.loads(mentals)
        except Exception:
            mentals = [mentals]
    for mm in mentals:
        lines.append(f"- *Mental Model:* {mm}")

    heuristics = role.get("heuristics", role.get("domain_heuristics", []))
    if isinstance(heuristics, str):
        try:
            heuristics = json.loads(heuristics)
        except Exception:
            heuristics = [heuristics]
    for h in heuristics:
        lines.append(f"- *Heuristic:* {h}")

    lines.extend([
        "",
        "---",
        "",
        f"## 2. Day-to-Day Operational Anatomy ({len(use_cases)} Use Cases)",
        "",
        "| Cadence | Operational Trigger | Inputs Consumed | Productivity & Domain Software | Output Artifacts |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])

    for uc in use_cases:
        cadence = uc.get("cadence", "DAILY")
        trigger = uc.get("trigger_event", uc.get("trigger", "Scheduled review"))
        inputs = ", ".join(uc.get("inputs_consumed", uc.get("inputs", []))) or "Domain Feeds"
        h_tools = uc.get("horizontal_tools", [])
        v_tools = uc.get("vertical_tools", uc.get("domain_tools", []))
        all_tools = ", ".join(h_tools + v_tools) or "Workstation Suite"
        artifacts = ", ".join(uc.get("output_artifacts", [])) or "Technical Document"
        lines.append(f"| `{cadence}` | {trigger} | {inputs} | {all_tools} | **{artifacts}** |")

    lines.extend([
        "",
        "### Detailed Operational Use Case Breakdown",
    ])
    for idx, uc in enumerate(use_cases, start=1):
        lines.extend([
            f"#### Use Case {idx}: {uc.get('title', 'Operational Task')}",
            f"- **Cadence & Trigger:** `{uc.get('cadence')}` triggered by *{uc.get('trigger_event', uc.get('trigger', ''))}*",
            f"- **Inputs:** {', '.join(uc.get('inputs_consumed', uc.get('inputs', [])))}",
            f"- **Horizontal Tools:** {', '.join(uc.get('horizontal_tools', []))}",
            f"- **Vertical Domain Software:** {', '.join(uc.get('vertical_tools', uc.get('domain_tools', [])))}",
            f"- **Cognitive Bottleneck:** {uc.get('cognitive_bottlenecks', 'High-complexity synthesis')}",
            f"- **Output Artifacts:** {', '.join(uc.get('output_artifacts', []))}",
            "",
        ])

    lines.extend([
        "---",
        "",
        f"## 3. Dual-Layer Tooling & Systems Architecture ({len(tools)} Associated Platforms)",
        "",
        "| Tool Name | Layer | Archetype | Usage Frequency | Proficiency Level | Primary Operational Purpose |",
        "| :--- | :--- | :--- | :--- | :--- | :--- |",
    ])

    for t in tools:
        t_name = t.get("name", t.get("tool_name", "Tool"))
        cat = t.get("category", "VERTICAL_DOMAIN")
        arch = t.get("archetype", "Platform")
        freq = t.get("usage_frequency", "PRIMARY_DAILY")
        prof = t.get("proficiency_level", "EXPERT")
        purpose = t.get("primary_purpose", "Core execution")
        lines.append(f"| **{t_name}** | `{cat}` | `{arch}` | `{freq}` | `{prof}` | {purpose} |")

    lines.extend([
        "",
        "---",
        "",
        f"## 4. Personal Subagent Swarm Architecture (\"Role-in-a-Box\" — {len(swarm)} Subagents)",
        "",
        "Every canonical role is decomposed into an acyclic swarm of specialized subagents orchestrated via Human-in-the-Loop checkpoints.",
        "",
    ])

    for sa in swarm:
        sa_name = sa.get("subagent_name", "Subagent")
        sa_role = sa.get("subagent_role", "SPECIALIST")
        hitl = sa.get("hitl_checkpoint", "Human sign-off required")
        mcp = sa.get("tool_mcp_bindings", sa.get("mcp_tools", []))
        if isinstance(mcp, str):
            try:
                mcp = json.loads(mcp)
            except Exception:
                mcp = [mcp]
        dag = sa.get("interaction_dag", {})
        if isinstance(dag, str):
            try:
                dag = json.loads(dag)
            except Exception:
                dag = {}

        lines.extend([
            f"### Subagent: {sa_name} (`{sa_role}`)",
            f"- **MCP Tool Bindings:** {', '.join(f'`{m}`' for m in mcp) if mcp else 'Standard I/O'}",
            f"- **Interaction DAG Upstream:** {', '.join(dag.get('upstream', [])) or 'None (Initiator)'}",
            f"- **Interaction DAG Downstream:** {', '.join(dag.get('downstream', [])) or 'Final Delivery'}",
            f"- **HITL Gate & Review Criteria:** {hitl}",
            "",
            "<details>",
            f"<summary>View {sa_name} System Prompt</summary>",
            "",
            "```markdown",
            sa.get("system_prompt", "").strip(),
            "```",
            "",
            "</details>",
            "",
        ])

    lines.extend([
        "---",
        "",
        "## 5. Generative AI Tooling Engineering Blueprint",
        "",
    ])

    if genai_plan:
        h_spec = genai_plan.get("horizontal_genai_spec", {})
        if isinstance(h_spec, str):
            try:
                h_spec = json.loads(h_spec)
            except Exception:
                h_spec = {}
        v_spec = genai_plan.get("vertical_genai_spec", {})
        if isinstance(v_spec, str):
            try:
                v_spec = json.loads(v_spec)
            except Exception:
                v_spec = {}
        mcp_ints = genai_plan.get("mcp_integrations", [])
        if isinstance(mcp_ints, str):
            try:
                mcp_ints = json.loads(mcp_ints)
            except Exception:
                mcp_ints = [mcp_ints]

        lines.extend([
            f"**RAG & Context Architecture:** {genai_plan.get('rag_context_architecture', 'Hybrid BM25 + Vector Context')}",
            f"**HITL Guardrails & Safety Triggers:** {genai_plan.get('hitl_guardrails', 'Strict validation required')}",
            f"**Quantified ROI & Productivity Impact:** {genai_plan.get('roi_productivity_impact', '25-45% acceleration')}",
            f"**Connected MCP Protocols:** {', '.join(f'`{m}`' for m in mcp_ints) if mcp_ints else 'Internal Bus'}",
            "",
            "### Horizontal GenAI Copilot Specifications",
            "",
        ])
        for k, v in h_spec.items():
            lines.append(f"- **{k.replace('_', ' ').title()}:** {v}")

        lines.extend([
            "",
            "### Vertical Domain System GenAI Integrations",
            "",
        ])
        for k, v in v_spec.items():
            lines.append(f"- **{k.replace('_', ' ').title()}:** {v}")
    else:
        lines.append("*GenAI Engineering Plan scheduled for generation.*")

    lines.extend([
        "",
        "---",
        "",
        "## 6. Compiled Canonical Meta-Prompt (Verbatim System Prompt)",
        "",
        "```markdown",
        prompt.strip(),
        "```",
        "",
    ])

    return "\n".join(lines)


def format_company_markdown(pkg_data: Dict[str, Any]) -> str:
    """Formats a company scaffolding package into an enterprise Markdown runbook."""
    company = pkg_data.get("company", {})
    divisions = pkg_data.get("divisions", [])
    employed_roles = pkg_data.get("employed_roles", [])
    tools = pkg_data.get("tools", [])
    swarms = pkg_data.get("swarms", [])
    comparison = pkg_data.get("comparison", {})
    problem = pkg_data.get("problem_statement")

    lines: List[str] = [
        f"# Enterprise Scaffolding Runbook: {company.get('name', 'Enterprise')}",
        "",
        f"**Fortune 500 Rank:** `#{company.get('rank', 'N/A')}`  |  **Revenue:** `${company.get('revenue_billions', 0.0):.2f}B`",
        f"**Macro Industry:** {company.get('macro_industry', 'Diversified')}  |  **Sub-Sector:** {company.get('sub_sector', 'Enterprise')}",
        f"**Business Model:** `{company.get('business_model', 'MULTI_SIDED_PLATFORM')}`  |  **Operating Archetype:** `{company.get('operating_archetype', 'PLATFORM_ECOSYSTEM')}`",
        f"**Company ID:** `{company.get('id', '')}`  |  **Slug:** `{company.get('slug', '')}`",
        "",
    ]

    if problem:
        lines.extend([
            "> **Executive Problem / Transformation Mandate:**",
            f"> {problem}",
            "",
        ])

    lines.extend([
        "---",
        "",
        f"## 1. Operating Divisions & Functional Architecture ({len(divisions)} Units)",
        "",
    ])
    for div in divisions:
        lines.append(f"- **Division:** {div}")

    lines.extend([
        "",
        "---",
        "",
        f"## 2. Employed Canonical Roles & Staffing Structure ({len(employed_roles)} Roles)",
        "",
        "| Department / Division | Role Title | Priority Tier | Role Archetype | Canonical Slug |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ])

    for er in employed_roles:
        dept = er.get("department", "Corporate Operations")
        title = er.get("name", er.get("title", "Staff"))
        tier = er.get("priority_tier", "CORE")
        arch = er.get("role_archetype", "domain_specialist")
        slug = er.get("slug", "")
        lines.append(f"| {dept} | **{title}** | `{tier}` | `{arch}` | `{slug}` |")

    lines.extend([
        "",
        "---",
        "",
        f"## 3. Enterprise Tooling Stack ({len(tools)} Standard Platforms)",
        "",
        "| Tool Platform | Category | Archetype | Vendor Examples |",
        "| :--- | :--- | :--- | :--- |",
    ])

    for t in tools:
        t_name = t.get("name", "Tool")
        cat = t.get("category", "PRODUCTIVITY")
        arch = t.get("archetype", "Platform")
        vendors = ", ".join(t.get("vendor_examples", [])) or "Enterprise Suite"
        lines.append(f"| **{t_name}** | `{cat}` | `{arch}` | {vendors} |")

    lines.extend([
        "",
        "---",
        "",
        f"## 4. Personal Subagent Swarm Deployments ({len(swarms)} Key Roles Equipped)",
        "",
    ])

    for sw in swarms:
        r_name = sw.get("role_name", sw.get("role_title", "Role"))
        r_slug = sw.get("role_slug", "")
        subagents = sw.get("subagents", [])
        lines.extend([
            f"### Personal Swarm: {r_name} (`{r_slug}`)",
            f"- **Subagents ({len(subagents)}):** {', '.join(s.get('subagent_name', '') for s in subagents)}",
            f"- **HITL Governance:** Multi-gate sign-off before operational dispatch.",
            "",
        ])

    if comparison:
        lines.extend([
            "---",
            "",
            "## 5. Internet Alignment & Delta Analysis",
            "",
            f"**Alignment Score:** `{comparison.get('alignment_score', 1.0):.2f}`  |  **Database Mapped Roles:** `{comparison.get('db_mapped_roles_count', len(employed_roles))}`",
            "",
            "### Delta Analysis",
            "",
            comparison.get("delta_analysis_md", "Full alignment verified with enterprise operating model.").strip(),
            "",
            "### Tailored Swarm Recommendation",
            "",
            comparison.get("tailored_swarm_recommendation_md", "Deploy standardized 6-agent personal swarms across core operations.").strip(),
            "",
        ])

    return "\n".join(lines)


def format_role_json(pkg_data: Dict[str, Any], indent: int = 2) -> str:
    """Serializes a role scaffolding package to JSON."""
    return json.dumps(pkg_data, indent=indent, default=str)


def format_company_json(pkg_data: Dict[str, Any], indent: int = 2) -> str:
    """Serializes a company scaffolding package to JSON."""
    return json.dumps(pkg_data, indent=indent, default=str)
