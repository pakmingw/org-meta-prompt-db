#!/usr/bin/env python3
"""Deterministic 50-Point Objective Evaluator & Blind Packet Builder for Phase 13."""

from __future__ import annotations

import json
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent
PRIV_DIR = BASE_DIR / "private_key"
BLIND_DIR = BASE_DIR / "blind_packets"


def _flatten_json(obj: Any, prefix: str = "") -> Dict[str, Any]:
    """Flatten nested JSON dictionaries for resilient key lookup across solver schemas."""
    out: Dict[str, Any] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            full_k = f"{prefix}.{k}" if prefix else str(k)
            out[k.lower()] = v
            out[full_k.lower()] = v
            if isinstance(v, (dict, list)):
                out.update(_flatten_json(v, full_k))
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            if isinstance(item, dict):
                out.update(_flatten_json(item, f"{prefix}[{idx}]"))
    return out


def _find_num(flat: Dict[str, Any], patterns: List[str]) -> Optional[float]:
    for pat in patterns:
        rx = re.compile(pat, re.I)
        for k, v in flat.items():
            if rx.search(k) and isinstance(v, (int, float)) and not isinstance(v, bool):
                return float(v)
    return None


def _find_bool(flat: Dict[str, Any], patterns: List[str]) -> Optional[bool]:
    for pat in patterns:
        rx = re.compile(pat, re.I)
        for k, v in flat.items():
            if rx.search(k) and isinstance(v, bool):
                return v
    return None


def _run_solution(run_dir: Path) -> tuple[bool, str, Dict[str, Any]]:
    sol = run_dir / "solution.py"
    metrics_path = run_dir / "metrics.json"
    if not sol.exists():
        return False, "solution.py missing", {}
    try:
        proc = subprocess.run(
            [sys.executable, str(sol)],
            cwd=str(run_dir),
            capture_output=True,
            text=True,
            timeout=90,
        )
    except Exception as exc:
        return False, f"execution exception: {exc}", {}
    if proc.returncode != 0:
        return False, f"returncode={proc.returncode}: {proc.stderr[-300:]}", {}
    if not metrics_path.exists():
        return False, "metrics.json missing after execution", {}
    try:
        data = json.loads(metrics_path.read_text(encoding="utf-8"))
        return True, "ok", data
    except Exception as exc:
        return False, f"invalid metrics.json: {exc}", {}


def evaluate_task1(run_dir: Path) -> Dict[str, Any]:
    ok, msg, metrics = _run_solution(run_dir)
    flat = _flatten_json(metrics)
    code = (run_dir / "solution.py").read_text(encoding="utf-8") if (run_dir / "solution.py").exists() else ""
    doc = (run_dir / "deliverable.md").read_text(encoding="utf-8") if (run_dir / "deliverable.md").exists() else ""

    # 1. Clean execution + 5,000 events (10 pts)
    total_ev = _find_num(flat, [r"total_events", r"events_processed"])
    c1 = (5 if ok else 0) + (5 if (ok and total_ev == 5000) else (3 if ok and metrics else 0))

    # 2. Conservation sum_debits == sum_credits, 0 double-spends, split-brain fencing (10 pts)
    deb = _find_num(flat, [r"sum_debits"])
    cred = _find_num(flat, [r"sum_credits"])
    cons_bool = _find_bool(flat, [r"conservation_invariant_passed", r"conservation"])
    dbl = _find_num(flat, [r"double_spend_count", r"double_spends"])
    sb = _find_num(flat, [r"split_brain_commits_prevented", r"stale_leader", r"fenced"])
    c2 = 0
    if (deb is not None and cred is not None and deb > 0 and deb == cred) or cons_bool is True:
        c2 += 4
    if dbl == 0.0 and re.search(r"end_to_end_id|dedup", code, re.I):
        c2 += 3
    if (sb is not None and sb >= 1) or re.search(r"clock_drift|lease|fenc|term|quorum", code, re.I):
        c2 += 3

    # 3. ZNS sequential zone-append & <= 14 active open zones (10 pts)
    open_z = _find_num(flat, [r"max_concurrent_open_zones", r"open_zones_used", r"active_open_zones"])
    zns_bool = _find_bool(flat, [r"zns_sequential_invariant", r"zns_invariant"])
    c3 = 0
    if open_z is not None and 1 <= open_z <= 14:
        c3 += 5
    if zns_bool is True or re.search(r"268435456|268_435_456|zone_capacity|write_pointer", code, re.I):
        c3 += 5

    # 4. Achieves p99.9 < 8.0ms under AZ3 220ms stall + baseline > 200ms comparison (10 pts)
    base_p999 = _find_num(flat, [r"baseline_p99_9", r"unmitigated_p99_9"])
    mit_p999 = _find_num(flat, [r"mitigated_p99_9", r"remediated_p99_9", r"^p99_9_ms$"])
    c4 = 0
    if mit_p999 is not None and 0.1 < mit_p999 < 8.0:
        c4 += 6
    if base_p999 is not None and base_p999 >= 200.0:
        c4 += 4

    # 5. ISO 20022 compliance/audit + canary blast-radius rollback gates in RFC (10 pts)
    c5 = 0
    if re.search(r"pacs\.008|iso\s*20022", doc, re.I) and re.search(r"audit|reconcil|merkle|hash|immutable", doc, re.I):
        c5 += 5
    if re.search(r"rollback|canary|blast[\s-]*radius|circuit[\s-]*breaker|abort", doc, re.I) and re.search(r"ms|%|threshold|gate", doc, re.I):
        c5 += 5

    breakdown = {
        "c1_clean_execution": c1,
        "c2_conservation_and_idempotency": c2,
        "c3_zns_zone_invariants": c3,
        "c4_tail_latency_sla": c4,
        "c5_audit_and_rollback_gates": c5,
    }
    return {"ok": ok, "status": msg, "objective_score_50": sum(breakdown.values()), "breakdown": breakdown, "metrics": metrics}


def evaluate_task2(run_dir: Path) -> Dict[str, Any]:
    ok, msg, metrics = _run_solution(run_dir)
    flat = _flatten_json(metrics)
    code = (run_dir / "solution.py").read_text(encoding="utf-8") if (run_dir / "solution.py").exists() else ""
    doc = (run_dir / "deliverable.md").read_text(encoding="utf-8") if (run_dir / "deliverable.md").exists() else ""

    # 1. >= 2,000 Monte Carlo paths cleanly executed (10 pts)
    paths = _find_num(flat, [r"num_monte_carlo_paths", r"monte_carlo_paths", r"n_paths", r"paths"])
    c1 = (5 if ok else 0) + (5 if (ok and paths is not None and paths >= 2000) else 0)

    # 2. 3-statement accounting identity Assets == Liabilities + Equity holds (10 pts)
    acc_ok = _find_bool(flat, [r"accounting_identity_passed", r"balance_sheet_balanced"])
    acc_err = _find_num(flat, [r"accounting_identity_max_error", r"max_balance_error", r"accounting_error"])
    c2 = 0
    if acc_ok is True:
        c2 += 5
    if (acc_err is not None and acc_err < 1e-3) or re.search(r"total_assets.*total_liab|assets\s*-\s*\(?liab", code, re.I):
        c2 += 5

    # 3. Models tail-correlation regime shift (rho -> 0.88 / non-Gaussian Student-t contagion) (10 pts)
    c_rho = _find_num(flat, [r"crisis_rho", r"modeled_crisis_rho"])
    c3 = 0
    if (c_rho is not None and abs(c_rho - 0.88) < 0.05) or re.search(r"0\.88", code):
        c3 += 5
    if re.search(r"student|standard_t|cholesky|copula|df", code, re.I) and re.search(r"gaussian|basis|contagion|0\.88", doc, re.I):
        c3 += 5

    # 4. Decisively reduces covenant breach P(Net Debt/EBITDA > 2.5x) & quantifies tail improvement (10 pts)
    unh_b = _find_num(flat, [r"unhedged_covenant_breach_prob", r"baseline_breach_prob"])
    str_b = _find_num(flat, [r"structured_covenant_breach_prob", r"hedged_breach_prob", r"mitigated_breach_prob"])
    unh_nd = _find_num(flat, [r"unhedged_p95_net_debt", r"unhedged_p95"])
    str_nd = _find_num(flat, [r"structured_p95_net_debt", r"structured_p95"])
    c4 = 0
    if unh_b is not None and str_b is not None and unh_b > str_b and (unh_b - str_b) >= 0.05:
        c4 += 6
    if unh_nd is not None and str_nd is not None and str_nd < unh_nd:
        c4 += 4

    # 5. Falsifiable quarterly Board trigger gates & sensitivity table in memo (10 pts)
    c5 = 0
    if "|" in doc and re.search(r"sensitiv|scenario|rho|tariff", doc, re.I):
        c5 += 5
    if re.search(r"trigger|gate|threshold|board|revolver|covenant", doc, re.I) and re.search(r"Q1|Q2|quarter|bps|x\b", doc, re.I):
        c5 += 5

    breakdown = {
        "c1_monte_carlo_execution": c1,
        "c2_accounting_identity": c2,
        "c3_regime_shift_contagion": c3,
        "c4_covenant_breach_reduction": c4,
        "c5_board_triggers_and_sensitivity": c5,
    }
    return {"ok": ok, "status": msg, "objective_score_50": sum(breakdown.values()), "breakdown": breakdown, "metrics": metrics}


def evaluate_task3(run_dir: Path) -> Dict[str, Any]:
    ok, msg, metrics = _run_solution(run_dir)
    flat = _flatten_json(metrics)
    code = (run_dir / "solution.py").read_text(encoding="utf-8") if (run_dir / "solution.py").exists() else ""
    doc = (run_dir / "deliverable.md").read_text(encoding="utf-8") if (run_dir / "deliverable.md").exists() else ""
    metrics_str = json.dumps(metrics)

    # 1. Clean execution on 2,400 rows + aggregate AUROC ~ 0.91-0.93 (10 pts)
    tot = _find_num(flat, [r"total_patients", r"n_total", r"cohort_size"])
    auroc = _find_num(flat, [r"aggregate_auroc", r"overall_auroc", r"^auroc$"])
    c1 = (5 if ok else 0) + (5 if (ok and tot == 2400 and auroc is not None and 0.88 <= auroc <= 0.96) else 0)

    # 2. Catches Simpson's Paradox & Hospital C >85% occupancy alert-throttling confounding (10 pts)
    c2 = 0
    if re.search(r"HOSP_C", code) and re.search(r"85", code) and re.search(r"HOSP_C|throttl|suppress", metrics_str, re.I):
        c2 += 5
    if re.search(r"simpson|confound|stratif", code + " " + doc, re.I) and re.search(r"mortality_30d|early_antibiotics", code):
        c2 += 5

    # 3. Recalibrates ANC < 500 subgroup (FN rate & ECE reduction + Net Benefit) (10 pts)
    pre_fn = _find_num(flat, [r"pre_recalibration_fn_rate", r"baseline_fn_rate", r"anc.*pre.*fn"])
    post_fn = _find_num(flat, [r"post_recalibration_fn_rate", r"calibrated_fn_rate", r"anc.*post.*fn"])
    pre_ece = _find_num(flat, [r"pre_recalibration_ece", r"baseline_ece", r"anc.*pre.*ece"])
    post_ece = _find_num(flat, [r"post_recalibration_ece", r"calibrated_ece", r"anc.*post.*ece"])
    c3 = 0
    if pre_fn is not None and post_fn is not None and pre_fn > 0.40 and post_fn < pre_fn:
        c3 += 4
    if pre_ece is not None and post_ece is not None and pre_ece > 0.15 and post_ece < pre_ece:
        c3 += 3
    if re.search(r"net_benefit|decision[\s_-]*curve", code + " " + metrics_str, re.I):
        c3 += 3

    # 4. OOD procalcitonin > 12 ng/mL drift detection (50 rows) + clinician HITL abstention gate (10 pts)
    c4 = 0
    if re.search(r"12\.0|12|PCT_LOT_DRIFT", code) and ("50" in metrics_str):
        c4 += 5
    if re.search(r"abstain|abstention|hitl|human[\s-]*in[\s-]*the[\s-]*loop", code + " " + doc, re.I):
        c4 += 5

    # 5. Complete FDA SaMD PCCP + IRB/clinical risk governance protocol (10 pts)
    c5 = 0
    if re.search(r"PCCP|Predetermined Change Control Plan", doc, re.I) and re.search(
        r"Modification\s+(?:Scope\s*&\s*)?Protocol|Impact Assessment|Modification Boundary", doc, re.I
    ):
        c5 += 5
    if re.search(r"IRB|clinical[\s-]*risk|rollback|guardrail|safety[\s-]*gate", doc, re.I):
        c5 += 5

    breakdown = {
        "c1_cohort_execution": c1,
        "c2_simpsons_and_hosp_c_confounding": c2,
        "c3_anc_subgroup_recalibration": c3,
        "c4_ood_abstention_gate": c4,
        "c5_fda_samd_pccp_governance": c5,
    }
    return {"ok": ok, "status": msg, "objective_score_50": sum(breakdown.values()), "breakdown": breakdown, "metrics": metrics}


def _sanitize_blind_text(text: str, run_uuid8: str) -> str:
    """Strip any self-identifying persona/arm strings so blind Auditor packets have zero leakage."""
    cleaned = text.replace(f"run_{run_uuid8}", "candidate_workspace")
    cleaned = cleaned.replace(f"persona_{run_uuid8}", "assigned_persona")
    cleaned = re.sub(r"\bSuperhuman\s+", "Lead ", cleaned, flags=re.I)
    cleaned = re.sub(r"org-superhuman-role-synthesizer", "specialist-methodology", cleaned, flags=re.I)
    cleaned = re.sub(r"\bsh_[a-z0-9_]+\b", "specialist_profile", cleaned)
    cleaned = re.sub(r"\bOKG\b", "Cross-Functional", cleaned)
    cleaned = re.sub(r"Organizational Knowledge Graph", "Cross-Functional Enterprise", cleaned, flags=re.I)
    cleaned = re.sub(r"\bSection\s+[478]\b", "Specification", cleaned)
    cleaned = re.sub(
        r"\b(?:infra|fin|health|tech|consult|sec|ops|legal)_([a-z0-9_]+)\b",
        lambda m: m.group(1).replace("_", " "),
        cleaned,
    )
    return cleaned


def run_all_evaluations_and_build_blind_packets() -> Dict[str, Any]:
    mapping = json.loads((PRIV_DIR / "arm_mapping.json").read_text(encoding="utf-8"))
    if BLIND_DIR.exists():
        shutil.rmtree(BLIND_DIR)
    BLIND_DIR.mkdir(parents=True, exist_ok=True)

    evaluators = {1: evaluate_task1, 2: evaluate_task2, 3: evaluate_task3}
    results_by_uuid: Dict[str, Any] = {}
    by_task: Dict[int, List[Dict[str, Any]]] = {1: [], 2: [], 3: []}

    for tr in mapping["trials"]:
        uid = tr["trial_uuid8"]
        tnum = tr["task_num"]
        rdir = Path(tr["run_dir"])
        ev = evaluators[tnum](rdir)
        sol_p, met_p, doc_p = rdir / "solution.py", rdir / "metrics.json", rdir / "deliverable.md"
        ev["artifact_sizes_bytes"] = {
            "solution_py": sol_p.stat().st_size if sol_p.exists() else 0,
            "metrics_json": met_p.stat().st_size if met_p.exists() else 0,
            "deliverable_md": doc_p.stat().st_size if doc_p.exists() else 0,
        }
        results_by_uuid[uid] = {**tr, "objective_eval": ev}
        by_task[tnum].append(tr)

    # Randomized blind permutation per task (distinct seeded shuffle for each task!)
    rng = random.Random(2026111099)
    blind_key: Dict[str, Dict[str, Any]] = {}
    for tnum in (1, 2, 3):
        shuffled = list(by_task[tnum])
        rng.shuffle(shuffled)
        t_blind_dir = BLIND_DIR / f"task_{tnum}"
        t_blind_dir.mkdir(parents=True, exist_ok=True)
        blind_key[f"task_{tnum}"] = {}
        for label, tr in zip(["Candidate_A", "Candidate_B", "Candidate_C"], shuffled):
            uid = tr["trial_uuid8"]
            cdir = t_blind_dir / label
            cdir.mkdir(parents=True, exist_ok=True)
            rdir = Path(tr["run_dir"])
            for fname in ("solution.py", "metrics.json", "deliverable.md"):
                src = rdir / fname
                if src.exists():
                    raw = src.read_text(encoding="utf-8")
                    (cdir / fname).write_text(_sanitize_blind_text(raw, uid), encoding="utf-8")
            blind_key[f"task_{tnum}"][label] = {
                "trial_uuid8": uid,
                "arm": tr["arm"],
                "persona_source": tr["persona_source"],
            }

    out = {"results_by_uuid": results_by_uuid, "blind_key": blind_key}
    (PRIV_DIR / "objective_and_blind_key.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


if __name__ == "__main__":
    summary = run_all_evaluations_and_build_blind_packets()
    for uid, rec in summary["results_by_uuid"].items():
        ev = rec["objective_eval"]
        print(f"Task {rec['task_num']} | {rec['arm']:17s} | run_{uid} -> {ev['objective_score_50']}/50 {ev['breakdown']}")
