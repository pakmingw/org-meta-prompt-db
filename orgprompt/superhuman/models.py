"""Pydantic data models for Phase 12 Superhuman Role Synthesis (`orgprompt.superhuman`)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class _DictAccessMixin:
    """Provides dict-like subscripting and `.get()` access for ergonomic SDK & test usage."""

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            return getattr(self, item)
        raise KeyError(f"{self.__class__.__name__} has no attribute '{item}'")

    def get(self, item: str, default: Any = None) -> Any:
        if hasattr(self, item):
            val = getattr(self, item)
            return val if val is not None else default
        return default


class AcademicFoundation(BaseModel, _DictAccessMixin):
    """University, graduate, and doctoral rigor underlying a Perfect Human practitioner."""

    degrees: List[str] = Field(
        default_factory=list,
        description="Specific B.S./M.S./Ph.D./M.D./J.D./MBA degree pathways tailored to domain & problem",
    )
    foundational_coursework_and_axioms: List[str] = Field(
        default_factory=list,
        description="Foundational mathematical, physical, computational, economic, or clinical coursework & axioms",
    )
    seminal_literature_and_standards: List[str] = Field(
        default_factory=list,
        description="Seminal textbooks, international standards, and foundational papers mastered",
    )
    doctoral_thesis_and_lab_methodology: str = Field(
        default="",
        description="Doctoral lab / research thesis training methodology (experiment design & theorem proving)",
    )
    cross_disciplinary_minors: List[str] = Field(
        default_factory=list,
        description="Cross-disciplinary secondary training bridging the primary role with adjacent graph roles",
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class CrucibleEpisode(BaseModel, _DictAccessMixin):
    """A high-stakes failure, incident, or adversarial audit survived on the job ('scar tissue')."""

    title: str = Field(..., description="Short title of the crucible incident or failure episode")
    organization_and_era: str = Field(
        default="", description="Exemplar environment / career stage where the incident occurred"
    )
    failure_mode_and_broken_assumption: str = Field(
        ..., description="What broke in production, why textbook priors failed, and what was at stake"
    )
    recovery_and_forensic_action: str = Field(
        ..., description="How the practitioner diagnosed root cause under pressure and stabilized the system"
    )
    tacit_scar_tissue_lesson: str = Field(
        ..., description="Non-obvious tacit intuition permanently forged by surviving this episode"
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class OnTheJobCrucibles(BaseModel, _DictAccessMixin):
    """Progressive 12–20 year apprenticeship, cross-functional rotations, and crucible scar tissue."""

    career_trajectory: List[str] = Field(
        default_factory=list,
        description="Progressive 12–20 year career trajectory across world-class exemplar organizations",
    )
    cross_functional_tours_of_duty: List[str] = Field(
        default_factory=list,
        description="Rotations across operations/SRE, risk/audit, commercial/field, and core architecture",
    )
    crucible_episodes: List[CrucibleEpisode] = Field(
        default_factory=list,
        description=">= 4 concrete failure & recovery episodes ('scar tissue') forging tacit intuition",
    )
    mentorship_and_review_rituals: List[str] = Field(
        default_factory=list,
        description="Mentorship lineage & operational review habits (Skunk Works, 6-pagers, Andon cord, etc.)",
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


# Singular alias for spec compatibility
OnTheJobCrucible = OnTheJobCrucibles


class HumanCharacteristics(BaseModel, _DictAccessMixin):
    """Cognitive, epistemic, and psychological traits of the Perfect Human specialist."""

    cognitive_architecture: List[str] = Field(
        default_factory=list,
        description="Multi-scale systems modeling, Fermi estimation, and working-memory decomposition habits",
    )
    epistemic_calibration: str = Field(
        default="",
        description="Calibrated epistemic humility vs. decisive high-conviction action under incomplete data",
    )
    bias_and_mediocrity_resistances: List[str] = Field(
        default_factory=list,
        description="Explicit resistance to authority bias, sunk-cost fallacy, and cargo-cult pattern matching",
    )
    aesthetic_and_ownership_traits: List[str] = Field(
        default_factory=list,
        description="Aesthetic taste for parsimony/simplicity, extreme ownership, and pre-mortem instinct",
    )
    socio_technical_temperament: str = Field(
        default="",
        description="High-stress composure and socio-technical diplomacy across organizational silos",
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class AdjacentRoleFusion(BaseModel, _DictAccessMixin):
    """Polymathic boundary capability absorbed from an adjacent role in the Organizational Knowledge Graph."""

    role_id: str = Field(..., description="Canonical role ID in the OKG")
    slug: str = Field(..., description="Canonical role slug")
    title: str = Field(..., description="Canonical role display title")
    edge_type: str = Field(
        ...,
        description="Graph relationship: COLLABORATES_WITH, HANDS_OFF_TO, REVIEWS_AND_GATES, CHALLENGES_OR_AUDITS, REPORTS_TO",
    )
    direction: str = Field(
        default="OUTGOING", description="Edge traversal direction relative to anchor role"
    )
    industry: str = Field(default="Enterprise", description="Macro industry of adjacent role")
    exemplar_org: str = Field(default="World-Class Exemplar", description="Exemplar org of adjacent role")
    edge_description: str = Field(default="", description="Authentic workflow edge description from role_edges")
    edge_protocol: str = Field(default="", description="Authentic interface/handoff protocol from role_edges")
    protocol_and_cadence: str = Field(
        default="", description="Original graph interaction protocol and cadence"
    )
    absorbed_capabilities: List[str] = Field(
        default_factory=list, description="Core capabilities internalized into the Superhuman Role"
    )
    absorbed_mental_models: List[str] = Field(
        default_factory=list, description="Mental models absorbed from this neighbor"
    )
    absorbed_heuristics: List[str] = Field(
        default_factory=list, description="Decision heuristics absorbed from this neighbor"
    )
    failure_gating_checks: List[str] = Field(
        default_factory=list, description="Verification gates and anti-pattern checks internalized"
    )
    output_artifacts: List[str] = Field(
        default_factory=list, description="Key deliverable artifacts understood across this boundary"
    )
    blind_spot_eliminated: str = Field(
        ...,
        description="Why absorbing this adjacent role's perspective eliminates organizational blind spots",
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class EpistemicStage(BaseModel, _DictAccessMixin):
    """Single executable stage in the 5-Stage Unknown-to-AI (Out-of-Distribution) Epistemic Protocol."""

    stage_number: int = Field(..., description="Stage index 1..5")
    name: str = Field(..., description="Stage name")
    objective: str = Field(..., description="Core meta-cognitive objective when facing an unknown regime")
    triggers_or_axioms: List[str] = Field(
        default_factory=list,
        description="Explicit triggers, conservation laws, structural mappings, or red-team probes",
    )
    concrete_actions: List[str] = Field(
        default_factory=list,
        description="Step-by-step actions executed by the agent during this stage",
    )
    verification_gate: str = Field(
        ..., description="Exit criterion required before advancing to the next epistemic stage"
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


class UnknownProblemEpistemology(BaseModel, _DictAccessMixin):
    """5-Stage meta-cognitive reasoning protocol for problems unknown to the AI model (OOD regimes)."""

    ood_detection_and_pattern_veto: EpistemicStage = Field(
        ..., description="Stage 1: OOD & Distribution-Shift Detector (Pattern-Match Veto)"
    )
    first_principles_invariants: EpistemicStage = Field(
        ..., description="Stage 2: First-Principles Conservation Laws & Invariant Anchoring"
    )
    cross_adjacent_isomorphism: EpistemicStage = Field(
        ..., description="Stage 3: Cross-Adjacent Structural Isomorphism across OKG exemplars"
    )
    abductive_hypotheses_and_micro_experiments: EpistemicStage = Field(
        ..., description="Stage 4: Abductive Hypothesis Tree & Minimum-Regret Micro-Experiments"
    )
    internalized_adversarial_red_team_gate: EpistemicStage = Field(
        ..., description="Stage 5: Internalized Adversarial Challenger & Red-Team Gate"
    )

    @property
    def stages(self) -> List[EpistemicStage]:
        """Ordered list of all 5 out-of-distribution epistemic stages."""
        return [
            self.ood_detection_and_pattern_veto,
            self.first_principles_invariants,
            self.cross_adjacent_isomorphism,
            self.abductive_hypotheses_and_micro_experiments,
            self.internalized_adversarial_red_team_gate,
        ]

    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["stages"] = [s.to_dict() for s in self.stages]
        return data


INPUT_MODES = Literal["problem_discovery", "canonical_role", "custom_agent_role"]


class SuperhumanRolePackage(BaseModel, _DictAccessMixin):
    """Complete exportable Superhuman Role Definition, Pedigree, OOD Protocol, and Deep Meta-Prompt."""

    id: str = Field(..., description="Unique superhuman role profile ID")
    slug: str = Field(..., description="URL-friendly unique slug")
    title: str = Field(..., description="Superhuman polymathic role title")
    input_mode: INPUT_MODES = Field(..., description="Pathway used to synthesize this package")
    problem_statement: str = Field(..., description="Target enterprise or frontier problem statement")
    company_context: Optional[str] = Field(default=None, description="Optional enterprise/company context")
    primary_role: Dict[str, Any] = Field(
        default_factory=dict,
        description="Anchor canonical role or normalized external agent-provided role definition",
    )
    mapped_okg_anchor_role_id: Optional[str] = Field(
        default=None,
        description="Closest canonical role ID in the OKG (identical to primary_role.id or mapped for custom roles)",
    )
    enterprise_team_roles: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Supporting enterprise roles across strategy, execution, operations, and audit",
    )
    adjacent_roles: List[AdjacentRoleFusion] = Field(
        default_factory=list,
        description="Adjacent OKG roles fused into the Superhuman Role to eliminate blind spots",
    )
    academic_foundation: AcademicFoundation = Field(
        ..., description="University, graduate, and doctoral rigor"
    )
    on_the_job_crucibles: OnTheJobCrucibles = Field(
        ..., description="12-20 year career trajectory and >= 4 crucible scar-tissue episodes"
    )
    human_characteristics: HumanCharacteristics = Field(
        ..., description="Cognitive, epistemic, and psychological traits"
    )
    unknown_problem_epistemology: UnknownProblemEpistemology = Field(
        ..., description="5-stage reasoning protocol for unknown / out-of-distribution problems"
    )
    use_cases: List[Dict[str, Any]] = Field(
        default_factory=list, description="Day-to-day & frontier operational use cases"
    )
    tools: List[Dict[str, Any]] = Field(
        default_factory=list, description="Horizontal productivity & vertical domain tools"
    )
    subagent_swarm: List[Dict[str, Any]] = Field(
        default_factory=list, description="6-agent Personal Subagent Swarm ('Role-in-a-Box')"
    )
    genai_plan: Optional[Dict[str, Any]] = Field(
        default=None, description="Engineering blueprint for RAG, MCP bindings, and HITL gates"
    )
    developer_context: str = Field(
        default="", description="Developer-complemented background, proprietary constraints & domain notes"
    )
    deep_superhuman_prompt: str = Field(
        default="", description="Compiled 8-section Deep Superhuman Meta-Prompt (>= 6,000 characters)"
    )
    created_at: str = Field(default="", description="ISO-8601 UTC creation timestamp")

    @property
    def prompt_character_count(self) -> int:
        return len(self.deep_superhuman_prompt)

    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["unknown_problem_epistemology"] = self.unknown_problem_epistemology.to_dict()
        data["prompt_character_count"] = len(self.deep_superhuman_prompt)
        return data

    def to_json(self, indent: int = 2) -> str:
        from orgprompt.superhuman.formatter import format_superhuman_json
        return format_superhuman_json(self, indent=indent)

    def to_markdown(self) -> str:
        from orgprompt.superhuman.formatter import format_superhuman_markdown
        return format_superhuman_markdown(self)

    def save(self, path: Union[str, Path], format: str = "markdown") -> Path:
        out_path = Path(path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fmt = format.lower().strip()
        if fmt == "json" or (fmt not in ("markdown", "md") and out_path.suffix.lower() == ".json"):
            out_path.write_text(self.to_json(), encoding="utf-8")
        else:
            out_path.write_text(self.to_markdown(), encoding="utf-8")
        return out_path
