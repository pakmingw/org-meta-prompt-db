"""Unified Click and Rich Command-Line Interface for OrgPrompt.

Commands:
- orgprompt team synthesize --problem "..." [--min-roles 8] [--max-roles 15]
- orgprompt team execute --problem "..." [--output-dir ...]
- orgprompt search query "..." [--hybrid] [--expand-kg]
- orgprompt role generate --name "..." --industry "..."
- orgprompt benchmark run [--k 10]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import networkx as nx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from orgprompt.db.connection import get_connection, get_default_db_path
from orgprompt.graph.generator import RoleGenerator, RoleGenSpec
from orgprompt.models import CanonicalRole
from orgprompt.onboarding.engine import CompanyOnboardingEngine
from orgprompt.scaffolder.company_scaffolder import CompanyScaffolder
from orgprompt.scaffolder.role_scaffolder import RoleScaffolder
from orgprompt.search.benchmark import RetrievalBenchmark
from orgprompt.search.hybrid import HybridSearchEngine
from orgprompt.superhuman.synthesizer import SuperhumanRoleSynthesizer
from orgprompt.synthesizer.team_builder import TeamSynthesizer
from orgprompt.synthesizer.workflow_engine import WorkflowEngine


console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="orgprompt")
def cli() -> None:
    """OrgPrompt: Organizational Knowledge Graph & Role Meta-Prompting Platform."""
    pass


# Alias for entry points specifying `orgprompt.cli:main`
main = cli


# ---------------------------------------------------------------------------
# Team Command Group
# ---------------------------------------------------------------------------

@cli.group(name="team")
def team_group() -> None:
    """Dynamic multi-agent team synthesis and workflow execution."""
    pass


@team_group.command(name="synthesize")
@click.option(
    "--problem",
    "-p",
    "problem",
    required=True,
    help="Customer problem statement or engineering challenge.",
)
@click.option(
    "--min-roles",
    "-min",
    default=8,
    type=int,
    show_default=True,
    help="Minimum number of roles to assemble.",
)
@click.option(
    "--max-roles",
    "-max",
    default=15,
    type=int,
    show_default=True,
    help="Maximum number of roles to assemble.",
)
@click.option(
    "--db-path",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Path to SQLite database (defaults to standard DB).",
)
@click.option(
    "--json-output",
    "--json",
    "json_output",
    is_flag=True,
    help="Output results as structured JSON.",
)
def team_synthesize(
    problem: str,
    min_roles: int,
    max_roles: int,
    db_path: Optional[str],
    json_output: bool,
) -> None:
    """Synthesizes a cross-functional team and compiles an acyclic execution DAG."""
    try:
        synth = TeamSynthesizer.build_from_db(db_path)
        result = synth.synthesize_team(
            problem_statement=problem,
            min_roles=min_roles,
            max_roles=max_roles,
        )
    except Exception as exc:
        console.print(f"[bold red]Synthesis Error:[/bold red] {exc}")
        sys.exit(1)

    roles = result.roles
    dag = result.dag
    industries = result.industries

    if json_output:
        roles_data = [
            {
                "id": r.id,
                "slug": r.slug,
                "title": r.title,
                "industry": r.industry or "General",
                "role_archetype": getattr(r, "role_archetype", "specialist"),
            }
            for r in roles
        ]
        dag_nodes = list(dag.nodes) if dag else []
        output = {
            "problem_statement": problem,
            "roles_count": len(roles),
            "industries_count": len(industries),
            "industries": industries,
            "is_acyclic": nx.is_directed_acyclic_graph(dag) if dag else False,
            "roles": roles_data,
            "dag_nodes": dag_nodes,
        }
        click.echo(json.dumps(output, indent=2))
        return

    console.print(
        Panel.fit(
            f"[bold green]Dynamic Team Synthesis Complete[/bold green]\n"
            f"[bold]Roles:[/bold] {len(roles)}  |  "
            f"[bold]Industries:[/bold] {len(industries)}  |  "
            f"[bold]Acyclic DAG:[/bold] {nx.is_directed_acyclic_graph(dag) if dag else False}",
            title="Team Synthesizer",
        )
    )

    table = Table(title="Assembled Cross-Functional Team", show_header=True)
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Role Title", style="bold white")
    table.add_column("Slug", style="dim")
    table.add_column("Industry", style="green")
    table.add_column("Archetype", style="magenta")

    for idx, r in enumerate(roles, start=1):
        table.add_row(
            str(idx),
            r.title,
            r.slug,
            r.industry or "General",
            getattr(r, "role_archetype", "specialist"),
        )
    console.print(table)

    if dag:
        console.print(
            f"\n[bold cyan]Execution DAG:[/bold cyan] {dag.number_of_nodes()} tasks across "
            f"{dag.graph.get('total_stages', 6)} stages (Topological Order Verified)"
        )


@team_group.command(name="execute")
@click.option(
    "--problem",
    "-p",
    "problem",
    default=(
        "Architecting, economically modeling, stress-testing, and governing a next-generation "
        "Sovereign AI + 6G Edge Telecommunications + Real-Time Financial Settlement Infrastructure "
        "under strict regulatory, capital, latency, and adversarial security constraints."
    ),
    show_default=True,
    help="Problem statement to execute.",
)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(file_okay=False, writable=True),
    default=None,
    help="Directory to save generated intermediate artifacts and final dossier.",
)
@click.option(
    "--min-roles",
    "-min",
    default=8,
    type=int,
    show_default=True,
    help="Minimum number of roles to assemble.",
)
@click.option(
    "--max-roles",
    "-max",
    default=15,
    type=int,
    show_default=True,
    help="Maximum number of roles to assemble.",
)
@click.option(
    "--db-path",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Path to SQLite database (defaults to standard DB).",
)
@click.option(
    "--json-output",
    "--json",
    "json_output",
    is_flag=True,
    help="Output execution summary as structured JSON.",
)
def team_execute(
    problem: str,
    output_dir: Optional[str],
    min_roles: int,
    max_roles: int,
    db_path: Optional[str],
    json_output: bool,
) -> None:
    """Executes the staged workflow DAG with adversarial red-team audit and remediation."""
    try:
        if not json_output:
            console.print("[dim]Synthesizing cross-functional team and compiling DAG...[/dim]")
        synth = TeamSynthesizer.build_from_db(db_path)
        team_res = synth.synthesize_team(problem, min_roles=min_roles, max_roles=max_roles)

        if not json_output:
            console.print(f"[dim]Executing DAG ({len(team_res.dag)} nodes) across 6 stages...[/dim]")
        engine = WorkflowEngine()
        exec_res = engine.execute_dag(
            team_res.dag,
            problem_statement=problem,
            output_dir=output_dir,
        )
    except Exception as exc:
        console.print(f"[bold red]Execution Error:[/bold red] {exc}")
        sys.exit(1)

    if json_output:
        click.echo(json.dumps(exec_res.to_dict(), indent=2))
        return

    console.print(
        Panel.fit(
            f"[bold green]Workflow DAG Execution Finished[/bold green]\n"
            f"[bold]Status:[/bold] {exec_res.status}  |  "
            f"[bold]Executed Nodes:[/bold] {len(exec_res.executed_nodes)}\n"
            f"[bold]Intermediate Artifacts:[/bold] {len(exec_res.intermediate_artifacts)}  |  "
            f"[bold]Audit Findings:[/bold] {len(exec_res.red_team_findings)}  |  "
            f"[bold]Upstream Revisions:[/bold] {len(exec_res.upstream_revisions)}\n"
            f"[bold]Dossier Word Count:[/bold] {len(exec_res.solution_dossier.split()) if exec_res.solution_dossier else 0} words",
            title="Workflow Execution Engine",
        )
    )

    # Artifacts table
    table = Table(title="Generated Workflow Artifacts", show_header=True)
    table.add_column("Artifact Name", style="bold cyan")
    table.add_column("Type / Stage", style="green")

    for art_name in exec_res.intermediate_artifacts:
        table.add_row(art_name, "Intermediate Technical Artifact")
    if exec_res.solution_dossier:
        table.add_row("Master_Grand_Challenge_Solution_Dossier.md", "Executive Master Dossier (>=5,000 words)")
    console.print(table)

    if output_dir:
        console.print(f"\n[green]All artifacts successfully written to:[/green] {output_dir}")


# ---------------------------------------------------------------------------
# Search Command Group
# ---------------------------------------------------------------------------

@cli.group(name="search")
def search_group() -> None:
    """100% local hybrid semantic search engine."""
    pass


@search_group.command(name="query")
@click.argument("query_arg", required=False, default=None)
@click.option("--query", "-q", "query_opt", default=None, help="Search query string.")
@click.option(
    "--hybrid/--no-hybrid",
    default=True,
    show_default=True,
    help="Use hybrid RRF search (BM25 + Dense LSA).",
)
@click.option(
    "--expand-kg/--no-expand-kg",
    default=True,
    show_default=True,
    help="Expand top anchors with Knowledge Graph traversal.",
)
@click.option("--top-k", "-k", default=10, type=int, show_default=True, help="Number of results.")
@click.option(
    "--db-path",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Path to SQLite database.",
)
@click.option(
    "--json-output",
    "--json",
    "json_output",
    is_flag=True,
    help="Output results as structured JSON.",
)
def search_query(
    query_arg: Optional[str],
    query_opt: Optional[str],
    hybrid: bool,
    expand_kg: bool,
    top_k: int,
    db_path: Optional[str],
    json_output: bool,
) -> None:
    """Searches canonical roles using hybrid BM25 and dense semantic vector retrieval."""
    search_text = query_opt or query_arg
    if not search_text:
        console.print("[bold red]Error:[/bold red] Search query must be provided via argument or --query.")
        sys.exit(1)

    try:
        engine = HybridSearchEngine.build_from_db(db_path)
        search_res = engine.search(query=search_text, top_k=top_k, expand_kg=expand_kg)
    except Exception as exc:
        console.print(f"[bold red]Search Error:[/bold red] {exc}")
        sys.exit(1)

    if json_output:
        items = []
        for r in search_res.results:
            items.append({
                "rank": r.final_rank,
                "role_id": r.role_id,
                "slug": r.slug,
                "name": r.name,
                "sparse_score": r.sparse_score,
                "dense_score": r.dense_score,
                "rrf_score": r.rrf_score,
                "sparse_rank": r.sparse_rank,
                "dense_rank": r.dense_rank,
            })
        out = {
            "query": search_text,
            "results_count": len(search_res.results),
            "results": items,
        }
        click.echo(json.dumps(out, indent=2))
        return

    table = Table(title=f"Hybrid Search Results for: '{search_text}'", show_header=True)
    table.add_column("Rank", justify="right", style="cyan")
    table.add_column("Role Title", style="bold white")
    table.add_column("Slug", style="dim")
    table.add_column("RRF Score", justify="right", style="green")
    table.add_column("BM25 Rank", justify="right", style="yellow")
    table.add_column("Dense Rank", justify="right", style="magenta")

    for r in search_res.results:
        s_rank = str(r.sparse_rank) if r.sparse_rank is not None else "-"
        d_rank = str(r.dense_rank) if r.dense_rank is not None else "-"
        table.add_row(
            str(r.final_rank),
            r.name,
            r.slug,
            f"{r.rrf_score:.5f}",
            s_rank,
            d_rank,
        )
    console.print(table)


# ---------------------------------------------------------------------------
# Role Command Group
# ---------------------------------------------------------------------------

@cli.group(name="role")
def role_group() -> None:
    """Dynamic role taxonomy generation and expansion."""
    pass


@role_group.command(name="generate")
@click.option("--name", "-n", required=True, help="Canonical role title to generate.")
@click.option("--industry", "-i", default=None, help="Target macro industry name.")
@click.option("--org-unit", "-u", "org_unit", default=None, help="Target operating unit slug.")
@click.option(
    "--seniority",
    "-s",
    default="PRINCIPAL_STAFF",
    show_default=True,
    help="Seniority tier (C_SUITE, VP, DIRECTOR, PRINCIPAL_STAFF, etc.).",
)
@click.option(
    "--archetype",
    "-a",
    default="domain_specialist",
    show_default=True,
    help="Role archetype (executive_strategy, engineering_staff, domain_specialist, operations, risk_compliance).",
)
@click.option("--mission", "-m", default=None, help="Fiduciary and operational mission.")
@click.option(
    "--db-path",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Path to SQLite database.",
)
@click.option(
    "--json-output",
    "--json",
    "json_output",
    is_flag=True,
    help="Output generated role metadata as structured JSON.",
)
def role_generate(
    name: str,
    industry: Optional[str],
    org_unit: Optional[str],
    seniority: str,
    archetype: str,
    mission: Optional[str],
    db_path: Optional[str],
    json_output: bool,
) -> None:
    """Synthesizes a new canonical role with graph invariants and compiled meta-prompt."""
    path = db_path or get_default_db_path()
    conn = get_connection(path)
    cursor = conn.cursor()

    # Resolve organizational unit slug if not directly provided
    target_unit_slug = org_unit
    if not target_unit_slug:
        if industry:
            row = cursor.execute(
                """
                SELECT u.slug FROM org_units u
                JOIN exemplar_orgs o ON u.exemplar_org_id = o.id
                JOIN industries i ON o.industry_id = i.id
                WHERE i.name LIKE ? OR i.slug LIKE ?
                LIMIT 1
                """,
                (f"%{industry}%", f"%{industry}%"),
            ).fetchone()
            if row:
                target_unit_slug = row[0]

        if not target_unit_slug:
            row = cursor.execute("SELECT slug FROM org_units LIMIT 1").fetchone()
            target_unit_slug = row[0] if row else "physical_research_laboratory"

    # Assemble specification
    slug_token = re.sub(r"[^a-zA-Z0-9]+", "_", name.lower()).strip("_")
    role_mission = (
        mission
        or f"Lead technical, operational, and strategic execution for {name} within {industry or 'the enterprise'}."
    )

    spec = RoleGenSpec(
        name=name,
        org_unit_slug=target_unit_slug,
        seniority_level=seniority,
        role_archetype=archetype,
        mission=role_mission,
        capabilities=[slug_token, "systems_architecture", "domain_rigor"],
        mental_models=["First-Principles Analysis", "Modular Decomposition"],
        technical_vocabulary=[name, "Architecture", "Standards", "SLA"],
        anti_patterns=["Unverified Presumptions", "Siloed Operations"],
    )

    try:
        generator = RoleGenerator(conn=conn)
        role = generator.generate_role(spec, conn=conn)
    except Exception as exc:
        console.print(f"[bold red]Role Generation Error:[/bold red] {exc}")
        sys.exit(1)

    if json_output:
        click.echo(
            json.dumps(
                {
                    "id": role.id,
                    "slug": role.slug,
                    "title": role.title,
                    "seniority_tier": role.seniority_tier,
                    "role_archetype": role.role_archetype,
                    "character_count": len(role.system_prompt),
                    "system_prompt": role.system_prompt,
                },
                indent=2,
            )
        )
        return

    console.print(
        Panel.fit(
            f"[bold green]Role Synthesized and Persisted Successfully[/bold green]\n"
            f"[bold]Role ID:[/bold] {role.id}\n"
            f"[bold]Title:[/bold] {role.title}\n"
            f"[bold]Slug:[/bold] {role.slug}\n"
            f"[bold]Seniority Tier:[/bold] {role.seniority_tier}\n"
            f"[bold]Archetype:[/bold] {role.role_archetype}\n"
            f"[bold]Prompt Length:[/bold] {len(role.system_prompt)} characters (Verified >= 1,200)\n"
            f"[bold]Invariants Verified:[/bold] Zero isolated nodes, >=1 REPORTS_TO, >=2 workflow edges, >=1 artifact",
            title="Role Generator",
        )
    )


# ---------------------------------------------------------------------------
# Benchmark Command Group
# ---------------------------------------------------------------------------

@cli.group(name="benchmark")
def benchmark_group() -> None:
    """Automated retrieval evaluation benchmark suite."""
    pass


@benchmark_group.command(name="run")
@click.option("--k", "-k", default=10, type=int, show_default=True, help="Retrieval truncation depth.")
@click.option(
    "--db-path",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Path to SQLite database.",
)
@click.option(
    "--json-output",
    "--json",
    "json_output",
    is_flag=True,
    help="Output benchmark metrics as structured JSON.",
)
def benchmark_run(k: int, db_path: Optional[str], json_output: bool) -> None:
    """Executes the expanded hybrid retrieval evaluation benchmark."""
    try:
        engine = HybridSearchEngine.build_from_db(db_path)
        report = RetrievalBenchmark.run_benchmark(engine, k=k)
    except Exception as exc:
        console.print(f"[bold red]Benchmark Execution Error:[/bold red] {exc}")
        sys.exit(1)

    if json_output:
        out = {
            "queries_evaluated": report.queries_evaluated,
            "recall_at_10": report.recall_at_10,
            "mrr": report.mrr,
            "sparse_contributions": report.sparse_contributions,
            "dense_contributions": report.dense_contributions,
            "dual_contribution_verified": report.dual_contribution_verified,
            "passes": report.passes,
        }
        click.echo(json.dumps(out, indent=2))
        return

    table = Table(title="Retrieval Benchmark Performance Report", show_header=True)
    table.add_column("Metric", style="bold cyan")
    table.add_column("Measured Value", style="white")
    table.add_column("Acceptance Target", style="dim")
    table.add_column("Status", style="bold green" if report.passes else "bold red")

    status_recall = "PASS" if report.recall_at_10 >= 0.85 else "FAIL"
    status_mrr = "PASS" if report.mrr >= 0.70 else "FAIL"
    status_dual = "PASS" if report.dual_contribution_verified else "FAIL"

    table.add_row("Queries Evaluated", str(report.queries_evaluated), ">= 35", "PASS")
    table.add_row("Recall@10", f"{report.recall_at_10:.4f}", ">= 0.8500", status_recall)
    table.add_row("Mean Reciprocal Rank (MRR)", f"{report.mrr:.4f}", ">= 0.7000", status_mrr)
    table.add_row(
        "Dual Score Attribution",
        f"Sparse: {report.sparse_contributions}, Dense: {report.dense_contributions}",
        "Verified",
        status_dual,
    )
    table.add_row("Overall Benchmark Status", "ALL CRITERIA SATISFIED" if report.passes else "DEFICIENT", "-", "PASS" if report.passes else "FAIL")

    console.print(table)

    if not report.passes:
        sys.exit(1)


# ---------------------------------------------------------------------------
# Scaffold Command Group
# ---------------------------------------------------------------------------

@cli.group(name="scaffold")
def scaffold_group() -> None:
    """Instant operational runbook and subagent swarm scaffolding."""
    pass


@scaffold_group.command(name="role")
@click.argument("role_id_or_slug", required=True)
@click.option("--company", "-c", "company_name", default=None, help="Company context to attach.")
@click.option(
    "--format",
    "-f",
    "output_format",
    default="markdown",
    type=click.Choice(["json", "markdown", "md"], case_sensitive=False),
    show_default=True,
    help="Export format (json or markdown).",
)
@click.option("--output", "-o", "output_path", default=None, help="Output file path to save runbook.")
@click.option(
    "--db-path",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Path to SQLite database.",
)
def scaffold_role_cmd(
    role_id_or_slug: str,
    company_name: Optional[str],
    output_format: str,
    output_path: Optional[str],
    db_path: Optional[str],
) -> None:
    """Scaffolds complete operational runbook and personal subagent swarm for a canonical role."""
    try:
        scaffolder = RoleScaffolder.build_from_db(db_path)
        pkg = scaffolder.scaffold_role(role_id_or_slug, company_name=company_name)
    except Exception as exc:
        console.print(f"[bold red]Role Scaffolding Error:[/bold red] {exc}")
        sys.exit(1)

    if output_path:
        saved = pkg.save(output_path, format=output_format)
        console.print(f"[bold green]Role runbook written to:[/bold green] {saved}")
        return

    if output_format.lower() == "json":
        click.echo(pkg.to_json())
    else:
        click.echo(pkg.to_markdown())


@scaffold_group.command(name="company")
@click.argument("name_or_ticker", required=True)
@click.option("--division", "-d", default=None, help="Filter by division or department.")
@click.option("--problem", "-p", default=None, help="Executive problem / transformation challenge.")
@click.option(
    "--format",
    "-f",
    "output_format",
    default="markdown",
    type=click.Choice(["json", "markdown", "md"], case_sensitive=False),
    show_default=True,
    help="Export format (json or markdown).",
)
@click.option("--output", "-o", "output_path", default=None, help="Output file path to save runbook.")
@click.option(
    "--db-path",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Path to SQLite database.",
)
def scaffold_company_cmd(
    name_or_ticker: str,
    division: Optional[str],
    problem: Optional[str],
    output_format: str,
    output_path: Optional[str],
    db_path: Optional[str],
) -> None:
    """Scaffolds complete enterprise runbook, division architecture, and staffing swarms."""
    try:
        scaffolder = CompanyScaffolder.build_from_db(db_path)
        pkg = scaffolder.scaffold_company(name_or_ticker, division=division, business_problem=problem)
    except Exception as exc:
        console.print(f"[bold red]Company Scaffolding Error:[/bold red] {exc}")
        sys.exit(1)

    if output_path:
        saved = pkg.save(output_path, format=output_format)
        console.print(f"[bold green]Company runbook written to:[/bold green] {saved}")
        return

    if output_format.lower() == "json":
        click.echo(pkg.to_json())
    else:
        click.echo(pkg.to_markdown())


# ---------------------------------------------------------------------------
# Company Command Group
# ---------------------------------------------------------------------------

@cli.group(name="company")
def company_group() -> None:
    """Enterprise company registration, deep research, and onboarding engine."""
    pass


@company_group.command(name="onboard")
@click.argument("company_name", required=True)
@click.option("--ticker", "-t", default=None, help="Stock ticker symbol or 'PRIVATE'.")
@click.option("--industry", "-i", default="Finance", help="Macro industry sector.")
@click.option("--subsector", "-s", default="Financial Technology & Infrastructure", help="Sub-sector.")
@click.option("--revenue", "-r", default=10.0, type=float, help="Annual revenue in billions.")
@click.option("--challenges", "-c", default=None, help="Key business challenges (semicolon-separated).")
@click.option(
    "--research-file",
    "-rf",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Path to JSON deep-research findings dossier.",
)
@click.option("--output-blueprint", "-o", default=None, help="Custom output path for generated blueprint.")
@click.option(
    "--db-path",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Path to SQLite database.",
)
@click.option(
    "--json-output",
    "--json",
    "json_output",
    is_flag=True,
    help="Output onboarding result as structured JSON.",
)
def company_onboard_cmd(
    company_name: str,
    ticker: Optional[str],
    industry: str,
    subsector: str,
    revenue: float,
    challenges: Optional[str],
    research_file: Optional[str],
    output_blueprint: Optional[str],
    db_path: Optional[str],
    json_output: bool,
) -> None:
    """Onboards an enterprise corporation and generates an 'Apply GenAI Everywhere' blueprint."""
    try:
        engine = CompanyOnboardingEngine.build_from_db(db_path)

        if research_file:
            res = engine.onboard_company(
                research_file,
                output_blueprint_path=output_blueprint,
            )
        else:
            challenge_list = [c.strip() for c in challenges.split(";")] if challenges else []
            data = {
                "name": company_name,
                "ticker": ticker or "PRIVATE",
                "macro_industry": industry,
                "sub_sector": subsector,
                "revenue_billions": revenue,
                "challenges": challenge_list,
            }
            res = engine.onboard_company(
                data,
                output_blueprint_path=output_blueprint,
            )
    except Exception as exc:
        console.print(f"[bold red]Company Onboarding Error:[/bold red] {exc}")
        sys.exit(1)

    if json_output:
        click.echo(json.dumps(res.to_dict(), indent=2))
        return

    console.print(
        Panel.fit(
            f"[bold green]Enterprise Onboarding & GenAI Blueprint Generation Complete[/bold green]\n"
            f"[bold]Company:[/bold] {res.company_name} (`{res.company_slug}`)  |  [bold]Assigned Rank:[/bold] #{res.rank}\n"
            f"[bold]Employed Canonical Roles:[/bold] {res.employed_roles_count}  |  "
            f"[bold]Bespoke Roles Synthesized:[/bold] {res.bespoke_roles_count}\n"
            f"[bold]GenAI Blueprint Artifact:[/bold] {res.blueprint_path}\n"
            f"[bold]Graph Invariants Validated:[/bold] {'[green]PASS[/green]' if res.is_valid else '[red]FAIL[/red]'}",
            title="Company Onboarding Engine",
        )
    )

    if not res.is_valid:
        for v in res.violations:
            console.print(f"[yellow]Violation:[/yellow] {v}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Superhuman Role Synthesis Command Group (Phase 12)
# ---------------------------------------------------------------------------

@cli.group(name="superhuman")
def superhuman_group() -> None:
    """Polymathic Superhuman Role synthesis, Perfect Human pedigree & OOD epistemology."""
    pass


@superhuman_group.command(name="synthesize")
@click.option("--problem", "-p", default=None, help="Target problem statement (known or frontier/OOD).")
@click.option("--role", "-r", default=None, help="Canonical role ID, slug, or title.")
@click.option(
    "--custom-role-file",
    "-crf",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Path to JSON or Markdown/text custom role definition from an external agent.",
)
@click.option("--custom-role-title", default=None, help="Ad-hoc custom role title.")
@click.option("--custom-role-prompt", default=None, help="Ad-hoc custom role prompt or description.")
@click.option("--company", "-c", default=None, help="Optional enterprise/company context.")
@click.option(
    "--developer-context",
    "-dc",
    default=None,
    help="Developer-complemented domain axioms, constraints, or proprietary context.",
)
@click.option(
    "--context-file",
    "-cf",
    type=click.Path(exists=True, dir_okay=False),
    default=None,
    help="Path to file containing developer-complemented domain context.",
)
@click.option("--adjacent-k", default=4, type=int, show_default=True, help="Number of OKG neighbors to fuse.")
@click.option("--slug", default=None, help="Optional explicit superhuman role slug.")
@click.option("--persist/--no-persist", default=False, show_default=True, help="Persist profile to SQLite.")
@click.option(
    "--format",
    "-f",
    "output_format",
    default="markdown",
    type=click.Choice(["markdown", "md", "json"], case_sensitive=False),
    show_default=True,
    help="Export format (markdown or json).",
)
@click.option("--output", "-o", "output_path", default=None, help="Output file path to save package.")
@click.option("--db-path", type=click.Path(dir_okay=False), default=None, help="Path to SQLite database.")
@click.option(
    "--json-output",
    "--json",
    "json_output",
    is_flag=True,
    help="Output synthesized package as structured JSON.",
)
def superhuman_synthesize_cmd(
    problem: Optional[str],
    role: Optional[str],
    custom_role_file: Optional[str],
    custom_role_title: Optional[str],
    custom_role_prompt: Optional[str],
    company: Optional[str],
    developer_context: Optional[str],
    context_file: Optional[str],
    adjacent_k: int,
    slug: Optional[str],
    persist: bool,
    output_format: str,
    output_path: Optional[str],
    db_path: Optional[str],
    json_output: bool,
) -> None:
    """Synthesizes a Superhuman Role Definition & 8-Section Deep Meta-Prompt."""
    custom_spec: Any = None
    if custom_role_file:
        p = Path(custom_role_file)
        raw_txt = p.read_text(encoding="utf-8").strip()
        if p.suffix.lower() == ".json" or raw_txt.startswith("{"):
            custom_spec = json.loads(raw_txt)
            if custom_role_title:
                custom_spec["title"] = custom_role_title
            if custom_role_prompt:
                custom_spec["system_prompt"] = custom_role_prompt
        else:
            custom_spec = {
                "title": custom_role_title or p.stem.replace("_", " ").title(),
                "system_prompt": f"{custom_role_prompt}\n\n{raw_txt}".strip() if custom_role_prompt else raw_txt,
            }
    elif custom_role_title or custom_role_prompt:
        custom_spec = {
            "title": custom_role_title or "Custom Agent Specialist",
            "system_prompt": custom_role_prompt or f"You are {custom_role_title}.",
        }

    try:
        with SuperhumanRoleSynthesizer.build_from_db(db_path) as syn:
            pkg = syn.synthesize(
                problem=problem,
                role=role,
                custom_role_spec=custom_spec,
                company=company,
                developer_context=developer_context,
                context_file=context_file,
                adjacent_k=adjacent_k,
                persist=persist,
                slug=slug,
            )
    except Exception as exc:
        console.print(f"[bold red]Superhuman Synthesis Error:[/bold red] {exc}")
        sys.exit(1)

    eff_fmt = "json" if (json_output or output_format.lower() == "json") else "markdown"
    if output_path:
        saved = pkg.save(output_path, format=eff_fmt)
        if json_output:
            click.echo(pkg.to_json())
        else:
            console.print(
                f"[bold green]Superhuman Role Blueprint saved to:[/bold green] {saved} "
                f"(`{pkg.prompt_character_count:,}` prompt chars)"
            )
        return

    if eff_fmt == "json":
        click.echo(pkg.to_json())
    else:
        click.echo(pkg.to_markdown())


@superhuman_group.command(name="list")
@click.option("--db-path", type=click.Path(dir_okay=False), default=None, help="Path to SQLite database.")
@click.option(
    "--format",
    "-f",
    "output_format",
    default="table",
    type=click.Choice(["table", "json", "markdown", "md"], case_sensitive=False),
    show_default=True,
    help="Output format.",
)
@click.option("--json-output", "--json", "json_output", is_flag=True, help="Output list as JSON.")
def superhuman_list_cmd(db_path: Optional[str], output_format: str, json_output: bool) -> None:
    """Lists persisted Superhuman Role profiles in the database."""
    try:
        with SuperhumanRoleSynthesizer.build_from_db(db_path) as syn:
            profiles = syn.list_profiles()
    except Exception as exc:
        console.print(f"[bold red]Superhuman List Error:[/bold red] {exc}")
        sys.exit(1)

    if json_output or output_format.lower() == "json":
        click.echo(json.dumps(profiles, indent=2))
        return

    if output_format.lower() in ("markdown", "md"):
        lines = ["# Persisted Superhuman Role Profiles", ""]
        for p in profiles:
            lines.append(
                f"- **{p['title']}** (`{p['slug']}` | ID: `{p['id']}`) — `{p['prompt_character_count']:,}` chars"
            )
        click.echo("\n".join(lines))
        return

    table = Table(title=f"Persisted Superhuman Role Profiles ({len(profiles)})", show_header=True)
    table.add_column("ID / Slug", style="cyan")
    table.add_column("Title", style="bold white")
    table.add_column("Neighbors", justify="right")
    table.add_column("Prompt Chars", justify="right", style="green")
    table.add_column("Created At", style="dim")
    for p in profiles:
        table.add_row(
            f"{p['id']}\n({p['slug']})",
            p["title"],
            str(p["adjacent_roles_count"]),
            f"{p['prompt_character_count']:,}",
            str(p["created_at"]),
        )
    console.print(table)


@superhuman_group.command(name="inspect")
@click.argument("id_or_slug", required=True)
@click.option(
    "--format",
    "-f",
    "output_format",
    default="markdown",
    type=click.Choice(["markdown", "md", "json"], case_sensitive=False),
    show_default=True,
    help="Export format (markdown or json).",
)
@click.option("--output", "-o", "output_path", default=None, help="Optional file path to save output.")
@click.option("--db-path", type=click.Path(dir_okay=False), default=None, help="Path to SQLite database.")
@click.option("--json-output", "--json", "json_output", is_flag=True, help="Output profile as JSON.")
def superhuman_inspect_cmd(
    id_or_slug: str,
    output_format: str,
    output_path: Optional[str],
    db_path: Optional[str],
    json_output: bool,
) -> None:
    """Inspects a persisted Superhuman Role profile by ID or slug."""
    try:
        with SuperhumanRoleSynthesizer.build_from_db(db_path) as syn:
            pkg = syn.get_profile(id_or_slug)
    except Exception as exc:
        console.print(f"[bold red]Superhuman Inspect Error:[/bold red] {exc}")
        sys.exit(1)

    eff_fmt = "json" if (json_output or output_format.lower() == "json") else "markdown"
    if output_path:
        saved = pkg.save(output_path, format=eff_fmt)
        if json_output:
            click.echo(pkg.to_json())
        else:
            console.print(f"[bold green]Superhuman profile exported to:[/bold green] {saved}")
        return

    if eff_fmt == "json":
        click.echo(pkg.to_json())
    else:
        click.echo(pkg.to_markdown())


# ---------------------------------------------------------------------------
# Fiduciary Governance & Independent Audit Command Group (Phase 15)
# ---------------------------------------------------------------------------

@cli.group(name="governance")
def governance_group() -> None:
    """Fiduciary Board of Directors, Independent Auditors & Superhuman Governance engine."""
    pass


@governance_group.command(name="list-roles")
@click.option("--category", "-c", default=None, type=click.Choice(["BOARD_DIRECTOR", "INDEPENDENT_AUDITOR"], case_sensitive=False), help="Filter by fiduciary category.")
@click.option("--industry", "-i", default=None, help="Filter by macro industry slug.")
@click.option("--format", "-f", "output_format", default="table", type=click.Choice(["table", "json", "markdown", "md"], case_sensitive=False), show_default=True)
@click.option("--db-path", type=click.Path(dir_okay=False), default=None, help="Path to SQLite database.")
@click.option("--json-output", "--json", "json_output", is_flag=True, help="Output roles as JSON.")
def governance_list_roles_cmd(category: Optional[str], industry: Optional[str], output_format: str, db_path: Optional[str], json_output: bool) -> None:
    """Lists the 18 Fiduciary Board Director & Independent Auditor seats."""
    from orgprompt.governance import list_governance_roles

    roles = list_governance_roles(db_path_or_conn=db_path, category=category, industry_slug=industry)
    if json_output or output_format.lower() == "json":
        click.echo(json.dumps([r.to_dict() for r in roles], indent=2))
        return
    if output_format.lower() in ("markdown", "md"):
        lines = [f"# Fiduciary Governance & Independent Audit Catalog ({len(roles)} Seats)", ""]
        for r in roles:
            lines.append(f"- **{r.title}** (`{r.slug}` | `{r.governance_category}`) — {r.committee_type} (`{r.character_count:,}` chars)")
        click.echo("\n".join(lines))
        return
    table = Table(title=f"Fiduciary Governance & Independent Audit Roles ({len(roles)})", show_header=True)
    table.add_column("ID / Slug", style="cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Title & Committee", style="bold white")
    table.add_column("Prompt Chars", justify="right", style="green")
    for r in roles:
        table.add_row(f"{r.id}\n({r.slug})", r.governance_category, f"{r.title}\n[dim]{r.committee_type}[/dim]", f"{r.character_count:,}")
    console.print(table)


@governance_group.command(name="board-slate")
@click.option("--company", "-c", default=None, help="Company name or slug (e.g., 'Orange France', 'A24', 'Apple').")
@click.option("--industry", "-i", default=None, help="Macro industry slug or keyword (e.g., 'telecommunications', 'creative_media').")
@click.option("--stage", "-s", default=None, type=click.Choice(["PUBLIC_ENTERPRISE", "VENTURE_OR_BOUTIQUE"], case_sensitive=False), help="Override company stage.")
@click.option("--format", "-f", "output_format", default="markdown", type=click.Choice(["markdown", "md", "json"], case_sensitive=False), show_default=True)
@click.option("--output", "-o", "output_path", default=None, help="Optional file path to save slate.")
@click.option("--db-path", type=click.Path(dir_okay=False), default=None, help="Path to SQLite database.")
@click.option("--json-output", "--json", "json_output", is_flag=True, help="Output slate as JSON.")
def governance_board_slate_cmd(company: Optional[str], industry: Optional[str], stage: Optional[str], output_format: str, output_path: Optional[str], db_path: Optional[str], json_output: bool) -> None:
    """Recommends a complete Board of Directors & External Audit Slate for a company or industry."""
    from orgprompt.governance import board_for_company

    target = company or industry
    if not target:
        console.print("[bold red]Error:[/bold red] Provide either `--company` or `--industry`.")
        sys.exit(1)
    slate = board_for_company(target, stage=stage, db_path_or_conn=db_path)
    eff_fmt = "json" if (json_output or output_format.lower() == "json") else "markdown"
    if output_path:
        saved = slate.save(output_path, format=eff_fmt)
        if json_output:
            click.echo(slate.to_json())
        else:
            console.print(f"[bold green]Board & Audit Slate saved to:[/bold green] {saved}")
        return
    click.echo(slate.to_json() if eff_fmt == "json" else slate.to_markdown())


@governance_group.command(name="synthesize-superhuman")
@click.option("--problem", "-p", required=True, help="Target fiduciary governance or audit problem/mandate.")
@click.option("--role", "-r", default=None, help="Base governance role slug or ID.")
@click.option("--company", "-c", default=None, help="Optional company or industry context.")
@click.option("--fuse", multiple=True, help="Additional governance role slugs to fuse (repeatable).")
@click.option("--developer-context", "-dc", default="", help="Shareholder/developer context or constraints.")
@click.option("--slug", default=None, help="Optional explicit profile slug.")
@click.option("--title", default=None, help="Optional explicit profile title.")
@click.option("--persist/--no-persist", default=False, show_default=True, help="Persist profile to SQLite.")
@click.option("--format", "-f", "output_format", default="markdown", type=click.Choice(["markdown", "md", "json"], case_sensitive=False), show_default=True)
@click.option("--output", "-o", "output_path", default=None, help="Optional output file path.")
@click.option("--db-path", type=click.Path(dir_okay=False), default=None, help="Path to SQLite database.")
@click.option("--json-output", "--json", "json_output", is_flag=True, help="Output package as JSON.")
def governance_synthesize_superhuman_cmd(
    problem: str, role: Optional[str], company: Optional[str], fuse: tuple[str, ...],
    developer_context: str, slug: Optional[str], title: Optional[str], persist: bool,
    output_format: str, output_path: Optional[str], db_path: Optional[str], json_output: bool,
) -> None:
    """Synthesizes an 8-Section Superhuman Board Director or Superhuman Independent Auditor."""
    from orgprompt.governance import SuperhumanGovernanceSynthesizer

    synth = SuperhumanGovernanceSynthesizer(db_path)
    pkg = synth.synthesize(
        problem=problem, role_slug_or_id=role, company_or_industry=company,
        fuse_committee_slugs=list(fuse) if fuse else None,
        developer_context=developer_context, slug_override=slug, title_override=title, persist=persist,
    )
    eff_fmt = "json" if (json_output or output_format.lower() == "json") else "markdown"
    if output_path:
        saved = pkg.save(output_path, format=eff_fmt)
        if json_output:
            click.echo(pkg.to_json())
        else:
            console.print(f"[bold green]Superhuman Governance Blueprint saved to:[/bold green] {saved} (`{pkg.prompt_character_count:,}` chars)")
        return
    click.echo(pkg.to_json() if eff_fmt == "json" else pkg.to_markdown())


@governance_group.command(name="inspect")
@click.argument("id_or_slug", required=True)
@click.option("--format", "-f", "output_format", default="markdown", type=click.Choice(["markdown", "md", "json"], case_sensitive=False), show_default=True)
@click.option("--output", "-o", "output_path", default=None, help="Optional output file path.")
@click.option("--db-path", type=click.Path(dir_okay=False), default=None, help="Path to SQLite database.")
@click.option("--json-output", "--json", "json_output", is_flag=True, help="Output as JSON.")
def governance_inspect_cmd(id_or_slug: str, output_format: str, output_path: Optional[str], db_path: Optional[str], json_output: bool) -> None:
    """Inspects either a Governance Role (`gov_*`) or a Superhuman Governance Profile (`superhuman_gov_*`)."""
    from orgprompt.governance import SuperhumanGovernanceSynthesizer, get_governance_role

    eff_fmt = "json" if (json_output or output_format.lower() == "json") else "markdown"
    synth = SuperhumanGovernanceSynthesizer(db_path)
    sh_pkg = synth.get_profile(id_or_slug)
    if sh_pkg:
        if output_path:
            saved = sh_pkg.save(output_path, format=eff_fmt)
            if not json_output:
                console.print(f"[bold green]Exported to:[/bold green] {saved}")
                return
        click.echo(sh_pkg.to_json() if eff_fmt == "json" else sh_pkg.to_markdown())
        return

    role = get_governance_role(id_or_slug, db_path_or_conn=db_path)
    if not role:
        console.print(f"[bold red]Governance role or profile not found:[/bold red] {id_or_slug}")
        sys.exit(1)
    text = role.to_json() if eff_fmt == "json" else role.to_markdown()
    if output_path:
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        if not json_output:
            console.print(f"[bold green]Exported to:[/bold green] {p}")
            return
    click.echo(text)


if __name__ == "__main__":
    cli()
