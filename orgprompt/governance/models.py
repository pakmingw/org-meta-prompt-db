"""Pydantic data models for the Fiduciary Oversight & Independent Audit Tier (`orgprompt.governance`)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class _GovDictMixin:
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


GovernanceCategory = Literal["BOARD_DIRECTOR", "INDEPENDENT_AUDITOR"]
CompanyStage = Literal["PUBLIC_ENTERPRISE", "VENTURE_OR_BOUTIQUE"]
GovernanceEdgeType = Literal[
    "OVERSEES_AND_ADVISES",
    "CHALLENGES_CAPITAL_ALLOCATION",
    "ATTESTS_FINANCIAL_CONTROLS",
    "AUDITS_STRATEGIC_AND_AI_PERFORMANCE",
    "GATES_COMPENSATION_AND_SUCCESSION",
]


class GovernanceRole(BaseModel, _GovDictMixin):
    """A first-class Board of Directors Member or Independent Auditor role outside management."""

    id: str
    slug: str
    title: str
    governance_category: GovernanceCategory
    committee_type: str
    selected_industries: List[str] = Field(default_factory=list)
    typical_human_background: str
    fiduciary_mandate: str
    quarterly_review_cadence: List[str] = Field(default_factory=list)
    kpi_value_tree: Dict[str, Any] = Field(default_factory=dict)
    red_flag_triggers: List[str] = Field(default_factory=list)
    oversight_targets: List[str] = Field(default_factory=list)
    system_prompt: str
    character_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["character_count"] = len(self.system_prompt)
        return data

    def to_markdown(self) -> str:
        from orgprompt.governance.formatter import format_governance_role_markdown
        return format_governance_role_markdown(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)


class GovernanceOversightEdge(BaseModel, _GovDictMixin):
    """Typed fiduciary oversight or independent audit edge targeting an operating management role."""

    id: str
    governance_role_id: str
    governance_role_slug: str = ""
    target_management_role_slug: str
    edge_type: GovernanceEdgeType
    review_artifact: str
    protocol: str

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class IndustryBoardComposition(BaseModel, _GovDictMixin):
    """Industry- and stage-specific Board of Directors and External Audit panel template."""

    id: str
    industry_slug: str
    industry_name: str
    company_stage: CompanyStage
    board_size: int
    seat_role_slugs: List[str] = Field(default_factory=list)
    external_auditor_slugs: List[str] = Field(default_factory=list)
    charter_summary: str
    quarterly_agenda: List[str] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class BoardSlateRecommendation(BaseModel, _GovDictMixin):
    """Resolved Board of Directors & Independent Audit Slate for a specific company or industry."""

    query: str
    company_name: Optional[str] = None
    company_slug: Optional[str] = None
    industry_slug: str
    industry_name: str
    company_stage: CompanyStage
    board_size: int
    charter_summary: str
    quarterly_agenda: List[str] = Field(default_factory=list)
    board_directors: List[GovernanceRole] = Field(default_factory=list)
    external_auditors: List[GovernanceRole] = Field(default_factory=list)
    oversight_edges: List[GovernanceOversightEdge] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "company_name": self.company_name,
            "company_slug": self.company_slug,
            "industry_slug": self.industry_slug,
            "industry_name": self.industry_name,
            "company_stage": self.company_stage,
            "board_size": self.board_size,
            "charter_summary": self.charter_summary,
            "quarterly_agenda": self.quarterly_agenda,
            "board_directors": [r.to_dict() for r in self.board_directors],
            "external_auditors": [r.to_dict() for r in self.external_auditors],
            "oversight_edges": [e.to_dict() for e in self.oversight_edges],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)

    def to_markdown(self) -> str:
        from orgprompt.governance.formatter import format_board_slate_markdown
        return format_board_slate_markdown(self)

    def save(self, path: Union[str, Path], format: str = "markdown") -> Path:
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fmt = format.lower().strip()
        if fmt == "json" or (fmt not in ("markdown", "md") and out_path.suffix.lower() == ".json"):
            out_path.write_text(self.to_json(), encoding="utf-8")
        else:
            out_path.write_text(self.to_markdown(), encoding="utf-8")
        return out_path


class AcademicCredentialFoundation(BaseModel, _GovDictMixin):
    """Doctoral, CPA/CFA/J.D./M.D. credentials & capital-allocation/accounting axioms."""

    degrees_and_certifications: List[str] = Field(default_factory=list)
    capital_and_accounting_axioms: List[str] = Field(default_factory=list)
    statutory_and_governance_standards: List[str] = Field(default_factory=list)
    seminal_treatises: List[str] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class BoardroomCrucibleEpisode(BaseModel, _GovDictMixin):
    """A high-stakes multi-cycle boardroom, fraud-detection, or turnaround scar-tissue episode."""

    title: str
    cycle_and_context: str
    management_spin_or_hidden_trap: str
    forensic_board_intervention: str
    permanent_fiduciary_scar_tissue: str

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class BoardroomAndAuditCrucibles(BaseModel, _GovDictMixin):
    """20–30 year multi-cycle boardroom, audit, and capital-allocation track record."""

    career_and_board_tenure: List[str] = Field(default_factory=list)
    committee_leadership_rotations: List[str] = Field(default_factory=list)
    crucible_episodes: List[BoardroomCrucibleEpisode] = Field(default_factory=list)
    executive_session_rituals: List[str] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class FiduciaryTemperament(BaseModel, _GovDictMixin):
    """Psychological independence and Socratic boardroom interrogation calibration."""

    boardroom_independence_posture: str
    socratic_interrogation_style: List[str] = Field(default_factory=list)
    cognitive_and_conformity_immunities: List[str] = Field(default_factory=list)
    truth_over_harmony_calibration: str

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class CommitteeAndSeamFusion(BaseModel, _GovDictMixin):
    """Fused perspective from an adjacent Board Committee, Auditor, or Management Counterparty."""

    slug: str
    title: str
    fusion_source_type: Literal["COMMITTEE_OR_AUDITOR", "MANAGEMENT_COUNTERPARTY"]
    edge_or_committee_role: str
    absorbed_audit_lenses: List[str] = Field(default_factory=list)
    blind_spot_eliminated: str

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class GovernanceEpistemicStage(BaseModel, _GovDictMixin):
    """Single executable stage in the 5-Stage Unknown-Risk & Management-Spin Falsification Protocol."""

    stage_number: int
    name: str
    objective: str
    conservation_laws_or_triggers: List[str] = Field(default_factory=list)
    forensic_actions: List[str] = Field(default_factory=list)
    fiduciary_gate: str

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class UnknownRiskEpistemology(BaseModel, _GovDictMixin):
    """5-Stage Unknown-Risk & Management-Spin Falsification Protocol for Superhuman Governance."""

    stage_1_management_narrative_pattern_veto: GovernanceEpistemicStage
    stage_2_cash_flow_and_unit_economics_conservation: GovernanceEpistemicStage
    stage_3_cross_industry_peer_and_sotp_benchmarking: GovernanceEpistemicStage
    stage_4_management_stress_test_and_forensic_probes: GovernanceEpistemicStage
    stage_5_constructive_board_directive_and_ai_value_resolution: GovernanceEpistemicStage

    @property
    def stages(self) -> List[GovernanceEpistemicStage]:
        return [
            self.stage_1_management_narrative_pattern_veto,
            self.stage_2_cash_flow_and_unit_economics_conservation,
            self.stage_3_cross_industry_peer_and_sotp_benchmarking,
            self.stage_4_management_stress_test_and_forensic_probes,
            self.stage_5_constructive_board_directive_and_ai_value_resolution,
        ]

    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["stages"] = [s.to_dict() for s in self.stages]
        return data


class SuperhumanGovernancePackage(BaseModel, _GovDictMixin):
    """Exportable Superhuman Board Director or Superhuman Independent Auditor Blueprint."""

    id: str
    slug: str
    title: str
    base_governance_role: GovernanceRole
    target_problem_or_company: str
    company_context: Optional[str] = None
    fused_committee_slugs: List[str] = Field(default_factory=list)
    committee_and_seam_fusions: List[CommitteeAndSeamFusion] = Field(default_factory=list)
    academic_and_credential_foundation: AcademicCredentialFoundation
    boardroom_and_audit_crucibles: BoardroomAndAuditCrucibles
    fiduciary_temperament: FiduciaryTemperament
    unknown_risk_epistemology: UnknownRiskEpistemology
    oversight_edges: List[GovernanceOversightEdge] = Field(default_factory=list)
    developer_context: str = ""
    deep_superhuman_governance_prompt: str = ""
    created_at: str = ""

    @property
    def prompt_character_count(self) -> int:
        return len(self.deep_superhuman_governance_prompt)

    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["unknown_risk_epistemology"] = self.unknown_risk_epistemology.to_dict()
        data["prompt_character_count"] = len(self.deep_superhuman_governance_prompt)
        return data

    def to_json(self, indent: int = 2) -> str:
        from orgprompt.governance.formatter import format_superhuman_governance_json
        return format_superhuman_governance_json(self, indent=indent)

    def to_markdown(self) -> str:
        from orgprompt.governance.formatter import format_superhuman_governance_markdown
        return format_superhuman_governance_markdown(self)

    def save(self, path: Union[str, Path], format: str = "markdown") -> Path:
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fmt = format.lower().strip()
        if fmt == "json" or (fmt not in ("markdown", "md") and out_path.suffix.lower() == ".json"):
            out_path.write_text(self.to_json(), encoding="utf-8")
        else:
            out_path.write_text(self.to_markdown(), encoding="utf-8")
        return out_path


__all__ = [
    "GovernanceCategory",
    "CompanyStage",
    "GovernanceEdgeType",
    "GovernanceRole",
    "GovernanceOversightEdge",
    "IndustryBoardComposition",
    "BoardSlateRecommendation",
    "AcademicCredentialFoundation",
    "BoardroomCrucibleEpisode",
    "BoardroomAndAuditCrucibles",
    "FiduciaryTemperament",
    "CommitteeAndSeamFusion",
    "GovernanceEpistemicStage",
    "UnknownRiskEpistemology",
    "SuperhumanGovernancePackage",
]
