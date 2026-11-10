"""Algorithmic Procedural Seeder for Personal Subagent Swarms & GenAI Tooling Plans."""

import json
import sqlite3
import sys
from typing import Any, Dict, List, Tuple
from orgprompt.db.connection import get_connection, init_db


def fetch_roles_with_context(conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Fetches all canonical roles with organizational, industry, and tooling context."""
    cur = conn.cursor()
    cur.execute("""
        SELECT r.id, r.name, r.seniority_level, r.role_archetype, r.mission, r.system_prompt,
               u.name, o.name, i.id, i.name
        FROM canonical_roles r
        JOIN org_units u ON r.org_unit_id = u.id
        JOIN exemplar_orgs o ON u.exemplar_org_id = o.id
        JOIN industries i ON o.industry_id = i.id
        ORDER BY r.id
    """)
    roles = [
        {"id": rw[0], "name": rw[1], "seniority": rw[2], "archetype": rw[3],
         "mission": rw[4], "system_prompt": rw[5], "unit_name": rw[6],
         "org_name": rw[7], "ind_id": rw[8], "ind_name": rw[9]}
        for rw in cur.fetchall()
    ]
    cur.execute("""
        SELECT rt.role_id, t.name, t.description
        FROM role_tooling rt
        JOIN tools t ON rt.tool_id = t.id
        WHERE t.category = 'VERTICAL_DOMAIN'
        ORDER BY rt.role_id, rt.id
    """)
    tool_map: Dict[str, List[Tuple[str, str]]] = {}
    for r_id, t_name, t_desc in cur.fetchall():
        tool_map.setdefault(r_id, []).append((t_name, t_desc))

    for r in roles:
        r["vertical_tools"] = tool_map.get(
            r["id"], [("Enterprise ERP & Systems Platform", "Core enterprise execution system")]
        )
    return roles


def build_swarms_and_plans(
    roles: List[Dict[str, Any]]
) -> Tuple[List[tuple], List[tuple], List[tuple]]:
    """Synthesizes swarms, GenAI plans, and upgraded Section 7 prompts for all roles."""
    swarm_rows, plan_rows, prompt_updates = [], [], []

    for r in roles:
        r_id, r_name, seniority = r["id"], r["name"], r["seniority"]
        archetype, mission = r["archetype"], r["mission"]
        unit_name, org_name = r["unit_name"], r["org_name"]
        ind_id, ind_name = r["ind_id"], r["ind_name"]
        clean_ind = ind_name.split(",")[0].strip()
        v_tool_name, v_tool_desc = r["vertical_tools"][0]

        is_risk = archetype in ("risk_compliance", "operations") or any(
            k in mission.lower() or k in r_name.lower()
            for k in ("risk", "compliance", "audit", "governance")
        )
        sixth_role = "QUALITY_CRITIC" if is_risk else "DOMAIN_SPECIALIST"
        sixth_name = f"{r_name} Adversarial Quality & Compliance Critic" if is_risk else f"{r_name} Deep Domain & Systems Specialist"
        sixth_prompt = (
            f"You are the Adversarial Quality & Compliance Critic subagent for the {r_name} at {org_name} ({unit_name}). "
            f"Rigorously audit, stress-test, and challenge all deliverables, policy proposals, and models in {clean_ind} "
            f"against institutional standards, regulatory baselines, and risk thresholds prior to executive release."
            if is_risk else
            f"You are the Deep Domain & Systems Specialist subagent for the {r_name} at {org_name} ({unit_name}). "
            f"Interface directly with vertical platforms like {v_tool_name}, executing complex technical analysis, "
            f"domain query synthesis, telemetry validation, and deep systems engineering for {clean_ind} operations."
        )
        sixth_bindings = ["mcp://regulatory_kb", "mcp://adversarial_redteam", "mcp://compliance_audit"] if is_risk else [f"mcp://{ind_id}_gateway", "mcp://telemetry_query", "mcp://domain_api"]
        sixth_dag = (
            {"upstream": ["DOCUMENT_DRAFTER", "DECK_PRESENTER"], "downstream": ["ROLE_PRINCIPAL"], "triggers": ["pre_release_gate", "audit_check"]}
            if is_risk else
            {"upstream": ["CHIEF_OF_STAFF", "ROLE_PRINCIPAL"], "downstream": ["DOCUMENT_DRAFTER", "QUANTITATIVE_MODELER"], "triggers": ["telemetry_event", "domain_task"]}
        )
        sixth_hitl = f"Mandatory compliance sign-off attestation by {r_name}." if is_risk else f"Technical architecture and parameter sign-off by {r_name}."

        cos_downstream = ["DOCUMENT_DRAFTER", "QUANTITATIVE_MODELER"] if is_risk else ["DOMAIN_SPECIALIST", "QUANTITATIVE_MODELER"]
        drafter_downstream = ["DECK_PRESENTER", "QUALITY_CRITIC"] if is_risk else ["DECK_PRESENTER"]
        deck_downstream = ["QUALITY_CRITIC"] if is_risk else ["ROLE_PRINCIPAL"]

        subagents = [
            (
                "CHIEF_OF_STAFF", f"{r_name} Chief of Staff & Workflow Orchestrator",
                f"You are the Chief of Staff and Workflow Orchestrator subagent dedicated to the {r_name} at {org_name} within {unit_name}. "
                f"Triage incoming executive mandates, decompose high-level initiatives in {clean_ind}, maintain priorities, schedule operational gates, and orchestrate handoffs across the personal subagent swarm.",
                ["mcp://filesystem", "mcp://communication_hub", "mcp://calendar_scheduler", "mcp://task_graph"],
                {"upstream": ["ROLE_PRINCIPAL", "EXECUTIVE_STEERING", "MEETING_GRAPH"], "downstream": cos_downstream, "triggers": ["daily_briefing", "mandate_intake", "escalation"]},
                f"Mandatory {r_name} sign-off on priority adjustments and cross-functional resource commitments.",
            ),
            (
                "DOCUMENT_DRAFTER", f"{r_name} Narrative Document & RFC Drafter",
                f"You are the Narrative Document and RFC Drafter subagent supporting the {r_name} at {org_name}. "
                f"Craft publication-grade engineering RFCs, strategic memos, governance frameworks, and decision records for {unit_name}, embodying {org_name}'s rigorous authorial tone and {clean_ind} technical vocabulary.",
                ["mcp://word_processor", "mcp://rag_enterprise_lake", "mcp://citation_engine"],
                {"upstream": ["CHIEF_OF_STAFF", "ROLE_PRINCIPAL"], "downstream": drafter_downstream, "triggers": ["rfc_drafting", "memo_authoring", "policy_revision"]},
                f"Full authorial review and affirmative editorial sign-off by {r_name} before external distribution.",
            ),
            (
                "QUANTITATIVE_MODELER", f"{r_name} Quantitative Modeler & Analytical Specialist",
                f"You are the Quantitative Modeler and Analytical Specialist subagent supporting the {r_name} at {org_name}. "
                f"Design and maintain parametric financial models, capacity projections, operational variance analyses, and quantitative simulations for {unit_name}, ensuring zero unverified assumptions across {clean_ind} operations.",
                ["mcp://spreadsheet_engine", "mcp://sql_bi_analytics", "mcp://statistical_sandbox"],
                {"upstream": ["CHIEF_OF_STAFF", "ROLE_PRINCIPAL"], "downstream": ["DOCUMENT_DRAFTER", "DECK_PRESENTER"], "triggers": ["model_simulation", "variance_analysis", "capacity_forecast"]},
                f"Boundary condition audit and formula verification sign-off by {r_name}.",
            ),
            (
                "DECK_PRESENTER", f"{r_name} Presentation Narrative & Visual Deck Builder",
                f"You are the Presentation Narrative and Visual Deck Builder subagent supporting the {r_name} at {org_name}. "
                f"Translate complex technical analyses, architectural specifications, and quantitative models into crisp executive slide decks, board briefings, and milestone reviews tailored for {unit_name} and external stakeholders.",
                ["mcp://presentation_builder", "mcp://chart_synthesizer", "mcp://visual_assets"],
                {"upstream": ["DOCUMENT_DRAFTER", "QUANTITATIVE_MODELER", "ROLE_PRINCIPAL"], "downstream": deck_downstream, "triggers": ["deck_synthesis", "milestone_review", "executive_briefing"]},
                f"Pre-presentation dry-run and storyline alignment approval by {r_name}.",
            ),
            (
                "MEETING_GRAPH", f"{r_name} Meeting Intelligence & Action Dispatcher",
                f"You are the Meeting Intelligence and Action Dispatcher subagent supporting the {r_name} at {org_name}. "
                f"Ingest multi-speaker meeting audio and transcripts, extract architectural decisions, construct dependency and commitment graphs, and dispatch verified action items to downstream tracking systems following {unit_name} working sessions.",
                ["mcp://meeting_intelligence", "mcp://decision_log", "mcp://jira_action_sync"],
                {"upstream": ["MEETING_AUDIO_STREAM", "TRANSCRIPT_INGEST"], "downstream": ["CHIEF_OF_STAFF"], "triggers": ["post_meeting_webhook", "session_adjournment"]},
                f"Action item commitment verification by {r_name} prior to team broadcast.",
            ),
            (sixth_role, sixth_name, sixth_prompt, sixth_bindings, sixth_dag, sixth_hitl),
        ]

        meta_json = json.dumps({"role_seniority": seniority, "role_archetype": archetype, "industry": ind_id})
        for s_role, s_name, s_prompt, s_tools, s_dag, s_hitl in subagents:
            s_id = f"rss_{r_id}_{s_role.lower()}"
            swarm_rows.append((s_id, r_id, s_name, s_role, s_prompt, json.dumps(s_tools), json.dumps(s_dag), s_hitl, meta_json))

        # GenAI Plan
        h_spec = {
            "word_copilot": {"capability": f"Authoring publication-grade RFCs, executive memos, and governance specs in {clean_ind}.", "rag_mode": f"Hybrid dense/sparse retrieval over {unit_name} document repository.", "target_tool": "Microsoft Word / Google Docs"},
            "excel_modeler": {"capability": f"Parametric financial and operational modeling for {unit_name} with automated formula auditing.", "rag_mode": "Tabular ledger RAG with cell dependency tracing.", "target_tool": "Microsoft Excel"},
            "slide_presenter": {"capability": f"Converting complex technical memos into visual presentation decks for {org_name} leadership.", "rag_mode": "Executive summary vector synthesis.", "target_tool": "Microsoft PowerPoint"},
            "meeting_dispatcher": {"capability": f"Real-time decision extraction, commitment graphing, and action routing for {r_name} sessions.", "rag_mode": "Session graph and transcript indexing.", "target_tool": "Meeting Intelligence & Communication Hub"},
        }
        v_spec = {
            "domain_system": v_tool_name,
            "capability": f"Specialized GenAI assistant for {v_tool_name} enabling semantic telemetry queries, anomaly diagnosis, and automated workflow execution in {clean_ind}.",
            "context_window": "128k tokens with structured tool-call interfaces",
            "integration_pattern": "MCP Gateway with bidirectional state validation",
        }
        rag_arch = (
            f"Dual-tier retrieval: local BM25 index over {unit_name} operational guidelines combined with "
            f"dense subword LSA embeddings over {ind_name} standards, reranked via reciprocal rank fusion (k=60) with 32k context injection."
        )
        mcp_ints = ["mcp://enterprise_kb", f"mcp://{ind_id}_gateway", "mcp://office_suite", "mcp://audit_trail"]
        hitl_guard = (
            f"Dual-gate sign-off: generative outputs affecting capital allocation, regulatory filings, "
            f"or mission-critical {clean_ind} systems require explicit affirmative verification by {r_name}."
        )
        roi_impact = (
            f"44% reduction in recurring memo/model synthesis cycle time; 65% faster turnaround on cross-functional handoffs; 92% first-pass compliance accuracy."
        )
        plan_id = f"rgp_{r_id}"
        plan_rows.append((plan_id, r_id, json.dumps(h_spec), json.dumps(v_spec), rag_arch, json.dumps(mcp_ints), hitl_guard, roi_impact, meta_json))

        # Section 7 Upgrade for System Prompt
        section_7 = (
            f"\n\n## 7. Day-to-Day Tooling, GenAI Build Plan & Personal Subagent Swarm Protocol\n\n"
            f"### Dual-Layer Operating Tooling Stack\n"
            f"As {r_name} in {unit_name} ({org_name}), daily execution is anchored across dual tooling layers:\n"
            f"1. **Horizontal Productivity Tooling**:\n"
            f"   - **Document & Narrative Authoring**: Standardized on Word & Document Processors for drafting RFCs, strategic memos, and governance policies.\n"
            f"   - **Quantitative & Financial Modeling**: Advanced Spreadsheets for capacity planning, cost modeling, variance tracking, and tabular analysis.\n"
            f"   - **Executive Presentations**: Slide Presentation builders for executive steering committee updates, board briefings, and milestone reviews.\n"
            f"   - **Meeting & Async Coordination**: Meeting Intelligence and Async Communication hubs for multi-speaker decision logging, action dispatch, and triage.\n"
            f"2. **Vertical Domain Platform Integration**:\n"
            f"   - Primary domain platform: {v_tool_name} ({v_tool_desc}), directly integrated into daily workflows for technical synthesis, telemetry analysis, and domain execution.\n\n"
            f"### GenAI Tooling Build Plan & RAG Context Architecture\n"
            f"To eliminate cognitive toil and elevate strategic throughput, {r_name} operates with a four-pillar GenAI Copilot architecture:\n"
            f"- **Document Copilot (Word/Docs)**: Specialized prompt generation and RAG context retrieval over {ind_name} standards, synthesizing first drafts of RFCs, technical memos, and compliance attestations.\n"
            f"- **Quantitative Copilot (Excel/Sheets)**: Automated formula generation, sensitivity tables, and variance diagnostics mapped against {clean_ind} operational data lakes.\n"
            f"- **Presentation Deck Synthesizer (PowerPoint/Slides)**: Automated conversion of technical memos into high-impact 6-to-10 slide executive narrative decks with structured speaking notes.\n"
            f"- **Meeting Decision Graph Dispatcher**: Continuous listening and extraction of action items, commitment matrices, and dependency graphs immediately dispatched to tracking systems.\n"
            f"- **Context & RAG Architecture**: Dual-tier retrieval combining BM25 lexical search over internal {unit_name} playbooks with dense vector semantic search over industry standards, served via 128k context windows with strict citation tracking.\n\n"
            f"### Personal Subagent Swarm Orchestration Protocol (\"Role-in-a-Box\")\n"
            f"{r_name} directs a personal swarm of 6 specialized subagents operating as an integrated force multiplier:\n"
            f"1. **{r_name} Chief of Staff**: Orchestrates incoming work streams, schedules pipeline gates, and dispatches subtasks across the swarm.\n"
            f"2. **Document Drafter Subagent**: Synthesizes structured narrative memos, technical specs, and policy documentation under {r_name}'s editorial voice.\n"
            f"3. **Quantitative Modeler Subagent**: Constructs and maintains mathematical models, cost models, and operational projections with automated variance checking.\n"
            f"4. **Deck Presenter Subagent**: Builds crisp executive presentations, visual architecture diagrams, and stakeholder briefing decks.\n"
            f"5. **Meeting Intelligence Subagent**: Transcribes meetings, extracts key decisions and action items, and generates post-meeting commitment matrices.\n"
            f"6. **{sixth_name}**: {sixth_prompt}\n\n"
            f"### Human-in-the-Loop (HITL) Guardrails & Governance\n"
            f"- **Mandatory Affirmative Sign-off**: All external communications, regulatory filings, capital allocations, and architectural baselines require explicit review and cryptographic or digital sign-off by {r_name}.\n"
            f"- **Adversarial Gate Validation**: Subagent-generated outputs must clear internal consistency checks and compliance audits before advancing to external collaborators.\n"
            f"- **SLA & Audit Trail**: Every automated subagent action, prompt invocation, and tool execution is recorded in an immutable audit ledger with full parameter provenance."
        )

        base_prompt = r["system_prompt"]
        if "## 7. Day-to-Day Tooling" in base_prompt:
            base_prompt = base_prompt.split("## 7. Day-to-Day Tooling")[0].rstrip()

        upgraded_prompt = base_prompt + section_7
        prompt_updates.append((upgraded_prompt, len(upgraded_prompt), r_id))

    return swarm_rows, plan_rows, prompt_updates


def seed_swarms_and_plans(conn: sqlite3.Connection) -> Tuple[int, int, int]:
    """Populates role_subagent_swarms, role_genai_plans, and upgrades canonical_roles prompts."""
    roles = fetch_roles_with_context(conn)
    swarm_rows, plan_rows, prompt_updates = build_swarms_and_plans(roles)

    conn.execute("DELETE FROM role_subagent_swarms")
    conn.execute("DELETE FROM role_genai_plans")

    conn.executemany("""
        INSERT INTO role_subagent_swarms (
            id, role_id, subagent_name, subagent_role, system_prompt,
            tool_mcp_bindings_json, interaction_dag_json, hitl_checkpoint, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, swarm_rows)

    conn.executemany("""
        INSERT INTO role_genai_plans (
            id, role_id, horizontal_genai_spec_json, vertical_genai_spec_json,
            rag_context_architecture, mcp_integrations_json, hitl_guardrails,
            roi_productivity_impact, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, plan_rows)

    conn.executemany("""
        UPDATE canonical_roles
        SET system_prompt = ?, character_count = ?
        WHERE id = ?
    """, prompt_updates)

    return len(swarm_rows), len(plan_rows), len(prompt_updates)


def main() -> None:
    """Executes database schema initialization and personal swarm/genai plan seeder."""
    conn = get_connection()
    init_db()

    swarms_cnt, plans_cnt, prompts_cnt = seed_swarms_and_plans(conn)
    conn.commit()

    cur = conn.cursor()
    cur.execute("PRAGMA foreign_key_check")
    fk_violations = cur.fetchall()
    if fk_violations:
        print(f"FAILED: Found {len(fk_violations)} foreign key violations: {fk_violations}")
        sys.exit(1)

    print(f"SUCCESS: Seeded {swarms_cnt} subagents, {plans_cnt} GenAI plans, and upgraded {prompts_cnt} role prompts.")


if __name__ == "__main__":
    main()
