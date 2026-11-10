"""100% Local Hybrid Search Engine & Retrieval Evaluation Benchmark Suite.

Couples SQLite FTS5 BM25 sparse lexical search with pure local subword character LSA
dense embeddings via Reciprocal Rank Fusion (k=60), followed by Knowledge Graph
Traversal Expansion to assemble balanced multi-agent teams.
"""

from __future__ import annotations

from orgprompt.search.benchmark import (
    CANONICAL_25_BENCHMARK_QUERIES,
    DEFAULT_BENCHMARK_QUERIES,
    EXPANDED_36_BENCHMARK_QUERIES,
    BenchmarkReport,
    RetrievalBenchmark,
)
from orgprompt.search.bm25 import (
    BM25Index,
    sanitize_fts5_query,
    search_sparse_bm25,
)
from orgprompt.search.dense import LocalDenseIndex
from orgprompt.search.expansion import expand_team_subgraph
from orgprompt.search.hybrid import (
    HybridSearchEngine,
    SearchResult,
    SearchResultItem,
    reciprocal_rank_fusion,
)

__all__ = [
    "BM25Index",
    "BenchmarkReport",
    "CANONICAL_25_BENCHMARK_QUERIES",
    "DEFAULT_BENCHMARK_QUERIES",
    "EXPANDED_36_BENCHMARK_QUERIES",
    "HybridSearchEngine",
    "LocalDenseIndex",
    "RetrievalBenchmark",
    "SearchResult",
    "SearchResultItem",
    "expand_team_subgraph",
    "reciprocal_rank_fusion",
    "sanitize_fts5_query",
    "search_sparse_bm25",
]
