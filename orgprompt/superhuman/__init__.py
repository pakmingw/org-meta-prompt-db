"""Phase 12 Superhuman Role Synthesis Engine (`orgprompt.superhuman`)."""

from orgprompt.superhuman.formatter import (
    compile_deep_superhuman_prompt,
    format_superhuman_json,
    format_superhuman_markdown,
)
from orgprompt.superhuman.models import (
    AcademicFoundation,
    AdjacentRoleFusion,
    CrucibleEpisode,
    EpistemicStage,
    HumanCharacteristics,
    OnTheJobCrucible,
    OnTheJobCrucibles,
    SuperhumanRolePackage,
    UnknownProblemEpistemology,
)
from orgprompt.superhuman.profiler import (
    build_academic_foundation,
    build_human_characteristics,
    build_on_the_job_crucibles,
    build_unknown_problem_epistemology,
)
from orgprompt.superhuman.synthesizer import SuperhumanRoleSynthesizer

__all__ = [
    "SuperhumanRoleSynthesizer",
    "SuperhumanRolePackage",
    "AcademicFoundation",
    "CrucibleEpisode",
    "OnTheJobCrucibles",
    "OnTheJobCrucible",
    "HumanCharacteristics",
    "AdjacentRoleFusion",
    "EpistemicStage",
    "UnknownProblemEpistemology",
    "compile_deep_superhuman_prompt",
    "format_superhuman_json",
    "format_superhuman_markdown",
    "build_academic_foundation",
    "build_on_the_job_crucibles",
    "build_human_characteristics",
    "build_unknown_problem_epistemology",
]
