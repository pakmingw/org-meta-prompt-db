# Task 2: 3-Statement Monte Carlo Liquidity, Inventory & Hedging Plan Under Multi-Tier Tariff + Rare-Earth Shock

## Financial & Supply-Chain Problem Statement
Structure a quantitative 4-quarter (`Q1..Q4`) 3-statement Monte Carlo liquidity, working-capital/inventory, and FX/commodity hedging plan for a `$24.0B` revenue global semiconductor enterprise hit by an abrupt **60% multi-tier tariff + rare-earth export quota shock** where historical Gaussian correlations break down (`rho = 0.15 -> 0.88` crisis contagion) and the quarterly **`Net Debt / LTM EBITDA <= 2.50x`** maintenance covenant is threatened.

### Baseline Profile & Constraints (`baseline_financials.json`)
- **Annual Baseline**: Revenue `$24,000M`, COGS `$14,400M`, OpEx `$4,800M`, EBITDA `$4,800M` (`20%` margin), Gross Debt `$10,500M`, Cash `$2,100M`, Net Debt `$8,400M` (`1.75x`), Undrawn Revolver `$1,500M`, Covenant **`Net Debt / LTM EBITDA <= 2.50x`** tested quarterly (`Q1..Q4`), Min Cash `$1,000M`.
- **Initial Balance Sheet (`$22,000M`)**: Strictly balanced (`Assets = Cash $2,100M + AR $3,551M + Inv $3,472M + PP&E $12,877M = $22,000M`; `Liabilities + Equity = AP $1,815M + Accrued $1,685M + Debt $10,500M + Equity $8,000M = $22,000M`), `DSO=54`, `DIO=88`, `DPO=46`.
- **BOM & Regime-Shift Risk**: `38%` of COGS is exposed to Tier-2 specialty substrates (`140`-day lead time). Under crisis contagion (`35%` crisis regime weight, `rho = 0.88` fat-tailed / Student-t co-movement vs. normal `rho = 0.15`), tariff cost surge, rare-earth spot surcharges, FX basis spikes, customer DSO elongation, and supplier disruption hit simultaneously.

## Required Deliverables (Write into Your Assigned Output Directory)
1. **`solution.py`**: Self-contained Python 3 script (`numpy` / `scipy` / stdlib) that loads `baseline_financials.json`, runs **`>= 2,000` Monte Carlo paths** across 4 quarters modeling the `rho = 0.15 -> 0.88` non-Gaussian regime shift, simulates **both** (a) **Unhedged Baseline** and (b) your **Structured Capital, Inventory & Hedging Strategy**, verifies exact 3-statement balance-sheet identity (`abs(Assets - (Liabilities + Equity)) < 1e-6` across all paths/quarters), and writes **`metrics.json`** with:
   - `num_monte_carlo_paths` (`>= 2000`), `accounting_identity_max_error`, `accounting_identity_passed` (`bool`)
   - ` modeled_normal_rho`, `modeled_crisis_rho`
   - `unhedged_covenant_breach_prob`, `structured_covenant_breach_prob`, `breach_prob_reduction_abs`
   - `unhedged_p95_net_debt_to_ebitda`, `structured_p95_net_debt_to_ebitda`
   - `unhedged_cvar95_fcf_usd_m`, `structured_cvar95_fcf_usd_m`, `hedging_and_working_capital_actions`
2. **`deliverable.md`** (`<= 240` lines): CFO Board Capital-Allocation Memo detailing the 3-statement shock transmission, why Gaussian hedges fail under `rho -> 0.88` basis/contagion risk, quantified instrument sizing & costs, sensitivity table across correlation/tariff regimes, and falsifiable quarterly Board trigger gates.

Execute `solution.py` before finishing so `metrics.json` is verified on disk.
