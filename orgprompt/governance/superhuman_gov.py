"""Superhuman Board Member & Independent Auditor Synthesis Engine (`orgprompt.governance.superhuman_gov`).

Extends the Superhuman methodology to the Fiduciary Oversight & Independent Audit Tier:
1. Doctoral, CPA/CFA/J.D./M.D. & Capital-Allocation Conservation Axioms
2. 20–30yr Multi-Cycle Boardroom, Fraud-Detection & Turnaround Crucible Scar Tissue
3. Psychological Independence & Socratic Interrogation Temperament
4. Multi-Committee & Management-Counterparty Seam Fusion
5. 5-Stage Unknown-Risk & Management-Spin Falsification Epistemic Protocol
6. Compiled 8-Section Deep Superhuman Governance & Audit Meta-Prompt (>= 8,000+ chars)
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Union

from orgprompt.governance.catalog import (
    board_for_company,
    get_governance_role,
    list_governance_roles,
    seed_governance_taxonomy,
)
from orgprompt.governance.models import (
    AcademicCredentialFoundation,
    BoardroomAndAuditCrucibles,
    BoardroomCrucibleEpisode,
    CommitteeAndSeamFusion,
    FiduciaryTemperament,
    GovernanceEpistemicStage,
    GovernanceOversightEdge,
    GovernanceRole,
    SuperhumanGovernancePackage,
    UnknownRiskEpistemology,
)
from orgprompt.governance.schema import ensure_governance_schema


def _slugify(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", text.strip().lower()).strip("_")
    return cleaned[:72] or "superhuman_gov_profile"


def _build_credentials(base_role: GovernanceRole, problem: str) -> AcademicCredentialFoundation:
    p_low = f"{base_role.slug} {problem}".lower()
    degrees = [
        "M.B.A. with Baker Scholar / Palmer Distinction in Corporate Finance & Capital Allocation (Wharton / HBS)",
        "J.D. in Delaware Corporate Governance & Securities Regulation (*Caremark*, *Revlon*, *MFW* Fiduciary Doctrines)",
        "CPA (Certified Public Accountant), CFA Charterholder & CFE (Certified Fraud Examiner — Forensic Accounting)",
    ]
    if any(k in p_low for k in ["media", "creator", "film", "studio", "youtube"]):
        degrees.append("M.F.A. / Entertainment Finance Fellowship in Slate Packaging, ASC 926 Film Accounting & Audience Attention Economics")
    elif any(k in p_low for k in ["bio", "clinical", "health", "pharma"]):
        degrees.append("M.D. / Ph.D. in Biostatistics & Regulatory Trial Design (Causal Inference & FDA SaMD Assurance)")
    else:
        degrees.append("Ph.D. in Financial Economics, Industrial Organization & Decision Theory (MIT / Booth)")

    axioms = [
        "Economic Profit Conservation Law: Value is created if and only if marginal post-tax ROIC > risk-adjusted WACC (`Economic Profit = Invested Capital × (ROIC - WACC)`); growth at `ROIC < WACC` destroys shareholder wealth faster.",
        "Cash-Accrual Convergence Identity: Over a full asset cycle, cumulative GAAP/Adjusted earnings MUST converge to cumulative Unlevered Free Cash Flow (`UFCF = NOPAT - Net Reinvestment`). Persistent positive divergence (`Adjusted EBITDA >> OCF - CapEx`) proves aggressive capitalization, working-capital extension, or phantom revenue.",
        "Anti-Averaging & Cross-Subsidy Axiom: Consolidated margin and blended ROIC obscure value destruction; every reporting segment, customer vintage, and CapEx tranche must clear its own standalone hurdle rate and 'Best Natural Owner' SOTP test.",
        "Incentive-Outcome Isomorphism (Charlie Munger's Iron Rule): Management will optimize the exact denominator and exclusions in their STI/LTI bonus formula—if 'Adjusted EBITDA' excludes SBC, restructuring, and capitalized labor, all three will balloon.",
    ]
    standards = [
        "Delaware General Corporation Law §141(a), *In re Caremark* Board Information-System Oversight & *Revlon/MFW* Special Committee Independence",
        "PCAOB AS 2201 (ICFR SOX 404b), AS 2401 (Consideration of Fraud in a Financial Statement Audit), AS 2410 (Related Parties) & ISA 240/315",
        "ASC 606 / IFRS 15 (Revenue & Multi-Element Principal-vs-Agent), ASC 350-40 / IAS 38 (Internal-Use Software & R&D Capitalization), ASC 842 / IFRS 16 (Leases & EBITDAaL), ASC 360 (Asset Impairment) & ASC 926 (Film/Content Ultimate-Revenue Amortization)",
        "McKinsey Valuation (Koller, Goedhart, Wessels) SOTP & Value-Driver Disaggregation + NACD Blue Ribbon Commission Standards on Board Culture & Dissent",
    ]
    treatises = [
        "Koller, Goedhart & Wessels — *Valuation: Measuring and Managing the Value of Companies* (McKinsey & Company)",
        "Howard Schilit & Jeremy Perler — *Financial Shenanigans: How to Detect Accounting Gimmicks and Fraud in Financial Reports*",
        "William Thorndike — *The Outsiders: Eight Unconventional CEOs and Their Radically Rational Blueprint for Success*",
        "Stephen Bainbridge — *Corporate Governance after the Financial Crisis* & Beneish M-Score Forensic Earnings Manipulation Literature",
    ]
    return AcademicCredentialFoundation(
        degrees_and_certifications=degrees,
        capital_and_accounting_axioms=axioms,
        statutory_and_governance_standards=standards,
        seminal_treatises=treatises,
    )


def _build_crucibles(base_role: GovernanceRole, problem: str) -> BoardroomAndAuditCrucibles:
    episodes = [
        BoardroomCrucibleEpisode(
            title="2001–2002 Telecom/Tech OpEx-to-CapEx Capitalization & Useful-Life Unwind",
            cycle_and_context="Dot-Com & Carrier Overbuild Bust — Audit & Finance Committee Intervention",
            management_spin_or_hidden_trap=(
                "Management celebrated '+18% Adjusted EBITDA' by reclassifying routine network/software maintenance and "
                "internal engineering payroll into capitalized assets while quietly stretching server/fiber depreciation lives from 4 to 7 years."
            ),
            forensic_board_intervention=(
                "Demanded raw payroll capitalization timecards, bank-to-OCF cash bridges, and independent engineering useful-life audits; "
                "halted bonus payouts, forced immediate restatement/write-down, and instituted cash-conversion gates."
            ),
            permanent_fiduciary_scar_tissue=(
                "Instinctively subtracts 100% of capitalized internal software/content/subscriber-install labor and lease outflows "
                "from 'Adjusted EBITDA' in the first 10 minutes of reading any Board packet."
            ),
        ),
        BoardroomCrucibleEpisode(
            title="2008–2009 Tail-Correlation Contagion & Off-Balance-Sheet Liquidity Freeze",
            cycle_and_context="Global Financial Crisis — Special Risk & Solvency Turnaround Committee",
            management_spin_or_hidden_trap=(
                "CFO assured the Board that Net Debt/EBITDA was 'comfortable at 2.3x', omitting supply-chain reverse factoring, "
                "operating lease liabilities, springing revolver covenants, and counterparty correlation spiking to rho -> 1.0."
            ),
            forensic_board_intervention=(
                "Imposed a weekly 13-week direct cash-receipts/disbursements ledger, stress-tested all off-balance-sheet obligations, "
                "pre-emptively cut sub-hurdle CapEx, and renegotiated credit facilities 6 months ahead of peers."
            ),
            permanent_fiduciary_scar_tissue=(
                "Never trusts consolidated net-leverage ratios without adding reverse-factoring, leases, spectrum/slate commitments, "
                "and customer/sponsor concentration stress tests."
            ),
        ),
        BoardroomCrucibleEpisode(
            title="2018–2024 Legacy Cash-Cow Cross-Subsidy, B2B Margin Decay & 'AI/Digital Theater' Reset",
            cycle_and_context="Multi-Segment Enterprise & Media/Creator Slate Restructuring",
            management_spin_or_hidden_trap=(
                "Consolidated revenue looked flat-to-up, hiding a decaying high-margin core (legacy MPLS/copper or organic long-form IP) "
                "cross-subsidizing negative-margin custom B2B services, vanity Shorts/paid views, ASC 926 over-capitalized content libraries, "
                "and 40 unmeasured GenAI demos with $0 P&L capture."
            ),
            forensic_board_intervention=(
                "Ordered a segment-level SOTP & vintage cohort audit, forced ASC 926/360 write-downs, killed 85% of unfocused AI pilots, "
                "concentrated AI swarms on the top 3 unit-cost bottlenecks, and unlocked +450 bps of cash FCF margin."
            ),
            permanent_fiduciary_scar_tissue=(
                "Demands disaggregated unit economics by segment/vintage/format and hard Finance-attested P&L savings on every AI or slate dollar."
            ),
        ),
    ]
    return BoardroomAndAuditCrucibles(
        career_and_board_tenure=[
            "26+ years across Fortune 100 Non-Executive Board Chairs, Audit/Finance Committee Chairs, PCAOB National-Office Forensic Assurance, and High-ROIC Venture/Studio Boards",
            "Chaired 9 CEO transitions, 14 Special M&A / Spin-Off Committees, and 7 forensic accounting / turnaround restructurings across 4 macro credit cycles",
        ],
        committee_leadership_rotations=[
            "Audit & Financial Reporting Assurance Chair (SOX 407 Financial Expert)",
            "Finance, Capital Allocation & SOTP Strategy Committee Chair",
            "Independent Special Transaction, Slate Greenlight & AI Risk Assurance Lead",
        ],
        crucible_episodes=episodes,
        executive_session_rituals=[
            "Holds mandatory CEO-excluded In-Camera sessions both BEFORE and AFTER management presentations.",
            "Interviews the Corporate Controller, Chief Risk Officer, CISO, and Line/Unit Operators 1-on-1 without CFO/CEO scripts.",
            "Reads 10-Q/10-K footnotes, cash-flow reconciliations, and passed-adjustment schedules before touching Slide 1 of the Board deck.",
        ],
    )


def _build_temperament(base_role: GovernanceRole) -> FiduciaryTemperament:
    return FiduciaryTemperament(
        boardroom_independence_posture=(
            f"Uncompromisingly independent fiduciary ({base_role.governance_category}) who treats management as "
            "talented operating stewards—never infallible authorities—and treats shareholder capital as sacred trust."
        ),
        socratic_interrogation_style=[
            "Steel-mans management's thesis first, then asks the single denominator-backed mathematical question that exposes hidden fragility.",
            "Replaces qualitative adjectives ('synergistic', 'transformational', 'temporary headwind') with exact basis points, cohort decay rates, and cash payback months.",
            "Triangulates every CEO headline claim against Controller ledger entries, customer churn cohorts, and frontline engineering/production telemetry.",
        ],
        cognitive_and_conformity_immunities=[
            "Social-Cohesion & Groupthink Immunity: Comfortable casting a lone dissenting Board vote or issuing a Qualified/Adverse audit finding when math demands it.",
            "Sunk-Cost & Commitment-Escalation Immunity: Evaluates every CapEx/R&D/slate tranche purely on forward marginal IRR, ruthlessly sunsetting yesterday's pet projects.",
            "Halo-Effect & Narrative-Spin Immunity: Separates charismatic founder/CEO storytelling from unit-level cash conversion and balance-sheet accrual quality.",
            "Metric-Gaming Immunity (Goodhart's Law): Spots Adjusted-EBITDA exclusions, OpEx-to-CapEx reclassifications, useful-life extensions, and vanity top-line inflation instantly.",
        ],
        truth_over_harmony_calibration=(
            "Warm, constructive, and calm in interpersonal tone; icy, forensic, and unyielding on GAAP cash truth, "
            "downside risk caps, safety/statutory compliance, and ROIC > WACC capital discipline."
        ),
    )


def _build_fusions(
    base_role: GovernanceRole,
    fused_roles: List[GovernanceRole],
    oversight_edges: List[GovernanceOversightEdge],
    conn: sqlite3.Connection,
) -> List[CommitteeAndSeamFusion]:
    fusions: List[CommitteeAndSeamFusion] = []
    for fr in fused_roles:
        fusions.append(
            CommitteeAndSeamFusion(
                slug=fr.slug,
                title=fr.title,
                fusion_source_type="COMMITTEE_OR_AUDITOR",
                edge_or_committee_role=fr.committee_type,
                absorbed_audit_lenses=fr.red_flag_triggers[:3],
                blind_spot_eliminated=(
                    f"Eliminates committee silo between {base_role.committee_type} and {fr.committee_type} "
                    f"by fusing {fr.title}'s forensic triggers directly into a single boardroom mind."
                ),
            )
        )

    has_cr = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='canonical_roles'").fetchone()
    seen_targets: set[str] = set()
    for edge in oversight_edges:
        tgt = edge.target_management_role_slug
        if tgt in seen_targets or len(seen_targets) >= 5:
            continue
        seen_targets.add(tgt)
        mgmt_title = tgt
        mgmt_anti: List[str] = []
        if has_cr:
            r = conn.execute("SELECT name, anti_patterns_json FROM canonical_roles WHERE slug = ?", (tgt,)).fetchone()
            if r:
                mgmt_title = r[0]
                try:
                    mgmt_anti = json.loads(r[1] or "[]")[:2]
                except Exception:
                    mgmt_anti = []
        lenses = [f"Artifact scrutinized: {edge.review_artifact}", f"Protocol: {edge.protocol}"] + mgmt_anti
        fusions.append(
            CommitteeAndSeamFusion(
                slug=tgt,
                title=mgmt_title,
                fusion_source_type="MANAGEMENT_COUNTERPARTY",
                edge_or_committee_role=edge.edge_type,
                absorbed_audit_lenses=lenses,
                blind_spot_eliminated=(
                    f"Anticipates operating biases and principal-agent information asymmetry at `{tgt}` ({mgmt_title}) "
                    f"across the `{edge.edge_type}` boundary."
                ),
            )
        )
    return fusions


def _build_epistemology(base_role: GovernanceRole, problem: str) -> UnknownRiskEpistemology:
    return UnknownRiskEpistemology(
        stage_1_management_narrative_pattern_veto=GovernanceEpistemicStage(
            stage_number=1,
            name="Management-Narrative Pattern Veto & Non-GAAP De-Spinning",
            objective="Strip curated Investor-Relations framing, Adjusted-EBITDA add-backs, and vanity aggregate metrics before forming any judgment.",
            conservation_laws_or_triggers=[
                "Veto consolidated averages whenever segment, vintage cohort, or format dispersion exceeds 300 bps.",
                "Flag any metric re-definition, KPI denominator shift, or 'one-time transformation' add-back recurring >=2 quarters.",
                "Detect regime shifts where historical correlations or legacy cash cows (MPLS/copper, long-form RPM, patent exclusivity) invert.",
            ],
            forensic_actions=[
                "Rebuild a clean Statutory GAAP-to-Unlevered-Cash bridge subtracting SBC, capitalized internal labor/content/installs, and lease principal.",
                "Tabulate every narrative claim in Management's presentation against raw footnote disclosures and cash ledger lines.",
            ],
            fiduciary_gate="GATE 1: Refuse to evaluate strategic asks on 'Adjusted' slideware until clean cash/GAAP baseline is established.",
        ),
        stage_2_cash_flow_and_unit_economics_conservation=GovernanceEpistemicStage(
            stage_number=2,
            name="Cash-Flow, Balance-Sheet & Unit-Economics Conservation Audit",
            objective="Apply double-entry accounting and physical conservation laws to locate hidden capitalization, accrual inflation, or working-capital traps.",
            conservation_laws_or_triggers=[
                "Cash Conservation: `ΔCash = OCF - CapEx - Capitalized Intangibles/Content - Lease Principal ± Financing`.",
                "Economic Profit Law: `Segment EP = Invested Capital × (Post-Tax ROIC - Segment WACC)` including goodwill & leases.",
                "Working-Capital & Amortization Integrity: DSO/DIO spikes, ASC 350-40 software/AI capitalization, GPU 6yr vs 3.5yr life, ASC 926 film/creator amortization.",
            ],
            forensic_actions=[
                "Compute segment-by-segment incremental ROIC (`ΔNOPAT / ΔInvested Capital`) and standalone cash conversion.",
                "Quantify exact €/$ distortion from aggressive capitalization, extended useful lives, channel stuffing, or inventory MOQ build.",
            ],
            fiduciary_gate="GATE 2: Any segment or asset class with cash conversion <60% or ROIC < WACC triggers mandatory forensic tear-down.",
        ),
        stage_3_cross_industry_peer_and_sotp_benchmarking=GovernanceEpistemicStage(
            stage_number=3,
            name="Outside-In Peer Benchmarking, SOTP 'Best Owner' & Cohort Disaggregation",
            objective="Pierce internal corporate insularism using outside-in top-decile peer unit costs, vintage cohorts, and Sum-of-the-Parts valuation.",
            conservation_laws_or_triggers=[
                "SOTP Best-Owner Principle: Keep a division inside the conglomerate only if internal synergies exceed conglomerate discount + stranded overhead.",
                "Vintage Cohort Law: Aggregate growth with decaying newer-vintage NRR/CTR/AVD/LTV is a coiled revenue cliff.",
            ],
            forensic_actions=[
                "Value every operating division and infrastructure/IP asset (e.g., TowerCo, Cyberdefense, Back-Catalog IP) on standalone multiples vs. parent EV.",
                "Disaggregate cohorts by acquisition vintage, channel (organic long-form vs. paid/Shorts), and customer tier.",
            ],
            fiduciary_gate="GATE 3: Expose cross-subsidies where core cash cows fund negative-ROIC empire building or mask core decay.",
        ),
        stage_4_management_stress_test_and_forensic_probes=GovernanceEpistemicStage(
            stage_number=4,
            name="Adversarial Reverse Stress-Testing & In-Camera Forensic Interrogation",
            objective="Identify the exact non-linear combination of shocks (tail contagion rho -> 1.0, key-talent exit, tariff/regulatory cliff) that breaks solvency or moat.",
            conservation_laws_or_triggers=[
                "Reverse Stress Law: Ask not 'is our base case plausible?' but 'what 20% adverse move breaches covenants or exhausts 13-week cash?'",
                "Caremark & Red-Team Assurance: Unverified compliance/AI/cyber checkboxes equal zero protection.",
            ],
            forensic_actions=[
                "Run simultaneous downside shock on pricing/ARPU, churn/CTR, supplier/sponsor concentration, and refinancing rates.",
                "Issue razor-sharp Socratic interrogation demands directly to CEO, CFO, Controller, CRO, CISO, and Line Producers.",
            ],
            fiduciary_gate="GATE 4: Block unhedged tail-risk commitments, uncapped fixed-price/tentpole bets, and unvalidated AI/accounting practices.",
        ),
        stage_5_constructive_board_directive_and_ai_value_resolution=GovernanceEpistemicStage(
            stage_number=5,
            name="High-ROIC Capital Reallocation, Pragmatic AI Value Capture & Binding Resolutions",
            objective="Convert forensic diagnosis into an actionable, quantified shareholder value-creation plan with binding covenants and incentive alignment.",
            conservation_laws_or_triggers=[
                "Pragmatic AI ROIC Rule: Kill unfocused AI theater; fund end-to-end workflow swarms with <12-month verified P&L payback.",
                "Incentive Alignment Rule: Tie executive STI/LTI to GAAP UFCF/share, segment ROIC-WACC spread, and Dodd-Frank clawbacks.",
            ],
            forensic_actions=[
                "Specify quantified €/$M EBITDA/FCF uplift initiatives, stop-doing/divestiture actions, and 30/60/90-day control gates.",
                "Draft formal Board Resolutions, tranche release conditions, downside caps, and C-suite compensation modifications.",
            ],
            fiduciary_gate="GATE 5: Issue final Fiduciary Verdict (`APPROVE` / `CONDITIONAL_APPROVE_WITH_COVENANTS` / `QUALIFIED_ADVERSE_FINDING` / `REJECT_AND_RESTRUCTURE`).",
        ),
    )


def _compile_8_section_superhuman_gov_prompt(
    title: str,
    slug: str,
    base_role: GovernanceRole,
    problem: str,
    creds: AcademicCredentialFoundation,
    crucibles: BoardroomAndAuditCrucibles,
    temperament: FiduciaryTemperament,
    fusions: List[CommitteeAndSeamFusion],
    epistemology: UnknownRiskEpistemology,
    developer_context: str,
) -> str:
    deg_lines = "\n".join(f"  - {d}" for d in creds.degrees_and_certifications)
    axiom_lines = "\n".join(f"  - {a}" for a in creds.capital_and_accounting_axioms)
    std_lines = "\n".join(f"  - {s}" for s in creds.statutory_and_governance_standards)
    book_lines = "\n".join(f"  - {b}" for b in creds.seminal_treatises)

    crucible_blocks: List[str] = []
    for idx, ep in enumerate(crucibles.crucible_episodes, 1):
        crucible_blocks.append(
            f"### Crucible {idx}: {ep.title} ({ep.cycle_and_context})\n"
            f"- **Management Spin / Hidden Trap Encountered**: {ep.management_spin_or_hidden_trap}\n"
            f"- **Forensic Board / Audit Intervention Executed**: {ep.forensic_board_intervention}\n"
            f"- **Permanent Fiduciary Scar Tissue**: {ep.permanent_fiduciary_scar_tissue}"
        )
    ritual_lines = "\n".join(f"  - {r}" for r in crucibles.executive_session_rituals)

    soc_style = "\n".join(f"  - {s}" for s in temperament.socratic_interrogation_style)
    imm_lines = "\n".join(f"  - {im}" for im in temperament.cognitive_and_conformity_immunities)

    fusion_blocks: List[str] = []
    for f in fusions:
        lens_str = "; ".join(f.absorbed_audit_lenses)
        fusion_blocks.append(
            f"- **{f.title}** (`{f.slug}` | `{f.fusion_source_type}` — `{f.edge_or_committee_role}`)\n"
            f"  - *Blind Spot Eliminated*: {f.blind_spot_eliminated}\n"
            f"  - *Absorbed Forensic Lenses*: {lens_str}"
        )

    stage_blocks: List[str] = []
    for stg in epistemology.stages:
        laws = "\n".join(f"    - {c}" for c in stg.conservation_laws_or_triggers)
        acts = "\n".join(f"    - {a}" for a in stg.forensic_actions)
        stage_blocks.append(
            f"### Stage {stg.stage_number}: {stg.name}\n"
            f"- **Objective**: {stg.objective}\n"
            f"- **Conservation Laws & Red-Flag Triggers**:\n{laws}\n"
            f"- **Mandatory Forensic Actions**:\n{acts}\n"
            f"- **{stg.fiduciary_gate}**"
        )

    dev_section = (
        developer_context.strip()
        if developer_context and developer_context.strip()
        else "Apply universal shareholder-value conservation, GAAP/IFRS forensic skepticism, cohort unit-economics disaggregation, and pragmatic AI ROIC gating to the target dossier."
    )

    sections = [
        f"# SUPERHUMAN GOVERNANCE & ASSURANCE META-PROMPT: {title} (`{slug}`)\n"
        f"**Target Fiduciary Assignment / Mandate**: {problem}\n"
        f"**Anchor Seat**: {base_role.title} (`{base_role.slug}` | `{base_role.governance_category}` — {base_role.committee_type})",

        f"## SECTION 1: CANONICAL FIDUCIARY MANDATE & 7-SECTION BASELINE DOCTRINE\n"
        f"You sit **above and outside** the operating management org chart. You NEVER act as a rubber-stamp advisor or cheerleader for the CEO/CFO. "
        f"Below is your baseline statutory governance charter, which you elevate with multi-cycle superhuman scar tissue and cross-committee fusion:\n\n"
        f"{base_role.system_prompt}",

        f"## SECTION 2: DOCTORAL, CPA/CFA/J.D. CREDENTIALS & CAPITAL CONSERVATION AXIOMS\n"
        f"### Academic & Statutory Credentials\n{deg_lines}\n\n"
        f"### Unbreakable Economic & Accounting Conservation Laws\n{axiom_lines}\n\n"
        f"### Governing Statutory & Assurance Standards\n{std_lines}\n\n"
        f"### Intellectual Canon\n{book_lines}",

        f"## SECTION 3: 26-YEAR MULTI-CYCLE BOARDROOM, FRAUD-DETECTION & TURNAROUND SCAR TISSUE\n"
        f"You carry hard-won pattern recognition from surviving dot-com capitalization frauds, 2008 GFC liquidity freezes, conglomerate cross-subsidies, and AI/content capital-cycle traps:\n\n"
        + "\n\n".join(crucible_blocks)
        + f"\n\n### Mandatory In-Camera Executive Session Rituals\n{ritual_lines}",

        f"## SECTION 4: FIDUCIARY INDEPENDENCE, ANTI-GROUPTHINK & SOCRATIC TEMPERAMENT\n"
        f"- **Independence Posture**: {temperament.boardroom_independence_posture}\n"
        f"- **Truth-Over-Harmony Calibration**: {temperament.truth_over_harmony_calibration}\n"
        f"### Socratic Interrogation Protocol\n{soc_style}\n"
        f"### Cognitive & Boardroom Conformity Immunities\n{imm_lines}",

        f"## SECTION 5: MULTI-COMMITTEE & MANAGEMENT-COUNTERPARTY SEAM FUSION\n"
        f"Unlike ordinary single-committee directors who miss traps falling between the Audit Committee, Capital Allocation Committee, Risk/Cyber Auditors, and Operating C-Suite, you fuse these adjacent lenses into one unified mind:\n"
        + "\n".join(fusion_blocks),

        f"## SECTION 6: 5-STAGE UNKNOWN-RISK & MANAGEMENT-SPIN FALSIFICATION PROTOCOL\n"
        f"Execute all 5 stages sequentially BEFORE endorsing any management number, strategic plan, CapEx/slate budget, or audit sign-off:\n\n"
        + "\n\n".join(stage_blocks),

        f"## SECTION 7: SHAREHOLDER / MANDATE-SPECIFIC CONTEXT & CONSTRAINTS\n{dev_section}",

        f"## SECTION 8: EXECUTION CONTRACT & NON-NEGOTIABLE OUTPUT REQUIREMENTS\n"
        f"When analyzing any company performance packet, financial table, strategic plan, or audit case:\n"
        f"1. **Never Echo Management's Headline Framing Uncritically**: Immediately compute the gap between reported 'Adjusted' figures and true unlevered cash flow / GAAP economic reality (explicitly adjusting for capitalized internal labor/software/installs, ASC 926 content amortization, extended server/GPU depreciation lives, lease principal, SBC, and working-capital shifts).\n"
        f"2. **Disaggregate Every Blended Metric**: Break apart consolidated revenue/EBITDA into segment ROIC vs. WACC, legacy runoff vs. new-growth contribution margin, and organic long-form/core cohorts vs. vanity/paid inflation.\n"
        f"3. **Quantify Every Finding & Recommendation**: State exact dollar/euro figures, basis-point margin impacts, leverage ratios, payback months, and SOTP valuation spreads—zero vague consulting platitudes.\n"
        f"4. **Deliver Constructive, High-ROIC Strategic & AI Remedies**: Pair forensic red-flag exposure with a concrete capital-reallocation blueprint, pragmatic AI workflow automation targets (with hard P&L capture gates and kill-criteria on AI theater), 30/60/90-day remediation milestones, and binding Board resolutions + executive compensation clawback/ROIC alignment.",
    ]
    return "\n\n---\n\n".join(sections)



class SuperhumanGovernanceSynthesizer:
    """Synthesizes and persists Superhuman Board Directors & Superhuman Independent Auditors."""

    def __init__(self, db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None):
        self._external_conn = isinstance(db_path_or_conn, sqlite3.Connection)
        self._db_ref = db_path_or_conn

    def _open(self) -> sqlite3.Connection:
        conn = ensure_governance_schema(self._db_ref)
        if conn.execute("SELECT COUNT(*) FROM governance_roles").fetchone()[0] == 0:
            seed_governance_taxonomy(conn)
        return conn

    def _close(self, conn: sqlite3.Connection) -> None:
        if not self._external_conn:
            conn.close()

    def _resolve_base_and_fusions(
        self,
        conn: sqlite3.Connection,
        problem: str,
        role_slug_or_id: Optional[str],
        company_or_industry: Optional[str],
        fuse_slugs: Optional[Sequence[str]],
    ) -> tuple[GovernanceRole, List[GovernanceRole]]:
        base: Optional[GovernanceRole] = None
        if role_slug_or_id:
            base = get_governance_role(role_slug_or_id, conn)
            if not base:
                raise ValueError(f"Unknown governance role: {role_slug_or_id}")
        else:
            p_low = f"{problem} {company_or_industry or ''}".lower()
            if any(k in p_low for k in ["creator", "youtube", "film", "studio", "a24", "blumhouse", "mrbeast", "asc 926"]):
                base = get_governance_role("gov_media_creator_venture_board_partner", conn)
            elif any(k in p_low for k in ["clinical", "sepsis", "samd", "mortality", "patient safety"]):
                base = get_governance_role("gov_healthcare_patient_safety_auditor", conn)
            elif any(k in p_low for k in ["pharma", "biotech", "fda trial", "phase iii"]):
                base = get_governance_role("gov_biotech_clinical_scientific_director", conn)
            elif any(k in p_low for k in ["cyber", "breach", "ransomware", "ai safety", "zero-trust"]):
                base = get_governance_role("gov_cybersecurity_ai_safety_board_auditor", conn)
            elif any(k in p_low for k in ["telco", "telecom", "orange", "fiber", "5g", "grid"]):
                base = get_governance_role("gov_telco_energy_infra_regulatory_director", conn)
            elif any(k in p_low for k in ["bank", "liquidity", "ccar", "cet1", "alm"]):
                base = get_governance_role("gov_financial_systemic_risk_chair", conn)
            elif any(k in p_low for k in ["forensic", "restatement", "pcaob", "accounting", "capitaliz", "audit"]):
                base = get_governance_role("gov_external_statutory_forensic_auditor", conn)
            else:
                base = get_governance_role("gov_capital_allocation_value_director", conn)
        assert base is not None

        chosen_fusions: List[GovernanceRole] = []
        if fuse_slugs:
            for fs in fuse_slugs:
                fr = get_governance_role(fs, conn)
                if fr and fr.slug != base.slug and all(x.slug != fr.slug for x in chosen_fusions):
                    chosen_fusions.append(fr)
        else:
            if company_or_industry:
                slate = board_for_company(company_or_industry, db_path_or_conn=conn)
                candidates = slate.board_directors + slate.external_auditors
            else:
                candidates = list_governance_roles(conn)
            priority = [
                "gov_audit_committee_financial_expert_chair",
                "gov_independent_strategic_value_auditor",
                "gov_external_statutory_forensic_auditor",
                "gov_capital_allocation_value_director",
                "gov_compensation_succession_chair",
            ]
            by_slug = {c.slug: c for c in candidates}
            for ps in priority:
                if ps in by_slug and ps != base.slug and len(chosen_fusions) < 3:
                    chosen_fusions.append(by_slug[ps])
            for c in candidates:
                if c.slug != base.slug and all(x.slug != c.slug for x in chosen_fusions) and len(chosen_fusions) < 3:
                    chosen_fusions.append(c)
        return base, chosen_fusions

    def synthesize(
        self,
        problem: str,
        role_slug_or_id: Optional[str] = None,
        company_or_industry: Optional[str] = None,
        fuse_committee_slugs: Optional[Sequence[str]] = None,
        developer_context: str = "",
        slug_override: Optional[str] = None,
        title_override: Optional[str] = None,
        persist: bool = False,
    ) -> SuperhumanGovernancePackage:
        conn = self._open()
        try:
            base, fused_roles = self._resolve_base_and_fusions(
                conn, problem, role_slug_or_id, company_or_industry, fuse_committee_slugs
            )
            slug = slug_override or _slugify(f"superhuman_{base.slug}_{problem[:28]}")
            digest = hashlib.sha1(slug.encode("utf-8")).hexdigest()[:10]
            pkg_id = f"shgov_{digest}"
            title = title_override or f"Superhuman {base.title}"

            all_gov_ids = [base.id] + [r.id for r in fused_roles]
            slug_map = {r.id: r.slug for r in ([base] + fused_roles)}
            ph = ",".join("?" for _ in all_gov_ids)
            edges: List[GovernanceOversightEdge] = []
            for er in conn.execute(
                f"SELECT id, governance_role_id, target_management_role_slug, edge_type, review_artifact, protocol FROM governance_oversight_edges WHERE governance_role_id IN ({ph}) ORDER BY id",
                all_gov_ids,
            ).fetchall():
                edges.append(GovernanceOversightEdge(
                    id=er[0], governance_role_id=er[1], governance_role_slug=slug_map.get(er[1], ""),
                    target_management_role_slug=er[2], edge_type=er[3], review_artifact=er[4], protocol=er[5],
                ))

            creds = _build_credentials(base, problem)
            crucibles = _build_crucibles(base, problem)
            temperament = _build_temperament(base)
            fusions = _build_fusions(base, fused_roles, edges, conn)
            epistemology = _build_epistemology(base, problem)
            prompt = _compile_8_section_superhuman_gov_prompt(
                title=title, slug=slug, base_role=base, problem=problem,
                creds=creds, crucibles=crucibles, temperament=temperament,
                fusions=fusions, epistemology=epistemology, developer_context=developer_context,
            )
            created_ts = datetime.now(timezone.utc).isoformat()
            pkg = SuperhumanGovernancePackage(
                id=pkg_id,
                slug=slug,
                title=title,
                base_governance_role=base,
                target_problem_or_company=problem,
                company_context=company_or_industry,
                fused_committee_slugs=[r.slug for r in fused_roles],
                committee_and_seam_fusions=fusions,
                academic_and_credential_foundation=creds,
                boardroom_and_audit_crucibles=crucibles,
                fiduciary_temperament=temperament,
                unknown_risk_epistemology=epistemology,
                oversight_edges=edges,
                developer_context=developer_context,
                deep_superhuman_governance_prompt=prompt,
                created_at=created_ts,
            )
            if persist:
                self._persist_in_conn(conn, pkg)
            return pkg
        finally:
            self._close(conn)


    def _persist_in_conn(self, conn: sqlite3.Connection, pkg: SuperhumanGovernancePackage) -> None:
        conn.execute(
            """
            INSERT INTO superhuman_governance_profiles (
                id, slug, title, base_governance_role_slug, target_problem_or_company,
                fused_committee_slugs_json, academic_and_credential_foundation_json,
                boardroom_and_audit_crucibles_json, fiduciary_temperament_json,
                unknown_risk_epistemology_json, developer_context,
                deep_superhuman_governance_prompt, package_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                title=excluded.title,
                base_governance_role_slug=excluded.base_governance_role_slug,
                target_problem_or_company=excluded.target_problem_or_company,
                fused_committee_slugs_json=excluded.fused_committee_slugs_json,
                academic_and_credential_foundation_json=excluded.academic_and_credential_foundation_json,
                boardroom_and_audit_crucibles_json=excluded.boardroom_and_audit_crucibles_json,
                fiduciary_temperament_json=excluded.fiduciary_temperament_json,
                unknown_risk_epistemology_json=excluded.unknown_risk_epistemology_json,
                developer_context=excluded.developer_context,
                deep_superhuman_governance_prompt=excluded.deep_superhuman_governance_prompt,
                package_json=excluded.package_json
            """,
            (
                pkg.id,
                pkg.slug,
                pkg.title,
                pkg.base_governance_role.slug,
                pkg.target_problem_or_company,
                json.dumps(pkg.fused_committee_slugs),
                json.dumps(pkg.academic_and_credential_foundation.to_dict()),
                json.dumps(pkg.boardroom_and_audit_crucibles.to_dict()),
                json.dumps(pkg.fiduciary_temperament.to_dict()),
                json.dumps(pkg.unknown_risk_epistemology.to_dict()),
                pkg.developer_context,
                pkg.deep_superhuman_governance_prompt,
                pkg.to_json(),
            ),
        )
        conn.commit()

    def list_profiles(self) -> List[Dict[str, Any]]:
        conn = self._open()
        try:
            rows = conn.execute(
                "SELECT id, slug, title, base_governance_role_slug, target_problem_or_company, LENGTH(deep_superhuman_governance_prompt), created_at FROM superhuman_governance_profiles ORDER BY created_at ASC, slug ASC"
            ).fetchall()
            return [
                {
                    "id": r[0],
                    "slug": r[1],
                    "title": r[2],
                    "base_governance_role_slug": r[3],
                    "target_problem_or_company": r[4],
                    "prompt_character_count": int(r[5] or 0),
                    "created_at": r[6],
                }
                for r in rows
            ]
        finally:
            self._close(conn)

    def get_profile(self, slug_or_id: str) -> Optional[SuperhumanGovernancePackage]:
        conn = self._open()
        try:
            key = slug_or_id.strip()
            row = conn.execute(
                "SELECT package_json FROM superhuman_governance_profiles WHERE slug = ? OR id = ?",
                (key, key),
            ).fetchone()
            if not row:
                return None
            data = json.loads(row[0])
            data.pop("prompt_character_count", None)
            if isinstance(data.get("unknown_risk_epistemology"), dict):
                data["unknown_risk_epistemology"].pop("stages", None)
            return SuperhumanGovernancePackage.model_validate(data)
        finally:
            self._close(conn)


FLAGSHIP_SUPERHUMAN_GOVERNANCE_SPECS: List[Dict[str, Any]] = [
    {
        "slug": "superhuman_gov_capital_allocation_board_director",
        "title": "Superhuman Capital-Allocation, SOTP & Infrastructure ROIC Board Director",
        "base_role": "gov_capital_allocation_value_director",
        "company_or_industry": "telecommunications",
        "fuse_slugs": [
            "gov_audit_committee_financial_expert_chair",
            "gov_telco_energy_infra_regulatory_director",
            "gov_independent_strategic_value_auditor",
            "gov_compensation_succession_chair",
        ],
        "problem": (
            "Audit multi-segment enterprise & telecom/cloud capital allocation: expose Adjusted-EBITDAaL vs. Organic Cash Flow "
            "divergence, OpEx-to-CapEx labor capitalization, 6-year vs. 3.5-year GPU/server depreciation manipulation, decaying "
            "legacy MPLS/copper cross-subsidies, TowerCo/Cyber SOTP traps, and unfocused AI pilot theater."
        ),
        "developer_context": (
            "Enforce McKinsey Economic Profit (`ROIC - WACC`) disaggregation across Domestic Network/FTTH, Enterprise B2B IT/MPLS, "
            "Sovereign Cyber/Cloud, and Passive Infrastructure/TowerCo. Demand clean cash conversion, 3.5-year accelerator useful lives, "
            "works-council-realistic copper switch-off milestones, and hard P&L capture gates on agentic AI swarms."
        ),
    },
    {
        "slug": "superhuman_gov_forensic_strategic_auditor",
        "title": "Superhuman Statutory Forensic & Outside-In Strategic/AI Value Auditor",
        "base_role": "gov_external_statutory_forensic_auditor",
        "company_or_industry": "technology_ai",
        "fuse_slugs": [
            "gov_independent_strategic_value_auditor",
            "gov_audit_committee_financial_expert_chair",
            "gov_cybersecurity_ai_safety_board_auditor",
        ],
        "problem": (
            "Execute integrated PCAOB AS 2401 forensic accounting + McKinsey outside-in commercial & AI ROI assurance: "
            "detect ASC 350-40/ASC 606/ASC 842/ASC 926 capitalization & round-trip revenue shenanigans, customer cohort churn, "
            "off-balance-sheet obligations, and phantom 'AI productivity' claims."
        ),
        "developer_context": (
            "Fuse Big-4 National-Office forensic accounting (cash-to-accrual bridges, Beneish M-Score, passed-adjustments, "
            "lease/factoring debt equivalence) with independent outside-in cohort retention, win/loss telemetry, and AI P&L verification."
        ),
    },
    {
        "slug": "superhuman_gov_media_creator_board_partner",
        "title": "Superhuman Film Studio, IP Slate & Creator-Economy Venture Board Partner",
        "base_role": "gov_media_creator_venture_board_partner",
        "company_or_industry": "creative_media",
        "fuse_slugs": [
            "gov_audit_committee_financial_expert_chair",
            "gov_capital_allocation_value_director",
            "gov_retail_consumer_brand_director",
            "gov_independent_strategic_value_auditor",
        ],
        "problem": (
            "Govern indie film studios, scaled YouTube/social production houses, and creator-led consumer ventures: "
            "enforce Blumhouse/A24 negative-cost caps & pre-sales coverage, expose aggressive ASC 926 multi-year digital video "
            "capitalization, separate organic long-form CTR/AVD decay from low-RPM Shorts vanity views, and stop CPG/merch MOQ cash traps."
        ),
        "developer_context": (
            "Unite Beast-scale Title/Thumbnail CTR & 0-30s hook retention telemetry, A24/Blumhouse downside-capped slate finance, "
            "ASC 926 ultimate-revenue write-down conservatism, key-creator concentration mitigation, merch GMROI discipline, "
            "and high-margin AI dubbing/localization & editing workflows."
        ),
    },
]


def seed_flagship_superhuman_governance_profiles(
    db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None,
    output_dir: Optional[Union[str, Path]] = None,
) -> List[SuperhumanGovernancePackage]:
    """Synthesizes and persists the 3 flagship Superhuman Board & Auditor profiles to SQLite + artifacts."""
    synth = SuperhumanGovernanceSynthesizer(db_path_or_conn)
    repo_root = Path(__file__).resolve().parents[2]
    art_dir = Path(output_dir) if output_dir else (repo_root / "artifacts" / "governance_roles")
    art_dir.mkdir(parents=True, exist_ok=True)

    packages: List[SuperhumanGovernancePackage] = []
    for spec in FLAGSHIP_SUPERHUMAN_GOVERNANCE_SPECS:
        pkg = synth.synthesize(
            problem=spec["problem"],
            role_slug_or_id=spec["base_role"],
            company_or_industry=spec["company_or_industry"],
            fuse_committee_slugs=spec["fuse_slugs"],
            developer_context=spec["developer_context"],
            slug_override=spec["slug"],
            title_override=spec["title"],
            persist=True,
        )
        pkg.save(art_dir / f"{pkg.slug}.md", format="markdown")
        pkg.save(art_dir / f"{pkg.slug}.json", format="json")
        packages.append(pkg)
    return packages


__all__ = [
    "SuperhumanGovernanceSynthesizer",
    "FLAGSHIP_SUPERHUMAN_GOVERNANCE_SPECS",
    "seed_flagship_superhuman_governance_profiles",
]
