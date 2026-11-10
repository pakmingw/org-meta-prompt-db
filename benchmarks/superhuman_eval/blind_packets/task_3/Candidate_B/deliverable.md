# Multi-Hospital ICU Sepsis AI Failure Diagnosis, Subgroup Recalibration & FDA SaMD PCCP Protocol

## 1. Executive Clinical Safety Incident Summary: The Aggregate AUROC Illusion
Across 4 ICU hospitals (`HOSP_A..HOSP_D`, $N = 2,400$; [sepsis_cohort.csv](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/benchmarks/superhuman_eval/tasks/task3_clinical_sepsis/sepsis_cohort.csv)), the deployed Sepsis Early-Warning SaMD exhibits strong aggregate discrimination (**`AUROC = 0.9248`**, accuracy `87.96%`, Brier `0.1109`, 10-bin `ECE = 0.1229` at global threshold `0.50`; reproduced via [solution.py](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/benchmarks/superhuman_eval/runs/candidate_workspace/solution.py) and [metrics.json](file:///home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/benchmarks/superhuman_eval/runs/candidate_workspace/metrics.json)). Yet aggregate `AUROC` is rank-based, threshold-agnostic, and dominated by immunocompetent standard-assay encounters ($84.3\%$ of patients), concealing **three simultaneous, life-threatening acute-care failures**:
1. **Operational Alert Throttling & Simpson's Paradox (`HOSP_C`)**: Nursing IT middleware silently suppressed **`100.0%` (`163/163`)** of positive AI alerts (`ai_risk_score >= 0.50`) whenever `HOSP_C` ICU occupancy exceeded `85%`, collapsing early antibiotic delivery by `-65.65` percentage points (`84.06% -> 18.40%`) and driving 30-day AI-positive mortality to `26.38%` while confounding naive observational safety audits.
2. **Subgroup Physiological Miscalibration (`anc_cells_ul < 500`, $n = 327$)**: Neutropenic oncology/transplant patients present with **atypical afebrile lactatemia** (`mean temp = 36.70°C` despite `mean lactate = 3.81 mmol/L`), compressing raw AI scores (`mean = 0.4150` in septic cases) below `0.50`, missing **`70.62%` (`137/194`)** of true sepsis cases (`ECE = 0.2880`), and delivering **lower Decision Curve Net Benefit than treating all patients blindly** (`0.1743 < 0.1865` at $p_t = 0.50$).
3. **Out-of-Distribution (OOD) Reagent Assay Drift (`PCT_LOT_DRIFT_X9`, $n = 50$)**: Uncalibrated procalcitonin lot drift (`> 12.0 ng/mL`, range `13.98–63.84 ng/mL`) saturated `100%` of affected encounters above `0.84` (`mean score = 0.9156`) despite a `22.0%` true sepsis rate, generating **`39` false-positive alarms (`36.45%` of all false positives across the 4-hospital network)** and eroding clinician trust.

---

## 2. Biostatistical Root-Cause Analysis & Recalibration Proof

### 2.1 Workflow & Telemetry Confounding: `HOSP_C` Occupancy Throttling & Dual Simpson's Paradox
Stratified telemetry audit across `(hospital_id, icu_occupancy_pct > 85%, ai_risk_score >= 0.50)` isolates a deterministic suppression defect exclusively in `HOSP_C` during surge occupancy:

| Stratum (`ai_risk_score >= 0.50`) | High-Risk $n$ | Alerts Delivered | Alert Suppression Rate (95% Wilson CI) | Early Antibiotics | True Sepsis | 30d Mortality |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`HOSP_C` Occupancy `> 85%`** ($N=502$) | **163** | **0** | **`100.0%` (`[97.70%, 100.0%]`)** | **`18.40%`** (`30/163`) | `88.96%` | **`26.38%`** (`43/163`) |
| **`HOSP_C` Occupancy `<= 85%`** ($N=198$) | 69 | 69 | `0.0%` (`[0.00%, 5.28%]`) | `84.06%` (`58/69`) | `86.96%` | `21.74%` (`15/69`) |
| **`HOSP_A, B, D` Occupancy `> 85%`** ($N=233$) | 61 | 61 | `0.0%` (`[0.00%, 5.92%]`) | `88.52%` (`54/61`) | `73.77%` | `11.48%` (`7/61`) |
| **`HOSP_A, B, D` Occupancy `<= 85%`** ($N=1,467$) | 360 | 360 | `0.0%` (`[0.00%, 1.05%]`) | `86.39%` (`311/360`) | `82.22%` | `13.06%` (`47/360`) |

**Resolution of Dual Simpson's Paradox**:
- **Paradox 1 — Alert Delivery vs. Mortality**: In unadjusted cohort analysis ($N = 2,400$), `alert_delivered = 1` exhibits **higher** 30-day mortality (`14.08%` [`69/490`]) than `alert_delivered = 0` (`8.80%` [`168/1,910`]; unadjusted RD = **`+5.29%`**), creating the false impression that AI alerts harm patients. This is pure confounding by baseline sepsis acuity (`81.84%` true sepsis in alerted vs. `17.12%` in unalerted). Restricting to AI-positive encounters (`ai_risk_score >= 0.50`, $n = 653$)—where `alert_delivered = 0` occurs solely via `HOSP_C` surge throttling—reverses the effect sign: alerted mortality is **`14.08%`** vs. **`26.38%`** when throttled (**RD = `-12.30%`**, Fisher's exact $p = 4.86 \times 10^{-4}$; Mantel–Haenszel RD = **`-11.61%`**, $\text{OR}_{\text{MH}} = 0.464$ stratified by true sepsis and immunocompromised status).
- **Paradox 2 — Early Antibiotics vs. Mortality**: Unadjusted cohort comparison masks antibiotic efficacy (`8.66%` [`62/716`] treated vs. `10.39%` [`175/1,684`] untreated; RD = `-1.73%`, $\chi^2 p = 0.220$) due to confounding by clinical indication (`56.01%` vs. `19.42%` sepsis prevalence). Stratified within true sepsis ($n = 728$), early antibiotics reduce 30-day mortality from **`40.98%` (`134/327`)** to **`13.47%` (`54/401`)** (**ARR = `-27.51%`**, $\chi^2 p = 6.75 \times 10^{-17}$)—and within immunocompromised sepsis ($n = 194$), from **`57.69%` (`75/130`)** to **`25.00%` (`16/64`)** (**ARR = `-32.69%`**). Across all 16 `(sepsis_ground_truth, immunocompromised, hospital_id)` strata, Cochran–Mantel–Haenszel pooling confirms a strong protective treatment effect ($\text{OR}_{\text{MH}} = 0.392$, adjusted RD = `-7.85%`).

### 2.2 Neutropenic Subgroup Recalibration (`anc_cells_ul < 500`) & Decision Curve Net Benefit
All `immunocompromised == 1` patients ($n = 327$, `0` OOD rows) have severe neutropenia (`anc_cells_ul < 500`) and `59.33%` (`194/327`) true sepsis prevalence. Unlike immunocompetent septic patients (`mean temp = 38.83°C`, `mean raw score = 0.7394`), neutropenic septic patients exhibit **afebrile lactatemia** (`mean temp = 36.70°C` vs. `36.59°C` non-septic; `mean lactate = 3.81` vs. `1.30 mmol/L`). Because the model relies heavily on fever for intercept calibration while still ordering lactate/PCT monotonically, subgroup **`AUROC` is `0.9456`**, yet raw probabilities are severely under-calibrated (`mean septic score = 0.4150`).

Applying 5-fold stratified out-of-fold (OOF) **Platt logistic recalibration** ($\hat{p}_{\text{cal}} = \sigma(-4.7472 + 20.4421 \cdot s)$) paired with a cost-asymmetric clinical threshold **`calibrated_subgroup_threshold = 0.30`** (reflecting a 3:7 false-alarm-to-missed-sepsis harm ratio given `57.69%` untreated neutropenic sepsis mortality; equivalent raw score cutpoint `0.1908`, whereas $\hat{p}_{\text{cal}} = 0.50$ maps to raw score `0.2322` and Youden's $J$ peaks at raw score `0.2424`) restores clinical safety:

| Subgroup Metric (`anc_cells_ul < 500`, $n = 327$) | Pre-Recalibration (`s >= 0.50`) | Post-Recalibration OOF ($\hat{p}_{\text{cal}} \ge 0.50$) | **Post-Recalibration OOF ($\hat{p}_{\text{cal}} \ge 0.30$)** | Clinical / Statistical Change |
| :--- | :---: | :---: | :---: | :--- |
| **False-Negative Rate (`FNR`)** | **`70.62%`** (`137/194`) | `10.31%` (`20/194`) | **`7.73%`** (`15/194`) | **`-62.89` pp** (`122` rescued sepsis cases) |
| **Expected Calibration Error (`ECE`, 10-bin)** | **`0.2880`** | `0.0295` | **`0.0295`** | **`-89.77%`** relative calibration error reduction |
| **Brier Score** | `0.2275` | `0.0886` | **`0.0886`** | **`-61.05%`** proper scoring loss reduction |
| **DCA Net Benefit at $p_t = 0.30$** (`Treat-All = 0.4190`) | `0.1743` (`s>=0.30`: `0.4443`) | — | **`0.5002`** | **`+0.3259` uplift** vs deployed (`+0.0559` vs raw `0.30`; `+0.0813` vs Treat-All) |
| **DCA Net Benefit at $p_t = 0.50$** (`Treat-All = 0.1865`) | `0.1743` (*worse than Treat-All*) | **`0.4832`** | — | **`+0.3089` uplift** (reverses `-0.0122` net harm vs Treat-All) |

### 2.3 Procalcitonin Reagent Drift (`PCT_LOT_DRIFT_X9`) & Mandatory HITL Abstention Gate
Cross-tabulating `analyzer_lot` against `procalcitonin_ng_ml` demonstrates **100% concordance** (`50/50` rows, `2.08%` of cohort) between `analyzer_lot == 'PCT_LOT_DRIFT_X9'` (`PCT` range `13.98–63.84 ng/mL`, mean `37.24`) and `procalcitonin_ng_ml > 12.0 ng/mL` (standard lot `PCT_LOT_STD_04` max is `9.87 ng/mL`). Unbounded feature scaling pushes all `50` drifted specimens into extreme score saturation (`0.8411–0.9786`), generating `39` false positives (`78.0%` false discovery rate within lot `X9`) and corrupting top-decile `[0.9, 1.0]` PPV (`82.73%` full cohort vs. **`100.0%`** cleaned).

- **Mandatory Pre-Inference Abstention Gate Rule**:
  `IF procalcitonin_ng_ml > 12.0 OR analyzer_lot != 'PCT_LOT_STD_04' -> ABSTAIN_TO_CLINICIAN_HITL` (suppress autonomous AI score and automated sepsis page; render OOD assay-drift banner; trigger stat repeat PCT/lactate on validated reagent lot).
- **Cleaned & Recalibrated Cohort Impact ($N = 2,350$)**: Removing the `50` abstained OOD encounters immediately lifts raw-score `AUROC` from `0.9248` to **`0.9428`**, accuracy from `87.96%` to **`89.36%`**, `PPV` from `83.61%` to **`88.72%`**, and lowers `FPR` from `6.40%` to **`4.16%`** (`Brier = 0.0992`). Pairing OOD abstention with subgroup-stratified OOF Platt recalibration across $N = 2,350$ achieves **`AUROC = 0.9831`**, **`ECE = 0.0080`**, **`Brier = 0.0453`**, and **`Accuracy = 93.79%`** (`93.15%` with `FNR = 11.16%` under the `0.30` neutropenic threshold).

---

## 3. FDA SaMD Predetermined Change Control Plan (PCCP)
Prepared per FDA Guidance *Marketing Submission Recommendations for a Predetermined Change Control Plan for Artificial Intelligence-Enabled Device Software Functions* (21 CFR 820 Design Controls, ISO 14971 Risk Management, Good Machine Learning Practice):

### 3.1 Description of Planned Modifications (DP)
1. **Subgroup-Conditional Monotonic Recalibration & Threshold Locking**: Post-hoc 2-parameter logistic (Platt) recalibration stratified by `anc_cells_ul < 500` vs. `>= 500` (with missing recent ANC `<72h` routed to oncology/transplant ICD-10 registry flag + HITL confirmation), paired with pre-specified cost-sensitive operating thresholds (`0.30` neutropenic; `0.50` immunocompetent).
2. **Pre-Inference LIS Telemetry & OOD Assay-Drift Abstention Gate**: Deterministic HL7/FHIR `OBX` input validation rejecting unverified `analyzer_lot` identifiers or physiologically extreme/uncalibrated `procalcitonin_ng_ml > 12.0 ng/mL` into a mandatory HITL abstention state.
3. **Middleware Alert-Routing Integrity Lock**: Cryptographic configuration lock prohibiting hospital IT middleware from dropping/throttling SaMD alerts based on `icu_occupancy_pct` or nurse staffing ratios.
4. **Explicit Out-of-Scope Boundary (Requires New 510(k)/Supplement)**: Changing core neural/gradient-boosted feature weights, adding unvalidated EHR predictors, expanding intended use outside adult ICUs, or enabling autonomous antibiotic order entry without clinician sign-off.

### 3.2 Modification Protocol (MP)
- **Confounding-Adjusted Reference Standard & Data Hygiene**: Because deployed alerts trigger `early_antibiotics` and alter `mortality_30d`, recalibration labels must strictly use adjudicated **Sepsis-3 onset prior to treatment** (`sepsis_ground_truth`), while downstream mortality surveillance must apply **Inverse Probability of Censored/Treatment Weighting (IPTW) or Cochran–Mantel–Haenszel stratification** across `(acuity, subgroup, hospital_id, occupancy)` to prevent Simpson's Paradox bias during model updates.
- **Validation Partitioning & Sample Size Floor**: Any quarterly site/subgroup recalibration requires a temporally disjoint holdout cohort ($\ge 250$ immunocompromised cases including $\ge 100$ sepsis events across $\ge 3$ hospitals) evaluated via 5-fold patient-grouped cross-validation plus external site holdout.
- **Acceptance Criteria (All Must Pass Prior to Promotion)**:
  1. Neutropenic (`anc_cells_ul < 500`) `ECE <= 0.05` (upper 95% bootstrap CI `<= 0.07`) and `FNR <= 10.0%` at `p_t = 0.30`.
  2. Immunocompetent (`anc_cells_ul >= 500`) `ECE <= 0.05`, `PPV >= 85.0%`, and `FPR <= 6.0%` at `p_t = 0.50`.
  3. Positive Decision Curve Net Benefit uplift over both `Treat-All` and `Treat-None` across the entire clinical threshold range $p_t \in [0.20, 0.50]$.
  4. `100.0%` deterministic capture of synthetic OOD lot-drift injection tests (`CLSI EP26-A` lot-to-lot verification handshake with LIS prior to activating any new `analyzer_lot` in production).

### 3.3 Impact Assessment (IA)
- **Benefit–Risk Balance**: Recalibrating neutropenic scores increases subgroup `FPR` from `0.0%` to `27.07%` (`36` additional false alarms out of `133` non-septic neutropenic stays), which is overwhelmingly outweighed by rescuing **`122 / 137` previously missed neutropenic sepsis patients** where delayed antibiotics carry a `+32.69%` excess 30-day mortality penalty (`NB` uplift `+0.3259`). Meanwhile, OOD abstention *eliminates* `39` spurious high-confidence false alarms across immunocompetent beds, **reducing net network false positives (`107 -> 104`)** even after lowering the neutropenic threshold.
- **Health Equity & Cross-Site Generalizability**: Eliminates systematic under-treatment of immunocompromised oncology/transplant patients and removes surge-capacity care rationing in `HOSP_C` (which serves the highest baseline sepsis prevalence, `37.29%`).

---

## 4. Clinician HITL Safety Governance, Guardrails & Rollback Protocol

### 4.1 Mandatory HITL Workflow for OOD Abstention & Surge Escalation
1. **OOD Abstention UI State (`PCT > 12.0` or Unverified `analyzer_lot`)**: Suppress numeric `ai_risk_score` completely (preventing automation bias from `0.92+` saturated scores). Display **Amber Safety Banner**: *"AI Risk Score Withheld — Procalcitonin Assay Outside Validated Calibration Range (`Lot Drift / >12 ng/mL`). Evaluate sepsis clinically using vital signs, lactate, and organ dysfunction; order stat repeat lab on validated lot."* Automatically notify Clinical Chemistry QA to quarantine the drifted reagent lot.
2. **Prohibition of Silent Throttling & Surge Load-Balancing (`HOSP_C` Remediation)**: Immediately disable the `icu_occupancy_pct > 85%` suppression script. During surge occupancy (`>85%`), route `ai_risk_score` alerts to a **tiered Charge Nurse / Sepsis Rapid-Response Team (RRT) / Tele-ICU Pharmacist queue** rather than dropping telemetry, preserving `100%` alert delivery while protecting bedside nurse cognitive load.
3. **Neutropenic Atypical Sepsis Presentation Card**: All positive neutropenic alerts (`anc_cells_ul < 500`, $\hat{p}_{\text{cal}} \ge 0.30$) display `temperature_c`, `lactate_mmol_l`, and `anc_cells_ul` inline with an explicit clinical reminder: *"Afebrile lactatemia in severe neutropenia carries >50% untreated mortality; evaluate for immediate 1-hour sepsis bundle."*

### 4.2 Quantitative Post-Market Surveillance Guardrails & Automated Rollback Triggers
Real-time Statistical Process Control (SPC / CUSUM) monitors every rolling 7-day / $N = 200$ encounter window per hospital, enforcing immediate **automated rollback to the prior validated parameter lock + fallback clinical SIRS/lactate safety rule** if any trigger fires:
- **Trigger R1 (Subgroup Calibration / Sensitivity Breach)**: Rolling neutropenic `ECE > 0.08` or adjudicated 14-day neutropenic `FNR > 12.0%` (or $\ge 2$ consecutive missed bacteremic/lactatemic `lactate >= 4.0 mmol/L` neutropenic sepsis deaths).
- **Trigger R2 (Assay Drift / Abstention Surge)**: Site OOD abstention rate exceeds **`3.0%`** over 24 hours, or Kolmogorov–Smirnov shift $p < 0.001$ on daily `procalcitonin_ng_ml` or `lactate_mmol_l` medians -> auto-quarantine LIS feed for that analyzer and revert SaMD to lab-lot-independent vital/lactate fallback mode.
- **Trigger R3 (Alert Delivery / Alarm Fatigue Breach)**: Middleware `alert_delivered / eligible_alerts` drops below **`99.5%`** in any 6-hour window (instant P1 page to Clinical Engineering), OR site `PPV` falls below **`70.0%`** / alert volume increases `> 35%` above baseline.

### 4.3 Multi-Disciplinary Governance & Sign-Off Matrix
No PCCP parameter update, threshold adjustment, or reagent-lot whitelist addition may enter production without cryptographically logged sign-off across five accountable authorities:
1. **Principal Clinical Biostatistician & AI Safety Lead**: Verifies OOF calibration (`ECE`), DCA Net Benefit, and Mantel–Haenszel confounding-adjusted outcome surveillance.
2. **Director of Oncology / Transplant Critical Care & ICU Medical Director**: Approves subgroup `0.30` threshold trade-offs and sepsis bundle escalation workflows.
3. **Director of Clinical Chemistry & Laboratory Medicine**: Certifies `CLSI EP26-A` `analyzer_lot` calibration concordance prior to LIS whitelist entry.
4. **Chief Medical Information Officer (CMIO) & Nursing Informatics Lead**: Certifies `100%` removal of occupancy-throttling rules and validates surge RRT/Tele-ICU routing.
5. **Regulatory Affairs & Institutional Review Board (IRB) / Clinical Risk Committee**: Confirms PCCP boundary compliance (21 CFR 820.30), logs CAPA closure for `HOSP_C` and `PCT_LOT_DRIFT_X9` incidents, and authorizes post-market safety reporting (21 CFR Part 803 MDR evaluation).
