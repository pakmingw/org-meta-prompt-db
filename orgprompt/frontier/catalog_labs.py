"""Catalog of the 5 Nov 2026 Frontier AI Labs and 30 Internal Operating Pods (`orgprompt.frontier.catalog_labs`)."""

from __future__ import annotations

from typing import Any, Dict, List

FRONTIER_AI_LABS_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "lab_anthropic",
        "slug": "anthropic",
        "name": "Anthropic",
        "company_id": "f500_anthropic",
        "headquarters": "San Francisco, CA (with London, Dublin, Zurich, Tokyo & Seattle Engineering Hubs)",
        "corporate_governance_structure": (
            "Delaware Public Benefit Corporation (PBC) governed alongside the independent Long-Term Benefit Trust "
            "(LTBT), which holds Class T shares empowering financially disinterested trustees to elect and remove "
            "a majority of the Board and enforce Responsible Scaling Policy (RSP) ASL-3/ASL-4 safety gates."
        ),
        "leadership": [
            "Dario Amodei (CEO & Co-Founder)",
            "Daniela Amodei (President & Co-Founder)",
            "Jared Kaplan (Chief Science Officer & RSP Officer)",
            "Mike Krieger (Chief Product Officer — Labs & Claude Code)",
            "Jan Leike & Alignment Science Leads (Scalable Oversight & Sabotage Auditing)",
        ],
        "research_to_product_loop": (
            "Tightly coupled Research-Engineer-First loop: Pretraining & Scaling Laws feed directly into "
            "Constitutional RL, Character Training, and SWE/Computer-Use RL gyms; dogfooded daily inside "
            "Anthropic via Claude Code and Model Context Protocol (MCP) servers before graduating through "
            "ASL-3/ASL-4 red-teaming into Claude Enterprise and Applied AI Pods."
        ),
        "flagship_models": [
            "Claude 4.x / Claude Opus & Sonnet Reasoning Series (Extended Thinking + Interleaved Tool Use)",
            "Claude Haiku Low-Latency Agentic Router & Subagent Tier",
            "Claude Code (Terminal-Native Autonomous SWE & Repository Agent)",
            "Model Context Protocol (MCP) Open Ecosystem & Computer-Use OS Harness",
        ],
        "safety_control_framework": (
            "Responsible Scaling Policy (RSP) with hard Capability Thresholds (AI Safety Levels ASL-3 deployed "
            "standard and ASL-4 CBRN/Cyber/Autonomous-R&D containment), Constitutional AI + Model Character "
            "shaping, Mechanistic Interpretability (Sparse Autoencoders & Circuit Tracing), and AI Control "
            "untrusted-model monitoring."
        ),
        "enterprise_gtm_fde_motion": (
            "Applied AI & Forward-Deployed Engineering pods co-designing MCP server topologies, Claude Code "
            "autonomous SDLC pipelines, and verifiable domain evals on AWS Bedrock, Google Vertex AI, and "
            "direct Claude Enterprise deployments across regulated finance, telecom, biotech, and defense."
        ),
        "compute_and_infra_strategy": (
            "Multi-cloud silicon diversification across AWS Trainium2/Trainium3 UltraClusters, Google Cloud TPU "
            "v6e/v7 Ironwood pods, and NVIDIA Blackwell clusters with disaggregated KV-cache prompt caching."
        ),
        "metadata": {
            "primary_superpowers": [
                "Autonomous SWE & Claude Code Harnesses",
                "Model Context Protocol (MCP) & Context Engineering",
                "Constitutional Alignment, Model Character & Mechanistic Interpretability",
                "ASL-3 / ASL-4 High-Assurance Safety & Cyber/Bio Containment",
            ]
        },
    },
    {
        "id": "lab_openai",
        "slug": "openai",
        "name": "OpenAI",
        "company_id": "f500_openai",
        "headquarters": "San Francisco, CA (with NYC, Seattle, London, Paris, Zurich, Tokyo & Singapore Hubs)",
        "corporate_governance_structure": (
            "Dual-tier structure with the OpenAI Foundation Nonprofit exercising governance oversight and "
            "equity stake over OpenAI Group PBC (Public Benefit Corporation), paired with a Board Safety & "
            "Security Committee holding binding deployment veto authority over Frontier Preparedness thresholds."
        ),
        "leadership": [
            "Sam Altman (CEO)",
            "Mark Chen (Chief Research Officer)",
            "Jakub Pachocki (Chief Scientist)",
            "Fidji Simo / Brad Lightcap (Applications, Enterprise & COO Leadership)",
            "Kevin Weil & Srinivas Narayanan (Product & Enterprise AI Engineering)",
        ],
        "research_to_product_loop": (
            "Unified Foundation + Test-Time Compute Reasoning RL flywheel: Large-scale multimodal pretraining "
            "merges with verifiable outcome-reward RL (math, code, browser/OS actions, deep research synthesis) "
            "inside stateful Responses API / Orchestration runtimes, validated with enterprise Forward-Deployed "
            "Engineers (FDEs) via Reinforcement Fine-Tuning (RFT)."
        ),
        "flagship_models": [
            "GPT-5.x Unified Multimodal + Adaptive Test-Time Reasoning Series",
            "o-Series Deep Reasoning & Reinforcement Fine-Tuning (RFT) Verifier Models",
            "Codex Cloud-Sandboxed Asynchronous Software Engineering Agent",
            "Deep Research, Operator Computer-Use & ChatGPT Work Enterprise Agent Platform",
        ],
        "safety_control_framework": (
            "Preparedness Framework v2 (High/Critical capability gates across Biosecurity, Cybersecurity, "
            "and AI Self-Improvement), Deliberative Alignment (explicit reasoning over the public Model Spec "
            "at test time), Chain-of-Thought monitorability preservation, and automated red-teaming."
        ),
        "enterprise_gtm_fde_motion": (
            "Dedicated Forward-Deployed Engineering (FDE) & Custom Post-Training teams embedding inside Global "
            "2000 enterprises to build custom RFT graders, stateful multi-agent Responses API workflows, "
            "and ChatGPT Work organizational memory connectors."
        ),
        "compute_and_infra_strategy": (
            "Multi-gigawatt Stargate AI factory campuses co-designed across Microsoft Azure, Oracle OCI, "
            "NVIDIA Blackwell/Rubin racks, and custom inference ASIC silicon with speculative decoding."
        ),
        "metadata": {
            "primary_superpowers": [
                "Test-Time Compute Scaling & Verifier Reinforcement Fine-Tuning (RFT)",
                "Asynchronous Cloud Sandboxed Agents (Codex, Deep Research, Operator)",
                "Deliberative Alignment & Public Model Spec Governance",
                "Global 2000 Forward-Deployed Engineering & ChatGPT Work Fleet Scale",
            ]
        },
    },
]

FRONTIER_AI_LABS_CATALOG.extend([
    {
        "id": "lab_google_deepmind",
        "slug": "google_deepmind",
        "name": "Google DeepMind",
        "company_id": "f500_google_deepmind",
        "headquarters": "London, UK & Mountain View, CA (with Zurich, Paris, New York, Montreal & Tokyo Hubs)",
        "corporate_governance_structure": (
            "Unified AI research and frontier model engine inside Alphabet Inc., led by CEO Demis Hassabis and "
            "CTO/Chief AI Architect Koray Kavukcuoglu, governed by the Responsibility & Safety Council (RSC) "
            "and Alphabet Frontier Safety Framework (FSF) while shipping directly into Google Cloud Vertex AI, "
            "Workspace, Search, Android, and Isomorphic Labs."
        ),
        "leadership": [
            "Demis Hassabis (CEO & Co-Founder, Nobel Laureate)",
            "Koray Kavukcuoglu (CTO & Alphabet Chief AI Architect)",
            "Oriol Vinyals & Jeff Dean (VP of Research / Gemini Co-Lead & Chief Scientist)",
            "Pushmeet Kohli (VP of Research — AI for Science & Reliability)",
            "Shane Legg & Anca Dragan (Chief AGI Scientist & Frontier Safety / AI Control)",
        ],
        "research_to_product_loop": (
            "Full-stack Silicon-to-Science-to-Product co-design: TPU v6e/v7 Ironwood & Pathways distributed "
            "training power natively multimodal long-context Gemini models, Deep-Thinking tree-search RL, "
            "generative interactive world models (Veo, Genie, Project Astra), and AlphaFold/AlphaEvolve "
            "scientific discovery engines."
        ),
        "flagship_models": [
            "Gemini 3.x Pro / Ultra / Deep Think (Multi-Million-Token Native Multimodal & Agentic RL)",
            "Gemini Flash & Flash-Lite Ultra-Low-Latency High-Throughput Enterprise Fleet Models",
            "Veo Generative Video, Genie Interactive 3D World Models & Project Astra Live Multimodal Agents",
            "AlphaFold 3, AlphaProteo, WeatherNext & AlphaEvolve Evolutionary Algorithm Discovery",
        ],
        "safety_control_framework": (
            "Frontier Safety Framework (FSF) enforcing Critical Capability Levels (CCLs) across CBRN, Cyber, "
            "Machine-Learning R&D autonomy, and deceptive alignment, backed by AI Control defense-in-depth "
            "sandboxing, SynthID cryptographic watermarking, and mechanistic safety probes."
        ),
        "enterprise_gtm_fde_motion": (
            "Joint Google DeepMind Applied + Google Cloud Vertex AI Customer Engineering pods delivering "
            "multi-million-token repository/document grounding, Live API real-time voice/vision agents, "
            "enterprise Agent2Agent (A2A) + MCP interoperability, and sovereign cloud regions."
        ),
        "compute_and_infra_strategy": (
            "Vertically integrated Google TPU v5p/v6e Trillium/v7 Ironwood optical-circuit-switched pods "
            "orchestrated via Pathways single-controller disaggregated prefill/decode serving."
        ),
        "metadata": {
            "primary_superpowers": [
                "Multi-Million-Token Native Multimodal Context & Live Audio-Video Streaming",
                "Interactive World Models (Genie, Veo) & Embodied Robotics Simulation",
                "AI for Science (AlphaFold, AlphaEvolve, Materials & Fusion Control)",
                "Vertical TPU Silicon + Optical Interconnect + Pathways Co-Design",
            ]
        },
    },
    {
        "id": "lab_meta_msl",
        "slug": "meta_msl",
        "name": "Meta Superintelligence Labs (MSL) & FAIR",
        "company_id": "f500_meta_superintelligence_labs",
        "headquarters": "Menlo Park, CA (with Paris FAIR, NYC, Seattle, London & Tel Aviv Research Hubs)",
        "corporate_governance_structure": (
            "Reorganized inside Meta Platforms under Chief AI Officer Alexandr Wang into 4 ultra-flat execution "
            "pillars: (1) TBD Lab (~200-person elite frontier reasoning & core model pod), (2) FAIR (Fundamental "
            "AI Research — world models, V-JEPA, self-supervised science), (3) Products & Applied Research "
            "(Nat Friedman — high span-of-control product pods), and (4) MSL Infra (Aparna Ramani — gigawatt clusters)."
        ),
        "leadership": [
            "Alexandr Wang (Chief AI Officer — Head of Meta Superintelligence Labs)",
            "Nat Friedman (Head of MSL Products & Applied Research)",
            "Aparna Ramani (VP of MSL Infrastructure — Prometheus & Hyperion Gigawatt Clusters)",
            "TBD Lab Core Frontier Leads & FAIR Fundamental Science Directors",
            "Rob Fergus / FAIR World-Model & Open Science Leadership",
        ],
        "research_to_product_loop": (
            "Ultra-flat high-GPU-per-researcher pod architecture: TBD Lab iterates rapidly on frontier sparse "
            "MoE reasoning & synthetic data/RL rubrics, FAIR pioneers non-generative latent world models "
            "(V-JEPA 2, DINOv3) and scientific datasets, while Applied pods ship to 3.3B+ users, Ray-Ban/Orion "
            "wearables, and the open-weight Llama enterprise ecosystem."
        ),
        "flagship_models": [
            "TBD Lab Frontier Reasoning & Multimodal Models (Muse / Next-Gen Frontier Architecture)",
            "Llama 4 / Llama Next Sparse MoE Open-Weight & Enterprise Distilled Model Family",
            "FAIR V-JEPA 2 Latent Action World Models, DINOv3 Vision & Meta Motivo Embodied Agents",
            "PyTorch 2.x / TorchTitan / Triton Compiler Stack (Industry-Wide Training Substrate)",
        ],
        "safety_control_framework": (
            "Meta Frontier AI Framework gating catastrophic cyber/CBRN uplift prior to open-weight or API "
            "release, Llama Guard / Prompt Guard runtime shields, CyberSecEval benchmark suites, and "
            "quantitative open-vs-closed marginal-risk evaluations."
        ),
        "enterprise_gtm_fde_motion": (
            "Open-weight & Sovereign VPC ecosystem enablement: Enterprises download, post-train, quantize, and "
            "distill Llama MoE checkpoints inside air-gapped on-prem or private cloud clusters with zero token "
            "data egress, supported by PyTorch/vLLM/TorchTune recipes and scale-data rubric pipelines."
        ),
        "compute_and_infra_strategy": (
            "Multi-gigawatt Prometheus (1GW+) and Hyperion (scaling toward 2–5GW) AI superclusters connected via "
            "RoCEv2/InfiniBand fabrics, custom MTIA inference silicon, and PyTorch TorchTitan 4D parallelism."
        ),
        "metadata": {
            "primary_superpowers": [
                "Open-Weight Sparse MoE Sovereignty & Zero-Egress On-Prem Distillation",
                "Latent Physical World Models (V-JEPA) & PyTorch/Triton Ecosystem Dominance",
                "High-Density Data Rubric Engineering & Ultra-Flat Elite Research Pods (TBD Lab)",
                "Multi-Gigawatt Prometheus & Hyperion Training Cluster Engineering",
            ]
        },
    },
    {
        "id": "lab_mistral_ai",
        "slug": "mistral_ai",
        "name": "Mistral AI",
        "company_id": "f500_mistral_ai",
        "headquarters": "Paris, France (with London, Palo Alto, NYC, Singapore & European Sovereign Cloud Hubs)",
        "corporate_governance_structure": (
            "Independent European frontier AI champion (French SAS) led by co-founders Arthur Mensch, Guillaume "
            "Lample, and Timothee Lacroix, maintaining strategic independence, EU AI Act systemic-risk compliance, "
            "and French/European sovereign defense & critical-infrastructure partnerships (ANSSI / SecNumCloud)."
        ),
        "leadership": [
            "Arthur Mensch (CEO & Co-Founder)",
            "Guillaume Lample (Chief Scientist & Co-Founder)",
            "Timothee Lacroix (CTO & Co-Founder)",
            "Audrey Herblin-Stoop (VP Public Affairs & EU Regulatory Sovereignty)",
            "Global Head of Applied AI & Forward-Deployed ML Engineering (Mistral Forge)",
        ],
        "research_to_product_loop": (
            "Extreme compute-efficiency Core Science + Embedded Forward-Deployed ML Engineering: A compact "
            "pretraining/post-training core builds frontier-per-FLOP Sparse MoE, coding (Codestral), vision/OCR "
            "(Pixtral), and edge models (Ministral), while Forward-Deployed Engineers run Mistral Forge directly "
            "on enterprise proprietary corpora for custom pretraining, DPO, and verifier RL."
        ),
        "flagship_models": [
            "Mistral Large & Magistral Multilingual Frontier Reasoning Series",
            "Codestral (Low-Latency Repository Completion, FIM & Legacy Migration Agent Model)",
            "Pixtral & Mistral OCR (High-Precision Engineering Schematic, PDF & Financial Table Multimodal)",
            "Ministral Edge/On-Device Series, Le Chat Enterprise & Mistral Forge Custom Model Factory",
        ],
        "safety_control_framework": (
            "EU AI Act General-Purpose AI (GPAI) Code of Practice & Systemic-Risk compliance, SecNumCloud / "
            "air-gapped sovereign deployment guarantees, strict data-residency isolation, and configurable "
            "system-level moderation & lawful-intercept governance."
        ),
        "enterprise_gtm_fde_motion": (
            "Palantir-style Forward-Deployed ML Engineer (FD-MLE) pods paired with Mistral Forge: FD-MLEs sit "
            "inside European telcos (e.g., Orange, Free), banks, defense ministries, and industrial OEMs to "
            "convert proprietary ERP/OSS/SCADA logs into custom domain-distilled MoE models owned by the client."
        ),
        "compute_and_infra_strategy": (
            "Mistral Compute sovereign European GPU superclusters (Essonne/Ile-de-France decarbonized nuclear/hydro "
            "powered NVIDIA Blackwell clusters) plus portable vLLM/TensorRT-LLM sovereign appliance images."
        ),
        "metadata": {
            "primary_superpowers": [
                "Mistral Forge Custom Enterprise Pretraining, DPO & Domain Distillation",
                "Sovereign, Air-Gapped, SecNumCloud & EU AI Act Regulated Deployment",
                "Frontier Compute-Efficiency Sparse MoE, Codestral & Pixtral Document OCR",
                "Multilingual European, Arabic & Emerging-Market Linguistic Fidelity",
            ]
        },
    },
])

from orgprompt.frontier.catalog_pods import FRONTIER_LAB_PODS_CATALOG

__all__ = ["FRONTIER_AI_LABS_CATALOG", "FRONTIER_LAB_PODS_CATALOG"]
