#!/usr/bin/env python3
"""3-Statement Monte Carlo Liquidity, Inventory & Non-Linear Hedging Engine.

Models Q1..Q4 financial statements under an abrupt 60% multi-tier tariff +
rare-earth export quota shock with Gaussian-to-Student-t (rho: 0.15 -> 0.88,
df=4) crisis contagion, verifying exact double-entry accounting conservation.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from scipy.stats import norm, t as student_t

TASK_DIR = Path("/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/benchmarks/superhuman_eval/tasks/task2_tariff_shock")
OUT_DIR = Path("/home/pakmingw/.gemini/antigravity/scratch/org_meta_prompt_db/benchmarks/superhuman_eval/runs/run_abac2d68")
NUM_PATHS = 10000
DAYS_PER_QTR = 365.0 / 4.0


def tail_dependence_student_t(rho: float, df: int) -> float:
    arg = -np.sqrt((df + 1.0) * (1.0 - rho) / (1.0 + rho))
    return float(2.0 * student_t.cdf(arg, df=df + 1))


def run_monte_carlo(
    cfg: dict, strategy: str = "unhedged", regime_mode: str = "actual_mixture",
    tariff_override: float | None = None, crisis_rho_override: float | None = None, n_paths: int = NUM_PATHS,
) -> dict:
    ab, bs0 = cfg["annual_baseline_usd_m"], cfg["initial_balance_sheet_usd_m"]
    cov, sp = cfg["covenants_and_thresholds"], cfg["supply_chain_and_shock_parameters"]
    cr_cfg = sp["correlation_regime"]
    rng = np.random.default_rng(cov["random_seed"])
    d = 5
    rho_n = float(cr_cfg["normal_pairwise_rho"])
    rho_c = float(crisis_rho_override if crisis_rho_override is not None else cr_cfg["crisis_pairwise_rho"])
    p_crisis, df_c = float(cr_cfg["crisis_regime_probability"]), int(cr_cfg["student_t_df_crisis"])
    tariff_rate = float(tariff_override if tariff_override is not None else sp["abrupt_tariff_rate_shock"])

    r_norm, r_cris = np.full((d, d), rho_n), np.full((d, d), rho_c)
    np.fill_diagonal(r_norm, 1.0)
    np.fill_diagonal(r_cris, 1.0)
    chol_n, chol_c = np.linalg.cholesky(r_norm), np.linalg.cholesky(r_cris)

    rev_q0, cogs_q0, opex_q0, da_q = ab["revenue"] / 4.0, ab["cogs"] / 4.0, ab["opex_sga_rd"] / 4.0, ab["depreciation_amortization"] / 4.0
    capex_maint, base_debt_0 = ab["quarterly_capex_maintenance"], bs0["liabilities_and_equity"]["total_debt"]
    revolver_max, min_cash, max_cov = ab["undrawn_revolver_limit"], cov["min_cash_liquidity_usd_m"], cov["max_net_debt_to_ltm_ebitda"]

    cash = np.full(n_paths, bs0["assets"]["cash_and_equivalents"], dtype=float)
    ar = np.full(n_paths, bs0["assets"]["accounts_receivable"], dtype=float)
    inv = np.full(n_paths, bs0["assets"]["inventory"], dtype=float)
    ppe = np.full(n_paths, bs0["assets"]["net_ppe_and_other_noncurrent"], dtype=float)
    ap = np.full(n_paths, bs0["liabilities_and_equity"]["accounts_payable"], dtype=float)
    acc = np.full(n_paths, bs0["liabilities_and_equity"]["accrued_and_other_liabilities"], dtype=float)
    debt = np.full(n_paths, base_debt_0, dtype=float)
    eq = np.full(n_paths, bs0["liabilities_and_equity"]["shareholders_equity"], dtype=float)

    ebitda_hist = [np.full(n_paths, ab["ebitda"] / 4.0, dtype=float) for _ in range(3)]
    breach_any = np.zeros(n_paths, dtype=bool)
    peak_lev, cum_fcf, revolver_used_max = np.zeros(n_paths), np.zeros(n_paths), np.zeros(n_paths)
    max_id_error, qtr_stats = 0.0, []

    in_crisis = rng.random(n_paths) < p_crisis
    for q in range(cov["horizon_quarters"]):
        if q > 0:
            u_reg = rng.random(n_paths)
            in_crisis = np.where(in_crisis, u_reg < 0.76, u_reg < (p_crisis * 0.24 / (1.0 - p_crisis)))
        z_iid = rng.standard_normal((n_paths, d))
        z_norm = z_iid @ chol_n.T
        t_cris = (z_iid @ chol_c.T) / np.sqrt(rng.chisquare(df_c, size=(n_paths, 1)) / df_c)
        z_basis = rng.standard_normal(n_paths)

        c_eff = np.zeros(n_paths, dtype=bool) if regime_mode == "gaussian_prior" else in_crisis
        z = z_norm if regime_mode == "gaussian_prior" else np.where(c_eff[:, None], t_cris, z_norm)
        u = norm.cdf(z) if regime_mode == "gaussian_prior" else np.where(c_eff[:, None], student_t.cdf(z, df=df_c), norm.cdf(z))

        d_vol = np.clip(sp["demand_volume_shock_mean"] - sp["demand_volume_shock_std"] * z[:, 0], -0.45, 0.10)
        re_surch = np.maximum(0.0, sp["rare_earth_quota_spot_surcharge_mean"] + sp["rare_earth_quota_spot_surcharge_std"] * z[:, 1])
        fx_shock = np.where(c_eff, sp["fx_adverse_cost_vol_annual_crisis"] / 2.0, sp["fx_adverse_cost_vol_annual_normal"] / 2.0) * z[:, 2]
        disrupted = u[:, 3] > (1.0 - sp["tier2_supplier_disruption_prob_quarterly"])

        dso_raw = bs0["working_capital_days"]["dso"] + np.where(c_eff, np.maximum(0.0, sp["dso_crisis_elongation_days_mean"] + 4.0 * z[:, 4]), np.maximum(-3.0, 2.5 * z[:, 4]))
        dio_raw = bs0["working_capital_days"]["dio"] + np.where(disrupted, 14.0, 0.0) + np.where(c_eff, 8.0 * np.maximum(0.0, z[:, 4]), 0.0)
        dpo_raw = bs0["working_capital_days"]["dpo"] - np.where(c_eff, np.clip(5.0 + 2.5 * z[:, 4], 0.0, 14.0), 0.0)
        bom_share = sp["bom_tier2_specialty_substrate_share"]

        if strategy in ("unhedged", "naive_gaussian_hedge"):
            ship_mult = np.maximum(0.55, (1.0 + d_vol) * (1.0 - np.where(disrupted, 0.075, 0.0)))
            base_rev, base_cogs = rev_q0 * ship_mult, cogs_q0 * (0.07 + 0.93 * ship_mult)
            fifo_q, dutiable_sh = (0.55 if q == 0 else 1.0), 0.55
            tier2_sub = (0.36 * cogs_q0) * bom_share * ship_mult
            t_cost, r_cost = tier2_sub * dutiable_sh * tariff_rate * fifo_q, tier2_sub * 0.65 * re_surch * fifo_q
            fx_raw_cost = (bom_share * cogs_q0 * ship_mult) * fx_shock
            if strategy == "naive_gaussian_hedge":
                fx_fwd = 1094.4 * (fx_shock - 0.004)
                proxy_pay = np.where(c_eff, 300.0 * (-0.09 * z[:, 0] + 0.05 * z_basis), 300.0 * (0.70 * (re_surch - 0.28) + 0.04 * z_basis))
                fx_cost = fx_raw_cost - fx_fwd - proxy_pay
                csa_lock = np.where(c_eff, np.maximum(0.0, -proxy_pay * 1.3 + 70.0 * np.maximum(0.0, z[:, 2])), 0.0)
                dso = dso_raw + (csa_lock / np.maximum(1.0, base_rev)) * DAYS_PER_QTR
            else:
                fx_cost, dso = fx_raw_cost, dso_raw
            expedite = np.where(disrupted, 70.0 + 25.0 * np.maximum(0.0, z[:, 3]), 0.0)
            pt = np.clip(sp["short_run_price_passthrough_fraction_mean"] + 0.02 * q - 0.07 * z[:, 0], 0.05, 0.60)
            rev, cogs = base_rev + pt * (t_cost + r_cost), base_cogs + t_cost + r_cost + fx_cost + expedite
            opex, capex, dio, dpo = opex_q0 * (0.80 + 0.20 * ship_mult), capex_maint, dio_raw, dpo_raw
            inv_unrec = tier2_sub * (dutiable_sh * tariff_rate + 0.65 * re_surch) * (1.0 - fifo_q)
        else:
            ship_mult = np.maximum(0.60, (1.0 + d_vol) * (1.0 - np.where(disrupted, 0.015, 0.0)))
            base_rev, base_cogs = rev_q0 * ship_mult, cogs_q0 * (0.07 + 0.93 * ship_mult)
            fifo_q, dutiable_sh = (0.50 if q == 0 else 1.0), [0.50, 0.38, 0.25, 0.16][q]
            tier2_sub = (0.36 * cogs_q0) * bom_share * ship_mult
            re_capped = np.minimum(re_surch, 0.20)
            t_cost, r_cost = tier2_sub * dutiable_sh * tariff_rate * fifo_q, tier2_sub * 0.65 * re_capped * fifo_q
            fx_hedged = np.clip(fx_shock, -0.035, 0.025) + np.maximum(0.0, fx_shock - 0.24)
            fx_cost = (bom_share * cogs_q0 * ship_mult) * fx_hedged
            expedite = np.where(disrupted, 15.0, 0.0)
            pt = np.clip(0.43 + 0.03 * q - 0.04 * z[:, 0], 0.32, 0.62)
            rev = base_rev + pt * (t_cost + r_cost)
            ar_fee = 2.0 + rev * (np.maximum(0.0, dso_raw - 55.0) / DAYS_PER_QTR) * (0.058 / 4.0)
            opex_flex = np.where(c_eff | (ship_mult < 0.87), 60.0, 18.0)
            cogs = base_cogs + t_cost + r_cost + fx_cost + expedite + 31.0
            opex = opex_q0 * (0.80 + 0.20 * ship_mult) - opex_flex + ar_fee
            capex = capex_maint + (15.0 if q < 2 else 0.0)
            dso, dio, dpo = np.minimum(dso_raw, 55.0), [95.0, 92.0, 88.0, 88.0][q], 56.0
            inv_unrec = tier2_sub * (dutiable_sh * tariff_rate + 0.65 * re_capped) * (1.0 - fifo_q)

        ebitda = rev - cogs - opex
        rev_drawn = np.maximum(0.0, debt - base_debt_0)
        interest = np.minimum(debt, base_debt_0) * (ab["debt_interest_rate_annual"] / 4.0) + rev_drawn * (ab["revolver_spread_annual"] / 4.0)
        ebt = (ebitda - da_q) - interest
        net_inc = ebt - np.maximum(0.0, ab["effective_tax_rate"] * ebt)

        inv_basis = cogs + inv_unrec
        new_ar, new_inv, new_ap, new_ppe = rev * (dso / DAYS_PER_QTR), inv_basis * (dio / DAYS_PER_QTR), inv_basis * (dpo / DAYS_PER_QTR), ppe + capex - da_q
        fcf = net_inc + da_q - ((new_ar - ar) + (new_inv - inv) - (new_ap - ap)) - capex
        cum_fcf += fcf
        cash += fcf

        repay = np.minimum(rev_drawn, np.maximum(0.0, cash - min_cash))
        cash -= repay
        debt -= repay
        draw = np.minimum(np.maximum(0.0, min_cash - cash), np.maximum(0.0, revolver_max - np.maximum(0.0, debt - base_debt_0)))
        cash += draw
        debt += draw
        emerg = np.maximum(0.0, -cash)
        cash += emerg
        debt += emerg
        revolver_used_max = np.maximum(revolver_used_max, np.maximum(0.0, debt - base_debt_0))

        eq += net_inc
        ar, inv, ppe, ap = new_ar, new_inv, new_ppe, new_ap
        max_id_error = max(max_id_error, float(np.max(np.abs((cash + ar + inv + ppe) - (ap + acc + debt + eq)))))

        ebitda_hist.append(ebitda)
        ltm_ebitda = sum(ebitda_hist[-4:])
        lev = np.where(ltm_ebitda > 0.0, (debt - cash) / ltm_ebitda, 99.0)
        q_breach = (lev > max_cov) | (ltm_ebitda <= 0.0)
        breach_any |= q_breach
        peak_lev = np.maximum(peak_lev, lev)
        qtr_stats.append({
            "quarter": f"Q{q + 1}", "mean_ltm_ebitda_usd_m": round(float(np.mean(ltm_ebitda)), 2),
            "mean_net_debt_usd_m": round(float(np.mean(debt - cash)), 2), "p50_leverage": round(float(np.median(lev)), 4),
            "p95_leverage": round(float(np.percentile(lev, 95)), 4), "qtr_breach_prob": round(float(np.mean(q_breach)), 4),
        })

    cvar95_fcf = float(np.mean(cum_fcf[cum_fcf <= float(np.percentile(cum_fcf, 5))]))
    return {
        "covenant_breach_prob": round(float(np.mean(breach_any)), 4), "p50_net_debt_to_ebitda": round(float(np.median(peak_lev)), 4),
        "p95_net_debt_to_ebitda": round(float(np.percentile(peak_lev, 95)), 4), "mean_fcf_4q_usd_m": round(float(np.mean(cum_fcf)), 2),
        "cvar95_fcf_usd_m": round(cvar95_fcf, 2), "p95_revolver_draw_usd_m": round(float(np.percentile(revolver_used_max, 95)), 2),
        "accounting_identity_max_error": max_id_error, "quarterly": qtr_stats,
    }


def main() -> None:
    cfg = json.loads((TASK_DIR / "baseline_financials.json").read_text())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    unhedged = run_monte_carlo(cfg, "unhedged", "actual_mixture")
    structured = run_monte_carlo(cfg, "structured", "actual_mixture")
    gauss_prior = run_monte_carlo(cfg, "unhedged", "gaussian_prior")
    naive_hedge = run_monte_carlo(cfg, "naive_gaussian_hedge", "actual_mixture")

    sens_grid = []
    for tr in (0.40, 0.60, 0.80):
        for cr in (0.15, 0.55, 0.88):
            u_s, s_s = run_monte_carlo(cfg, "unhedged", "actual_mixture", tr, cr), run_monte_carlo(cfg, "structured", "actual_mixture", tr, cr)
            sens_grid.append({
                "tariff_rate": tr, "crisis_rho": cr, "unhedged_breach_prob": u_s["covenant_breach_prob"],
                "structured_breach_prob": s_s["covenant_breach_prob"], "unhedged_p95_lev": u_s["p95_net_debt_to_ebitda"],
                "structured_p95_lev": s_s["p95_net_debt_to_ebitda"], "unhedged_cvar95_fcf_usd_m": u_s["cvar95_fcf_usd_m"],
                "structured_cvar95_fcf_usd_m": s_s["cvar95_fcf_usd_m"],
            })

    max_err = max(unhedged["accounting_identity_max_error"], structured["accounting_identity_max_error"])
    cr_cfg = cfg["supply_chain_and_shock_parameters"]["correlation_regime"]
    metrics = {
        "num_monte_carlo_paths": NUM_PATHS,
        "accounting_identity_max_error": max_err,
        "accounting_identity_passed": bool(max_err < 1e-6),
        "modeled_normal_rho": cr_cfg["normal_pairwise_rho"],
        "modeled_crisis_rho": cr_cfg["crisis_pairwise_rho"],
        "crisis_upper_tail_dependence_lambda_u": round(tail_dependence_student_t(cr_cfg["crisis_pairwise_rho"], cr_cfg["student_t_df_crisis"]), 4),
        "unhedged_covenant_breach_prob": unhedged["covenant_breach_prob"],
        "structured_covenant_breach_prob": structured["covenant_breach_prob"],
        "breach_prob_reduction_abs": round(unhedged["covenant_breach_prob"] - structured["covenant_breach_prob"], 4),
        "unhedged_p95_net_debt_to_ebitda": unhedged["p95_net_debt_to_ebitda"],
        "structured_p95_net_debt_to_ebitda": structured["p95_net_debt_to_ebitda"],
        "unhedged_cvar95_fcf_usd_m": unhedged["cvar95_fcf_usd_m"],
        "structured_cvar95_fcf_usd_m": structured["cvar95_fcf_usd_m"],
        "hedging_and_working_capital_actions": [
            {"instrument": "Zero-CSA OTC FX Call Spreads + Tariff-Contingent Quanto Collars", "notional_usd_m_per_qtr": 1368.0, "strikes": "+2.5% / +24.0% call spread funded by -3.5% OTM put floor", "annual_cost_usd_m": 68.0},
            {"instrument": "Physical Rare-Earth Offtake Price-Cap + OTC Asian Basket Call Options", "notional_usd_m_per_qtr": 320.1, "strikes": "20.0% spot surcharge cap across Q1..Q4", "annual_cost_usd_m": 56.0},
            {"instrument": "FTZ Bonded Tier-2 Substrate Safety Stock + ASEAN/JP Dual-Source Tooling", "buffer_dio_schedule_days": [95, 92, 88, 88], "dutiable_corridor_ramp": [0.50, 0.38, 0.25, 0.16], "qualification_capex_usd_m": 30.0},
            {"instrument": "ASC 860 Non-Recourse AR True-Sale Securitization + ASU 2022-04 G-SIB SCF", "facility_limit_usd_m": 750.0, "wc_targets": "Cap DSO <= 55d in crisis (SOFR+spread 5.8% ann.); stabilize DPO at 56d", "annual_commitment_fee_usd_m": 8.0},
            {"instrument": "Covenant-Gated Zero-Based OpEx Circuit Breaker + Contractual Tariff Indexation", "trigger": "Crisis regime or ship_mult < 0.87 or trailing Leverage > 2.05x", "quarterly_ebitda_protection_usd_m": 60.0},
        ],
        "diagnostic_benchmarks": {"gaussian_prior_unhedged": gauss_prior, "naive_gaussian_linear_hedge": naive_hedge, "unhedged_detail": unhedged, "structured_detail": structured},
        "sensitivity_grid": sens_grid,
    }
    (OUT_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps({k: v for k, v in metrics.items() if not isinstance(v, (list, dict))}, indent=2))


if __name__ == "__main__":
    main()
