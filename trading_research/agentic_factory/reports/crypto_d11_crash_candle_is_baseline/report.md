# Crypto-D11 — Crash-Candle Reversion v1 In-Sample (IS) Baseline (BTC/ETH/SOL spot, 2020–2023)

**This is an IN-SAMPLE BASELINE step only.** No OOS, no 2024/2025/2026, no
optimization, no parameter or rule change, no network, no exchange API, no broker,
no paper, no live. Frozen data was read **read-only** and not modified. S30/futures
untouched; JARVIS/`templates/base.html`/hydra untouched. No staging, no commit.

- **Created:** 2026-05-30
- **Binding context (committed):** D8 audit `ca4d9eb`, D9 frozen spec `6e0c85b`,
  D10 engine+tests `ce499c6`; data freeze D3b `5b3d94c`, ratified D3c `fe5594f`.
- **Frozen snapshot:** `data_crypto/spot_binance_usdt_1d_2020_2025/`
- **Engine:** `engine/crypto_crash_candle_reversion.py` (CCR1 v1, GROSS; friction a
  separate layer).

---

## 1. Inputs & OOS seal

| Symbol | File | IS window | Full rows | IS rows (≤2023) | rows>2023 used |
|---|---|---|---|---|---|
| BTC | `BTCUSDT_1d_2020_2025.csv` | 2020-01-01..2023-12-31 | 2192 | 1461 | 0 |
| ETH | `ETHUSDT_1d_2020_2025.csv` | 2020-01-01..2023-12-31 | 2192 | 1461 | 0 |
| SOL | `SOLUSDT_1d_2020_2025.csv` | 2020-08-11..2023-12-31 | 1969 | 1238 | 0 |

Each symbol was sliced to **year ≤ 2023 BEFORE any computation** (no SMA/trend
warmup is needed — v1 has no trend filter). **No 2024/2025/2026 bar is read.** A
late-2023 entry that cannot complete its 3-bar horizon by 2023-12-31 exits
`data_end` at the 2023-12-31 close. SOL is a **PARTIAL IS** (starts 2020-08-11) —
reported separately, never padded. **OOS 2024–2025 and 2026 remain SEALED.**

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

## 3. Per-symbol metrics (gross unless noted; net = per-trade additive friction)

| Metric | BTC (primary) | ETH | SOL (partial) |
|---|---|---|---|
| Trades | 69 | 97 | 143 |
| Gross total | +86.58% | +159.21% | +300.32% |
| Net total @0.30% | +65.88% | +130.11% | +257.42% |
| Net total @0.45% | +55.53% | +115.56% | +235.97% |
| Avg trade (base) | +0.95% | +1.34% | +1.80% |
| Median trade (base) | +0.29% | +0.84% | **−0.11%** |
| Win rate (gross) | 56.52% | 60.82% | 51.05% |
| PF (gross) | 1.609 | 1.647 | 1.533 |
| PF (net 0.30%) | 1.436 | 1.505 | 1.440 |
| PF (net 0.45%) | 1.356 | 1.438 | 1.396 |
| Best trade | +22.54% | +25.23% | +52.47% |
| Worst trade | −15.02% | −27.25% | −56.82% |
| Exits | {time_exit: 69} | {time_exit: 97} | {time_exit: 143} |
| Top-3 removal (net 0.30%) | **PASS** (+15.76%) | **PASS** (+62.59%) | **PASS** (+118.57%) |

All exits are `time_exit` (the fixed 3-bar horizon) — no `data_end` artifact
occurred, so every IS signal completed its full horizon inside 2020–2023.

### Year-by-year gross total (by entry year)

- **BTC** — 2020: +67.42% (14t), 2021: +26.55% (29t), 2022: **−17.60%** (20t),
  2023: +10.21% (6t); positive years: 3/4.
- **ETH** — 2020: +52.47% (24t), 2021: +118.91% (37t), 2022: **−25.99%** (30t),
  2023: +13.82% (6t); positive years: 3/4.
- **SOL** — 2020: +24.94% (29t), 2021: +333.95% (48t), 2022: **−97.13%** (44t),
  2023: +38.56% (22t); positive years: 3/4.

**Every symbol loses in the 2022 bear.**

## 4. Combined metrics (BTC+ETH+SOL pooled)

- Trades: **309** (BTC 69, ETH 97, SOL 143)
- Gross total **+546.11%**; net @0.30% **+453.41%**; net @0.45% **+407.06%**
- Win rate 55.34%; PF gross **1.574**, PF net0.30 **1.456**, PF net0.45 **1.401**
- Avg trade base +1.47%; median base +0.37%; best +52.47%, worst −56.82%
- Year totals (gross) — 2020 +144.83% (67t), 2021 **+479.41% (114t)**,
  2022 **−140.72% (94t)**, 2023 +62.59% (34t); positive years 3/4.

## 5. Friction & +50% stress (per-trade additive)

| Pool | Gross | Net @0.30% | Net @0.45% | PF gross | PF @0.30% | PF @0.45% |
|---|---|---|---|---|---|---|
| BTC | +86.58% | +65.88% | +55.53% | 1.609 | 1.436 | 1.356 |
| ETH | +159.21% | +130.11% | +115.56% | 1.647 | 1.505 | 1.438 |
| SOL | +300.32% | +257.42% | +235.97% | 1.533 | 1.440 | 1.396 |
| **Combined** | **+546.11%** | **+453.41%** | **+407.06%** | **1.574** | **1.456** | **1.401** |

Net PF survives the +50% friction stress on every symbol and combined — a clear
contrast with CODR-1, whose combined net PF fell below 1.3 at base friction.

## 6. Top-3-winner-removal gate (the universal killer)

| Pool | net ex-top3 @0.30% | pass |
|---|---|---|
| BTC | +15.76% | ✅ |
| ETH | +62.59% | ✅ |
| SOL | +118.57% | ✅ |
| **Combined** | **+314.55%** | ✅ |

**PASS on all three symbols AND combined at base friction.** The gate that parked
every futures branch and failed 2/3 of CODR-1's symbols is **NOT** the failure
point for crash-candle v1. The higher BTC event count (69 vs CODR-1's 9) dilutes
single-winner concentration.

## 7. Sequence-risk (PRELIMINARY, non-binding — full check is a later step)

- Seeded (seed=0, 5000 iter) on combined net-base per-trade returns. Label:
  **SEQUENCE_RISK_PRELIMINARY_NONBINDING**.
- Bootstrap P(total≤0) = **0.0108**; p05 +1.259, p50 +4.524, p95 +7.642.
- Longest losing streak 6; realized max DD 1.29 (return-units). **Not a gate at D11.**

## 8. Gate scorecard vs frozen Crypto-D9 gates

| Gate | Result | Pass |
|---|---|---|
| BTC ≥30 trades | 69 | ✅ |
| BTC net expectancy >0 @0.30% | +0.95%/trade | ✅ |
| BTC top-3 removal positive @0.30% | +15.76% | ✅ |
| Combined net PF >1.3 @0.30% | 1.456 | ✅ |
| Combined positive @0.45% stress | +407.06% | ✅ |
| ≥2/3 symbols positive @0.30% | 3/3 | ✅ |
| **No single year >60% of net** | BTC 96% / combined 98% | ❌ |
| Sequence risk not fragile | preliminary non-fragile | DEFERRED |

**6 of 8 pass — every BTC-primary gate passes — but the single-year-dominance gate
FAILS hard.**

## 9. The single-year-dominance failure (the central concern)

- **BTC:** 2020 alone is **96%** of net base. Remove 2020 and BTC's three-year net
  base is only **+2.7%** over **55 trades** — essentially flat. BTC is profitable
  in 2020/2021/2023 but loses in 2022.
- **Combined:** 2021 alone is **98%** of net base. Remove 2021 and the pooled
  three-year net base is only **+8.2%** over **195 trades** — marginal.
- **2022 bear:** every symbol is negative (BTC −17.6%, ETH −26.0%, SOL −97.1%
  gross). The strategy is, on this IS slice, effectively a **2020–2021
  bull-regime crash-buyer** — exactly the regime fragility the ladder exists to
  catch.

The headline returns are real and the structural CODR-1 problem (BTC sparsity) is
solved — but the edge is not demonstrated to be regime-robust.

## 10. IS verdict

### **IS_WATCH**

- **NOT IS_CONTINUE:** a hard gate (single-year dominance) failed, and the standing
  conservative rule forbids CONTINUE while a robustness gate is unresolved.
- **NOT IS_FAIL:** none of the explicit IS_FAIL triggers fired — BTC primary did
  **not** fail hard (it passes trade-count, expectancy, top-3, PF, stress),
  combined friction did **not** fail, BTC top-3 did **not** fail, trade count did
  **not** fail. ETH/SOL pooling is **not** rescuing a BTC failure here; BTC stands
  on its own.
- → The honest conservative reading is **IS_WATCH**: a genuinely stronger profile
  than every parked branch, held back by one hard gate — regime concentration.

## 11. Recommendation

**IS_WATCH — do NOT run OOS yet.** Per the D9 ladder an IS_WATCH *may* proceed to
**Crypto-D12 (OOS protocol pre-registration)** under **separate authorization** —
but **only if D12 pre-registers an explicit regime / single-year robustness
analysis as a first-class OOS acceptance criterion.** **OOS 2024–2025 stays SEALED
until a D12 protocol is committed.**

- **What D11 proves:** the raw crash candle fires enough on BTC (69 events) to
  power a friction-survivable, top-3-robust, per-symbol-positive IS profile —
  dropping the trend/confirmation filter solved CODR-1's BTC sparsity.
- **What D11 does NOT prove:** a regime-robust edge. The net is a single-bull-year
  artifact (BTC 2020, combined 2021); every symbol loses in the 2022 bear; no OOS
  bar has been touched.
- **Central risk:** regime concentration. OOS 2024–2025 (bull + chop) is the real
  test, and it stays sealed until D12.
- **Anti-overfit:** no tuning of v1 — do not change −5%, do not switch to
  −7%/−10%, do not add an SMA/trend or confirmation filter, do not change the
  3-bar exit. Any of those is a NEW spec id and a fresh ladder.
- **Fail path:** if the single-year dominance is judged disqualifying on review,
  park crash-candle v1 as a bull-only artifact and do not run OOS.

## 12. Forbidden actions (this lane)

`no_oos_use` · `no_2024_2025_2026` · `no_optimization` · `no_parameter_change` ·
`no_strategy_rule_change` · `no_network` · `no_exchange_api_execution` ·
`no_broker` · `no_paper_or_live` · `no_modification_of_frozen_data` ·
`do_not_touch_s30_or_futures` · `jarvis_templates_base_hydra_untouched` ·
`no_staging` · `no_commit` · `no_perps`

---

**Trading recommendation:** NONE — research IS baseline only. **Crash-Candle
Reversion v1 is IS_WATCH**: a strong BTC-primary profile (69 trades, net
expectancy +0.95%/trade, PF 1.44 net, top-3 removal POSITIVE on all symbols,
3/3 symbols friction-positive) that is a clear step up from CODR-1 — but the
**single-year-dominance hard gate FAILS** (BTC 2020 = 96% of net, combined 2021 =
98%) and **every symbol loses in the 2022 bear**, so the edge is a 2020–2021 bull
artifact, not a validated edge. No OOS was run; **OOS 2024–2025 and 2026 remain
sealed**; perps remain blocked; crypto stays a separate research lane; **S30 stays
PARKED and the futures branches are untouched.** No crypto strategy is paper-ready
or live-ready.
