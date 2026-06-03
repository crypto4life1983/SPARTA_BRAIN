# Crypto-D1 Baseline Backtest Plan — V002 IS/OOS Addendum

**Status: Pre-registration addendum. Pins the existing validated baseline backtest plan and runner to a specific frozen dataset version. No backtest is run by this addendum. No historical result is produced by this addendum.**

This addendum does **not** replace, modify, or re-author the canonical plan. It supplies the one missing pre-registration artifact the canonical plan explicitly calls for in its `required_future_artifacts`: *"IS / OOS window addendum — explicit IS/OOS date ranges pinned to a specific dataset_id+dataset_version."*

| Field | Value |
|---|---|
| Addendum to | `reports/crypto_d1_baseline_backtest_plan_v1/backtest_plan.json` + `backtest_plan.md` |
| Runner pinned | `tools/crypto_d1_backtest_runner.py` (crypto_d1_backtest_runner_v1) |
| Plan version | crypto_d1_baseline_backtest_plan_v1 |
| Addendum author | Mahmoud Cherif (operator) |
| Addendum date | 2026-06-03 |
| Official master at write | 5ee5255 |

---

## 1. Dataset

- **Dataset ID:** CRYPTO_D1_SPOT_BTC_ETH_SOL_V001
- **Dataset version:** **V002**
- **On-disk location:** `data/crypto_d1_research/CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V002/`
- **Assets:** BTC, ETH, SOL (USD-quote, 1d, UTC)
- **Data range:** 2021-06-17 → 2025-12-31 (4,976 rows total)
- **Freeze status:** FROZEN (checksummed, immutable)

## 2. QA status

- **QA verdict:** QA_WARN (37 checks: 36 PASS / 1 WARN / 0 FAIL).
- **QA report ID:** f0111872581a873e
- **QA report:** `reports/crypto_d1_qa_runtime_v1/CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002/qa_report.json` + `qa_report.md`.
- **Operator acceptance:** QA_WARN accepted by operator memo `reports/crypto_d1_qa_runtime_v1/CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002/operator_acceptance_memo.md`, committed at master **5ee5255**.
- This satisfies the canonical plan's `required_dataset_gate.qa_status_pass_or_approved_warn` condition ("QA_PASS OR ('QA_WARN' with an explicit operator-acceptance note attached)").
- **QA_WARN remains QA_WARN.** This addendum does not relabel the dataset QA_PASS.

## 3. IS / OOS split

Declared in writing **before** any run, per the canonical plan's `IS_OOS_policy` (no overlap, no leakage, OOS sealed until after IS verdict):

- **In-sample (IS):** 2021-06-17 → 2024-06-16 (~3.0 yr).
- **Out-of-sample (OOS):** 2024-06-17 → 2025-12-31 (~1.55 yr).
- **No overlap** between IS and OOS. OOS is **sealed** — not read or tuned against until the IS verdict is fixed.
- Windows pin to the dataset manifest's `time_start` (2021-06-17) and `time_end` (2025-12-31).
- The single BTC missing day (2024-03-31) falls inside **IS**, leaving OOS fully intact.

## 4. BTC missing day handling

- **Affected:** BTC missing the single daily bar of **2024-03-31** (BTC observed 1658 vs expected 1659; ETH and SOL complete). This is the sole QA_WARN cause (`missing_days_reconciled`, group B_timestamp).
- **Do not forward-fill.**
- **Do not synthesize.**
- **Treat as a true gap:** indicators bridge across the absent bar (next available bar = 2024-04-01); any open position carries through with no fill/PnL recorded on the missing date.
- **Report it explicitly** in every future backtest output for this dataset (count=1, date=2024-03-31, asset=BTC), so results are auditable against the QA report. No silent handling.

## 5. First execution batch

The first sealed run executes a **subset** of the canonical plan's six pre-registered families. Mapping to canonical family IDs:

- **B0 — Buy & Hold benchmark** → `buy_and_hold_benchmark` (status: benchmark). Per asset + equal-weight monthly-rebalanced basket. The mandatory reference every active strategy must beat after costs.
- **B1 — Moving-average trend filter / SMA 50/200** → `moving_average_trend_filter` (status: primary). Long when fast MA > slow MA; flat otherwise. Long-only, daily close.
- **B2 — Momentum continuation / time-series momentum N=30 and N=90** → `momentum_continuation` (status: primary). Long if trailing-N-day return > 0; exit on signal flip. N ∈ {30, 90}. Long-only, daily close.
- **B3 — Donchian channel breakout 55/20** → `donchian_channel_breakout` (status: primary). Entry on 55-day rolling high; exit on 20-day rolling low. Long-only, daily close.

All long/flat only — no shorting, no leverage — consistent with the canonical `position_sizing_policy`. Parameters above are drawn from the canonical pre-registered grids; this batch fixes the specific values to run first and does not expand any grid.

## 6. Deferred (not in the first execution batch)

The following remain pre-registered in the canonical plan but are **deferred** to separately-authorized later runs:

- **Volatility-regime gate** (`volatility_regime_gate`, additive filter).
- **Mean reversion** (`mean_reversion`, WATCH-only).
- **Any extra parameter sweeps** beyond the fixed B0–B3 values listed in §5.

Deferring these keeps the first run small and auditable. Adding them later is a distinct, separately-approved decision.

## 7. Fees / slippage

Pulled verbatim from the frozen V002 `fees.json` (`data/crypto_d1_research/CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V002/fees.json`, conservative Kraken Pro spot low-volume baseline):

- **Taker fee:** 40 bps per side (assume taker / conservative fills).
- **Slippage:** 10 bps per side.
- **Spread proxy:** 10 bps per side.
- Consistent with the canonical `cost_model_requirements` (taker default, fees as a distinct PnL line, no zero-cost baseline) and `slippage_model_requirements` (no zero-slippage baseline). No maker assumption, no fee-tier improvement, no rebate.

## 8. Safety boundaries

- **No backtest is run by this addendum.** No historical result is produced by this addendum.
- This addendum does not imply edge. A future PASS is not trading authorization.
- **No paper/live trading is authorized.** No order placement. No exchange connection. No data fetch.
- **No ACTIVE/STRONG promotion.** `crypto_d1_protocol` remains **WATCH / MIXED**.
- **QA_WARN remains QA_WARN, not QA_PASS.**
- No scheduler / background daemon. No credential or .env access. No synthetic / mock-priced data as evidence.
- Crypto trend ideas are not profitable until tested with full costs and forward-validated; this addendum does neither. A good historical chart does not imply future returns. 24/7 session handling; weekday-only filters forbidden.
- The canonical `backtest_plan.json`, `backtest_plan.md`, the runner, and all V001/V002 frozen dataset files are left untouched by this addendum.
