"""Aggregated Frontier AI Lab Tools, 16 Canonical Roles, Workflow DAG & F500 Employers (Phase 16)."""

from __future__ import annotations
from typing import Any, Dict, List, Tuple

from orgprompt.db.frontier_tools_spec import FRONTIER_LAB_VERTICAL_TOOLS
from orgprompt.db.frontier_roles_p1 import FRONTIER_ROLES_P1
from orgprompt.db.frontier_roles_p2 import FRONTIER_ROLES_P2
from orgprompt.db.frontier_roles_p3 import FRONTIER_ROLES_P3
from orgprompt.db.frontier_roles_p4 import FRONTIER_ROLES_P4
from orgprompt.db.frontier_roles_p5a import FRONTIER_ROLES_P5A
from orgprompt.db.frontier_roles_p5b import FRONTIER_ROLES_P5B

FRONTIER_ROLES_SPECS: List[Dict[str, Any]] = (
    FRONTIER_ROLES_P1
    + FRONTIER_ROLES_P2
    + FRONTIER_ROLES_P3
    + FRONTIER_ROLES_P4
    + FRONTIER_ROLES_P5A
    + FRONTIER_ROLES_P5B
)

# 16 REPORTS_TO + 50 Workflow DAG edges (each frontier_* role gets 1 REPORTS_TO + 3..4 outgoing workflow edges)
FRONTIER_WORKFLOW_EDGES: List[Tuple[str, str, str, str]] = [
    # 1. REPORTS_TO hierarchy anchoring into Frontier AI Research, Safety, Infra & Science leadership
    ("frontier_test_time_compute_reasoning_rl_lead", "tech_vp_frontier_ai_research", "REPORTS_TO", "Reports RLVR & test-time compute breakthroughs to VP of Frontier AI Research"),
    ("frontier_agent_post_training_computer_use_lead", "tech_vp_frontier_ai_research", "REPORTS_TO", "Reports OS/browser agent post-training & CUA safety metrics to VP of Frontier AI Research"),
    ("frontier_coding_agent_swe_harness_architect", "tech_vp_frontier_ai_research", "REPORTS_TO", "Reports autonomous SDLC harness & SWE-bench pass rates to VP of Frontier AI Research"),
    ("frontier_context_engineering_mcp_architect", "tech_chief_cloud_infrastructure_architect", "REPORTS_TO", "Reports MCP protocol ecosystem & prefix-cache serving topology to Chief Cloud Architect"),
    ("frontier_synthetic_data_curriculum_selfplay_lead", "tech_director_pretraining_program", "REPORTS_TO", "Reports synthetic self-play curricula & decontaminated mixtures to Pretraining Director"),
    ("frontier_multimodal_world_model_sim_architect", "tech_vp_frontier_ai_research", "REPORTS_TO", "Reports 3D/4D world-model physics & native omni checkpoints to VP of Frontier AI Research"),
    ("frontier_long_context_moe_architecture_lead", "tech_director_pretraining_program", "REPORTS_TO", "Reports Sparse MoE, MLA long-context & IsoFLOP scaling laws to Pretraining Director"),
    ("frontier_disaggregated_inference_kv_systems_lead", "tech_chief_cloud_infrastructure_architect", "REPORTS_TO", "Reports disaggregated prefill/decode & KV-pool goodput SLAs to Chief Cloud Architect"),
    ("frontier_gigawatt_cluster_tpu_gpu_codesign_lead", "tech_chief_cloud_infrastructure_architect", "REPORTS_TO", "Reports gigawatt training cluster uptime, SDC & silicon co-design to Chief Cloud Architect"),
    ("frontier_research_engineer_orchestration_lead", "tech_vp_frontier_ai_research", "REPORTS_TO", "Reports multi-agent orchestration & ablation velocity to VP of Frontier AI Research"),
    ("frontier_model_character_spec_alignment_lead", "tech_head_of_ai_safety_alignment", "REPORTS_TO", "Reports Constitutional/Model Spec character & anti-sycophancy to Head of AI Safety"),
    ("frontier_asl_preparedness_control_evaluator", "tech_head_of_ai_safety_alignment", "REPORTS_TO", "Reports ASL-3/ASL-4 CBRN/Cyber red-team & AI Control clearances to Head of AI Safety"),
    ("frontier_eval_science_benchmark_contamination_lead", "tech_head_of_ai_safety_alignment", "REPORTS_TO", "Reports sealed holdout evals & contamination forensics to Head of AI Safety"),
    ("frontier_forward_deployed_ai_engineer_lead", "tech_vp_frontier_ai_research", "REPORTS_TO", "Reports enterprise FDE workflow deployments & OOD RL feedback to VP of Frontier AI Research"),
    ("frontier_enterprise_distillation_forge_lead", "tech_chief_cloud_infrastructure_architect", "REPORTS_TO", "Reports enterprise custom RFT/distillation & sovereign VPC models to Chief Cloud Architect"),
    ("frontier_ai_for_science_discovery_lead", "research_director_general_cern", "REPORTS_TO", "Reports biomolecular/materials discovery & wet-lab validation to Frontier Science Leadership"),
    # 2. Outgoing Workflow DAG edges (3 per frontier_* role = 48 edges -> out_degree = 1+2+1+3 = 7 on every frontier role!)
    ("frontier_test_time_compute_reasoning_rl_lead", "frontier_coding_agent_swe_harness_architect", "HANDS_OFF_TO", "Delivers RLVR reasoning policy checkpoints for SWE repo-agent harness integration"),
    ("frontier_test_time_compute_reasoning_rl_lead", "frontier_disaggregated_inference_kv_systems_lead", "COLLABORATES_WITH", "Co-optimizes dynamic thinking-token budgets with speculative decoding & KV pools"),
    ("frontier_test_time_compute_reasoning_rl_lead", "frontier_synthetic_data_curriculum_selfplay_lead", "CHALLENGES_OR_AUDITS", "Audits verifier rubrics for reward-hacking loopholes and pass@k entropy collapse"),
    ("frontier_agent_post_training_computer_use_lead", "frontier_context_engineering_mcp_architect", "COLLABORATES_WITH", "Unifies GUI pixel actions with structured MCP tool-call fallback protocols"),
    ("frontier_agent_post_training_computer_use_lead", "frontier_forward_deployed_ai_engineer_lead", "HANDS_OFF_TO", "Hands off computer-using agent checkpoints for legacy ERP/Citrix enterprise pods"),
    ("frontier_agent_post_training_computer_use_lead", "frontier_model_character_spec_alignment_lead", "COLLABORATES_WITH", "Enforces untrusted DOM/pixel prompt-injection hierarchy & irreversible HITL gates"),
    ("frontier_coding_agent_swe_harness_architect", "frontier_context_engineering_mcp_architect", "COLLABORATES_WITH", "Co-designs AGENTS.md/CLAUDE.md compaction & lazy MCP repo tool schemas"),
    ("frontier_coding_agent_swe_harness_architect", "frontier_forward_deployed_ai_engineer_lead", "HANDS_OFF_TO", "Delivers hermetic autonomous SDLC harnesses for Global 2000 codebase migrations"),
    ("frontier_coding_agent_swe_harness_architect", "frontier_research_engineer_orchestration_lead", "COLLABORATES_WITH", "Scales Firecracker SWE verification gyms across 10,000+ parallel actor workers"),
    ("frontier_context_engineering_mcp_architect", "frontier_disaggregated_inference_kv_systems_lead", "COLLABORATES_WITH", "Aligns byte-stable MCP prompt prefixes with RadixAttention distributed KV caching"),
    ("frontier_context_engineering_mcp_architect", "frontier_forward_deployed_ai_engineer_lead", "HANDS_OFF_TO", "Provides zero-trust OAuth 2.1 MCP connector templates for customer ERP/CRM/EHR stacks"),
    ("frontier_context_engineering_mcp_architect", "frontier_coding_agent_swe_harness_architect", "REVIEWS_AND_GATES", "Gates eager tool-schema token budgets & confused-deputy permission boundaries"),
    ("frontier_synthetic_data_curriculum_selfplay_lead", "frontier_test_time_compute_reasoning_rl_lead", "HANDS_OFF_TO", "Supplies difficulty-calibrated verifiable self-play curricula in [0.15, 0.75] pass zone"),
    ("frontier_synthetic_data_curriculum_selfplay_lead", "frontier_long_context_moe_architecture_lead", "HANDS_OFF_TO", "Delivers decontaminated late-stage annealing mixtures for frontier MoE runs"),
    ("frontier_synthetic_data_curriculum_selfplay_lead", "frontier_enterprise_distillation_forge_lead", "COLLABORATES_WITH", "Co-builds domain-rubric synthetic trace generators for sovereign student distillation"),
    ("frontier_multimodal_world_model_sim_architect", "frontier_agent_post_training_computer_use_lead", "HANDS_OFF_TO", "Provides native audio-video & screen-dynamics perception encoders for live agents"),
    ("frontier_multimodal_world_model_sim_architect", "frontier_ai_for_science_discovery_lead", "COLLABORATES_WITH", "Shares 3D/4D spatiotemporal physics & PDE surrogate representations"),
    ("frontier_multimodal_world_model_sim_architect", "frontier_disaggregated_inference_kv_systems_lead", "COLLABORATES_WITH", "Co-engineers sub-250ms full-duplex streaming audio/video causal ring attention"),
    ("frontier_long_context_moe_architecture_lead", "frontier_test_time_compute_reasoning_rl_lead", "HANDS_OFF_TO", "Delivers pretrained Sparse MoE + MLA 1M-context base checkpoints for RLVR"),
    ("frontier_long_context_moe_architecture_lead", "frontier_disaggregated_inference_kv_systems_lead", "COLLABORATES_WITH", "Co-designs MLA KV-compression & MTP heads for lossless speculative serving"),
    ("frontier_long_context_moe_architecture_lead", "frontier_gigawatt_cluster_tpu_gpu_codesign_lead", "COLLABORATES_WITH", "Aligns expert-parallel routing arity with NVLink72 / TPU torus bisection bandwidth"),
    ("frontier_disaggregated_inference_kv_systems_lead", "frontier_forward_deployed_ai_engineer_lead", "HANDS_OFF_TO", "Provides high-goodput disaggregated serving & sovereign VPC deployment engines"),
    ("frontier_disaggregated_inference_kv_systems_lead", "frontier_enterprise_distillation_forge_lead", "COLLABORATES_WITH", "Co-tunes FP8/NVFP4 quantized student architectures & multi-tenant LoRA serving"),
    ("frontier_disaggregated_inference_kv_systems_lead", "tech_inference_serving_architect", "REVIEWS_AND_GATES", "Gates TTFT/TPOT tail-latency SLAs & lossless speculative verification accuracy"),
    ("frontier_gigawatt_cluster_tpu_gpu_codesign_lead", "frontier_long_context_moe_architecture_lead", "HANDS_OFF_TO", "Delivers verified 100K+ accelerator 5D-parallelism & sub-minute fault-recovery fabric"),
    ("frontier_gigawatt_cluster_tpu_gpu_codesign_lead", "tech_principal_distributed_training_engineer", "COLLABORATES_WITH", "Co-executes asynchronous in-memory checkpointing & collective communication overlap"),
    ("frontier_gigawatt_cluster_tpu_gpu_codesign_lead", "tech_principal_silicon_microarchitect", "CHALLENGES_OR_AUDITS", "Audits HBM4 bandwidth ratios & Silent Data Corruption (SDC) silicon checksums"),
    ("frontier_research_engineer_orchestration_lead", "frontier_test_time_compute_reasoning_rl_lead", "COLLABORATES_WITH", "Eliminates actor-learner rollout stragglers & orchestrates IsoFLOP ablation ladders"),
    ("frontier_research_engineer_orchestration_lead", "frontier_coding_agent_swe_harness_architect", "HANDS_OFF_TO", "Promotes validated planner-worker-auditor swarm runtimes into production SDKs"),
    ("frontier_research_engineer_orchestration_lead", "frontier_eval_science_benchmark_contamination_lead", "COLLABORATES_WITH", "Automates continuous per-commit holdout evaluation & regression gating"),
    ("frontier_model_character_spec_alignment_lead", "frontier_test_time_compute_reasoning_rl_lead", "REVIEWS_AND_GATES", "Gates frontier reasoning policies on deliberative alignment, honesty & anti-sycophancy"),
    ("frontier_model_character_spec_alignment_lead", "tech_mechanistic_interpretability_researcher", "COLLABORATES_WITH", "Applies SAE feature probes to detect deceptive alignment or evaluation sandbagging"),
    ("frontier_model_character_spec_alignment_lead", "frontier_asl_preparedness_control_evaluator", "COLLABORATES_WITH", "Co-defines safe-completion vs. catastrophic-harm refusal thresholds"),
    ("frontier_asl_preparedness_control_evaluator", "frontier_test_time_compute_reasoning_rl_lead", "CHALLENGES_OR_AUDITS", "Red-teams frontier checkpoints for ASL-3/ASL-4 CBRN, cyber & autonomy uplift"),
    ("frontier_asl_preparedness_control_evaluator", "frontier_coding_agent_swe_harness_architect", "REVIEWS_AND_GATES", "Enforces AI Control trusted-monitoring & egress locks on autonomous SWE sandboxes"),
    ("frontier_asl_preparedness_control_evaluator", "tech_ai_red_team_penetration_lead", "COLLABORATES_WITH", "Executes maximum-scaffolding offensive cyber CTF & model-weight exfiltration drills"),
    ("frontier_eval_science_benchmark_contamination_lead", "frontier_synthetic_data_curriculum_selfplay_lead", "CHALLENGES_OR_AUDITS", "Audits synthetic shards via canary UUIDs & perplexity-cliff contamination forensics"),
    ("frontier_eval_science_benchmark_contamination_lead", "frontier_long_context_moe_architecture_lead", "REVIEWS_AND_GATES", "Gates architectural claims on sealed dynamic holdouts & style-controlled Elo"),
    ("frontier_eval_science_benchmark_contamination_lead", "frontier_forward_deployed_ai_engineer_lead", "COLLABORATES_WITH", "Co-constructs GDPval-grade economically grounded enterprise workflow benchmarks"),
    ("frontier_forward_deployed_ai_engineer_lead", "frontier_enterprise_distillation_forge_lead", "HANDS_OFF_TO", "Hands off anonymized customer golden evals & shadow traces for Forge distillation"),
    ("frontier_forward_deployed_ai_engineer_lead", "frontier_agent_post_training_computer_use_lead", "CHALLENGES_OR_AUDITS", "Feeds real-world Fortune 500 ERP/EHR OOD failure modes back into lab RLVR gyms"),
    ("frontier_forward_deployed_ai_engineer_lead", "frontier_context_engineering_mcp_architect", "COLLABORATES_WITH", "Co-architects production customer MCP servers, RBAC scopes & cascade routers"),
    ("frontier_enterprise_distillation_forge_lead", "frontier_forward_deployed_ai_engineer_lead", "HANDS_OFF_TO", "Delivers 10x-faster domain-distilled student checkpoints for sovereign VPC rollout"),
    ("frontier_enterprise_distillation_forge_lead", "frontier_disaggregated_inference_kv_systems_lead", "HANDS_OFF_TO", "Hands off multi-tenant LoRA & quantized student weights for low-TTFT serving"),
    ("frontier_enterprise_distillation_forge_lead", "frontier_eval_science_benchmark_contamination_lead", "COLLABORATES_WITH", "Verifies zero catastrophic forgetting across domain & general holdout suites"),
    ("frontier_ai_for_science_discovery_lead", "frontier_test_time_compute_reasoning_rl_lead", "COLLABORATES_WITH", "Couples evolutionary/RL search with exact DFT, Lean4 & physics conservation verifiers"),
    ("frontier_ai_for_science_discovery_lead", "frontier_asl_preparedness_control_evaluator", "REVIEWS_AND_GATES", "Screens de novo biomolecular candidates against pathogen/toxin biosecurity gates"),
    ("frontier_ai_for_science_discovery_lead", "frontier_gigawatt_cluster_tpu_gpu_codesign_lead", "COLLABORATES_WITH", "Scales all-atom diffusion & neural PDE surrogates across exascale GPU/TPU pods"),
]

FRONTIER_F500_EMPLOYERS: List[str] = [
    "f500_alphabet", "f500_microsoft", "f500_meta_platforms", "f500_nvidia",
    "f500_amazon_com", "f500_apple", "f500_ibm", "f500_oracle",
    "f500_salesforce", "f500_cisco_systems", "f500_dell_technologies", "f500_hewlett_packard_enterprise",
    "f500_intel", "f500_advanced_micro_devices", "f500_qualcomm", "f500_broadcom",
    "f500_jpmorgan_chase", "f500_goldman_sachs_group", "f500_morgan_stanley",
    "f500_eli_lilly", "f500_pfizer", "f500_merck",
    "f500_verizon_communications", "f500_at_t", "f500_lockheed_martin", "f500_orange_france",
]
