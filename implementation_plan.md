# Implementation Plan: Fortune 500 & Personal Subagent Swarm Expansion

## Executive Summary
This expansion elevates the Organizational Knowledge Graph and Meta-Prompting Database from 48 exemplar organizations and 336 roles to:
1. Complete Fortune 500 coverage (`>= 500` companies with rank, industry, business model, operating archetype, functional units, mined via `search_web`).
2. Canonical Role Taxonomy expansion to `500–600+` distinct roles (540 roles) with `>= 15,000` `EMPLOYS_ROLE` edges in SQLite & NetworkX.
3. Day-to-Day Individual Work Anatomy & Dual-Layer Tooling (`tools`, `role_use_cases`, `role_tooling`, `>= 4` use cases per role, `>= 2,000` use cases).
4. Personal Subagent Swarms ("Role-in-a-Box") (`role_subagent_swarms` with 4–7 specialized subagents per role) & GenAI Tooling Build Plans (`role_genai_plans` + Section 7 of System Prompts, `>= 3,000` chars/prompt, 100% unique).
5. Instant Scaffolder CLI (`orgprompt scaffold role`, `orgprompt scaffold company`), Local Hybrid Search Index expansion (>=35 queries benchmark), and Grand Challenge Dossier expansion (`>= 7,500` words).
6. Company-by-company Fortune 500 Mega-Output generation and Internet Comparison Encyclopedia (`artifacts/fortune500_encyclopedia/` multi-volume) & `company_internet_comparisons` SQLite table.
7. Company Onboarding & Enterprise GenAI Blueprint Engine (`orgprompt company onboard` + `artifacts/company_onboarding/<slug>_genai_blueprint.md`).
8. Two Antigravity Skills installed in both `.agents/skills/` and `/home/pakmingw/.gemini/config/skills/` (`org-role-search-and-scaffold` and `org-company-deep-onboard`).
9. Clean packaging and publication to GitHub under `https://github.com/pakmingw/org-meta-prompt-db`.

---

## Milestone Breakdown & Delegation Strategy

### Phase 0: Survey & Schema Analysis (COMPLETE)
- **Explorer 1**: Codebase & DB Architecture Survey — 100% test pass verified (149/149), zero-regression seeding strategy established, additive schema designed.
- **Spec-Miner 2**: Fortune 500 Catalog & Role Taxonomy — official 70th edition Fortune 500 (#1 to #500), 540 canonical roles (+198 enterprise roles), 18,500 `EMPLOYS_ROLE` edges specified.
- **Explorer 3**: Tooling taxonomy, subagent swarms, scaffolder, and search expansion designs reviewed and synthesized.

### Milestone 1A (Exp-M1A): Fortune 500 Enterprise Catalog & Role Graph Expansion
- **Scope**:
  - Add `fortune500_companies` and `employs_role` table in SQLite schema (`data/org_knowledge_base.db`) and NetworkX.
  - Expand canonical roles to >= 540 clean roles (547 clean roles) with all 4 graph invariants and Level-2 `## 1.` through `## 6.` prompt headers.
  - Populate >= 500 authentic Fortune 500 companies (#1 Walmart to #500 O-I Glass, zero synthetic placeholders) and >= 15,000 `EMPLOYS_ROLE` edges.
  - Relocate all role definitions into production package (`orgprompt/db/roles_families_1_9.py` and `orgprompt/db/roles_families_10_13.py`), removing `.agents/` imports.
  - Update `RoleGenerator.generate_role()` to automatically wire default `employs_role` edges for dynamically generated roles to prevent invariant orphans.
  - Ensure 0 orphan roles, 0 graph invariant violations, 100% pytest pass.
- **Workers**:
  - `Worker 1-3`: Initial schema, catalog, roles, and seeder implementation.
  - `Worker 4 (Remediation)`: Execute all 6 remediation actions (relocate roles_families_1_9, replace 411 synthetic companies with authentic mined companies, add 10 roles to reach 547 clean canonical roles, update prompt headers to `## N.`, wire RoleGenerator `employs_role`, clean conftest and database, re-seed and verify tests).
- **Gates**: Reviewers (2), Challengers (2), Forensic Auditor (clean verification required).

### Milestone 1B (Exp-M1B): Fortune 500 Mega-Output Company-by-Company Encyclopedia & Internet Role Comparison
- **Scope**:
  - Author `orgprompt/db/seed_encyclopedia.py` to:
    - Read all 500 authentic Fortune 500 companies from `data/org_knowledge_base.db` and `fortune500_catalog.py`.
    - Generate multi-volume Markdown encyclopedia in `artifacts/fortune500_encyclopedia/volume_{N}_ranks_{start}_{end}.md` (5 volumes of 100 companies each: Vol 1: 1-100, Vol 2: 101-200, Vol 3: 201-300, Vol 4: 301-400, Vol 5: 401-500).
    - For each company: SEC 10-K operating divisions, authentic public bespoke job titles, mapped DB canonical roles via `employs_role`, delta analysis, alignment score (0.0–1.0), and tailored personal subagent swarm recommendation.
    - Populate `company_internet_comparisons` SQLite table in `data/org_knowledge_base.db` for all 500 companies with 0 nulls and 100% foreign key consistency.
  - Create `tests/test_encyclopedia.py` verifying:
    - Exactly 500 rows in `company_internet_comparisons`.
    - Contiguous ranks 1..500 without gaps.
    - Non-empty `internet_divisions_json`, `internet_bespoke_roles_json`, `delta_analysis_md`, `tailored_swarm_recommendation_md`.
    - Mean alignment score >= 0.70.
    - All 5 encyclopedia volume markdown files exist, are >= 50,000 characters each, and cover all 500 companies.
- **Workers**:
  - `Worker 3 (Encyclopedia Builder)`: Author generator script `orgprompt/db/seed_encyclopedia.py` (< 250 lines of procedural algorithmic Python), generate all 5 volumes in `artifacts/fortune500_encyclopedia/`, populate SQLite table `company_internet_comparisons` with 500 rows, author `tests/test_encyclopedia.py`, and run verification.
- **Status**: Completed (CLEAN Forensic Audit Passed, 5 volumes 2.27 MB, 500 rows in SQLite, 193/193 tests pass).
- **Gates**: Passed (Reviewer 1 APPROVE, Reviewer 2 APPROVE, Challenger 1 APPROVE, Forensic Auditor CLEAN).

### Milestone 2 (Exp-M2): Day-to-Day Work Anatomy & Dual-Layer Tooling
- **Scope**:
  - Verify relational tables `tools`, `role_use_cases`, `role_tooling` in `schema.sql`.
  - Author `orgprompt/db/seed_tooling.py` (procedural Python < 300 lines) to populate:
    - 6 Horizontal Tool archetypes (`WORD_PROCESSOR`, `SPREADSHEET_PROCESSOR`, `SLIDE_PRESENTER`, `MEETING_NOTE_TAKER`, `COMMUNICATION_TRIAGE`, `BI_ANALYTICS`) with real vendor examples and typical artifacts.
    - >= 40 Vertical Domain software platforms across all 16 industries (Bloomberg, FactSet, SAP S/4HANA, Salesforce, Epic EHR, Synopsys, Siemens NX, Relativity, Workday, etc.).
    - >= 4 authentic operational use cases per canonical role across all 547 roles (>= 2,188 total use cases in `role_use_cases`), each specifying cadence, trigger, inputs, horizontal tools, domain software, cognitive bottlenecks, and output artifacts.
    - >= 2,500 role-tooling associations in `role_tooling`.
  - Author `tests/test_tooling_use_cases.py` asserting:
    - `tools` count >= 45.
    - `role_use_cases` count >= 2,000.
    - Every single role in `canonical_roles` has >= 4 use cases (0 roles with < 4 use cases).
    - Foreign key referential integrity across all tables.
    - Valid non-empty JSON arrays and zero null fields.
  - Run full pytest suite to verify 100% pass (0 failures).
- **Workers**:
  - `Worker 1 (Tooling & Use Cases Builder)`: Implement `seed_tooling.py`, seed database, author `tests/test_tooling_use_cases.py`, and run verification.
- **Status**: Completed (Clean Forensic Audit Passed, 51 tools, 2,735 use cases, 3,282 tooling associations, seed_tooling 307 LOC, 209/209 tests pass).
- **Gates**: Passed (Reviewer 1 APPROVE, Reviewer 2 APPROVE, Challenger 1 APPROVE, Forensic Auditor CLEAN).

### Milestone 3 (Exp-M3): Personal Subagent Swarms ("Role-in-a-Box") & GenAI Tooling Build Plans
- **Scope**:
  - Add relational tables `role_subagent_swarms` and `role_genai_plans` to `schema.sql` and `data/org_knowledge_base.db`.
  - Add Pydantic models `RoleSubagentSwarm` and `RoleGenAIPlan` in `orgprompt/models.py`.
  - Author `orgprompt/db/seed_swarms_plans.py` (< 350 lines of procedural Python):
    - For all 547 canonical roles: generate 4–7 specialized subagents per role in `role_subagent_swarms` (Role Chief-of-Staff, Word-Processor Drafter, Spreadsheet Modeler, Slide Narrative Subagent, Meeting Note Subagent, Domain Specialist, Quality Critic) with prompts, tool bindings, interaction DAG, and HITL checkpoints (>= 2,500 total swarm subagent records).
    - For all 547 canonical roles: generate concrete GenAI tooling build plan in `role_genai_plans` across horizontal and vertical systems (547 records).
    - Upgrade prompt compilation to include **Section 7: Day-to-Day Tooling, GenAI Build Plan & Personal Subagent Swarm Protocol**, bringing every single canonical role prompt to >= 3,000 characters with 100% uniqueness and 0 stubs.
  - Author `tests/test_subagent_swarms.py` verifying:
    - `role_subagent_swarms` count >= 2,500 (0 roles with < 4 subagents).
    - `role_genai_plans` count = 547.
    - All 547 role prompts are >= 3,000 characters each and contain all 7 numbered sections (`## 1.` through `## 7.`).
    - 100% prompt uniqueness across all 547 roles and 0 stubs.
    - Foreign keys and constraints clean.
  - Run full pytest test suite (100% pass, 0 regressions).
- **Workers**:
  - `Worker 1 (Swarm & GenAI Plan Builder)`: Author `seed_swarms_plans.py` (< 350 LOC), seed DB, upgrade prompts, author `tests/test_subagent_swarms.py`, and run verification.
  - `Worker 2 (Remediation Builder)`: Apply Challenger 1 remediations:
    1. Disentangle interaction DAG cycles in `seed_swarms_plans.py` (ensure MEETING_GRAPH -> CHIEF_OF_STAFF -> specialists -> DECK/CRITIC -> PRINCIPAL is strictly acyclic).
    2. Add `VALID_SUBAGENT_ROLES = Literal[...]` enum validation to `RoleSubagentSwarm.subagent_role` in `orgprompt/models.py`.
    3. Add DAG acyclicity (`nx.is_directed_acyclic_graph`, `nx.topological_sort`) and Pydantic validation tests in `tests/test_subagent_swarms.py`.
    4. Re-run `python3 -m orgprompt.db.seed_swarms_plans` and verify all tests pass.
- **Status**: Completed (Clean Forensic Audit Passed, Reviewer 1 & 2 Approved, Challenger 2 Approved, 100% Acyclic DAGs, Pydantic Enum Validated, 218/218 tests pass).
- **Gates**: Passed (Reviewer 1 APPROVE, Reviewer 2 APPROVE, Challenger 2 APPROVE, Forensic Auditor CLEAN).

### Milestone 4 (Exp-M4): Instant Scaffolder CLI, Onboarding Engine, Antigravity Skills & Search Upgrade
- **Scope**:
  1. **Instant Scaffolder CLI & APIs** (`orgprompt/scaffolder/`):
     - `role_scaffolder.py`: Export JSON and Markdown runbooks for any canonical role (7-section prompt, 6-agent swarm DAG, tools, HITL checkpoints).
     - `company_scaffolder.py`: Export JSON and Markdown runbooks for any Fortune 500 or onboarded company.
     - CLI integration in `orgprompt/cli.py`: `orgprompt scaffold role <id_or_slug>` and `orgprompt scaffold company <name_or_ticker>`.
  2. **Programmatic Company Onboarding & Enterprise GenAI Blueprint Engine** (`orgprompt/onboarding/`):
     - `engine.py`: `CompanyOnboardingEngine` accepting deep-research findings (publicly traded status, financials, business challenges, operating units, bespoke roles), inserting/updating company in SQLite DB, synthesizing any new bespoke roles with full 7-section prompts, day-to-day use cases, dual-layer tools, and 6-agent acyclic swarms while strictly preserving 0 graph invariant violations.
     - `blueprint_generator.py`: Generates complete "Apply Generative AI Everywhere" Blueprint in `artifacts/company_onboarding/<slug>_genai_blueprint.md`.
     - Updates skill's dynamic catalog `references/onboarded_companies.md`.
     - CLI integration: `orgprompt company onboard <name> [--research-file <path>] [--ticker <ticker>] [--industry <ind>] [--challenges <text>]`.
  3. **Two Antigravity Skills**:
     - Installed in BOTH `/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/.agents/skills/` (committed to git, `.gitignore` allows `.agents/skills/`) AND `/home/pakmingw/.gemini/config/skills/`:
       - `org-role-search-and-scaffold/SKILL.md` (with `scripts/` and `references/`).
       - `org-company-deep-onboard/SKILL.md` (with `scripts/` and `references/onboarded_companies.md`).
  4. **Local Hybrid Search Upgrade** (`orgprompt/search/`):
     - Index all 500 Fortune 500 companies, 547 roles, use cases, tools, and swarms.
     - Expand benchmark suite to >= 35 queries (36 queries), asserting Recall@10 >= 0.85 and MRR >= 0.70.
  5. **Automated Test Suite**:
     - `tests/test_scaffolder.py`: CLI and programmatic scaffolding (9 tests).
     - `tests/test_company_onboard_skill.py`: End-to-end test of `orgprompt company onboard` on Stripe (real non-F500 company), verifying DB insertion, blueprint generation, skill reference catalog update, and 0 graph invariant violations (2 tests).
     - `tests/test_search_expanded.py`: Hybrid search across companies, roles, swarms, and >= 35 query benchmark (4 tests).
- **Workers**:
  - `Worker 1 (Exp-M4 Lead Builder)`: Implemented scaffolding, onboarding engine, CLI commands, 2 Antigravity skills in both locations, search engine expansion, and tests (completed hard handoff).
  - `Worker 2 (Exp-M4 Remediation Builder)`: Execute remediation:
    1. In `orgprompt/search/benchmark.py`: define `CANONICAL_25_BENCHMARK_QUERIES = DEFAULT_BENCHMARK_QUERIES[:25]` and `EXPANDED_36_BENCHMARK_QUERIES = DEFAULT_BENCHMARK_QUERIES`.
    2. In `tests/test_search.py`: update `test_retrieval_benchmark_runner_full_suite` and `test_retrieval_benchmark_hybrid_superiority` to use `CANONICAL_25_BENCHMARK_QUERIES` (or `benchmark_queries_25` fixture) when testing the in-memory 336-role `seeded_db`.
    3. In `orgprompt/scaffolder/role_scaffolder.py` and `company_scaffolder.py`: add guard clauses raising `KeyError` for empty or whitespace-only queries.
    4. Run `pytest tests/ -v` to ensure 233/233 tests pass with 0 failures, 0 regressions.
- **Status**: Completed (Clean Forensic Re-Audit Passed, 242/242 tests pass).
- **Gates**: Passed (Reviewer 1 APPROVE, Reviewer 2 APPROVE, Challenger 1 APPROVE, Forensic Auditor 2 CLEAN).

### Milestone 5 (Exp-M5): Dossier Upgrade, End-to-End Pytest Verification & Forensic Audit
- **Scope**:
  - Update Grand Challenge Master Solution Dossier (`artifacts/grand_challenge_dossier.md`) to >= 7,500 words with:
    - Chapter 10: Enterprise Scale Expansion — Fortune 500 Knowledge Graph & Internet Grounding (all 500 companies, SEC 10-K divisions, alignment analysis, 5 encyclopedia volumes).
    - Chapter 11: Micro-Operational Anatomy — Day-to-Day Tooling & Personal Subagent Swarms ("Role-in-a-Box") (6 horizontal tools, 45+ vertical platforms, 2,735 use cases, 3,282 subagents with strictly acyclic DAGs, Section 7 prompts >= 3,000 chars).
    - Chapter 12: Autonomous Execution Infrastructure — Instant Scaffolder CLI, Onboarding Engine & Antigravity Skills (`orgprompt scaffold`, `orgprompt company onboard`, dual skills in `.agents/skills/` and `~/.gemini/config/skills/`, 36-query search benchmark).
  - Verify word count strictly >= 7,500 words.
  - Automated test suite (`pytest`) passes 100% of tests with 0 failures, 0 skipped (242+ tests).
  - Reviewer verification, Challenger empirical stress test, and final Forensic Integrity Audit.
- **Workers**:
  - `Worker 1 (worker_m5_1)`: Author Chapters 10, 11, and 12 in `orgprompt/challenge/chapters/`, expand MasterDossierCompiler, author `tests/test_challenge_expanded.py`, compile dossier to 9,284 words, and run full test suite (244/244 pass).
- **Status**: Completed (Clean Forensic Audit Passed, 9,284 words, 244/244 pytests pass).
- **Gates**: Passed (Reviewer 1 APPROVE, Reviewer 2 APPROVE, Challenger 1 APPROVE, Forensic Victory Auditor CLEAN).

### Milestone 6 (Exp-M6): GitHub Repository Packaging & Publication (`pakmingw/org-meta-prompt-db`)
- **Scope**:
  1. **Production README.md**:
     - Author comprehensive, world-class documentation in `/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/README.md`.
     - Cover all architectural pillars: Fortune 500 Knowledge Graph (#1 to #500), 549 canonical roles, 26,900+ edges, 51 tools, 2,735 use cases, 3,282 subagents with strictly acyclic DAGs, 547 GenAI build plans, 5-volume encyclopedia (2.27 MB), Scaffolder CLI, Company Onboarding Engine, dual Antigravity skills, hybrid search engine, installation, CLI usage, and test verification (244/244 pytests passing).
  2. **Git Ignore Configuration**:
     - Ensure `.gitignore` explicitly ignores `.agents/teamwork/` (orchestrator coordination metadata) while tracking `!.agents/skills/` and `!.agents/skills/**`.
     - Ensure python bytecode, pytest caches, and scratch files are ignored.
  3. **Git Initialization & Clean Commit**:
     - Initialize git (`git init`) in `/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db`.
     - Configure local git identity (`pakmingw`).
     - Stage all tracked files (`git add .`).
     - Create clean, professional commit: `feat: enterprise fortune 500 knowledge graph and personal subagent swarms expansion`.
  4. **GitHub Publication**:
     - Check GitHub CLI (`gh auth status`) and remote configuration.
     - Create public repository `pakmingw/org-meta-prompt-db` on GitHub via `gh repo create pakmingw/org-meta-prompt-db --public --source=. --remote=origin --push` (or git remote push).
     - Verify remote tracking branch and remote URL: `https://github.com/pakmingw/org-meta-prompt-db`.
- **Workers**:
  - `Worker 1 (worker_m6_1)`: Execute README authoring, gitignore check, git init, commit, and GitHub push.
- **Status**: IN_PROGRESS
- **Gates**: Reviewer 1 (git commit & README verification), Forensic Victory Auditor (remote verification & cleanliness).

