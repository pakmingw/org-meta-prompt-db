#!/usr/bin/env python3
"""Prepare 6 isolated, UUID-anonymized Boardroom & Auditor solver trials for Phase 15."""

from __future__ import annotations

import json
import sqlite3
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent.parent
DB_PATH = REPO_ROOT / "data" / "org_knowledge_base.db"
RUNS_DIR = BASE_DIR / "runs"
PRIV_DIR = BASE_DIR / "private_key"
PERSONA_DIR = PRIV_DIR / "personas"


def main() -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    PERSONA_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(DB_PATH))

    def get_typical_gov_role(slug: str) -> tuple[str, str, str]:
        row = conn.execute(
            "SELECT id, title, system_prompt FROM governance_roles WHERE slug = ?",
            (slug,),
        ).fetchone()
        if not row:
            raise RuntimeError(f"Missing governance_roles slug={slug}")
        return row[0], row[1], row[2]

    def get_superhuman_gov_profile(slug: str) -> tuple[str, str, str, str]:
        row = conn.execute(
            "SELECT id, title, base_governance_role_slug, deep_superhuman_governance_prompt "
            "FROM superhuman_governance_profiles WHERE slug = ?",
            (slug,),
        ).fetchone()
        if not row:
            raise RuntimeError(f"Missing superhuman_governance_profiles slug={slug}")
        return row[0], row[1], row[2], row[3]

    # Case 1: Enterprise Forensic Audit & Capital Allocation (1-to-1 Base Seat vs Superhuman Expansion)
    sh1_id, sh1_title, sh1_base_slug, sh1_prompt = get_superhuman_gov_profile(
        "superhuman_gov_capital_allocation_board_director"
    )
    arm2_case1_slug = sh1_base_slug  # gov_capital_allocation_value_director
    g1_id, g1_title, g1_prompt = get_typical_gov_role(arm2_case1_slug)

    # Case 2: Venture Indie Film & Creator Media Studio Board Review
    sh2_id, sh2_title, sh2_base_slug, sh2_prompt = get_superhuman_gov_profile(
        "superhuman_gov_media_creator_board_partner"
    )
    g2_id, g2_title, g2_prompt = get_typical_gov_role("gov_media_creator_venture_board_partner")

    cases_spec = [
        {
            "case_num": 1,
            "case_id": "case1_enterprise_board_audit",
            "case_dir": str(BASE_DIR / "tasks" / "case1_enterprise_board_audit"),
            "deck_file": str(BASE_DIR / "tasks" / "case1_enterprise_board_audit" / "management_board_deck.md"),
            "packet_file": str(
                BASE_DIR / "tasks" / "case1_enterprise_board_audit" / "financial_and_operational_packet.json"
            ),
            "role_label": "Independent Board Director & Forensic Audit Reviewer (Enterprise Telecom/Cloud)",
            "arms": {
                "Arm_1_Baseline": {
                    "persona_source": "Generic 2-Sentence Board Advisor & Auditor Prompt",
                    "prompt": (
                        "You are an experienced Independent Corporate Board Director and Financial Auditor "
                        "advising a public European cloud and telecommunications enterprise. Review management's "
                        "quarterly board packet rigorously, verify all financial figures in Python, and deliver "
                        "a clear Board & Audit Committee resolution memo."
                    ),
                },
                "Arm_2_Typical_Gov": {
                    "persona_source": f"Typical Governance Role ({arm2_case1_slug}: {g1_title})",
                    "prompt": g1_prompt,
                },
                "Arm_3_Superhuman_Gov": {
                    "persona_source": f"Superhuman Governance Role (superhuman_gov_capital_allocation_board_director: {sh1_title})",
                    "prompt": sh1_prompt,
                },
            },
        },
        {
            "case_num": 2,
            "case_id": "case2_creator_studio_board",
            "case_dir": str(BASE_DIR / "tasks" / "case2_creator_studio_board"),
            "deck_file": str(BASE_DIR / "tasks" / "case2_creator_studio_board" / "management_board_deck.md"),
            "packet_file": str(
                BASE_DIR / "tasks" / "case2_creator_studio_board" / "studio_financial_and_channel_packet.json"
            ),
            "role_label": "Series B Board Director & Studio Audit Reviewer (Film & Creator Media)",
            "arms": {
                "Arm_1_Baseline": {
                    "persona_source": "Generic 2-Sentence Studio Board Member Prompt",
                    "prompt": (
                        "You are an experienced Venture Board Member and Financial Advisor to digital media "
                        "and entertainment studios. Review management's Series B board packet rigorously, "
                        "verify all channel and financial metrics in Python, and deliver a clear Board resolution memo."
                    ),
                },
                "Arm_2_Typical_Gov": {
                    "persona_source": f"Typical Governance Role (gov_media_creator_venture_board_partner: {g2_title})",
                    "prompt": g2_prompt,
                },
                "Arm_3_Superhuman_Gov": {
                    "persona_source": f"Superhuman Governance Role (superhuman_gov_media_creator_board_partner: {sh2_title})",
                    "prompt": sh2_prompt,
                },
            },
        },
    ]

    rng_ns = uuid.UUID("91f8b3c2-4a77-4d19-8e23-5c81a904e715")
    trials = []
    for c in cases_spec:
        for arm_key, arm_info in c["arms"].items():
            uid8 = uuid.uuid5(rng_ns, f"{c['case_id']}::{arm_key}").hex[:8]
            run_dir = RUNS_DIR / f"run_{uid8}"
            run_dir.mkdir(parents=True, exist_ok=True)
            persona_path = PERSONA_DIR / f"persona_{uid8}.md"
            persona_path.write_text(arm_info["prompt"], encoding="utf-8")
            trials.append({
                "trial_uuid8": uid8,
                "case_num": c["case_num"],
                "case_id": c["case_id"],
                "arm": arm_key,
                "persona_source": arm_info["persona_source"],
                "persona_char_count": len(arm_info["prompt"]),
                "persona_path": str(persona_path),
                "task_md_path": str(Path(c["case_dir"]) / "TASK.md"),
                "deck_file_path": c["deck_file"],
                "packet_file_path": c["packet_file"],
                "run_dir": str(run_dir),
                "role_label": c["role_label"],
            })

    (PRIV_DIR / "arm_mapping.json").write_text(json.dumps({"trials": trials}, indent=2), encoding="utf-8")
    for tr in trials:
        print(f"Prepared run_{tr['trial_uuid8']} | Case {tr['case_num']} | {tr['arm']} ({tr['persona_char_count']} chars)")


if __name__ == "__main__":
    main()
