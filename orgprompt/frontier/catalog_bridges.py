"""Unified Cross-Industry & Horizontal Real-World <-> Frontier AI Lab Bridges Catalog (`orgprompt.frontier.catalog_bridges`)."""

from __future__ import annotations

from typing import Any, Dict, List

from orgprompt.frontier.catalog_bridges_part1 import BRIDGES_PART1
from orgprompt.frontier.catalog_bridges_part2 import BRIDGES_PART2

REAL_WORLD_TO_FRONTIER_BRIDGES_CATALOG: List[Dict[str, Any]] = [
    *BRIDGES_PART1,
    *BRIDGES_PART2,
]

__all__ = ["REAL_WORLD_TO_FRONTIER_BRIDGES_CATALOG"]
