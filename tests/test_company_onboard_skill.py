"""End-to-end integration test of CompanyOnboardingEngine and Antigravity skills.

Verifies onboarding of Stripe (real non-F500 fintech company):
1. Verifies company inserted into SQLite database with employs_role edges.
2. Verifies bespoke roles synthesized with full 7-section prompt, 5 use cases, and 6-agent swarms.
3. Verifies artifacts/company_onboarding/stripe_genai_blueprint.md generated, >= 5,000 characters.
4. Verifies skill reference catalog references/onboarded_companies.md updated in both skill directories.
5. Verifies all 4 graph invariants pass (0 orphan roles, 0 invariant violations).
6. Verifies CLI invocation 'orgprompt company onboard'.
"""

import json
from pathlib import Path
import sqlite3
import pytest
from click.testing import CliRunner

from orgprompt.cli import cli
from orgprompt.db.connection import get_connection, get_default_db_path
from orgprompt.graph.engine import KnowledgeGraphEngine
from orgprompt.graph.invariants import validate_expansion_invariants
from orgprompt.onboarding.engine import CompanyOnboardingEngine


STRIPE_RESEARCH_DOSSIER = {
    "name": "Stripe",
    "ticker": "STRIPE",
    "is_public": False,
    "revenue_billions": 14.0,
    "headquarters": "San Francisco, CA & Dublin, Ireland",
    "macro_industry": "Finance",
    "sub_sector": "Global Payment Processing & Financial Infrastructure",
    "business_model": "MULTI_SIDED_PLATFORM",
    "operating_archetype": "PLATFORM_ECOSYSTEM",
    "challenges": [
        "Minimizing global transaction authorization latency while maximizing payment acceptance rates across multi-card networks",
        "Automating continuous multi-jurisdiction tax, AML, and PSD3 regulatory compliance",
        "Mitigating zero-day adversarial fraud and synthetic identity fraud at microsecond latencies via real-time ML scoring",
        "Guaranteeing zero-downtime API availability and seamless backward compatibility for mission-critical developer infrastructure",
    ],
    "divisions": [
        "Global Payments & Network Engineering",
        "Risk, Fraud & Financial Intelligence",
        "Developer Platform & Core APIs",
        "Billing & Revenue Automation",
        "Treasury & Banking-as-a-Service",
        "Regulatory Compliance & Fiduciary Affairs",
    ],
    "employed_canonical_roles": [
        "fin_chief_investment_officer",
        "fin_aml_sanctions_compliance_director",
        "fin_chief_risk_officer",
        "tech_principal_distributed_training_engineer",
        "cyber_chief_information_security_officer",
    ],
    "bespoke_roles": [
        {
            "name": "Stripe Payments Platform Lead Architect",
            "division": "Global Payments & Network Engineering",
            "seniority": "PRINCIPAL_STAFF",
            "archetype": "engineering_staff",
            "mission": "Direct ultra-low latency card network settlement, high-throughput idempotency, and 99.999% payment infrastructure reliability.",
        },
        {
            "name": "Stripe Radar ML Risk Specialist",
            "division": "Risk, Fraud & Financial Intelligence",
            "seniority": "SENIOR_SPECIALIST",
            "archetype": "domain_specialist",
            "mission": "Develop real-time sub-millisecond fraud scoring models, adversarial anomaly detection, and automated merchant chargeback mitigation.",
        },
    ],
}


@pytest.fixture
def db_conn():
    conn = get_connection(get_default_db_path())
    yield conn


def test_onboard_stripe_end_to_end(db_conn, tmp_path):
    engine = CompanyOnboardingEngine(conn=db_conn)

    # 1. Onboard Stripe
    blueprint_file = Path("artifacts/company_onboarding/stripe_genai_blueprint.md")
    result = engine.onboard_company(
        company_data=STRIPE_RESEARCH_DOSSIER,
        output_blueprint_path=blueprint_file,
        validate_graph=True,
    )

    # Verify OnboardingResult
    assert result.company_name == "Stripe"
    assert result.company_slug == "stripe"
    assert result.rank >= 501
    assert result.employed_roles_count >= 7  # 5 canonical + 2 bespoke
    assert result.bespoke_roles_count == 2
    assert result.is_valid is True
    assert len(result.violations) == 0

    # 2. Verify SQLite DB insertion
    cursor = db_conn.cursor()
    c_row = cursor.execute(
        "SELECT id, slug, name, rank, revenue_billions, macro_industry, business_model, operating_archetype FROM fortune500_companies WHERE slug = 'stripe';"
    ).fetchone()
    assert c_row is not None
    assert c_row[1] == "stripe"
    assert c_row[2] == "Stripe"
    assert c_row[3] >= 501
    assert c_row[4] == 14.0
    assert c_row[6] == "MULTI_SIDED_PLATFORM"
    assert c_row[7] == "PLATFORM_ECOSYSTEM"

    # 3. Verify employs_role edges
    edges = cursor.execute(
        "SELECT er.role_id, er.department, er.priority_tier, r.name FROM employs_role er JOIN canonical_roles r ON er.role_id = r.id WHERE er.company_id = ?;",
        (c_row[0],),
    ).fetchall()
    assert len(edges) >= 7
    role_names = [e[3] for e in edges]
    assert any("Chief Investment Officer" in name for name in role_names)
    assert "Stripe Payments Platform Lead Architect" in role_names
    assert "Stripe Radar ML Risk Specialist" in role_names

    # 4. Verify Bespoke Roles Quality & Invariants
    for b_role in STRIPE_RESEARCH_DOSSIER["bespoke_roles"]:
        r_record = cursor.execute(
            "SELECT id, slug, name, system_prompt, character_count FROM canonical_roles WHERE name = ?;",
            (b_role["name"],),
        ).fetchone()
        assert r_record is not None
        b_id, b_slug, b_name, b_prompt, b_chars = r_record
        assert b_chars >= 3000
        assert "## 1." in b_prompt
        assert "## 7." in b_prompt

        # Check 5 use cases
        ucs = cursor.execute(
            "SELECT COUNT(*) FROM role_use_cases WHERE role_id = ?;", (b_id,)
        ).fetchone()[0]
        assert ucs == 5

        # Check tooling
        tools_cnt = cursor.execute(
            "SELECT COUNT(*) FROM role_tooling WHERE role_id = ?;", (b_id,)
        ).fetchone()[0]
        assert tools_cnt >= 4

        # Check 6 subagents in swarm
        swarms = cursor.execute(
            "SELECT subagent_role, system_prompt, hitl_checkpoint FROM role_subagent_swarms WHERE role_id = ?;",
            (b_id,),
        ).fetchall()
        assert len(swarms) == 6
        swarm_roles = [s[0] for s in swarms]
        assert "CHIEF_OF_STAFF" in swarm_roles
        assert "DOCUMENT_DRAFTER" in swarm_roles
        assert "QUANTITATIVE_MODELER" in swarm_roles
        assert "DECK_PRESENTER" in swarm_roles
        assert "MEETING_GRAPH" in swarm_roles
        assert "QUALITY_CRITIC" in swarm_roles

        # Check GenAI plan
        gplan = cursor.execute(
            "SELECT rag_context_architecture, hitl_guardrails, roi_productivity_impact FROM role_genai_plans WHERE role_id = ?;",
            (b_id,),
        ).fetchone()
        assert gplan is not None

    # 5. Verify Blueprint artifact >= 5,000 characters
    assert blueprint_file.exists()
    blueprint_content = blueprint_file.read_text(encoding="utf-8")
    assert len(blueprint_content) >= 5000
    assert "Enterprise Generative AI Blueprint: Stripe" in blueprint_content
    assert "Word Processor / Docs" in blueprint_content
    assert "Spreadsheet Modeler" in blueprint_content
    assert "Slide Presenter" in blueprint_content
    assert "Meeting Note Taker" in blueprint_content
    assert "Communication Hub" in blueprint_content
    assert "Personal Subagent Swarm Architecture" in blueprint_content
    assert "CHIEF_OF_STAFF" in blueprint_content
    assert "Global Payments & Network Engineering" in blueprint_content

    # 6. Verify skill catalogs updated in both skill locations
    catalog_paths = [
        Path("/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/.agents/skills/org-company-deep-onboard/references/onboarded_companies.md"),
        Path("/home/pakmingw/.gemini/config/skills/org-company-deep-onboard/references/onboarded_companies.md"),
    ]
    for cp in catalog_paths:
        assert cp.exists()
        catalog_text = cp.read_text(encoding="utf-8")
        assert "stripe" in catalog_text
        assert "Stripe" in catalog_text
        assert "$14.00B" in catalog_text

    # 7. Verify all graph invariants pass (0 orphan roles, 0 violations)
    G = KnowledgeGraphEngine.build_from_db(conn=db_conn)
    val_report = validate_expansion_invariants(G)
    assert val_report.is_valid is True, f"Graph invariant violations: {[v.message for v in val_report.violations]}"


def test_cli_company_onboard(tmp_path):
    runner = CliRunner()
    research_file = tmp_path / "stripe_dossier.json"
    research_file.write_text(json.dumps(STRIPE_RESEARCH_DOSSIER), encoding="utf-8")

    bp_out = tmp_path / "stripe_cli_blueprint.md"

    res = runner.invoke(
        cli,
        [
            "company",
            "onboard",
            "Stripe",
            "--research-file",
            str(research_file),
            "--output-blueprint",
            str(bp_out),
            "--json",
        ],
    )
    assert res.exit_code == 0
    data = json.loads(res.output)
    assert data["company_slug"] == "stripe"
    assert data["is_valid"] is True
    assert Path(bp_out).exists()
    assert len(Path(bp_out).read_text(encoding="utf-8")) >= 5000
