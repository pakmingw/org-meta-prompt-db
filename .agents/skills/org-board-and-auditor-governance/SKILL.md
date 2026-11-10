---
name: org-board-and-auditor-governance
description: >-
  Summon industry-tailored Board of Directors slates, Independent Statutory /
  Forensic / Strategic / Domain Auditors, and 8-Section Superhuman Governance
  Profiles (`orgprompt.governance`) sitting above and outside management to
  audit company performance packets, expose Non-GAAP/capitalization spin, stress
  ROIC vs. WACC & SOTP value creation, and issue binding Board resolutions.
  ACTIVATE this skill when the user asks to convene a Board of Directors, run an
  independent financial/forensic/strategic/AI audit, evaluate a quarterly Board
  deck, challenge CEO/CFO capital allocation, or govern any public enterprise,
  indie film studio, or creator venture.
---

# Fiduciary Board of Directors & Independent Auditor Governance (`org-board-and-auditor-governance`)

Provides a dedicated **Fiduciary Oversight & Assurance Taxonomy Tier (`orgprompt.governance`)** located **strictly above and outside** the operating management org chart (`canonical_roles`).

- **Why Separate from Operating Management**: Operating executives (`CEO`, `CFO`, `CTO`, `Showrunner`) execute inside the hierarchy. Board Directors (`BOARD_DIRECTOR`) and Independent External Auditors (`INDEPENDENT_AUDITOR`) owe fiduciary and statutory duties (*Caremark*, *DGCL §141(a)*, *SOX 407*, *PCAOB AS 2201/2401*, *ASC 606/350/842/926*) to shareholders and public stakeholders—de-spinning management narratives, auditing cash conversion, policing `ROIC > WACC`, and gating executive incentives.
- **Workspace Root**: `/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db`

---

## Core Capabilities & CLI Commands

### 1. List All 18 Fiduciary Board & Independent Auditor Roles
- **6 Universal Seats**: Non-Executive Chair (`gov_lead_independent_board_chair`), Audit Committee SOX 407 Chair (`gov_audit_committee_financial_expert_chair`), Capital-Allocation / SOTP Director (`gov_capital_allocation_value_director`), Compensation & Succession Chair (`gov_compensation_succession_chair`), External Statutory & Forensic Auditor (`gov_external_statutory_forensic_auditor`), and Independent Strategic & AI Value Auditor (`gov_independent_strategic_value_auditor`).
- **12 Industry-Selected Specialist Directors & Domain Auditors**: Covering Tech/Frontier AI/Fab CapEx, Cyber/AI Safety, Bank Systemic Risk/CCAR, Biotech FDA Trials, Clinical Quality/SaMD Safety, Telco/Grid Regulated Infra, Cleared Defense/Aerospace, Manufacturing/Supply-Chain Quality, Retail/GMROI/Brand, Indie Film/YouTube/Creator Venture (`gov_media_creator_venture_board_partner`), Climate/CSRD/Works-Council Labor, and Special M&A/Spin-Off/Turnaround.

```bash
cd /home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db
python3 -m orgprompt.cli governance list-roles
python3 -m orgprompt.cli governance list-roles --category INDEPENDENT_AUDITOR --format markdown
```

### 2. Assemble an Industry- or Company-Specific Board & Audit Slate
Resolves any of the `507+` companies in `data/org_knowledge_base.db` (e.g., `Orange France`, `Apple`, `A24`, `Blumhouse Productions`, `Beast Industries`, `Kurzgesagt`) or any of the `16` macro industries across `PUBLIC_ENTERPRISE` and `VENTURE_OR_BOUTIQUE` stages:

```bash
python3 -m orgprompt.cli governance board-slate --company "Orange France" --output artifacts/governance_roles/orange_board_slate.md
python3 -m orgprompt.cli governance board-slate --company "A24" --stage VENTURE_OR_BOUTIQUE
python3 -m orgprompt.cli governance board-slate --industry telecommunications --json
```

### 3. Inspect or Synthesize 8-Section Superhuman Board Directors & Auditors (`34,000+` chars)
Three flagship Superhuman Governance profiles are pre-seeded in `superhuman_governance_profiles` (and `artifacts/governance_roles/`):
1. `superhuman_gov_capital_allocation_board_director` — Multi-segment ROIC/WACC, SOTP, OpEx-to-CapEx & GPU useful-life discipline.
2. `superhuman_gov_forensic_strategic_auditor` — PCAOB AS 2401 forensic accounting fused with McKinsey outside-in cohort & AI ROI verification.
3. `superhuman_gov_media_creator_board_partner` — Blumhouse/A24 downside caps, ASC 926 film/creator amortization, organic CTR/AVD vs. Shorts vanity views, and merch working capital.

```bash
# Inspect an existing Superhuman Governance profile or canonical seat
python3 -m orgprompt.cli governance inspect superhuman_gov_capital_allocation_board_director

# Synthesize a bespoke Superhuman Director / Auditor for any problem or company
python3 -m orgprompt.cli governance synthesize-superhuman \
  --problem "Audit Q4 Board packet for aggressive software capitalization, B2B MPLS margin decay, and AI pilot theater" \
  --role gov_capital_allocation_value_director \
  --company "Orange France" \
  --fuse gov_external_statutory_forensic_auditor \
  --fuse gov_telco_energy_infra_regulatory_director \
  --persist \
  --output artifacts/governance_roles/custom_board_audit.md
```

---

## Multi-Agent Boardroom Tear-Down Workflow (Subagent Execution Pattern)

When asked to review a company performance packet, 10-K/10-Q, strategic plan, or studio slate:
1. **Resolve the Board Slate**: Run `scripts/run_board_audit.py --company "<Name>"` (or `orgprompt governance board-slate`) to select the voting Board seats and Independent External Auditors (`references/industry_board_selection_guide.md`).
2. **Pull Superhuman Governance Prompts**: Retrieve `deep_superhuman_governance_prompt` via `SuperhumanGovernanceSynthesizer` (or `orgprompt governance inspect --json`).
3. **Spawn Independent Oversight Subagents (`invoke_subagent`)**: Launch separate subagents for (a) the **Superhuman Capital-Allocation / Sector Director** and (b) the **Superhuman Forensic & Strategic Auditor**, feeding them the raw company packet with strict instructions to apply the **5-Stage Unknown-Risk & Management-Spin Falsification Protocol**.
4. **Synthesize Binding Board Resolutions**: Consolidate findings into the 6-part Fiduciary Governance Dossier: (1) Verdict, (2) Management Spin vs. Cash/GAAP Reality Tear-Down, (3) Segment ROIC/WACC & Cohort Value Bridge, (4) 30/60/90-Day Forensic & Control Demands, (5) Quantified High-ROIC Operational & Pragmatic AI Directives, and (6) Binding Covenants & Executive Compensation Clawback/ROIC Alignment.
