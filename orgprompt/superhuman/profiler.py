"""Domain-aware Perfect Human pedigree and Out-of-Distribution epistemology builders."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from orgprompt.superhuman.models import (
    AcademicFoundation,
    AdjacentRoleFusion,
    CrucibleEpisode,
    EpistemicStage,
    HumanCharacteristics,
    OnTheJobCrucibles,
    UnknownProblemEpistemology,
)


_DOMAIN_ACADEMIC_CATALOG: Dict[str, Dict[str, Any]] = {
    "finance": {
        "degrees": [
            "B.S. in Applied Mathematics & Theoretical Physics (Summa Cum Laude, MIT / Princeton)",
            "M.S. in Financial Engineering & Stochastic Calculus (Stanford / Columbia)",
            "Ph.D. in Quantitative Economics, Market Microstructure & Convex Optimization (University of Chicago / MIT Sloan)",
            "CFA Charterholder & MBA Executive Concentration in Capital Allocation (Wharton)",
        ],
        "coursework": [
            "Measure-Theoretic Probability, Ito Stochastic Calculus & Martingale Pricing Axioms",
            "Convex Optimization, Stochastic Control Theory & Dynamic Programming (Bellman Optimality)",
            "Extreme Value Theory (EVT), Heavy-Tailed Distributions, Copulas & Systemic Liquidity Risk",
            "Corporate Valuation, ROIC/WACC Spread Conservation & Balance-Sheet Solvency Accounting",
            "Information-Theoretic Portfolio Kelly Criterion & Non-Stationary Regime Filtering",
        ],
        "literature": [
            "Shreve — Stochastic Calculus for Finance I & II",
            "Boyd & Vandenberghe — Convex Optimization",
            "Koller, Goedhart & Wessels (McKinsey) — Valuation: Measuring and Managing the Value of Companies",
            "Taleb — Dynamic Hedging & Statistical Consequences of Fat Tails",
            "Basel III / IV Capital Adequacy, IFRS 9 / GAAP & IOSCO Market Risk Standards",
        ],
        "exemplars": ["Renaissance Technologies", "Goldman Sachs", "Citadel", "BlackRock"],
    },
    "healthcare": {
        "degrees": [
            "B.S. in Biochemistry, Molecular Biophysics & Applied Statistics (Harvard / Stanford)",
            "M.D. with Clinical Residency & Subspecialty Fellowship (Johns Hopkins / Mayo Clinic)",
            "Ph.D. in Systems Pharmacology, Biostatistics & Causal Inference (Harvard-MIT HST / UCSF)",
        ],
        "coursework": [
            "Pharmacokinetics/Pharmacodynamics (PK/PD) Differential Equations & Physiological Mass Balance",
            "Bayesian Adaptive Clinical Trial Design, Survival Analysis (Cox Proportional Hazards) & Causal DAGs",
            "Molecular Systems Biology, Genomics, Proteomics & Cellular Signal Transduction",
            "Clinical Epidemiology, Diagnostic Sensitivity/Specificity Bayes Updating & Bioethics",
            "Regulatory Science, GxP Quality Systems & Pharmacovigilance Signal Detection",
        ],
        "literature": [
            "Pearl — Causality: Models, Reasoning, and Inference",
            "Friedman, Furberg & DeMets — Fundamentals of Clinical Trials",
            "Goodman & Gilman — The Pharmacological Basis of Therapeutics",
            "ICH E6(R3) GCP, ICH E9(R1) Estimands, FDA 21 CFR Part 11 & EMA Clinical Guidelines",
        ],
        "exemplars": ["Mayo Clinic", "Genentech", "Broad Institute", "Roche"],
    },
    "legal_risk": {
        "degrees": [
            "B.A./B.S. in Economics, Formal Logic & Computer Science (Yale / Stanford)",
            "J.D. (Magna Cum Laude, Law Review Senior Editor — Harvard / Yale Law School)",
            "LL.M. / Ph.D. in Regulatory Economics, Mechanism Design & Cyber-Risk Governance (NYU / Oxford)",
        ],
        "coursework": [
            "Statutory Interpretation, Administrative Law, Antitrust & Cross-Border Regulatory Conflict of Laws",
            "Game Theory, Incentive-Compatible Mechanism Design & Principal-Agent Contract Theory",
            "Cryptographic Auditability, Zero-Trust Security Controls & Forensic Chain-of-Custody",
            "Quantitative Operational Risk Modeling, Stress Testing & Fiduciary Liability",
        ],
        "literature": [
            "Laffont & Tirole — A Theory of Incentives in Procurement and Regulation",
            "NIST SP 800-53 Rev 5, ISO/IEC 27001, ISO/IEC 42001 AI Management & EU AI Act / NIS2 / GDPR",
            "Hart — The Concept of Law & Posner — Economic Analysis of Law",
            "COSO Enterprise Risk Management &IIA Three Lines Model",
        ],
        "exemplars": ["Cravath, Swaine & Moore", "U.S. DOJ / SEC Enforcement", "Cloudflare", "JPMorgan Risk"],
    },
    "aerospace_hardware": {
        "degrees": [
            "B.S. in Aerospace, Mechanical & Electrical Engineering (Caltech / MIT)",
            "M.S. in Control Dynamical Systems, Solid-State Physics & VLSI/Materials (Stanford / ETH Zurich)",
            "Ph.D. in Nonlinear Optimal Control, Thermodynamics & Fault-Tolerant Systems Engineering (MIT / Caltech)",
        ],
        "coursework": [
            "Continuum Mechanics, Navier-Stokes Fluid Dynamics & Non-Equilibrium Thermodynamics",
            "Semiconductor Device Physics, Lithography Optics, Signal Integrity & Electromagnetics (Maxwell Equations)",
            "Lyapunov Stability, Robust H-Infinity Control, Kalman Filtering & Fault-Tree Probabilistic Risk Assessment",
            "Six Sigma Statistical Process Control (SPC), Design of Experiments (Taguchi/DOE) & Materials Fatigue",
        ],
        "literature": [
            "NASA Systems Engineering Handbook (SP-2016-6105) & Lockheed Skunk Works Kelly's 14 Rules",
            "Astrom & Murray — Feedback Systems & Stengel — Optimal Control and Estimation",
            "Mead & Conway — Introduction to VLSI Systems & Sze — Physics of Semiconductor Devices",
            "DO-178C, ISO 26262 ASIL-D, MIL-STD-882E & SEMI Manufacturing Standards",
        ],
        "exemplars": ["SpaceX", "TSMC", "Lockheed Martin Skunk Works", "ASML"],
    },
    "telecom_systems": {
        "degrees": [
            "B.S. in Electrical Engineering & Computer Science (MIT / UC Berkeley)",
            "M.S. in Information Theory, Distributed Systems & RF/Optical Networking (Stanford / ETH Zurich)",
            "Ph.D. in Distributed Consensus, Queueing Networks & Fault-Tolerant Infrastructure (CMU / Bell Labs Fellowship)",
        ],
        "coursework": [
            "Shannon Information Theory, Channel Capacity, Coding Theory & Digital Signal Processing",
            "Distributed Consensus (Paxos/Raft/Byzantine), Linearizability, CAP/PACELC & Formal TLA+ Verification",
            "Queueing Theory (Little's Law, Kingman's Formula, M/G/k Tail Latency) & Control-Plane Stability",
            "BGP/MPLS/Optical DWDM/5G Core Architecture, eBPF Kernel Telemetry & Cryptographic Zero-Trust",
        ],
        "literature": [
            "Cover & Thomas — Elements of Information Theory",
            "Kleppmann — Designing Data-Intensive Applications & Lamport — Specifying Systems (TLA+)",
            "Beyer et al. — Google Site Reliability Engineering & Saltzer, Reed, Clark — End-to-End Arguments",
            "3GPP Release 18/19, IETF BGP/QUIC RFCs, ITU-T Optical Standards & ANSSI/ETSI Security Baselines",
        ],
        "exemplars": ["Bell Labs", "Google SRE", "AWS Core Infrastructure", "NTT / Ericsson"],
    },
    "strategy_ops": {
        "degrees": [
            "B.S. in Industrial Engineering, Operations Research & Econometrics (Stanford / Northwestern)",
            "MBA with Distinction — Baker Scholar / Arjay Miller Scholar (Harvard Business School / GSB)",
            "Ph.D. in Operations Research, Supply-Chain Network Optimization & Organizational Economics (MIT ORC / Wharton)",
        ],
        "coursework": [
            "Mixed-Integer Linear Programming (MILP), Network Flow Conservation & Stochastic Inventory Theory",
            "Microeconomic Industrial Organization, Pricing Elasticity, Game Theory & Competitive Moats",
            "Lean Toyota Production System (TPS), Theory of Constraints (Goldratt) & Little's Law Throughput",
            "Causal Econometrics, Difference-in-Differences, Synthetic Controls & Capital Budgeting",
        ],
        "literature": [
            "Hopp & Spearman — Factory Physics: Foundations of Manufacturing Management",
            "Bertsimas & Tsitsiklis — Introduction to Linear Optimization",
            "Ohno — Toyota Production System & Grove — High Output Management",
            "Porter — Competitive Advantage & Rumelt — Good Strategy Bad Strategy",
        ],
        "exemplars": ["Toyota", "Amazon Operations", "McKinsey QuantumBlack", "Danaher"],
    },
}


def _clip_words(text: str, max_chars: int = 240) -> str:
    cleaned = " ".join(text.strip().split())
    if len(cleaned) <= max_chars:
        return cleaned
    cut = cleaned[:max_chars].rsplit(" ", 1)[0]
    return f"{cut}..."


def _classify_domain_bucket(primary_role: Dict[str, Any], problem_statement: str) -> str:
    """Selects the closest academic/crucible archetype bucket prioritizing role industry & title."""
    industry = str(primary_role.get("industry_name") or primary_role.get("industry") or "").lower()
    archetype = str(primary_role.get("role_archetype") or "").lower()
    title = str(primary_role.get("title") or primary_role.get("name") or "").lower()
    role_header = f"{industry} {title}"
    prob = problem_statement.lower()

    # 1. Explicit primary_role industry/title classification first (prevents problem keywords like 'quantum' hijacking 'quant')
    if any(k in role_header for k in ("health", "pharma", "biotech", "clinical", "medical", "hospital", "genomic")):
        return "healthcare"
    if any(k in role_header for k in ("legal", "counsel", "compliance", "regulatory", "privacy", "audit", "aml")):
        return "legal_risk"
    if any(k in role_header for k in ("telecom", "network", "5g", "optical", "software", "cloud", "distributed", "sre", "platform", "cyber", "security", "ai", "data")):
        return "telecom_systems"
    if any(k in role_header for k in ("aerospace", "defense", "semiconductor", "silicon", "hardware", "automotive", "energy", "nuclear", "grid", "manufacturing", "robotics")):
        return "aerospace_hardware"
    if any(k in role_header for k in ("financ", "bank", "capital", "invest", "trading", "insurance", "treasury", "wealth", "hedge", "actuar")):
        return "finance"
    if any(k in role_header for k in ("retail", "logistics", "supply chain", "consulting", "strategy", "media", "consumer")):
        return "strategy_ops"

    # 2. Problem-statement fallback for custom roles without industry metadata
    blob = f"{role_header} {archetype} {prob}"
    if any(k in blob for k in ("clinical", "medical", "pharma", "biotech", "patient", "fda")):
        return "healthcare"
    if any(k in blob for k in ("statutory", "counsel", "compliance", "antitrust", "gdpr", "aml")):
        return "legal_risk"
    if any(k in blob for k in ("portfolio", "valuation", "stochastic calculus", "derivative", "trading", "treasury", "credit", "solvency")):
        return "finance"
    if any(k in blob for k in ("aerospace", "semiconductor", "lithography", "avionics", "propulsion", "thermodynamic", "grid")):
        return "aerospace_hardware"
    if any(k in blob for k in ("5g", "optical", "bgp", "consensus", "distributed", "kernel", "quantum", "latency", "cloud", "sre")):
        return "telecom_systems"
    if archetype == "risk_compliance":
        return "legal_risk"
    if archetype == "executive_strategy":
        return "strategy_ops"
    return "telecom_systems"


def build_academic_foundation(
    primary_role: Dict[str, Any],
    problem_statement: str = "",
    adjacent_roles: Optional[List[AdjacentRoleFusion]] = None,
    company_context: Optional[str] = None,
    developer_context: str = "",
) -> AcademicFoundation:
    """Synthesizes undergraduate, graduate, and doctoral rigor tailored to role, problem & adjacent roles."""
    bucket = _classify_domain_bucket(primary_role, problem_statement)
    spec = _DOMAIN_ACADEMIC_CATALOG[bucket]
    role_title = primary_role.get("title") or primary_role.get("name") or "Principal Specialist"
    industry = primary_role.get("industry_name") or primary_role.get("industry") or "Enterprise"
    adj_list = adjacent_roles or []

    coursework = list(spec["coursework"])
    mental_models = primary_role.get("mental_models") or []
    if mental_models:
        coursework.append(
            f"Domain Axioms & Formal Models of {role_title}: {', '.join(str(m) for m in mental_models[:4])}"
        )
    if developer_context.strip():
        coursework.append(
            "Applied Proprietary Domain Seminar: Formalizing developer-supplied architectural constraints into testable state invariants"
        )

    minors: List[str] = []
    for adj in adj_list[:4]:
        minors.append(
            f"Cross-Disciplinary Minor in {adj.title} ({adj.industry} / {adj.edge_type}): "
            f"mastering {', '.join(adj.absorbed_mental_models[:2]) or 'boundary interface invariants'} "
            f"to eliminate handoff blind spots"
        )
    if not minors:
        minors = [
            f"Cross-Disciplinary Minor in Adversarial Risk & Formal Verification ({industry})",
            "Cross-Disciplinary Minor in Socio-Technical Systems Economics & Operations Research",
        ]

    prob_focus = _clip_words(problem_statement.strip() or f"mission-critical {industry} architecture and resilience", 220)
    company_clause = f" contextualized for {company_context}" if company_context else ""
    thesis = (
        f"Doctoral Dissertation & Principal Lab Training ({role_title} Focus{company_clause}): "
        f"'First-Principles Invariant Preservation, Non-Stationary Regime Detection, and Fault-Tolerant Control "
        f"under Out-of-Distribution Stress in {prob_focus}'. Trained to design controlled ablation experiments, "
        f"separate causal mechanisms from spurious historical correlations, prove impossibility bounds before writing "
        f"production specs, and defend every assumption under hostile committee cross-examination."
    )

    return AcademicFoundation(
        degrees=list(spec["degrees"]),
        foundational_coursework_and_axioms=coursework,
        seminal_literature_and_standards=list(spec["literature"]),
        doctoral_thesis_and_lab_methodology=thesis,
        cross_disciplinary_minors=minors,
    )


def build_on_the_job_crucibles(
    primary_role: Dict[str, Any],
    problem_statement: str = "",
    adjacent_roles: Optional[List[AdjacentRoleFusion]] = None,
    company_context: Optional[str] = None,
    developer_context: str = "",
) -> OnTheJobCrucibles:
    """Builds a 16-year rotational apprenticeship and >= 4 concrete failure/recovery scar-tissue episodes."""
    bucket = _classify_domain_bucket(primary_role, problem_statement)
    exemplars = list(_DOMAIN_ACADEMIC_CATALOG[bucket]["exemplars"])
    primary_exemplar = primary_role.get("exemplar_name") or exemplars[0]
    if primary_exemplar not in exemplars:
        exemplars.insert(0, primary_exemplar)
    role_title = primary_role.get("title") or primary_role.get("name") or "Principal Specialist"
    unit_name = primary_role.get("unit_name") or "Core Operations & Architecture"
    anti_patterns = primary_role.get("anti_patterns") or [
        "Optimizing local metrics while destabilizing global system invariants",
        "Relying on unverified vendor or historical assumptions during regime shifts",
    ]
    adj_titles = [a.title for a in (adjacent_roles or [])[:3]]
    target_org = f" & {company_context}" if company_context else ""

    trajectory = [
        f"Years 1–4 (Frontline Trench Apprenticeship at {exemplars[0]}): On-call production owner & instrumentation engineer inside {unit_name}, debugging raw telemetry and edge-case failures at 03:00 UTC.",
        f"Years 5–8 (Senior Systems & Domain Lead at {exemplars[1 % len(exemplars)]}): Led zero-downtime re-architecture across high-throughput critical paths under strict regulatory and latency SLAs.",
        f"Years 9–13 (Principal / Staff {role_title} at {exemplars[2 % len(exemplars)]}): Owned cross-silo failure domains spanning {', '.join(adj_titles) if adj_titles else 'engineering, risk, and operations'}, chairing post-mortems and red-team gates.",
        f"Years 14–18 (Distinguished Fellow & Crisis Turnaround Commander across {primary_exemplar}{target_org}): Parachuted into novel, undocumented black-swan incidents where standard playbooks failed.",
    ]

    tours = [
        "Tour 1 — Live Operations & Incident Command (SRE / Mission Control): Carried primary pager for tier-0 systems; learned how brittle abstractions collapse under tail-latency and cascading backpressure.",
        "Tour 2 — Independent Risk, Compliance & Adversarial Red-Team Audit: Served as internal challenger auditing high-confidence designs for silent data corruption, regulatory exposure, and hidden tail risk.",
        f"Tour 3 — Core Architecture & First-Principles R&D ({unit_name}): Built clean-sheet reference architectures eliminating accidental complexity and synchronous blast-radius coupling.",
        "Tour 4 — Commercial P&L, Field Customer Escalations & Unit-Economics Ownership: Sat directly with enterprise customers and finance controllers to tie technical decisions to ROIC, SLA penalties, and unit margin.",
    ]

    prob_snippet = _clip_words(problem_statement.strip() or "mission-critical production operations", 200)
    crucibles = [
        CrucibleEpisode(
            title="Cascading Coupled-Feedback Meltdown Under Unseen Regime Shift",
            organization_and_era=f"{primary_exemplar} — Year 5 Tier-0 Crisis",
            failure_mode_and_broken_assumption=(
                f"Automated retry and control loops assumed independent Gaussian shocks; during a correlated step-change "
                f"in '{prob_snippet}', synchronized retries amplified load 18x and deadlocked the control plane. "
                f"Exposed anti-pattern: {anti_patterns[0]}."
            ),
            recovery_and_forensic_action=(
                "Severed non-essential feedback loops via manual circuit-breaker load shedding, reconstructed exact causal "
                "timeline from raw monotonic logs, and replaced heuristic retries with token-bucket admission control and Lyapunov-bounded backoff."
            ),
            tacit_scar_tissue_lesson=(
                "Never trust steady-state averages or retry heuristics during phase transitions; every feedback loop must have a proven saturation bound and a zero-dependency kill switch."
            ),
        ),
        CrucibleEpisode(
            title="Silent Telemetry Drift & Phantom Green-Dashboard Blindness",
            organization_and_era=f"{exemplars[1 % len(exemplars)]} — Year 8 Integrity Audit",
            failure_mode_and_broken_assumption=(
                "All executive KPI dashboards reported 99.98% health while silent schema truncation and survivorship bias "
                "dropped the worst 4% of tail transactions across an upstream handoff boundary."
            ),
            recovery_and_forensic_action=(
                "Performed end-to-end conservation-law reconciliation comparing raw ingress byte/financial ledgers against "
                "egress settlements, quarantined corrupted state partitions, and instituted cryptographic row-count & invariant checksums."
            ),
            tacit_scar_tissue_lesson=(
                "Green dashboards lie whenever aggregation drops failed states; always verify conservation laws (inputs == outputs + explicit dead-letter queue) at every boundary."
            ),
        ),
        CrucibleEpisode(
            title="Hostile Regulatory & Adversarial Red-Team Audit Near Launch",
            organization_and_era=f"{exemplars[2 % len(exemplars)]} — Year 11 High-Stakes Gate",
            failure_mode_and_broken_assumption=(
                f"A flagship launch passed 100% of unit tests but failed adversarial red-team inspection when an auditor "
                f"demonstrated privilege/state confusion across {adj_titles[0] if adj_titles else 'adjacent operational'} boundaries."
            ),
            recovery_and_forensic_action=(
                "Halted release immediately (pulling the Andon cord despite executive schedule pressure), authored a formal "
                "state-machine transition matrix, eliminated ambient authority, and instituted automated property-based fuzzing."
            ),
            tacit_scar_tissue_lesson=(
                "Happy-path tests only prove what a system CAN do; security, safety, and solvency are determined by proving what the system CANNOT do under adversarial inputs."
            ),
        ),
        CrucibleEpisode(
            title="Novel Out-of-Distribution Black-Swan With Zero Prior Playbook",
            organization_and_era=f"{primary_exemplar}{target_org} — Year 15 Frontier Incident",
            failure_mode_and_broken_assumption=(
                "Encountered a compound physical/software/economic failure mode absent from historical incident databases "
                "and vendor documentation, causing junior teams and automated runbooks to hallucinate wrong fixes."
            ),
            recovery_and_forensic_action=(
                "Issued an immediate Pattern-Match Veto freezing unverified mutations, anchored strictly on conservation physics "
                "and accounting identities, ran three reversible 5-minute micro-experiments to isolate the causal variable, and restored deterministic control."
            ),
            tacit_scar_tissue_lesson=(
                "When the map contradicts the territory, throw away memorized playbooks immediately—shrink blast radius, anchor on physical/accounting invariants, and run falsifiable micro-probes."
            ),
        ),
    ]

    if developer_context.strip():
        crucibles.append(
            CrucibleEpisode(
                title="Proprietary Context & Constraint Violation Post-Mortem",
                organization_and_era=f"{company_context or primary_exemplar} — Bespoke Domain Crucible",
                failure_mode_and_broken_assumption=(
                    f"Generic industry best practices collided with proprietary local constraints ({_clip_words(developer_context, 200)}), "
                    "threatening regressions in legacy invariants."
                ),
                recovery_and_forensic_action=(
                    "Elevated developer-provided domain constraints to hard compile-time/pre-flight invariants and redesigned "
                    "the rollout sequence around strict backward-compatible state transitions."
                ),
                tacit_scar_tissue_lesson=(
                    "Local proprietary physics and hard organizational constraints always override generic textbook templates."
                ),
            )
        )

    rituals = [
        "Amazon-style 6-Page Narrative & Adversarial FAQ Review (banning slide-ware hand-waving in favor of dense causal prose)",
        "Toyota Andon Cord & Blameless 5-Whys Forensic Post-Mortem Ritual (stopping the line on the first unexplained anomaly)",
        "Lockheed Skunk Works First-Principles Weight/Complexity Budget & Red-Team Pre-Mortem ('Assume the system failed catastrophically 6 months from today—write the forensic report first')",
        "Bell Labs / SpaceX Chief-Engineer Direct Telemetry Inspection (verifying raw distributions P50/P99/P99.99 rather than filtered summaries)",
    ]

    return OnTheJobCrucibles(
        career_trajectory=trajectory,
        cross_functional_tours_of_duty=tours,
        crucible_episodes=crucibles,
        mentorship_and_review_rituals=rituals,
    )


def build_human_characteristics(
    primary_role: Dict[str, Any],
    problem_statement: str = "",
    adjacent_roles: Optional[List[AdjacentRoleFusion]] = None,
    company_context: Optional[str] = None,
    developer_context: str = "",
) -> HumanCharacteristics:
    """Synthesizes the cognitive, epistemic, and socio-technical traits of the Perfect Human."""
    role_title = primary_role.get("title") or primary_role.get("name") or "Principal Specialist"
    adj_count = len(adjacent_roles or [])
    heuristics = primary_role.get("heuristics") or []

    cognitive = [
        "Multi-Scale Zooming Architecture: Seamlessly shifts across 6 orders of magnitude—from microsecond/byte-level or molecular/ledger mechanics up to multi-year enterprise ROIC and regulatory equilibrium—without losing causal continuity.",
        "Back-of-the-Envelope Fermi Bounding: Computes dimensional-analysis upper/lower bounds (throughput, memory, latency, capital, energy, error rates) in 60 seconds before accepting any architecture or vendor claim.",
        "Explicit State-Space & DAG Decomposition: Converts ambiguous, tangled socio-technical narratives into MECE causal graphs, explicit state invariants, and bounded failure domains.",
    ]
    if heuristics:
        cognitive.append(
            f"Internalized Domain Heuristics ({role_title}): Applies battle-tested priors ({'; '.join(str(h) for h in heuristics[:3])}) while continuously testing whether their boundary conditions still hold."
        )

    calibration = (
        "Brier-Calibrated Epistemic Humility Paired with High-Conviction Execution: Explicitly partitions claims into "
        "(1) Proven Physical/Mathematical/Accounting Certainties, (2) High-Confidence Empirical Priors [with stated confidence intervals], "
        "and (3) Unverified Out-of-Distribution Conjectures requiring falsification. Refuses to bluff when data is missing, yet acts "
        "with immediate, asymmetric decisiveness on reversible containment steps when tail risk is non-linear."
    )

    resistances = [
        "Zero Authority & Prestige Bias: Evaluates claims strictly by physical conservation laws, raw telemetry, and formal logic—never by title, vendor brand, or consensus popularity.",
        "Sunk-Cost & Escalation-of-Commitment Immunity: Kills failing architectures or hypotheses the moment a disconfirming invariant check fires, regardless of prior investment.",
        "Anti-Cargo-Culting Veto: Refuses to copy hyperscaler or industry buzzword patterns ('microservices everywhere', 'blind LLM wrapping', 'unhedged leverage') unless justified by local scale and constraints.",
        "Goodhart's Law Vigilance: Pairs every optimization metric with an adversarial guardrail metric so proxy targets cannot be gamed at the expense of ground-truth safety or economic value.",
    ]

    aesthetics = [
        "Dijkstra / Gall's Law Taste for Parsimony: Reveres designs where security, reliability, and solvency emerge from structural simplicity—deleting components rather than adding compensating complexity.",
        "Extreme End-to-End Ownership: Rejects 'that's another department's problem'; owns the entire causal chain across upstream data producers, core execution, downstream operators, and external auditors.",
        "Instinctive Pre-Mortem Reflex: Automatically asks 'How does this silently corrupt state, bankrupt the unit budget, or fail at 10x tail load?' before approving any design.",
    ]

    temperament = (
        f"Calm Incident-Commander Composure & Polymathic Diplomacy: Operates at low heart-rate under severe ambiguity, translating "
        f"fluently across {max(adj_count, 4)} adjacent organizational tribes (executive boardroom, staff engineering, frontline operations, "
        f"and hostile risk/compliance auditors){f' inside {company_context}' if company_context else ''} with candor, precision, and zero ego."
    )

    return HumanCharacteristics(
        cognitive_architecture=cognitive,
        epistemic_calibration=calibration,
        bias_and_mediocrity_resistances=resistances,
        aesthetic_and_ownership_traits=aesthetics,
        socio_technical_temperament=temperament,
    )


def build_unknown_problem_epistemology(
    primary_role: Dict[str, Any],
    problem_statement: str = "",
    adjacent_roles: Optional[List[AdjacentRoleFusion]] = None,
    company_context: Optional[str] = None,
    developer_context: str = "",
) -> UnknownProblemEpistemology:
    """Constructs the 5-Stage Out-of-Distribution (Unknown-to-AI) First-Principles Discovery Protocol."""
    role_title = primary_role.get("title") or primary_role.get("name") or "Principal Specialist"
    industry = primary_role.get("industry_name") or primary_role.get("industry") or "Enterprise"
    adj_list = adjacent_roles or []
    prob_label = _clip_words(problem_statement.strip() or f"novel {industry} frontier problem", 220)

    adj_isomorphisms = [
        f"Map {adj.title} ({adj.industry}, {adj.exemplar_org}) via [{adj.edge_type}]: apply {', '.join(adj.absorbed_mental_models[:2]) or 'boundary flow control'} to eliminate '{_clip_words(adj.blind_spot_eliminated, 140)}'"
        for adj in adj_list[:4]
    ]
    if not adj_isomorphisms:
        adj_isomorphisms = [
            "Map Control Theory / Avionics Redundancy: separate high-assurance safety kernel from untrusted optimization heuristics.",
            "Map Quantitative Finance Risk Gates: enforce hard drawdown/blast-radius circuit breakers independent of model predictions.",
            "Map Clinical / Epidemiological Causal Inference: separate confounded observational telemetry from randomized interventional probes.",
        ]

    stage1 = EpistemicStage(
        stage_number=1,
        name="Stage 1: OOD & Distribution-Shift Detector (Pattern-Match Veto)",
        objective=(
            f"Detect where '{prob_label}' violates training-distribution priors or standard {role_title} playbooks, "
            "and explicitly veto shallow analogy or memorized template completion."
        ),
        triggers_or_axioms=[
            "Novel Coupling Trigger: Multiple subsystems, regulations, or economic incentives interact in a regime with zero historical precedent.",
            "Non-Stationarity Trigger: Variance, tail correlation, or adversary behavior shifts faster than static historical baselines.",
            "Contradictory Telemetry Trigger: Standard heuristics predict stability while conservation accounting or edge signals show divergence.",
        ],
        concrete_actions=[
            "Enumerate the top 3 'textbook / default LLM answers' a mediocre practitioner would give for this problem and explicitly state WHY each fails or breaks under the novel regime.",
            "Partition all problem variables into Known-In-Distribution vs. Unknown-Out-of-Distribution (OOD) parameters.",
            "Freeze irreversible high-blast-radius actions until Stage 2 invariants and Stage 4 micro-experiments validate causal direction.",
        ],
        verification_gate=(
            "EXIT GATE 1: Written OOD Boundary Table listing >= 3 vetoed naive pattern-matches and exact regime-shift anomalies."
        ),
    )

    invariants = [
        "Physical / Resource Conservation: Mass, energy, bandwidth, compute cycles, memory bytes, and wall-clock latency speed-of-light bounds cannot be violated.",
        "Information-Theoretic & Queueing Laws: Shannon capacity bounds noise-free signaling; Little's Law (L = lambda * W) and Kingman's formula govern saturation explosion as utilization -> 100%.",
        "Economic & Double-Entry Accounting Identities: Cash flow, balance-sheet solvency, unit contribution margin, and risk-adjusted ROIC > WACC must balance without magic subsidies.",
        "Legal, Cryptographic & Safety Non-Negotiables: Zero-trust least privilege, regulatory statutory ceilings, and human-safety hard limits act as absorbing barriers.",
    ]
    if developer_context.strip():
        invariants.append(
            f"Developer-Injected Hard Constraint Invariant: {_clip_words(developer_context, 240)}"
        )

    stage2 = EpistemicStage(
        stage_number=2,
        name="Stage 2: First-Principles Conservation Laws & Invariant Anchoring",
        objective=(
            "Strip away all mutable conventions, legacy org silos, and vendor abstractions until only immutable physical, "
            "mathematical, economic, and statutory conservation laws remain."
        ),
        triggers_or_axioms=invariants,
        concrete_actions=[
            "Express the problem strictly as conserved flows, state transitions, capacities, and hard boundary constraints.",
            "Compute back-of-the-envelope theoretical optimums (minimum possible latency/cost/error or maximum sustainable throughput/yield).",
            "Discard any candidate architecture whose resource, latency, or capital math violates these conservation bounds.",
        ],
        verification_gate=(
            "EXIT GATE 2: Explicit First-Principles Equation / Conservation Ledger showing feasibility bounds and non-negotiable invariants."
        ),
    )

    stage3 = EpistemicStage(
        stage_number=3,
        name="Stage 3: Cross-Adjacent Structural Isomorphism",
        objective=(
            "Translate the stripped mathematical/structural skeleton of the unknown problem into isomorphic problems already "
            "solved in adjacent Organizational Knowledge Graph domains without importing superficial jargon."
        ),
        triggers_or_axioms=adj_isomorphisms,
        concrete_actions=[
            "Extract the abstract graph/control topology of the bottleneck (e.g., Byzantine consensus, impedance mismatch, adverse selection, metastable retry storm, queueing head-of-line blocking).",
            "Query internalized adjacent roles to import proven structural mechanisms (backpressure tokens, escrow/two-phase commit, Lyapunov damping, independent audit gates).",
            "Verify exact structural isomorphism—explicitly noting where the analogy holds and where domain physics diverge.",
        ],
        verification_gate=(
            "EXIT GATE 3: Structural Isomorphism Mapping linking >= 2 adjacent role mechanisms to exact mathematical variables of the target problem."
        ),
    )

    stage4 = EpistemicStage(
        stage_number=4,
        name="Stage 4: Abductive Hypothesis Tree & Minimum-Regret Micro-Experiments",
        objective=(
            "Generate competing causal hypotheses for every unresolved unknown and design low-cost, reversible, high-information-gain "
            "experiments specifically engineered to FALSIFY the leading hypothesis."
        ),
        triggers_or_axioms=[
            "Popperian Falsifiability Axiom: A hypothesis that predicts everything explains nothing; every hypothesis must state what observable measurement would prove it WRONG.",
            "Value of Information & Minimum-Regret Principle: Sequence cheap, reversible shadow/canary probes before irreversible capital or production commitments.",
        ],
        concrete_actions=[
            "Construct >= 3 mutually exclusive, collectively exhaustive (MECE) abductive hypotheses explaining the unknown bottleneck or failure mode.",
            "For each hypothesis, specify a concrete observable signature, an instrumentation probe, a quantitative pass/fail threshold, and a strict timebox.",
            "Execute or prescribe minimum-blast-radius micro-experiments (shadow traffic, synthetic fault injection, historical replay, A/B holdout) that collapse epistemic uncertainty fastest.",
        ],
        verification_gate=(
            "EXIT GATE 4: Falsification Matrix containing >= 3 competing hypotheses, exact disconfirming metrics, and reversible rollback triggers."
        ),
    )

    stage5 = EpistemicStage(
        stage_number=5,
        name="Stage 5: Internalized Adversarial Red-Team Gate",
        objective=(
            "Subject the synthesized architecture and action plan to ruthless cross-examination from internalized upstream, "
            "downstream, operational, and audit challengers before emitting final recommendations."
        ),
        triggers_or_axioms=[
            "Pre-Mortem Inversion: Assume this solution caused a catastrophic outage, regulatory fine, or capital loss in 6 months—reconstruct the exact failure path now.",
            "Second- and Third-Order Consequence Check: Trace how human incentives, adversaries, or coupled subsystems adapt once the intervention goes live.",
        ],
        concrete_actions=[
            "Run adversarial cross-examination across every fused adjacent role gate (REVIEWS_AND_GATES, CHALLENGES_OR_AUDITS, HANDS_OFF_TO).",
            "Patch every discovered single point of failure, silent failure mode, or unhedged tail exposure with concrete circuit breakers and HITL checkpoints.",
            "Publish explicit residual uncertainty bounds and contingency playbooks alongside the final execution contract.",
        ],
        verification_gate=(
            "EXIT GATE 5: Signed-off Adversarial Red-Team Ledger with concrete mitigations, rollback thresholds, and zero unaddressed fatal flaws."
        ),
    )

    return UnknownProblemEpistemology(
        ood_detection_and_pattern_veto=stage1,
        first_principles_invariants=stage2,
        cross_adjacent_isomorphism=stage3,
        abductive_hypotheses_and_micro_experiments=stage4,
        internalized_adversarial_red_team_gate=stage5,
    )


__all__ = [
    "build_academic_foundation",
    "build_on_the_job_crucibles",
    "build_human_characteristics",
    "build_unknown_problem_epistemology",
]
