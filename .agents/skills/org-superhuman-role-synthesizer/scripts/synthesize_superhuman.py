#!/usr/bin/env python3
"""CLI helper script for the org-superhuman-role-synthesizer Antigravity skill."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def _bootstrap_repo_path() -> None:
    """Ensure `orgprompt` is importable whether invoked from workspace or global skill dir."""
    candidates: List[Path] = []
    env_root = os.environ.get("ORGPROMPT_ROOT")
    if env_root:
        candidates.append(Path(env_root).expanduser().resolve())

    # Workspace skill path: <repo>/.agents/skills/org-superhuman-role-synthesizer/scripts/synthesize_superhuman.py
    script_path = Path(__file__).resolve()
    if len(script_path.parents) >= 5:
        candidates.append(script_path.parents[4])

    candidates.append(Path.cwd().resolve())
    candidates.append(
        Path("/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db")
    )

    for candidate in candidates:
        if (candidate / "orgprompt" / "__init__.py").is_file():
            cand_str = str(candidate)
            if cand_str not in sys.path:
                sys.path.insert(0, cand_str)
            break


_bootstrap_repo_path()

from orgprompt.superhuman import SuperhumanRoleSynthesizer  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Synthesize, list, or inspect Polymathic Superhuman Role Definitions, "
            "Perfect Human Pedigrees, and 5-Stage Unknown-Problem Meta-Prompts."
        )
    )
    parser.add_argument(
        "action",
        nargs="?",
        choices=["synthesize", "list", "inspect"],
        default="synthesize",
        help="Optional action: synthesize (default), list, or inspect",
    )
    parser.add_argument(
        "target_id_or_slug",
        nargs="?",
        default=None,
        help="Profile ID or slug when action is 'inspect'",
    )
    parser.add_argument(
        "--problem",
        "-p",
        default=None,
        help="Target enterprise, scientific, or out-of-distribution problem statement",
    )
    parser.add_argument(
        "--role",
        "-r",
        default=None,
        help="Canonical OKG role ID or slug to expand into a Superhuman Role",
    )
    parser.add_argument(
        "--custom-role-file",
        "-crf",
        default=None,
        help="Path to JSON or Markdown/text custom role definition supplied by an agent",
    )
    parser.add_argument(
        "--custom-role-title",
        default=None,
        help="Inline custom role title when expanding an ad-hoc agent role without a file",
    )
    parser.add_argument(
        "--custom-role-prompt",
        default=None,
        help="Inline custom role prompt/mission when expanding an ad-hoc agent role",
    )
    parser.add_argument(
        "--company",
        "-c",
        default=None,
        help="Optional enterprise company context (e.g., 'Orange France', 'NVIDIA', 'Walmart')",
    )
    parser.add_argument(
        "--developer-context",
        "-dc",
        default=None,
        help="Developer-complemented proprietary constraints, SLAs, architecture notes",
    )
    parser.add_argument(
        "--context-file",
        "-cf",
        default=None,
        help="Path to developer context file to inject into the Superhuman Role",
    )
    parser.add_argument(
        "--adjacent-k",
        type=int,
        default=4,
        help="Maximum number of adjacent OKG roles to fuse across 5 edge types (default: 4)",
    )
    parser.add_argument(
        "--persist",
        action="store_true",
        help="Persist synthesized profile into superhuman_role_profiles SQLite table",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "md", "json"],
        default="markdown",
        help="Output format: markdown or json (default: markdown)",
    )
    parser.add_argument(
        "--json",
        dest="json_flag",
        action="store_true",
        help="Shortcut flag to emit JSON output",
    )
    parser.add_argument(
        "--output",
        "-o",
        default=None,
        help="Optional file path to write the rendered Superhuman Role Package",
    )
    parser.add_argument(
        "--db-path",
        default=None,
        help="Optional SQLite database path override (defaults to data/org_knowledge_base.db)",
    )
    return parser


def _resolve_custom_role(args: argparse.Namespace) -> Optional[Any]:
    if args.custom_role_file:
        file_path = Path(args.custom_role_file)
        if not file_path.is_file():
            raise FileNotFoundError(f"Custom role file not found: {file_path}")
        return file_path
    if args.custom_role_title or args.custom_role_prompt:
        spec: Dict[str, Any] = {}
        if args.custom_role_title:
            spec["name"] = args.custom_role_title
            spec["title"] = args.custom_role_title
        if args.custom_role_prompt:
            spec["system_prompt"] = args.custom_role_prompt
            spec["mission"] = args.custom_role_prompt
        return spec
    return None


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    out_fmt = "json" if args.json_flag or args.format == "json" else "markdown"

    try:
        synthesizer = SuperhumanRoleSynthesizer.build_from_db(db_path=args.db_path)
        try:
            if args.action == "list":
                profiles = synthesizer.list_profiles()
                if out_fmt == "json":
                    rendered = json.dumps(profiles, indent=2)
                else:
                    lines = [f"# Persisted Superhuman Role Profiles ({len(profiles)})", ""]
                    for item in profiles:
                        lines.append(
                            f"- **{item.get('title')}** (`{item.get('slug')}`) — "
                            f"ID: `{item.get('id')}` | Problem: {item.get('problem_statement', '')}"
                        )
                    rendered = "\n".join(lines)
                if args.output:
                    out_p = Path(args.output)
                    out_p.parent.mkdir(parents=True, exist_ok=True)
                    out_p.write_text(rendered, encoding="utf-8")
                else:
                    print(rendered)
                return 0

            if args.action == "inspect":
                target = args.target_id_or_slug or args.role
                if not target or not str(target).strip():
                    raise ValueError("Profile ID or slug is required for 'inspect'.")
                pkg = synthesizer.get_profile(target)
                if args.output:
                    pkg.save(args.output, format=out_fmt)
                    print(f"Saved inspected Superhuman Role Package to {args.output}")
                elif out_fmt == "json":
                    print(pkg.to_json())
                else:
                    print(pkg.to_markdown())
                return 0

            custom_spec = _resolve_custom_role(args)
            pkg = synthesizer.synthesize(
                problem=args.problem,
                role=args.role,
                custom_role_spec=custom_spec,
                company=args.company,
                developer_context=args.developer_context,
                context_file=args.context_file,
                adjacent_k=args.adjacent_k,
                persist=args.persist,
            )

            if args.output:
                pkg.save(args.output, format=out_fmt)
                if out_fmt == "json":
                    print(
                        json.dumps(
                            {
                                "id": pkg.id,
                                "slug": pkg.slug,
                                "title": pkg.title,
                                "output": str(args.output),
                                "prompt_character_count": pkg.prompt_character_count,
                            },
                            indent=2,
                        )
                    )
                else:
                    print(f"Saved Superhuman Role Package ({pkg.slug}) to {args.output}")
            elif out_fmt == "json":
                print(pkg.to_json())
            else:
                print(pkg.to_markdown())
            return 0
        finally:
            if hasattr(synthesizer, "close"):
                synthesizer.close()
    except (ValueError, KeyError, FileNotFoundError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
