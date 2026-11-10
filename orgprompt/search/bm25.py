"""Sparse lexical retrieval engine using SQLite FTS5 BM25.

Provides robust FTS5 query sanitization protecting against punctuation/hyphen syntax
errors ('C++', '6G', 'p99.9', slashes, unmatched quotes, boolean tokens), and executes
BM25 queries against the roles_fts virtual table.
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from orgprompt.db.connection import get_connection, get_default_db_path


def sanitize_fts5_query(query_text: str) -> str:
    """Safely sanitizes a raw user query for SQLite FTS5 MATCH execution.

    Strips invalid syntax characters and operators, extracts alphanumeric and
    hyphenated tokens, and formats them with prefix wildcards. Returns an empty
    quoted string if no valid tokens remain to avoid syntax errors.
    """
    if not query_text or not query_text.strip():
        return '""'

    # Extract tokens with word characters and hyphens
    tokens = [re.sub(r"[^\w\-]", "", t) for t in query_text.split() if t.strip()]
    valid_tokens = [f'"{t}"*' for t in tokens if len(t) > 0]

    return " OR ".join(valid_tokens) if valid_tokens else '""'


def search_sparse_bm25(
    db_conn: sqlite3.Connection,
    query_text: str,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """Executes a sparse lexical BM25 search on the roles_fts virtual table.

    Args:
        db_conn: Open SQLite database connection.
        query_text: Free-text search query.
        limit: Maximum number of candidate results to return.

    Returns:
        List of dicts containing role_id, slug, name, sparse_rank, and sparse_score.
    """
    sanitized = sanitize_fts5_query(query_text)
    if sanitized == '""':
        return []

    cursor = db_conn.cursor()
    # In SQLite FTS5, bm25() returns negative numbers where more negative is more relevant.
    # We sort ASC by raw_score, and invert it as sparse_score (-raw_score) so higher is better.
    sql = """
        SELECT
            f.role_id,
            r.slug,
            r.name,
            bm25(roles_fts) as raw_score
        FROM roles_fts f
        JOIN canonical_roles r ON f.role_id = r.id
        WHERE roles_fts MATCH ?
        ORDER BY raw_score ASC
        LIMIT ?;
    """
    cursor.execute(sql, (sanitized, limit))
    rows = cursor.fetchall()

    results: List[Dict[str, Any]] = []
    for rank, (role_id, slug, name, raw_score) in enumerate(rows, start=1):
        raw_val = float(raw_score)
        results.append({
            "role_id": role_id,
            "slug": slug,
            "name": name,
            "sparse_rank": rank,
            "sparse_score": -raw_val,
            "raw_score": raw_val,
        })

    return results


class BM25Index:
    """Self-contained interface for sparse BM25 lexical search over SQLite FTS5."""

    def __init__(
        self,
        db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None,
    ) -> None:
        if isinstance(db_path_or_conn, sqlite3.Connection):
            self._conn = db_path_or_conn
            self._owns_conn = False
        else:
            path = db_path_or_conn or get_default_db_path()
            self._conn = get_connection(path)
            self._owns_conn = True

    def search(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Searches roles_fts using BM25 ranking and sanitization."""
        return search_sparse_bm25(self._conn, query, limit=limit)

    def close(self) -> None:
        """Closes the underlying connection if owned."""
        if self._owns_conn and self._conn:
            self._conn.close()
