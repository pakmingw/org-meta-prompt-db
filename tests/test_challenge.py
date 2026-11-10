"""Tests for Grand Challenge Runner, Red Team Auditor, and Master Dossier Compiler.

Validates:
- 6-stage DAG trajectory execution
- Generation of >= 6 domain-authentic intermediate artifacts
- Adversarial Red Team audit discovering 3 empirical vulnerabilities and issuing 3 mandates
- Stage 4 rejection verdict ('REJECTED_MANDATORY_REVISION_REQUIRED')
- Upstream engineering redesigns and Stage 5 clearance ('PASSED_FULL_CERTIFICATION')
- Compilation of 9-chapter master solution dossier exceeding >= 5,000 words
- Filesystem persistence to output directory and artifacts folder
- Integration with WorkflowEngine.execute_grand_challenge()
"""

import json
import os
from pathlib import Path
import pytest

from orgprompt.challenge import (
    DEFAULT_FLAGSHIP_PROBLEM,
    DossierCompilationError,
    GrandChallengeReport,
    GrandChallengeRunner,
    MasterDossierCompiler,
    RedTeamAuditor,
    RedTeamAuditReport,
    RemediationMandate,
    UpstreamRevisionRecord,
    VulnerabilityFinding,
)
from orgprompt.challenge.chapters import ALL_CHAPTER_RENDERERS
from orgprompt.synthesizer import WorkflowEngine


def test_grand_challenge_runner_e2e_full_trajectory():
    """Validates the complete 6-stage Grand Challenge trajectory end-to-end."""
    runner = GrandChallengeRunner()
    report = runner.execute()

    assert report is not None
    assert report.status == "COMPLETED"
    assert report.problem_statement == DEFAULT_FLAGSHIP_PROBLEM

    # 1. Verify all 6 stages executed
    assert len(report.stages_executed) == 6
    expected_stage_prefixes = [
        "Stage 1",
        "Stage 2",
        "Stage 3",
        "Stage 4",
        "Stage 5",
        "Stage 6",
    ]
    for prefix in expected_stage_prefixes:
        assert any(s.startswith(prefix) for s in report.stages_executed), f"Missing {prefix}"

    # 2. Verify intermediate artifacts (>= 6)
    assert len(report.intermediate_artifacts) >= 6
    assert len(report.intermediate_artifacts) == 13

    # Check key intermediate artifacts exist in artifacts dict
    assert "Sovereign_Infrastructure_Charter_SLA_Hierarchy.md" in report.artifacts
    assert "Regulatory_Compliance_Jurisdictional_Boundary_Map.md" in report.artifacts
    assert "6G_SubTHz_Edge_Topology_URLLC_Numerology_Spec.json" in report.artifacts
    assert "ORAN_DU_Deterministic_MAC_Scheduler_Architecture.md" in report.artifacts
    assert "Atomic_RTGS_DvP_PvP_Settlement_State_Machine.json" in report.artifacts
    assert "Intraday_Liquidity_Optimization_Collateral_Stress_Model.py" in report.artifacts
    assert "Sovereign_Edge_AI_Inference_Pipeline_Spec.md" in report.artifacts
    assert "PostQuantum_HSM_Asynchronous_BFT_Consensus_Spec.json" in report.artifacts
    assert "Unified_EndToEnd_Latency_Capital_Security_Interface_Spec.md" in report.artifacts
    assert "Adversarial_RedTeam_StressTest_Vulnerability_Dossier.md" in report.artifacts
    assert "Remediation_Crypto_Hardware_Acceleration_Redesign.md" in report.artifacts
    assert "Remediation_Dynamic_Liquidity_Backstop_AMM_Vaults.md" in report.artifacts
    assert "Remediation_Enclave_ZK_Data_Fencing.md" in report.artifacts

    # 3. Verify Adversarial Red Team findings (3 vulnerabilities)
    assert len(report.red_team_findings) == 3
    vuln_ids = {f.vuln_id for f in report.red_team_findings}
    assert "VULN-001-PQC-LATENCY" in vuln_ids
    assert "VULN-002-LIQUIDITY-GRIDLOCK" in vuln_ids
    assert "VULN-003-AI-RESIDENCY-LEAK" in vuln_ids
    for f in report.red_team_findings:
        assert f.severity_cvss >= 8.5
        assert len(f.affected_roles) >= 2
        assert len(f.affected_components) >= 2

    # 4. Verify Upstream Revisions (3 records)
    assert len(report.upstream_revisions) == 3
    rev_ids = {r.revision_id for r in report.upstream_revisions}
    assert "REV-001-ASIC-NTT" in rev_ids
    assert "REV-002-DYNAMIC-AMM-LIQUIDITY" in rev_ids
    assert "REV-003-ENCLAVE-ZK-FENCE" in rev_ids
    for r in report.upstream_revisions:
        assert r.sla_status == "PASSED_AND_VERIFIED"
        assert len(r.redesign_summary) > 50

    # 5. Verify Master Dossier word count (>= 5,000 words)
    assert report.solution_dossier != ""
    word_count = len(report.solution_dossier.split())
    assert word_count >= 5000, f"Dossier has {word_count} words; expected >= 5,000 words"

    # 6. Verify dict and attr access compatibility
    assert report["status"] == "COMPLETED"
    assert len(report["intermediate_artifacts"]) >= 6
    assert report.get("solution_dossier") == report.solution_dossier


def test_red_team_auditor_stage4_and_stage5_cycles():
    """Unit test for RedTeamAuditor Stage 4 audit and Stage 5 remediation verification."""
    auditor = RedTeamAuditor()

    # Stage 4 Audit
    stage4 = auditor.run_stage4_audit(
        intermediate_artifacts={"dummy_art": "content"},
        constraints={"target_sla_ms": 5.0},
    )
    assert stage4.audit_id == "AUDIT-STAGE4-ADV-REDTEAM-001"
    assert stage4.verdict == "REJECTED_MANDATORY_REVISION_REQUIRED"
    assert len(stage4.findings) == 3
    assert len(stage4.mandates) == 3
    assert "## 1. Executive Summary of Audit Findings" in stage4.dossier_markdown

    # Stage 5 Verification
    stage5 = auditor.verify_remediations(
        remediation_artifacts={"Remediation_Crypto_Hardware_Acceleration_Redesign.md": "content"}
    )
    assert stage5.audit_id == "AUDIT-STAGE5-VERIFY-002"
    assert stage5.verdict == "PASSED_FULL_CERTIFICATION"
    assert len(stage5.revisions) == 3
    assert "ALL MANDATES SATISFIED" in stage5.dossier_markdown


def test_master_dossier_compiler_all_chapters():
    """Validates that MasterDossierCompiler compiles all 9 chapters with full technical depth."""
    compiler = MasterDossierCompiler()
    dossier = compiler.compile_dossier(
        problem_statement="Sovereign AI + 6G Edge Telecommunications + Real-Time Financial Settlement Infrastructure"
    )

    word_count = len(dossier.split())
    assert word_count >= 5000, f"Compiled dossier word count {word_count} < 5000"

    # Validate presence of each chapter title and core technical concepts
    assert "# Chapter 1: Executive Summary, Geopolitical Architecture & Strategic Mandate" in dossier
    assert "RACI Matrix" in dossier
    assert "99.9999%" in dossier

    assert "# Chapter 2: 6G Sub-Terahertz Physical Layer & O-RAN Edge Network Architecture" in dossier
    assert "140.0" in dossier
    assert "Extreme Massive MIMO" in dossier
    assert "O-RAN Split-7.2x" in dossier

    assert "# Chapter 3: Ultra-Low Latency Atomic Financial Settlement Engine" in dossier
    assert "DvP Model 1" in dossier
    assert "Simplex cycle-canceling" in dossier
    assert "ISO 20022" in dossier

    assert "# Chapter 4: Distributed Sovereign Edge AI Inference & Speculative Privacy Fencing" in dossier
    assert "AMD Secure Encrypted Virtualization-Secure Nested Paging" in dossier
    assert "Plonky3" in dossier
    assert "EU Artificial Intelligence Act" in dossier

    assert "# Chapter 5: Adversarial Red-Team Stress-Test & Regulatory Audit Findings" in dossier
    assert "VULN-001-PQC-LATENCY" in dossier
    assert "VULN-002-LIQUIDITY-GRIDLOCK" in dossier
    assert "VULN-003-AI-RESIDENCY-LEAK" in dossier

    assert "# Chapter 6: Upstream Architectural Remediations & Empirical Verification" in dossier
    assert "REV-001-ASIC-NTT" in dossier
    assert "REV-002-DYNAMIC-AMM-LIQUIDITY" in dossier
    assert "REV-003-ENCLAVE-ZK-FENCE" in dossier

    assert "# Chapter 7: Regulatory Compliance, CPMI-IOSCO PFMI Matrix & Legal Governance" in dossier
    assert "CPMI-IOSCO Principles for Financial Market Infrastructures" in dossier
    assert "BCBS 248" in dossier

    assert "# Chapter 8: Quantitative Economic Viability, CAPEX/OPEX & Intraday Liquidity Model" in dossier
    assert "Total Cost of Ownership" in dossier
    assert "$42,500,000" in dossier
    assert "Net Present Value" in dossier

    assert "# Chapter 9: Execution DAG Verification, Rollout Roadmap & Governance Sign-Off" in dossier
    assert "Staged Task Projection" in dossier
    assert "UNANIMOUS FULL PRODUCTION CERTIFICATION" in dossier


def test_dossier_compiler_word_count_enforcement(monkeypatch):
    """Verifies that MasterDossierCompiler enforces the >= 5,000 words threshold."""
    compiler = MasterDossierCompiler()
    # Mock renderers returning small stub to test threshold exception
    def stub_renderer(ctx):
        return "Short chapter text."

    monkeypatch.setattr(
        "orgprompt.challenge.dossier_compiler.render_chapter_1",
        stub_renderer,
    )
    monkeypatch.setattr(
        "orgprompt.challenge.dossier_compiler.render_chapter_2",
        stub_renderer,
    )
    monkeypatch.setattr(
        "orgprompt.challenge.dossier_compiler.render_chapter_3",
        stub_renderer,
    )
    monkeypatch.setattr(
        "orgprompt.challenge.dossier_compiler.render_chapter_4",
        stub_renderer,
    )
    monkeypatch.setattr(
        "orgprompt.challenge.dossier_compiler.render_chapter_5",
        stub_renderer,
    )
    monkeypatch.setattr(
        "orgprompt.challenge.dossier_compiler.render_chapter_6",
        stub_renderer,
    )
    monkeypatch.setattr(
        "orgprompt.challenge.dossier_compiler.render_chapter_7",
        stub_renderer,
    )
    monkeypatch.setattr(
        "orgprompt.challenge.dossier_compiler.render_chapter_8",
        stub_renderer,
    )
    monkeypatch.setattr(
        "orgprompt.challenge.dossier_compiler.render_chapter_9",
        stub_renderer,
    )

    with pytest.raises(DossierCompilationError, match="below required 5,000 words"):
        compiler.compile_dossier("Test short problem")


def test_grand_challenge_runner_filesystem_persistence(tmp_path):
    """Validates that GrandChallengeRunner writes all intermediate artifacts and master dossier to disk."""
    runner = GrandChallengeRunner()
    report = runner.execute(output_dir=str(tmp_path))

    # Verify intermediate files written to tmp_path
    assert (tmp_path / "Sovereign_Infrastructure_Charter_SLA_Hierarchy.md").exists()
    assert (tmp_path / "Regulatory_Compliance_Jurisdictional_Boundary_Map.md").exists()
    assert (tmp_path / "6G_SubTHz_Edge_Topology_URLLC_Numerology_Spec.json").exists()
    assert (tmp_path / "ORAN_DU_Deterministic_MAC_Scheduler_Architecture.md").exists()
    assert (tmp_path / "Atomic_RTGS_DvP_PvP_Settlement_State_Machine.json").exists()
    assert (tmp_path / "Intraday_Liquidity_Optimization_Collateral_Stress_Model.py").exists()
    assert (tmp_path / "Sovereign_Edge_AI_Inference_Pipeline_Spec.md").exists()
    assert (tmp_path / "PostQuantum_HSM_Asynchronous_BFT_Consensus_Spec.json").exists()
    assert (tmp_path / "Unified_EndToEnd_Latency_Capital_Security_Interface_Spec.md").exists()
    assert (tmp_path / "Adversarial_RedTeam_StressTest_Vulnerability_Dossier.md").exists()
    assert (tmp_path / "Remediation_Crypto_Hardware_Acceleration_Redesign.md").exists()
    assert (tmp_path / "Remediation_Dynamic_Liquidity_Backstop_AMM_Vaults.md").exists()
    assert (tmp_path / "Remediation_Enclave_ZK_Data_Fencing.md").exists()
    assert (tmp_path / "Executive_Governance_Signoff_and_Deployment_Certification.md").exists()

    # Verify Master Dossier on disk
    dossier_file = tmp_path / "Master_Grand_Challenge_Solution_Dossier.md"
    assert dossier_file.exists()
    with open(dossier_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert len(content.split()) >= 5000

    # Also verify the primary project artifact was written
    project_root = Path(__file__).resolve().parent.parent
    primary_dossier = project_root / "artifacts" / "grand_challenge_dossier.md"
    assert primary_dossier.exists()
    with open(primary_dossier, "r", encoding="utf-8") as f:
        primary_content = f.read()
    assert len(primary_content.split()) >= 5000


def test_workflow_engine_grand_challenge_integration(tmp_path):
    """Validates that WorkflowEngine.execute_grand_challenge integrates seamlessly with runner."""
    engine = WorkflowEngine()
    result = engine.execute_grand_challenge(output_dir=str(tmp_path))

    assert result.status == "COMPLETED"
    assert len(result.intermediate_artifacts) >= 6
    assert len(result.red_team_findings) == 3
    assert len(result.upstream_revisions) == 3
    assert len(result.solution_dossier.split()) >= 5000
    assert (tmp_path / "Master_Grand_Challenge_Solution_Dossier.md").exists()
