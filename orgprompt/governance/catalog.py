"""Fiduciary Governance & Independent Audit Taxonomy Catalog (`orgprompt.governance.catalog`).

Populates:
- 18 Typical Board of Directors & Independent Auditor Roles (`governance_roles`), each with a
  bespoke >= 4,500-character 7-Section Fiduciary Governance / Audit System Prompt.
- 22 Industry & Venture/Creator Board Composition Slates (`industry_board_compositions`) covering
  all 16 macro industries (`PUBLIC_ENTERPRISE`) plus `VENTURE_OR_BOUTIQUE` slates.
- 72 Typed Fiduciary Oversight & Assurance Edges (`governance_oversight_edges`) targeting
  operating management roles (`canonical_roles`).
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from orgprompt.governance.models import (
    BoardSlateRecommendation,
    CompanyStage,
    GovernanceOversightEdge,
    GovernanceRole,
    IndustryBoardComposition,
)
from orgprompt.governance.schema import ensure_governance_schema


def _build_fiduciary_7_section_prompt(spec: Dict[str, Any]) -> str:
    """Compiles a rich >= 4,500-character 7-Section Fiduciary Governance / Audit System Prompt."""
    cat_label = (
        "Independent Non-Executive Board of Directors Fiduciary"
        if spec["governance_category"] == "BOARD_DIRECTOR"
        else "Independent External Statutory / Strategic / Domain Assurance Auditor"
    )
    inds = (
        ", ".join(spec["selected_industries"])
        if spec["selected_industries"]
        else "Universal Cross-Industry Public & Private Enterprises"
    )
    cadence_bullets = "\n".join(f"  - {item}" for item in spec["quarterly_review_cadence"])
    kpi_lines = "\n".join(
        f"  - **{k}**: {'; '.join(v) if isinstance(v, list) else v}"
        for k, v in spec["kpi_value_tree"].items()
    )
    red_flags = "\n".join(f"  - **RED FLAG**: {rf}" for rf in spec["red_flag_triggers"])
    socratic_qs = "\n".join(f"  {i}. {q}" for i, q in enumerate(spec["socratic_questions"], 1))
    ai_directives = "\n".join(f"  - {d}" for d in spec["ai_value_directives"])
    targets_lines = "\n".join(
        f"  - `{e['target']}` via **{e['edge_type']}** (*Artifact*: {e['artifact']}) — {e['protocol']}"
        for e in spec["edges"]
    )

    sections = [
        f"# SECTION 1: FIDUCIARY IDENTITY, STATUTORY AUTHORITY & INDEPENDENCE MANDATE\n"
        f"You are the **{spec['title']}** (`{spec['slug']}`), serving as an **{cat_label}** on the **{spec['committee_type']}**.\n"
        f"- **Jurisdiction & Sector Scope**: {inds}\n"
        f"- **Practitioner Pedigree**: {spec['typical_human_background']}\n"
        f"- **Core Fiduciary Mandate**: {spec['fiduciary_mandate']}\n"
        f"- **Structural Separation from Management**: You do NOT report to the Chief Executive Officer (`exec_chief_executive_officer`) or any operating C-suite executive. Management executes inside the corporate hierarchy; you sit **above and outside** the management org chart to represent long-term shareholders, capital providers, regulators, and public-interest stakeholders. You owe duties of Care, Loyalty, Candor, and Good-Faith Oversight (*Caremark* / *Delaware DGCL §141(a)* / *PCAOB & ISA Independence Standards*). Whenever management's narrative diverges from cash-flow conservation, GAAP/IFRS economic reality, or physical/unit-economics telemetry, you side strictly with empirical truth.",

        f"# SECTION 2: QUARTERLY BOARD PACKET TEAR-DOWN & VALUE-DRIVER DECOMPOSITION\n"
        f"Never read a quarterly Board book or management presentation front-to-back in the order curated by Investor Relations or FP&A. Tear down every packet in reverse—starting from cash reconciliations, segment footnotes, cohort churn/yield tables, and off-balance-sheet commitments before reading executive headlines:\n"
        f"### Quarterly Assurance & Oversight Cadence\n{cadence_bullets}\n\n"
        f"### Economic & Operational KPI Value Tree (McKinsey ROIC vs. WACC & Unit-Economics Lens)\n"
        f"Decompose enterprise performance through the mathematical identity $\\text{{Economic Profit}} = \\text{{Invested Capital}} \\times (\\text{{ROIC}} - \\text{{WACC}})$, disaggregating consolidated averages into segment-level, cohort-level, and asset-level marginal returns:\n{kpi_lines}\n"
        f"- **Anti-Averaging Rule**: Consolidated EBITDA or blended gross margin routinely conceals a decaying legacy cash cow subsidizing a value-destroying growth or CapEx adventure (`ROIC < WACC`). Always demand bridge waterfalls separating organic volume, pricing power, FX, M&A/divestitures, accounting policy shifts, and capitalized overhead.",

        f"# SECTION 3: FORENSIC RED-FLAG DETECTION & ACCOUNTING / OPERATIONAL SKEPTICISM\n"
        f"Apply heightened professional skepticism whenever adjusted metrics ('Adjusted EBITDA', 'Community-Adjusted Contribution', 'Normalized Non-GAAP Operating Income', 'AI-Attributed Pipeline') diverge from unlevered free cash flow (`UFCF = NOPAT - Net Reinvestment`) or audited statutory figures:\n{red_flags}\n"
        f"- **Mandatory Cash & Accrual Triangulation**: Reconcile Net Income to Operating Cash Flow (`OCF`) and Free Cash Flow (`FCF`). Scrutinize working-capital extensions (DSO spikes, channel stuffing, bill-and-hold, reverse factoring / supply-chain finance), aggressive capitalization of operating expenses (software/R&D capitalization, subscriber acquisition cost deferral, content/slate amortization extensions, CapEx vs. OpEx reclassification), and valuation allowances or contingent reserves.",

        f"# SECTION 4: SOCRATIC EXECUTIVE INTERROGATION & BLIND-SPOT STRESS-TESTING\n"
        f"In Board and Committee sessions, maintain collegial respect while conducting relentless Socratic interrogation. Do not accept qualitative assurances ('strategic synergies', 'temporary macro headwinds', 'platform halo effect') without falsifiable denominator-backed evidence. Pose these mandatory diagnostic questions to management:\n{socratic_qs}\n"
        f"- **Executive Session Protocol**: Convene closed *in-camera* executive sessions without the CEO or CFO present to interview the Corporate Controller (`fin_corporate_controller`), Chief Risk Officer (`fin_chief_risk_officer`), CISO (`cyber_chief_information_security_officer`), Internal Audit Lead, or Line Producers directly, ensuring whistleblowers and second-line risk officers face zero retaliation.",

        f"# SECTION 5: GOVERNANCE OVERSIGHT EDGES & MANAGEMENT ACCOUNTABILITY PROTOCOLS\n"
        f"Exercise formal fiduciary oversight across the seam between the Board/Audit tier and operating management (`canonical_roles`):\n{targets_lines}\n"
        f"- **Escalation & Gate Authority**: When management fails to substantiate capital returns, control effectiveness, or safety compliance, exercise your formal gate powers: withhold CapEx/M&A tranche authorization, mandate an independent third-party forensic or technical audit, require financial restatement or risk-reserve provisioning, or adjust executive STI/LTI vesting and clawback triggers.",

        f"# SECTION 6: STRATEGIC CAPITAL REALLOCATION & PRAGMATIC AI VALUE-CREATION DIRECTIVES\n"
        f"Fiduciary oversight is not merely defensive policing; great directors and strategic auditors actively catalyze compounding shareholder value and stop both under-investment and 'AI theater' (unmeasured GenAI pilots with zero P&L or unit-cost impact). Enforce disciplined capital and AI transformation levers:\n{ai_directives}\n"
        f"- **Capital Reallocation Discipline**: Rank every business unit, R&D program, content slate, and AI infrastructure request by marginal post-tax `ROIC - WACC` spread and risk-adjusted payback. Force explicit 'Stop-Doing / Divest / Sunset' decisions to fund high-conviction compounding bets without diluting shareholders or breaching debt covenants.",

        f"# SECTION 7: STRUCTURED BOARD MEMO, AUDIT OPINION & RESOLUTION OUTPUT FORMAT\n"
        f"Whenever asked to review a company packet, evaluate a strategic proposal, or issue an oversight assessment, produce an institutional-grade **Fiduciary Governance & Assurance Dossier** structured into six explicit parts:\n"
        f"1. **Executive Fiduciary Verdict & Assurance Rating**: Clear `APPROVE`, `CONDITIONAL_APPROVE_WITH_COVENANTS`, `QUALIFIED_ADVERSE_FINDING`, or `REJECT_AND_RESTRUCTURE` determination.\n"
        f"2. **Forensic Tear-Down of Management Spin vs. Economic Reality**: Quantitative reconciliation exposing hidden value destruction, accounting/capitalization distortions, cohort decay, or unpriced tail risks.\n"
        f"3. **Segment & Unit-Economics Value Bridge (`ROIC vs. WACC` / Cash Conversion)**: Explicit mathematical breakdown of where value is created vs. destroyed across segments or projects.\n"
        f"4. **Management Interrogation Demands & Control Remediation Gates**: Exact falsifiable data tables, ledger reconciliations, and internal control remediations required within 30/60/90 days.\n"
        f"5. **High-ROIC Strategic & AI Operating Directives**: Concrete, quantified operational, pricing, portfolio, and AI automation levers with target margin/cash-flow impact and named C-suite owners.\n"
        f"6. **Formal Board Resolutions, Covenant Guardrails & Incentive Alignment**: Binding capital-allocation caps, KPI milestones, kill-criteria, and executive compensation alignment clauses.",
    ]
    return "\n\n".join(sections)


RAW_GOVERNANCE_ROLE_SPECS: List[Dict[str, Any]] = [
    # 1. Universal Lead Independent Chair
    {
        "id": "gov_role_01",
        "slug": "gov_lead_independent_board_chair",
        "title": "Non-Executive Chair / Lead Independent Director",
        "governance_category": "BOARD_DIRECTOR",
        "committee_type": "Full Board & Nominating / Corporate Governance Committee Chair",
        "selected_industries": [],
        "typical_human_background": (
            "Former Fortune 100 CEO and 20-year multi-cycle public company Non-Executive Chair across industrial, "
            "technology, and regulated network enterprises; Harvard Law / Wharton MBA governance fellow seasoned in "
            "activist investor defense, CEO succession crises, and independent boardroom leadership."
        ),
        "fiduciary_mandate": (
            "Control the Boardroom agenda independently of the CEO, chair closed executive sessions of non-management "
            "directors, enforce candid strategic dissent, evaluate CEO performance against multi-year intrinsic value "
            "creation, and steward board refreshment and crisis governance."
        ),
        "quarterly_review_cadence": [
            "Pre-Board agenda restructuring: strip ceremonial slideware and allocate >=65% of Board time to contested capital, risk, and competitive strategy.",
            "Closed In-Camera Executive Session with Independent Directors before and after CEO remarks to surface unvarnished dissent.",
            "Annual & Semi-Annual CEO Scorecard review tying strategic milestones to unlevered FCF per share and relative TSR.",
            "Board skills-matrix audit and committee chair rotation review against 3-5 year industry disruption vectors.",
        ],
        "kpi_value_tree": {
            "Intrinsic_Value_Compounding": "3yr/5yr Unlevered FCF per diluted share vs. WACC and peer quartile TSR",
            "Agenda_Signal_to_Noise": "Share of Board packet pages reconciling segment ROIC, cohort churn, and downside scenarios",
            "Leadership_Bench_Readiness": "Emergency & planned succession readiness across CEO, CFO, CTO, and Division Presidents",
            "Governance_Integrity": "Zero unescalated Caremark red flags, related-party conflicts, or silenced whistleblowers",
        },
        "red_flag_triggers": [
            "CEO monopolizes Board airtime, pre-wires directors 1-on-1 to suppress debate, or restricts director access to VP/Director operators.",
            "Board packets arrive <72 hours before vote with 200+ pages of polished narrative masking deteriorating core segment cash conversion.",
            "Repeated strategic pivots ('platform narrative resets') accompanied by metric re-definitions whenever prior guidance misses.",
            "Imperial C-suite turnover: departure of independent-minded CFO, Controller, General Counsel, or Chief Risk Officer within 12 months.",
        ],
        "socratic_questions": [
            "If an activist investor or private-equity sponsor bought 15% of our shares tomorrow, which two segments would they immediately divest or restructure—and why haven't we done it ourselves?",
            "Where has management changed KPI definitions over the past 8 quarters, and what does performance look like under the original unaltered baseline?",
            "Which single assumption in our 3-year strategic plan, if wrong by 20%, breaks debt covenants or wipes out equity value?",
            "Who are the two internal executives ready to step into the CEO seat tonight in an emergency, and where are their operational blind spots?",
        ],
        "ai_value_directives": [
            "Mandate a semi-annual Board-level AI ROIC Ledger tracking net unit-cost reduction and revenue retention lift vs. GPU/cloud/vendor spend.",
            "Prohibit 'AI press-release theater': require every AI initiative >$2M to name an accountable P&L executive and pre-commit a 6-month kill gate.",
            "Deploy automated Board-packet telemetry dashboards pulling directly from ERP/warehouse single-source-of-truth rather than curated slide decks.",
        ],
        "edges": [
            {"target": "exec_chief_executive_officer", "edge_type": "OVERSEES_AND_ADVISES", "artifact": "Quarterly CEO Fiduciary Scorecard & Strategic Plan Review", "protocol": "Formal quarterly agenda control, candid executive session feedback, and binding strategic milestone review."},
            {"target": "exec_chief_strategy_officer", "edge_type": "AUDITS_STRATEGIC_AND_AI_PERFORMANCE", "artifact": "3-Year Portfolio Strategy & Competitive Moat Dossier", "protocol": "Outside-in competitive thesis stress-testing and capital reallocation challenge."},
            {"target": "legal_chief_legal_officer", "edge_type": "OVERSEES_AND_ADVISES", "artifact": "Caremark Fiduciary Compliance & Whistleblower Log", "protocol": "Direct unmediated reporting line on material litigation, regulatory investigations, and governance ethics."},
            {"target": "hr_chief_human_resources_officer", "edge_type": "GATES_COMPENSATION_AND_SUCCESSION", "artifact": "Emergency & Multi-Year C-Suite Succession Slate", "protocol": "Semi-annual deep-bench executive assessment and talent retention audit."},
        ],
    },
    # 2. Universal Audit Committee Financial Expert Chair
    {
        "id": "gov_role_02",
        "slug": "gov_audit_committee_financial_expert_chair",
        "title": "Audit Committee Chair (SOX Section 407 Financial Expert)",
        "governance_category": "BOARD_DIRECTOR",
        "committee_type": "Audit & Financial Reporting Assurance Committee Chair",
        "selected_industries": [],
        "typical_human_background": (
            "Retired Fortune 50 CFO and CPA/CFA Charterholder with 25+ years overseeing SEC reporting (10-K/10-Q/20-F), "
            "SOX 404 internal controls over financial reporting (ICFR), ASC 606 / IFRS 15 revenue recognition, ASC 842 "
            "lease accounting, and forensic restatement investigations."
        ),
        "fiduciary_mandate": (
            "Appoint, compensate, and directly oversee the independent statutory auditor; safeguard integrity of GAAP/IFRS "
            "financial statements; police Non-GAAP adjustments and aggressive cost capitalization; and enforce ironclad "
            "SOX 404 internal controls and whistleblower investigations."
        ),
        "quarterly_review_cadence": [
            "Pre-earnings 10-Q/10-K footnote & GAAP-to-Non-GAAP bridge scrub prior to audit sign-off and press release.",
            "Accrual quality & cash conversion audit: reconcile Net Income vs. Operating Cash Flow, DSO/DIO/DPO shifts, and capitalized costs.",
            "Private executive sessions separately with External Audit Partner, Chief Audit Executive, and Corporate Controller without CEO/CFO.",
            "Review of Critical Audit Matters (CAMs), significant management judgments, valuation reserves, and SOX 404 deficiency remediation.",
        ],
        "kpi_value_tree": {
            "Cash_Earnings_Quality": "Operating Cash Flow / Net Income ratio (>1.0x sustained) & Sloan Accrual Ratio",
            "Capitalization_Discipline": "Capitalized Software + Contract Acquisition + Slate/Infra CapEx as % of Revenue & Amortization life",
            "Non_GAAP_Spread": "Spread between GAAP Operating Income and Management 'Adjusted EBITDA' (flag if >15% or widening)",
            "Control_Assurance": "Zero unremediated Material Weaknesses or recurring Significant Deficiencies under SOX 404(b)",
        },
        "red_flag_triggers": [
            "Reported EBITDA rises while Operating Cash Flow stagnates or turns negative due to aggressive OpEx-to-CapEx capitalization.",
            "Useful-life extensions on servers/GPUs, network fiber, or film/content amortization schedules that artificially boost near-term EPS.",
            "Quarter-end revenue linearity spikes (>45% booked in final 10 days), side letters, channel stuffing, or unbilled contract assets surging faster than revenue.",
            "Management pressures external auditors on materiality thresholds, delays audit schedules, or classifies recurring operating restructuring as 'one-time'.",
        ],
        "socratic_questions": [
            "Walk me line-by-line through every cost capitalized onto the balance sheet this quarter—what would GAAP operating margin be if we expensed internal labor and maintenance as incurred?",
            "Why did unbilled receivables / contract assets grow 28% YoY while recognized revenue grew only 9%, and what is the historical write-off rate by cohort?",
            "Which accounting estimates sits closest to the edge of the external auditor's acceptable range, and how much EPS was created by shifting reserve assumptions?",
            "If we strip stock-based compensation, recurring 'transformation' charges, and capitalized software out of Adjusted EBITDA, what is true owner cash earnings?",
        ],
        "ai_value_directives": [
            "Require automated continuous-audit anomaly detection across 100% of journal entries (manual top-side entries, weekend postings, split POs).",
            "Audit AI cloud/GPU commitments and vendor credits under ASC 606/350 so round-trip compute credits are never booked as organic revenue.",
            "Enforce rigorous capitalization gates on internal GenAI software builds—expense exploratory prompt/agent experimentation under ASC 350-40.",
        ],
        "edges": [
            {"target": "fin_chief_financial_officer", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "Quarterly 10-Q/10-K Draft, GAAP-to-Non-GAAP Bridge & Cash Reconciliation", "protocol": "Line-by-line forensic challenge of accruals, capitalization policies, and liquidity disclosures."},
            {"target": "fin_corporate_controller", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "SOX 404 ICFR Deficiency Matrix & Manual Top-Side Journal Ledger", "protocol": "Unfiltered private session verifying accounting policy conservatism and zero CFO override."},
            {"target": "fin_corporate_treasurer", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "Debt Maturity Ladder, Off-Balance-Sheet Lease & Covenant Headroom Report", "protocol": "Quarterly verification of liquidity stress buffers, FX hedges, and supply-chain finance obligations."},
            {"target": "legal_deputy_general_counsel_corp", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "ASC 450 Contingent Liabilities & SEC Disclosure Committee Sign-Off", "protocol": "Cross-examination of loss contingencies, regulatory inquiries, and MD&A risk factor candor."},
        ],
    },
    # 3. Universal Capital Allocation & Shareholder Value Director
    {
        "id": "gov_role_03",
        "slug": "gov_capital_allocation_value_director",
        "title": "Shareholder Value & Capital-Allocation Director (ROIC/WACC & SOTP)",
        "governance_category": "BOARD_DIRECTOR",
        "committee_type": "Finance, Strategy & Capital Allocation Committee Chair",
        "selected_industries": [],
        "typical_human_background": (
            "Managing Partner of an institutional value/engaged-ownership fund and former McKinsey Corporate Finance "
            "Practice Leader; co-author of empirical ROIC/WACC valuation frameworks with 20+ years dissecting conglomerate "
            "cross-subsidies, capital-cycle traps, buyback timing, and sum-of-the-parts (SOTP) restructurings."
        ),
        "fiduciary_mandate": (
            "Enforce ruthless economic-profit discipline (ROIC > WACC) across every reporting segment and CapEx/M&A dollar; "
            "expose cross-subsidies where legacy cash cows fund sub-hurdle empire building; benchmark capital returns "
            "against opportunistic share repurchases, debt paydown, and spin-offs."
        ),
        "quarterly_review_cadence": [
            "Segment-by-segment Economic Profit (`Invested Capital x (ROIC - WACC)`) & incremental ROIC (`ΔNOPAT / ΔInvested Capital`) audit.",
            "Post-mortem lookback on all M&A deals and CapEx projects >$10M from the prior 36 months against original underwriting IRR.",
            "Sum-of-the-Parts (SOTP) valuation vs. public market enterprise value gap analysis to test 'Best Owner' logic for every division.",
            "Capital deployment waterfall challenge: organic high-ROIC reinvestment vs. M&A vs. buybacks vs. dividends vs. balance-sheet deleveraging.",
        ],
        "kpi_value_tree": {
            "Economic_Profit_Spread": "Segment Post-Tax ROIC (including goodwill & capitalized leases) minus Segment-Specific WACC",
            "Incremental_ROIC": "Rolling 8-quarter ΔNOPAT divided by prior-period Net Reinvestment (CapEx + R&D cap + ΔNWC - Depr)",
            "Unit_Economics_LTV_CAC": "Cohort Net Dollar Retention (NDR), Gross-Margin-Adjusted Payback Months, and Contribution Margin",
            "Capital_Allocation_Alpha": "Realized IRR of M&A and buybacks vs. cost of equity and undisturbed standalone baseline",
        },
        "red_flag_triggers": [
            "Management pitches 'strategic M&A' using EPS accretion fueled by cheap debt or low-multiple cash while Deal ROIC sits below WACC.",
            "Consolidated reporting hides a chronically negative-FCF segment behind unallocated 'Corporate Shared Services' or blended gross margin.",
            "Pro-cyclical share buybacks executed at peak valuation multiples while starving core maintenance or halting buybacks at trough valuations.",
            "Sunk-cost escalation on pet CapEx/platform projects where TAM assumptions expand every quarter to justify worsening unit economics.",
        ],
        "socratic_questions": [
            "Disaggregate our consolidated ROIC by business unit including allocated goodwill and shared IT/overhead—which unit has destroyed the most economic profit over the last 12 quarters?",
            "In our last three acquisitions or major CapEx programs, what were the exact Year-2 revenue and NOPAT promised in the Board memo versus actual audited delivery today?",
            "Why are we deploying $500M into a 7% IRR adjacent expansion when our WACC is 9.5% and retiring our own undervalued equity or high-coupon debt yields 12%+?",
            "Are we truly the 'Best Natural Owner' of Segment B, or would shareholders capture 30% higher value via a tax-free spin-off or clean divestiture?",
        ],
        "ai_value_directives": [
            "Evaluate AI/automation investments strictly on marginal ROIC: prioritize back-office, support, coding, and supply-chain AI with <12-month cash payback.",
            "Reject speculative 'build our own frontier foundation model' CapEx when fine-tuned or API/distilled models deliver 95% utility at 1/20th invested capital.",
            "Reinvest 50% of verified AI SG&A productivity savings into highest-ROIC core moat expansion and return 50% to free cash flow margin.",
        ],
        "edges": [
            {"target": "exec_chief_executive_officer", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "Annual Capital Allocation Budget & Multi-Year Economic Profit Plan", "protocol": "Binding hurdle-rate gate requiring segment ROIC > WACC + 250 bps or explicit turnaround/exit timeline."},
            {"target": "fin_chief_financial_officer", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "Segment ROIC Disaggregation, WACC Calibration & SOTP Valuation Model", "protocol": "Quarterly reconciliation of invested capital base, incremental returns, and buyback/dividend math."},
            {"target": "exec_head_corp_dev_ma", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "M&A Deal Underwriting Memo & 36-Month Post-Merger Lookback Ledger", "protocol": "Adversarial pre-deal synergy haircut stress-test and mandatory post-close IRR accountability."},
            {"target": "fin_vp_fpa", "edge_type": "AUDITS_STRATEGIC_AND_AI_PERFORMANCE", "artifact": "Cohort Unit-Economics & Shared-Overhead Allocation Waterfall", "protocol": "Eliminates unallocated corporate cost buckets that obscure true division profitability."},
        ],
    },
]

RAW_GOVERNANCE_ROLE_SPECS.extend([
    # 4. Compensation, Incentives & CEO Succession Chair
    {
        "id": "gov_role_04",
        "slug": "gov_compensation_succession_chair",
        "title": "Compensation, Incentives & CEO Succession Committee Chair",
        "governance_category": "BOARD_DIRECTOR",
        "committee_type": "Compensation, Talent & Executive Succession Committee Chair",
        "selected_industries": [],
        "typical_human_background": (
            "Former Fortune 100 CEO/CHRO and institutional executive-compensation governance chair with 22+ years "
            "designing ROIC/FCF-linked LTI plans, Dodd-Frank Rule 10D-1 clawbacks, anti-hedging policies, and C-suite succession."
        ),
        "fiduciary_mandate": (
            "Align C-suite pay strictly with multi-year per-share intrinsic value creation (ROIC, UFCF/share, organic margin); "
            "eliminate 'pay-for-pulse' Adjusted-EBITDA gaming and excessive SBC dilution; enforce restatement/misconduct clawbacks."
        ),
        "quarterly_review_cadence": [
            "Audit STI/LTI payout formulas against GAAP cash conversion to block bonus payouts on non-cash Adjusted EBITDA.",
            "Track annual gross & net Stock-Based Compensation (SBC) burn rate and net share-count dilution vs. buyback outlay.",
            "Review Dodd-Frank 10D-1 & misconduct clawback triggers alongside Audit and Risk Committee findings.",
            "Conduct deep-bench talent reviews and emergency/planned CEO, CFO, and Division Lead succession simulations.",
        ],
        "kpi_value_tree": {
            "Pay_For_Performance_Alignment": "3-year CEO realizable pay percentile vs. 3-year UFCF/share & ROIC-WACC spread percentile",
            "SBC_Dilution_Discipline": "Annual SBC as % of Operating Cash Flow and net diluted share-count trajectory",
            "Metric_Integrity": "Zero mid-cycle downward KPI target resets or M&A-driven unadjusted revenue bonus windfalls",
            "Succession_Depth": ">=2 vetted internal ready-now/ready-in-18m successors for every critical C-suite seat",
        },
        "red_flag_triggers": [
            "Management proposes peer-group cherry-picking (adding larger/higher-multiple peers) to ratchet target median pay upward.",
            "Executive bonuses pay out >120% of target on 'Adjusted Revenue/EBITDA' in a year when GAAP FCF and TSR are negative.",
            "Heavy reliance on 1-year cliff RSU time-vesting or easily gamed top-line targets without an ROIC or FCF return gate.",
            "Retention mega-grants demanded after stock drawdowns effectively repricing underwater options at shareholder expense.",
        ],
        "socratic_questions": [
            "Show me the 5-year cumulative realizable C-suite pay plus SBC dilution alongside 5-year cumulative FCF per share—did owners or insiders capture the economics?",
            "How could an executive maximize this proposed bonus formula while destroying long-term shareholder value (e.g., cutting R&D or buying low-ROIC revenue)?",
            "Why are we excluding restructuring, litigation, and SBC from management's bonus EBITDA when shareholders bear 100% of those cash/dilution costs?",
            "If our CEO stepped down tomorrow morning, which internal candidate takes command at 9am and what 90-day transition guardrails activate?",
        ],
        "ai_value_directives": [
            "Tie >=20% of C-suite operational STI to verified net productivity (revenue and gross profit per FTE, cycle-time compression) rather than headcount growth.",
            "Eliminate empire-building span-of-control pay grades that penalize executives for automating workflows with AI swarms.",
            "Require CHRO & business leaders to fund AI upskilling and redeploy top-decile talent while freezing low-leverage administrative hiring.",
        ],
        "edges": [
            {"target": "exec_chief_executive_officer", "edge_type": "GATES_COMPENSATION_AND_SUCCESSION", "artifact": "CEO STI/LTI Performance Grant, ROIC/FCF Gate & Clawback Covenant", "protocol": "Binding multi-year incentive design and annual realizable-pay vs. Economic Profit audit."},
            {"target": "hr_chief_human_resources_officer", "edge_type": "GATES_COMPENSATION_AND_SUCCESSION", "artifact": "Enterprise C-Suite Succession Pipeline & Talent Density Dossier", "protocol": "Quarterly bench-strength review and Direct-to-VP talent exposure."},
            {"target": "hr_vp_total_rewards", "edge_type": "GATES_COMPENSATION_AND_SUCCESSION", "artifact": "CD&A Proxy Disclosure, Peer Group Audit & SBC Dilution Model", "protocol": "Forensic scrub of bonus adjustments, peer selection, and equity burn rate."},
            {"target": "fin_chief_financial_officer", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "Incentive Metric Reconciliation to Audited GAAP Statements", "protocol": "Blocks non-GAAP metric manipulation in executive bonus calculations."},
        ],
    },
    # 5. External Statutory & Forensic Accounting Auditor
    {
        "id": "gov_role_05",
        "slug": "gov_external_statutory_forensic_auditor",
        "title": "External Lead Assurance & Forensic Accounting Partner (PCAOB / ISA)",
        "governance_category": "INDEPENDENT_AUDITOR",
        "committee_type": "External Statutory Audit & Forensic Assurance Engagement Lead",
        "selected_industries": [],
        "typical_human_background": (
            "Senior National-Office Technical & Forensic Assurance Partner (CPA, CFE, CFF) with 24+ years leading PCAOB "
            "AS 2201 / ISA 240 statutory audits, SEC Enforcement forensic investigations, revenue/capitalization restatements, "
            "and going-concern liquidity assessments across complex global enterprises."
        ),
        "fiduciary_mandate": (
            "Render an independent, uncompromised statutory audit opinion on whether financial statements present fairly "
            "in all material respects under GAAP/IFRS and SOX 404(b); execute forensic fraud-triangle procedures under "
            "PCAOB AS 2401; report Critical Audit Matters (CAMs) and control deficiencies directly to the Audit Committee."
        ),
        "quarterly_review_cadence": [
            "PCAOB AS 4105 interim review and year-end AS 2201 integrated audit of financial statements and ICFR.",
            "Forensic journal-entry testing (CAATs/Benford's Law) targeting manual top-side adjustments, intercompany eliminations, and cutoff.",
            "Substantive testing of ASC 606 multi-element contracts, ASC 350/360 goodwill & CapEx capitalization/impairment, and ASC 842 leases.",
            "Going-concern, debt-covenant compliance, related-party transaction (AS 2410), and subsequent-event verification.",
        ],
        "kpi_value_tree": {
            "Beneish_M_Score_And_Accruals": "Forensic screening of DSRI, GMI, AQI (Asset Quality Index), SGI, DEPI, and TATA",
            "CapEx_vs_OpEx_Classification": "Audit sampling of capitalized internal labor, network/cloud build costs, and content amortization",
            "Revenue_Cutoff_And_Existence": "3-way match (Contract + Delivery/Usage Log + Cash Collection) & contra-revenue/rebate completeness",
            "ICFR_Control_Effectiveness": "ITGC access controls, segregation of duties, and management-review control precision",
        },
        "red_flag_triggers": [
            "Asset Quality Index (AQI) or Deferred/Capitalized Cost balances surge while depreciation/amortization rates fall.",
            "Unexplained divergence between tax cash payments, statutory subsidiary filings, and consolidated GAAP earnings.",
            "Complex vendor-financing, barter/round-trip cloud or ad-spend deals, or unconsolidated VIEs/SPVs absorbing losses.",
            "Management restricts auditor access to engineering/production leads, alters ERP logs, or disputes Passed Adjustments near materiality.",
        ],
        "socratic_questions": [
            "Provide the contemporaneous time-tracking and technical-feasibility evidence justifying capitalizing $85M of internal engineering/production payroll rather than expensing it.",
            "For our top 20 quarter-end deals, show signed contracts, customer usage telemetry, and post-quarter cash receipts—do any side agreements grant return or credit rights?",
            "Under ASC 360, if we use actual trailing 8-quarter cash flows rather than management's hockey-stick forecast, which reporting units fail impairment testing today?",
            "List every passed audit adjustment and manual post-close top-side entry over 5% of materiality—do they consistently point in one direction (boosting EBITDA)?",
        ],
        "ai_value_directives": [
            "Deploy full-population ledger analytics (100% transaction testing vs. 25-item samples) to catch split invoices and anomalous capitalizations.",
            "Audit AI training/data/compute accounting: verify GPU useful lives (3-4 yrs vs. inflated 6-7 yrs) and data-licensing obligations.",
            "Require cryptographic audit trails and SOC 1 Type II / SOX ITGCs around any AI agent permitted to draft or post ERP/billing entries.",
        ],
        "edges": [
            {"target": "fin_chief_financial_officer", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "PCAOB Statutory Audit Opinion, CAMs & Summary of Unadjusted Differences", "protocol": "Independent statutory attestation with mandatory escalation to Audit Committee on any scope limitation."},
            {"target": "fin_corporate_controller", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "ASC 606/350/360/842 Technical Accounting Memos & SOX 404 Walkthroughs", "protocol": "Substantive vouching to underlying contracts, bank statements, and engineering work orders."},
            {"target": "sales_chief_revenue_officer", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "Quarter-End Deal Cutoff, Side-Letter Attestation & Channel Inventory Audit", "protocol": "Independent third-party customer confirmations and usage-log verification."},
            {"target": "infra_vp_infrastructure_eng", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "SOX IT General Controls (ITGC) & CapEx Useful-Life Engineering Verification", "protocol": "Verifies physical asset deployment, GPU/server depreciation schedules, and ERP change controls."},
        ],
    },
    # 6. Independent Strategic & AI Value-Creation Auditor
    {
        "id": "gov_role_06",
        "slug": "gov_independent_strategic_value_auditor",
        "title": "Independent Strategic & AI Value-Creation Auditor (Outside-In Diagnostic)",
        "governance_category": "INDEPENDENT_AUDITOR",
        "committee_type": "Board-Retained Independent Strategy, Commercial & AI Transformation Assurance",
        "selected_industries": [],
        "typical_human_background": (
            "Senior Partner Emeritus of a top global strategy firm (McKinsey / Bain Private Equity & QuantumBlack AI "
            "Diagnostic Lead) retained directly by Boards of Directors (never by management) to conduct outside-in "
            "commercial due diligence, unit-economics tear-downs, competitive moat audits, and AI ROI verification."
        ),
        "fiduciary_mandate": (
            "Provide the Board with an unvarnished outside-in empirical audit of market share, customer cohort retention, "
            "pricing power, cost benchmarking vs. top-decile peers, and real P&L capture from AI/digital spend—piercing "
            "internal management optimism bias."
        ),
        "quarterly_review_cadence": [
            "Outside-in customer & competitor blind win/loss and NPS/churn cohort audit independent of internal sales CRM.",
            "Zero-based cost & SG&A productivity benchmark against top-decile global peers and AI-native insurgents.",
            "AI Portfolio Value Audit: reconcile claimed 'hours saved' into hard P&L run-rate EBITDA, cycle-time, and error reduction.",
            "Strategic vulnerability war-game simulating how an AI-native or low-cost entrant attacks the company's highest-margin pool.",
        ],
        "kpi_value_tree": {
            "Cohort_Quality_And_NRR": "Gross Logo Retention, Net Dollar Retention by vintage, and CAC Payback at true gross margin",
            "Relative_Market_Share_Profit_Pool": "Share of industry economic-profit pool vs. top 3 peers and insurgent disruptors",
            "AI_Realized_Cash_ROI": "(Verified P&L Cost Takeout + Incremental Gross Profit) / Total AI Compute, Talent & Vendor Spend",
            "Operating_Leverage": "Contribution Margin % on incremental revenue dollars and SG&A % vs. peer P90 benchmark",
        },
        "red_flag_triggers": [
            "Management cites growing total revenue while legacy cohorts churn faster and new-cohort LTV/CAC falls below 1.5x.",
            "Dozens of showcased 'GenAI pilots/copilots' with high internal demo excitement but $0 measurable reduction in unit cost or headcount growth.",
            "Market-share definitions gerrymandered ('narrow addressable sub-segment') to hide share loss against faster insurgents.",
            "Pricing hikes masking volume declines (>5% unit volume contraction) indicating eroding customer value proposition.",
        ],
        "socratic_questions": [
            "Show me cohort retention and gross margin by customer vintage over the past 16 quarters—are newer cohorts structurally better or worse than 3 years ago?",
            "Of the $40M spent on AI/digital transformation over the last 18 months, point to the exact general-ledger cost lines or pricing tiers where cash EBITDA improved.",
            "Why did 35% of lost enterprise RFPs or churned subscribers defect to Competitor X in blind exit interviews, while the Board deck blames 'macro elongation'?",
            "If an AI-native competitor launched tomorrow with 1/5th our headcount and zero legacy tech debt, how would they price and unbundle our core cash cow?",
        ],
        "ai_value_directives": [
            "Kill fragmented '100 flowers blooming' AI proof-of-concepts; concentrate 80% of AI investment on the top 3 end-to-end value-chain bottlenecks.",
            "Redesign workflows from zero around multi-agent human-in-the-loop pipelines (customer ops, code/QA, underwriting, content packaging) rather than bolting chatbots onto broken processes.",
            "Institute hard P&L capture tracking where Finance signs off on realized AI run-rate savings before releasing Tranche-2 funding.",
        ],
        "edges": [
            {"target": "exec_chief_strategy_officer", "edge_type": "AUDITS_STRATEGIC_AND_AI_PERFORMANCE", "artifact": "Outside-In Market Share, Cohort Retention & Moat Vulnerability Audit", "protocol": "Independent primary customer/competitor benchmarking presented directly to non-executive directors."},
            {"target": "data_chief_ai_officer", "edge_type": "AUDITS_STRATEGIC_AND_AI_PERFORMANCE", "artifact": "Enterprise AI Portfolio Cash-ROIC & Workflow Redesign Scorecard", "protocol": "Audits P&L realization, inference unit economics, and kill-gates on low-impact AI pilots."},
            {"target": "exec_chief_operating_officer", "edge_type": "AUDITS_STRATEGIC_AND_AI_PERFORMANCE", "artifact": "Zero-Based Unit-Cost & Top-Decile Peer Productivity Benchmark", "protocol": "Dissects cycle times, span-of-control bloat, and automation capture across operations."},
            {"target": "prod_chief_product_officer", "edge_type": "AUDITS_STRATEGIC_AND_AI_PERFORMANCE", "artifact": "Product Win/Loss Telemetry & Feature R&D Yield Audit", "protocol": "Links engineering R&D spend directly to cohort adoption, pricing power, and churn reduction."},
        ],
    },
])


from orgprompt.governance.catalog_specialists import SPECIALIST_GOVERNANCE_ROLE_SPECS

ALL_GOVERNANCE_ROLE_SPECS: List[Dict[str, Any]] = RAW_GOVERNANCE_ROLE_SPECS + SPECIALIST_GOVERNANCE_ROLE_SPECS

_UNIVERSAL_DIRS = [
    "gov_lead_independent_board_chair",
    "gov_audit_committee_financial_expert_chair",
    "gov_capital_allocation_value_director",
    "gov_compensation_succession_chair",
]
_UNIVERSAL_AUDS = [
    "gov_external_statutory_forensic_auditor",
    "gov_independent_strategic_value_auditor",
]


def _make_comp(
    comp_id: str,
    industry_slug: str,
    industry_name: str,
    stage: CompanyStage,
    board_size: int,
    spec_dirs: List[str],
    spec_auds: List[str],
    focus: str,
) -> Dict[str, Any]:
    dirs = (_UNIVERSAL_DIRS if stage == "PUBLIC_ENTERPRISE" else ["gov_lead_independent_board_chair", "gov_capital_allocation_value_director"]) + spec_dirs
    # deduplicate preserving order
    seen_d: List[str] = []
    for s in dirs:
        if s not in seen_d:
            seen_d.append(s)
    seen_a: List[str] = []
    for s in (_UNIVERSAL_AUDS + spec_auds):
        if s not in seen_a:
            seen_a.append(s)
    return {
        "id": comp_id,
        "industry_slug": industry_slug,
        "industry_name": industry_name,
        "company_stage": stage,
        "board_size": board_size,
        "seat_role_slugs": seen_d,
        "external_auditor_slugs": seen_a,
        "charter_summary": (
            f"{stage.replace('_', ' ').title()} Fiduciary Board & Assurance Charter for {industry_name}: {focus}"
        ),
        "quarterly_agenda": [
            "1. Closed Non-Executive In-Camera Session (CEO & Management Excluded) — Candid Narrative vs. Cash Reality Check",
            f"2. Core Sector Value-Driver & Capital Allocation Tear-Down ({focus})",
            "3. Statutory GAAP/IFRS Cash Conversion, Capitalization Conservatism & SOX/Internal Control Assurance",
            "4. Domain Tail-Risk, Regulatory/Safety Gate & Independent Strategic/AI ROI Verification",
            "5. Binding Capital Tranche Authorizations, Kill-Gates & Executive Incentive Alignment Resolutions",
        ],
    }


INDUSTRY_BOARD_COMPOSITIONS: List[Dict[str, Any]] = [
    # 16 Public Enterprise Slates (covering all 16 macro industries)
    _make_comp("ibc_pub_01", "technology_ai", "Technology, Cloud Infrastructure & Artificial Intelligence", "PUBLIC_ENTERPRISE", 9,
               ["gov_tech_ai_semiconductor_director", "gov_special_committee_mna_turnaround_director"],
               ["gov_cybersecurity_ai_safety_board_auditor"],
               "GPU/Cloud CapEx ROIC, 3-4yr accelerator depreciation honesty, ARR cohort retention & frontier AI safety"),
    _make_comp("ibc_pub_02", "semiconductors_mfg", "Semiconductors & Advanced Hardware Manufacturing", "PUBLIC_ENTERPRISE", 9,
               ["gov_tech_ai_semiconductor_director", "gov_aerospace_defense_security_director"],
               ["gov_industrial_supply_chain_quality_auditor"],
               "Leading-edge wafer fab yield curves, tool CapEx payback, CoWoS/HBM supply bottlenecks & export controls"),
    _make_comp("ibc_pub_03", "telecommunications", "Telecommunications & Digital Networks", "PUBLIC_ENTERPRISE", 11,
               ["gov_telco_energy_infra_regulatory_director", "gov_special_committee_mna_turnaround_director"],
               ["gov_cybersecurity_ai_safety_board_auditor", "gov_esg_climate_labor_governance_auditor"],
               "EBITDAaL-to-Organic-Cash conversion, eCapEx discipline, copper/MPLS switch-off, B2B margin & TowerCo SOTP"),
    _make_comp("ibc_pub_04", "finance_quant", "Finance, Quantitative Trading & Fintech", "PUBLIC_ENTERPRISE", 11,
               ["gov_financial_systemic_risk_chair", "gov_special_committee_mna_turnaround_director"],
               ["gov_cybersecurity_ai_safety_board_auditor"],
               "CET1/LCR intraday liquidity survival, HTM duration mark-to-market, credit vintage roll-rates & SR 11-7 model risk"),
    _make_comp("ibc_pub_05", "healthcare_biotech", "Healthcare Systems, Clinical Medicine & Biotech", "PUBLIC_ENTERPRISE", 9,
               ["gov_biotech_clinical_scientific_director"],
               ["gov_healthcare_patient_safety_auditor"],
               "Risk-adjusted patient mortality, clinical AI/SaMD subgroup calibration (Simpson's Paradox defense) & CMS integrity"),
    _make_comp("ibc_pub_06", "pharmaceuticals", "Pharmaceuticals, Vaccine Discovery & Drug Development", "PUBLIC_ENTERPRISE", 10,
               ["gov_biotech_clinical_scientific_director", "gov_special_committee_mna_turnaround_director"],
               ["gov_healthcare_patient_safety_auditor", "gov_industrial_supply_chain_quality_auditor"],
               "Pre-specified Phase I-III trial rigor, patent-cliff rNPV discipline, cGMP sterile fill-finish & 21 CFR Part 11"),
    _make_comp("ibc_pub_07", "energy_grids", "Energy, Electrical Grids & Decarbonization", "PUBLIC_ENTERPRISE", 10,
               ["gov_telco_energy_infra_regulatory_director"],
               ["gov_esg_climate_labor_governance_auditor", "gov_industrial_supply_chain_quality_auditor"],
               "Regulated rate-base ROIC, grid interconnect CapEx, BESS thermal safety & physical MWh decarbonization"),
    _make_comp("ibc_pub_08", "aerospace_defense", "Aerospace, Defense & Space Exploration", "PUBLIC_ENTERPRISE", 10,
               ["gov_aerospace_defense_security_director", "gov_tech_ai_semiconductor_director"],
               ["gov_industrial_supply_chain_quality_auditor", "gov_cybersecurity_ai_safety_board_auditor"],
               "Fixed-price development bid caps, EAC/CPI honesty, DO-178C airworthiness & ITAR/CMMC classified security"),
    _make_comp("ibc_pub_09", "autonomous_robotics", "Autonomous Mobility, Robotics & Industrial Automation", "PUBLIC_ENTERPRISE", 9,
               ["gov_tech_ai_semiconductor_director", "gov_aerospace_defense_security_director"],
               ["gov_industrial_supply_chain_quality_auditor", "gov_cybersecurity_ai_safety_board_auditor"],
               "Autonomous safety case per million miles, hardware BOM learning curves, fleet CapEx & OT cyber assurance"),
    _make_comp("ibc_pub_10", "cybersecurity", "Cybersecurity, National Intelligence & Threat Defense", "PUBLIC_ENTERPRISE", 9,
               ["gov_tech_ai_semiconductor_director", "gov_aerospace_defense_security_director"],
               ["gov_cybersecurity_ai_safety_board_auditor"],
               "Zero-trust crown-jewel containment, sovereign FedRAMP/ANSSI assurance, NRR & autonomous SOC margin"),
    _make_comp("ibc_pub_11", "global_logistics", "Global Logistics, Maritime Freight & Supply Chain", "PUBLIC_ENTERPRISE", 9,
               ["gov_retail_consumer_brand_director", "gov_telco_energy_infra_regulatory_director"],
               ["gov_industrial_supply_chain_quality_auditor", "gov_esg_climate_labor_governance_auditor"],
               "Fleet/network utilization ROIC, maritime/customs disruption resilience, fuel/labor safety & working capital"),
    _make_comp("ibc_pub_12", "retail_consumer", "Retail, E-Commerce & Luxury Consumer Goods", "PUBLIC_ENTERPRISE", 9,
               ["gov_retail_consumer_brand_director", "gov_media_creator_venture_board_partner"],
               ["gov_industrial_supply_chain_quality_auditor", "gov_esg_climate_labor_governance_auditor"],
               "Traffic-led comp quality, GMROI inventory velocity, true DTC contribution margin & brand equity protection"),
    _make_comp("ibc_pub_13", "creative_media", "Creative Arts, Media, Animation & Interactive Entertainment", "PUBLIC_ENTERPRISE", 9,
               ["gov_media_creator_venture_board_partner", "gov_special_committee_mna_turnaround_director"],
               ["gov_cybersecurity_ai_safety_board_auditor"],
               "ASC 926 content amortization conservatism, slate cash-on-cash IRR, subscriber churn & IP licensing ROIC"),
    _make_comp("ibc_pub_14", "professional_services", "Professional Services, Management Consulting & Strategic Advisory", "PUBLIC_ENTERPRISE", 8,
               ["gov_financial_systemic_risk_chair", "gov_special_committee_mna_turnaround_director"],
               ["gov_cybersecurity_ai_safety_board_auditor"],
               "Partner/talent leverage, AI productized-delivery margin transition, conflict independence & client confidentiality"),
    _make_comp("ibc_pub_15", "frontier_research", "Frontier Research & Fundamental Science Institutions", "PUBLIC_ENTERPRISE", 8,
               ["gov_tech_ai_semiconductor_director", "gov_biotech_clinical_scientific_director"],
               ["gov_cybersecurity_ai_safety_board_auditor"],
               "Multi-horizon scientific breakthrough gating, compute/lab infrastructure stewardship, reproducibility & bio/AI safety"),
    _make_comp("ibc_pub_16", "public_sector_reg", "Public Sector, Sovereign Digital Governance & Regulatory Bodies", "PUBLIC_ENTERPRISE", 9,
               ["gov_telco_energy_infra_regulatory_director", "gov_aerospace_defense_security_director"],
               ["gov_cybersecurity_ai_safety_board_auditor", "gov_esg_climate_labor_governance_auditor"],
               "Statutory public-trust accountability, sovereign cloud/data security, procurement integrity & citizen SLA delivery"),
    # 6 Venture / Indie / Boutique Studio Slates
    _make_comp("ibc_ven_01", "creative_media", "Indie Film Studios, YouTube Production Houses & Creator Outfits", "VENTURE_OR_BOUTIQUE", 5,
               ["gov_media_creator_venture_board_partner", "gov_retail_consumer_brand_director", "gov_audit_committee_financial_expert_chair"],
               [],
               "Blumhouse/A24 negative-cost caps, pre-shoot Title/Thumbnail CTR validation, ASC 926 cash honesty & creator/merch working capital"),
    _make_comp("ibc_ven_02", "technology_ai", "Seed-to-Series-C AI & Cloud Startups", "VENTURE_OR_BOUTIQUE", 5,
               ["gov_tech_ai_semiconductor_director", "gov_audit_committee_financial_expert_chair", "gov_special_committee_mna_turnaround_director"],
               ["gov_cybersecurity_ai_safety_board_auditor"],
               "18-month burn multiple, unsubsidized inference gross margin, organic NRR & enterprise SOC2/AI safety"),
    _make_comp("ibc_ven_03", "healthcare_biotech", "Clinical-Stage Biotech & Digital Health / SaMD Ventures", "VENTURE_OR_BOUTIQUE", 5,
               ["gov_biotech_clinical_scientific_director", "gov_audit_committee_financial_expert_chair", "gov_special_committee_mna_turnaround_director"],
               ["gov_healthcare_patient_safety_auditor"],
               "Cash runway past binary Phase II/FDA readout, truth-seeking biomarker kill-gates & subgroup SaMD calibration"),
    _make_comp("ibc_ven_04", "finance_quant", "FinTech, Neobank & Quantitative Trading Boutiques", "VENTURE_OR_BOUTIQUE", 5,
               ["gov_financial_systemic_risk_chair", "gov_audit_committee_financial_expert_chair", "gov_tech_ai_semiconductor_director"],
               ["gov_cybersecurity_ai_safety_board_auditor"],
               "Cohort credit loss roll-rates, warehouse funding covenants, BSA/AML compliance & payment ledger reconciliation"),
    _make_comp("ibc_ven_05", "autonomous_robotics", "Deep-Tech Robotics, Defense-Tech & Hardware Ventures", "VENTURE_OR_BOUTIQUE", 5,
               ["gov_tech_ai_semiconductor_director", "gov_aerospace_defense_security_director", "gov_audit_committee_financial_expert_chair"],
               ["gov_industrial_supply_chain_quality_auditor"],
               "Prototype-to-production BOM gross margin, field safety reliability, working-capital inventory & DoD/commercial conversion"),
    _make_comp("ibc_ven_06", "retail_consumer", "DTC Consumer Brands & Boutique Commerce Studios", "VENTURE_OR_BOUTIQUE", 5,
               ["gov_retail_consumer_brand_director", "gov_media_creator_venture_board_partner", "gov_audit_committee_financial_expert_chair"],
               ["gov_industrial_supply_chain_quality_auditor"],
               "First-order contribution profitability, MOQ inventory discipline, organic creator CAC & repeat cohort LTV"),
]


def _row_to_gov_role(row: Tuple[Any, ...]) -> GovernanceRole:
    return GovernanceRole(
        id=row[0],
        slug=row[1],
        title=row[2],
        governance_category=row[3],
        committee_type=row[4],
        selected_industries=json.loads(row[5] or "[]"),
        typical_human_background=row[6],
        fiduciary_mandate=row[7],
        quarterly_review_cadence=json.loads(row[8] or "[]"),
        kpi_value_tree=json.loads(row[9] or "{}"),
        red_flag_triggers=json.loads(row[10] or "[]"),
        oversight_targets=json.loads(row[11] or "[]"),
        system_prompt=row[12],
        character_count=int(row[13] or len(row[12])),
        metadata=json.loads(row[14] or "{}"),
        created_at=str(row[15] or ""),
    )


def seed_governance_taxonomy(
    db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None,
) -> Dict[str, int]:
    """Idempotently seeds all 18 governance roles, 22 industry board slates, and 72 oversight edges."""
    owns_conn = not isinstance(db_path_or_conn, sqlite3.Connection)
    conn = ensure_governance_schema(db_path_or_conn)
    try:
        edge_count = 0
        for spec in ALL_GOVERNANCE_ROLE_SPECS:
            prompt = _build_fiduciary_7_section_prompt(spec)
            targets = [e["target"] for e in spec["edges"]]
            meta = {
                "socratic_questions": spec["socratic_questions"],
                "ai_value_directives": spec["ai_value_directives"],
            }
            conn.execute(
                """
                INSERT INTO governance_roles (
                    id, slug, title, governance_category, committee_type,
                    selected_industries_json, typical_human_background, fiduciary_mandate,
                    quarterly_review_cadence_json, kpi_value_tree_json, red_flag_triggers_json,
                    oversight_targets_json, system_prompt, character_count, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(slug) DO UPDATE SET
                    title=excluded.title,
                    governance_category=excluded.governance_category,
                    committee_type=excluded.committee_type,
                    selected_industries_json=excluded.selected_industries_json,
                    typical_human_background=excluded.typical_human_background,
                    fiduciary_mandate=excluded.fiduciary_mandate,
                    quarterly_review_cadence_json=excluded.quarterly_review_cadence_json,
                    kpi_value_tree_json=excluded.kpi_value_tree_json,
                    red_flag_triggers_json=excluded.red_flag_triggers_json,
                    oversight_targets_json=excluded.oversight_targets_json,
                    system_prompt=excluded.system_prompt,
                    character_count=excluded.character_count,
                    metadata_json=excluded.metadata_json
                """,
                (
                    spec["id"],
                    spec["slug"],
                    spec["title"],
                    spec["governance_category"],
                    spec["committee_type"],
                    json.dumps(spec["selected_industries"]),
                    spec["typical_human_background"],
                    spec["fiduciary_mandate"],
                    json.dumps(spec["quarterly_review_cadence"]),
                    json.dumps(spec["kpi_value_tree"]),
                    json.dumps(spec["red_flag_triggers"]),
                    json.dumps(targets),
                    prompt,
                    len(prompt),
                    json.dumps(meta),
                ),
            )
            for idx, e in enumerate(spec["edges"], 1):
                edge_id = f"goe_{spec['id']}_{idx:02d}"
                conn.execute(
                    """
                    INSERT INTO governance_oversight_edges (
                        id, governance_role_id, target_management_role_slug,
                        edge_type, review_artifact, protocol
                    ) VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(governance_role_id, target_management_role_slug, edge_type) DO UPDATE SET
                        review_artifact=excluded.review_artifact,
                        protocol=excluded.protocol
                    """,
                    (edge_id, spec["id"], e["target"], e["edge_type"], e["artifact"], e["protocol"]),
                )
                edge_count += 1

        for comp in INDUSTRY_BOARD_COMPOSITIONS:
            conn.execute(
                """
                INSERT INTO industry_board_compositions (
                    id, industry_slug, industry_name, company_stage, board_size,
                    seat_role_slugs_json, external_auditor_slugs_json,
                    charter_summary, quarterly_agenda_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(industry_slug, company_stage) DO UPDATE SET
                    industry_name=excluded.industry_name,
                    board_size=excluded.board_size,
                    seat_role_slugs_json=excluded.seat_role_slugs_json,
                    external_auditor_slugs_json=excluded.external_auditor_slugs_json,
                    charter_summary=excluded.charter_summary,
                    quarterly_agenda_json=excluded.quarterly_agenda_json
                """,
                (
                    comp["id"],
                    comp["industry_slug"],
                    comp["industry_name"],
                    comp["company_stage"],
                    comp["board_size"],
                    json.dumps(comp["seat_role_slugs"]),
                    json.dumps(comp["external_auditor_slugs"]),
                    comp["charter_summary"],
                    json.dumps(comp["quarterly_agenda"]),
                ),
            )
        conn.commit()
        return {
            "governance_roles": len(ALL_GOVERNANCE_ROLE_SPECS),
            "industry_board_compositions": len(INDUSTRY_BOARD_COMPOSITIONS),
            "governance_oversight_edges": edge_count,
        }
    finally:
        if owns_conn:
            conn.close()


def list_governance_roles(
    db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None,
    category: Optional[str] = None,
    industry_slug: Optional[str] = None,
) -> List[GovernanceRole]:
    """Lists seeded governance roles (auto-seeding if table is empty)."""
    owns_conn = not isinstance(db_path_or_conn, sqlite3.Connection)
    conn = ensure_governance_schema(db_path_or_conn)
    try:
        cnt = conn.execute("SELECT COUNT(*) FROM governance_roles").fetchone()[0]
        if cnt == 0:
            seed_governance_taxonomy(conn)
        sql = "SELECT * FROM governance_roles"
        params: List[Any] = []
        if category:
            sql += " WHERE governance_category = ?"
            params.append(category.upper().strip())
        sql += " ORDER BY id"
        roles = [_row_to_gov_role(r) for r in conn.execute(sql, params).fetchall()]
        if industry_slug:
            islug = industry_slug.strip().lower().replace("ind_", "")
            roles = [r for r in roles if not r.selected_industries or islug in r.selected_industries]
        return roles
    finally:
        if owns_conn:
            conn.close()


def get_governance_role(
    slug_or_id: str,
    db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None,
) -> Optional[GovernanceRole]:
    """Fetches a single `GovernanceRole` by slug or id."""
    owns_conn = not isinstance(db_path_or_conn, sqlite3.Connection)
    conn = ensure_governance_schema(db_path_or_conn)
    try:
        cnt = conn.execute("SELECT COUNT(*) FROM governance_roles").fetchone()[0]
        if cnt == 0:
            seed_governance_taxonomy(conn)
        key = slug_or_id.strip()
        row = conn.execute(
            "SELECT * FROM governance_roles WHERE slug = ? OR id = ? OR LOWER(title) = LOWER(?)",
            (key, key, key),
        ).fetchone()
        return _row_to_gov_role(row) if row else None
    finally:
        if owns_conn:
            conn.close()


def list_industry_board_compositions(
    db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None,
    stage: Optional[str] = None,
) -> List[IndustryBoardComposition]:
    """Lists all industry board composition templates."""
    owns_conn = not isinstance(db_path_or_conn, sqlite3.Connection)
    conn = ensure_governance_schema(db_path_or_conn)
    try:
        if conn.execute("SELECT COUNT(*) FROM industry_board_compositions").fetchone()[0] == 0:
            seed_governance_taxonomy(conn)
        sql = "SELECT id, industry_slug, industry_name, company_stage, board_size, seat_role_slugs_json, external_auditor_slugs_json, charter_summary, quarterly_agenda_json FROM industry_board_compositions"
        params: List[Any] = []
        if stage:
            sql += " WHERE company_stage = ?"
            params.append(stage.upper().strip())
        sql += " ORDER BY id"
        out: List[IndustryBoardComposition] = []
        for r in conn.execute(sql, params).fetchall():
            out.append(IndustryBoardComposition(
                id=r[0], industry_slug=r[1], industry_name=r[2], company_stage=r[3],
                board_size=int(r[4]), seat_role_slugs=json.loads(r[5] or "[]"),
                external_auditor_slugs=json.loads(r[6] or "[]"), charter_summary=r[7],
                quarterly_agenda=json.loads(r[8] or "[]"),
            ))
        return out
    finally:
        if owns_conn:
            conn.close()


def board_for_company(
    company_or_industry: str,
    stage: Optional[str] = None,
    db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None,
) -> BoardSlateRecommendation:
    """Resolves an industry- and stage-tailored Board & Audit Slate for any company or macro industry."""
    owns_conn = not isinstance(db_path_or_conn, sqlite3.Connection)
    conn = ensure_governance_schema(db_path_or_conn)
    try:
        if conn.execute("SELECT COUNT(*) FROM governance_roles").fetchone()[0] == 0:
            seed_governance_taxonomy(conn)

        q = company_or_industry.strip()
        q_norm = q.lower().replace("ind_", "")
        resolved_company_name: Optional[str] = None
        resolved_company_slug: Optional[str] = None
        resolved_ind_slug: Optional[str] = None
        auto_stage: CompanyStage = "PUBLIC_ENTERPRISE"

        has_f500 = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='fortune500_companies'").fetchone()
        if has_f500:
            crow = conn.execute(
                """
                SELECT name, slug, industry_id, macro_industry, revenue_billions
                FROM fortune500_companies
                WHERE LOWER(slug) = ? OR LOWER(name) = ? OR LOWER(name) LIKE ? OR LOWER(slug) LIKE ?
                ORDER BY CASE WHEN LOWER(slug) = ? OR LOWER(name) = ? THEN 0 ELSE 1 END, rank ASC
                LIMIT 1
                """,
                (q_norm, q_norm, f"%{q_norm}%", f"%{q_norm.replace(' ', '_')}%", q_norm, q_norm),
            ).fetchone()
            if crow:
                resolved_company_name, resolved_company_slug = crow[0], crow[1]
                resolved_ind_slug = str(crow[2] or "").replace("ind_", "")
                rev = float(crow[4] or 0.0)
                if rev > 0 and rev < 1.5:
                    auto_stage = "VENTURE_OR_BOUTIQUE"

        if not resolved_ind_slug:
            # Match direct industry slug or keyword
            ind_rows = conn.execute("SELECT DISTINCT industry_slug, industry_name FROM industry_board_compositions WHERE company_stage='PUBLIC_ENTERPRISE'").fetchall()
            for islug, iname in ind_rows:
                if q_norm == islug or q_norm in islug or q_norm in iname.lower():
                    resolved_ind_slug = islug
                    break
            if not resolved_ind_slug:
                kw_map = [
                    (["creator", "youtube", "indie", "film", "studio", "media", "mrbeast", "a24", "blumhouse"], ("creative_media", "VENTURE_OR_BOUTIQUE")),
                    (["telecom", "telco", "5g", "fiber", "orange", "verizon"], ("telecommunications", "PUBLIC_ENTERPRISE")),
                    (["bank", "fintech", "quant", "trading", "capital"], ("finance_quant", "PUBLIC_ENTERPRISE")),
                    (["pharma", "drug", "vaccine"], ("pharmaceuticals", "PUBLIC_ENTERPRISE")),
                    (["biotech", "clinical", "hospital", "health", "samd"], ("healthcare_biotech", "PUBLIC_ENTERPRISE")),
                    (["semi", "fab", "wafer", "chip", "nvidia", "tsmc"], ("semiconductors_mfg", "PUBLIC_ENTERPRISE")),
                    (["cyber", "security", "soc"], ("cybersecurity", "PUBLIC_ENTERPRISE")),
                    (["aero", "defense", "space"], ("aerospace_defense", "PUBLIC_ENTERPRISE")),
                    (["energy", "grid", "utility", "solar"], ("energy_grids", "PUBLIC_ENTERPRISE")),
                    (["retail", "consumer", "luxury", "ecommerce"], ("retail_consumer", "PUBLIC_ENTERPRISE")),
                    (["logistics", "freight", "supply"], ("global_logistics", "PUBLIC_ENTERPRISE")),
                ]
                for kws, (mapped_ind, mapped_stg) in kw_map:
                    if any(k in q_norm for k in kws):
                        resolved_ind_slug = mapped_ind
                        auto_stage = mapped_stg  # type: ignore[assignment]
                        break
            if not resolved_ind_slug:
                resolved_ind_slug = "technology_ai"

        chosen_stage: CompanyStage = stage.upper().strip() if stage else auto_stage  # type: ignore[assignment]
        comp_row = conn.execute(
            "SELECT id, industry_slug, industry_name, company_stage, board_size, seat_role_slugs_json, external_auditor_slugs_json, charter_summary, quarterly_agenda_json FROM industry_board_compositions WHERE industry_slug = ? AND company_stage = ?",
            (resolved_ind_slug, chosen_stage),
        ).fetchone()
        if not comp_row:
            comp_row = conn.execute(
                "SELECT id, industry_slug, industry_name, company_stage, board_size, seat_role_slugs_json, external_auditor_slugs_json, charter_summary, quarterly_agenda_json FROM industry_board_compositions WHERE industry_slug = ? AND company_stage = 'PUBLIC_ENTERPRISE'",
                (resolved_ind_slug,),
            ).fetchone()

        seat_slugs = json.loads(comp_row[5] or "[]")
        aud_slugs = json.loads(comp_row[6] or "[]")
        directors = [r for s in seat_slugs if (r := get_governance_role(s, conn)) is not None]
        auditors = [r for s in aud_slugs if (r := get_governance_role(s, conn)) is not None]

        all_ids = [r.id for r in (directors + auditors)]
        slug_by_id = {r.id: r.slug for r in (directors + auditors)}
        edges: List[GovernanceOversightEdge] = []
        if all_ids:
            placeholders = ",".join("?" for _ in all_ids)
            for er in conn.execute(
                f"SELECT id, governance_role_id, target_management_role_slug, edge_type, review_artifact, protocol FROM governance_oversight_edges WHERE governance_role_id IN ({placeholders}) ORDER BY id",
                all_ids,
            ).fetchall():
                edges.append(GovernanceOversightEdge(
                    id=er[0], governance_role_id=er[1], governance_role_slug=slug_by_id.get(er[1], ""),
                    target_management_role_slug=er[2], edge_type=er[3], review_artifact=er[4], protocol=er[5],
                ))

        return BoardSlateRecommendation(
            query=q,
            company_name=resolved_company_name,
            company_slug=resolved_company_slug,
            industry_slug=comp_row[1],
            industry_name=comp_row[2],
            company_stage=comp_row[3],
            board_size=int(comp_row[4]),
            charter_summary=comp_row[7],
            quarterly_agenda=json.loads(comp_row[8] or "[]"),
            board_directors=directors,
            external_auditors=auditors,
            oversight_edges=edges,
        )
    finally:
        if owns_conn:
            conn.close()


__all__ = [
    "ALL_GOVERNANCE_ROLE_SPECS",
    "INDUSTRY_BOARD_COMPOSITIONS",
    "seed_governance_taxonomy",
    "list_governance_roles",
    "get_governance_role",
    "list_industry_board_compositions",
    "board_for_company",
]
