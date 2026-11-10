#!/usr/bin/env python3
"""Independent Board & Audit Committee Forensic and Capital Allocation Analysis.

Entity: EuroNet Cloud & Fiber S.A. (Case 1 — Q4 / FY2026 Board Review)
Performs IAS 38 / IAS 16 & IAS 7 / IFRS 7 restatements, Clause 22.4 Senior RCF
covenant compliance testing, DCF / ROIC / Economic Profit valuation of Project
Alpine, and IRR / NPV / 12-month deleveraging modeling of the deferred internal
AI & autonomous copper-decommissioning capital backlog.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Sequence


def compute_pv(cash_flows: Sequence[float], discount_rate: float) -> float:
    """Present value of sequential annual cash flows occurring at t = 1..N."""
    return sum(cf / ((1.0 + discount_rate) ** t) for t, cf in enumerate(cash_flows, start=1))


def compute_irr_pct(cash_flows_t0: Sequence[float], low: float = -0.95, high: float = 5.0) -> float:
    """Exact internal rate of return (%) via bisection on conventional cash flows."""
    def npv_at(rate: float) -> float:
        return sum(cf / ((1.0 + rate) ** t) for t, cf in enumerate(cash_flows_t0))

    lo, hi = low, high
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if npv_at(mid) > 0.0:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi) * 100.0


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    packet_path = (
        base_dir.parents[1]
        / "tasks"
        / "case1_enterprise_board_audit"
        / "financial_and_operational_packet.json"
    )
    with packet_path.open("r", encoding="utf-8") as fh:
        packet = json.load(fh)

    params = packet["corporate_parameters"]
    wacc = float(params["wacc_annual"])
    tax_rate = float(params["effective_tax_rate"])
    rcf_limit_x = float(params["rcf_maintenance_covenant_max_net_debt_to_ebitda"])

    fy25 = packet["income_and_cashflow_summary_eur_m"]["fy2025_audited"]
    fy26 = packet["income_and_cashflow_summary_eur_m"]["fy2026_unaudited_management"]
    bs = packet["balance_sheet_debt_and_liquidity_eur_m"]
    notes = packet["unaudited_accounting_and_treasury_footnotes"]

    # 1. IAS 38.57 / IAS 16 OpEx Capitalization Reversal & True Normalized EBITDA
    reported_ebitda = float(fy26["reported_adjusted_ebitda"])
    fy25_ebitda = float(fy25["reported_adjusted_ebitda"])
    cap_opex_reversal = float(
        notes["note_7_aurora_capitalization_policy_change"]["total_reclassified_from_opex_to_ecapex_eur_m"]
    )
    true_ebitda = reported_ebitda - cap_opex_reversal
    true_ebitda_yoy_pct = ((true_ebitda - fy25_ebitda) / fy25_ebitda) * 100.0

    # 2. IAS 7 / IFRS 7 Supplier Reverse Factoring OCF Distortion & Underlying FCF
    # Reversing Note 7 reduces both OCF and eCapEx by EUR 310.0M (FCF-neutral);
    # Reversing Note 11 reclassifies EUR 160.0M YoY novated bank inflow from OCF to CFF.
    fy25_fcf = float(fy25["free_cash_flow"])
    reported_fcf = float(fy26["free_cash_flow_reported"])
    reported_fcf_yoy_pct = ((reported_fcf - fy25_fcf) / fy25_fcf) * 100.0
    rf_ocf_distortion = float(
        notes["note_11_supplier_reverse_factoring_program"][
            "net_yoy_working_capital_cash_inflow_booked_in_ocf_eur_m"
        ]
    )
    true_ocf = float(fy26["operating_cash_flow_reported"]) - cap_opex_reversal - rf_ocf_distortion
    true_ecapex = float(fy26["ecapex_reported"]) - cap_opex_reversal
    true_fcf = true_ocf - true_ecapex

    # 3. Net Debt Restatement & Senior RCF Clause 22.4 Covenant Compliance
    reported_net_debt = float(bs["net_debt_reported"])
    rf_debt_reclass = float(notes["note_11_supplier_reverse_factoring_program"]["facility_balance_fy2026_eur_m"])
    true_net_debt = reported_net_debt + rf_debt_reclass
    reported_net_leverage_x = reported_net_debt / reported_ebitda
    true_net_leverage_x = true_net_debt / true_ebitda
    covenant_breached_pre_mna = bool(true_net_leverage_x > rcf_limit_x)

    # 4. Project Alpine M&A Valuation (ROIC vs. WACC, DCF PV/NPV, Pro-Forma Leverage)
    alpine = packet["project_alpine_mna_due_diligence_schedule"]
    alpine_ev = float(alpine["purchase_enterprise_value_eur_m"])
    alpine_new_debt = float(alpine["new_acquisition_debt_eur_m"])
    alpine_ltm_ebitda = float(alpine["target_ltm_ebitda_eur_m"])
    alpine_risks = alpine["business_mix_and_risk_findings"]
    alpine_econ = alpine["independent_steady_state_economics_eur_m"]

    pro_forma_mna_net_leverage_x = (true_net_debt + alpine_new_debt) / (true_ebitda + alpine_ltm_ebitda)
    alpine_nopat = float(alpine_econ["normalized_nopat_eur_m"])
    alpine_roic_pct = (alpine_nopat / alpine_ev) * 100.0

    alpine_fcfs = [float(x) for x in alpine_econ["explicit_unlevered_fcf_years_1_to_5_eur_m"]]
    alpine_tv_y5 = float(alpine_econ["year_6_terminal_unlevered_fcf_eur_m"]) / (
        wacc - float(alpine_econ["perpetual_terminal_growth_rate"])
    )
    alpine_pv = compute_pv(alpine_fcfs, wacc) + alpine_tv_y5 / ((1.0 + wacc) ** 5)
    alpine_npv = alpine_pv - alpine_ev
    fully_loaded_cost = (
        alpine_ev
        + float(alpine_risks["unfunded_ias19_pension_and_works_council_liability_eur_m"])
        + float(alpine_risks["required_integration_and_severance_outlay_eur_m"])
    )
    mna_board_vote = "REJECT" if (alpine_npv < 0.0 or pro_forma_mna_net_leverage_x > rcf_limit_x) else "APPROVE"

    # 5. Internal AI & Copper-Decommissioning Capital Redeployment Backlog
    backlog = packet["deferred_internal_ai_and_infra_redeployment_backlog"]
    init_a = backlog["initiative_a_autonomous_copper_decommissioning"]
    init_b = backlog["initiative_b_agentic_soc_and_sdwan_swarms"]

    capex_a = float(init_a["upfront_capex_eur_m"])
    cfs_a = [float(x) for x in init_a["annual_after_tax_cash_savings_years_1_to_5_eur_m"]]
    cfs_a[-1] += float(init_a["salvage_copper_and_real_estate_release_year_5_eur_m"])

    capex_b = float(init_b["upfront_capex_eur_m"])
    cfs_b = [float(x) for x in init_b["annual_after_tax_cash_uplift_years_1_to_5_eur_m"]]
    cfs_b[-1] += float(init_b["terminal_value_year_5_conservative_eur_m"])

    total_ai_capex = capex_a + capex_b
    blended_cfs_1_to_5 = [a + b for a, b in zip(cfs_a, cfs_b)]
    blended_irr_pct = compute_irr_pct([-total_ai_capex, *blended_cfs_1_to_5])
    blended_npv = compute_pv(blended_cfs_1_to_5, wacc) - total_ai_capex

    # 12-month post-redeployment deleveraging trajectory (self-funded from organic FCF + Y1 AI savings)
    y1_after_tax_uplift = blended_cfs_1_to_5[0]
    y1_pre_tax_ebitda_uplift = y1_after_tax_uplift / (1.0 - tax_rate)
    post_12m_net_debt = true_net_debt + total_ai_capex - true_fcf - y1_after_tax_uplift
    post_12m_ebitda = true_ebitda + y1_pre_tax_ebitda_uplift
    post_redeployment_12m_net_leverage_x = post_12m_net_debt / post_12m_ebitda

    findings = {
        "reported_ebitda_eur_m": round(reported_ebitda, 2),
        "capitalized_opex_reversal_eur_m": round(cap_opex_reversal, 2),
        "true_normalized_ebitda_eur_m": round(true_ebitda, 2),
        "true_ebitda_yoy_pct": round(true_ebitda_yoy_pct, 2),
        "reported_fcf_eur_m": round(reported_fcf, 2),
        "reported_fcf_yoy_pct": round(reported_fcf_yoy_pct, 2),
        "reverse_factoring_ocf_distortion_eur_m": round(rf_ocf_distortion, 2),
        "true_underlying_fcf_eur_m": round(true_fcf, 2),
        "reported_net_debt_eur_m": round(reported_net_debt, 2),
        "reverse_factoring_debt_reclass_eur_m": round(rf_debt_reclass, 2),
        "true_adjusted_net_debt_eur_m": round(true_net_debt, 2),
        "reported_net_leverage_x": round(reported_net_leverage_x, 2),
        "true_adjusted_net_leverage_x": round(true_net_leverage_x, 2),
        "rcf_covenant_limit_x": round(rcf_limit_x, 2),
        "covenant_breached_pre_mna": covenant_breached_pre_mna,
        "pro_forma_mna_net_leverage_x": round(pro_forma_mna_net_leverage_x, 2),
        "project_alpine_roic_pct": round(alpine_roic_pct, 2),
        "company_wacc_pct": round(wacc * 100.0, 2),
        "project_alpine_pv_eur_m": round(alpine_pv, 2),
        "project_alpine_npv_eur_m": round(alpine_npv, 2),
        "mna_board_vote": mna_board_vote,
        "internal_ai_infra_total_capex_eur_m": round(total_ai_capex, 2),
        "internal_ai_infra_blended_irr_pct": round(blended_irr_pct, 2),
        "internal_ai_infra_npv_eur_m": round(blended_npv, 2),
        "post_redeployment_12m_net_leverage_x": round(post_redeployment_12m_net_leverage_x, 2),
        "supporting_schedules": {
            "restated_ocf_eur_m": round(true_ocf, 2),
            "restated_ecapex_eur_m": round(true_ecapex, 2),
            "true_fcf_yoy_pct_vs_fy25_reported": round(((true_fcf - fy25_fcf) / fy25_fcf) * 100.0, 2),
            "project_alpine_fully_loaded_cost_eur_m": round(fully_loaded_cost, 2),
            "project_alpine_fully_loaded_roic_pct": round((alpine_nopat / fully_loaded_cost) * 100.0, 2),
            "project_alpine_fully_loaded_npv_eur_m": round(alpine_pv - fully_loaded_cost, 2),
            "project_alpine_fully_loaded_leverage_x": round(
                (true_net_debt + fully_loaded_cost) / (true_ebitda + alpine_ltm_ebitda), 2
            ),
            "initiative_a_npv_eur_m": round(compute_pv(cfs_a, wacc) - capex_a, 2),
            "initiative_a_irr_pct": round(compute_irr_pct([-capex_a, *cfs_a]), 2),
            "initiative_b_npv_eur_m": round(compute_pv(cfs_b, wacc) - capex_b, 2),
            "initiative_b_irr_pct": round(compute_irr_pct([-capex_b, *cfs_b]), 2),
            "post_redeployment_12m_net_debt_eur_m": round(post_12m_net_debt, 2),
            "post_redeployment_12m_ebitda_eur_m": round(post_12m_ebitda, 2),
            "post_redeployment_12m_leverage_ungrossed_cash_basis_x": round(
                post_12m_net_debt / (true_ebitda + y1_after_tax_uplift), 2
            ),
        },
    }

    out_path = base_dir / "findings.json"
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(findings, fh, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main()
