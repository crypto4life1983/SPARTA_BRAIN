# Crypto-D6 — CODR-1 In-Sample (IS) Baseline (BTC/ETH/SOL spot, 2020–2023)

**This is an IN-SAMPLE BASELINE step only.** No OOS, no 2024/2025/2026, no optimization, no parameter or rule change, no network, no exchange API, no broker, no paper, no live. Frozen data was read **read-only** and not modified. S30/futures untouched; JARVIS/`templates/base.html`/hydra untouched. No staging, no commit.

- **Created:** 2026-05-30
- **Binding context (committed):** D1 `c8a59fe`, D2 `a035ab0`, D3 `31ebdaf`, D3a `ae25f43`, D3b `5b3d94c`, D3c `fe5594f`, D4 `5552356`, D5 `4614190`.
- **Frozen snapshot:** `trading_research/agentic_factory/data_crypto/spot_binance_usdt_1d_2020_2025/`

---

## 1. Inputs & OOS seal

| Symbol | File | IS window | Full rows | IS rows (≤2023) | rows>2023 used |
|---|---|---|---|---|---|
| BTC | `BTCUSDT_1d_2020_2025.csv` | 2020-01-01..2023-12-31 | 2192 | 1461 | 0 |
| ETH | `ETHUSDT_1d_2020_2025.csv` | 2020-01-01..2023-12-31 | 2192 | 1461 | 0 |
| SOL | `SOLUSDT_1d_2020_2025.csv` | 2020-08-11..2023-12-31 | 1969 | 1238 | 0 |

SOL is a **PARTIAL IS** (starts 2020-08-11) — reduced power, reported separately, never padded or stitched. **No 2024/2025/2026 bar is read:** only year≤2023 bars enter the engine; a late-2023 entry that cannot complete its 5-bar horizon by 2023-12-31 exits as `data_end` at the 2023-12-31 close.

## 2. Data QA (IS slice)

| Check | BTC | ETH | SOL |
|---|---|---|---|
| Rows | 1461 | 1461 | 1238 |
| Range | 2020-01-01→2023-12-31 | 2020-01-01→2023-12-31 | 2020-08-11→2023-12-31 |
| Duplicate ts | 0 | 0 | 0 |
| Invalid OHLC | 0 | 0 | 0 |
| Zero/neg vol | 0 | 0 | 0 |
| Rows >2023 | 0 | 0 | 0 |

QA verdict: **CLEAN** on the IS slice.

## 3. Per-symbol metrics (gross unless noted)

| Metric | BTC (primary) | ETH | SOL (partial) |
|---|---|---|---|
| Trades | 9 | 27 | 30 |
| Gross total | -2.23% | 34.80% | 69.37% |
| Avg trade (gross) | -0.25% | 1.29% | 2.31% |
| Median trade | -0.11% | 1.03% | 3.23% |
| Win rate | 44.44% | 51.85% | 53.33% |
| PF (gross) | 0.911 | 1.278 | 1.528 |
| PF (net 0.30%) | 0.814 | 1.207 | 1.446 |
| Best trade | 9.42% | 24.75% | 28.71% |
| Worst trade | -12.11% | -25.69% | -21.41% |
| Avg hold (bars) | 5.00 | 4.44 | 4.37 |
| Exits | {'time_stop': 8, 'protective_stop': 1} | {'protective_stop': 7, 'time_stop': 20} | {'time_stop': 21, 'protective_stop': 9} |
| Top-3 gate (gross) | FAIL | FAIL | PASS |

### Year-by-year gross total (entry year)

- **BTC** — 2020: 9.31% (2t), 2021: -11.53% (7t); positive years: 1
- **ETH** — 2020: 26.82% (7t), 2021: 12.73% (19t), 2023: -4.75% (1t); positive years: 2
- **SOL** — 2021: 71.22% (24t), 2022: -0.62% (2t), 2023: -1.23% (4t); positive years: 1

## 4. Combined metrics (BTC+ETH+SOL pooled)

- Trades: **66** (BTC 9, ETH 27, SOL 30)
- Gross total: **101.94%**, avg trade 1.54%, median 1.09%
- Win rate: 51.52%; PF gross **1.362**; avg hold 4.48 bars
- Best 28.71%, worst -25.69%; exits {'time_stop': 49, 'protective_stop': 17}
- Year totals — 2020: 36.12% (9t), 2021: 72.42% (50t), 2022: -0.62% (2t), 2023: -5.98% (5t); positive years 2/4

## 5. Friction & +50% stress (per-trade additive)

| Pool | Gross total | Net @0.30% | Net @0.45% | PF gross | PF @0.30% | PF @0.45% |
|---|---|---|---|---|---|---|
| BTC | -2.23% | -4.93% | -6.28% | 0.911 | 0.814 | 0.769 |
| ETH | 34.80% | 26.70% | 22.65% | 1.278 | 1.207 | 1.173 |
| SOL | 69.37% | 60.37% | 55.87% | 1.528 | 1.446 | 1.406 |
| **Combined** | 101.94% | 82.14% | 72.24% | **1.362** | **1.282** | 1.244 |

## 6. Top-3-winner-removal gate (the universal killer)

| Pool | net ex-top3 (gross) | gross pass | net ex-top3 @0.30% | @0.30% pass | @0.45% pass |
|---|---|---|---|---|---|
| BTC | -23.32% | ❌ | -25.12% | ❌ | ❌ |
| ETH | -27.85% | ❌ | -35.05% | ❌ | ❌ |
| SOL | 5.24% | ✅ | -2.86% | ❌ | ❌ |
| **Combined** | 25.64% | ✅ | 6.74% | ✅ | ❌ |

Per-symbol gross top-3 pass count: **1/3**. The combined-pool pass is pooling-dependent, not per-symbol robust.

## 7. Sequence-risk (PRELIMINARY, non-binding — full check is Crypto-D10)

- Seeded (seed=0, 5000 iter) on combined gross R-multiples. Verdict label: **SEQUENCE_RISK_INCONCLUSIVE**.
- Bootstrap P(total≤0) = 0.1482; p05=-5.74R, p50=9.93R, p95=26.07R.
- Longest losing streak 3; realized max DD 6.60R (shuffle p95 10.79R).
- **Not a gate at D6.** Recorded for context only.

## 8. Gate scorecard vs frozen Crypto-D4 gates

| Gate | BTC | ETH | SOL | Combined |
|---|---|---|---|---|
| ≥30 trades | ❌ (9) | ❌ (27) | ✅ (30) | ✅ (66) |
| Expectancy>0 net0.30 | ❌ | ✅ | ✅ | ✅ |
| PF>1.3 gross | ❌ | ❌ | ✅ | ✅ |
| PF>1.3 net0.30 | ❌ | ❌ | ✅ | ❌ |
| Top-3 removal gross | ❌ | ❌ | ✅ | ✅ |
| Top-3 removal net0.45 | ❌ | ❌ | ❌ | ❌ |

Multi-asset corroboration (net0.30 expectancy>0): **2/3** (BTC negative).

## 9. IS verdict

### **IS_FAIL**

- BTC (PRIMARY) fails hard: 9 trades (<30), gross expectancy NEG, PF_gross 0.911 (<1.3), top-3 gate FAIL.
- Combined PF after pre-registered 0.30% friction 1.282 < 1.3 (gross passes, friction does not -> never CONTINUE).
- Combined top-3-winner-removal FAILS under +50% friction stress (net_ex_top3 -0.0271).
- The hard top-3 gate (the gate that parked every futures branch) passes on only 1/3 symbols gross -- the combined-pool pass is pooling-dependent, not per-symbol robust.

**Regime note:** the edge is concentrated in the 2020–2021 bull. The `close>SMA200` trend filter suppresses entries in the 2022 bear (combined 2022: 2 trades, 2023: 5 trades), so the strategy is effectively a bull-only dip-buyer — exactly the regime fragility the ladder is built to catch.

## 10. Recommendation

PARK CODR-1 v1. Do NOT pre-register an OOS protocol and do NOT run OOS (Crypto-D7/D8 not reached). The IS baseline does not clear the frozen gates: the primary symbol (BTC) is unprofitable and fails the hard top-3 gate, the edge is concentrated in the 2020-2021 bull (the trend filter suppresses trades in 2022-2023), and combined profitability does not survive friction on profit-factor or the +50% stress top-3 gate. Any future attempt requires a NEW spec id and a fresh ladder, not a tweak.

## 11. Forbidden actions (this lane)

`no_oos_use` · `no_2024_2025_2026` · `no_optimization` · `no_parameter_change` · `no_strategy_rule_change` · `no_network` · `no_exchange_api_execution` · `no_broker` · `no_paper_or_live` · `no_modification_of_frozen_data` · `do_not_touch_s30_or_futures` · `jarvis_templates_base_hydra_untouched` · `no_staging` · `no_commit`

---

**Trading recommendation:** NONE -- research IS baseline only; CODR-1 PARKED after IS_FAIL. No crypto strategy is paper-ready or live-ready; perps remain blocked; crypto stays a separate research lane; S30 stays PARKED and the futures branches are untouched.
