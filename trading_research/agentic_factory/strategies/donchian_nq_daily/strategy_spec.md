# Strategy Spec — NQ-only Daily Donchian 55/20 No-Pyramid Slice

**Status: `CONTINUE — GATED`**
Document type: handoff spec (PLAN/SPEC-ONLY). No code, no backtest, no data, no fetch.
This is a frozen design record for the *first* old-report strategy handed into the
Agentic Backtest Factory. Nothing here is executed by writing this file.

---

## 1. Strategy name

**NQ-only Daily Donchian 55/20 No-Pyramid Slice**

A single-instrument, daily-bar trend-following breakout system: the smallest
faithful slice of the stronger multi-market old-report Donchian candidate.

---

## 2. Source lineage (read-only evidence, NOT parameter inheritance)

- **S10-D2 Cross-Asset Donchian No-Pyramid Reparam-Cap — Cost-Stress Matrix (sealed)**
  `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_cost_stress_matrix_result_sealed.json`
- **S10-D2 Tier-N spec (sealed)**
  `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_tier_n_spec.md`
  (Tier-N seal sha256 `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`)
- Surfaced via the idea_miner candidate `IM_064_s10_d2_cross_asset_donchian_no_pyramid_reparam_c`.
- Ancestor lineage (all PARKED, cited as evidence only): s4 Turtle → s5 single-market
  Donchian → s6 multi-market pyramided (money-losing) → s7-d1 → s8-d1 → s10-d2.

The S10-D2 chain is sealed and byte-stable. This spec **cites** it as upstream
evidence; it does **not** modify, revive, or re-use its sealed candidate_record_id.
Any factory variant is a **fresh** artifact under the factory namespace.

---

## 3. Why this is the first handoff

It is the **simplest safe slice** of the strongest old-report Donchian candidate.
The full S10-D2 result is a 4-market daily portfolio (NQ + GC + ZN + CL) with
ATR volatility sizing and portfolio-level equity accounting — too large a first
bite for a factory engine that today runs one intraday CSV. Taking the **NQ leg
only** lets us:

- reuse the local data closest to what the factory already transcoded (NQ);
- prove the daily-bar + Donchian-channel + ATR engine extension cheaply;
- reproduce a single known benchmark (the NQ leg) before committing to the
  GC/ZN/CL transcode and the portfolio-accounting build.

---

## 4. Instrument

**NQ.c.0 only** (Nasdaq-100 continuous front contract, c.0 roll).

---

## 5. Timeframe

**Daily bars**, built from local continuous NQ data (the factory's existing
1-minute / parquet NQ source resampled to daily OHLCV). All channel logic is
computed on daily bars. No intraday logic in this strategy.

---

## 6. Entry rule

- **Long** when price makes a **new 55-day high** (breakout above the prior
  55-day Donchian upper channel).
- **Short** when price makes a **new 55-day low** (breakout below the prior
  55-day Donchian lower channel).
- **Filter: NONE** (matches the sealed spec; every 55-day breakout is taken —
  no Turtle "skip-after-winner" filter).

---

## 7. Exit rule

- **Exit long** on a **new 20-day low** (price closes/touches below the prior
  20-day Donchian lower channel).
- **Exit short** on a **new 20-day high**.

---

## 8. Stop / risk

- **Volatility unit N = Wilder ATR(20)** on daily bars.
- **Hard stop = 2.0 N** from entry.
- Original sealed spec uses **1.0% portfolio-equity risk per trade** with
  volatility-adjusted contract sizing.
- **First factory baseline simplification:** until proper dollar sizing,
  point-value, and cost handling are implemented, the baseline may use a
  **simplified fixed-R accounting** model (P&L expressed in R multiples, where
  1R = the 2N stop distance), as the existing NQ-ORB baseline does. This is an
  explicit, documented deviation from the sealed spec and means early results
  are **not** dollar-comparable to the old report until sizing lands.

---

## 9. No-pyramid rule

`max_units_per_market = 1`. **No pyramiding** — at most one open unit in NQ at
any time. (Pyramid spacing 0.5N from the parent recipe is vestigial and never
fires under max_units = 1.) This is the key risk-control delta that fixed the
money-losing pyramided ancestor (s6 MaxDD ~123% → S10-D2 no-pyramid ~28%).

---

## 10. Known benchmark from the old report

In the sealed 4-market S10-D2 cost-stress matrix (in-sample, tier S0), the
**NQ leg alone** was **positive: ≈ +$114,308, 54 trades, ~35.2% win rate**.

Caveats on this benchmark:
- It is **in-sample only** (IS window 2013-01-01 → 2022-12-30).
- It was measured **inside the 4-market portfolio** with full ATR/dollar sizing,
  point-value, and cost handling on $500k starting capital.
- **Exact reproduction requires that full sizing/point-value/cost machinery.**
  A simplified fixed-R single-market baseline will **not** reproduce the
  ~+$114k figure; it tests the *rule mechanics*, not the dollar result.

---

## 11. Data needed

- **Target (full):** daily NQ continuous OHLCV for **2013 → 2022** (in-sample),
  later **2023 → 2025** as **sealed OOS** (never inspected until IS passes its
  own pre-committed criteria).
- **First implementation (smallest step):** start with **2013-only** daily NQ,
  resampled from the **existing local 2013 1-minute NQ CSV/parquet** the factory
  already holds. No fetch, no Databento call, no new download — transcode/resample
  of already-local data only, in a later approved step.
- Every dataset must pass the factory's `data_quality.py` scanner before any
  result is trusted; a single year (2013) is expected to grade
  `RESEARCH_OK_NOT_PROFITABILITY_GRADE` at best (single regime), never
  profitability-grade.

---

## 12. Known risks

- **In-sample only** — the old evidence has zero out-of-sample confirmation.
- **OOS not inspected** — the 2023–2025 seal must stay closed until IS clears
  pre-registered criteria.
- **Slice ≠ portfolio** — a single-market NQ slice may not match the portfolio
  result; the portfolio's edge leaned heavily on CL and ZN (NQ was the weakest
  positive leg; GC was near-dead).
- **Diversification dependence** — the original edge may rely on CL/ZN
  correlation diversification that a single market cannot provide.
- **Reproduction fidelity** — results depend on the **continuous-contract roll
  method** and on **sizing fidelity**; different roll/sizing → different numbers.
- **Low statistical power** — ~54 NQ trades over 10 years (far fewer in 2013-only).
- **No live-trading claim** — research/offline only; live remains blocked.

---

## 13. Suggested next implementation steps (each needs separate explicit authorization)

- **S23-D7** — create this spec *(this step; spec-only, no code)*.
- **S23-D8** — prepare daily NQ data: resample the existing local 2013 1-minute
  NQ CSV/parquet to daily OHLCV (offline transcode of already-local data; no fetch).
- **S23-D9** — build the daily Donchian baseline engine extension (55/20 channels,
  Wilder ATR(20), 2N stop, max_units = 1) as a **fresh** strategy module; do not
  modify the existing NQ-ORB engine, backtester, metrics, decision, or loop.
- **S23-D10** — run the NQ-only **2013 baseline** (one fixed, KILL-able run;
  gate on `data_quality.py` first; label "2013 baseline only — research, not
  profitability proof").
- **Later** — expand to full IS 2013–2022, then a pre-registered sealed-OOS
  protocol for 2023–2025; only after that, consider the GC/ZN/CL portfolio build.

---

## 14. Status

**`CONTINUE — GATED`**

Reason: this is the most promising old-report candidate and a fully-specified,
deterministic rule, but it **needs a daily-NQ data preparation step and a daily
Donchian engine extension before any backtest can run**. The decisive unknown —
out-of-sample behavior — remains untouched. No backtest, data, or code is
produced by this spec.

---

## Safety contract (mirrors factory README)

- Offline-only, research-only, local-only. No network, broker, exchange, or
  Databento API.
- No secrets/credentials access.
- All writes confined to `trading_research/agentic_factory/`.
- This document modifies no engine, config, data, report, or test file.
- No staging, no committing.
