# Organizational Knowledge Graph & Role Meta-Prompting Database (`orgprompt`)

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://python.org)
[![Database](https://img.shields.io/badge/Database-SQLite%20FTS5%20%2B%20NetworkX-emerald.svg)](https://sqlite.org)
[![Tests](https://img.shields.io/badge/Pytest-328%20passed%20(100%25)-success.svg)](tests/)
[![Search](https://img.shields.io/badge/Hybrid%20Search-BM25%20%2B%20LSA%20Dense%20%2B%20RRF-purple.svg)](orgprompt/search/)
[![Skills](https://img.shields.io/badge/Antigravity%20Skills-5%20Installed-orange.svg)](.agents/skills/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, internet-grounded **Organizational Knowledge Graph**, **Canonical Role Taxonomy**, **Superhuman Role & Governance Synthesizer**, **Nov 2026 Frontier AI Lab Bridge**, **Dual-Layer Tooling Model**, and **Personal Subagent Swarm ("Role-in-a-Box") Orchestration Platform**.

The repository models **512 real-world organizations** — all **500 Fortune 500 corporations** (#1 Walmart to #500 O-I Glass), **Orange France**, **6 Indie Film & YouTube Creator Studios** (`A24`, `Blumhouse Productions`, `Beast Industries`, `Mythical Entertainment`, `Corridor Digital`, `Kurzgesagt`), and **5 Nov 2026 Frontier AI Labs** (`Anthropic`, `OpenAI`, `Google DeepMind`, `Meta Superintelligence Labs`, `Mistral AI`), plus sample onboarding blueprints (`Stripe`). These organizations connect to **579 canonical operational roles** + **18 fiduciary Board & Independent Auditor governance roles** (**597 total roles**) via **27,669 `EMPLOYS_ROLE` edges**, **60 horizontal + vertical tools**, **2,895 day-to-day use cases**, **3,474 strictly acyclic personal subagent swarms**, **10 Superhuman 8-Section Profiles** (`7` operational + `3` fiduciary governance), and **1,721 real-world-to-frontier-lab role joins**.

---

## Key Metrics at a Glance (Phases 1–16)

| Pillar | Quantitative Specification | Status |
|---|---|---|
| **Organization Coverage** | **512 Persisted Orgs**: 500 Fortune 500 + Orange France + 6 Indie Film/YouTube Studios + 5 Nov 2026 Frontier AI Labs (+ Stripe sample blueprint) | 100% Validated |
| **Macro Industries** | **16 Macro Industries** & **6 Operating Archetypes** | 100% Validated |
| **Canonical & Governance Roles** | **579 Canonical Roles** (incl. 14 Creator/Film + 16 Frontier Lab roles) + **18 Fiduciary Board & Auditor Roles** = **597 Total Roles** | 0 Orphans, 4 Invariants |
| **Graph Density** | **27,669 `EMPLOYS_ROLE` Edges** + **2,278 `role_edges`** + **72 `governance_oversight_edges`** | Bidirectional Verified |
| **Work Anatomy & Tools** | **60 Tools** (6 horizontal productivity + 54 vertical/creator/frontier platforms) & **3,653 `role_tooling` links** | Relational Schema |
| **Operational Use Cases** | **2,895 Day-to-Day Use Cases** (cadence, triggers, cognitive bottlenecks) | >=5 per Role |
| **Personal Subagent Swarms** | **3,474 Subagents** (6 specialized agents per canonical role, strictly acyclic DAGs) | 100% Acyclic & HITL |
| **GenAI Tooling & Section 7 Prompts** | **579 Concrete GenAI Build Plans** & **579 Compiled 7-Section System Prompts** (>=6,480 chars, 0 stubs) | 100% Coverage |
| **Superhuman Synthesis** | **7 Superhuman Role Profiles** + **3 Superhuman Governance Profiles** (8-Section Deep Meta-Prompts + 5-Stage OOD Epistemology) | A/B Benchmarked (+61.1 pts) |
| **Board & Auditor Governance** | **18 Board/Auditor Roles**, **22 Industry Board Slates**, **72 Oversight Edges** (`orgprompt.governance`) | A/B Benchmarked (+68.7 pts) |
| **Nov 2026 Frontier AI Lab Bridge** | **5 Frontier AI Labs**, **30 Lab Pods**, **22 Cross-Industry Bridges** across **16/16 Industries**, **1,721 `role_frontier_joins`** | 100% Join Coverage |
| **Encyclopedia & Comparisons** | **5 Volumes (2.27 MB)** + **512 Public SEC / Internet Comparison Records** | Grounded & Verified |
| **Local Hybrid Search** | SQLite FTS5 BM25 + dense LSA (TruncatedSVD) + Reciprocal Rank Fusion ($k=60$) | Recall@10: 0.9306, MRR: 0.7917 |
| **Antigravity Agent Skills** | **5 Installed Skills** in `.agents/skills/` and `~/.gemini/config/skills/` | Byte-Identical Sync |
| **Automated Test Suite** | **328 / 328 Pytest suite passing** (0 skipped, 0 failed) | 100% Passing |

---

## Architectural Overview

```
                     +-------------------------------------------------------------------------------+
                     |                        User / CLI / 5 Antigravity Agent Skills                |
                     +---------------------------------------+---------------------------------------+
                                                             |
            +------------------------+-----------------------+-----------------------+------------------------+
            |                        |                       |                       |                        |
            v                        v                       v                       v                        v
   [ Scaffolder & Search ]  [ Company Onboarder ]   [ Superhuman Engine ]   [ Governance Engine ]    [ Frontier Bridge ]
  `scaffold` / `search`     `company onboard`       `orgprompt superhuman`  `orgprompt governance`   `orgprompt frontier`
   BM25 + LSA Dense + RRF   10-K & Web Synthesis    8-Sec OOD Meta-Prompts  Board & Auditor Slates   5 Labs / 1,721 Joins
            |                        |                       |                       |                        |
            +------------------------+-----------------------+-----------------------+------------------------+
                                                             |
                                                             v
                                    +-------------------------------------------------+
                                    |       Hybrid SQLite FTS5 DB & NetworkX KG       |
                                    |  - 512 Organizations (F500, Telecom, Creators,  |
                                    |    Anthropic, OpenAI, GDM, MSL/FAIR, Mistral)   |
                                    |  - 579 Canonical + 18 Governance = 597 Roles    |
                                    |  - 27,669 EMPLOYS_ROLE + 1,721 Frontier Joins   |
                                    |  - 60 Tools | 2,895 Use Cases | 3,474 Subagents |
                                    |  - 10 Persisted Superhuman 8-Section Profiles   |
                                    +-------------------------------------------------+
```

### Core Capabilities Across Phases 1–16
1. **Enterprise, Creator & Frontier Lab Catalog (`512` Organizations)**:
   - Models all **500 Fortune 500 corporations** across **16 Macro Industries** and **6 Operating Archetypes**, plus **Orange France** (European Telecom & Cyber), **6 Indie Film & YouTube Creator Studios** (`A24`, `Blumhouse`, `Beast Industries`, `Mythical`, `Corridor Digital`, `Kurzgesagt`), and **5 Nov 2026 Frontier AI Labs** (`Anthropic`, `OpenAI`, `Google DeepMind`, `Meta Superintelligence Labs`, `Mistral AI`).
2. **Canonical Role Taxonomy (`579` Roles) & Personal Subagent Swarms (`3,474` Subagents)**:
   - Covers 13 enterprise functional families plus dedicated indie film/creator production roles (`14`) and frontier AI lab research/safety/deployment roles (`16`). Every role links to **60 horizontal & vertical tools**, **>=5 operational use cases**, a **GenAI build plan**, a **6-agent strictly acyclic subagent swarm DAG** with HITL gates, and a **compiled 7-section System Prompt**.
3. **Polymathic Superhuman Role Synthesizer (`orgprompt.superhuman`)**:
   - Synthesizes **Perfect Human Backgrounds** (dual doctoral foundations, 12–20 year crucible scar tissue), **Org-Graph Adjacency Fusions**, and **8-Section Deep Meta-Prompts** with **5-Stage Out-of-Distribution (Unknown-to-AI) Epistemic Protocols**. Validated on a 12-case blind benchmark (`98.9/100` vs `37.8/100` vanilla, `+61.1` pts, 100% win rate).
4. **Fiduciary Board of Directors & Independent Auditor Governance (`orgprompt.governance`)**:
   - Models **18 non-executive fiduciary roles** (`10` Board Directors + `8` Statutory/Forensic/Strategic/AI Safety Auditors) sitting strictly above management (`0` `REPORTS_TO` edges into executives, `72` `governance_oversight_edges`), **22 industry-tailored Board slates**, and **3 Superhuman Governance Profiles**. Validated on a 12-case forensic Board audit benchmark (`99.0/100` vs `30.2/100` vanilla, `+68.7` pts, `100%` accounting-spin trap detection).
5. **Nov 2026 Frontier AI Lab & Enterprise Join Engine (`orgprompt.frontier`)**:
   - Models the **5 Nov 2026 Frontier AI Labs**, **30 internal research/post-training/safety/product pods**, **22 cross-industry bridges** spanning all **16/16 industries**, and **1,721 deterministic `role_frontier_joins`** mapping any enterprise or creator role/company/problem to its exact frontier lab pod, RL outcome verifier recipe, MCP context runtime, distillation forge, and ASL-3+/FSF safety gate.

---

## Installed Antigravity Agent Skills (`5` Native Skills)

All 5 skills are tracked in `.agents/skills/` and installed byte-identically into `~/.gemini/config/skills/`:

| Skill Name | Primary Engine / Helper | Purpose & Activation Trigger |
|---|---|---|
| **`org-role-search-and-scaffold`** | `orgprompt scaffold role` / `scaffold_role_helper.py` | Searches canonical roles, day-to-day workflows, dual-layer tooling, and scaffolds Role-in-a-Box subagent swarms (JSON & Markdown). |
| **`org-company-deep-onboard`** | `orgprompt company onboard` / `onboard_company_helper.py` | Researches and onboards any public/private corporation or studio into SQLite, wires graph edges, and generates an **"Apply GenAI Everywhere"** blueprint. |
| **`org-superhuman-role-synthesizer`** | `orgprompt superhuman` / `synthesize_superhuman_role.py` | Synthesizes polymathic Superhuman Role Definitions, Perfect Human pedigrees, Org-Graph Adjacency Fusions, and 5-Stage OOD Epistemic Meta-Prompts. |
| **`org-board-and-auditor-governance`** | `orgprompt governance` / `convene_board_and_audit.py` | Convenes industry-tailored Board of Directors slates, Independent Statutory/Forensic/Strategic Auditors, and 8-Section Superhuman Governance Profiles. |
| **`org-frontier-lab-enterprise-bridge`** | `orgprompt frontier` / `bridge_frontier_lab.py` | Joins any real-world enterprise, creator studio, role, or hard problem to the 5 Nov 2026 Frontier AI Labs, 30 lab pods, RL verifiers, MCP runtimes, and ASL/FSF gates. |

---

## Flagship Reports & Session Brain Artifacts

All major architectural reports, forensic audits, playbooks, and benchmark dossiers are preserved in `artifacts/` and mirrored in `artifacts/session_brain_docs/`:

- **[Nov 2026 Frontier AI Labs & Enterprise Bridge Report](artifacts/frontier_labs/frontier_ai_labs_nov2026_and_enterprise_bridge_report.md)** — Complete architecture of Anthropic, OpenAI, Google DeepMind, Meta Superintelligence Labs / FAIR, and Mistral AI (`30` pods, `1,721` joins, Orange France & Beast Industries bridges).
- **[Board of Directors & Independent Auditor Governance Report](artifacts/governance_roles/board_and_auditor_governance_report.md)** — Fiduciary oversight graph (`18` roles, `22` slates) and 12-case forensic Board audit benchmark (`99.0` vs `30.2`, `+68.7` pts).
- **[Superhuman Skill Benchmark Report](artifacts/superhuman_roles/superhuman_skill_benchmark_report.md)** — Blind 12-case known + OOD evaluation (`98.9` vs `37.8`, `+61.1` pts, 100% win rate).
- **[Social Media & Indie Film Channel Launch Playbook](artifacts/superhuman_roles/social_media_channel_launch_playbook.md)** — Zero-to-1M subscriber creator studio blueprint grounded in A24, Blumhouse, Beast Industries, Corridor Digital, Kurzgesagt, and Mythical.
- **[Orange France McKinsey Shareholder Value Audit](artifacts/company_onboarding/orange_france_mckinsey_shareholder_value_audit.md)** — FY2025–2028 financial & strategic ROIC/WACC/SOTP audit and GenAI transformation roadmap.
- **[Master Grand Challenge Dossier](artifacts/grand_challenge_dossier.md)** — Comprehensive multi-chapter organizational synthesis dossier.
- **[Fortune 500 5-Volume Encyclopedia](artifacts/fortune500_encyclopedia/)** — 2.27 MB, 5-volume public SEC 10-K vs. knowledge-graph alignment encyclopedia across all 500 Fortune 500 enterprises.
- **[Session Brain Documentation Mirror](artifacts/session_brain_docs/)** — Complete archive of `walkthrough.md`, `implementation_plan.md`, subagent prompts, and all session reports.

---

## Directory Structure

```
org_meta_prompt_db/
├── pyproject.toml                         # Project metadata and pytest configuration
├── setup.py                               # Package installation script
├── README.md                              # Production documentation (Phases 1-16)
├── data/
│   └── org_knowledge_base.db              # SQLite FTS5 DB (512 orgs, 597 roles, 60 tools, 1,721 joins)
├── orgprompt/
│   ├── cli.py                             # Unified CLI (`scaffold`, `company`, `superhuman`, `governance`, `frontier`, `search`, `benchmark`)
│   ├── models.py                          # Pydantic schemas & validation invariants
│   ├── db/                                # Schema, F500/Creator/Frontier seeders, governance & join tables
│   ├── graph/                             # NetworkX graph hydration & 0-orphan invariant validators
│   ├── prompts/                           # 7-section operational prompt compiler & quality validator
│   ├── search/                            # Hybrid SQLite FTS5 BM25 + LSA Dense + RRF search engine
│   ├── scaffolder/                        # Role & Company runbook exporters (Markdown & JSON)
│   ├── onboarding/                        # Deep company research ingestion & GenAI blueprint generator
│   ├── superhuman/                        # Polymathic Superhuman 8-section & 5-stage OOD synthesizer
│   ├── governance/                        # Fiduciary Board slates, Independent Auditors & governance synthesizer
│   └── frontier/                          # Nov 2026 Frontier AI Lab pod & enterprise/creator join engine
├── .agents/skills/                        # 5 Native Antigravity Skills (byte-synced with ~/.gemini/config/skills/)
│   ├── org-role-search-and-scaffold/
│   ├── org-company-deep-onboard/
│   ├── org-superhuman-role-synthesizer/
│   ├── org-board-and-auditor-governance/
│   └── org-frontier-lab-enterprise-bridge/
├── benchmarks/
│   ├── superhuman_eval/                   # 12-case Superhuman vs Vanilla blind evaluation suite & results
│   └── governance_eval/                   # 12-case Board & Forensic Auditor blind evaluation suite & results
├── artifacts/
│   ├── fortune500_encyclopedia/           # 5-volume, 2.27 MB Fortune 500 Encyclopedia
│   ├── company_onboarding/                # Enterprise, Creator & Frontier Lab GenAI blueprints (17 orgs)
│   ├── superhuman_roles/                  # Persisted Superhuman 8-section JSON/MD profiles & playbooks
│   ├── governance_roles/                  # Persisted Superhuman Board/Auditor profiles & benchmark report
│   ├── frontier_labs/                     # Frontier AI Lab report & enterprise/creator bridge runbooks
│   ├── runbooks/                          # Scaffolded enterprise & studio runbooks
│   └── session_brain_docs/                # Complete mirror of session walkthrough, implementation plan & reports
└── tests/                                 # 328 unit, integration, benchmark & adversarial tests (100% passing)
```

---

## Installation & Setup

```bash
git clone https://github.com/pakmingw/org-meta-prompt-db.git
cd org-meta-prompt-db
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

The pre-seeded, integrity-verified SQLite database is included at `data/org_knowledge_base.db` (`PRAGMA integrity_check == ok`).

---

## Command-Line Interface (`orgprompt`) Quick-Reference

### 1. Instant Role & Company Scaffolder (`scaffold`)
```bash
# Export a complete Role-in-a-Box runbook (7-section prompt, 6-agent acyclic swarm DAG, tools, HITL gates)
orgprompt scaffold role chief-ai-officer --company "Microsoft" --format markdown

# Export an enterprise-wide organizational and agent architecture
orgprompt scaffold company "Orange France" --format markdown
```

### 2. Deep Enterprise & Studio Onboarding (`company onboard`)
```bash
# Onboard any public/private company or creator studio and generate an "Apply GenAI Everywhere" blueprint
orgprompt company onboard "Stripe" \
  --ticker "PRIVATE" \
  --industry "Financial Services" \
  --challenges "Expanding global embedded finance while controlling merchant fraud"

# Onboard from a structured deep-research JSON file
orgprompt company onboard "Beast Industries" --research-file research/beast_industries.json
```

### 3. Polymathic Superhuman Role Synthesizer (`superhuman`)
```bash
# Synthesize an 8-section Superhuman Role & 5-stage OOD epistemology for a frontier problem
orgprompt superhuman synthesize \
  --problem "Design a zero-copy ZNS NVMe Raft consensus ledger surviving correlated firmware bit-rot" \
  --role principal-distributed-systems-architect \
  --adjacent-k 4 --persist --format markdown

# List and inspect persisted Superhuman Role profiles (7 persisted profiles)
orgprompt superhuman list
orgprompt superhuman inspect superhuman_frontier_post_training_verifier_chief --format markdown
```

### 4. Fiduciary Board of Directors & Independent Auditors (`governance`)
```bash
# List all 18 Fiduciary Board Director & Independent Auditor seats
orgprompt governance list-roles

# Convene a tailored Board of Directors & External Audit Slate for any enterprise or creator studio
orgprompt governance board-slate --company "Orange France" --format markdown
orgprompt governance board-slate --company "A24" --stage VENTURE_OR_BOUTIQUE --format markdown

# Synthesize an 8-Section Superhuman Forensic Auditor or Board Director
orgprompt governance synthesize-superhuman \
  --problem "Audit FY2025 Non-GAAP EBITDA add-backs, spectrum capex capitalization, and ROIC vs WACC" \
  --role gov_forensic_accounting_auditor \
  --company "Orange France" \
  --fuse gov_audit_committee_chair --format markdown
```

### 5. Nov 2026 Frontier AI Lab & Enterprise Bridge (`frontier`)
```bash
# List the 5 Nov 2026 Frontier AI Labs and their 30 internal operating pods
orgprompt frontier labs
orgprompt frontier inspect-lab anthropic --format markdown

# Join any real-world canonical role or company to its counterpart Frontier Lab pods & RL/MCP recipes
orgprompt frontier join-role chief-information-security-officer --company "Orange France" --format markdown
orgprompt frontier join-company "Beast Industries" --format markdown

# Bridge any novel business, engineering, or creator problem to enterprise roles + Frontier AI Lab pods
orgprompt frontier bridge-problem \
  --problem "Build verifiable agentic telecom network self-healing with zero PII leakage under EU AI Act" \
  --company "Orange France" --top-k 6 --format markdown
```

### 6. Local Hybrid Search & Retrieval Benchmark (`search`, `benchmark`)
```bash
# Hybrid SQLite FTS5 BM25 + LSA Dense + Reciprocal Rank Fusion (RRF) search
orgprompt search query "post-training RL outcome verifier MCP runtime safety"

# Run the 36-query enterprise retrieval evaluation benchmark (Recall@10: 0.9306, MRR: 0.7917)
orgprompt benchmark run
```

---

## Testing & Verification (`328` Tests — `100%` Passing)

The repository enforces relational foreign keys, 0-orphan NetworkX graph invariants, DAG acyclicity across all `3,474` subagents, fiduciary non-subordination (`0` Board `REPORTS_TO` executive edges), `1,721` deterministic frontier lab joins across all `16/16` industries, and blind A/B benchmark assertions across **27 test modules (`328` tests)**:

```bash
# Run the complete 328-test suite
pytest -q

# Run targeted Governance & Frontier AI Lab test suites
pytest tests/test_frontier_labs_and_bridges.py tests/test_governance_board_auditors.py -q
```

---

## License

This project is licensed under the MIT License.
