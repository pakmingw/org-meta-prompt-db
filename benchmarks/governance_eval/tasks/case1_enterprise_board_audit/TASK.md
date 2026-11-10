# Board & Audit Committee Review Assignment — Case 1: EuroNet Cloud & Fiber S.A.

## Fiduciary Mandate
You have been convened prior to Friday's Board vote on **EuroNet Cloud & Fiber S.A.** (`management_board_deck.md` and `financial_and_operational_packet.json`). Management reports `+9.4%` YoY Adjusted EBITDA growth (`€2,260.0M`), `2.10x` Net Leverage, `"AI transformation on track"`, and requests binding approval of Resolution `2026-Q4-M&A-01` (`€1,800.0M` debt-funded acquisition of Helvetia Legacy IT Services AG at `11.5x` EBITDA).

Conduct an independent forensic audit, covenant compliance test, capital-allocation valuation (`ROIC` vs. `WACC` & `NPV`), executive-incentive alignment review, and AI/operational capital-redeployment analysis.

## Required Deliverables (Write into Your Assigned Output Directory)
1. **`audit_analysis.py`** (`<= 230` lines): Self-contained Python 3 script (stdlib / `numpy`) that loads `financial_and_operational_packet.json`, performs all forensic accounting reclassifications, RCF covenant calculations, DCF/NPV/ROIC/IRR valuations for both `Project Alpine` and the internal AI/Copper-Decommissioning backlog, and writes **`findings.json`** containing:
   - `reported_ebitda_eur_m`, `capitalized_opex_reversal_eur_m`, `true_normalized_ebitda_eur_m`, `true_ebitda_yoy_pct`
   - `reported_fcf_eur_m`, `reported_fcf_yoy_pct`, `reverse_factoring_ocf_distortion_eur_m`, `true_underlying_fcf_eur_m`
   - `reported_net_debt_eur_m`, `reverse_factoring_debt_reclass_eur_m`, `true_adjusted_net_debt_eur_m`
   - `reported_net_leverage_x`, `true_adjusted_net_leverage_x`, `rcf_covenant_limit_x`, `covenant_breached_pre_mna` (`bool`), `pro_forma_mna_net_leverage_x`
   - `project_alpine_roic_pct`, `company_wacc_pct`, `project_alpine_pv_eur_m`, `project_alpine_npv_eur_m`, `mna_board_vote` (`"APPROVE"` or `"REJECT"`)
   - `internal_ai_infra_total_capex_eur_m`, `internal_ai_infra_blended_irr_pct`, `internal_ai_infra_npv_eur_m`, `post_redeployment_12m_net_leverage_x`
2. **`board_resolution_memo.md`** (`<= 230` lines): Formal Board & Audit Committee Resolution Memo containing: (a) Forensic & Covenant Restatements (`IAS 38`, `IAS 7 / IFRS 7`), (b) Binding Vote & Economic Profit Tear-Down of `Project Alpine`, (c) Compensation Clawback / LTIP Governance Reform, and (d) Quantified AI Subagent Swarm & Copper-Decommissioning Value-Creation Roadmap with quarterly verification gates.

Execute `audit_analysis.py` before finishing so `findings.json` is verified on disk.
