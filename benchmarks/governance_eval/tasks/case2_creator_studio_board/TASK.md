# Series B Board & Audit Review Assignment — Case 2: NovaFrame Studios & Channels, Inc.

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
