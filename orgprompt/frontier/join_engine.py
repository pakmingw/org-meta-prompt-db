"""Nov 2026 Frontier AI Lab & Real-World Enterprise Join Engine (`orgprompt.frontier.join_engine`)."""

from __future__ import annotations

import json
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from orgprompt.frontier.catalog_bridges import REAL_WORLD_TO_FRONTIER_BRIDGES_CATALOG
from orgprompt.frontier.catalog_labs import FRONTIER_AI_LABS_CATALOG, FRONTIER_LAB_PODS_CATALOG
from orgprompt.frontier.models import (
    CompanyFrontierJoinResult,
    FrontierAILab,
    FrontierLabPod,
    ProblemFrontierBridgeResult,
    RealWorldToFrontierBridge,
    RoleFrontierJoinEdge,
    RoleFrontierJoinResult,
)
from orgprompt.frontier.role_mapper import select_frontier_joins_for_role
from orgprompt.frontier.schema import ensure_frontier_schema


def seed_frontier_join_layer(
    db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None,
) -> Dict[str, int]:
    """Idempotently seeds the 5 Frontier AI Labs, 30 Pods, 22 Cross-Industry Bridges, and 100% Role Joins."""
    owns_conn = not isinstance(db_path_or_conn, sqlite3.Connection)
    conn = ensure_frontier_schema(db_path_or_conn)
    try:
        cur = conn.cursor()

        # Resolve company_id dynamically if onboarded in fortune500_companies
        f500_rows = cur.execute("SELECT id, slug, lower(name) FROM fortune500_companies").fetchall()
        f500_by_key: Dict[str, str] = {}
        for cid, cslug, cname in f500_rows:
            f500_by_key[cid] = cid
            f500_by_key[cslug] = cid
            f500_by_key[cname] = cid

        for lab in FRONTIER_AI_LABS_CATALOG:
            resolved_cid = (
                f500_by_key.get(lab["company_id"] or "")
                or f500_by_key.get(lab["slug"])
                or f500_by_key.get(lab["name"].lower())
                or lab["company_id"]
            )
            cur.execute(
                """
                INSERT OR REPLACE INTO frontier_ai_labs (
                    id, slug, name, company_id, headquarters, corporate_governance_structure,
                    leadership_json, research_to_product_loop, flagship_models_json,
                    safety_control_framework, enterprise_gtm_fde_motion, compute_and_infra_strategy,
                    metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    lab["id"], lab["slug"], lab["name"], resolved_cid, lab["headquarters"],
                    lab["corporate_governance_structure"], json.dumps(lab["leadership"]),
                    lab["research_to_product_loop"], json.dumps(lab["flagship_models"]),
                    lab["safety_control_framework"], lab["enterprise_gtm_fde_motion"],
                    lab["compute_and_infra_strategy"], json.dumps(lab.get("metadata", {})),
                ),
            )

        for pod in FRONTIER_LAB_PODS_CATALOG:
            cur.execute(
                """
                INSERT OR REPLACE INTO frontier_lab_pods (
                    id, lab_id, slug, name, pod_category, mandate,
                    canonical_role_slugs_json, signature_artifacts_json, operating_cadence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pod["id"], pod["lab_id"], pod["slug"], pod["name"], pod["pod_category"],
                    pod["mandate"], json.dumps(pod["canonical_role_slugs"]),
                    json.dumps(pod["signature_artifacts"]), pod["operating_cadence"],
                ),
            )

        valid_industries = {r[0] for r in cur.execute("SELECT id FROM industries").fetchall()}
        bridges_seeded = 0
        for b in REAL_WORLD_TO_FRONTIER_BRIDGES_CATALOG:
            if b["industry_id"] not in valid_industries:
                continue
            cur.execute(
                """
                INSERT OR REPLACE INTO real_world_to_frontier_bridges (
                    id, slug, industry_id, domain_name, real_world_goal,
                    real_world_role_slugs_json, real_world_bottlenecks_json,
                    why_naive_llm_wrappers_fail, lead_frontier_labs_json,
                    frontier_pod_ids_json, frontier_role_slugs_json,
                    frontier_technical_recipe, joint_enterprise_lab_pod_topology
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    b["id"], b["slug"], b["industry_id"], b["domain_name"], b["real_world_goal"],
                    json.dumps(b["real_world_role_slugs"]), json.dumps(b["real_world_bottlenecks"]),
                    b["why_naive_llm_wrappers_fail"], json.dumps(b["lead_frontier_labs"]),
                    json.dumps(b["frontier_pod_ids"]), json.dumps(b["frontier_role_slugs"]),
                    b["frontier_technical_recipe"], b["joint_enterprise_lab_pod_topology"],
                ),
            )
            bridges_seeded += 1

        # Deterministic 100% canonical_roles join seeding
        role_rows = cur.execute(
            """
            SELECT r.id, r.slug, r.name, r.seniority_level, r.role_archetype, r.mission, COALESCE(o.industry_id, '')
            FROM canonical_roles r
            LEFT JOIN org_units u ON r.org_unit_id = u.id
            LEFT JOIN exemplar_orgs o ON u.exemplar_org_id = o.id
            ORDER BY r.slug
            """
        ).fetchall()
        roles_by_slug = {r[1]: r[0] for r in role_rows}

        cur.execute("DELETE FROM role_frontier_joins;")
        joins_seeded = 0
        for rid, rslug, rname, rsen, rarch, rmission, ind_id in role_rows:
            specs = select_frontier_joins_for_role(
                {
                    "id": rid, "slug": rslug, "name": rname,
                    "seniority_level": rsen, "role_archetype": rarch,
                    "mission": rmission, "industry_id": ind_id,
                },
                roles_by_slug,
            )
            for s in specs:
                edge_id = f"rfj_{rslug}__{s['target_slug']}__{s['join_mechanism'].lower()}"
                cur.execute(
                    """
                    INSERT OR REPLACE INTO role_frontier_joins (
                        id, source_enterprise_role_id, target_frontier_role_id,
                        join_mechanism, enterprise_pain_point, frontier_lab_capability,
                        joint_artifact, recommended_labs_json, priority_rank
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        edge_id, rid, s["target_id"], s["join_mechanism"],
                        s["enterprise_pain_point"], s["frontier_lab_capability"],
                        s["joint_artifact"], json.dumps(s["recommended_labs"]), s["priority_rank"],
                    ),
                )
                joins_seeded += 1

        conn.commit()
        return {
            "labs": len(FRONTIER_AI_LABS_CATALOG),
            "pods": len(FRONTIER_LAB_PODS_CATALOG),
            "bridges": bridges_seeded,
            "role_frontier_joins": joins_seeded,
        }
    finally:
        if owns_conn:
            conn.close()


class FrontierLabJoinEngine:
    """SDK Engine joining Real-World Enterprise/Creator Orgs & Roles to Nov 2026 Frontier AI Labs."""

    def __init__(self, db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None) -> None:
        self._owns_conn = not isinstance(db_path_or_conn, sqlite3.Connection)
        self.conn = ensure_frontier_schema(db_path_or_conn)
        self._search_engine: Any = None
        cnt = self.conn.execute("SELECT COUNT(*) FROM frontier_ai_labs").fetchone()[0]
        if cnt == 0:
            seed_frontier_join_layer(self.conn)

    def _get_search_engine(self) -> Any:
        if self._search_engine is None:
            import networkx as nx
            from orgprompt.search.hybrid import HybridSearchEngine
            self._search_engine = HybridSearchEngine.build_from_db(self.conn, graph=nx.MultiDiGraph())
        return self._search_engine

    def close(self) -> None:
        if self._owns_conn and self.conn:
            self.conn.close()

    def __enter__(self) -> FrontierLabJoinEngine:
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    def _hydrate_pod(self, row: tuple[Any, ...]) -> FrontierLabPod:
        return FrontierLabPod(
            id=row[0], lab_id=row[1], slug=row[2], name=row[3],
            pod_category=row[4], mandate=row[5],
            canonical_role_slugs=json.loads(row[6] or "[]"),
            signature_artifacts=json.loads(row[7] or "[]"),
            operating_cadence=row[8],
        )

    def _hydrate_lab(self, row: tuple[Any, ...], pods: List[FrontierLabPod]) -> FrontierAILab:
        return FrontierAILab(
            id=row[0], slug=row[1], name=row[2], company_id=row[3],
            headquarters=row[4], corporate_governance_structure=row[5],
            leadership=json.loads(row[6] or "[]"), research_to_product_loop=row[7],
            flagship_models=json.loads(row[8] or "[]"), safety_control_framework=row[9],
            enterprise_gtm_fde_motion=row[10], compute_and_infra_strategy=row[11],
            metadata=json.loads(row[12] or "{}"), pods=pods,
        )

    def _hydrate_bridge(self, row: tuple[Any, ...]) -> RealWorldToFrontierBridge:
        return RealWorldToFrontierBridge(
            id=row[0], slug=row[1], industry_id=row[2], domain_name=row[3],
            real_world_goal=row[4], real_world_role_slugs=json.loads(row[5] or "[]"),
            real_world_bottlenecks=json.loads(row[6] or "[]"), why_naive_llm_wrappers_fail=row[7],
            lead_frontier_labs=json.loads(row[8] or "[]"), frontier_pod_ids=json.loads(row[9] or "[]"),
            frontier_role_slugs=json.loads(row[10] or "[]"), frontier_technical_recipe=row[11],
            joint_enterprise_lab_pod_topology=row[12],
        )

    def _fetch_role_joins(self, role_ids: List[str]) -> List[RoleFrontierJoinEdge]:
        if not role_ids:
            return []
        placeholders = ",".join("?" for _ in role_ids)
        rows = self.conn.execute(
            f"""
            SELECT j.id, j.source_enterprise_role_id, sr.slug, sr.name,
                   j.target_frontier_role_id, tr.slug, tr.name,
                   j.join_mechanism, j.enterprise_pain_point, j.frontier_lab_capability,
                   j.joint_artifact, j.recommended_labs_json, j.priority_rank
            FROM role_frontier_joins j
            JOIN canonical_roles sr ON j.source_enterprise_role_id = sr.id
            JOIN canonical_roles tr ON j.target_frontier_role_id = tr.id
            WHERE j.source_enterprise_role_id IN ({placeholders})
            ORDER BY sr.slug, j.priority_rank
            """,
            role_ids,
        ).fetchall()
        return [
            RoleFrontierJoinEdge(
                id=r[0], source_enterprise_role_id=r[1], source_enterprise_role_slug=r[2],
                source_enterprise_role_title=r[3], target_frontier_role_id=r[4],
                target_frontier_role_slug=r[5], target_frontier_role_title=r[6],
                join_mechanism=r[7], enterprise_pain_point=r[8], frontier_lab_capability=r[9],
                joint_artifact=r[10], recommended_labs=json.loads(r[11] or "[]"), priority_rank=r[12],
            )
            for r in rows
        ]

    def list_labs(self) -> List[FrontierAILab]:
        pod_rows = self.conn.execute(
            "SELECT id, lab_id, slug, name, pod_category, mandate, canonical_role_slugs_json, signature_artifacts_json, operating_cadence FROM frontier_lab_pods ORDER BY id"
        ).fetchall()
        pods_by_lab: Dict[str, List[FrontierLabPod]] = {}
        for pr in pod_rows:
            pod = self._hydrate_pod(pr)
            pods_by_lab.setdefault(pod.lab_id, []).append(pod)

        lab_rows = self.conn.execute(
            """
            SELECT id, slug, name, company_id, headquarters, corporate_governance_structure,
                   leadership_json, research_to_product_loop, flagship_models_json,
                   safety_control_framework, enterprise_gtm_fde_motion, compute_and_infra_strategy, metadata_json
            FROM frontier_ai_labs ORDER BY id
            """
        ).fetchall()
        return [self._hydrate_lab(lr, pods_by_lab.get(lr[0], [])) for lr in lab_rows]

    def inspect_lab(self, slug_or_name: str) -> FrontierAILab:
        key = slug_or_name.strip().lower()
        aliases = {
            "gdm": "google_deepmind", "deepmind": "google_deepmind", "google": "google_deepmind",
            "meta": "meta_msl", "msl": "meta_msl", "fair": "meta_msl",
            "mistral": "mistral_ai", "claude": "anthropic", "gpt": "openai",
        }
        norm = aliases.get(key, key.replace(" ", "_").replace("-", "_"))
        for lab in self.list_labs():
            if key in (lab.id.lower(), lab.slug.lower(), lab.name.lower()) or norm in (lab.slug.lower(), lab.id.lower()):
                return lab
            if key in lab.name.lower():
                return lab
        raise ValueError(f"Frontier AI Lab not found for '{slug_or_name}'.")

    def list_bridges(self, industry_id_or_slug: Optional[str] = None) -> List[RealWorldToFrontierBridge]:
        rows = self.conn.execute(
            """
            SELECT id, slug, industry_id, domain_name, real_world_goal,
                   real_world_role_slugs_json, real_world_bottlenecks_json,
                   why_naive_llm_wrappers_fail, lead_frontier_labs_json,
                   frontier_pod_ids_json, frontier_role_slugs_json,
                   frontier_technical_recipe, joint_enterprise_lab_pod_topology
            FROM real_world_to_frontier_bridges ORDER BY id
            """
        ).fetchall()
        bridges = [self._hydrate_bridge(r) for r in rows]
        if not industry_id_or_slug:
            return bridges
        q = industry_id_or_slug.strip().lower()
        return [b for b in bridges if q in (b.industry_id.lower(), b.industry_id.replace("ind_", "").lower()) or q in b.slug.lower()]


    def _resolve_company(self, company_name_or_slug: str) -> tuple[str, str, str, int, str, str]:
        q = company_name_or_slug.strip()
        ql = q.lower()
        qslug = ql.replace(" ", "_").replace("-", "_")
        row = self.conn.execute(
            """
            SELECT c.id, c.slug, c.name, c.rank, c.industry_id, COALESCE(i.name, c.macro_industry)
            FROM fortune500_companies c
            LEFT JOIN industries i ON c.industry_id = i.id
            WHERE lower(c.id) = ? OR lower(c.slug) = ? OR lower(c.name) = ? OR lower(c.slug) = ?
            LIMIT 1
            """,
            (ql, ql, ql, qslug),
        ).fetchone()
        if not row:
            row = self.conn.execute(
                """
                SELECT c.id, c.slug, c.name, c.rank, c.industry_id, COALESCE(i.name, c.macro_industry)
                FROM fortune500_companies c
                LEFT JOIN industries i ON c.industry_id = i.id
                WHERE lower(c.name) LIKE ? OR lower(c.slug) LIKE ?
                ORDER BY c.rank ASC LIMIT 1
                """,
                (f"%{ql}%", f"%{qslug}%"),
            ).fetchone()
        if not row:
            raise ValueError(f"Company not found in fortune500_companies: '{company_name_or_slug}'")
        return (row[0], row[1], row[2], int(row[3]), row[4], row[5])

    def join_role(
        self,
        role_slug_or_query: str,
        company_name_or_slug: Optional[str] = None,
    ) -> RoleFrontierJoinResult:
        q = role_slug_or_query.strip()
        ql = q.lower()
        row = self.conn.execute(
            """
            SELECT r.id, r.slug, r.name, r.mission, COALESCE(i.id, ''), COALESCE(i.name, '')
            FROM canonical_roles r
            LEFT JOIN org_units u ON r.org_unit_id = u.id
            LEFT JOIN exemplar_orgs o ON u.exemplar_org_id = o.id
            LEFT JOIN industries i ON o.industry_id = i.id
            WHERE lower(r.id) = ? OR lower(r.slug) = ? OR lower(r.name) = ?
            LIMIT 1
            """,
            (ql, ql, ql),
        ).fetchone()
        if not row:
            search_engine = self._get_search_engine()
            sr = search_engine.search(q, top_k=5)
            chosen_id = None
            for item in sr.results:
                if not item.slug.startswith("frontier_"):
                    chosen_id = item.role_id
                    break
            if chosen_id is None and sr.results:
                chosen_id = sr.results[0].role_id
            if chosen_id:
                row = self.conn.execute(
                    """
                    SELECT r.id, r.slug, r.name, r.mission, COALESCE(i.id, ''), COALESCE(i.name, '')
                    FROM canonical_roles r
                    LEFT JOIN org_units u ON r.org_unit_id = u.id
                    LEFT JOIN exemplar_orgs o ON u.exemplar_org_id = o.id
                    LEFT JOIN industries i ON o.industry_id = i.id
                    WHERE r.id = ?
                    """,
                    (chosen_id,),
                ).fetchone()
        if not row:
            raise ValueError(f"Canonical role not found for '{role_slug_or_query}'.")

        rid, rslug, rtitle, rmission, ind_id, ind_name = row
        comp_name: Optional[str] = None
        comp_slug: Optional[str] = None
        if company_name_or_slug:
            _, comp_slug, comp_name, _, comp_ind_id, comp_ind_name = self._resolve_company(company_name_or_slug)
            if not ind_id:
                ind_id, ind_name = comp_ind_id, comp_ind_name

        swarms = [
            f"{s[0]} ({s[1]})"
            for s in self.conn.execute(
                "SELECT subagent_name, subagent_role FROM role_subagent_swarms WHERE role_id = ? ORDER BY subagent_role",
                (rid,),
            ).fetchall()
        ]
        joins = self._fetch_role_joins([rid])
        all_bridges = self.list_bridges()
        matching_bridges = [
            b for b in all_bridges
            if rslug in b.real_world_role_slugs or (ind_id and b.industry_id == ind_id)
        ][:3]

        lab_counts: Counter[str] = Counter()
        for j in joins:
            for lname in j.recommended_labs:
                lab_counts[lname] += 1
        labs_by_name = {l.name: l for l in self.list_labs()}
        rec_labs = [labs_by_name[n] for n, _ in lab_counts.most_common(3) if n in labs_by_name]

        return RoleFrontierJoinResult(
            query=role_slug_or_query, role_id=rid, role_slug=rslug, role_title=rtitle,
            industry_id=ind_id, industry_name=ind_name, role_mission=rmission,
            company_name=comp_name, company_slug=comp_slug, personal_subagents=swarms,
            frontier_joins=joins, matching_bridges=matching_bridges, recommended_labs=rec_labs,
        )

    def join_company(
        self,
        company_name_or_slug: str,
        focus: Optional[str] = None,
    ) -> CompanyFrontierJoinResult:
        cid, cslug, cname, crank, ind_id, ind_name = self._resolve_company(company_name_or_slug)
        emp_rows = self.conn.execute(
            """
            SELECT er.role_id, r.slug, r.name, er.department
            FROM employs_role er
            JOIN canonical_roles r ON er.role_id = r.id
            WHERE er.company_id = ?
            ORDER BY r.slug
            """,
            (cid,),
        ).fetchall()
        role_ids = [r[0] for r in emp_rows]
        if focus:
            fl = focus.lower()
            filtered = [r[0] for r in emp_rows if fl in r[1].lower() or fl in r[2].lower() or fl in r[3].lower()]
            if filtered:
                role_ids = filtered

        joins = self._fetch_role_joins(role_ids)
        counterpart_counts: Counter[tuple[str, str]] = Counter()
        mech_counts: Counter[str] = Counter()
        lab_counts: Counter[str] = Counter()
        for j in joins:
            counterpart_counts[(j.target_frontier_role_slug, j.target_frontier_role_title)] += 1
            mech_counts[j.join_mechanism] += 1
            for lname in j.recommended_labs:
                lab_counts[lname] += 1

        top_counterparts = [
            {"slug": k[0], "title": k[1], "joined_enterprise_roles_count": v}
            for k, v in counterpart_counts.most_common(8)
        ]
        labs_by_name = {l.name: l for l in self.list_labs()}
        lead_labs = [labs_by_name[n] for n, _ in lab_counts.most_common(3) if n in labs_by_name]
        ind_bridges = self.list_bridges(ind_id)

        return CompanyFrontierJoinResult(
            query=company_name_or_slug, company_id=cid, company_slug=cslug,
            company_name=cname, rank=crank, industry_id=ind_id, industry_name=ind_name,
            focus=focus, employed_roles_count=len(emp_rows), total_frontier_join_edges=len(joins),
            top_frontier_counterparts=top_counterparts, mechanism_distribution=dict(mech_counts),
            lead_frontier_labs=lead_labs, industry_bridges=ind_bridges,
            sample_role_joins=joins[:15],
        )


    def bridge_problem(
        self,
        problem_statement: str,
        company_name_or_slug: Optional[str] = None,
        top_k: int = 6,
    ) -> ProblemFrontierBridgeResult:
        from orgprompt.search.hybrid import HybridSearchEngine

        comp_name: Optional[str] = None
        comp_slug: Optional[str] = None
        comp_ind_id: Optional[str] = None
        allowed_role_ids: Optional[set[str]] = None
        if company_name_or_slug:
            cid, comp_slug, comp_name, _, comp_ind_id, _ = self._resolve_company(company_name_or_slug)
            emp = self.conn.execute("SELECT role_id FROM employs_role WHERE company_id = ?", (cid,)).fetchall()
            if emp:
                allowed_role_ids = {r[0] for r in emp}

        search_query = f"{comp_name} {problem_statement}" if comp_name else problem_statement
        search_engine = self._get_search_engine()
        sr = search_engine.search(search_query, top_k=max(top_k * 4, 24))

        selected_items = []
        for item in sr.results:
            if item.slug.startswith("frontier_"):
                continue
            if allowed_role_ids and item.role_id not in allowed_role_ids:
                continue
            selected_items.append(item)
            if len(selected_items) >= top_k:
                break

        if len(selected_items) < top_k:
            seen_ids = {x.role_id for x in selected_items}
            for item in sr.results:
                if not item.slug.startswith("frontier_") and item.role_id not in seen_ids:
                    selected_items.append(item)
                    seen_ids.add(item.role_id)
                    if len(selected_items) >= top_k:
                        break

        retrieved_roles = [
            {
                "role_id": it.role_id,
                "slug": it.slug,
                "title": it.name,
                "rrf_score": round(it.rrf_score, 5),
                "industry": it.role.industry if it.role else "",
            }
            for it in selected_items
        ]
        role_ids = [it.role_id for it in selected_items]
        joins = self._fetch_role_joins(role_ids)
        target_f_slugs = {j.target_frontier_role_slug for j in joins}
        source_r_slugs = {it.slug for it in selected_items}

        # Match pods whose canonical_role_slugs overlap the activated frontier roles
        all_labs = self.list_labs()
        pod_candidates: List[tuple[int, FrontierLabPod]] = []
        for lab in all_labs:
            for pod in lab.pods:
                overlap = len(target_f_slugs.intersection(pod.canonical_role_slugs))
                if overlap > 0:
                    pod_candidates.append((overlap, pod))
        pod_candidates.sort(key=lambda x: (-x[0], x[1].id))
        activated_pods = [p for _, p in pod_candidates[:6]]

        # Score bridges by overlap with retrieved enterprise roles, industry, and problem tokens
        p_tokens = {w.lower() for w in problem_statement.replace("/", " ").replace("-", " ").split() if len(w) > 3}
        scored_bridges: List[tuple[int, RealWorldToFrontierBridge]] = []
        for b in self.list_bridges():
            score = 3 * len(source_r_slugs.intersection(b.real_world_role_slugs))
            if comp_ind_id and b.industry_id == comp_ind_id:
                score += 4
            b_text = f"{b.domain_name} {b.real_world_goal} {b.frontier_technical_recipe}".lower()
            score += sum(1 for tok in p_tokens if tok in b_text)
            if score > 0:
                scored_bridges.append((score, b))
        scored_bridges.sort(key=lambda x: (-x[0], x[1].id))
        matching_bridges = [b for _, b in scored_bridges[:3]] or self.list_bridges()[:2]

        lab_counts: Counter[str] = Counter()
        for j in joins:
            for lname in j.recommended_labs:
                lab_counts[lname] += 1
        for b in matching_bridges:
            for lname in b.lead_frontier_labs:
                lab_counts[lname] += 2
        labs_by_name = {l.name: l for l in all_labs}
        rec_labs = [labs_by_name[n] for n, _ in lab_counts.most_common(3) if n in labs_by_name]

        plan = [
            f"Phase 1 — Ground Real-World Workflow & Failure Modes: Anchor on {', '.join(r['title'] for r in retrieved_roles[:3])} and their 6-Agent Personal Subagent Swarms; reject naive unverified prompt wrappers.",
            f"Phase 2 — Stand Up Typed MCP & Context Harnesses: Pair enterprise system owners with `{next((s for s in target_f_slugs if 'mcp' in s or 'computer_use' in s), 'frontier_context_engineering_mcp_architect')}` to expose read/canary-write domain state.",
            f"Phase 3 — Build Deterministic Outcome Verifiers & RFT/Distillation Forge: Co-design execution/conservation graders with `{next((s for s in target_f_slugs if 'rl' in s or 'swe' in s or 'eval' in s), 'frontier_test_time_compute_reasoning_rl_lead')}` across {', '.join(l.name for l in rec_labs[:2])}.",
            "Phase 4 — Enforce ASL / AI Control Safety & Production SLA Gate: Run subgroup calibration, indirect prompt-injection sandboxing, and unit-economics distillation sign-off prior to fleet rollout.",
        ]

        return ProblemFrontierBridgeResult(
            problem_statement=problem_statement, company_name=comp_name, company_slug=comp_slug,
            retrieved_enterprise_roles=retrieved_roles, frontier_joins=joins,
            activated_frontier_pods=activated_pods, matching_bridges=matching_bridges,
            recommended_labs=rec_labs, co_design_execution_plan=plan,
        )


def list_frontier_labs(db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None) -> List[FrontierAILab]:
    with FrontierLabJoinEngine(db_path_or_conn) as eng:
        return eng.list_labs()


def inspect_frontier_lab(slug_or_name: str, db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None) -> FrontierAILab:
    with FrontierLabJoinEngine(db_path_or_conn) as eng:
        return eng.inspect_lab(slug_or_name)


__all__ = [
    "seed_frontier_join_layer",
    "FrontierLabJoinEngine",
    "list_frontier_labs",
    "inspect_frontier_lab",
]
