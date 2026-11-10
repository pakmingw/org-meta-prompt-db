"""Retrieval Evaluation Benchmark Suite for Hybrid Search Engine.

Evaluates 25 diverse single-domain and cross-industry benchmark queries spanning
all 16 macro industries. Programmatically measures Recall@10 and Mean Reciprocal Rank (MRR),
and verifies dual score contribution from both the sparse BM25 and dense vector indexes.
Acceptance targets:
    - Recall@10 >= 0.85
    - MRR >= 0.70
    - DualContribution = True
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from orgprompt.search.hybrid import HybridSearchEngine


# Authoritative 25 Benchmark Queries defined in SPEC-MINER-SURVEY2 § 7.2 & tests/conftest.py
DEFAULT_BENCHMARK_QUERIES: List[Dict[str, Any]] = [
    {
        "id": "Q01_OPTICAL_ORAN",
        "query": "Shannon capacity optical link budget O-RAN beamforming",
        "ground_truth": ["telecom_chief_network_architect", "telecom_principal_ran_systems_engineer"],
        "industry": "Telecommunications",
    },
    {
        "id": "Q02_HFT_FPGA",
        "query": "Sub-millisecond low-latency FPGA high-frequency market making",
        "ground_truth": ["fin_principal_fpga_trading_architect", "fin_chief_investment_officer"],
        "industry": "Finance",
    },
    {
        "id": "Q03_GPU_DISTRIB_TRAIN",
        "query": "Distributed foundation model pretraining NCCL GPU cluster orchestration",
        "ground_truth": ["tech_chief_cloud_infrastructure_architect", "tech_principal_distributed_training_engineer"],
        "industry": "Technology & AI",
    },
    {
        "id": "Q04_PIXAR_BRAINTRUST",
        "query": "Pixar Braintrust story development CGI animation pipeline",
        "ground_truth": ["media_head_of_story_editorial", "media_lead_character_animator"],
        "industry": "Creative Arts & Media",
    },
    {
        "id": "Q05_CLINICAL_ONCOLOGY",
        "query": "Translational clinical oncology genomic sequencing pathology",
        "ground_truth": ["health_chief_medical_officer", "health_director_precision_medicine"],
        "industry": "Healthcare & Biotech",
    },
    {
        "id": "Q06_EUV_LITHOGRAPHY",
        "query": "EUV photolithography wafer fabrication pellicle alignment 2nm",
        "ground_truth": ["semi_vp_euv_systems_engineering", "semi_optical_mirror_interferometry_specialist"],
        "industry": "Semiconductors",
    },
    {
        "id": "Q07_METHALOX_ROCKET",
        "query": "Starship methalox full-flow staged combustion Raptor engine trajectory",
        "ground_truth": ["aero_lead_propulsion_systems_director", "aero_chief_engineer_starship"],
        "industry": "Aerospace & Defense",
    },
    {
        "id": "Q08_HVDC_BESS",
        "query": "High-voltage direct current HVDC battery storage BESS dispatch Autobidder",
        "ground_truth": ["energy_chief_transmission_officer", "energy_principal_battery_storage_algorithm_engineer"],
        "industry": "Energy & Grids",
    },
    {
        "id": "Q09_AMAZON_ROBOTICS",
        "query": "Working backwards PR/FAQ robotic fulfillment warehouse sortation",
        "ground_truth": ["retail_vp_global_fulfillment_technology", "retail_principal_kiva_robotics_controls_engineer"],
        "industry": "Retail & Logistics",
    },
    {
        "id": "Q10_CONTAINER_VESSEL",
        "query": "Chief marine operations officer container vessel stowage marine safety demurrage",
        "ground_truth": ["logistics_chief_marine_operations_officer", "logistics_master_vessel_stowage_planner"],
        "industry": "Global Logistics",
    },
    {
        "id": "Q11_DIGITAL_GOV_AV",
        "query": "National digital identity citizen authentication civil aviation safety Part 25",
        "ground_truth": ["gov_chief_digital_technology_officer", "gov_faa_associate_administrator_safety"],
        "industry": "Public Sector & Regulation",
    },
    {
        "id": "Q12_MCKINSEY_STRAT",
        "query": "Pyramid Principle MECE executive strategy believability-weighted decision",
        "ground_truth": ["consult_senior_partner_managing_director", "consult_chief_systematic_macro_strategist"],
        "industry": "Professional Services",
    },
    {
        "id": "Q13_CERN_DARPA",
        "query": "Large Hadron Collider ATLAS detector double-blind discovery Heilmeier catechism",
        "ground_truth": ["research_director_general_cern", "research_darpa_director"],
        "industry": "Frontier Research",
    },
    {
        "id": "Q14_MRNA_VACCINE",
        "query": "mRNA lipid nanoparticle formulation cGMP sterile fill finish vaccine",
        "ground_truth": ["pharma_chief_scientific_officer", "pharma_principal_lipid_nanoparticle_formulator"],
        "industry": "Pharmaceuticals",
    },
    {
        "id": "Q15_ZERO_TRUST_CROWD",
        "query": "Zero Trust Architecture Falcon threat hunting 1-10-60 adversarial red team",
        "ground_truth": ["cyber_nsa_director_cybersecurity", "cyber_vp_overwatch_threat_hunting"],
        "industry": "Cybersecurity",
    },
    {
        "id": "Q16_AV_SIM_WAYMO",
        "query": "Level-4 autonomous driving simulation corner cases model predictive control",
        "ground_truth": ["robotics_chief_safety_officer_waymo", "robotics_principal_simulation_fuzzing_engineer"],
        "industry": "Autonomous Robotics",
    },
    {
        "id": "Q17_BASEL_FRTB",
        "query": "Basel III IV fundamental review trading book expected shortfall capital",
        "ground_truth": ["fin_frtb_capital_adequacy_lead", "fin_chief_investment_officer"],
        "industry": "Finance & Banking",
    },
    {
        "id": "Q18_SUBSEA_OPTICAL",
        "query": "Subsea transoceanic fiber landing station optical attenuation",
        "ground_truth": ["telecom_vp_global_infrastructure", "telecom_subsea_optical_director"],
        "industry": "Telecommunications",
    },
    {
        "id": "Q19_ZEISS_OPTICS",
        "query": "Extreme ultraviolet EUV systems engineering Zeiss mirror metrology VP",
        "ground_truth": ["semi_vp_euv_systems_engineering"],
        "industry": "Semiconductors",
    },
    {
        "id": "Q20_NERC_CIP",
        "query": "NERC CIP high impact bulk electric system cyber perimeter defense",
        "ground_truth": ["energy_nerc_cip_grid_cybersecurity_auditor"],
        "industry": "Energy Cybersecurity",
    },
    {
        "id": "Q21_DO178C_AVIONICS",
        "query": "RTCA DO-178C DAL A avionics flight control certification",
        "ground_truth": ["aero_do178c_do254_avionics_auditor", "gov_faa_associate_administrator_safety"],
        "industry": "Aerospace Certification",
    },
    {
        "id": "Q22_TOYOTA_ANDON",
        "query": "Toyota Production System Andon cord Kaizen continuous improvement",
        "ground_truth": ["semi_andon_cord_quality_assurance_lead"],
        "industry": "Advanced Manufacturing",
    },
    {
        "id": "Q23_FDA_21CFR11",
        "query": "FDA 21 CFR Part 11 electronic records clinical trial protocol",
        "ground_truth": ["pharma_fda_21cfr_part11_data_integrity_auditor"],
        "industry": "Pharmaceutical Compliance",
    },
    {
        "id": "Q24_K8S_BORG",
        "query": "Kubernetes Borg cluster scheduler fault tolerance eBPF networking",
        "ground_truth": ["tech_chief_cloud_infrastructure_architect"],
        "industry": "Cloud Infrastructure",
    },
    {
        "id": "Q25_BOSTON_DYNAMICS",
        "query": "Autonomous humanoid dynamic locomotion torque control Boston Dynamics",
        "ground_truth": ["robotics_principal_mpc_locomotion_architect"],
        "industry": "Robotics & Locomotion",
    },
    {
        "id": "Q26_EUV_INTERFEROMETRY",
        "query": "EUV optical mirror interferometry sub-nanometer wavefront measurement",
        "ground_truth": ["semi_optical_mirror_interferometry_specialist"],
        "industry": "Semiconductors Metrology",
    },
    {
        "id": "Q27_KANBAN_JIT_SCM",
        "query": "Just-in-time Kanban supply chain inventory replenishment safety stock quant",
        "ground_truth": ["retail_principal_inventory_replenishment_quant", "semi_kanban_jit_supply_chain_manager"],
        "industry": "Supply Chain Operations",
    },
    {
        "id": "Q28_PRIVACY_GDPR",
        "query": "GDPR privacy anonymization cross-border data transfer data protection officer",
        "ground_truth": ["cyber_privacy_gdpr_anonymization_officer"],
        "industry": "Corporate Governance & Privacy",
    },
    {
        "id": "Q29_FINOPS_CLOUD",
        "query": "Chief cloud infrastructure architect Kubernetes Borg cluster scheduler FinOps",
        "ground_truth": ["tech_chief_cloud_infrastructure_architect"],
        "industry": "Cloud Infrastructure & FinOps",
    },
    {
        "id": "Q30_CISO_GOVERNANCE",
        "query": "Chief Information Security Officer enterprise zero-trust cybersecurity risk governance CISO",
        "ground_truth": ["cyber_chief_information_security_officer"],
        "industry": "Enterprise Cybersecurity",
    },
    {
        "id": "Q31_IP_PATENTS",
        "query": "Intellectual property copyright chain of title counsel media entertainment trade secrets",
        "ground_truth": ["media_ip_copyright_chain_of_title_counsel"],
        "industry": "Intellectual Property Law",
    },
    {
        "id": "Q32_ENERGY_TRADING_VPP",
        "query": "VP distributed energy trading wholesale power trader virtual power plant electricity",
        "ground_truth": ["energy_vp_distributed_energy_trading", "energy_lead_wholesale_power_trader"],
        "industry": "Energy Markets",
    },
    {
        "id": "Q33_MODEL_RISK_SR11_7",
        "query": "Enterprise model risk management SR 11-7 backtesting credit valuation adjustment",
        "ground_truth": ["fin_chief_risk_officer", "fin_model_risk_governance_director"],
        "industry": "Risk Management",
    },
    {
        "id": "Q34_BIOPROCESS_TITERS",
        "query": "Bioprocess cell line development Chinese hamster ovary perfusion bioreactor titer",
        "ground_truth": ["health_bioprocess_cell_line_engineer"],
        "industry": "Biotechnology",
    },
    {
        "id": "Q35_SOVEREIGN_CLOUD",
        "query": "Sovereign cloud compliance FedRAMP High air-gapped cryptographic enclave",
        "ground_truth": ["gov_principal_sovereign_cloud_security_architect"],
        "industry": "Public Sector & Sovereign AI",
    },
    {
        "id": "Q36_IRB_CLINICAL_TRIALS",
        "query": "Institutional review board IRB clinical trials bioethics FDA investigational new drug IND",
        "ground_truth": ["health_irb_bioethics_committee_chair", "health_director_clinical_trials_office"],
        "industry": "Clinical Compliance",
    },
]

# Canonical 25 benchmark queries matching the 336 canonical seed roles in in-memory test databases
CANONICAL_25_BENCHMARK_QUERIES: List[Dict[str, Any]] = DEFAULT_BENCHMARK_QUERIES[:25]

# Expanded 36 benchmark queries covering expanded Fortune 500 taxonomy roles in full persistent database
EXPANDED_36_BENCHMARK_QUERIES: List[Dict[str, Any]] = DEFAULT_BENCHMARK_QUERIES


@dataclass
class BenchmarkReport:
    """Detailed retrieval evaluation performance report."""

    recall_at_10: float
    mrr: float
    queries_evaluated: int
    sparse_contributions: int
    dense_contributions: int
    dual_contribution_verified: bool
    passes: bool
    query_details: List[Dict[str, Any]] = field(default_factory=list)

    # Convenience aliases for multiple interface standards
    @property
    def recall_at_k(self) -> float:
        return self.recall_at_10

    @property
    def mean_reciprocal_rank(self) -> float:
        return self.mrr

    def summary(self) -> str:
        status = "PASSED" if self.passes else "FAILED"
        return (
            f"Retrieval Benchmark [{status}]:\n"
            f"  - Queries Evaluated: {self.queries_evaluated}\n"
            f"  - Recall@10:         {self.recall_at_10:.4f} (target >= 0.85)\n"
            f"  - MRR:               {self.mrr:.4f} (target >= 0.70)\n"
            f"  - Dual Contribution: {self.dual_contribution_verified} "
            f"(Sparse hits: {self.sparse_contributions}, Dense hits: {self.dense_contributions})\n"
        )


class RetrievalBenchmark:
    """Benchmark runner for automated hybrid search evaluation."""

    @staticmethod
    def run_benchmark(
        engine: HybridSearchEngine,
        queries: Optional[List[Dict[str, Any]]] = None,
        k: int = 10,
    ) -> BenchmarkReport:
        """Executes the benchmark query suite and measures Recall@K and MRR.

        Args:
            engine: Instantiated HybridSearchEngine to evaluate.
            queries: Optional list of query dicts; defaults to 25 canonical queries.
            k: Retrieval truncation depth for Recall@K (default k=10).

        Returns:
            BenchmarkReport with metrics and pass/fail status.
        """
        benchmark_set = queries or DEFAULT_BENCHMARK_QUERIES
        total_recall = 0.0
        total_reciprocal_rank = 0.0
        sparse_contributions = 0
        dense_contributions = 0
        query_details: List[Dict[str, Any]] = []

        for item in benchmark_set:
            q_text = item["query"]
            ground_truth: Set[str] = set(item["ground_truth"])

            # Search hybrid engine
            search_result = engine.search(q_text, top_k=k)
            retrieved_slugs = [
                r.slug if hasattr(r, "slug") else r["slug"] for r in search_result.results
            ]

            # 1. Recall@K
            hits = len(set(retrieved_slugs) & ground_truth)
            recall = hits / len(ground_truth) if ground_truth else 0.0
            total_recall += recall

            # 2. Reciprocal Rank (MRR)
            reciprocal_rank = 0.0
            for rank, s in enumerate(retrieved_slugs, start=1):
                if s in ground_truth:
                    reciprocal_rank = 1.0 / rank
                    break
            total_reciprocal_rank += reciprocal_rank

            # 3. Dual Score Attribution Verification
            for res in search_result.results:
                has_sparse = (
                    getattr(res, "has_sparse_contribution", False)
                    or (isinstance(res, dict) and res.get("has_sparse_contribution"))
                )
                has_dense = (
                    getattr(res, "has_dense_contribution", False)
                    or (isinstance(res, dict) and res.get("has_dense_contribution"))
                )
                if has_sparse:
                    sparse_contributions += 1
                if has_dense:
                    dense_contributions += 1

            query_details.append({
                "id": item.get("id", ""),
                "query": q_text,
                "ground_truth": list(ground_truth),
                "retrieved": retrieved_slugs,
                "recall_at_k": recall,
                "reciprocal_rank": reciprocal_rank,
                "hits": hits,
            })

        num_queries = len(benchmark_set)
        mean_recall = total_recall / num_queries if num_queries else 0.0
        mean_mrr = total_reciprocal_rank / num_queries if num_queries else 0.0

        dual_verified = (sparse_contributions > 0) and (dense_contributions > 0)
        passes = (mean_recall >= 0.85) and (mean_mrr >= 0.70) and dual_verified

        return BenchmarkReport(
            recall_at_10=mean_recall,
            mrr=mean_mrr,
            queries_evaluated=num_queries,
            sparse_contributions=sparse_contributions,
            dense_contributions=dense_contributions,
            dual_contribution_verified=dual_verified,
            passes=passes,
            query_details=query_details,
        )
