#!/usr/bin/env python3
"""Task 3: Multi-Hospital Sepsis AI Failure Diagnosis, Subgroup Recalibration & OOD Abstention."""

import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import logit
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold

COHORT_CSV = Path(
    "/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/"
    "benchmarks/superhuman_eval/tasks/task3_clinical_sepsis/sepsis_cohort.csv"
)
OUT_DIR = Path(__file__).resolve().parent


def compute_ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    n, ece = len(y_true), 0.0
    for i in range(n_bins):
        mask = (y_prob >= bins[i]) & (y_prob <= bins[i + 1] if i == n_bins - 1 else y_prob < bins[i + 1])
        if np.any(mask):
            ece += (np.sum(mask) / n) * abs(float(np.mean(y_true[mask])) - float(np.mean(y_prob[mask])))
    return float(ece)


def net_benefit(y_true: np.ndarray, y_pred_bin: np.ndarray, pt: float) -> float:
    n = len(y_true)
    tp = int(np.sum((y_pred_bin == 1) & (y_true == 1)))
    fp = int(np.sum((y_pred_bin == 1) & (y_true == 0)))
    return float((tp / n) - (fp / n) * (pt / (1.0 - pt)))


def mantel_haenszel(df: pd.DataFrame, treat: str, outcome: str, strata: list[str]) -> dict:
    rd_num, rd_den, or_num, or_den = 0.0, 0.0, 0.0, 0.0
    for _, g in df.groupby(strata):
        t1, t0 = g[g[treat] == 1][outcome], g[g[treat] == 0][outcome]
        n1, n0 = len(t1), len(t0)
        if n1 == 0 or n0 == 0:
            continue
        a, c = int(t1.sum()), int(t0.sum())
        b, d, n_tot = n1 - a, n0 - c, n1 + n0
        w = (n1 * n0) / n_tot
        rd_num, rd_den = rd_num + w * ((a / n1) - (c / n0)), rd_den + w
        or_num, or_den = or_num + (a * d) / n_tot, or_den + (b * c) / n_tot
    return {
        "mh_adjusted_risk_difference": round(float(rd_num / rd_den), 6),
        "mh_common_odds_ratio": round(float(or_num / or_den), 6),
    }


def oof_platt(scores: np.ndarray, y: np.ndarray, skf: StratifiedKFold) -> np.ndarray:
    oof = np.zeros_like(scores)
    for tr, va in skf.split(scores.reshape(-1, 1), y):
        clf = LogisticRegression(C=1e6, solver="lbfgs").fit(scores[tr].reshape(-1, 1), y[tr])
        oof[va] = clf.predict_proba(scores[va].reshape(-1, 1))[:, 1]
    return oof


def analyze_cohort(csv_path: Path) -> dict:
    df = pd.read_csv(csv_path)
    n_total = int(len(df))
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # 1. Simpson's Paradox & HOSP_C High-Occupancy (>85%) Throttling
    hc = df[df["hospital_id"] == "HOSP_C"]
    hc_hi = hc[hc["icu_occupancy_pct"] > 85.0]
    hc_hi_el = hc_hi[hc_hi["ai_risk_score"] >= 0.50]
    hc_lo_el = hc[hc["icu_occupancy_pct"] <= 85.0][lambda x: x["ai_risk_score"] >= 0.50]
    hc_all_el = hc[hc["ai_risk_score"] >= 0.50]

    unadj_al1, unadj_al0 = float(df[df["alert_delivered"] == 1]["mortality_30d"].mean()), float(df[df["alert_delivered"] == 0]["mortality_30d"].mean())
    unadj_abx1, unadj_abx0 = float(df[df["early_antibiotics"] == 1]["mortality_30d"].mean()), float(df[df["early_antibiotics"] == 0]["mortality_30d"].mean())
    elig = df[df["ai_risk_score"] >= 0.50]
    el_al1, el_al0 = float(elig[elig["alert_delivered"] == 1]["mortality_30d"].mean()), float(elig[elig["alert_delivered"] == 0]["mortality_30d"].mean())
    sep = df[df["sepsis_ground_truth"] == 1]
    sep_al1, sep_al0 = float(sep[sep["alert_delivered"] == 1]["mortality_30d"].mean()), float(sep[sep["alert_delivered"] == 0]["mortality_30d"].mean())
    sep_abx1, sep_abx0 = float(sep[sep["early_antibiotics"] == 1]["mortality_30d"].mean()), float(sep[sep["early_antibiotics"] == 0]["mortality_30d"].mean())

    std_abx1 = sum((len(g) / n_total) * float(g[g["early_antibiotics"] == 1]["mortality_30d"].mean()) for _, g in df.groupby(["sepsis_ground_truth", "immunocompromised"]))
    std_abx0 = sum((len(g) / n_total) * float(g[g["early_antibiotics"] == 0]["mortality_30d"].mean()) for _, g in df.groupby(["sepsis_ground_truth", "immunocompromised"]))

    simpsons_block = {
        "hosp_c_total_patients": int(len(hc)),
        "hosp_c_high_occupancy_gt_85_patients": int(len(hc_hi)),
        "hosp_c_high_occupancy_score_ge_050_n": int(len(hc_hi_el)),
        "hosp_c_high_occupancy_alerts_delivered": int(hc_hi_el["alert_delivered"].sum()),
        "hosp_c_high_occupancy_alert_suppression_rate": round(1.0 - float(hc_hi_el["alert_delivered"].mean()), 6),
        "hosp_c_normal_occupancy_alert_suppression_rate": round(1.0 - float(hc_lo_el["alert_delivered"].mean()), 6),
        "hosp_c_overall_eligible_alert_suppression_rate": round(1.0 - float(hc_all_el["alert_delivered"].mean()), 6),
        "hosp_c_score_ge_050_early_antibiotics_rate_throttled_gt_85": round(float(hc_hi_el["early_antibiotics"].mean()), 6),
        "hosp_c_score_ge_050_early_antibiotics_rate_unthrottled_le_85": round(float(hc_lo_el["early_antibiotics"].mean()), 6),
        "hosp_c_score_ge_050_mortality_throttled_gt_85": round(float(hc_hi_el["mortality_30d"].mean()), 6),
        "hosp_c_score_ge_050_mortality_unthrottled_le_85": round(float(hc_lo_el["mortality_30d"].mean()), 6),
        "unadjusted_cohort_mortality_by_alert": {
            "alert_delivered_1": round(unadj_al1, 6), "alert_delivered_0": round(unadj_al0, 6), "naive_risk_difference": round(unadj_al1 - unadj_al0, 6),
        },
        "unadjusted_cohort_mortality_by_early_antibiotics": {
            "early_antibiotics_1": round(unadj_abx1, 6), "early_antibiotics_0": round(unadj_abx0, 6), "naive_risk_difference": round(unadj_abx1 - unadj_abx0, 6),
        },
        "confounding_adjusted_and_stratified_effects": {
            "score_ge_050_alert_mortality_delivered_1": round(el_al1, 6),
            "score_ge_050_alert_mortality_throttled_0": round(el_al0, 6),
            "score_ge_050_alert_risk_difference": round(el_al1 - el_al0, 6),
            "sepsis_positive_alert_mortality_delivered_1": round(sep_al1, 6),
            "sepsis_positive_alert_mortality_unalerted_0": round(sep_al0, 6),
            "sepsis_positive_alert_risk_difference": round(sep_al1 - sep_al0, 6),
            "sepsis_positive_early_abx_mortality_1": round(sep_abx1, 6),
            "sepsis_positive_early_abx_mortality_0": round(sep_abx0, 6),
            "sepsis_positive_early_abx_risk_difference": round(sep_abx1 - sep_abx0, 6),
            "immunocompromised_sepsis_early_abx_mortality_1": round(float(sep[(sep["anc_cells_ul"] < 500) & (sep["early_antibiotics"] == 1)]["mortality_30d"].mean()), 6),
            "immunocompromised_sepsis_early_abx_mortality_0": round(float(sep[(sep["anc_cells_ul"] < 500) & (sep["early_antibiotics"] == 0)]["mortality_30d"].mean()), 6),
            "mantel_haenszel_alert_effect": mantel_haenszel(df, "alert_delivered", "mortality_30d", ["sepsis_ground_truth", "immunocompromised"]),
            "mantel_haenszel_early_antibiotics_effect": mantel_haenszel(df, "early_antibiotics", "mortality_30d", ["sepsis_ground_truth", "immunocompromised"]),
            "standardized_g_comp_early_antibiotics_ate": round(std_abx1 - std_abx0, 6),
        },
    }

    # 2. Immunocompromised Subgroup (anc_cells_ul < 500): Platt Recalibration & DCA Net Benefit
    imm = df[df["anc_cells_ul"] < 500].copy()
    y_imm, p_imm = imm["sepsis_ground_truth"].to_numpy(), imm["ai_risk_score"].to_numpy()
    oof_cal = oof_platt(p_imm, y_imm, skf)
    full_clf = LogisticRegression(C=1e6, solver="lbfgs").fit(p_imm.reshape(-1, 1), y_imm)
    slope, intercept = float(full_clf.coef_[0][0]), float(full_clf.intercept_[0])

    pt_target = 0.30
    post_pred = (oof_cal >= pt_target).astype(int)
    nb_dep = net_benefit(y_imm, (p_imm >= 0.50).astype(int), pt_target)
    nb_uncal = net_benefit(y_imm, (p_imm >= pt_target).astype(int), pt_target)
    nb_post = net_benefit(y_imm, post_pred, pt_target)
    nb_all = net_benefit(y_imm, np.ones_like(y_imm), pt_target)
    imm_sep = imm[imm["sepsis_ground_truth"] == 1]

    imm_block = {
        "n": int(len(imm)),
        "sepsis_cases": int(y_imm.sum()),
        "sepsis_prevalence": round(float(y_imm.mean()), 6),
        "mortality_30d_rate": round(float(imm["mortality_30d"].mean()), 6),
        "afebrile_sepsis_pct_temp_lt_38c": round(float((imm_sep["temperature_c"] < 38.0).mean()), 6),
        "mean_sepsis_temperature_c": round(float(imm_sep["temperature_c"].mean()), 4),
        "mean_sepsis_lactate_mmol_l": round(float(imm_sep["lactate_mmol_l"].mean()), 4),
        "subgroup_auroc": round(float(roc_auc_score(y_imm, p_imm)), 6),
        "pre_recalibration_fn_rate": round(float(np.sum((p_imm < 0.50) & (y_imm == 1)) / np.sum(y_imm == 1)), 6),
        "pre_recalibration_ece": round(compute_ece(y_imm, p_imm), 6),
        "pre_recalibration_brier": round(float(brier_score_loss(y_imm, p_imm)), 6),
        "post_recalibration_fn_rate": round(float(np.sum((post_pred == 0) & (y_imm == 1)) / np.sum(y_imm == 1)), 6),
        "post_recalibration_fp_rate": round(float(np.sum((post_pred == 1) & (y_imm == 0)) / np.sum(y_imm == 0)), 6),
        "post_recalibration_ece": round(compute_ece(y_imm, oof_cal), 6),
        "post_recalibration_brier": round(float(brier_score_loss(y_imm, oof_cal)), 6),
        "calibrated_subgroup_threshold": pt_target,
        "equivalent_raw_ai_risk_score_threshold": round(float((logit(pt_target) - intercept) / slope), 6),
        "platt_calibration_params": {"slope": round(slope, 6), "intercept": round(intercept, 6)},
        "decision_curve_net_benefit": {
            "threshold_probability_pt": pt_target,
            "pre_recalibration_deployed_050_nb": round(nb_dep, 6),
            "pre_recalibration_uncalibrated_030_nb": round(nb_uncal, 6),
            "treat_all_nb": round(nb_all, 6),
            "post_recalibration_nb": round(nb_post, 6),
            "net_benefit_uplift_vs_deployed_050": round(nb_post - nb_dep, 6),
            "net_benefit_uplift_vs_uncalibrated_030": round(nb_post - nb_uncal, 6),
            "net_benefit_uplift_vs_treat_all": round(nb_post - nb_all, 6),
        },
    }

    # 3. OOD Procalcitonin Assay Drift (>12.0 ng/mL / PCT_LOT_DRIFT_X9) & Cleaned Cohort
    ood_mask = (df["procalcitonin_ng_ml"] > 12.0) | (df["analyzer_lot"] == "PCT_LOT_DRIFT_X9")
    ood_df, clean_df = df[ood_mask], df[~ood_mask].copy().reset_index(drop=True)
    yc, pc = clean_df["sepsis_ground_truth"].to_numpy(), clean_df["ai_risk_score"].to_numpy()
    pred_c_raw = (pc >= 0.50).astype(int)

    pc_cal, pred_c_cal = np.zeros_like(pc), np.zeros_like(yc)
    for m, thresh in [((clean_df["anc_cells_ul"] < 500).to_numpy(), pt_target), ((clean_df["anc_cells_ul"] >= 500).to_numpy(), 0.50)]:
        pc_cal[m] = oof_platt(pc[m], yc[m], skf)
        pred_c_cal[m] = (pc_cal[m] >= thresh).astype(int)

    ood_block = {
        "detected_ood_rows": int(ood_mask.sum()),
        "pct_gt_12_and_drift_lot_exact_concordance": bool(((df["procalcitonin_ng_ml"] > 12.0) == (df["analyzer_lot"] == "PCT_LOT_DRIFT_X9")).all()),
        "abstention_gate_rule": (
            "IF procalcitonin_ng_ml > 12.0 OR analyzer_lot != 'PCT_LOT_STD_04' (e.g. 'PCT_LOT_DRIFT_X9') "
            "THEN suppress autonomous AI score, emit OOD_ASSAY_ABSTAIN flag, and route to mandatory clinician HITL review"
        ),
        "ood_subset_diagnostics": {
            "mean_ai_risk_score": round(float(ood_df["ai_risk_score"].mean()), 6),
            "true_sepsis_prevalence": round(float(ood_df["sepsis_ground_truth"].mean()), 6),
            "ood_auroc": round(float(roc_auc_score(ood_df["sepsis_ground_truth"], ood_df["ai_risk_score"])), 6),
            "ood_ece": round(compute_ece(ood_df["sepsis_ground_truth"].to_numpy(), ood_df["ai_risk_score"].to_numpy()), 6),
            "false_positives_eliminated": int(((ood_df["ai_risk_score"] >= 0.50) & (ood_df["sepsis_ground_truth"] == 0)).sum()),
        },
        "cleaned_cohort_metrics": {
            "n_cleaned": int(len(clean_df)),
            "auroc_raw_cleaned": round(float(roc_auc_score(yc, pc)), 6),
            "accuracy_at_050_raw_cleaned": round(float(accuracy_score(yc, pred_c_raw)), 6),
            "precision_at_050_raw_cleaned": round(float(precision_score(yc, pred_c_raw)), 6),
            "sensitivity_at_050_raw_cleaned": round(float(recall_score(yc, pred_c_raw)), 6),
            "ece_raw_cleaned": round(compute_ece(yc, pc), 6),
            "brier_raw_cleaned": round(float(brier_score_loss(yc, pc)), 6),
            "auroc_post_stratified_recalibration": round(float(roc_auc_score(yc, pc_cal)), 6),
            "accuracy_post_stratified_recalibration": round(float(accuracy_score(yc, pred_c_cal)), 6),
            "sensitivity_post_stratified_recalibration": round(float(recall_score(yc, pred_c_cal)), 6),
            "ece_post_stratified_recalibration": round(compute_ece(yc, pc_cal), 6),
            "brier_post_stratified_recalibration": round(float(brier_score_loss(yc, pc_cal)), 6),
        },
    }

    return {
        "total_patients": n_total,
        "aggregate_auroc": round(float(roc_auc_score(df["sepsis_ground_truth"], df["ai_risk_score"])), 6),
        "aggregate_mortality_30d_auroc": round(float(roc_auc_score(df["mortality_30d"], df["ai_risk_score"])), 6),
        "simpsons_paradox_and_hosp_c_throttling": simpsons_block,
        "immunocompromised_anc_lt_500": imm_block,
        "ood_procalcitonin_abstention": ood_block,
    }


if __name__ == "__main__":
    out_path = OUT_DIR / "metrics.json"
    out_path.write_text(json.dumps(analyze_cohort(COHORT_CSV), indent=2) + "\n", encoding="utf-8")
    print(f"Verified metrics written to {out_path}")
