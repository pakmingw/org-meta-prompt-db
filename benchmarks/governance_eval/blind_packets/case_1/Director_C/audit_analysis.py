#!/usr/bin/env python3
"""Forensic Audit, Covenant, Capital Allocation & AI Redeployment Valuation — EuroNet Cloud & Fiber S.A."""

import json
from pathlib import Path
from typing import List


def compute_npv(rate: float, cash_flows: List[float]) -> float:
    """Discount cash_flows where index 0 is t=0 and index t is Year t."""
    return sum(cf / ((1.0 + rate) ** t) for t, cf in enumerate(cash_flows))


def compute_irr(cash_flows: List[float], guess: float = 0.25, tol: float = 1e-10, max_iter: int = 200) -> float:
    """Compute Internal Rate of Return via Newton-Raphson with bisection safeguard."""
    low, high = -0.90, 5.00
    r = guess
    for _ in range(max_iter):
        f_val = sum(cf / ((1.0 + r) ** t) for t, cf in enumerate(cash_flows))
        if abs(f_val) < tol:
            return r
        df_val = sum(-t * cf / ((1.0 + r) ** (t + 1)) for t, cf in enumerate(cash_flows) if t > 0)
        if abs(df_val) < 1e-14:
            break
        r_next = r - f_val / df_val
        if r_next <= low or r_next >= high:
            break
        r = r_next
    for _ in range(max_iter):
        mid = 0.5 * (low + high)
        if compute_npv(mid, cash_flows) > 0:
            low = mid
        else:
            high = mid
        if abs(high - low) < tol:
            return 0.5 * (low + high)
    return r


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    packet_path = (
        script_dir.parent.parent
        / "tasks"
        / "case1_enterprise_board_audit"
        / "financial_and_operational_packet.json"
    )
    with packet_path.open("r", encoding="utf-8") as fh:
        pkt = json.load(fh)

    corp = pkt["corporate_parameters"]
    wacc = float(corp["wacc_annual"])
    tax_rate = float(corp["effective_tax_rate"])
    rcf_limit_x = float(corp["rcf_maintenance_covenant_max_net_debt_to_ebitda"])

    fy25 = pkt["income_and_cashflow_summary_eur_m"]["fy2025_audited"]
    fy26 = pkt["income_and_cashflow_summary_eur_m"]["fy2026_unaudited_management"]
    bs = pkt["balance_sheet_debt_and_liquidity_eur_m"]
    notes = pkt["unaudited_accounting_and_treasury_footnotes"]

    # 1. Forensic Accounting Reclassifications (IAS 38.57 & IAS 7 / IFRS 7)
    reported_ebitda = float(fy26["reported_adjusted_ebitda"])
    cap_opex_reversal = float(notes["note_7_aurora_capitalization_policy_change"]["total_reclassified_from_opex_to_ecapex_eur_m"])
    true_ebitda = reported_ebitda - cap_opex_reversal
    true_ebitda_yoy_pct = ((true_ebitda - float(fy25["reported_adjusted_ebitda"])) / float(fy25["reported_adjusted_ebitda"])) * 100.0

    reported_fcf = float(fy26["free_cash_flow_reported"])
    fy25_fcf = float(fy25["free_cash_flow"])
    reported_fcf_yoy_pct = ((reported_fcf - fy25_fcf) / fy25_fcf) * 100.0
    rf_ocf_distortion = float(notes["note_11_supplier_reverse_factoring_program"]["net_yoy_working_capital_cash_inflow_booked_in_ocf_eur_m"])
    true_ocf = float(fy26["operating_cash_flow_reported"]) - cap_opex_reversal - rf_ocf_distortion
    true_ecapex = float(fy26["ecapex_reported"]) - cap_opex_reversal
    true_fcf = true_ocf - true_ecapex  # Equivalent to reported_fcf - rf_ocf_distortion
    true_fcf_yoy_pct = ((true_fcf - fy25_fcf) / fy25_fcf) * 100.0

    # 2. Net Debt & Senior RCF Clause 22.4 Covenant Compliance
    reported_net_debt = float(bs["net_debt_reported"])
    rf_debt_reclass = float(notes["note_11_supplier_reverse_factoring_program"]["facility_balance_fy2026_eur_m"])
    true_net_debt = reported_net_debt + rf_debt_reclass
    reported_leverage_x = reported_net_debt / reported_ebitda
    true_leverage_x = true_net_debt / true_ebitda
    covenant_breached_pre_mna = bool(true_leverage_x > rcf_limit_x)

    # 3. Project Alpine M&A Valuation & Pro-Forma Leverage
    alpine = pkt["project_alpine_mna_due_diligence_schedule"]
    alpine_ev = float(alpine["purchase_enterprise_value_eur_m"])
    alpine_new_debt = float(alpine["new_acquisition_debt_eur_m"])
    alpine_ltm_ebitda = float(alpine["target_ltm_ebitda_eur_m"])
    alpine_risks = alpine["business_mix_and_risk_findings"]
    pension_liab = float(alpine_risks["unfunded_ias19_pension_and_works_council_liability_eur_m"])
    integration_outlay = float(alpine_risks["required_integration_and_severance_outlay_eur_m"])

    pro_forma_mna_leverage_x = (true_net_debt + alpine_new_debt) / (true_ebitda + alpine_ltm_ebitda)
    pro_forma_mna_all_in_leverage_x = (true_net_debt + alpine_new_debt + pension_liab + integration_outlay) / (true_ebitda + alpine_ltm_ebitda)

    econ = alpine["independent_steady_state_economics_eur_m"]
    alpine_nopat = float(econ["normalized_nopat_eur_m"])
    alpine_roic_pct = (alpine_nopat / alpine_ev) * 100.0
    alpine_all_in_roic_pct = (alpine_nopat / (alpine_ev + pension_liab + integration_outlay)) * 100.0

    fcf_1_to_5 = [float(x) for x in econ["explicit_unlevered_fcf_years_1_to_5_eur_m"]]
    tv_year_5 = float(econ["year_6_terminal_unlevered_fcf_eur_m"]) / (
        float(econ["discount_rate_wacc"]) - float(econ["perpetual_terminal_growth_rate"])
    )
    alpine_pv = sum(cf / ((1.0 + wacc) ** t) for t, cf in enumerate(fcf_1_to_5, start=1)) + tv_year_5 / ((1.0 + wacc) ** 5)
    alpine_npv = alpine_pv - alpine_ev
    alpine_all_in_npv = alpine_pv - (alpine_ev + pension_liab + integration_outlay)
    mna_vote = "APPROVE" if (alpine_npv > 0 and not covenant_breached_pre_mna and pro_forma_mna_leverage_x <= rcf_limit_x) else "REJECT"

    # 4. Deferred Internal AI & Copper-Decommissioning Backlog Valuation
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
    blended_cf = [a + b for a, b in zip(cf_a, cf_b)]
    blended_npv = compute_npv(wacc, blended_cf)
    blended_irr_pct = compute_irr(blended_cf) * 100.0

    # 12-Month Post-Redeployment De-Leveraging Bridge (Organic FCF + Yr-1 AI/Copper Cash & Pre-Tax EBITDA Uplift)
    yr1_after_tax_uplift = blended_cf[1]
    yr1_pre_tax_ebitda_uplift = yr1_after_tax_uplift / (1.0 - tax_rate)
    post_12m_net_debt = true_net_debt - true_fcf + total_ai_capex - yr1_after_tax_uplift
    post_12m_ebitda = true_ebitda + yr1_pre_tax_ebitda_uplift
    post_redeployment_12m_leverage_x = post_12m_net_debt / post_12m_ebitda

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
        "reported_net_leverage_x": round(reported_leverage_x, 2),
        "true_adjusted_net_leverage_x": round(true_leverage_x, 2),
        "rcf_covenant_limit_x": round(rcf_limit_x, 2),
        "covenant_breached_pre_mna": covenant_breached_pre_mna,
        "pro_forma_mna_net_leverage_x": round(pro_forma_mna_leverage_x, 2),
        "project_alpine_roic_pct": round(alpine_roic_pct, 2),
        "company_wacc_pct": round(wacc * 100.0, 2),
        "project_alpine_pv_eur_m": round(alpine_pv, 2),
        "project_alpine_npv_eur_m": round(alpine_npv, 2),
        "mna_board_vote": mna_vote,
        "internal_ai_infra_total_capex_eur_m": round(total_ai_capex, 2),
        "internal_ai_infra_blended_irr_pct": round(blended_irr_pct, 2),
        "internal_ai_infra_npv_eur_m": round(blended_npv, 2),
        "post_redeployment_12m_net_leverage_x": round(post_redeployment_12m_leverage_x, 2),
        "supplementary_diagnostics": {
            "true_ocf_eur_m": round(true_ocf, 2),
            "true_ecapex_eur_m": round(true_ecapex, 2),
            "true_fcf_yoy_pct": round(true_fcf_yoy_pct, 2),
            "project_alpine_economic_profit_annual_eur_m": round(alpine_ev * (alpine_roic_pct / 100.0 - wacc), 2),
            "project_alpine_all_in_cost_eur_m": round(alpine_ev + pension_liab + integration_outlay, 2),
            "project_alpine_all_in_roic_pct": round(alpine_all_in_roic_pct, 2),
            "project_alpine_all_in_npv_eur_m": round(alpine_all_in_npv, 2),
            "pro_forma_mna_all_in_net_leverage_x": round(pro_forma_mna_all_in_leverage_x, 2),
            "initiative_a_npv_eur_m": round(compute_npv(wacc, cf_a), 2),
            "initiative_a_irr_pct": round(compute_irr(cf_a) * 100.0, 2),
            "initiative_b_npv_eur_m": round(compute_npv(wacc, cf_b), 2),
            "initiative_b_irr_pct": round(compute_irr(cf_b) * 100.0, 2),
            "post_12m_net_debt_eur_m": round(post_12m_net_debt, 2),
            "post_12m_ebitda_eur_m": round(post_12m_ebitda, 2),
            "disallowed_ceo_cfo_ltip_bonus_pool_eur_m": round(float(notes["note_14_executive_compensation_ltip_gate"]["fy2026_ceo_cfo_bonus_pool_eur_m"]), 2),
        },
    }

    out_path = script_dir / "findings.json"
    with out_path.open("w", encoding="utf-8") as fh:
        json.dump(findings, fh, indent=2)


if __name__ == "__main__":
    main()
