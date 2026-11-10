"""Algorithmic Procedural Seeder for Dual-Layer Tooling and Day-to-Day Role Use Cases."""

import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple
from orgprompt.db.connection import get_connection, init_db

HORIZONTAL_TOOLS: List[Dict[str, Any]] = [
    {
        "id": "tool_word_processor", "slug": "word_processor", "name": "Word & Document Processor",
        "category": "HORIZONTAL_PRODUCTIVITY", "archetype": "WORD_PROCESSOR",
        "vendors": ["Microsoft Word", "Google Docs", "Notion"],
        "artifacts": ["Strategic Memos", "RFC Specifications", "Policy Frameworks", "Executive Briefings"],
        "desc": "Long-form narrative document authoring, collaborative RFC drafting, and governance memos.",
    },
    {
        "id": "tool_spreadsheet_processor", "slug": "spreadsheet_processor", "name": "Spreadsheet & Financial Modeler",
        "category": "HORIZONTAL_PRODUCTIVITY", "archetype": "SPREADSHEET_PROCESSOR",
        "vendors": ["Microsoft Excel", "Google Sheets"],
        "artifacts": ["Financial Models", "CapEx Forecasts", "Variance Analyses", "Tabular Ledgers"],
        "desc": "Quantitative tabular modeling, multi-variable financial projections, and capacity budgeting.",
    },
    {
        "id": "tool_slide_presenter", "slug": "slide_presenter", "name": "Presentation Deck Builder",
        "category": "HORIZONTAL_PRODUCTIVITY", "archetype": "SLIDE_PRESENTER",
        "vendors": ["Microsoft PowerPoint", "Google Slides", "Apple Keynote"],
        "artifacts": ["Executive Briefing Decks", "Board Presentations", "Sprint Review Decks"],
        "desc": "Visual narrative synthesis, executive committee briefings, and milestone stakeholder decks.",
    },
    {
        "id": "tool_meeting_note_taker", "slug": "meeting_note_taker", "name": "Meeting Intelligence & Action Dispatcher",
        "category": "HORIZONTAL_PRODUCTIVITY", "archetype": "MEETING_NOTE_TAKER",
        "vendors": ["Otter.ai", "Zoom AI Companion", "Microsoft Copilot"],
        "artifacts": ["Decision Logs", "Action Graphs", "Commitment Matrices", "Meeting Minutes"],
        "desc": "Real-time multi-speaker transcription, decision extraction, and automated action-item dispatching.",
    },
    {
        "id": "tool_communication_triage", "slug": "communication_triage", "name": "Async Communication & Incident Hub",
        "category": "HORIZONTAL_PRODUCTIVITY", "archetype": "COMMUNICATION_TRIAGE",
        "vendors": ["Slack", "Microsoft Teams", "Microsoft Outlook"],
        "artifacts": ["Incident Escalations", "War Room Threads", "Async Triage Broadcasts"],
        "desc": "High-velocity async communication, team channels, queue triage, and war-room coordination.",
    },
    {
        "id": "tool_bi_analytics", "slug": "bi_analytics", "name": "Business Intelligence & Telemetry Analytics",
        "category": "HORIZONTAL_PRODUCTIVITY", "archetype": "BI_ANALYTICS",
        "vendors": ["Tableau", "Microsoft Power BI", "Looker"],
        "artifacts": ["Executive KPI Dashboards", "Operational Metrics Reports", "Cohort Visualizations"],
        "desc": "Enterprise metrics visualization, SQL dimensional querying, KPI dashboards, and trend analytics.",
    },
]

VERTICAL_TOOLS: List[Dict[str, Any]] = [
    # Finance & Trading
    {"id": "tool_bloomberg_terminal", "slug": "bloomberg_terminal", "name": "Bloomberg Terminal", "archetype": "MARKET_DATA_EXECUTION", "vendors": ["Bloomberg L.P."], "artifacts": ["Market Telemetry", "Yield Curves", "Pricing Feeds"], "desc": "Real-time financial market analytics, multi-asset security pricing, and fixed income execution."},
    {"id": "tool_factset", "slug": "factset", "name": "FactSet Financial Data", "archetype": "PORTFOLIO_ANALYTICS", "vendors": ["FactSet Research Systems"], "artifacts": ["Portfolio Attribution", "Multi-Asset Risk Models"], "desc": "Institutional investment research, fundamental equity modeling, and risk attribution."},
    {"id": "tool_charles_river_ims", "slug": "charles_river_ims", "name": "Charles River IMS", "archetype": "ORDER_MANAGEMENT", "vendors": ["State Street Charles River"], "artifacts": ["Trade Execution Records", "Compliance Pre-Trade Checks"], "desc": "Front-and-middle office investment management, order routing, and portfolio compliance."},
    {"id": "tool_fis_sungard", "slug": "fis_sungard", "name": "FIS SunGard Quantum", "archetype": "TREASURY_RISK_MANAGEMENT", "vendors": ["FIS Global"], "artifacts": ["Treasury Cash Forecasts", "Derivatives Valuations"], "desc": "Corporate treasury operations, balance sheet risk modeling, and liquidity management."},
    # Healthcare & Life Sciences
    {"id": "tool_epic_ehr", "slug": "epic_ehr", "name": "Epic Systems EHR", "archetype": "CLINICAL_HEALTH_RECORD", "vendors": ["Epic Systems"], "artifacts": ["Clinical Care Summaries", "Medication Orders", "Care Pathways"], "desc": "Inpatient and ambulatory electronic health records, order entry, and clinical workflow coordination."},
    {"id": "tool_cerner_millennium", "slug": "cerner_millennium", "name": "Oracle Cerner Millennium", "archetype": "HOSPITAL_OPERATIONS", "vendors": ["Oracle Health"], "artifacts": ["Inpatient Admission Records", "Clinical Flowsheets"], "desc": "Acute care clinical documentation, hospital pharmacy dispensing, and surgical scheduling."},
    {"id": "tool_veeva_vault", "slug": "veeva_vault", "name": "Veeva Vault Clinical", "archetype": "REGULATORY_CLINICAL_CONTENT", "vendors": ["Veeva Systems"], "artifacts": ["Trial Master Files", "FDA Submission Dossiers", "SOP Binders"], "desc": "Life sciences regulatory document management, trial master file oversight, and submission tracking."},
    {"id": "tool_medidata_rave", "slug": "medidata_rave", "name": "Medidata Rave EDC", "archetype": "CLINICAL_DATA_CAPTURE", "vendors": ["Dassault Systèmes Medidata"], "artifacts": ["Case Report Forms", "Clinical Trial Datasets"], "desc": "Electronic data capture, clinical trial data validation, and clinical telemetry aggregation."},
    # Semiconductors & Engineering
    {"id": "tool_synopsys_dc", "slug": "synopsys_dc", "name": "Synopsys Design Compiler", "archetype": "EDA_LOGIC_SYNTHESIS", "vendors": ["Synopsys"], "artifacts": ["Gate-Level Netlists", "Timing Slack Reports", "Area Optimization Constraints"], "desc": "RTL logic synthesis, gate-level timing closure, and silicon area power optimization."},
    {"id": "tool_cadence_innovus", "slug": "cadence_innovus", "name": "Cadence Innovus Implementation", "archetype": "EDA_PHYSICAL_DESIGN", "vendors": ["Cadence Design Systems"], "artifacts": ["Floorplans", "Clock Tree Synthesis Defs", "GDSII Stream Files"], "desc": "Advanced node physical place-and-route, clock tree optimization, and tapeout verification."},
    {"id": "tool_siemens_nx", "slug": "siemens_nx", "name": "Siemens NX CAD/CAM", "archetype": "MECHANICAL_CAD_CAM", "vendors": ["Siemens Digital Industries"], "artifacts": ["3D Parametric CAD Assemblies", "Finite Element Meshes", "CNC Toolpaths"], "desc": "High-precision parametric CAD modeling, multi-axis machining toolpaths, and digital twin engineering."},
    {"id": "tool_dassault_catia", "slug": "dassault_catia", "name": "Dassault Systèmes CATIA", "archetype": "AEROSPACE_SYSTEMS_CAD", "vendors": ["Dassault Systèmes"], "artifacts": ["Digital Mockups", "Aerodynamic Surface Definitions", "Composite Layup Plans"], "desc": "Aerospace surface modeling, complex aerostructures engineering, and digital mockup integration."},
    {"id": "tool_ansys_fluent", "slug": "ansys_fluent", "name": "Ansys Fluent CFD", "archetype": "PHYSICS_SIMULATION_CFD", "vendors": ["Ansys"], "artifacts": ["Aerodynamic Pressure Contours", "Thermal Dissipation Profiles", "Mach Drag Polars"], "desc": "Computational fluid dynamics, supersonic aerodynamics simulation, and thermal dissipation modeling."},
    {"id": "tool_ptc_windchill", "slug": "ptc_windchill", "name": "PTC Windchill PLM", "archetype": "PRODUCT_LIFECYCLE_MGMT", "vendors": ["PTC"], "artifacts": ["Engineering Change Orders", "BOM Hierarchies", "Compliance Baselines"], "desc": "Enterprise product lifecycle management, multi-cad bill of materials, and engineering change control."},
    # Enterprise ERP & Supply Chain
    {"id": "tool_sap_s4hana", "slug": "sap_s4hana", "name": "SAP S/4HANA ERP", "archetype": "ENTERPRISE_ERP", "vendors": ["SAP SE"], "artifacts": ["General Ledger Balances", "Purchase Orders", "Cost Center Summaries"], "desc": "Integrated enterprise resource planning, core general ledger, and global materials management."},
    {"id": "tool_oracle_erp_cloud", "slug": "oracle_erp_cloud", "name": "Oracle ERP Cloud", "archetype": "FINANCIAL_CONSOLIDATION", "vendors": ["Oracle"], "artifacts": ["Intercompany Eliminations", "Treasury Vouchers", "Audit Trail Logs"], "desc": "Global multi-entity financial consolidation, statutory reporting, and automated procurement."},
    {"id": "tool_salesforce_crm", "slug": "salesforce_crm", "name": "Salesforce CRM & Revenue Cloud", "archetype": "COMMERCIAL_CRM", "vendors": ["Salesforce"], "artifacts": ["Sales Opportunity Pipelines", "Customer Account 360 Profiles", "Quotes"], "desc": "Enterprise sales opportunity pipeline tracking, customer account engagement, and CPQ quoting."},
    {"id": "tool_workday_hcm", "slug": "workday_hcm", "name": "Workday HCM & Adaptive Planning", "archetype": "ENTERPRISE_HCM", "vendors": ["Workday"], "artifacts": ["Headcount Budgets", "Talent Succession Matrices", "Compensation Models"], "desc": "Human capital management, workforce planning, payroll administration, and organizational design."},
    {"id": "tool_manhattan_wms", "slug": "manhattan_wms", "name": "Manhattan Associates WMS", "archetype": "WAREHOUSE_MANAGEMENT", "vendors": ["Manhattan Associates"], "artifacts": ["Pallet Routing Manifests", "Slotting Maps", "Pick Waves"], "desc": "Warehouse execution systems, automated picking wave dispatch, and inventory slotting optimization."},
    {"id": "tool_blue_yonder_scm", "slug": "blue_yonder_scm", "name": "Blue Yonder SCM", "archetype": "SUPPLY_CHAIN_PLANNING", "vendors": ["Blue Yonder"], "artifacts": ["Demand Forecast Models", "Safety Stock Parametrizations", "Multi-Echelon Plans"], "desc": "Multi-echelon supply chain planning, machine-learning demand forecasting, and inventory replenishment."},
    # Energy, Industrial & Grids
    {"id": "tool_aspen_plus", "slug": "aspen_plus", "name": "Aspen Plus Process Simulator", "archetype": "PROCESS_SIMULATION", "vendors": ["AspenTech"], "artifacts": ["Refinery Flowsheets", "Thermodynamic Balances", "Emissions Profiles"], "desc": "Continuous chemical process simulation, distillation column design, and mass-energy balance modeling."},
    {"id": "tool_aveva_pi", "slug": "aveva_pi", "name": "AVEVA PI System", "archetype": "TIME_SERIES_HISTORIAN", "vendors": ["AVEVA Group"], "artifacts": ["Industrial Telemetry Logs", "Turbine Vibration Trends", "Tag Value Streams"], "desc": "High-throughput operational time-series data historian, asset telemetry monitoring, and plant analytics."},
    {"id": "tool_ge_grid_solutions", "slug": "ge_grid_solutions", "name": "GE Grid Solutions EMS", "archetype": "ENERGY_MANAGEMENT_SYSTEM", "vendors": ["GE Vernova"], "artifacts": ["Substation Telemetry", "Power Dispatch Schedules", "N-1 Contingency Analyses"], "desc": "Electrical grid transmission dispatch, state estimation, and supervisory control and data acquisition."},
    {"id": "tool_etap_power", "slug": "etap_power", "name": "ETAP Power System Enterprise", "archetype": "ELECTRICAL_GRID_SIMULATION", "vendors": ["ETAP"], "artifacts": ["Load Flow Studies", "Short-Circuit Calculations", "Arc Flash Assessments"], "desc": "Electrical power distribution simulation, transient stability analysis, and relay coordination."},
    # Cybersecurity & Defense
    {"id": "tool_palo_alto_cortex", "slug": "palo_alto_cortex", "name": "Palo Alto Cortex XSOAR", "archetype": "SECURITY_SOAR", "vendors": ["Palo Alto Networks"], "artifacts": ["Incident Playbooks", "Threat IOC Envelopes", "Remediation Workflows"], "desc": "Security orchestration, automated threat hunting playbooks, and incident response triage."},
    {"id": "tool_crowdstrike_falcon", "slug": "crowdstrike_falcon", "name": "CrowdStrike Falcon Platform", "archetype": "ENDPOINT_DETECTION_RESPONSE", "vendors": ["CrowdStrike"], "artifacts": ["Endpoint Telemetry Logs", "Adversary TTP Profiles", "Zero-Trust Attestations"], "desc": "Cloud-native endpoint protection, kernel-level threat detection, and active adversary disruption."},
    {"id": "tool_splunk_siem", "slug": "splunk_siem", "name": "Splunk Enterprise SIEM", "archetype": "SECURITY_INFORMATION_EVENT", "vendors": ["Splunk / Cisco"], "artifacts": ["Correlated Anomaly Alerts", "Audit Investigation Dossiers", "Compliance Reports"], "desc": "Enterprise log aggregation, multi-source telemetry correlation, and compliance monitoring."},
    {"id": "tool_tenable_nessus", "slug": "tenable_nessus", "name": "Tenable Nessus Enterprise", "archetype": "VULNERABILITY_MANAGEMENT", "vendors": ["Tenable"], "artifacts": ["CVE Exposure Matrices", "Asset Risk Scores", "Patch Prioritization Plans"], "desc": "Network vulnerability scanning, zero-day CVE exposure analysis, and configuration auditing."},
    # Telecommunications & Networks
    {"id": "tool_keysight_3gpp", "slug": "keysight_3gpp", "name": "Keysight 3GPP Signaling Analyzer", "archetype": "RF_PROTOCOL_TESTING", "vendors": ["Keysight Technologies"], "artifacts": ["5G NR Conformance Traces", "Carrier Aggregation Logs", "Beamforming IQ Captures"], "desc": "Radio frequency physical layer testing, 3GPP protocol conformance verification, and gNodeB testing."},
    {"id": "tool_wireshark", "slug": "wireshark", "name": "Wireshark Protocol Analyzer", "archetype": "NETWORK_PACKET_INSPECTION", "vendors": ["Wireshark Foundation"], "artifacts": ["PCAP Traces", "TCP Stream Decodes", "Latency Breakdown Profiles"], "desc": "Deep packet inspection, microsecond latency troubleshooting, and network protocol debugging."},
    {"id": "tool_cisco_dna_spaces", "slug": "cisco_dna_spaces", "name": "Cisco Catalyst SD-WAN & DNA", "archetype": "NETWORK_ORCHESTRATION", "vendors": ["Cisco Systems"], "artifacts": ["SD-WAN Routing Policies", "Telemetry Health Baselines", "Fabric Configurations"], "desc": "Software-defined wide area network management, edge routing policy orchestration, and fabric telemetry."},
    {"id": "tool_viavi_solutions", "slug": "viavi_solutions", "name": "VIAVI TeraVM Network Emulation", "archetype": "RAN_CORE_EMULATION", "vendors": ["VIAVI Solutions"], "artifacts": ["Core Network Load Stress Logs", "Throughput Degradation Curves"], "desc": "Virtualised 5G/6G core network emulation, extreme load stress testing, and RAN slice slicing."},
    # Technology, Cloud & DevSecOps
    {"id": "tool_github_enterprise", "slug": "github_enterprise", "name": "GitHub Enterprise Platform", "archetype": "SOURCE_CODE_DEVSECOPS", "vendors": ["GitHub / Microsoft"], "artifacts": ["Git Pull Requests", "CI/CD Actions Manifests", "Security Advisories"], "desc": "Enterprise source code version control, pull request review gates, and automated CI/CD."},
    {"id": "tool_gitlab_cicd", "slug": "gitlab_cicd", "name": "GitLab CI/CD Ultimate", "archetype": "DEVOPS_AUTOMATION", "vendors": ["GitLab"], "artifacts": ["Deployment Pipelines", "Container Vulnerability Scans", "Release Changelogs"], "desc": "End-to-end DevOps automation, continuous integration pipelines, and container security gating."},
    {"id": "tool_aws_console", "slug": "aws_console", "name": "AWS Management Console & CLI", "archetype": "CLOUD_INFRASTRUCTURE_MGMT", "vendors": ["Amazon Web Services"], "artifacts": ["Terraform / CloudFormation Stacks", "IAM Role Policies", "VPC Architecture Maps"], "desc": "Cloud compute, serverless orchestration, enterprise IAM boundaries, and distributed storage."},
    {"id": "tool_snowflake_cloud", "slug": "snowflake_cloud", "name": "Snowflake Data Cloud", "archetype": "CLOUD_DATA_WAREHOUSE", "vendors": ["Snowflake"], "artifacts": ["Analytical Data Marts", "Dynamic Tables", "Cross-Region Data Shares"], "desc": "Elastic cloud data warehousing, SQL transformations, cross-cloud sharing, and data governance."},
    {"id": "tool_databricks", "slug": "databricks", "name": "Databricks Lakehouse Platform", "archetype": "BIG_DATA_ML_PLATFORM", "vendors": ["Databricks"], "artifacts": ["Apache Spark Pipelines", "MLflow Experiment Runs", "Feature Store Tables"], "desc": "Managed Apache Spark distributed computation, MLflow machine learning pipelines, and Delta Lake."},
    {"id": "tool_servicenow_itsm", "slug": "servicenow_itsm", "name": "ServiceNow Enterprise ITSM", "archetype": "IT_SERVICE_MANAGEMENT", "vendors": ["ServiceNow"], "artifacts": ["Change Requests", "CMDB Asset Records", "Incident Escalation Tickets"], "desc": "Enterprise IT service management, ITIL incident lifecycle, change management, and CMDB tracking."},
    {"id": "tool_jira_confluence", "slug": "jira_confluence", "name": "Atlassian Jira & Confluence", "archetype": "AGILE_COLLABORATION_TRACKING", "vendors": ["Atlassian"], "artifacts": ["Sprint Epics", "Architecture RFC Documentation", "Kanban Issue Boards"], "desc": "Agile project tracking, cross-functional sprint planning, and engineering knowledge base management."},
    # Frontier Research, Simulation, Spatial & Legal
    {"id": "tool_matlab_simulink", "slug": "matlab_simulink", "name": "MATLAB & Simulink", "archetype": "SCIENTIFIC_COMPUTING_DSP", "vendors": ["MathWorks"], "artifacts": ["Algorithm M-Files", "Simulink Control Diagrams", "Transfer Functions"], "desc": "High-performance matrix mathematics, digital signal processing algorithms, and control theory modeling."},
    {"id": "tool_relativity_ediscovery", "slug": "relativity_ediscovery", "name": "Relativity eDiscovery Platform", "archetype": "LEGAL_EDISCOVERY_COMPLIANCE", "vendors": ["Relativity"], "artifacts": ["Privilege Logs", "Subpoena Production Packages", "Document Coding Sets"], "desc": "Legal hold tracking, litigation document review, regulatory subpoena productions, and privilege analysis."},
    {"id": "tool_epic_unreal_engine", "slug": "epic_unreal_engine", "name": "Epic Games Unreal Engine", "archetype": "REALTIME_3D_SIMULATION", "vendors": ["Epic Games"], "artifacts": ["Realtime Level Builds", "Shader Graph Shaders", "Physics Simulation Renders"], "desc": "Photorealistic real-time 3D rendering, virtual world simulation, and physics-based environment testing."},
    {"id": "tool_autodesk_maya", "slug": "autodesk_maya", "name": "Autodesk Maya 3D Pipeline", "archetype": "3D_ANIMATION_MODELING", "vendors": ["Autodesk"], "artifacts": ["Character Rigging Sets", "Polygon Meshes", "Animation Keyframe Curves"], "desc": "High-fidelity 3D modeling, skeletal character rigging, procedural texturing, and keyframe animation."},
    {"id": "tool_esri_arcgis", "slug": "esri_arcgis", "name": "Esri ArcGIS Enterprise", "archetype": "GEOSPATIAL_INFORMATION_SYS", "vendors": ["Esri"], "artifacts": ["Geospatial Vector Layers", "Topological Buffer Analyses", "Spatial Risk Choropleths"], "desc": "Geospatial coordinate analysis, sovereign territorial mapping, spatial risk modeling, and GIS telemetry."},
    {"id": "tool_mckinsey_solutions", "slug": "mckinsey_solutions", "name": "Corporate Strategy & Due Diligence Suite", "archetype": "STRATEGIC_ANALYTICS_SUITE", "vendors": ["Alteryx", "McKinsey Solutions"], "artifacts": ["M&A Valuation Models", "Synergy Realization Plans", "Due Diligence Decks"], "desc": "Mergers & acquisitions due diligence, cost transformation benchmarking, and corporate strategic planning."},
]

INDUSTRY_VERTICAL_MAP: Dict[str, List[str]] = {
    "ind_finance_quant": ["tool_bloomberg_terminal", "tool_factset", "tool_charles_river_ims", "tool_fis_sungard"],
    "ind_healthcare_biotech": ["tool_epic_ehr", "tool_cerner_millennium", "tool_veeva_vault", "tool_medidata_rave"],
    "ind_pharmaceuticals": ["tool_veeva_vault", "tool_medidata_rave", "tool_sap_s4hana", "tool_snowflake_cloud"],
    "ind_semiconductors_mfg": ["tool_synopsys_dc", "tool_cadence_innovus", "tool_siemens_nx", "tool_ptc_windchill"],
    "ind_aerospace_defense": ["tool_dassault_catia", "tool_ansys_fluent", "tool_siemens_nx", "tool_ptc_windchill"],
    "ind_autonomous_robotics": ["tool_siemens_nx", "tool_ansys_fluent", "tool_matlab_simulink", "tool_github_enterprise"],
    "ind_energy_grids": ["tool_aspen_plus", "tool_aveva_pi", "tool_ge_grid_solutions", "tool_etap_power"],
    "ind_cybersecurity": ["tool_palo_alto_cortex", "tool_crowdstrike_falcon", "tool_splunk_siem", "tool_tenable_nessus"],
    "ind_telecommunications": ["tool_keysight_3gpp", "tool_wireshark", "tool_cisco_dna_spaces", "tool_viavi_solutions"],
    "ind_technology_ai": ["tool_github_enterprise", "tool_gitlab_cicd", "tool_aws_console", "tool_snowflake_cloud", "tool_databricks"],
    "ind_retail_consumer": ["tool_sap_s4hana", "tool_salesforce_crm", "tool_manhattan_wms", "tool_blue_yonder_scm"],
    "ind_global_logistics": ["tool_manhattan_wms", "tool_blue_yonder_scm", "tool_sap_s4hana", "tool_oracle_erp_cloud"],
    "ind_professional_services": ["tool_salesforce_crm", "tool_workday_hcm", "tool_mckinsey_solutions", "tool_snowflake_cloud"],
    "ind_public_sector_reg": ["tool_relativity_ediscovery", "tool_esri_arcgis", "tool_servicenow_itsm", "tool_splunk_siem"],
    "ind_frontier_research": ["tool_matlab_simulink", "tool_databricks", "tool_github_enterprise", "tool_ansys_fluent"],
    "ind_creative_media": ["tool_epic_unreal_engine", "tool_autodesk_maya", "tool_jira_confluence", "tool_github_enterprise"],
}


def seed_tools_catalog(conn: sqlite3.Connection) -> int:
    """Inserts horizontal and vertical tools into the tools table."""
    all_tools = HORIZONTAL_TOOLS + VERTICAL_TOOLS
    rows = []
    for t in all_tools:
        rows.append((
            t["id"], t["slug"], t["name"], t.get("category", "VERTICAL_DOMAIN"), t["archetype"],
            json.dumps(t["vendors"]), json.dumps(t["artifacts"]), t["desc"],
            json.dumps({"vendor_count": len(t["vendors"]), "artifact_count": len(t["artifacts"])}),
        ))
    conn.executemany("""
        INSERT OR REPLACE INTO tools (
            id, slug, name, category, archetype, vendor_examples_json, typical_artifacts_json, description, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    return len(rows)


def select_role_tools(archetype: str, seniority: str, ind_id: str) -> Tuple[List[str], List[Tuple[str, str, str, str]]]:
    """Determines horizontal & vertical tools plus role_tooling metadata for a role."""
    h_tools = []
    if archetype == "executive_strategy" or seniority in ("C_SUITE", "VP", "DIRECTOR"):
        h_tools = ["tool_word_processor", "tool_slide_presenter", "tool_meeting_note_taker", "tool_communication_triage"]
    elif archetype == "engineering_staff":
        h_tools = ["tool_word_processor", "tool_communication_triage", "tool_spreadsheet_processor", "tool_bi_analytics"]
    elif archetype == "operations":
        h_tools = ["tool_spreadsheet_processor", "tool_bi_analytics", "tool_communication_triage", "tool_meeting_note_taker"]
    elif archetype == "risk_compliance":
        h_tools = ["tool_word_processor", "tool_spreadsheet_processor", "tool_slide_presenter", "tool_communication_triage"]
    else:  # domain_specialist
        h_tools = ["tool_word_processor", "tool_bi_analytics", "tool_meeting_note_taker", "tool_communication_triage"]

    v_candidates = INDUSTRY_VERTICAL_MAP.get(ind_id, ["tool_sap_s4hana", "tool_github_enterprise", "tool_bi_analytics"])
    v_tools = v_candidates[:2] if len(v_candidates) >= 2 else v_candidates

    tooling_entries = []
    # Primary horizontal
    tooling_entries.append((h_tools[0], "PRIMARY_DAILY", "EXPERT", f"Core narrative and specification authoring for {archetype.replace('_', ' ')}."))
    tooling_entries.append((h_tools[1], "PRIMARY_DAILY", "EXPERT", f"Operational modeling and stakeholder presentation synthesis."))
    tooling_entries.append((h_tools[2], "FREQUENT_WEEKLY", "PROFICIENT", f"Collaborative decision tracking and cross-functional sync."))
    if len(h_tools) > 3:
        tooling_entries.append((h_tools[3], "FREQUENT_WEEKLY", "PROFICIENT", f"High-velocity async communication and escalation triage."))
    # Vertical tools
    for idx, vt in enumerate(v_tools):
        freq = "PRIMARY_DAILY" if idx == 0 else "FREQUENT_WEEKLY"
        tooling_entries.append((vt, freq, "EXPERT", f"Primary domain execution platform for {ind_id.replace('ind_', '').replace('_', ' ')} workflows."))

    return h_tools, tooling_entries


def seed_use_cases_and_tooling(conn: sqlite3.Connection) -> Tuple[int, int]:
    """Generates >= 4 structured operational use cases and role_tooling associations per role."""
    cur = conn.cursor()
    cur.execute("""
        SELECT r.id, r.name, r.seniority_level, r.role_archetype, i.id, i.name
        FROM canonical_roles r
        JOIN org_units u ON r.org_unit_id = u.id
        JOIN exemplar_orgs o ON u.exemplar_org_id = o.id
        JOIN industries i ON o.industry_id = i.id
        ORDER BY r.id
    """)
    roles = cur.fetchall()

    use_case_rows = []
    tooling_rows = []

    for r_id, r_name, seniority, archetype, ind_id, ind_name in roles:
        h_tools, tool_entries = select_role_tools(archetype, seniority, ind_id)
        v_tools = [t[0] for t in tool_entries if t[0].startswith("tool_") and t[0] not in h_tools]
        clean_ind = ind_name.split(",")[0].strip()

        # Wire role_tooling records
        for t_id, freq, prof, purp in tool_entries:
            rt_id = f"rt_{r_id}_{t_id}"
            tooling_rows.append((rt_id, r_id, t_id, freq, prof, purp, json.dumps({"industry": ind_id})))

        # 5 Structured Operational Use Cases per Role
        use_cases = [
            (
                f"ruc_{r_id}_1", r_id, f"{r_name}: Daily Operational Queue Triage & Handoff Sync",
                "DAILY", f"Receipt of overnight telemetry alerts, system handoff logs, and priority dispatch queues in {clean_ind}.",
                [f"{clean_ind} Telemetry Streams", "Prior Shift Handover Log", "Urgent Ticket Queue"],
                [h_tools[0], h_tools[-1]], [v_tools[0]] if v_tools else ["tool_bi_analytics"],
                f"High-velocity prioritization under strict SLA constraints; reconciling conflicting stakeholder signals without stalling critical execution pathways.",
                [f"{r_name} Daily Priority Matrix", "Escalation Handoff Briefing"],
            ),
            (
                f"ruc_{r_id}_2", r_id, f"{r_name}: Weekly Core Deliverable Synthesis & Milestone Review",
                "WEEKLY", f"Scheduled sprint delivery milestone and peer cross-functional review cycle.",
                [f"Draft {r_name} Specification", "Subsystem Telemetry Logs", "Dependency Architecture Specs"],
                [h_tools[0], h_tools[1]], v_tools[:2] if len(v_tools) >= 2 else v_tools,
                f"Translating domain-specific technical complexities into modular, robust deliverables while preserving backwards compatibility and safety margins.",
                [f"{r_name} Milestone Delivery Package", "Peer Technical Review Memo"],
            ),
            (
                f"ruc_{r_id}_3", r_id, f"{r_name}: Monthly Performance Analysis & Variance Reconciliation",
                "MONTHLY", f"Monthly operating review, budget variance audit, and throughput health assessment.",
                [f"Monthly Operating Ledger", f"{clean_ind} Throughput Metrics", "Historical Benchmark Baseline"],
                ["tool_spreadsheet_processor", "tool_bi_analytics"], [v_tools[0]] if v_tools else ["tool_sap_s4hana"],
                f"Isolating genuine systemic process degradation from transient environmental noise across multi-variable operational parameters.",
                [f"{r_name} Operational Variance Dossier", "Executive Performance Scorecard"],
            ),
            (
                f"ruc_{r_id}_4", r_id, f"{r_name}: Quarterly Strategic Governance Gate & Capability Audit",
                "QUARTERLY", f"Quarterly executive committee review, capability roadmap gate, and regulatory audit cycle.",
                [f"Quarterly Performance Retrospective", "Regulatory Compliance Baselines", "Enterprise Strategic Plan"],
                ["tool_slide_presenter", "tool_word_processor"], v_tools[:1],
                f"Synthesizing long-term resilience, regulatory compliance, and capital efficiency against immediate competitive delivery pressures.",
                [f"{r_name} Quarterly Roadmap Deck", "Governance Compliance Attestation"],
            ),
            (
                f"ruc_{r_id}_5", r_id, f"{r_name}: Critical Incident Root Cause Analysis & Escalation Defense",
                "AD_HOC", f"Unplanned Sev-1 system anomaly, adversarial audit challenge, or regulatory inquiry.",
                ["Raw Incident Core Dumps", "Audit Challenge Brief", "Network Diagnostic Traces"],
                ["tool_meeting_note_taker", "tool_communication_triage"], [v_tools[0]] if v_tools else ["tool_splunk_siem"],
                f"Executing rapid forensic hypothesis testing under extreme operational pressure without contaminating post-incident investigative integrity.",
                [f"{r_name} Root Cause Post-Mortem", "Corrective Action Implementation Plan"],
            ),
        ]

        for u_id, role_fk, title, cad, trig, inps, hts, vts, bot, outs in use_cases:
            use_case_rows.append((
                u_id, role_fk, title, cad, trig, json.dumps(inps), json.dumps(hts), json.dumps(vts),
                bot, json.dumps(outs), json.dumps({"role_seniority": seniority, "industry": ind_id}),
            ))

    # Clean existing rows to allow idempotent re-seeding
    conn.execute("DELETE FROM role_tooling")
    conn.execute("DELETE FROM role_use_cases")

    conn.executemany("""
        INSERT INTO role_tooling (
            id, role_id, tool_id, usage_frequency, proficiency_level, primary_purpose, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, tooling_rows)

    conn.executemany("""
        INSERT INTO role_use_cases (
            id, role_id, title, cadence, trigger_event, inputs_consumed_json,
            horizontal_tools_json, vertical_tools_json, cognitive_bottlenecks,
            output_artifacts_json, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, use_case_rows)

    return len(use_case_rows), len(tooling_rows)


def main() -> None:
    """Executes database schema initialization and dual-layer tooling seeder."""
    conn = get_connection()
    init_db()

    tools_count = seed_tools_catalog(conn)
    use_cases_count, tooling_count = seed_use_cases_and_tooling(conn)
    conn.commit()

    # Integrity verification
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_key_check")
    fk_violations = cur.fetchall()
    if fk_violations:
        print(f"FAILED: Found {len(fk_violations)} foreign key violations: {fk_violations}")
        sys.exit(1)

    cur.execute("SELECT COUNT(DISTINCT role_id) FROM role_use_cases GROUP BY role_id HAVING COUNT(*) < 4")
    under_represented = cur.fetchall()
    if under_represented:
        print(f"FAILED: Found roles with < 4 use cases: {len(under_represented)}")
        sys.exit(1)

    print(f"SUCCESS: Seeded {tools_count} tools, {use_cases_count} use cases, {tooling_count} role_tooling records.")


if __name__ == "__main__":
    main()
