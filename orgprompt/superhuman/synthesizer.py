"""Superhuman Role Synthesis Engine supporting 3 input pathways and 5-edge OKG fusion."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from orgprompt.db.connection import get_connection, get_default_db_path
from orgprompt.db.schema import ensure_superhuman_schema
from orgprompt.scaffolder.role_scaffolder import RoleScaffolder, RoleScaffoldingPackage
from orgprompt.search.hybrid import HybridSearchEngine
from orgprompt.superhuman.formatter import compile_deep_superhuman_prompt
from orgprompt.superhuman.models import (
     INPUT_MODES,
    AdjacentRoleFusion,
    SuperhumanRolePackage,
)
from orgprompt.superhuman.profiler import (
    build_academic_foundation,
    build_human_characteristics,
    build_on_the_job_crucibles,
    build_unknown_problem_epistemology,
)


_EDGE_PRIORITY = {
    "CHALLENGES_OR_AUDITS": 0,
    "REVIEWS_AND_GATES": 1,
    "HANDS_OFF_TO": 2,
    "COLLABORATES_WITH": 3,
    "REPORTS_TO": 4,
}


def _slugify(text: str, max_len: int = 48) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return (cleaned[:max_len].rstrip("_")) or "specialist"


def _merge_developer_context(
    developer_context: Optional[str],
    context_file: Optional[Union[str, Path]],
) -> str:
    parts: List[str] = []
    if developer_context and developer_context.strip():
        parts.append(developer_context.strip())
    if context_file is not None and str(context_file).strip():
        cpath = Path(context_file)
        if not cpath.is_file():
            raise FileNotFoundError(f"Developer context file not found: {cpath}")
        file_text = cpath.read_text(encoding="utf-8").strip()
        if file_text:
            parts.append(f"[Source File: {cpath.name}]\n{file_text}")
    return "\n\n".join(parts)


def _parse_custom_role_spec(
    raw_spec: Union[Dict[str, Any], str, Path],
    problem_hint: str = "",
) -> Dict[str, Any]:
    """Normalizes a dict, file path, JSON string, or raw agent prompt/title into a role dict."""
    data: Dict[str, Any] = {}

    if isinstance(raw_spec, dict):
        data = dict(raw_spec)
    elif isinstance(raw_spec, Path):
        if not raw_spec.is_file():
            raise FileNotFoundError(f"Custom role file not found: {raw_spec}")
        content = raw_spec.read_text(encoding="utf-8").strip()
        if raw_spec.suffix.lower() == ".json" or content.startswith("{"):
            data = json.loads(content)
        else:
            data = _extract_role_from_text(content, fallback_title=raw_spec.stem.replace("_", " ").title())
    elif isinstance(raw_spec, str):
        stripped = raw_spec.strip()
        if not stripped:
            raise ValueError("Empty custom_role_spec string provided.")
        is_potential_path = len(stripped) < 512 and "\n" not in stripped and not stripped.startswith("{")
        if is_potential_path and Path(stripped).is_file():
            p = Path(stripped)
            content = p.read_text(encoding="utf-8").strip()
            if p.suffix.lower() == ".json" or content.startswith("{"):
                data = json.loads(content)
            else:
                data = _extract_role_from_text(content, fallback_title=p.stem.replace("_", " ").title())
        elif stripped.startswith("{"):
            try:
                data = json.loads(stripped)
            except json.JSONDecodeError:
                data = _extract_role_from_text(stripped, fallback_title="Custom Specialist Agent")
        elif len(stripped) <= 110 and "\n" not in stripped:
            data = {
                "title": stripped,
                "mission": f"Execute specialized {stripped} responsibilities for: {problem_hint or 'frontier engineering challenges'}.",
                "system_prompt": f"You are {stripped}. Solve mission-critical domain challenges rigorously.",
            }
        else:
            data = _extract_role_from_text(stripped, fallback_title="Custom Agent Specialist")
    else:
        raise TypeError(f"Unsupported custom_role_spec type: {type(raw_spec)}")

    # Unwrap nested {"role": {...}} if passed a scaffolded role JSON
    if "role" in data and isinstance(data["role"], dict) and ("title" in data["role"] or "name" in data["role"]):
        inner = dict(data["role"])
        for extra_k in ("use_cases", "tools", "subagent_swarm", "genai_plan"):
            if extra_k in data and extra_k not in inner:
                inner[extra_k] = data[extra_k]
        data = inner

    title = str(data.get("title") or data.get("name") or data.get("role_title") or "Custom Agent Specialist").strip()
    slug = str(data.get("slug") or f"custom_{_slugify(title)}").strip()
    role_id = str(data.get("id") or f"role_{slug}").strip()
    mission = str(
        data.get("mission")
        or data.get("description")
        or f"Architect, execute, and verify high-assurance solutions as {title}."
    ).strip()
    sys_prompt = str(
        data.get("system_prompt")
        or data.get("prompt")
        or f"You are {title}. Mission: {mission}"
    ).strip()

    return {
        "id": role_id,
        "slug": slug,
        "name": title,
        "title": title,
        "seniority_level": str(data.get("seniority_level") or data.get("seniority_tier") or "PRINCIPAL_STAFF"),
        "seniority_tier": str(data.get("seniority_tier") or data.get("seniority_level") or "PRINCIPAL_STAFF"),
        "role_archetype": str(data.get("role_archetype") or "domain_specialist"),
        "mission": mission,
        "system_prompt": sys_prompt,
        "character_count": len(sys_prompt),
        "capabilities": list(data.get("capabilities") or []),
        "mental_models": list(data.get("mental_models") or []),
        "heuristics": list(data.get("heuristics") or data.get("domain_heuristics") or []),
        "vocabulary": list(data.get("vocabulary") or data.get("technical_vocabulary") or []),
        "anti_patterns": list(data.get("anti_patterns") or []),
        "unit_name": str(data.get("unit_name") or "Custom Agent Architecture Unit"),
        "exemplar_name": str(data.get("exemplar_name") or data.get("exemplar_org") or "Frontier Agentic Exemplar"),
        "industry_name": str(data.get("industry_name") or data.get("industry") or "Cross-Domain Enterprise"),
        "_custom_use_cases": data.get("use_cases"),
        "_custom_tools": data.get("tools"),
        "_custom_swarm": data.get("subagent_swarm"),
    }


def _extract_role_from_text(text: str, fallback_title: str) -> Dict[str, Any]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    title = fallback_title
    for ln in lines[:8]:
        m_head = re.match(r"^#+\s+(.+)$", ln)
        if m_head:
            title = m_head.group(1).strip()[:90]
            break
        m_you = re.search(r"You are (?:an?|the)\s+([^.,\n]{4,80})", ln, flags=re.IGNORECASE)
        if m_you:
            title = m_you.group(1).strip()
            break
    mission = lines[1] if len(lines) > 1 else lines[0][:240]
    return {
        "title": title,
        "mission": mission[:300],
        "system_prompt": text,
    }


def _blind_spot_rationale(edge_type: str, direction: str, neighbor_title: str, industry: str) -> str:
    if edge_type == "CHALLENGES_OR_AUDITS":
        return (
            f"Internalizes independent adversarial scrutiny from {neighbor_title} ({industry}), catching silent "
            f"compliance, tail-risk, and security blind spots before external audit or production failure."
        )
    if edge_type == "REVIEWS_AND_GATES":
        return (
            f"Embeds the release/architecture quality gate of {neighbor_title} directly into design time, preventing "
            f"late-stage rework and broken readiness invariants."
        )
    if edge_type == "HANDS_OFF_TO":
        if direction == "OUTGOING":
            return (
                f"Eliminates 'throw-it-over-the-wall' handoff friction by designing outputs directly operable and "
                f"verifiable by downstream {neighbor_title}."
            )
        return (
            f"Eliminates upstream data/spec poisoning by enforcing strict ingress validation on artifacts received from {neighbor_title}."
        )
    if edge_type == "REPORTS_TO":
        return (
            f"Aligns technical execution with executive capital-allocation, ROIC, and strategic trade-offs governed by {neighbor_title}."
        )
    return (
        f"Bridges cross-silo impedance mismatch with peer {neighbor_title} ({industry}), ensuring shared state invariants hold end-to-end."
    )


class SuperhumanRoleSynthesizer:
    """Synthesizes Superhuman Role Packages across Problem Discovery, Canonical Role, and Custom Agent Role modes."""

    def __init__(
        self,
        conn: Optional[sqlite3.Connection] = None,
        db_path: Optional[Union[str, Path]] = None,
        search_engine: Optional[HybridSearchEngine] = None,
        scaffolder: Optional[RoleScaffolder] = None,
    ) -> None:
        self._db_path = db_path
        self.conn = conn or get_connection(db_path or get_default_db_path())
        self._owns_conn = conn is None
        self._search_engine = search_engine
        self._scaffolder = scaffolder

    def __enter__(self) -> SuperhumanRoleSynthesizer:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_conn and self.conn is not None:
            self.conn.close()

    @classmethod
    def build_from_db(
        cls,
        db_path_or_conn: Optional[Union[sqlite3.Connection, str, Path]] = None,
        db_path: Optional[Union[str, Path]] = None,
    ) -> SuperhumanRoleSynthesizer:
        target = db_path_or_conn if db_path_or_conn is not None else db_path
        if isinstance(target, sqlite3.Connection):
            return cls(conn=target)
        return cls(db_path=target)

    @property
    def search_engine(self) -> HybridSearchEngine:
        if self._search_engine is None:
            self._search_engine = HybridSearchEngine.build_from_db(self.conn)
        return self._search_engine

    @property
    def scaffolder(self) -> RoleScaffolder:
        if self._scaffolder is None:
            self._scaffolder = RoleScaffolder(conn=self.conn)
        return self._scaffolder

    def _assemble_enterprise_team(
        self,
        query: str,
        exclude_role_id: Optional[str],
        max_team: int = 6,
    ) -> List[Dict[str, Any]]:
        res = self.search_engine.search(query, top_k=16)
        chosen: List[Dict[str, Any]] = []
        seen_ids = {exclude_role_id} if exclude_role_id else set()
        seen_archetypes = set()

        # Pass 1: maximize archetype diversity
        for item in res.results:
            if item.role_id in seen_ids:
                continue
            arch = item.role.role_archetype if item.role else "specialist"
            if arch not in seen_archetypes:
                seen_archetypes.add(arch)
                seen_ids.add(item.role_id)
                chosen.append({
                    "id": item.role_id,
                    "slug": item.slug,
                    "title": item.name,
                    "role_archetype": arch,
                    "seniority_tier": item.role.seniority_tier if item.role else "PRINCIPAL_STAFF",
                    "industry": item.role.industry if item.role else "Enterprise",
                    "rrf_score": round(item.rrf_score, 6),
                })
                if len(chosen) >= max_team:
                    return chosen

        # Pass 2: fill remaining top-ranked specialists
        for item in res.results:
            if len(chosen) >= max_team:
                break
            if item.role_id in seen_ids:
                continue
            seen_ids.add(item.role_id)
            chosen.append({
                "id": item.role_id,
                "slug": item.slug,
                "title": item.name,
                "role_archetype": item.role.role_archetype if item.role else "specialist",
                "seniority_tier": item.role.seniority_tier if item.role else "PRINCIPAL_STAFF",
                "industry": item.role.industry if item.role else "Enterprise",
                "rrf_score": round(item.rrf_score, 6),
            })
        return chosen

    def _traverse_adjacent_roles(
        self,
        anchor_role_id: Optional[str],
        adjacent_k: int = 4,
    ) -> List[AdjacentRoleFusion]:
        if not anchor_role_id or adjacent_k <= 0:
            return []
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT
                e.source_role_id, e.target_role_id, e.edge_type,
                e.description, e.protocol, e.cadence
            FROM role_edges e
            WHERE (e.source_role_id = ? OR e.target_role_id = ?)
              AND e.edge_type IN (
                  'COLLABORATES_WITH', 'HANDS_OFF_TO',
                  'REVIEWS_AND_GATES', 'CHALLENGES_OR_AUDITS', 'REPORTS_TO'
              )
            """,
            (anchor_role_id, anchor_role_id),
        )
        raw_edges = cur.fetchall()
        if not raw_edges:
            return []

        candidates: List[Tuple[int, str, str, str, str, str, str]] = []
        for src_id, dst_id, edge_type, desc, proto, cadence in raw_edges:
            if src_id == anchor_role_id:
                neighbor_id = dst_id
                direction = "OUTGOING"
            else:
                neighbor_id = src_id
                direction = "INCOMING"
            if neighbor_id == anchor_role_id:
                continue
            prio = _EDGE_PRIORITY.get(edge_type, 9)
            candidates.append((prio, neighbor_id, edge_type, direction, desc or "", proto or "", cadence or ""))

        # Sort by edge priority while diversifying across edge types first
        candidates.sort(key=lambda x: (x[0], x[1]))
        selected: List[Tuple[str, str, str, str, str, str]] = []
        seen_neighbors = set()
        used_edge_types = set()

        for _, nid, etype, direc, desc, proto, cad in candidates:
            if nid in seen_neighbors:
                continue
            if etype not in used_edge_types:
                used_edge_types.add(etype)
                seen_neighbors.add(nid)
                selected.append((nid, etype, direc, desc, proto, cad))
                if len(selected) >= adjacent_k:
                    break

        for _, nid, etype, direc, desc, proto, cad in candidates:
            if len(selected) >= adjacent_k:
                break
            if nid in seen_neighbors:
                continue
            seen_neighbors.add(nid)
            selected.append((nid, etype, direc, desc, proto, cad))

        fused: List[AdjacentRoleFusion] = []
        for nid, etype, direc, desc, proto, cad in selected:
            r_row = cur.execute(
                """
                SELECT
                    r.id, r.slug, r.name, r.capabilities_json, r.mental_models_json,
                    r.domain_heuristics_json, r.anti_patterns_json,
                    o.name, i.name
                FROM canonical_roles r
                LEFT JOIN org_units u ON r.org_unit_id = u.id
                LEFT JOIN exemplar_orgs o ON u.exemplar_org_id = o.id
                LEFT JOIN industries i ON o.industry_id = i.id
                WHERE r.id = ?
                LIMIT 1;
                """,
                (nid,),
            ).fetchone()
            if not r_row:
                continue

            art_rows = cur.execute(
                """
                SELECT a.name
                FROM role_artifacts ra
                JOIN artifacts a ON ra.artifact_id = a.id
                WHERE ra.role_id = ?
                ORDER BY ra.direction ASC, a.name ASC
                LIMIT 5;
                """,
                (nid,),
            ).fetchall()
            artifacts = [ar[0] for ar in art_rows]
            if not artifacts:
                uc_rows = cur.execute(
                    "SELECT output_artifacts_json FROM role_use_cases WHERE role_id = ? LIMIT 2;",
                    (nid,),
                ).fetchall()
                for ucr in uc_rows:
                    if ucr[0]:
                        artifacts.extend(json.loads(ucr[0]))
                artifacts = list(dict.fromkeys(artifacts))[:4]

            caps = json.loads(r_row[3]) if r_row[3] else []
            mmodels = json.loads(r_row[4]) if r_row[4] else []
            heur = json.loads(r_row[5]) if r_row[5] else []
            anti = json.loads(r_row[6]) if r_row[6] else []
            exemplar_org = r_row[7] or "World-Class Exemplar"
            industry = r_row[8] or "Enterprise"
            proto_cad = f"{proto} ({cad})".strip(" ()") if (proto or cad) else desc[:120]

            fused.append(
                AdjacentRoleFusion(
                    role_id=r_row[0],
                    slug=r_row[1],
                    title=r_row[2],
                    edge_type=etype,
                    direction=direc,
                    industry=industry,
                    exemplar_org=exemplar_org,
                    edge_description=desc,
                    edge_protocol=proto,
                    protocol_and_cadence=proto_cad,
                    absorbed_capabilities=caps[:4],
                    absorbed_mental_models=mmodels[:4],
                    absorbed_heuristics=heur[:4],
                    failure_gating_checks=(anti[:3] + heur[:2])[:4],
                    output_artifacts=artifacts,
                    blind_spot_eliminated=_blind_spot_rationale(etype, direc, r_row[2], industry),
                )
            )
        return fused


    def synthesize(
        self,
        problem: Optional[str] = None,
        role: Optional[str] = None,
        custom_role_spec: Optional[Union[Dict[str, Any], str, Path]] = None,
        custom_role: Optional[Union[Dict[str, Any], str, Path]] = None,
        company: Optional[str] = None,
        company_name: Optional[str] = None,
        developer_context: Optional[str] = None,
        context_file: Optional[Union[str, Path]] = None,
        adjacent_k: int = 4,
        persist: bool = False,
    ) -> SuperhumanRolePackage:
        """Synthesizes a complete SuperhumanRolePackage via any of the 3 input pathways."""
        clean_problem = (problem or "").strip()
        clean_role = (role or "").strip()
        eff_company = (company if company is not None else company_name)
        eff_company = eff_company.strip() if eff_company and eff_company.strip() else None

        raw_custom = custom_role_spec if custom_role_spec is not None else custom_role
        has_custom = False
        if isinstance(raw_custom, dict):
            has_custom = len(raw_custom) > 0
        elif isinstance(raw_custom, Path):
            has_custom = True
        elif isinstance(raw_custom, str):
            has_custom = bool(raw_custom.strip())

        if not clean_problem and not clean_role and not has_custom:
            raise ValueError(
                "Superhuman synthesis requires at least one of 'problem', 'role', or 'custom_role_spec'."
            )

        merged_dev_ctx = _merge_developer_context(developer_context, context_file)

        input_mode: INPUT_MODES
        primary_role: Dict[str, Any]
        mapped_anchor_id: Optional[str] = None
        use_cases: List[Dict[str, Any]] = []
        tools: List[Dict[str, Any]] = []
        swarm: List[Dict[str, Any]] = []
        genai_plan: Optional[Dict[str, Any]] = None
        enterprise_team: List[Dict[str, Any]] = []

        if has_custom and raw_custom is not None:
            # Pathway 3: Custom Agent Role + OKG Neighborhood Projection
            input_mode = "custom_agent_role"
            parsed_custom = _parse_custom_role_spec(raw_custom, problem_hint=clean_problem)
            custom_use_cases = parsed_custom.pop("_custom_use_cases", None)
            custom_tools = parsed_custom.pop("_custom_tools", None)
            custom_swarm = parsed_custom.pop("_custom_swarm", None)

            proj_query = (
                f"{parsed_custom['title']} {parsed_custom['mission']} "
                f"{clean_problem} {parsed_custom['system_prompt'][:400]}"
            ).strip()
            search_hits = self.search_engine.search(proj_query, top_k=10)
            if search_hits.results:
                mapped_anchor_id = search_hits.results[0].role_id
                anchor_pkg: RoleScaffoldingPackage = self.scaffolder.scaffold_role(
                    mapped_anchor_id, company_name=eff_company
                )
                ar = anchor_pkg.role
                # Borrow missing structured fields from closest OKG anchor while preserving custom identity!
                for k_borrow in ("capabilities", "mental_models", "heuristics", "vocabulary", "anti_patterns"):
                    if not parsed_custom.get(k_borrow):
                        parsed_custom[k_borrow] = list(ar.get(k_borrow) or [])
                if parsed_custom.get("industry_name") == "Cross-Domain Enterprise" and ar.get("industry_name"):
                    parsed_custom["industry_name"] = ar["industry_name"]
                use_cases = list(custom_use_cases) if custom_use_cases else anchor_pkg.use_cases
                tools = list(custom_tools) if custom_tools else anchor_pkg.tools
                swarm = list(custom_swarm) if custom_swarm else anchor_pkg.subagent_swarm
                genai_plan = anchor_pkg.genai_plan
                enterprise_team = self._assemble_enterprise_team(proj_query, exclude_role_id=mapped_anchor_id)
            else:
                use_cases = list(custom_use_cases or [])
                tools = list(custom_tools or [])
                swarm = list(custom_swarm or [])

            primary_role = parsed_custom
            if not clean_problem:
                clean_problem = (
                    f"Execute and stress-test {primary_role['title']} mission ({primary_role['mission']}) "
                    f"across novel out-of-distribution and adversarial boundary conditions."
                )

        elif clean_role:
            # Pathway 2: Canonical Role + Optional Problem / Company
            input_mode = "canonical_role"
            role_pkg = self.scaffolder.scaffold_role(clean_role, company_name=eff_company)
            primary_role = role_pkg.role
            mapped_anchor_id = primary_role["id"]
            use_cases = role_pkg.use_cases
            tools = role_pkg.tools
            swarm = role_pkg.subagent_swarm
            genai_plan = role_pkg.genai_plan
            if not clean_problem:
                clean_problem = (
                    f"Solve mission-critical and out-of-distribution enterprise challenges as "
                    f"{primary_role['title']}: {primary_role['mission']}"
                )
            enterprise_team = self._assemble_enterprise_team(
                f"{primary_role['title']} {clean_problem} {eff_company or ''}",
                exclude_role_id=mapped_anchor_id,
            )

        else:
            # Pathway 1: Problem Discovery via Hybrid Search (BM25 + Dense LSA + RRF)
            input_mode = "problem_discovery"
            discovery_query = f"{clean_problem} {eff_company or ''}".strip()
            search_hits = self.search_engine.search(discovery_query, top_k=12)
            if not search_hits.results:
                raise RuntimeError("HybridSearchEngine returned zero candidate roles from database.")
            mapped_anchor_id = search_hits.results[0].role_id
            role_pkg = self.scaffolder.scaffold_role(mapped_anchor_id, company_name=eff_company)
            primary_role = role_pkg.role
            use_cases = role_pkg.use_cases
            tools = role_pkg.tools
            swarm = role_pkg.subagent_swarm
            genai_plan = role_pkg.genai_plan
            enterprise_team = self._assemble_enterprise_team(discovery_query, exclude_role_id=mapped_anchor_id)

        adjacent_roles = self._traverse_adjacent_roles(mapped_anchor_id, adjacent_k=max(0, adjacent_k))

        academic = build_academic_foundation(
            primary_role=primary_role,
            problem_statement=clean_problem,
            adjacent_roles=adjacent_roles,
            company_context=eff_company,
            developer_context=merged_dev_ctx,
        )
        crucibles = build_on_the_job_crucibles(
            primary_role=primary_role,
            problem_statement=clean_problem,
            adjacent_roles=adjacent_roles,
            company_context=eff_company,
            developer_context=merged_dev_ctx,
        )
        characteristics = build_human_characteristics(
            primary_role=primary_role,
            problem_statement=clean_problem,
            adjacent_roles=adjacent_roles,
            company_context=eff_company,
            developer_context=merged_dev_ctx,
        )
        epistemology = build_unknown_problem_epistemology(
            primary_role=primary_role,
            problem_statement=clean_problem,
            adjacent_roles=adjacent_roles,
            company_context=eff_company,
            developer_context=merged_dev_ctx,
        )

        base_title = primary_role.get("title") or primary_role.get("name") or "Principal Specialist"
        superhuman_title = (
            base_title if base_title.lower().startswith("superhuman ") else f"Superhuman {base_title}"
        )
        if eff_company and eff_company.lower() not in superhuman_title.lower():
            superhuman_title = f"{superhuman_title} ({eff_company})"

        fingerprint = hashlib.sha256(
            f"{input_mode}|{primary_role.get('slug', '')}|{clean_problem}|{eff_company or ''}|{merged_dev_ctx[:256]}".encode(
                "utf-8"
            )
        ).hexdigest()[:8]
        base_slug = _slugify(primary_role.get("slug") or base_title, max_len=40)
        sh_slug = f"superhuman_{base_slug}_{fingerprint}"
        sh_id = f"sh_{base_slug}_{fingerprint}"
        now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        pkg = SuperhumanRolePackage(
            id=sh_id,
            slug=sh_slug,
            title=superhuman_title,
            input_mode=input_mode,
            problem_statement=clean_problem,
            company_context=eff_company,
            primary_role=primary_role,
            mapped_okg_anchor_role_id=mapped_anchor_id,
            enterprise_team_roles=enterprise_team,
            adjacent_roles=adjacent_roles,
            academic_foundation=academic,
            on_the_job_crucibles=crucibles,
            human_characteristics=characteristics,
            unknown_problem_epistemology=epistemology,
            use_cases=use_cases,
            tools=tools,
            subagent_swarm=swarm,
            genai_plan=genai_plan,
            developer_context=merged_dev_ctx,
            deep_superhuman_prompt="",
            created_at=now_iso,
        )
        pkg.deep_superhuman_prompt = compile_deep_superhuman_prompt(pkg)

        if persist:
            self._persist_package(pkg)

        return pkg

    def _persist_package(self, pkg: SuperhumanRolePackage) -> None:
        ensure_superhuman_schema(self.conn)
        adj_ids = [a.role_id for a in pkg.adjacent_roles]
        primary_id_val = pkg.mapped_okg_anchor_role_id or pkg.primary_role.get("id")
        self.conn.execute(
            """
            INSERT INTO superhuman_role_profiles (
                id, slug, title, problem_statement, primary_role_id,
                adjacent_role_ids_json, academic_foundation_json,
                on_the_job_crucibles_json, human_characteristics_json,
                unknown_problem_protocol_json, developer_context,
                deep_superhuman_prompt, package_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                slug = excluded.slug,
                title = excluded.title,
                problem_statement = excluded.problem_statement,
                primary_role_id = excluded.primary_role_id,
                adjacent_role_ids_json = excluded.adjacent_role_ids_json,
                academic_foundation_json = excluded.academic_foundation_json,
                on_the_job_crucibles_json = excluded.on_the_job_crucibles_json,
                human_characteristics_json = excluded.human_characteristics_json,
                unknown_problem_protocol_json = excluded.unknown_problem_protocol_json,
                developer_context = excluded.developer_context,
                deep_superhuman_prompt = excluded.deep_superhuman_prompt,
                package_json = excluded.package_json,
                created_at = excluded.created_at;
            """,
            (
                pkg.id,
                pkg.slug,
                pkg.title,
                pkg.problem_statement,
                primary_id_val,
                json.dumps(adj_ids),
                json.dumps(pkg.academic_foundation.to_dict()),
                json.dumps(pkg.on_the_job_crucibles.to_dict()),
                json.dumps(pkg.human_characteristics.to_dict()),
                json.dumps(pkg.unknown_problem_epistemology.to_dict()),
                pkg.developer_context,
                pkg.deep_superhuman_prompt,
                json.dumps(pkg.to_dict()),
                pkg.created_at,
            ),
        )
        self.conn.commit()

    def list_profiles(self) -> List[Dict[str, Any]]:
        """Lists all persisted Superhuman Role profiles in SQLite."""
        ensure_superhuman_schema(self.conn)
        rows = self.conn.execute(
            """
            SELECT
                id, slug, title, problem_statement, primary_role_id,
                adjacent_role_ids_json, LENGTH(deep_superhuman_prompt), created_at
            FROM superhuman_role_profiles
            ORDER BY created_at DESC, id ASC;
            """
        ).fetchall()
        out: List[Dict[str, Any]] = []
        for r in rows:
            adj_list = json.loads(r[5]) if r[5] else []
            out.append({
                "id": r[0],
                "slug": r[1],
                "title": r[2],
                "problem_statement": r[3],
                "primary_role_id": r[4],
                "adjacent_roles_count": len(adj_list),
                "prompt_character_count": r[6] or 0,
                "created_at": r[7],
            })
        return out

    def get_profile(self, id_or_slug: str) -> SuperhumanRolePackage:
        """Loads a persisted SuperhumanRolePackage by ID or slug."""
        if not id_or_slug or not id_or_slug.strip():
            raise KeyError("Empty superhuman profile identifier provided.")
        ensure_superhuman_schema(self.conn)
        key = id_or_slug.strip()
        row = self.conn.execute(
            """
            SELECT package_json
            FROM superhuman_role_profiles
            WHERE id = ? OR slug = ?
            LIMIT 1;
            """,
            (key, key),
        ).fetchone()
        if not row:
            row = self.conn.execute(
                """
                SELECT package_json
                FROM superhuman_role_profiles
                WHERE slug LIKE ? OR id LIKE ? OR LOWER(title) = LOWER(?)
                LIMIT 1;
                """,
                (f"%{key}%", f"%{key}%", key),
            ).fetchone()
        if not row or not row[0]:
            raise KeyError(f"Superhuman role profile '{id_or_slug}' not found.")
        payload = json.loads(row[0])
        payload.pop("prompt_character_count", None)
        if isinstance(payload.get("unknown_problem_epistemology"), dict):
            payload["unknown_problem_epistemology"].pop("stages", None)
        return SuperhumanRolePackage.model_validate(payload)


__all__ = ["SuperhumanRoleSynthesizer"]
