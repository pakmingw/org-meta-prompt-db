---
name: org-role-search-and-scaffold
description: >-
  Search the Organizational Knowledge Graph for enterprise canonical roles,
  day-to-day use cases, dual-layer tooling, and personal subagent swarms ("Role-in-a-Box"),
  and instantly scaffold executable JSON and Markdown runbooks.
  ACTIVATE this skill when the user asks to find, inspect, generate, or scaffold
  canonical roles, system prompts, operational workflows, or team swarms.
---

# Org Role Search & Instant Scaffolder (`org-role-search-and-scaffold`)

A production Antigravity skill for discovering, evaluating, and instantly scaffolding enterprise professional roles from the 547-role Organizational Knowledge Graph (OKG) spanning 16 macro industries and all 500 Fortune 500 enterprises.

## Core Capabilities

1. **Local Hybrid Semantic Search**:
   - Fuses SQLite FTS5 BM25 lexical retrieval and subword character LSA dense semantic vector search via Reciprocal Rank Fusion ($k=60$).
   - Returns verifiable dual-score attribution tracking (`sparse_score`, `dense_score`, `rrf_score`).
   - Supports Knowledge Graph expansion to assemble cross-functional teams.

2. **Personal Subagent Swarms ("Role-in-a-Box")**:
   - Every role is backed by a 6-agent acyclic swarm (`CHIEF_OF_STAFF`, `DOCUMENT_DRAFTER`, `QUANTITATIVE_MODELER`, `DECK_PRESENTER`, `MEETING_GRAPH`, `QUALITY_CRITIC`).
   - Includes bound MCP tools, topological DAG interaction paths, and Human-in-the-Loop (HITL) checkpoints.

3. **Day-to-Day Work Anatomy & Dual-Layer Tooling**:
   - Covers >= 4 operational use cases per role (trigger, cadence, inputs, outputs, bottlenecks).
   - Maps 6 horizontal tool archetypes (`WORD_PROCESSOR`, `SPREADSHEET_PROCESSOR`, `SLIDE_PRESENTER`, `MEETING_NOTE_TAKER`, `COMMUNICATION_TRIAGE`, `BI_ANALYTICS`) and vertical domain platforms (SAP, Epic EHR, Bloomberg, Synopsys, Salesforce, Workday, etc.).

4. **Instant Multi-Format Scaffolding**:
   - Exports executive Markdown runbooks and machine-readable JSON packages ready for autonomous agent execution.

---

## Workflows & Usage

### 1. Searching for Roles via CLI

Search the database with hybrid RRF retrieval:
```bash
python3 -m orgprompt.cli search query "FPGA low-latency market making" --top-k 5
```

Or run the skill helper script:
```bash
python3 scripts/search_and_scaffold.py search --query "Chief Information Security Officer" --top-k 3
```

### 2. Scaffolding a Canonical Role Runbook

Generate a complete Markdown runbook for a role:
```bash
python3 -m orgprompt.cli scaffold role fin_chief_investment_officer --company "JPMorgan Chase" --format markdown --output artifacts/runbooks/cio_runbook.md
```

Or export as structured JSON:
```bash
python3 -m orgprompt.cli scaffold role tech_principal_distributed_training_engineer --format json --output artifacts/runbooks/distributed_engineer.json
```

### 3. Scaffolding an Enterprise Company

Scaffold an entire company's division structure, employed roles, and swarms:
```bash
python3 -m orgprompt.cli scaffold company Walmart --division "Supply Chain" --format markdown --output artifacts/runbooks/walmart_scaffold.md
```

### 4. Programmatic Python API

```python
from orgprompt.scaffolder import RoleScaffolder, CompanyScaffolder
from orgprompt.search.hybrid import HybridSearchEngine

# 1. Search for roles
engine = HybridSearchEngine.build_from_db()
results = engine.search("Optical link budget Shannon capacity", top_k=5)
top_role = results[0]

# 2. Scaffold role runbook
scaffolder = RoleScaffolder.build_from_db()
pkg = scaffolder.scaffold_role(top_role.slug, company_name="AT&T")
print(pkg.to_markdown())

# 3. Scaffold enterprise company
comp_scaffolder = CompanyScaffolder.build_from_db()
comp_pkg = comp_scaffolder.scaffold_company("Apple")
print(comp_pkg.to_json())
```
