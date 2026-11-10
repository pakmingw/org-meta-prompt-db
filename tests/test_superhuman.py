"""Comprehensive Phase 12 test suite for `orgprompt.superhuman` & `org-superhuman-role-synthesizer`."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from click.testing import CliRunner

from orgprompt.cli import cli
from orgprompt.db.connection import get_connection, get_default_db_path
from orgprompt.superhuman import SuperhumanRolePackage, SuperhumanRoleSynthesizer

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKSPACE_SKILL_DIR = REPO_ROOT / ".agents" / "skills" / "org-superhuman-role-synthesizer"
GLOBAL_SKILL_DIR = Path("/home/pakmingw/.gemini/config/skills/org-superhuman-role-synthesizer")


@pytest.fixture(scope="module")
def shared_synthesizer():
    syn = SuperhumanRoleSynthesizer.build_from_db()
    yield syn
    if hasattr(syn, "close"):
        syn.close()


@pytest.fixture(scope="module")
def discovery_pkg(shared_synthesizer) -> SuperhumanRolePackage:
    return shared_synthesizer.synthesize(
        problem="Mitigate subsea coherent optical transceiver Kerr phase noise and BGP route flap cascades",
        company="Orange France",
        adjacent_k=5,
    )


@pytest.fixture
def isolated_db_path(tmp_path: Path) -> Path:
    dst = tmp_path / "isolated_org_kb.db"
    shutil.copy2(get_default_db_path(), dst)
    return dst


def test_01_problem_discovery_mode(discovery_pkg: SuperhumanRolePackage):
    assert discovery_pkg.input_mode == "problem_discovery"
    assert discovery_pkg.mapped_okg_anchor_role_id is not None
    assert discovery_pkg.company_context == "Orange France"
    assert len(discovery_pkg.enterprise_team_roles) >= 2
    assert len(discovery_pkg.use_cases) >= 4
    assert len(discovery_pkg.tools) >= 4
    assert len(discovery_pkg.subagent_swarm) == 6


def test_02_canonical_role_expansion_mode(shared_synthesizer):
    pkg = shared_synthesizer.synthesize(
        role="tech_principal_distributed_training_engineer",
        problem="Eliminate all-reduce straggler stalls across 16,384 GPU RoCEv2 clusters",
        adjacent_k=5,
    )
    assert pkg.input_mode == "canonical_role"
    assert pkg.primary_role["slug"] == "tech_principal_distributed_training_engineer"
    assert pkg.mapped_okg_anchor_role_id == "role_tech_principal_distributed_training_engineer"
    assert pkg.prompt_character_count >= 6000


def test_03_custom_agent_role_via_dict(shared_synthesizer):
    custom_dict = {
        "name": "Principal Cryogenic Quantum Interconnect Architect",
        "mission": "Engineer low-loss millikelvin superconducting microwave interconnects across dilution refrigerators.",
        "capabilities": ["Superconducting resonator design", "Cryogenic thermal budget modeling"],
        "mental_models": ["Lindblad master equation decoherence", "Microwave S-parameter impedance matching"],
    }
    pkg = shared_synthesizer.synthesize(
        custom_role_spec=custom_dict,
        problem="Suppress quasiparticle poisoning across modular superconducting qubit links",
    )
    assert pkg.input_mode == "custom_agent_role"
    assert "Cryogenic Quantum Interconnect" in pkg.title or "Cryogenic Quantum Interconnect" in pkg.primary_role.get("name", "")
    assert pkg.mapped_okg_anchor_role_id is not None
    assert len(pkg.adjacent_roles) >= 3


def test_04_custom_agent_role_via_json_file(shared_synthesizer, tmp_path: Path):
    role_file = tmp_path / "external_agent_role.json"
    role_file.write_text(
        json.dumps(
            {
                "title": "Autonomous Post-Quantum Lattice Cryptography Verifier",
                "system_prompt": "Formally verify constant-time ML-KEM / Kyber hardware polynomial multipliers against power side-channels.",
                "technical_vocabulary": ["ML-KEM", "NTT butterfly", "TVLA side-channel leakage"],
            }
        ),
        encoding="utf-8",
    )
    pkg = shared_synthesizer.synthesize(
        custom_role_spec=role_file,
        problem="Prove zero timing and power side-channel leakage in masked lattice NTT microcode",
    )
    assert pkg.input_mode == "custom_agent_role"
    assert pkg.mapped_okg_anchor_role_id is not None
    assert pkg.prompt_character_count >= 6000


def test_05_custom_agent_role_via_raw_string(shared_synthesizer):
    raw_role = (
        "Chief Hypersonic Thermal Protection Ablation Modeler: model aerothermal shock-layer "
        "radiative heating and carbon-phenolic pyrolysis during atmospheric reentry."
    )
    pkg = shared_synthesizer.synthesize(
        custom_role=raw_role,
        problem="Bound recession uncertainty during Mach 25 skip-entry plasma blackout",
    )
    assert pkg.input_mode == "custom_agent_role"
    assert pkg.mapped_okg_anchor_role_id is not None
    assert len(pkg.deep_superhuman_prompt) >= 6000


def test_06_org_graph_adjacency_fusion(discovery_pkg: SuperhumanRolePackage):
    valid_edges = {
        "COLLABORATES_WITH",
        "HANDS_OFF_TO",
        "REVIEWS_AND_GATES",
        "CHALLENGES_OR_AUDITS",
        "REPORTS_TO",
    }
    assert len(discovery_pkg.adjacent_roles) >= 3
    seen_edges = {adj.edge_type for adj in discovery_pkg.adjacent_roles}
    assert seen_edges.issubset(valid_edges)
    assert len(seen_edges) >= 2
    for adj in discovery_pkg.adjacent_roles:
        assert adj.blind_spot_eliminated and len(adj.blind_spot_eliminated) > 20
        assert len(adj.absorbed_capabilities) >= 1
        assert len(adj.absorbed_heuristics) >= 1


def test_07_academic_foundation_rigor(discovery_pkg: SuperhumanRolePackage):
    acad = discovery_pkg.academic_foundation
    assert len(acad.degrees) >= 2
    assert len(acad.foundational_coursework_and_axioms) >= 3
    assert len(acad.seminal_literature_and_standards) >= 3
    assert len(acad.doctoral_thesis_and_lab_methodology) > 40
    assert len(acad.cross_disciplinary_minors) >= 2


def test_08_on_the_job_crucibles_and_scar_tissue(discovery_pkg: SuperhumanRolePackage):
    crucibles = discovery_pkg.on_the_job_crucibles
    assert len(crucibles.career_trajectory) >= 3
    assert len(crucibles.cross_functional_tours_of_duty) >= 3
    assert len(crucibles.mentorship_and_review_rituals) >= 2
    assert len(crucibles.crucible_episodes) >= 4
    for ep in crucibles.crucible_episodes:
        assert ep.title and len(ep.title) > 5
        assert len(ep.failure_mode_and_broken_assumption) > 25
        assert len(ep.recovery_and_forensic_action) > 25
        assert len(ep.tacit_scar_tissue_lesson) > 25


def test_09_human_characteristics_depth(discovery_pkg: SuperhumanRolePackage):
    hc = discovery_pkg.human_characteristics
    assert len(hc.cognitive_architecture) >= 3
    assert len(hc.epistemic_calibration) > 30
    assert len(hc.bias_and_mediocrity_resistances) >= 3
    assert len(hc.aesthetic_and_ownership_traits) >= 3
    assert len(hc.socio_technical_temperament) > 30


def test_10_unknown_problem_epistemology_five_stages(discovery_pkg: SuperhumanRolePackage):
    epist = discovery_pkg.unknown_problem_epistemology
    stages = epist.stages
    assert len(stages) == 5
    assert [s.stage_number for s in stages] == [1, 2, 3, 4, 5]
    for stg in stages:
        assert stg.name and stg.objective
        assert len(stg.triggers_or_axioms) >= 2
        assert len(stg.concrete_actions) >= 2
        assert len(stg.verification_gate) > 15


def test_11_deep_superhuman_prompt_completeness(discovery_pkg: SuperhumanRolePackage):
    prompt = discovery_pkg.deep_superhuman_prompt
    assert len(prompt) >= 6000
    assert discovery_pkg.prompt_character_count == len(prompt)
    for stage in discovery_pkg.unknown_problem_epistemology.stages:
        assert stage.name in prompt
    assert discovery_pkg.adjacent_roles[0].title in prompt
    assert discovery_pkg.on_the_job_crucibles.crucible_episodes[0].title in prompt


def test_12_developer_context_inline_injection(shared_synthesizer):
    sentinel = "PROPRIETARY_ZNS_NVME_P999_BUDGET_6MS"
    pkg = shared_synthesizer.synthesize(
        role="infra_principal_cloud_platform_architect",
        problem="Stabilize multi-AZ consensus WAL tail latency during SSD garbage collection",
        developer_context=f"Hardware invariant: {sentinel} under dual-rack power maintenance.",
    )
    assert sentinel in pkg.developer_context
    assert sentinel in pkg.deep_superhuman_prompt
    assert sentinel in pkg.to_markdown()


def test_13_developer_context_file_injection(shared_synthesizer, tmp_path: Path):
    ctx_file = tmp_path / "proprietary_constraints.md"
    sentinel = "ANSSI_SEC_NUM_CLOUD_HSM_QUORUM_RULE_42"
    ctx_file.write_text(f"# Security Constraint\nEnforce {sentinel} across all root CA ceremonies.\n", encoding="utf-8")
    pkg = shared_synthesizer.synthesize(
        role="sec_chief_information_security_officer",
        problem="Architect zero-trust sovereign key ceremony failover",
        context_file=ctx_file,
    )
    assert sentinel in pkg.developer_context
    assert sentinel in pkg.deep_superhuman_prompt


def test_14_markdown_json_and_save_roundtrip(discovery_pkg: SuperhumanRolePackage, tmp_path: Path):
    md_text = discovery_pkg.to_markdown()
    json_data = json.loads(discovery_pkg.to_json())
    assert len(md_text) >= 6500
    assert json_data["slug"] == discovery_pkg.slug
    assert len(json_data["unknown_problem_epistemology"]["stages"]) == 5

    md_file = discovery_pkg.save(tmp_path / "pkg.md", format="markdown")
    js_file = discovery_pkg.save(tmp_path / "pkg.json", format="json")
    assert md_file.read_text(encoding="utf-8") == md_text
    assert json.loads(js_file.read_text(encoding="utf-8"))["id"] == discovery_pkg.id


def test_15_sqlite_persistence_list_and_get_profile(isolated_db_path: Path):
    syn = SuperhumanRoleSynthesizer.build_from_db(db_path=isolated_db_path)
    try:
        pkg = syn.synthesize(
            role="fin_chief_investment_officer",
            problem="Cross-currency basis swap liquidity freeze under sovereign yield curve control exit",
            persist=True,
        )
        listed = syn.list_profiles()
        assert any(item["slug"] == pkg.slug for item in listed)

        by_slug = syn.get_profile(pkg.slug)
        by_id = syn.get_profile(pkg.id)
        assert by_slug.id == pkg.id
        assert by_id.deep_superhuman_prompt == pkg.deep_superhuman_prompt

        with pytest.raises(KeyError):
            syn.get_profile("nonexistent_superhuman_profile_xyz")
    finally:
        if hasattr(syn, "close"):
            syn.close()


def test_16_empty_and_whitespace_inputs_raise_value_error(shared_synthesizer):
    with pytest.raises(ValueError):
        shared_synthesizer.synthesize()
    with pytest.raises(ValueError):
        shared_synthesizer.synthesize(problem="   \n\t  ")
    with pytest.raises(ValueError):
        shared_synthesizer.synthesize(problem="", role="   ", custom_role_spec="  ")


def test_17_cli_superhuman_synthesize_markdown_and_json(isolated_db_path: Path, tmp_path: Path):
    runner = CliRunner()
    res_md = runner.invoke(
        cli,
        [
            "superhuman",
            "synthesize",
            "--problem",
            "Design radiation-tolerant LEO optical inter-satellite phased array acquisition",
            "--db-path",
            str(isolated_db_path),
        ],
    )
    assert res_md.exit_code == 0, res_md.output
    assert len(res_md.output) >= 6000

    out_json = tmp_path / "cli_superhuman.json"
    res_js = runner.invoke(
        cli,
        [
            "superhuman",
            "synthesize",
            "--role",
            "semi_vp_euv_systems_engineering",
            "--problem",
            "Eliminate stochastic EUV resist line-edge roughness at High-NA 0.55 numerical aperture",
            "--format",
            "json",
            "--output",
            str(out_json),
            "--db-path",
            str(isolated_db_path),
        ],
    )
    assert res_js.exit_code == 0, res_js.output
    payload = json.loads(out_json.read_text(encoding="utf-8"))
    assert payload["input_mode"] == "canonical_role"
    assert payload["prompt_character_count"] >= 6000


def test_18_cli_superhuman_custom_role_inline(isolated_db_path: Path):
    runner = CliRunner()
    res = runner.invoke(
        cli,
        [
            "superhuman",
            "synthesize",
            "--custom-role-title",
            "Chief Fusion Magnetohydrodynamic Divertor Engineer",
            "--custom-role-prompt",
            "Control detached plasma heat flux in high-field HTS tokamak divertors.",
            "--problem",
            "Prevent tungsten monoblock recrystallization during unmitigated ELM transients",
            "--developer-context",
            "REBCO 20-Tesla magnets; peak steady heat flux <= 10 MW/m^2.",
            "--json",
            "--db-path",
            str(isolated_db_path),
        ],
    )
    assert res.exit_code == 0, res.output
    data = json.loads(res.output)
    assert data["input_mode"] == "custom_agent_role"
    assert "REBCO 20-Tesla" in data["deep_superhuman_prompt"]


def test_19_cli_superhuman_persist_list_and_inspect(isolated_db_path: Path):
    runner = CliRunner()
    res_syn = runner.invoke(
        cli,
        [
            "superhuman",
            "synthesize",
            "--role",
            "pharma_chief_scientific_officer",
            "--problem",
            "De-risk off-target hepatotoxicity in extrahepatic lipid nanoparticle mRNA delivery",
            "--persist",
            "--json",
            "--db-path",
            str(isolated_db_path),
        ],
    )
    assert res_syn.exit_code == 0, res_syn.output
    created = json.loads(res_syn.output)
    slug = created["slug"]

    res_list = runner.invoke(cli, ["superhuman", "list", "--json", "--db-path", str(isolated_db_path)])
    assert res_list.exit_code == 0, res_list.output
    items = json.loads(res_list.output)
    assert any(i["slug"] == slug for i in items)

    res_insp_json = runner.invoke(cli, ["superhuman", "inspect", slug, "--format", "json", "--db-path", str(isolated_db_path)])
    assert res_insp_json.exit_code == 0, res_insp_json.output
    assert json.loads(res_insp_json.output)["slug"] == slug

    res_insp_md = runner.invoke(cli, ["superhuman", "inspect", slug, "--format", "markdown", "--db-path", str(isolated_db_path)])
    assert res_insp_md.exit_code == 0, res_insp_md.output
    assert len(res_insp_md.output) >= 6000


def test_20_cli_error_handling_on_empty_or_missing(isolated_db_path: Path):
    runner = CliRunner()
    bad_syn = runner.invoke(cli, ["superhuman", "synthesize", "--problem", "   ", "--db-path", str(isolated_db_path)])
    assert bad_syn.exit_code != 0

    bad_insp = runner.invoke(cli, ["superhuman", "inspect", "missing_profile_slug_999", "--db-path", str(isolated_db_path)])
    assert bad_insp.exit_code != 0


def test_21_skill_helper_script_end_to_end(isolated_db_path: Path, tmp_path: Path):
    script = WORKSPACE_SKILL_DIR / "scripts" / "synthesize_superhuman.py"
    out_file = tmp_path / "script_out.json"
    proc = subprocess.run(
        [
            sys.executable,
            str(script),
            "--role",
            "robotics_principal_mpc_locomotion_architect",
            "--problem",
            "Whole-body dynamic contact recovery on deformable granular terrain under actuator saturation",
            "--developer-context",
            "500 Hz torque control loop; zero-slip friction cone estimation.",
            "--persist",
            "--format",
            "json",
            "--output",
            str(out_file),
            "--db-path",
            str(isolated_db_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    saved = json.loads(out_file.read_text(encoding="utf-8"))
    assert saved["prompt_character_count"] >= 6000

    bad_proc = subprocess.run(
        [sys.executable, str(script), "--problem", "   ", "--db-path", str(isolated_db_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert bad_proc.returncode != 0


def test_22_skill_bundle_parity_and_frontmatter():
    rel_files = [
        "SKILL.md",
        "scripts/synthesize_superhuman.py",
        "references/superhuman_epistemology_framework.md",
    ]
    for rel in rel_files:
        ws_file = WORKSPACE_SKILL_DIR / rel
        gl_file = GLOBAL_SKILL_DIR / rel
        assert ws_file.is_file(), f"Missing workspace skill file: {ws_file}"
        assert gl_file.is_file(), f"Missing global skill file: {gl_file}"
        assert ws_file.read_bytes() == gl_file.read_bytes(), f"Byte parity mismatch for {rel}"

    skill_text = (WORKSPACE_SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    parts = skill_text.split("---", 2)
    assert len(parts) >= 3
    fm = yaml.safe_load(parts[1])
    assert fm["name"] == "org-superhuman-role-synthesizer"
    assert "ACTIVATE" in fm["description"]
    assert "invoke_subagent" in skill_text


def test_23_orange_france_permanence_in_default_db():
    conn = get_connection(get_default_db_path())
    try:
        row = conn.execute(
            "SELECT id, slug, rank FROM fortune500_companies WHERE id = 'f500_orange_france'"
        ).fetchone()
        assert row is not None, "f500_orange_france must survive pytest runs!"
        assert row[1] == "orange_france"
        assert row[2] >= 501
        emp_cnt = conn.execute(
            "SELECT count(*) FROM employs_role WHERE company_id = 'f500_orange_france'"
        ).fetchone()[0]
        assert emp_cnt >= 41
        role_cnt = conn.execute("SELECT count(*) FROM canonical_roles").fetchone()[0]
        assert role_cnt >= 551
    finally:
        conn.close()
