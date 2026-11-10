"""Fiduciary Governance & Independent Audit Taxonomy Tier (`orgprompt.governance`).

Sits above and outside the operating management org chart (`canonical_roles`) to represent
shareholders, capital providers, regulators, and independent statutory/strategic assurance.
"""

from orgprompt.governance.catalog import (
    ALL_GOVERNANCE_ROLE_SPECS,
    INDUSTRY_BOARD_COMPOSITIONS,
    board_for_company,
    get_governance_role,
    list_governance_roles,
    list_industry_board_compositions,
    seed_governance_taxonomy,
)
from orgprompt.governance.formatter import (
    format_board_slate_markdown,
    format_governance_role_markdown,
    format_superhuman_governance_json,
    format_superhuman_governance_markdown,
)
from orgprompt.governance.models import (
    AcademicCredentialFoundation,
    BoardroomAndAuditCrucibles,
    BoardroomCrucibleEpisode,
    BoardSlateRecommendation,
    CommitteeAndSeamFusion,
    CompanyStage,
    FiduciaryTemperament,
    GovernanceCategory,
    GovernanceEdgeType,
    GovernanceEpistemicStage,
    GovernanceOversightEdge,
    GovernanceRole,
    IndustryBoardComposition,
    SuperhumanGovernancePackage,
    UnknownRiskEpistemology,
)
from orgprompt.governance.schema import (
    COMPANY_STAGES,
    GOVERNANCE_CATEGORIES,
    GOVERNANCE_EDGE_TYPES,
    GOVERNANCE_SCHEMA_DDL,
    ensure_governance_schema,
)
from orgprompt.governance.superhuman_gov import (
    FLAGSHIP_SUPERHUMAN_GOVERNANCE_SPECS,
    SuperhumanGovernanceSynthesizer,
    seed_flagship_superhuman_governance_profiles,
)

__all__ = [
    "ALL_GOVERNANCE_ROLE_SPECS",
    "INDUSTRY_BOARD_COMPOSITIONS",
    "COMPANY_STAGES",
    "GOVERNANCE_CATEGORIES",
    "GOVERNANCE_EDGE_TYPES",
    "GOVERNANCE_SCHEMA_DDL",
    "ensure_governance_schema",
    "seed_governance_taxonomy",
    "list_governance_roles",
    "get_governance_role",
    "list_industry_board_compositions",
    "board_for_company",
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
    "SuperhumanGovernanceSynthesizer",
    "FLAGSHIP_SUPERHUMAN_GOVERNANCE_SPECS",
    "seed_flagship_superhuman_governance_profiles",
    "format_governance_role_markdown",
    "format_board_slate_markdown",
    "format_superhuman_governance_markdown",
    "format_superhuman_governance_json",
]
