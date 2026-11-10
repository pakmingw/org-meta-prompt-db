"""Comprehensive Unit and Integration Test Suite for 100% Local Hybrid Search Engine.

Validates:
1. SQLite FTS5 BM25 search interface & robust query sanitization against punctuation/hyphens.
2. Pure local subword character LSA dense semantic vectorizer & cosine similarity.
3. Zero-norm division protection and bounded cosine similarity [-1.0, 1.0].
4. Reciprocal Rank Fusion (RRF, k=60) mathematical fusion & dual-score attribution.
5. SearchResult & SearchResultItem contracts (both object attribute and dict-like indexing).
6. Knowledge Graph Traversal Expansion across behavioral edges (audits, reviews, handoffs, collaborations).
7. Cross-functional team archetype balancing.
8. Automated 25-query retrieval evaluation benchmark (Recall@10 >= 0.85, MRR >= 0.70, dual score verification).
"""

import sqlite3
import numpy as np
import pytest
import networkx as nx

from orgprompt.db.connection import get_default_db_path
from orgprompt.models import CanonicalRole
from orgprompt.search import (
    BM25Index,
    BenchmarkReport,
    CANONICAL_25_BENCHMARK_QUERIES,
    DEFAULT_BENCHMARK_QUERIES,
    HybridSearchEngine,
    LocalDenseIndex,
    RetrievalBenchmark,
    SearchResult,
    SearchResultItem,
    expand_team_subgraph,
    reciprocal_rank_fusion,
    sanitize_fts5_query,
    search_sparse_bm25,
)


# ===========================================================================
# 1. BM25 Query Sanitization and Scoring Tests
# ===========================================================================

def test_bm25_query_sanitization_adversarial(seeded_db):
    """Verifies that sanitize_fts5_query protects against FTS5 syntax errors with special chars."""
    adversarial_inputs = [
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
        "3GPP Release-18 Rel-19",
        "zero-trust & micro-segmentation",
    ]

    cursor = seeded_db.cursor()
    for raw in adversarial_inputs:
        sanitized = sanitize_fts5_query(raw)
        assert isinstance(sanitized, str)
        # Execution must never raise sqlite3.OperationalError
        sql = "SELECT role_id, bm25(roles_fts) FROM roles_fts WHERE roles_fts MATCH ? LIMIT 5"
        try:
            cursor.execute(sql, (sanitized,))
            rows = cursor.fetchall()
            assert isinstance(rows, list)
        except sqlite3.OperationalError as e:
            pytest.fail(f"FTS5 query failed on sanitized query '{sanitized}' (from '{raw}'): {e}")


def test_bm25_search_scoring_order(seeded_db):
    """Verifies that BM25 search ranks results, inverts negative raw score, and sets sparse_rank."""
    results = search_sparse_bm25(seeded_db, "Shannon optical link budget", limit=5)
    assert len(results) > 0

    prev_score = float("inf")
    for idx, item in enumerate(results, start=1):
        assert item["sparse_rank"] == idx
        assert item["sparse_score"] == -item["raw_score"]
        assert item["sparse_score"] > 0
        assert item["sparse_score"] <= prev_score
        prev_score = item["sparse_score"]
        assert "role_id" in item
        assert "slug" in item
        assert "name" in item


def test_bm25_index_class_wrapper(seeded_db):
    """Verifies BM25Index class instantiation and search wrapper."""
    index = BM25Index(seeded_db)
    results = index.search("FPGA low-latency trading", limit=10)
    assert len(results) > 0
    assert results[0]["sparse_rank"] == 1


# ===========================================================================
# 2. Local Dense LSA Vectorizer Tests
# ===========================================================================

def test_dense_vectorizer_fit_and_properties():
    """Verifies LocalDenseIndex feature extraction, SVD fitting, and cosine search."""
    corpus = [
        "high frequency quantitative trading alpha statistical arbitrage",
        "extreme ultraviolet lithography pellicle defect inspection 2nm",
        "6G terahertz phased array beamforming link budget",
        "monoclonal antibody cell line bioreactor perfusion",
    ]
    role_ids = ["role_fin", "role_semi", "role_telecom", "role_pharma"]
    role_slugs = ["fin", "semi", "telecom", "pharma"]

    dense_index = LocalDenseIndex(n_components=3, random_state=42)
    assert not dense_index.is_fitted
    dense_index.fit(role_ids, role_slugs, corpus)
    assert dense_index.is_fitted

    # Search for semantically related query
    results = dense_index.search("quantitative statistical arbitrage", limit=2)
    assert len(results) == 2
    assert results[0]["slug"] == "fin"
    assert results[0]["dense_rank"] == 1
    assert -1.0 <= results[0]["dense_score"] <= 1.0


def test_dense_vectorizer_zero_norm_division_guard():
    """Verifies division-by-zero protection on empty or rare whitespace queries."""
    corpus = ["test document alpha", "test document beta"]
    dense_index = LocalDenseIndex(n_components=1)
    dense_index.fit(["r1", "r2"], ["s1", "s2"], corpus)

    # Empty query
    assert dense_index.search("") == []
    assert dense_index.search("   ") == []

    # Query with symbols that yield zero TF-IDF
    results = dense_index.search("!@#$%^&*()")
    assert isinstance(results, list)
    for r in results:
        assert not np.isnan(r["dense_score"])
        assert not np.isinf(r["dense_score"])


def test_dense_vectorizer_fit_from_db(seeded_db):
    """Verifies LocalDenseIndex.fit_from_db over all seeded canonical roles."""
    dense_index = LocalDenseIndex.fit_from_db(seeded_db, n_components=64)
    assert dense_index.is_fitted
    assert len(dense_index.role_ids) == 336
    assert len(dense_index.role_slugs) == 336

    results = dense_index.search("Kubernetes cloud infrastructure Borg", limit=5)
    assert len(results) == 5
    assert results[0]["dense_rank"] == 1
    assert "tech_chief_cloud_infrastructure_architect" in [r["slug"] for r in results]


# ===========================================================================
# 3. Reciprocal Rank Fusion (RRF) & Attribution Tests
# ===========================================================================

def test_reciprocal_rank_fusion_math_and_attribution():
    """Verifies exact RRF math formula and single/dual attribution tracking."""
    sparse_results = [
        {"role_id": "r1", "slug": "s1", "name": "Role 1", "sparse_rank": 1, "sparse_score": 10.0, "raw_score": -10.0},
        {"role_id": "r2", "slug": "s2", "name": "Role 2", "sparse_rank": 2, "sparse_score": 8.0, "raw_score": -8.0},
    ]
    dense_results = [
        {"role_id": "r2", "slug": "s2", "name": "Role 2", "dense_rank": 1, "dense_score": 0.95},
        {"role_id": "r3", "slug": "s3", "name": "Role 3", "dense_rank": 2, "dense_score": 0.90},
    ]

    k = 60
    fused = reciprocal_rank_fusion(sparse_results, dense_results, k=k, top_limit=5)
    assert len(fused) == 3

    # Role 2 has dual contribution: 1/(60+2) + 1/(60+1)
    # Role 1 has sparse only: 1/(60+1)
    # Role 3 has dense only: 1/(60+2)
    expected_r2_score = (1.0 / 62) + (1.0 / 61)
    expected_r1_score = 1.0 / 61
    expected_r3_score = 1.0 / 62

    assert fused[0]["role_id"] == "r2"
    assert abs(fused[0]["rrf_score"] - expected_r2_score) < 1e-9
    assert fused[0]["has_sparse_contribution"] is True
    assert fused[0]["has_dense_contribution"] is True

    assert fused[1]["role_id"] == "r1"
    assert abs(fused[1]["rrf_score"] - expected_r1_score) < 1e-9
    assert fused[1]["has_sparse_contribution"] is True
    assert fused[1]["has_dense_contribution"] is False

    assert fused[2]["role_id"] == "r3"
    assert abs(fused[2]["rrf_score"] - expected_r3_score) < 1e-9
    assert fused[2]["has_sparse_contribution"] is False
    assert fused[2]["has_dense_contribution"] is True


def test_search_result_item_and_container():
    """Verifies SearchResultItem and SearchResult attribute and dict-like behavior."""
    item = SearchResultItem(
        role_id="role_test",
        slug="test_role",
        name="Test Role",
        sparse_score=5.0,
        dense_score=0.8,
        rrf_score=0.03,
        has_sparse_contribution=True,
        has_dense_contribution=True,
    )

    # Attribute access
    assert item.slug == "test_role"
    assert item.has_sparse_contribution is True

    # Dict-like indexing
    assert item["slug"] == "test_role"
    assert item["sparse_score"] == 5.0
    assert item.get("has_dense_contribution") is True
    assert item.get("non_existent", "default") == "default"

    # SearchResult container
    result = SearchResult(query="test query", results=[item])
    assert len(result) == 1
    assert result[0].slug == "test_role"
    assert [r.slug for r in result] == ["test_role"]

    scores = result.scores
    assert len(scores) == 1
    assert scores[0]["rrf_score"] == 0.03


# ===========================================================================
# 4. Knowledge Graph Traversal Expansion Tests
# ===========================================================================

def test_kg_traversal_expansion_edge_priorities_and_balance(populated_graph):
    """Verifies Knowledge Graph traversal expansion and functional archetype balancing."""
    anchors = ["telecom_chief_network_architect"]

    team = expand_team_subgraph(
        graph=populated_graph,
        anchor_role_ids=anchors,
        min_roles=8,
        max_roles=12,
    )

    assert team["team_size"] >= 8
    assert team["team_size"] <= 12
    assert "role:telecom_chief_network_architect" in team["team_role_ids"]
    assert "telecom_chief_network_architect" in team["team_slugs"]
    assert isinstance(team["subgraph"], nx.Graph)
    assert len(team["edges"]) > 0

    # Verify multiple archetype representation
    archetypes = team["archetypes"]
    assert len(archetypes) >= 2


def test_kg_traversal_expansion_empty_graceful():
    """Verifies expansion degrades gracefully on empty graph."""
    empty_g = nx.DiGraph()
    res = expand_team_subgraph(empty_g, ["role_foo"], min_roles=8, max_roles=12)
    assert res["team_size"] == 1
    assert res["team_slugs"] == ["foo"]


# ===========================================================================
# 5. Hybrid Search Engine End-to-End Tests
# ===========================================================================

def test_hybrid_search_engine_build_and_search(seeded_db):
    """Verifies HybridSearchEngine end-to-end integration with BM25, Dense, RRF, and KG expansion."""
    engine = HybridSearchEngine.build_from_db(seeded_db)

    # 1. Search without KG expansion
    res = engine.search("EUV photolithography wafer fabrication", top_k=5, expand_kg=False)
    assert len(res) == 5
    assert res.expanded_team is None
    for item in res:
        assert item.slug
        assert item.name
        assert item.rrf_score > 0

    # 2. Search with KG expansion
    res_kg = engine.search("6G terahertz phased array beamforming", top_k=5, expand_kg=True)
    assert len(res_kg) == 5
    assert res_kg.expanded_team is not None
    assert res_kg.expanded_team["team_size"] >= 8


def test_hybrid_search_engine_dynamic_index(seeded_db):
    """Verifies HybridSearchEngine.index updates the in-memory index with new roles."""
    engine = HybridSearchEngine.build_from_db(seeded_db)

    new_role = CanonicalRole(
        id="role_custom_specialist",
        org_unit_id="unit_custom",
        slug="custom_specialist",
        title="Custom Bio-Quantum Nanotechnology Specialist",
        mission="Pioneer atomic-scale bio-quantum nano structures.",
        capabilities=["bio_quantum", "nanotech", "cryo_em"],
        mental_models=["Quantum Tunneling"],
        vocabulary=["Q-Dot", "Angstrom"],
        system_prompt="Custom System Prompt " * 80,
    )

    engine.index([new_role])
    assert "role_custom_specialist" in engine.roles_by_id

    # Dense search for new role keywords
    results = engine.search("bio-quantum cryo-em nanotech", top_k=5)
    retrieved_slugs = [r.slug for r in results]
    assert "custom_specialist" in retrieved_slugs


# ===========================================================================
# 6. Automated 25-Query Retrieval Evaluation Benchmark Tests
# ===========================================================================

def test_retrieval_benchmark_runner_full_suite(seeded_db):
    """Verifies that the benchmark achieves Recall@10 >= 0.85 and MRR >= 0.70."""
    engine = HybridSearchEngine.build_from_db(seeded_db)

    report = RetrievalBenchmark.run_benchmark(engine, queries=CANONICAL_25_BENCHMARK_QUERIES, k=10)

    assert isinstance(report, BenchmarkReport)
    assert report.queries_evaluated >= 25
    assert report.recall_at_10 >= 0.85, f"Recall@10 was {report.recall_at_10:.4f}, expected >= 0.85"
    assert report.mrr >= 0.70, f"MRR was {report.mrr:.4f}, expected >= 0.70"
    assert report.dual_contribution_verified is True
    assert report.sparse_contributions > 0
    assert report.dense_contributions > 0
    assert report.passes is True

    # Check summary string
    summary = report.summary()
    assert "PASSED" in summary
    assert "Recall@10" in summary
    assert "MRR" in summary


def test_retrieval_benchmark_hybrid_superiority(seeded_db):
    """Verifies that composite RRF achieves superior or equal performance to sparse or dense alone."""
    engine = HybridSearchEngine.build_from_db(seeded_db)

    sparse_hits = 0
    dense_hits = 0
    hybrid_hits = 0
    total_gt = 0

    for item in CANONICAL_25_BENCHMARK_QUERIES:
        q_text = item["query"]
        gt = set(item["ground_truth"])
        total_gt += len(gt)

        # Sparse alone top 10
        sparse_res = engine.bm25_index.search(q_text, limit=10)
        sparse_slugs = [r["slug"] for r in sparse_res]
        sparse_hits += len(set(sparse_slugs) & gt)

        # Dense alone top 10
        dense_res = engine.dense_index.search(q_text, limit=10)
        dense_slugs = [r["slug"] for r in dense_res]
        dense_hits += len(set(dense_slugs) & gt)

        # Hybrid top 10
        hybrid_res = engine.search(q_text, top_k=10)
        hybrid_slugs = [r.slug for r in hybrid_res]
        hybrid_hits += len(set(hybrid_slugs) & gt)

    hybrid_recall = hybrid_hits / total_gt
    sparse_recall = sparse_hits / total_gt
    dense_recall = dense_hits / total_gt

    # RRF combines complementary strengths, outperforming single modalities
    assert hybrid_recall >= max(sparse_recall, dense_recall), (
        f"Hybrid recall ({hybrid_recall:.4f}) failed to match or beat single components "
        f"(sparse={sparse_recall:.4f}, dense={dense_recall:.4f})"
    )
