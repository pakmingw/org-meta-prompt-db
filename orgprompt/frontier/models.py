"""Pydantic data models for the Nov 2026 Frontier AI Lab & Real-World Join Layer (`orgprompt.frontier`)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class _FrontierDictMixin:
    """Ergonomic dict-like subscripting and `.get()` access for SDK & test compatibility."""

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            return getattr(self, item)
        raise KeyError(f"{self.__class__.__name__} has no attribute '{item}'")

    def get(self, item: str, default: Any = None) -> Any:
        if hasattr(self, item):
            val = getattr(self, item)
            return val if val is not None else default
        return default

    def _save_helper(self, path: Union[str, Path], format: str = "markdown") -> Path:
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fmt = format.lower().strip()
        if fmt == "json" or (fmt not in ("markdown", "md") and out_path.suffix.lower() == ".json"):
            out_path.write_text(self.to_json(), encoding="utf-8")  # type: ignore[attr-defined]
        else:
            out_path.write_text(self.to_markdown(), encoding="utf-8")  # type: ignore[attr-defined]
        return out_path


FrontierJoinMechanism = Literal[
    "FDE_WORKFLOW_EMBEDDING",
    "RL_VERIFIER_AND_EVAL_HARNESS",
    "MCP_CONTEXT_AND_TOOL_RUNTIME",
    "DOMAIN_DISTILLATION_AND_POST_TRAINING",
    "SAFETY_CONTROL_AND_RED_TEAM_GATE",
    "WORLD_MODEL_AND_SCIENTIFIC_SIM",
]

FrontierPodCategory = Literal[
    "PRETRAINING_AND_ARCHITECTURE",
    "REASONING_AND_AGENTIC_POST_TRAINING",
    "ALIGNMENT_CONTROL_AND_EVALS",
    "GIGAWATT_INFRA_AND_INFERENCE",
    "APPLIED_PRODUCT_AND_ORCHESTRATION",
    "FDE_ENTERPRISE_AND_SCIENCE",
]


class FrontierLabPod(BaseModel, _FrontierDictMixin):
    """Internal operating pod inside a Nov 2026 Frontier AI Lab."""

    id: str
    lab_id: str
    slug: str
    name: str
    pod_category: FrontierPodCategory
    mandate: str
    canonical_role_slugs: List[str] = Field(default_factory=list)
    signature_artifacts: List[str] = Field(default_factory=list)
    operating_cadence: str

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class FrontierAILab(BaseModel, _FrontierDictMixin):
    """Comprehensive Nov 2026 Frontier AI Lab organizational record."""

    id: str
    slug: str
    name: str
    company_id: Optional[str] = None
    headquarters: str
    corporate_governance_structure: str
    leadership: List[str] = Field(default_factory=list)
    research_to_product_loop: str
    flagship_models: List[str] = Field(default_factory=list)
    safety_control_framework: str
    enterprise_gtm_fde_motion: str
    compute_and_infra_strategy: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    pods: List[FrontierLabPod] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["pods"] = [p.to_dict() for p in self.pods]
        return data

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        from orgprompt.frontier.formatter import format_lab_markdown
        return format_lab_markdown(self)

    def save(self, path: Union[str, Path], format: str = "markdown") -> Path:
        return self._save_helper(path, format=format)


class RealWorldToFrontierBridge(BaseModel, _FrontierDictMixin):
    """Cross-industry or horizontal blueprint joining real-world goals to Frontier Lab pods & recipes."""

    id: str
    slug: str
    industry_id: str
    domain_name: str
    real_world_goal: str
    real_world_role_slugs: List[str] = Field(default_factory=list)
    real_world_bottlenecks: List[str] = Field(default_factory=list)
    why_naive_llm_wrappers_fail: str
    lead_frontier_labs: List[str] = Field(default_factory=list)
    frontier_pod_ids: List[str] = Field(default_factory=list)
    frontier_role_slugs: List[str] = Field(default_factory=list)
    frontier_technical_recipe: str
    joint_enterprise_lab_pod_topology: str

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class RoleFrontierJoinEdge(BaseModel, _FrontierDictMixin):
    """Single relational join edge linking a canonical role to a Frontier AI Lab counterpart role."""

    id: str
    source_enterprise_role_id: str
    source_enterprise_role_slug: str
    source_enterprise_role_title: str
    target_frontier_role_id: str
    target_frontier_role_slug: str
    target_frontier_role_title: str
    join_mechanism: FrontierJoinMechanism
    enterprise_pain_point: str
    frontier_lab_capability: str
    joint_artifact: str
    recommended_labs: List[str] = Field(default_factory=list)
    priority_rank: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class RoleFrontierJoinResult(BaseModel, _FrontierDictMixin):
    """Complete Frontier Lab bridge blueprint for a single enterprise/creator canonical role."""

    query: str
    role_id: str
    role_slug: str
    role_title: str
    industry_id: str = ""
    industry_name: str = ""
    role_mission: str = ""
    company_name: Optional[str] = None
    company_slug: Optional[str] = None
    personal_subagents: List[str] = Field(default_factory=list)
    frontier_joins: List[RoleFrontierJoinEdge] = Field(default_factory=list)
    matching_bridges: List[RealWorldToFrontierBridge] = Field(default_factory=list)
    recommended_labs: List[FrontierAILab] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "role_id": self.role_id,
            "role_slug": self.role_slug,
            "role_title": self.role_title,
            "industry_id": self.industry_id,
            "industry_name": self.industry_name,
            "role_mission": self.role_mission,
            "company_name": self.company_name,
            "company_slug": self.company_slug,
            "personal_subagents": self.personal_subagents,
            "frontier_joins": [j.to_dict() for j in self.frontier_joins],
            "matching_bridges": [b.to_dict() for b in self.matching_bridges],
            "recommended_labs": [l.to_dict() for l in self.recommended_labs],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        from orgprompt.frontier.formatter import format_role_join_markdown
        return format_role_join_markdown(self)

    def save(self, path: Union[str, Path], format: str = "markdown") -> Path:
        return self._save_helper(path, format=format)


class CompanyFrontierJoinResult(BaseModel, _FrontierDictMixin):
    """Enterprise-wide Frontier AI Lab co-design & deployment join blueprint for an organization."""

    query: str
    company_id: str
    company_slug: str
    company_name: str
    rank: int
    industry_id: str
    industry_name: str
    focus: Optional[str] = None
    employed_roles_count: int = 0
    total_frontier_join_edges: int = 0
    top_frontier_counterparts: List[Dict[str, Any]] = Field(default_factory=list)
    mechanism_distribution: Dict[str, int] = Field(default_factory=dict)
    lead_frontier_labs: List[FrontierAILab] = Field(default_factory=list)
    industry_bridges: List[RealWorldToFrontierBridge] = Field(default_factory=list)
    sample_role_joins: List[RoleFrontierJoinEdge] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "company_id": self.company_id,
            "company_slug": self.company_slug,
            "company_name": self.company_name,
            "rank": self.rank,
            "industry_id": self.industry_id,
            "industry_name": self.industry_name,
            "focus": self.focus,
            "employed_roles_count": self.employed_roles_count,
            "total_frontier_join_edges": self.total_frontier_join_edges,
            "top_frontier_counterparts": self.top_frontier_counterparts,
            "mechanism_distribution": self.mechanism_distribution,
            "lead_frontier_labs": [l.to_dict() for l in self.lead_frontier_labs],
            "industry_bridges": [b.to_dict() for b in self.industry_bridges],
            "sample_role_joins": [j.to_dict() for j in self.sample_role_joins],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        from orgprompt.frontier.formatter import format_company_join_markdown
        return format_company_join_markdown(self)

    def save(self, path: Union[str, Path], format: str = "markdown") -> Path:
        return self._save_helper(path, format=format)


class ProblemFrontierBridgeResult(BaseModel, _FrontierDictMixin):
    """Problem-to-Frontier-Lab synthesis joining HybridSearch real-world roles to Frontier Lab pods."""

    problem_statement: str
    company_name: Optional[str] = None
    company_slug: Optional[str] = None
    retrieved_enterprise_roles: List[Dict[str, Any]] = Field(default_factory=list)
    frontier_joins: List[RoleFrontierJoinEdge] = Field(default_factory=list)
    activated_frontier_pods: List[FrontierLabPod] = Field(default_factory=list)
    matching_bridges: List[RealWorldToFrontierBridge] = Field(default_factory=list)
    recommended_labs: List[FrontierAILab] = Field(default_factory=list)
    co_design_execution_plan: List[str] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "problem_statement": self.problem_statement,
            "company_name": self.company_name,
            "company_slug": self.company_slug,
            "retrieved_enterprise_roles": self.retrieved_enterprise_roles,
            "frontier_joins": [j.to_dict() for j in self.frontier_joins],
            "activated_frontier_pods": [p.to_dict() for p in self.activated_frontier_pods],
            "matching_bridges": [b.to_dict() for b in self.matching_bridges],
            "recommended_labs": [l.to_dict() for l in self.recommended_labs],
            "co_design_execution_plan": self.co_design_execution_plan,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        from orgprompt.frontier.formatter import format_problem_bridge_markdown
        return format_problem_bridge_markdown(self)

    def save(self, path: Union[str, Path], format: str = "markdown") -> Path:
        return self._save_helper(path, format=format)
