"""Challenge module for the Flagship Sovereign 6G + Financial AI Grand Challenge.

Provides:
- GrandChallengeRunner & GrandChallengeReport: End-to-end 6-stage trajectory execution.
- RedTeamAuditor, RedTeamAuditReport, VulnerabilityFinding, RemediationMandate & UpstreamRevisionRecord:
  Adversarial stress-testing, vulnerability discovery, and upstream remediation verification.
- MasterDossierCompiler: 9-chapter executive solution dossier compilation (>= 5,000 words).
"""

from orgprompt.challenge.dossier_compiler import (
    DossierCompilationError,
    MasterDossierCompiler,
)
from orgprompt.challenge.red_team import (
    RedTeamAuditor,
    RedTeamAuditReport,
    RemediationMandate,
    UpstreamRevisionRecord,
    VulnerabilityFinding,
)
from orgprompt.challenge.runner import (
    DEFAULT_FLAGSHIP_PROBLEM,
    GrandChallengeReport,
    GrandChallengeRunner,
)

__all__ = [
    "GrandChallengeRunner",
    "GrandChallengeReport",
    "RedTeamAuditor",
    "RedTeamAuditReport",
    "VulnerabilityFinding",
    "RemediationMandate",
    "UpstreamRevisionRecord",
    "MasterDossierCompiler",
    "DossierCompilationError",
    "DEFAULT_FLAGSHIP_PROBLEM",
]
