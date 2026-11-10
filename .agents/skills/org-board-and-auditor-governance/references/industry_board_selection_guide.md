# Industry Board of Directors & Independent Auditor Selection Guide

## 1. Universal Fiduciary Foundation (`PUBLIC_ENTERPRISE` vs. `VENTURE_OR_BOUTIQUE`)

Every corporate Board of Directors and Independent Audit Panel in `orgprompt.governance` separates **Operating Management** (`canonical_roles`) from **Fiduciary Oversight** (`governance_roles`):

| Stage | Voting Board Size | Core Universal Seats | Independent External Auditors |
| :--- | :---: | :--- | :--- |
| **`PUBLIC_ENTERPRISE`** (`>=$1.5B` rev / listed) | `8–11` Directors | `gov_lead_independent_board_chair`, `gov_audit_committee_financial_expert_chair` (SOX 407), `gov_capital_allocation_value_director`, `gov_compensation_succession_chair` | `gov_external_statutory_forensic_auditor` (PCAOB/ISA), `gov_independent_strategic_value_auditor` (Outside-In / AI ROI) |
| **`VENTURE_OR_BOUTIQUE`** (`<$1.5B` rev / Studio / Series A–C) | `5` Directors | `gov_lead_independent_board_chair`, `gov_capital_allocation_value_director`, `gov_audit_committee_financial_expert_chair` | `gov_external_statutory_forensic_auditor`, `gov_independent_strategic_value_auditor` |

---

## 2. Sector-Specialist Director & Domain Auditor Mapping (All 16 Macro Industries)

| Macro Industry (`industry_slug`) | Specialist Board Directors Added | Domain Auditors Added | Primary Boardroom Red-Flag Focus |
| :--- | :--- | :--- | :--- |
| **`technology_ai`** | `gov_tech_ai_semiconductor_director`, `gov_special_committee_mna_turnaround_director` | `gov_cybersecurity_ai_safety_board_auditor` | 6yr vs. 3.5yr GPU depreciation, round-trip cloud credit ARR, AI gross margin & safety |
| **`semiconductors_mfg`** | `gov_tech_ai_semiconductor_director`, `gov_aerospace_defense_security_director` | `gov_industrial_supply_chain_quality_auditor` | Leading-edge fab D0 yield, CoWoS/HBM bottlenecks, tool CapEx payback & export controls |
| **`telecommunications`** | `gov_telco_energy_infra_regulatory_director`, `gov_special_committee_mna_turnaround_director` | `gov_cybersecurity_ai_safety_board_auditor`, `gov_esg_climate_labor_governance_auditor` | EBITDAaL vs. Organic Cash Flow, copper/MPLS switch-off, B2B margin drag & TowerCo SOTP |
| **`finance_quant`** | `gov_financial_systemic_risk_chair`, `gov_special_committee_mna_turnaround_director` | `gov_cybersecurity_ai_safety_board_auditor` | Intraday LCR, HTM duration unrealized losses, credit vintage roll-rates & SR 11-7 model risk |
| **`healthcare_biotech`** | `gov_biotech_clinical_scientific_director` | `gov_healthcare_patient_safety_auditor` | Stratified O/E mortality, Simpson's Paradox in clinical AI/SaMD & CMS upcoding compliance |
| **`pharmaceuticals`** | `gov_biotech_clinical_scientific_director`, `gov_special_committee_mna_turnaround_director` | `gov_healthcare_patient_safety_auditor`, `gov_industrial_supply_chain_quality_auditor` | Pre-specified SAP endpoints, patent-cliff M&A rNPV discipline & cGMP sterile fill-finish |
| **`energy_grids`** | `gov_telco_energy_infra_regulatory_director` | `gov_esg_climate_labor_governance_auditor`, `gov_industrial_supply_chain_quality_auditor` | Rate-base ROIC, grid interconnect queues, UL9540A BESS thermal safety & physical MWh reduction |
| **`aerospace_defense`** | `gov_aerospace_defense_security_director`, `gov_tech_ai_semiconductor_director` | `gov_industrial_supply_chain_quality_auditor`, `gov_cybersecurity_ai_safety_board_auditor` | Fixed-price development forward losses, EAC/CPI honesty, DO-178C stop-launch & ITAR/CMMC |
| **`autonomous_robotics`** | `gov_tech_ai_semiconductor_director`, `gov_aerospace_defense_security_director` | `gov_industrial_supply_chain_quality_auditor`, `gov_cybersecurity_ai_safety_board_auditor` | Safety disengagements per million miles, hardware BOM learning curve & OT cyber safety |
| **`cybersecurity`** | `gov_tech_ai_semiconductor_director`, `gov_aerospace_defense_security_director` | `gov_cybersecurity_ai_safety_board_auditor` | Zero-trust blast-radius MTTC, sovereign ANSSI/FedRAMP compliance & autonomous SOC margin |
| **`global_logistics`** | `gov_retail_consumer_brand_director`, `gov_telco_energy_infra_regulatory_director` | `gov_industrial_supply_chain_quality_auditor`, `gov_esg_climate_labor_governance_auditor` | Fleet utilization ROIC, maritime/customs disruption TTR, fuel/safety & working capital |
| **`retail_consumer`** | `gov_retail_consumer_brand_director`, `gov_media_creator_venture_board_partner` | `gov_industrial_supply_chain_quality_auditor`, `gov_esg_climate_labor_governance_auditor` | Traffic vs. ticket comp quality, GMROI inventory turns, true DTC net contribution & brand trust |
| **`creative_media`** *(Public & Indie/Creator)* | `gov_media_creator_venture_board_partner`, `gov_retail_consumer_brand_director` | `gov_cybersecurity_ai_safety_board_auditor` | Blumhouse/A24 negative-cost caps, ASC 926 digital video capitalization, organic CTR/AVD vs. Shorts vanity views & merch MOQ risk |
| **`professional_services`** | `gov_financial_systemic_risk_chair`, `gov_special_committee_mna_turnaround_director` | `gov_cybersecurity_ai_safety_board_auditor` | Partner leverage, AI productized-margin transition, conflict independence & client data hygiene |
| **`frontier_research`** | `gov_tech_ai_semiconductor_director`, `gov_biotech_clinical_scientific_director` | `gov_cybersecurity_ai_safety_board_auditor` | Truth-seeking milestone gates, compute/lab stewardship, reproducibility & dual-use safety |
| **`public_sector_reg`** | `gov_telco_energy_infra_regulatory_director`, `gov_aerospace_defense_security_director` | `gov_cybersecurity_ai_safety_board_auditor`, `gov_esg_climate_labor_governance_auditor` | Sovereign cloud/data residency, procurement integrity, citizen SLA & fiscal accountability |

---

## 3. Typed Fiduciary Oversight Edge Vocabulary (`governance_oversight_edges`)
1. `OVERSEES_AND_ADVISES` — Direct non-executive supervision, agenda setting, and strategic counsel.
2. `CHALLENGES_CAPITAL_ALLOCATION` — Hurdle-rate (`ROIC > WACC`), CapEx/M&A/slate tranche gating, and SOTP challenge.
3. `ATTESTS_FINANCIAL_CONTROLS` — Statutory GAAP/IFRS, SOX 404 ICFR, capitalization, and regulatory safety attestation.
4. `AUDITS_STRATEGIC_AND_AI_PERFORMANCE` — Outside-in cohort unit economics, peer cost benchmark, and verified AI cash ROI audit.
5. `GATES_COMPENSATION_AND_SUCCESSION` — STI/LTI metric integrity, SBC dilution caps, Dodd-Frank clawbacks, and C-suite succession.
