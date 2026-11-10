#!/usr/bin/env python3
"""Independent Board & Audit Forensic Analysis — NovaFrame Studios & Channels, Inc."""

from __future__ import annotations

import json
from pathlib import Path
import numpy as np


def load_packet(run_dir: Path) -> dict:
    """Load the financial and channel telemetry packet from canonical task path."""
    candidates = [
        run_dir.parent.parent / "tasks" / "case2_creator_studio_board" / "studio_financial_and_channel_packet.json",
        Path("/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/benchmarks/governance_eval/tasks/case2_creator_studio_board/studio_financial_and_channel_packet.json"),
    ]
    for path in candidates:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    raise FileNotFoundError("Could not locate studio_financial_and_channel_packet.json")


def run_audit() -> dict:
    run_dir = Path(__file__).resolve().parent
    packet = load_packet(run_dir)

    cash_base = packet["cash_and_runway_baseline_usd"]
    prior = packet["channel_telemetry_and_unit_economics"]["q4_2025_prior_year"]
    curr = packet["channel_telemetry_and_unit_economics"]["q4_2026_current"]
    acct = packet["accounting_and_brand_contract_audit_schedule"]
    retainer_issue = acct["asc606_upfront_retainer_recognition_issue"]
    make_good = acct["audience_guarantee_make_good_exposure"]
    exp = packet["proposed_expansion_commitments_resolution_exp02"]
    turnaround = packet["alternative_operating_model_benchmarks"]["blumhouse_mrbeast_ai_swarm_turnaround_spec"]

    # 1. Channel Telemetry & Vanity-View Disaggregation
    total_views_m = float(curr["total_monthly_views_m"])
    shorts_views_m = float(curr["syndicated_shorts_monthly_views_m"])
    shorts_share_pct = round((shorts_views_m / total_views_m) * 100.0, 2)
    shorts_rpm_usd = float(curr["shorts_rpm_usd"])

    lf_prior_m = float(prior["core_long_form_monthly_views_m"])
    lf_curr_m = float(curr["core_long_form_monthly_views_m"])
    lf_yoy_pct = round(((lf_curr_m - lf_prior_m) / lf_prior_m) * 100.0, 2)

    ctr_prior_pct = float(prior["long_form_packaging_ctr_pct"])
    ctr_curr_pct = float(curr["long_form_packaging_ctr_pct"])
    avd_prior_pct = float(prior["long_form_average_view_duration_avd_pct"])
    avd_curr_pct = float(curr["long_form_average_view_duration_avd_pct"])

    renewal_prior = float(prior["core_brand_sponsor_renewal_rate_pct"])
    renewal_curr = float(curr["core_brand_sponsor_renewal_rate_pct"])
    sponsor_renewal_decay_pct = round(((renewal_curr - renewal_prior) / renewal_prior) * 100.0, 2)

    # 2. ASC 606 Revenue Deferral & ASC 450 / 606-10-32 Make-Good Liability Audit
    reported_rev_m = round(float(acct["reported_fy2026_revenue_usd"]) / 1e6, 2)
    reported_adj_ebitda_m = round(float(acct["reported_fy2026_adjusted_ebitda_usd"]) / 1e6, 2)
    deferred_rev_reversal_m = round(float(retainer_issue["unearned_revenue_requiring_deferral_reversal_usd"]) / 1e6, 2)
    unbooked_make_good_m = round(float(make_good["unbooked_make_good_ad_inventory_and_rebate_liability_usd"]) / 1e6, 2)
    cash_rebates_h1_2027_usd = float(make_good["cash_rebate_demands_due_h1_2027_usd"])

    true_gaap_rev_m = round(reported_rev_m - deferred_rev_reversal_m, 2)
    ebitda_post_deferral_only_m = round(reported_adj_ebitda_m - deferred_rev_reversal_m, 2)
    true_gaap_ebitda_m = round(reported_adj_ebitda_m - deferred_rev_reversal_m - unbooked_make_good_m, 2)

    # 3. Cash Burn & Expansion Insolvency Stress Test (Months 1-6)
    ending_cash_usd = float(cash_base["ending_unrestricted_cash_q4_2026"])
    ending_cash_m = round(ending_cash_usd / 1e6, 2)
    inflows = cash_base["current_monthly_cash_inflows_verified"]
    outflows = cash_base["current_monthly_cash_operating_outflows"]
    monthly_receipts_usd = float(np.sum([
        inflows["long_form_youtube_adsense"],
        inflows["syndicated_shorts_adsense"],
        inflows["earned_cash_sponsorships_and_merch"],
    ]))
    monthly_opex_usd = float(np.sum([
        outflows["long_form_production_4_episodes_at_185k_each"],
        outflows["sga_editorial_and_studio_overhead_38_fte"],
    ]))
    baseline_burn_usd = monthly_opex_usd - monthly_receipts_usd
    baseline_burn_k = round(baseline_burn_usd / 1e3, 2)

    expansion_added_monthly_usd = float(np.sum([
        exp["fixed_talent_mg_monthly_cash_outflow_usd"],
        exp["la_soundstage_monthly_lease_and_ops_usd"],
        exp["la_soundstage_buildout_monthly_draws_months_1_to_6_usd"],
    ]))
    proposed_exp_burn_usd = baseline_burn_usd + expansion_added_monthly_usd
    proposed_exp_burn_k = round(proposed_exp_burn_usd / 1e3, 2)
    proposed_exp_runway_months = round(ending_cash_usd / proposed_exp_burn_usd, 2)
    expansion_vote = "REJECT" if proposed_exp_runway_months < 12.0 else "APPROVE"

    # 4. Blumhouse / MrBeast Packaging-First + AI Production Swarm Turnaround
    curr_ep_cost_usd = float(curr["cost_per_long_form_episode_usd"])
    turnaround_ep_cost_usd = float(turnaround["turnaround_cost_per_episode_usd"])
    turnaround_ep_cost_k = round(turnaround_ep_cost_usd / 1e3, 2)
    ep_cost_reduction_pct = round(((curr_ep_cost_usd - turnaround_ep_cost_usd) / curr_ep_cost_usd) * 100.0, 2)

    turnaround_opex_usd = float(turnaround["turnaround_total_monthly_cash_opex_usd"])
    transition_receipts_usd = float(turnaround["conservative_stabilized_monthly_cash_receipts_during_makegood_burnoff_usd"])
    stabilized_receipts_usd = float(turnaround["stabilized_post_q2_monthly_cash_receipts_with_dubbing_and_ctr_recovery_usd"])
    transition_burn_usd = turnaround_opex_usd - transition_receipts_usd
    net_cash_after_rebates_usd = ending_cash_usd - cash_rebates_h1_2027_usd
    turnaround_transition_runway_months = round(net_cash_after_rebates_usd / transition_burn_usd, 2)

    findings = {
        "total_monthly_views_m": total_views_m,
        "shorts_views_share_pct": shorts_share_pct,
        "shorts_rpm_usd": shorts_rpm_usd,
        "long_form_views_yoy_pct": lf_yoy_pct,
        "long_form_ctr_prior_pct": ctr_prior_pct,
        "long_form_ctr_current_pct": ctr_curr_pct,
        "long_form_avd_prior_pct": avd_prior_pct,
        "long_form_avd_current_pct": avd_curr_pct,
        "sponsor_renewal_decay_pct": sponsor_renewal_decay_pct,
        "reported_revenue_usd_m": reported_rev_m,
        "asc606_deferred_revenue_reversal_usd_m": deferred_rev_reversal_m,
        "true_gaap_revenue_usd_m": true_gaap_rev_m,
        "true_gaap_ebitda_usd_m": true_gaap_ebitda_m,
        "unbooked_make_good_liability_usd_m": unbooked_make_good_m,
        "ending_cash_usd_m": ending_cash_m,
        "baseline_monthly_burn_usd_k": baseline_burn_k,
        "proposed_expansion_monthly_burn_usd_k": proposed_exp_burn_k,
        "proposed_expansion_runway_months": proposed_exp_runway_months,
        "expansion_board_vote": expansion_vote,
        "turnaround_episode_cost_usd_k": turnaround_ep_cost_k,
        "episode_cost_reduction_pct": ep_cost_reduction_pct,
        "turnaround_transition_runway_months": turnaround_transition_runway_months,
        "audit_schedules": {
            "shorts_views_yoy_pct": round(((shorts_views_m - float(prior["syndicated_shorts_monthly_views_m"])) / float(prior["syndicated_shorts_monthly_views_m"])) * 100.0, 2),
            "hook_30s_retention_prior_pct": float(prior["first_30s_hook_retention_pct"]),
            "hook_30s_retention_current_pct": float(curr["first_30s_hook_retention_pct"]),
            "sponsor_ndr_prior_pct": float(prior["sponsor_net_dollar_retention_pct"]),
            "sponsor_ndr_current_pct": float(curr["sponsor_net_dollar_retention_pct"]),
            "ebitda_post_deferral_pre_makegood_usd_m": ebitda_post_deferral_only_m,
            "cash_rebate_demands_h1_2027_usd_m": round(cash_rebates_h1_2027_usd / 1e6, 2),
            "expansion_runway_after_h1_rebates_months": round(net_cash_after_rebates_usd / proposed_exp_burn_usd, 2),
            "turnaround_transition_monthly_burn_usd_k": round(transition_burn_usd / 1e3, 2),
            "turnaround_pre_rebate_runway_months": round(ending_cash_usd / transition_burn_usd, 2),
            "post_q2_stabilized_monthly_fcf_usd_k": round((stabilized_receipts_usd - turnaround_opex_usd) / 1e3, 2),
        },
    }

    (run_dir / "findings.json").write_text(json.dumps(findings, indent=2) + "\n", encoding="utf-8")
    return findings


if __name__ == "__main__":
    print(json.dumps(run_audit(), indent=2))
