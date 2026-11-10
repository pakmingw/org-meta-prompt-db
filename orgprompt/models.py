"""Core Pydantic data schemas for the Organizational Knowledge Graph."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, model_validator


class Industry(BaseModel):
    """Macro socioeconomic industry sector."""

    id: str = Field(..., description="Unique ID, e.g. 'ind_telecommunications'")
    slug: str = Field(default="", description="URL-friendly slug, e.g. 'telecommunications'")
    name: str = Field(..., description="Industry display name")
    description: str = Field(..., description="Substantive industry description")
    category: str = Field(default="Infrastructure & Engineering", description="Macro category")
    exemplar_org_ids: List[str] = Field(default_factory=list, description="IDs of exemplar organizations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")

    @model_validator(mode="before")
    @classmethod
    def populate_slug(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("slug") and data.get("id"):
                data["slug"] = data["id"].replace("ind_", "")
        return data


class ExemplarOrg(BaseModel):
    """World-class exemplar organization."""

    id: str = Field(..., description="Unique ID, e.g. 'org_bell_labs'")
    industry_id: str = Field(..., description="Parent industry ID, e.g. 'ind_telecommunications'")
    slug: str = Field(default="", description="Unique slug, e.g. 'bell_labs'")
    name: str = Field(..., description="Organization display name")
    lineage: str = Field(default="", description="Founding lineage and historical ethos")
    description: str = Field(default="", description="Detailed organizational profile")
    signature_mechanisms_summary: str = Field(
        default="", description="Summary of key signature operating mechanisms"
    )
    operating_mechanisms: List[str] = Field(
        default_factory=list, description="List of operating mechanism names or IDs"
    )
    operating_unit_ids: List[str] = Field(
        default_factory=list, description="IDs of functional operating units"
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")

    @model_validator(mode="before")
    @classmethod
    def populate_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("slug") and data.get("id"):
                data["slug"] = data["id"].replace("org_", "")
            if not data.get("signature_mechanisms_summary") and data.get("operating_mechanisms"):
                data["signature_mechanisms_summary"] = "; ".join(data["operating_mechanisms"])
            if not data.get("description") and data.get("lineage"):
                data["description"] = data["lineage"]
        return data


class OrgUnit(BaseModel):
    """Functional operating unit within an exemplar organization."""

    id: str = Field(..., description="Unique ID, e.g. 'unit_bell_labs_physical_research'")
    org_id: str = Field(..., description="Parent exemplar organization ID, e.g. 'org_bell_labs'")
    slug: str = Field(default="", description="Unique slug")
    name: str = Field(..., description="Unit display name")
    division: str = Field(default="Engineering", description="Division grouping")
    department: str = Field(default="Core Systems", description="Department grouping")
    unit_type: str = Field(
        default="ENGINEERING",
        description="One of: 'R_AND_D', 'ENGINEERING', 'OPERATIONS', 'GOVERNANCE', 'PRODUCT', 'COMMERCIAL'",
    )
    description: str = Field(default="", description="Unit description")
    value_creation_loop: Any = Field(
        default_factory=dict, description="4-stage value creation loop (dict or formatted str)"
    )
    signature_mechanism: str = Field(default="", description="Primary signature operating mechanism")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")

    @property
    def exemplar_org_id(self) -> str:
        return self.org_id

    @model_validator(mode="before")
    @classmethod
    def populate_org_id(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("org_id") and data.get("exemplar_org_id"):
                data["org_id"] = data["exemplar_org_id"]
            if not data.get("slug") and data.get("id"):
                data["slug"] = data["id"].replace("unit_", "")
        return data


class CanonicalRole(BaseModel):
    """Deeply specified professional canonical role."""

    id: str = Field(..., description="Unique ID, e.g. 'role_telecom_chief_network_architect'")
    org_unit_id: str = Field(..., description="Parent operating unit ID")
    title: str = Field(..., description="Canonical role title")
    slug: str = Field(default="", description="URL-friendly slug")
    seniority_tier: str = Field(
        default="PRINCIPAL_STAFF",
        description="Seniority tier: 'C_SUITE', 'VP', 'DIRECTOR', 'PRINCIPAL_STAFF', 'SENIOR_SPECIALIST', 'LEAD_AUDITOR', 'OPERATIONS_COMMANDER'",
    )
    role_archetype: str = Field(
        default="engineering_staff",
        description="Archetype: 'executive_strategy', 'engineering_staff', 'domain_specialist', 'operations', 'risk_compliance'",
    )
    exemplar_lineage: str = Field(default="", description="Exemplar lineage and pedigree")
    mission: str = Field(default="", description="Core fiduciary and operational duty")
    mental_models: List[str] = Field(
        default_factory=list, description="First-principles mental models & theorems"
    )
    heuristics: List[str] = Field(
        default_factory=list, description="Operational heuristics and decision rules"
    )
    vocabulary: List[str] = Field(
        default_factory=list, description="Specialized technical vocabulary & standards"
    )
    anti_patterns: List[str] = Field(
        default_factory=list, description="Rejection criteria and anti-patterns"
    )
    system_prompt: str = Field(
        default="", description="Full compiled domain meta-prompt (>= 1,200 chars)"
    )
    input_artifact_ids: List[str] = Field(
        default_factory=list, description="IDs of consumed input artifacts"
    )
    output_artifact_ids: List[str] = Field(
        default_factory=list, description="IDs of produced output artifacts"
    )
    capabilities: List[str] = Field(
        default_factory=list, description="Flattened capability tags"
    )
    industry: Optional[str] = Field(default=None, description="Parent macro industry name or category")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")

    @property
    def name(self) -> str:
        return self.title

    @property
    def seniority_level(self) -> str:
        return self.seniority_tier

    @property
    def domain_heuristics(self) -> List[str]:
        return self.heuristics

    @property
    def technical_vocabulary(self) -> List[str]:
        return self.vocabulary

    @property
    def character_count(self) -> int:
        return len(self.system_prompt)

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            return getattr(self, item)
        if self.metadata and item in self.metadata:
            return self.metadata[item]
        raise KeyError(f"CanonicalRole has no attribute '{item}'")

    def get(self, item: str, default: Any = None) -> Any:
        if hasattr(self, item):
            val = getattr(self, item)
            return val if val is not None else default
        if self.metadata and item in self.metadata:
            return self.metadata.get(item, default)
        return default

    @model_validator(mode="before")
    @classmethod
    def sync_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("title") and data.get("name"):
                data["title"] = data["name"]
            if not data.get("seniority_tier") and data.get("seniority_level"):
                data["seniority_tier"] = data["seniority_level"]
            if not data.get("heuristics") and data.get("domain_heuristics"):
                data["heuristics"] = data["domain_heuristics"]
            if not data.get("vocabulary") and data.get("technical_vocabulary"):
                data["vocabulary"] = data["technical_vocabulary"]
            if not data.get("slug") and data.get("id"):
                data["slug"] = data["id"].replace("role_", "")
        return data


class RoleEdge(BaseModel):
    """Directed graph edge connecting two canonical roles."""

    source_role_id: str = Field(..., description="Originating role ID")
    target_role_id: str = Field(..., description="Destination role ID")
    edge_type: str = Field(
        ...,
        description="Edge type: 'REPORTS_TO', 'COLLABORATES_WITH', 'HANDS_OFF_TO', 'REVIEWS_AND_GATES', 'CHALLENGES_OR_AUDITS'",
    )
    description: str = Field(default="", description="Description of the interaction")
    protocol: str = Field(default="", description="Interaction protocol or interface contract")
    cadence: str = Field(default="CONTINUOUS", description="Frequency of engagement")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")


class Artifact(BaseModel):
    """Concrete deliverable produced or consumed by canonical roles."""

    id: str = Field(..., description="Unique ID, e.g. 'art_telecom_6g_blueprint'")
    slug: str = Field(default="", description="Unique slug")
    name: str = Field(..., description="Artifact display name")
    description: str = Field(default="", description="Artifact substantive description")
    artifact_type: str = Field(
        default="SPECIFICATION",
        description="Type: 'SPECIFICATION', 'MODEL', 'POLICY', 'CODE', 'DOSSIER', 'AUDIT_REPORT', 'DATASET'",
    )
    schema_def: Dict[str, Any] = Field(
        default_factory=dict, description="JSON Schema definition of the artifact"
    )
    exemplar_context: str = Field(default="", description="Exemplar standard or context")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")

    @property
    def schema_definition(self) -> Dict[str, Any]:
        return self.schema_def

    @model_validator(mode="before")
    @classmethod
    def populate_schema(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("schema_def") and data.get("schema_definition"):
                data["schema_def"] = data["schema_definition"]
            if not data.get("slug") and data.get("id"):
                data["slug"] = data["id"].replace("art_", "")
        return data


class OperatingMechanism(BaseModel):
    """Signature operational ritual, gate, or mechanism driving world-class execution."""

    id: str = Field(..., description="Unique ID, e.g. 'mech_andon_cord'")
    exemplar_org_id: str = Field(..., description="Exemplar organization ID")
    slug: str = Field(default="", description="Unique slug")
    name: str = Field(..., description="Mechanism display name")
    mechanism_type: str = Field(
        default="GATE",
        description="Type: 'GATE', 'CADENCE', 'AUDIT', 'REVIEW_COUNCIL', 'PROBLEM_SOLVING'",
    )
    description: str = Field(default="", description="Detailed description")
    execution_steps: List[str] = Field(default_factory=list, description="Sequential steps")
    enforcement_rules: str = Field(default="", description="Mandatory enforcement rules")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")


class InvariantViolation(BaseModel):
    """Record of a Knowledge Graph structural invariant violation."""

    role_id: str
    role_name: str
    invariant_code: str
    message: str


class ValidationReport(BaseModel):
    """Report detailing invariant validation of the Knowledge Graph."""

    is_valid: bool
    total_roles: int
    violations: List[InvariantViolation] = Field(default_factory=list)

    @property
    def violation_count(self) -> int:
        return len(self.violations)


class RoleGenSpec(BaseModel):
    """Specification for dynamic role synthesis."""

    name: str = Field(..., description="Canonical role title")
    org_unit_slug: str = Field(..., description="Slug of existing org unit")
    seniority_level: str = Field(default="PRINCIPAL_STAFF", description="Seniority level")
    role_archetype: str = Field(default="engineering_staff", description="Role archetype")
    mission: str = Field(..., description="Fiduciary and operational mission")
    capabilities: List[str] = Field(default_factory=list, description="Capability keywords")
    mental_models: List[str] = Field(default_factory=list, description="Mental models & theorems")
    technical_vocabulary: List[str] = Field(default_factory=list, description="Domain vocabulary")
    anti_patterns: List[str] = Field(default_factory=list, description="Anti-patterns & filters")
    reports_to_role_slug: Optional[str] = Field(None, description="Supervisor role slug")
    collaborates_with_role_slugs: List[str] = Field(
        default_factory=list, description="Peer collaboration slugs"
    )
    output_artifact_name: Optional[str] = Field(None, description="Output artifact name")
    output_artifact_schema: Optional[Dict[str, Any]] = Field(None, description="Output schema")


# Alias RoleGenerationRequest to RoleGenSpec for full spec compatibility
RoleGenerationRequest = RoleGenSpec


class RoleGenerationResult(BaseModel):
    """Result of dynamic role synthesis."""

    success: bool
    role_id: str
    role_slug: str
    character_count: int
    edges_created: int
    artifacts_created: int
    validation_passed: bool
    system_prompt: str
    role: Optional[CanonicalRole] = None


class Fortune500Company(BaseModel):
    """Fortune 500 Enterprise entity with authentic economic and organizational profile."""

    id: str = Field(..., description="Unique ID, e.g. 'f500_walmart'")
    slug: str = Field(default="", description="URL-friendly slug, e.g. 'walmart'")
    name: str = Field(..., description="Corporate legal name")
    rank: int = Field(..., description="Fortune 500 rank (1-500)")
    revenue_billions: float = Field(..., description="Annual revenue in billions USD")
    macro_industry: str = Field(..., description="Macro socioeconomic industry")
    industry_id: str = Field(..., description="Foreign key to industries.id, e.g. 'ind_retail_consumer'")
    sub_sector: str = Field(..., description="Specific industry sub-sector")
    business_model: str = Field(..., description="Business model archetype")
    operating_archetype: str = Field(..., description="Operating coordination archetype")
    functional_units: List[str] = Field(default_factory=list, description="Primary operational units/divisions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata (ticker, HQ, etc.)")

    @property
    def title(self) -> str:
        """Alias for name for UI/search consistency."""
        return self.name

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            return getattr(self, item)
        if self.metadata and item in self.metadata:
            return self.metadata[item]
        raise KeyError(f"Fortune500Company has no attribute '{item}'")

    def get(self, item: str, default: Any = None) -> Any:
        if hasattr(self, item):
            val = getattr(self, item)
            return val if val is not None else default
        if self.metadata and item in self.metadata:
            return self.metadata.get(item, default)
        return default

    @model_validator(mode="before")
    @classmethod
    def populate_helpers(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("slug") and data.get("id"):
                data["slug"] = data["id"].replace("f500_", "")
            if not data.get("slug") and data.get("name"):
                data["slug"] = (
                    data["name"]
                    .lower()
                    .replace(" ", "_")
                    .replace(".", "")
                    .replace("-", "_")
                    .replace("/", "_")
                    .replace(",", "")
                    .replace("&", "and")
                )
            if not data.get("functional_units") and data.get("functional_units_json"):
                raw = data["functional_units_json"]
                data["functional_units"] = json.loads(raw) if isinstance(raw, str) else raw
            if not data.get("metadata") and data.get("metadata_json"):
                raw = data["metadata_json"]
                data["metadata"] = json.loads(raw) if isinstance(raw, str) else raw
        return data


class EmploysRoleEdge(BaseModel):
    """High-density bipartite relationship between a Fortune 500 company and a canonical role."""

    id: Optional[str] = Field(default=None, description="Unique ID, e.g. 'emp_f500_walmart_role_ceo'")
    company_id: str = Field(..., description="Foreign key to fortune500_companies.id")
    role_id: str = Field(..., description="Foreign key to canonical_roles.id")
    department: str = Field(..., description="Department or functional division")
    priority_tier: str = Field(
        ...,
        description="Priority tier: 'STRATEGIC_LEADERSHIP', 'SHARED_SERVICE', 'CORE', 'SPECIALIZED', etc.",
    )
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            return getattr(self, item)
        if self.metadata and item in self.metadata:
            return self.metadata[item]
        raise KeyError(f"EmploysRoleEdge has no attribute '{item}'")

    def get(self, item: str, default: Any = None) -> Any:
        if hasattr(self, item):
            val = getattr(self, item)
            return val if val is not None else default
        if self.metadata and item in self.metadata:
            return self.metadata.get(item, default)
        return default

    @model_validator(mode="before")
    @classmethod
    def populate_helpers(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("id") and data.get("company_id") and data.get("role_id"):
                data["id"] = f"emp_{data['company_id']}_{data['role_id']}"
            if not data.get("metadata") and data.get("metadata_json"):
                raw = data["metadata_json"]
                data["metadata"] = json.loads(raw) if isinstance(raw, str) else raw
        return data


class CompanyInternetComparison(BaseModel):
    """Deep SEC 10-K divisions and internet-mined ground truth vs knowledge base alignment."""

    id: Optional[str] = Field(default=None, description="Unique ID, e.g. 'cic_f500_walmart'")
    company_id: str = Field(..., description="Foreign key to fortune500_companies.id")
    f500_rank: int = Field(..., description="Fortune 500 rank (1-500)")
    company_name: str = Field(..., description="Company name")
    internet_divisions: List[str] = Field(default_factory=list, description="Divisions discovered from public SEC 10-K/filings")
    internet_bespoke_roles: List[str] = Field(default_factory=list, description="Live job titles discovered from public job boards")
    db_mapped_roles_count: int = Field(default=0, description="Number of canonical roles mapped in SQLite")
    alignment_score: float = Field(default=1.0, description="Alignment score (0.0 - 1.0)")
    delta_analysis_md: str = Field(default="", description="Markdown delta analysis between internet and DB")
    tailored_swarm_recommendation_md: str = Field(default="", description="Tailored subagent swarm recommendation")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            return getattr(self, item)
        raise KeyError(f"CompanyInternetComparison has no attribute '{item}'")

    def get(self, item: str, default: Any = None) -> Any:
        if hasattr(self, item):
            val = getattr(self, item)
            return val if val is not None else default
        return default

    @model_validator(mode="before")
    @classmethod
    def populate_helpers(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("id") and data.get("company_id"):
                data["id"] = f"cic_{data['company_id']}"
            if not data.get("internet_divisions") and data.get("internet_divisions_json"):
                raw = data["internet_divisions_json"]
                data["internet_divisions"] = json.loads(raw) if isinstance(raw, str) else raw
            if not data.get("internet_bespoke_roles") and data.get("internet_bespoke_roles_json"):
                raw = data["internet_bespoke_roles_json"]
                data["internet_bespoke_roles"] = json.loads(raw) if isinstance(raw, str) else raw
        return data


class Tool(BaseModel):
    """Horizontal productivity or vertical domain software tool."""

    id: str = Field(..., description="Unique tool ID, e.g. 'tool_word_processor'")
    slug: str = Field(default="", description="Unique URL-friendly slug")
    name: str = Field(..., description="Tool display name")
    category: str = Field(
        ...,
        description="Category: 'HORIZONTAL_PRODUCTIVITY' or 'VERTICAL_DOMAIN'",
    )
    archetype: str = Field(..., description="Archetype classification")
    vendor_examples: List[str] = Field(default_factory=list, description="Industry vendor examples")
    typical_artifacts: List[str] = Field(default_factory=list, description="Standard artifacts produced/edited")
    description: str = Field(default="", description="Detailed description")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")
    created_at: Optional[str] = None

    @property
    def layer(self) -> str:
        return self.category

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            return getattr(self, item)
        if self.metadata and item in self.metadata:
            return self.metadata[item]
        raise KeyError(f"Tool has no attribute '{item}'")

    def get(self, item: str, default: Any = None) -> Any:
        if hasattr(self, item):
            val = getattr(self, item)
            return val if val is not None else default
        if self.metadata and item in self.metadata:
            return self.metadata.get(item, default)
        return default

    @model_validator(mode="before")
    @classmethod
    def populate_helpers(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("slug") and data.get("id"):
                data["slug"] = data["id"].replace("tool_", "")
            if not data.get("category") and data.get("layer"):
                data["category"] = data["layer"]
            if not data.get("vendor_examples") and data.get("vendor_examples_json"):
                raw = data["vendor_examples_json"]
                data["vendor_examples"] = json.loads(raw) if isinstance(raw, str) else raw
            if not data.get("typical_artifacts") and data.get("typical_artifacts_json"):
                raw = data["typical_artifacts_json"]
                data["typical_artifacts"] = json.loads(raw) if isinstance(raw, str) else raw
            if not data.get("metadata") and data.get("metadata_json"):
                raw = data["metadata_json"]
                data["metadata"] = json.loads(raw) if isinstance(raw, str) else raw
        return data


# Alias ToolDefinition to Tool for full spec compatibility
ToolDefinition = Tool


class RoleUseCase(BaseModel):
    """Day-to-day operational use case for a canonical role."""

    id: str = Field(..., description="Unique use case ID, e.g. 'ruc_role_123_1'")
    role_id: str = Field(..., description="Foreign key to canonical_roles.id")
    title: str = Field(..., description="Operational title of the use case")
    cadence: str = Field(
        ...,
        description="Cadence: 'DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY', 'AD_HOC', 'CONTINUOUS'",
    )
    trigger_event: str = Field(..., description="Trigger event activating the use case")
    inputs_consumed: List[str] = Field(default_factory=list, description="Inputs and data sources consumed")
    horizontal_tools: List[str] = Field(default_factory=list, description="Horizontal productivity tools used")
    vertical_tools: List[str] = Field(default_factory=list, description="Vertical domain systems used")
    cognitive_bottlenecks: str = Field(default="", description="Key cognitive bottleneck or challenge")
    output_artifacts: List[str] = Field(default_factory=list, description="Output artifacts produced")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")
    created_at: Optional[str] = None

    @property
    def trigger(self) -> str:
        return self.trigger_event

    @property
    def inputs(self) -> List[str]:
        return self.inputs_consumed

    @property
    def domain_tools(self) -> List[str]:
        return self.vertical_tools

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            return getattr(self, item)
        if self.metadata and item in self.metadata:
            return self.metadata[item]
        raise KeyError(f"RoleUseCase has no attribute '{item}'")

    def get(self, item: str, default: Any = None) -> Any:
        if hasattr(self, item):
            val = getattr(self, item)
            return val if val is not None else default
        if self.metadata and item in self.metadata:
            return self.metadata.get(item, default)
        return default

    @model_validator(mode="before")
    @classmethod
    def populate_helpers(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("trigger_event") and data.get("trigger"):
                data["trigger_event"] = data["trigger"]
            if not data.get("inputs_consumed") and data.get("inputs"):
                data["inputs_consumed"] = data["inputs"]
            if not data.get("inputs_consumed") and data.get("inputs_consumed_json"):
                raw = data["inputs_consumed_json"]
                data["inputs_consumed"] = json.loads(raw) if isinstance(raw, str) else raw
            if not data.get("horizontal_tools") and data.get("horizontal_tools_json"):
                raw = data["horizontal_tools_json"]
                data["horizontal_tools"] = json.loads(raw) if isinstance(raw, str) else raw
            if not data.get("vertical_tools") and data.get("domain_tools"):
                data["vertical_tools"] = data["domain_tools"]
            if not data.get("vertical_tools") and data.get("vertical_tools_json"):
                raw = data["vertical_tools_json"]
                data["vertical_tools"] = json.loads(raw) if isinstance(raw, str) else raw
            if not data.get("output_artifacts") and data.get("output_artifacts_json"):
                raw = data["output_artifacts_json"]
                data["output_artifacts"] = json.loads(raw) if isinstance(raw, str) else raw
            if isinstance(data.get("cognitive_bottlenecks"), list):
                data["cognitive_bottlenecks"] = "; ".join(data["cognitive_bottlenecks"])
            if not data.get("metadata") and data.get("metadata_json"):
                raw = data["metadata_json"]
                data["metadata"] = json.loads(raw) if isinstance(raw, str) else raw
        return data


class RoleTooling(BaseModel):
    """Bipartite association between a canonical role and a software tool."""

    id: Optional[str] = Field(default=None, description="Unique ID, e.g. 'rt_role_123_tool_word_processor'")
    role_id: str = Field(..., description="Foreign key to canonical_roles.id")
    tool_id: str = Field(..., description="Foreign key to tools.id")
    usage_frequency: str = Field(
        ...,
        description="Usage frequency: 'PRIMARY_DAILY', 'FREQUENT_WEEKLY', 'OCCASIONAL', 'CRITICAL_INCIDENT'",
    )
    proficiency_level: str = Field(
        ...,
        description="Proficiency level: 'EXPERT', 'PROFICIENT', 'WORKING_KNOWLEDGE', 'BASIC'",
    )
    primary_purpose: str = Field(..., description="Primary reason the role uses this tool")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")
    created_at: Optional[str] = None

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            return getattr(self, item)
        if self.metadata and item in self.metadata:
            return self.metadata[item]
        raise KeyError(f"RoleTooling has no attribute '{item}'")

    def get(self, item: str, default: Any = None) -> Any:
        if hasattr(self, item):
            val = getattr(self, item)
            return val if val is not None else default
        if self.metadata and item in self.metadata:
            return self.metadata.get(item, default)
        return default

    @model_validator(mode="before")
    @classmethod
    def populate_helpers(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("id") and data.get("role_id") and data.get("tool_id"):
                data["id"] = f"rt_{data['role_id']}_{data['tool_id']}"
            if not data.get("metadata") and data.get("metadata_json"):
                raw = data["metadata_json"]
                data["metadata"] = json.loads(raw) if isinstance(raw, str) else raw
        return data


VALID_SUBAGENT_ROLES = Literal[
    "CHIEF_OF_STAFF",
    "DOCUMENT_DRAFTER",
    "QUANTITATIVE_MODELER",
    "DECK_PRESENTER",
    "MEETING_GRAPH",
    "DOMAIN_SPECIALIST",
    "QUALITY_CRITIC",
]


class RoleSubagentSwarm(BaseModel):
    """Personal Subagent Swarm ("Role-in-a-Box") specification for a canonical role."""

    id: Optional[str] = Field(default=None, description="Unique ID, e.g. 'rss_role_123_chief_of_staff'")
    role_id: str = Field(..., description="Foreign key to canonical_roles.id")
    subagent_name: str = Field(..., description="Display name of the specialized subagent")
    subagent_role: VALID_SUBAGENT_ROLES = Field(
        ...,
        description="Archetype role: 'CHIEF_OF_STAFF', 'DOCUMENT_DRAFTER', 'QUANTITATIVE_MODELER', 'DECK_PRESENTER', 'MEETING_GRAPH', 'DOMAIN_SPECIALIST', 'QUALITY_CRITIC'",
    )
    system_prompt: str = Field(..., description="Specialized domain prompt for the subagent")
    tool_mcp_bindings: List[str] = Field(default_factory=list, description="Bound tools and MCP server endpoints")
    interaction_dag: Dict[str, Any] = Field(default_factory=dict, description="Interaction DAG (triggers, upstream, downstream handoffs)")
    hitl_checkpoint: str = Field(..., description="Human-in-the-loop review criteria and audit checkpoints")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")
    created_at: Optional[str] = None

    @property
    def archetype(self) -> str:
        return self.subagent_role

    @property
    def mcp_tools(self) -> List[str]:
        return self.tool_mcp_bindings

    @property
    def upstream_subagents(self) -> List[str]:
        return self.interaction_dag.get("upstream", [])

    @property
    def downstream_subagents(self) -> List[str]:
        return self.interaction_dag.get("downstream", [])

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            return getattr(self, item)
        if self.metadata and item in self.metadata:
            return self.metadata[item]
        raise KeyError(f"RoleSubagentSwarm has no attribute '{item}'")

    def get(self, item: str, default: Any = None) -> Any:
        if hasattr(self, item):
            val = getattr(self, item)
            return val if val is not None else default
        if self.metadata and item in self.metadata:
            return self.metadata.get(item, default)
        return default

    @model_validator(mode="before")
    @classmethod
    def populate_helpers(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("id") and data.get("role_id") and (data.get("subagent_role") or data.get("archetype")):
                role_val = data.get("subagent_role") or data.get("archetype")
                data["id"] = f"rss_{data['role_id']}_{role_val.lower()}"
            if not data.get("subagent_role") and data.get("archetype"):
                data["subagent_role"] = data["archetype"]
            if not data.get("tool_mcp_bindings") and data.get("mcp_tools"):
                data["tool_mcp_bindings"] = data["mcp_tools"]
            if not data.get("tool_mcp_bindings") and data.get("tool_mcp_bindings_json"):
                raw = data["tool_mcp_bindings_json"]
                data["tool_mcp_bindings"] = json.loads(raw) if isinstance(raw, str) else raw
            if not data.get("interaction_dag") and data.get("interaction_dag_json"):
                raw = data["interaction_dag_json"]
                data["interaction_dag"] = json.loads(raw) if isinstance(raw, str) else raw
            if not data.get("metadata") and data.get("metadata_json"):
                raw = data["metadata_json"]
                data["metadata"] = json.loads(raw) if isinstance(raw, str) else raw
        return data


# Alias SubagentSpec to RoleSubagentSwarm for interface compatibility
SubagentSpec = RoleSubagentSwarm


class RoleGenAIPlan(BaseModel):
    """Generative AI Tooling Engineering Blueprint for a canonical role."""

    id: Optional[str] = Field(default=None, description="Unique ID, e.g. 'rgp_role_123'")
    role_id: str = Field(..., description="Foreign key to canonical_roles.id")
    horizontal_genai_spec: Dict[str, Any] = Field(default_factory=dict, description="Specs for Word Copilot, Excel Modeler, Slide Builder, Meeting Graph")
    vertical_genai_spec: Dict[str, Any] = Field(default_factory=dict, description="Specs for vertical domain system copilot/automation")
    rag_context_architecture: str = Field(..., description="Retrieval-augmented generation architecture and context window strategy")
    mcp_integrations: List[str] = Field(default_factory=list, description="Connected MCP servers and protocols")
    hitl_guardrails: str = Field(..., description="Human sign-off gates, audit triggers, and risk thresholds")
    roi_productivity_impact: str = Field(..., description="Quantified ROI and time-to-deliver reduction metrics")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata")
    created_at: Optional[str] = None

    @property
    def context_rag_architecture(self) -> str:
        return self.rag_context_architecture

    @property
    def quantified_roi_impact(self) -> str:
        return self.roi_productivity_impact

    def __getitem__(self, item: str) -> Any:
        if hasattr(self, item):
            return getattr(self, item)
        if self.metadata and item in self.metadata:
            return self.metadata[item]
        raise KeyError(f"RoleGenAIPlan has no attribute '{item}'")

    def get(self, item: str, default: Any = None) -> Any:
        if hasattr(self, item):
            val = getattr(self, item)
            return val if val is not None else default
        if self.metadata and item in self.metadata:
            return self.metadata.get(item, default)
        return default

    @model_validator(mode="before")
    @classmethod
    def populate_helpers(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("id") and data.get("role_id"):
                data["id"] = f"rgp_{data['role_id']}"
            if not data.get("rag_context_architecture") and data.get("context_rag_architecture"):
                data["rag_context_architecture"] = data["context_rag_architecture"]
            if not data.get("roi_productivity_impact") and data.get("quantified_roi_impact"):
                data["roi_productivity_impact"] = data["quantified_roi_impact"]
            if not data.get("horizontal_genai_spec") and data.get("horizontal_genai_spec_json"):
                raw = data["horizontal_genai_spec_json"]
                data["horizontal_genai_spec"] = json.loads(raw) if isinstance(raw, str) else raw
            if not data.get("vertical_genai_spec") and data.get("vertical_genai_spec_json"):
                raw = data["vertical_genai_spec_json"]
                data["vertical_genai_spec"] = json.loads(raw) if isinstance(raw, str) else raw
            if not data.get("mcp_integrations") and data.get("mcp_integrations_json"):
                raw = data["mcp_integrations_json"]
                data["mcp_integrations"] = json.loads(raw) if isinstance(raw, str) else raw
            if not data.get("metadata") and data.get("metadata_json"):
                raw = data["metadata_json"]
                data["metadata"] = json.loads(raw) if isinstance(raw, str) else raw
        return data


# Alias GenAIPlan to RoleGenAIPlan for interface compatibility
GenAIPlan = RoleGenAIPlan

