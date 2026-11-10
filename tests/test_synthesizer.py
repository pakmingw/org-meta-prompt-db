"""Tests for CapabilityExtractor, TeamSynthesizer, WorkflowDAGCompiler, and WorkflowEngine."""

from pathlib import Path
import networkx as nx
import pytest

from orgprompt.db.connection import get_default_db_path
from orgprompt.synthesizer import (
    ArtifactEnvelope,
    CapabilityExtractor,
    CapabilityProfile,
    TeamSynthesisResult,
    TeamSynthesizer,
    WorkflowDAGCompiler,
    WorkflowEngine,
    WorkflowEngineResult,
    WorkflowExecutionError,
    WorkflowTaskResult,
    WorkflowTaskState,
)


FLAGSHIP_PROBLEM = (
    "Architecting, economically modeling, stress-testing, and governing a next-generation "
    "Sovereign AI + 6G Edge Telecommunications + Real-Time Financial Settlement Infrastructure "
    "under strict regulatory, capital, latency, and adversarial security constraints."
)


# ---------------------------------------------------------------------------
# 1. Capability Extractor Tests
# ---------------------------------------------------------------------------

def test_capability_extractor_domains():
    extractor = CapabilityExtractor()
    profile = extractor.extract(FLAGSHIP_PROBLEM)

    assert isinstance(profile, CapabilityProfile)
    assert len(profile.domains) >= 3
    # Verify expected domains identified
    expected_any = [
        "Telecommunications & Digital Networks",
        "Finance & Quantitative Trading",
        "Technology & AI",
        "Cybersecurity & Defense",
        "Public Sector & Regulation",
    ]
    assert any(d in profile.domains for d in expected_any)


def test_capability_extractor_disciplines_and_constraints():
    extractor = CapabilityExtractor()
    profile = extractor.extract(FLAGSHIP_PROBLEM)

    assert len(profile.technical_disciplines) > 0
    assert "latency" in profile.constraints
    assert "capital" in profile.constraints
    assert "regulatory" in profile.constraints
    assert "adversarial" in profile.constraints

    assert profile.constraints["latency"]["target_end_to_end"] == "< 5.0ms"
    assert "Basel III/IV Intraday Monitoring" in profile.constraints["capital"]["frameworks"]


def test_capability_extractor_fallback():
    extractor = CapabilityExtractor()
    sparse_query = "Build a simple app"
    profile = extractor.extract(sparse_query)

    # Fallback should guarantee at least 3 domains
    assert len(profile.domains) >= 3


def test_capability_profile_dict_and_subscript():
    extractor = CapabilityExtractor()
    profile = extractor.extract(FLAGSHIP_PROBLEM)

    d = profile.to_dict()
    assert isinstance(d, dict)
    assert d["domains"] == profile.domains
    assert profile["domains"] == profile.domains
    assert profile.get("domains") == profile.domains
    assert profile.get("non_existent", "default_val") == "default_val"


# ---------------------------------------------------------------------------
# 2. Team Synthesizer Tests
# ---------------------------------------------------------------------------

def test_team_synthesizer_constraints():
    db_path = get_default_db_path()
    synthesizer = TeamSynthesizer.build_from_db(db_path)
    result = synthesizer.synthesize_team(FLAGSHIP_PROBLEM, min_roles=8)

    assert isinstance(result, TeamSynthesisResult)
    roles = result.roles
    assert len(roles) >= 8

    # Check industry diversity
    industries = {r.industry for r in roles if r.industry}
    assert len(industries) >= 3

    # Check archetype balance
    archetypes = {getattr(r, "role_archetype", "") for r in roles}
    assert any("executive" in a.lower() for a in archetypes)
    assert any("risk" in a.lower() or "compliance" in a.lower() or "audit" in a.lower() for a in archetypes)
    assert any("operations" in a.lower() for a in archetypes)
    assert any("engineering" in a.lower() or "specialist" in a.lower() for a in archetypes)

    # Check helper methods
    assert result.has_archetype("executive")
    assert result["problem_statement"] == FLAGSHIP_PROBLEM
    assert result.get("roles") == roles


def test_team_synthesizer_custom_bounds():
    db_path = get_default_db_path()
    synthesizer = TeamSynthesizer.build_from_db(db_path)
    result = synthesizer.synthesize_team(
        "Design quantum cryptographic key distribution for power grids",
        min_roles=9,
        max_roles=12,
    )
    assert len(result.roles) >= 9
    assert len(result.roles) <= 12


# ---------------------------------------------------------------------------
# 3. Workflow DAG Compiler Tests
# ---------------------------------------------------------------------------

def test_workflow_dag_compiler_acyclic_and_stages():
    db_path = get_default_db_path()
    synthesizer = TeamSynthesizer.build_from_db(db_path)
    result = synthesizer.synthesize_team(FLAGSHIP_PROBLEM, min_roles=8)

    dag = result.dag
    assert dag is not None
    assert nx.is_directed_acyclic_graph(dag), "Compiled execution DAG must be provably acyclic"

    # Verify all 6 stages present in the DAG nodes
    stages_present = {dag.nodes[n].get("stage") for n in dag.nodes}
    expected_stages = {
        "stage_1_scoping",
        "stage_2_specialists",
        "stage_3_integration",
        "stage_4_audit_gate",
        "stage_5_remediation",
        "stage_6_final_dossier",
    }
    assert expected_stages.issubset(stages_present)

    # Verify topological order
    topo_order = list(nx.topological_sort(dag))
    assert len(topo_order) == len(dag.nodes)

    # Stage 4 must contain a gate
    stage4_nodes = [n for n in dag.nodes if dag.nodes[n].get("stage_num") == 4]
    assert len(stage4_nodes) >= 1
    assert any(dag.nodes[n].get("is_gate") for n in stage4_nodes)


# ---------------------------------------------------------------------------
# 4. Workflow Engine Execution Tests
# ---------------------------------------------------------------------------

def test_workflow_engine_execution(tmp_path: Path):
    db_path = get_default_db_path()
    synthesizer = TeamSynthesizer.build_from_db(db_path)
    team_res = synthesizer.synthesize_team(FLAGSHIP_PROBLEM, min_roles=8)

    engine = WorkflowEngine()
    exec_res = engine.execute_dag(
        team_res.dag,
        problem_statement=FLAGSHIP_PROBLEM,
        output_dir=tmp_path,
    )

    assert isinstance(exec_res, WorkflowEngineResult)
    assert exec_res.status == "COMPLETED"
    assert len(exec_res.executed_nodes) == len(team_res.dag.nodes)

    # Check intermediate artifacts
    assert len(exec_res.intermediate_artifacts) >= 6
    for art_name in exec_res.intermediate_artifacts:
        art_file = tmp_path / art_name
        assert art_file.exists(), f"Artifact file {art_name} was not written to disk"
        assert art_file.stat().st_size > 0

    # Check red-team audit findings and upstream remediations
    assert len(exec_res.red_team_findings) >= 1
    assert len(exec_res.upstream_revisions) >= 1

    # Check master dossier compilation
    assert len(exec_res.solution_dossier.split()) >= 5000

    # Check dict conversion and access
    d = exec_res.to_dict()
    assert d["status"] == "COMPLETED"
    assert exec_res["status"] == "COMPLETED"
    assert exec_res.get("status") == "COMPLETED"


def test_workflow_cycle_rejection():
    # Construct a deliberately cyclic graph
    cyclic_graph = nx.DiGraph()
    cyclic_graph.add_edge("task_a", "task_b")
    cyclic_graph.add_edge("task_b", "task_a")

    engine = WorkflowEngine()
    with pytest.raises(WorkflowExecutionError):
        engine.execute(cyclic_graph)


def test_workflow_task_state_and_artifact_envelope():
    state = WorkflowTaskState(
        task_id="task_1",
        stage="stage_1_scoping",
        stage_num=1,
        role_slug="telecom_chief_architect",
        role_title="Chief Architect",
        artifact_name="charter.md",
        artifact_content="# Charter",
    )
    assert state.task_id == "task_1"
    assert state.status == "COMPLETED"
    assert state["task_id"] == "task_1"
    assert state.to_dict()["task_id"] == "task_1"

    envelope = ArtifactEnvelope(
        name="test_artifact.md",
        content="# Test Content",
        stage_num=2,
        role_slug="spec_engineer",
        role_title="Specialist Engineer",
    )
    assert envelope.name == "test_artifact.md"
    assert envelope["content"] == "# Test Content"
    assert envelope.to_dict()["stage_num"] == 2
