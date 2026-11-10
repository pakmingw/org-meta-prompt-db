"""Modular Chapters for Grand Challenge Master Solution Dossier.

Contains 9 modular chapters, each providing deep, authentic domain specifications,
radio link budgets, atomic settlement state machines, cryptographic formulas,
remediation benchmarks, regulatory matrices, and economic models.
"""

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

ALL_CHAPTER_RENDERERS = [
    render_chapter_1,
    render_chapter_2,
    render_chapter_3,
    render_chapter_4,
    render_chapter_5,
    render_chapter_6,
    render_chapter_7,
    render_chapter_8,
    render_chapter_9,
    render_chapter_10,
    render_chapter_11,
    render_chapter_12,
]

__all__ = [
    "render_chapter_1",
    "render_chapter_2",
    "render_chapter_3",
    "render_chapter_4",
    "render_chapter_5",
    "render_chapter_6",
    "render_chapter_7",
    "render_chapter_8",
    "render_chapter_9",
    "render_chapter_10",
    "render_chapter_11",
    "render_chapter_12",
    "ALL_CHAPTER_RENDERERS",
]
