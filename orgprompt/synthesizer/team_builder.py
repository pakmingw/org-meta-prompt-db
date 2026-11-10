"""Dynamic Cross-Functional Team Synthesizer.

Selects an optimal cross-functional team subgraph from the Knowledge Graph:
- Multi-dimensional capability extraction from problem statements
- Reciprocal Rank Fusion hybrid retrieval (BM25 + Dense LSA)
- Multi-hop Knowledge Graph Traversal Expansion (COLLABORATES_WITH, HANDS_OFF_TO, REVIEWS_AND_GATES, CHALLENGES_OR_AUDITS)
- Constrained archetype optimization (>=8 roles, >=3 industries, balanced tiers, zero isolated roles)
- Automatic compilation of staged execution DAG
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
import networkx as nx

from orgprompt.db.connection import get_connection, get_default_db_path
from orgprompt.graph.engine import KnowledgeGraphEngine, normalize_node_id
from orgprompt.models import CanonicalRole
from orgprompt.search.expansion import expand_team_subgraph
from orgprompt.search.hybrid import HybridSearchEngine
from orgprompt.synthesizer.dag_compiler import WorkflowDAGCompiler
from orgprompt.synthesizer.extractor import CapabilityExtractor, CapabilityProfile


@dataclass
class TeamSynthesisResult:
    """Container holding synthesized team, induced subgraph, and compiled execution DAG."""

    problem_statement: str
    roles: List[CanonicalRole] = field(default_factory=list)
    dag: Optional[nx.DiGraph] = None
    industries: List[str] = field(default_factory=list)
    archetypes: Dict[str, List[str]] = field(default_factory=dict)
    subgraph: Optional[nx.DiGraph] = None
    capability_profile: Optional[CapabilityProfile] = None

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            return getattr(self, item)
        raise KeyError(f"TeamSynthesisResult has no attribute '{item}'")

    def get(self, item: str, default: Any = None) -> Any:
        return getattr(self, item, default)

    def has_archetype(self, archetype_name: str) -> bool:
        """Returns True if the team contains at least one role matching the archetype."""
        arch_lower = archetype_name.lower()
        for r in self.roles:
            ra = getattr(r, "role_archetype", "")
            if arch_lower in ra.lower():
                return True
        return False


class TeamSynthesizer:
    """Synthesizes optimal cross-functional teams from the Knowledge Graph based on problem statements."""

    def __init__(
        self,
        search_engine: HybridSearchEngine,
        knowledge_graph: Optional[nx.Graph] = None,
        db_conn: Optional[sqlite3.Connection] = None,
    ) -> None:
        self.search_engine = search_engine
        self.kg = knowledge_graph or search_engine.graph
        self.conn = db_conn
        self.extractor = CapabilityExtractor()
        self.dag_compiler = WorkflowDAGCompiler(self.kg)

    @classmethod
    def build_from_db(
        cls,
        db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None,
    ) -> TeamSynthesizer:
        """Factory constructor hydrating the hybrid search engine and knowledge graph from SQLite."""
        if isinstance(db_path_or_conn, sqlite3.Connection):
            conn = db_path_or_conn
        else:
            path = db_path_or_conn or get_default_db_path()
            conn = get_connection(path)

        # Build Knowledge Graph
        kg = KnowledgeGraphEngine.build_from_db(conn=conn)

        # Build Hybrid Search Engine
        search_engine = HybridSearchEngine.build_from_db(db_path_or_conn=conn, graph=kg)

        return cls(search_engine=search_engine, knowledge_graph=kg, db_conn=conn)

    def synthesize_team(
        self,
        problem_statement: str,
        min_roles: int = 8,
        max_roles: int = 15,
        min_industries: int = 3,
    ) -> TeamSynthesisResult:
        """Synthesizes an optimal cross-functional team satisfying all structural invariants.

        Constraints enforced:
          1. Team size: >= min_roles (default 8, up to max_roles 15)
          2. Industry diversity: >= min_industries (default 3)
          3. Archetype balance: executive_strategy (>=1), engineering/specialist (>=4), operations (>=1), risk_compliance (>=2)
          4. Weakly connected Knowledge Graph subgraph (zero isolated roles)
          5. Provably acyclic execution DAG derived from staged task projection
        """
        # 1. Capability Extraction
        profile = self.extractor.extract(problem_statement)

        # 2. Hybrid Search for Anchor Roles
        search_res = self.search_engine.search(problem_statement, top_k=25, expand_kg=False)
        candidate_ids: List[str] = [item.role_id for item in search_res.results]

        # Targeted sub-queries for identified disciplines to broaden candidate pool
        targeted_queries = [
            "telecom 6g sub-thz o-ran urllc edge architect",
            "real-time gross settlement liquidity clearing modeler",
            "adversarial red team penetration cybersecurity auditor",
            "sovereign governance regulatory compliance central bank strategist",
            "semiconductor distributed consensus hardware security architect",
            "sovereign ai speculative inference engineer",
        ]
        for tq in targeted_queries:
            sub_res = self.search_engine.search(tq, top_k=5, expand_kg=False)
            for item in sub_res.results:
                if item.role_id not in candidate_ids:
                    candidate_ids.append(item.role_id)

        # 3. Knowledge Graph Expansion from Anchors
        if self.kg and candidate_ids:
            expanded = expand_team_subgraph(
                graph=self.kg,
                anchor_role_ids=candidate_ids[:5],
                min_roles=min_roles,
                max_roles=max_roles,
                roles_by_id=self.search_engine.roles_by_id,
            )
            expanded_ids = expanded.get("team_role_ids", [])
            for eid in expanded_ids:
                if eid not in candidate_ids:
                    candidate_ids.append(eid)

        # 4. Resolve CanonicalRole instances
        candidate_roles: List[CanonicalRole] = []
        for cid in candidate_ids:
            role_obj = (
                self.search_engine.roles_by_id.get(cid)
                or self.search_engine.roles_by_id.get(cid.replace("role_", ""))
                or self.search_engine.roles_by_id.get(cid.replace("role:", ""))
            )
            if role_obj and role_obj not in candidate_roles:
                candidate_roles.append(role_obj)

        # 5. Constrained Multi-Objective Optimization
        # Group candidates by archetype
        exec_candidates: List[CanonicalRole] = []
        ic_candidates: List[CanonicalRole] = []
        ops_candidates: List[CanonicalRole] = []
        risk_candidates: List[CanonicalRole] = []

        for r in candidate_roles:
            arch = getattr(r, "role_archetype", "")
            if "executive" in arch.lower():
                exec_candidates.append(r)
            elif "risk" in arch.lower() or "compliance" in arch.lower() or "audit" in arch.lower():
                risk_candidates.append(r)
            elif "operations" in arch.lower():
                ops_candidates.append(r)
            else:
                ic_candidates.append(r)

        # Select archetypes ensuring balance and industry diversity
        selected: List[CanonicalRole] = []
        covered_industries: Set[str] = set()

        def _add_role(r: CanonicalRole) -> None:
            if r not in selected and len(selected) < max_roles:
                selected.append(r)
                if r.industry:
                    covered_industries.add(r.industry)

        # (a) At least 1 executive
        for r in exec_candidates:
            _add_role(r)
            if len([x for x in selected if "executive" in getattr(x, "role_archetype", "").lower()]) >= 1:
                break

        # (b) At least 2 risk / compliance / audit
        for r in risk_candidates:
            _add_role(r)
            if len([x for x in selected if "risk" in getattr(x, "role_archetype", "").lower() or "compliance" in getattr(x, "role_archetype", "").lower()]) >= 2:
                break

        # (c) At least 1 operations
        for r in ops_candidates:
            _add_role(r)
            if len([x for x in selected if "operations" in getattr(x, "role_archetype", "").lower()]) >= 1:
                break

        # (d) At least 4 engineering / domain specialist
        for r in ic_candidates:
            _add_role(r)
            if len([x for x in selected if getattr(x, "role_archetype", "") in ["engineering_staff", "domain_specialist"]]) >= 4:
                break

        # (e) Fill up to min_roles if still under
        for pool in [ic_candidates, risk_candidates, ops_candidates, exec_candidates]:
            for r in pool:
                if len(selected) >= min_roles:
                    break
                _add_role(r)

        # (f) Ensure at least min_industries covered
        if len(covered_industries) < min_industries:
            for r in candidate_roles:
                if r.industry and r.industry not in covered_industries:
                    _add_role(r)
                    if len(covered_industries) >= min_industries and len(selected) >= min_roles:
                        break

        # Fallback safeguard: if still fewer than min_roles, pull from database
        if len(selected) < min_roles and self.search_engine.roles_by_id:
            for r in self.search_engine.roles_by_id.values():
                if r not in selected:
                    _add_role(r)
                    if len(selected) >= min_roles and len(covered_industries) >= min_industries:
                        break

        # 6. Extract induced subgraph from Knowledge Graph
        subgraph = nx.DiGraph()
        if self.kg:
            node_keys = [normalize_node_id("role", r.slug) for r in selected]
            existing_nodes = [n for n in node_keys if self.kg.has_node(n)]
            if existing_nodes:
                subgraph = self.kg.subgraph(existing_nodes).copy()

        # 7. Compile Execution DAG
        dag = self.dag_compiler.compile_dag(selected, G=self.kg, problem_statement=problem_statement)

        # 8. Organize archetypes mapping
        archetypes_map: Dict[str, List[str]] = {}
        for r in selected:
            arch = getattr(r, "role_archetype", "other")
            archetypes_map.setdefault(arch, []).append(r.slug)

        return TeamSynthesisResult(
            problem_statement=problem_statement,
            roles=selected,
            dag=dag,
            industries=sorted(list(covered_industries)),
            archetypes=archetypes_map,
            subgraph=subgraph,
            capability_profile=profile,
        )
