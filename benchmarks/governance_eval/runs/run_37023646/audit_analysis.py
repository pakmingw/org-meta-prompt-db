#!/usr/bin/env python3
"""Independent Series B Board & Audit Verification — NovaFrame Studios & Channels, Inc."""

from __future__ import annotations

import json
from pathlib import Path


def resolve_packet_path(script_dir: Path) -> Path:
    candidates = [
        script_dir.parent.parent / "tasks" / "case2_creator_studio_board" / "studio_financial_and_channel_packet.json",
        Path("/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/benchmarks/governance_eval/tasks/case2_creator_studio_board/studio_financial_and_channel_packet.json"),
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError("Could not locate studio_financial_and_channel_packet.json")


def run_audit() -> dict:
    script_dir = Path(__file__).resolve().parent
    packet_path = resolve_packet_path(script_dir)
    with packet_path.open("r", encoding="utf-8") as f:
        packet = json.load(f)

    cash_base = packet["cash_and_runway_baseline_usd"]
    telemetry = packet["channel_telemetry_and_unit_economics"]
    prior = telemetry["q4_2025_prior_year"]
    curr = telemetry["q4_2026_current"]
    acct = packet["accounting_and_brand_contract_audit_schedule"]
    asc606 = acct["asc606_upfront_retainer_recognition_issue"]
    makegood = acct["audience_guarantee_make_good_exposure"]
    exp = packet["proposed_expansion_commitments_resolution_exp02"]
    turnaround = packet["alternative_operating_model_benchmarks"]["blumhouse_mrbeast_ai_swarm_turnaround_spec"]

    # 1. Creator Telemetry & Unit Economics Decomposition
    total_views_m = float(curr["total_monthly_views_m"])
    shorts_views_m = float(curr["syndicated_shorts_monthly_views_m"])
    shorts_share_pct = round((shorts_views_m / total_views_m) * 100.0, 2)
    shorts_rpm_usd = float(curr["shorts_rpm_usd"])

    lf_prior_m = float(prior["core_long_form_monthly_views_m"])
    lf_curr_m = float(curr["core_long_form_monthly_views_m"])
    lf_views_yoy_pct = round(((lf_curr_m - lf_prior_m) / lf_prior_m) * 100.0, 2)

    ctr_prior_pct = float(prior["long_form_packaging_ctr_pct"])
    ctr_curr_pct = float(curr["long_form_packaging_ctr_pct"])
    avd_prior_pct = float(prior["long_form_average_view_duration_avd_pct"])
    avd_curr_pct = float(curr["long_form_average_view_duration_avd_pct"])

    ren_prior = float(prior["core_brand_sponsor_renewal_rate_pct"])
    ren_curr = float(curr["core_brand_sponsor_renewal_rate_pct"])
    sponsor_renewal_decay_pct = round(((ren_curr - ren_prior) / ren_prior) * 100.0, 2)

    # Verify AdSense math against verified cash inflows
    inflows = cash_base["current_monthly_cash_inflows_verified"]
    calc_shorts_adsense = round(shorts_views_m * 1000.0 * shorts_rpm_usd, 2)
    calc_lf_adsense = round(lf_curr_m * 1000.0 * float(curr["long_form_adsense_rpm_usd"]), 2)
    assert abs(calc_shorts_adsense - inflows["syndicated_shorts_adsense"]) < 1.0
    assert abs(calc_lf_adsense - inflows["long_form_youtube_adsense"]) < 1.0

    # 2. ASC 606 Revenue Restatement & Make-Good Liability Audit
    reported_rev_m = round(acct["reported_fy2026_revenue_usd"] / 1e6, 2)
    reported_ebitda_m = round(acct["reported_fy2026_adjusted_ebitda_usd"] / 1e6, 2)
    asc606_reversal_m = round(asc606["unearned_revenue_requiring_deferral_reversal_usd"] / 1e6, 2)
    true_gaap_rev_m = round(reported_rev_m - asc606_reversal_m, 2)
    true_gaap_ebitda_m = round(reported_ebitda_m - asc606_reversal_m, 2)

    unbooked_make_good_m = round(
        (makegood["unbooked_make_good_ad_inventory_and_rebate_liability_usd"]
         - makegood["accrued_liability_booked_on_balance_sheet_usd"]) / 1e6,
        2,
    )
    cash_rebates_h1_usd = float(makegood["cash_rebate_demands_due_h1_2027_usd"])

    # 3. Monthly Cash Burn & Expansion Runway Stress Test (Resolution 2026-Q4-EXP-02)
    ending_cash_usd = float(cash_base["ending_unrestricted_cash_q4_2026"])
    ending_cash_m = round(ending_cash_usd / 1e6, 2)
    monthly_receipts_usd = float(inflows["total_monthly_cash_receipts"])
    monthly_opex_usd = float(cash_base["current_monthly_cash_operating_outflows"]["total_monthly_cash_opex"])
    baseline_burn_usd = monthly_opex_usd - monthly_receipts_usd
    baseline_burn_k = round(baseline_burn_usd / 1e3, 2)

    exp_incremental_monthly_usd = (
        float(exp["fixed_talent_mg_monthly_cash_outflow_usd"])
        + float(exp["la_soundstage_monthly_lease_and_ops_usd"])
        + float(exp["la_soundstage_buildout_monthly_draws_months_1_to_6_usd"])
    )
    proposed_exp_burn_usd = baseline_burn_usd + exp_incremental_monthly_usd
    proposed_exp_burn_k = round(proposed_exp_burn_usd / 1e3, 2)
    proposed_exp_runway_months = round(ending_cash_usd / proposed_exp_burn_usd, 2)
    expansion_board_vote = "REJECT" if proposed_exp_runway_months < 12.0 else "APPROVE"

    # 4. Packaging-First + AI Swarm Operating Turnaround
    curr_ep_cost_usd = float(curr["cost_per_long_form_episode_usd"])
    turn_ep_cost_usd = float(turnaround["turnaround_cost_per_episode_usd"])
    turn_ep_cost_k = round(turn_ep_cost_usd / 1e3, 2)
    ep_cost_reduction_pct = round(((curr_ep_cost_usd - turn_ep_cost_usd) / curr_ep_cost_usd) * 100.0, 2)

    turn_opex_usd = float(turnaround["turnaround_total_monthly_cash_opex_usd"])
    turn_makegood_receipts_usd = float(
        turnaround["conservative_stabilized_monthly_cash_receipts_during_makegood_burnoff_usd"]
    )
    turn_post_q2_receipts_usd = float(
        turnaround["stabilized_post_q2_monthly_cash_receipts_with_dubbing_and_ctr_recovery_usd"]
    )
    turn_transition_burn_usd = turn_opex_usd - turn_makegood_receipts_usd
    net_cash_after_rebates_usd = ending_cash_usd - cash_rebates_h1_usd
    turn_transition_runway_months = round(net_cash_after_rebates_usd / turn_transition_burn_usd, 2)

    findings = {
        "total_monthly_views_m": total_views_m,
        "shorts_views_share_pct": shorts_share_pct,
        "shorts_rpm_usd": shorts_rpm_usd,
        "long_form_views_yoy_pct": lf_views_yoy_pct,
        "long_form_ctr_prior_pct": ctr_prior_pct,
        "long_form_ctr_current_pct": ctr_curr_pct,
        "long_form_avd_prior_pct": avd_prior_pct,
        "long_form_avd_current_pct": avd_curr_pct,
        "sponsor_renewal_decay_pct": sponsor_renewal_decay_pct,
        "reported_revenue_usd_m": reported_rev_m,
        "asc606_deferred_revenue_reversal_usd_m": asc606_reversal_m,
        "true_gaap_revenue_usd_m": true_gaap_rev_m,
        "true_gaap_ebitda_usd_m": true_gaap_ebitda_m,
        "unbooked_make_good_liability_usd_m": unbooked_make_good_m,
        "ending_cash_usd_m": ending_cash_m,
        "baseline_monthly_burn_usd_k": baseline_burn_k,
        "proposed_expansion_monthly_burn_usd_k": proposed_exp_burn_k,
        "proposed_expansion_runway_months": proposed_exp_runway_months,
        "expansion_board_vote": expansion_board_vote,
        "turnaround_episode_cost_usd_k": turn_ep_cost_k,
        "episode_cost_reduction_pct": ep_cost_reduction_pct,
        "turnaround_transition_runway_months": turn_transition_runway_months,
        "supplementary_stress_metrics": {
            "net_adsense_yoy_monthly_loss_usd": round((calc_lf_adsense + calc_shorts_adsense) - (33.6 * 1000 * 18.5 + 42.0 * 1000 * 0.06), 2),
            "fully_provisioned_economic_revenue_usd_m": round(true_gaap_rev_m - unbooked_make_good_m, 2),
            "fully_provisioned_economic_ebitda_usd_m": round(true_gaap_ebitda_m - unbooked_make_good_m, 2),
            "expansion_stressed_runway_with_rebates_and_makegoods_months": round(
                net_cash_after_rebates_usd / (monthly_opex_usd + exp_incremental_monthly_usd - turn_makegood_receipts_usd), 2
            ),
            "turnaround_h1_ending_cash_usd_m": round((net_cash_after_rebates_usd - 6.0 * turn_transition_burn_usd) / 1e6, 2),
            "turnaround_post_q2_monthly_net_cash_flow_usd_k": round((turn_post_q2_receipts_usd - turn_opex_usd) / 1e3, 2),
        },
    }

    out_path = script_dir / "findings.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2)
    return findings


if __name__ == "__main__":
    results = run_audit()
    print(json.dumps(results, indent=2))
