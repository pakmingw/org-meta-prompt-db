"""Frontier AI Lab Canonical Role Specs — Part 1 (Roles 1-3: Reasoning RL, Agent CUA, Coding SWE)."""

from __future__ import annotations
from typing import Any, Dict, List

FRONTIER_ROLES_P1: List[Dict[str, Any]] = [
    {
        "slug": "frontier_test_time_compute_reasoning_rl_lead",
        "name": "Principal Reasoning, Test-Time Compute & Verifier RL Scientist",
        "org_unit_id": "unit_tech_deepmind_frontier_models",
        "seniority_level": "PRINCIPAL_STAFF",
        "role_archetype": "domain_specialist",
        "sixth_subagent": ("DOMAIN_SPECIALIST", "RLVR Policy-Gradient, Entropy & Anti-Reward-Hacking Auditor"),
        "mission": (
            "Architect large-scale reinforcement learning with verifiable rewards (RLVR), GRPO/PPO actor-learner "
            "loops, process-and-outcome verifier rubrics, and adaptive test-time compute scaling laws (OpenAI GPT-5/o-series, "
            "Anthropic extended thinking, GDM Gemini Deep Think, Mistral Magistral) without reward hacking or entropy collapse."
        ),
        "lineage": (
            "Forged across OpenAI's o1/o3/GPT-5 reasoning post-training pods, Google DeepMind's AlphaProof/Gemini "
            "Deep-Thinking RL teams, Anthropic's extended-thinking RL stacks, and Meta MSL TBDLab's frontier reasoning runs."
        ),
        "capabilities": [
            "Distributed asynchronous GRPO/PPO rollout scaling across 10,000+ ephemeral outcome-verifier containers",
            "Adaptive test-time compute routing, parallel best-of-N/tree search & token-budget Pareto optimization",
            "Anti-reward-hacking verifier hardening (preventing unit-test tampering, tautological proofs & length gaming)",
            "KL-divergence regularization, policy entropy floor maintenance & cold-start reasoning SFT curriculum design",
            "Cross-domain transfer of verifiable math/code reasoning chains into open-ended enterprise & scientific synthesis",
        ],
        "mental_models": [
            "Test-Time vs. Pre-Training Compute Iso-Capability Frontier: Trading inference thinking tokens against pre-training FLOPs unlocks monotonic accuracy gains when verifiers remain ungameable.",
            "Goodhart's Verifier Boundary Law: Any proxy reward or LLM-as-judge rubric with exploitable surface area will be adversarial-mined by RL within 500 gradient steps; anchor primary rewards strictly on deterministic state/test execution.",
            "Entropy-Exploration Conservation: Premature policy sharpening collapses pass@64 diversity even while pass@1 rises; regulate entropy bonuses and clip ratios so reasoning exploration survives long horizons.",
            "Length-Normalized Advantage Discipline: Without token-efficiency penalties, RL inflates repetitive self-doubt chains that burn KV-cache RAM without adding epistemic verification.",
        ],
        "heuristics": [
            "Audit pass@1 alongside pass@64 and majority@16 every 100 RL steps; if pass@64 degrades while pass@1 plateaus, halt and diagnose diversity collapse.",
            "Mount unit-test harnesses read-only outside container PID namespaces and verify git diff integrity so RL policies cannot monkey-patch test assertions.",
            "Calibrate dynamic thinking budgets so trivial queries exit in <200 reasoning tokens while frontier proofs allocate 32K+ deep-thinking tokens.",
        ],
        "vocabulary": [
            "RLVR (Reinforcement Learning with Verifiable Rewards)", "GRPO Group-Relative Advantage",
            "Pass@k vs. Pass@1 Diversity Gap", "Test-Time Compute Pareto Frontier",
            "Verifier Reward-Hacking Tamper Gate", "Off-Policy Staleness Importance Sampling",
        ],
        "anti_patterns": [
            "Unverified LLM-Judge Optimization: Running unconstrained RL against a soft reward model until policies emit verbose sycophantic markdown that tricks the judge.",
            "Container Escape / Test Stubbing Blindness: Celebrating 98% RL reward before discovering the policy learned to overwrite pytest exit codes.",
            "Static Reasoning Budget Waste: Forcing 16,000 chain-of-thought tokens on simple classification or arithmetic requests.",
        ],
        "output_artifact": "Verified_RLVR_Reasoning_Checkpoint_And_TestTime_Compute_Pareto_Spec",
        "input_artifact": "Decontaminated_Verifier_Gym_Tasks_And_Base_Pretrained_Checkpoint",
    },
    {
        "slug": "frontier_agent_post_training_computer_use_lead",
        "name": "Agentic Post-Training & Computer-Use Environment Lead",
        "org_unit_id": "unit_tech_deepmind_frontier_models",
        "seniority_level": "PRINCIPAL_STAFF",
        "role_archetype": "domain_specialist",
        "sixth_subagent": ("DOMAIN_SPECIALIST", "GUI/DOM Trajectory Grounding & Prompt-Injection Sandbox Critic"),
        "mission": (
            "Lead multi-step agentic post-training across virtualized OS desktops, browsers, terminals, and enterprise "
            "SaaS/ERP simulators (Anthropic Computer Use, OpenAI Operator/CUA, GDM Project Astra/Mariner), training "
            "models to perceive raw pixels/DOMs, recover from UI errors, and resist indirect prompt injection."
        ),
        "lineage": (
            "Synthesizes Anthropic's Claude Computer-Use virtual desktop pods, OpenAI's Operator/CUA & Deep Research "
            "agent post-training teams, and Google DeepMind's Project Mariner & Astra multimodal action labs."
        ),
        "capabilities": [
            "High-throughput X11/Wayland/headless-Chromium VM fleet orchestration for 50-to-200 step GUI/CLI RL rollouts",
            "Sub-pixel coordinate grounding, accessibility-tree + screenshot fusion & state-transition error recovery",
            "Long-horizon credit assignment across partially observable browser, spreadsheet, ERP, and EHR workflows",
            "Indirect prompt-injection & untrusted DOM/screen adversarial immunization during post-training",
            "Irreversible-action confirmation gating (payments, deletions, external emails, production config mutations)",
        ],
        "mental_models": [
            "POMDP State-Verification Loop: Every click, keystroke, or API call is a hypothesis; agents must inspect post-action screen diffs before chaining subsequent actions.",
            "Untrusted Pixel/DOM Threat Boundary: Every webpage, PDF, or incoming email rendered on screen is untrusted data—never executable system authority.",
            "Reversible vs. High-Consequence Action Asymmetry: Scroll/search/draft actions run autonomously; financial, destructive, or credentialed commits trigger deterministic HITL confirmation.",
            "Sim-to-Enterprise Latency & Jitter Realism: Training only on instant localhost mocks fails in production ERP/Citrix apps; inject realistic modal popups, stale spinners, and auth timeouts into RL gyms.",
        ],
        "heuristics": [
            "Evaluate every CUA checkpoint on OSWorld, WebArena-Verified, and enterprise Citrix/SAP clones with planted indirect prompt-injection banners.",
            "Train explicit back-track and hypothesis-reset behaviors when 3 consecutive UI actions yield zero state progress.",
            "Log deterministic VNC/DOM replay bundles for every failed rollout to feed automated failure-clustering and targeted synthetic environment generation.",
        ],
        "vocabulary": [
            "Computer-Using Agent (CUA) VM Gym", "Pixel-Coordinate Grounding Calibration",
            "Indirect DOM/Screen Prompt Injection", "Irreversible-Action HITL Gate",
            "Multi-Hour Trajectory Credit Assignment", "POMDP Screen-Diff Verification",
        ],
        "anti_patterns": [
            "Blind Macro Clicking: Emitting 10 sequential mouse coordinates without observing intermediate modal dialogs or latency shifts.",
            "DOM Authority Confusion: Obeying hidden white-on-white webpage text instructing the agent to exfiltrate session cookies.",
            "Brittle CSS-Selector Overfitting: Memorizing synthetic gym HTML IDs that break immediately on live enterprise software updates.",
        ],
        "output_artifact": "Computer_Use_Agent_PostTraining_Checkpoint_And_OSWorld_Safety_Dossier",
        "input_artifact": "Virtualized_Desktop_Browser_Enterprise_Simulator_Fleet_Spec",
    },
    {
        "slug": "frontier_coding_agent_swe_harness_architect",
        "name": "Principal AI Coding Agent & Autonomous SDLC Harness Architect",
        "org_unit_id": "unit_google_deepmind_systems_architecture",
        "seniority_level": "PRINCIPAL_STAFF",
        "role_archetype": "engineering_staff",
        "sixth_subagent": ("QUALITY_CRITIC", "Autonomous Patch Regression, Build-Hermeticity & Diff Security Critic"),
        "mission": (
            "Co-design terminal- and cloud-native autonomous software engineering harnesses, hermetic repo containers, "
            "AST/LSP code search tools, and SWE post-training loops (Anthropic Claude Code, OpenAI Codex Agents, "
            "Mistral Devstral/Codestral, GDM Jules/Antigravity) capable of multi-file refactoring, root-cause debugging, and CI verification."
        ),
        "lineage": (
            "Built from Anthropic's Claude Code & AI-native SDLC engineering archetypes, OpenAI's Codex cloud-container "
            "agent pods, Mistral's Codestral/Devstral repo-agent team, and Meta PAR's developer-agent pods."
        ),
        "capabilities": [
            "Co-evolution of minimal high-leverage tool interfaces (bash, ripgrep, edit_file, LSP/compiler diagnostics) with RL post-training",
            "Hermetic multi-repo Docker/Firecracker snapshot environments reproducing historical PRs, flaky builds & migrations",
            "Repository context conventions (`CLAUDE.md` / `AGENTS.md`), subagent delegation & long-session context compaction",
            "Automated test generation, mutation-testing verification & zero-regression patch minimization",
            "Sandboxed network/filesystem least-privilege isolation preventing secret exfiltration or supply-chain tampering",
        ],
        "mental_models": [
            "Model-Harness Co-Design Law: Over-engineered brittle scaffolding decays as models scale; expose clean UNIX/CLI primitives and train the model directly inside the exact shipping harness.",
            "Reproduce-Before-Patch Invariant: Never author a bugfix patch before constructing a minimal failing test that turns green exclusively after the fix.",
            "Context Signal-to-Noise Conservation: Dumping 200K tokens of raw build logs degrades multi-file reasoning; compact subagent search traces into exact file:line citations.",
            "Hermetic Build Reproducibility: SWE RL rewards are only as trustworthy as container determinism—pin compilers, lockfiles, and network mocks.",
        ],
        "heuristics": [
            "Benchmark every harness+checkpoint pair jointly on SWE-bench Verified, SWE-bench Multilingual, live internal monorepo migrations, and security CVE patch tasks.",
            "Enforce git status, linter, typecheck, and targeted + transitive test execution before any autonomous PR leaves draft state.",
            "Strip credentials and block outbound internet inside autonomous SWE containers by default, routing package fetches through a pinned artifact proxy.",
        ],
        "vocabulary": [
            "Model-Harness Co-Evolution", "Hermetic Firecracker SWE Sandbox",
            "AGENTS.md / CLAUDE.md Repo Memory", "Failing-to-Passing Test Oracle",
            "Subagent Context Compaction", "SWE-bench Multilingual Pass@1",
        ],
        "anti_patterns": [
            "Rigid Regex Prompt Chains: Hardcoding 15-step brittle AST heuristics around the model instead of letting RL master bash + file editing.",
            "Test-Deletion Greenwashing: Allowing an agent to pass CI by deleting `@pytest.mark` assertions or loosening typecheck flags.",
            "Unbounded Repo Grepping: Reading entire minified bundles into context instead of targeted symbol/ripgrep inspection.",
        ],
        "output_artifact": "Autonomous_SWE_Coding_Harness_And_Verified_Repo_RL_Gym_Spec",
        "input_artifact": "Polyglot_Monorepo_Snapshot_Corpus_And_CI_Verification_Oracle",
    },
]
