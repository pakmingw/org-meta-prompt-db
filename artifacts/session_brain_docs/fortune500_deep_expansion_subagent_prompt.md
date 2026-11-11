# Gemini 4 Argon (High) Mega-Output Subagent Prompt: Company-by-Company Fortune 500 Operating Model & Internet Role Comparison

> [!TIP]
> **How This Prompt Exploits Gemini 4 Argon (High)**:
> Gemini 4 Argon (High) (`Model: inherit`) supports an ultra-large context window and massive single-turn output token budgets. Standard prompts cause agents to summarize or batch companies together. This prompt explicitly unlocks **uncompressed, company-by-company exhaustive generation**, forcing the subagent to combine live `search_web` ground truth with full database introspection (`data/org_knowledge_base.db`) and output a complete operating model + role gap analysis for **every individual company one by one**.

---

## Copy-Paste / Programmable Subagent Prompt Template

```markdown
You are running on **Gemini 4 Argon (High)** (`Model: inherit`) with an ultra-large input context window and a massive output token generation budget.

### Mission
Iterate **company-by-company, one by one** through your assigned Fortune 500 cohort (`Rank {{START_RANK}}` to `Rank {{END_RANK}}`) in `/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/data/org_knowledge_base.db`.
For **EVERY SINGLE COMPANY** in your range (zero skipping, zero grouping, zero elision), you must:
1. **Mine Public Ground Truth (`search_web`)**: Execute targeted web searches to extract the company's real-world public organizational structure:
   - Actual SEC 10-K reportable business segments and operating divisions,
   - Real C-suite / SVP functional leadership structure and proprietary operating system or management rituals (e.g., Walmart Retail Link & Merchant Squads, Danaher Business System, JPMorgan Chase CIB/CCB/AWM + Onyx, ExxonMobil Upstream/Product Solutions/Low Carbon + Global Projects, UnitedHealth Optum vs. UnitedHealthcare),
   - Real specialized job families and high-leverage roles actively hired by that company on public career portals and engineering/corporate disclosures.
2. **Introspect Our Database Model (`data/org_knowledge_base.db`)**:
   - Query `fortune500_companies`, `company_role_edges`, `canonical_roles`, `org_units`, and `role_subagent_swarms` for that exact company (`rank` and `company_id`).
   - Extract the operating model, archetype, functional units, and the `30+` canonical roles currently linked to that company via `EMPLOYS_ROLE` edges.
3. **Generate Exhaustive Company-by-Company Output (Exploit Full Output Token Window)**:
   For each company (`Rank #N: <Company Name>`), write an un-abbreviated deep profile containing:
   - **A. Internet-Verified Operating Model & Divisional Architecture**:
     - Revenue engine, primary P&L segments (10-K verified), core value-creation loop, and proprietary management/operating mechanisms.
     - How decisions flow across HQ, operating divisions, risk/compliance, and frontline execution.
   - **B. Real-World Key Roles & Job Architecture (Internet Ground Truth)**:
     - The critical executive, principal IC, specialist operator, and governance roles that actually drive this specific company's P&L and technical/operational moat, including their day-to-day horizontal tools (`WORD_PROCESSOR`, `SPREADSHEET_PROCESSOR`, `SLIDE_PRESENTER`, `MEETING_NOTE_TAKER`, `COMMUNICATION_TRIAGE`, `BI_ANALYTICS`) and vertical enterprise systems (e.g., SAP, Epic, Guidewire, Bloomberg, Palantir, Manhattan WMS, Synopsys).
   - **C. Side-by-Side Comparison: Internet Ground Truth vs. `org_knowledge_base.db`**:
     - **Exact Matches (High-Fidelity Coverage)**: Which canonical roles and operating units in `org_knowledge_base.db` accurately mirror the company's real-world workforce and workflows.
     - **Company-Specific Nuances & Bespoke Role Deltas**: Which proprietary roles, specialized sub-units, or unique operating rituals found on the internet are unique to this company (e.g., Walmart's *Replenishment Manager / Retail Link Analyst*, JPMorgan's *Model Risk Governance MD (SR 11-7)*, Boeing/Lockheed's *DER — Designated Engineering Representative*) and how they map to or extend our canonical roles.
     - **Recommended Personal Subagent Swarm & Tooling Calibration for This Company**: How to tailor our `orgprompt scaffold company` recommendation specifically for this enterprise's real software stack and operating cadence.

### Strict Anti-Truncation & Mega-Output Rules
- **NEVER** group companies together (e.g., NEVER write "Ranks 45–50 follow a similar retail model").
- **NEVER** use placeholders (`...`, `TBD`, `etc.`, `see above`).
- Exploit your full output token capacity in every write call (`write_file` / `Append: true`) to produce rich, empirical, company-specific analysis for every single company from `Rank {{START_RANK}}` to `Rank {{END_RANK}}`.
- Persist your output both to:
  1. `/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/artifacts/fortune500_encyclopedia/volume_{{VOLUME_ID}}_ranks_{{START_RANK}}_{{END_RANK}}.md`
  2. The `company_internet_comparisons` table in `/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/data/org_knowledge_base.db` (storing `company_id`, `f500_rank`, `company_name`, `internet_divisions_json`, `internet_bespoke_roles_json`, `db_mapped_roles_count`, `alignment_score`, `delta_analysis_md`, `tailored_swarm_recommendation_md`).
```
