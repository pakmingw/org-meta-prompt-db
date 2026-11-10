"""Reciprocal Rank Fusion (RRF) Hybrid Search Engine with Dual-Score Attribution.

Couples SQLite FTS5 BM25 sparse lexical search with pure local subword character LSA
dense embeddings via Reciprocal Rank Fusion:
    RRF(d) = sum_{m in M} 1 / (60 + r_m(d))
Provides strictly verifiable dual-score attribution tracking, exposes SearchResult
models conforming to project interface contracts, and seamlessly invokes Knowledge Graph
Traversal Expansion.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Union

import networkx as nx

from orgprompt.db.connection import get_connection, get_default_db_path
from orgprompt.graph.engine import KnowledgeGraphEngine
from orgprompt.models import CanonicalRole
from orgprompt.search.bm25 import BM25Index
from orgprompt.search.dense import LocalDenseIndex
from orgprompt.search.expansion import expand_team_subgraph


def reciprocal_rank_fusion(
    sparse_results: List[Dict[str, Any]],
    dense_results: List[Dict[str, Any]],
    k: int = 60,
    top_limit: int = 20,
) -> List[Dict[str, Any]]:
    """Combines sparse and dense ranked candidate lists via Reciprocal Rank Fusion.

    Formula:
        RRF(d) = sum_{m in {sparse, dense}} 1 / (k + r_m(d))
    If an item is absent from system m's ranking, its contribution from m is 0.0.

    Args:
        sparse_results: Ranked list from BM25 sparse search.
        dense_results: Ranked list from dense semantic search.
        k: Smoothing constant (standard k=60).
        top_limit: Maximum number of merged results to return.

    Returns:
        List of merged candidate dicts with score attribution.
    """
    scores: Dict[str, float] = {}
    details: Dict[str, Dict[str, Any]] = {}
    meta: Dict[str, Dict[str, Any]] = {}

    for item in sparse_results:
        rid = item["role_id"]
        rank = item["sparse_rank"]
        contrib = 1.0 / (k + rank)
        scores[rid] = scores.get(rid, 0.0) + contrib
        if rid not in details:
            details[rid] = {}
        details[rid]["sparse"] = {
            "rank": rank,
            "score": item["sparse_score"],
            "raw_score": item.get("raw_score", -item["sparse_score"]),
            "contrib": contrib,
        }
        meta[rid] = {
            "role_id": rid,
            "slug": item.get("slug", rid.replace("role_", "")),
            "name": item.get("name", ""),
        }

    for item in dense_results:
        rid = item["role_id"]
        rank = item["dense_rank"]
        contrib = 1.0 / (k + rank)
        scores[rid] = scores.get(rid, 0.0) + contrib
        if rid not in details:
            details[rid] = {}
        details[rid]["dense"] = {
            "rank": rank,
            "score": item["dense_score"],
            "contrib": contrib,
        }
        if rid not in meta:
            meta[rid] = {
                "role_id": rid,
                "slug": item.get("slug", rid.replace("role_", "")),
                "name": item.get("name", ""),
            }

    # Sort descending by composite RRF score
    sorted_roles = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_limit]

    output: List[Dict[str, Any]] = []
    for final_rank, (rid, rrf_score) in enumerate(sorted_roles, start=1):
        item_details = details[rid]
        has_sparse = "sparse" in item_details
        has_dense = "dense" in item_details
        sparse_meta = item_details.get("sparse", {})
        dense_meta = item_details.get("dense", {})

        output.append({
            "role_id": rid,
            "slug": meta[rid]["slug"],
            "name": meta[rid]["name"],
            "final_rank": final_rank,
            "rrf_score": rrf_score,
            "sparse_rank": sparse_meta.get("rank"),
            "sparse_score": sparse_meta.get("score", 0.0),
            "dense_rank": dense_meta.get("rank"),
            "dense_score": dense_meta.get("score", 0.0),
            "has_sparse_contribution": has_sparse,
            "has_dense_contribution": has_dense,
            "attribution": item_details,
        })

    return output


@dataclass
class SearchResultItem:
    """Individual search result representing a retrieved CanonicalRole with dual-score attribution."""

    role_id: str
    slug: str
    name: str
    role: Optional[CanonicalRole] = None
    sparse_score: float = 0.0
    dense_score: float = 0.0
    sparse_rank: Optional[int] = None
    dense_rank: Optional[int] = None
    rrf_score: float = 0.0
    final_rank: int = 0
    has_sparse_contribution: bool = False
    has_dense_contribution: bool = False
    attribution: Dict[str, Any] = field(default_factory=dict)

    def __getitem__(self, item: str) -> Any:
        """Enables dict-like subscripting for backward and test compatibility."""
        if hasattr(self, item):
            return getattr(self, item)
        if item in self.attribution:
            return self.attribution[item]
        raise KeyError(f"SearchResultItem has no key or attribute '{item}'")

    def get(self, item: str, default: Any = None) -> Any:
        """Enables dict-like get method."""
        if hasattr(self, item):
            return getattr(self, item)
        return self.attribution.get(item, default)


@dataclass
class SearchResult:
    """Aggregated container returned by HybridSearchEngine.search()."""

    query: str
    results: List[SearchResultItem] = field(default_factory=list)
    expanded_team: Optional[Dict[str, Any]] = None

    def __iter__(self) -> Iterator[SearchResultItem]:
        return iter(self.results)

    def __len__(self) -> int:
        return len(self.results)

    def __getitem__(self, index: int) -> SearchResultItem:
        return self.results[index]

    @property
    def scores(self) -> List[Dict[str, Any]]:
        """Returns score attribution list satisfying PROJECT.md interface contract."""
        return [
            {
                "sparse_score": r.sparse_score,
                "dense_score": r.dense_score,
                "rrf_score": r.rrf_score,
                "role": r.role,
                "slug": r.slug,
            }
            for r in self.results
        ]


class HybridSearchEngine:
    """100% Local Self-Contained Hybrid Search Engine (SQLite FTS5 BM25 + Subword LSA + RRF)."""

    def __init__(
        self,
        bm25_index: BM25Index,
        dense_index: LocalDenseIndex,
        roles_by_id: Optional[Dict[str, CanonicalRole]] = None,
        graph: Optional[nx.Graph] = None,
        k: int = 60,
    ) -> None:
        self.bm25_index = bm25_index
        self.dense_index = dense_index
        self.roles_by_id: Dict[str, CanonicalRole] = roles_by_id or {}
        self.graph = graph
        self.k = k

    @classmethod
    def build_from_db(
        cls,
        db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None,
        graph: Optional[nx.Graph] = None,
        k: int = 60,
    ) -> HybridSearchEngine:
        """Factory constructor hydrating BM25 index, Dense index, and Graph from SQLite."""
        if isinstance(db_path_or_conn, sqlite3.Connection):
            conn = db_path_or_conn
            close_on_exit = False
        else:
            path = db_path_or_conn or get_default_db_path()
            conn = get_connection(path)
            close_on_exit = False

        # 1. Initialize BM25
        bm25 = BM25Index(conn)

        # 2. Fit Local Dense Index
        dense = LocalDenseIndex.fit_from_db(conn, n_components=128)

        # 3. Hydrate CanonicalRole models
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                r.id, r.org_unit_id, r.slug, r.name, r.seniority_level, r.role_archetype,
                r.mission, r.system_prompt, r.capabilities_json, r.mental_models_json,
                r.domain_heuristics_json, r.technical_vocabulary_json, r.anti_patterns_json,
                i.name
            FROM canonical_roles r
            LEFT JOIN org_units u ON r.org_unit_id = u.id
            LEFT JOIN exemplar_orgs o ON u.exemplar_org_id = o.id
            LEFT JOIN industries i ON o.industry_id = i.id;
        """)
        roles_by_id: Dict[str, CanonicalRole] = {}
        for row in cursor.fetchall():
            role_obj = CanonicalRole(
                id=row[0],
                org_unit_id=row[1],
                slug=row[2],
                title=row[3],
                seniority_tier=row[4],
                role_archetype=row[5],
                mission=row[6],
                system_prompt=row[7],
                industry=row[13] if len(row) > 13 else None,
            )
            roles_by_id[row[0]] = role_obj
            roles_by_id[row[2]] = role_obj  # Index by slug as well

        # 4. Hydrate Graph if not passed
        if graph is None:
            try:
                graph = KnowledgeGraphEngine.build_from_db(conn=conn)
            except Exception:
                graph = None

        return cls(
            bm25_index=bm25,
            dense_index=dense,
            roles_by_id=roles_by_id,
            graph=graph,
            k=k,
        )

    def index(self, roles: List[CanonicalRole]) -> None:
        """Updates the in-memory index with newly provided CanonicalRole instances."""
        for r in roles:
            self.roles_by_id[r.id] = r
            self.roles_by_id[r.slug] = r

        # Re-fit dense index across all unique roles currently in memory
        unique_roles = {r.id: r for r in self.roles_by_id.values()}
        role_ids = []
        role_slugs = []
        corpus = []

        for r in unique_roles.values():
            role_ids.append(r.id)
            role_slugs.append(r.slug)
            text = (
                f"{r.title} {r.slug.replace('_', ' ')} {r.mission} "
                f"{' '.join(r.capabilities)} {' '.join(r.mental_models)} "
                f"{' '.join(r.vocabulary)} {r.system_prompt[:1200]}"
            )
            corpus.append(text)

        if corpus:
            self.dense_index.fit(role_ids, role_slugs, corpus)

    def search(
        self,
        query: str,
        top_k: int = 10,
        expand_kg: bool = False,
    ) -> SearchResult:
        """Performs hybrid retrieval using BM25 and Dense LSA fused via RRF.

        Args:
            query: User search query or problem description.
            top_k: Number of top roles to retrieve.
            expand_kg: Whether to traverse the Knowledge Graph to assemble a team.

        Returns:
            SearchResult containing SearchResultItems with dual score attribution.
        """
        # Fetch candidate pools from sparse and dense indexes
        sparse_candidates = self.bm25_index.search(query, limit=50)
        dense_candidates = self.dense_index.search(query, limit=50)

        # Merge via Reciprocal Rank Fusion
        fused = reciprocal_rank_fusion(
            sparse_candidates,
            dense_candidates,
            k=self.k,
            top_limit=top_k,
        )

        items: List[SearchResultItem] = []
        anchor_ids: List[str] = []

        for f_item in fused:
            r_id = f_item["role_id"]
            slug = f_item["slug"]
            role_model = self.roles_by_id.get(r_id) or self.roles_by_id.get(slug)
            name = role_model.title if role_model else f_item.get("name", slug)

            item_obj = SearchResultItem(
                role_id=r_id,
                slug=slug,
                name=name,
                role=role_model,
                sparse_score=f_item["sparse_score"],
                dense_score=f_item["dense_score"],
                sparse_rank=f_item["sparse_rank"],
                dense_rank=f_item["dense_rank"],
                rrf_score=f_item["rrf_score"],
                final_rank=f_item["final_rank"],
                has_sparse_contribution=f_item["has_sparse_contribution"],
                has_dense_contribution=f_item["has_dense_contribution"],
                attribution=f_item["attribution"],
            )
            items.append(item_obj)
            anchor_ids.append(r_id)

        # Knowledge Graph Expansion if requested
        expanded_team = None
        if expand_kg and self.graph and anchor_ids:
            expanded_team = expand_team_subgraph(
                graph=self.graph,
                anchor_role_ids=anchor_ids[:3],
                min_roles=8,
                max_roles=12,
                roles_by_id=self.roles_by_id,
            )

        return SearchResult(
            query=query,
            results=items,
            expanded_team=expanded_team,
        )
