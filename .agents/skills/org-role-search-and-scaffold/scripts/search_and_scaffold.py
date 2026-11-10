#!/usr/bin/env python3
"""Helper CLI script for the org-role-search-and-scaffold skill."""

import argparse
import json
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from orgprompt.scaffolder.company_scaffolder import CompanyScaffolder
from orgprompt.scaffolder.role_scaffolder import RoleScaffolder
from orgprompt.search.hybrid import HybridSearchEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="OrgPrompt Search & Scaffold Helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search sub-command
    search_p = subparsers.add_parser("search", help="Search roles using hybrid semantic retrieval")
    search_p.add_argument("--query", "-q", required=True, help="Search query string")
    search_p.add_argument("--top-k", "-k", type=int, default=5, help="Number of results to return")
    search_p.add_argument("--json", action="store_true", help="Output results as JSON")

    # Scaffold role sub-command
    scaffold_role_p = subparsers.add_parser("scaffold-role", help="Scaffold role runbook")
    scaffold_role_p.add_argument("role_id_or_slug", help="Role ID or slug")
    scaffold_role_p.add_argument("--company", "-c", default=None, help="Company context")
    scaffold_role_p.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown", help="Output format")
    scaffold_role_p.add_argument("--output", "-o", default=None, help="Output file path")

    # Scaffold company sub-command
    scaffold_comp_p = subparsers.add_parser("scaffold-company", help="Scaffold company runbook")
    scaffold_comp_p.add_argument("name_or_ticker", help="Company name or ticker")
    scaffold_comp_p.add_argument("--division", "-d", default=None, help="Division filter")
    scaffold_comp_p.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown", help="Output format")
    scaffold_comp_p.add_argument("--output", "-o", default=None, help="Output file path")

    args = parser.parse_args()

    if args.command == "search":
        engine = HybridSearchEngine.build_from_db()
        results = engine.search(args.query, top_k=args.top_k)
        if args.json:
            out = [
                {
                    "rank": r.final_rank,
                    "name": r.name,
                    "slug": r.slug,
                    "role_id": r.role_id,
                    "rrf_score": r.rrf_score,
                    "sparse_rank": r.sparse_rank,
                    "dense_rank": r.dense_rank,
                }
                for r in results
            ]
            print(json.dumps(out, indent=2))
        else:
            print(f"Hybrid Search Results for '{args.query}':\n")
            for r in results:
                print(f"[{r.final_rank}] {r.name} (`{r.slug}`) - RRF: {r.rrf_score:.4f} (BM25 #{r.sparse_rank}, Dense #{r.dense_rank})")

    elif args.command == "scaffold-role":
        scaffolder = RoleScaffolder.build_from_db()
        pkg = scaffolder.scaffold_role(args.role_id_or_slug, company_name=args.company)
        if args.output:
            pkg.save(args.output, format=args.format)
            print(f"Saved role runbook to {args.output}")
        elif args.format == "json":
            print(pkg.to_json())
        else:
            print(pkg.to_markdown())

    elif args.command == "scaffold-company":
        scaffolder = CompanyScaffolder.build_from_db()
        pkg = scaffolder.scaffold_company(args.name_or_ticker, division=args.division)
        if args.output:
            pkg.save(args.output, format=args.format)
            print(f"Saved company runbook to {args.output}")
        elif args.format == "json":
            print(pkg.to_json())
        else:
            print(pkg.to_markdown())


if __name__ == "__main__":
    main()
