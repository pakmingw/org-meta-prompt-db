"""Pytest fixtures for orgprompt test suite."""

import sqlite3
import pytest
import networkx as nx

from orgprompt.db.connection import init_db
from orgprompt.db.seed_data import seed_database
from orgprompt.graph.engine import KnowledgeGraphEngine
from orgprompt.prompts.compiler import PromptCompiler


@pytest.fixture
def empty_db() -> sqlite3.Connection:
    """Provides a fresh, unpopulated in-memory SQLite database with schema initialized."""
    conn = init_db(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def db_conn() -> sqlite3.Connection:
    """Provides an initialized in-memory SQLite database connection (alias for empty_db)."""
    conn = init_db(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def seeded_db() -> sqlite3.Connection:
    """Provides a fully populated in-memory SQLite database with 16 industries, 48 orgs,

    120 units, and 336 canonical roles.
    """
    conn = seed_database(":memory:")
    yield conn
    conn.close()


@pytest.fixture
def populated_graph(seeded_db: sqlite3.Connection) -> nx.MultiDiGraph:
    """Provides a fully hydrated NetworkX Knowledge Graph from the seeded database."""
    return KnowledgeGraphEngine.build_from_db(conn=seeded_db)


@pytest.fixture
def sample_valid_prompt() -> str:
    """Returns a valid 6-section compiled domain prompt meeting all quality invariants."""
    return PromptCompiler.compile({
        "title": "Principal Photonic Systems Architect",
        "seniority_tier": "PRINCIPAL_STAFF",
        "role_archetype": "engineering_staff",
        "exemplar": "Bell Labs",
        "unit": "Physical Sciences Research Lab",
        "mission": "Lead ultra-low-noise coherent optical link architecture and Shannon limit testing.",
        "exemplar_lineage": "Bell Labs Shannon Research Fellow, Optical Transmission Systems Division.",
        "mental_models": [
            "Shannon Channel Capacity Theorem",
            "Kerr Optical Non-Linearity Limit",
            "Quantum Efficiency and Shot Noise Limit",
        ],
        "heuristics": [
            "Maintain OSNR margins exceeding 6dB above FEC threshold under all thermal conditions.",
            "Eliminate polarization mode dispersion prior to coherent detection.",
        ],
        "vocabulary": [
            "DWDM 800Gbps C-Band",
            "Erbium-Doped Fiber Amplifier (EDFA)",
            "QAM-64 Constellation Shaping",
        ],
        "anti_patterns": [
            "Overdriving amplifier stages into non-linear four-wave mixing.",
            "Omitting chromatic dispersion compensation across multi-span links.",
        ],
        "output_artifact": "Coherent_Optical_Link_Budget_Specification",
        "input_artifact": "Transoceanic_Fiber_Attenuation_Survey",
        "edges": {
            "REPORTS_TO": ["telecom_chief_network_architect"],
            "COLLABORATES_WITH": ["telecom_fiber_cable_plant_engineer"],
            "HANDS_OFF_TO": ["telecom_carrier_grade_sre"],
            "REVIEWS_AND_GATES": ["telecom_latency_profiling_specialist"],
        },
    })


@pytest.fixture
def sample_graph() -> nx.MultiDiGraph:
    """Provides a minimal valid sample graph satisfying all 4 structural invariants."""
    G = nx.MultiDiGraph()
    G.add_node("ind:telecom", type="Industry", label="Telecommunications")
    G.add_node("org:bell_labs", type="ExemplarOrg", label="Bell Labs", industry_id="ind:telecom")
    G.add_node("unit:bell_labs_rf_lab", type="OrgUnit", label="Bell Labs RF Lab", org_id="org:bell_labs")

    roles = [
        ("role:chief_rf_architect", "Chief RF Architect", "C_SUITE"),
        ("role:staff_oran_engineer", "Staff O-RAN Engineer", "PRINCIPAL_STAFF"),
        ("role:lead_security_auditor", "Lead Security Auditor", "LEAD_AUDITOR"),
    ]
    for r_id, r_label, sen in roles:
        G.add_node(r_id, type="CanonicalRole", label=r_label, seniority=sen, archetype="engineering_staff")
        G.add_edge(r_id, "unit:bell_labs_rf_lab", key="BELONGS_TO", type="BELONGS_TO")

    # Artifacts
    G.add_node("art:rf_spec", type="Artifact", label="RF Spec")
    G.add_node("art:oran_spec", type="Artifact", label="O-RAN Spec")
    G.add_node("art:audit_spec", type="Artifact", label="Audit Spec")

    G.add_edge("role:chief_rf_architect", "art:rf_spec", key="PRODUCES", type="PRODUCES")
    G.add_edge("role:staff_oran_engineer", "art:oran_spec", key="PRODUCES", type="PRODUCES")
    G.add_edge("role:lead_security_auditor", "art:audit_spec", key="PRODUCES", type="PRODUCES")

    # Reports to
    G.add_edge("role:staff_oran_engineer", "role:chief_rf_architect", key="REPORTS_TO", type="REPORTS_TO")
    G.add_edge("role:lead_security_auditor", "role:chief_rf_architect", key="REPORTS_TO", type="REPORTS_TO")

    # Workflow edges
    G.add_edge("role:chief_rf_architect", "role:staff_oran_engineer", key="COLLABORATES_WITH", type="COLLABORATES_WITH")
    G.add_edge("role:chief_rf_architect", "role:lead_security_auditor", key="REVIEWS_AND_GATES", type="REVIEWS_AND_GATES")
    G.add_edge("role:staff_oran_engineer", "role:lead_security_auditor", key="HANDS_OFF_TO", type="HANDS_OFF_TO")
    G.add_edge("role:lead_security_auditor", "role:staff_oran_engineer", key="CHALLENGES_OR_AUDITS", type="CHALLENGES_OR_AUDITS")

    return G


@pytest.fixture
def benchmark_queries_25() -> list[dict]:
    """Provides 25 benchmark queries across all 16 macro industries for retrieval evaluation."""
    return [
        {
            "query": "Shannon capacity optical link budget O-RAN beamforming",
            "ground_truth": ["telecom_chief_network_architect", "telecom_principal_ran_systems_engineer"]
        },
        {
            "query": "Sub-millisecond low-latency FPGA high-frequency market making",
            "ground_truth": ["fin_principal_fpga_trading_architect", "fin_chief_investment_officer"]
        },
        {
            "query": "Distributed foundation model pretraining NCCL GPU cluster orchestration",
            "ground_truth": ["tech_chief_cloud_infrastructure_architect", "tech_principal_distributed_training_engineer"]
        },
        {
            "query": "Pixar Braintrust story development CGI animation pipeline",
            "ground_truth": ["media_head_of_story_editorial", "media_lead_character_animator"]
        },
        {
            "query": "Translational clinical oncology genomic sequencing pathology",
            "ground_truth": ["health_chief_medical_officer", "health_director_precision_medicine"]
        },
        {
            "query": "EUV photolithography wafer fabrication pellicle alignment 2nm",
            "ground_truth": ["semi_vp_euv_systems_engineering", "semi_optical_mirror_interferometry_specialist"]
        },
        {
            "query": "Starship methalox full-flow staged combustion Raptor engine trajectory",
            "ground_truth": ["aero_lead_propulsion_systems_director", "aero_chief_engineer_starship"]
        },
        {
            "query": "High-voltage direct current HVDC battery storage BESS dispatch Autobidder",
            "ground_truth": ["energy_chief_transmission_officer", "energy_principal_battery_storage_algorithm_engineer"]
        },
        {
            "query": "Working backwards PR/FAQ robotic fulfillment warehouse sortation",
            "ground_truth": ["retail_vp_global_fulfillment_technology", "retail_principal_kiva_robotics_controls_engineer"]
        },
        {
            "query": "Container vessel stowage marine safety demurrage automated customs clearance",
            "ground_truth": ["logistics_chief_marine_operations_officer", "logistics_master_vessel_stowage_planner"]
        },
        {
            "query": "National digital identity citizen authentication civil aviation safety Part 25",
            "ground_truth": ["gov_chief_digital_technology_officer", "gov_faa_associate_administrator_safety"]
        },
        {
            "query": "Pyramid Principle MECE executive strategy believability-weighted decision",
            "ground_truth": ["consult_senior_partner_managing_director", "consult_chief_systematic_macro_strategist"]
        },
        {
            "query": "Large Hadron Collider ATLAS detector double-blind discovery Heilmeier catechism",
            "ground_truth": ["research_director_general_cern", "research_darpa_director"]
        },
        {
            "query": "mRNA lipid nanoparticle formulation cGMP sterile fill finish vaccine",
            "ground_truth": ["pharma_chief_scientific_officer", "pharma_principal_lipid_nanoparticle_formulator"]
        },
        {
            "query": "Zero Trust Architecture Falcon threat hunting 1-10-60 adversarial red team",
            "ground_truth": ["cyber_nsa_director_cybersecurity", "cyber_vp_overwatch_threat_hunting"]
        },
        {
            "query": "Level-4 autonomous driving simulation corner cases model predictive control",
            "ground_truth": ["robotics_chief_safety_officer_waymo", "robotics_principal_simulation_fuzzing_engineer"]
        },
        {
            "query": "Basel III IV fundamental review trading book expected shortfall capital",
            "ground_truth": ["fin_frtb_capital_adequacy_lead", "fin_chief_investment_officer"]
        },
        {
            "query": "Subsea transoceanic fiber landing station optical attenuation",
            "ground_truth": ["telecom_vp_global_infrastructure", "telecom_subsea_optical_director"]
        },
        {
            "query": "Extreme ultraviolet Zeiss mirror micromirror interferometer metrology",
            "ground_truth": ["semi_vp_euv_systems_engineering"]
        },
        {
            "query": "NERC CIP high impact bulk electric system cyber perimeter defense",
            "ground_truth": ["energy_nerc_cip_grid_cybersecurity_auditor"]
        },
        {
            "query": "RTCA DO-178C DAL A avionics flight control certification",
            "ground_truth": ["aero_do178c_do254_avionics_auditor", "gov_faa_associate_administrator_safety"]
        },
        {
            "query": "Toyota Production System Andon cord Kaizen continuous improvement",
            "ground_truth": ["semi_andon_cord_quality_assurance_lead"]
        },
        {
            "query": "FDA 21 CFR Part 11 electronic records clinical trial protocol",
            "ground_truth": ["pharma_fda_21cfr_part11_data_integrity_auditor"]
        },
        {
            "query": "Kubernetes Borg cluster scheduler fault tolerance eBPF networking",
            "ground_truth": ["tech_chief_cloud_infrastructure_architect"]
        },
        {
            "query": "Autonomous humanoid dynamic locomotion torque control Boston Dynamics",
            "ground_truth": ["robotics_principal_mpc_locomotion_architect"]
        }
    ]


@pytest.fixture(autouse=True)
def cleanup_disk_db():
    """Cleans up any dynamically created test roles and artifacts from the disk database."""
    from orgprompt.db.connection import get_default_db_path, get_connection
    db_path = get_default_db_path()

    def do_cleanup():
        if db_path.exists():
            try:
                conn = get_connection(db_path, enable_foreign_keys=True)
                with conn:
                    # Clean up test roles
                    conn.execute("DELETE FROM canonical_roles WHERE slug IN ('bio_quantum_simulation_specialist', 'quantum_metrology_specialist', 'failing_role', 'adversarial_staff_penetration_tester')")
                    conn.execute("DELETE FROM canonical_roles WHERE slug LIKE 'test_%'")
                    conn.execute("DELETE FROM canonical_roles WHERE slug LIKE 'adversarial_verification_%'")
                    conn.execute("DELETE FROM canonical_roles WHERE slug LIKE 'temp_%'")
                    conn.execute("DELETE FROM canonical_roles WHERE slug LIKE 'stripe_%'")
                    # Clean up test companies and related expansion records
                    conn.execute("DELETE FROM role_subagent_swarms WHERE role_id LIKE 'role_stripe_%'")
                    conn.execute("DELETE FROM role_genai_plans WHERE role_id LIKE 'role_stripe_%'")
                    conn.execute("DELETE FROM role_tooling WHERE role_id LIKE 'role_stripe_%'")
                    conn.execute("DELETE FROM role_use_cases WHERE role_id LIKE 'role_stripe_%'")
                    conn.execute("DELETE FROM employs_role WHERE company_id IN (SELECT id FROM fortune500_companies WHERE rank >= 501 OR slug = 'stripe')")
                    conn.execute("DELETE FROM fortune500_companies WHERE rank >= 501 OR slug = 'stripe'")
                    # Clean up test artifacts matching test slugs or orphaned
                    conn.execute("""
                        DELETE FROM artifacts
                        WHERE slug LIKE '%bio_quantum%'
                           OR slug LIKE '%quantum_metrology%'
                           OR slug LIKE '%failing_role%'
                           OR slug LIKE 'adversarial_verification_%'
                           OR id NOT IN (SELECT artifact_id FROM role_artifacts)
                    """)
                    # Clean up any orphaned role_edges, role_artifacts, or employs_role if present
                    conn.execute("DELETE FROM role_edges WHERE source_role_id NOT IN (SELECT id FROM canonical_roles) OR target_role_id NOT IN (SELECT id FROM canonical_roles)")
                    conn.execute("DELETE FROM role_artifacts WHERE role_id NOT IN (SELECT id FROM canonical_roles)")
                    conn.execute("DELETE FROM employs_role WHERE role_id NOT IN (SELECT id FROM canonical_roles)")
                    conn.execute("DELETE FROM employs_role WHERE company_id NOT IN (SELECT id FROM fortune500_companies)")
                conn.close()
            except Exception:
                pass

    do_cleanup()
    yield
    do_cleanup()
