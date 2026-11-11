"""Nov 2026 Frontier AI Lab Vertical Domain Tooling Specifications (Phase 16)."""

from __future__ import annotations
from typing import Any, Dict, List

FRONTIER_LAB_VERTICAL_TOOLS: List[Dict[str, Any]] = [
    {
        "id": "tool_agentic_rl_gym_verifiers",
        "slug": "agentic_rl_gym_verifiers",
        "name": "Agentic RL Gyms, SWE Sandboxes & Outcome Verifier Harnesses",
        "category": "VERTICAL_DOMAIN",
        "archetype": "AGENTIC_RL_OUTCOME_VERIFIER_GYM",
        "vendor_examples": [
            "OpenAI RLVR & Codex Multi-Container Verifier Gyms",
            "Anthropic Constitutional & SWE Sandbox RL Harnesses",
            "Google DeepMind Pathways Agentic RL & Deep-Thinking Loops",
            "Prime Intellect / OpenRLHF / verl Distributed GRPO-PPO Rollout Engine",
        ],
        "typical_artifacts": [
            "Containerized Multi-Turn RL Trajectory & Unit-Test Reward Logs",
            "Anti-Reward-Hacking Rubric & Deterministic State-Diff Verifiers",
            "Test-Time Compute Pass@k vs. Token-Budget Pareto Curves",
            "Asynchronous Actor-Learner Off-Policy Rollout Checkpoints",
        ],
        "description": (
            "Ephemeral containerized software, browser, math, and enterprise simulator gyms "
            "pairing multi-step agent trajectories with deterministic unit-test, formal-proof, "
            "and rubric outcome verifiers for GRPO/PPO reinforcement learning."
        ),
    },
    {
        "id": "tool_mcp_context_computer_use_runtime",
        "slug": "mcp_context_computer_use_runtime",
        "name": "Model Context Protocol (MCP), Computer-Use & Browser/OS Action Harnesses",
        "category": "VERTICAL_DOMAIN",
        "archetype": "MCP_CONTEXT_AND_OS_ACTION_HARNESS",
        "vendor_examples": [
            "Anthropic Model Context Protocol (MCP) SDK & Registry",
            "Claude Code & Claude Computer-Use X11/Wayland Virtual Desktop",
            "OpenAI Operator CUA & Agents SDK / AGENTS.md Runtime",
            "Google DeepMind Project Astra Live Multimodal Action Harness",
        ],
        "typical_artifacts": [
            "Versioned MCP Server JSON-RPC Schemas & Capability Manifests",
            "Sandboxed GUI/DOM Coordinate & Terminal Action Trajectories",
            "Context-Compaction & Prompt-Cache Prefix Topology Specs",
            "Scoped OAuth2 / Zero-Trust Tool-Call Permission Policies",
        ],
        "description": (
            "Standardized Model Context Protocol (MCP) server/client buses, terminal-native coding "
            "harnesses, and virtualized OS/browser GUI execution sandboxes for long-horizon tool use."
        ),
    },
    {
        "id": "tool_disaggregated_kv_inference_stack",
        "slug": "disaggregated_kv_inference_stack",
        "name": "Disaggregated Prefill/Decode, Speculative Decoding & vLLM/SGLang/TensorRT-LLM Stack",
        "category": "VERTICAL_DOMAIN",
        "archetype": "DISAGGREGATED_KV_INFERENCE_ENGINE",
        "vendor_examples": [
            "SGLang RadixAttention & Mooncake RDMA KV-Cache Pool",
            "vLLM V1 & NVIDIA TensorRT-LLM / Dynamo Disaggregated Serving",
            "Google DeepMind Pathways TPU v6e/Ironwood MegaCore Serving",
            "DeepSeek DualPipe / FlashMLA & FP8/NVFP4 Quantized Kernels",
        ],
        "typical_artifacts": [
            "Prefill-Decode RDMA KV-Cache Transfer & Prefix-Hit Telemetry",
            "Multi-Token Prediction (MTP) Speculative Acceptance Profiles",
            "TTFT / TPOT Goodput vs. Batch-Concurrency SLA Envelopes",
            "Expert-Parallel All-to-All Load-Balancing & Kernel Traces",
        ],
        "description": (
            "High-goodput disaggregated prefill/decode serving engines, RadixAttention global KV-cache "
            "tiers, speculative decoding draft verifiers, and FP8/FP4 expert-parallel MoE kernels."
        ),
    },
    {
        "id": "tool_frontier_eval_preparedness_suite",
        "slug": "frontier_eval_preparedness_suite",
        "name": "Frontier Capability Evals, ASL/Preparedness CBRN-Cyber Gates & Inspect Harness",
        "category": "VERTICAL_DOMAIN",
        "archetype": "FRONTIER_SAFETY_ASL_EVAL_HARNESS",
        "vendor_examples": [
            "UK AISI Inspect & METR Autonomous Replication/Cyber Task Suite",
            "Anthropic RSP ASL-3/ASL-4 CBRN, Cyber & Weight-Security Gates",
            "OpenAI Preparedness Framework v2 & Reasoning Chain Monitors",
            "Google DeepMind Frontier Safety Framework & AI Control Sandboxes",
        ],
        "typical_artifacts": [
            "ASL-3/ASL-4 & Preparedness Threshold Capability Scorecards",
            "Untrusted-Model vs. Trusted-Monitor AI Control Audit Logs",
            "Decontaminated Holdout Canary & N-Gram/Semantic Leak Reports",
            "Mechanistic Sparse-Autoencoder (SAE) / Circuit Probe Traces",
        ],
        "description": (
            "Automated frontier evaluation harnesses measuring CBRN uplift, autonomous cyber offense, "
            "self-proliferation, deceptive alignment, AI Control untrusted-monitoring, and benchmark contamination."
        ),
    },
    {
        "id": "tool_fde_custom_posttraining_forge",
        "slug": "fde_custom_posttraining_forge",
        "name": "Forward-Deployed Enterprise Post-Training, Distillation & Sovereign VPC Forge",
        "category": "VERTICAL_DOMAIN",
        "archetype": "ENTERPRISE_POSTTRAINING_DISTILLATION_FORGE",
        "vendor_examples": [
            "Mistral Forge Custom Enterprise Pre-/Post-Training & SecNumCloud Stack",
            "OpenAI Forward-Deployed Reinforcement Fine-Tuning (RFT) & Evals API",
            "Anthropic Enterprise Bedrock/Vertex VPC Custom Context & Workbench",
            "Meta Llama Stack & TorchTune Sovereign On-Prem Distillation Pipeline",
        ],
        "typical_artifacts": [
            "Customer-Workflow Golden Eval Rubrics & Domain DPO/RFT Datasets",
            "Teacher-to-Student Distilled Checkpoint Latency/Accuracy Matrices",
            "Air-Gapped / SecNumCloud / FedRAMP Sovereign Deployment Helm Specs",
            "Forward-Deployed Production Drift, Hallucination & ROI Ledgers",
        ],
        "description": (
            "End-to-end Forward-Deployed Engineering (FDE) workbench transforming proprietary enterprise "
            "workflows and telemetry into custom RFT/DPO/distilled checkpoints inside sovereign or VPC enclaves."
        ),
    },
]
