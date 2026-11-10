"""Pure local semantic vectorizer using subword character LSA embeddings.

Integrates scikit-learn TfidfVectorizer (character n-grams 3–5 with word boundaries)
combined with TruncatedSVD (Latent Semantic Analysis, 128 dimensions) and cosine similarity.
Runs 100% locally on CPU with zero network dependencies and zero external API keys.
Guards against zero-norm vector division and preserves subword morphology for technical acronyms.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer

from orgprompt.db.connection import get_connection, get_default_db_path


class LocalDenseIndex:
    """100% Local Dense Semantic Index utilizing Subword Character LSA Embeddings."""

    def __init__(
        self,
        n_components: int = 128,
        ngram_range: Tuple[int, int] = (3, 5),
        random_state: int = 42,
    ) -> None:
        self.n_components = n_components
        self.ngram_range = ngram_range
        self.random_state = random_state

        self.vectorizer = TfidfVectorizer(
            analyzer="char_wb",
            ngram_range=self.ngram_range,
            sublinear_tf=True,
        )
        self.svd = TruncatedSVD(
            n_components=self.n_components,
            random_state=self.random_state,
        )

        self.role_ids: List[str] = []
        self.role_slugs: List[str] = []
        self.embeddings: Optional[np.ndarray] = None
        self._is_fitted: bool = False

    @property
    def is_fitted(self) -> bool:
        """Returns True if the index has been fitted with a role corpus."""
        return self._is_fitted

    def fit(
        self,
        role_ids: List[str],
        role_slugs: List[str],
        role_corpus: List[str],
    ) -> LocalDenseIndex:
        """Fits the subword TF-IDF vectorizer and SVD decomposition over the corpus.

        Args:
            role_ids: List of canonical role IDs (e.g. 'role_telecom_chief_network_architect').
            role_slugs: List of role slugs (e.g. 'telecom_chief_network_architect').
            role_corpus: List of rich role text descriptions.

        Returns:
            Self (fitted index).
        """
        if not role_corpus:
            raise ValueError("Cannot fit LocalDenseIndex on empty role corpus.")

        self.role_ids = list(role_ids)
        self.role_slugs = list(role_slugs)

        # Dynamic component count adaptation if corpus size is smaller than n_components
        effective_components = min(self.n_components, len(role_corpus) - 1)
        if effective_components < 1:
            effective_components = 1
        if effective_components != self.n_components:
            self.svd = TruncatedSVD(
                n_components=effective_components,
                random_state=self.random_state,
            )

        tfidf_matrix = self.vectorizer.fit_transform(role_corpus)
        dense_vectors = self.svd.fit_transform(tfidf_matrix)

        # Unit normalize embeddings with division-by-zero protection (SPEC § 2 Edge Case 4)
        norms = np.linalg.norm(dense_vectors, axis=1, keepdims=True)
        self.embeddings = dense_vectors / np.maximum(norms, 1e-12)
        self._is_fitted = True

        return self

    @classmethod
    def fit_from_db(
        cls,
        db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None,
        n_components: int = 128,
    ) -> LocalDenseIndex:
        """Hydrates role metadata from SQLite and fits the LocalDenseIndex."""
        if isinstance(db_path_or_conn, sqlite3.Connection):
            conn = db_path_or_conn
            close_on_exit = False
        else:
            path = db_path_or_conn or get_default_db_path()
            conn = get_connection(path)
            close_on_exit = True

        try:
            cursor = conn.cursor()
            # Aggregate role contextual entities across graph
            cursor.execute("""
                SELECT role_id, GROUP_CONCAT(title || ' ' || cognitive_bottlenecks, ' ')
                FROM role_use_cases
                GROUP BY role_id;
            """)
            use_cases_by_role = dict(cursor.fetchall())

            cursor.execute("""
                SELECT rt.role_id, GROUP_CONCAT(t.name || ' ' || t.archetype, ' ')
                FROM role_tooling rt
                JOIN tools t ON rt.tool_id = t.id
                GROUP BY rt.role_id;
            """)
            tools_by_role = dict(cursor.fetchall())

            cursor.execute("""
                SELECT role_id, GROUP_CONCAT(subagent_name || ' ' || subagent_role, ' ')
                FROM role_subagent_swarms
                GROUP BY role_id;
            """)
            swarms_by_role = dict(cursor.fetchall())

            cursor.execute("""
                SELECT er.role_id, GROUP_CONCAT(c.name || ' ' || c.macro_industry, ' ')
                FROM employs_role er
                JOIN fortune500_companies c ON er.company_id = c.id
                GROUP BY er.role_id;
            """)
            companies_by_role = dict(cursor.fetchall())

            cursor.execute("""
                SELECT
                    id,
                    slug,
                    name,
                    mission,
                    capabilities_json,
                    mental_models_json,
                    technical_vocabulary_json,
                    system_prompt
                FROM canonical_roles
                ORDER BY id ASC;
            """)
            rows = cursor.fetchall()
            if not rows:
                raise ValueError("No canonical roles found in database to fit dense index.")

            role_ids = []
            role_slugs = []
            role_corpus = []

            for r in rows:
                r_id, r_slug, r_name, r_mission, caps_j, mental_j, vocab_j, prompt = r
                caps = " ".join(json.loads(caps_j) if caps_j else [])
                mentals = " ".join(json.loads(mental_j) if mental_j else [])
                vocabs = " ".join(json.loads(vocab_j) if vocab_j else [])
                readable_slug = r_slug.replace("_", " ")

                uc_text = use_cases_by_role.get(r_id, "")
                tools_text = tools_by_role.get(r_id, "")
                swarms_text = swarms_by_role.get(r_id, "")
                comps_text = companies_by_role.get(r_id, "")

                # Construct rich multimodal lexical document incorporating Section 7 & graph entities
                text = (
                    f"{r_name} {readable_slug} {r_mission} "
                    f"{caps} {mentals} {vocabs} "
                    f"{uc_text} {tools_text} {swarms_text} {comps_text} "
                    f"{prompt[:3500]}"
                )
                role_ids.append(r_id)
                role_slugs.append(r_slug)
                role_corpus.append(text)

            index = cls(n_components=n_components)
            index.fit(role_ids, role_slugs, role_corpus)
            return index
        finally:
            if close_on_exit and conn:
                conn.close()

    def search(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Computes cosine similarity of query against role embeddings and returns top-k.

        Guards against zero-norm vectors when query contains only rare characters or whitespace.
        """
        if not self._is_fitted or self.embeddings is None:
            raise RuntimeError("LocalDenseIndex must be fitted before calling search().")

        if not query or not query.strip():
            return []

        # Vectorize query
        q_tfidf = self.vectorizer.transform([query])
        q_dense = self.svd.transform(q_tfidf)

        q_norm = float(np.linalg.norm(q_dense))
        # Zero-norm division guard (SPEC § 2 Edge Case 4 & Tier 2 Boundary)
        q_normed = q_dense / max(q_norm, 1e-12)

        # Dot product of L2-normalized vectors yields exact cosine similarity
        similarities = np.dot(self.embeddings, q_normed.T).flatten()

        # Bounded cosine similarity guard [-1.0, 1.0]
        similarities = np.clip(similarities, -1.0, 1.0)

        effective_limit = min(limit, len(self.role_ids))
        top_indices = np.argsort(-similarities)[:effective_limit]

        results: List[Dict[str, Any]] = []
        for rank, idx in enumerate(top_indices, start=1):
            results.append({
                "role_id": self.role_ids[idx],
                "slug": self.role_slugs[idx],
                "dense_rank": rank,
                "dense_score": float(similarities[idx]),
            })

        return results
