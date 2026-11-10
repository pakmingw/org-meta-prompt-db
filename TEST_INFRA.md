# Test Infrastructure Architecture: 4-Tier Opaque-Box Verification Framework

**Project**: Organizational Knowledge Graph & Professional Role Meta-Prompting Database  
**Author**: E2E Test Writer (`teamwork_preview_test_writer_e2e_1`)  
**Status**: Authoritative Test Specification & Architecture  
**Target Root**: `/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db`  
**Governing Documents**: `ORIGINAL_REQUEST.md`, `PROJECT.md`

---

## 1. Executive Summary & Test Philosophy

### 1.1 Opaque-Box, Requirement-Driven Verification
This testing framework adheres strictly to an **opaque-box, contract-driven testing philosophy**. The test suite treats the implementation modules as a black box:
1. **Behavioral Invariants Over Internal State**: Tests interact strictly through public interfaces, standard models, CLI commands, and query endpoints specified in `PROJECT.md` and `ORIGINAL_REQUEST.md`.
2. **Authoritative Ground Truth Derivation**: Every test assertion is derived from the non-negotiable acceptance criteria of `ORIGINAL_REQUEST.md` (e.g., minimum entity counts, graph invariant degrees, character thresholds, retrieval metrics, DAG acyclicity, and dossier word counts).
3. **Zero Facades & Zero Mock Bypasses**: The tests execute genuine algorithmic computations — running SQLite relational constraints, NetworkX degree validations, scikit-learn SVD vectorizations, Reciprocal Rank Fusion arithmetic, topological sorting, and markdown text analyses.
4. **Adversarial & Corner-Case Robustness**: The suite actively probes boundary conditions, malformed queries, out-of-vocabulary acronyms, punctuation edge cases, cycle resolutions, and adversarial audit failures.

### 1.2 Progressive Testability & Milestone Decoupling
To support concurrent multi-agent development and iterative milestone delivery:
- **Standard Fixtures (`tests/conftest.py`)**: Provide isolated temporary SQLite databases, pre-configured seed schemas, hydrated in-memory NetworkX graphs, sample roles, benchmark query sets, and safe import guards.
- **Milestone-Aware Execution**: Tests use graceful imports and fixture guards (`pytest.importorskip` where appropriate for pending worker milestones) while asserting exact interface contracts. When a module is implemented, tests immediately execute the end-to-end logic without requiring test modifications.

---

## 2. Feature Inventory Mapping (All 21 Features)

The table below enumerates all 21 features defined in `PROJECT.md`, mapping each feature to its functional layer, governing milestone, authoritative contract, and primary test tier.

| Feature ID | Feature Name | Milestone | Functional Module | Governing Contract | Primary Test Tier |
|---|---|---|---|---|---|
| **F01** | Global Industry Taxonomy | M1 | `orgprompt.models`, `orgprompt.db.seed_data` | 16 macro industries, 48 exemplar orgs with lineage | Tier 1 & Tier 4 |
| **F02** | Operating Units & Loops | M1 | `orgprompt.models`, `orgprompt.db.seed_data` | 120 operating units, 4-stage value creation loops | Tier 1 |
| **F03** | SQLite Relational Schema | M1 | `orgprompt.db.schema`, `orgprompt.db.connection` | 9 typed tables, foreign keys, triggers, FTS5 table | Tier 1 & Tier 2 |
| **F04** | NetworkX Graph Engine | M1 | `orgprompt.graph.engine`, `invariants` | Heterogeneous graph hydration, 4 structural invariants | Tier 1 & Tier 3 |
| **F05** | Extensible Role Generator | M1 | `orgprompt.graph.generator` | Dynamic role synthesis preserving all graph invariants | Tier 1 & Tier 2 |
| **F06** | Meta-Prompt Compilation Engine | M2 | `orgprompt.prompts.compiler`, `templates` | Procedural compilation for 336 roles, 6 sections | Tier 1 |
| **F07** | Meta-Prompt Invariant Gate | M2 | `orgprompt.prompts.validator` | >= 1,200 chars, 6 sections, 0 stubs, 100% unique | Tier 1 & Tier 2 |
| **F08** | Sparse Lexical Search (BM25) | M3 | `orgprompt.search.bm25` | SQLite FTS5 BM25 ranking across titles, tags, text | Tier 1 & Tier 2 |
| **F09** | Pure Local Dense Vectorizer | M3 | `orgprompt.search.dense` | Character n-gram LSA dense embeddings, cosine similarity | Tier 1 & Tier 2 |
| **F10** | Reciprocal Rank Fusion (RRF) | M3 | `orgprompt.search.hybrid` | RRF ($k=60$) combining sparse & dense with attribution | Tier 1 & Tier 2 |
| **F11** | Knowledge Graph Expansion | M3 | `orgprompt.search.expansion` | Multi-hop traversal to assemble cross-functional teams | Tier 1 & Tier 3 |
| **F12** | Retrieval Benchmark Suite | M3 | `orgprompt.search.benchmark` | 25 test queries: Recall@10 >= 0.85, MRR >= 0.70 | Tier 1 & Tier 3 |
| **F13** | Capability Extractor API/CLI | M4 | `orgprompt.synthesizer.extractor` | Decomposition into domains, disciplines, archetypes | Tier 1 & Tier 2 |
| **F14** | Dynamic Team Synthesizer | M4 | `orgprompt.synthesizer.team_builder` | Constrained assembly (>=8 roles, >=3 industries, tiers) | Tier 1 & Tier 3 |
| **F15** | Topological DAG Compiler | M4 | `orgprompt.synthesizer.dag_compiler` | Staged task projection compiling cycles to acyclic DAG | Tier 1 & Tier 2 |
| **F16** | Workflow DAG Execution Engine | M4 | `orgprompt.synthesizer.workflow_engine` | Topological execution, artifact routing, validation | Tier 1 & Tier 3 |
| **F17** | Grand Challenge Trajectory | M5 | `orgprompt.challenge.runner` | 6-stage trajectory for Sovereign AI + 6G + Settlement | Tier 4 (E2E) |
| **F18** | Adversarial Red-Team Gate | M5 | `orgprompt.challenge.red_team` | Empirical critique discovering 3 vulnerabilities | Tier 4 (E2E) |
| **F19** | Upstream Revision Loop | M5 | `orgprompt.challenge.runner`, `red_team` | Documented upstream redesigns remediating flaws | Tier 4 (E2E) |
| **F20** | Executive Solution Dossier | M5 | `orgprompt.challenge.dossier_compiler` | >= 5,000 words dossier across 9 substantive chapters | Tier 4 (E2E) |
| **F21** | Comprehensive Pytest Suite | M6/E2E | `tests/` | 100% pass rate across unit, boundary, integration, E2E | All Tiers |

---

## 3. The 4-Tier Test Architecture

```
+-----------------------------------------------------------------------------------------------+
|                                  TIER 4: REAL-WORLD E2E SCENARIOS                             |
|  - Flagship Grand Challenge Trajectory (Sovereign AI + 6G Edge + RTGS Financial Settlement)   |
|  - 6-Stage Topological Pipeline Execution & Multi-Specialist Artifact Generation              |
|  - Adversarial Red-Team Veto Gate & Forced Upstream Redesign Revisions                        |
|  - Executive Master Solution Dossier Integrity (>= 5,000 words, 9 Chapters)                   |
+-----------------------------------------------+-----------------------------------------------+
                                                |
+-----------------------------------------------+-----------------------------------------------+
|                             TIER 3: CROSS-FEATURE INTEGRATION FLOWS                           |
|  - SQLite DML Trigger Synchronization with FTS5 Virtual Index                                 |
|  - SQLite Relational Hydration into NetworkX Heterogeneous Knowledge Graph                    |
|  - Dynamic Role Generation -> DB Insert -> FTS5 Sync -> Graph Invariant Preservation          |
|  - Hybrid Search (BM25 + Dense LSA) -> RRF Fusion -> KG Subgraph Expansion                    |
|  - Capability Extraction -> Team Synthesizer -> DAG Compilation -> Workflow Execution         |
+-----------------------------------------------+-----------------------------------------------+
                                                |
+-----------------------------------------------+-----------------------------------------------+
|                           TIER 2: BOUNDARY, CORNER & ADVERSARIAL CASES                        |
|  - FTS5 Query Sanitization (Special Characters: C++, 6G, Sliders, Punctuation, Quotes)        |
|  - Zero-Norm Vector Division Guard & Out-Of-Vocabulary Acronym Resilience                     |
|  - Prompt Length Thresholds (Exactly 1,200 chars vs 1,199 chars rejection)                    |
|  - Graph Invariant Edge Bounds (Degree = 0 isolation, Single workflow edge rejection)         |
|  - Acyclic DAG Cycle Prevention & Disconnected Component Handling                            |
|  - Word Count Boundary Verification (< 5,000 words rejection)                                 |
+-----------------------------------------------+-----------------------------------------------+
                                                |
+-----------------------------------------------+-----------------------------------------------+
|                           TIER 1: FEATURE-LEVEL CONTRACT COVERAGE                             |
|  - Individual Unit & Schema Tests for all 21 Features                                         |
|  - Pydantic Model Validation & Typed Constraint Checking                                      |
|  - SQLite DDL Table Creation, Foreign Key Cascades, and Index Verification                    |
|  - NetworkX Node/Edge Type Assertions & Invariant Calculation Algorithms                      |
|  - Prompt Section Header Matching & JSON Schema Extraction                                    |
|  - BM25 and LSA Cosine Similarity Mathematical Correctness                                    |
+-----------------------------------------------------------------------------------------------+
```

---

## 4. Tier 1: Feature Coverage Specifications

Tier 1 isolates every individual feature contract, validating input handling, standard operation, and expected return types.

### 4.1 Data & Storage Features (F01–F03)
- **`test_feature_01_global_industry_taxonomy`**:
  - *Contract*: Database contains $\ge 16$ macro industries and $\ge 48$ exemplar organizations.
  - *Assertions*: Industry slugs unique; exemplar organizations have valid `industry_id` foreign keys, documented lineage, and signature mechanisms.
- **`test_feature_02_operating_units_and_loops`**:
  - *Contract*: Database contains $\ge 120$ operating units with 4-stage value creation loops.
  - *Assertions*: `unit_type` in allowed enum; `core_value_loop` non-empty string.
- **`test_feature_03_sqlite_relational_schema`**:
  - *Contract*: 9 typed tables (`industries`, `exemplar_orgs`, `org_units`, `canonical_roles`, `artifacts`, `operating_mechanisms`, `role_edges`, `role_artifacts`, `role_mechanisms`) with `PRAGMA foreign_keys = ON`.
  - *Assertions*: Foreign key constraints strictly enforced; cascading deletes operate correctly; FTS5 virtual table `roles_fts` created.

### 4.2 Graph & Generation Features (F04–F05)
- **`test_feature_04_networkx_graph_engine`**:
  - *Contract*: Hydrates NetworkX `DiGraph` from SQLite tables with typed nodes and directed edges.
  - *Assertions*: Invariant engine detects: (1) isolated roles, (2) missing `REPORTS_TO`, (3) insufficient workflow edges ($< 2$), and (4) missing output `Artifact`.
- **`test_feature_05_extensible_role_generator`**:
  - *Contract*: `RoleGenerator.generate_role(spec, db_conn, graph)` synthesizes a new canonical role.
  - *Assertions*: Synthesized role is inserted into SQLite and NetworkX without violating any of the 4 graph invariants.

### 4.3 Meta-Prompt Features (F06–F07)
- **`test_feature_06_meta_prompt_compilation_engine`**:
  - *Contract*: Compiles 6 mandatory sections:
    1. Role Identity & Exemplar Lineage
    2. First-Principles Mental Models & Domain Heuristics
    3. Technical Vocabulary & Standards
    4. Anti-Patterns & Mediocrity Filters
    5. Collaboration, Handoff & Escalation Protocols
    6. Concrete Output Artifact Schemas
  - *Assertions*: Verbatim matching of section headers in compiled prompts.
- **`test_feature_07_meta_prompt_invariant_gate`**:
  - *Contract*: Minimum character count $\ge 1,200$, 100% prompt uniqueness, zero stubs (`TODO`, `TBD`, `placeholder`, `...`).
  - *Assertions*: Regex search for stubs returns zero matches; pairwise hash collisions = 0.

### 4.4 Hybrid Search Engine Features (F08–F12)
- **`test_feature_08_sparse_lexical_search_bm25`**:
  - *Contract*: Queries `roles_fts` using BM25 ranking.
  - *Assertions*: Returns sorted candidates with monotonic BM25 score ranking.
- **`test_feature_09_pure_local_dense_vectorizer`**:
  - *Contract*: Subword character n-gram TF-IDF + TruncatedSVD (128 dims) with cosine similarity.
  - *Assertions*: Cosine similarities bounded in $[-1.0, 1.0]$; zero external API calls.
- **`test_feature_10_reciprocal_rank_fusion`**:
  - *Contract*: $RRF(d) = \sum_{m} \frac{1}{60 + r_m(d)}$ with attribution tracking.
  - *Assertions*: Returns composite score and attribution breakdown for sparse and dense sources.
- **`test_feature_11_knowledge_graph_expansion`**:
  - *Contract*: Expands top anchor roles across `COLLABORATES_WITH`, `HANDS_OFF_TO`, `REVIEWS_AND_GATES`, `CHALLENGES_OR_AUDITS`.
  - *Assertions*: Expanded set contains required cross-functional collaborators.
- **`test_feature_12_retrieval_benchmark_suite`**:
  - *Contract*: 25 diverse queries evaluated on Recall@10 and MRR.
  - *Assertions*: `Recall@10 >= 0.85`, `MRR >= 0.70`, DualContribution=True.

### 4.5 Team Synthesis & Workflow Features (F13–F16)
- **`test_feature_13_capability_extractor`**:
  - *Contract*: Decomposes text into domain tags, technical disciplines, and constraints.
  - *Assertions*: Correctly extracts multi-domain requirements from complex statements.
- **`test_feature_14_dynamic_team_synthesizer`**:
  - *Contract*: Assembles $\ge 8$ roles across $\ge 3$ industries with balanced archetypes.
  - *Assertions*: Team includes executive, engineering IC, operations, and risk/audit.
- **`test_feature_15_topological_dag_compiler`**:
  - *Contract*: Projects cyclic role relationships into a staged, provably acyclic execution DAG.
  - *Assertions*: `nx.is_directed_acyclic_graph(dag) is True`; `nx.topological_sort` succeeds.
- **`test_feature_16_workflow_dag_execution_engine`**:
  - *Contract*: Stage-by-stage task execution with artifact schema validation.
  - *Assertions*: Artifacts produced in Stage $i$ are routed to Stage $i+1$ consumers.

---

## 5. Tier 2: Boundary, Edge & Adversarial Corner Cases

Tier 2 attacks edge conditions, malformed inputs, and extremal bounds.

### 5.1 FTS5 Query Syntax & Lexical Adversarial Cases
- **Punctuation & Boolean Operators**: Queries containing `"C++"`, `"6G/O-RAN"`, `"p99.9"`, `"AND OR NOT"`, unmatched quotes, or empty whitespace must not crash SQLite FTS5; sanitizers must quote tokens safely.
- **Extreme Length Queries**: 1,000-word queries and single-character queries must execute without buffer overflow or exception.

### 5.2 Dense Vector & Mathematical Extremes
- **Zero-Norm Division**: Empty queries, stopword-only queries, or non-alphabetical queries yielding all-zero vectors must not produce `NaN` or `ZeroDivisionError`; guarded via $\max(\|v\|_2, 10^{-12})$.
- **Out-of-Vocabulary Resilience**: Novel acronyms (`ML-KEM`, `zk-SNARK`, `eCPRI`) must match related subword n-grams through character-level analysis.

### 5.3 Knowledge Graph Invariant Boundaries
- **Degree Boundary**: Role with exactly 1 workflow edge fails invariant check (minimum 2 required).
- **Executive Hierarchy**: Executive roles with in-degree $\ge 1$ for `REPORTS_TO` (subordinates reporting in) pass Invariant 2 even if out-degree is 0.
- **Cycle Injection**: Circular workflow handoffs ($A \to B \to A$) must be handled gracefully by DAG compiler via task instance staging rather than infinite loops.

### 5.4 Prompt Invariant Boundaries
- **Length Boundary**: Prompt of length 1,199 characters triggers rejection; prompt of length 1,200 passes.
- **Section Ordering**: Prompts missing one of the 6 headers or with headers out of order fail validation.
- **Stub Detection**: Prohibited substrings (`TODO`, `TBD`, `placeholder`, `TBA`, `...`, `FIXME`) trigger immediate failure even if character count exceeds 1,200.

---

## 6. Tier 3: Cross-Feature Integration Workflows

Tier 3 validates data flow across system boundaries:
1. **DML Trigger Sync**:
   - `INSERT INTO canonical_roles` $\implies$ automatic insertion into `roles_fts`.
   - `UPDATE canonical_roles` $\implies$ old row deleted from `roles_fts`, new row inserted.
   - `DELETE FROM canonical_roles` $\implies$ row deleted from `roles_fts`.
2. **Database to Graph Hydration**:
   - SQLite tables $\implies$ NetworkX DiGraph $\implies$ Invariant validation $\implies$ Subgraph extraction.
3. **Dynamic Role Synthesis Pipeline**:
   - `RoleGenerator.generate_role()` $\implies$ SQLite base table write $\implies$ Trigger sync to FTS5 $\implies$ NetworkX node/edge addition $\implies$ Invariant re-check passes.
4. **Hybrid Search to Team Subgraph**:
   - Query $\implies$ BM25 candidates + Dense candidates $\implies$ RRF rank aggregation $\implies$ Top anchors $\implies$ KG neighbor expansion $\implies$ Connected cross-functional team.

---

## 7. Tier 4: Real-World Enterprise Grand Challenge (E2E)

Tier 4 validates the flagship end-to-end trajectory on the *"Sovereign AI + 6G Edge + Real-Time Settlement"* challenge:
1. **Team Assembly**: Dynamic selection of 9 roles spanning 6 industries (Telecommunications, Finance, AI, Semiconductors, Cybersecurity, Regulation).
2. **6-Stage DAG Execution**:
   - Stage 1: Problem Decomposition & Governance Charters (`Sovereign_Infrastructure_Charter_SLA_Hierarchy.md`, `Regulatory_Compliance_Jurisdictional_Boundary_Map.md`).
   - Stage 2: Parallel Specialist Artifact Creation (6 domain artifacts covering 6G PHY, O-RAN MAC, RTGS DvP, Liquidity stress model, Edge AI inference, PQC HSM BFT).
   - Stage 3: Cross-Role Interface Synthesis (`Unified_EndToEnd_Latency_Capital_Security_Interface_Spec.md`).
   - Stage 4: Adversarial Red-Team & Regulatory Audit Gate:
     - Discovers 3 vulnerabilities:
       1. Post-quantum cryptographic signature latency blowout ($1.4\text{ms}$ CPU verification vs $5.0\text{ms}$ SLA).
       2. Multilateral liquidity gridlock in FIFO queue during volatility spikes (\$1.8B frozen).
       3. Speculative KV-cache data residency leakage across sovereign borders.
     - Gate Verdict: `REJECTED_MANDATORY_REVISION_REQUIRED`.
   - Stage 5: Upstream Revision Loop:
     - Remediation 1: Hardware NTT accelerator coprocessors in HSM ASIC silicon ($120\mu\text{s}$ latency).
     - Remediation 2: Algorithmic AMM Intraday Liquidity Vaults + continuous cycle-canceling Simplex solver.
     - Remediation 3: AMD SEV-SNP memory encryption enclaves + Plonky3 zero-knowledge proof fencing.
   - Stage 6: Master Solution Dossier Compilation:
     - Compiles `Master_Grand_Challenge_Solution_Dossier.md`.
     - Asserts word count $\ge 5,000$ substantive words across all 9 chapters.
     - Obtains Executive Governance & Regulatory Sign-off certification.

---

## 8. Expected Output Derivation & Authoritative Sources

| Metric / Check | Authoritative Source | Required Threshold / Formula |
|---|---|---|
| Macro Industries | `ORIGINAL_REQUEST.md` R1 | $\ge 15$ macro industries |
| Exemplar Organizations | `ORIGINAL_REQUEST.md` R1 | $\ge 45$ organizations ($\ge 3$ per industry) |
| Operating Units | `ORIGINAL_REQUEST.md` R1 | $\ge 100$ units |
| Canonical Roles | `ORIGINAL_REQUEST.md` R2 | $\ge 300$ roles |
| Isolated Roles | `ORIGINAL_REQUEST.md` Phase 1 & 2 AC | Exactly 0 (degree $> 0$ for all roles) |
| Hierarchy Edges | `ORIGINAL_REQUEST.md` Phase 1 & 2 AC | $\text{deg}_{\text{REPORTS\_TO}}(r) \ge 1$ |
| Workflow Edges | `ORIGINAL_REQUEST.md` Phase 1 & 2 AC | $\text{deg}_{\text{workflow}}(r) \ge 2$ |
| Output Artifacts | `ORIGINAL_REQUEST.md` Phase 1 & 2 AC | $\text{out\_deg}_{\text{PRODUCES}}(r) \ge 1$ |
| Prompt Character Count | `ORIGINAL_REQUEST.md` Phase 3 AC | $\ge 1,200$ characters per role |
| Prompt Sections | `ORIGINAL_REQUEST.md` R3 | Exactly 6 mandatory structural sections |
| Prompt Uniqueness | `ORIGINAL_REQUEST.md` Phase 3 AC | $100\%$ unique prompts (0 duplicates) |
| Prompt Stubs | `ORIGINAL_REQUEST.md` Phase 3 AC | 0 stubs (`TODO`, `TBD`, `placeholder`, `...`) |
| BM25 Formula | SQLite FTS5 Specification | $k_1 = 1.2, b = 0.75$ |
| Dense Embedding Space | Latent Semantic Analysis | 128 dimensions, subword n-grams (3,5) |
| RRF Formula | `spec.md` § 6.4 | $RRF(d) = \sum_{m} \frac{1}{60 + r_m(d)}$ |
| Retrieval Recall@10 | `ORIGINAL_REQUEST.md` Phase 3 AC | $\text{Recall}@10 \ge 0.85$ on 25 benchmark queries |
| Retrieval MRR | `ORIGINAL_REQUEST.md` Phase 3 AC | $\text{MRR} \ge 0.70$ on 25 benchmark queries |
| Dual Score Contribution | `ORIGINAL_REQUEST.md` Phase 3 AC | Both sparse and dense contribute to top results |
| Team Selection Size | `ORIGINAL_REQUEST.md` Phase 4 AC | $\ge 8$ roles spanning $\ge 3$ industries |
| DAG Acyclicity | `PROJECT.md` § 5 | $G_{\text{DAG}}$ must be strictly acyclic |
| Audit Critique Cycle | `ORIGINAL_REQUEST.md` Phase 4 AC | At least 1 adversarial rejection triggering revision |
| Master Dossier Length | `ORIGINAL_REQUEST.md` Phase 4 AC | $\ge 5,000$ substantive words across 9 chapters |

---

## 9. Test Execution Matrix & Commands

```bash
# Run all tests in the repository
pytest -v

# Run only E2E acceptance requirements tests
pytest -v tests/test_e2e_requirements.py

# Run Tier 1 feature contract tests
pytest -v tests/test_tier1_features.py

# Run Tier 2 boundary and corner case tests
pytest -v tests/test_tier2_boundaries.py

# Run with coverage report
pytest --cov=orgprompt --cov-report=term-missing tests/
```
