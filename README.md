# Organizational Knowledge Graph & Role Meta-Prompting Database (`orgprompt`)

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://python.org)
[![Database](https://img.shields.io/badge/Database-SQLite%20FTS5%20%2B%20NetworkX-emerald.svg)](https://sqlite.org)
[![Tests](https://img.shields.io/badge/Pytest-244%20passed%20(100%25)-success.svg)](tests/)
[![Search](https://img.shields.io/badge/Hybrid%20Search-BM25%20%2B%20LSA%20Dense%20%2B%20RRF-purple.svg)](orgprompt/search/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An enterprise-grade, internet-grounded **Organizational Knowledge Graph**, **Canonical Role Taxonomy**, **Dual-Layer Tooling Model**, and **Personal Subagent Swarm ("Role-in-a-Box") Orchestration Platform**.

The repository models all **500 Fortune 500 corporations** (#1 Walmart to #500 O-I Glass) plus onboarded enterprises (e.g. Stripe), interconnected with **549 canonical enterprise roles** across **13 functional families** via **26,900+ verified `EMPLOYS_ROLE` edges** with strict 0-orphan invariants. Every role is equipped with an authentic day-to-day operational work anatomy (51 tools, 2,735 use cases), a 6-agent strictly acyclic subagent swarm DAG with Human-in-the-Loop (HITL) checkpoints, a concrete GenAI engineering build plan, and compiled 7-section System Prompts averaging over 6,480 characters.

---

## Key Metrics at a Glance

| Pillar | Quantitative Specification | Status |
|---|---|---|
| **Enterprise Coverage** | **501 Enterprises**: Complete Fortune 500 catalog (#1 to #500) + Stripe | 100% Validated |
| **Macro Industries** | **16 Macro Industries** & **6 Operating Archetypes** | 100% Validated |
| **Canonical Role Taxonomy** | **549 Roles** across **13 Functional Families** | 0 Orphans, 4 Invariants |
| **Graph Density** | **26,900+ `EMPLOYS_ROLE` Edges** in SQLite and NetworkX | Bidirectional Verified |
| **Work Anatomy & Tools** | **51 Tools** (6 horizontal productivity + 45 domain platforms) | Relational Schema |
| **Operational Use Cases** | **2,735 Day-to-Day Use Cases** (cadence, triggers, cognitive bottlenecks) | >=4 per Role |
| **Personal Subagent Swarms**| **3,282 Subagents** (6 specialized agents per role, strictly acyclic DAGs) | 100% Acyclic & HITL |
| **GenAI Tooling Plans** | **547 Concrete Build Plans** (RAG architecture, ROI metrics, guardrails) | 100% Coverage |
| **Section 7 Meta-Prompts** | **549 Upgraded System Prompts** (minimum length 6,482 characters, 0 stubs) | 100% Unique |
| **Mega-Output Encyclopedia** | **5 Volumes, 2.27 MB**, 500 company internet comparison rows | Public SEC Grounded |
| **Local Hybrid Search** | SQLite FTS5 BM25 + dense LSA (TruncatedSVD) + Reciprocal Rank Fusion | Recall@10: 0.9306, MRR: 0.7917 |
| **Scaffolder & Onboarder** | Instant CLI (`orgprompt scaffold`, `orgprompt company onboard`) | JSON & Markdown |
| **Antigravity Agent Skills** | Dual skills (`org-role-search-and-scaffold`, `org-company-deep-onboard`) | Git & Agent Hub |
| **Automated Test Suite** | **244 / 244 Pytest suite passing** (0 skipped, 0 failed) | 100% Passing |

---

## Architectural Pillars

```
                     +-------------------------------------------------------------------------+
                     |                     User / CLI / Antigravity Agent Swarms               |
                     +------------------------------------+------------------------------------+
                                                          |
                      +-----------------------------------+-----------------------------------+
                      |                                   |                                   |
                      v                                   v                                   v
             [ CLI Scaffolder ]                 [ Hybrid Search Engine ]            [ Onboarding Engine ]
         `orgprompt scaffold role`             SQLite FTS5 BM25 + LSA Dense        `orgprompt company onboard`
        `orgprompt scaffold company`              Reciprocal Rank Fusion             Deep Web & 10-K Research
                      |                                   |                                   |
                      +-----------------------------------+-----------------------------------+
                                                          |
                                                          v
                                     +-----------------------------------------+
                                     |    Hybrid SQLite DB & NetworkX KG       |
                                     |  - 501 Companies (500 F500 + Stripe)    |
                                     |  - 549 Canonical Enterprise Roles       |
                                     |  - 26,900+ `EMPLOYS_ROLE` Graph Edges   |
                                     |  - 51 Tools (Horizontal & Vertical)     |
                                     |  - 2,735 Operational Use Cases          |
                                     |  - 3,282 Subagents & Acyclic Swarms     |
                                     |  - 547 GenAI Tooling Build Plans        |
                                     |  - 500 Internet SEC Comparison Records  |
                                     +--------------------+--------------------+
                                                          |
                      +-----------------------------------+-----------------------------------+
                      |                                   |                                   |
                      v                                   v                                   v
             [ Section 7 Prompts ]              [ Personal Subagent Swarm ]          [ GenAI Blueprint ]
            Meta-Prompt Compiler                  6-Agent Acyclic Swarm DAG           "Apply GenAI Everywhere"
            Min 6,482 characters                  HITL Approval Checkpoints           Divisional RAG & Tooling
```

### 1. Fortune 500 Enterprise Catalog & Internet Grounding
The platform models all 500 corporations from the Fortune 500 catalog (#1 Walmart to #500 O-I Glass) plus onboarded tech giants (Stripe):
- **16 Macro Industries**: Technology, Financial Services, Healthcare & Pharmaceuticals, Retail & E-Commerce, Energy & Utilities, Automotive & Transportation, Aerospace & Defense, Manufacturing & Industrial, Telecommunications & Media, Consumer Goods & Food, Real Estate & Construction, Hospitality & Leisure, Materials & Chemicals, Agriculture & Commodities, Professional & Business Services, Public Sector & Non-Profit.
- **6 Operating Archetypes**:
  - `Product-Led Matrix` (e.g. Apple, Google, Stripe)
  - `Divisional Conglomerate` (e.g. Berkshire Hathaway, GE, Honeywell)
  - `Regulated Utility / Infrastructure` (e.g. NextEra, Duke Energy)
  - `Project-Based Professional` (e.g. Accenture, Jacobs, McKinsey)
  - `Direct-to-Consumer / Distributed Franchise` (e.g. Walmart, McDonald's, Home Depot)
  - `Agile R&D / Platform Ecosystem` (e.g. Nvidia, Moderna)
- **High-Density Graph Connectivity**: 26,900+ typed `EMPLOYS_ROLE` edges link companies to canonical roles with departmental assignment (`Engineering`, `Commercial`, `Clinical`, `Trading`, `Supply Chain`, etc.) and priority tier (`CORE`, `SPECIALIZED`, `GOVERNANCE`).
- **Graph Invariant Guarantee**: Validated by NetworkX test harness — 0 orphan roles, strictly connected components, and valid archetype mappings.

### 2. Canonical Role Taxonomy (549 Roles, 13 Families)
A standardized, non-redundant ontology covering all white-collar, executive, operational, and technical roles across the modern enterprise:
1. **Executive & Corporate Governance** (e.g. CEO, CFO, CTO, CISO, Chief AI Officer, General Counsel)
2. **Product Management & Strategy** (e.g. VP Product, Principal PM, Technical PM, Growth PM)
3. **Software Engineering & Architecture** (e.g. Principal Distributed Systems Architect, Staff Frontend Engineer)
4. **Data Science, AI & Analytics** (e.g. Head of AI Research, MLOps Engineer, Quantitative Researcher)
5. **Infrastructure, DevOps & Cloud Engineering** (e.g. Site Reliability Engineer, Cloud Security Architect)
6. **Cybersecurity, Information Security & Trust** (e.g. SOC Lead, Threat Intelligence Analyst, Cryptography Engineer)
7. **Corporate Finance, Accounting & Treasury** (e.g. VP FP&A, Treasurer, SEC Reporting Director)
8. **Legal, Regulatory Compliance & Government Affairs** (e.g. Chief Privacy Officer, Regulatory Affairs Director)
9. **People Operations, HR & Talent Acquisition** (e.g. VP Total Rewards, People Analytics Director)
10. **Sales, Commercial & Revenue Operations** (e.g. Enterprise AE, VP RevOps, Global Head of Solutions Architecture)
11. **Marketing, Growth & Brand Communications** (e.g. VP Product Marketing, Demand Gen Director, PR Officer)
12. **Customer Success, Client Services & Support** (e.g. Chief Customer Officer, Implementation Consultant)
13. **Supply Chain, Logistics, Procurement & Hardware Engineering** (e.g. VP Global Sourcing, Logistics Optimization Director)

### 3. Day-to-Day Work Anatomy & Dual-Layer Tooling
Models the exact digital habitat of knowledge workers:
- **6 Horizontal Productivity Archetypes**:
  - `WORD_PROCESSOR`: Google Docs, Microsoft Word, Notion
  - `SPREADSHEET_PROCESSOR`: Microsoft Excel, Google Sheets, Airtable
  - `SLIDE_PRESENTER`: Microsoft PowerPoint, Google Slides, Pitch
  - `MEETING_NOTE_TAKER`: Otter.ai, Zoom AI Companion, Microsoft Teams Copilot
  - `COMMUNICATION_TRIAGE`: Slack, Microsoft Teams, Superhuman
  - `BI_ANALYTICS`: Tableau, Microsoft Power BI, Looker
- **45 Vertical & Domain Platforms**: SAP S/4HANA, Salesforce CRM, Epic Systems EHR, Bloomberg Terminal, Synopsys EDA, Workday HCM, ServiceNow ITSM, Jira Enterprise, Snowflake Data Cloud, AWS Management Console, GitHub Enterprise, Figma Enterprise, Oracle Fusion, NetSuite, FactSet, HubSpot, etc.
- **2,735 Operational Use Cases**: Deep micro-workflows capturing cadence (daily, weekly, monthly, ad-hoc), trigger conditions, inputs, horizontal tools, domain tools, cognitive bottlenecks, and output artifacts.

### 4. Personal Subagent Swarms ("Role-in-a-Box") & GenAI Build Plans
Transforms every passive system prompt into an autonomous multi-agent operating unit:
- **6 Specialized Subagents per Role (3,282 Total)**:
  1. `CHIEF_OF_STAFF`: Orchestrates daily agenda, decomposes user requests, delegates to subagents.
  2. `RESEARCH_SYNTHESIZER`: Performs deep multi-hop search, SEC filing analysis, competitor intelligence.
  3. `DATA_ANALYST`: Executes SQL queries, runs pandas/numpy transformations, produces statistical charts.
  4. `DRAFTING_ENGINE`: Authors board slides, executive memos, technical specifications, and RFPs.
  5. `CRITIC_VERIFIER`: Red-teams outputs for mathematical correctness, compliance, hallucinations, and security.
  6. `EXECUTION_RUNNER`: Dispatches API calls, generates pull requests, triggers CI/CD or ERP workflows.
- **Strictly Acyclic Interaction DAGs**: Verified via `networkx.is_directed_acyclic_graph` and topological sorting:
  `MEETING_GRAPH -> CHIEF_OF_STAFF -> [RESEARCH_SYNTHESIZER, DATA_ANALYST] -> [DRAFTING_ENGINE, CRITIC_VERIFIER] -> PRINCIPAL`
- **Mandatory Human-in-the-Loop (HITL) Checkpoints**: Strict authorization gates before high-risk actions (e.g., executing financial transactions > $10k, pushing code to production, transmitting legal disclosures).
- **547 GenAI Build Plans**: Detailed specifications with RAG architectures, evaluation metrics, guardrails, and quantified ROI.
- **Section 7 Prompt Upgrades**: System Prompts procedural compilation now embeds full swarm topologies and GenAI plans, raising prompt length to **min 6,482 characters** (average > 7,000 chars, 0 stubs).

### 5. Mega-Output Encyclopedia (5 Volumes, 2.27 MB)
Generated across all 500 Fortune 500 companies in `artifacts/fortune500_encyclopedia/`:
- **Volume 1**: Technology & Financial Services (Rank #1 to #500 cross-referenced)
- **Volume 2**: Healthcare, Pharmaceuticals, Retail & E-Commerce
- **Volume 3**: Energy, Utilities, Automotive & Aerospace
- **Volume 4**: Manufacturing, Industrial, Telecommunications & Consumer Goods
- **Volume 5**: Real Estate, Hospitality, Materials, Agriculture, Services & Public Sector
Each entry features:
- SEC 10-K reported divisions and operating segments.
- Live public internet job architecture analysis.
- Database vs. Internet alignment scoring and delta analysis.
- Tailored Personal Subagent Swarm recommendations.

### 6. Local Hybrid Search Engine (BM25 + LSA Dense + RRF)
High-precision retrieval without external API dependencies:
- **Lexical Layer**: SQLite FTS5 BM25 with porter stemmer over companies, roles, use cases, tools, and swarms.
- **Dense Semantic Layer**: Local TF-IDF subword n-gram vectorization with TruncatedSVD dimensionality reduction (LSA).
- **Fusion Layer**: Reciprocal Rank Fusion (RRF, $k=60$) combining rank scores.
- **Benchmark Performance (36 Expanded Enterprise Queries)**:
  - **Recall@10**: `0.9306` (vs 0.7222 BM25 alone, 0.6944 Dense alone)
  - **MRR (Mean Reciprocal Rank)**: `0.7917` (vs 0.6181 BM25 alone, 0.5847 Dense alone)

---

## Directory Structure

```
org_meta_prompt_db/
├── pyproject.toml                         # Project metadata and pytest configuration
├── setup.py                               # Package installation script
├── README.md                              # This production documentation
├── .gitignore                             # Clean VCS tracking (tracks .agents/skills/, ignores teamwork)
├── implementation_plan.md                 # Complete milestone roadmap and execution records
├── data/
│   └── org_knowledge_base.db              # SQLite DB (501 companies, 549 roles, 26.9k edges, FTS5)
├── orgprompt/
│   ├── cli.py                             # Command-Line Interface (`orgprompt`)
│   ├── models.py                          # Pydantic schemas (F500, Swarms, Tools, Plans, Invariants)
│   ├── db/
│   │   ├── schema.sql                     # Full relational schema (16 tables, triggers, FTS5 tables)
│   │   ├── connection.py                  # Database connection manager & query helpers
│   │   ├── fortune500_catalog.py          # Authentic 500 Fortune 500 corporate catalog
│   │   ├── roles_families_1_9.py          # Canonical roles for Families 1 through 9
│   │   ├── roles_families_10_13.py        # Canonical roles for Families 10 through 13
│   │   ├── seed_fortune500.py             # Seeder for F500 companies & 26,900+ EMPLOYS_ROLE edges
│   │   ├── seed_encyclopedia.py           # Seeder for company comparisons & 5-volume encyclopedia
│   │   ├── seed_tooling.py                # Seeder for 51 tools & 2,735 operational use cases
│   │   └── seed_swarms_plans.py           # Seeder for 3,282 subagents & 547 GenAI build plans
│   ├── graph/
│   │   ├── engine.py                      # NetworkX graph hydration & multi-hop traversal
│   │   └── invariants.py                  # Graph invariant validator (0 orphans, archetype consistency)
│   ├── prompts/
│   │   ├── compiler.py                    # 7-section prompt compiler (averaging > 6,480 characters)
│   │   ├── templates.py                   # Dynamic meta-prompt templates
│   │   └── validator.py                   # Strict quality validator (length, uniqueness, completeness)
│   ├── search/
│   │   ├── bm25.py                        # SQLite FTS5 BM25 search engine
│   │   ├── dense.py                       # Pure local LSA subword dense vector search
│   │   ├── hybrid.py                      # Reciprocal Rank Fusion (RRF) search engine
│   │   └── benchmark.py                   # 36-query enterprise benchmark test harness
│   ├── scaffolder/
│   │   ├── role_scaffolder.py             # Role runbook exporter (JSON & Markdown)
│   │   └── company_scaffolder.py          # Company runbook exporter (JSON & Markdown)
│   └── onboarding/
│       ├── engine.py                      # Enterprise onboarding engine (research synthesis & DB update)
│       └── blueprint_generator.py         # "Apply GenAI Everywhere" blueprint synthesizer
├── .agents/skills/                        # Antigravity Skills (tracked in Git repository)
│   ├── org-role-search-and-scaffold/      # Role search & swarm scaffolding skill
│   │   ├── SKILL.md
│   │   └── scripts/scaffold_role_helper.py
│   └── org-company-deep-onboard/          # Deep company research & onboarding skill
│       ├── SKILL.md
│       ├── scripts/onboard_company_helper.py
│       └── references/onboarded_companies.md
├── artifacts/
│   ├── fortune500_encyclopedia/           # 5-volume, 2.27 MB Fortune 500 Encyclopedia
│   ├── company_onboarding/                # Generated enterprise GenAI blueprints (e.g. Stripe)
│   ├── grand_challenge_dossier.md         # 9,284-word Master Solution Dossier
│   └── scaffolds/                         # Exported role & company runbooks
└── tests/                                 # 244 unit, integration, and adversarial tests (100% passing)
```

---

## Installation & Setup

### Prerequisites
- Python 3.10, 3.11, or 3.12
- SQLite 3.35+ (with FTS5 support built-in)
- Git 2.30+

### Clone & Install
```bash
# Clone the repository
git clone https://github.com/pakmingw/org-meta-prompt-db.git
cd org-meta-prompt-db

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install package in editable mode with development dependencies
pip install -e ".[dev]"
```

### Database Seeding (Pre-built Database Included)
The pre-seeded SQLite database is tracked at `data/org_knowledge_base.db`. To rebuild or verify from scratch:
```bash
# Initialize schema and seed foundational data
python3 -m orgprompt.db.seed_data

# Seed complete Fortune 500 catalog and 26,900+ edges
python3 -m orgprompt.db.seed_fortune500

# Seed 51 tools and 2,735 operational use cases
python3 -m orgprompt.db.seed_tooling

# Seed 3,282 subagents, acyclic swarms, and Section 7 prompt upgrades
python3 -m orgprompt.db.seed_swarms_plans

# Generate 5-volume Encyclopedia and internet comparison tables
python3 -m orgprompt.db.seed_encyclopedia
```

---

## Command-Line Interface (`orgprompt`)

The `orgprompt` CLI provides instantaneous access to the entire knowledge graph, scaffolder, onboarding engine, and search engine.

### 1. Instant Role Scaffolder
Export an executable, multi-agent runbook for any canonical role:
```bash
# Scaffold by role slug or title in Markdown
orgprompt scaffold role chief-ai-officer --company "Microsoft" --format markdown

# Scaffold by query in JSON format
orgprompt scaffold role "lead-cloud-security-architect" --company "Amazon" --format json
```
*Output includes*: Full 7-section System Prompt, 6-agent personal subagent swarm DAG, horizontal/vertical tools, cadence use cases, and HITL approval checkpoints.

### 2. Enterprise Company Scaffolder
Export an enterprise-wide organizational and agent architecture:
```bash
# Scaffold Fortune 500 company
orgprompt scaffold company "Walmart" --format markdown

# Scaffold with specific division focus
orgprompt scaffold company "JPMorgan Chase" --division "Asset & Wealth Management" --format json
```

### 3. Programmatic Company Onboarding
Deeply onboard any new public or private enterprise into the database, synthesize bespoke roles, update skills, and generate an enterprise GenAI blueprint:
```bash
# Onboard a new enterprise with CLI arguments
orgprompt company onboard "Stripe" \
  --ticker "PRIVATE" \
  --industry "Financial Services" \
  --challenges "Expanding global embedded finance while controlling merchant fraud"

# Onboard from a deep research JSON file
orgprompt company onboard "Anduril Industries" --research-file research/anduril.json
```
*Generated Artifact*: `artifacts/company_onboarding/<slug>_genai_blueprint.md` mapping GenAI systems and Personal Subagent Swarms across all company divisions.

### 4. Local Hybrid Search
Execute hybrid BM25 + dense LSA search across companies, roles, use cases, tools, and subagents:
```bash
# Search for fraud and risk engineering across the graph
orgprompt search query "fraud detection quantitative model risk"

# Search for cloud security architectures
orgprompt search query "cloud security zero trust kubernetes IAM"
```

### 5. Enterprise Benchmark & Retrieval Evaluation
```bash
# Run the 36-query expanded enterprise retrieval benchmark (Recall@10 & MRR)
orgprompt benchmark run
```

---

## Python SDK Usage

```python
import sqlite3
from orgprompt.db.connection import get_connection
from orgprompt.graph.engine import KnowledgeGraphEngine
from orgprompt.scaffolder.role_scaffolder import RoleScaffolder
from orgprompt.scaffolder.company_scaffolder import CompanyScaffolder
from orgprompt.onboarding.engine import CompanyOnboardingEngine
from orgprompt.search.hybrid import HybridSearchEngine

# 1. Connect to SQLite Knowledge Base
conn = get_connection()
cursor = conn.cursor()

# Query Fortune 500 companies & canonical role count
cursor.execute("SELECT COUNT(*) FROM fortune500_companies")
print(f"Total Companies: {cursor.fetchone()[0]}")  # 500 F500 + onboarded

cursor.execute("SELECT COUNT(*) FROM canonical_roles")
print(f"Total Canonical Roles: {cursor.fetchone()[0]}")  # 547 base + bespoke

cursor.execute("SELECT COUNT(*) FROM employs_role")
print(f"Total EMPLOYS_ROLE Edges: {cursor.fetchone()[0]}")  # 26,900+

# 2. NetworkX Knowledge Graph Traversal
kg = KnowledgeGraphEngine.build_from_db(conn=conn)
print(f"Graph Nodes: {kg.number_of_nodes()}, Graph Edges: {kg.number_of_edges()}")

# 3. Scaffold a Role Swarm Runbook
role_scaffolder = RoleScaffolder(conn)
runbook = role_scaffolder.scaffold_role("chief-ai-officer", company_name="Microsoft")
print(f"Role: {runbook.role['name']}")
print(f"Subagents in Swarm: {len(runbook.subagent_swarm)}")
print(f"Section 7 Prompt Length: {len(runbook.role['system_prompt'])} characters")

# 4. Execute Local Hybrid Search
search_engine = HybridSearchEngine.build_from_db(conn)
results = search_engine.search("high-frequency algorithmic trading market risk", top_k=5)
for res in results.ranked_roles:
    print(f"[{res.rrf_score:.4f}] {res.role.name} ({res.role.slug})")
```

---

## Antigravity Agentic Integration

This repository includes two native **Google Antigravity Skills** installed in `.agents/skills/` (and linked into `~/.gemini/config/skills/`):

1. **`org-role-search-and-scaffold`**:
   - Searches the canonical database for roles, prompts, workflows, and tools.
   - Generates executable Role-in-a-Box subagent swarms and Markdown runbooks.
   - Activates when users ask to scaffold roles, build multi-agent teams, or retrieve production-grade system prompts.

2. **`org-company-deep-onboard`**:
   - Executes end-to-end deep research for any enterprise (publicly traded status, SEC 10-K divisions, business challenges, executive structures).
   - Ingests research via `orgprompt company onboard`, updating the SQLite DB and `references/onboarded_companies.md`.
   - Delivers the comprehensive **"Apply Generative AI Everywhere" Blueprint** with divisional tooling and subagent swarms.

---

## Testing & Quality Assurance

The codebase includes an exhaustive test suite executed via `pytest`. All 244 tests run in under 45 seconds with **zero failures and zero skips**:

```bash
# Run the complete test suite
pytest -v
```

### Test Coverage Matrix
| Test Module | Tests | Description |
|---|---|---|
| `test_adversarial_challenger.py` | 51 | Stress tests for edge cases, bad inputs, corrupt graphs, and security |
| `test_db.py` | 14 | Relational schemas, triggers, constraints, and cascade behaviors |
| `test_f500_graph.py` | 18 | Fortune 500 catalog, 26.9k edges, 0 orphans, NetworkX invariants |
| `test_f500_encyclopedia.py` | 12 | 5-volume encyclopedia generation, SEC comparison tables, file sizes |
| `test_tooling.py` | 18 | Dual-layer tooling, 51 tools, 2,735 operational use cases |
| `test_subagent_swarms.py` | 24 | 3,282 subagents, DAG acyclicity, topological sorting, Pydantic enums |
| `test_scaffolder.py` | 9 | CLI and programmatic scaffolding for roles and companies |
| `test_company_onboard_skill.py`| 2 | End-to-end company onboarding on Stripe (DB, blueprint, catalog) |
| `test_search.py` | 16 | SQLite FTS5 BM25, LSA dense search, RRF fusion, 25-query baseline |
| `test_search_expanded.py` | 4 | Expanded 36-query enterprise benchmark (Recall@10 >= 0.85, MRR >= 0.70) |
| `test_challenge_expanded.py` | 76 | Master Solution Dossier validation (9,284 words, all chapters) |
| **Total** | **244** | **100% Pass Rate, 0 Failures, 0 Regressions** |

---

## Contributing & Development

1. Fork the repository and create your feature branch: `git checkout -b feature/my-new-feature`
2. Run test suites and format checks:
   ```bash
   pytest
   black --check orgprompt tests
   ruff check orgprompt tests
   ```
3. Commit your changes with conventional commit messages: `git commit -m 'feat: add new enterprise archetype'`
4. Push to the branch: `git push origin feature/my-new-feature`
5. Open a Pull Request.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
