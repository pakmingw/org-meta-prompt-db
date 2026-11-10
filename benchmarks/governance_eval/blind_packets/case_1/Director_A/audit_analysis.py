#!/usr/bin/env python3
"""Forensic Accounting, RCF Covenant & Capital-Allocation Audit — Case 1: EuroNet Cloud & Fiber S.A."""

import json
from pathlib import Path


def compute_npv(rate: float, cash_flows: list[float]) -> float:
    """Compute Net Present Value for cash_flows[0..N] where index 0 is t=0."""
    return sum(cf / ((1.0 + rate) ** t) for t, cf in enumerate(cash_flows))


def compute_irr(cash_flows: list[float], low: float = -0.90, high: float = 5.0, tol: float = 1e-10) -> float:
    """Compute Internal Rate of Return via deterministic bisection."""
    npv_low = compute_npv(low, cash_flows)
    for _ in range(200):
        mid = 0.5 * (low + high)
        npv_mid = compute_npv(mid, cash_flows)
        if abs(npv_mid) < tol:
            return mid
        if npv_low * npv_mid <= 0.0:
            high = mid
        else:
            low = mid
            npv_low = npv_mid
    return 0.5 * (low + high)


def main() -> None:
    run_dir = Path(__file__).resolve().parent
    packet_path = (
        run_dir.parent.parent
        / "tasks"
        / "case1_enterprise_board_audit"
        / "financial_and_operational_packet.json"
    )
    with packet_path.open("r", encoding="utf-8") as fh:
        pkt = json.load(fh)

    params = pkt["corporate_parameters"]
    wacc = float(params["wacc_annual"])
    tax_rate = float(params["effective_tax_rate"])
    rcf_limit_x = float(params["rcf_maintenance_covenant_max_net_debt_to_ebitda"])

    fy25 = pkt["income_and_cashflow_summary_eur_m"]["fy2025_audited"]
    fy26 = pkt["income_and_cashflow_summary_eur_m"]["fy2026_unaudited_management"]
    bs = pkt["balance_sheet_debt_and_liquidity_eur_m"]
    notes = pkt["unaudited_accounting_and_treasury_footnotes"]

    # 1. IAS 38.57 Capitalized Maintenance Reversal & True Normalized EBITDA
    ebitda_fy25 = float(fy25["reported_adjusted_ebitda"])
    reported_ebitda = float(fy26["reported_adjusted_ebitda"])
    cap_opex_reversal = float(
        notes["note_7_aurora_capitalization_policy_change"]["total_reclassified_from_opex_to_ecapex_eur_m"]
    )
    true_normalized_ebitda = reported_ebitda - cap_opex_reversal
    true_ebitda_yoy_pct = ((true_normalized_ebitda - ebitda_fy25) / ebitda_fy25) * 100.0

    # 2. IAS 7 / IFRS 7 Reverse Factoring OCF Distortion & True Underlying FCF
    fcf_fy25 = float(fy25["free_cash_flow"])
    reported_fcf = float(fy26["free_cash_flow_reported"])
    reported_fcf_yoy_pct = ((reported_fcf - fcf_fy25) / fcf_fy25) * 100.0
    rf_note = notes["note_11_supplier_reverse_factoring_program"]
    rf_ocf_distortion = float(rf_note["net_yoy_working_capital_cash_inflow_booked_in_ocf_eur_m"])
    true_normalized_ocf = float(fy26["operating_cash_flow_reported"]) - cap_opex_reversal - rf_ocf_distortion
    true_normalized_ecapex = float(fy26["ecapex_reported"]) - cap_opex_reversal
    true_underlying_fcf = true_normalized_ocf - true_normalized_ecapex
    true_fcf_yoy_pct = ((true_underlying_fcf - fcf_fy25) / fcf_fy25) * 100.0

    # 3. Net Debt Restatement & Senior RCF Clause 22.4 Covenant Test
    reported_net_debt = float(bs["net_debt_reported"])
    rf_debt_reclass = float(rf_note["facility_balance_fy2026_eur_m"])
    true_adjusted_net_debt = reported_net_debt + rf_debt_reclass
    reported_net_leverage_x = reported_net_debt / reported_ebitda
    true_adjusted_net_leverage_x = true_adjusted_net_debt / true_normalized_ebitda
    covenant_breached_pre_mna = bool(true_adjusted_net_leverage_x > rcf_limit_x)

    # 4. Project Alpine M&A Valuation (ROIC vs. WACC, DCF PV/NPV, Pro-Forma Leverage)
    mna = pkt["project_alpine_mna_due_diligence_schedule"]
    alpine_ev = float(mna["purchase_enterprise_value_eur_m"])
    alpine_new_debt = float(mna["new_acquisition_debt_eur_m"])
    alpine_ltm_ebitda = float(mna["target_ltm_ebitda_eur_m"])
    alpine_risk = mna["business_mix_and_risk_findings"]
    alpine_pension = float(alpine_risk["unfunded_ias19_pension_and_works_council_liability_eur_m"])
    alpine_severance = float(alpine_risk["required_integration_and_severance_outlay_eur_m"])
    alpine_all_in_cost = alpine_ev + alpine_pension + alpine_severance

    pro_forma_mna_net_leverage_x = (true_adjusted_net_debt + alpine_new_debt) / (
        true_normalized_ebitda + alpine_ltm_ebitda
    )
    pro_forma_mna_all_in_net_leverage_x = (
        true_adjusted_net_debt + alpine_new_debt + alpine_pension + alpine_severance
    ) / (true_normalized_ebitda + alpine_ltm_ebitda)

    econ = mna["independent_steady_state_economics_eur_m"]
    alpine_nopat = float(econ["normalized_nopat_eur_m"])
    alpine_roic_pct = (alpine_nopat / alpine_ev) * 100.0
    alpine_all_in_roic_pct = (alpine_nopat / alpine_all_in_cost) * 100.0

    explicit_fcfs = [float(x) for x in econ["explicit_unlevered_fcf_years_1_to_5_eur_m"]]
    tv_year5 = float(econ["year_6_terminal_unlevered_fcf_eur_m"]) / (
        float(econ["discount_rate_wacc"]) - float(econ["perpetual_terminal_growth_rate"])
    )
    pv_explicit = sum(cf / ((1.0 + wacc) ** t) for t, cf in enumerate(explicit_fcfs, start=1))
    pv_terminal = tv_year5 / ((1.0 + wacc) ** 5)
    alpine_pv = pv_explicit + pv_terminal
    alpine_npv = alpine_pv - alpine_ev
    alpine_all_in_npv = alpine_pv - alpine_all_in_cost
    mna_board_vote = "APPROVE" if (alpine_npv > 0.0 and alpine_roic_pct > wacc * 100.0) else "REJECT"

    # 5. Internal AI & Copper-Decommissioning Capital Redeployment Valuation
    backlog = pkt["deferred_internal_ai_and_infra_redeployment_backlog"]
    init_a = backlog["initiative_a_autonomous_copper_decommissioning"]
    init_b = backlog["initiative_b_agentic_soc_and_sdwan_swarms"]

    capex_a = float(init_a["upfront_capex_eur_m"])
    cf_a = [-capex_a] + [float(x) for x in init_a["annual_after_tax_cash_savings_years_1_to_5_eur_m"]]
    cf_a[-1] += float(init_a["salvage_copper_and_real_estate_release_year_5_eur_m"])

    capex_b = float(init_b["upfront_capex_eur_m"])
    cf_b = [-capex_b] + [float(x) for x in init_b["annual_after_tax_cash_uplift_years_1_to_5_eur_m"]]
    cf_b[-1] += float(init_b["terminal_value_year_5_conservative_eur_m"])

    total_ai_capex = capex_a + capex_b
    cf_blended = [a + b for a, b in zip(cf_a, cf_b)]
    blended_npv = compute_npv(wacc, cf_blended)
    blended_irr_pct = compute_irr(cf_blended) * 100.0

    # 12-Month Deleveraging Bridge: Organic FCF + Year-1 AI Cash Uplift less Upfront CapEx
    yr1_after_tax_uplift = cf_blended[1]
    yr1_pre_tax_ebitda_uplift = yr1_after_tax_uplift / (1.0 - tax_rate)
    net_debt_12m = true_adjusted_net_debt - true_underlying_fcf + total_ai_capex - yr1_after_tax_uplift
    ebitda_12m = true_normalized_ebitda + yr1_pre_tax_ebitda_uplift
    post_redeployment_12m_net_leverage_x = net_debt_12m / ebitda_12m

    findings = {
        "reported_ebitda_eur_m": round(reported_ebitda, 2),
        "capitalized_opex_reversal_eur_m": round(cap_opex_reversal, 2),
        "true_normalized_ebitda_eur_m": round(true_normalized_ebitda, 2),
        "true_ebitda_yoy_pct": round(true_ebitda_yoy_pct, 2),
        "reported_fcf_eur_m": round(reported_fcf, 2),
        "reported_fcf_yoy_pct": round(reported_fcf_yoy_pct, 2),
        "reverse_factoring_ocf_distortion_eur_m": round(rf_ocf_distortion, 2),
        "true_underlying_fcf_eur_m": round(true_underlying_fcf, 2),
        "reported_net_debt_eur_m": round(reported_net_debt, 2),
        "reverse_factoring_debt_reclass_eur_m": round(rf_debt_reclass, 2),
        "true_adjusted_net_debt_eur_m": round(true_adjusted_net_debt, 2),
        "reported_net_leverage_x": round(reported_net_leverage_x, 2),
        "true_adjusted_net_leverage_x": round(true_adjusted_net_leverage_x, 2),
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
        "supplementary_forensic_detail": {
            "true_fcf_yoy_pct": round(true_fcf_yoy_pct, 2),
            "true_normalized_ocf_eur_m": round(true_normalized_ocf, 2),
            "true_normalized_ecapex_eur_m": round(true_normalized_ecapex, 2),
            "project_alpine_all_in_invested_capital_eur_m": round(alpine_all_in_cost, 2),
            "project_alpine_all_in_roic_pct": round(alpine_all_in_roic_pct, 2),
            "project_alpine_all_in_npv_eur_m": round(alpine_all_in_npv, 2),
            "pro_forma_mna_all_in_net_leverage_x": round(pro_forma_mna_all_in_net_leverage_x, 2),
            "initiative_a_npv_eur_m": round(compute_npv(wacc, cf_a), 2),
            "initiative_a_irr_pct": round(compute_irr(cf_a) * 100.0, 2),
            "initiative_b_npv_eur_m": round(compute_npv(wacc, cf_b), 2),
            "initiative_b_irr_pct": round(compute_irr(cf_b) * 100.0, 2),
            "post_redeployment_12m_net_debt_eur_m": round(net_debt_12m, 2),
            "post_redeployment_12m_ebitda_eur_m": round(ebitda_12m, 2),
        },
    }

    out_path = run_dir / "findings.json"
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(findings, fh, indent=2)


if __name__ == "__main__":
    main()
