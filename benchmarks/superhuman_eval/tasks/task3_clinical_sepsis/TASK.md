# Task 3: Multi-Hospital Sepsis AI Failure Diagnosis, Subgroup Recalibration & FDA SaMD PCCP Protocol

## Clinical Deployment & Safety Incident Statement
A 4-hospital ICU Sepsis Early-Warning AI (`HOSP_A..HOSP_D`, `N = 2,400` in `sepsis_cohort.csv`) reports a strong aggregate **`AUROC ~ 0.91`** at threshold `0.50`, yet **immunocompromised oncology/transplant ICU mortality is rising** and site clinicians report erratic false alarms and missed deteriorations.

### Clinical & Operational Context (`sepsis_cohort.csv`)
- **Subgroup Physiology**: Neutropenic immunocompromised patients (`anc_cells_ul < 500`) frequently present with **atypical afebrile lactatemia** (normal/low temperature despite rising lactate).
- **Workflow & Telemetry Confounding**: Hospital nursing IT configured occupancy-dependent alert routing (`icu_occupancy_pct`, `alert_delivered`, `early_antibiotics`). Specifically, inspect whether automated nurse-alert throttling during high occupancy (`> 85%` in `HOSP_C`) suppresses alerts and confounds naive treated-outcome / Simpson's Paradox evaluations.
- **Lab Assay Drift**: Clinical chemistry flagged potential reagent/analyzer drift (`analyzer_lot`, `procalcitonin_ng_ml > 12.0 ng/mL`) causing out-of-distribution (OOD) score saturation requiring mandatory clinician HITL abstention rather than autonomous alerting/suppression.

## Required Deliverables (Write into Your Assigned Output Directory)
1. **`solution.py`**: Self-contained Python 3 script (stdlib / `numpy` / `scipy` / `pandas` / `sklearn` if installed) analyzing `sepsis_cohort.csv` and writing **`metrics.json`** with:
   - `total_patients`, `aggregate_auroc`
   - `simpsons_paradox_and_hosp_c_throttling`: quantified alert suppression rate in `HOSP_C` high occupancy (`>85%`) and unadjusted vs. stratified/confounding-adjusted mortality & treatment effect
   - `immunocompromised_anc_lt_500`: `n`, `pre_recalibration_fn_rate` (at `0.50`), `pre_recalibration_ece`, `post_recalibration_fn_rate`, `post_recalibration_ece`, `calibrated_subgroup_threshold`, and Decision Curve **Net Benefit** uplift
   - `ood_procalcitonin_abstention`: count of detected OOD rows (`procalcitonin_ng_ml > 12.0` / `analyzer_lot` drift), abstention gate rule, and cleaned cohort calibration/accuracy metrics
2. **`deliverable.md`** (`<= 240` lines): Biostatistical Root-Cause Analysis & **FDA SaMD Predetermined Change Control Plan (PCCP)** + **Clinician HITL Safety Governance Protocol** (modification protocol, impact assessment, subgroup guardrails, IRB/clinical risk sign-off, and rollback triggers).

Execute `solution.py` before finishing so `metrics.json` is verified on disk.
