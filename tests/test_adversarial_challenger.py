"""Adversarial Challenger Empirical Stress-Testing Suite.

Authoritative source: Final Challenger Dispatch Assignment.
Stress-tests the platform under edge cases and adversarial scenarios:
1. Adversarial Search Queries: Extreme punctuation, unbalanced quotes, empty strings,
   multi-lingual unicode/emojis, SQL injection attempts, 10k-character inputs.
2. Adversarial Team Synthesis: 1-word inputs, 10k-char inputs, conflicting multi-industry
   constraints, empty/whitespace inputs. Verifies >= 8 roles, >= 3 industries, balanced
   archetypes, and provably acyclic execution DAGs.
3. Graph Invariant Boundary Tests: Isolation, invalid hierarchy targets, insufficient
   workflow connectivity, non-artifact output targets, executive incoming report allowance.
4. CLI End-to-End Execution: Subprocess verification of all CLI commands (synthesize,
   execute, search, generate, benchmark) with JSON validation and graceful error handling.
"""

from __future__ import annotations

import json
import sqlite3
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, List

import networkx as nx
import pytest

from orgprompt.db.connection import get_default_db_path
from orgprompt.db.seed_data import seed_database
from orgprompt.graph.engine import KnowledgeGraphEngine
from orgprompt.graph.invariants import validate_knowledge_graph
from orgprompt.search.bm25 import sanitize_fts5_query, search_sparse_bm25
from orgprompt.search.hybrid import HybridSearchEngine
from orgprompt.synthesizer.team_builder import TeamSynthesizer
from orgprompt.synthesizer.workflow_engine import WorkflowEngine


@pytest.fixture(scope="module")
def module_db():
    """Module-scoped in-memory database populated with 16 industries, 48 orgs, 336 roles."""
    conn = seed_database(":memory:")
    yield conn
    conn.close()


@pytest.fixture(scope="module")
def shared_hybrid_engine(module_db: sqlite3.Connection) -> HybridSearchEngine:
    """Module-scoped hybrid search engine initialized once for fast query execution."""
    return HybridSearchEngine.build_from_db(module_db)


@pytest.fixture(scope="module")
def shared_team_synthesizer(module_db: sqlite3.Connection) -> TeamSynthesizer:
    """Module-scoped team synthesizer initialized once for fast team synthesis tests."""
    return TeamSynthesizer.build_from_db(module_db)


# ===========================================================================
# 1. Adversarial Search Queries
# ===========================================================================

ADVERSARIAL_SEARCH_QUERIES = [
    # Extreme punctuation & symbols
    "!@#$%^&*()_+~|}{[]:;?><,./",
    "--------------------",
    "-+-+-+-",
    "***???///\\\\",
    '""""""',
    "''''''",
    '"\'"',
    # Malformed & unbalanced quotes
    '"unmatched quote',
    '"""',
    '"" ""',
    '"foo" "bar',
    'foo"bar',
    # Whitespace & empty strings
    "",
    "   ",
    "\n\t\r  \v\f",
    # Multi-lingual unicode & emojis
    "🚀 🔥 💻 🤖 ⚡",
    "Quantum 6G 🚀 Satellite 🛰️",
    "量子コンピューティング 通信プロトコル",
    "主权人工智能与超低延迟结算",
    "أمان الشبكات السحابية الكمومية",
    "Сверхпроводящие квантовые вычисления",
    "Hochfrequenzhandel-Risikomodellierung",
    "Κρυπτογραφική ασφάλεια δικτύου",
    # SQL injection & FTS5 syntax attacks
    "'; DROP TABLE canonical_roles; --",
    "' OR '1'='1",
    '" OR ""',
    "NOT AND OR NEAR/5",
    "UNION ALL SELECT 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 --",
    "*",
    '""*',
    # Extreme length inputs
    "ultra low latency FPGA 6G telecom " * 300,
    "A" * 5000,
]


@pytest.mark.parametrize("query", ADVERSARIAL_SEARCH_QUERIES)
def test_adversarial_search_queries_bm25_and_hybrid(
    query: str,
    module_db: sqlite3.Connection,
    shared_hybrid_engine: HybridSearchEngine,
):
    """Stress-tests BM25 and Hybrid search engines against adversarial queries."""
    # 1. FTS5 Query Sanitization & Execution
    sanitized = sanitize_fts5_query(query)
    assert isinstance(sanitized, str)
    bm25_results = search_sparse_bm25(module_db, query, limit=10)
    assert isinstance(bm25_results, list)

    # 2. Hybrid Search Engine Execution
    hybrid_res = shared_hybrid_engine.search(query, top_k=10, expand_kg=True)

    assert hybrid_res is not None
    assert isinstance(hybrid_res.results, list)
    assert hybrid_res.query == query

    # Verify score bounds and invariants on any returned results
    for item in hybrid_res.results:
        assert item.final_rank >= 1
        assert item.rrf_score >= 0.0
        if item.sparse_score is not None:
            assert item.sparse_score >= 0.0
        if item.dense_score is not None:
            assert -1.000001 <= item.dense_score <= 1.000001

    # Verify SQL injection did not drop or corrupt tables
    cursor = module_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM canonical_roles")
    role_count = cursor.fetchone()[0]
    assert role_count == 336, f"Database corruption detected: role count {role_count} != 336"


# ===========================================================================
# 2. Adversarial Team Synthesis
# ===========================================================================

ADVERSARIAL_PROBLEMS = [
    # 1-word inputs
    "crypto",
    "audit",
    "space",
    "quantum",
    "42",
    ".",
    # Empty & whitespace
    "",
    "   ",
    # Nonsense jargon
    "nonexistent_gobbledygook_term_xyz_123_random_text",
    # 10,000 character input
    "Sovereign AI distributed consensus high frequency trading risk " * 150,
    # Conflicting multi-industry constraints
    (
        "We require a low-latency 6G sub-THz beamforming antenna array, "
        "integrated with FDA-compliant clinical mRNA therapeutics trial protocol, "
        "real-time gross settlement under Basel IV, Hollywood movie production braintrust, "
        "and deep geothermal well drilling."
    ),
    (
        "Design a pediatric oncology clinical trial protocol that also mines Bitcoin "
        "on a low-orbit CubeSat and complies with FAA DO-178C avionics and Basel IV regulations."
    ),
]


@pytest.mark.parametrize("problem", ADVERSARIAL_PROBLEMS)
def test_adversarial_team_synthesis_constraints_and_dag(
    problem: str,
    shared_team_synthesizer: TeamSynthesizer,
):
    """Stress-tests TeamSynthesizer to verify invariant enforcement on adversarial problem statements."""
    result = shared_team_synthesizer.synthesize_team(problem, min_roles=8, max_roles=15)

    # 1. Team size invariant: >= 8 roles
    assert len(result.roles) >= 8, f"Team size {len(result.roles)} < 8 for problem: {problem[:40]}"

    # 2. Industry diversity invariant: >= 3 macro industries
    assert len(result.industries) >= 3, f"Industries {len(result.industries)} < 3 for problem: {problem[:40]}"

    # 3. Archetype balance
    has_exec = any("executive" in getattr(r, "role_archetype", "").lower() for r in result.roles)
    has_risk = len([r for r in result.roles if "risk" in getattr(r, "role_archetype", "").lower() or "compliance" in getattr(r, "role_archetype", "").lower() or "audit" in getattr(r, "role_archetype", "").lower()]) >= 2
    has_ops = any("operations" in getattr(r, "role_archetype", "").lower() for r in result.roles)
    has_ic = len([r for r in result.roles if getattr(r, "role_archetype", "") in ["engineering_staff", "domain_specialist"]]) >= 4

    assert has_exec, f"Missing executive role for problem: {problem[:40]}"
    assert has_risk, f"Insufficient risk/compliance roles for problem: {problem[:40]}"
    assert has_ops, f"Missing operations role for problem: {problem[:40]}"
    assert has_ic, f"Insufficient IC/engineering roles for problem: {problem[:40]}"

    # 4. Compiled DAG invariant: strictly acyclic
    assert result.dag is not None, f"DAG is None for problem: {problem[:40]}"
    assert nx.is_directed_acyclic_graph(result.dag), f"DAG contains cycle for problem: {problem[:40]}"
    assert len(result.dag.nodes) >= 8, f"DAG node count {len(result.dag.nodes)} < 8"


def test_adversarial_workflow_execution_on_conflicting_problem(shared_team_synthesizer: TeamSynthesizer):
    """Tests that a conflicting multi-industry problem compiles and executes end-to-end cleanly."""
    problem = (
        "We require a low-latency 6G sub-THz beamforming antenna array, "
        "integrated with FDA-compliant clinical mRNA therapeutics trial protocol, "
        "real-time gross settlement under Basel IV, Hollywood movie production braintrust, "
        "and deep geothermal well drilling."
    )
    result = shared_team_synthesizer.synthesize_team(problem)

    with tempfile.TemporaryDirectory() as tmpdir:
        engine = WorkflowEngine()
        exec_res = engine.execute_dag(result.dag, problem_statement=problem, output_dir=tmpdir)

        assert exec_res.status == "COMPLETED"
        assert len(exec_res.executed_nodes) >= 8
        assert len(exec_res.intermediate_artifacts) >= 5
        assert len(exec_res.red_team_findings) >= 1
        assert len(exec_res.upstream_revisions) >= 1
        assert exec_res.solution_dossier is not None
        word_count = len(exec_res.solution_dossier.split())
        assert word_count >= 5000, f"Dossier word count {word_count} < 5,000"

        # Verify artifacts exist on filesystem
        written_files = list(Path(tmpdir).iterdir())
        assert len(written_files) >= 5


# ===========================================================================
# 3. Graph Invariant Boundary Enforcement
# ===========================================================================

def test_graph_invariant_isolation_boundary():
    """Boundary test: Isolated CanonicalRole node (degree=0) must fail with INV-1-ISOLATION."""
    g = nx.DiGraph()
    g.add_node("role:isolated_candidate", type="CanonicalRole", label="Isolated Candidate")
    report = validate_knowledge_graph(g)
    assert not report.is_valid
    codes = [v.invariant_code for v in report.violations]
    assert "INV-1-ISOLATION" in codes


def test_graph_invariant_hierarchy_linkage_boundary():
    """Boundary test: Role with 0 REPORTS_TO edges or REPORTS_TO to non-CanonicalRole fails."""
    # Subtest A: Missing REPORTS_TO
    g_a = nx.MultiDiGraph()
    g_a.add_node("role:alice", type="CanonicalRole", label="Alice")
    g_a.add_node("role:bob", type="CanonicalRole", label="Bob")
    g_a.add_node("art:doc", type="Artifact", label="Document")
    g_a.add_edge("role:alice", "role:bob", key="COLLAB", type="COLLABORATES_WITH")
    g_a.add_edge("role:bob", "role:alice", key="COLLAB", type="COLLABORATES_WITH")
    g_a.add_edge("role:alice", "art:doc", key="PROD", type="PRODUCES")
    g_a.add_edge("role:bob", "art:doc", key="PROD", type="PRODUCES")

    report_a = validate_knowledge_graph(g_a)
    assert not report_a.is_valid
    assert any(v.invariant_code == "INV-2-REPORTS-TO" for v in report_a.violations)

    # Subtest B: REPORTS_TO points to OrgUnit, not CanonicalRole
    g_b = nx.MultiDiGraph()
    g_b.add_node("role:alice", type="CanonicalRole", label="Alice")
    g_b.add_node("unit:lab", type="OrgUnit", label="Lab Unit")
    g_b.add_node("art:doc", type="Artifact", label="Document")
    g_b.add_edge("role:alice", "unit:lab", key="REP", type="REPORTS_TO")
    g_b.add_edge("role:alice", "art:doc", key="PROD", type="PRODUCES")

    report_b = validate_knowledge_graph(g_b)
    assert not report_b.is_valid
    assert any(v.invariant_code == "INV-2-REPORTS-TO" for v in report_b.violations)

    # Subtest C: Executive with 0 outgoing REPORTS_TO, but incoming REPORTS_TO from subordinate
    g_c = nx.MultiDiGraph()
    g_c.add_node("role:ceo", type="CanonicalRole", label="CEO", seniority="C_SUITE")
    g_c.add_node("role:vp", type="CanonicalRole", label="VP", seniority="VP")
    g_c.add_node("role:peer", type="CanonicalRole", label="Peer", seniority="STAFF")
    g_c.add_node("art:exec_doc", type="Artifact", label="Exec Doc")

    # Subordinate reports up to CEO
    g_c.add_edge("role:vp", "role:ceo", key="REP1", type="REPORTS_TO")
    g_c.add_edge("role:peer", "role:ceo", key="REP2", type="REPORTS_TO")

    # Workflow edges across roles (>= 2 per role)
    g_c.add_edge("role:ceo", "role:vp", key="W1", type="COLLABORATES_WITH")
    g_c.add_edge("role:ceo", "role:peer", key="W2", type="REVIEWS_AND_GATES")
    g_c.add_edge("role:vp", "role:peer", key="W3", type="COLLABORATES_WITH")
    g_c.add_edge("role:peer", "role:vp", key="W4", type="HANDS_OFF_TO")

    # Artifact linkage (>= 1 PRODUCES per role)
    g_c.add_edge("role:ceo", "art:exec_doc", key="P1", type="PRODUCES")
    g_c.add_edge("role:vp", "art:exec_doc", key="P2", type="PRODUCES")
    g_c.add_edge("role:peer", "art:exec_doc", key="P3", type="PRODUCES")

    report_c = validate_knowledge_graph(g_c)
    assert report_c.is_valid, f"Expected g_c to be valid, got violations: {report_c.violations}"
    inv2_violations = [v for v in report_c.violations if v.invariant_code == "INV-2-REPORTS-TO"]
    assert len(inv2_violations) == 0


def test_graph_invariant_workflow_connectivity_boundary():
    """Boundary test: Minimum 2 workflow edges required. 0 or 1 edge fails."""
    # Exactly 1 workflow edge
    g = nx.MultiDiGraph()
    g.add_node("role:lead", type="CanonicalRole", label="Lead")
    g.add_node("role:peer", type="CanonicalRole", label="Peer")
    g.add_node("art:doc", type="Artifact", label="Doc")
    g.add_edge("role:peer", "role:lead", key="REP", type="REPORTS_TO")
    g.add_edge("role:peer", "role:lead", key="W1", type="COLLABORATES_WITH")
    g.add_edge("role:lead", "art:doc", key="P1", type="PRODUCES")
    g.add_edge("role:peer", "art:doc", key="P2", type="PRODUCES")

    report = validate_knowledge_graph(g)
    assert not report.is_valid
    assert any(v.invariant_code == "INV-3-WORKFLOW-EDGES" for v in report.violations)

    # Add 2nd workflow edge -> Invariant 3 passes for both
    g.add_edge("role:lead", "role:peer", key="W2", type="REVIEWS_AND_GATES")
    report2 = validate_knowledge_graph(g)
    inv3_violations = [v for v in report2.violations if v.invariant_code == "INV-3-WORKFLOW-EDGES"]
    assert len(inv3_violations) == 0


def test_graph_invariant_produces_artifact_boundary():
    """Boundary test: Role must produce concrete Artifact node. Role-to-role PRODUCES fails."""
    g = nx.MultiDiGraph()
    g.add_node("role:dev", type="CanonicalRole", label="Developer")
    g.add_node("role:lead", type="CanonicalRole", label="Lead")
    g.add_edge("role:dev", "role:lead", key="REP", type="REPORTS_TO")
    g.add_edge("role:dev", "role:lead", key="W1", type="COLLABORATES_WITH")
    g.add_edge("role:lead", "role:dev", key="W2", type="REVIEWS_AND_GATES")
    # Non-compliant: PRODUCES points to role instead of Artifact
    g.add_edge("role:dev", "role:lead", key="P1", type="PRODUCES")

    report = validate_knowledge_graph(g)
    assert not report.is_valid
    assert any(v.invariant_code == "INV-4-PRODUCES-ARTIFACT" for v in report.violations)

    # Add real Artifact node -> Invariant 4 passes
    g.add_node("art:code", type="Artifact", label="Source Code")
    g.add_edge("role:dev", "art:code", key="P2", type="PRODUCES")
    g.add_edge("role:lead", "art:code", key="P3", type="PRODUCES")
    report2 = validate_knowledge_graph(g)
    inv4_violations = [v for v in report2.violations if v.invariant_code == "INV-4-PRODUCES-ARTIFACT"]
    assert len(inv4_violations) == 0


def test_complete_knowledge_graph_invariants(module_db: sqlite3.Connection):
    """Verifies that all 336 canonical roles in the production database satisfy all invariants."""
    graph = KnowledgeGraphEngine.build_from_db(conn=module_db)
    report = validate_knowledge_graph(graph)
    assert report.is_valid, f"Production Knowledge Graph has {len(report.violations)} invariant violations"
    assert report.total_roles == 336
    assert len(report.violations) == 0


# ===========================================================================
# 4. CLI End-to-End Execution
# ===========================================================================

def test_cli_search_query_subprocess():
    """Verifies CLI 'orgprompt search query' via subprocess execution."""
    # Test JSON mode
    res = subprocess.run(
        ["orgprompt", "search", "query", "FPGA ultra low latency", "--json"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"CLI error: {res.stderr}"
    data = json.loads(res.stdout)
    assert "query" in data
    assert data["results_count"] > 0
    assert len(data["results"]) > 0

    # Test error on empty query
    res_err = subprocess.run(
        ["orgprompt", "search", "query", ""],
        capture_output=True,
        text=True,
    )
    assert res_err.returncode != 0


def test_cli_team_synthesize_subprocess():
    """Verifies CLI 'orgprompt team synthesize' via subprocess execution."""
    res = subprocess.run(
        [
            "orgprompt",
            "team",
            "synthesize",
            "-p",
            "Autonomous satellite constellation 6G relay mesh network",
            "--json",
        ],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"CLI error: {res.stderr}"
    data = json.loads(res.stdout)
    assert data["roles_count"] >= 8
    assert data["industries_count"] >= 3
    assert data["is_acyclic"] is True
    assert len(data["dag_nodes"]) >= 8


def test_cli_role_generate_subprocess(tmp_path: Path):
    """Verifies CLI 'orgprompt role generate' via subprocess execution on isolated DB."""
    import shutil
    prod_db = get_default_db_path()
    temp_db = tmp_path / "test_isolated.db"
    shutil.copyfile(prod_db, temp_db)

    unique_token = uuid.uuid4().hex[:6]
    test_role_name = f"Adversarial Verification Staff Engineer {unique_token}"
    res = subprocess.run(
        [
            "orgprompt",
            "role",
            "generate",
            "--name",
            test_role_name,
            "--industry",
            "Cybersecurity",
            "--db-path",
            str(temp_db),
            "--json",
        ],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"CLI error: {res.stderr}"
    data = json.loads(res.stdout)
    assert "id" in data
    assert data["character_count"] >= 1200
    assert "system_prompt" in data


def test_cli_benchmark_run_subprocess():
    """Verifies CLI 'orgprompt benchmark run' via subprocess execution."""
    res = subprocess.run(
        ["orgprompt", "benchmark", "run", "--k", "10", "--json"],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"CLI error: {res.stderr}"
    data = json.loads(res.stdout)
    assert data["queries_evaluated"] >= 25
    assert data["recall_at_10"] >= 0.85
    assert data["mrr"] >= 0.70
    assert data["passes"] is True


def test_cli_team_execute_subprocess():
    """Verifies CLI 'orgprompt team execute' via subprocess execution."""
    with tempfile.TemporaryDirectory() as tmpdir:
        res = subprocess.run(
            [
                "orgprompt",
                "team",
                "execute",
                "-p",
                "Sovereign AI low-latency settlement infrastructure",
                "-o",
                tmpdir,
                "--json",
            ],
            capture_output=True,
            text=True,
        )
        assert res.returncode == 0, f"CLI error: {res.stderr}"
        data = json.loads(res.stdout)
        assert data["status"] == "COMPLETED"
        assert len(data["executed_nodes"]) >= 8
        assert len(data["intermediate_artifacts"]) >= 5
        assert len(data["red_team_findings"]) >= 1
        assert len(data["upstream_revisions"]) >= 1
        dossier_text = data.get("solution_dossier", "")
        assert len(dossier_text.split()) >= 5000
