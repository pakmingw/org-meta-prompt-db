"""Comprehensive test suite for Fortune 500 Encyclopedia & Internet Comparisons (Exp-M1B)."""

import json
import re
from pathlib import Path
import pytest

from orgprompt.db.connection import get_connection, get_default_db_path
from orgprompt.db.seed_encyclopedia import seed_encyclopedia


@pytest.fixture(scope="module")
def encyclopedia_db():
    """Ensures database is seeded with encyclopedia comparisons and returns active connection."""
    conn = get_connection()
    # Ensure encyclopedia has been populated
    seed_encyclopedia(db_path=get_default_db_path())
    yield conn
    conn.close()


def test_encyclopedia_table_row_count(encyclopedia_db):
    """Verifies exactly 500 rows in company_internet_comparisons."""
    cur = encyclopedia_db.cursor()
    count = cur.execute("SELECT COUNT(*) FROM company_internet_comparisons").fetchone()[0]
    assert count == 500, f"Expected exactly 500 rows in company_internet_comparisons, got {count}"


def test_encyclopedia_ranks_contiguity(encyclopedia_db):
    """Verifies ranks 1..500 are contiguous without gaps."""
    cur = encyclopedia_db.cursor()
    ranks = [r[0] for r in cur.execute("SELECT f500_rank FROM company_internet_comparisons ORDER BY f500_rank ASC").fetchall()]
    assert ranks == list(range(1, 501)), "f500_rank must be strictly contiguous from 1 to 500"


def test_encyclopedia_referential_integrity(encyclopedia_db):
    """Verifies all company_id references exist in fortune500_companies."""
    cur = encyclopedia_db.cursor()
    orphans = cur.execute("""
        SELECT cic.company_id FROM company_internet_comparisons cic
        LEFT JOIN fortune500_companies f500 ON cic.company_id = f500.id
        WHERE f500.id IS NULL
    """).fetchall()
    assert len(orphans) == 0, f"Found orphan company_id entries: {orphans}"


def test_encyclopedia_no_null_or_empty_columns(encyclopedia_db):
    """Verifies zero nulls, empty strings, or empty lists across all columns."""
    cur = encyclopedia_db.cursor()
    rows = cur.execute("""
        SELECT id, company_id, f500_rank, company_name, internet_divisions_json,
               internet_bespoke_roles_json, db_mapped_roles_count, alignment_score,
               delta_analysis_md, tailored_swarm_recommendation_md
        FROM company_internet_comparisons
    """).fetchall()

    assert len(rows) == 500
    for r in rows:
        cid, comp_id, rank, name, divs_json, bespoke_json, roles_cnt, score, delta_md, swarm_md = r
        assert cid and cid.startswith("cic_f500_")
        assert comp_id and comp_id.startswith("f500_")
        assert 1 <= rank <= 500
        assert name and len(name) > 1

        # Check JSON parsing
        divs = json.loads(divs_json)
        assert isinstance(divs, list) and len(divs) >= 2, f"Company {name} has invalid divisions"

        bespoke = json.loads(bespoke_json)
        assert isinstance(bespoke, list) and len(bespoke) >= 4, f"Company {name} has < 4 bespoke roles"

        assert roles_cnt >= 20, f"Company {name} has unexpectedly low mapped roles: {roles_cnt}"
        assert 0.70 <= score <= 1.0, f"Company {name} alignment score {score} out of bounds"
        assert len(delta_md.strip()) >= 200, f"Company {name} delta_analysis_md is too short"
        assert len(swarm_md.strip()) >= 300, f"Company {name} tailored_swarm_recommendation_md is too short"


def test_encyclopedia_alignment_scores(encyclopedia_db):
    """Verifies alignment score bounds and average >= 0.75."""
    cur = encyclopedia_db.cursor()
    avg_score, min_score, max_score = cur.execute(
        "SELECT AVG(alignment_score), MIN(alignment_score), MAX(alignment_score) FROM company_internet_comparisons"
    ).fetchone()

    assert avg_score >= 0.75, f"Average alignment score {avg_score} must be >= 0.75"
    assert min_score >= 0.78, f"Minimum alignment score {min_score} must be >= 0.78"
    assert max_score <= 0.94, f"Maximum alignment score {max_score} must be <= 0.94"


def test_encyclopedia_marquee_companies(encyclopedia_db):
    """Verifies marquee enterprise 10-K divisions are accurately reflected."""
    cur = encyclopedia_db.cursor()
    c1 = cur.execute("SELECT internet_divisions_json FROM company_internet_comparisons WHERE f500_rank = 1").fetchone()
    walmart_divs = json.loads(c1[0])
    assert "Walmart U.S." in walmart_divs
    assert "Sam's Club" in walmart_divs

    c2 = cur.execute("SELECT internet_divisions_json FROM company_internet_comparisons WHERE f500_rank = 2").fetchone()
    amazon_divs = json.loads(c2[0])
    assert "Amazon Web Services (AWS)" in amazon_divs


def test_encyclopedia_volumes_exist_and_size():
    """Verifies all 5 volume files exist, each >= 50,000 characters and contain 100 companies."""
    proj_root = Path(__file__).resolve().parent.parent
    art_dir = proj_root / "artifacts" / "fortune500_encyclopedia"
    assert art_dir.is_dir(), f"Directory {art_dir} does not exist"

    volume_specs = [
        (1, 1, 100),
        (2, 101, 200),
        (3, 201, 300),
        (4, 301, 400),
        (5, 401, 500),
    ]

    for vol_num, start_rank, end_rank in volume_specs:
        vol_file = art_dir / f"volume_{vol_num}_ranks_{start_rank}_{end_rank}.md"
        assert vol_file.is_file(), f"Volume file {vol_file.name} missing"

        content = vol_file.read_text(encoding="utf-8")
        assert len(content) >= 50000, f"{vol_file.name} length {len(content)} is less than 50,000 characters"

        # Check all 100 companies present in volume
        ranks_in_vol = [int(m) for m in re.findall(r"## Rank #(\d+):", content)]
        assert len(ranks_in_vol) == 100, f"{vol_file.name} has {len(ranks_in_vol)} companies, expected 100"
        assert ranks_in_vol == list(range(start_rank, end_rank + 1)), f"{vol_file.name} ranks mismatch"

        # Check section formatting
        assert "### A. Internet-Verified Operating Model & Divisional Architecture" in content
        assert "### B. Real-World Key Roles & Job Architecture (Internet Ground Truth)" in content
        assert "### C. Side-by-Side Comparison: Internet Ground Truth vs. org_knowledge_base.db" in content
        assert "Tailored Personal Subagent Swarm Recommendation" in content


def test_encyclopedia_seeder_idempotency(encyclopedia_db):
    """Verifies seed_encyclopedia is fully idempotent and maintains exact invariants."""
    res = seed_encyclopedia()
    assert res["companies_seeded"] == 500
    assert res["volumes_written"] == 5

    cur = encyclopedia_db.cursor()
    cnt = cur.execute("SELECT COUNT(*) FROM company_internet_comparisons").fetchone()[0]
    assert cnt == 500
