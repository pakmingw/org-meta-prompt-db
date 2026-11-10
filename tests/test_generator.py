"""Unit tests for Dynamic Role Generator utility and invariant compliance."""

import sqlite3
import pytest
import networkx as nx

from orgprompt.graph.engine import KnowledgeGraphEngine
from orgprompt.graph.generator import RoleGenerator, RoleSpecificationError
from orgprompt.models import RoleGenSpec


def test_generate_role_with_inferred_linkages(
    seeded_db: sqlite3.Connection, populated_graph: nx.MultiDiGraph
):
    """Verifies generating a role with minimal inputs correctly infers hierarchy, workflow edges,

    and output artifact while satisfying all invariants.
    """
    initial_roles_count = populated_graph.number_of_nodes()

    spec = RoleGenSpec(
        name="Cryogenic Silicon Photonics Test Engineer",
        org_unit_slug="telecom_bell_labs_physical_research",
        seniority_level="SENIOR_SPECIALIST",
        role_archetype="domain_specialist",
        mission="Execute sub-Kelvin characterization of optical ring resonators and low-noise amplifiers.",
        mental_models=[
            "Thermal Noise (Johnson-Nyquist Limit)",
            "Photon-Phonon Scattering in Waveguides",
        ],
        technical_vocabulary=[
            "Dilution Refrigerator 10mK",
            "Mach-Zehnder Interferometer (MZI)",
            "Fiber-to-Chip Grating Coupler",
        ],
        anti_patterns=[
            "Uncalibrated thermal drift corrupting Q-factor measurements",
            "Neglecting cable thermal anchoring leading to parasitic heat loads",
        ],
        output_artifact_name="Cryogenic Photonic Resonator Q-Factor Benchmark Log",
    )

    new_role = RoleGenerator.generate_role(spec, conn=seeded_db, G=populated_graph)

    # 1. Check returned CanonicalRole attributes
    assert new_role.id == "role_cryogenic_silicon_photonics_test_engineer"
    assert new_role.title == "Cryogenic Silicon Photonics Test Engineer"
    assert new_role.seniority_tier == "SENIOR_SPECIALIST"
    assert new_role.role_archetype == "domain_specialist"
    assert len(new_role.system_prompt) >= 1200
    assert len(new_role.output_artifact_ids) >= 1

    # 2. Check Database Persistence
    db_row = seeded_db.execute(
        "SELECT name, seniority_level, character_count FROM canonical_roles WHERE id = ?",
        (new_role.id,),
    ).fetchone()
    assert db_row is not None
    assert db_row[0] == "Cryogenic Silicon Photonics Test Engineer"
    assert db_row[1] == "SENIOR_SPECIALIST"
    assert db_row[2] >= 1200

    # 3. Check SQLite FTS5 Real-time Sync
    fts_rows = seeded_db.execute(
        "SELECT role_id, name, industry FROM roles_fts WHERE roles_fts MATCH 'cryogenic photonics'"
    ).fetchall()
    assert len(fts_rows) >= 1
    assert any(r[0] == new_role.id for r in fts_rows)

    # 4. Check NetworkX Graph Integration & Invariants
    assert f"role:{new_role.slug}" in populated_graph
    report = KnowledgeGraphEngine.validate_invariants(populated_graph)
    assert report.is_valid is True
    assert report.total_roles == 337
    assert report.violation_count == 0


def test_generate_role_with_explicit_supervisors_and_collaborators(
    seeded_db: sqlite3.Connection, populated_graph: nx.MultiDiGraph
):
    """Verifies generating a role with user-specified supervisor and peer collaborators."""
    spec = RoleGenSpec(
        name="Staff LLM Quantization Engineer",
        org_unit_slug="tech_nvidia_cuda_software",
        seniority_level="PRINCIPAL_STAFF",
        role_archetype="engineering_staff",
        mission="Develop ultra-low-bit FP4 and INT2 quantization algorithms for Blackwell Tensor Cores.",
        mental_models=[
            "Outlier Feature Suppression (SmoothQuant)",
            "Information-Theoretic Quantization Error Bounds",
        ],
        reports_to_role_slug="tech_vp_frontier_ai_research",
        collaborates_with_role_slugs=[
            "tech_chief_cloud_infrastructure_architect",
            "tech_head_of_ai_safety_alignment",
        ],
        output_artifact_name="Blackwell FP4 Kernel Quantization Benchmark Dossier",
    )

    new_role = RoleGenerator.generate_role(spec, conn=seeded_db, G=populated_graph)

    # Verify edge connections in SQLite
    reports_edge = seeded_db.execute(
        """SELECT target_role_id FROM role_edges
           WHERE source_role_id = ? AND edge_type = 'REPORTS_TO'""",
        (new_role.id,),
    ).fetchone()
    assert reports_edge is not None
    assert reports_edge[0] == "role_tech_vp_frontier_ai_research"

    # Verify Graph Invariants
    report = KnowledgeGraphEngine.validate_invariants(populated_graph)
    assert report.is_valid is True
    assert report.total_roles == 337


def test_generate_role_duplicate_slug_raises_error(
    seeded_db: sqlite3.Connection, populated_graph: nx.MultiDiGraph
):
    """Verifies attempting to create a duplicate role raises RoleSpecificationError."""
    spec = RoleGenSpec(
        name="Unique Test Specialist",
        org_unit_slug="telecom_bell_labs_network_algorithms",
        mission="First generation succeeds.",
    )
    RoleGenerator.generate_role(spec, conn=seeded_db, G=populated_graph)

    # Second attempt with same name and slug must raise RoleSpecificationError
    with pytest.raises(RoleSpecificationError, match="already exists"):
        RoleGenerator.generate_role(spec, conn=seeded_db, G=populated_graph)


def test_generate_role_nonexistent_unit_raises_error(
    seeded_db: sqlite3.Connection, populated_graph: nx.MultiDiGraph
):
    """Verifies referencing a completely non-existent org unit raises RoleSpecificationError."""
    spec = RoleGenSpec(
        name="Unicorn Rancher Specialist",
        org_unit_slug="completely_imaginary_nonexistent_department_xyz123",
        mission="Herd mythological beasts.",
    )

    with pytest.raises(RoleSpecificationError, match="does not exist"):
        RoleGenerator.generate_role(spec, conn=seeded_db, G=populated_graph)
