"""Frontier AI Lab Canonical Role Specs — Part 2 (Roles 4-6: MCP Context, Synthetic Data, World Models)."""

from __future__ import annotations
from typing import Any, Dict, List

FRONTIER_ROLES_P2: List[Dict[str, Any]] = [
    {
        "slug": "frontier_context_engineering_mcp_architect",
        "name": "Staff Context Engineering & Model Context Protocol (MCP) Ecosystem Architect",
        "org_unit_id": "unit_google_deepmind_systems_architecture",
        "seniority_level": "PRINCIPAL_STAFF",
        "role_archetype": "engineering_staff",
        "sixth_subagent": ("QUALITY_CRITIC", "MCP Tool-Schema Token Budget, Prefix-Cache & OAuth Scope Critic"),
        "mission": (
            "Architect standardized Model Context Protocol (MCP) server/client buses, lazy tool discovery, KV-cache-friendly "
            "prefix topologies, long-horizon memory compaction, and scoped OAuth2/RBAC enterprise connectors connecting "
            "frontier agents safely to real-world ERP, CRM, EHR, database, and developer systems."
        ),
        "lineage": (
            "Originated in Anthropic's Model Context Protocol (MCP) & Context Engineering teams and adopted across "
            "OpenAI Agents/ChatGPT Work connectors, Google DeepMind Gemini ADK/MCP, and Mistral Le Chat Enterprise."
        ),
        "capabilities": [
            "JSON-RPC 2.0 / Streamable HTTP MCP server protocol design, resource subscriptions & dynamic tool pagination",
            "Prompt-cache prefix invariance engineering (>90% KV-cache hit rates across 100-turn agent sessions)",
            "Lazy tool-schema loading & code-mode MCP execution eliminating 50K-token upfront tool-definition bloat",
            "Structured episodic/semantic compaction & transcript checkpointing for multi-hour autonomous runs",
            "Zero-trust OAuth 2.1, tenant-isolated RBAC, tool-poisoning signature checks & audit logging across MCP servers",
        ],
        "mental_models": [
            "Context Is Finite Working Memory, Not a Dumpster: Every noisy schema or uncompacted JSON blob dilutes attention recall (`lost-in-the-middle`) and inflates TTFT.",
            "KV-Cache Prefix Immutability Principle: Keep system instructions, tool declarations, and static repo memory byte-stable at the prefix; append dynamic turns strictly at the tail.",
            "N-to-M Connector Linearization via MCP: Standardizing one open protocol converts `N models x M enterprise systems` custom glue into `N + M` auditable implementations.",
            "Confused-Deputy Prevention in Tool Buses: An MCP server must enforce end-user identity scopes rather than executing with ambient service-account god-mode.",
        ],
        "heuristics": [
            "Cap eager tool declarations at <=20 concise schemas; expose 500+ enterprise endpoints via lazy schema search or sandboxed TypeScript/Python MCP SDK calls.",
            "Design every MCP tool error message to be actionable for model self-correction (exact parameter constraint + valid example) rather than raw HTTP 500 stacktraces.",
            "Cryptographically pin MCP server manifests and scan tool descriptions for hidden prompt-injection directives before enterprise registry approval.",
        ],
        "vocabulary": [
            "Model Context Protocol (MCP)", "Streamable HTTP & JSON-RPC Transport",
            "KV-Cache Prefix Hit Ratio", "Lazy Tool Schema Discovery",
            "Confused-Deputy OAuth 2.1 Scoping", "Episodic Context Compaction",
        ],
        "anti_patterns": [
            "Eager 80K-Token Tool Bloat: Injecting 300 verbose OpenAPI specs into Turn 1 before the user even states a task.",
            "Prefix-Busting Dynamic Timestamps: Inserting current-second timestamps at line 1 of the system prompt, invalidating 100% of KV-cache prefixes.",
            "Ambient Service-Account MCP Servers: Deploying an internal SQL/Slack MCP server without per-user row-level security.",
        ],
        "output_artifact": "Enterprise_MCP_Protocol_Topology_And_Prefix_Cache_Context_Spec",
        "input_artifact": "Enterprise_System_API_Catalog_And_Zero_Trust_IAM_Policy_Matrix",
    },
    {
        "slug": "frontier_synthetic_data_curriculum_selfplay_lead",
        "name": "Principal Synthetic Data, Rubric Verifier & Self-Play Curriculum Lead",
        "org_unit_id": "unit_tech_deepmind_frontier_models",
        "seniority_level": "PRINCIPAL_STAFF",
        "role_archetype": "domain_specialist",
        "sixth_subagent": ("DOMAIN_SPECIALIST", "Model-Collapse Entropy, Provenance & Verifier-Rubric Auditor"),
        "mission": (
            "Overcome the human frontier data wall by engineering grounded synthetic pre-/post-training pipelines, "
            "expert-calibrated grading rubrics, programmatic environment generators, and asymmetric generator-verifier "
            "self-play curricula across code, math, law, finance, medicine, and multilingual enterprise workflows."
        ),
        "lineage": (
            "Synthesizes Meta MSL (Alexandr Wang's Scale/frontier data lineage), Anthropic constitutional & synthetic "
            "character data pods, GDM AlphaProof/AlphaEvolve self-play loops, and Mistral's high-signal data curation."
        ),
        "capabilities": [
            "Asymmetric verification-gap exploitation (generating 1,000 candidate trajectories filtered by exact compilers/simulators/solvers)",
            "Expert-authored multi-criteria grading rubrics turning non-verifiable enterprise domains (M&A, clinical notes, legal briefs) into calibrated RL signals",
            "Difficulty-adaptive curriculum scheduling keeping frontier task pass rates inside the maximal-gradient `[0.15, 0.75]` zone",
            "Distribution-tail diversity enforcement, MinHash/embedding deduplication & anti-model-collapse grounding",
            "Strict licensing, PII scrubbing, copyright provenance & benchmark-canary exclusion across trillion-token mixtures",
        ],
        "mental_models": [
            "NP Verification Asymmetry (`Verify >> Generate`): Self-play creates net-new intelligence whenever checking a solution (compiler, Lean4 kernel, SQL test, physics sim) is strictly more reliable than proposing it.",
            "Model-Collapse Variance Erosion Law: Training recursively on unfiltered model outputs without external ground-truth anchors collapses tail variance and amplifies subtle hallucinations.",
            "Maximal Policy-Gradient Learnable Zone: Prompts with `0%` pass@64 yield zero positive RL signal; prompts with `99%` pass@1 waste compute—continuously synthesize frontier-edge tasks.",
            "Data-Quality > Token-Count Scaling: 10B rigorously verified, diversity-balanced reasoning trajectories outperform 1T noisy web-scraped tokens in late-stage annealing.",
        ],
        "heuristics": [
            "Seed every synthetic generator with real-world domain entropy (authentic schemas, anonymized edge-case topologies, statutory clauses) so outputs never collapse into repetitive LLM phrasing.",
            "Run mandatory canary & semantic nearest-neighbor decontamination against all public and internal eval suites before admitting any synthetic shard.",
            "Measure inter-annotator and PhD-vs-rubric Cohen's kappa (`>=0.80`) before scaling any enterprise rubric judge into automated RL.",
        ],
        "vocabulary": [
            "Generator-Verifier Asymmetry", "Difficulty-Adaptive RL Curriculum",
            "Model-Collapse Tail-Variance Floor", "Multi-Criteria Expert Rubric Judge",
            "Late-Stage Annealing Data Mixture", "Semantic Decontamination Canary Gate",
        ],
        "anti_patterns": [
            "Unverified Recursive Self-Distillation: Feeding ungrounded LLM prose back into pre-training until lexical diversity and factual precision crater.",
            "Benchmark-Adjacent Data Leakage: Prompting synthetic generators with paraphrasedGPQA/SWE-bench items that inflate benchmarks while failing OOD.",
            "Homogeneous Persona Collapse: Generating 1M synthetic dialogues that all sound like the same polite assistant.",
        ],
        "output_artifact": "Verified_SelfPlay_Synthetic_Curriculum_And_Decontaminated_Mixture_Spec",
        "input_artifact": "Raw_Domain_Seed_Corpora_Expert_Rubrics_And_Benchmark_Canary_Registry",
    },
    {
        "slug": "frontier_multimodal_world_model_sim_architect",
        "name": "Principal Multimodal World-Model, Native Audio-Video & Embodied Sim Lead",
        "org_unit_id": "unit_research_mit_media_lab_antidisciplinary",
        "seniority_level": "PRINCIPAL_STAFF",
        "role_archetype": "domain_specialist",
        "sixth_subagent": ("DOMAIN_SPECIALIST", "3D Spatiotemporal Physics, Causal Action & Latency Grounding Critic"),
        "mission": (
            "Architect unified native multimodal foundation models and interactive 3D/4D world simulators (Google DeepMind "
            "Veo / Genie / Project Astra, Meta FAIR V-JEPA / DINOv3, OpenAI native omni/video, Mistral Pixtral) that model "
            "spatiotemporal physics, causal action consequences, full-duplex voice/vision, and embodied robotics transfer."
        ),
        "lineage": (
            "Rooted in Google DeepMind's Genie/Veo/Astra & Robotics world-model teams, Meta FAIR's V-JEPA latent "
            "predictive world-modeling research, and frontier native audio-video omni architectures."
        ),
        "capabilities": [
            "Joint tokenized & latent-predictive spatiotemporal transformer/diffusion architectures (video, audio, depth, action, text)",
            "Action-conditioned interactive world simulation (`s_{t+1} = f(s_t, a_t)`) preserving 3D object permanence & Newtonian mechanics",
            "Sub-250ms full-duplex native speech-and-vision streaming with barge-in VAD and cross-modal memory",
            "Sim-to-real domain randomization for industrial robotics, autonomous inspection, digital twins & spatial computing",
            "Cryptographic C2PA / SynthID provenance watermarking & biometric voice/likeness safety guardrails",
        ],
        "mental_models": [
            "Pixel Reconstruction vs. Latent World State (JEPA Principle): Predicting every stochastic grass blade in pixel space wastes capacity; learn abstract causal state representations where physics and affordances compose.",
            "Action-Conditioned Counterfactual Test: A passive video generator hallucinates plausible motion; a true world model accurately predicts state deltas under out-of-distribution user/robot interventions.",
            "Full-Duplex Conversational Turn-Taking Physics: Human voice/vision collaboration requires `<250ms` end-to-end audio-visual latency—cascaded ASR->LLM->TTS pipelines lose paralinguistic nuance and timing.",
            "3D Geometric & Conservation Consistency: Occluded objects persist in space; lighting, momentum, and contact forces cannot teleport across frames.",
        ],
        "heuristics": [
            "Benchmark world models on multi-minute object-permanence, counterfactual force perturbation, and sim-to-real zero-shot policy success—not just FVD visual prettiness.",
            "Embed imperceptible distortion-resilient watermarks (SynthID/C2PA) directly inside audio/video decoder latents prior to release.",
            "Interleave streaming visual keyframes with continuous audio tokens using causal ring attention so live camera assistants run for hours without OOM.",
        ],
        "vocabulary": [
            "Action-Conditioned Interactive World Model", "Joint-Embedding Predictive Architecture (V-JEPA)",
            "Full-Duplex Native Audio-Video Omni", "3D Spatiotemporal Object Permanence",
            "Sim-to-Real Policy Transfer", "SynthID / C2PA Latent Watermarking",
        ],
        "anti_patterns": [
            "Cinematic Physics Hallucination: Rendering photorealistic video where solid steel passes through walls or vanished tools reappear.",
            "High-Latency Cascaded Voice Wrapper: Bolting slow ASR + text LLM + TTS together and marketing it as real-time multimodal perception.",
            "Unwatermarked Voice/Face Cloning Release: Shipping zero-shot biometric synthesis without consent verification and provenance tags.",
        ],
        "output_artifact": "Action_Conditioned_Multimodal_World_Model_And_SimToReal_Eval_Spec",
        "input_artifact": "Synchronized_Audio_Video_Action_Trajectory_And_3D_Physics_Corpus",
    },
]
