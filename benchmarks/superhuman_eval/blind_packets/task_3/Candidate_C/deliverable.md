# Biostatistical Root-Cause Analysis, FDA SaMD PCCP & Clinician HITL Safety Protocol

## 1. OOD Regime Diagnosis & Pattern-Match Veto Ledger (Stage 1 — Exit Gate 1)
Aggregate discrimination across the 4-hospital ICU deployment (`N = 2,400`, `HOSP_A..HOSP_D`) appears strong (**`AUROC = 0.9248`** for `sepsis_ground_truth` vs. `0.91` nominal target; **`0.6748`** for `mortality_30d`), creating a classic **Phantom Green-Dashboard illusion**. Partitioning the state space exposes one well-behaved in-distribution core and three orthogonal failure regimes:
- **Known In-Distribution Core (`n = 2,023`)**: Immunocompetent (`anc_cells_ul >= 500`) patients assayed on standard reagent lot `PCT_LOT_STD_04` (`procalcitonin_ng_ml <= 12.0`), where baseline `AUROC = 0.9866`, `Accuracy@0.50 = 94.41%`, and `Sensitivity = 91.40%`.
- **OOD / Confounded Regimes (`n = 377` unique patients)**: (1) **Subgroup Covariate Shift (`n = 327`, `anc_cells_ul < 500`)** exhibiting 100% afebrile hyperlactatemia (`30d mortality = 28.75%` vs. `6.90%` immunocompetent); (2) **Workflow Confounding (`HOSP_C`, `n = 700`)** where nursing IT throttled 100% of alerts whenever `icu_occupancy_pct > 85%`; and (3) **Assay Drift (`n = 50`, `PCT_LOT_DRIFT_X9`)** where `procalcitonin_ng_ml > 12.0 ng/mL` saturates `ai_risk_score` (`mean = 0.9156`).

| Vetoed Naive Textbook / LLM Pattern-Match | Mechanistic & Biostatistical Failure Mode Under Local Physics |
| :--- | :--- |
| **Veto 1: Lower global threshold (`0.50 -> 0.25`) or retrain one pooled model on `N = 2,400`** | Floods immunocompetent ICUs (`86.4%` of volume) with false alarms, accelerating nurse alert fatigue, while baking `PCT_LOT_DRIFT_X9` reagent corruption directly into model weights. |
| **Veto 2: Decommission AI alerts because unadjusted alerted mortality is higher (`14.08%` vs. `8.80%`)** | Violates Pearl's back-door criterion (**Simpson's Paradox**): `alert_delivered=0` is diluted by `1,672` low-acuity non-septic patients (`~3.0%` mortality), masking a massive life-saving alert effect within septic strata. |
| **Veto 3: Winsorize/clip `procalcitonin_ng_ml` at `12.0 ng/mL` and continue autonomous alerting** | On `PCT_LOT_DRIFT_X9` (`n = 50`), within-lot `AUROC = 0.4242` (worse than random) and `PPV = 22.0%`. Clipping still forces a deterministic `score >= 0.84` false-positive storm (`39` FPs) instead of failing safe to HITL. |

---

## 2. First-Principles Conservation & Fermi Feasibility Proof (Stage 2 — Exit Gate 2)

### 2.1 Causal Structural Equations & Telemetry Conservation Law
Let $Z \in \{0,1\}$ be true sepsis, $I = \mathbb{I}(\text{ANC} < 500)$, $O = \mathbb{I}(\text{HOSP\_C} \land \text{Occ} > 85\%)$, and $L = \mathbb{I}(\text{PCT} > 12 \lor \text{Lot} \neq \text{STD\_04})$. Every score-eligible encounter must obey the **Zero-Silent-Drop Alert Conservation Identity**:
$$\text{Eligible}(S \ge \tau_I) \equiv \text{Delivered}_{\text{Bedside}} + \text{Routed}_{\text{RapidResponse}} + \text{Abstained}_{\text{OOD\_HITL}} + \underbrace{\text{Suppressed}_{\text{Silent}}}_{\text{Hard Invariant } \equiv 0}$$
In `HOSP_C` (`n = 700`), `502` admissions (`71.71%`) occurred at `icu_occupancy_pct > 85%`. Among `163` high-occupancy patients with `ai_risk_score >= 0.50`, **`0/163` alerts were delivered (`100.0%` suppression rate**, vs. `0.0%` suppression [`69/69` delivered] at `<= 85%` occupancy, and `70.26%` [`163/232`] suppressed overall in `HOSP_C`). Throttling severed the treatment mediator: `early_antibiotics` collapsed from **`84.06%`** (`<= 85%` occ) to **`18.40%`** (`> 85%` occ), raising `HOSP_C` high-score 30d mortality from **`21.74%` to `26.38%`**.

### 2.2 Resolution of Simpson's Paradox & Causal Treatment Estimands
- **Unadjusted Illusion (`N = 2,400`)**: `alert_delivered = 1` exhibits `14.08%` mortality vs. `8.80%` for `alert_delivered = 0` (**naive `RD = +5.29%`**); `early_antibiotics = 1` shows `8.66%` vs. `10.39%` (**naive `RD = -1.73%`**).
- **Confounding-Adjusted Reality**: Conditioning on score eligibility (`ai_risk_score >= 0.50`, `n = 653`, where `alert_delivered = 0` occurs exclusively via `HOSP_C` throttling) reverses the sign: **`14.08%` (delivered) vs. `26.38%` (throttled), `RD = -12.30%`**. Within `sepsis_ground_truth = 1` (`n = 728`), alert delivery lowers mortality **`16.46%` vs. `37.31%` (`RD = -20.85%`)**, and `early_antibiotics` lowers mortality **`13.47%` vs. `40.98%` (`RD = -27.51%`)**. In immunocompromised sepsis (`n = 194`), `early_antibiotics` cuts 30d mortality from **`57.69%` (`75/130`) to `25.00%` (`16/64`), `ARR = -32.69%` (`NNT = 3.06`)**. Cochran-Mantel-Haenszel stratification across `(sepsis x immunocompromised)` yields common **`RD = -8.20%` (`OR = 0.518`)** for alerts and **`RD = -9.12%` (`OR = 0.349`)** for early antibiotics (G-computation standardized `ATE = -7.08%`).

### 2.3 Subgroup Pathophysiology, Decision-Curve Utility & Queueing Load Proof
In `anc_cells_ul < 500` (`n = 327`, sepsis prevalence `59.33%`), neutrophil depletion ablates pyrogenic cytokine cascades: **`100.0%` (`194/194`) of septic patients are afebrile (`temperature_c < 38.0°C`, mean `36.70°C` vs. `38.87°C` immunocompetent)** while **`100.0%` exhibit hyperlactatemia (`lactate_mmol_l > 2.0`, mean `3.81 mmol/L`)**. The fever-reliant model compresses septic scores to `mean = 0.4150`, yielding **`pre_recalibration_fn_rate = 70.62%` (`137/194` missed)** and **`pre_recalibration_ece = 0.2880`** at threshold `0.50`, despite intact rank ordering (`subgroup AUROC = 0.9456`).
- **Vickers-Elkin Harm-Benefit Bound**: Given `ARR = 32.69%` from early antibiotics in neutropenic sepsis, clinical utility dictates threshold probability **$p_t = 0.30$** (harm-to-benefit exchange `p_t/(1-p_t) = 1:2.33`, accepting $\le 2.33$ empiric antibiotic workups per true sepsis rescued):
  $$\text{NB}(p_t) = \frac{TP}{N} - \frac{FP}{N}\left(\frac{p_t}{1 - p_t}\right)$$
- **Little's Law Nursing Capacity Proof**: System-wide false positives at baseline (`107` total) include `39` OOD drift FPs (`36.4%` of all FPs from `2.08%` of patients!). Abstaining on the `50` OOD rows (`-39` FPs) while recalibrating `ANC < 500` at $p_t = 0.30$ (`+36` FPs, `+122` TPs rescued) yields **net `-3` false positives system-wide (`107 -> 104`)**, proving zero added false-alarm burden while rescuing `122` missed neutropenic sepsis cases (~`34` preventable deaths across `ANC < 500` + `HOSP_C`).

---

## 3. Polymathic Architecture & FDA SaMD PCCP + HITL Protocol (Stage 3 — Exit Gate 3)

### 3.1 Cross-Adjacent Structural Isomorphism Mapping (Exit Gate 3)
| Internalized Cross-Functional Neighbor Role | Imported Mechanism | Exact Mathematical / Operational Mapping in Sepsis SaMD |
| :--- | :--- | :--- |
| **Director of Clinical Trials Ops (GCP)** (`CHALLENGES_OR_AUDITS`) | **ICH E9(R1) Estimands & O'Brien-Fleming Alpha-Spending (`FWER <= 0.025`)** | Separates *Treatment-Policy* (throttled `HOSP_C`) from *Hypothetical Unthrottled* estimand; enforces multiplicity-controlled subgroup stopping boundaries (`FNR <= 10%`, `ECE <= 0.05`). |
| **Director of FDA Regulatory Affairs** (`HANDS_OFF_TO`) | **FDA SaMD PCCP (Modification Protocol + Impact Assessment)** | Pre-specifies bounded monotonic Platt subgroup recalibration + OOD abstention gate without triggering a de novo 510(k)/PMA supplement. |
| **Lead CRA & Site Monitor** (`COLLABORATES_WITH`) | **100% Source Document Verification (SDV) & 24h SAE Escalation** | Cryptographic HL7 `OBX-15` analyzer-lot checksum + EHR bidirectional `ACK` ledger verifying `Eligible == Delivered + Escalated`; 24h SAE review on any septic death with unacknowledged alert. |

### 3.2 FDA SaMD Predetermined Change Control Plan (PCCP) Specification
1. **Description of Planned Modifications**:
   - **Mod-1 (Subgroup Monotonic Platt Recalibration — Immediate)**: For `anc_cells_ul < 500` (valid within 72h EHR window), map raw score $s$ via locked 5-fold CV logistic link $\hat{p}_{\text{cal}} = \sigma(20.4421 s - 4.7472)$ and fire bedside sepsis bundle alert at **`calibrated_subgroup_threshold = 0.30`** (algebraically equivalent to raw `ai_risk_score >= 0.1908`). Validated 5-fold CV results: **`post_recalibration_ece = 0.0295`** (down `-89.8%` from `0.2880`), **`post_recalibration_fn_rate = 7.73%`** (`15/194`, down `-89.1%` from `70.62%`), and **Decision Curve `Net Benefit = 0.5002`** vs. `0.1743` deployed (`+0.3259` uplift), `0.4443` uncalibrated `@0.30` (`+0.0559` uplift), and `0.4190` Treat-All (`+0.0812` uplift).
   - **Mod-2 (Bounded Covariate Interaction Update — Phase 2 PCCP)**: Pre-specified retraining envelope adding explicit `(ai_risk_score, lactate_mmol_l, temperature_c)` interaction for `ANC < 500` (`5-fold CV AUROC = 0.9955`, `Brier = 0.0062`), gated by prospective shadow validation (`N >= 500` subgroup encounters).
   - **Mod-3 (Pre-Inference OOD Assay Abstention Gate)**: Deterministic rule `IF procalcitonin_ng_ml > 12.0 OR analyzer_lot NOT IN Approved_Std_Lots ('PCT_LOT_STD_04') -> EMIT OOD_ASSAY_ABSTAIN`. Suppresses corrupted AI probability (`50/50` `PCT_LOT_DRIFT_X9` rows caught with 100% concordance) and cleans cohort (`n = 2,350`) to **`AUROC = 0.9428` raw / `0.9831` post-stratified-recalibration**, **`Accuracy = 93.15%`**, and **`ECE = 0.0080`**.
2. **Clinician HITL Safety Governance & `HOSP_C` Anti-Throttling Architecture**:
   - **OOD HITL Workflow**: When `OOD_ASSAY_ABSTAIN` fires, Epic/Cerner suppresses the numerical AI score, displays *"Assay Drift / Out-of-Range PCT (`>12 ng/mL` or unverified lot): AI Abstained — Evaluate Bedside Lactate & Clinical Signs"*, orders stat repeat chemistry/lactate, and logs attending attestation.
   - **Zero-Throttle Escalation Relay**: Prohibits occupancy-based suppression (`21 CFR 820.30` design control lock). When `icu_occupancy_pct > 85%`, unacknowledged primary-RN alerts at `T + 5 min` auto-route to the **ICU Charge Nurse + Sepsis Rapid Response Nurse**, bounding bedside queuing delay without dropping alerts.
   - **Governance Sign-Off**: Requires affirmative co-signature from Chair of Clinical Risk Committee, Oncology/Transplant ICU Medical Director, Laboratory Medicine CLIA Director, CISO/Clinical Informatics Lead, and central IRB expedited safety determination prior to production cutover.

---

## 4. Falsifiable Hypothesis Tree & Micro-Experiments (Stage 4 — Exit Gate 4)
| ID | Competing Abductive Hypothesis | Instrumentation Probe & Micro-Experiment (Timebox) | Disconfirming Metric / Pass-Fail Gate | Instant Rollback Trigger |
| :--- | :--- | :--- | :--- | :--- |
| **H1** | `ANC < 500` excess mortality stems from afebrile calibration shift (`FNR = 70.6%`), not rank-order collapse. | 14-day silent shadow replay + prospective canary on Oncology ICU (`n >= 60`). | **Pass**: Subgroup `AUROC >= 0.90`, `ECE <= 0.05`, `FNR <= 10%` at $p_t=0.30$. **Falsified** if `AUROC < 0.80`. | Revert to clinician lactate>=2.0 rule if subgroup `FPR > 35%` or `ECE > 0.08`. |
| **H2** | `HOSP_C` excess mortality (`13.86%`) is mediated by `>85%` occupancy IT throttling severing early antibiotics. | Audit HL7 broker queue vs. Epic BPA delivery logs; restore RRT routing in 7-day `HOSP_C` canary. | **Pass**: Alert delivery `100%` at `>85%` occ; `early_antibiotics` rises `>= 75%` within 3h. | Route overflow alerts to Tele-ICU physician pool if bedside RN ACK latency `P95 > 12 min`. |
| **H3** | False-alarm bursts originate specifically from `PCT_LOT_DRIFT_X9` (`PCT > 12.0`) reagent lot bias. | Split-sample CLIA paired run (`PCT_LOT_DRIFT_X9` vs. `PCT_LOT_STD_04`, `n = 30` aliquots, 48h). | **Pass**: Paired bias `> +10 ng/mL` on `DRIFT_X9`; cleaned `PPV >= 88%`. | Quarantine analyzer channel & widen abstention to `PCT > 8.0 ng/mL` if residual `ECE > 0.06`. |
| **H4** | Residual `ANC < 500` mortality reflects antimicrobial resistance despite timely empiric therapy. | 30-day blood-culture bug-drug concordance audit on treated neutropenic sepsis (`n = 64`). | **Falsifies AI-only sufficiency** if `>15%` of `early_antibiotics=1` deaths had discordant empiric coverage. | Escalate default neutropenic order set to carbapenem + vancomycin per ID stewardship. |

---

## 5. Internalized Red-Team Pre-Mortem & Traceability Matrix (Stage 5 — Exit Gate 5)
Assuming a catastrophic post-remediation audit failure in 6 months, we pre-emptively close five adversarial vectors:
1. **Missing/Stale `ANC` on New ICU Transfers**: Newly admitted oncology transfers lacking an `ANC` within 72h would default to the immunocompetent `0.50` threshold. *Mitigation*: Pull active ICD-10 oncology/transplant problem-list flags (`C81–C96`, `Z94.*`) as a conservative proxy routing to the `ANC < 500` safety curve until stat CBC results post.
2. **HL7 Missing `OBX-15` Lot Tag**: Middleware stripping `analyzer_lot` could bypass lot-name checks. *Mitigation*: Dual OR-gate (`procalcitonin_ng_ml > 12.0` **OR** missing/unapproved `analyzer_lot` **OR** rolling 50-sample median PCT shift `> 3 sigma` via CUSUM drift monitor).
3. **Compensatory Nurse Alert Dismissal in `HOSP_C`**: Restoring `163` suppressed alerts during `>85%` surge could trigger reflexive dismissal. *Mitigation*: Route `>85%` surge alerts directly to Rapid Response / Tele-ICU pharmacist pre-staging antibiotic orders (1-click MD co-sign).
4. **Multiplicity & Post-Deployment Calibration Drift**: Repeated monthly recalibration across 4 sites inflates false positives. *Mitigation*: Lock Platt parameters (`slope=20.4421, intercept=-4.7472`) under versioned checksums; permit updates only via Holm-Bonferroni (`FWER <= 0.025`) quarterly PCCP gates.
5. **Developer Context Zero-Omission Verification**: (a) `HOSP_C` `>85%` throttling quantified (`100%` suppression) & locked out; (b) `ANC < 500` afebrile lactatemia (`100% <38°C`, mean lactate `3.81`) recalibrated (`ECE 0.2880 -> 0.0295`, `FNR 70.62% -> 7.73%`); (c) `PCT > 12 ng/mL` (`50` OOD rows) gated to mandatory clinician HITL abstention.

---

## 6. Sequenced Execution Runbook & Rollback Triggers
- **Day 1 (Immediate Andon-Cord Containment)**: (1) Quarantine `PCT_LOT_DRIFT_X9` with CLIA Lab Director and deploy `OOD_ASSAY_ABSTAIN` gate (`PCT > 12.0` or non-standard lot); (2) Disable `HOSP_C` `>85%` occupancy throttling rule and enable Rapid-Response overflow relay; (3) Issue Retrospective Safety Lookback (`137` missed `ANC < 500` + `163` throttled `HOSP_C` charts) to Clinical Risk & Site Monitors.
- **Days 2–30 (PCCP Mod-1 Cutover)**: Obtain IRB/Clinical Risk co-signatures; deploy `ANC < 500` Platt recalibration (`p_t = 0.30` / raw `>= 0.1908`) with `21 CFR Part 11` immutable audit logging.
- **Days 31–90 (Surveillance & Mod-2 Shadowing)**: Run weekly CUSUM calibration audits (`ECE`, `FNR`, `PPV`, `ACK` latency) across `HOSP_A..D` and shadow-test Mod-2 `(score, lactate, temp)` interaction model.
- **Automated Deterministic Rollback Circuit-Breakers**: Instant revert to baseline + bedside SIRS/lactate protocol if any rolling 14-day window breaches: (1) Subgroup `ECE > 0.06`, (2) `ANC < 500` `FNR > 12.0%`, (3) Cleaned cohort `PPV < 80.0%`, or (4) Any single silent alert drop (`Eligible - Delivered - Abstained != 0`).
