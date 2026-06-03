# Crypto-D1 Momentum Robustness — Decision Memo

- **Memo date:** 2026-06-03
- **Official master at decision time:** `49280ca986dc23adec39ebcb3091c7a886ec44c6`
- **Scope:** research-only. This memo authorizes **no** trading, data fetch, or
  promotion. It records a research direction only.

---

## 1. Context

The `momentum_robustness_v1` sweep completed over the frozen V002 dataset
(`CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V002`), run_id `458a1e7764fff90d`,
result status **WATCH** (exit 0, 0 failures).

Findings:

- Momentum was **positive out-of-sample (OOS) on every tested lookback**
  (N = 20, 30, 45, 60, 90) across **all three assets** (BTC / ETH / SOL).
  Not a single OOS cell flipped negative — the edge is a contiguous positive
  plateau, not one lucky point.
- OOS momentum **beat per-asset buy-and-hold OOS everywhere** (B&H OOS:
  BTC +0.32, ETH −0.15, SOL −0.13).
- OOS magnitude **decays monotonically as the lookback lengthens**, and
  statistical reliability (the per-asset 20-trade OOS floor) only holds at the
  **short end**: N=20 clears the floor on all three assets; N=30 clears it on
  BTC only (ETH 19, SOL 18 — just under); N≥45 becomes thin-sample.
- The conservative classifier correctly held **WATCH** because most longer-
  lookback OOS cells fall below the trade-count floor.

**Current lane state (unchanged):** Crypto-D1 = **WATCH / MIXED**;
`readiness_status` = **NOT_READY_FOR_REAL_DATA**; all safety flags locked
(research_only=True; fetch / exchange / live / broker / paper / order all False).

---

## 2. Decision

**Continue Crypto-D1 as the primary research lane for ONE more confirmation
pass.** The robustness evidence is strong enough in *direction* to justify a
focused confirmation, but not strong enough to change the lane verdict.
No promotion, no new data, no trading.

---

## 3. Recommendations (next research step)

1. **Focus next on N=20 and N=30 momentum only.** These are the best-sampled,
   floor-clearing lookbacks; the longer lookbacks are thin-sample and should be
   dropped from the confirmation pass (they remain on record in this report).
2. **Fix benchmark reporting first** (do this before any new strategy work):
   - The equal-weight buy-and-hold basket must be **allocate-once, not daily-
     rebalanced.** *(Note: `momentum_robustness_v1` already wired the
     allocate-once `buy_and_hold_basket_equal_weight` as the PRIMARY basket; the
     concrete remaining gap is that this single-stream basket reports
     `OOS_ret = None` — it has no per-basket IS/OOS split. The confirmation pass
     should add an OOS-window basket figure so the basket is comparable to the
     per-asset OOS strategy returns.)*
   - An **optional monthly-rebalanced** basket benchmark may be added later as an
     additive third variant; it is **not required** for the first confirmation
     pass.
3. **Keep the same V002 dataset** (`CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V002`,
   checksum-verified). No re-freeze.
4. **Keep the same IS/OOS split:** IS 2021-06-17 → 2024-06-16, OOS
   2024-06-17 → 2025-12-31 (explicit UTC date windows).
5. **Keep the same cost model:** fee 40 bps + slippage 10 bps + spread proxy
   10 bps = 60 bps/side, 120 bps round-trip (from the frozen V002 `fees.json`).
6. **Do not add new data yet.** Specification/analysis completeness is not data
   readiness; the missing-items checklist stays open.
7. **Do not promote ACTIVE / STRONG.** Lane stays WATCH / MIXED.
8. **Do not authorize paper or live trading.** Paper/live remain locked.
9. **Do not start Bundle 23.**
10. **Next implementation step:** produce a focused **Momentum Confirmation v1
    runner/report plan** (plan only) — scoped to N=20 + N=30, the basket OOS-
    reporting fix, the unchanged dataset/split/costs, and the conservative
    WATCH-ceiling classifier. No code, no run until separately approved.

---

## 4. Honesty / non-authorization statement

- The BTC gap on **2024-03-31** remains a true gap — flagged, never forward-
  filled or synthesized.
- A positive OOS result is **not** a trading signal and does **not** promote the
  lane. WATCH is the honest ceiling for this evidence.
- This memo changes no dataset, no QA report, no runner code, and no dashboard.
  It is a research-direction record only.
