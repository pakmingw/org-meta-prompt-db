#!/usr/bin/env python3
"""Generate realistic Quarterly Board & Audit Tear-Down Packets for Phase 15 Governance Benchmark."""

from __future__ import annotations

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TASKS_DIR = BASE_DIR / "tasks"


def setup_case1_enterprise_board_audit() -> Path:
    """Create Case 1: EuroNet Cloud & Fiber S.A. Q4 2026 Board Deck, Financial Packet & TASK.md."""
    case_dir = TASKS_DIR / "case1_enterprise_board_audit"
    case_dir.mkdir(parents=True, exist_ok=True)

    deck_md = """# CONFIDENTIAL — BOARD OF DIRECTORS & AUDIT COMMITTEE PACKET (Q4 / FY2026)
**Entity**: EuroNet Cloud & Fiber S.A. (`Euronext: ENCF`)
**Prepared By**: Chief Executive Officer & Chief Financial Officer
**Meeting Agenda**: (1) FY2026 Operational & AI Outperformance Review; (2) Approval of Resolution `2026-Q4-M&A-01` ("Project Alpine" — €1,800M Acquisition of Helvetia Legacy IT Services AG)

---

## 1. CEO & CFO Executive Highlights ("Transformation Ahead of Target")
- **Industry-Leading Adjusted EBITDA Growth (`+9.4% YoY`)**: FY2026 Adjusted EBITDA reached **`€2,260.0M`** (up from `€2,065.8M` in FY2025, `28.68%` margin on `€7,880.0M` revenue), comfortably beating our `+8.0%` Executive LTIP stretch target.
- **Fortress Balance Sheet (`2.10x` Net Leverage)**: Reported Net Debt stands at **`€4,746.0M`** (`€5,420.0M` Gross Debt less `€674.0M` Cash & Equivalents), representing **`2.10x` Reported Adjusted EBITDA**—providing `0.40x` headroom inside our **`2.50x` Senior Revolving Credit Facility (`€1,500M` RCF)** maintenance covenant.
- **Enterprise AI Transformation "On Track"**: Deployed `12,400` general-purpose seat licenses of office chat copilots (`89%` monthly prompt-login badge completion). To conserve M&A firepower, we paused `€400M` of capital-intensive Autonomous Copper-Exchange Decommissioning and Agentic SOC/SD-WAN Zero-Touch Automation until FY2028+.
- **Strategic M&A Resolution (`Project Alpine` — Requesting Immediate Binding Sign-Off)**:
  - Acquire **Helvetia Legacy IT Services AG** (DACH/Benelux B2B mainframe, Solaris, and private-hosting outsourcer; `€156.52M` LTM EBITDA) for **`€1,800.0M` Enterprise Value (`11.50x` EV/EBITDA)**, funded 100% via a new **`6.85%` Senior Bridge-to-Bond Debt Facility**.
  - Management projects `"€65M of run-rate AI cross-sell synergies"` by Year 3 and urges the Board to waive external fairness/forensic review to sign the binding SPA before Friday's exclusivity deadline.
"""
    (case_dir / "management_board_deck.md").write_text(deck_md, encoding="utf-8")

    packet = {
        "packet_id": "case1_euronet_cloud_fiber_q4_2026",
        "entity": "EuroNet Cloud & Fiber S.A.",
        "currency": "EUR_MILLIONS",
        "corporate_parameters": {
            "wacc_annual": 0.078,
            "effective_tax_rate": 0.25,
            "senior_rcf_facility_limit_eur_m": 1500.0,
            "rcf_maintenance_covenant_max_net_debt_to_ebitda": 2.50,
            "rcf_covenant_definition_note": (
                "Per Clause 22.4 of the €1,500M Senior RCF Agreement, Consolidated EBITDA excludes capitalized "
                "routine operating maintenance not meeting IAS 38.57 development criteria, and Consolidated Net Debt "
                "includes any supplier finance / reverse factoring obligations novated to financial institutions or "
                "extended >90 days beyond standard 60-day industry trade terms under IAS 7 / IFRS 7, while excluding "
                "legally trapped/escrowed cash only if pledged (unrestricted cash = €674.0M)."
            ),
        },
        "income_and_cashflow_summary_eur_m": {
            "fy2025_audited": {
                "revenue": 7650.0,
                "operating_expenses_excl_da": 5584.2,
                "reported_adjusted_ebitda": 2065.8,
                "operating_cash_flow": 1820.0,
                "ecapex": 1170.0,
                "free_cash_flow": 650.0,
            },
            "fy2026_unaudited_management": {
                "revenue": 7880.0,
                "operating_expenses_excl_da": 5620.0,
                "reported_adjusted_ebitda": 2260.0,
                "reported_ebitda_yoy_growth_pct": 9.4007,
                "operating_cash_flow_reported": 2039.0,
                "ecapex_reported": 1480.0,
                "free_cash_flow_reported": 559.0,
            },
        },
        "balance_sheet_debt_and_liquidity_eur_m": {
            "gross_financial_debt_reported": 5420.0,
            "unrestricted_cash_and_equivalents": 674.0,
            "net_debt_reported": 4746.0,
            "reported_net_debt_to_ebitda_x": 2.10,
            "trade_payables_standard_60d": 890.0,
        },
        "unaudited_accounting_and_treasury_footnotes": {
            "note_7_aurora_capitalization_policy_change": {
                "effective_date": "2026-01-01",
                "total_reclassified_from_opex_to_ecapex_eur_m": 310.0,
                "components_eur_m": {
                    "tier2_tier3_legacy_oss_bss_bugfix_and_ticket_maintenance": 185.0,
                    "recurring_copper_drop_weather_fault_truck_roll_repairs": 125.0,
                },
                "internal_audit_workpaper_comment": (
                    "Internal engineering logs confirm 0% new software feature creation or asset useful-life extension; "
                    "100% of the €310.0M represents recurring day-to-day maintenance previously expensed in OpEx in FY2025. "
                    "IAS 38.57 technical/economic feasibility gates were bypassed via CFO manual journal override."
                ),
            },
            "note_11_supplier_reverse_factoring_program": {
                "facility_balance_fy2026_eur_m": 480.0,
                "facility_balance_fy2025_eur_m": 320.0,
                "net_yoy_working_capital_cash_inflow_booked_in_ocf_eur_m": 160.0,
                "original_vendor_payment_terms_days": 60,
                "extended_bank_settlement_terms_days": 180,
                "interest_margin_paid_by_euronet_to_bank": "EURIBOR + 265 bps",
                "legal_structure": (
                    "Tri-party novation agreement extinguishing original vendor trade payable at Day 60 and creating an "
                    "interest-bearing financial obligation to Alpine Trade Bank AG at Day 180; classified by CFO under "
                    "'Other Working Capital Accruals' outside Reported Gross Debt."
                ),
            },
            "note_14_executive_compensation_ltip_gate": {
                "fy2026_ceo_cfo_bonus_pool_eur_m": 18.4,
                "vesting_formula": (
                    "70% weighted on Reported Adjusted EBITDA YoY growth >= +8.0% (cliff threshold) and "
                    "30% weighted on Reported Net Debt / Adjusted EBITDA <= 2.25x. Zero FCF, eCapEx, or ROIC metrics."
                ),
            },
        },
        "project_alpine_mna_due_diligence_schedule": {
            "target_name": "Helvetia Legacy IT Services AG",
            "purchase_enterprise_value_eur_m": 1800.0,
            "new_acquisition_debt_eur_m": 1800.0,
            "new_debt_interest_rate": 0.0685,
            "target_ltm_ebitda_eur_m": 156.52,
            "acquisition_ev_to_ebitda_multiple_x": 11.50,
            "business_mix_and_risk_findings": {
                "legacy_mainframe_solaris_mpls_revenue_share": 0.68,
                "annual_legacy_revenue_attrition_rate": -0.065,
                "top5_bank_contracts_expiring_2027_share": 0.41,
                "unfunded_ias19_pension_and_works_council_liability_eur_m": 95.0,
                "required_integration_and_severance_outlay_eur_m": 110.0,
            },
            "independent_steady_state_economics_eur_m": {
                "normalized_post_synergy_ebit_eur_m": 100.80,
                "effective_tax_rate": 0.25,
                "normalized_nopat_eur_m": 75.60,
                "explicit_unlevered_fcf_years_1_to_5_eur_m": [42.0, 68.0, 82.0, 85.0, 86.0],
                "year_6_terminal_unlevered_fcf_eur_m": 88.58,
                "perpetual_terminal_growth_rate": 0.010,
                "discount_rate_wacc": 0.078,
            },
        },
        "deferred_internal_ai_and_infra_redeployment_backlog": {
            "initiative_a_autonomous_copper_decommissioning": {
                "name": "AI GIS Dispatch & Autonomous Copper-to-FTTH Exchange Decommissioning (1,450 Exchanges)",
                "upfront_capex_eur_m": 260.0,
                "annual_after_tax_cash_savings_years_1_to_5_eur_m": [72.0, 108.0, 118.0, 122.0, 125.0],
                "salvage_copper_and_real_estate_release_year_5_eur_m": 65.0,
            },
            "initiative_b_agentic_soc_and_sdwan_swarms": {
                "name": "Agentic Tier-1/2 Cyber SOC Triage & Zero-Touch NetBox/Terraform SD-WAN Provisioning Swarms",
                "upfront_capex_eur_m": 140.0,
                "annual_after_tax_cash_uplift_years_1_to_5_eur_m": [52.0, 76.0, 88.0, 94.0, 98.0],
                "terminal_value_year_5_conservative_eur_m": 110.0,
            },
        },
    }
    (case_dir / "financial_and_operational_packet.json").write_text(json.dumps(packet, indent=2), encoding="utf-8")

    task_md = """# Board & Audit Committee Review Assignment — Case 1: EuroNet Cloud & Fiber S.A.

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
"""
    (case_dir / "TASK.md").write_text(task_md, encoding="utf-8")
    return case_dir


def setup_case2_creator_studio_board() -> Path:
    """Create Case 2: NovaFrame Studios & Channels, Inc. Series B Board Deck, Packet & TASK.md."""
    case_dir = TASKS_DIR / "case2_creator_studio_board"
    case_dir.mkdir(parents=True, exist_ok=True)

    deck_md = """# CONFIDENTIAL — SERIES B BOARD OF DIRECTORS PACKET (Q4 / FY2026)
**Entity**: NovaFrame Studios & Channels, Inc. (Venture-Backed Indie Film & Creator Media Studio)
**Prepared By**: Co-Founder/CEO & Head of Finance
**Meeting Agenda**: (1) Explosive `140M` Monthly Viewership Milestone (`+85% YoY`); (2) Approval of Resolution `2026-Q4-EXP-02` (`$12.0M` Fixed 2-Year Talent Minimum Guarantees + `$4.5M` Custom Los Angeles Soundstage Lease & Build-Out)

---

## 1. Management Executive Narrative ("Hyper-Growth & Studio Institutionalization")
- **Audience Hyper-Growth (`140.0M` Monthly Views, `+85.2% YoY`)**: Total monthly cross-platform views jumped from `75.6M` in Q4 2025 to **`140.0M` in Q4 2026**, validating our high-volume multi-channel slate.
- **Record Recognized Revenue (`$18.40M`) & Positive Adjusted EBITDA (`+$1.15M`)**: Following strong Q3–Q4 multi-quarter brand partnership signings, recognized FY2026 revenue hit **`$18.40M`** with **`$7.10M` unrestricted cash** on hand at year-end.
- **Expansion Resolution `2026-Q4-EXP-02` (Requesting Immediate Board Sign-Off)**:
  1. **Lock In Tier-1 On-Screen Creator Hosts (`$12.0M` Fixed 2-Year Minimum Guarantees)**: Execute binding 24-month non-cancellable cash retainers (`$6.00M/yr` = `$500.0k/month` fixed cash draw regardless of episode CTR/AVD or sponsorship sales).
  2. **Open Flagship Custom Burbank LA Soundstage (`$4.50M` Commitment)**: Sign a non-cancellable facility lease (`$150.0k/month` = `$1.80M/yr` fixed rent/ops) plus **`$2.70M` custom set & LED-wall build-out** payable in `6` equal monthly contractor draws of `$450.0k/month` across Months 1–6 of 2027.
"""
    (case_dir / "management_board_deck.md").write_text(deck_md, encoding="utf-8")

    packet = {
        "packet_id": "case2_novaframe_creator_studio_q4_2026",
        "entity": "NovaFrame Studios & Channels, Inc.",
        "currency": "USD",
        "cash_and_runway_baseline_usd": {
            "ending_unrestricted_cash_q4_2026": 7_100_000.0,
            "venture_debt_or_credit_lines_available": 0.0,
            "current_monthly_cash_inflows_verified": {
                "long_form_youtube_adsense": 342_250.0,
                "syndicated_shorts_adsense": 7_290.0,
                "earned_cash_sponsorships_and_merch": 310_460.0,
                "total_monthly_cash_receipts": 660_000.0,
            },
            "current_monthly_cash_operating_outflows": {
                "long_form_production_4_episodes_at_185k_each": 740_000.0,
                "sga_editorial_and_studio_overhead_38_fte": 299_166.67,
                "total_monthly_cash_opex": 1_039_166.67,
            },
            "current_baseline_monthly_net_burn": 379_166.67,
        },
        "channel_telemetry_and_unit_economics": {
            "q4_2025_prior_year": {
                "total_monthly_views_m": 75.6,
                "syndicated_shorts_monthly_views_m": 42.0,
                "shorts_rpm_usd": 0.06,
                "core_long_form_monthly_views_m": 33.6,
                "long_form_adsense_rpm_usd": 18.50,
                "long_form_packaging_ctr_pct": 8.4,
                "long_form_average_view_duration_avd_pct": 54.0,
                "first_30s_hook_retention_pct": 81.0,
                "core_brand_sponsor_renewal_rate_pct": 68.0,
                "sponsor_net_dollar_retention_pct": 112.0,
                "cost_per_long_form_episode_usd": 142_000.0,
            },
            "q4_2026_current": {
                "total_monthly_views_m": 140.0,
                "syndicated_shorts_monthly_views_m": 121.5,
                "shorts_rpm_usd": 0.06,
                "shorts_to_long_form_sub_conversion_pct": 0.14,
                "core_long_form_monthly_views_m": 18.5,
                "long_form_adsense_rpm_usd": 18.50,
                "long_form_packaging_ctr_pct": 3.9,
                "long_form_average_view_duration_avd_pct": 36.0,
                "first_30s_hook_retention_pct": 56.0,
                "core_brand_sponsor_renewal_rate_pct": 46.92,
                "core_sponsor_renewal_relative_decay_pct": -31.0,
                "sponsor_net_dollar_retention_pct": 77.28,
                "cost_per_long_form_episode_usd": 185_000.0,
                "episodes_produced_per_month": 4,
                "pre_production_title_thumbnail_testing_rate_pct": 0.0,
            },
        },
        "accounting_and_brand_contract_audit_schedule": {
            "reported_fy2026_revenue_usd": 18_400_000.0,
            "reported_fy2026_adjusted_ebitda_usd": 1_150_000.0,
            "asc606_upfront_retainer_recognition_issue": {
                "upfront_recognized_2027_multi_quarter_retainers_usd": 6_200_000.0,
                "total_contracted_integrations": 34,
                "integrations_filmed_or_aired_as_of_2026_12_31": 6,
                "undelivered_2027_integrations_recognized_upfront": 28,
                "unearned_revenue_requiring_deferral_reversal_usd": 6_200_000.0,
                "audit_note": (
                    "Management booked 100% of $6.20M multi-quarter 2027 brand retainers as Q3/Q4 2026 revenue upon "
                    "contract signature (`ASC 606-10-25` violation: performance obligations are distinct episode "
                    "integrations satisfied only at public broadcast/upload)."
                ),
            },
            "audience_guarantee_make_good_exposure": {
                "contracts_missing_guaranteed_view_thresholds_count": 19,
                "unbooked_make_good_ad_inventory_and_rebate_liability_usd": 3_800_000.0,
                "cash_rebate_demands_due_h1_2027_usd": 600_000.0,
                "free_make_good_episode_slots_owed_in_2027": 19,
                "accrued_liability_booked_on_balance_sheet_usd": 0.0,
            },
        },
        "proposed_expansion_commitments_resolution_exp02": {
            "fixed_2yr_talent_minimum_guarantee_total_usd": 12_000_000.0,
            "fixed_talent_mg_monthly_cash_outflow_usd": 500_000.0,
            "la_soundstage_year1_total_commitment_usd": 4_500_000.0,
            "la_soundstage_monthly_lease_and_ops_usd": 150_000.0,
            "la_soundstage_buildout_capex_total_usd": 2_700_000.0,
            "la_soundstage_buildout_monthly_draws_months_1_to_6_usd": 450_000.0,
        },
        "alternative_operating_model_benchmarks": {
            "blumhouse_mrbeast_ai_swarm_turnaround_spec": {
                "kill_gate_rule": (
                    "Zero principal photography until Title + Thumbnail concept achieves >= 6.5% simulated/panel CTR "
                    "and 0-30s script animatic clears >= 75% retention (`Beast/Blumhouse Packaging-First Gate`)."
                ),
                "ai_production_and_localization_swarm": (
                    "Replace manual footage logging, rough-cut assembly, and outsourced dubbing with AI transcript "
                    "NLE rough-cut swarm, multi-variant thumbnail/hook telemetry testing, and 6-language AI voice/lip "
                    "localization—cutting per-episode cost from $185,000 to $96,000 (-48.1%) and reducing total "
                    "monthly cash OpEx (incl. modular day-rate stage rentals & profit-share talent pods) to $665,000/mo."
                ),
                "turnaround_cost_per_episode_usd": 96_000.0,
                "turnaround_total_monthly_cash_opex_usd": 665_000.0,
                "conservative_stabilized_monthly_cash_receipts_during_makegood_burnoff_usd": 370_000.0,
                "stabilized_post_q2_monthly_cash_receipts_with_dubbing_and_ctr_recovery_usd": 820_000.0,
            },
        },
    }
    (case_dir / "studio_financial_and_channel_packet.json").write_text(json.dumps(packet, indent=2), encoding="utf-8")

    task_md = """# Series B Board & Audit Review Assignment — Case 2: NovaFrame Studios & Channels, Inc.

## Fiduciary Mandate
You sit on the Board of Directors of **NovaFrame Studios & Channels, Inc.** (`management_board_deck.md` and `studio_financial_and_channel_packet.json`). Management highlights `140.0M` monthly views (`+85.2%` YoY), `$18.40M` revenue, `+$1.15M` Adjusted EBITDA, and `$7.10M` cash, and requests immediate approval of Resolution `2026-Q4-EXP-02` (`$12.0M` in fixed 2-year talent MGs + `$4.5M` custom LA soundstage lease & build-out).

Conduct an independent creator-telemetry decomposition, `ASC 606` revenue & make-good liability audit, monthly cash-burn & runway stress test, and studio operating-model turnaround analysis.

## Required Deliverables (Write into Your Assigned Output Directory)
1. **`audit_analysis.py`** (`<= 230` lines): Self-contained Python 3 script (stdlib / `numpy`) that loads `studio_financial_and_channel_packet.json`, audits viewership unit economics, `ASC 606` revenue/liability adjustments, and monthly cash runway under both Management's Expansion Plan and a Packaging-First + AI Swarm Turnaround, and writes **`findings.json`** containing:
   - `total_monthly_views_m`, `shorts_views_share_pct`, `shorts_rpm_usd`, `long_form_views_yoy_pct`
   - `long_form_ctr_prior_pct`, `long_form_ctr_current_pct`, `long_form_avd_prior_pct`, `long_form_avd_current_pct`, `sponsor_renewal_decay_pct`
   - `reported_revenue_usd_m`, `asc606_deferred_revenue_reversal_usd_m`, `true_gaap_revenue_usd_m`, `true_gaap_ebitda_usd_m`, `unbooked_make_good_liability_usd_m`
   - `ending_cash_usd_m`, `baseline_monthly_burn_usd_k`, `proposed_expansion_monthly_burn_usd_k`, `proposed_expansion_runway_months`, `expansion_board_vote` (`"APPROVE"` or `"REJECT"`)
   - `turnaround_episode_cost_usd_k`, `episode_cost_reduction_pct`, `turnaround_transition_runway_months`
2. **`board_resolution_memo.md`** (`<= 230` lines): Formal Series B Board Resolution & Operating Turnaround Memo containing: (a) Shorts vs. Long-Form Telemetry & Sponsor Decay Diagnosis, (b) `ASC 606` Restatement & Make-Good Remediation Plan, (c) Binding Vote on `$12M` Talent MGs & `$4.5M` Soundstage (`4.8`-Month Insolvency Proof), and (d) *Blumhouse* Micro-Budget Kill-Gate + *MrBeast* Title/Thumbnail Pre-Validation + AI Production Swarm Roadmap (`-48%` Episode Cost & `22+` Month Runway).

Execute `audit_analysis.py` before finishing so `findings.json` is verified on disk.
"""
    (case_dir / "TASK.md").write_text(task_md, encoding="utf-8")
    return case_dir


def main() -> None:
    c1 = setup_case1_enterprise_board_audit()
    c2 = setup_case2_creator_studio_board()
    print(f"Generated Case 1 packet at: {c1}")
    print(f"Generated Case 2 packet at: {c2}")


if __name__ == "__main__":
    main()
