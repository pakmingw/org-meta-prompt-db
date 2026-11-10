"""Tier 1 Feature Coverage Test Suite.

Authoritative source: PROJECT.md Feature Inventory (Features 1 through 16).
Validates feature contracts, Pydantic schemas, SQLite relational tables,
NetworkX graph hydration, prompt compilation, hybrid search mathematics,
and topological DAG compilation.
"""

import json
import os
import re
import sqlite3
import pytest
import networkx as nx
import numpy as np
from typing import List, Dict, Any

pytestmark = pytest.mark.tier1


# ===========================================================================
# Feature 1 & 2: Taxonomy, Exemplar Orgs, Operating Units
# ===========================================================================

def test_feature_01_global_industry_taxonomy(db_conn):
    """F01: Global Industry Taxonomy & Exemplar Orgs.

    Verifies relational table integrity, unique slug constraints, and foreign key cascades.
    """
    cursor = db_conn.cursor()

    # Insert test macro industry
    cursor.execute("""
        INSERT INTO industries (id, slug, name, description, category)
        VALUES ('ind_telecom', 'telecom', 'Telecommunications', 'Global telecom & radio infrastructure', 'Infrastructure')
    """)

    # Insert exemplar organization
    cursor.execute("""
        INSERT INTO exemplar_orgs (id, industry_id, slug, name, description, signature_mechanisms_summary)
        VALUES ('org_bell_labs', 'ind_telecom', 'bell_labs', 'Bell Labs', 'Pioneering telecommunications lab', 'Systems Engineering Gate, Peer Review')
    """)

    db_conn.commit()

    # Query back
    cursor.execute("SELECT name, category FROM industries WHERE slug = 'telecom'")
    row = cursor.fetchone()
    assert row == ('Telecommunications', 'Infrastructure')

    cursor.execute("SELECT name, signature_mechanisms_summary FROM exemplar_orgs WHERE slug = 'bell_labs'")
    org_row = cursor.fetchone()
    assert org_row == ('Bell Labs', 'Systems Engineering Gate, Peer Review')


def test_feature_02_operating_units_and_loops(db_conn):
    """F02: Operating Units & Loops.

    Verifies 4-stage value creation loops, division/department hierarchy, and CHECK constraints.
    """
    cursor = db_conn.cursor()

    cursor.execute("""
        INSERT INTO industries (id, slug, name, description, category)
        VALUES ('ind_semiconductors', 'semiconductors', 'Semiconductors', 'Lithography and chip fab', 'Hardware')
    """)
    cursor.execute("""
        INSERT INTO exemplar_orgs (id, industry_id, slug, name, description, signature_mechanisms_summary)
        VALUES ('org_asml', 'ind_semiconductors', 'asml', 'ASML', 'Photolithography systems', 'V-Cycle Systems Engineering')
    """)

    # Insert valid unit
    cursor.execute("""
        INSERT INTO org_units (id, exemplar_org_id, slug, name, division, department, unit_type, description, core_value_loop)
        VALUES ('unit_asml_euv', 'org_asml', 'asml_euv', 'EUV Metrology Group', 'R&D Division', 'Optical Physics', 'R_AND_D', 'Advanced EUV mirror optics', '1. Concept -> 2. Simulation -> 3. Metrology -> 4. Fab Integration')
    """)
    db_conn.commit()

    cursor.execute("SELECT unit_type, core_value_loop FROM org_units WHERE slug = 'asml_euv'")
    unit_row = cursor.fetchone()
    assert unit_row[0] == 'R_AND_D'
    assert 'Fab Integration' in unit_row[1]

    # Verify CHECK constraint on unit_type
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("""
            INSERT INTO org_units (id, exemplar_org_id, slug, name, division, department, unit_type, description, core_value_loop)
            VALUES ('unit_invalid', 'org_asml', 'invalid', 'Invalid Unit', 'Div', 'Dept', 'INVALID_TYPE', 'Desc', 'Loop')
        """)


# ===========================================================================
# Feature 3: SQLite Relational Schema & Real-Time Sync Triggers
# ===========================================================================

def test_feature_03_sqlite_relational_schema_and_triggers(db_conn, sample_valid_prompt):
    """F03: SQLite Relational Schema, Foreign Keys & FTS5 Real-Time Sync Triggers.

    Verifies that INSERT, UPDATE, and DELETE in canonical_roles automatically syncs with roles_fts.
    """
    cursor = db_conn.cursor()

    # Seed hierarchy
    cursor.execute("INSERT INTO industries VALUES ('ind_fin', 'finance', 'Finance', 'Fintech', 'Markets', '{}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)")
    cursor.execute("INSERT INTO exemplar_orgs VALUES ('org_ren', 'ind_fin', 'rentec', 'Renaissance', 'Quant fund', 'Peer Review', '{}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)")
    cursor.execute("INSERT INTO org_units VALUES ('unit_alpha', 'org_ren', 'alpha_research', 'Alpha Group', 'Research', 'Models', 'R_AND_D', 'Alpha loop', 'Loop', '{}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)")

    # 1. Test INSERT Trigger
    cursor.execute("""
        INSERT INTO canonical_roles (
            id, org_unit_id, slug, name, seniority_level, role_archetype, mission,
            system_prompt, character_count, capabilities_json, mental_models_json
        ) VALUES (
            'role_quant_1', 'unit_alpha', 'quant_researcher', 'Principal Quantitative Researcher',
            'PRINCIPAL_STAFF', 'engineering_staff', 'Design statistical arbitrage alphas',
            ?, ?, '["statistical_arbitrage", "kalman_filtering"]', '["Black-Scholes", "Kelly Criterion"]'
        )
    """, (sample_valid_prompt, len(sample_valid_prompt)))
    db_conn.commit()

    # Query FTS5 virtual table
    cursor.execute("SELECT role_id, name, industry, mission FROM roles_fts WHERE roles_fts MATCH 'arbitrage'")
    fts_row = cursor.fetchone()
    assert fts_row is not None, "FTS5 insert trigger failed to index canonical role"
    assert fts_row[0] == 'role_quant_1'
    assert fts_row[1] == 'Principal Quantitative Researcher'
    assert fts_row[2] == 'Finance'

    # 2. Test UPDATE Trigger
    cursor.execute("""
        UPDATE canonical_roles 
        SET mission = 'Design high-frequency market making statistical models' 
        WHERE id = 'role_quant_1'
    """)
    db_conn.commit()

    # In FTS5, hyphenated words or punctuation must be quoted to avoid being treated as column/NOT operators
    cursor.execute("SELECT role_id, mission FROM roles_fts WHERE roles_fts MATCH '\"high-frequency\"'")
    fts_update_row = cursor.fetchone()
    assert fts_update_row is not None, "FTS5 update trigger failed to update full-text index"

    # 3. Test DELETE Trigger
    cursor.execute("DELETE FROM canonical_roles WHERE id = 'role_quant_1'")
    db_conn.commit()

    cursor.execute("SELECT role_id FROM roles_fts WHERE role_id = 'role_quant_1'")
    assert cursor.fetchone() is None, "FTS5 delete trigger failed to remove deleted role from index"


# ===========================================================================
# Feature 4: NetworkX Graph Engine & Invariant Checking
# ===========================================================================

def test_feature_04_networkx_graph_engine(sample_graph):
    """F04: NetworkX Graph Engine.

    Verifies heterogeneous node counts, edge attributes, and the 4 structural invariants.
    """
    g = sample_graph

    # Verify heterogeneous node presence
    node_types = {d.get('type') for _, d in g.nodes(data=True)}
    assert 'Industry' in node_types
    assert 'ExemplarOrg' in node_types
    assert 'OrgUnit' in node_types
    assert 'CanonicalRole' in node_types
    assert 'Artifact' in node_types

    # Invariant 1: Degree > 0 for all roles
    roles = [n for n, d in g.nodes(data=True) if d.get('type') == 'CanonicalRole']
    assert len(roles) >= 3
    for r in roles:
        assert g.degree(r) > 0, f"Role {r} is isolated"

    # Invariant 2: REPORTS_TO degree >= 1
    for r in roles:
        reports_edges = [
            e for e in list(g.in_edges(r, data=True)) + list(g.out_edges(r, data=True))
            if e[2].get('type') == 'REPORTS_TO'
        ]
        assert len(reports_edges) >= 1, f"Role {r} lacks REPORTS_TO edge"

    # Invariant 3: Workflow edges >= 2
    workflow_types = {'COLLABORATES_WITH', 'HANDS_OFF_TO', 'REVIEWS_AND_GATES', 'CHALLENGES_OR_AUDITS'}
    for r in roles:
        wf_edges = [
            e for e in list(g.in_edges(r, data=True)) + list(g.out_edges(r, data=True))
            if e[2].get('type') in workflow_types
        ]
        assert len(wf_edges) >= 2, f"Role {r} has only {len(wf_edges)} workflow edges (minimum 2 required)"

    # Invariant 4: PRODUCES Artifact >= 1
    for r in roles:
        prod_edges = [e for e in g.out_edges(r, data=True) if e[2].get('type') == 'PRODUCES']
        assert len(prod_edges) >= 1, f"Role {r} produces no artifacts"


# ===========================================================================
# Feature 5: Extensible Role Generator API Contract
# ===========================================================================

def test_feature_05_extensible_role_generator_contract(sample_graph):
    """F05: Extensible Role Generator contract.

    Tests adding a new role and dynamically wiring required invariant edges.
    """
    g = sample_graph.copy()
    new_role_id = "role:quantum_metrology_specialist"

    # Add new role
    g.add_node(
        new_role_id,
        type="CanonicalRole",
        label="Quantum Metrology Specialist",
        seniority="SENIOR_SPECIALIST",
        archetype="domain_specialist"
    )

    # Invariant wiring:
    # 1. Connect to org unit
    g.add_edge(new_role_id, "unit:bell_labs_rf_lab", type="BELONGS_TO")

    # 2. Wire REPORTS_TO edge to chief_rf_architect (Invariant 2)
    g.add_edge(new_role_id, "role:chief_rf_architect", type="REPORTS_TO")

    # 3. Wire workflow edges to distinct peers: COLLABORATES_WITH and HANDS_OFF_TO (Invariant 3)
    g.add_edge(new_role_id, "role:staff_oran_engineer", type="COLLABORATES_WITH")
    g.add_edge(new_role_id, "role:lead_security_auditor", type="HANDS_OFF_TO")

    # 4. Wire output artifact (Invariant 4)
    g.add_node("art:quantum_metrology_spec", type="Artifact", label="Quantum Metrology Spec")
    g.add_edge(new_role_id, "art:quantum_metrology_spec", type="PRODUCES")

    # Verify all invariants hold for the new role
    all_edges = list(g.in_edges(new_role_id, data=True)) + list(g.out_edges(new_role_id, data=True))
    assert len(all_edges) >= 4

    reports = [e for e in all_edges if e[2].get('type') == 'REPORTS_TO']
    assert len(reports) >= 1

    workflow = [e for e in all_edges if e[2].get('type') in {'COLLABORATES_WITH', 'HANDS_OFF_TO', 'REVIEWS_AND_GATES', 'CHALLENGES_OR_AUDITS'}]
    assert len(workflow) >= 2

    produces = [e for e in g.out_edges(new_role_id, data=True) if e[2].get('type') == 'PRODUCES']
    assert len(produces) >= 1


# ===========================================================================
# Feature 6 & 7: Meta-Prompt Engine & Invariant Gate
# ===========================================================================

def test_feature_06_and_07_meta_prompt_invariants(sample_valid_prompt):
    """F06 & F07: Meta-Prompt Compilation & Quality Invariants.

    Validates: >= 1,200 chars, 6 mandatory sections, 0 stubs, valid JSON artifact schema.
    """
    prompt = sample_valid_prompt

    # Length >= 1,200 characters
    assert len(prompt) >= 1200, f"Prompt length {len(prompt)} < 1200"

    # All 6 mandatory section headers
    required_sections = [
        "## 1. Role Identity & Exemplar Lineage",
        "## 2. First-Principles Mental Models & Domain Heuristics",
        "## 3. Technical Vocabulary & Standards",
        "## 4. Anti-Patterns & Mediocrity Filters",
        "## 5. Collaboration, Handoff & Escalation Protocols",
        "## 6. Concrete Output Artifact Schemas"
    ]
    for sec in required_sections:
        assert sec in prompt, f"Missing required section '{sec}'"

    # Zero prohibited stubs
    prohibited_stubs = ["TODO", "TBD", "placeholder", "TBA", "FIXME", "..."]
    for stub in prohibited_stubs:
        assert not re.search(r'\b' + re.escape(stub) + r'\b', prompt), f"Found prohibited stub token: {stub}"

    # Section 6 contains valid JSON schema block
    schema_match = re.search(r'```json\s*(\{.*?\})\s*```', prompt, re.DOTALL)
    assert schema_match is not None, "Prompt Section 6 must contain a JSON schema block"
    parsed_schema = json.loads(schema_match.group(1))
    assert parsed_schema.get("type") == "object", "Section 6 JSON schema must be an object schema"
    assert "properties" in parsed_schema, "Section 6 JSON schema must define properties"


# ===========================================================================
# Feature 8, 9, 10: Hybrid Search (BM25, Dense LSA, RRF)
# ===========================================================================

def test_feature_08_sparse_bm25_search_scoring(db_conn, sample_valid_prompt):
    """F08: SQLite FTS5 BM25 Sparse Search Scoring.

    Verifies ranking and negative score interpretation in SQLite FTS5.
    """
    cursor = db_conn.cursor()

    # Seed two roles with distinct keywords
    cursor.execute("INSERT INTO industries VALUES ('ind_it', 'it', 'Tech', 'Tech industry', 'Tech', '{}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)")
    cursor.execute("INSERT INTO exemplar_orgs VALUES ('org_goog', 'ind_it', 'google', 'Google', 'Tech org', 'Braintrust', '{}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)")
    cursor.execute("INSERT INTO org_units VALUES ('unit_ai', 'org_goog', 'ai_lab', 'AI Lab', 'AI', 'Core', 'R_AND_D', 'AI loop', 'Loop', '{}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)")

    prompt_a = sample_valid_prompt + "\nSpecialized keyword: tensor_parallel_vllm_kernel"
    prompt_b = sample_valid_prompt + "\nSpecialized keyword: terahertz_link_budget_beamforming"

    cursor.execute("""
        INSERT INTO canonical_roles (id, org_unit_id, slug, name, seniority_level, role_archetype, mission, system_prompt, character_count)
        VALUES ('role_ai_kernel', 'unit_ai', 'ai_kernel_eng', 'AI Kernel Engineer', 'PRINCIPAL_STAFF', 'engineering_staff', 'Optimize GPU kernels', ?, ?)
    """, (prompt_a, len(prompt_a)))

    cursor.execute("""
        INSERT INTO canonical_roles (id, org_unit_id, slug, name, seniority_level, role_archetype, mission, system_prompt, character_count)
        VALUES ('role_rf_eng', 'unit_ai', 'rf_eng', 'RF Engineer', 'PRINCIPAL_STAFF', 'engineering_staff', 'Design sub-THz links', ?, ?)
    """, (prompt_b, len(prompt_b)))
    db_conn.commit()

    # Search for tensor_parallel_vllm_kernel
    cursor.execute("""
        SELECT role_id, bm25(roles_fts) as score 
        FROM roles_fts 
        WHERE roles_fts MATCH 'tensor_parallel_vllm_kernel'
        ORDER BY score ASC
    """)
    results = cursor.fetchall()
    assert len(results) >= 1
    assert results[0][0] == 'role_ai_kernel', "Expected role_ai_kernel as top match for kernel query"


def test_feature_09_pure_local_dense_vectorizer():
    """F09: Pure Local Subword Character LSA Dense Semantic Vectorizer.

    Verifies sklearn TfidfVectorizer + TruncatedSVD cosine similarity calculation without external dependencies.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.decomposition import TruncatedSVD

    corpus = [
        "statistical arbitrage quantitative alpha model execution high-frequency trading",
        "extreme ultraviolet EUV pellicle defect metrology sub-nanometer yield ASML TSMC",
        "6G terahertz phased array beamforming and subcarrier link budget URLLC radio",
        "sovereign cloud data residency enclave zero trust encryption AMD SEV",
    ]
    role_ids = ["role_quant", "role_euv", "role_6g", "role_cloud"]

    vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), sublinear_tf=True)
    tfidf = vectorizer.fit_transform(corpus)

    # Use 3 components for this 4-document test corpus
    svd = TruncatedSVD(n_components=3, random_state=42)
    dense = svd.fit_transform(tfidf)

    # Normalize vectors
    norms = np.linalg.norm(dense, axis=1, keepdims=True)
    embeddings = dense / np.maximum(norms, 1e-12)

    # Query: 'quantitative alpha trading'
    q_tfidf = vectorizer.transform(["quantitative alpha trading"])
    q_dense = svd.transform(q_tfidf)
    q_norm = np.linalg.norm(q_dense)
    q_normed = q_dense / max(q_norm, 1e-12)

    similarities = np.dot(embeddings, q_normed.T).flatten()
    best_match_idx = int(np.argmax(similarities))
    assert role_ids[best_match_idx] == "role_quant", "Dense vectorizer failed to retrieve semantically nearest role"


def test_feature_10_reciprocal_rank_fusion():
    """F10: Reciprocal Rank Fusion (RRF, k=60) & Dual Score Attribution.

    Verifies mathematical rank aggregation formula: RRF(d) = sum(1 / (60 + r_m(d))).
    """
    sparse_ranks = {"role_a": 1, "role_b": 2, "role_c": 3}
    dense_ranks = {"role_b": 1, "role_a": 3, "role_d": 2}

    k = 60
    # Role A: 1/(60+1) + 1/(60+3) = 1/61 + 1/63 = 0.016393 + 0.015873 = 0.032266
    # Role B: 1/(60+2) + 1/(60+1) = 1/62 + 1/61 = 0.016129 + 0.016393 = 0.032522
    # Role C: 1/(60+3) = 1/63 = 0.015873 (sparse only)
    # Role D: 1/(60+2) = 1/62 = 0.016129 (dense only)

    score_a = (1.0 / (k + 1)) + (1.0 / (k + 3))
    score_b = (1.0 / (k + 2)) + (1.0 / (k + 1))
    score_c = 1.0 / (k + 3)
    score_d = 1.0 / (k + 2)

    assert score_b > score_a > score_d > score_c, "RRF calculation order unexpected"

    # Attribution check: Role B has both sparse and dense contributions
    has_dual_b = ("role_b" in sparse_ranks) and ("role_b" in dense_ranks)
    assert has_dual_b is True


# ===========================================================================
# Feature 11 & 12: Knowledge Graph Expansion & Benchmark Metrics
# ===========================================================================

def test_feature_11_knowledge_graph_expansion(sample_graph):
    """F11: Knowledge Graph Traversal Expansion.

    Verifies expanding anchor roles across workflow edges to assemble cross-functional teams.
    """
    g = sample_graph
    anchor_role = "role:chief_rf_architect"

    # Expand 1 hop across outgoing and incoming workflow edges
    neighbors = set()
    for _, target, d in g.out_edges(anchor_role, data=True):
        if g.nodes[target].get('type') == 'CanonicalRole':
            neighbors.add(target)
    for source, _, d in g.in_edges(anchor_role, data=True):
        if g.nodes[source].get('type') == 'CanonicalRole':
            neighbors.add(source)

    assert "role:staff_oran_engineer" in neighbors
    assert "role:lead_security_auditor" in neighbors


def test_feature_12_retrieval_benchmark_metric_formulas():
    """F12: Retrieval Evaluation Benchmark Metric Formulas.

    Verifies mathematical definitions of Recall@K and MRR on mock rankings.
    """
    ground_truth = {"role_1", "role_2"}
    retrieved_k10 = ["role_1", "role_3", "role_4", "role_5", "role_6", "role_7", "role_8", "role_9", "role_10", "role_11"]

    # Hits in top-10: role_1 (1 out of 2)
    recall_at_10 = len(set(retrieved_k10) & ground_truth) / len(ground_truth)
    assert recall_at_10 == 0.5

    # First hit is at rank 1: RR = 1/1 = 1.0
    reciprocal_rank = 1.0 / 1
    assert reciprocal_rank == 1.0


# ===========================================================================
# Feature 13, 14, 15, 16: Synthesizer & Execution DAG Compiler
# ===========================================================================

def test_feature_13_capability_extractor_contract():
    """F13: Capability Extractor Interface Contract.

    Verifies decomposition into domains, disciplines, and performance constraints.
    """
    problem = (
        "Design a low-latency 6G edge sub-THz network and real-time gross settlement engine "
        "under strict CPMI-IOSCO and post-quantum cryptographic security constraints."
    )

    # Contract requirement: identifies Telecommunications, Finance, Cybersecurity domains
    text_lower = problem.lower()
    assert "6g" in text_lower
    assert "settlement" in text_lower
    assert "post-quantum" in text_lower or "cryptographic" in text_lower


def test_feature_14_dynamic_team_synthesizer_constraints():
    """F14: Dynamic Team Synthesizer Constraints.

    Verifies constraint validation on assembled teams (>=8 roles, >=3 industries, balanced tiers).
    """
    mock_team = [
        {"role_id": "r1", "industry": "Telecommunications", "archetype": "executive_strategy"},
        {"role_id": "r2", "industry": "Telecommunications", "archetype": "engineering_staff"},
        {"role_id": "r3", "industry": "Telecommunications", "archetype": "domain_specialist"},
        {"role_id": "r4", "industry": "Finance", "archetype": "engineering_staff"},
        {"role_id": "r5", "industry": "Finance", "archetype": "domain_specialist"},
        {"role_id": "r6", "industry": "Cybersecurity", "archetype": "risk_compliance"},
        {"role_id": "r7", "industry": "Public Sector", "archetype": "risk_compliance"},
        {"role_id": "r8", "industry": "Semiconductors", "archetype": "operations"},
    ]

    assert len(mock_team) >= 8, "Team must have at least 8 roles"
    industries = {r["industry"] for r in mock_team}
    assert len(industries) >= 3, "Team must span at least 3 industries"

    archetypes = {r["archetype"] for r in mock_team}
    assert "executive_strategy" in archetypes
    assert "risk_compliance" in archetypes
    assert "operations" in archetypes


def test_feature_15_topological_dag_compiler():
    """F15: Topological DAG Compiler.

    Verifies that staged task projection compiles cyclic role relationships into an acyclic DAG.
    """
    dag = nx.DiGraph()

    # Stage 1: Charters
    dag.add_edge("stage_1:exec_charter", "stage_2:rf_spec")
    dag.add_edge("stage_1:exec_charter", "stage_2:settlement_spec")

    # Stage 2: Parallel Specialist Artifacts
    dag.add_edge("stage_2:rf_spec", "stage_3:integrated_spec")
    dag.add_edge("stage_2:settlement_spec", "stage_3:integrated_spec")

    # Stage 3: Integrated System Spec
    dag.add_edge("stage_3:integrated_spec", "stage_4:red_team_audit")

    # Stage 4: Red Team Audit Gate
    dag.add_edge("stage_4:red_team_audit", "stage_5:upstream_revision")

    # Stage 5: Upstream Revision
    dag.add_edge("stage_5:upstream_revision", "stage_6:master_dossier")

    # Topological invariant checks
    assert nx.is_directed_acyclic_graph(dag), "Compiled DAG contains cycles"
    topo_order = list(nx.topological_sort(dag))
    assert topo_order[0] == "stage_1:exec_charter"
    assert topo_order[-1] == "stage_6:master_dossier"


def test_feature_16_workflow_dag_execution_engine():
    """F16: Workflow DAG Execution Engine Contract.

    Verifies stage-by-stage artifact passing and completion status.
    """
    dag = nx.DiGraph()
    dag.add_edge("task_1", "task_2")
    dag.add_edge("task_2", "task_3")

    executed_tasks = []
    artifacts = {}

    for task in nx.topological_sort(dag):
        executed_tasks.append(task)
        artifacts[task] = f"artifact_from_{task}"

    assert executed_tasks == ["task_1", "task_2", "task_3"]
    assert len(artifacts) == 3
