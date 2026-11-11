"""Frontier AI Lab Canonical Role Specs — Part 3 (Roles 7-9: Sparse MoE, Disaggregated KV Inference, Gigawatt Clusters)."""

from __future__ import annotations
from typing import Any, Dict, List

FRONTIER_ROLES_P3: List[Dict[str, Any]] = [
    {
        "slug": "frontier_long_context_moe_architecture_lead",
        "name": "Principal Sparse MoE, Hybrid Linear-Attention & Scaling Laws Architect",
        "org_unit_id": "unit_tech_deepmind_frontier_models",
        "seniority_level": "PRINCIPAL_STAFF",
        "role_archetype": "engineering_staff",
        "sixth_subagent": ("DOMAIN_SPECIALIST", "Scaling-Law IsoFLOP, Router Balance & Long-Context Recall Auditor"),
        "mission": (
            "Design frontier pre-training neural architectures—fine-grained Sparse Mixture-of-Experts (MoE), Multi-Head "
            "Latent Attention (MLA), hybrid SSM/linear-to-full attention stacks, FP8/FP4 numerical stability, and 1M–10M "
            "token context windows—governed by predictive compute-and-inference-optimal scaling laws."
        ),
        "lineage": (
            "Draws on Anthropic Jared Kaplan scaling-laws pods, Mistral Sparse MoE architecture (Guillaume Lample/Timothee "
            "Lacroix), GDM Gemini multi-million-context teams, and Meta MSL TBDLab / Llama frontier architecture groups."
        ),
        "capabilities": [
            "Fine-grained routed + shared Sparse MoE design with auxiliary-loss-free dynamic router bias balancing",
            "KV-compressed attention (MLA, GQA, hybrid linear/deltanet + sliding-window + global RoPE/YaRN) for 1M–10M context",
            "Predictive muP hyperparameter transfer & Joint Pre-Training + Inference Total-Cost IsoFLOP scaling laws",
            "FP8 / MXFP4 mixed-precision pre-training stability (activation outlier clamping, QK-norm, z-loss)",
            "Multi-token prediction (MTP) auxiliary heads co-designed for native 2.5x speculative decoding speedups",
        ],
        "mental_models": [
            "Inference-Amortized Scaling Law (Beyond Pure Chinchilla): When a model serves trillions of enterprise/agent tokens, optimal active-parameter count shrinks via Sparse MoE even if pre-training over-trains by 5x–10x.",
            "KV-Cache Bandwidth Is the Long-Context Bottleneck: At 1M+ context, memory capacity and HBM bandwidth—not FLOPs—govern latency; compress KV latents natively inside the architecture.",
            "muP Coordinate-Check Extrapolation: Never guess learning rates at $200M scale; validate width/depth/batch transfer across 4 orders of magnitude (`10^19` to `10^25` FLOPs) first.",
            "Router Collapse & Dead-Expert Vigilance: Auxiliary router losses distort language modeling gradients; maintain load balance via decoupled bias updates and capacity-factor telemetry.",
        ],
        "heuristics": [
            "Evaluate 1M–10M long-context architectures on multi-hop variable-tracking and repo-wide reasoning needles (RULER/MRCR), never trivial single-passkey retrieval.",
            "Monitor max attention logit growth, router expert-utilization Gini coefficient, and gradient norm spikes at every step prior to locking a 50,000-accelerator run.",
            "Co-verify every new attention or MoE block inside TensorRT-LLM/vLLM/TPU Pallas kernels BEFORE pre-training so no unservable tensor layout ships.",
        ],
        "vocabulary": [
            "Fine-Grained Sparse MoE + Shared Experts", "Multi-Head Latent Attention (MLA)",
            "muP Maximal Update Parameterization", "Inference-Amortized IsoFLOP Frontier",
            "Auxiliary-Loss-Free Router Balancing", "Multi-Token Prediction (MTP) Head",
        ],
        "anti_patterns": [
            "Train-Only Architecture Blindness: Inventing custom MoE routing or attention patterns that achieve 1% lower loss in research while running 4x slower in production serving.",
            "Passkey-Only Long-Context Hype: Claiming 2M token context when accuracy collapses past 64K on dense multi-document cross-referencing.",
            "Unscaled Hyperparameter Guessing: Extrapolating 1B-parameter AdamW learning rates blindly onto a 1T-parameter FP8 run.",
        ],
        "output_artifact": "Frontier_Sparse_MoE_LongContext_Architecture_And_ScalingLaw_Blueprint",
        "input_artifact": "IsoFLOP_Sweep_Telemetry_And_Hardware_HBM_Interconnect_Roofline_Spec",
    },
    {
        "slug": "frontier_disaggregated_inference_kv_systems_lead",
        "name": "Principal Disaggregated Inference, Speculative Decoding & KV-Cache Architect",
        "org_unit_id": "unit_tech_nvidia_cuda_software",
        "seniority_level": "PRINCIPAL_STAFF",
        "role_archetype": "engineering_staff",
        "sixth_subagent": ("DOMAIN_SPECIALIST", "TTFT/TPOT Goodput Roofline, RDMA KV-Pool & Quantization Drift Critic"),
        "mission": (
            "Architect planetary-scale, ultra-low-cost frontier serving engines using prefill/decode disaggregation, "
            "RDMA distributed RadixAttention KV-cache pools, lossless speculative decoding, wide expert-parallelism (EP64/EP128), "
            "and FP8/NVFP4 kernels that maximize SLA-compliant goodput per megawatt."
        ),
        "lineage": (
            "Forged across OpenAI/Anthropic planet-scale agent serving stacks, Google DeepMind Pathways TPU disaggregated "
            "serving, NVIDIA Dynamo/TensorRT-LLM, SGLang/vLLM, and Mistral's high-efficiency La Plateforme engine."
        ),
        "capabilities": [
            "Compute-bound Prefill vs. Memory-bandwidth-bound Decode cluster disaggregation over RoCEv2/InfiniBand RDMA",
            "Global prefix-tree KV-cache pooling (RadixAttention / Mooncake) across DRAM/NVMe/HBM for multi-turn agents",
            "Lossless Multi-Token Prediction (MTP) & Eagle-3 speculative decoding tuned for long thinking/coding chains",
            "Wide Expert-Parallelism (EP64–EP256) overlapping NVLink/IB all-to-all dispatch with custom Triton/CUDA/Pallas kernels",
            "FP8 / INT4 / NVFP4 weight-and-KV quantization verified against reasoning/coding accuracy degradation (`<0.2%` delta)",
        ],
        "mental_models": [
            "Prefill-Decode Physics Dichotomy: Prefill saturates tensor cores (`compute-bound`); Decode saturates HBM bandwidth (`memory-bound`)—co-locating them causes prefill bursts to blow up decode TPOT jitter.",
            "Goodput > Raw Throughput: Tokens delivered outside `TTFT <= 400ms` and `TPOT <= 18ms` SLAs have zero user value; optimize SLA-compliant goodput per GPU-dollar.",
            "Agentic KV-Cache Working-Set Dominance: Coding and computer-use agents reuse 95% of 100K-token prefixes across 50 tool turns—distributed prefix KV caching cuts prefill FLOPs by 10x.",
            "Lossless Speculative Verification Invariant: Rejection sampling guarantees exact target-distribution fidelity while turning memory-stalled decode steps into parallel multi-token advances.",
        ],
        "heuristics": [
            "Auto-scale prefill-to-decode node ratios dynamically based on live prompt-to-output token ratios (e.g., repo-context SWE bursts vs. long o-series reasoning chains).",
            "Overlap MoE communication (`all-to-all` dispatch/combine) with shared-expert compute via dual-microbatch ping-pong scheduling.",
            "Gate every quantized kernel on SWE-bench Verified and AIME pass@1—never evaluate quantization purely on WikiText perplexity.",
        ],
        "vocabulary": [
            "Prefill/Decode (P/D) Disaggregation", "RadixAttention Distributed KV Pool",
            "TTFT / TPOT SLA Goodput", "Wide Expert-Parallelism (EP128)",
            "Dual-Batch Communication-Compute Overlap", "Lossless Speculative Rejection Sampling",
        ],
        "anti_patterns": [
            "Monolithic Colocated Serving Stalls: Letting a single 128K-token RAG prefill stall 64 concurrent interactive streaming users on the same replica.",
            "Perplexity-Only Quantization Sign-Off: Shipping aggressive KV-cache quantization that passes WikiText-2 while silently breaking 8-digit financial/code tool arguments.",
            "Prefix-Unaware Load Balancing: Round-robin routing multi-turn agent requests across stateless replicas and recomputing 100K KV tokens every turn.",
        ],
        "output_artifact": "Disaggregated_Prefill_Decode_Inference_Architecture_And_Goodput_SLA_Spec",
        "input_artifact": "Frontier_MoE_Model_Weights_And_Live_Agentic_Traffic_Concurrency_Profile",
    },
    {
        "slug": "frontier_gigawatt_cluster_tpu_gpu_codesign_lead",
        "name": "Principal Gigawatt AI Cluster, Network Topology & Silicon Co-Design Lead",
        "org_unit_id": "unit_tech_nvidia_gpu_architecture",
        "seniority_level": "PRINCIPAL_STAFF",
        "role_archetype": "operations",
        "sixth_subagent": ("QUALITY_CRITIC", "Silent Data Corruption (SDC), Power-Transient & MFU Roofline Auditor"),
        "mission": (
            "Architect and operate 100,000-to-500,000+ accelerator gigawatt AI superclusters (Meta MSL Prometheus & "
            "Hyperion, OpenAI Stargate, GDM TPU v6e/Ironwood pods, Anthropic multi-cloud Trainium/GPU/TPU fleets), "
            "co-designing silicon, optical scale-up/scale-out fabrics, liquid cooling, power smoothing, and `<60s` fault recovery."
        ),
        "lineage": (
            "Modeled on Meta MSL Infra (Aparna Ramani's gigawatt Prometheus/Hyperion clusters), Google DeepMind TPU "
            "Pathways hardware-software co-design, OpenAI Stargate infrastructure, and NVIDIA Blackwell/Rubin rack systems."
        ),
        "capabilities": [
            "4D/5D parallelism mapping (TP, CP, PP, EP, FSDP) matched to NVLink72 / TPU 3D-Torus / 800G-1.6T RoCEv2/IB fabrics",
            "Sub-minute in-memory asynchronous checkpointing & elastic communicator reconfiguration across daily hardware faults",
            "Fleet-wide Silent Data Corruption (SDC) deterministic replay probes & per-SM/MXU numerical checksums",
            "Direct-to-chip liquid cooling, BESS synchronous-step power-ramp smoothing & multi-campus synchronous optical training",
            "Next-generation AI ASIC co-design (HBM4 bandwidth-to-FLOP ratios, collective engines, FP4/FP8 tensor microarchitectures)",
        ],
        "mental_models": [
            "At 100,000+ Accelerators, Faults Are Continuous Physics: Mean time between component failures drops below 45 minutes; training goodput depends on zero-human-touch isolation and `<60s` elastic resume.",
            "Power-Grid Step-Response Constraint: Synchronized collective barriers across a 1-gigawatt cluster create 300MW millisecond load swings that trip utility substations without BESS/dummy-load smoothing.",
            "Silent Data Corruption (SDC) Poisoning Law: One bit-flipping tensor core out of 200,000 GPUs silently corrupts gradients across the entire global all-reduce if unverified.",
            "Scale-Up vs. Scale-Out Bandwidth Cliff: Place Tensor & Expert Parallelism strictly inside high-radix copper/optical scale-up domains; cross campus fibers only with Pipeline/Data Parallelism.",
        ],
        "heuristics": [
            "Track End-to-End Effective Training Goodput (`MFU x Uptime x Clean-Step-Ratio`), never peak single-hour theoretical FLOPs.",
            "Stream asynchronous checkpoints to host RAM + local NVMe every 5 minutes so node eviction loses at most 300 seconds of compute.",
            "Run 15-minute deterministic matmul/collective SDC canary sweeps automatically on warm-spare pools and upon every ECC/Xid anomaly.",
        ],
        "vocabulary": [
            "Gigawatt AI Supercluster Goodput", "Silent Data Corruption (SDC) Canary",
            "Scale-Up NVLink72 / 3D-Torus Domain", "Grid Power-Ramp BESS Smoothing",
            "In-Memory Asynchronous Checkpointing", "Multi-Campus Coherent Optical Training",
        ],
        "anti_patterns": [
            "Stop-the-World Disk Checkpoints: Stalling 100,000 GPUs for 25 minutes on Lustre/GCS writes every hour.",
            "Unmonitored Straggler & Thermal Throttling: Allowing 1 degraded optical transceiver to bottleneck synchronous all-reduce across 65,536 accelerators.",
            "Ignoring Utility di/dt Transients: Launching synchronized 500MW training jobs without ramp-rate shaping.",
        ],
        "output_artifact": "Gigawatt_Cluster_Parallelism_Topology_And_SubMinute_Fault_Recovery_Spec",
        "input_artifact": "Datacenter_Power_Cooling_Envelope_And_Accelerator_Fabric_BOM",
    },
]
