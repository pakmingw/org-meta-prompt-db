---
name: org-frontier-lab-enterprise-bridge
description: >-
  Join real-world Fortune 500 enterprises, regulated European/global industries,
  and indie film/creator studios to the 5 Nov 2026 Frontier AI Labs (Anthropic,
  OpenAI, Google DeepMind, Meta Superintelligence Labs / FAIR, and Mistral AI).
  Maps any enterprise company, canonical role, or complex business/scientific
  problem to its exact counterpart Frontier AI Lab pods, 16 `frontier_*` lab
  roles, RL outcome verifiers, MCP context runtimes, distillation forges, and
  ASL/FSF safety gates (`orgprompt.frontier`). ACTIVATE this skill when the user
  asks how frontier AI labs are organized, how to bridge a real-world enterprise
  or creator workflow to frontier AI capabilities, or which frontier lab pod and
  post-training/MCP recipe solves a domain bottleneck.
---

# Real-World Enterprise <-> Nov 2026 Frontier AI Lab Bridge (`org-frontier-lab-enterprise-bridge`)

Connects the **Real-World Operating Layer** (`512` organizations, `563` enterprise/creator roles, `6`-agent Personal Subagent Swarms) directly to the **Nov 2026 Frontier AI Lab Layer** (`5` Frontier AI Labs, `30` internal operating pods, `16` `frontier_*` canonical roles, `5` frontier vertical tools, `22` cross-industry bridges, and `1,720+` relational `role_frontier_joins`).

- **Workspace Root**: `/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db`
- **Core Architectural Insight**: Naive enterprise "prompt-and-RAG wrappers" fail in production because they lack **deterministic outcome verifiers**, **typed MCP/Computer-Use state harnesses**, **domain post-training/distillation unit economics**, and **AI Control / ASL safety gates**. Every enterprise workflow requires a joint pod pairing the domain owner's **6-Agent Personal Swarm** with specific **Frontier Lab counterparts**.

---

## Core Capabilities & CLI Commands

### 1. List & Inspect the 5 Nov 2026 Frontier AI Labs (`30` Internal Pods)
Covers **Anthropic** (`lab_anthropic`), **OpenAI** (`lab_openai`), **Google DeepMind** (`lab_google_deepmind`), **Meta Superintelligence Labs (MSL) & FAIR** (`lab_meta_msl`), and **Mistral AI** (`lab_mistral_ai`):

```bash
cd /home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db
python3 -m orgprompt.cli frontier labs
python3 -m orgprompt.cli frontier inspect-lab anthropic --output artifacts/frontier_labs/anthropic_profile.md
python3 -m orgprompt.cli frontier inspect-lab mistral_ai --format json
```

### 2. Join Any Real-World Role to Its Counterpart Frontier AI Lab Roles
Resolves any of the `579` canonical roles (by slug, ID, or natural-language query) across the **6 Typed Join Mechanisms** (`FDE_WORKFLOW_EMBEDDING`, `RL_VERIFIER_AND_EVAL_HARNESS`, `MCP_CONTEXT_AND_TOOL_RUNTIME`, `DOMAIN_DISTILLATION_AND_POST_TRAINING`, `SAFETY_CONTROL_AND_RED_TEAM_GATE`, `WORLD_MODEL_AND_SCIENTIFIC_SIM`):

```bash
python3 -m orgprompt.cli frontier join-role principal_ftth_copper_decommissioning_architect_plan_cuivre --company "Orange France"
python3 -m orgprompt.cli frontier join-role creator_solo_founder_one_person_media_studio --company "Beast Industries"
```

### 3. Generate a Full Company <-> Frontier AI Lab Co-Design Blueprint
Aggregates all `employs_role` edges for any of the `512` companies into top counterpart `frontier_*` roles, mechanism distributions, recommended labs, and industry technical recipes:

```bash
python3 -m orgprompt.cli frontier join-company "Orange France" --output artifacts/frontier_labs/orange_france_frontier_lab_bridge.md
python3 -m orgprompt.cli frontier join-company "Beast Industries" --output artifacts/frontier_labs/beast_industries_frontier_lab_bridge.md
```

### 4. Bridge Any Arbitrary Problem Statement to Real-World + Frontier Pods
Runs `HybridSearchEngine` (`BM25 + Dense LSA + RRF`) to retrieve the anchor real-world enterprise roles AND joins them via SQL + Graph to Frontier Lab pods and a 4-phase co-design execution plan:

```bash
python3 -m orgprompt.cli frontier bridge-problem \
  --problem "Accelerate FTTH Plan Cuivre copper decommissioning and sovereign 5G OSS/BSS mediation under ANSSI SecNumCloud" \
  --company "Orange France" \
  --output artifacts/frontier_labs/plan_cuivre_bridge.md
```

---

## Multi-Agent Co-Design Execution Workflow

1. **Retrieve the Enterprise + Frontier Bridge**: Run `scripts/bridge_frontier_lab.py --problem "..." [--company "..."]` (see `references/nov2026_frontier_labs_matrix.md` for lab selection heuristics).
2. **Pull Counterpart Superhuman / Canonical Prompts**: Fetch the real-world anchor role prompt AND a Frontier Bridge Superhuman (`superhuman_frontier_fde_enterprise_bridge_architect` or `superhuman_frontier_post_training_verifier_chief` via `orgprompt superhuman inspect`).
3. **Co-Design Verifier + MCP + Distillation Spec**: Spawn paired subagents (`invoke_subagent`) to author (a) the typed MCP state server & conservation invariants, and (b) the RFT/RL outcome grader + sovereign deployment topology.
