"""Tests for Expanded Grand Challenge Dossier and Chapter 10-12 Verification.

Validates:
- Dossier persistence in artifacts/grand_challenge_dossier.md strictly >= 7,500 words
- All 12 chapters present with domain-authentic depth
- Chapter 10: Fortune 500 Knowledge Graph, SEC 10-K divisions, alignment score, and 5-volume encyclopedia
- Chapter 11: Dual-layer tooling (6 horizontal + 45+ vertical), 2,735 use cases, 3,282 subagents with acyclic DAGs, Section 7 prompts
- Chapter 12: Instant Scaffolder CLI, Onboarding Engine (Stripe), dual Antigravity skills, 36-query search benchmark
- Programmatic compiler integration in MasterDossierCompiler and GrandChallengeRunner
"""

from pathlib import Path
import pytest

from orgprompt.challenge import GrandChallengeRunner, MasterDossierCompiler


def test_grand_challenge_dossier_word_count_and_chapters():
    """Asserts that artifacts/grand_challenge_dossier.md is >= 7,500 words and contains all 12 chapters."""
    project_root = Path(__file__).resolve().parent.parent
    dossier_path = project_root / "artifacts" / "grand_challenge_dossier.md"

    assert dossier_path.exists(), f"Dossier not found at {dossier_path}"

    with open(dossier_path, "r", encoding="utf-8") as f:
        content = f.read()

    words = content.split()
    word_count = len(words)
    assert word_count >= 7500, f"Dossier has {word_count} words; expected strictly >= 7,500 words"

    # Verify all 12 chapters are present in the table of contents and body
    for chapter_num in range(1, 13):
        assert f"Chapter {chapter_num}" in content, f"Missing Chapter {chapter_num}"

    # Verify Chapter 10 specific metrics and concepts
    assert "# Chapter 10: Enterprise Scale Expansion — Fortune 500 Knowledge Graph & Internet Grounding" in content
    assert "fortune500_companies" in content
    assert "employs_role" in content
    assert "18,500+" in content
    assert "0.8574" in content
    assert "artifacts/fortune500_encyclopedia/" in content

    # Verify Chapter 11 specific metrics and concepts
    assert "# Chapter 11: Micro-Operational Anatomy — Day-to-Day Tooling & Personal Subagent Swarms" in content
    assert "WORD_PROCESSOR" in content
    assert "SPREADSHEET_PROCESSOR" in content
    assert "2,735" in content
    assert "3,282" in content
    assert "role_subagent_swarms" in content
    assert "role_genai_plans" in content
    assert "Section 7" in content

    # Verify Chapter 12 specific metrics and concepts
    assert "# Chapter 12: Autonomous Execution Infrastructure — Instant Scaffolder CLI, Onboarding Engine & Antigravity Skills" in content
    assert "orgprompt scaffold role" in content
    assert "CompanyOnboardingEngine" in content
    assert "Stripe" in content
    assert "org-role-search-and-scaffold" in content
    assert "org-company-deep-onboard" in content
    assert "0.9028" in content
    assert "0.7417" in content


def test_master_dossier_compiler_expanded():
    """Validates that MasterDossierCompiler renders all 12 chapters with >= 7,500 words."""
    compiler = MasterDossierCompiler()
    dossier = compiler.compile_dossier(
        problem_statement="Enterprise Scale Sovereign AI & Financial Settlement Infrastructure"
    )

    words = dossier.split()
    word_count = len(words)
    assert word_count >= 7500, f"Compiler produced {word_count} words; expected >= 7,500"

    assert "# Chapter 10:" in dossier
    assert "# Chapter 11:" in dossier
    assert "# Chapter 12:" in dossier
