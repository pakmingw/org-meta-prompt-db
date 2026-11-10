#!/usr/bin/env python3
"""Prepare 9 isolated, randomized solver trial directories & verbatim persona files for Phase 13."""

from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent.parent
DB_PATH = REPO_ROOT / "data" / "org_knowledge_base.db"
SH_DIR = REPO_ROOT / "artifacts" / "superhuman_roles"
RUNS_DIR = BASE_DIR / "runs"
PRIV_DIR = BASE_DIR / "private_key"
PERSONA_DIR = PRIV_DIR / "personas"


def main() -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    PERSONA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))

    sh1 = json.loads((SH_DIR / "superhuman_1_zns_raft_ledger.json").read_text(encoding="utf-8"))
    sh2 = json.loads((SH_DIR / "superhuman_2_cfo_tariff_shock.json").read_text(encoding="utf-8"))
    sh3 = json.loads((SH_DIR / "superhuman_3_clinical_sepsis_samd.json").read_text(encoding="utf-8"))

    def get_canonical_prompt(role_id: str) -> tuple[str, str, str]:
        row = conn.execute(
            "SELECT id, slug, name, system_prompt FROM canonical_roles WHERE id = ?",
            (role_id,),
        ).fetchone()
        if not row:
            raise RuntimeError(f"Missing canonical role {role_id}")
        return row[0], row[2], row[3]

    c1_id, c1_name, c1_prompt = get_canonical_prompt(sh1["mapped_okg_anchor_role_id"])
    c2_id, c2_name, c2_prompt = get_canonical_prompt(sh2["mapped_okg_anchor_role_id"])
    c3_id, c3_name, c3_prompt = get_canonical_prompt(sh3["mapped_okg_anchor_role_id"])

    tasks_spec = [
        {
            "task_num": 1,
            "task_id": "task1_zns_raft",
            "task_dir": str(BASE_DIR / "tasks" / "task1_zns_raft"),
            "input_file": str(BASE_DIR / "tasks" / "task1_zns_raft" / "input_workload.json"),
            "role_label": "Distributed Storage & Settlement Systems Specialist",
            "arms": {
                "Arm_1_Baseline": {
                    "persona_source": "Generic 2-Sentence Specialist Prompt",
                    "prompt": (
                        "You are an experienced Principal Distributed Systems and Storage Engineer specializing "
                        "in Raft consensus protocols, NVMe storage engines, and financial payment ledgers. "
                        "Deliver rigorous, production-grade simulation code, accurate metrics, and a clear architectural RFC."
                    ),
                },
                "Arm_2_Canonical": {
                    "persona_source": f"Canonical OKG Role ({c1_id}: {c1_name})",
                    "prompt": c1_prompt,
                },
                "Arm_3_Superhuman": {
                    "persona_source": f"Superhuman Pathway A ({sh1['id']}: {sh1['title']})",
                    "prompt": sh1["deep_superhuman_prompt"],
                },
            },
        },
        {
            "task_num": 2,
            "task_id": "task2_tariff_shock",
            "task_dir": str(BASE_DIR / "tasks" / "task2_tariff_shock"),
            "input_file": str(BASE_DIR / "tasks" / "task2_tariff_shock" / "baseline_financials.json"),
            "role_label": "Corporate Finance & Quantitative Risk Specialist",
            "arms": {
                "Arm_1_Baseline": {
                    "persona_source": "Generic 2-Sentence Specialist Prompt",
                    "prompt": (
                        "You are an experienced Chief Financial Officer and Quantitative Corporate Treasury Strategist "
                        "for a global semiconductor hardware enterprise. Deliver an accurate 3-statement Monte Carlo "
                        "financial simulation, verified metrics, and an actionable CFO Board capital-allocation memo."
                    ),
                },
                "Arm_2_Canonical": {
                    "persona_source": f"Canonical OKG Role ({c2_id}: {c2_name})",
                    "prompt": c2_prompt,
                },
                "Arm_3_Superhuman": {
                    "persona_source": f"Superhuman Pathway B ({sh2['id']}: {sh2['title']})",
                    "prompt": sh2["deep_superhuman_prompt"],
                },
            },
        },
        {
            "task_num": 3,
            "task_id": "task3_clinical_sepsis",
            "task_dir": str(BASE_DIR / "tasks" / "task3_clinical_sepsis"),
            "input_file": str(BASE_DIR / "tasks" / "task3_clinical_sepsis" / "sepsis_cohort.csv"),
            "role_label": "Clinical Biostatistics & Medical AI Safety Specialist",
            "arms": {
                "Arm_1_Baseline": {
                    "persona_source": "Generic 2-Sentence Specialist Prompt",
                    "prompt": (
                        "You are an experienced Principal Clinical Biostatistician and Medical AI Regulatory Safety "
                        "Specialist focusing on acute-care decision support and FDA SaMD compliance. Deliver rigorous "
                        "cohort evaluation code, calibrated subgroup metrics, and a complete clinical safety protocol."
                    ),
                },
                "Arm_2_Canonical": {
                    "persona_source": f"Canonical OKG Role ({c3_id}: {c3_name})",
                    "prompt": c3_prompt,
                },
                "Arm_3_Superhuman": {
                    "persona_source": f"Superhuman Pathway C ({sh3['id']}: {sh3['title']})",
                    "prompt": sh3["deep_superhuman_prompt"],
                },
            },
        },
    ]

    rng_ns = uuid.UUID("651faa68-d992-466c-8de1-d6b3baa2c3b8")
    trials = []
    for t in tasks_spec:
        for arm_key, arm_info in t["arms"].items():
            uid8 = uuid.uuid5(rng_ns, f"{t['task_id']}::{arm_key}").hex[:8]
            run_dir = RUNS_DIR / f"run_{uid8}"
            run_dir.mkdir(parents=True, exist_ok=True)
            persona_path = PERSONA_DIR / f"persona_{uid8}.md"
            persona_path.write_text(arm_info["prompt"], encoding="utf-8")
            trials.append({
                "trial_uuid8": uid8,
                "task_num": t["task_num"],
                "task_id": t["task_id"],
                "arm": arm_key,
                "persona_source": arm_info["persona_source"],
                "persona_char_count": len(arm_info["prompt"]),
                "persona_path": str(persona_path),
                "task_md_path": str(Path(t["task_dir"]) / "TASK.md"),
                "input_file_path": t["input_file"],
                "run_dir": str(run_dir),
                "role_label": t["role_label"],
            })

    mapping_path = PRIV_DIR / "arm_mapping.json"
    mapping_path.write_text(json.dumps({"trials": trials}, indent=2), encoding="utf-8")
    for tr in trials:
        print(f"Prepared run_{tr['trial_uuid8']} | Task {tr['task_num']} | {tr['arm']} ({tr['persona_char_count']} chars)")


if __name__ == "__main__":
    main()
