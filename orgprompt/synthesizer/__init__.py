"""Synthesizer module for dynamic team selection and workflow DAG compilation.

Provides:
- CapabilityExtractor & CapabilityProfile: Natural language problem decomposition.
- TeamSynthesizer & TeamSynthesisResult: Constrained cross-functional team assembly.
- WorkflowDAGCompiler: Staged task projection compiling cyclic KG relationships into an acyclic DAG.
- WorkflowEngine, WorkflowEngineResult, WorkflowTaskState & ArtifactEnvelope: Topological DAG execution.
"""

from orgprompt.synthesizer.dag_compiler import WorkflowDAGCompiler
from orgprompt.synthesizer.extractor import (
    CapabilityExtractor,
    CapabilityProfile,
)
from orgprompt.synthesizer.team_builder import (
    TeamSynthesisResult,
    TeamSynthesizer,
)
from orgprompt.synthesizer.workflow_engine import (
    ArtifactEnvelope,
    WorkflowEngine,
    WorkflowEngineResult,
    WorkflowExecutionError,
    WorkflowState,
    WorkflowTaskResult,
    WorkflowTaskState,
)

__all__ = [
    "CapabilityExtractor",
    "CapabilityProfile",
    "TeamSynthesizer",
    "TeamSynthesisResult",
    "WorkflowDAGCompiler",
    "WorkflowEngine",
    "WorkflowEngineResult",
    "WorkflowTaskResult",
    "WorkflowTaskState",
    "ArtifactEnvelope",
    "WorkflowState",
    "WorkflowExecutionError",
]
