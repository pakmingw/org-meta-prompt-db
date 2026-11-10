"""Procedural Meta-Prompt Compiler for Canonical Professional Roles."""

from typing import Any, Dict, List, Optional
import json


class PromptCompiler:
    """Compiles deeply engineered, domain-authentic 6-section System Prompts."""

    MANDATORY_SECTIONS = [
        "1. Role Identity & Exemplar Lineage",
        "2. First-Principles Mental Models & Domain Heuristics",
        "3. Technical Vocabulary & Standards",
        "4. Anti-Patterns & Mediocrity Filters",
        "5. Collaboration, Handoff & Escalation Protocols",
        "6. Concrete Output Artifact Schemas",
    ]

    @classmethod
    def compile(cls, role_data: Dict[str, Any]) -> str:
        """Compiles a complete 6-section markdown prompt meeting the >=1,200 char threshold."""
        title = role_data.get("title") or role_data.get("name", "Specialist")
        seniority = role_data.get("seniority_tier") or role_data.get(
            "seniority_level", "PRINCIPAL_STAFF"
        )
        archetype = role_data.get("role_archetype", "engineering_staff")
        exemplar = role_data.get("exemplar", "World-Class Exemplar")
        unit = role_data.get("unit", "Operations & Engineering Division")
        mission = role_data.get(
            "mission",
            f"Execute fiduciary and operational responsibilities as {title} with zero-defect rigor.",
        )
        lineage = role_data.get(
            "exemplar_lineage",
            f"Derived from world-class practices at {exemplar}, emphasizing empirical rigor, high agency, and structural integrity.",
        )

        mental_models: List[str] = role_data.get("mental_models", [])
        if not mental_models and role_data.get("mental_models_json"):
            try:
                mental_models = json.loads(role_data["mental_models_json"])
            except Exception:
                mental_models = []

        heuristics: List[str] = role_data.get("heuristics") or role_data.get(
            "domain_heuristics", []
        )
        vocabulary: List[str] = role_data.get("vocabulary") or role_data.get(
            "technical_vocabulary", []
        )
        anti_patterns: List[str] = role_data.get("anti_patterns", [])

        edges: Dict[str, List[str]] = role_data.get("edges", {})
        output_artifact = (
            role_data.get("output_artifact")
            or role_data.get("output_artifact_name")
            or f"{title.replace(' ', '_')}_Technical_Specification"
        )
        input_artifact = (
            role_data.get("input_artifact")
            or role_data.get("input_artifact_name")
            or "Upstream_Requirements_And_Architecture_Directive"
        )

        # Build Section 1: Role Identity & Exemplar Lineage
        sec1 = (
            f"## 1. Role Identity & Exemplar Lineage\n"
            f"- **Role Title**: {title}\n"
            f"- **Seniority Level**: {seniority}\n"
            f"- **Functional Archetype**: {archetype}\n"
            f"- **Exemplar Organization & Unit**: {exemplar} — {unit}\n"
            f"- **Operational Mission**: {mission}\n"
            f"- **Founding Lineage & Ethos**: {lineage}\n"
            f"You represent the highest echelon of domain execution within your industry. "
            f"Your fiduciary responsibility is to uphold world-class standards, refusing compromises on technical "
            f"depth, analytical fidelity, and systematic verification. You act with the decisive ownership expected of "
            f"an elite practitioner at {exemplar}."
        )

        # Build Section 2: First-Principles Mental Models & Domain Heuristics
        models_bullets = "\n".join([f"- **{m}**: Apply rigorous first-principles thinking, decomposing problems to fundamental axioms before synthesis." for m in mental_models]) if mental_models else "- **First-Principles Decomposition**: Deconstruct complex systems into fundamental thermodynamic, mathematical, and logical invariants.\n- **Zero-Tolerance Defect Analysis**: Treat anomalies as signals of underlying system design gaps."
        heuristics_bullets = "\n".join([f"- **Operational Heuristic**: {h}" for h in heuristics]) if heuristics else "- **Root-Cause Isolation**: Never mask symptoms; trace every degradation to root causes before proposing mitigations.\n- **Quantified Trade-off Analysis**: Evaluate every architecture through explicit pareto frontier modeling."

        sec2 = (
            f"## 2. First-Principles Mental Models & Domain Heuristics\n"
            f"### Foundational Mental Models\n"
            f"{models_bullets}\n\n"
            f"### Domain Decision Heuristics\n"
            f"{heuristics_bullets}\n"
            f"- Never accept unverified assertions. Require verifiable empirical telemetry, reproducible unit tests, or formal mathematical proofs.\n"
            f"- Optimize for global end-to-end efficiency and systemic stability rather than local subsystem convenience."
        )

        # Build Section 3: Technical Vocabulary & Standards
        vocab_bullets = "\n".join([f"- `{v}`: Rigorously defined domain terminology and conformance standard." for v in vocabulary]) if vocabulary else "- `ISO/IEC/IEEE Standards`: Conformance with international technical baselines.\n- `SLA/SLO Verification`: Precise mathematical specification of service level commitments."

        sec3 = (
            f"## 3. Technical Vocabulary & Standards\n"
            f"You communicate with uncompromising technical precision using established standards and domain terminology:\n"
            f"{vocab_bullets}\n"
            f"- All interfaces must specify explicit error contracts, throughput bounds, latency percentiles (p50, p99, p99.9), and deterministic state transitions."
        )

        # Build Section 4: Anti-Patterns & Mediocrity Filters
        anti_bullets = "\n".join([f"- ❌ **{ap}**: Reject outright; identify immediately during review gates." for ap in anti_patterns]) if anti_patterns else "- ❌ **Surface-Level Generalization**: Avoid vague hand-waving without concrete specifications or mathematical models.\n- ❌ **Unchecked Assumption Passing**: Never pass unverified assumptions across organizational handoff boundaries."

        sec4 = (
            f"## 4. Anti-Patterns & Mediocrity Filters\n"
            f"You aggressively detect and reject the following domain failure modes:\n"
            f"{anti_bullets}\n"
            f"- ❌ **Facade Compliance**: Superficial paperwork that disguises deep architectural flaws.\n"
            f"- ❌ **Deferred Reliability**: Postponing stress testing, edge-case analysis, or adversarial red-teaming to downstream phases."
        )

        # Build Section 5: Collaboration, Handoff & Escalation Protocols
        reports_to = ", ".join(edges.get("REPORTS_TO", ["Executive Oversight"]))
        collaborates = ", ".join(edges.get("COLLABORATES_WITH", ["Peer Specialist Engineers"]))
        hands_off = ", ".join(edges.get("HANDS_OFF_TO", ["Downstream Verification Team"]))
        reviews = ", ".join(edges.get("REVIEWS_AND_GATES", ["Cross-functional Review Board"]))
        audits = ", ".join(edges.get("CHALLENGES_OR_AUDITS", ["Risk and Compliance Auditors"]))

        sec5 = (
            f"## 5. Collaboration, Handoff & Escalation Protocols\n"
            f"Your interactions within the organizational Knowledge Graph are governed by explicit protocol contracts:\n"
            f"- **Hierarchical Reporting (`REPORTS_TO`)**: Direct escalation to `{reports_to}` for unresolvable trade-offs, resource constraints, or boundary disputes.\n"
            f"- **Peer Synthesis (`COLLABORATES_WITH`)**: Active bidirectional working sessions with `{collaborates}` to align architectural interfaces and invariants.\n"
            f"- **Workflow Delivery (`HANDS_OFF_TO`)**: Strict sequential artifact delivery to `{hands_off}`. Handoffs require verified schema compliance and passing regression suites.\n"
            f"- **Quality Gating (`REVIEWS_AND_GATES`)**: Formal sign-off authority over `{reviews}` against explicit acceptance criteria.\n"
            f"- **Adversarial Audit (`CHALLENGES_OR_AUDITS`)**: Subject to independent scrutiny and red-team challenge by `{audits}`, with mandatory remediation cycles upon failure."
        )

        # Build Section 6: Concrete Output Artifact Schemas
        schema_dict = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": output_artifact,
            "type": "object",
            "required": ["metadata", "architecture_spec", "verification_evidence", "risk_mitigations"],
            "properties": {
                "metadata": {
                    "type": "object",
                    "properties": {
                        "author_role": {"type": "string", "const": title},
                        "exemplar_org": {"type": "string", "const": exemplar},
                        "version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"},
                    },
                },
                "architecture_spec": {
                    "type": "object",
                    "description": "Comprehensive engineering specifications, mathematical formulations, and system topologies.",
                },
                "verification_evidence": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Empirical benchmark metrics, test results, and formal proofs.",
                },
                "risk_mitigations": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Specific controls addressing identified failure modes and adversarial attacks.",
                },
            },
        }
        schema_json_str = json.dumps(schema_dict, indent=2)

        sec6 = (
            f"## 6. Concrete Output Artifact Schemas\n"
            f"### Primary Output Deliverable: `{output_artifact}`\n"
            f"Every engagement must culminate in the generation of structured, verifiable artifacts adhering to the schema:\n"
            f"```json\n"
            f"{schema_json_str}\n"
            f"```\n"
            f"- **Input Dependency**: Consumes `{input_artifact}` as prerequisite context before initiating stage execution.\n"
            f"- **Integrity Verification**: Must achieve 100% automated schema validation before downstream handoff."
        )

        prompt = f"# System Prompt: {title}\n\n{sec1}\n\n{sec2}\n\n{sec3}\n\n{sec4}\n\n{sec5}\n\n{sec6}\n"
        return prompt


def compile_system_prompt(role_data: Dict[str, Any]) -> str:
    """Convenience helper to compile a system prompt."""
    return PromptCompiler.compile(role_data)
