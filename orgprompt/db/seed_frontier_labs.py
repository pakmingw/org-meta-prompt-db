"""Idempotent Seeder for Phase 16: Nov 2026 Frontier AI Lab Vertical Tools & 16 Canonical Roles.

Non-destructively expands `data/org_knowledge_base.db` with:
1. 5 Frontier AI Lab Vertical Tools (`VERTICAL_DOMAIN` in `tools` -> 60 total).
2. 16 Canonical Frontier AI Lab Roles (`canonical_roles` -> 579 total), each with a >= 6,000-char
   7-section `system_prompt` (including `### Operational Tooling Stack` in Section 7), `roles_fts`
   synchronization, concrete `PRODUCES` & `CONSUMES` `artifacts`, 5 `role_use_cases`, 11 `role_tooling`
   bindings (6 horizontal + 5 frontier vertical), 6 acyclic `role_subagent_swarms`, 1 `role_genai_plans`,
   `REPORTS_TO` + workflow DAG edges (`out_degree >= 5` and `<= 15`), and `employs_role` links.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from orgprompt.db.connection import get_connection, get_default_db_path
from orgprompt.db.frontier_roles_specs import (
    FRONTIER_F500_EMPLOYERS,
    FRONTIER_LAB_VERTICAL_TOOLS,
    FRONTIER_ROLES_SPECS,
    FRONTIER_WORKFLOW_EDGES,
)
from orgprompt.prompts.compiler import PromptCompiler

HORIZONTAL_TOOL_IDS: List[str] = [
    "tool_word_processor",
    "tool_spreadsheet_processor",
    "tool_slide_presenter",
    "tool_meeting_note_taker",
    "tool_communication_triage",
    "tool_bi_analytics",
]


def _build_section_7(role_spec: Dict[str, Any], unit_name: str, org_name: str, ind_name: str) -> str:
    r_name = role_spec["name"]
    sixth_code, sixth_label = role_spec["sixth_subagent"]
    return (
        f"\n\n## 7. Day-to-Day Tooling, GenAI Build Plan & Personal Subagent Swarm Protocol\n\n"
        f"### Operational Tooling Stack\n"
        f"As **{r_name}** operating inside {unit_name} ({org_name} / {ind_name}), day-to-day frontier research, "
        f"post-training, systems co-design, safety evaluation, and enterprise deployment command an 11-tool dual-layer stack:\n"
        f"1. **Horizontal Productivity Layer (6 Core Suites)**:\n"
        f"   - `tool_word_processor` (Docs / LaTeX / Notion / RFCs): Pre-registration ablation RFCs, Model Specs, Safety Cases, and FDE architecture memos.\n"
        f"   - `tool_spreadsheet_processor` (Sheets / Python-Backed Workbooks): IsoFLOP scaling sheets, pass@k Pareto tables, cluster MFU budgets, and token unit-economics.\n"
        f"   - `tool_slide_presenter` (Slides / Executive Briefs): Readiness gate decks, Board Safety/Preparedness reviews, and customer deployment readouts.\n"
        f"   - `tool_meeting_note_taker` (Transcript & Decision Graph): Training war-room logs, ablation post-mortems, and FDE shadow-review action items.\n"
        f"   - `tool_communication_triage` (Slack / Incident Channels): Live loss-spike triage, SDC cluster alerts, and multi-pod release coordination.\n"
        f"   - `tool_bi_analytics` (Experiment & Telemetry BI): Real-time Elo/holdout scorecards, TTFT/TPOT goodput dashboards, and enterprise adoption metrics.\n"
        f"2. **Vertical Frontier AI Lab Layer (5 Specialized Platforms)**:\n"
        f"   - `tool_agentic_rl_gym_verifiers`: Containerized multi-turn SWE, OSWorld, math, and enterprise simulator RLVR gyms with tamper-proof outcome verifiers.\n"
        f"   - `tool_mcp_context_computer_use_runtime`: Model Context Protocol (MCP) JSON-RPC servers, `AGENTS.md`/`CLAUDE.md` harnesses, and virtualized GUI/CLI sandboxes.\n"
        f"   - `tool_disaggregated_kv_inference_stack`: Disaggregated prefill/decode engines, RadixAttention RDMA KV pools, MTP speculative decoding, and FP8/NVFP4 MoE kernels.\n"
        f"   - `tool_frontier_eval_preparedness_suite`: UK AISI Inspect / METR autonomy & cyber harnesses, ASL-3/ASL-4 CBRN gates, AI Control monitors, and canary decontamination.\n"
        f"   - `tool_fde_custom_posttraining_forge`: Forward-Deployed Enterprise RFT/DPO/distillation pipelines (`Mistral Forge` / OpenAI RFT) and SecNumCloud/VPC sovereign packaging.\n\n"
        f"### GenAI Tooling Build Plan & RAG Context Architecture\n"
        f"- **Ablation & Safety-Case Document Copilot**: Drafts pre-registered scaling hypotheses, ASL/Preparedness safety dossiers, and customer architecture specs grounded in verified experiment logs.\n"
        f"- **IsoFLOP, Goodput & Eval Statistical Modeler**: Computes paired bootstrap 95% confidence intervals, pass@k entropy curves, KV-cache hit economics, and cluster goodput rooflines.\n"
        f"- **Readiness & Customer Gate Presenter**: Compiles release-gate scorecards, contamination-forensics summaries, and executive FDE ROI decks.\n"
        f"- **War-Room & Rollout Transcript Dispatcher**: Clusters failed multi-turn agent trajectories and converts training/FDE syncs into tracked tickets.\n"
        f"- **Hybrid Frontier RAG Memory**: Unites BM25 lexical search over exact commit SHAs, kernel configs, MCP schemas, and canary UUIDs with dense semantic retrieval over research post-mortems.\n\n"
        f"### Personal Subagent Swarm Orchestration Protocol (\"Role-in-a-Box\")\n"
        f"{r_name} orchestrates a strictly acyclic 6-agent Personal Subagent Swarm with deterministic handoff contracts:\n"
        f"1. **{r_name} Research & Deployment Chief of Staff (`CHIEF_OF_STAFF`)**: Triages cluster allocations, eval gates, and pod dependencies.\n"
        f"2. **{sixth_label} (`{sixth_code}`)**: Executes deep domain verification across RLVR rewards, kernel rooflines, MCP security, or ASL thresholds.\n"
        f"3. **Scaling, Goodput & Psychometric Modeler (`QUANTITATIVE_MODELER`)**: Runs IsoFLOP regressions, style-controlled Elo, and TTFT/TPOT latency models.\n"
        f"4. **RFC, Model-Spec & Safety-Case Drafter (`DOCUMENT_DRAFTER`)**: Authors reproducible experiment specs, deployment runbooks, and governance filings.\n"
        f"5. **Release-Gate & Architecture Presenter (`DECK_PRESENTER`)**: Synthesizes checkpoint comparison boards and customer executive readouts.\n"
        f"6. **Training War-Room & Trajectory Graph (`MEETING_GRAPH`)**: Extracts structured root-cause actions from run logs and review syncs.\n\n"
        f"### Human-in-the-Loop (HITL) Guardrails & Governance\n"
        f"- **Mandatory Human Sign-Off on Irreversible Launches**: No frontier training run (`>1,024` accelerators), public weight/API release, ASL/Preparedness threshold clearance, or sovereign customer production cutover executes without explicit human principal sign-off by {r_name}.\n"
        f"- **Zero Reward-Hacking & Zero Contamination Tolerance**: Every benchmark claim requires verified canary decontamination, paired confidence intervals, and raw rollout audit sampling."
    )


def seed_frontier_labs(
    db_path_or_conn: Optional[Union[str, Path, sqlite3.Connection]] = None,
) -> Dict[str, int]:
    """Idempotently seeds the 5 Frontier Lab tools and 16 canonical roles into SQLite."""
    owns_conn = not isinstance(db_path_or_conn, sqlite3.Connection)
    conn = (
        get_connection(db_path_or_conn or get_default_db_path(), enable_foreign_keys=True)
        if owns_conn
        else db_path_or_conn
    )
    cur = conn.cursor()

    # 1. Upsert 5 Frontier AI Lab Vertical Tools
    for t in FRONTIER_LAB_VERTICAL_TOOLS:
        cur.execute(
            """
            INSERT INTO tools (
                id, slug, name, category, archetype, vendor_examples_json,
                typical_artifacts_json, description, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                slug = excluded.slug,
                name = excluded.name,
                category = excluded.category,
                archetype = excluded.archetype,
                vendor_examples_json = excluded.vendor_examples_json,
                typical_artifacts_json = excluded.typical_artifacts_json,
                description = excluded.description,
                metadata_json = excluded.metadata_json;
            """,
            (
                t["id"],
                t["slug"],
                t["name"],
                t["category"],
                t["archetype"],
                json.dumps(t["vendor_examples"]),
                json.dumps(t["typical_artifacts"]),
                t["description"],
                json.dumps({"vendor_count": len(t["vendor_examples"]), "artifact_count": len(t["typical_artifacts"]), "phase": 16}),
            ),
        )

    frontier_tool_ids = [t["id"] for t in FRONTIER_LAB_VERTICAL_TOOLS]
    edges_by_slug: Dict[str, Dict[str, List[str]]] = {r["slug"]: {} for r in FRONTIER_ROLES_SPECS}
    for src, dst, etype, _ in FRONTIER_WORKFLOW_EDGES:
        if src in edges_by_slug:
            edges_by_slug[src].setdefault(etype, []).append(dst)

    cadence_specs = [
        ("DAILY", "Daily Training/Rollout Telemetry Triage, Verifier Audit & Cluster Queue Sync", "Receipt of overnight RLVR/pre-training loss curves, container verifier logs, and FDE shadow telemetry"),
        ("WEEKLY", "Weekly Checkpoint Ablation Gate, Holdout Eval Review & Pod Handoff Sync", "Scheduled weekly IsoFLOP/RL checkpoint freeze, contamination check, and cross-pod integration gate"),
        ("MONTHLY", "Monthly Scaling-Law Calibration, Goodput Roofline Audit & Safety Red-Team Drill", "Monthly review of compute-to-capability curves, TTFT/TPOT serving unit-economics, and ASL/Preparedness tripwires"),
        ("QUARTERLY", "Quarterly Frontier Model Family Roadmap, Cluster Allocation & Enterprise Forge Review", "Quarterly compute allocation lock across pre-training, agentic RL, world models, and Global 2000 FDE deployments"),
        ("AD_HOC", "Live Loss-Spike / Reward-Hacking / ASL Canary Incident & Production Hotfix Escalation", "Detection of gradient divergence, reward-hacking exploit, SDC hardware fault, or high-severity enterprise OOD failure"),
    ]

    for r in FRONTIER_ROLES_SPECS:
        slug = r["slug"]
        role_id = f"role_{slug}"
        u_row = cur.execute(
            """
            SELECT u.name, o.name, i.id, i.name
            FROM org_units u
            JOIN exemplar_orgs o ON u.exemplar_org_id = o.id
            JOIN industries i ON o.industry_id = i.id
            WHERE u.id = ?;
            """,
            (r["org_unit_id"],),
        ).fetchone()
        if not u_row:
            raise ValueError(f"Missing org_unit_id {r['org_unit_id']} for {slug}")
        unit_name, org_name, ind_id, ind_name = u_row

        # Concrete Output & Input Artifacts (PRODUCES + CONSUMES)
        for art_label, direction, freq in [
            (r["output_artifact"], "PRODUCES", "WEEKLY"),
            (r["input_artifact"], "CONSUMES", "DAILY"),
        ]:
            art_slug = art_label.lower()
            art_id = f"art_{art_slug}"
            art_schema = {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "title": art_label,
                "type": "object",
                "required": ["artifact_id", "role_owner", "verification_metrics", "decontamination_hash", "hitl_signoff"],
            }
            cur.execute(
                """
                INSERT INTO artifacts (id, slug, name, artifact_type, schema_definition, description, exemplar_context, metadata_json)
                VALUES (?, ?, ?, 'SPECIFICATION', ?, ?, ?, '{"phase": 16}')
                ON CONFLICT(id) DO UPDATE SET name = excluded.name, schema_definition = excluded.schema_definition;
                """,
                (art_id, art_slug, art_label, json.dumps(art_schema), f"{direction.title()} artifact for {r['name']}.", org_name),
            )

        base_prompt = PromptCompiler.compile(
            {
                "title": r["name"],
                "seniority_tier": r["seniority_level"],
                "role_archetype": r["role_archetype"],
                "exemplar": org_name,
                "unit": unit_name,
                "mission": r["mission"],
                "exemplar_lineage": r["lineage"],
                "mental_models": r["mental_models"],
                "heuristics": r["heuristics"],
                "vocabulary": r["vocabulary"],
                "anti_patterns": r["anti_patterns"],
                "edges": edges_by_slug[slug],
                "output_artifact": r["output_artifact"],
                "input_artifact": r["input_artifact"],
            }
        )
        full_prompt = base_prompt + _build_section_7(r, unit_name, org_name, ind_name)
        char_count = len(full_prompt)
        if char_count < 6000:
            raise ValueError(f"Prompt for {slug} too short: {char_count} < 6000")

        cur.execute(
            """
            INSERT INTO canonical_roles (
                id, org_unit_id, slug, name, seniority_level, role_archetype,
                mission, system_prompt, character_count, capabilities_json,
                mental_models_json, domain_heuristics_json, technical_vocabulary_json,
                anti_patterns_json, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                org_unit_id = excluded.org_unit_id,
                name = excluded.name,
                seniority_level = excluded.seniority_level,
                role_archetype = excluded.role_archetype,
                mission = excluded.mission,
                system_prompt = excluded.system_prompt,
                character_count = excluded.character_count,
                capabilities_json = excluded.capabilities_json,
                mental_models_json = excluded.mental_models_json,
                domain_heuristics_json = excluded.domain_heuristics_json,
                technical_vocabulary_json = excluded.technical_vocabulary_json,
                anti_patterns_json = excluded.anti_patterns_json,
                updated_at = CURRENT_TIMESTAMP;
            """,
            (
                role_id, r["org_unit_id"], slug, r["name"], r["seniority_level"], r["role_archetype"],
                r["mission"], full_prompt, char_count, json.dumps(r["capabilities"]),
                json.dumps(r["mental_models"]), json.dumps(r["heuristics"]),
                json.dumps(r["vocabulary"]), json.dumps(r["anti_patterns"]),
                json.dumps({"phase": 16, "domain": "frontier_ai_labs_nov2026"}),
            ),
        )

        # Link both PRODUCES and CONSUMES artifacts
        cur.execute(
            """
            INSERT OR REPLACE INTO role_artifacts (id, role_id, artifact_id, direction, frequency, description, metadata_json)
            VALUES (?, ?, ?, 'PRODUCES', 'WEEKLY', ?, '{"phase": 16}');
            """,
            (f"ra_prod_{slug}", role_id, f"art_{r['output_artifact'].lower()}", f"{r['name']} produces {r['output_artifact']}"),
        )
        cur.execute(
            """
            INSERT OR REPLACE INTO role_artifacts (id, role_id, artifact_id, direction, frequency, description, metadata_json)
            VALUES (?, ?, ?, 'CONSUMES', 'DAILY', ?, '{"phase": 16}');
            """,
            (f"ra_cons_{slug}", role_id, f"art_{r['input_artifact'].lower()}", f"{r['name']} consumes {r['input_artifact']}"),
        )

        # 5 Day-to-Day Use Cases (strictly 1 per required cadence, >= 2 inputs, >= 2 outputs)
        for idx, (cadence, suffix, trig) in enumerate(cadence_specs, start=1):
            cur.execute(
                """
                INSERT OR REPLACE INTO role_use_cases (
                    id, role_id, title, cadence, trigger_event, inputs_consumed_json,
                    horizontal_tools_json, vertical_tools_json, cognitive_bottlenecks,
                    output_artifacts_json, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    f"ruc_{role_id}_{idx}", role_id, f"{r['name']}: {suffix}", cadence, trig,
                    json.dumps([r["input_artifact"], "RLVR Verifier & Holdout Eval Telemetry", "Disaggregated Cluster & FDE Shadow Traces"]),
                    json.dumps(["tool_word_processor", "tool_spreadsheet_processor", "tool_communication_triage"]),
                    json.dumps(frontier_tool_ids[:3]),
                    f"Balancing compute/latency rooflines, verifier anti-reward-hacking rigor, and ASL safety invariants for {r['name']}.",
                    json.dumps([f"{r['output_artifact']}_{cadence}_Deliverable", f"{slug}_{cadence}_Verification_Scorecard"]),
                    json.dumps({"role_seniority": r["seniority_level"], "industry": ind_id, "phase": 16}),
                ),
            )

        # 11 Dual-Layer Tooling Bindings (6 Horizontal + 5 Frontier Lab Vertical = 11 exact)
        role_tools = HORIZONTAL_TOOL_IDS + frontier_tool_ids
        for t_idx, tool_id in enumerate(role_tools):
            freq = "PRIMARY_DAILY" if (tool_id in frontier_tool_ids or t_idx < 3) else "FREQUENT_WEEKLY"
            prof = "EXPERT" if (tool_id in frontier_tool_ids or t_idx < 2) else "PROFICIENT"
            cur.execute(
                """
                INSERT INTO role_tooling (id, role_id, tool_id, usage_frequency, proficiency_level, primary_purpose, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(role_id, tool_id) DO UPDATE SET
                    usage_frequency = excluded.usage_frequency,
                    proficiency_level = excluded.proficiency_level,
                    primary_purpose = excluded.primary_purpose;
                """,
                (f"rt_{role_id}_{tool_id}", role_id, tool_id, freq, prof, f"Core Nov 2026 frontier AI lab execution for {r['name']}", '{"phase": 16}'),
            )

        # 6 Acyclic Personal Subagent Swarms
        sixth_code, sixth_label = r["sixth_subagent"]
        swarm_defs = [
            ("MEETING_GRAPH", f"{r['name']} War-Room & Rollout Log Graph", {"upstream": [], "downstream": ["CHIEF_OF_STAFF"], "triggers": ["ablation_sync", "incident_postmortem"]}),
            ("CHIEF_OF_STAFF", f"{r['name']} Pod Chief of Staff", {"upstream": ["MEETING_GRAPH"], "downstream": [sixth_code, "QUANTITATIVE_MODELER"], "triggers": ["compute_allocation", "release_gate"]}),
            (sixth_code, f"{r['name']} {sixth_label}", {"upstream": ["CHIEF_OF_STAFF"], "downstream": ["DOCUMENT_DRAFTER"], "triggers": ["verifier_audit", "asl_control_check"]}),
            ("QUANTITATIVE_MODELER", f"{r['name']} IsoFLOP, Goodput & Eval Modeler", {"upstream": ["CHIEF_OF_STAFF"], "downstream": ["DOCUMENT_DRAFTER", "DECK_PRESENTER"], "triggers": ["scaling_fit", "elo_bootstrap"]}),
            ("DOCUMENT_DRAFTER", f"{r['name']} RFC, Model-Spec & Safety Drafter", {"upstream": [sixth_code, "QUANTITATIVE_MODELER"], "downstream": ["DECK_PRESENTER"], "triggers": ["rfc_synthesis", "safety_case_draft"]}),
            ("DECK_PRESENTER", f"{r['name']} Readiness & FDE Architecture Presenter", {"upstream": ["DOCUMENT_DRAFTER", "QUANTITATIVE_MODELER"], "downstream": [], "triggers": ["board_safety_deck", "fde_exec_readout"]}),
        ]
        for sa_code, sa_name, sa_dag in swarm_defs:
            cur.execute(
                """
                INSERT INTO role_subagent_swarms (
                    id, role_id, subagent_name, subagent_role, system_prompt,
                    tool_mcp_bindings_json, interaction_dag_json, hitl_checkpoint, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(role_id, subagent_role) DO UPDATE SET
                    subagent_name = excluded.subagent_name,
                    system_prompt = excluded.system_prompt,
                    interaction_dag_json = excluded.interaction_dag_json;
                """,
                (
                    f"rss_{role_id}_{sa_code.lower()}", role_id, sa_name, sa_code,
                    f"You are {sa_name} (`{sa_code}`) supporting {r['name']}. Enforce first-principles scaling physics, ungameable outcome verification, canary decontamination, and ASL/AI-Control guardrails.",
                    json.dumps(["mcp://rlvr_verifier_gym", "mcp://inspect_safety_evals", "mcp://kv_inference_telemetry", "mcp://fde_forge_registry"]),
                    json.dumps(sa_dag),
                    f"Mandatory human principal sign-off by {r['name']} before >1K-GPU launches, weight releases, or production customer cutovers.",
                    '{"phase": 16}',
                ),
            )

        # 1 GenAI Build Plan
        cur.execute(
            """
            INSERT INTO role_genai_plans (
                id, role_id, horizontal_genai_spec_json, vertical_genai_spec_json,
                rag_context_architecture, mcp_integrations_json, hitl_guardrails,
                roi_productivity_impact, metadata_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(role_id) DO UPDATE SET
                horizontal_genai_spec_json = excluded.horizontal_genai_spec_json,
                vertical_genai_spec_json = excluded.vertical_genai_spec_json,
                rag_context_architecture = excluded.rag_context_architecture;
            """,
            (
                f"rgp_{role_id}", role_id,
                json.dumps({
                    "word_copilot": f"Pre-registered ablation RFCs, Model Specs, ASL safety cases & FDE runbooks for {r['name']}",
                    "excel_modeler": "IsoFLOP regressions, pass@k Pareto curves, disaggregated TTFT/TPOT goodput & token ROI sheets",
                    "slide_presenter": "Checkpoint readiness gates, Safety Advisory Group readouts & Global 2000 FDE architecture decks",
                    "meeting_dispatcher": "Automated trajectory failure-clustering & training war-room action routing",
                }),
                json.dumps({
                    "domain_system": "Agentic RLVR Gyms + MCP/Computer-Use Harness + Disaggregated KV Serving + Inspect ASL Suite + Enterprise Forge",
                    "capability": "Closed-loop rollout verification, prefix-cached multi-turn tool execution, canary decontamination, and domain student distillation",
                }),
                "Hybrid BM25 lexical + subword LSA semantic RAG indexing experiment commits, kernel traces, MCP schemas, canary registries, and enterprise eval rubrics.",
                json.dumps(["mcp://agentic_rl_gym", "mcp://mcp_runtime_registry", "mcp://disaggregated_kv_serving", "mcp://frontier_inspect_evals", "mcp://fde_posttraining_forge"]),
                f"Explicit human sign-off by {r['name']} required on frontier cluster runs, ASL/Preparedness clearances, and customer production deployments.",
                "50-70% faster hypothesis-to-verified-ablation and enterprise eval-to-production deployment cycle times with zero contamination or reward-hacking regressions.",
                '{"phase": 16}',
            ),
        )

    # 3. Wire Frontier AI Lab REPORTS_TO + Workflow DAG Edges
    for idx, (src_slug, dst_slug, etype, desc) in enumerate(FRONTIER_WORKFLOW_EDGES, start=1):
        cur.execute(
            """
            INSERT OR REPLACE INTO role_edges (
                id, source_role_id, target_role_id, edge_type, description, protocol, cadence, metadata_json
            ) VALUES (?, ?, ?, ?, ?, 'Frontier Pod Checkpoint & Safety Gate Protocol', 'WEEKLY', '{"phase": 16}');
            """,
            (f"edge_p16_{idx}_{src_slug[:22]}_{etype.lower()}", f"role_{src_slug}", f"role_{dst_slug}", etype, desc),
        )

    # 4. Wire realistic employs_role across 26 Tech/Cloud/Semi/Finance/Pharma/Telco/Defense F500 enterprises
    valid_comp_ids = [
        row[0] for row in cur.execute(
            f"SELECT id FROM fortune500_companies WHERE id IN ({','.join('?' for _ in FRONTIER_F500_EMPLOYERS)});",
            FRONTIER_F500_EMPLOYERS,
        ).fetchall()
    ]
    for r in FRONTIER_ROLES_SPECS:
        role_id = f"role_{r['slug']}"
        for comp_id in valid_comp_ids:
            cur.execute(
                """
                INSERT OR IGNORE INTO employs_role (id, company_id, role_id, department, priority_tier, metadata_json)
                VALUES (?, ?, ?, 'Frontier AI Research, Post-Training & Applied FDE', 'STRATEGIC_DIFFERENTIATOR', '{"phase": 16}');
                """,
                (f"emp_{comp_id}_{role_id}", comp_id, role_id),
            )

    conn.commit()
    summary = {
        "tools_seeded": len(FRONTIER_LAB_VERTICAL_TOOLS),
        "roles_seeded": len(FRONTIER_ROLES_SPECS),
        "workflow_edges_seeded": len(FRONTIER_WORKFLOW_EDGES),
        "f500_employers_wired": len(valid_comp_ids),
    }
    if owns_conn:
        conn.close()
    return summary


if __name__ == "__main__":
    res = seed_frontier_labs()
    print(f"SUCCESS: Phase 16 Frontier AI Labs tools & roles seeded: {res}")
