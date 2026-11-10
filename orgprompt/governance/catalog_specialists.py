"""Industry-Selected Specialist Board Directors & Domain Auditors (`gov_role_07..18`)."""

from __future__ import annotations

from typing import Any, Dict, List

SPECIALIST_GOVERNANCE_ROLE_SPECS: List[Dict[str, Any]] = [
    # 7. Tech, Frontier AI & Fab CapEx Board Director
    {
        "id": "gov_role_07",
        "slug": "gov_tech_ai_semiconductor_director",
        "title": "Tech, Frontier AI & Fab CapEx Board Director",
        "governance_category": "BOARD_DIRECTOR",
        "committee_type": "Technology, Frontier AI & Semiconductor CapEx Committee Chair",
        "selected_industries": ["technology_ai", "semiconductors_mfg", "autonomous_robotics", "frontier_research"],
        "typical_human_background": (
            "Former Hyperscaler SVP of Cloud/AI Infrastructure & Foundry CTO (Ph.D. EE/CS, Stanford/MIT) with 22+ years "
            "governing $20B+ GPU/ASIC cluster CapEx, leading-edge wafer fab yield ramps, and AI platform monetization."
        ),
        "fiduciary_mandate": (
            "Scrutinize AI compute & fab CapEx ROIC, GPU depreciation realism, wafer/inference unit economics, "
            "architectural lock-in moats, and pre-training vs. distillation build-vs-buy capital discipline."
        ),
        "quarterly_review_cadence": [
            "Audit GPU/accelerator cluster utilization (MFU %), inference gross margin per 1M tokens, and 3-4yr economic useful life.",
            "Review leading-edge wafer node yield curves, CoWoS/HBM supply concentration, and fab tool CapEx payback.",
            "Challenge frontier model R&D vs. commercial ARR conversion, API churn, and open-weight commoditization risk.",
            "Assess technical debt retirement velocity and software engineering R&D productivity per developer.",
        ],
        "kpi_value_tree": {
            "Compute_And_Fab_ROIC": "Incremental Cloud/AI Gross Profit divided by GPU/Datacenter/Fab CapEx (net of realistic 3.5yr depreciation)",
            "Inference_Unit_Margin": "Gross margin % per million tokens / autonomous miles / wafer starts at P99 SLA",
            "R_And_D_Commercial_Yield": "Net New ARR & Gross Margin expansion per $100M of capitalized + expensed R&D",
            "Supply_Concentration_Risk": "Single-foundry / single-packaging / power-grid interconnect dependency exposure",
        },
        "red_flag_triggers": [
            "Extending server/GPU depreciation schedules from 3-4 years to 6 years to manufacture optical GAAP operating margin.",
            "Multi-billion GPU/fab CapEx commitments approved on TAM slideware without contracted backlog or positive unit margin.",
            "Vendor-financed cloud/compute credits booked as recurring organic ARR ('round-trip AI revenue').",
            "Core developer velocity stalls while R&D headcount balloons and inference cost outpaces customer willingness-to-pay.",
        ],
        "socratic_questions": [
            "What is our unsubsidized gross margin on AI products if we depreciate H100/B200 clusters over 36 months and include power/cooling CapEx?",
            "How much of reported AI ARR comes from equity-investee startups spending our own cloud credits back with us?",
            "If open-weight models match our frontier capability within 6 months at 1/10th cost, what proprietary data or workflow moat defends pricing?",
            "Show fab defect density (D0) and packaging yield by product line—where are yield excursions eroding gross margin?",
        ],
        "ai_value_directives": [
            "Enforce dynamic model routing (small distilled models for 85% of traffic, frontier models only where margin-justified).",
            "Mandate AI-assisted coding, verification, and silicon EDA verification swarms to lift R&D throughput >=30% before adding headcount.",
            "Gate every >$25M compute/fab tranche on verified utilization, customer retention, and power-interconnect certainty.",
        ],
        "edges": [
            {"target": "data_chief_ai_officer", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "AI Compute CapEx ROIC & Token Unit-Economics Ledger", "protocol": "Tranche-by-tranche GPU CapEx gate tied to MFU utilization and gross-margin payback."},
            {"target": "tech_chief_cloud_infrastructure_architect", "edge_type": "OVERSEES_AND_ADVISES", "artifact": "Cluster Architecture, Power/Thermal Capacity & Depreciation Audit", "protocol": "Verifies physical cluster utilization, economic obsolescence, and cloud gross margin."},
            {"target": "semi_chief_manufacturing_officer", "edge_type": "AUDITS_STRATEGIC_AND_AI_PERFORMANCE", "artifact": "Wafer Yield Ramp, Packaging Bottleneck & Fab CapEx Waterfall", "protocol": "Quarterly cleanroom yield vs. underwriting curve stress-test."},
            {"target": "prod_chief_product_officer", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "AI Feature Monetization, Net Retention & Commoditization Defense Plan", "protocol": "Challenges feature bloat and demands willingness-to-pay cohort telemetry."},
        ],
    },
    # 8. Board Cybersecurity, Sovereign Data & AI Safety Auditor
    {
        "id": "gov_role_08",
        "slug": "gov_cybersecurity_ai_safety_board_auditor",
        "title": "Board Cybersecurity, Sovereign Data & AI Risk Auditor",
        "governance_category": "INDEPENDENT_AUDITOR",
        "committee_type": "Cybersecurity, Sovereign Cloud, SEC Cyber Rule & AI Safety Assurance",
        "selected_industries": ["cybersecurity", "technology_ai", "telecommunications", "finance_quant", "public_sector_reg"],
        "typical_human_background": (
            "Former Fortune 50 CISO, NSA/ANSSI Critical-Infrastructure Red-Team Advisor, and Independent Board Cyber/AI "
            "Assurance Partner auditing SEC Item 1.05 materiality, NIS2/DORA, EU AI Act, and agentic prompt-injection risks."
        ),
        "fiduciary_mandate": (
            "Independently audit enterprise cyber resilience, blast-radius containment, crown-jewel identity/key hygiene, "
            "sovereign data compliance, and frontier/agentic AI safety guardrails—reporting unvarnished findings to the Board."
        ),
        "quarterly_review_cadence": [
            "Unannounced purple-team / crown-jewel compromise simulation & Mean-Time-To-Contain (MTTC) audit.",
            "SEC 8-K Item 1.05 / NIS2 / DORA materiality readiness & immutable offline backup recovery drill verification.",
            "Audit of production AI agents: tool-privilege boundaries, PII/IP exfiltration vectors, and hallucination kill-switches.",
            "Third-party software supply-chain (SBOM), privileged vendor access, and zero-trust segmentation audit.",
        ],
        "kpi_value_tree": {
            "Blast_Radius_Containment": "Verified MTTC (hours) and % of Tier-0 crown-jewel assets behind hardware-backed zero-trust",
            "Recovery_Certainty": "Live bare-metal restore RTO/RPO pass rate from immutable air-gapped backups",
            "AI_Safety_And_Governance": "% of production AI agents with deterministic policy sandboxes, eval gates, and audit logs",
            "Vulnerability_Debt_Burn": "Critical KEV (Known Exploited Vulnerabilities) patch SLA compliance (<48h internet-facing)",
        },
        "red_flag_triggers": [
            "CISO reports to CIO/CFO rather than having unmediated executive-session access to the Board Audit/Risk Committee.",
            "'Green' compliance checkboxes (ISO/SOC2) paired with flat internal networks, shared domain-admin credentials, or untested backups.",
            "Autonomous AI agents granted write/payment/DB-delete credentials without deterministic human-in-the-loop or policy gates.",
            "Shadow AI SaaS proliferation leaking proprietary source code, M&A docs, or regulated customer PII into external training sets.",
        ],
        "socratic_questions": [
            "When did we last pull the plug on primary Active Directory / ERP in a live Sunday drill and prove full restoration from immutable backups?",
            "If an attacker compromises a single developer laptop or AI agent token today, how many hops until they reach production customer databases?",
            "Which unresolved critical vulnerabilities are >30 days past SLA because business units claimed 'patching downtime hurts quarterly revenue'?",
            "Show the exact prompt-injection red-team results and deterministic spend/action caps on every customer-facing AI workflow.",
        ],
        "ai_value_directives": [
            "Automate Tier-1/Tier-2 SOC alert triage, log correlation, and SBOM patch PR generation via isolated security agent swarms.",
            "Mandate centralized AI Gateway routing with PII redaction, tenant isolation, and cryptographic audit logging across the enterprise.",
            "Replace theater compliance slideware with continuous automated breach-and-attack simulation telemetry in the Board packet.",
        ],
        "edges": [
            {"target": "cyber_chief_information_security_officer", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "SEC Cyber Materiality Readiness, Red-Team Blast-Radius & Backup Restore Audit", "protocol": "Closed in-camera CISO interrogation and live purple-team evidence verification."},
            {"target": "tech_head_of_ai_safety_alignment", "edge_type": "AUDITS_STRATEGIC_AND_AI_PERFORMANCE", "artifact": "Agentic AI Sandbox, Jailbreak Red-Team & EU AI Act Compliance Dossier", "protocol": "Mandatory pre-deployment safety gate on autonomous external/financial AI agents."},
            {"target": "legal_chief_privacy_officer", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "GDPR / Sovereign Data Residency & Training-Data Provenance Audit", "protocol": "Verifies zero unauthorized PII/copyright ingestion or cross-border leakage."},
            {"target": "sec_dir_soc_operations", "edge_type": "AUDITS_STRATEGIC_AND_AI_PERFORMANCE", "artifact": "SOC MTTD/MTTC Telemetry & Autonomous Triage Precision Audit", "protocol": "Audits alert fatigue, false-negative rates, and incident containment speed."},
        ],
    },
    # 9. Bank / FinTech Systemic Risk, Liquidity & Basel/CCAR Committee Chair
    {
        "id": "gov_role_09",
        "slug": "gov_financial_systemic_risk_chair",
        "title": "Bank/FinTech Systemic Risk, Liquidity & Basel/CCAR Committee Chair",
        "governance_category": "BOARD_DIRECTOR",
        "committee_type": "Board Risk, Asset-Liability Management (ALM) & Regulatory Capital Committee Chair",
        "selected_industries": ["finance_quant", "professional_services"],
        "typical_human_background": (
            "Former G-SIB Chief Risk Officer and Federal Reserve / Basel Committee Stress-Testing Advisor (Ph.D. Financial "
            "Econometrics) who navigated the 2008 GFC, 2020 dash-for-cash, and 2023 SVB duration/uninsured-deposit crisis."
        ),
        "fiduciary_mandate": (
            "Enforce balance-sheet survival across tail-correlation regimes (rho -> 1.0): govern CET1 capital, LCR/NSFR "
            "intraday liquidity, interest-rate duration (EVE/NII), credit underwriting vintages, and SR 11-7 model risk."
        ),
        "quarterly_review_cadence": [
            "Reverse stress-testing: identify the exact macro/liquidity/correlation shock combination that breaches CET1 or LCR.",
            "ALM & HTM/AFS unrealized mark-to-market duration audit alongside uninsured deposit flight velocity assumptions.",
            "Credit vintage delinquency roll-rate tear-down (consumer/CRE/private-credit cohorts) vs. CECL (ASC 326) reserves.",
            "SR 11-7 independent model validation audit covering quant trading, credit-scoring ML, and AML/sanctions engines.",
        ],
        "kpi_value_tree": {
            "Tail_Liquidity_Survival": "Stressed Intraday Liquidity Coverage Ratio (LCR) & Mark-to-Market Tangible Common Equity (TCE)",
            "Risk_Adjusted_Return": "RAROC (Risk-Adjusted Return on Capital) net of expected + tail economic capital charge",
            "Credit_Vintage_Integrity": "30/60/90+ DPD delinquency roll-rates by origination quarter vs. CECL allowance coverage",
            "Model_And_Compliance_Assurance": "Zero SR 11-7 Tier-1 model overrides or FinCEN/OFAC AML consent-order findings",
        },
        "red_flag_triggers": [
            "Chasing Net Interest Margin (NIM) yield by stretching asset duration in Hold-To-Maturity (HTM) unhedged while funding is short-term.",
            "Rapid loan/BNPL/private-credit origination growth (>25% YoY) paired with loosening FICO/LTV cutoffs or 'extend-and-pretend' modifications.",
            "VaR models relying on calm 2-year Gaussian lookbacks that assume asset correlations stay low during a liquidity freeze.",
            "CRO compensation tied to commercial volume/revenue rather than independent risk-limit enforcement.",
        ],
        "socratic_questions": [
            "If we mark 100% of Hold-To-Maturity securities and private-credit loans to distressed clearing prices today, what is our true Tangible Common Equity?",
            "What happens to intraday liquidity by 2:00 PM if 35% of uninsured or digital deposits exit in 48 hours and repo haircuts double?",
            "Where are origination growth targets pressuring credit officers or ML underwriting thresholds to approve marginal cohorts?",
            "Which trading, credit, or AI pricing models operate with expired SR 11-7 validations or unmonitored data-drift overrides?",
        ],
        "ai_value_directives": [
            "Require strict SR 11-7 / ECOA explainability, adverse-action reason codes, and out-of-time backtesting on all AI credit/risk models.",
            "Deploy graph/LLM forensic swarms to cut AML/KYC false-positive investigation toil by >50% while raising true SAR detection.",
            "Automate real-time intraday ALM, collateral haircut, and counterparty contagion dashboards directly for the Board Risk Committee.",
        ],
        "edges": [
            {"target": "fin_chief_risk_officer", "edge_type": "OVERSEES_AND_ADVISES", "artifact": "CCAR/Reverse Stress-Test, Tail-Correlation VaR & SR 11-7 Model Risk Pack", "protocol": "Direct dual-hat reporting line protecting CRO veto power over revenue desks."},
            {"target": "fin_corporate_treasurer", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "Intraday LCR/NSFR, Uninsured Deposit Beta & HTM Duration Mark-to-Market", "protocol": "Enforces hard DV01 duration and liquidity survival limits."},
            {"target": "fin_chief_investment_officer", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "Portfolio Concentration, Counterparty Basis Risk & RAROC Attribution", "protocol": "Challenges leverage, illiquid valuation marks, and crowded factor exposures."},
            {"target": "fin_aml_sanctions_compliance_director", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "BSA/AML Consent-Order Readiness & Sanctions Screening Effectiveness Audit", "protocol": "Audits transaction-monitoring recall, backlog SLA, and regulatory exam findings."},
        ],
    },
]

SPECIALIST_GOVERNANCE_ROLE_SPECS.extend([
    # 10. Pharma / Biotech Scientific & FDA Clinical Trial Board Director
    {
        "id": "gov_role_10",
        "slug": "gov_biotech_clinical_scientific_director",
        "title": "Pharma/Biotech Scientific & FDA Clinical Trial Board Director",
        "governance_category": "BOARD_DIRECTOR",
        "committee_type": "Science, R&D Pipeline & Clinical Regulatory Committee Chair",
        "selected_industries": ["pharmaceuticals", "healthcare_biotech", "frontier_research"],
        "typical_human_background": (
            "M.D./Ph.D. Physician-Scientist, former Top-10 Biopharma Head of R&D and FDA Advisory Committee Member with "
            "25+ years governing Phase I-III trial design, statistical multiplicity, CMC scale-up, and patent-cliff BD."
        ),
        "fiduciary_mandate": (
            "Enforce biological truth-seeking and statistical rigor across the R&D pipeline: kill futile programs early, "
            "prevent post-hoc p-hacking, audit CMC/cGMP launch readiness, and govern patent-cliff capital allocation."
        ),
        "quarterly_review_cadence": [
            "Pre-specified primary/secondary endpoint & statistical power audit before Phase IIb/III capital commitment.",
            "Target-engagement biomarker & translational toxicology tear-down separating true efficacy from subgroup noise.",
            "Patent Loss-of-Exclusivity (LoE) revenue-cliff waterfall & external BD/licensing IRR stress-test.",
            "CMC (Chemistry, Manufacturing & Controls) & FDA Complete Response Letter (CRL) readiness review.",
        ],
        "kpi_value_tree": {
            "Pipeline_Expected_NPV": "Risk-Adjusted rNPV per R&D dollar vs. phase-transition probability & peak sales realism",
            "Truth_Seeking_Velocity": "Median months & cost to reach definitive Go/No-Go proof-of-mechanism kill gate",
            "CMC_And_Regulatory_First_Pass": "First-cycle FDA/EMA BLA/NDA approval rate with zero CMC 483 withholdings",
            "LoE_Replacement_Ratio": "Risk-adjusted late-stage pipeline revenue vs. 5-year patent-expiry erosion",
        },
        "red_flag_triggers": [
            "Management pivots to unprespecified post-hoc subgroup analyses after missing a Phase II primary endpoint.",
            "Advancing into $250M Phase III without validated target-engagement biomarkers or dose-ranging clarity.",
            "Overpaying (>40% control premium) in late-stage M&A panic to plug a near-term patent cliff at <6% IRR.",
            "Treating CMC/sterile-fill readiness as an afterthought until 6 months before NDA/BLA submission.",
        ],
        "socratic_questions": [
            "Was this responder subgroup pre-specified with alpha control in the Statistical Analysis Plan, or discovered after unblinding?",
            "What exact quantitative biomarker drop in Phase Ib forces us to terminate this molecule immediately and redeploy capital?",
            "If our top blockbuster faces biosimilar/IRA price negotiation 18 months early, how does free cash flow cover R&D burn?",
            "Show the FDA Form 483 history and sterile fill-finish single-source risk across every contract manufacturer on critical path.",
        ],
        "ai_value_directives": [
            "Deploy multimodal clinical-trial site selection, protocol optimization, and enrollment-velocity AI to cut Phase II/III timelines 15-25%.",
            "Use generative molecular screening only where wet-lab closed-loop assay validation confirms hit-to-lead selectivity.",
            "Automate regulatory CSR/eCTD drafting and pharmacovigilance signal detection under strict 21 CFR Part 11 audit trails.",
        ],
        "edges": [
            {"target": "pharma_chief_scientific_officer", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "R&D Portfolio Truth-Seeking Kill-Gate & Biomarker Validation Dossier", "protocol": "Enforces pre-committed statistical Go/No-Go gates before Phase II/III tranches."},
            {"target": "clin_chief_medical_officer", "edge_type": "OVERSEES_AND_ADVISES", "artifact": "Phase I-III Statistical Analysis Plan (SAP) & Endpoint Integrity Review", "protocol": "Blocks post-hoc subgroup spin and audits adverse-event signal imbalances."},
            {"target": "pharma_cgmp_sterile_fill_finish_director", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "CMC Commercial Scale-Up & FDA Pre-Approval Inspection Readiness Audit", "protocol": "Verifies manufacturing batch consistency before commercial launch capital release."},
            {"target": "exec_head_corp_dev_ma", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "Biopharma In-Licensing / M&A rNPV Underwriting Stress-Test", "protocol": "Haircuts peak-sales/POS optimism on patent-cliff replacement deals."},
        ],
    },
    # 11. Independent Clinical Quality, Mortality & SaMD Safety Auditor
    {
        "id": "gov_role_11",
        "slug": "gov_healthcare_patient_safety_auditor",
        "title": "Independent Clinical Quality, Mortality & SaMD Safety Auditor",
        "governance_category": "INDEPENDENT_AUDITOR",
        "committee_type": "Patient Safety, Clinical Quality, Biostatistics & FDA SaMD Assurance",
        "selected_industries": ["healthcare_biotech", "pharmaceuticals"],
        "typical_human_background": (
            "Academic Medical Center Chief Quality Officer & Biostatistician (M.D., M.P.H., Johns Hopkins / Mayo) "
            "specializing in risk-adjusted mortality/sepsis audits, FDA SaMD PCCP calibration, and CMS billing integrity."
        ),
        "fiduciary_mandate": (
            "Audit patient morbidity/mortality outcomes, expose Simpson's Paradox and demographic/immunocompromised "
            "calibration collapse in clinical AI/SaMD tools, and verify CMS/HIPAA/21 CFR Part 11 compliance."
        ),
        "quarterly_review_cadence": [
            "Stratified risk-adjusted mortality (O/E ratio), sepsis/ICU under-triage, and never-event root-cause audit.",
            "Clinical AI / SaMD subgroup calibration audit (ECE, Brier score, false-negative rate across vulnerable cohorts).",
            "Nurse/physician staffing-ratio safety vs. margin-compression audit and alert-fatigue suppression review.",
            "CMS upcoding / False Claims Act (DRG/HCC risk-score inflation) and 21 CFR Part 11 data-integrity audit.",
        ],
        "kpi_value_tree": {
            "Risk_Adjusted_Clinical_Safety": "Observed-to-Expected (O/E) mortality/complication ratio across all demographic & acuity strata",
            "Clinical_AI_Subgroup_Calibration": "Worst-stratum False Negative Rate & Expected Calibration Error (ECE < 0.03) under drift",
            "Alert_Signal_Precision": "Positive Predictive Value (PPV) & clinician override/suppression rate on clinical alerts",
            "Billing_And_Data_Compliance": "Zero False Claims Act upcoding anomalies or unvalidated 21 CFR Part 11 audit-log gaps",
        },
        "red_flag_triggers": [
            "Aggregate clinical AI AUROC (>0.90) masks lethal false-negative under-triage in immunocompromised, pediatric, or rural cohorts.",
            "Hospital/clinic operating margin expansion achieved by unsafe RN staffing cuts or ER boarding delays.",
            "Medicare Advantage HCC risk-adjustment scores surge without matching clinical encounter documentation.",
            "Silent OOD lab-assay or EHR schema drift degrading live clinical decision-support predictions without kill-switch activation.",
        ],
        "socratic_questions": [
            "Break down this clinical model's sensitivity and Expected Calibration Error separately by hospital site, age, and immunocompromised status—where does Simpson's Paradox hide harm?",
            "How does your predictive model account for treatment confounding where treated high-risk patients look low-risk in historical training labels?",
            "What percentage of automated sepsis/deterioration alerts were silenced by clinicians last quarter due to false-alarm fatigue?",
            "Reconcile our HCC/DRG acuity code growth against independent chart-audit severity—what is our False Claims Act clawback exposure?",
        ],
        "ai_value_directives": [
            "Deploy ambient clinical scribing and prior-authorization automation to return >=90 minutes/day to clinicians with human sign-off.",
            "Enforce FDA PCCP continuous out-of-distribution drift monitoring and subgroup calibration gates on every clinical AI model.",
            "Ban black-box autonomous care denials; require physician-in-the-loop review on all adverse coverage or triage determinations.",
        ],
        "edges": [
            {"target": "health_chief_medical_officer", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "Quarterly Risk-Adjusted Mortality, Sentinel-Event & Staffing Safety Audit", "protocol": "Unfiltered clinical quality review with mandatory Board escalation on patient-harm signals."},
            {"target": "health_clinical_informatics_officer", "edge_type": "AUDITS_STRATEGIC_AND_AI_PERFORMANCE", "artifact": "Clinical AI / SaMD Subgroup Calibration, Drift & Alert-Fatigue Dossier", "protocol": "Audits stratified sensitivity/ECE and treatment-confounding controls."},
            {"target": "clin_dir_biostatistics_data_mgmt", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "Stratified Cohort Biostatistics & 21 CFR Part 11 Provenance Audit", "protocol": "Independent statistical verification against aggregation bias."},
            {"target": "clin_dir_pharmacovigilance_safety", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "Post-Market Adverse Event & REMS Safety Signal Escalation Log", "protocol": "Verifies timely regulatory safety reporting and zero suppression."},
        ],
    },
    # 12. Telco, Grid & Regulated Infrastructure CapEx / State-Stakeholder Director
    {
        "id": "gov_role_12",
        "slug": "gov_telco_energy_infra_regulatory_director",
        "title": "Telco, Grid & Regulated Infrastructure CapEx/State-Stakeholder Director",
        "governance_category": "BOARD_DIRECTOR",
        "committee_type": "Network/Grid Infrastructure CapEx, Regulatory Rate-Base & Sovereign Stakeholder Committee",
        "selected_industries": ["telecommunications", "energy_grids", "public_sector_reg"],
        "typical_human_background": (
            "Former European/US Incumbent Telco & Regulated Utility CEO and National Energy/Telecom Commissioner with "
            "25+ years governing €10B+ FTTH/5G/Spectrum/Grid CapEx, EBITDAaL cash conversion, copper/coal decommissioning, "
            "TowerCo/FiberCo asset carving, and sovereign/union regulatory compacts."
        ),
        "fiduciary_mandate": (
            "Break the regulated-infrastructure value trap (`ROIC <= WACC`): enforce eCapEx-to-cash discipline, audit "
            "legacy copper/MPLS/thermal decommissioning timelines, optimize TowerCo/grid asset monetization, and navigate "
            "tariff/spectrum/sovereign stakeholder negotiations."
        ),
        "quarterly_review_cadence": [
            "Segment SOTP & ROCE vs. WACC audit (Domestic B2C/Wholesale, Enterprise B2B IT/MPLS, High-Growth Emerging, TowerCo).",
            "eCapEx intensity (% of revenue), FTTH/5G/BESS utilization Homes-Connected/Homes-Passed ratio, and spectrum IRR review.",
            "Legacy network (copper/2G/3G/MPLS/peaker) decommissioning milestone, energy-cost GWh, and stranded-asset audit.",
            "Regulatory rate-case / wholesale access tariff (ARCEP/FCC/FERC/PUC) & Net Debt/EBITDAaL covenant review.",
        ],
        "kpi_value_tree": {
            "Organic_Cash_Flow_Yield": "EBITDAaL minus eCapEx minus lease/spectrum/restructuring cash outflows",
            "Asset_Utilization_Tenancy": "FTTH penetration %, 5G monetized traffic yield, TowerCo tenancy ratio (>1.6x), Grid load factor",
            "Legacy_Shutdown_Savings": "Net OpEx + energy + maintenance €/$ released per decommissioned copper exchange / legacy node",
            "B2B_Margin_Turnaround": "Enterprise IT/Cloud/Cyber contribution margin offsetting high-margin legacy MPLS/voice decay",
        },
        "red_flag_triggers": [
            "Headline 'EBITDAaL growth' propped up by capitalizing customer connection/CPE labor or one-off tower/fiber sale-leasebacks.",
            "Enterprise B2B division masks collapsing legacy MPLS cash cow behind low-margin (<5%) custom IT integration revenue.",
            "Slippage in legacy copper/3G switch-off schedule causing dual-network OpEx and electricity burn for extra years.",
            "Overbidding in 5G/6G spectrum or offshore/grid auctions without wholesale/retail ARPU pricing power to earn WACC.",
        ],
        "socratic_questions": [
            "Show Organic Cash Flow by segment after fully deducting lease liabilities, spectrum installments, and capitalized subscriber installation labor.",
            "In our Enterprise B2B division, what is standalone gross margin on new Cloud/Integration contracts once legacy MPLS runoff is stripped out?",
            "Why are we running parallel copper and fiber exchanges in zones with >80% FTTH coverage—what blocks accelerating switch-off by 18 months?",
            "Does retaining 100% of passive TowerCo/FiberCo equity beat monetizing a minority stake at 18x EBITDAaL to retire debt or buy back shares at 5x?",
        ],
        "ai_value_directives": [
            "Deploy autonomous RAN/Grid sleep-mode energy optimization and predictive field-dispatch swarms to cut network OpEx & truck-rolls 15-20%.",
            "Re-engineer B2B service delivery, quote-to-cash, and MSSP/SOC Tier-1/2 operations with AI agent pods to expand B2B EBITDAaL margin >=400 bps.",
            "Use churn-propensity & household value-tier AI to replace blanket promotional discounting with surgical ARPU retention.",
        ],
        "edges": [
            {"target": "telecom_chief_technology_officer", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "eCapEx Intensity, Copper/Legacy Switch-Off & Network Energy Audit", "protocol": "Gates network CapEx tranches on homes-connected yield and legacy node shutdown milestones."},
            {"target": "telecom_chief_network_architect", "edge_type": "OVERSEES_AND_ADVISES", "artifact": "5G SA / FTTH / Cloud-RAN Architecture & Vendor Lock-In Review", "protocol": "Audits TCO per GB, multi-vendor Open/Cloud RAN economics, and resilience."},
            {"target": "energy_chief_transition_officer", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "Grid Interconnect, PPA Hedging & BESS Rate-Base ROIC Dossier", "protocol": "Verifies regulated rate-of-return certainty and UL9540A thermal safety."},
            {"target": "fin_chief_financial_officer", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "Segment SOTP, Organic Cash Flow & TowerCo/Infra Balance-Sheet Model", "protocol": "Polices lease-adjusted leverage (Net Debt/EBITDAaL) and sale-leaseback economics."},
        ],
    },
])

SPECIALIST_GOVERNANCE_ROLE_SPECS.extend([
    # 13. Cleared National Security & Mission-Assurance Board Director
    {
        "id": "gov_role_13",
        "slug": "gov_aerospace_defense_security_director",
        "title": "Cleared National Security & Mission-Assurance Board Director",
        "governance_category": "BOARD_DIRECTOR",
        "committee_type": "Classified National Security (FOCI/Proxy), Mission Assurance & Fixed-Price Program Committee",
        "selected_industries": ["aerospace_defense", "autonomous_robotics", "public_sector_reg"],
        "typical_human_background": (
            "Retired 4-Star Acquisition Commander / Former Deputy Secretary of Defense & Aerospace Prime COO holding "
            "TS/SCI clearance, seasoned in FAR/DFARS fixed-price development traps, DO-178C flight safety, and ITAR/FOCI."
        ),
        "fiduciary_mandate": (
            "Govern classified program execution, Earned Value Management (EAC/CPI/SPI) honesty, fixed-price R&D bid "
            "discipline, flight/mission safety airworthiness, and ITAR/CMMC national-security compliance."
        ),
        "quarterly_review_cadence": [
            "Classified & unclassified program Estimate-at-Completion (EAC) audit on every contract with CPI or SPI < 0.95.",
            "Bid/No-Bid gate review prohibiting uncapped firm-fixed-price (FFP) bids on immature TRL < 6 development.",
            "Flight/launch safety, DO-178C/DO-254 verification independence, and quality-escape root-cause review.",
            "DCSA FOCI mitigation, ITAR export-control, CMMC 2.0, and single-source sub-tier defense supplier audit.",
        ],
        "kpi_value_tree": {
            "Program_EAC_Integrity": "Cost Performance Index (CPI), Schedule Performance Index (SPI) & cumulative EAC charge ratio",
            "Backlog_Cash_Conversion": "Funded backlog coverage, progress-payment milestone velocity & unbilled receivable aging",
            "Mission_Flight_Assurance": "Zero flight-critical safety escapes, weld/avionics non-conformances, or FAA/DoD groundings",
            "Bid_Margin_Realization": "Realized production margin vs. bid underwriting across Cost-Plus and Fixed-Price transitions",
        },
        "red_flag_triggers": [
            "Signing Firm-Fixed-Price (FFP) development contracts withfixed production options to 'win strategic franchise'—creating multi-billion forward losses.",
            "Program managers masking schedule slips by re-baselining Earned Value Management (EVM) milestones without customer funding.",
            "Engineering safety/quality inspectors reporting to schedule-driven manufacturing VPs instead of an independent Chief Engineer.",
            "Sub-tier specialty castings, energetics, or radiation-hardened microelectronics bottlenecks stalling final assembly.",
        ],
        "socratic_questions": [
            "List every fixed-price development or LRIP contract in our backlog—what is worst-case forward loss if schedule slips 12 months?",
            "Does our Chief Engineer / Mission Assurance Lead hold an unoverridable stop-launch veto independent of program P&L pressure?",
            "Where has unbilled contract work-in-process grown because technical milestones failed government acceptance testing?",
            "Which sub-tier suppliers have sole-source status or foreign-ownership vulnerabilities across our top 5 programs?",
        ],
        "ai_value_directives": [
            "Deploy digital-twin MBSE, automated DO-178C test-case generation, and NDT weld-inspection vision AI with deterministic human sign-off.",
            "Enforce air-gapped sovereign IL5/IL6 deployment for all engineering and proposal AI swarms handling CUI/ITAR data.",
            "Use sub-tier supply-chain telemetry AI to detect casting/avionics delinquency 6 months before factory line-stop.",
        ],
        "edges": [
            {"target": "aero_skunk_works_program_director", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "Program EAC/CPI/SPI Ledger & Fixed-Price Bid Risk Gate", "protocol": "Blocks uncapped FFP development bids and audits forward-loss reserves."},
            {"target": "aero_do178c_do254_avionics_auditor", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "Independent Airworthiness, Safety Escape & Verification Audit", "protocol": "Protects independent engineering stop-work authority."},
            {"target": "aero_lead_launch_director_operations", "edge_type": "OVERSEES_AND_ADVISES", "artifact": "Flight Readiness Review (FRR) & Anomaly Closure Dossier", "protocol": "Audits launch/flight anomaly root-cause closure against schedule fever."},
            {"target": "cyber_fedramp_high_compliance_director", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "CMMC 2.0, ITAR Export Control & Classified enclave Security Audit", "protocol": "Verifies zero unauthorized sovereign/defense tech transfer."},
        ],
    },
    # 14. Manufacturing Yield, Process Safety & Supply-Chain Resilience Auditor
    {
        "id": "gov_role_14",
        "slug": "gov_industrial_supply_chain_quality_auditor",
        "title": "Manufacturing Yield, Process Safety & Supply-Chain Resilience Auditor",
        "governance_category": "INDEPENDENT_AUDITOR",
        "committee_type": "Operations Quality, Lean/Andon Assurance, Process Safety & Multi-Tier Supply Chain Audit",
        "selected_industries": ["semiconductors_mfg", "global_logistics", "autonomous_robotics", "energy_grids"],
        "typical_human_background": (
            "Former Toyota Production System (TPS) Master Sensei & Global Supply-Chain Risk Partner with 25+ years "
            "auditing factory First-Pass Yield, OSHA/EPA process safety, inventory bullwhip distortions, and N-tier resilience."
        ),
        "fiduciary_mandate": (
            "Audit physical shop-floor/warehouse reality against ERP fiction: verify First-Pass Yield, warranty/recall "
            "reserves, working-capital inventory obsolescence, process safety, and multi-tier geopolitical choke points."
        ),
        "quarterly_review_cadence": [
            "Gemba physical plant & warehouse walk: audit First-Pass Yield, scrap/rework hidden factories, and Andon cord pulls.",
            "Inventory quality & DIO aging tear-down separating salable buffer stock from obsolete/slow-moving write-down risk.",
            "Sub-tier (Tier-2/3/4) bill-of-materials single-point-of-failure (rare earths, substrates, maritime lanes) stress-test.",
            "Process Safety Management (PSM), arc-flash/thermal hazard, and warranty/recall accrual adequacy audit.",
        ],
        "kpi_value_tree": {
            "First_Pass_Yield_And_COPQ": "True First-Pass Yield (FPY %) & Cost of Poor Quality (scrap + rework + warranty % of sales)",
            "Cash_Conversion_Cycle": "DIO / DSO / DPO velocity, inventory turns & slow/obsolete reserve coverage",
            "Time_To_Recover_TTR": "Days to restore output if primary Tier-1/Tier-2 region, fab, or port closes for 60 days",
            "Process_Safety_Integrity": "Tier-1/Tier-2 process safety incident rate (TRIR/PSIR) & preventive maintenance compliance",
        },
        "red_flag_triggers": [
            "Gross margin propped up by over-producing into finished-goods inventory (absorbing fixed overhead onto balance sheet).",
            "Deferring preventive equipment maintenance or silencing factory Andon stops to hit quarter-end shipment volume.",
            "Simultaneous supplier concentration where multiple 'dual-source' Tier-1s secretly rely on the exact same Tier-2 plant.",
            "Warranty claims and field failure rates rising faster than warranty reserve accruals.",
        ],
        "socratic_questions": [
            "How much of this quarter's gross-margin beat came from inventory build absorbing fixed factory overhead rather than sell-through?",
            "Map our top 10 revenue products down to Tier-3 raw materials—where does a single country quota, tariff, or factory fire halt >25% of revenue?",
            "Show overdue safety-critical maintenance work orders across all plants and fleet assets—where are we borrowing margin from future outages?",
            "Reconcile field return telemetry over the last 6 months against our balance-sheet warranty reserve accrual.",
        ],
        "ai_value_directives": [
            "Deploy computer-vision inline metrology/defect detection and predictive maintenance AI to cut unplanned downtime & scrap >=25%.",
            "Build N-tier supply-chain knowledge-graph & tariff/port-shock simulation swarms tied directly to S&OP working-capital buffers.",
            "Automate warehouse slotting, route optimization, and customs documentation while enforcing hard physical safety interlocks.",
        ],
        "edges": [
            {"target": "scm_chief_supply_chain_officer", "edge_type": "AUDITS_STRATEGIC_AND_AI_PERFORMANCE", "artifact": "N-Tier BOM Single-Point-of-Failure & Inventory Aging Audit", "protocol": "Stress-tests tail contagion, tariff/quota shocks, and obsolete stock reserves."},
            {"target": "mfg_lead_quality_control_metrology_eng", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "First-Pass Yield, Hidden-Factory Rework & Warranty Reserve Verification", "protocol": "Gemba shop-floor audit verifying quality metrics and recall accruals."},
            {"target": "semi_andon_cord_quality_assurance_lead", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "Andon Stop-Line Log & Excursion Root-Cause Audit", "protocol": "Verifies operators retain unpenalized stop-line authority."},
            {"target": "logistics_chief_customs_freight_officer", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "Tariff Classification, Maritime Chokepoint & C-TPAT Compliance Audit", "protocol": "Audits duty/sanctions exposure and freight disruption contingencies."},
        ],
    },
    # 15. Retail, Omnichannel Working-Capital & Brand Equity Director
    {
        "id": "gov_role_15",
        "slug": "gov_retail_consumer_brand_director",
        "title": "Retail, Omnichannel Working-Capital & Brand Equity Director",
        "governance_category": "BOARD_DIRECTOR",
        "committee_type": "Commercial Merchandising, Brand Moat & Omnichannel Economics Committee",
        "selected_industries": ["retail_consumer", "global_logistics"],
        "typical_human_background": (
            "Former Global Omnichannel/Costco-Archetype CEO & Luxury/Consumer Brand Chair with 24+ years governing "
            "same-store traffic vs. ticket, GMROI (Gross Margin Return on Inventory Investment), private-label moats, "
            "and DTC cohort CAC/LTV."
        ),
        "fiduciary_mandate": (
            "Protect brand pricing power and customer trust against promotional drug addiction: audit real traffic-driven "
            "comp sales, GMROI working-capital velocity, fulfillment unit economics, and repeat-cohort retention."
        ),
        "quarterly_review_cadence": [
            "Same-store / organic comp decomposition: separate true foot/digital traffic growth from price inflation.",
            "GMROI, markdown/shrinkage leakage, and seasonal inventory open-to-buy discipline audit.",
            "Omnichannel / e-commerce variable contribution margin audit after shipping, returns, pick-pack, and paid-search CAC.",
            "Brand equity, Net Promoter Score, private-label penetration, and customer repeat-frequency cohort review.",
        ],
        "kpi_value_tree": {
            "Comp_Quality_Mix": "Same-store traffic % + units-per-basket vs. AUR (Average Unit Retail) price hikes",
            "Inventory_GMROI": "Gross Margin $ / Average Inventory Cost & negative/low-day working-capital cycle",
            "True_DTC_Contribution": "Order revenue minus COGS, outbound + return freight, fulfillment labor, payment fees & CAC",
            "Customer_Retention_Moat": "Membership renewal rate (>90%) / 12-month repeat cohort net contribution",
        },
        "red_flag_triggers": [
            "Positive comp-sales headline driven 100% by price increases while customer traffic and unit volumes contract for 3+ quarters.",
            "Growing e-commerce top-line where every incremental shipped order loses money after return rates and paid digital CAC.",
            "Cutting store labor, product quality, or craftsmanship to hit short-term EPS—silently liquidating decades of brand trust.",
            "Channel stuffing wholesale distributors at quarter-end followed by heavy markdown allowances next quarter.",
        ],
        "socratic_questions": [
            "Decompose our +4% comp growth into transactions, units per basket, and price—are we serving more customers or squeezing fewer loyal ones?",
            "What is the fully loaded contribution margin of our bottom quartile of SKUs and e-commerce orders after returns and paid acquisition?",
            "Where have we quietly degraded material specs, portion sizes, or store service levels to pad gross margin—and what do repeat cohorts show?",
            "Why is inventory growing 14% YoY when forward unit demand is projected at +3%—what markdown hit is sitting in warehouses?",
        ],
        "ai_value_directives": [
            "Deploy SKU-store demand sensing, dynamic markdown optimization, and automated replenishment to lift GMROI and cut stockouts >=20%.",
            "Use personalized lifecycle merchandising and AI customer-service resolution while banning dark-pattern subscription traps.",
            "Automate fulfillment robotics orchestration and return-fraud triage to turn omnichannel unit economics structurally cash-positive.",
        ],
        "edges": [
            {"target": "retail_chief_merchant_costco", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "SKU Rationalization, GMROI & Price-Value Guardrail Review", "protocol": "Polices merchandising discipline, margin caps, and inventory open-to-buy."},
            {"target": "retail_lead_private_label_product_director", "edge_type": "OVERSEES_AND_ADVISES", "artifact": "Private-Label Quality, Margin Spread & Supplier Concentration Dossier", "protocol": "Audits brand quality benchmarks and gross-margin accretion."},
            {"target": "retail_director_fulfillment_center_robotics", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "Fulfillment Automation CapEx Payback & Cost-Per-Order Waterfall", "protocol": "Verifies pick-pack-ship unit-cost savings vs. robotics CapEx."},
            {"target": "sales_chief_revenue_officer", "edge_type": "AUDITS_STRATEGIC_AND_AI_PERFORMANCE", "artifact": "Cohort Repeat Retention, CAC Payback & Wholesale Channel Health", "protocol": "Blocks channel stuffing and unprofitable paid-CAC growth."},
        ],
    },
])

SPECIALIST_GOVERNANCE_ROLE_SPECS.extend([
    # 16. Film Studio, IP Slate & Creator-Economy Venture Board Partner
    {
        "id": "gov_role_16",
        "slug": "gov_media_creator_venture_board_partner",
        "title": "Film Studio, IP Slate & Creator-Economy Venture Board Partner",
        "governance_category": "BOARD_DIRECTOR",
        "committee_type": "Slate Greenlight, Content Amortization, Creator Packaging & IP Monetization Committee",
        "selected_industries": ["creative_media", "retail_consumer", "technology_ai"],
        "typical_human_background": (
            "Lead Media/Creator Venture Partner & Independent Film Studio Board Member (A24 / Blumhouse / Beast-Scale "
            "Creator Studio & Entertainment Finance veteran) with 20+ years governing micro-budget slate downside caps, "
            "ASC 926 film/content amortization, YouTube CTR/AVD retention economics, and owned-IP commerce diversification."
        ),
        "fiduciary_mandate": (
            "Enforce Blumhouse/A24-grade greenlight downside caps, police ASC 926 content-cost capitalization & ultimate-revenue "
            "write-downs, audit organic long-form retention vs. paid/Shorts vanity views, and govern creator/commerce working capital."
        ),
        "quarterly_review_cadence": [
            "Slate Greenlight & Pre-Sales Coverage Audit: verify foreign pre-sales + tax credits cover >=65-80% of negative cost before shoot.",
            "ASC 926 Content Amortization & Ultimate-Revenue Forecast Tear-Down: force immediate write-downs on underperforming titles/formats.",
            "Channel & Audience Cohort Audit: separate organic long-form CTR, 0-30s hook survival & AVD from paid-boosted or low-RPM Shorts vanity views.",
            "Creator/Talent Key-Person Concentration, Sponsor Concentration & Consumer Product/Merch Inventory GMROI review.",
        ],
        "kpi_value_tree": {
            "Slate_Cash_On_Cash_ROIC": "Unlevered post-recoupment cash IRR per title/show net of P&A, residuals & production overhead",
            "Packaging_And_Retention_Health": "Organic Browse/Suggested CTR (%), 30-second survival (>70%), AVD, and RPM/CPM net yield",
            "Amortization_Conservatism": "1st-year ASC 926 content amortization % vs. actual cash decay curve of views/licensing",
            "IP_Diversification_Margin": "Contribution margin of memberships, licensing, dubbing & consumer products net of inventory risk",
        },
        "red_flag_triggers": [
            "Capitalizing routine creator/production payroll onto the balance sheet under multi-year 'library amortization' when 90% of YouTube/social revenue lands in 30 days.",
            "Greenlighting >$20M ego projects or mega-set builds before packaging (Title/Thumbnail/Concept) or pre-sales validate audience demand.",
            "Headline 'Billions of Monthly Views' masking collapsing long-form AVD/RPM via zero-margin vertical Shorts inflation.",
            "Launching founder-led CPG/merch lines with massive minimum-order-quantity (MOQ) inventory commitments and negative cash flow.",
        ],
        "socratic_questions": [
            "If we expense 85% of digital episode production costs in Month 1 matching actual view decay instead of capitalizing over 36 months, what is real GAAP EBITDA?",
            "Show organic long-form Impressions, CTR, and 30-second retention over the last 12 releases excluding Shorts and paid promotion—is audience pull strengthening or fatiguing?",
            "Before committing $8M to this tentpole shoot, what pre-sales, tax incentives, or brand integrations cap our net cash at risk below $2M?",
            "What happens to studio revenue within 90 days if the lead on-camera founder/talent takes a 6-month hiatus or top 2 sponsors churn?",
        ],
        "ai_value_directives": [
            "Mandate AI pre-visualization, title/thumbnail packaging simulation, and multilingual dubbing/localization (12+ languages at >75% margin).",
            "Deploy automated script-retention pacing diagnostics and rough-cut transcript editing swarms so lean pods ship 2-3x creative iterations.",
            "Protect authentic human creative voice & audience trust: ban low-effort synthetic slop that erodes channel browse CTR and brand equity.",
        ],
        "edges": [
            {"target": "creator_channel_showrunner_creative_director", "edge_type": "OVERSEES_AND_ADVISES", "artifact": "Quarterly Format Retention, Creative Burnout & Showrunner Bench Review", "protocol": "Audits show format longevity, host diversification, and production cadence."},
            {"target": "creator_youtube_head_of_ideation_packaging", "edge_type": "AUDITS_STRATEGIC_AND_AI_PERFORMANCE", "artifact": "Pre-Shoot Packaging Validation, Organic CTR & 0-30s Hook Telemetry", "protocol": "Enforces packaging-first gate prior to expensive physical production."},
            {"target": "media_indie_film_line_producer_upm", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "Slate Negative-Cost Cap, Tax-Credit/Pre-Sale Coverage & ASC 926 Schedule", "protocol": "Caps per-project cash downside and polices production cost capitalization."},
            {"target": "creator_brand_partnerships_monetization_lead", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "Sponsor Concentration, Membership LTV & Merch Working-Capital Audit", "protocol": "Prevents inventory bloat in creator CPG/merch and diversifies monetization."},
        ],
    },
    # 17. Independent Climate, Energy-Transition & Works-Council / Labor Auditor
    {
        "id": "gov_role_17",
        "slug": "gov_esg_climate_labor_governance_auditor",
        "title": "Independent Climate, Energy-Transition & Works-Council/Labor Auditor",
        "governance_category": "INDEPENDENT_AUDITOR",
        "committee_type": "Sustainability Assurance (CSRD/ISSB), Decarbonization CapEx & European/Global Labor Compact Audit",
        "selected_industries": ["energy_grids", "telecommunications", "global_logistics", "retail_consumer", "public_sector_reg"],
        "typical_human_background": (
            "Independent CSRD/ISSB Statutory Sustainability Assurance Partner & European Works-Council / Industrial "
            "Relations Mediator with 22+ years auditing Scope 1/2/3 inventories, greenwashing claims, OSHA human-capital "
            "safety, and unionized workforce restructuring transitions."
        ),
        "fiduciary_mandate": (
            "Verify physical MWh/tonnage decarbonization economics (separating ROIC-positive energy reduction from unverified "
            "offset greenwashing), attest CSRD/ISSB disclosures, and audit labor/works-council execution risk during AI & legacy shifts."
        ),
        "quarterly_review_cadence": [
            "Limited/Reasonable Assurance audit of Scope 1, 2 (market vs. location) & material Scope 3 emissions and kWh/unit.",
            "Greenwashing & carbon-offset litigation scrub: reconcile public Net-Zero pledges against funded engineering CapEx.",
            "Workforce safety (LTIR/fatalities), attrition, union/works-council consultation timelines, and AI reskilling audit.",
            "Supply-chain forced-labor (UFLPA / EU CSDDD) and conflict-mineral traceability audit.",
        ],
        "kpi_value_tree": {
            "Physical_Energy_Efficiency": "MWh / petabyte, kWh / wafer, or fuel / ton-km reduction & hard OpEx €/$ saved",
            "Transition_CapEx_Credibility": "% of pledged 2030 decarbonization backed by IRR-positive funded engineering projects",
            "Human_Capital_Stability": "High-performer retention %, works-council agreement velocity & Lost-Time Injury Rate",
            "Supply_Chain_Provenance": "% of high-risk Tier-1/2 suppliers passing independent on-site labor & EHS audits",
        },
        "red_flag_triggers": [
            "Public 'Carbon Neutral' marketing reliant on cheap junk Voluntary Carbon Offsets rather than physical energy/grid reduction.",
            "Transformation/copper-shutdown/AI savings forecast ignores statutory European Works Council consultation timelines and severance cash.",
            "Spike in warehouse/plant injury rates or contractor misclassification masking labor cost cuts.",
            "Unverified Scope 3 supplier estimates copied from industry averages while claiming precision sustainability leadership.",
        ],
        "socratic_questions": [
            "Strip out purchased RECs and carbon offsets—did our physical MWh and Scope 1+2 emissions per unit of output rise or fall this quarter?",
            "Does our 18-month AI & network restructuring plan realistically budget the cash severance, retraining, and works-council negotiation timeline?",
            "Which public environmental claims in our annual report or consumer packaging lack auditable primary-data backing?",
            "Where in our Tier-2/Tier-3 supply chain could a UFLPA customs detention halt product imports tomorrow?",
        ],
        "ai_value_directives": [
            "Account explicitly for AI cluster electricity & water footprint while deploying AI to optimize building HVAC, fleet routing, and RAN/grid sleep modes.",
            "Co-design transparent AI augmentation & internal mobility compacts with workforce representatives to avoid strike paralysis.",
            "Automate primary utility-bill and supplier ERP data ingestion for audit-grade CSRD/ISSB reporting instead of manual spreadsheet consultants.",
        ],
        "edges": [
            {"target": "exec_vp_esg_sustainability", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "CSRD/ISSB Statutory Emissions Inventory & Anti-Greenwashing Verification", "protocol": " Substantive primary-meter and PPA vouching; blocks unsubstantiated offset claims."},
            {"target": "legal_dir_ehs_compliance", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "OSHA/EHS Fatality Prevention, Environmental Liability & CSDDD Audit", "protocol": "Audits site safety remediation and environmental remediation reserves."},
            {"target": "hr_chief_human_resources_officer", "edge_type": "OVERSEES_AND_ADVISES", "artifact": "Works-Council Compact, AI Workforce Transition & Safety Scorecard", "protocol": "Stress-tests social/union feasibility and cash restructuring schedules."},
            {"target": "consult_esg_carbon_accounting_auditor", "edge_type": "AUDITS_STRATEGIC_AND_AI_PERFORMANCE", "artifact": "Decarbonization Marginal Abatement Cost Curve (MACC) & Energy ROI", "protocol": "Ranks decarbonization projects by €/$ saved per ton abated."},
        ],
    },
    # 18. Special M&A, Spin-Off, Restructuring & Solvency Director
    {
        "id": "gov_role_18",
        "slug": "gov_special_committee_mna_turnaround_director",
        "title": "Special M&A, Spin-Off, Restructuring & Solvency Director",
        "governance_category": "BOARD_DIRECTOR",
        "committee_type": "Independent Special Transaction, Activist Settlement, Spin-Off & Turnaround Committee Chair",
        "selected_industries": ["professional_services", "finance_quant", "creative_media", "telecommunications", "retail_consumer"],
        "typical_human_background": (
            "Veteran Delaware Special Committee Chair, Restructuring Turnaround CRO/Director & M&A Fairness Advisor "
            "with 25+ years governing conflicted MBO/take-privates (*MFW*/*Entire Fairness*), tax-free spin-offs, "
            "13-week cash-burn liquidity turnarounds, and distressed debt exchanges."
        ),
        "fiduciary_mandate": (
            "Chair independent Special Committees with unconflicted legal/financial advisors; police M&A synergy fantasy, "
            "execute value-unlocking spin-offs/carve-outs, and enforce 13-week cash-survival discipline in turnarounds."
        ),
        "quarterly_review_cadence": [
            "13-Week Direct Cash-Flow Forecast & Liquidity Runway audit (weekly receipts vs. disbursements in stressed situations).",
            "Independent M&A / Spin-Off / Carve-Out evaluation against standalone DCF and undisturbed market alternatives.",
            "Conflicted transaction (*Revlon* / *MFW* / controller related-party) procedural independence & fairness audit.",
            "Turnaround zero-based cost reset, stranded corporate-overhead elimination, and covenant renegotiation tracking.",
        ],
        "kpi_value_tree": {
            "Standalone_vs_Transaction_NPV": "Risk-adjusted Net Present Value per share of sale/spin-off vs. status-quo execution",
            "Thirteen_Week_Liquidity_Headroom": "Minimum weekly unrestricted cash + undrawn committed revolver net of springing covenants",
            "Carve_Out_Stranded_Cost_Elimination": "% of dis-synergies and stranded parent corporate overhead eliminated within 12 months",
            "Synergy_Realization_Honesty": "Verified run-rate cash cost synergies minus cash restructuring outlays vs. deal pitch",
        },
        "red_flag_triggers": [
            "CEO/management steers a sale process toward a favored private-equity buyer offering management rollover equity while chilling strategic bidders.",
            "Investment bank fairness opinion relies on sudden downward revisions to management's standalone projections to make a lowball bid look fair.",
            "Acquirer underwrites 'revenue synergies' to justify paying >14x EBITDA while pushing pro-forma leverage above 4.5x.",
            "Spin-off or divestiture leaves parent company with 100% of legacy shared-services overhead ('stranded costs') and pension liabilities.",
        ],
        "socratic_questions": [
            "Compare management's standalone 5-year projections in today's fairness deck against the strategic plan presented to this Board 6 months ago—why did terminal EBITDA drop 20%?",
            "Show our 13-week direct cash-flow receipts and disbursements assuming zero revolver extensions and a 15% customer/advertising downturn.",
            "If we spin off our high-growth jewel (e.g., Cyberdefense or Studio IP), how do we eliminate $150M of stranded parent corporate overhead on Day 1?",
            "What exact management rollover, change-of-control golden parachute, or advisor contingency fee creates a conflict of interest in this transaction?",
        ],
        "ai_value_directives": [
            "Use clean-room AI contract extraction (change-of-control clauses, customer assignments, TSA schedules) to cut M&A/carve-out legal cost & timeline 50%.",
            "Deploy zero-based SG&A and working-capital collection AI swarms during turnarounds to unlock immediate cash within 90 days.",
            "Audit target-company AI technical debt, open-source/IP contamination, and customer churn velocity before signing any LOI.",
        ],
        "edges": [
            {"target": "exec_chief_executive_officer", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "Strategic Alternatives, Spin-Off SOTP & Turnaround Mandate", "protocol": "Independent Special Committee authority to say 'No' to empire-building or conflicted deals."},
            {"target": "exec_head_corp_dev_ma", "edge_type": "CHALLENGES_CAPITAL_ALLOCATION", "artifact": "M&A Process Bid Log, Synergy Haircut & Carve-Out TSA Plan", "protocol": "Polices auction fairness, synergy realism, and stranded-cost removal."},
            {"target": "fin_corporate_treasurer", "edge_type": "ATTESTS_FINANCIAL_CONTROLS", "artifact": "13-Week Direct Cash Forecast, Solvency & Covenant Springing-Test Model", "protocol": "Weekly/quarterly cash-conservation gate in leveraged or turnaround regimes."},
            {"target": "legal_chief_legal_officer", "edge_type": "OVERSEES_AND_ADVISES", "artifact": "Delaware Revlon / MFW Special Committee Charter & Conflict Disclosure Log", "protocol": "Ensures strict procedural independence and conflict sanitization."},
        ],
    },
])
