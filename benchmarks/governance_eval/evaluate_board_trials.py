#!/usr/bin/env python3
"""Deterministic 50-Point Objective Evaluator & Single-Blind Packet Builder for Phase 15."""

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
    """Flatten nested JSON structures for resilient key lookup across solver schemas."""
    out: Dict[str, Any] = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            full_k = f"{prefix}.{k}" if prefix else str(k)
            out[str(k).lower()] = v
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


def _find_str(flat: Dict[str, Any], patterns: List[str]) -> Optional[str]:
    for pat in patterns:
        rx = re.compile(pat, re.I)
        for k, v in flat.items():
            if rx.search(k) and isinstance(v, str):
                return v
    return None


def _run_audit_script(run_dir: Path) -> tuple[bool, str, Dict[str, Any]]:
    script = run_dir / "audit_analysis.py"
    findings_path = run_dir / "findings.json"
    if not script.exists():
        return False, "audit_analysis.py missing", {}
    try:
        proc = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(run_dir),
            capture_output=True,
            text=True,
            timeout=90,
        )
    except Exception as exc:
        return False, f"execution exception: {exc}", {}
    if proc.returncode != 0:
        return False, f"returncode={proc.returncode}: {proc.stderr[-300:]}", {}
    if not findings_path.exists():
        return False, "findings.json missing after execution", {}
    try:
        data = json.loads(findings_path.read_text(encoding="utf-8"))
        return True, "ok", data
    except Exception as exc:
        return False, f"invalid findings.json: {exc}", {}


def evaluate_case1(run_dir: Path) -> Dict[str, Any]:
    """Score Case 1 (EuroNet Cloud & Fiber S.A.) across 5 deterministic criteria (50 pts)."""
    ok, msg, findings = _run_audit_script(run_dir)
    flat = _flatten_json(findings)
    code = (run_dir / "audit_analysis.py").read_text(encoding="utf-8") if (run_dir / "audit_analysis.py").exists() else ""
    memo = (run_dir / "board_resolution_memo.md").read_text(encoding="utf-8") if (run_dir / "board_resolution_memo.md").exists() else ""

    # 1. Clean script execution + structured findings & memo present (10 pts)
    c1 = (5 if ok else 0) + (5 if (ok and len(findings) >= 8 and len(memo) >= 800) else 0)

    # 2. Forensic OpEx Capitalization (€310M IAS 38 reversal -> €1,950M EBITDA) & -14.0% FCF divergence (10 pts)
    cap_rev = _find_num(flat, [r"capitalized_opex_reversal", r"opex_reclass", r"ias38"])
    true_ebitda = _find_num(flat, [r"true_normalized_ebitda", r"adjusted_true_ebitda", r"normalized_ebitda"])
    fcf_yoy = _find_num(flat, [r"reported_fcf_yoy_pct", r"fcf_yoy"])
    true_fcf = _find_num(flat, [r"true_underlying_fcf", r"underlying_fcf"])
    c2 = 0
    if (cap_rev is not None and abs(abs(cap_rev) - 310.0) < 1.0) and (true_ebitda is not None and abs(true_ebitda - 1950.0) < 2.0):
        c2 += 5
    if (fcf_yoy is not None and (abs(fcf_yoy - (-14.0)) < 0.5 or abs(fcf_yoy - (-0.14)) < 0.01)) and (
        true_fcf is not None and (abs(true_fcf - 399.0) < 5.0 or abs(true_fcf - 559.0) < 5.0)
    ):
        c2 += 5

    # 3. Off-balance-sheet Reverse Factoring (€480M -> €5,226M Net Debt) & 2.68x > 2.50x RCF Covenant Breach (10 pts)
    rf_debt = _find_num(flat, [r"reverse_factoring_debt_reclass", r"reverse_factoring.*debt", r"supplier_finance"])
    true_nd = _find_num(flat, [r"true_adjusted_net_debt", r"adjusted_net_debt", r"true_net_debt"])
    true_lev = _find_num(flat, [r"true_adjusted_net_leverage", r"true_net_leverage", r"adjusted_leverage"])
    breached = _find_bool(flat, [r"covenant_breached_pre_mna", r"covenant_breached", r"rcf_breach"])
    c3 = 0
    if (rf_debt is not None and abs(rf_debt - 480.0) < 2.0) and (true_nd is not None and abs(true_nd - 5226.0) < 5.0):
        c3 += 4
    if true_lev is not None and abs(true_lev - 2.68) < 0.03:
        c3 += 3
    if breached is True:
        c3 += 3

    # 4. Project Alpine €1.8B M&A Value Destruction (ROIC 4.2% < WACC 7.8%, NPV ~ -€620M) & REJECT vote (10 pts)
    roic = _find_num(flat, [r"project_alpine_roic", r"mna_roic", r"alpine_roic"])
    wacc = _find_num(flat, [r"company_wacc", r"^wacc"])
    npv_mna = _find_num(flat, [r"project_alpine_npv", r"mna_npv", r"alpine_npv"])
    vote = _find_str(flat, [r"mna_board_vote", r"board_vote"])
    c4 = 0
    if roic is not None and (abs(roic - 4.2) < 0.3 or abs(roic - 0.042) < 0.003) and wacc is not None:
        c4 += 4
    if npv_mna is not None and -850.0 <= npv_mna <= -550.0:
        c4 += 3
    if vote is not None and "REJECT" in vote.upper():
        c4 += 3

    # 5. Internal €400M AI Swarm & Copper-Decommissioning Redeployment (>22% IRR, >+€400M NPV) + LTIP Clawback (10 pts)
    ai_irr = _find_num(flat, [r"internal_ai_infra_blended_irr", r"redeployed.*irr", r"ai.*irr"])
    ai_npv = _find_num(flat, [r"internal_ai_infra_npv", r"redeployed.*npv", r"ai_infra_npv"])
    c5 = 0
    if ai_irr is not None and (ai_irr > 22.0 or (0.22 < ai_irr < 1.0)) and ai_npv is not None and ai_npv > 350.0:
        c5 += 6
    if re.search(r"18\.4|ltip|bonus|clawback|remuneration|compensation", memo + " " + code, re.I):
        c5 += 4

    breakdown = {
        "c1_clean_execution_and_schema": c1,
        "c2_forensic_opex_and_fcf_divergence": c2,
        "c3_reverse_factoring_and_covenant_breach": c3,
        "c4_mna_veto_and_economic_profit_math": c4,
        "c5_ai_redeployment_and_ltip_governance": c5,
    }
    return {"ok": ok, "status": msg, "objective_score_50": sum(breakdown.values()), "breakdown": breakdown, "findings": findings}


def evaluate_case2(run_dir: Path) -> Dict[str, Any]:
    """Score Case 2 (NovaFrame Studios & Channels, Inc.) across 5 deterministic criteria (50 pts)."""
    ok, msg, findings = _run_audit_script(run_dir)
    flat = _flatten_json(findings)
    code = (run_dir / "audit_analysis.py").read_text(encoding="utf-8") if (run_dir / "audit_analysis.py").exists() else ""
    memo = (run_dir / "board_resolution_memo.md").read_text(encoding="utf-8") if (run_dir / "board_resolution_memo.md").exists() else ""

    # 1. Clean script execution + structured findings & memo present (10 pts)
    c1 = (5 if ok else 0) + (5 if (ok and len(findings) >= 8 and len(memo) >= 800) else 0)

    # 2. Shorts $0.06 RPM mix-shift (86.8% share) + Long-Form CTR (8.4->3.9%) / AVD (54->36%) + -31% sponsor decay (10 pts)
    s_rpm = _find_num(flat, [r"shorts_rpm"])
    ctr_cur = _find_num(flat, [r"long_form_ctr_current", r"current_ctr"])
    avd_cur = _find_num(flat, [r"long_form_avd_current", r"current_avd"])
    sp_decay = _find_num(flat, [r"sponsor_renewal_decay", r"renewal_decay"])
    c2 = 0
    if s_rpm is not None and abs(s_rpm - 0.06) < 0.01:
        c2 += 4
    if (ctr_cur is not None and (abs(ctr_cur - 3.9) < 0.2 or abs(ctr_cur - 0.039) < 0.002)) and (
        avd_cur is not None and (abs(avd_cur - 36.0) < 1.0 or abs(avd_cur - 0.36) < 0.01)
    ):
        c2 += 3
    if sp_decay is not None and (abs(abs(sp_decay) - 31.0) < 1.5 or abs(abs(sp_decay) - 0.31) < 0.02):
        c2 += 3

    # 3. ASC 606 $6.20M upfront retainer deferral ($18.4M -> $12.2M GAAP rev) + $3.80M make-good liability (10 pts)
    rev_def = _find_num(flat, [r"asc606_deferred_revenue_reversal", r"deferred_revenue_reversal", r"premature_revenue"])
    gaap_rev = _find_num(flat, [r"true_gaap_revenue", r"gaap_adjusted_revenue", r"adjusted_revenue"])
    mg_liab = _find_num(flat, [r"unbooked_make_good_liability", r"make_good_liability", r"makegood"])
    c3 = 0
    if (rev_def is not None and (abs(abs(rev_def) - 6.2) < 0.2 or abs(abs(rev_def) - 6_200_000) < 50_000)) and (
        gaap_rev is not None and (abs(gaap_rev - 12.2) < 0.5 or abs(gaap_rev - 12_200_000) < 500_000 or abs(gaap_rev - 8.4) < 0.5)
    ):
        c3 += 5
    if mg_liab is not None and (abs(mg_liab - 3.8) < 0.2 or abs(mg_liab - 3_800_000) < 50_000):
        c3 += 5

    # 4. Cash Runway Cliff (~4.8 months on $7.1M cash) & binding REJECT vote on $12M MGs + $4.5M Soundstage (10 pts)
    exp_runway = _find_num(flat, [r"proposed_expansion_runway_months", r"proposed_plan_runway", r"expansion_runway"])
    vote = _find_str(flat, [r"expansion_board_vote", r"board_vote"])
    c4 = 0
    if exp_runway is not None and 4.0 <= exp_runway <= 5.2:
        c4 += 6
    if vote is not None and "REJECT" in vote.upper():
        c4 += 4

    # 5. Blumhouse Kill-Gate + MrBeast Packaging Pre-Validation + AI Swarm (-48.1% episode cost & 22+m runway) (10 pts)
    ep_red = _find_num(flat, [r"episode_cost_reduction_pct", r"cost_reduction_pct"])
    turn_runway = _find_num(flat, [r"turnaround_transition_runway_months", r"turnaround_runway"])
    c5 = 0
    if (ep_red is not None and (45.0 <= abs(ep_red) <= 50.0 or 0.45 <= abs(ep_red) <= 0.50)) and (
        turn_runway is not None and turn_runway >= 21.5
    ):
        c5 += 5
    if re.search(r"kill[\s-]*gate|thumbnail|6\.5%", memo, re.I) and re.search(r"swarm|dubbing|rough[\s-]*cut|back[\s-]*end|profit", memo, re.I):
        c5 += 5

    breakdown = {
        "c1_clean_execution_and_schema": c1,
        "c2_shorts_illusion_and_retention_decay": c2,
        "c3_asc606_restatement_and_makegood_liability": c3,
        "c4_insolvency_runway_and_expansion_veto": c4,
        "c5_blumhouse_mrbeast_ai_swarm_turnaround": c5,
    }
    return {"ok": ok, "status": msg, "objective_score_50": sum(breakdown.values()), "breakdown": breakdown, "findings": findings}


def _sanitize_blind_text(text: str, run_uuid8: str) -> str:
    """Strip any self-identifying persona/arm strings so single-blind Auditor packets have zero leakage."""
    cleaned = text.replace(f"run_{run_uuid8}", "director_workspace")
    cleaned = cleaned.replace(f"persona_{run_uuid8}", "assigned_mandate")
    cleaned = re.sub(r"\bSuperhuman\s+", "Independent ", cleaned, flags=re.I)
    cleaned = re.sub(r"\bsuperhuman_gov_[a-z0-9_]+\b", "fiduciary_director_profile", cleaned, flags=re.I)
    cleaned = re.sub(r"\bgov_[a-z0-9_]+\b", "fiduciary_board_seat", cleaned, flags=re.I)
    cleaned = re.sub(r"org-board-and-auditor-governance", "fiduciary-governance-framework", cleaned, flags=re.I)
    cleaned = re.sub(r"org-superhuman-role-synthesizer", "fiduciary-synthesis-framework", cleaned, flags=re.I)
    cleaned = re.sub(r"\bsh_[a-z0-9_]+\b", "director_profile", cleaned)
    cleaned = re.sub(r"\bOKG\b", "Enterprise", cleaned)
    cleaned = re.sub(r"Organizational Knowledge Graph", "Enterprise Operating Graph", cleaned, flags=re.I)
    cleaned = re.sub(r"\bSection\s+[478]\b", "Governance Charter", cleaned)
    cleaned = re.sub(r"\bQUALIFIED_ADVERSE_FINDING\b", "Qualified Adverse Audit Finding", cleaned)
    cleaned = re.sub(r"\bREJECT_AND_RESTRUCTURE\b", "Reject and Restructure", cleaned)
    cleaned = re.sub(r"\bCONDITIONAL_REMEDIATION\b", "Conditional Remediation", cleaned)
    cleaned = re.sub(r"\bUNQUALIFIED_APPROVAL\b", "Unqualified Approval", cleaned)
    cleaned = re.sub(
        r"\b(?:infra|fin|health|tech|consult|sec|ops|legal|media|creator)_([a-z0-9_]+)\b",
        lambda m: m.group(1).replace("_", " "),
        cleaned,
    )
    return cleaned


def run_all_evaluations_and_build_blind_packets() -> Dict[str, Any]:
    mapping = json.loads((PRIV_DIR / "arm_mapping.json").read_text(encoding="utf-8"))
    if BLIND_DIR.exists():
        shutil.rmtree(BLIND_DIR)
    BLIND_DIR.mkdir(parents=True, exist_ok=True)

    evaluators = {1: evaluate_case1, 2: evaluate_case2}
    results_by_uuid: Dict[str, Any] = {}
    by_case: Dict[int, List[Dict[str, Any]]] = {1: [], 2: []}

    for tr in mapping["trials"]:
        uid = tr["trial_uuid8"]
        cnum = tr["case_num"]
        rdir = Path(tr["run_dir"])
        ev = evaluators[cnum](rdir)
        scr_p, fnd_p, mem_p = rdir / "audit_analysis.py", rdir / "findings.json", rdir / "board_resolution_memo.md"
        ev["artifact_sizes_bytes"] = {
            "audit_analysis_py": scr_p.stat().st_size if scr_p.exists() else 0,
            "findings_json": fnd_p.stat().st_size if fnd_p.exists() else 0,
            "board_resolution_memo_md": mem_p.stat().st_size if mem_p.exists() else 0,
        }
        results_by_uuid[uid] = {**tr, "objective_eval": ev}
        by_case[cnum].append(tr)

    rng = random.Random(2026111015)
    blind_key: Dict[str, Dict[str, Any]] = {}
    for cnum in (1, 2):
        shuffled = list(by_case[cnum])
        rng.shuffle(shuffled)
        c_blind_dir = BLIND_DIR / f"case_{cnum}"
        c_blind_dir.mkdir(parents=True, exist_ok=True)
        blind_key[f"case_{cnum}"] = {}
        for label, tr in zip(["Director_A", "Director_B", "Director_C"], shuffled):
            uid = tr["trial_uuid8"]
            ddir = c_blind_dir / label
            ddir.mkdir(parents=True, exist_ok=True)
            rdir = Path(tr["run_dir"])
            for fname in ("audit_analysis.py", "findings.json", "board_resolution_memo.md"):
                src = rdir / fname
                if src.exists():
                    raw = src.read_text(encoding="utf-8")
                    (ddir / fname).write_text(_sanitize_blind_text(raw, uid), encoding="utf-8")
            blind_key[f"case_{cnum}"][label] = {
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
        print(f"Case {rec['case_num']} | {rec['arm']:17s} | run_{uid} -> {ev['objective_score_50']}/50 {ev['breakdown']}")
