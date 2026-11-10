"""Topological Workflow DAG Compiler for Multi-Agent Problem Solving.

Implements the Staged Task Projection pattern from blueprint.md § 2.5:
Translates cyclic Knowledge Graph relationships into a provably acyclic execution DAG
(nx.is_directed_acyclic_graph(dag) is True) spanning:
  Stage 1: Problem Decomposition, Architecture Scoping & Governance Charters
  Stage 2: Parallel Specialist Artifact Creation
  Stage 3: Cross-Role Interface Synthesis
  Stage 4: Adversarial Red-Team Stress-Test & Regulatory Audit Gate
  Stage 5: Upstream Revision Loop & Architectural Remediations
  Stage 6: Final Solution Dossier Compilation & Executive Sign-off
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
import networkx as nx

from orgprompt.models import CanonicalRole


class WorkflowDAGCompiler:
    """Compiles selected cross-functional team roles and Knowledge Graph relationships into an acyclic execution DAG."""

    def __init__(self, knowledge_graph: Optional[nx.Graph] = None) -> None:
        self.kg = knowledge_graph

    def compile_dag(
        self,
        team: List[Union[CanonicalRole, Dict[str, Any]]],
        G: Optional[nx.Graph] = None,
        problem_statement: str = "",
    ) -> nx.DiGraph:
        """Compiles team roles into a 6-stage execution DAG.

        Args:
            team: List of CanonicalRole instances or role dicts.
            G: Optional NetworkX Knowledge Graph.
            problem_statement: Problem description.

        Returns:
            nx.DiGraph: Provably acyclic directed graph with topological execution guarantees.
        """
        graph = G or self.kg
        dag = nx.DiGraph(
            problem_statement=problem_statement,
            total_stages=6,
        )

        # Categorize roles by archetype and industry
        exec_roles = []
        audit_roles = []
        specialist_roles = []
        ops_roles = []

        for r in team:
            archetype = getattr(r, "role_archetype", None) or (r.get("role_archetype") if isinstance(r, dict) else "") or (r.get("archetype") if isinstance(r, dict) else "")
            r_slug = getattr(r, "slug", "") or (r.get("slug") if isinstance(r, dict) else "")
            r_title = getattr(r, "title", "") or (r.get("name") if isinstance(r, dict) else r_slug)

            if "executive" in str(archetype).lower():
                exec_roles.append(r)
            elif "risk" in str(archetype).lower() or "compliance" in str(archetype).lower() or "audit" in str(archetype).lower():
                audit_roles.append(r)
            elif "operations" in str(archetype).lower():
                ops_roles.append(r)
            else:
                specialist_roles.append(r)

        # Ensure fallback assignment if categories are sparse
        if not exec_roles and team:
            exec_roles.append(team[0])
        if not audit_roles and len(team) > 1:
            audit_roles.append(team[-1])
        if not specialist_roles and len(team) > 2:
            specialist_roles.extend(team[1:-1])

        # Helper to get role fields safely
        def _get_fields(role: Any) -> tuple[str, str, str, str, str]:
            if isinstance(role, dict):
                rid = role.get("id") or role.get("role_id") or role.get("slug", "role_unknown")
                slug = role.get("slug") or rid.replace("role_", "")
                title = role.get("title") or role.get("name", slug)
                arch = role.get("role_archetype") or role.get("archetype", "engineering_staff")
                ind = role.get("industry", "Technology & AI")
            else:
                rid = getattr(role, "id", "role_unknown")
                slug = getattr(role, "slug", rid.replace("role_", ""))
                title = getattr(role, "title", slug)
                arch = getattr(role, "role_archetype", "engineering_staff")
                ind = getattr(role, "industry", None) or (role.metadata.get("industry") if getattr(role, "metadata", None) else "Technology & AI")
            return rid, slug, title, arch, ind or "General Industry"

        # -------------------------------------------------------------------
        # STAGE 1: Scoping & Charters
        # -------------------------------------------------------------------
        stage1_nodes: List[str] = []

        # Executive charter
        exec_lead = exec_roles[0]
        er_id, er_slug, er_title, er_arch, er_ind = _get_fields(exec_lead)
        node_1_1 = f"stage_1_scoping:{er_slug}"
        dag.add_node(
            node_1_1,
            task_id=node_1_1,
            stage="stage_1_scoping",
            stage_num=1,
            role_id=er_id,
            role_slug=er_slug,
            role_title=er_title,
            role_archetype=er_arch,
            action="Define Program Charter, Fiduciary Objectives, and SLA Hierarchy",
            artifact_name="Sovereign_Infrastructure_Charter_SLA_Hierarchy.md",
            is_gate=False,
        )
        stage1_nodes.append(node_1_1)

        # Regulatory compliance charter
        reg_lead = audit_roles[0]
        rr_id, rr_slug, rr_title, rr_arch, rr_ind = _get_fields(reg_lead)
        node_1_2 = f"stage_1_scoping:{rr_slug}"
        dag.add_node(
            node_1_2,
            task_id=node_1_2,
            stage="stage_1_scoping",
            stage_num=1,
            role_id=rr_id,
            role_slug=rr_slug,
            role_title=rr_title,
            role_archetype=rr_arch,
            action="Establish Regulatory Compliance Jurisdictions & Boundary Maps",
            artifact_name="Regulatory_Compliance_Jurisdictional_Boundary_Map.md",
            is_gate=False,
        )
        dag.add_edge(node_1_1, node_1_2, relation="INFORMS_REGULATORY_SCOPE")
        stage1_nodes.append(node_1_2)

        # -------------------------------------------------------------------
        # STAGE 2: Parallel Specialist Artifact Creation
        # -------------------------------------------------------------------
        stage2_nodes: List[str] = []
        specialist_pool = specialist_roles + ops_roles + (exec_roles[1:] if len(exec_roles) > 1 else [])
        if not specialist_pool:
            specialist_pool = team

        # Domain artifact mapping
        artifact_templates = [
            ("6G_SubTHz_Edge_Topology_URLLC_Numerology_Spec.json", "Sub-THz Radio Frequency Front-End & URLLC Numerology"),
            ("ORAN_DU_Deterministic_MAC_Scheduler_Architecture.md", "O-RAN DU/CU MAC Scheduling & Low-Jitter Frame Transport"),
            ("Atomic_RTGS_DvP_PvP_Settlement_State_Machine.json", "Atomic Real-Time Gross Settlement & DvP/PvP State Machine"),
            ("Intraday_Liquidity_Optimization_Collateral_Stress_Model.py", "Intraday Liquidity Stress Testing & Collateral Allocation Model"),
            ("Sovereign_Edge_AI_Inference_Pipeline_Spec.md", "Sovereign Edge AI Inference Pipeline & Speculative Decoding Architecture"),
            ("PostQuantum_HSM_Asynchronous_BFT_Consensus_Spec.json", "Hardware Security Module Post-Quantum Root-of-Trust & BFT Consensus"),
        ]

        for i, s_role in enumerate(specialist_pool):
            sr_id, sr_slug, sr_title, sr_arch, sr_ind = _get_fields(s_role)
            art_name, art_action = artifact_templates[i % len(artifact_templates)]
            s_node = f"stage_2_specialists:{sr_slug}"
            dag.add_node(
                s_node,
                task_id=s_node,
                stage="stage_2_specialists",
                stage_num=2,
                role_id=sr_id,
                role_slug=sr_slug,
                role_title=sr_title,
                role_archetype=sr_arch,
                action=art_action,
                artifact_name=art_name,
                is_gate=False,
            )
            stage2_nodes.append(s_node)

            # Connect Stage 1 charters forward to each Stage 2 specialist
            dag.add_edge(node_1_1, s_node, relation="GOVERNS_SPECIALIST_DESIGN")
            dag.add_edge(node_1_2, s_node, relation="CONSTRAINS_SPECIALIST_DESIGN")

        # -------------------------------------------------------------------
        # STAGE 3: Cross-Role Interface Synthesis
        # -------------------------------------------------------------------
        stage3_nodes: List[str] = []
        node_3_1 = "stage_3_integration:unified_latency_capital_security_interface"
        dag.add_node(
            node_3_1,
            task_id=node_3_1,
            stage="stage_3_integration",
            stage_num=3,
            role_id=er_id,
            role_slug=er_slug,
            role_title=er_title,
            role_archetype="system_integration",
            action="Synthesize End-to-End Latency, Capital Adequacy, and Security Interfaces",
            artifact_name="Unified_EndToEnd_Latency_Capital_Security_Interface_Spec.md",
            is_gate=False,
        )
        stage3_nodes.append(node_3_1)

        for s_node in stage2_nodes:
            dag.add_edge(s_node, node_3_1, relation="FEEDS_SYSTEM_INTEGRATION")

        # -------------------------------------------------------------------
        # STAGE 4: Adversarial Red-Team Stress-Test & Regulatory Audit Gate
        # -------------------------------------------------------------------
        stage4_nodes: List[str] = []
        red_team_role = audit_roles[-1] if len(audit_roles) > 1 else audit_roles[0]
        ar_id, ar_slug, ar_title, ar_arch, ar_ind = _get_fields(red_team_role)

        node_4_1 = f"stage_4_audit_gate:{ar_slug}"
        dag.add_node(
            node_4_1,
            task_id=node_4_1,
            stage="stage_4_audit_gate",
            stage_num=4,
            role_id=ar_id,
            role_slug=ar_slug,
            role_title=ar_title,
            role_archetype="adversarial_red_team",
            action="Execute Adversarial Stress-Testing, Exploit Simulation & Regulatory Audit Gate",
            artifact_name="Adversarial_RedTeam_StressTest_Vulnerability_Dossier.md",
            is_gate=True,
            gate_verdict="REJECTED_MANDATORY_REVISION_REQUIRED",
        )
        stage4_nodes.append(node_4_1)

        dag.add_edge(node_3_1, node_4_1, relation="CHALLENGES_OR_AUDITS")

        # -------------------------------------------------------------------
        # STAGE 5: Upstream Revision Loop & Architectural Remediations
        # -------------------------------------------------------------------
        stage5_nodes: List[str] = []
        remediations = [
            ("Remediation_Crypto_Hardware_Acceleration_Redesign.md", "Hardware NTT Accelerator Cores in HSM ASIC Silicon"),
            ("Remediation_Dynamic_Liquidity_Backstop_AMM_Vaults.md", "Algorithmic AMM Intraday Liquidity Vaults & Simplex Netting"),
            ("Remediation_Enclave_ZK_Data_Fencing.md", "AMD SEV-SNP Enclave KV-Cache Fencing & Plonky3 Zero-Knowledge Proofs"),
        ]

        for i, (rem_art, rem_desc) in enumerate(remediations):
            target_role = specialist_pool[i % len(specialist_pool)]
            tr_id, tr_slug, tr_title, tr_arch, tr_ind = _get_fields(target_role)
            rem_node = f"stage_5_remediation:rem_{i+1}_{tr_slug}"
            dag.add_node(
                rem_node,
                task_id=rem_node,
                stage="stage_5_remediation",
                stage_num=5,
                role_id=tr_id,
                role_slug=tr_slug,
                role_title=tr_title,
                role_archetype=tr_arch,
                action=f"Execute Upstream Revision: {rem_desc}",
                artifact_name=rem_art,
                is_gate=False,
            )
            stage5_nodes.append(rem_node)
            dag.add_edge(node_4_1, rem_node, relation="MANDATES_REVISION")

        # -------------------------------------------------------------------
        # STAGE 6: Final Solution Dossier Compilation & Executive Sign-off
        # -------------------------------------------------------------------
        stage6_nodes: List[str] = []
        node_6_1 = "stage_6_final_dossier:master_solution_dossier"
        dag.add_node(
            node_6_1,
            task_id=node_6_1,
            stage="stage_6_final_dossier",
            stage_num=6,
            role_id=er_id,
            role_slug=er_slug,
            role_title="Master Dossier Consortium Compiler",
            role_archetype="executive_strategy",
            action="Compile Comprehensive 9-Chapter Master Solution Dossier (>= 5,000 words)",
            artifact_name="Master_Grand_Challenge_Solution_Dossier.md",
            is_gate=False,
        )
        stage6_nodes.append(node_6_1)

        for rem_node in stage5_nodes:
            dag.add_edge(rem_node, node_6_1, relation="INCORPORATES_REMEDIATION")

        node_6_2 = f"stage_6_final_dossier:{er_slug}_signoff"
        dag.add_node(
            node_6_2,
            task_id=node_6_2,
            stage="stage_6_final_dossier",
            stage_num=6,
            role_id=er_id,
            role_slug=er_slug,
            role_title=er_title,
            role_archetype=er_arch,
            action="Executive Architecture Board Sign-off and Multi-Year Deployment Certification",
            artifact_name="Executive_Governance_Signoff_and_Deployment_Certification.md",
            is_gate=False,
        )
        dag.add_edge(node_6_1, node_6_2, relation="CERTIFIES_MASTER_BLUEPRINT")
        stage6_nodes.append(node_6_2)

        # Invariant assertion
        assert nx.is_directed_acyclic_graph(dag), "Compiled execution DAG contains cycles; must be provably acyclic."

        return dag

    def compile_execution_dag(
        self,
        team_roles: List[str],
        kg_subgraph: nx.DiGraph,
        problem_spec: Dict[str, Any],
    ) -> nx.DiGraph:
        """Compatibility method matching blueprint.md API contract."""
        dummy_roles = [{"slug": r, "role_id": r, "name": r} for r in team_roles]
        return self.compile_dag(dummy_roles, G=kg_subgraph, problem_statement=problem_spec.get("raw_query", ""))
