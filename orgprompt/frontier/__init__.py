"""Nov 2026 Frontier AI Lab & Real-World Enterprise Join Layer (`orgprompt.frontier`)."""

from orgprompt.frontier.catalog_bridges import REAL_WORLD_TO_FRONTIER_BRIDGES_CATALOG
from orgprompt.frontier.catalog_labs import FRONTIER_AI_LABS_CATALOG, FRONTIER_LAB_PODS_CATALOG
from orgprompt.frontier.formatter import (
    format_company_join_markdown,
    format_lab_markdown,
    format_problem_bridge_markdown,
    format_role_join_markdown,
)
from orgprompt.frontier.join_engine import (
    FrontierLabJoinEngine,
    inspect_frontier_lab,
    list_frontier_labs,
    seed_frontier_join_layer,
)
from orgprompt.frontier.models import (
    CompanyFrontierJoinResult,
    FrontierAILab,
    FrontierJoinMechanism,
    FrontierLabPod,
    FrontierPodCategory,
    ProblemFrontierBridgeResult,
    RealWorldToFrontierBridge,
    RoleFrontierJoinEdge,
    RoleFrontierJoinResult,
)
from orgprompt.frontier.schema import (
    FRONTIER_JOIN_MECHANISMS,
    FRONTIER_POD_CATEGORIES,
    FRONTIER_SCHEMA_DDL,
    ensure_frontier_schema,
)

__all__ = [
    "FRONTIER_AI_LABS_CATALOG",
    "FRONTIER_LAB_PODS_CATALOG",
    "REAL_WORLD_TO_FRONTIER_BRIDGES_CATALOG",
    "FRONTIER_JOIN_MECHANISMS",
    "FRONTIER_POD_CATEGORIES",
    "FRONTIER_SCHEMA_DDL",
    "ensure_frontier_schema",
    "seed_frontier_join_layer",
    "FrontierLabJoinEngine",
    "list_frontier_labs",
    "inspect_frontier_lab",
    "FrontierJoinMechanism",
    "FrontierPodCategory",
    "FrontierLabPod",
    "FrontierAILab",
    "RealWorldToFrontierBridge",
    "RoleFrontierJoinEdge",
    "RoleFrontierJoinResult",
    "CompanyFrontierJoinResult",
    "ProblemFrontierBridgeResult",
    "format_lab_markdown",
    "format_role_join_markdown",
    "format_company_join_markdown",
    "format_problem_bridge_markdown",
]
