"""Capability and Constraint Extractor for Dynamic Team Synthesis.

Parses unstructured customer problem statements into formal capability requirements:
- Macro-industry domains
- Specialized technical disciplines
- Multi-dimensional performance and governance constraints (latency, capital, regulatory, adversarial)
- Required functional archetype distributions
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CapabilityProfile(BaseModel):
    """Structured capability requirement extracted from a problem statement."""

    raw_query: str = Field(..., description="Original customer problem statement")
    domains: List[str] = Field(default_factory=list, description="Target macro industry domains")
    technical_disciplines: List[str] = Field(
        default_factory=list, description="Specific scientific/engineering disciplines"
    )
    constraints: Dict[str, Any] = Field(
        default_factory=dict, description="Parsed operational, latency, capital, and regulatory constraints"
    )
    required_archetypes: List[str] = Field(
        default_factory=list, description="Mandatory functional archetype categories"
    )

    def to_dict(self) -> Dict[str, Any]:
        """Returns standard dictionary representation."""
        return {
            "domains": self.domains,
            "technical_disciplines": self.technical_disciplines,
            "constraints": self.constraints,
            "required_archetypes": self.required_archetypes,
            "raw_query": self.raw_query,
        }

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)

    def get(self, item: str, default: Any = None) -> Any:
        return getattr(self, item, default)


class CapabilityExtractor:
    """Decomposes unstructured customer problem statements into formal capability requirements."""

    DOMAIN_ONTOLOGY: Dict[str, List[str]] = {
        "Telecommunications & Digital Networks": [
            "telecom", "telecommunications", "6g", "5g", "radio", "rf", "o-ran", "oran",
            "sub-thz", "sub-terahertz", "urllc", "fronthaul", "front-haul", "mac scheduler",
            "antenna", "mimo", "spectrum", "carrier", "packet core", "link budget"
        ],
        "Finance & Quantitative Trading": [
            "finance", "trading", "settlement", "rtgs", "clearing", "liquidity", "dvp", "pvp",
            "payment", "payments", "capital", "basel", "collateral", "credit line", "repo",
            "amm", "market microstructure", "stablecoin", "cbdc", "high-frequency", "derivatives"
        ],
        "Technology & AI": [
            "ai", "sovereign ai", "llm", "large language model", "inference", "speculative decoding",
            "kv-cache", "kv cache", "tensor core", "foundational model", "gpu", "machine learning",
            "neural", "deep learning", "edge ai"
        ],
        "Cybersecurity & Defense": [
            "security", "cybersecurity", "adversarial", "red-team", "red team", "cryptography",
            "cryptographic", "post-quantum", "pqc", "lattice", "ml-kem", "ml-dsa", "kyber",
            "dilithium", "side-channel", "exploit", "penetration", "zero-day", "fips 203", "fips 204",
            "tamper", "vulnerability"
        ],
        "Public Sector & Regulation": [
            "regulation", "regulatory", "compliance", "governance", "sovereign", "audit",
            "cpmi-iosco", "iosco", "gdpr", "eu ai act", "central bank", "bis", "fiduciary",
            "jurisdiction", "statute", "legal", "oversight"
        ],
        "Semiconductors & Advanced Manufacturing": [
            "semiconductor", "semiconductors", "hardware", "chip", "asic", "fpga", "hsm",
            "hardware security module", "silicon", "enclave", "sev-snp", "tdx", "root of trust",
            "tsmc", "arm", "bft", "byzantine consensus"
        ],
        "Professional Services & Strategy": [
            "strategy", "consulting", "executive", "charter", "roadmap", "program director",
            "mckinsey", "operating model", "governance charter"
        ],
    }

    DISCIPLINE_ONTOLOGY: Dict[str, List[str]] = {
        "sub_thz_rf": [
            "sub-thz", "sub-terahertz", "140 ghz", "d-band", "rf", "antenna array",
            "beamforming", "massive mimo", "friis", "shannon", "molecular absorption"
        ],
        "oran_urllc": [
            "o-ran", "oran", "urllc", "split-7.2x", "ecpri", "mac scheduler",
            "subcarrier spacing", "numerology", "radio resource"
        ],
        "atomic_settlement": [
            "settlement", "rtgs", "dvp", "pvp", "clearing", "atomic commit",
            "double-spend", "gross settlement", "delivery-versus-payment"
        ],
        "intraday_liquidity": [
            "liquidity", "collateral", "basel iii", "basel iv", "overdraft",
            "repo facility", "amm vault", "multilateral netting", "gridlock"
        ],
        "pqc_lattice": [
            "post-quantum", "pqc", "lattice", "ml-kem", "ml-dsa", "fips 203",
            "fips 204", "crystals", "kyber", "dilithium", "quantum"
        ],
        "sovereign_ai": [
            "sovereign ai", "edge ai", "pagedattention", "kv-cache",
            "speculative decoding", "fraud scoring", "sanction screening"
        ],
        "hardware_enclave_consensus": [
            "hsm", "byzantine", "bft", "consensus", "root of trust", "sev-snp",
            "confidential computing", "ntt accelerator", "zk-snark", "snark"
        ],
    }

    def extract(self, problem_statement: str) -> CapabilityProfile:
        """Extracts domains, disciplines, constraints, and archetypes from a problem statement."""
        text_lower = problem_statement.lower()

        # 1. Macro-Domain Identification
        matched_domains: List[str] = []
        for domain, keywords in self.DOMAIN_ONTOLOGY.items():
            if any(re.search(r"\b" + re.escape(kw) + r"\b", text_lower) for kw in keywords):
                matched_domains.append(domain)

        # Fallback guarantee: ensure at least 3 relevant domains if sparse
        if len(matched_domains) < 3:
            for fallback in [
                "Telecommunications & Digital Networks",
                "Finance & Quantitative Trading",
                "Cybersecurity & Defense",
            ]:
                if fallback not in matched_domains:
                    matched_domains.append(fallback)

        # 2. Specialized Technical Disciplines
        matched_disciplines: List[str] = []
        for discipline, keywords in self.DISCIPLINE_ONTOLOGY.items():
            if any(kw in text_lower for kw in keywords):
                matched_disciplines.append(discipline)

        # 3. Performance & Governance Constraint Parsing
        constraints: Dict[str, Any] = {}

        # Latency constraints
        if any(w in text_lower for w in ["latency", "sub-millisecond", "urllc", "sub-thz", "real-time"]):
            constraints["latency"] = {
                "target_phy_latency": "< 100us",
                "target_end_to_end": "< 5.0ms",
                "tier": "deterministic_urllc",
            }

        # Capital & Liquidity constraints
        if any(w in text_lower for w in ["capital", "liquidity", "collateral", "basel", "settlement"]):
            constraints["capital"] = {
                "frameworks": ["Basel III/IV Intraday Monitoring", "CPMI-IOSCO PFMI"],
                "credit_risk": "zero_uncollateralized_exposure",
                "netting_target": "< 200ms",
            }

        # Regulatory statutes
        reg_statutes: List[str] = []
        if "cpmi" in text_lower or "iosco" in text_lower or "settlement" in text_lower:
            reg_statutes.append("CPMI-IOSCO PFMI")
        if "eu ai act" in text_lower or "ai" in text_lower:
            reg_statutes.append("EU AI Act High-Risk Oversight")
        if "gdpr" in text_lower or "privacy" in text_lower or "sovereign" in text_lower:
            reg_statutes.append("GDPR Article 22 / Sovereign Data Isolation")
        if "basel" in text_lower or "capital" in text_lower or "finance" in text_lower:
            reg_statutes.append("Basel III/IV BCBS 248")
        constraints["regulatory"] = reg_statutes or ["CPMI-IOSCO", "Sovereign Regulatory Oversight"]

        # Adversarial security posture
        if any(w in text_lower for w in ["adversarial", "security", "post-quantum", "pqc", "red-team", "byzantine"]):
            constraints["adversarial"] = {
                "threat_model": "state_sponsored_byzantine_fault",
                "cryptography": "NIST FIPS 203 (ML-KEM) / FIPS 204 (ML-DSA)",
                "audit_gate": "mandatory_red_team_veto",
            }

        # 4. Required Archetypes
        required_archetypes = [
            "executive_strategy",
            "engineering_staff",
            "domain_specialist",
            "operations",
            "risk_compliance",
        ]

        return CapabilityProfile(
            raw_query=problem_statement,
            domains=matched_domains,
            technical_disciplines=matched_disciplines,
            constraints=constraints,
            required_archetypes=required_archetypes,
        )

    def extract_capabilities(self, problem_statement: str) -> Dict[str, Any]:
        """Compatibility method matching blueprint.md API contract."""
        profile = self.extract(problem_statement)
        return profile.to_dict()
