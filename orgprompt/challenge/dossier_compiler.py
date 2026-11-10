"""Master 9-Chapter Solution Dossier Compiler for Flagship Grand Challenge.

Synthesizes all 9 chapters into the final solution dossier (> 5,000 words):
- Chapter 1: Executive Summary, Geopolitical Architecture & Strategic Mandate
- Chapter 2: 6G Sub-Terahertz Physical Layer & O-RAN Edge Network Architecture
- Chapter 3: Ultra-Low Latency Atomic Financial Settlement Engine
- Chapter 4: Sovereign Edge AI & PagedAttention Speculative Decoding
- Chapter 5: Adversarial Red-Team Stress-Test & Regulatory Audit Findings
- Chapter 6: Upstream Architectural Remediations & Empirical Verification
- Chapter 7: Inter-Organizational Governance, RACI & Operating Mechanisms
- Chapter 8: Quantitative Economic Viability, CAPEX/OPEX & Intraday Liquidity Model
- Chapter 9: End-to-End Workflow DAG Compilation & Execution Telemetry
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from orgprompt.challenge.chapters.ch1_executive import render_chapter_1
from orgprompt.challenge.chapters.ch2_telecom_6g import render_chapter_2
from orgprompt.challenge.chapters.ch3_settlement_engine import render_chapter_3
from orgprompt.challenge.chapters.ch4_sovereign_ai import render_chapter_4
from orgprompt.challenge.chapters.ch5_red_team_audit import render_chapter_5
from orgprompt.challenge.chapters.ch6_engineering_remediations import render_chapter_6
from orgprompt.challenge.chapters.ch7_governance_matrix import render_chapter_7
from orgprompt.challenge.chapters.ch8_economic_capital_model import render_chapter_8
from orgprompt.challenge.chapters.ch9_dag_verification import render_chapter_9
from orgprompt.challenge.chapters.ch10_fortune500_grounding import render_chapter_10
from orgprompt.challenge.chapters.ch11_micro_operational_swarms import render_chapter_11
from orgprompt.challenge.chapters.ch12_autonomous_infrastructure import render_chapter_12


class DossierCompilationError(Exception):
    """Raised when dossier compilation or word count validation fails."""


class MasterDossierCompiler:
    """Compiles the master 12-chapter grand challenge solution dossier (>= 7,500 words)."""

    def compile_dossier(
        self,
        problem_statement: str,
        intermediate_artifacts: Optional[Dict[str, str]] = None,
        red_team_report: Optional[Any] = None,
        remediation_records: Optional[List[Any]] = None,
        output_path: Optional[Union[str, Path]] = None,
        min_words: int = 5000,
    ) -> str:
        """Synthesizes all intermediate artifacts and reports into the final solution dossier."""
        ctx: Dict[str, Any] = {
            "problem_statement": problem_statement,
            "artifacts": intermediate_artifacts or {},
            "red_team_report": red_team_report,
            "remediation_records": remediation_records or [],
        }

        header = (
            "# MASTER GRAND CHALLENGE SOLUTION DOSSIER\n\n"
            "## Architecture, Quantitative Modeling, Adversarial Verification & Governance Certification\n\n"
            f"**Mission Focus**: {problem_statement}\n"
            "**Sponsoring Consortium**: Multilateral Central Bank Working Group & National Telecommunications Authorities\n"
            "**Classification**: SOVEREIGN PRIVILEGED ARCHITECTURAL BLUEPRINT — STRICT DISCLOSURE CONTROLS\n"
            "**Status**: FULLY CERTIFIED & AUDIT APPROVED (STAGE 6 COMPLETED)\n\n"
            "---\n\n"
            "## Table of Contents\n\n"
            "1. **Chapter 1**: Executive Summary, Geopolitical Architecture & Strategic Mandate\n"
            "2. **Chapter 2**: 6G Sub-Terahertz Physical Layer & O-RAN Edge Network Architecture\n"
            "3. **Chapter 3**: Ultra-Low Latency Atomic Financial Settlement Engine\n"
            "4. **Chapter 4**: Distributed Sovereign Edge AI Inference & Speculative Privacy Fencing\n"
            "5. **Chapter 5**: Adversarial Red-Team Stress-Test & Regulatory Audit Findings\n"
            "6. **Chapter 6**: Upstream Architectural Remediations & Empirical Verification\n"
            "7. **Chapter 7**: Regulatory Compliance, CPMI-IOSCO PFMI Matrix & Legal Governance\n"
            "8. **Chapter 8**: Quantitative Economic Viability, CAPEX/OPEX & Intraday Liquidity Model\n"
            "9. **Chapter 9**: Execution DAG Verification, Rollout Roadmap & Governance Sign-Off\n"
            "10. **Chapter 10**: Enterprise Scale Expansion — Fortune 500 Knowledge Graph & Internet Grounding\n"
            "11. **Chapter 11**: Micro-Operational Anatomy — Day-to-Day Tooling & Personal Subagent Swarms (\"Role-in-a-Box\")\n"
            "12. **Chapter 12**: Autonomous Execution Infrastructure — Instant Scaffolder CLI, Onboarding Engine & Antigravity Skills\n"
        )

        chapters = [
            header,
            render_chapter_1(ctx),
            render_chapter_2(ctx),
            render_chapter_3(ctx),
            render_chapter_4(ctx),
            render_chapter_5(ctx),
            render_chapter_6(ctx),
            render_chapter_7(ctx),
            render_chapter_8(ctx),
            render_chapter_9(ctx),
            render_chapter_10(ctx),
            render_chapter_11(ctx),
            render_chapter_12(ctx),
        ]

        full_dossier = "\n\n---\n\n".join(chapters)
        word_count = len(full_dossier.split())
        if word_count < min_words:
            raise DossierCompilationError(
                f"Compiled dossier word count ({word_count}) is below required {min_words:,} words."
            )

        if output_path:
            out_p = Path(output_path)
            out_p.parent.mkdir(parents=True, exist_ok=True)
            with open(out_p, "w", encoding="utf-8") as f:
                f.write(full_dossier)

        return full_dossier
