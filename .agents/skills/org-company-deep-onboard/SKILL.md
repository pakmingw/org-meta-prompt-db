---
name: org-company-deep-onboard
description: >-
  Deeply research and onboard any enterprise or private corporation into the
  Organizational Knowledge Graph, wire graph employment edges, synthesize bespoke
  roles with full 7-section prompts and personal subagent swarms, update the skill catalog,
  and deliver a comprehensive "Apply Generative AI Everywhere" strategic blueprint.
  ACTIVATE this skill when the user asks to onboard a company, research an organization,
  or create an enterprise-wide GenAI transformation blueprint.
---

# Enterprise Deep Onboarding & GenAI Strategic Blueprint Skill (`org-company-deep-onboard`)

A production Antigravity skill that enables autonomous agents to take any enterprise or private company name, launch deep multi-source research into its operating architecture, register it in the Organizational Knowledge Graph (OKG), wire bipartite employment edges, synthesize bespoke canonical roles with 6-agent personal swarms, update skill registries, and deliver an authoritative "Apply Generative AI Everywhere" strategic blueprint.

## Core Capabilities

1. **Deep Organization Research**:
   - Analyzes public capital structure, SEC 10-K/10-Q filings (or venture status), annual revenue, headquarters, and governance.
   - Identifies operating archetype (`UNIFICATION`, `COORDINATION`, `REPLICATION`, `DIVERSIFICATION`, `PLATFORM_ECOSYSTEM`) and business model (`MULTI_SIDED_PLATFORM`, `RECURRING_SUBSCRIPTION_SAAS`, etc.).
   - Mines authentic functional units, operating divisions, and bespoke job architectures.
   - Synthesizes 3–6 mission-critical business and operational bottlenecks.

2. **Programmatic Knowledge Graph Onboarding**:
   - Registers enterprise in SQLite `fortune500_companies` (assigning contiguous ranks for non-F500 corporations).
   - Wires high-density `employs_role` edges linking company divisions to canonical roles.
   - Synthesizes bespoke roles with full 7-section meta-prompts (>=3,000 chars), 5 day-to-day use cases, dual-layer tooling, and 6-agent acyclic personal subagent swarms.
   - Enforces 0 graph invariant violations (`validate_expansion_invariants`).

3. **Enterprise "Apply Generative AI Everywhere" Blueprint**:
   - Generates an exhaustive strategic blueprint saved to `artifacts/company_onboarding/<slug>_genai_blueprint.md` (>= 5,000 characters).
   - Maps 5 horizontal GenAI copilots (`Word Processor`, `Spreadsheet Modeler`, `Slide Presenter`, `Meeting Note Taker`, `Communication Hub`).
   - Maps vertical domain software copilots across all operating divisions.
   - Provisions 6-agent personal subagent swarms (`Role-in-a-Box`) with human-in-the-loop gates.
   - Delivers an 18-month phased implementation roadmap with quantified ROI projections.

4. **Dynamic Catalog Maintenance**:
   - Automatically appends onboarded enterprises to `references/onboarded_companies.md`.

---

## Autonomous Agent Execution Runbook

When the user asks:
> *"Please onboard <Company Name> into the database and give me a recommendation on how to apply generative AI to them everywhere."*

Follow this exact 5-step runbook:

### Step 1: Launch Deep Research
Use `search_web` to inspect:
- Legal entity name, public ticker or private venture status, estimated annual revenue, headquarters.
- Business model and operating archetype.
- 4–6 core operating divisions (e.g. from 10-K or organizational disclosures).
- 3–5 high-priority business and operational challenges.
- 2–5 authentic bespoke role titles specific to this company.

### Step 2: Execute Programmatic Onboarding
Invoke `CompanyOnboardingEngine` via CLI:
```bash
python3 -m orgprompt.cli company onboard "Stripe" \
  --ticker "STRIPE" \
  --industry "Finance" \
  --subsector "Fintech & Global Payment Infrastructure" \
  --revenue 14.0 \
  --challenges "Global payment latency & cross-border authorization rates; Multi-jurisdiction tax & AML compliance; Developer platform API zero-downtime upgrades"
```

Or pass a rich research JSON file:
```bash
python3 -m orgprompt.cli company onboard "Stripe" --research-file "research/stripe_dossier.json"
```

### Step 3: Verify Artifacts and Graph Invariants
Confirm:
1. Company inserted in SQLite `fortune500_companies` and `employs_role` edges created.
2. Any bespoke roles created with full 7-section prompts, 5 use cases, and 6 subagents.
3. Graph invariants valid (0 orphan roles, 0 violations).
4. `artifacts/company_onboarding/<slug>_genai_blueprint.md` generated (>= 5,000 characters).
5. Catalog `references/onboarded_companies.md` updated in both skill locations.

### Step 4: Deliver Strategic Recommendation to User
Present the executive summary, horizontal copilot architecture, vertical domain integrations, personal swarm topology, and phased ROI roadmap directly to the user, citing the generated blueprint artifact.
