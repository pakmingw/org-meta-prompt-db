"""Regression tests for Phase 13 3-Arm Superhuman Role Benchmark artifacts & evaluator."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SH_DIR = REPO_ROOT / "artifacts" / "superhuman_roles"
EVAL_DIR = REPO_ROOT / "benchmarks" / "superhuman_eval"
DB_PATH = REPO_ROOT / "data" / "org_knowledge_base.db"


@pytest.mark.parametrize(
    ("json_name", "md_name", "expected_mode"),
    [
        ("superhuman_1_zns_raft_ledger.json", "superhuman_1_zns_raft_ledger.md", "problem_discovery"),
        ("superhuman_2_cfo_tariff_shock.json", "superhuman_2_cfo_tariff_shock.md", "canonical_role"),
        ("superhuman_3_clinical_sepsis_samd.json", "superhuman_3_clinical_sepsis_samd.md", "custom_agent_role"),
    ],
)
def test_three_synthesized_superhumans_cover_all_pathways(
    json_name: str, md_name: str, expected_mode: str
) -> None:
    json_path = SH_DIR / json_name
    md_path = SH_DIR / md_name
    assert json_path.exists(), f"Missing {json_path}"
    assert md_path.exists(), f"Missing {md_path}"

    pkg = json.loads(json_path.read_text(encoding="utf-8"))
    assert pkg["input_mode"] == expected_mode
    assert len(pkg["deep_superhuman_prompt"]) >= 30_000
    assert len(pkg["adjacent_roles"]) >= 3
    assert len(pkg["enterprise_team_roles"]) >= 4
    assert len(pkg["on_the_job_crucibles"]["crucible_episodes"]) >= 4
    assert len(pkg["unknown_problem_epistemology"]["stages"]) == 5
    assert pkg["developer_context"]
    assert md_path.stat().st_size >= 25_000


def test_persisted_superhuman_profiles_in_sqlite() -> None:
    conn = sqlite3.connect(str(DB_PATH))
    count = conn.execute("SELECT COUNT(*) FROM superhuman_role_profiles").fetchone()[0]
    assert count >= 3


def test_deterministic_benchmark_task_inputs() -> None:
    w = json.loads((EVAL_DIR / "tasks" / "task1_zns_raft" / "input_workload.json").read_text(encoding="utf-8"))
    assert len(w["events"]) == 5000

    fin = json.loads((EVAL_DIR / "tasks" / "task2_tariff_shock" / "baseline_financials.json").read_text(encoding="utf-8"))
    bs = fin["initial_balance_sheet_usd_m"]
    assert bs["assets"]["total_assets"] == bs["liabilities_and_equity"]["total_liabilities_and_equity"] == 22000.0

    sepsis_lines = (EVAL_DIR / "tasks" / "task3_clinical_sepsis" / "sepsis_cohort.csv").read_text(encoding="utf-8").splitlines()
    assert len(sepsis_lines) == 2401  # header + 2,400 rows


def test_objective_evaluator_and_blind_packets_integrity() -> None:
    obj_key_path = EVAL_DIR / "private_key" / "objective_and_blind_key.json"
    assert obj_key_path.exists(), "Run evaluate_trials.py before executing benchmark artifact tests"
    data = json.loads(obj_key_path.read_text(encoding="utf-8"))
    assert len(data["results_by_uuid"]) == 9

    for uid, rec in data["results_by_uuid"].items():
        ev = rec["objective_eval"]
        assert ev["ok"] is True, f"Trial run_{uid} failed clean execution: {ev['status']}"
        assert 0 <= ev["objective_score_50"] <= 50

    for tnum in (1, 2, 3):
        t_dir = EVAL_DIR / "blind_packets" / f"task_{tnum}"
        arms_seen = set()
        for cand in ("Candidate_A", "Candidate_B", "Candidate_C"):
            c_dir = t_dir / cand
            for fname in ("solution.py", "metrics.json", "deliverable.md"):
                p = c_dir / fname
                assert p.exists()
                txt = p.read_text(encoding="utf-8")
                assert "org-superhuman-role-synthesizer" not in txt
                assert "Superhuman " not in txt
            arms_seen.add(data["blind_key"][f"task_{tnum}"][cand]["arm"])
        assert arms_seen == {"Arm_1_Baseline", "Arm_2_Canonical", "Arm_3_Superhuman"}


def test_published_benchmark_report_exists() -> None:
    report = SH_DIR / "superhuman_skill_benchmark_report.md"
    assert report.exists()
    content = report.read_text(encoding="utf-8")
    assert "Arm 1" in content or "Baseline" in content
    assert "Canonical" in content
    assert "Superhuman" in content
