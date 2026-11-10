#!/usr/bin/env python3
"""3-Statement Monte Carlo Liquidity, Inventory & Hedging Engine (Task 2)."""

import json
from pathlib import Path
import numpy as np
from scipy import stats


def load_baseline() -> dict:
    base = Path(__file__).resolve().parent
    for p in (base / "baseline_financials.json", base.parent.parent / "tasks" / "task2_tariff_shock" / "baseline_financials.json"):
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    raise FileNotFoundError("baseline_financials.json not found.")


def generate_regime_factors(
    n_paths: int, quarters: int, seed: int, rho_n: float, rho_c: float, p_crisis: float, df_c: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Markov-switching Gaussian (normal) to heavy-tailed Student-t (crisis) factor engine."""
    rng = np.random.default_rng(seed)
    p_cc = 0.70 if 0.0 < p_crisis < 1.0 else (1.0 if p_crisis >= 1.0 else 0.0)
    p_nc = p_crisis * (1.0 - p_cc) / max(1e-9, 1.0 - p_crisis) if p_crisis < 1.0 else 1.0
    crisis = np.zeros((n_paths, quarters), dtype=bool)
    crisis[:, 0] = rng.random(n_paths) < p_crisis
    for q in range(1, quarters):
        crisis[:, q] = np.where(crisis[:, q - 1], rng.random(n_paths) < p_cc, rng.random(n_paths) < p_nc)

    dim = 5
    chol_n = np.linalg.cholesky((1.0 - rho_n) * np.eye(dim) + rho_n * np.ones((dim, dim)))
    chol_c = np.linalg.cholesky((1.0 - rho_c) * np.eye(dim) + rho_c * np.ones((dim, dim)))
    iqr_scale = float(stats.norm.ppf(0.75) / stats.t.ppf(0.75, df=df_c)) if df_c < 100 else 1.0

    z_factors, u_copula = np.zeros((n_paths, quarters, dim)), np.zeros((n_paths, quarters, dim))
    basis_noise = rng.standard_normal((n_paths, quarters))
    for q in range(quarters):
        g_raw = rng.standard_normal((n_paths, dim))
        z_norm = g_raw @ chol_n.T
        if df_c < 100:
            t_raw = (g_raw @ chol_c.T) / np.sqrt(rng.chisquare(df_c, size=(n_paths, 1)) / float(df_c))
            z_cris, u_cris = np.clip(t_raw * iqr_scale, -8.0, 8.0), stats.t.cdf(t_raw, df=df_c)
        else:
            z_cris = g_raw @ chol_c.T
            u_cris = stats.norm.cdf(z_cris)
        c_mask = crisis[:, q]
        z_factors[:, q, :] = np.where(c_mask[:, None], z_cris, z_norm)
        u_copula[:, q, :] = np.where(c_mask[:, None], u_cris, stats.norm.cdf(z_norm))
    return crisis, z_factors, u_copula, basis_noise


def run_three_statement_mc(
    cfg: dict, mode: str, crisis: np.ndarray, z_fac: np.ndarray, u_cop: np.ndarray,
    basis_noise: np.ndarray, tariff_override: float | None = None
) -> dict:
    """Simulate Q1..Q4 integrated Income Statement, Balance Sheet, and Cash Flow Statement."""
    ann, ibs = cfg["annual_baseline_usd_m"], cfg["initial_balance_sheet_usd_m"]
    cov, shk = cfg["covenants_and_thresholds"], cfg["supply_chain_and_shock_parameters"]
    n_paths, quarters, _ = z_fac.shape

    rev_q0, cogs_q0, opex_q0, da_q = ann["revenue"] / 4.0, ann["cogs"] / 4.0, ann["opex_sga_rd"] / 4.0, ann["depreciation_amortization"] / 4.0
    r_debt_q, r_rev_q, tax_rate = ann["debt_interest_rate_annual"] / 4.0, ann["revolver_spread_annual"] / 4.0, ann["effective_tax_rate"]
    capex_base, rev_limit, min_cash, cov_max = ann["quarterly_capex_maintenance"], ann["undrawn_revolver_limit"], cov["min_cash_liquidity_usd_m"], cov["max_net_debt_to_ltm_ebitda"]

    bom_t2 = shk["bom_tier2_specialty_substrate_share"]
    tariff_rate = shk["abrupt_tariff_rate_shock"] if tariff_override is None else tariff_override
    re_mean, re_std = shk["rare_earth_quota_spot_surcharge_mean"], shk["rare_earth_quota_spot_surcharge_std"]
    vol_mean, vol_std, pt_mean = shk["demand_volume_shock_mean"], shk["demand_volume_shock_std"], shk["short_run_price_passthrough_fraction_mean"]
    fx_vn, fx_vc = shk["fx_adverse_cost_vol_annual_normal"], shk["fx_adverse_cost_vol_annual_crisis"]
    p_disrupt_base, dso_elong = shk["tier2_supplier_disruption_prob_quarterly"], shk["dso_crisis_elongation_days_mean"]

    a0, l0, wc0 = ibs["assets"], ibs["liabilities_and_equity"], ibs["working_capital_days"]
    cash, ar, inv, ppe = [np.full(n_paths, a0[k]) for k in ("cash_and_equivalents", "accounts_receivable", "inventory", "net_ppe_and_other_noncurrent")]
    ap, acc, term_debt, equity = [np.full(n_paths, l0[k]) for k in ("accounts_payable", "accrued_and_other_liabilities", "total_debt", "shareholders_equity")]
    rev_debt = np.zeros(n_paths)
    dso0, dio0, dpo0 = wc0["dso"], wc0["dio"], wc0["dpo"]

    ebitda_hist = [np.full(n_paths, ann["ebitda"] / 4.0) for _ in range(4)]
    prev_lev = np.full(n_paths, ann["net_debt_to_ebitda"])
    breach_any, rev_used_any, shortfall_any = np.zeros(n_paths, dtype=bool), np.zeros(n_paths, dtype=bool), np.zeros(n_paths, dtype=bool)
    peak_lev, cum_fcf, max_err, q_stats = np.zeros(n_paths), np.zeros(n_paths), 0.0, []
    cogs_fifo_lag, re_intensity = [0.45, 0.85, 1.00, 1.00], 0.35

    for q in range(quarters):
        c_m = crisis[:, q]
        z1, z2, z3, _, z5 = [z_fac[:, q, i] for i in range(5)]
        if mode == "structured":
            disrupt = u_cop[:, q, 3] > (1.0 - [0.15, 0.13, 0.11, 0.10][q])
            dutiable_share, vol_drag = [0.40, 0.37, 0.32, 0.29][q], -0.008
            pt_frac = np.clip([0.41, 0.44, 0.47, 0.49][q] - 0.035 * z5 - np.where(c_m, 0.02, 0.0), 0.25, 0.60)
        else:
            disrupt = u_cop[:, q, 3] > (1.0 - p_disrupt_base)
            dutiable_share, vol_drag = 0.45, 0.0
            pt_frac = np.clip(pt_mean - 0.06 * z5 - np.where(c_m, 0.05, 0.0), 0.12, 0.58)

        vol_mult = np.clip(1.0 + vol_mean + vol_drag - vol_std * z1 - np.where(disrupt, 0.035, 0.0), 0.58, 1.08)
        re_surcharge = np.maximum(0.0, re_mean + re_std * z2)
        fx_move = (np.where(c_m, fx_vc, fx_vn) / 2.0) * z3
        raw_t2 = bom_t2 * (dutiable_share * tariff_rate + re_intensity * re_surcharge + fx_move + np.where(disrupt, 0.07, 0.0))
        unit_is, unit_repl = 1.0 + cogs_fifo_lag[q] * raw_t2, 1.0 + raw_t2
        cogs_vol = cogs_q0 * vol_mult
        rev = rev_q0 * vol_mult + pt_frac * np.maximum(0.0, cogs_vol * (unit_is - 1.0))

        hedge_pay, opex_prog, fin_fee, csa_days = np.zeros(n_paths), 0.0, 0.0, np.zeros(n_paths)
        if mode == "gaussian_naive":
            fx_pay = 950.0 * np.where(c_m, 0.42 * fx_move + 0.02 * basis_noise[:, q], 0.85 * fx_move)
            lme_pay = 420.0 * np.where(c_m, -0.04 * z1 + 0.03 * basis_noise[:, q], 0.55 * (re_surcharge - 0.22))
            hedge_pay, csa_days = fx_pay + lme_pay - 4.0, np.where(c_m, np.maximum(0.0, 2.5 + 1.2 * z3), 0.0)
        elif mode == "structured":
            fx_col = 950.0 * (np.clip(fx_move - 0.025, 0.0, 0.16) - np.maximum(0.0, -fx_move - 0.045))
            re_spr = 430.0 * 0.85 * np.clip(re_surcharge - 0.20, 0.0, 0.55)
            corridor = np.where((z2 > 0.80) & (z3 > 0.80), np.clip(35.0 + 22.0 * (0.5 * (z2 + z3) - 0.80), 0.0, 85.0), 0.0)
            hedge_pay, opex_prog, fin_fee = fx_col + re_spr + corridor - 24.5, 16.5, 12.0

        cogs_is, cogs_repl = np.maximum(1000.0, cogs_vol * unit_is - hedge_pay), np.maximum(1500.0, cogs_vol * unit_repl)
        ebitda = rev - cogs_is - (opex_q0 * (0.82 + 0.18 * vol_mult) + opex_prog)
        ebitda_hist.append(ebitda)
        ltm_ebitda = sum(ebitda_hist[-4:])
        ebt = ebitda - da_q - (term_debt * r_debt_q + rev_debt * r_rev_q + fin_fee)
        net_inc = ebt - np.maximum(0.0, ebt) * tax_rate

        if mode == "structured":
            dso = [52.0, 50.5, 50.0, 49.5][q] + np.where(c_m, np.clip(3.5 + 1.2 * z5, 0.0, 6.0), np.clip(z5, 0.0, 2.5))
            dio = [86.0, 84.5, 83.5, 83.0][q] + np.where(disrupt, 5.5, 0.0) + np.where(c_m, 2.5, 0.0)
            dpo = [48.0, 49.5, 50.0, 50.5][q] - np.where(c_m, 1.0, 0.0)
            capex = np.where(c_m | (prev_lev > 1.95), 185.0, capex_base)
        else:
            dso = dso0 + csa_days + np.where(c_m, np.maximum(0.0, dso_elong + 4.0 * z5), np.maximum(0.0, 2.0 * z5))
            dio = dio0 + np.where(disrupt, 10.0, 0.0) + np.where(c_m, 5.0, 0.0)
            dpo, capex = dpo0 - np.where(c_m, 3.0, 0.0), np.full(n_paths, capex_base)

        ar_n, inv_n, ap_n = (4.0 * rev) * (dso / 365.0), (4.0 * cogs_repl) * (dio / 365.0), (4.0 * cogs_repl) * (dpo / 365.0)
        fcf = net_inc + da_q - ((ar_n - ar) + (inv_n - inv) - (ap_n - ap)) - capex
        cum_fcf += fcf

        pre_cash = cash + fcf
        draw, repay = np.clip(min_cash - pre_cash, 0.0, rev_limit - rev_debt), np.minimum(rev_debt, np.maximum(0.0, pre_cash - min_cash))
        post_cash, rev_debt = pre_cash + draw - repay, rev_debt + draw - repay
        term_prepay = np.minimum(term_debt, np.maximum(0.0, post_cash - 1650.0)) if mode == "structured" else np.zeros(n_paths)

        cash, term_debt = post_cash - term_prepay, term_debt - term_prepay
        ar, inv, ap, ppe, equity = ar_n, inv_n, ap_n, ppe + capex - da_q, equity + net_inc
        max_err = max(max_err, float(np.max(np.abs((cash + ar + inv + ppe) - (ap + acc + term_debt + rev_debt + equity)))))

        net_debt = (term_debt + rev_debt) - cash
        lev = np.where(ltm_ebitda > 50.0, net_debt / ltm_ebitda, 99.0)
        prev_lev, q_breach = lev, (lev > cov_max) | (ltm_ebitda <= 0.0)
        breach_any |= q_breach
        rev_used_any |= rev_debt > 1e-3
        shortfall_any |= cash < (min_cash - 1e-3)
        peak_lev = np.maximum(peak_lev, lev)
        q_stats.append({"quarter": f"Q{q + 1}", "mean_ltm_ebitda_usd_m": round(float(ltm_ebitda.mean()), 2),
                        "mean_net_debt_usd_m": round(float(net_debt.mean()), 2), "median_leverage": round(float(np.median(lev)), 4),
                        "p95_leverage": round(float(np.percentile(lev, 95)), 4), "covenant_breach_prob": round(float(q_breach.mean()), 4),
                        "mean_fcf_usd_m": round(float(fcf.mean()), 2)})

    cvar95 = float(cum_fcf[cum_fcf <= np.percentile(cum_fcf, 5)].mean())
    return {"covenant_breach_prob": round(float(breach_any.mean()), 4), "p95_net_debt_to_ebitda": round(float(np.percentile(peak_lev, 95)), 4),
            "median_peak_net_debt_to_ebitda": round(float(np.median(peak_lev)), 4), "cvar95_fcf_usd_m": round(cvar95, 2),
            "mean_annual_fcf_usd_m": round(float(cum_fcf.mean()), 2), "revolver_draw_prob": round(float(rev_used_any.mean()), 4),
            "min_cash_shortfall_prob": round(float(shortfall_any.mean()), 4), "max_identity_error": max_err, "quarterly": q_stats}


def main() -> None:
    cfg = load_baseline()
    cov, cr = cfg["covenants_and_thresholds"], cfg["supply_chain_and_shock_parameters"]["correlation_regime"]
    n_paths, quarters, seed = max(10000, cov["min_monte_carlo_paths"]), cov["horizon_quarters"], cov["random_seed"]
    rho_n, rho_c, p_c, df_c = cr["normal_pairwise_rho"], cr["crisis_pairwise_rho"], cr["crisis_regime_probability"], cr["student_t_df_crisis"]

    crisis, z_f, u_c, b_n = generate_regime_factors(n_paths, quarters, seed, rho_n, rho_c, p_c, df_c)
    unhedged = run_three_statement_mc(cfg, "unhedged", crisis, z_f, u_c, b_n)
    gaussian_naive = run_three_statement_mc(cfg, "gaussian_naive", crisis, z_f, u_c, b_n)
    structured = run_three_statement_mc(cfg, "structured", crisis, z_f, u_c, b_n)

    regimes = [("Normal_Gaussian_rho0.15", 0.15, 0.15, 0.0, 200), ("Gaussian_HighRho_0.88", 0.15, 0.88, 0.35, 200),
               ("Base_Contagion_t4_rho0.88", 0.15, 0.88, 0.35, 4), ("Severe_Contagion_t4_p0.60_rho0.92", 0.15, 0.92, 0.60, 4)]
    sens, max_err = [], max(unhedged["max_identity_error"], gaussian_naive["max_identity_error"], structured["max_identity_error"])
    for lbl, rn, rc, pc, df in regimes:
        cs, zs, us, bs = generate_regime_factors(n_paths, quarters, seed, rn, rc, pc, df)
        for tr in (0.30, 0.60, 0.75):
            ur, sr = run_three_statement_mc(cfg, "unhedged", cs, zs, us, bs, tr), run_three_statement_mc(cfg, "structured", cs, zs, us, bs, tr)
            max_err = max(max_err, ur["max_identity_error"], sr["max_identity_error"])
            sens.append({"regime": lbl, "tariff_rate": tr, "unhedged_breach_prob": ur["covenant_breach_prob"],
                         "structured_breach_prob": sr["covenant_breach_prob"], "unhedged_p95_lev": ur["p95_net_debt_to_ebitda"],
                         "structured_p95_lev": sr["p95_net_debt_to_ebitda"], "structured_cvar95_fcf_usd_m": sr["cvar95_fcf_usd_m"]})

    metrics = {
        "num_monte_carlo_paths": n_paths, "accounting_identity_max_error": max_err, "accounting_identity_passed": bool(max_err < 1e-6),
        "modeled_normal_rho": rho_n, "modeled_crisis_rho": rho_c,
        "unhedged_covenant_breach_prob": unhedged["covenant_breach_prob"],
        "structured_covenant_breach_prob": structured["covenant_breach_prob"],
        "breach_prob_reduction_abs": round(unhedged["covenant_breach_prob"] - structured["covenant_breach_prob"], 4),
        "unhedged_p95_net_debt_to_ebitda": unhedged["p95_net_debt_to_ebitda"],
        "structured_p95_net_debt_to_ebitda": structured["p95_net_debt_to_ebitda"],
        "unhedged_cvar95_fcf_usd_m": unhedged["cvar95_fcf_usd_m"],
        "structured_cvar95_fcf_usd_m": structured["cvar95_fcf_usd_m"],
        "hedging_and_working_capital_actions": [
            {"pillar": "1_Customs_FTZ_And_Dual_Sourcing", "sizing_usd_m": 2462.4, "annual_cost_usd_m": 66.0,
             "mechanism": "19 CFR 152.103 First-Sale customs unbundling + FTZ duty deferral + Q3-Q4 allied Tier-2 substrate ramp (dutiable share 45% -> 29%)"},
            {"pillar": "2_Zero_CSA_FX_And_RareEarth_Convexity", "sizing_usd_m": 6920.0, "annual_cost_usd_m": 98.0,
             "mechanism": "$3,800M/yr zero-CSA Asian FX risk-reversal collar (+2.5%/+18.5%/-4.5%), $1,720M/yr PrNd/DyTb oxide OTC call spread (20%-75%), $1,400M/yr dual-trigger contagion corridor"},
            {"pillar": "3_Commercial_Tariff_Indexation", "sizing_usd_m": 5472.0, "annual_cost_usd_m": 0.0,
             "mechanism": "Quarterly OEM/hyperscaler tariff & rare-earth surcharge clauses lifting short-run passthrough 40% -> 49% (-80 bps volume elasticity)"},
            {"pillar": "4_NonRecourse_AR_And_SCF_WorkingCapital", "sizing_usd_m": 1150.0, "annual_cost_usd_m": 48.0,
             "mechanism": "$650M ASC-860 non-recourse AR securitization (DSO 54->49.5d, crisis cap +6d) + $500M reverse factoring (DPO 46->50.5d) + bonded VMI (DIO 88->83d)"},
            {"pillar": "5_Cash_Sweep_And_Contingent_CapEx_Gate", "sizing_usd_m": 850.0, "annual_cost_usd_m": 0.0,
             "mechanism": "Excess cash sweep >$1,650M retiring 5.50% Term Debt at par + $40M/qtr CapEx deferral gate when prior leverage >1.95x or crisis active"},
        ],
        "diagnostics": {"unhedged": unhedged, "gaussian_naive_benchmark": gaussian_naive, "structured": structured, "sensitivity_matrix": sens},
    }
    out = Path(__file__).resolve().parent / "metrics.json"
    out.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"Wrote {out} | err={max_err:.3e} | unhedged={unhedged['covenant_breach_prob']:.4f} -> structured={structured['covenant_breach_prob']:.4f}")


if __name__ == "__main__":
    main()
