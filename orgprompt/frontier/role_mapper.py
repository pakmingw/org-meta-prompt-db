"""Domain-intelligent deterministic mapper from Real-World Canonical Roles to Nov 2026 Frontier AI Lab Roles."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple


# Maps domain clusters to 3 (frontier_role_slug, join_mechanism, lab_capability_summary, joint_artifact_template, labs)
DOMAIN_JOIN_PROFILES: Dict[str, List[Tuple[str, str, str, str, List[str]]]] = {
    "swe_infra_telecom": [
        (
            "frontier_coding_agent_swe_harness_architect",
            "RL_VERIFIER_AND_EVAL_HARNESS",
            "Containerized multi-repo SWE RL environments with deterministic CI, AST, and chaos-replay verifiers",
            "Hermetic Repository & Network Config Verifier Harness",
            ["Anthropic", "OpenAI", "Mistral AI"],
        ),
        (
            "frontier_context_engineering_mcp_architect",
            "MCP_CONTEXT_AND_TOOL_RUNTIME",
            "Typed Model Context Protocol (MCP) servers exposing live observability, OSS/BSS, and infra state",
            "Production Read/Canary-Write MCP Server Specification",
            ["Anthropic", "Google DeepMind", "Mistral AI"],
        ),
        (
            "frontier_disaggregated_inference_kv_systems_lead",
            "DOMAIN_DISTILLATION_AND_POST_TRAINING",
            "Disaggregated prefill/decode KV-cache routing and speculative decoding for low-latency fleet serving",
            "Sub-50ms Disaggregated KV & FinOps Serving Blueprint",
            ["Google DeepMind", "Meta Superintelligence Labs (MSL) & FAIR", "OpenAI"],
        ),
    ],
    "science_pharma_energy_semi_aero": [
        (
            "frontier_ai_for_science_discovery_lead",
            "WORLD_MODEL_AND_SCIENTIFIC_SIM",
            "Equivariant physics/biomolecular surrogates and closed-loop wet-lab / solver active learning",
            "Physics-Constrained Surrogate & Lab Validation Loop",
            ["Google DeepMind", "Meta Superintelligence Labs (MSL) & FAIR", "Anthropic"],
        ),
        (
            "frontier_test_time_compute_reasoning_rl_lead",
            "RL_VERIFIER_AND_EVAL_HARNESS",
            "Test-time compute scaling graded against formal EDA, AC-OPF, CFD, or PK/PD conservation solvers",
            "Conservation-Law Outcome Verifier & RFT Grader Suite",
            ["OpenAI", "Google DeepMind", "Anthropic"],
        ),
        (
            "frontier_enterprise_distillation_forge_lead",
            "DOMAIN_DISTILLATION_AND_POST_TRAINING",
            "Air-gapped domain post-training and Sparse MoE distillation inside sovereign/ITAR/foundry enclaves",
            "Zero-Egress Sovereign Domain Checkpoint",
            ["Mistral AI", "Meta Superintelligence Labs (MSL) & FAIR"],
        ),
    ],
    "robotics_mfg_media_creator": [
        (
            "frontier_multimodal_world_model_sim_architect",
            "WORLD_MODEL_AND_SCIENTIFIC_SIM",
            "Native audio-video-action 3D world models (Veo/Genie/V-JEPA) for physical sim, VFX, and retention pacing",
            "Action-Conditioned Multimodal World/Timeline Simulator",
            ["Google DeepMind", "Meta Superintelligence Labs (MSL) & FAIR", "OpenAI"],
        ),
        (
            "frontier_context_engineering_mcp_architect",
            "MCP_CONTEXT_AND_TOOL_RUNTIME",
            "Direct MCP tool integration into NLE video timelines, OpenUSD scene graphs, CAD, and PLC/MES buses",
            "Creative/Industrial Tool-Bus MCP Integration Spec",
            ["Anthropic", "Google DeepMind"],
        ),
        (
            "frontier_synthetic_data_curriculum_selfplay_lead",
            "DOMAIN_DISTILLATION_AND_POST_TRAINING",
            "Rubric-verified synthetic edge-case curricula (sim-to-real fuzzing or CTR/AVD hook packaging critics)",
            "Adversarial Curriculum & Packaging Rubric Dataset",
            ["Meta Superintelligence Labs (MSL) & FAIR", "OpenAI", "Google DeepMind"],
        ),
    ],
    "security_risk_legal_gov_health": [
        (
            "frontier_asl_preparedness_control_evaluator",
            "SAFETY_CONTROL_AND_RED_TEAM_GATE",
            "AI Control dual-privilege sandboxing, indirect prompt-injection defense, and ASL/FSF red-team gates",
            "AI Control Defense-in-Depth & Red-Team Assurance Dossier",
            ["Anthropic", "Google DeepMind", "OpenAI"],
        ),
        (
            "frontier_model_character_spec_alignment_lead",
            "DOMAIN_DISTILLATION_AND_POST_TRAINING",
            "Constitutional / Deliberative Alignment over statutory rules with calibrated epistemic abstention",
            "Statutory Model Spec & Calibrated Abstention Policy",
            ["Anthropic", "OpenAI", "Mistral AI"],
        ),
        (
            "frontier_eval_science_benchmark_contamination_lead",
            "RL_VERIFIER_AND_EVAL_HARNESS",
            "Subgroup calibration auditing, contamination forensics, and deterministic statutory/clinical verifiers",
            "Subgroup Calibration & Zero-Hallucination Eval Suite",
            ["Anthropic", "Google DeepMind", "Mistral AI"],
        ),
    ],
    "finance_quant_data_consult_exec": [
        (
            "frontier_test_time_compute_reasoning_rl_lead",
            "RL_VERIFIER_AND_EVAL_HARNESS",
            "Multi-step quantitative reasoning RL verified against Python/SQL double-entry and causal invariants",
            "Code-Verified Financial & Causal Reasoning Grader",
            ["OpenAI", "Anthropic", "Google DeepMind"],
        ),
        (
            "frontier_forward_deployed_ai_engineer_lead",
            "FDE_WORKFLOW_EMBEDDING",
            "Embedded Forward-Deployed AI engineering wiring Personal Subagent Swarms into ERP/VDR/alpha pipelines",
            "Production FDE Enterprise Swarm & ROI Runbook",
            ["OpenAI", "Anthropic", "Mistral AI"],
        ),
        (
            "frontier_long_context_moe_architecture_lead",
            "MCP_CONTEXT_AND_TOOL_RUNTIME",
            "Multi-million-token cross-filing/ledger context synthesis paired with point-in-time MCP data fences",
            "Point-in-Time Long-Context Filing & Ledger Grounding Spec",
            ["Google DeepMind", "Anthropic", "Mistral AI"],
        ),
    ],
    "ops_scm_logistics_retail_gtm_hr": [
        (
            "frontier_agent_post_training_computer_use_lead",
            "MCP_CONTEXT_AND_TOOL_RUNTIME",
            "Browser/OS Computer-Use and MCP action harnesses automating legacy ERP, WMS, customs, and CRM portals",
            "Sandboxed Portal Computer-Use & MCP Action Workflow",
            ["Anthropic", "OpenAI", "Google DeepMind"],
        ),
        (
            "frontier_forward_deployed_ai_engineer_lead",
            "FDE_WORKFLOW_EMBEDDING",
            "Forward-Deployed workflow decomposition turning high-friction human handoffs into gated agent DAGs",
            "Joint FDE + 6-Agent Personal Swarm Execution Topology",
            ["Mistral AI", "OpenAI", "Anthropic"],
        ),
        (
            "frontier_enterprise_distillation_forge_lead",
            "DOMAIN_DISTILLATION_AND_POST_TRAINING",
            "Teacher-to-student distillation and DPO on proprietary enterprise telemetry for sub-second unit economics",
            "Distilled Domain Policy & Unit-Economics SLA Spec",
            ["Meta Superintelligence Labs (MSL) & FAIR", "Mistral AI", "Google DeepMind"],
        ),
    ],
}


def classify_role_domain_bucket(
    slug: str,
    title: str,
    role_archetype: str,
    industry_id: str,
) -> str:
    """Deterministically maps any canonical role into its primary Frontier Join domain profile."""
    s = slug.lower()
    t = title.lower()
    if s.startswith(("cyber_", "sec_", "legal_", "gov_", "health_")) or role_archetype == "risk_compliance":
        return "security_risk_legal_gov_health"
    if s.startswith(("pharma_", "research_", "aero_", "energy_", "semi_", "clin_")) or industry_id in (
        "ind_pharmaceuticals",
        "ind_frontier_research",
        "ind_aerospace_defense",
        "ind_energy_grids",
        "ind_semiconductors_mfg",
    ):
        return "science_pharma_energy_semi_aero"
    if s.startswith(("robotics_", "mfg_", "media_", "creator_")) or industry_id in (
        "ind_autonomous_robotics",
        "ind_creative_media",
    ):
        return "robotics_mfg_media_creator"
    if s.startswith(("infra_", "tech_", "telecom_", "principal_ftth", "chief_orange", "orange_cyber", "principal_5g")) or (
        "architect" in t and industry_id in ("ind_technology_ai", "ind_telecommunications")
    ):
        return "swe_infra_telecom"
    if s.startswith(("fin_", "data_", "consult_", "exec_")) or role_archetype == "executive_strategy":
        return "finance_quant_data_consult_exec"
    return "ops_scm_logistics_retail_gtm_hr"


def select_frontier_joins_for_role(
    role_row: Dict[str, Any],
    available_roles_by_slug: Dict[str, str],
) -> List[Dict[str, Any]]:
    """Returns 2–3 deterministic Frontier Lab join specs for a single canonical role."""
    slug = role_row["slug"]
    title = role_row["name"]
    mission = role_row.get("mission", "")
    archetype = role_row.get("role_archetype", "domain_specialist")
    seniority = role_row.get("seniority_level", "PRINCIPAL_STAFF")
    industry_id = role_row.get("industry_id", "")

    # Cross-lab counterpart links for frontier_* roles themselves (2 distinct counterparts)
    if slug.startswith("frontier_"):
        cross_candidates = [
            ("frontier_eval_science_benchmark_contamination_lead", "RL_VERIFIER_AND_EVAL_HARNESS"),
            ("frontier_asl_preparedness_control_evaluator", "SAFETY_CONTROL_AND_RED_TEAM_GATE"),
            ("frontier_forward_deployed_ai_engineer_lead", "FDE_WORKFLOW_EMBEDDING"),
        ]
        out: List[Dict[str, Any]] = []
        for c_slug, mech in cross_candidates:
            if c_slug != slug and c_slug in available_roles_by_slug and len(out) < 2:
                out.append({
                    "target_slug": c_slug,
                    "target_id": available_roles_by_slug[c_slug],
                    "join_mechanism": mech,
                    "enterprise_pain_point": f"Aligning {title} breakthroughs with production deployment & safety gates.",
                    "frontier_lab_capability": "Cross-pod evaluation forensics, ASL safety gating, and enterprise FDE feedback.",
                    "joint_artifact": f"Cross-Pod Verification & Deployment Gate for {title}",
                    "recommended_labs": ["Anthropic", "OpenAI", "Google DeepMind", "Meta Superintelligence Labs (MSL) & FAIR", "Mistral AI"],
                    "priority_rank": len(out) + 1,
                })
        return out

    bucket = classify_role_domain_bucket(slug, title, archetype, industry_id)
    base_specs = list(DOMAIN_JOIN_PROFILES[bucket])

    # Specialize cluster/hardware & executive orchestration roles so all 16 frontier_* roles get rich coverage
    if any(k in slug for k in ("datacenter", "silicon", "cluster", "fpga", "cleanroom", "thermal")):
        base_specs[2] = (
            "frontier_gigawatt_cluster_tpu_gpu_codesign_lead",
            "FDE_WORKFLOW_EMBEDDING",
            "Silicon-to-cluster fabric, liquid-cooling thermal, and collective-communication co-design",
            "Hardware-Cluster Co-Design & Goodput Optimization Spec",
            ["Google DeepMind", "Meta Superintelligence Labs (MSL) & FAIR", "OpenAI"],
        )
    elif seniority in ("C_SUITE", "VP") and bucket != "swe_infra_telecom":
        base_specs[2] = (
            "frontier_research_engineer_orchestration_lead",
            "FDE_WORKFLOW_EMBEDDING",
            "Multi-agent fleet orchestration uniting executive KPIs with verifiable cross-division swarms",
            "Executive Multi-Agent Fleet & Governance Orchestration Spec",
            ["Anthropic", "OpenAI", "Google DeepMind"],
        )

    fallback_tech = [
        "tech_lead_post_training_rl_specialist",
        "tech_vp_frontier_ai_research",
        "tech_inference_serving_architect",
        "tech_head_of_ai_safety_alignment",
    ]
    short_mission = (mission[:155].rstrip(".") + ".") if mission else f"Executing {title} workflows reliably at scale."

    results: List[Dict[str, Any]] = []
    used_targets = {slug}
    for idx, (f_slug, mech, cap, artifact, labs) in enumerate(base_specs, start=1):
        resolved_slug = f_slug if f_slug in available_roles_by_slug else None
        if resolved_slug is None:
            for fb in fallback_tech:
                if fb in available_roles_by_slug and fb not in used_targets:
                    resolved_slug = fb
                    break
        if resolved_slug is None or resolved_slug in used_targets:
            continue
        used_targets.add(resolved_slug)
        results.append({
            "target_slug": resolved_slug,
            "target_id": available_roles_by_slug[resolved_slug],
            "join_mechanism": mech,
            "enterprise_pain_point": f"[{title}] {short_mission}",
            "frontier_lab_capability": cap,
            "joint_artifact": f"{artifact} ({title})",
            "recommended_labs": labs,
            "priority_rank": idx,
        })
    return results


__all__ = ["DOMAIN_JOIN_PROFILES", "classify_role_domain_bucket", "select_frontier_joins_for_role"]
