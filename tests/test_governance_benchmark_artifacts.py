"""Regression tests for Phase 15B Single-Blind Boardroom & Auditor Benchmark artifacts."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GOV_ART_DIR = REPO_ROOT / "artifacts" / "governance_roles"
EVAL_DIR = REPO_ROOT / "benchmarks" / "governance_eval"


def test_deterministic_board_packets_math() -> None:
    p1 = json.loads(
        (EVAL_DIR / "tasks" / "case1_enterprise_board_audit" / "financial_and_operational_packet.json").read_text(
            encoding="utf-8"
        )
    )
    rep_ebitda = p1["income_and_cashflow_summary_eur_m"]["fy2026_unaudited_management"]["reported_adjusted_ebitda"]
    cap_opex = p1["unaudited_accounting_and_treasury_footnotes"]["note_7_aurora_capitalization_policy_change"][
        "total_reclassified_from_opex_to_ecapex_eur_m"
    ]
    rep_nd = p1["balance_sheet_debt_and_liquidity_eur_m"]["net_debt_reported"]
    rf_debt = p1["unaudited_accounting_and_treasury_footnotes"]["note_11_supplier_reverse_factoring_program"][
        "facility_balance_fy2026_eur_m"
    ]
    assert round(rep_nd / rep_ebitda, 4) == 2.1000
    assert round((rep_nd + rf_debt) / (rep_ebitda - cap_opex), 4) == 2.6800

    p2 = json.loads(
        (EVAL_DIR / "tasks" / "case2_creator_studio_board" / "studio_financial_and_channel_packet.json").read_text(
            encoding="utf-8"
        )
    )
    cash = p2["cash_and_runway_baseline_usd"]["ending_unrestricted_cash_q4_2026"]
    base_burn = p2["cash_and_runway_baseline_usd"]["current_baseline_monthly_net_burn"]
    exp = p2["proposed_expansion_commitments_resolution_exp02"]
    exp_burn = (
        base_burn
        + exp["fixed_talent_mg_monthly_cash_outflow_usd"]
        + exp["la_soundstage_monthly_lease_and_ops_usd"]
        + exp["la_soundstage_buildout_monthly_draws_months_1_to_6_usd"]
    )
    assert round(cash / exp_burn, 4) == 4.8000


def test_objective_evaluator_and_blind_packet_sanitization() -> None:
    obj_key_path = EVAL_DIR / "private_key" / "objective_and_blind_key.json"
    assert obj_key_path.exists()
    data = json.loads(obj_key_path.read_text(encoding="utf-8"))
    assert len(data["results_by_uuid"]) == 6

    for uid, rec in data["results_by_uuid"].items():
        ev = rec["objective_eval"]
        assert ev["ok"] is True, f"Trial run_{uid} failed clean execution: {ev['status']}"
        assert ev["objective_score_50"] == 50

    leak_rx = re.compile(
        r"QUALIFIED_ADVERSE_FINDING|REJECT_AND_RESTRUCTURE|superhuman|orgprompt|gov_role|"
        r"daa55402|affe7ff5|6b9324ad|37023646|64a3dec9|b797d7d7",
        re.I,
    )
    for cnum in (1, 2):
        c_dir = EVAL_DIR / "blind_packets" / f"case_{cnum}"
        arms_seen = set()
        for label in ("Director_A", "Director_B", "Director_C"):
            d_dir = c_dir / label
            for fname in ("audit_analysis.py", "findings.json", "board_resolution_memo.md"):
                txt = (d_dir / fname).read_text(encoding="utf-8")
                assert not leak_rx.search(txt), f"Leak found in case_{cnum}/{label}/{fname}"
            arms_seen.add(data["blind_key"][f"case_{cnum}"][label]["arm"])
        assert arms_seen == {"Arm_1_Baseline", "Arm_2_Typical_Gov", "Arm_3_Superhuman_Gov"}


def test_locked_blind_auditor_scores_and_published_report() -> None:
    locked_path = EVAL_DIR / "blind_packets" / "locked_blind_auditor_scores.json"
    rec_path = EVAL_DIR / "private_key" / "unblinded_reconciliation.json"
    rep_path = GOV_ART_DIR / "board_and_auditor_governance_report.md"

    assert locked_path.exists()
    assert rec_path.exists()
    assert rep_path.exists()

    rec = json.loads(rec_path.read_text(encoding="utf-8"))
    assert len(rec["reconciled_trials"]) == 6
    by_arm = {}
    for row in rec["reconciled_trials"]:
        by_arm.setdefault(row["arm"], []).append(row["combined_score_100"])
    assert sum(by_arm["Arm_2_Typical_Gov"]) / 2 > sum(by_arm["Arm_1_Baseline"]) / 2
    assert sum(by_arm["Arm_3_Superhuman_Gov"]) / 2 > sum(by_arm["Arm_1_Baseline"]) / 2

    report_txt = rep_path.read_text(encoding="utf-8")
    assert "97.25" in report_txt and "96.75" in report_txt and "92.50" in report_txt
