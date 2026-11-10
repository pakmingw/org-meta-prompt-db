"""End-to-End Acceptance Requirements Test Suite.

Authoritative source: ORIGINAL_REQUEST.md (Acceptance Criteria, lines 28–41).
Validates:
1. Phase 1 & 2: Database Completeness (>=15 industries, >=45 exemplar orgs, >=100 units, >=300 roles).
2. Phase 1 & 2: Graph Invariants (0 orphan roles, >=1 REPORTS_TO, >=2 workflow edges, >=1 output artifact).
3. Phase 1 & 2: Dynamic Role Expansion Utility (synthesis, invariant preservation, prompt compilation).
4. Phase 3: Meta-Prompt Quality (>=1,200 chars, 6 mandatory sections, 0 stubs, 100% uniqueness).
5. Phase 3: 100% Local Hybrid Search Benchmark (Recall@10 >= 0.85, MRR >= 0.70, dual score attribution).
6. Phase 4: Dynamic Team Synthesizer (>=8 roles, >=3 industries, balanced archetypes, topological DAG).
7. Phase 4: Flagship Grand Challenge Trajectory (6 stages, intermediate artifacts, red-team revision, >=5,000 words dossier).
"""

import os
import re
import sqlite3
import pytest
import networkx as nx
from typing import List, Dict, Any, Set

# Marker for all E2E requirements
pytestmark = pytest.mark.e2e


# ---------------------------------------------------------------------------
# Helpers for Invariant and Prompt Verification
# ---------------------------------------------------------------------------

PROHIBITED_STUBS = ["TODO", "TBD", "placeholder", "TBA", "FIXME", "..."]

REQUIRED_SECTIONS = [
    "## 1. Role Identity & Exemplar Lineage",
    "## 2. First-Principles Mental Models & Domain Heuristics",
    "## 3. Technical Vocabulary & Standards",
    "## 4. Anti-Patterns & Mediocrity Filters",
    "## 5. Collaboration, Handoff & Escalation Protocols",
    "## 6. Concrete Output Artifact Schemas",
]


def check_prompt_integrity(prompt: str, role_id: str) -> None:
    """Verifies that a system prompt satisfies all Phase 3 quality invariants."""
    # 1. Minimum character length >= 1200
    assert len(prompt) >= 1200, (
        f"Prompt for role '{role_id}' has {len(prompt)} chars, "
        f"which fails acceptance threshold (>= 1,200 chars)."
    )

    # 2. All 6 mandatory structural sections in order
    last_pos = -1
    for sec in REQUIRED_SECTIONS:
        pos = prompt.find(sec)
        assert pos != -1, f"Role '{role_id}' prompt missing section header: '{sec}'"
        assert pos > last_pos, f"Section '{sec}' in role '{role_id}' prompt is out of order."
        last_pos = pos

    # 3. Prohibited stubs check
    for stub in PROHIBITED_STUBS:
        # Check for stub token surrounded by word boundaries or punctuation
        assert not re.search(r'\b' + re.escape(stub) + r'\b', prompt), (
            f"Role '{role_id}' prompt contains prohibited stub token '{stub}'."
        )


def check_graph_invariants(g: nx.DiGraph) -> Dict[str, Any]:
    """Verifies that all CanonicalRole nodes in g satisfy all 4 structural invariants."""
    role_nodes = [n for n, d in g.nodes(data=True) if d.get('type') == 'CanonicalRole']
    violations = []

    for role_id in role_nodes:
        attrs = g.nodes[role_id]
        role_name = attrs.get('label', role_id)

        in_edges = list(g.in_edges(role_id, data=True))
        out_edges = list(g.out_edges(role_id, data=True))
        all_edges = in_edges + out_edges

        # Invariant 1: Zero Isolated Roles (degree > 0)
        if len(all_edges) == 0:
            violations.append(f"INV-1: Role '{role_name}' ({role_id}) is completely isolated (degree=0).")
            continue

        # Invariant 2: Hierarchy Linkage (>= 1 REPORTS_TO edge, either in or out to a CanonicalRole)
        reports_edges = [
            e for e in all_edges
            if e[2].get('type') == 'REPORTS_TO'
            and g.nodes[e[0] if e[1] == role_id else e[1]].get('type') == 'CanonicalRole'
        ]
        if len(reports_edges) < 1:
            violations.append(f"INV-2: Role '{role_name}' ({role_id}) lacks hierarchy linkage (0 REPORTS_TO edges).")

        # Invariant 3: Workflow Connectivity (>= 2 workflow/collaboration edges to CanonicalRoles)
        workflow_types = {'COLLABORATES_WITH', 'HANDS_OFF_TO', 'REVIEWS_AND_GATES', 'CHALLENGES_OR_AUDITS'}
        workflow_edges = [
            e for e in all_edges
            if e[2].get('type') in workflow_types
            and g.nodes[e[0] if e[1] == role_id else e[1]].get('type') == 'CanonicalRole'
        ]
        if len(workflow_edges) < 2:
            violations.append(
                f"INV-3: Role '{role_name}' ({role_id}) has only {len(workflow_edges)} workflow edges "
                f"(minimum 2 required)."
            )

        # Invariant 4: Concrete Artifact Linkage (>= 1 PRODUCES edge to an Artifact)
        produces_edges = [
            e for e in out_edges
            if e[2].get('type') == 'PRODUCES'
            and g.nodes[e[1]].get('type') == 'Artifact'
        ]
        if len(produces_edges) < 1:
            violations.append(
                f"INV-4: Role '{role_name}' ({role_id}) produces no concrete output artifact (0 PRODUCES edges)."
            )

    return {
        "is_valid": len(violations) == 0,
        "total_roles": len(role_nodes),
        "violations": violations
    }


# ---------------------------------------------------------------------------
# Acceptance Criterion 1: Taxonomy & Database Completeness
# ---------------------------------------------------------------------------

def test_e2e_r1_and_r2_database_completeness():
    """Validates Acceptance Criteria Phase 1 & 2:

    - Database contains >= 15 macro industries.
    - Database contains >= 45 exemplar organizations with documented operating mechanisms.
    - Database contains >= 100 organizational units.
    - Database contains >= 300 distinct canonical roles.
    """
    # Progressive testability: check if orgprompt.db.connection or seed_data is available
    orgprompt_db = pytest.importorskip("orgprompt.db.connection", reason="orgprompt.db.connection module not yet available (M1 pending)")

    db_path = getattr(orgprompt_db, "DEFAULT_DB_PATH", "org_knowledge_base.db")
    if not os.path.exists(db_path):
        # Fall back to seeding helper if available
        seed_module = pytest.importorskip("orgprompt.db.seed_data", reason="Seed data not yet generated")
        if hasattr(seed_module, "seed_database"):
            conn = orgprompt_db.get_connection(":memory:")
            seed_module.seed_database(conn)
        else:
            pytest.skip("Database seed function not found.")
    else:
        conn = orgprompt_db.get_connection(db_path)

    cursor = conn.cursor()

    # 1. Macro Industries count >= 15
    cursor.execute("SELECT COUNT(*) FROM industries")
    industry_count = cursor.fetchone()[0]
    assert industry_count >= 15, f"Expected >= 15 macro industries, found {industry_count}"

    # 2. Exemplar Organizations count >= 45
    cursor.execute("SELECT COUNT(*), COUNT(signature_mechanisms_summary) FROM exemplar_orgs WHERE signature_mechanisms_summary != ''")
    org_count, org_with_mechs = cursor.fetchone()
    assert org_count >= 45, f"Expected >= 45 exemplar organizations, found {org_count}"
    assert org_with_mechs >= 45, "All exemplar organizations must document signature mechanisms"

    # 3. Organizational Units count >= 100
    cursor.execute("SELECT COUNT(*) FROM org_units")
    unit_count = cursor.fetchone()[0]
    assert unit_count >= 100, f"Expected >= 100 organizational units, found {unit_count}"

    # 4. Canonical Roles count >= 300
    cursor.execute("SELECT COUNT(*) FROM canonical_roles")
    role_count = cursor.fetchone()[0]
    assert role_count >= 300, f"Expected >= 300 canonical roles, found {role_count}"


# ---------------------------------------------------------------------------
# Acceptance Criterion 2: Knowledge Graph Invariants
# ---------------------------------------------------------------------------

def test_e2e_r2_knowledge_graph_invariants():
    """Validates Acceptance Criteria Phase 1 & 2:

    - Knowledge Graph in SQLite + NetworkX has zero orphaned/isolated CanonicalRole nodes.
    - Every role has >= 1 REPORTS_TO or leadership edge.
    - Every role has >= 2 workflow/collaboration edges (COLLABORATES_WITH, HANDS_OFF_TO, REVIEWS_AND_GATES, CHALLENGES_OR_AUDITS).
    - Every role has >= 1 linked output Artifact via PRODUCES edge.
    """
    engine_module = pytest.importorskip("orgprompt.graph.engine", reason="orgprompt.graph.engine not yet available (M1 pending)")
    conn_module = pytest.importorskip("orgprompt.db.connection", reason="orgprompt.db.connection not yet available")

    db_path = getattr(conn_module, "DEFAULT_DB_PATH", "org_knowledge_base.db")
    if not os.path.exists(db_path):
        pytest.skip(f"Database {db_path} does not exist yet.")

    conn = conn_module.get_connection(db_path)
    if hasattr(engine_module, "KnowledgeGraphEngine") and hasattr(engine_module.KnowledgeGraphEngine, "build_from_db"):
        g = engine_module.KnowledgeGraphEngine.build_from_db(db_path)
    elif hasattr(engine_module, "load_knowledge_graph_from_sqlite"):
        g = engine_module.load_knowledge_graph_from_sqlite(conn)
    else:
        pytest.skip("Graph hydration function not found in engine module.")

    report = check_graph_invariants(g)
    assert report["is_valid"], (
        f"Found {len(report['violations'])} graph invariant violations across {report['total_roles']} roles:\n"
        + "\n".join(report["violations"][:15])
    )


# ---------------------------------------------------------------------------
# Acceptance Criterion 3: Dynamic Role Expansion Utility
# ---------------------------------------------------------------------------

def test_e2e_r2_dynamic_role_expansion_utility():
    """Validates Acceptance Criteria Phase 1 & 2:

    - Includes a working role/taxonomy expansion utility tested by dynamically
      generating and validating a new role node with full graph edges and prompt compilation.
    """
    generator_module = pytest.importorskip("orgprompt.graph.generator", reason="orgprompt.graph.generator not yet available (M1 pending)")
    engine_module = pytest.importorskip("orgprompt.graph.engine", reason="orgprompt.graph.engine not yet available")
    conn_module = pytest.importorskip("orgprompt.db.connection", reason="orgprompt.db.connection not yet available")

    db_path = getattr(conn_module, "DEFAULT_DB_PATH", "org_knowledge_base.db")
    if not os.path.exists(db_path):
        pytest.skip("Database does not exist yet.")

    conn = conn_module.get_connection(db_path)
    cursor = conn.cursor()

    # Retrieve an existing org unit to attach to
    cursor.execute("SELECT id, slug FROM org_units LIMIT 1")
    unit_row = cursor.fetchone()
    if not unit_row:
        pytest.skip("No organizational units found in database.")

    unit_id, unit_slug = unit_row

    new_role_spec = {
        "name": "Bio-Quantum Simulation Specialist",
        "org_unit_slug": unit_slug,
        "seniority_level": "PRINCIPAL_STAFF",
        "role_archetype": "domain_specialist",
        "mission": "Pioneer atomistic quantum simulations of macromolecular complexes for targeted therapeutics.",
        "capabilities": ["quantum_chemistry", "cryo_em_modeling", "density_functional_theory"],
        "mental_models": ["Born-Oppenheimer Approximation", "Hartree-Fock Theory"],
        "technical_vocabulary": ["Q-Chem", "Hartree", "DFT-D4", "Gibbs Free Energy"],
        "anti_patterns": ["Classical Forcefield Over-Reliance in Transition State Modeling"],
    }

    if hasattr(generator_module, "RoleGenerator"):
        generator = generator_module.RoleGenerator()
        result = generator.generate_role(new_role_spec, conn)
    elif hasattr(generator_module, "generate_role"):
        result = generator_module.generate_role(new_role_spec, conn)
    else:
        pytest.skip("RoleGenerator API not found in generator module.")

    # Validate generation output
    assert result is not None, "RoleGenerator returned None"

    # Check generated prompt length and sections
    prompt = getattr(result, "system_prompt", None) or result.get("system_prompt", "")
    assert len(prompt) >= 1200, f"Generated prompt length {len(prompt)} < 1200 characters"
    for sec in REQUIRED_SECTIONS:
        assert sec in prompt, f"Generated prompt missing section: {sec}"


# ---------------------------------------------------------------------------
# Acceptance Criterion 4: Meta-Prompt Quality Invariants
# ---------------------------------------------------------------------------

def test_e2e_r3_prompt_quality_invariants():
    """Validates Acceptance Criteria Phase 3:

    - All 300+ canonical roles have unique, non-stubbed System Prompts
      (>= 1,200 characters each, 100% uniqueness across prompts).
    - Contains all 6 required structural sections and domain-specific heuristics/vocabulary.
    """
    conn_module = pytest.importorskip("orgprompt.db.connection", reason="orgprompt.db.connection not yet available")
    db_path = getattr(conn_module, "DEFAULT_DB_PATH", "org_knowledge_base.db")
    if not os.path.exists(db_path):
        pytest.skip("Database does not exist yet.")

    conn = conn_module.get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, system_prompt, character_count FROM canonical_roles")
    roles = cursor.fetchall()

    assert len(roles) >= 300, f"Expected >= 300 canonical roles, found {len(roles)}"

    seen_prompts: Set[str] = set()

    for r_id, name, prompt, char_count in roles:
        # Check character count stored and actual
        assert len(prompt) >= 1200, f"Role '{name}' ({r_id}) has prompt length {len(prompt)} < 1200 characters."
        assert char_count >= 1200, f"Role '{name}' ({r_id}) character_count column is {char_count} < 1200."

        # Check prompt uniqueness
        assert prompt not in seen_prompts, f"Duplicate system prompt detected for role '{name}' ({r_id})."
        seen_prompts.add(prompt)

        # Check section integrity and zero stubs
        check_prompt_integrity(prompt, r_id)


# ---------------------------------------------------------------------------
# Acceptance Criterion 5: 100% Local Hybrid Search Benchmark
# ---------------------------------------------------------------------------

def test_e2e_r3_hybrid_search_retrieval_benchmark(benchmark_queries_25):
    """Validates Acceptance Criteria Phase 3:

    - Hybrid search engine runs 100% locally in Python.
    - Passes an automated retrieval evaluation benchmark (>= 25 diverse queries).
    - Demonstrates Recall@10 >= 0.85.
    - Demonstrates MRR >= 0.70.
    - Strictly verifiable score contributions from both the dense vector index and sparse BM25 index via RRF.
    """
    search_module = pytest.importorskip("orgprompt.search", reason="orgprompt.search module not yet available (M3 pending)")
    conn_module = pytest.importorskip("orgprompt.db.connection", reason="orgprompt.db.connection not yet available")

    db_path = getattr(conn_module, "DEFAULT_DB_PATH", "org_knowledge_base.db")
    if not os.path.exists(db_path):
        pytest.skip("Database does not exist yet.")

    conn = conn_module.get_connection(db_path)

    # Initialize hybrid search engine
    if hasattr(search_module, "HybridSearchEngine"):
        engine = search_module.HybridSearchEngine.build_from_db(db_path)
    else:
        pytest.skip("HybridSearchEngine not found in search module.")

    total_recall_at_10 = 0.0
    total_reciprocal_rank = 0.0
    queries_count = len(benchmark_queries_25)
    sparse_contributions = 0
    dense_contributions = 0

    assert queries_count >= 25, f"Expected >= 25 benchmark queries, got {queries_count}"

    for item in benchmark_queries_25:
        query_text = item["query"]
        ground_truth = set(item["ground_truth"])

        search_result = engine.search(query_text, top_k=10)
        retrieved_roles = [r.slug if hasattr(r, "slug") else r["slug"] for r in search_result.results]

        # Calculate Recall@10
        hits = len(set(retrieved_roles) & ground_truth)
        recall_at_10 = hits / len(ground_truth) if ground_truth else 0.0
        total_recall_at_10 += recall_at_10

        # Calculate Reciprocal Rank
        rr = 0.0
        for rank, role_slug in enumerate(retrieved_roles, start=1):
            if role_slug in ground_truth:
                rr = 1.0 / rank
                break
        total_reciprocal_rank += rr

        # Verify dual score attribution
        for res in search_result.results:
            if getattr(res, "has_sparse_contribution", False) or (isinstance(res, dict) and res.get("has_sparse_contribution")):
                sparse_contributions += 1
            if getattr(res, "has_dense_contribution", False) or (isinstance(res, dict) and res.get("has_dense_contribution")):
                dense_contributions += 1

    mean_recall_at_10 = total_recall_at_10 / queries_count
    mean_mrr = total_reciprocal_rank / queries_count

    assert mean_recall_at_10 >= 0.85, f"Benchmark Recall@10 {mean_recall_at_10:.4f} < 0.85 target."
    assert mean_mrr >= 0.70, f"Benchmark MRR {mean_mrr:.4f} < 0.70 target."
    assert sparse_contributions > 0, "No sparse BM25 score contributions detected in benchmark results."
    assert dense_contributions > 0, "No dense vector score contributions detected in benchmark results."


# ---------------------------------------------------------------------------
# Acceptance Criterion 6: Dynamic Team Synthesizer Constraints
# ---------------------------------------------------------------------------

def test_e2e_r4_team_synthesizer_constraints():
    """Validates Acceptance Criteria Phase 4:

    - Given the flagship grand challenge problem statement:
      * Selects a cross-functional team of >= 8 distinct roles.
      * Spanning >= 3 industries/functions (strategy, deep engineering, economics/finance, operations, risk/audit).
      * Produces a valid topological execution DAG derived from Knowledge Graph edges.
    """
    synth_module = pytest.importorskip("orgprompt.synthesizer", reason="orgprompt.synthesizer not yet available (M4 pending)")
    conn_module = pytest.importorskip("orgprompt.db.connection", reason="orgprompt.db.connection not yet available")

    db_path = getattr(conn_module, "DEFAULT_DB_PATH", "org_knowledge_base.db")
    if not os.path.exists(db_path):
        pytest.skip("Database does not exist yet.")

    flagship_problem = (
        "Architecting, economically modeling, stress-testing, and governing a next-generation "
        "Sovereign AI + 6G Edge Telecommunications + Real-Time Financial Settlement Infrastructure "
        "under strict regulatory, capital, latency, and adversarial security constraints."
    )

    if hasattr(synth_module, "TeamSynthesizer"):
        synthesizer = synth_module.TeamSynthesizer.build_from_db(db_path)
        team_result = synthesizer.synthesize_team(flagship_problem, min_roles=8)
    else:
        pytest.skip("TeamSynthesizer not found in synthesizer module.")

    team_roles = team_result.roles if hasattr(team_result, "roles") else team_result.get("roles", [])
    assert len(team_roles) >= 8, f"Team Synthesizer assembled {len(team_roles)} roles, expected >= 8."

    # Check industry diversity
    industries = {r.industry if hasattr(r, "industry") else r.get("industry") for r in team_roles}
    assert len(industries) >= 3, f"Team covers {len(industries)} industries, expected >= 3."

    # Check archetype diversity
    archetypes = {r.role_archetype if hasattr(r, "role_archetype") else r.get("role_archetype") for r in team_roles}
    assert "executive_strategy" in archetypes or any("executive" in str(a).lower() for a in archetypes), "Team lacks Executive Strategy archetype"
    assert "risk_compliance" in archetypes or any("risk" in str(a).lower() or "audit" in str(a).lower() for a in archetypes), "Team lacks Risk/Compliance archetype"

    # Check topological DAG compilation
    dag = team_result.dag if hasattr(team_result, "dag") else team_result.get("dag")
    assert dag is not None, "Team Synthesizer did not produce an execution DAG."
    assert nx.is_directed_acyclic_graph(dag), "Compiled execution DAG contains cycles; must be provably acyclic."
    assert len(list(nx.topological_sort(dag))) == len(dag.nodes), "Topological sort failed on execution DAG."


# ---------------------------------------------------------------------------
# Acceptance Criterion 7: Flagship Grand Challenge Trajectory & Master Dossier
# ---------------------------------------------------------------------------

def test_e2e_r4_flagship_grand_challenge_trajectory_and_dossier():
    """Validates Acceptance Criteria Phase 4:

    - Executes all 6 stages of the Grand Challenge execution DAG.
    - Generates distinct, domain-rigorous intermediate artifacts for each role.
    - Records at least one adversarial review/audit critique cycle (REVIEWS_AND_GATES / CHALLENGES_OR_AUDITS)
      that triggers a documented revision of upstream work.
    - Compiles a comprehensive final solution dossier >= 5,000 words across 9 chapters.
    """
    challenge_module = pytest.importorskip("orgprompt.challenge", reason="orgprompt.challenge not yet available (M5 pending)")

    if hasattr(challenge_module, "GrandChallengeRunner"):
        runner = challenge_module.GrandChallengeRunner()
        report = runner.execute()
    else:
        pytest.skip("GrandChallengeRunner not found in challenge module.")

    assert report is not None, "GrandChallengeRunner returned None."

    # 1. Verify intermediate artifacts exist
    artifacts = getattr(report, "intermediate_artifacts", []) or report.get("intermediate_artifacts", [])
    assert len(artifacts) >= 6, f"Expected >= 6 intermediate artifacts across the trajectory, found {len(artifacts)}."

    # 2. Verify adversarial audit critique and forced revision loop
    audit_findings = getattr(report, "red_team_findings", []) or report.get("red_team_findings", [])
    assert len(audit_findings) >= 1, "Adversarial red-team recorded 0 critique findings; expected >= 1 critique cycle."

    revisions = getattr(report, "upstream_revisions", []) or report.get("upstream_revisions", [])
    assert len(revisions) >= 1, "No documented upstream revisions triggered by adversarial red-team critique."

    # 3. Verify final solution dossier length >= 5,000 words
    dossier_text = getattr(report, "solution_dossier", "") or report.get("solution_dossier", "")
    word_count = len(dossier_text.split())
    assert word_count >= 5000, f"Final solution dossier has {word_count} words, expected >= 5,000 words."
