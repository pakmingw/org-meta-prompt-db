# Walkthrough: Global Organizational Knowledge Graph, Fortune 500 Role Meta-Prompting Database, Personal Subagent Swarms & Antigravity Skills (`orgprompt`)

> [!IMPORTANT]
> **Independent Audit Verdict (Phases 1–16)**: **`UNCONDITIONAL AUDIT APPROVAL`** ([Independent Architecture & Quality Auditor](conversation://cc5b4383-4bd4-44cc-beb5-fb19a5006b78) & [Victory Auditor](conversation://fbf2db61-c584-42b5-b945-534ffbf5ef61))
> **Live GitHub Repository**: **`https://github.com/pakmingw/org-meta-prompt-db`** (`main` branch, commit `0b792b2` Phase 16; prior commits `0b28566` Phase 15 & `eff6642` Phase 14)
> **Local Workspace**: `/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db`
> **Automated Verification Suite**: **`328 passed, 0 failed, 0 skipped`** (`100%` pass rate across `29` test modules)
> **Flagship Empirical Reports & Playbooks**:
> - **Phase 11 McKinsey Shareholder Value Audit (Orange France)**: [orange_france_mckinsey_shareholder_value_audit.md](file:///home/pakmingw/.gemini/antigravity/brain/1e96291d-9d64-4bac-9f19-67c0822cf354/orange_france_mckinsey_shareholder_value_audit.md)
> - **Phase 13 Single-Blind Superhuman Role Benchmark (`96.33 / 100`, `3/3` `#1` Wins)**: [superhuman_skill_benchmark_report.md](file:///home/pakmingw/.gemini/antigravity/brain/1e96291d-9d64-4bac-9f19-67c0822cf354/superhuman_skill_benchmark_report.md)
> - **Phase 14 Indie Film, YouTube & Solo Creator Channel Launch Playbook**: [social_media_channel_launch_playbook.md](file:///home/pakmingw/.gemini/antigravity/brain/1e96291d-9d64-4bac-9f19-67c0822cf354/social_media_channel_launch_playbook.md)
> - **Phase 15 Fiduciary Board & Auditor Governance Single-Blind Benchmark (`97.25` & `96.75` vs. `92.50` Baseline)**: [board_and_auditor_governance_report.md](file:///home/pakmingw/.gemini/antigravity/brain/1e96291d-9d64-4bac-9f19-67c0822cf354/board_and_auditor_governance_report.md)
> - **Phase 16 Nov 2026 Frontier AI Labs & Real-World Enterprise Bridge Report**: [frontier_ai_labs_nov2026_and_enterprise_bridge_report.md](file:///home/pakmingw/.gemini/antigravity/brain/1e96291d-9d64-4bac-9f19-67c0822cf354/frontier_ai_labs_nov2026_and_enterprise_bridge_report.md)

---

## 1. Verified Acceptance Metrics (Phases 1–9)

| Milestone / Dimension | Target Threshold | Verified Audit Result | Key Implementation Files |
| :--- | :--- | :--- | :--- |
| **Fortune 500 Enterprise Catalog (`Exp-M1A`)** | $\ge 500$ Fortune 500 companies | **500 contiguous Fortune 500 companies (`#1 Walmart` to `#500 O-I Glass`, revenues `\$648.1B` to `\$7.1B`)** | [seed_fortune500.py](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/orgprompt/db/seed_fortune500.py) |
| **Canonical Roles & Knowledge Graph (`Exp-M1A`)** | $500\text{–}600+$ roles, $\ge 15,000$ edges | **547 canonical roles, 16 industries, 26,900 `employs_role` edges (`29,061` total edges, `0` orphans)** | [roles_families_1_9.py](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/orgprompt/db/roles_families_1_9.py), [roles_families_10_13.py](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/orgprompt/db/roles_families_10_13.py), [engine.py](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/orgprompt/graph/engine.py) |
| **5-Volume Fortune 500 Encyclopedia (`Exp-M1B`)** | All 500 companies one-by-one vs. internet | **5 Volumes (`2.27 MB`, `0` stubs) + 500 rows in `company_internet_comparisons` (mean alignment `0.8574`)** | [seed_encyclopedia.py](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/orgprompt/db/seed_encyclopedia.py), [volume_1_ranks_1_100.md](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/artifacts/fortune500_encyclopedia/volume_1_ranks_1_100.md) – [volume_5_ranks_401_500.md](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/artifacts/fortune500_encyclopedia/volume_5_ranks_401_500.md) |
| **Day-to-Day Work Anatomy & Tooling (`Exp-M2`)** | $\ge 4$ use cases/role ($\ge 2,000$ total) | **51 enterprise tools (`6` horizontal + `45` vertical), 2,735 use cases (`5`/role), 3,282 tool bindings** | [seed_tooling.py](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/orgprompt/db/seed_tooling.py) |
| **Personal Subagent Swarms & GenAI Plans (`Exp-M3`)** | $4\text{–}7$ subagents/role, 7-section prompts | **3,282 subagents (`6`/role, `100%` acyclic DAGs), 547 GenAI build plans, 547 prompts (avg `10,145` chars, `100%` unique)** | [seed_swarms_plans.py](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/orgprompt/db/seed_swarms_plans.py), [compiler.py](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/orgprompt/prompts/compiler.py) |
| **Scaffolder CLI, Onboarding & Skills (`Exp-M4`)** | `scaffold`, `company onboard`, 2 Skills, $\ge 35$ queries | **$\text{Recall@10} = 0.9306$, $\text{MRR} = 0.7917$ (`36` queries), `stripe_genai_blueprint.md` (`15.8 KB`), 2 Skills installed** | [role_scaffolder.py](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/orgprompt/scaffolder/role_scaffolder.py), [company_scaffolder.py](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/orgprompt/scaffolder/company_scaffolder.py), [onboarding/engine.py](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/orgprompt/onboarding/engine.py) |
| **Master Solution Dossier (`Exp-M5`)** | $\ge 7,500$ words | **9,284 words (`74,992` chars) across 12 substantive chapters (`0` stubs)** | [grand_challenge_dossier.md](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/artifacts/grand_challenge_dossier.md), [dossier_compiler.py](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/orgprompt/challenge/dossier_compiler.py) |
| **GitHub Repository Publication (`Exp-M6`)** | Published under `github.com/pakmingw` | **Live at `https://github.com/pakmingw/org-meta-prompt-db` (`107` tracked files on `main`)** | [README.md](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/README.md) |

---

## 2. Installed Antigravity Skills (Global & Git-Tracked Workspace)

Both skills are installed globally in `~/.gemini/config/skills/` (available in any workspace) and tracked in the Git repository under `.agents/skills/`:

1. **`org-role-search-and-scaffold`**:
   - Global: [SKILL.md](file:///home/pakmingw/.gemini/config/skills/org-role-search-and-scaffold/SKILL.md) | Workspace: [SKILL.md](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/.agents/skills/org-role-search-and-scaffold/SKILL.md)
   - Helper Script: [search_and_scaffold.py](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/.agents/skills/org-role-search-and-scaffold/scripts/search_and_scaffold.py)
   - **What It Does**: Searches the `547` canonical roles, `500` Fortune 500 enterprises, `2,735` day-to-day workflows, and `51` horizontal/vertical tools via the local Hybrid Search Engine, and instantly scaffolds a role's or company's **Personal Subagent Swarm ("Role-in-a-Box") + GenAI Tooling Build Plan**.
2. **`org-company-deep-onboard`**:
   - Global: [SKILL.md](file:///home/pakmingw/.gemini/config/skills/org-company-deep-onboard/SKILL.md) | Workspace: [SKILL.md](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/.agents/skills/org-company-deep-onboard/SKILL.md)
   - Helper Script: [onboard_company.py](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/.agents/skills/org-company-deep-onboard/scripts/onboard_company.py)
   - Registry: [onboarded_companies.md](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/.agents/skills/org-company-deep-onboard/references/onboarded_companies.md)
   - **What It Does**: Give Antigravity the name of *any* company $\rightarrow$ runs deep `search_web` research into its organization, publicly traded status, and business challenges $\rightarrow$ executes `orgprompt company onboard` to update the SQLite database, Knowledge Graph, and skill registry $\rightarrow$ generates a complete **"Apply Generative AI Everywhere" Blueprint** (see verified sample: [stripe_genai_blueprint.md](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/artifacts/company_onboarding/stripe_genai_blueprint.md)).

3. **`org-superhuman-role-synthesizer` (`Phase 12`)**:
   - Global: [SKILL.md](file:///home/pakmingw/.gemini/config/skills/org-superhuman-role-synthesizer/SKILL.md) | Workspace: [SKILL.md](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/.agents/skills/org-superhuman-role-synthesizer/SKILL.md)
   - Helper Script: [synthesize_superhuman.py](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/.agents/skills/org-superhuman-role-synthesizer/scripts/synthesize_superhuman.py)
   - Epistemology Rubric: [superhuman_epistemology_framework.md](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/.agents/skills/org-superhuman-role-synthesizer/references/superhuman_epistemology_framework.md)
   - **What It Does**: Takes any problem statement, canonical OKG role, or external agent-provided custom role (+ optional developer background context), fuses adjacent roles across 5 Org-Graph edge types (`COLLABORATES_WITH`, `HANDS_OFF_TO`, `REVIEWS_AND_GATES`, `CHALLENGES_OR_AUDITS`, `REPORTS_TO`), synthesizes the **Perfect Human Background** (University/Doctoral foundations, 12–20 year On-the-Job crucibles & scar tissue, cognitive/psychological traits), and compiles an **8-Section Deep Superhuman Meta-Prompt (`~36,400–37,400` chars)** with a **5-Stage Unknown-to-AI (Out-of-Distribution) Epistemic Protocol** (see sample: [demo_unknown_problem_superhuman_role.md](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/artifacts/superhuman_roles/demo_unknown_problem_superhuman_role.md)).

4. **`org-board-and-auditor-governance` (`Phase 15`)**:
   - Global: [SKILL.md](file:///home/pakmingw/.gemini/config/skills/org-board-and-auditor-governance/SKILL.md) | Workspace: [SKILL.md](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/.agents/skills/org-board-and-auditor-governance/SKILL.md)
   - Helper Script: [run_board_audit.py](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/.agents/skills/org-board-and-auditor-governance/scripts/run_board_audit.py)
   - Industry Selection Matrix: [industry_board_selection_guide.md](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/.agents/skills/org-board-and-auditor-governance/references/industry_board_selection_guide.md)
   - **What It Does**: Sits in a dedicated **Fiduciary Oversight Taxonomy Tier (`orgprompt.governance`)** outside and above management (`canonical_roles`). Assembles industry-selected Board of Directors & Independent Statutory/Forensic/Strategic Auditor slates (`18` governance roles, `22` `PUBLIC_ENTERPRISE` + `VENTURE_OR_BOUTIQUE` slates, `72` oversight edges) and **Superhuman Governance Profiles** (`superhuman_governance_profiles`, `~34,000–35,150` chars) to tear down management spin, stress `ROIC` vs. `WACC` & `SOTP`, expose Non-GAAP/capitalization/reverse-factoring/`ASC 606` distortions, and issue binding Board resolutions + AI value-creation roadmaps.

5. **`org-frontier-lab-enterprise-bridge` (`Phase 16`)**:
   - Global: [SKILL.md](file:///home/pakmingw/.gemini/config/skills/org-frontier-lab-enterprise-bridge/SKILL.md) | Workspace: [SKILL.md](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/.agents/skills/org-frontier-lab-enterprise-bridge/SKILL.md)
   - Helper Script: [bridge_frontier_lab.py](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/.agents/skills/org-frontier-lab-enterprise-bridge/scripts/bridge_frontier_lab.py)
   - Lab Matrix: [nov2026_frontier_labs_matrix.md](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/.agents/skills/org-frontier-lab-enterprise-bridge/references/nov2026_frontier_labs_matrix.md)
   - **What It Does**: Joins real-world Fortune 500 enterprises, regulated European/global industries, and creator/film studios (`563` non-frontier roles, `100%` covered via `1,721` `role_frontier_joins` rows across `6` typed join mechanisms and `22` cross-industry blueprints) directly to the **5 Nov 2026 Frontier AI Labs** (`Anthropic`, `OpenAI`, `Google DeepMind`, `Meta Superintelligence Labs / FAIR`, `Mistral AI`), their `30` internal operating pods, and `16` `frontier_*` canonical roles (`579` total canonical roles, `60` tools).

### Live Domain Expansions (`Phases 10–16`)
- **Telecommunications & Shareholder Value Audit (`Phases 10 & 11` — Orange S.A. / `EPA: ORA`)**: Onboarded `f500_orange_france` (Rank `#501`) and published [orange_france_mckinsey_shareholder_value_audit.md](file:///home/pakmingw/.gemini/antigravity/brain/1e96291d-9d64-4bac-9f19-67c0822cf354/orange_france_mckinsey_shareholder_value_audit.md).
- **Indie Film, Scaled YouTube & Solo Creator Studios (`Phase 14`)**: Added `4` creator/film vertical tools (`55` total), `12` canonical film & creator-economy roles (`563` canonical roles), `6` studios (`A24`, `Blumhouse Productions`, `Beast Industries`, `Mythical Entertainment`, `Corridor Digital`, `Kurzgesagt` $\rightarrow$ `507` companies), `2` Creator Superhumans, and [social_media_channel_launch_playbook.md](file:///home/pakmingw/.gemini/antigravity/brain/1e96291d-9d64-4bac-9f19-67c0822cf354/social_media_channel_launch_playbook.md).
- **Fiduciary Board & Independent Auditor Tier (`Phase 15`)**: Implemented [orgprompt/governance/](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/orgprompt/governance/__init__.py) (`18` Board & Auditor roles, `22` board compositions, `72` C-suite oversight edges, `3` flagship Superhuman Governance profiles) and benchmarked them in [board_and_auditor_governance_report.md](file:///home/pakmingw/.gemini/antigravity/brain/1e96291d-9d64-4bac-9f19-67c0822cf354/board_and_auditor_governance_report.md).
- **Nov 2026 Frontier AI Labs & Real-World Enterprise Bridge (`Phase 16`)**: Implemented [seed_frontier_labs.py](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/orgprompt/db/seed_frontier_labs.py) and [orgprompt/frontier/](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/orgprompt/frontier/__init__.py) (`+5` vertical lab tools $\rightarrow$ `60` tools; `+16` `frontier_*` canonical roles $\rightarrow$ `579` canonical roles; `5` Frontier Labs onboarded $\rightarrow$ `512` companies; `30` lab pods; `22` industry bridges across `16/16` industries; `1,721` `role_frontier_joins`; `2` Frontier Bridge Superhumans $\rightarrow$ `7` total) and published [frontier_ai_labs_nov2026_and_enterprise_bridge_report.md](file:///home/pakmingw/.gemini/antigravity/brain/1e96291d-9d64-4bac-9f19-67c0822cf354/frontier_ai_labs_nov2026_and_enterprise_bridge_report.md) + sample bridges ([orange_france_frontier_lab_bridge.md](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/artifacts/frontier_labs/orange_france_frontier_lab_bridge.md), [beast_industries_frontier_lab_bridge.md](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/artifacts/frontier_labs/beast_industries_frontier_lab_bridge.md)).

---

## 3. CLI & Python Quick Reference (`orgprompt`)

```bash
cd /home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db

# 1. Scaffold a Personal Subagent Swarm ("Role-in-a-Box") + GenAI Tooling Build Plan for any role (including Creator & Frontier Lab roles)
python3 -m orgprompt.cli scaffold role "frontier_forward_deployed_ai_engineer_lead" --format markdown

# 2. Scaffold an Enterprise, Creator Studio, or Frontier AI Lab GenAI Tooling & Multi-Role Subagent Swarm Roadmap
python3 -m orgprompt.cli scaffold company "Anthropic" --format markdown

# 3. Join Real-World Enterprises, Roles & Business Bottlenecks to Nov 2026 Frontier AI Lab Pods & Recipes
python3 -m orgprompt.cli frontier labs
python3 -m orgprompt.cli frontier inspect-lab "Meta Superintelligence Labs" --format markdown
python3 -m orgprompt.cli frontier join-role "fin_chief_financial_officer" --company "NVIDIA" --format markdown
python3 -m orgprompt.cli frontier join-company "Orange France" --format markdown
python3 -m orgprompt.cli frontier bridge-problem \
  --company "Orange France" \
  --problem "Automate Plan Cuivre civil-duct CAD validation and 5G SA Open RAN slice assurance under ANSSI SecNumCloud"

# 4. Synthesize a Superhuman Role Definition & Deep Human/OOD Meta-Prompt
python3 -m orgprompt.cli superhuman synthesize \
  --role "frontier_test_time_compute_reasoning_rl_lead" \
  --problem "Architect outcome-verified agentic RL environments and ASL/AI-Control sandboxes free of reward hacking" \
  --persist --format markdown

# 5. Assemble an Industry-Tailored Board of Directors & Independent Auditor Slate (Public Enterprise or Venture/Creator Studio)
python3 -m orgprompt.cli governance board-slate --company "Orange France" --format markdown
python3 -m orgprompt.cli governance inspect "superhuman_gov_forensic_strategic_auditor" --format markdown

# 6. Run the Hybrid Search Benchmark & Full 328-Test Verification Suite
python3 -m orgprompt.cli benchmark run
python3 -m pytest tests/ -q
```
