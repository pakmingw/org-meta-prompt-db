-- ==============================================================================
-- SQLite Relational Schema for Organizational Knowledge Graph & Role Database
-- 9 Typed Tables, Foreign Keys, Indexes, FTS5 Virtual Table, and Triggers
-- ==============================================================================

PRAGMA foreign_keys = ON;

-- 1. Industries Table
CREATE TABLE IF NOT EXISTS industries (
    id TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Exemplar Organizations Table
CREATE TABLE IF NOT EXISTS exemplar_orgs (
    id TEXT PRIMARY KEY,
    industry_id TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    signature_mechanisms_summary TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (industry_id) REFERENCES industries(id) ON DELETE CASCADE
);

-- 3. Organizational Units Table
CREATE TABLE IF NOT EXISTS org_units (
    id TEXT PRIMARY KEY,
    exemplar_org_id TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    division TEXT NOT NULL,
    department TEXT NOT NULL,
    unit_type TEXT NOT NULL CHECK(unit_type IN ('R_AND_D', 'ENGINEERING', 'OPERATIONS', 'GOVERNANCE', 'PRODUCT', 'COMMERCIAL')),
    description TEXT NOT NULL,
    core_value_loop TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exemplar_org_id) REFERENCES exemplar_orgs(id) ON DELETE CASCADE
);

-- 4. Canonical Roles Table
CREATE TABLE IF NOT EXISTS canonical_roles (
    id TEXT PRIMARY KEY,
    org_unit_id TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    seniority_level TEXT NOT NULL CHECK(seniority_level IN ('C_SUITE', 'VP', 'DIRECTOR', 'PRINCIPAL_STAFF', 'SENIOR_SPECIALIST', 'LEAD_AUDITOR', 'OPERATIONS_COMMANDER')),
    role_archetype TEXT NOT NULL CHECK(role_archetype IN ('executive_strategy', 'engineering_staff', 'domain_specialist', 'operations', 'risk_compliance')),
    mission TEXT NOT NULL,
    system_prompt TEXT NOT NULL,
    character_count INTEGER NOT NULL,
    capabilities_json TEXT NOT NULL DEFAULT '[]',
    mental_models_json TEXT NOT NULL DEFAULT '[]',
    domain_heuristics_json TEXT NOT NULL DEFAULT '[]',
    technical_vocabulary_json TEXT NOT NULL DEFAULT '[]',
    anti_patterns_json TEXT NOT NULL DEFAULT '[]',
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (org_unit_id) REFERENCES org_units(id) ON DELETE CASCADE
);

-- 5. Artifacts Table
CREATE TABLE IF NOT EXISTS artifacts (
    id TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    artifact_type TEXT NOT NULL CHECK(artifact_type IN ('SPECIFICATION', 'MODEL', 'POLICY', 'CODE', 'DOSSIER', 'AUDIT_REPORT', 'DATASET')),
    schema_definition TEXT NOT NULL,
    description TEXT NOT NULL,
    exemplar_context TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Operating Mechanisms Table
CREATE TABLE IF NOT EXISTS operating_mechanisms (
    id TEXT PRIMARY KEY,
    exemplar_org_id TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    mechanism_type TEXT NOT NULL CHECK(mechanism_type IN ('GATE', 'CADENCE', 'AUDIT', 'REVIEW_COUNCIL', 'PROBLEM_SOLVING')),
    description TEXT NOT NULL,
    execution_steps_json TEXT NOT NULL DEFAULT '[]',
    enforcement_rules TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (exemplar_org_id) REFERENCES exemplar_orgs(id) ON DELETE CASCADE
);

-- 7. Role Edges Table
CREATE TABLE IF NOT EXISTS role_edges (
    id TEXT PRIMARY KEY,
    source_role_id TEXT NOT NULL,
    target_role_id TEXT NOT NULL,
    edge_type TEXT NOT NULL CHECK(edge_type IN ('REPORTS_TO', 'COLLABORATES_WITH', 'HANDS_OFF_TO', 'REVIEWS_AND_GATES', 'CHALLENGES_OR_AUDITS')),
    description TEXT NOT NULL,
    protocol TEXT DEFAULT '',
    cadence TEXT DEFAULT '',
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_role_id) REFERENCES canonical_roles(id) ON DELETE CASCADE,
    FOREIGN KEY (target_role_id) REFERENCES canonical_roles(id) ON DELETE CASCADE,
    UNIQUE(source_role_id, target_role_id, edge_type)
);

-- 8. Role Artifacts Table
CREATE TABLE IF NOT EXISTS role_artifacts (
    id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,
    artifact_id TEXT NOT NULL,
    direction TEXT NOT NULL CHECK(direction IN ('PRODUCES', 'CONSUMES')),
    frequency TEXT DEFAULT 'PER_MILESTONE',
    description TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES canonical_roles(id) ON DELETE CASCADE,
    FOREIGN KEY (artifact_id) REFERENCES artifacts(id) ON DELETE CASCADE,
    UNIQUE(role_id, artifact_id, direction)
);

-- 9. Role Mechanisms Table
CREATE TABLE IF NOT EXISTS role_mechanisms (
    id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,
    mechanism_id TEXT NOT NULL,
    participation_level TEXT NOT NULL CHECK(participation_level IN ('CHAIRS', 'PARTICIPATES', 'ENFORCES', 'AUDITED_BY')),
    description TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES canonical_roles(id) ON DELETE CASCADE,
    FOREIGN KEY (mechanism_id) REFERENCES operating_mechanisms(id) ON DELETE CASCADE,
    UNIQUE(role_id, mechanism_id)
);

-- Relational Indexes
CREATE INDEX IF NOT EXISTS idx_exemplar_orgs_industry ON exemplar_orgs(industry_id);
CREATE INDEX IF NOT EXISTS idx_org_units_org ON org_units(exemplar_org_id);
CREATE INDEX IF NOT EXISTS idx_canonical_roles_unit ON canonical_roles(org_unit_id);
CREATE INDEX IF NOT EXISTS idx_canonical_roles_seniority ON canonical_roles(seniority_level);
CREATE INDEX IF NOT EXISTS idx_canonical_roles_archetype ON canonical_roles(role_archetype);
CREATE INDEX IF NOT EXISTS idx_role_edges_source ON role_edges(source_role_id);
CREATE INDEX IF NOT EXISTS idx_role_edges_target ON role_edges(target_role_id);
CREATE INDEX IF NOT EXISTS idx_role_edges_type ON role_edges(edge_type);
CREATE INDEX IF NOT EXISTS idx_role_artifacts_role ON role_artifacts(role_id);
CREATE INDEX IF NOT EXISTS idx_role_artifacts_artifact ON role_artifacts(artifact_id);
CREATE INDEX IF NOT EXISTS idx_role_mechanisms_role ON role_mechanisms(role_id);
CREATE INDEX IF NOT EXISTS idx_role_mechanisms_mech ON role_mechanisms(mechanism_id);

-- FTS5 Virtual Table for BM25 Search
CREATE VIRTUAL TABLE IF NOT EXISTS roles_fts USING fts5(
    role_id UNINDEXED,
    name,
    industry,
    org_unit,
    mission,
    capabilities,
    mental_models,
    system_prompt,
    tokenize = 'porter unicode61'
);

-- Real-time Sync Trigger: INSERT
CREATE TRIGGER IF NOT EXISTS trg_roles_ai AFTER INSERT ON canonical_roles
BEGIN
    INSERT INTO roles_fts(
        role_id, name, industry, org_unit, mission, capabilities, mental_models, system_prompt
    )
    SELECT
        new.id,
        new.name,
        i.name,
        u.name,
        new.mission,
        new.capabilities_json,
        new.mental_models_json,
        new.system_prompt
    FROM org_units u
    JOIN exemplar_orgs o ON u.exemplar_org_id = o.id
    JOIN industries i ON o.industry_id = i.id
    WHERE u.id = new.org_unit_id;
END;

-- Real-time Sync Trigger: UPDATE
CREATE TRIGGER IF NOT EXISTS trg_roles_au AFTER UPDATE ON canonical_roles
BEGIN
    DELETE FROM roles_fts WHERE role_id = old.id;
    INSERT INTO roles_fts(
        role_id, name, industry, org_unit, mission, capabilities, mental_models, system_prompt
    )
    SELECT
        new.id,
        new.name,
        i.name,
        u.name,
        new.mission,
        new.capabilities_json,
        new.mental_models_json,
        new.system_prompt
    FROM org_units u
    JOIN exemplar_orgs o ON u.exemplar_org_id = o.id
    JOIN industries i ON o.industry_id = i.id
    WHERE u.id = new.org_unit_id;
END;

-- Real-time Sync Trigger: DELETE
CREATE TRIGGER IF NOT EXISTS trg_roles_ad AFTER DELETE ON canonical_roles
BEGIN
    DELETE FROM roles_fts WHERE role_id = old.id;
END;

-- ==============================================================================
-- 10. Fortune 500 Companies Table
-- ==============================================================================
CREATE TABLE IF NOT EXISTS fortune500_companies (
    id TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    rank INTEGER NOT NULL UNIQUE,
    revenue_billions REAL NOT NULL,
    macro_industry TEXT NOT NULL,
    industry_id TEXT NOT NULL,
    sub_sector TEXT NOT NULL,
    business_model TEXT NOT NULL CHECK(business_model IN (
        'HIGH_VELOCITY_DISTRIBUTOR',
        'MULTI_SIDED_PLATFORM',
        'RECURRING_SUBSCRIPTION_SAAS',
        'ASSET_HEAVY_MANUFACTURER',
        'FINANCIAL_RISK_INTERMEDIARY',
        'INTEGRATED_ENERGY_OPERATOR',
        'CLINICAL_LIFE_SCIENCES_INNOVATOR',
        'PROFESSIONAL_KNOWLEDGE_ADVISORY'
    )),
    operating_archetype TEXT NOT NULL CHECK(operating_archetype IN (
        'UNIFICATION',
        'COORDINATION',
        'REPLICATION',
        'DIVERSIFICATION',
        'PLATFORM_ECOSYSTEM'
    )),
    functional_units_json TEXT NOT NULL DEFAULT '[]',
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (industry_id) REFERENCES industries(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_f500_rank ON fortune500_companies(rank);
CREATE INDEX IF NOT EXISTS idx_f500_industry ON fortune500_companies(industry_id);
CREATE INDEX IF NOT EXISTS idx_f500_macro_industry ON fortune500_companies(macro_industry);
CREATE INDEX IF NOT EXISTS idx_f500_archetype ON fortune500_companies(operating_archetype);
CREATE INDEX IF NOT EXISTS idx_f500_model ON fortune500_companies(business_model);

-- Trigger: fortune500_companies updated_at
CREATE TRIGGER IF NOT EXISTS trg_f500_au AFTER UPDATE ON fortune500_companies
BEGIN
    UPDATE fortune500_companies SET updated_at = CURRENT_TIMESTAMP WHERE id = old.id;
END;

-- ==============================================================================
-- 11. Employs Role Edges Table (>= 15,000 High-Density Bipartite Graph Edges)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS employs_role (
    id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    role_id TEXT NOT NULL,
    department TEXT NOT NULL,
    priority_tier TEXT NOT NULL CHECK(priority_tier IN (
        'STRATEGIC_LEADERSHIP',
        'SHARED_SERVICE',
        'CORE',
        'SPECIALIZED',
        'CORE_MISSION',
        'STRATEGIC_DIFFERENTIATOR',
        'OPERATIONAL_STANDARD',
        'SUPPORTING'
    )),
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES fortune500_companies(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES canonical_roles(id) ON DELETE CASCADE,
    UNIQUE(company_id, role_id)
);

CREATE INDEX IF NOT EXISTS idx_employs_role_company ON employs_role(company_id);
CREATE INDEX IF NOT EXISTS idx_employs_role_role ON employs_role(role_id);
CREATE INDEX IF NOT EXISTS idx_employs_role_priority ON employs_role(priority_tier);
CREATE INDEX IF NOT EXISTS idx_employs_role_dept ON employs_role(department);

-- ==============================================================================
-- 12. Company Internet Comparisons Table
-- ==============================================================================
CREATE TABLE IF NOT EXISTS company_internet_comparisons (
    id TEXT PRIMARY KEY,
    company_id TEXT NOT NULL,
    f500_rank INTEGER NOT NULL,
    company_name TEXT NOT NULL,
    internet_divisions_json TEXT NOT NULL DEFAULT '[]',
    internet_bespoke_roles_json TEXT NOT NULL DEFAULT '[]',
    db_mapped_roles_count INTEGER NOT NULL DEFAULT 0,
    alignment_score REAL NOT NULL DEFAULT 1.0,
    delta_analysis_md TEXT NOT NULL DEFAULT '',
    tailored_swarm_recommendation_md TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES fortune500_companies(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_cic_company ON company_internet_comparisons(company_id);
CREATE INDEX IF NOT EXISTS idx_cic_rank ON company_internet_comparisons(f500_rank);

-- ==============================================================================
-- 13. Tools Table (Horizontal Productivity & Vertical Domain Platforms)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS tools (
    id TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    category TEXT NOT NULL CHECK(category IN ('HORIZONTAL_PRODUCTIVITY', 'VERTICAL_DOMAIN')),
    archetype TEXT NOT NULL,
    vendor_examples_json TEXT NOT NULL DEFAULT '[]',
    typical_artifacts_json TEXT NOT NULL DEFAULT '[]',
    description TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tools_category ON tools(category);
CREATE INDEX IF NOT EXISTS idx_tools_archetype ON tools(archetype);

-- ==============================================================================
-- 14. Role Use Cases Table (Day-to-Day Operational Anatomy)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS role_use_cases (
    id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,
    title TEXT NOT NULL,
    cadence TEXT NOT NULL CHECK(cadence IN ('DAILY', 'WEEKLY', 'MONTHLY', 'QUARTERLY', 'AD_HOC', 'CONTINUOUS')),
    trigger_event TEXT NOT NULL,
    inputs_consumed_json TEXT NOT NULL DEFAULT '[]',
    horizontal_tools_json TEXT NOT NULL DEFAULT '[]',
    vertical_tools_json TEXT NOT NULL DEFAULT '[]',
    cognitive_bottlenecks TEXT NOT NULL,
    output_artifacts_json TEXT NOT NULL DEFAULT '[]',
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES canonical_roles(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ruc_role ON role_use_cases(role_id);
CREATE INDEX IF NOT EXISTS idx_ruc_cadence ON role_use_cases(cadence);

-- ==============================================================================
-- 15. Role Tooling Table (Bipartite Role-Tool Proficiency & Purpose)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS role_tooling (
    id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL,
    tool_id TEXT NOT NULL,
    usage_frequency TEXT NOT NULL CHECK(usage_frequency IN ('PRIMARY_DAILY', 'FREQUENT_WEEKLY', 'OCCASIONAL', 'CRITICAL_INCIDENT')),
    proficiency_level TEXT NOT NULL CHECK(proficiency_level IN ('EXPERT', 'PROFICIENT', 'WORKING_KNOWLEDGE', 'BASIC')),
    primary_purpose TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES canonical_roles(id) ON DELETE CASCADE,
    FOREIGN KEY (tool_id) REFERENCES tools(id) ON DELETE CASCADE,
    UNIQUE(role_id, tool_id)
);

CREATE INDEX IF NOT EXISTS idx_rt_role ON role_tooling(role_id);
CREATE INDEX IF NOT EXISTS idx_rt_tool ON role_tooling(tool_id);

-- ==============================================================================
-- 16. Role Subagent Swarms Table ("Role-in-a-Box")
-- ==============================================================================
CREATE TABLE IF NOT EXISTS role_subagent_swarms (
    id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL REFERENCES canonical_roles(id) ON DELETE CASCADE,
    subagent_name TEXT NOT NULL,
    subagent_role TEXT NOT NULL CHECK(subagent_role IN (
        'CHIEF_OF_STAFF',
        'DOCUMENT_DRAFTER',
        'QUANTITATIVE_MODELER',
        'DECK_PRESENTER',
        'MEETING_GRAPH',
        'DOMAIN_SPECIALIST',
        'QUALITY_CRITIC'
    )),
    system_prompt TEXT NOT NULL,
    tool_mcp_bindings_json TEXT NOT NULL DEFAULT '[]',
    interaction_dag_json TEXT NOT NULL DEFAULT '{}',
    hitl_checkpoint TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, subagent_role)
);

CREATE INDEX IF NOT EXISTS idx_rss_role ON role_subagent_swarms(role_id);
CREATE INDEX IF NOT EXISTS idx_rss_subagent_role ON role_subagent_swarms(subagent_role);

-- ==============================================================================
-- 17. Role GenAI Plans Table (Engineering Blueprint for Tooling & GenAI)
-- ==============================================================================
CREATE TABLE IF NOT EXISTS role_genai_plans (
    id TEXT PRIMARY KEY,
    role_id TEXT NOT NULL REFERENCES canonical_roles(id) ON DELETE CASCADE,
    horizontal_genai_spec_json TEXT NOT NULL DEFAULT '{}',
    vertical_genai_spec_json TEXT NOT NULL DEFAULT '{}',
    rag_context_architecture TEXT NOT NULL,
    mcp_integrations_json TEXT NOT NULL DEFAULT '[]',
    hitl_guardrails TEXT NOT NULL,
    roi_productivity_impact TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id)
);

CREATE INDEX IF NOT EXISTS idx_rgp_role ON role_genai_plans(role_id);

