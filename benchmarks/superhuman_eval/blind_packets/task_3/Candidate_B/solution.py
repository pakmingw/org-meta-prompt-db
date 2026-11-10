#!/usr/bin/env python3
"""Multi-Hospital ICU Sepsis AI Failure Diagnosis, Subgroup Recalibration & OOD Abstention."""

import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.special import logit
from scipy.stats import chi2_contingency, fisher_exact
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedKFold

COHORT_PATH = Path("/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/benchmarks/superhuman_eval/tasks/task3_clinical_sepsis/sepsis_cohort.csv")
OUT_METRICS_PATH = Path(__file__).resolve().parent / "metrics.json"


def expected_calibration_error(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece, n = 0.0, len(y_true)
    for i in range(n_bins):
        mask = (y_prob >= bins[i]) & (y_prob <= bins[i + 1] if i == n_bins - 1 else y_prob < bins[i + 1])
        if np.any(mask):
            ece += (np.sum(mask) / n) * abs(float(np.mean(y_true[mask])) - float(np.mean(y_prob[mask])))
    return float(ece)


def net_benefit(y_true: np.ndarray, pred_pos: np.ndarray, pt: float) -> float:
    n = len(y_true)
    tp = float(np.sum((pred_pos == 1) & (y_true == 1)))
    fp = float(np.sum((pred_pos == 1) & (y_true == 0)))
    return (tp / n) - (fp / n) * (pt / (1.0 - pt))


def wilson_ci(k: int, n: int, z: float = 1.959964) -> list[float]:
    p, denom = k / n, 1.0 + (z**2) / n
    center = (p + (z**2) / (2.0 * n)) / denom
    half = (z * np.sqrt((p * (1.0 - p) + (z**2) / (4.0 * n)) / n)) / denom
    return [round(max(0.0, center - half), 6), round(min(1.0, center + half), 6)]


def mantel_haenszel_rd(df: pd.DataFrame, treat_col: str, outcome_col: str, strata_cols: list[str]) -> dict:
    rd_num = rd_den = or_num = or_den = 0.0
    for _, g in df.groupby(strata_cols):
        t1, t0 = g[g[treat_col] == 1], g[g[treat_col] == 0]
        n1, n0 = len(t1), len(t0)
        if n1 == 0 or n0 == 0:
            continue
        a, c = float(t1[outcome_col].sum()), float(t0[outcome_col].sum())
        n_s, w = n1 + n0, (n1 * n0) / (n1 + n0)
        rd_num += w * ((a / n1) - (c / n0))
        rd_den += w
        or_num += (a * (n0 - c)) / n_s
        or_den += ((n1 - a) * c) / n_s
    return {"mh_adjusted_risk_difference": round(rd_num / rd_den, 6), "mh_common_odds_ratio": round(or_num / or_den, 6)}


def classification_summary(y_true: np.ndarray, y_prob: np.ndarray, threshold: float | np.ndarray = 0.50) -> dict:
    pred = (y_prob >= threshold).astype(int)
    tp, fn = int(np.sum((pred == 1) & (y_true == 1))), int(np.sum((pred == 0) & (y_true == 1)))
    fp, tn = int(np.sum((pred == 1) & (y_true == 0))), int(np.sum((pred == 0) & (y_true == 0)))
    return {
        "auroc": round(float(roc_auc_score(y_true, y_prob)), 6), "accuracy": round(float(accuracy_score(y_true, pred)), 6),
        "ece_10bin": round(expected_calibration_error(y_true, y_prob, 10), 6), "brier_score": round(float(brier_score_loss(y_true, y_prob)), 6),
        "fn_rate": round(fn / (tp + fn), 6), "fp_rate": round(fp / (fp + tn), 6),
        "ppv": round(tp / (tp + fp), 6) if (tp + fp) else 0.0, "npv": round(tn / (tn + fn), 6) if (tn + fn) else 0.0,
        "tp": tp, "fn": fn, "fp": fp, "tn": tn,
    }


def main() -> None:
    df = pd.read_csv(COHORT_PATH)
    y_all, p_all = df["sepsis_ground_truth"].to_numpy(), df["ai_risk_score"].to_numpy()

    # 1. HOSP_C High-Occupancy Alert Throttling & Simpson's Paradox
    hosp_c = df[df["hospital_id"] == "HOSP_C"]
    hc_hi_pos = hosp_c[(hosp_c["icu_occupancy_pct"] > 85.0) & (hosp_c["ai_risk_score"] >= 0.50)]
    hc_lo_pos = hosp_c[(hosp_c["icu_occupancy_pct"] <= 85.0) & (hosp_c["ai_risk_score"] >= 0.50)]
    other_hi_pos = df[(df["hospital_id"] != "HOSP_C") & (df["icu_occupancy_pct"] > 85.0) & (df["ai_risk_score"] >= 0.50)]
    suppressed_n, n_hc_hi_pos = int((hc_hi_pos["alert_delivered"] == 0).sum()), int(len(hc_hi_pos))

    al1, al0 = df[df["alert_delivered"] == 1], df[df["alert_delivered"] == 0]
    pos_df = df[df["ai_risk_score"] >= 0.50]
    pos_al1, pos_al0 = pos_df[pos_df["alert_delivered"] == 1], pos_df[pos_df["alert_delivered"] == 0]
    _, p_fisher_pos = fisher_exact([[int(pos_al1["mortality_30d"].sum()), int(len(pos_al1) - pos_al1["mortality_30d"].sum())],
                                    [int(pos_al0["mortality_30d"].sum()), int(len(pos_al0) - pos_al0["mortality_30d"].sum())]])

    abx1, abx0 = df[df["early_antibiotics"] == 1], df[df["early_antibiotics"] == 0]
    sep_df = df[df["sepsis_ground_truth"] == 1]
    sep_abx1, sep_abx0 = sep_df[sep_df["early_antibiotics"] == 1], sep_df[sep_df["early_antibiotics"] == 0]
    _, p_abx_unadj, _, _ = chi2_contingency([[int(abx1["mortality_30d"].sum()), int(len(abx1) - abx1["mortality_30d"].sum())],
                                             [int(abx0["mortality_30d"].sum()), int(len(abx0) - abx0["mortality_30d"].sum())]])
    _, p_abx_sep, _, _ = chi2_contingency([[int(sep_abx1["mortality_30d"].sum()), int(len(sep_abx1) - sep_abx1["mortality_30d"].sum())],
                                           [int(sep_abx0["mortality_30d"].sum()), int(len(sep_abx0) - sep_abx0["mortality_30d"].sum())]])
    mh_abx = mantel_haenszel_rd(df, "early_antibiotics", "mortality_30d", ["sepsis_ground_truth", "immunocompromised", "hospital_id"])
    mh_alert = mantel_haenszel_rd(pos_df, "alert_delivered", "mortality_30d", ["sepsis_ground_truth", "immunocompromised"])

    # 2. Immunocompromised Neutropenic Subgroup (anc_cells_ul < 500) Recalibration & DCA
    imm = df[df["anc_cells_ul"] < 500].copy().reset_index(drop=True)
    y_imm, p_imm = imm["sepsis_ground_truth"].to_numpy(), imm["ai_risk_score"].to_numpy()
    pre_imm = classification_summary(y_imm, p_imm, 0.50)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    oof_imm = np.zeros_like(p_imm)
    for tr_i, va_i in skf.split(p_imm.reshape(-1, 1), y_imm):
        oof_imm[va_i] = LogisticRegression(C=1e6).fit(p_imm[tr_i].reshape(-1, 1), y_imm[tr_i]).predict_proba(p_imm[va_i].reshape(-1, 1))[:, 1]

    cal_full = LogisticRegression(C=1e6).fit(p_imm.reshape(-1, 1), y_imm)
    platt_a, platt_b = float(cal_full.intercept_[0]), float(cal_full.coef_[0, 0])
    cal_th = 0.30
    fpr_a, tpr_a, th_a = roc_curve(y_imm, p_imm)
    post_imm_p30, post_imm_p50 = classification_summary(y_imm, oof_imm, cal_th), classification_summary(y_imm, oof_imm, 0.50)

    nb_pre_050_p30 = net_benefit(y_imm, (p_imm >= 0.50).astype(int), cal_th)
    nb_pre_raw_p30 = net_benefit(y_imm, (p_imm >= cal_th).astype(int), cal_th)
    nb_all_p30, nb_post_p30 = net_benefit(y_imm, np.ones_like(y_imm), cal_th), net_benefit(y_imm, (oof_imm >= cal_th).astype(int), cal_th)
    nb_pre_050_p50 = net_benefit(y_imm, (p_imm >= 0.50).astype(int), 0.50)
    nb_all_p50, nb_post_p50 = net_benefit(y_imm, np.ones_like(y_imm), 0.50), net_benefit(y_imm, (oof_imm >= 0.50).astype(int), 0.50)

    # 3. OOD Procalcitonin Assay Drift Gate & Cleaned Cohort Performance
    ood_mask = (df["procalcitonin_ng_ml"] > 12.0) | (df["analyzer_lot"] != "PCT_LOT_STD_04")
    ood_df, clean_df = df[ood_mask], df[~ood_mask].copy().reset_index(drop=True)
    oof_clean = np.zeros(len(clean_df))
    imm_clean_flag = (clean_df["anc_cells_ul"] < 500).to_numpy()
    for flag in (False, True):
        idx = np.where(imm_clean_flag == flag)[0]
        y_s, p_s = clean_df.loc[idx, "sepsis_ground_truth"].to_numpy(), clean_df.loc[idx, "ai_risk_score"].to_numpy().reshape(-1, 1)
        for tr_i, va_i in skf.split(p_s, y_s):
            oof_clean[idx[va_i]] = LogisticRegression(C=1e6).fit(p_s[tr_i], y_s[tr_i]).predict_proba(p_s[va_i])[:, 1]

    ood_fp = int(((ood_df["ai_risk_score"] >= 0.50) & (ood_df["sepsis_ground_truth"] == 0)).sum())
    all_fp = int(((p_all >= 0.50) & (y_all == 0)).sum())

    metrics = {
        "total_patients": int(len(df)),
        "aggregate_auroc": round(float(roc_auc_score(y_all, p_all)), 6),
        "aggregate_baseline_at_050": classification_summary(y_all, p_all, 0.50),
        "simpsons_paradox_and_hosp_c_throttling": {
            "hosp_c_high_occupancy_threshold_pct": 85.0, "hosp_c_high_occupancy_total_n": int((hosp_c["icu_occupancy_pct"] > 85.0).sum()),
            "hosp_c_high_occupancy_ai_pos_n": n_hc_hi_pos, "hosp_c_high_occupancy_alerts_suppressed_n": suppressed_n,
            "hosp_c_high_occupancy_alert_suppression_rate": round(suppressed_n / n_hc_hi_pos, 6),
            "hosp_c_high_occupancy_suppression_95ci": wilson_ci(suppressed_n, n_hc_hi_pos),
            "hosp_c_low_occupancy_alert_suppression_rate": round(float((hc_lo_pos["alert_delivered"] == 0).mean()), 6),
            "other_hospitals_high_occupancy_alert_suppression_rate": round(float((other_hi_pos["alert_delivered"] == 0).mean()), 6),
            "hosp_c_ai_pos_early_antibiotics_low_vs_high_occ": {
                "low_occ_le_85_rate": round(float(hc_lo_pos["early_antibiotics"].mean()), 6),
                "high_occ_gt_85_rate": round(float(hc_hi_pos["early_antibiotics"].mean()), 6),
                "absolute_treatment_drop": round(float(hc_hi_pos["early_antibiotics"].mean() - hc_lo_pos["early_antibiotics"].mean()), 6),
            },
            "alert_delivery_mortality_paradox": {
                "unadjusted_alerted_mortality": round(float(al1["mortality_30d"].mean()), 6),
                "unadjusted_unalerted_mortality": round(float(al0["mortality_30d"].mean()), 6),
                "unadjusted_risk_difference": round(float(al1["mortality_30d"].mean() - al0["mortality_30d"].mean()), 6),
                "stratified_ai_pos_alerted_mortality": round(float(pos_al1["mortality_30d"].mean()), 6),
                "stratified_ai_pos_throttled_mortality": round(float(pos_al0["mortality_30d"].mean()), 6),
                "stratified_ai_pos_risk_difference": round(float(pos_al1["mortality_30d"].mean() - pos_al0["mortality_30d"].mean()), 6),
                "stratified_ai_pos_fisher_p_value": round(float(p_fisher_pos), 8), **mh_alert,
            },
            "early_antibiotics_treatment_effect": {
                "unadjusted_treated_mortality": round(float(abx1["mortality_30d"].mean()), 6),
                "unadjusted_untreated_mortality": round(float(abx0["mortality_30d"].mean()), 6),
                "unadjusted_risk_difference": round(float(abx1["mortality_30d"].mean() - abx0["mortality_30d"].mean()), 6),
                "unadjusted_chi2_p_value": round(float(p_abx_unadj), 6),
                "sepsis_positive_treated_mortality": round(float(sep_abx1["mortality_30d"].mean()), 6),
                "sepsis_positive_untreated_mortality": round(float(sep_abx0["mortality_30d"].mean()), 6),
                "sepsis_positive_absolute_risk_reduction": round(float(sep_abx1["mortality_30d"].mean() - sep_abx0["mortality_30d"].mean()), 6),
                "sepsis_positive_chi2_p_value": float(f"{p_abx_sep:.4e}"),
                "immunocompromised_sepsis_treated_mortality": round(float(imm[(imm["sepsis_ground_truth"] == 1) & (imm["early_antibiotics"] == 1)]["mortality_30d"].mean()), 6),
                "immunocompromised_sepsis_untreated_mortality": round(float(imm[(imm["sepsis_ground_truth"] == 1) & (imm["early_antibiotics"] == 0)]["mortality_30d"].mean()), 6),
                **mh_abx,
            },
        },
        "immunocompromised_anc_lt_500": {
            "n": int(len(imm)), "sepsis_cases": int(y_imm.sum()), "sepsis_prevalence": round(float(y_imm.mean()), 6),
            "subgroup_auroc": pre_imm["auroc"],
            "afebrile_lactatemia_physiology": {
                "septic_mean_temp_c": round(float(imm[y_imm == 1]["temperature_c"].mean()), 4),
                "septic_mean_lactate_mmol_l": round(float(imm[y_imm == 1]["lactate_mmol_l"].mean()), 4),
                "septic_mean_raw_ai_score": round(float(p_imm[y_imm == 1].mean()), 4),
                "immunocompetent_septic_mean_temp_c": round(float(df[(df["anc_cells_ul"] >= 500) & (df["sepsis_ground_truth"] == 1)]["temperature_c"].mean()), 4),
            },
            "pre_recalibration_fn_rate": pre_imm["fn_rate"], "pre_recalibration_ece": pre_imm["ece_10bin"],
            "pre_recalibration_brier": pre_imm["brier_score"],
            "platt_scaling_params": {"intercept": round(platt_a, 6), "slope": round(platt_b, 6)},
            "calibrated_subgroup_threshold": cal_th,
            "equivalent_raw_score_threshold_at_p30": round(float((logit(cal_th) - platt_a) / platt_b), 6),
            "equivalent_raw_score_threshold_at_p50": round(float(-platt_a / platt_b), 6),
            "youden_optimal_raw_score_threshold": round(float(th_a[int(np.argmax(tpr_a - fpr_a))]), 6),
            "post_recalibration_fn_rate": post_imm_p30["fn_rate"], "post_recalibration_fp_rate": post_imm_p30["fp_rate"],
            "post_recalibration_ece": post_imm_p30["ece_10bin"], "post_recalibration_brier": post_imm_p30["brier_score"],
            "post_recalibration_fn_rate_at_p50": post_imm_p50["fn_rate"],
            "decision_curve_net_benefit_uplift": round(nb_post_p30 - nb_pre_050_p30, 6),
            "decision_curve_analysis": {
                "at_pt_030": {
                    "pre_deployed_050_nb": round(nb_pre_050_p30, 6), "pre_uncalibrated_p30_nb": round(nb_pre_raw_p30, 6),
                    "treat_all_nb": round(nb_all_p30, 6), "post_recalibrated_nb": round(nb_post_p30, 6),
                    "uplift_vs_deployed_050": round(nb_post_p30 - nb_pre_050_p30, 6),
                    "uplift_vs_uncalibrated_p30": round(nb_post_p30 - nb_pre_raw_p30, 6),
                    "uplift_vs_treat_all": round(nb_post_p30 - nb_all_p30, 6),
                },
                "at_pt_050": {
                    "pre_deployed_050_nb": round(nb_pre_050_p50, 6), "treat_all_nb": round(nb_all_p50, 6),
                    "post_recalibrated_nb": round(nb_post_p50, 6), "uplift_vs_deployed_050": round(nb_post_p50 - nb_pre_050_p50, 6),
                },
            },
        },
        "ood_procalcitonin_abstention": {
            "detected_ood_count": int(ood_mask.sum()), "detected_ood_fraction": round(float(ood_mask.mean()), 6),
            "lot_and_pct_gt_12_perfect_concordance": bool(((df["procalcitonin_ng_ml"] > 12.0) == (df["analyzer_lot"] == "PCT_LOT_DRIFT_X9")).all()),
            "abstention_gate_rule": "ABSTAIN_TO_CLINICIAN_HITL if procalcitonin_ng_ml > 12.0 OR analyzer_lot != 'PCT_LOT_STD_04'; suppress autonomous AI risk score/alert, display OOD assay-drift warning, and order stat repeat PCT/lactate.",
            "ood_subset_diagnostics": {
                "mean_procalcitonin_ng_ml": round(float(ood_df["procalcitonin_ng_ml"].mean()), 4), "min_procalcitonin_ng_ml": round(float(ood_df["procalcitonin_ng_ml"].min()), 4),
                "mean_ai_risk_score": round(float(ood_df["ai_risk_score"].mean()), 6), "min_ai_risk_score": round(float(ood_df["ai_risk_score"].min()), 6),
                "true_sepsis_prevalence": round(float(ood_df["sepsis_ground_truth"].mean()), 6),
                "false_positive_alerts_generated": ood_fp, "share_of_all_cohort_false_positives": round(ood_fp / all_fp, 6),
            },
            "cleaned_cohort_n": int(len(clean_df)),
            "cleaned_cohort_raw_score_metrics": classification_summary(clean_df["sepsis_ground_truth"].to_numpy(), clean_df["ai_risk_score"].to_numpy(), 0.50),
            "cleaned_cohort_stratified_recalibrated_at_050": classification_summary(clean_df["sepsis_ground_truth"].to_numpy(), oof_clean, 0.50),
            "cleaned_cohort_stratified_recalibrated_cost_sensitive": classification_summary(clean_df["sepsis_ground_truth"].to_numpy(), oof_clean, np.where(imm_clean_flag, cal_th, 0.50)),
        },
    }
    OUT_METRICS_PATH.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_METRICS_PATH} ({len(df)} rows analyzed).")


if __name__ == "__main__":
    main()
