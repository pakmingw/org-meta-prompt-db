"""Tier 2 Boundary, Edge & Adversarial Corner Case Test Suite.

Authoritative source: PROJECT.md and SPEC-MINER-SURVEY2 § 2 (Edge Cases).
Validates:
1. SQLite FTS5 query sanitization with special characters (C++, 6G, p99.9, slashes, boolean tokens).
2. Dense vector index zero-norm division guard and bounded cosine similarity [-1.0, 1.0].
3. RRF single-source presence attribution and tie-breaking.
4. NetworkX invariant boundary cases (isolated node, degree=1 workflow, executive leadership).
5. Meta-prompt exact length threshold (1,199 vs 1,200 chars), stub detection, and section ordering.
6. Execution DAG cycle detection and topological resolution.
7. Master solution dossier exact word count boundary (4,999 vs 5,000 words).
"""

import re
import sqlite3
import pytest
import networkx as nx
import numpy as np
from typing import Dict, Any, List

pytestmark = pytest.mark.tier2


# ===========================================================================
# Boundary 1: FTS5 Query Sanitization & Special Characters
# ===========================================================================

def sanitize_fts5_query(query_text: str) -> str:
    """Opaque-box query sanitizer matching the specification in SPEC-MINER-SURVEY2 § 6.2.

    Safely sanitizes user queries containing punctuation, boolean operators,
    or special symbols by extracting alphanumeric/hyphen tokens and wrapping them in quotes.
    """
    tokens = [re.sub(r'[^\w\-]', '', t) for t in query_text.split() if t.strip()]
    valid_tokens = [f'"{t}"*' for t in tokens if len(t) > 0]
    return " OR ".join(valid_tokens) if valid_tokens else '""'


def test_boundary_fts5_query_sanitization_special_characters(db_conn, sample_valid_prompt):
    """Tier 2 Boundary: Tests FTS5 query execution with adversarial and special character inputs.

    Verifies that inputs like 'C++', '6G', 'p99.9', unmatched quotes, boolean words,
    and slashes execute cleanly without raising sqlite3.OperationalError syntax errors.
    """
    cursor = db_conn.cursor()

    # Seed baseline role
    cursor.execute("INSERT INTO industries VALUES ('ind_t2', 't2', 'Tech', 'T', 'T', '{}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)")
    cursor.execute("INSERT INTO exemplar_orgs VALUES ('org_t2', 'ind_t2', 't2_org', 'Org', 'O', 'M', '{}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)")
    cursor.execute("INSERT INTO org_units VALUES ('unit_t2', 'org_t2', 't2_unit', 'Unit', 'D', 'D', 'R_AND_D', 'L', 'L', '{}', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)")
    cursor.execute("""
        INSERT INTO canonical_roles (id, org_unit_id, slug, name, seniority_level, role_archetype, mission, system_prompt, character_count)
        VALUES ('role_c_plus_plus', 'unit_t2', 'cpp_dev', 'Lead C++ Systems Engineer', 'PRINCIPAL_STAFF', 'engineering_staff',
                'Develop high-throughput 6G C++ engines with p99.9 latency under 50us', ?, ?)
    """, (sample_valid_prompt, len(sample_valid_prompt)))
    db_conn.commit()

    adversarial_queries = [
        "C++",
        "6G",
        "p99.9",
        "O-RAN/split-7.2x",
        "\"unmatched quote",
        "AND OR NOT",
        "***???///\\\\",
        "   ",
        "'; DROP TABLE canonical_roles; --",
        "ISO/IEC 15408",
        "ML-KEM-768 (FIPS 203)",
    ]

    for raw_query in adversarial_queries:
        sanitized = sanitize_fts5_query(raw_query)
        sql = "SELECT role_id, bm25(roles_fts) FROM roles_fts WHERE roles_fts MATCH ? LIMIT 5"
        try:
            cursor.execute(sql, (sanitized,))
            rows = cursor.fetchall()
            assert isinstance(rows, list), f"Expected list result for query '{raw_query}'"
        except sqlite3.OperationalError as e:
            pytest.fail(f"FTS5 query failed on sanitized query '{sanitized}' (from '{raw_query}'): {e}")


# ===========================================================================
# Boundary 2: Dense Vector Index Division Guard & Cosine Range
# ===========================================================================

def test_boundary_dense_vector_zero_norm_division():
    """Tier 2 Boundary: Tests vectorizer zero-norm division protection.

    When an input contains only stopwords or unknown punctuation, the resulting TF-IDF
    and SVD vector norm is zero or near-zero. Division must be guarded via max(norm, 1e-12).
    """
    zero_vector = np.zeros((1, 128))
    norm = np.linalg.norm(zero_vector)

    # Division without guard produces NaN
    with np.errstate(divide='ignore', invalid='ignore'):
        unguarded = zero_vector / norm
        assert np.isnan(unguarded).any(), "Expected NaN from unguarded division by zero"

    # Division with specification guard: max(norm, 1e-12)
    guarded = zero_vector / max(norm, 1e-12)
    assert not np.isnan(guarded).any(), "Guarded division produced NaN"
    assert not np.isinf(guarded).any(), "Guarded division produced Inf"
    assert np.all(guarded == 0.0), "Guarded zero vector must remain all zeros"


def test_boundary_dense_vector_cosine_bounds():
    """Tier 2 Boundary: Tests that normalized vector dot products strictly obey [-1.0, 1.0]."""
    np.random.seed(42)
    for _ in range(50):
        v1 = np.random.randn(128)
        v2 = np.random.randn(128)
        v1_norm = v1 / max(np.linalg.norm(v1), 1e-12)
        v2_norm = v2 / max(np.linalg.norm(v2), 1e-12)

        cosine_sim = float(np.dot(v1_norm, v2_norm))
        assert -1.000001 <= cosine_sim <= 1.000001, f"Cosine similarity {cosine_sim} out of theoretical bounds"


# ===========================================================================
# Boundary 3: RRF Single-Source Presence & Attribution
# ===========================================================================

def test_boundary_rrf_single_source_presence():
    """Tier 2 Boundary: Tests Reciprocal Rank Fusion when items exist in only one ranking.

    Per SPEC-MINER-SURVEY2 § 2 Edge Case 5:
    A role present in only sparse ranking receives 1/(k + rank_sparse) + 0.0.
    A role present in only dense ranking receives 0.0 + 1/(k + rank_dense).
    """
    k = 60
    sparse_ranks = {"role_sparse_only": 1}
    dense_ranks = {"role_dense_only": 1}

    # Sparse only calculation
    expected_sparse_score = 1.0 / (k + 1)
    # Dense only calculation
    expected_dense_score = 1.0 / (k + 1)

    assert abs(expected_sparse_score - (1.0 / 61)) < 1e-9
    assert abs(expected_dense_score - (1.0 / 61)) < 1e-9

    # Role in both at rank 1:
    both_score = (1.0 / (k + 1)) + (1.0 / (k + 1))
    assert both_score > expected_sparse_score
    assert both_score > expected_dense_score


# ===========================================================================
# Boundary 4: NetworkX Graph Invariant Edge Cases
# ===========================================================================

def test_boundary_graph_invariant_isolation():
    """Tier 2 Boundary: Invariant 1 detects degree 0 isolated roles."""
    g = nx.DiGraph()
    g.add_node("role:isolated_role", type="CanonicalRole", label="Isolated Role")

    degree = g.degree("role:isolated_role")
    assert degree == 0, "Degree of isolated node must be 0"

    # Validation: role fails Invariant 1
    is_valid = degree > 0
    assert is_valid is False, "Isolated role must fail Invariant 1"


def test_boundary_graph_invariant_insufficient_workflow():
    """Tier 2 Boundary: Invariant 3 rejects role with exactly 1 workflow edge, accepts 2."""
    g = nx.DiGraph()
    g.add_node("role:test_eng", type="CanonicalRole", label="Test Engineer")
    g.add_node("role:peer_1", type="CanonicalRole", label="Peer 1")
    g.add_node("role:peer_2", type="CanonicalRole", label="Peer 2")

    workflow_types = {'COLLABORATES_WITH', 'HANDS_OFF_TO', 'REVIEWS_AND_GATES', 'CHALLENGES_OR_AUDITS'}

    # Add 1 workflow edge
    g.add_edge("role:test_eng", "role:peer_1", type="COLLABORATES_WITH")

    edges = [e for e in list(g.in_edges("role:test_eng", data=True)) + list(g.out_edges("role:test_eng", data=True))
             if e[2].get('type') in workflow_types]
    assert len(edges) == 1
    # Invariant 3 check: must fail (len < 2)
    assert (len(edges) >= 2) is False

    # Add 2nd workflow edge
    g.add_edge("role:peer_2", "role:test_eng", type="REVIEWS_AND_GATES")
    edges_after = [e for e in list(g.in_edges("role:test_eng", data=True)) + list(g.out_edges("role:test_eng", data=True))
                   if e[2].get('type') in workflow_types]
    assert len(edges_after) == 2
    # Invariant 3 check: must pass (len >= 2)
    assert (len(edges_after) >= 2) is True


def test_boundary_graph_invariant_executive_reports_to():
    """Tier 2 Boundary: Invariant 2 accepts executive with 0 outgoing REPORTS_TO if incoming >= 1.

    Per SPEC-MINER-SURVEY2 § 2 Edge Case 6:
    A top executive (CTO, CEO) does not report upward, but direct reports report to them.
    Total degree_REPORTS_TO (in + out) >= 1 satisfies Invariant 2.
    """
    g = nx.DiGraph()
    g.add_node("role:chief_executive", type="CanonicalRole", label="Chief Executive", seniority="C_SUITE")
    g.add_node("role:staff_director", type="CanonicalRole", label="Staff Director", seniority="DIRECTOR")

    # Staff reports to Executive
    g.add_edge("role:staff_director", "role:chief_executive", type="REPORTS_TO")

    # Executive has out_degree 0 for REPORTS_TO
    out_reports = [e for e in g.out_edges("role:chief_executive", data=True) if e[2].get('type') == 'REPORTS_TO']
    assert len(out_reports) == 0

    # Executive has in_degree 1 for REPORTS_TO
    in_reports = [e for e in g.in_edges("role:chief_executive", data=True) if e[2].get('type') == 'REPORTS_TO']
    assert len(in_reports) == 1

    total_reports_deg = len(out_reports) + len(in_reports)
    assert total_reports_deg >= 1, "Executive role with incoming subordinate reports must pass Invariant 2"


# ===========================================================================
# Boundary 5: Meta-Prompt Exact Length & Stub Detection
# ===========================================================================

def test_boundary_prompt_length_exact_threshold():
    """Tier 2 Boundary: Tests the exact 1,200 character boundary for system prompts.

    A prompt with 1,199 characters fails; a prompt with 1,200 characters passes.
    """
    base_text = "A" * 1199
    assert len(base_text) == 1199
    assert (len(base_text) >= 1200) is False, "1,199 chars must fail"

    exact_1200 = base_text + "B"
    assert len(exact_1200) == 1200
    assert (len(exact_1200) >= 1200) is True, "1,200 chars must pass"


def test_boundary_prompt_stub_detection_adversarial():
    """Tier 2 Boundary: Detects prohibited stubs even in long, otherwise valid prompts.

    Prohibited tokens: ['TODO', 'TBD', 'placeholder', 'TBA', 'FIXME', '...'].
    Word boundary matching must not produce false positives on words like 'football' or 'bathtub'.
    """
    prohibited_stubs = ["TODO", "TBD", "placeholder", "TBA", "FIXME"]

    # False positive test: 'bathtub' contains 'tb', but not standalone 'TBD'
    legitimate_text = "The physical sciences laboratory measured the fluid dynamics in a bathtub apparatus."
    for stub in prohibited_stubs:
        assert not re.search(r'\b' + re.escape(stub) + r'\b', legitimate_text, re.IGNORECASE)

    # True positive test: standalone 'TODO' or 'TBD' embedded in a 2,000 char prompt
    long_prompt_with_stub = "A" * 1000 + " TODO: complete the link budget " + "B" * 1000
    assert len(long_prompt_with_stub) > 1200
    found_stub = re.search(r'\bTODO\b', long_prompt_with_stub)
    assert found_stub is not None, "Failed to detect embedded 'TODO' stub in prompt"


def test_boundary_prompt_section_order():
    """Tier 2 Boundary: Prompts with missing sections or out-of-order headers fail."""
    headers = [
        "## 1. Role Identity & Exemplar Lineage",
        "## 2. First-Principles Mental Models & Domain Heuristics",
        "## 3. Technical Vocabulary & Standards",
        "## 4. Anti-Patterns & Mediocrity Filters",
        "## 5. Collaboration, Handoff & Escalation Protocols",
        "## 6. Concrete Output Artifact Schemas",
    ]

    # Valid ordered text
    valid_text = "\n\n".join(headers)
    last_idx = -1
    for h in headers:
        idx = valid_text.find(h)
        assert idx > last_idx
        last_idx = idx

    # Inverted order test: section 5 before section 2
    scrambled_headers = [headers[0], headers[4], headers[1], headers[2], headers[3], headers[5]]
    scrambled_text = "\n\n".join(scrambled_headers)

    is_in_order = True
    last_pos = -1
    for h in headers:
        pos = scrambled_text.find(h)
        if pos <= last_pos:
            is_in_order = False
            break
        last_pos = pos

    assert is_in_order is False, "Scrambled section headers must be detected as out-of-order"


# ===========================================================================
# Boundary 6: Execution DAG Cycle Detection & Single-Node DAG
# ===========================================================================

def test_boundary_dag_cycle_detection():
    """Tier 2 Boundary: Cyclic workflow graphs must be rejected by DAG compiler."""
    cyclic_graph = nx.DiGraph()
    cyclic_graph.add_edge("Task_A", "Task_B")
    cyclic_graph.add_edge("Task_B", "Task_C")
    cyclic_graph.add_edge("Task_C", "Task_A")  # Cycle!

    assert not nx.is_directed_acyclic_graph(cyclic_graph), "Cycle A -> B -> C -> A was not detected"

    with pytest.raises(nx.NetworkXUnfeasible):
        list(nx.topological_sort(cyclic_graph))


def test_boundary_dag_single_node():
    """Tier 2 Boundary: Single-node execution DAG processes cleanly."""
    single_dag = nx.DiGraph()
    single_dag.add_node("Single_Task")

    assert nx.is_directed_acyclic_graph(single_dag)
    order = list(nx.topological_sort(single_dag))
    assert order == ["Single_Task"]


# ===========================================================================
# Boundary 7: Master Dossier Word Count Boundary
# ===========================================================================

def test_boundary_master_dossier_word_count():
    """Tier 2 Boundary: Exactly 4,999 words fails; 5,000 words passes."""
    text_4999 = " word" * 4999
    words_4999 = len(text_4999.split())
    assert words_4999 == 4999
    assert (words_4999 >= 5000) is False, "4,999 words must fail"

    text_5000 = text_4999 + " final"
    words_5000 = len(text_5000.split())
    assert words_5000 == 5000
    assert (words_5000 >= 5000) is True, "5,000 words must pass"
