#!/usr/bin/env python3
"""Standalone CLI helper for `org-board-and-auditor-governance` skill.

Assembles an industry/company Board & Independent Audit Slate and optionally synthesizes
a tailored 8-Section Superhuman Board Director / Auditor dossier.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path("/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from orgprompt.governance import (  # noqa: E402
    SuperhumanGovernanceSynthesizer,
    board_for_company,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Fiduciary Board & Independent Auditor Slate + Superhuman Synthesis")
    parser.add_argument("--company", "-c", help="Target company name/slug (e.g., 'Orange France', 'A24')")
    parser.add_argument("--industry", "-i", help="Target macro industry slug (e.g., 'telecommunications', 'creative_media')")
    parser.add_argument("--stage", "-s", choices=["PUBLIC_ENTERPRISE", "VENTURE_OR_BOUTIQUE"], default=None)
    parser.add_argument("--problem", "-p", default=None, help="Optional audit/governance problem to synthesize a Superhuman profile")
    parser.add_argument("--role", "-r", default=None, help="Optional base governance role slug")
    parser.add_argument("--db-path", default=str(REPO_ROOT / "data" / "org_knowledge_base.db"))
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", "-o", default=None, help="Optional output file path")
    args = parser.parse_args()

    target = args.company or args.industry or "technology_ai"
    slate = board_for_company(target, stage=args.stage, db_path_or_conn=args.db_path)

    if args.problem:
        synth = SuperhumanGovernanceSynthesizer(args.db_path)
        pkg = synth.synthesize(
            problem=args.problem,
            role_slug_or_id=args.role,
            company_or_industry=target,
            persist=False,
        )
        rendered = pkg.to_json() if args.format == "json" else (slate.to_markdown() + "\n---\n\n" + pkg.to_markdown())
    else:
        rendered = slate.to_json() if args.format == "json" else slate.to_markdown()

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered, encoding="utf-8")
        print(f"Wrote governance dossier to {out}")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
