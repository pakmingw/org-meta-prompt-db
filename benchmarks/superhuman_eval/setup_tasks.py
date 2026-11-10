#!/usr/bin/env python3
"""Deterministic benchmark input & TASK.md generator for Phase 13 3-Arm Superhuman Evaluation."""

from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TASKS_DIR = BASE_DIR / "tasks"


def setup_task1_zns_raft() -> Path:
    """Create Task 1: 3-Region NVMe-ZNS Append-Only Raft Settlement Ledger workload + TASK.md."""
    task_dir = TASKS_DIR / "task1_zns_raft"
    task_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20261110)

    num_accounts = 200
    initial_balance_cents = 1_000_000_000  # $10,000,000.00 per account
    accounts = [f"ACCT_{i:03d}" for i in range(num_accounts)]

    events = []
    seen_txs = []
    total_events = 5000
    # Target ~18% duplicate client retries (900 duplicates + 4100 unique pacs.008 transfers)
    for idx in range(total_events):
        ts_ms = round(idx * 12.0 + rng.uniform(0.0, 3.0), 3)
        in_retry_burst = (1200 <= idx < 1650) or (3100 <= idx < 3550)
        dup_prob = 0.42 if in_retry_burst else 0.125
        is_duplicate = (len(seen_txs) > 25) and (rng.random() < dup_prob)

        if is_duplicate:
            orig = rng.choice(seen_txs[-120:])
            ev = {
                "seq_id": idx,
                "timestamp_ms": ts_ms,
                "msg_type": "pacs.008.001.10",
                "end_to_end_id": orig["end_to_end_id"],
                "debtor_account": orig["debtor_account"],
                "creditor_account": orig["creditor_account"],
                "amount_cents": orig["amount_cents"],
                "payload_bytes": 4096,
                "client_retry": True,
            }
        else:
            debtor, creditor = rng.sample(accounts, 2)
            amount_cents = rng.randint(50_00, 250_000_00)
            e2e_id = f"E2E-20261110-{idx:05d}-{rng.randint(1000, 9999)}"
            ev = {
                "seq_id": idx,
                "timestamp_ms": ts_ms,
                "msg_type": "pacs.008.001.10",
                "end_to_end_id": e2e_id,
                "debtor_account": debtor,
                "creditor_account": creditor,
                "amount_cents": amount_cents,
                "payload_bytes": 4096,
                "client_retry": False,
            }
            seen_txs.append(ev)
        events.append(ev)

    workload = {
        "benchmark_id": "task1_zns_raft_pacs008",
        "cluster_topology": {
            "nodes": ["AZ1_PRIMARY", "AZ2_INTRA_REGION", "AZ3_INTER_REGION_DR"],
            "rtt_ms": {
                "AZ1_AZ2_intra_region": 1.4,
                "AZ1_AZ3_inter_region": 18.0,
                "AZ2_AZ3_inter_region": 18.4,
            },
            "nvme_zns_spec": {
                "zone_capacity_bytes": 268_435_456,  # 256 MB sequential zone
                "max_active_open_zones": 14,
                "sequential_append_latency_ms": 0.35,
                "zone_reset_latency_ms": 220.0,
                "lba_block_bytes": 4096,
            },
            "sla_and_invariants": {
                "target_p99_9_latency_ms": 8.0,
                "dedup_window_hours": 24,
                "initial_account_balance_cents": initial_balance_cents,
                "num_accounts": num_accounts,
            },
        },
        "fault_injection_schedule": {
            "az3_zns_zone_reset_stalls": [
                {"start_seq": 1200, "end_seq": 1650, "stall_latency_ms": 220.0},
                {"start_seq": 3100, "end_seq": 3550, "stall_latency_ms": 220.0},
            ],
            "split_brain_partition_and_clock_skew": {
                "start_seq": 2400,
                "end_seq": 2550,
                "old_leader": "AZ1_PRIMARY",
                "old_leader_clock_drift_ms": 12.0,
                "nominal_lease_ms": 10.0,
                "partitioned_from": ["AZ2_INTRA_REGION", "AZ3_INTER_REGION_DR"],
                "new_quorum_partition": ["AZ2_INTRA_REGION", "AZ3_INTER_REGION_DR"],
            },
        },
        "summary_counts": {
            "total_events": len(events),
            "unique_end_to_end_ids": len(seen_txs),
            "duplicate_retry_events": len(events) - len(seen_txs),
        },
        "events": events,
    }

    (task_dir / "input_workload.json").write_text(json.dumps(workload, indent=2), encoding="utf-8")

    task_md = """# Task 1: 3-Region NVMe-ZNS Append-Only Raft Settlement Ledger Remediation

## Operational Context & Incident Problem Statement
Our 3-zone ISO 20022 `pacs.008` real-time settlement ledger is suffering `p99.9 > 250ms` tail-latency collapse and split-brain double-spend risk during client retry storms.

### System Architecture & Hard Constraints
- **Topology**: 3 nodes across `AZ1_PRIMARY`, `AZ2_INTRA_REGION` (`1.4ms` RTT from `AZ1`), and `AZ3_INTER_REGION_DR` (`18.0ms` inter-region RTT from `AZ1`).
- **SLA**: Strict commit latency `p99.9 < 8.0ms` under normal and single-AZ degraded storage conditions.
- **Storage Hardware (NVMe ZNS)**: `256MB` sequential-write-only zones (`4096B` alignment) with a strict controller hardware limit of **`max_active_open_zones <= 14`**. In-place random overwrites are illegal on ZNS (`ZoneInvalidWrite`), and blocking foreground WAL appends behind synchronous zone resets (`220ms`) triggers tail-latency collapse.
- **Faults Present in `input_workload.json` (`5,000` `pacs.008` events across `200` accounts)**:
  1. **AZ3 ZNS Zone-Reset Stalls (`220ms`)** during `seq_id 1200..1650` and `3100..3550`.
  2. **Upstream Gateway Retry Storm (`~18%` duplicate `EndToEndId` retries)** requiring deterministic `24h` idempotent deduplication without double-debiting or re-executing committed transfers.
  3. **Partition + `12ms` Monotonic Clock Drift (`seq_id 2400..2550`)**: `AZ1_PRIMARY` is partitioned from `{AZ2, AZ3}` while holding a `10ms` local wall/monotonic lease skewed by `+12ms` drift, threatening split-brain stale leader commits while `{AZ2, AZ3}` elect a new term leader.
- **Conservation Law**: Exact double-entry monetary conservation (`sum_debits == sum_credits`, total system balance unchanged, `0` duplicate `EndToEndId` settlements, `0` split-brain divergent commits).

## Required Deliverables (Write into Your Assigned Output Directory)
1. **`solution.py`**: Self-contained Python 3 script (standard library / numpy) that loads `input_workload.json`, simulates both the **unmitigated baseline failure** and your **remediated ZNS + Raft settlement ledger** across all `5,000` events, verifies all conservation & ZNS zone invariants, and writes **`metrics.json`** containing:
   - `baseline_p99_9_ms` and `mitigated_p99_9_ms` (plus `mitigated_p50_ms`, `mitigated_p99_ms`)
   - `total_events`, `unique_committed_transfers`, `duplicates_deduplicated`, `double_spend_count`
   - `sum_debits_cents`, `sum_credits_cents`, `conservation_invariant_passed` (`bool`), `split_brain_commits_prevented`
   - `max_concurrent_open_zones_used` (`<= 14`), `zns_sequential_invariant_passed` (`bool`)
2. **`deliverable.md`** (`<= 240` lines): Production Engineering RFC detailing root-cause mechanics, ZNS zone-append & background GC isolation, quorum/fencing/lease design under `12ms` clock skew, ISO 20022 audit/compliance trail, and canary blast-radius rollback gates.

Execute `solution.py` before finishing so `metrics.json` is verified on disk.
"""
    (task_dir / "TASK.md").write_text(task_md, encoding="utf-8")
    return task_dir


def setup_task2_tariff_shock() -> Path:
    """Create Task 2: 3-Statement Monte Carlo Tariff + Rare-Earth Shock Financials + TASK.md."""
    task_dir = TASKS_DIR / "task2_tariff_shock"
    task_dir.mkdir(parents=True, exist_ok=True)

    financials = {
        "benchmark_id": "task2_cfo_tariff_rare_earth_shock",
        "company_profile": "Global AI & Semiconductor Hardware Enterprise (Annualized Baseline in $M)",
        "annual_baseline_usd_m": {
            "revenue": 24000.0,
            "cogs": 14400.0,
            "opex_sga_rd": 4800.0,
            "ebitda": 4800.0,
            "ebitda_margin": 0.20,
            "depreciation_amortization": 800.0,
            "gross_debt": 10500.0,
            "cash": 2100.0,
            "net_debt": 8400.0,
            "net_debt_to_ebitda": 1.75,
            "undrawn_revolver_limit": 1500.0,
            "debt_interest_rate_annual": 0.055,
            "revolver_spread_annual": 0.0675,
            "effective_tax_rate": 0.18,
            "quarterly_capex_maintenance": 225.0,
        },
        "initial_balance_sheet_usd_m": {
            "assets": {
                "cash_and_equivalents": 2100.0,
                "accounts_receivable": 3551.0,
                "inventory": 3472.0,
                "net_ppe_and_other_noncurrent": 12877.0,
                "total_assets": 22000.0,
            },
            "liabilities_and_equity": {
                "accounts_payable": 1815.0,
                "accrued_and_other_liabilities": 1685.0,
                "total_debt": 10500.0,
                "shareholders_equity": 8000.0,
                "total_liabilities_and_equity": 22000.0,
            },
            "working_capital_days": {"dso": 54.0, "dio": 88.0, "dpo": 46.0},
        },
        "covenants_and_thresholds": {
            "max_net_debt_to_ltm_ebitda": 2.50,
            "min_cash_liquidity_usd_m": 1000.0,
            "horizon_quarters": 4,
            "min_monte_carlo_paths": 2000,
            "random_seed": 20261110,
        },
        "supply_chain_and_shock_parameters": {
            "bom_tier2_specialty_substrate_share": 0.38,
            "tier2_substrate_lead_time_days": 140,
            "abrupt_tariff_rate_shock": 0.60,
            "rare_earth_quota_spot_surcharge_mean": 0.28,
            "rare_earth_quota_spot_surcharge_std": 0.14,
            "short_run_price_passthrough_fraction_mean": 0.40,
            "demand_volume_shock_mean": -0.09,
            "demand_volume_shock_std": 0.06,
            "fx_adverse_cost_vol_annual_normal": 0.12,
            "fx_adverse_cost_vol_annual_crisis": 0.26,
            "tier2_supplier_disruption_prob_quarterly": 0.16,
            "dso_crisis_elongation_days_mean": 14.0,
            "correlation_regime": {
                "normal_pairwise_rho": 0.15,
                "crisis_pairwise_rho": 0.88,
                "crisis_regime_probability": 0.35,
                "student_t_df_crisis": 4,
            },
        },
    }
    (task_dir / "baseline_financials.json").write_text(json.dumps(financials, indent=2), encoding="utf-8")

    task_md = """# Task 2: 3-Statement Monte Carlo Liquidity, Inventory & Hedging Plan Under Multi-Tier Tariff + Rare-Earth Shock

## Financial & Supply-Chain Problem Statement
Structure a quantitative 4-quarter (`Q1..Q4`) 3-statement Monte Carlo liquidity, working-capital/inventory, and FX/commodity hedging plan for a `$24.0B` revenue global semiconductor enterprise hit by an abrupt **60% multi-tier tariff + rare-earth export quota shock** where historical Gaussian correlations break down (`rho = 0.15 -> 0.88` crisis contagion) and the quarterly **`Net Debt / LTM EBITDA <= 2.50x`** maintenance covenant is threatened.

### Baseline Profile & Constraints (`baseline_financials.json`)
- **Annual Baseline**: Revenue `$24,000M`, COGS `$14,400M`, OpEx `$4,800M`, EBITDA `$4,800M` (`20%` margin), Gross Debt `$10,500M`, Cash `$2,100M`, Net Debt `$8,400M` (`1.75x`), Undrawn Revolver `$1,500M`, Covenant **`Net Debt / LTM EBITDA <= 2.50x`** tested quarterly (`Q1..Q4`), Min Cash `$1,000M`.
- **Initial Balance Sheet (`$22,000M`)**: Strictly balanced (`Assets = Cash $2,100M + AR $3,551M + Inv $3,472M + PP&E $12,877M = $22,000M`; `Liabilities + Equity = AP $1,815M + Accrued $1,685M + Debt $10,500M + Equity $8,000M = $22,000M`), `DSO=54`, `DIO=88`, `DPO=46`.
- **BOM & Regime-Shift Risk**: `38%` of COGS is exposed to Tier-2 specialty substrates (`140`-day lead time). Under crisis contagion (`35%` crisis regime weight, `rho = 0.88` fat-tailed / Student-t co-movement vs. normal `rho = 0.15`), tariff cost surge, rare-earth spot surcharges, FX basis spikes, customer DSO elongation, and supplier disruption hit simultaneously.

## Required Deliverables (Write into Your Assigned Output Directory)
1. **`solution.py`**: Self-contained Python 3 script (`numpy` / `scipy` / stdlib) that loads `baseline_financials.json`, runs **`>= 2,000` Monte Carlo paths** across 4 quarters modeling the `rho = 0.15 -> 0.88` non-Gaussian regime shift, simulates **both** (a) **Unhedged Baseline** and (b) your **Structured Capital, Inventory & Hedging Strategy**, verifies exact 3-statement balance-sheet identity (`abs(Assets - (Liabilities + Equity)) < 1e-6` across all paths/quarters), and writes **`metrics.json`** with:
   - `num_monte_carlo_paths` (`>= 2000`), `accounting_identity_max_error`, `accounting_identity_passed` (`bool`)
   - ` modeled_normal_rho`, `modeled_crisis_rho`
   - `unhedged_covenant_breach_prob`, `structured_covenant_breach_prob`, `breach_prob_reduction_abs`
   - `unhedged_p95_net_debt_to_ebitda`, `structured_p95_net_debt_to_ebitda`
   - `unhedged_cvar95_fcf_usd_m`, `structured_cvar95_fcf_usd_m`, `hedging_and_working_capital_actions`
2. **`deliverable.md`** (`<= 240` lines): CFO Board Capital-Allocation Memo detailing the 3-statement shock transmission, why Gaussian hedges fail under `rho -> 0.88` basis/contagion risk, quantified instrument sizing & costs, sensitivity table across correlation/tariff regimes, and falsifiable quarterly Board trigger gates.

Execute `solution.py` before finishing so `metrics.json` is verified on disk.
"""
    (task_dir / "TASK.md").write_text(task_md, encoding="utf-8")
    return task_dir


def setup_task3_clinical_sepsis() -> Path:
    """Create Task 3: 2,400-patient Sepsis Cohort CSV with Simpson's Paradox, ANC<500 FN/ECE & OOD Drift."""
    task_dir = TASKS_DIR / "task3_clinical_sepsis"
    task_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20261110)

    rows = []
    # 2,400 patients across HOSP_A (600), HOSP_B (550), HOSP_C (700), HOSP_D (550)
    hospital_plan = (
        [("HOSP_A", 600), ("HOSP_B", 550), ("HOSP_C", 700), ("HOSP_D", 550)]
    )

    pid = 1
    ood_indices = set(rng.sample(range(1, 2401), 50))

    for hosp_id, count in hospital_plan:
        for _ in range(count):
            is_ood = pid in ood_indices
            # ~14% immunocompromised neutropenic oncology/transplant subgroup (ANC < 500)
            if is_ood:
                immunocomp = 0
                anc = rng.randint(2400, 9200)
            else:
                immunocomp = 1 if rng.random() < (0.18 if hosp_id in ("HOSP_C", "HOSP_D") else 0.11) else 0
                anc = rng.randint(80, 480) if immunocomp == 1 else rng.randint(1800, 11500)

            icu_occ = round(
                rng.uniform(86.0, 98.5) if (hosp_id == "HOSP_C" and rng.random() < 0.68)
                else rng.uniform(58.0, 89.0),
                1,
            )

            if is_ood:
                # OOD analyzer reagent drift on procalcitonin > 12 ng/mL in low-risk non-septic / noisy patients
                sepsis_gt = 1 if rng.random() < 0.16 else 0
                temp_c = round(rng.gauss(37.0, 0.35), 2)
                lactate = round(max(0.6, rng.gauss(1.3, 0.35)), 2)
                pct = round(rng.uniform(13.5, 68.0), 2)
                analyzer_lot = "PCT_LOT_DRIFT_X9"
                # Corrupted procalcitonin saturates naive model logit -> erratic extreme score
                ai_score = round(min(0.99, max(0.02, rng.uniform(0.84, 0.98))), 4)
            elif immunocomp == 1:
                # Neutropenic subgroup: high true sepsis prevalence (~60%) with atypical AFEBRILE lactatemia
                sepsis_gt = 1 if rng.random() < 0.60 else 0
                if sepsis_gt == 1:
                    temp_c = round(rng.gauss(36.65, 0.30), 2)  # Afebrile!
                    lactate = round(max(2.2, rng.gauss(3.85, 0.75)), 2)
                    pct = round(max(0.4, rng.gauss(2.9, 0.9)), 2)
                    # Deployed model over-relies on fever -> systematically under-predicts septic neutropenic patients!
                    ai_score = round(min(0.96, max(0.05, rng.gauss(0.43, 0.16))), 4)
                else:
                    temp_c = round(rng.gauss(36.60, 0.28), 2)
                    lactate = round(max(0.6, rng.gauss(1.25, 0.35)), 2)
                    pct = round(max(0.05, rng.gauss(0.35, 0.18)), 2)
                    ai_score = round(min(0.55, max(0.01, rng.gauss(0.14, 0.08))), 4)
                analyzer_lot = "PCT_LOT_STD_04"
            else:
                # Immunocompetent ICU population: aggregate cohort AUROC ~ 0.91
                base_sepsis_p = 0.36 if hosp_id == "HOSP_C" else 0.24
                sepsis_gt = 1 if rng.random() < base_sepsis_p else 0
                if sepsis_gt == 1:
                    temp_c = round(rng.gauss(38.85, 0.55), 2)
                    lactate = round(max(1.8, rng.gauss(3.5, 0.8)), 2)
                    pct = round(max(0.8, rng.gauss(4.6, 1.6)), 2)
                    ai_score = round(min(0.99, max(0.08, rng.gauss(0.73, 0.18))), 4)
                else:
                    temp_c = round(rng.gauss(36.95, 0.35), 2)
                    lactate = round(max(0.5, rng.gauss(1.15, 0.35)), 2)
                    pct = round(max(0.04, rng.gauss(0.28, 0.16)), 2)
                    ai_score = round(min(0.88, max(0.01, rng.gauss(0.22, 0.17))), 4)
                analyzer_lot = "PCT_LOT_STD_04"

            # Hospital C deployed automated nurse-alert throttling when icu_occupancy_pct > 85.0%
            throttled = (hosp_id == "HOSP_C") and (icu_occ > 85.0)
            alert_delivered = 1 if (ai_score >= 0.50 and not throttled) else 0

            # Early antibiotics driven strongly by alert_delivered (confounding observed mortality!)
            if alert_delivered == 1:
                early_abx = 1 if rng.random() < 0.88 else 0
            else:
                early_abx = 1 if rng.random() < 0.14 else 0

            # 30-day mortality physics: true sepsis + immunocomp + lack of early_abx drives mortality
            if sepsis_gt == 1:
                if immunocomp == 1:
                    mort_p = 0.16 if early_abx == 1 else 0.54
                else:
                    mort_p = 0.09 if early_abx == 1 else 0.34
            else:
                mort_p = 0.04 if (is_ood and early_abx == 1) else 0.025
            mortality_30d = 1 if rng.random() < mort_p else 0

            rows.append({
                "patient_id": f"PT_{pid:04d}",
                "hospital_id": hosp_id,
                "icu_occupancy_pct": icu_occ,
                "immunocompromised": immunocomp,
                "anc_cells_ul": anc,
                "temperature_c": temp_c,
                "lactate_mmol_l": lactate,
                "procalcitonin_ng_ml": pct,
                "analyzer_lot": analyzer_lot,
                "ai_risk_score": ai_score,
                "alert_delivered": alert_delivered,
                "early_antibiotics": early_abx,
                "sepsis_ground_truth": sepsis_gt,
                "mortality_30d": mortality_30d,
            })
            pid += 1

    csv_path = task_dir / "sepsis_cohort.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    task_md = """# Task 3: Multi-Hospital Sepsis AI Failure Diagnosis, Subgroup Recalibration & FDA SaMD PCCP Protocol

## Clinical Deployment & Safety Incident Statement
A 4-hospital ICU Sepsis Early-Warning AI (`HOSP_A..HOSP_D`, `N = 2,400` in `sepsis_cohort.csv`) reports a strong aggregate **`AUROC ~ 0.91`** at threshold `0.50`, yet **immunocompromised oncology/transplant ICU mortality is rising** and site clinicians report erratic false alarms and missed deteriorations.

### Clinical & Operational Context (`sepsis_cohort.csv`)
- **Subgroup Physiology**: Neutropenic immunocompromised patients (`anc_cells_ul < 500`) frequently present with **atypical afebrile lactatemia** (normal/low temperature despite rising lactate).
- **Workflow & Telemetry Confounding**: Hospital nursing IT configured occupancy-dependent alert routing (`icu_occupancy_pct`, `alert_delivered`, `early_antibiotics`). Specifically, inspect whether automated nurse-alert throttling during high occupancy (`> 85%` in `HOSP_C`) suppresses alerts and confounds naive treated-outcome / Simpson's Paradox evaluations.
- **Lab Assay Drift**: Clinical chemistry flagged potential reagent/analyzer drift (`analyzer_lot`, `procalcitonin_ng_ml > 12.0 ng/mL`) causing out-of-distribution (OOD) score saturation requiring mandatory clinician HITL abstention rather than autonomous alerting/suppression.

## Required Deliverables (Write into Your Assigned Output Directory)
1. **`solution.py`**: Self-contained Python 3 script (stdlib / `numpy` / `scipy` / `pandas` / `sklearn` if installed) analyzing `sepsis_cohort.csv` and writing **`metrics.json`** with:
   - `total_patients`, `aggregate_auroc`
   - `simpsons_paradox_and_hosp_c_throttling`: quantified alert suppression rate in `HOSP_C` high occupancy (`>85%`) and unadjusted vs. stratified/confounding-adjusted mortality & treatment effect
   - `immunocompromised_anc_lt_500`: `n`, `pre_recalibration_fn_rate` (at `0.50`), `pre_recalibration_ece`, `post_recalibration_fn_rate`, `post_recalibration_ece`, `calibrated_subgroup_threshold`, and Decision Curve **Net Benefit** uplift
   - `ood_procalcitonin_abstention`: count of detected OOD rows (`procalcitonin_ng_ml > 12.0` / `analyzer_lot` drift), abstention gate rule, and cleaned cohort calibration/accuracy metrics
2. **`deliverable.md`** (`<= 240` lines): Biostatistical Root-Cause Analysis & **FDA SaMD Predetermined Change Control Plan (PCCP)** + **Clinician HITL Safety Governance Protocol** (modification protocol, impact assessment, subgroup guardrails, IRB/clinical risk sign-off, and rollback triggers).

Execute `solution.py` before finishing so `metrics.json` is verified on disk.
"""
    (task_dir / "TASK.md").write_text(task_md, encoding="utf-8")
    return task_dir


if __name__ == "__main__":
    t1 = setup_task1_zns_raft()
    t2 = setup_task2_tariff_shock()
    t3 = setup_task3_clinical_sepsis()
    print(f"Generated deterministic tasks:\n - {t1}\n - {t2}\n - {t3}")
