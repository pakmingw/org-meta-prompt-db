#!/usr/bin/env python3
"""Helper CLI script for the org-company-deep-onboard skill."""

import argparse
import json
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from orgprompt.onboarding.engine import CompanyOnboardingEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="OrgPrompt Enterprise Deep Onboarding Helper")
    parser.add_argument("company_name", help="Enterprise company name")
    parser.add_argument("--ticker", "-t", default=None, help="Stock ticker symbol or 'PRIVATE'")
    parser.add_argument("--industry", "-i", default="Finance", help="Macro industry sector")
    parser.add_argument("--subsector", "-s", default="Financial Technology & Infrastructure", help="Subsector")
    parser.add_argument("--revenue", "-r", type=float, default=10.0, help="Annual revenue in billions")
    parser.add_argument("--challenges", "-c", default=None, help="Core challenges (semicolon-separated)")
    parser.add_argument("--research-file", "-rf", default=None, help="Path to deep research JSON dossier")
    parser.add_argument("--output-blueprint", "-o", default=None, help="Custom blueprint output path")
    parser.add_argument("--json", action="store_true", help="Output result as JSON")

    args = parser.parse_args()

    engine = CompanyOnboardingEngine.build_from_db()

    if args.research_file:
        res = engine.onboard_company(args.research_file, output_blueprint_path=args.output_blueprint)
    else:
        challenge_list = [c.strip() for c in args.challenges.split(";")] if args.challenges else []
        payload = {
            "name": args.company_name,
            "ticker": args.ticker or "PRIVATE",
            "macro_industry": args.industry,
            "sub_sector": args.subsector,
            "revenue_billions": args.revenue,
            "challenges": challenge_list,
        }
        res = engine.onboard_company(payload, output_blueprint_path=args.output_blueprint)

    if args.json:
        print(json.dumps(res.to_dict(), indent=2))
    else:
        print(f"\nSuccessfully Onboarded: {res.company_name} (#{res.rank})")
        print(f"Employed Roles: {res.employed_roles_count} | Bespoke Roles: {res.bespoke_roles_count}")
        print(f"Blueprint Generated: {res.blueprint_path}")
        print(f"Graph Invariant Validation: {'PASS' if res.is_valid else 'FAIL'}")
        if not res.is_valid:
            for v in res.violations:
                print(f"  Violation: {v}")
            sys.exit(1)


if __name__ == "__main__":
    main()
