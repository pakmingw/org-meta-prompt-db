# Teamwork Project Prompt — Draft (Phase 5 & 6 Expansion)

> Status: Completed — VICTORY CONFIRMED (244/244 tests passing; published at https://github.com/pakmingw/org-meta-prompt-db)
> Goal: Craft prompt → get user approval → delegate to teamwork_preview
> Requested team: [none — teamwork routes from the description]

Expand and upgrade the Organizational Knowledge Graph and Professional Role Meta-Prompting Database in `/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db` so that we have an empirically grounded model for **every Fortune 500 enterprise (`>= 500` companies)** and **how every individual role (`500–600+` canonical roles) works day-to-day**, enabling us to **instantly scaffold a tailored recommendation of the GenAI Tooling AND the Personal Subagent Swarm** needed to help any individual, division, or enterprise do their job. Actively use `search_web` and Gemini 4 Argon High's long context (`Model: inherit`) to ground all Fortune 500 profiles, role workflows, software tooling stacks, and subagent swarm architectures in authentic public information.

Working directory: /home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db
Integrity mode: development

## Architectural Critique of Current Build (To Resolve in This Expansion)

1. **From Monolithic Single-Role Prompt to Personal Subagent Swarm ("Role-in-a-Box")**: The current build models each role only as a single monolithic prompt inside a macro committee. Real enterprise professionals juggle document drafting, spreadsheet modeling, slide creation, meetings, inbox triage, and specialist software. Every canonical role must now be backed by a decomposed **Personal Subagent Swarm (`4–7` specialized subagents working *for* that individual)** alongside their core role prompt.
2. **From Abstract Artifacts to Day-to-Day Work Anatomy & Dual-Layer Tooling**: The current build lists high-level output artifacts without modeling *how* individuals work day-to-day or *what tools* they use. Every role must now map its daily/weekly workflows to both **Horizontal Productivity Tooling** (`WORD_PROCESSOR`, `SPREADSHEET_PROCESSOR`, `SLIDE_PRESENTER`, `MEETING_NOTE_TAKER`, `COMMUNICATION_TRIAGE`, `BI_ANALYTICS`) and **Vertical Domain Systems** (e.g., ERP/SAP, CRM/Salesforce, EHR/Epic, EDA/Synopsys, CAD, Bloomberg, IDE, ServiceNow).
3. **From 48 Exemplars to Complete Fortune 500 Coverage**: The database must expand from 48 exemplar organizations to cover **all 500 companies in the Fortune 500** (`>= 500` companies mapped across `500–600+` canonical roles with `>= 15,000` company-to-role employment edges in the Knowledge Graph).
4. **From Single Grand-Challenge Runner to Instant Enterprise & Role Scaffolder**: We need an instant scaffolding engine (`orgprompt scaffold`) that takes any Fortune 500 company, division, individual role, or customer scenario and immediately outputs a deployable **GenAI Tooling Build Plan + Subagent Swarm Configuration**.

## Requirements

### R1. Complete Fortune 500 Enterprise Catalog & Role Graph Expansion (`500+` Companies, `500–600+` Roles)
Using active `search_web` mining and long-context synthesis, expand the organization registry in `data/org_knowledge_base.db` to include **all 500 companies in the Fortune 500** (in addition to existing global frontier exemplars, totaling `>= 500` companies). Record each Fortune 500 company's rank, macro industry, sub-sector, business model, operating archetype, and functional organizational units. Expand the canonical role taxonomy from 340 roles to **`500–600+` distinct canonical roles** across all Fortune 500 functions, and populate **`>= 15,000` company-to-role employment edges (`EMPLOYS_ROLE`)** in SQLite and the NetworkX Knowledge Graph connecting all 500 Fortune 500 companies to the canonical roles they employ.

### R2. Day-to-Day Individual Work Anatomy & Dual-Layer Tooling Taxonomy
Design and populate relational tables and Knowledge Graph nodes (`tools`, `role_use_cases`, `role_tooling`) capturing how individuals in every canonical role (`500+` roles) work day-to-day:
- **Horizontal Productivity Tooling Archetypes**: `WORD_PROCESSOR` (document/memo/contract/RFC authoring), `SPREADSHEET_PROCESSOR` (financial/quantitative/capacity modeling & tabular data processing), `SLIDE_PRESENTER` (executive/board/client presentation decks), `MEETING_NOTE_TAKER` (meeting transcription, decision logging, action-item dispatch), `COMMUNICATION_TRIAGE` (email/chat/escalation orchestration), and `BI_ANALYTICS` (dashboards & SQL/KPI reporting).
- **Vertical Domain-Specific Tooling**: Enterprise & technical platforms specific to each role and industry (e.g., SAP S/4HANA, Salesforce, Epic EHR, Synopsys/Cadence EDA, Siemens NX, Bloomberg Terminal, 3GPP Protocol Analyzers, SCADA/EMS, LIMS, ServiceNow, Git/IDE/CI-CD).
- **Primary Day-to-Day Job Use Cases**: Every canonical role (`500+` roles) must have `>= 4` concrete daily/weekly operational use cases (`>= 2,000` total use cases) detailing the workflow trigger, inputs consumed, horizontal + domain tools used, cognitive bottlenecks, and output artifacts produced.

### R3. Per-Role Personal Subagent Swarm ("Role-in-a-Box") & GenAI Tooling Build Plan
For every canonical role (`500+` roles), compile and persist:
1. **A Personal Subagent Swarm Blueprint (`role_subagent_swarms` table)**: A coordinated swarm of `4–7` specialized subagents designed to help that individual execute their day-to-day job (including a *Role Chief-of-Staff Orchestrator*, *Word-Processor Drafter Subagent*, *Spreadsheet/Quantitative Modeler Subagent*, *Slide Narrative & Deck Subagent*, *Meeting Note & Action-Graph Subagent*, *Domain System/MCP Specialist Subagent*, and *Quality/Compliance Critic Subagent*), complete with subagent system prompts, tool/MCP bindings, interaction DAG, and human-in-the-loop checkpoints.
2. **A Per-Role Generative AI Tooling Build Plan (`role_genai_plans` table + Section 7 of System Prompt)**: Concrete engineering blueprint for building GenAI into each horizontal tool (`WORD_PROCESSOR`, `SPREADSHEET_PROCESSOR`, `SLIDE_PRESENTER`, `MEETING_NOTE_TAKER`) and vertical domain system used by that role (specifying long-context/RAG architecture, multimodal I/O, MCP integrations, evaluation metrics, HITL guardrails, and quantified productivity/ROI impact). Upgrade every role's compiled System Prompt to include **Section 7: Day-to-Day Tooling, GenAI Build Plan & Personal Subagent Swarm Protocol**.

### R4. Instant Enterprise & Role Scaffolder (`orgprompt scaffold`), Hybrid Search Upgrade & End-to-End Verification
- **Local Hybrid Search Expansion**: Index all `500+` Fortune 500 companies, `500+` canonical roles, day-to-day use cases, horizontal/vertical tools, GenAI build plans, and subagent swarm specs in the 100% local Hybrid Search Engine (SQLite FTS5 BM25 + local dense LSA embeddings + RRF + Knowledge Graph traversal).
- **Instant Scaffolding Engine & CLI (`orgprompt scaffold`)**:
  - `orgprompt scaffold role`: Given any role ID or natural-language job description (and optional Fortune 500 company context), instantly scaffold a deployable **Individual Role Subagent Swarm + GenAI Tooling Recommendation Package** (JSON + Markdown runbook).
  - `orgprompt scaffold company`: Given any Fortune 500 company name (and optional division or business problem), traverse the company's Knowledge Graph to scaffold an **Enterprise/Division GenAI Tooling Roadmap & Multi-Role Subagent Swarm Architecture** showing how each role's personal subagent swarm collaborates across the organization.
- **Grand Challenge & Dossier Upgrade**: Update the Grand Challenge runner and Master Solution Dossier (`artifacts/grand_challenge_dossier.md`, `>= 7,500` words) to demonstrate end-to-end enterprise scaffolding—including the per-role personal subagent swarms and horizontal/domain GenAI tooling build plans for the synthesized cross-functional team.

### R5. Company-by-Company Mega-Output Encyclopedia & GitHub Repository Publication (`https://github.com/pakmingw`)
- Using the Gemini 4 Argon (High) Mega-Output Subagent Prompt (`/home/pakmingw/.gemini/antigravity/brain/1e96291d-9d64-4bac-9f19-67c0822cf354/fortune500_deep_expansion_subagent_prompt.md`), generate the multi-volume **Company-by-Company Fortune 500 Operating Model & Internet Role Comparison Encyclopedia** (`artifacts/fortune500_encyclopedia/`) and `company_internet_comparisons` SQLite table covering all 500 companies one by one.
- Package all code, tests, documentation (`README.md`), and artifacts into a clean Git repository and publish/push it to a new GitHub repository under `https://github.com/pakmingw` (e.g., `https://github.com/pakmingw/org-meta-prompt-db`).

### R6. Antigravity Skills for Role Search & Live Deep-Research Company Onboarding (`orgprompt company onboard`)
- Build a programmatic **Company Onboarding & GenAI Blueprint Engine** (`orgprompt/onboarding/` and CLI command `orgprompt company onboard`) that accepts a company name plus deep-research structured inputs (publicly traded status/ticker/financials, business challenges, divisions/operating units, canonical & bespoke roles), inserts/updates the company in `data/org_knowledge_base.db` (`fortune500_companies`, `org_units`, `canonical_roles`, `company_role_edges`, `company_internet_comparisons`), updates the skill's `references/onboarded_companies.md` index, and generates a comprehensive **"Apply Generative AI Everywhere" Enterprise Blueprint** (`artifacts/company_onboarding/<slug>_genai_blueprint.md`) mapping GenAI tooling (`Word Processor`, `Spreadsheet/Processor`, `Slide Presenter`, `Meeting Note Taker`, `Comm Hub` + domain systems) and **Personal Subagent Swarms** across every division and role to solve the company's specific business challenges.
- Create and install two official Antigravity Skills in **both** `.agents/skills/` (committed to the Git repo) and `/home/pakmingw/.gemini/config/skills/` (global discovery):
  1. `org-role-search-and-scaffold` (`SKILL.md` + helper scripts/references): Search the database for roles, prompts, day-to-day workflows, and tools, and scaffold role/team subagent swarms.
  2. `org-company-deep-onboard` (`SKILL.md` + helper scripts + `references/onboarded_companies.md`): End-to-end runbook teaching the agent how to take any company name from the user, launch deep `search_web` research into its organization, publicly traded status, and business challenges, invoke `orgprompt company onboard` to update the database and skill, and return a complete enterprise-wide Generative AI transformation recommendation.

## Acceptance Criteria

### Fortune 500 & Expanded Knowledge Graph Completeness
- [ ] Database contains `>= 500` distinct Fortune 500 companies (with authentic company names, Fortune 500 ranks, industry mappings, and operating archetypes mined via `search_web`), `>= 16` macro industries, `>= 150` functional operating units, and `>= 500` distinct canonical roles.
- [ ] Knowledge Graph contains `>= 15,000` `EMPLOYS_ROLE` edges linking Fortune 500 companies to their canonical roles, with `0` orphaned roles and `0` graph invariant violations across all `500+` canonical roles.

### Day-to-Day Use Cases, Dual-Layer Tooling & Personal Subagent Swarms
- [ ] Every one of the `500+` canonical roles has `>= 4` structured day-to-day job use cases (`>= 2,000` total use cases) explicitly mapped to both horizontal productivity tooling (`WORD_PROCESSOR`, `SPREADSHEET_PROCESSOR`, `SLIDE_PRESENTER`, `MEETING_NOTE_TAKER`, etc.) and domain-specific software tools.
- [ ] Every one of the `500+` canonical roles has a complete, non-stubbed **Personal Subagent Swarm Blueprint** (`4–7` specialized subagents with prompts, tool/MCP bindings, and handoff DAG in `role_subagent_swarms`) AND a **Generative AI Tooling Build Plan** (`role_genai_plans` + **Section 7** of its compiled System Prompt, with `100%` uniqueness across all `500+` role prompts, `>= 3,000` characters per prompt, and `0` stubs).

### Scaffolder Engine, Hybrid Search & Verification Suite
- [ ] Local Hybrid Search Engine passes an expanded retrieval benchmark (`>= 35` queries spanning single-domain roles, cross-industry teams, Fortune 500 company roles, day-to-day tooling use cases, and GenAI/subagent swarm queries) with `Recall@10 >= 0.85` and `MRR >= 0.70`.
- [ ] `orgprompt scaffold role` and `orgprompt scaffold company` CLI commands and Python APIs execute cleanly for any queried Fortune 500 company or role, exporting validated JSON + Markdown scaffolding packages, and `artifacts/grand_challenge_dossier.md` (`>= 7,500` words) includes the complete GenAI Tooling & Personal Subagent Swarm Blueprints.
- [ ] Complete automated test suite (`pytest`) passes `100%` of tests (`0` failures, `0` skipped) verifying all Phase 1–6 requirements, boundaries, and adversarial stress tests.

---
*Next: when approved → delegate via invoke_subagent (see Delegation Protocol)*
