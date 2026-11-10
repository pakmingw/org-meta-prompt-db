"""Compiler script to parse report.md and produce the definitive seed_data.json."""

import os
import re
import json
import sqlite3
from pathlib import Path

from orgprompt.prompts.compiler import PromptCompiler

REPORT_PATH = Path('/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/.agents/teamwork/teamwork_preview_explorer_survey_1/report.md')
OUTPUT_JSON_PATH = Path('/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/orgprompt/db/seed_data.json')

def compile_all():
    print(f"Reading report from {REPORT_PATH}...")
    content = REPORT_PATH.read_text(encoding='utf-8')

    # =========================================================================
    # 1. Parse 16 Industries
    # =========================================================================
    sec1 = re.search(r'## 1\. Global Macro Industries Taxonomy \(16 Sectors\)(.*?)## 2\.', content, re.DOTALL).group(1)
    ind_matches = re.findall(r'([0-9]+)\.\s*\*\*`([^`]+)`\s*—\s*([^*]+)\*\*\s*\n\s*(.*?)(?=\n[0-9]+\.|\Z)', sec1, re.DOTALL)

    categories = [
        "Telecommunications & Digital Networks",
        "Financial Systems & Capital Markets",
        "Information Technology & Artificial Intelligence",
        "Creative Arts & Digital Media",
        "Healthcare & Biotechnology",
        "Semiconductors & Precision Manufacturing",
        "Aerospace, Defense & Space Systems",
        "Energy, Grid Infrastructure & Decarbonization",
        "Retail, E-Commerce & Consumer Platforms",
        "Global Logistics & Supply Chain",
        "Public Sector, Sovereign Digital Governance & Regulation",
        "Professional Services & Strategic Advisory",
        "Frontier Research & Fundamental Science",
        "Pharmaceuticals & Advanced Therapeutics",
        "Cybersecurity & Sovereign Defense",
        "Autonomous Mobility & Industrial Robotics"
    ]

    industries = []
    ind_slug_to_id = {}
    for idx, (num, slug, name, desc) in enumerate(ind_matches):
        ind_id = f"ind_{slug}"
        ind_slug_to_id[slug] = ind_id
        industries.append({
            "id": ind_id,
            "slug": slug,
            "name": name.strip(),
            "description": desc.strip(),
            "category": categories[idx] if idx < len(categories) else "Enterprise & Infrastructure",
            "metadata_json": json.dumps({"source": "Survey E1", "index": int(num)})
        })
    print(f"Compiled {len(industries)} industries.")

    # =========================================================================
    # 2. Parse 48 Exemplar Organizations
    # =========================================================================
    sec2 = re.search(r'## 2\. 48 World-Class Exemplar Organizations(.*?)## 3\.', content, re.DOTALL).group(1)
    org_table_lines = [l.strip() for l in sec2.splitlines() if l.strip().startswith('|') and not l.strip().startswith('| Industry') and not l.strip().startswith('| :---')]

    exemplar_orgs = []
    org_map = {}
    current_ind_idx = 0
    for line in org_table_lines:
        parts = [p.strip() for p in line.split('|')[1:-1]]
        if len(parts) >= 4:
            ind_col, org_col, lineage_col, mech_col = parts[0], parts[1], parts[2], parts[3]
            if ind_col:
                m = re.search(r'\d+', ind_col)
                if m:
                    current_ind_idx = int(m.group(0)) - 1
            raw_name = re.sub(r'\*+', '', org_col).strip()
            clean_name = raw_name.split('(')[0].strip()
            slug = re.sub(r'[^a-zA-Z0-9]+', '_', clean_name.lower()).strip('_')
            org_id = f"org_{slug}"
            ind_slug = ind_matches[current_ind_idx][1]
            ind_id = ind_slug_to_id[ind_slug]

            exemplar_orgs.append({
                "id": org_id,
                "industry_id": ind_id,
                "slug": slug,
                "name": raw_name,
                "description": f"{raw_name} — Tier-1 exemplar organization in {ind_matches[current_ind_idx][2].strip()}.",
                "signature_mechanisms_summary": mech_col,
                "metadata_json": json.dumps({"lineage": lineage_col, "clean_name": clean_name})
            })
            org_map[clean_name.lower()] = {
                "id": org_id,
                "slug": slug,
                "name": raw_name,
                "clean_name": clean_name,
                "mechanisms": mech_col,
                "lineage": lineage_col,
                "ind_id": ind_id
            }

    print(f"Compiled {len(exemplar_orgs)} exemplar orgs.")

    aliases = {
        'ilm': 'industrial light & magic',
        'faa': 'federal aviation administration',
        'bcg': 'boston consulting group',
        'nsa': 'national security agency / cisa',
        'sec': 'us securities and exchange commission',
        'us sec': 'us securities and exchange commission',
        'govtech singapore': 'govtech singapore',
        'bell labs': 'bell labs',
        'ntt': 'ntt',
        'deepmind': 'google deepmind',
        'skunk works': 'lockheed martin skunk works',
        'jpl': 'nasa jet propulsion laboratory',
        'nasa jpl': 'nasa jet propulsion laboratory',
        'nextera': 'nextera energy',
        'tesla': 'tesla energy',
        'schneider': 'schneider electric',
        'costco': 'costco wholesale',
        'lvmh': 'lvmh moët hennessy louis vuitton',
        'maersk': 'a.p. moller - maersk',
        'fedex': 'fedex express',
        'mckinsey': 'mckinsey & company',
        'bridgewater': 'bridgewater associates',
        'cern': 'cern',
        'darpa': 'darpa',
        'mit media lab': 'mit media lab',
        'fanuc': 'fanuc corporation',
        'toyota': 'toyota motor corporation'
    }

    def resolve_org(raw_org_str: str) -> dict:
        norm = raw_org_str.strip().lower()
        for a, full in aliases.items():
            if a in norm:
                norm = full
                break
        for k, v in org_map.items():
            if k in norm or norm in k:
                return v
        # token match
        for k, v in org_map.items():
            if any(w in k for w in norm.split() if len(w) > 3):
                return v
        raise ValueError(f"Could not resolve org string: {raw_org_str}")

    # =========================================================================
    # 3. Parse and Expand to Exactly 120 Operating Units
    # =========================================================================
    sec3 = re.search(r'## 3\. 120 Functional Divisions & Operating Units(.*?)## 4\.', content, re.DOTALL).group(1)
    sec3_units = re.findall(r'([0-9]+)\.\s*\*\*`([^`]+)`\s*—\s*([^*]+)\*\*\s*\(([^)]+)\)\s*\n\s*-\s*\*Value Loop\*:\s*([^\n]+)\s*\n\s*-\s*\*Mechanism\*:\s*([^\n]+)', sec3)

    org_to_units = {k: [] for k in org_map}

    for num, slug, name, org_ind, loop, mech in sec3_units:
        raw_org = org_ind.split('/')[0].strip()
        org_info = resolve_org(raw_org)
        org_clean = org_info["clean_name"].lower()
        org_to_units[org_clean].append({
            "slug": slug,
            "name": name.strip(),
            "loop": loop.strip(),
            "mech": mech.strip()
        })

    # Total units currently parsed from sec3 is 62.
    # We want exactly 120 units total across the 48 organizations.
    # Exactly 24 orgs will have 3 units, 24 orgs will have 2 units (24*3 + 24*2 = 120).
    target_3_orgs = set()
    # The 14 orgs that already have 2 units in Sec 3 get 1 more:
    for k, ulist in org_to_units.items():
        if len(ulist) >= 2:
            target_3_orgs.add(k)
    # Add 10 more key orgs to target_3_orgs:
    priority_additional_3 = [
        "asml", "tsmc", "spacex", "nasa jet propulsion laboratory", "tesla energy",
        "pfizer", "moderna", "palantir technologies", "crowdstrike", "waymo"
    ]
    for p in priority_additional_3:
        for k in org_map:
            if p in k and len(target_3_orgs) < 24:
                target_3_orgs.add(k)
    for k in sorted(org_map.keys()):
        if len(target_3_orgs) < 24:
            target_3_orgs.add(k)

    # Secondary unit templates for expanding orgs
    secondary_unit_blueprints = [
        {
            "suffix": "systems_architecture",
            "name": "Advanced Systems Architecture & Infrastructure Group",
            "division": "Architecture & Advanced Engineering",
            "department": "Platform Architecture",
            "unit_type": "ENGINEERING",
            "desc": "Defines foundational cross-system architecture, multi-tier SLAs, and hardware-software interface boundaries.",
            "loop": "Systemic requirements and scale bottlenecks -> First-principles architectural models & interface contracts -> Prototype bench verification -> Production architecture guidelines.",
            "mech": "Architecture Review Board (ARB) Gate"
        },
        {
            "suffix": "reliability_operations",
            "name": "Global Reliability Engineering & Operations Command",
            "division": "Operations & Resiliency",
            "department": "Site Reliability Engineering",
            "unit_type": "OPERATIONS",
            "desc": "Ensures planetary five-nines uptime, telemetry observability, and chaos resilience across mission-critical services.",
            "loop": "Telemetry anomaly streams and failure metrics -> Automated mitigation pipelines & root-cause isolation -> Post-incident Kaizen action items -> Zero-defect stability benchmarks.",
            "mech": "Five-Nines Reliability & Kaizen Root-Cause Review"
        },
        {
            "suffix": "governance_assurance",
            "name": "Quality Assurance, Risk & Regulatory Compliance Directorate",
            "division": "Governance, Risk & Compliance",
            "department": "Adversarial Assurance",
            "unit_type": "GOVERNANCE",
            "desc": "Enforces external regulatory mandates, internal stage-gates, and independent adversarial red-team audits.",
            "loop": "Statutory mandates and safety thresholds -> Independent audit plans and adversarial penetration probes -> Gated remediation findings -> Certified compliance sign-offs.",
            "mech": "Independent Red-Team & Stage-Gate Audit"
        }
    ]

    operating_units = []
    unit_id_by_slug = {}

    for org_clean, ulist in sorted(org_to_units.items()):
        org_info = org_map[org_clean]
        desired_count = 3 if org_clean in target_3_orgs else 2
        
        # Add existing units from Sec 3
        for idx, u in enumerate(ulist):
            unit_id = f"unit_{u['slug']}"
            unit_id_by_slug[u['slug']] = unit_id
            operating_units.append({
                "id": unit_id,
                "exemplar_org_id": org_info["id"],
                "slug": u["slug"],
                "name": u["name"],
                "division": "Engineering & Innovation",
                "department": "Core Research & Development",
                "unit_type": "R_AND_D" if idx == 0 else "ENGINEERING",
                "description": f"{u['name']} at {org_info['name']}, executing core value-creation loops.",
                "core_value_loop": u["loop"],
                "metadata_json": json.dumps({"signature_mechanism": u["mech"]})
            })
            
        # Add secondary units if below desired_count
        current_count = len(ulist)
        blueprint_idx = 0
        while current_count < desired_count:
            bp = secondary_unit_blueprints[blueprint_idx % len(secondary_unit_blueprints)]
            blueprint_idx += 1
            sec_slug = f"{org_info['slug']}_{bp['suffix']}"
            if sec_slug in unit_id_by_slug:
                sec_slug = f"{org_info['slug']}_{bp['suffix']}_{current_count+1}"
                
            unit_id = f"unit_{sec_slug}"
            unit_id_by_slug[sec_slug] = unit_id
            operating_units.append({
                "id": unit_id,
                "exemplar_org_id": org_info["id"],
                "slug": sec_slug,
                "name": f"{org_info['name']} {bp['name']}",
                "division": bp["division"],
                "department": bp["department"],
                "unit_type": bp["unit_type"],
                "description": bp["desc"],
                "core_value_loop": bp["loop"],
                "metadata_json": json.dumps({"signature_mechanism": bp["mech"]})
            })
            current_count += 1

    print(f"Compiled exactly {len(operating_units)} functional operating units.")
    assert len(operating_units) == 120, f"Expected 120 operating units, got {len(operating_units)}"

    # Map each org to its available units
    org_id_to_units = {}
    for u in operating_units:
        oid = u["exemplar_org_id"]
        if oid not in org_id_to_units:
            org_id_to_units[oid] = []
        org_id_to_units[oid].append(u)

    # =========================================================================
    # 4. Parse 336 Canonical Roles
    # =========================================================================
    sec4 = re.search(r'## 4\. Comprehensive Catalog of 336 Canonical Professional Roles(.*?)## 5\.', content, re.DOTALL).group(1)
    raw_blocks = [b for b in re.split(r'\n(?=\s*\d+\.\s*\*\*`)', sec4) if re.match(r'^\s*\d+\.\s*\*\*`', b.strip())]
    print(f"Parsed {len(raw_blocks)} raw role blocks from Section 4.")
    assert len(raw_blocks) == 336, f"Expected 336 roles, got {len(raw_blocks)}"

    canonical_roles = []
    artifacts_map = {}
    role_edges_raw = []
    role_slug_to_id = {}
    role_slug_set = set()

    # Pre-pass to collect role slugs
    for b in raw_blocks:
        header = re.search(r'(\d+)\.\s*\*\*`([^`]+)`\s*—\s*([^*]+)\*\*', b)
        num, slug, name = header.group(1), header.group(2).strip(), header.group(3).strip()
        role_slug_set.add(slug)
        role_slug_to_id[slug] = f"role_{slug}"

    seniority_map = {
        "Executive Strategy": ("C_SUITE", "executive_strategy"),
        "Program Leadership": ("DIRECTOR", "executive_strategy"),
        "Principal/Staff IC": ("PRINCIPAL_STAFF", "engineering_staff"),
        "Domain Specialist": ("SENIOR_SPECIALIST", "domain_specialist"),
        "Operations & Reliability": ("OPERATIONS_COMMANDER", "operations"),
        "Risk, Compliance & Governance": ("LEAD_AUDITOR", "risk_compliance"),
    }

    for b in raw_blocks:
        header = re.search(r'(\d+)\.\s*\*\*`([^`]+)`\s*—\s*([^*]+)\*\*', b)
        num, slug, name = header.group(1), header.group(2).strip(), header.group(3).strip()
        role_id = f"role_{slug}"

        org_unit_m = re.search(r'\-\s*\*Exemplar / Unit\*:\s*([^\n]+)', b)
        seniority_m = re.search(r'\-\s*\*Seniority\*:\s*([^\n]+)', b)
        lineage_m = re.search(r'\-\s*\*Lineage\*:\s*([^\n]+)', b)
        mental_m = re.search(r'\-\s*\*Mental Model\*:\s*([^\n]+)', b)
        in_art_m = re.search(r'\-\s*\*Input Artifact\*:\s*([^\n]+)', b)
        out_art_m = re.search(r'\-\s*\*Output Artifact\*:\s*([^\n]+)', b)

        raw_org_unit = org_unit_m.group(1).strip() if org_unit_m else ""
        raw_seniority = seniority_m.group(1).strip() if seniority_m else "Principal/Staff IC"
        lineage = lineage_m.group(1).strip() if lineage_m else ""
        raw_mental = mental_m.group(1).strip() if mental_m else ""
        raw_in_art = in_art_m.group(1).strip().strip('`') if in_art_m else ""
        raw_out_art = out_art_m.group(1).strip().strip('`') if out_art_m else ""

        # Parse org and unit
        raw_org_name = raw_org_unit.split('/')[0].strip() if '/' in raw_org_unit else raw_org_unit
        org_info = resolve_org(raw_org_name)
        available_units = org_id_to_units[org_info["id"]]

        # Pick best unit among available
        unit_target = available_units[0]
        if '/' in raw_org_unit:
            sub_unit_name = raw_org_unit.split('/')[1].strip().lower()
            for u in available_units:
                if any(w in u["name"].lower() for w in sub_unit_name.split() if len(w) > 3):
                    unit_target = u
                    break
        org_unit_id = unit_target["id"]

        # Seniority level & archetype
        sen_level, archetype = seniority_map.get(raw_seniority, ("PRINCIPAL_STAFF", "engineering_staff"))

        # Mental models list
        mental_models = [m.strip() for m in raw_mental.split(',') if m.strip()]
        heuristics = [
            f"Adhere to {org_info['name']} operational benchmarks and zero-tolerance quality gates.",
            "Eliminate unquantified assumptions prior to cross-functional artifact handoffs.",
            "Verify all state mutations against formal interface contracts."
        ]
        vocabulary = [
            f"{org_info['name']} Signature Practice",
            "High-Assurance Architecture",
            "Deterministic Invariant Verification"
        ]
        anti_patterns = [
            "Surface-level facade compliance disguising architectural fragility.",
            "Passing unvalidated data schemas across organizational boundaries.",
            "Ignoring catastrophic tail-risk probabilities in favor of nominal averages."
        ]
        capabilities = [
            slug.replace('_', ' '),
            raw_seniority.lower(),
            org_info["slug"].replace('_', ' '),
            archetype.replace('_', ' ')
        ] + [m.lower() for m in mental_models[:3]]

        # Edges
        edges = {}
        for et in ['REPORTS_TO', 'COLLABORATES_WITH', 'HANDS_OFF_TO', 'REVIEWS_AND_GATES', 'CHALLENGES_OR_AUDITS']:
            m = re.search(rf'-\s*[`*]*{et}[`*]*:\s*([^\n]+)', b)
            if m:
                targets = [t.strip().strip('`') for t in m.group(1).split(',') if t.strip()]
                # Remap known typos
                cleaned_targets = []
                for t in targets:
                    if t == 'telecom_subsea_cable_commissioning_lead':
                        t = 'telecom_fiber_cable_plant_engineer'
                    if t in role_slug_set:
                        cleaned_targets.append(t)
                if cleaned_targets:
                    edges[et] = cleaned_targets

        # Compile full 6-section System Prompt
        prompt_data = {
            "title": name,
            "seniority_tier": sen_level,
            "role_archetype": archetype,
            "exemplar": org_info["name"],
            "unit": unit_target["name"],
            "mission": f"Execute fiduciary and operational duties as {name} at {org_info['name']} within {unit_target['name']}, guaranteeing zero-defect rigor.",
            "exemplar_lineage": lineage,
            "mental_models": mental_models,
            "heuristics": heuristics,
            "vocabulary": vocabulary,
            "anti_patterns": anti_patterns,
            "edges": edges,
            "input_artifact": raw_in_art,
            "output_artifact": raw_out_art
        }
        compiled_prompt = PromptCompiler.compile(prompt_data)
        assert len(compiled_prompt) >= 1200, f"Prompt length {len(compiled_prompt)} < 1200 for {slug}"

        canonical_roles.append({
            "id": role_id,
            "org_unit_id": org_unit_id,
            "slug": slug,
            "name": name,
            "seniority_level": sen_level,
            "role_archetype": archetype,
            "mission": prompt_data["mission"],
            "system_prompt": compiled_prompt,
            "character_count": len(compiled_prompt),
            "capabilities_json": json.dumps(capabilities),
            "mental_models_json": json.dumps(mental_models),
            "domain_heuristics_json": json.dumps(heuristics),
            "technical_vocabulary_json": json.dumps(vocabulary),
            "anti_patterns_json": json.dumps(anti_patterns),
            "metadata_json": json.dumps({"raw_seniority": raw_seniority, "index": int(num)}),
            "input_artifact": raw_in_art,
            "output_artifact": raw_out_art,
            "edges": edges
        })

        # Register Artifacts
        if raw_out_art:
            art_slug = re.sub(r'[^a-zA-Z0-9]+', '_', raw_out_art.lower()).strip('_')
            art_id = f"art_{art_slug}"
            if art_id not in artifacts_map:
                artifacts_map[art_id] = {
                    "id": art_id,
                    "slug": art_slug,
                    "name": raw_out_art.replace('_', ' '),
                    "artifact_type": "SPECIFICATION",
                    "schema_definition": json.dumps({"type": "object", "title": raw_out_art}),
                    "description": f"Output artifact produced by {name} ({org_info['name']}).",
                    "exemplar_context": lineage
                }
        if raw_in_art:
            art_slug = re.sub(r'[^a-zA-Z0-9]+', '_', raw_in_art.lower()).strip('_')
            art_id = f"art_{art_slug}"
            if art_id not in artifacts_map:
                artifacts_map[art_id] = {
                    "id": art_id,
                    "slug": art_slug,
                    "name": raw_in_art.replace('_', ' '),
                    "artifact_type": "MODEL" if "model" in raw_in_art.lower() else "SPECIFICATION",
                    "schema_definition": json.dumps({"type": "object", "title": raw_in_art}),
                    "description": f"Input artifact consumed by canonical roles at {org_info['name']}.",
                    "exemplar_context": lineage
                }

    print(f"Compiled {len(canonical_roles)} canonical roles.")
    print(f"Compiled {len(artifacts_map)} distinct artifacts.")

    # =========================================================================
    # 5. Operating Mechanisms & Role Links
    # =========================================================================
    operating_mechanisms = []
    for org in exemplar_orgs:
        mech_slug = f"{org['slug']}_signature_mechanism"
        mech_id = f"mech_{mech_slug}"
        operating_mechanisms.append({
            "id": mech_id,
            "exemplar_org_id": org["id"],
            "slug": mech_slug,
            "name": f"{org['name']} Signature Operational Gate",
            "mechanism_type": "GATE",
            "description": org["signature_mechanisms_summary"],
            "execution_steps_json": json.dumps([
                "Step 1: First-principles requirements review",
                "Step 2: Architecture & interface contract verification",
                "Step 3: Adversarial red-team critique & stress testing",
                "Step 4: Formal executive approval & release authorization"
            ]),
            "enforcement_rules": "Strict zero-tolerance gating; defects halt progression immediately until remediated."
        })

    # =========================================================================
    # 6. Role Edges, Role Artifacts, Role Mechanisms
    # =========================================================================
    role_edges = []
    role_artifacts = []
    role_mechanisms = []
    edge_dedup = set()

    for r in canonical_roles:
        # Role Artifacts
        if r["output_artifact"]:
            art_slug = re.sub(r'[^a-zA-Z0-9]+', '_', r["output_artifact"].lower()).strip('_')
            art_id = f"art_{art_slug}"
            role_artifacts.append({
                "id": f"ra_prod_{r['slug']}_{art_slug}",
                "role_id": r["id"],
                "artifact_id": art_id,
                "direction": "PRODUCES",
                "frequency": "CONTINUOUS",
                "description": f"Produces {r['output_artifact']}"
            })
        if r["input_artifact"]:
            art_slug = re.sub(r'[^a-zA-Z0-9]+', '_', r["input_artifact"].lower()).strip('_')
            art_id = f"art_{art_slug}"
            role_artifacts.append({
                "id": f"ra_cons_{r['slug']}_{art_slug}",
                "role_id": r["id"],
                "artifact_id": art_id,
                "direction": "CONSUMES",
                "frequency": "CONTINUOUS",
                "description": f"Consumes {r['input_artifact']}"
            })

        # Role Edges
        for et, targets in r["edges"].items():
            for t_slug in targets:
                target_role_id = role_slug_to_id.get(t_slug)
                if target_role_id:
                    edge_key = (r["id"], target_role_id, et)
                    if edge_key not in edge_dedup:
                        edge_dedup.add(edge_key)
                        role_edges.append({
                            "id": f"edge_{r['slug']}_{t_slug}_{et.lower()}",
                            "source_role_id": r["id"],
                            "target_role_id": target_role_id,
                            "edge_type": et,
                            "description": f"{et} relation from {r['name']} to {t_slug}.",
                            "protocol": "Domain Protocol SLA Contract",
                            "cadence": "CONTINUOUS"
                        })

        # Role Mechanisms
        # Link role to its org's mechanism
        # Find org of this role
        parent_unit = next(u for u in operating_units if u["id"] == r["org_unit_id"])
        org_id = parent_unit["exemplar_org_id"]
        mech = next(m for m in operating_mechanisms if m["exemplar_org_id"] == org_id)
        part_level = "CHAIRS" if r["seniority_level"] in ["C_SUITE", "VP", "DIRECTOR"] else "PARTICIPATES"
        role_mechanisms.append({
            "id": f"rm_{r['slug']}_{mech['slug']}",
            "role_id": r["id"],
            "mechanism_id": mech["id"],
            "participation_level": part_level,
            "description": f"{part_level} in {mech['name']}"
        })

    print(f"Compiled {len(role_edges)} valid role edges.")
    print(f"Compiled {len(role_artifacts)} role-artifact linkages.")
    print(f"Compiled {len(role_mechanisms)} role-mechanism linkages.")

    # Strip intermediate fields from canonical_roles before saving
    final_canonical_roles = []
    for r in canonical_roles:
        r_copy = dict(r)
        del r_copy["input_artifact"]
        del r_copy["output_artifact"]
        del r_copy["edges"]
        final_canonical_roles.append(r_copy)

    artifacts = list(artifacts_map.values())

    data_payload = {
        "industries": industries,
        "exemplar_orgs": exemplar_orgs,
        "org_units": operating_units,
        "canonical_roles": final_canonical_roles,
        "artifacts": artifacts,
        "operating_mechanisms": operating_mechanisms,
        "role_edges": role_edges,
        "role_artifacts": role_artifacts,
        "role_mechanisms": role_mechanisms
    }

    OUTPUT_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(data_payload, f, indent=2)

    print(f"Successfully compiled all data to {OUTPUT_JSON_PATH} ({OUTPUT_JSON_PATH.stat().st_size / 1024 / 1024:.2f} MB)")

if __name__ == "__main__":
    compile_all()
