# Biostatistical Root-Cause Analysis, Subgroup Recalibration & FDA SaMD PCCP Governance Protocol

**Author Role**: Principal Clinical Biostatistician (`Genentech Signature Practice` — Zero-Defect High-Assurance Architecture)  
**Governance Chain**: Collaborates with & audited by `health_director_clinical_trials_office` | Gates `Cross-functional Review Board` | Regulatory handoff to `health_fda_ind_regulatory_lead`  
**Cohort & Telemetry Scope**: Multi-hospital acute-care ICU EHR deployment (`HOSP_A..HOSP_D`, `N = 2,400`, Oracle Cerner Millennium telemetry contract)

---

## 1. Executive Incident Synthesis: Rejecting Aggregate Facade Compliance

At the global decision threshold `0.50`, the deployed Sepsis Early-Warning SaMD exhibits **Facade Compliance**: an apparently strong aggregate **`AUROC = 0.9248`** (`95% bootstrap CI: [0.9136, 0.9368]`, accuracy `87.96%`, Brier `0.1109`, `ECE = 0.1229`) conceals three simultaneous, statistically decisive clinical failure modes driving immunocompromised mortality (`28.75%` overall; `46.91%` among septic neutropenic patients) and bedside alarm distrust:

1. **Physiological Subgroup Under-Prediction (`anc_cells_ul < 500`, `n = 327`)**: Neutropenic oncology/transplant sepsis (`n = 194`, `59.33%` subgroup prevalence) presents as **afebrile lactatemia** (mean temperature **`36.70 °C`** vs `38.83 °C` in immunocompetent sepsis; mean lactate **`3.81 mmol/L`**). Because model logits weight fever heavily, septic neutropenic scores compress to mean `0.4150` (vs `0.7429` in `anc >= 500`), producing a **`70.62%` False Negative rate (`137/194` missed)** at `0.50` and severe miscalibration (`ECE = 0.2880`). Untreated neutropenic sepsis carries **`57.69%` 30-day mortality** (`75/130`) vs **`25.00%`** (`16/64`) when early antibiotics are delivered.
2. **Operational Telemetry Throttling & Simpson's Paradox (`HOSP_C`, `icu_occupancy_pct > 85%`)**: `HOSP_C` operates at `>85%` ICU occupancy in `71.71%` (`502/700`) of admissions and enforces automated nursing-IT alert suppression during surge, throttling **`100.0%` (`163/163`)** of eligible (`ai_risk_score >= 0.50`) alerts (`0.0%` suppression at `<=85%` occupancy in `HOSP_C` [`0/69`] and `0.0%` [`0/421`] in `HOSP_A/B/D`). Throttling collapses early antibiotic administration among alert-eligible patients from **`86.33%` (`423/490`) to `18.40%` (`30/163`)**, inflating 30-day mortality from **`14.08%` to `26.38%`**.
3. **Clinical Chemistry Reagent Drift & OOD Saturation (`PCT_LOT_DRIFT_X9` / `procalcitonin_ng_ml > 12.0`, `n = 50`)**: Exactly `50` patients (`100%` concordance between `procalcitonin_ng_ml > 12.0 ng/mL` [range `13.98–64.35`] and lot `PCT_LOT_DRIFT_X9`, vs max `9.87 ng/mL` in `PCT_LOT_STD_04`) suffer assay-induced score saturation (mean score **`0.9156`**, range `0.8411–0.9786`). Although true sepsis prevalence is only `22.00%` (`11/50`), **`100.0%` (`39/39`)** of non-septic OOD cases trigger false positives—accounting for **`36.45%` (`39/107`) of all false positives across the 4-hospital network** and `33` unnecessary broad-spectrum antibiotic exposures.

---

## 2. First-Principles Biostatistical Root-Cause Analysis

### 2.1 Simpson's Paradox, Confounding by Indication & Non-Proportional Hazards
Naive observational audits of EHR outcomes without causal conditioning invert clinical reality across two coupled pathways:

| Causal / Analytical Contrast | Unadjusted Treated Mortality | Unadjusted Untreated Mortality | Unadjusted Risk Diff (RD) | Confounding-Adjusted Stratum | Adjusted Treated Mortality | Adjusted Untreated Mortality | Adjusted RD (`CHR_30`) |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: | :---: |
| **`alert_delivered` (`1` vs `0`)** | `14.08%` (`69/490`) | `8.80%` (`168/1910`) | **`+5.29%`** *(appears harmful)* | Alert-eligible (`score >= 0.50`, `n=653`) | **`14.08%`** (`69/490`) | **`26.38%`** (`43/163` throttled) | **`-12.30%`** (`0.4956`) |
| **`alert_delivered` (`HOSP_C` only)** | `21.74%` (`15/69`) | `13.00%` (`82/631`) | **`+8.74%`** *(appears harmful)* | `HOSP_C` `score >= 0.50` (`n=232`) | **`21.74%`** (`15/69`) | **`26.38%`** (`43/163` throttled) | **`-4.64%`** (`0.8005`) |
| **`early_antibiotics` (`1` vs `0`)** | `8.66%` (`62/716`) | `10.39%` (`175/1684`) | **`-1.73%`** *(attenuated; `+0.56%` at `<=85%` occ)* | Confirmed Sepsis (`sepsis = 1`, `n=728`) | **`13.47%`** (`54/401`) | **`40.98%`** (`134/327`) | **`-27.51%`** (`0.2743`) |
| **`early_antibiotics` (`anc < 500`)** | `23.46%` (`19/81`) | `30.49%` (`75/246`) | **`-7.03%`** *(diluted by non-sepsis)* | Neutropenic Sepsis (`n=194`) | **`25.00%`** (`16/64`) | **`57.69%`** (`75/130`) | **`-32.69%`** (`0.3346`) |

- **Causal Mechanism of Paradox**: `alert_delivered = 1` occurs exclusively when `ai_risk_score >= 0.50` (`81.84%` true sepsis), whereas `alert_delivered = 0` pools `1,747` low-risk patients (`10.42%` sepsis, `7.16%` mortality) with `163` throttled `HOSP_C` high-risk patients (`88.96%` sepsis, `26.38%` mortality). Across `(sepsis_ground_truth x immunocompromised)` strata, Mantel-Haenszel pooled `early_antibiotics` RD is **`-9.12%`** and direct-standardized population ATE is **`-7.08%`**.
- **Survival & Non-Proportional Hazards Axiom**: Delayed antimicrobial therapy in neutropenic bacteremia induces a steep early-phase hazard spike within hours `0–72` followed by late plateauing, violating constant Cox proportional-hazards assumptions over 30 days. Inference is therefore anchored on exact 30-day Kaplan-Meier landmark risk differences $\Delta \hat{S}(30) = -\text{RD}$ and complementary log-log cumulative hazard ratios $\text{CHR}_{30} = \ln \hat{S}_1(30) / \ln \hat{S}_0(30)$ (`0.4956` for alert delivery; `0.2743` for early antibiotics in sepsis), paired with Restricted Mean Survival Time ($\text{RMST}_{30}$) in prospective monitoring.

### 2.2 Multiplicity Error Control (Holm-Bonferroni Step-Down FWER Gate, $\alpha = 0.05$)
To eliminate family-wise Type I inflation across the 5 co-primary diagnostic hypotheses, exact two-sided Fisher tests were gated under Holm-Bonferroni FWER control:
- **$H_4$ (Neutropenic FN disparity: `70.62%` vs `8.43%` in `anc >= 500`)**: raw $p = 2.19 \times 10^{-61}$, **Holm-adjusted $p = 1.10 \times 10^{-60}$** (Reject $H_0$).
- **$H_1$ (`HOSP_C` `>85%` occupancy alert throttling: `100.0%` vs `0.0%`)**: raw $p = 8.25 \times 10^{-61}$, **Holm-adjusted $p = 3.30 \times 10^{-60}$** (Reject $H_0$).
- **$H_5$ (OOD `PCT > 12.0` / `PCT_LOT_DRIFT_X9` non-septic FP rate: `100.0%` vs `4.16%`)**: raw $p = 1.52 \times 10^{-50}$, **Holm-adjusted $p = 4.56 \times 10^{-50}$** (Reject $H_0$).
- **$H_3$ (Early antibiotics mortality reduction in sepsis: `-27.51%` RD)**: raw $p = 3.85 \times 10^{-17}$, **Holm-adjusted $p = 7.70 \times 10^{-17}$** (Reject $H_0$).
- **$H_2$ (Alert delivery mortality reduction in `score >= 0.50`: `-12.30%` RD)**: raw $p = 4.86 \times 10^{-4}$, **Holm-adjusted $p = 4.86 \times 10^{-4}$** (Reject $H_0$).

---

## 3. Immunocompromised Subgroup Recalibration & OOD Abstention Performance

### 3.1 Neutropenic (`anc_cells_ul < 500`, `n = 327`) Recalibration & Decision Curve Net Benefit
Because subgroup discrimination remains high (`AUROC = 0.9456`), failure at `0.50` is primarily a **calibration-in-the-large and slope defect** exacerbated by omitted afebrile-lactatemia interaction:
- **Phase-1 Locked-Feature Platt Recalibration** ($\hat{p}_{\text{cal}} = \text{logit}^{-1}(-4.7472 + 20.4421 \cdot s)$, 5-fold stratified CV):
  - Maps calibrated posterior threshold $p_t = 0.50$ to raw-score **`calibrated_subgroup_threshold = 0.2322`** (and high-sensitivity sepsis threshold $p_t = 0.30$ to raw score **`0.1908`**).
  - Reduces 5-fold out-of-fold **False Negative rate from `70.62%` (`137/194`) to `10.31%` (`20/194`)** (`85.4%` relative miss reduction) and **`ECE` from `0.2880` to `0.0295`** (`89.8%` reduction).
  - **Decision Curve Analysis (DCA) Net Benefit** ($\text{NB}(p_t) = \frac{TP}{N} - \frac{FP}{N}\frac{p_t}{1-p_t}$): At $p_t = 0.50$, uncalibrated AI (`NB = 0.1743`) is **inferior to blind Treat-All (`NB = 0.1865`)**, proving net clinical harm from uncalibrated deployment. Subgroup Platt recalibration lifts OOF Net Benefit to **`0.4832` (`+0.3089` uplift, or `+30.9` net true positives per 100 patients)**; at clinical sepsis threshold $p_t = 0.30$, Net Benefit rises from `0.1743` to **`0.5002` (`+0.3259` uplift)**.
- **Phase-2 PCCP Afebrile-Lactatemia Covariate Recalibration** ($\text{logit}(s) + \text{lactate} + \text{temperature}$, 5-fold CV): Explicitly resolves fever-lactate antagonism, achieving **`OOF AUROC = 0.9971`**, **`FN rate = 0.52%` (`1/194`)**, **`ECE = 0.0095`**, and **`NB uplift = +0.4098`** at $p_t = 0.50$.

### 3.2 OOD Assay Drift Abstention Gate & Cleaned Cohort Verification (`N = 2,350`)
- **Deterministic Abstention Invariant**: `IF (procalcitonin_ng_ml > 12.0) OR (analyzer_lot != 'PCT_LOT_STD_04') -> STATE = ABSTAIN_HITL_LAB_QC`.
- Quarantining the `50` OOD records improves raw in-distribution (`N = 2,350`) **`AUROC` from `0.9248` to `0.9428`**, **`Specificity` from `93.60%` to `95.84%`**, **`PPV` from `83.61%` to `88.72%`**, and Brier from `0.1109` to `0.0992`. Pairing OOD abstention with dual-stratum (`anc < 500` / `anc >= 500`) Platt recalibration yields **`AUROC = 0.9831`**, **`Accuracy = 93.79%`**, **`Sensitivity = 88.15%`**, **`Specificity = 96.26%`**, **`Brier = 0.0453`**, and **`ECE = 0.0080`**.

---

## 4. FDA SaMD Predetermined Change Control Plan (PCCP) & Clinician HITL Governance

Per FDA *Marketing Submission Recommendations for a PCCP for AI-Enabled Device Software Functions*, ISO 14971, and IEC 62304 Class C controls:

### 4.1 Authorized PCCP Modification Scope & Protocol
1. **Modification Boundary (3 Locked Change Types)**:
   - *Mod-1 (Immediate)*: Deploy deterministic OOD Procalcitonin/Lot-ID abstention gate (`PCT > 12.0 ng/mL` or unverified `analyzer_lot` / rolling lot median `> 2.0 ng/mL`) + hard removal of occupancy-dependent alert suppression in `HOSP_C` middleware.
   - *Mod-2 (Phase-1 Calibration)*: Stratum-specific monotone Platt recalibration for `anc_cells_ul < 500` (`s* = 0.2322` at $p_t = 0.50$; optional oncology-ICU high-sensitivity mode `s* = 0.1908` at $p_t = 0.30$).
   - *Mod-3 (Phase-2 Feature Interaction)*: Pre-specified GLM recalibration layer incorporating `(logit(score), lactate_mmol_l, temperature_c)` for `anc_cells_ul < 500` after prospective silent shadow validation (`N >= 500` immunocompromised admissions across all 4 hospitals).
2. **Deterministic Interface, Latency & State Machine Contracts (Oracle Cerner Millennium / FHIR R4)**:
   - End-to-end CDS Hook inference + gate verification latency bounds: **`p50 <= 120 ms`**, **`p99 <= 450 ms`**, **`p99.9 <= 900 ms`** at sustained throughput `>= 250 eval/s`; schema/missing-ANC/unregistered-lot faults deterministically transition `IDLE -> VALIDATE_SCHEMA -> {IN_DIST_CALIBRATED_EVAL | ABSTAIN_HITL_LAB_QC | FAILSAFE_CLINICAL_PATHWAY}` (zero silent suppression permitted).
3. **Statistical Acceptance & Multiplicity Guardrails**:
   - Every candidate PCCP update must pass 5-fold hospital-stratified validation under **Lan-DeMets O'Brien-Fleming alpha-spending** ($\alpha_{\text{total}} = 0.025$ one-sided): (i) `anc < 500` FN rate `<= 12.0%` and `ECE <= 0.050`; (ii) non-inferiority on `anc >= 500` (`AUROC >= 0.975`, `Specificity >= 94.0%`, `Delta PPV >= -1.5%`); (iii) positive DCA Net Benefit uplift across $p_t \in [0.20, 0.50]$ at every individual hospital (`HOSP_A..HOSP_D`).

### 4.2 Clinician HITL Safety Workflow, Sign-Off Matrix & Rollback Triggers
- **Mandatory Clinician HITL Routing**:
  - *OOD Abstention Banner*: Suppresses numeric AI score; displays yellow **Lab Assay Drift / OOD Abstention** card instructing bedside MD/RN to order stat repeat PCT on verified lot + venous lactate + blood cultures before empiric escalation unless hemodynamic shock is present.
  - *Surge Routing (`icu_occupancy_pct > 85%`)*: Prohibits alert deletion; routes `p_cal >= 0.50` alerts directly to ICU Rapid-Response Charge Nurse + Covering Intensivist with a 15-minute acknowledgment SLA.
- **Affirmative Sign-Off & Audit Governance**: Requires cryptographic sign-off by Principal Clinical Biostatistician, red-team audit clearance by `health_director_clinical_trials_office`, `Cross-functional Review Board` + multi-site IRB risk determination (waiver/amendment for prospective shadow registry), and formal regulatory filing handoff to `health_fda_ind_regulatory_lead` with immutable audit-ledger provenance.
- **Automated Deterministic Rollback Triggers**: Instantaneous (<60 s) automated fallback to previous locked baseline + clinical sepsis bundle pathway if any rolling 14-day window breaches:
  1. Subgroup `ECE > 0.070` or Bayesian Beta-Binomial posterior $\Pr(\text{FNR}_{\text{anc}<500} > 0.15 \mid \mathcal{D}) > 0.90$;
  2. Lot-level PCT Page's CUSUM shift `> 3 sigma` or abstention rate `> 5.0%` over 24 hours;
  3. Alert-delivery integrity `< 99.5%` among eligible in-distribution patients at any hospital (`HOSP_A..HOSP_D`) regardless of ICU occupancy.

### 4.3 Validated SAP & PCCP Artifact Attestation (`1.0.0`)
```json
{
  "metadata": {"author_role": "Principal Clinical Biostatistician", "exemplar_org": "Genentech", "version": "1.0.0"},
  "architecture_spec": {"ehr_platform": "Oracle Cerner Millennium", "latency_ms": {"p50": 120, "p99": 450, "p99.9": 900}, "fwer_alpha": 0.05},
  "verification_evidence": ["N=2400 cohort audited; H1-H5 Holm-Bonferroni p<=4.86e-4", "ANC<500 FNR 70.62%->10.31%, ECE 0.2880->0.0295, DCA NB +0.3089", "OOD n=50 quarantined; dual-recal clean AUROC=0.9831, ECE=0.0080"],
  "risk_mitigations": ["Hard ban on occupancy alert throttling", "Deterministic PCT>12/lot-drift HITL abstention", "Bayesian + CUSUM auto-rollback"]
}
```
