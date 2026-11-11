#!/usr/bin/env python3
"""CLI helper for the `org-frontier-lab-enterprise-bridge` skill."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path("/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from orgprompt.frontier import FrontierLabJoinEngine  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Bridge real-world companies, roles, and problems to Nov 2026 Frontier AI Labs.")
    parser.add_argument("--lab", help="Inspect a specific Frontier AI Lab (anthropic, openai, google_deepmind, meta_msl, mistral_ai).")
    parser.add_argument("--company", help="Company name or slug to join (e.g. 'Orange France', 'Beast Industries').")
    parser.add_argument("--role", help="Canonical role slug or query to join to Frontier Lab roles.")
    parser.add_argument("--problem", help="Problem statement to bridge across HybridSearch enterprise roles + Frontier Pods.")
    parser.add_argument("--focus", default=None, help="Optional division/keyword focus for --company.")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format.")
    parser.add_argument("--output", default=None, help="Optional file path to save output.")
    parser.add_argument("--db-path", default=None, help="Optional SQLite DB path override.")
    args = parser.parse_args()

    with FrontierLabJoinEngine(args.db_path) as eng:
        if args.problem:
            res = eng.bridge_problem(args.problem, company_name_or_slug=args.company)
        elif args.role:
            res = eng.join_role(args.role, company_name_or_slug=args.company)
        elif args.company:
            res = eng.join_company(args.company, focus=args.focus)
        elif args.lab:
            res = eng.inspect_lab(args.lab)
        else:
            labs = eng.list_labs()
            for l in labs:
                print(f"- {l.name} ({l.slug}): {len(l.pods)} pods | {', '.join(l.flagship_models[:2])}")
            return 0

    if args.output:
        saved = res.save(args.output, format=args.format)
        print(f"Saved Frontier Bridge artifact to: {saved}")
        return 0

    print(res.to_json() if args.format == "json" else res.to_markdown())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
