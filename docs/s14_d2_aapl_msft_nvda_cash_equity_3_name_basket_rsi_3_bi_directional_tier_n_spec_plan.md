# S14-D2 cash-equity 3-name basket RSI(3) bi-directional Tier-N spec PLAN

**Status:** `PLAN_ONLY` (no DRAFT, no SEAL, no BUILD, no fetch, no signal computation, no backtest, no OOS, no live; the next step is a separate operator authorization to author the DRAFT).

**Authored:** 2026-05-27
**Authorization phrase (typed by operator this turn):**
`Ratify T2 rev2 as primary. Authorize s14-d1 cash-equity 3-name basket RSI(3) bi-directional Tier-N spec PLAN only — bound by DR10 v2.`

**Candidate_record_id (fresh):** `s14-d2-aapl-msft-nvda-cash-equity-3-name-basket-rsi-3-bi-directional`

**Naming note (s14-d2 vs s14-d1):** The rev2 plan §5.2 placeholder used `s14-d1-aapl-msft-nvda-...`, but commit `5376de7` (T1 micro-futures basket) has already taken the `s14-d1-...` prefix. To avoid candidate_record_id ambiguity in the orchestrator's phase classifier (which uses prefix matching on the candidate slug), this T2 candidate uses **`s14-d2-`** — following the established `s10-d1` / `s10-d2` convention where d-numbers distinguish structurally different candidates within the same s-number series. The s14 series contains:
- `s14-d1` micro-futures basket (T1; `PROVISIONAL_NOT_FULLY_RATIFIED` at `5376de7`; not advanced)
- `s14-d2` cash-equity 3-name basket (T2; this PLAN; **operator-ratified PRIMARY**)

**Bound by:** DR10 v2 AND-conjunction (per framework SEAL at `78cd22e` and governance supplement at `fdf9d6e`).

---

## 0. Parent references (pinned)

| Anchor | Commit | Sha (prefix) |
|---|---|---|
| DR10 v2 SEAL | `78cd22e` | report_seal `7794bb52…` |
| DR10 v2 governance supplement | `fdf9d6e` | report_seal `953ad6f3…` |
| Master reconciliation memo | `1e51680` | report_seal `e2714c8e…` |
| Rev2 next-track plan | `ee2bfc1` | md `11dffb7b…` |
| Rev2 governance supplement | `7d7bb52` | report_seal `eba24331…` |
| T1-vs-T2 comparison memo (RATIFY_T2_PRIMARY recommendation) | `18bc7b0` | report_seal `9d8d6a80…` |
| S14-D1 T1 micro-futures PLAN (PROVISIONAL) | `5376de7` | md `be53ca7e…` |
| S13-D1 SEAL (DR10 v1 canonical source) | `262491c` | report_seal `2f9d1763…` |
| S13-D1 P7 decision memo | `cc1817b` | file `ec5addcc…` |

---

## 1. HARD BOUNDARIES (held by this PLAN turn)

PLAN only. No DRAFT. No SEAL. No code. No backtest. No simulator. No signal computation. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No Polygon call. No Alpaca call. No IEX call. No `DATABENTO_API_KEY` access. No QC / LEAN call. No network IO. No `review_queue.json` mutation. No production `idea_memory` mutation. No Strategy Lab run. No candidate promotion. **No s13-d1 / s12-d1 / s10-d2 / s10-d1 / s9 / s7-d1 / B005 / B006 / T8 revival.** **No retroactive application of DR10 v2 to any existing sealed candidate.** **No reinterpretation of any existing sealed candidate's verdict.** **No modification of any existing sealed candidate artifact** (s11-d1 / s12-d1 / s13-d1 SEAL/P1/P2/P3/P4/P6/P6.5/P7 + framework_dr10_revision_seal_v2 + governance supplements + comparison memo all byte-stable). **No `5376de7` modification** (T1 micro-futures PLAN remains byte-stable as `PROVISIONAL_NOT_FULLY_RATIFIED`). **No T1 advancement.** No phase-2 safety contract template modification. No CLAUDE.md modification. No `.gitignore` modification. **No `brain_memory/projects/trading_bot/lessons.md` modification or staging.** No `tmp/` helper modification. No `app.py` or Research Orchestrator file modification. No branch change. No git push. No live trading. No paper trading. No profitability claim. No live-readiness claim. No OOS-confirmation claim. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

---

## 2. Strategic context: why T2 selected over T1 (per comparison memo `18bc7b0`)

Per the T1-vs-T2 comparison memo at `18bc7b0` (T2 = 45/60 vs T1 = 32/60; T2 wins 5 of 6 decision-matrix dimensions):

| Reason | Detail |
|---|---|
| **Stronger DR10 v2 cost-drag margin** | Cash-equity per-share commissions (~$0.005/share at retail brokers) are tiny vs per-share notional ($150-400 for large-cap names). S2 cost_drag typically 0.3-0.5% — **far below 5% threshold**. Under DR10 v2 AND-conjunction, cost_drag is the load-bearing branch; T2 is structurally robust here. T1 at DA4=B was ~4.7% (0.3pp from 5% flip — calibration-fragile). |
| **Lower contract-quantization issue** | Cash equities allow share-level granularity (1 share = ~$200 for AAPL). Micro-futures force contract-level granularity (1 MNQ = $30k notional minimum). At retail-scale start_cash, T1's contract-quantization forces per-trade notional ≥15% of start_cash. T2 has continuous sizing freedom. |
| **Operationally more meaningful** | T2 expands the diagnostic series to a **new asset class** (cash equity) for the first time. All prior candidates were futures (s7/s10/s11/s12/s13/B005/B006/T8) or ETFs (s9). Cross-asset evidence base broadens. |
| **Better framework integrity** | Choosing T2 over T1 demonstrates `GOV-RULE-CO-PRIMARY-OPERATOR-SELECTION-PHRASE-V1` (from `7d7bb52`) actually binds operator selection. Establishes precedent that autonomous-PLAN-progression (5376de7) does NOT foreclose operator-level decisions. |
| **T1 correlation caveat** | MNQ/MES/MYM/M2K are highly correlated US equity-index micros (pairwise corr typically >0.90-0.95; →1.0 in stress). A7 `effective_independent_bets` likely 1.5-2 (not 4); T1's K9 OOS 9/10 score in rev2 plan was conditional on A7=4 assumption. Honest A7 adjustment → effective K9 OOS ~51-68/y portfolio (borderline vs 50/y floor). |
| **T1 cost-drag caveat** | At DA4=B $100k, T1's S2 cost_drag ~4.7% requires actual MES/MYM/M2K commission + slippage precommit at SEAL; calibration-fragility on the DR10 v2 load-bearing branch. |

**T1 status under this PLAN:** `PROVISIONAL_NOT_FULLY_RATIFIED` per `7d7bb52` §6 — preserved byte-stable in repo, available for re-evaluation in a future selection turn, but **not advanced**. This T2 PLAN does NOT roll back 5376de7, does NOT modify 5376de7, and does NOT treat T1 as operator-selected.

---

## 3. Candidate concept

| Field | Value |
|---|---|
| Candidate_record_id | `s14-d2-aapl-msft-nvda-cash-equity-3-name-basket-rsi-3-bi-directional` |
| Mechanic family | F3-adjacent (RSI mean-reversion; slower period than s13-d1's RSI(2); bi-directional) |
| Mechanic detail (PLAN-time placeholder; locked at SEAL) | RSI(3) thresholds 15/55/85/45 (entry-long at RSI≤15; exit-long at RSI≥55; entry-short at RSI≥85; exit-short at RSI≤45); per-name max 1 position; portfolio-level cap |
| Universe (PLAN-time precommit) | `{AAPL, MSFT, NVDA}` (3-name US large-cap tech basket; SEAL may revise to a stronger universe with operator-typed selection — see §6 universe caveats) |
| Asset class | cash equity (US large-cap) |
| Sizing | DA3=B (0.5% per-trade risk; standard sizing — nano-sizing is no longer required under v2 per rev2 plan §5.2) |
| Cash | DA4=A or DA4=B or DA4=C (PLAN does NOT precommit DA4; SEAL locks DA4 after cost surface calibration in §9) |
| Bar interval | daily OHLCV (close-to-close; no intraday) |
| Direction | bi-directional (long and short) |
| Data scope | requires fresh daily OHLCV fetch (operator-side, **separate authorization required** — not authorized by this PLAN) |
| C1-C8 phase-2 safety contracts | carry by-reference with **C5 explicit extension for equity corporate actions** (see §6) |
| K-gates K1/K2/K4/K7/K8/K9/K12 | carry by-reference; K9 inviolate ≥100 closed trades; OOS K9 ≥50/y binding |
| DR rules DR1/DR2/DR3/DR4/DR5/DR6/DR7/DR9 | carry by-reference |
| **DR10 v2 AND-conjunction** | binding per `78cd22e` framework SEAL; evaluated at PLAN time in §8 and required at SEAL time per `7d7bb52` §9 |
| K9-reachability discipline | binding |
| DR10-reachability discipline (under v2 AND-conjunction) | binding |
| Lifecycle expected | PLAN → DRAFT → SEAL → P1 → P2 → P3 BUILD → P4 smoke → P6 IS → P6.5 cost-stress → P7 decision → P10 OOS → P11 lifecycle memo (each step requires separate operator-typed authorization; see §10) |

---

## 4. Non-revision attestation

This is a **fresh candidate_record_id**, NOT a revision of any prior candidate.

| Prior candidate | Why this is NOT a revision |
|---|---|
| **s13-d1** RSI(2) bi-directional MNQ.c.0 single-instrument | DIFFERENT asset class (cash equity vs micro-futures); DIFFERENT mechanic period (RSI(3) vs RSI(2)); DIFFERENT universe (3-name large-cap tech basket vs single MNQ.c.0); DIFFERENT sizing approach (DA4 left to SEAL vs DA4=C $200k); DIFFERENT cost surface (per-share commission + half-bid-ask vs per-contract commission + tick slippage). NOT T-FORBID-9 (T-FORBID-9 is "re-attempt RSI(2) bi-directional MNQ.c.0 with DA3=B + DA4=C" — different mechanic, different universe, different asset class). NOT T-FORBID-10 (T-FORBID-10 prohibits `_revN_` of s13-d1 parameters — this is a fresh candidate_record_id with materially different structure). NOT T-FORBID-12 (s13-d1 fired DR10 v1 on turnover; T2 clears DR10 v2 on cost_drag — different gate, different outcome at PLAN time). |
| **s12-d1** Donchian-15/8 daily MNQ.c.0 | DIFFERENT mechanic family (F3 RSI vs F1 Donchian); DIFFERENT asset class; DIFFERENT universe. |
| **s10-d2** cross-asset Donchian-no-pyramid reparam cap cost-stress | DIFFERENT mechanic family; DIFFERENT universe (3-name large-cap tech vs 4-market futures basket); DIFFERENT asset class; DIFFERENT cash scale. |
| **s9** RSI(2) cross-asset mean-reversion 4-ETF basket | **Closest prior lineage** (also RSI mean-reversion bi-directional on a basket). Why not a revision: DIFFERENT mechanic period (RSI(3) vs RSI(2) — 50% slower; structurally fewer signals); DIFFERENT universe (3-name single-stock large-cap tech vs 4-ETF basket — different instruments entirely; no shared ticker); DIFFERENT cost surface (per-share commission + half-bid-ask + SEC/FINRA fees on individual stocks vs ETF expense ratios + per-share commission); s9 was long-only, T2 is bi-directional. First-principles argument: s9 falsification was 4-ETF-basket-specific (DR2/DR3 negative-edge S0 PnL on that universe); T2 is a different test on different instruments with a different mechanic period. Operator must explicitly weigh this lineage burden at SEAL time per rev2 plan §5.2 Cons row 4. |
| **s7-d1** cross-asset Donchian no-pyramid (parked on concentration/USO dominance) | DIFFERENT mechanic family; DIFFERENT universe; concentration-risk lesson DOES carry forward (see §3 portfolio cap requirement). |
| **B005 / B006 / T8 lineage** | All futures/options lineage; different asset class. |
| **5376de7 s14-d1** T1 micro-futures basket (PROVISIONAL) | DIFFERENT asset class (cash equity vs micro-futures); DIFFERENT universe (3-name large-cap tech vs 4-equity-index-micros); DIFFERENT mechanic period (RSI(3) vs RSI(2)); fresh candidate_record_id (`s14-d2-` vs `s14-d1-`). T1 is preserved as `PROVISIONAL_NOT_FULLY_RATIFIED`; T2 (this PLAN) is the operator-ratified PRIMARY. |

**No revival. No reinterpretation. No reuse of any prior candidate's verdict or artifact.**

---

## 5. Data requirements

### 5.1 Equity OHLCV needed

| Field | Detail |
|---|---|
| Symbols | AAPL, MSFT, NVDA (PLAN-precommitted; SEAL may revise per §6 caveats) |
| Bar interval | daily OHLCV (open, high, low, close, volume); close-to-close adjusted for splits per §6.1 |
| IS window length | ~5 years (matching scale of s13-d1's ~4.6y MNQ window); exact dates locked at SEAL |
| OOS window length | ~2 years (post-IS holdout for K9 OOS evaluation; ≥50/y trade-count floor binding) |
| Adjustments | split-adjusted (CRSP-style); dividend handling per §6.2 |
| Data source (PLAN does NOT precommit) | One of: Databento equities · yfinance · Polygon.io · Alpaca · IEX Cloud. **SEAL-time selection required**; each source carries different sealed-CSV protocol adaptation cost (see §9). |

### 5.2 Data fetch authorization

**No data fetch is authorized by this PLAN.** Any fetch requires a separate operator-typed authorization phrase, e.g.:

```
Authorize s14-d2 cash-equity OHLCV fetch from <source> for {AAPL, MSFT, NVDA} only (operator-side; DR9-equivalent audit required).
```

The fetch turn must:
- Use the SEAL-precommitted source (not chosen ad-hoc)
- Produce sealed CSV files with documented sha256 anchors
- Run a DR9-equivalent audit (data continuity check; gap detection; holiday-aware bar count) for the equity calendar
- Be authored operator-side (not by this assistant) per CLAUDE.md "SPARTA Read-Only Default" guard

This PLAN turn does NOT fetch any data, does NOT make any network IO call, and does NOT access `DATABENTO_API_KEY` or any broker credential.

---

## 6. C5 / corporate action risk (explicit)

Equities have corporate actions that micro-futures do not. The C5 safety contract (corporate-action-handling) needs to be explicitly extended or authored for this PLAN. The following events MUST be handled per the contract:

### 6.1 Splits / reverse splits

- **Sealed CSV must carry split-adjusted prices** (CRSP-style backward adjustment: pre-split prices divided by split ratio).
- Trade-quantity tracking must account for split ratios (a position of 100 shares pre-split becomes 400 shares after a 4:1 split at no cost).
- Historical splits in PLAN-precommitted universe (informational; SEAL must verify against IS-window data):
  - AAPL: 7:1 (2014-06-09), 4:1 (2020-08-31) — both pre-IS-window-likely-start
  - MSFT: no splits since 2003
  - NVDA: 4:1 (2021-07-20), 10:1 (2024-06-10) — **both within plausible IS window**
- SEAL-time precommit required: which split-adjustment convention is used; whether sealed CSV is fully back-adjusted or whether split events are processed at runtime.

### 6.2 Dividends

- **Strategy precommitment at PLAN time:** non-reinvestment (cash account semantics; dividends are received but not auto-reinvested into additional shares). This avoids dividend-reinvestment look-ahead bias and matches realistic retail-account behavior.
- Dividend cash flows reduce per-share notional on ex-dividend date (price drop typically ~= dividend amount).
- Total return calculation: include dividends in P&L tracking but NOT in adjusted-price OHLCV signal computation (use unadjusted-for-dividend prices for RSI signal; track dividend income separately).
- SEAL-time precommit required: dividend tracking methodology; whether RSI is computed on price-only or total-return series.

### 6.3 Mergers / acquisitions / delistings

- AAPL, MSFT, NVDA are all S&P 100 names with no expected merger/acquisition risk in IS window — but **NOT zero risk**.
- If a universe member is delisted, merged, or acquired during the IS or OOS window, the candidate must specify:
  - **Substitution rule:** automatic shift to next-eligible name from a precommitted eligibility list (e.g., top-10 S&P 500 by market cap excluding current universe) — OR — close-and-do-not-replace (basket shrinks).
  - **PLAN precommit:** close-and-do-not-replace (basket shrinks to 2 names if one delists). This is the simpler rule; avoids look-ahead via eligibility-list maintenance.
  - SEAL must verify: no AAPL/MSFT/NVDA delisting events in IS+OOS window; if any found, candidate must be re-PLANned with a different universe.

### 6.4 Spin-offs

- Spin-offs create new entities (e.g., HPE from HPQ in 2015, AGN from PFE in 2007). PLAN-precommitted universe should have no spin-off events in IS+OOS window.
- If a spin-off occurs, the candidate must specify: spin-off shares are sold immediately at market open price; cash credited to account; original position size adjusted per spin-off ratio.
- SEAL must verify: no AAPL/MSFT/NVDA spin-off events in IS+OOS window.

### 6.5 Special dividends

- One-time large cash distributions (e.g., MSFT 2004 $3/share). Should be treated as regular dividend per §6.2 (cash to account; price drop on ex-date).
- SEAL must verify: any special-dividend events in IS+OOS window are documented and handled per §6.2.

### 6.6 Survivorship bias risk

- The PLAN-precommitted universe AAPL/MSFT/NVDA is **all currently-thriving** large-cap US tech. Selecting from this universe in 2026 carries survivorship bias for 2019-2025 IS window (these names outperformed; failure cases like NOK/BBRY/IBM are not represented).
- NVDA in particular had AI-driven outperformance 2023-2025 = regime-specific tailwind that may not generalize.
- SEAL must:
  - Document the universe-selection rationale verbatim (sector concentration acknowledgment + survivorship bias acknowledgment)
  - Precommit whether the universe is "frozen 3-name basket" (selection bias accepted) OR "rolling 3-name basket from precommitted eligibility list" (more robust but more complex)
- This PLAN precommits **frozen 3-name basket {AAPL, MSFT, NVDA}** — simplest and most reproducible. The diagnostic value is "did RSI(3) bi-directional work on these 3 names in 2019-2025?" — a precise question with a precise answer, even if not maximally generalizable.

### 6.7 C5 contract status

**C5 must be authored or extended before SEAL.** This PLAN flags the requirement; the actual C5 contract authoring is a separate operator-typed authorization scope. SEAL cannot proceed without an explicit C5-equity-extension.

---

## 7. Preliminary K9 reachability expectations

### 7.1 K9 inviolate ≥ 100 closed trades (PLAN-time estimate)

| Window | Length (y) | Required trades/y for K9 | Expected RSI(3) trades/y per name | 3-name basket expected | K9 status |
|---|---:|---|---|---|---|
| IS | ~5 | ≥ 20 | ~25-40 (slower than s13-d1's ~34/y RSI(2) on MNQ; RSI(3) is 50% slower so ~17-25/y per name) | 3 × 17-25 = 51-75/y | **CLEARS** (51 × 5 = 255 >> 100; 75 × 5 = 375) |
| **OOS** | **~2** | **≥ 50.0** | ~17-25 per name | 51-75/y | **CLEARS** (51 × 2 = 102 ≥ 100; 75 × 2 = 150 ≥ 100; basket trade rate >> floor) |

### 7.2 K9 OOS reachability caveat (per rev2 governance supplement §8)

Even though 3-name single-stock basket is **less correlated** than 4-equity-index-micros basket (which was T1's problem), the 3 large-cap US tech names AAPL/MSFT/NVDA still have meaningful positive correlation (pairwise typically 0.6-0.8 normal regimes; →0.85-0.95 in stress).

**A7 effective_independent_bets caveat (required at SEAL):**
- Linear extrapolation assumes A7=3 (one independent bet per name).
- Realistic A7 for 3-name large-cap US tech basket is likely 1.5-2.5 (sector concentration reduces effective independence).
- Effective trade count at A7=2: ~34-50/y portfolio (still likely clears 50/y OOS floor at the high end; borderline at the low end).
- **SEAL-time A7 evidence required** before claiming K9 OOS margin: computed from historical AAPL/MSFT/NVDA daily returns over IS window via correlation eigenvalue decomposition or equivalent.
- If A7 measured at SEAL is <1.5 (highly concentrated), K9 OOS margin is at risk and operator should consider:
  - Adding a 4th name from a different sector (financials/healthcare/energy) to lift A7
  - Substituting one tech name with a non-tech mega-cap (preserving 3-name basket size)
  - Or accepting the borderline K9 OOS margin with explicit acknowledgment

### 7.3 K9-reachability discipline binding

K9-reachability discipline (introduced post-s12-d1) is binding for this PLAN. SEAL artifact must include a K9-reachability table with computed trade-count expectations (not just extrapolated) from the actual SEAL-precommitted RSI(3) thresholds and IS-window date range.

---

## 8. Preliminary DR10 v2 reachability expectations

### 8.1 DR10 v2 AND-conjunction binding (per `78cd22e` and `fdf9d6e`)

```
DR10 v2: (annual_turnover > 0.50 AND S2_cost_drag > 0.05) -> REJECT_FAST
```

**Both branches must fire** for DR10 v2 to fire. Cost is the load-bearing branch.

### 8.2 PLAN-time DR10 v2 reachability table (placeholder; SEAL must recompute)

| Sizing assumption | Per-trade notional | Trades/y | annual_turnover | S2 cost_drag est. | DR10 v2 status |
|---|---|---|---|---|---|
| 0.5% risk × $200k = $1,000 risk; AAPL ATR ~$5 → 200 shares × $200 = $40,000 notional | $40,000 | 60-75 (basket) | ~25-30 (turnover branch fires: > 0.50) | ~0.3-0.5% (per-share commission ~$0.005/share × 200 shares = $1/trade = 0.0025% of $40k notional; + half-bid-ask ~0.1-0.3% + exchange + SEC/FINRA fees) | **CLEARS** (cost_drag << 5%; AND-conjunction does NOT fire) |
| 0.5% risk × $100k = $500 risk; 100 shares × $200 = $20,000 notional | $20,000 | 60-75 (basket) | ~12-15 (turnover branch fires) | ~0.5-1.0% (commission as fraction is larger at smaller notional but still well below 5%) | **CLEARS** with comfortable margin |
| 0.5% risk × $50k = $250 risk; 50 shares × $200 = $10,000 notional | $10,000 | 60-75 (basket) | ~6-8 (turnover branch fires) | ~1.0-2.0% (commission fraction is larger but still below 5%) | **CLEARS** |

### 8.3 DR10 v2 reachability caveat (per rev2 governance supplement §9)

Per `7d7bb52` §9, **SEAL-time precommit required**:
- Per-share commission rate from SEAL-selected broker fee schedule (e.g., IBKR: $0.0035/share + exchange fees; Schwab: $0/trade + SEC/FINRA; Alpaca: $0/trade)
- Half-bid-ask slippage measured from sealed CSV (using bid-ask spread proxy or executing-broker quote history)
- Exchange fees + SEC/FINRA TAF (regulatory passthroughs)
- Full S2 cost_drag computed at SEAL-precommitted DA4 with actual cost model — NOT extrapolated from a placeholder

**Calibration robustness:** even at smallest reasonable retail DA4 ($50k), expected S2 cost_drag is ~1-2% (well below 5%). DR10 v2 has comfortable margin on the load-bearing branch for cash equities — this is the operationally most robust feature of T2 over T1.

### 8.4 DR10-reachability discipline binding (under v2 AND-conjunction)

DR10-reachability discipline (introduced post-s13-d1) is binding for this PLAN. SEAL artifact must include an explicit DR10-v2-reachability table per §8.2 format with actual SEAL-precommitted DA4 and computed cost surface.

---

## 9. Cost model assumptions that must be resolved before SEAL

| # | Assumption | Status | Required at SEAL |
|---|---|---|---|
| 1 | Per-share commission rate | NOT precommitted at PLAN | Lock to specific broker fee schedule (precommit broker by name); document URL/screenshot of fee schedule at time of SEAL |
| 2 | Half-bid-ask slippage | NOT precommitted at PLAN | Measure from sealed CSV bar-level quote data OR from a documented spread proxy (e.g., effective spread estimate from TAQ; or 1-2 basis points minimum for large-cap names) |
| 3 | Exchange fees | NOT precommitted at PLAN | Source from broker fee schedule; typically <$0.001/share for liquid large-cap names |
| 4 | SEC fees (sell-side only) | NOT precommitted at PLAN | Current rate (~$8/$1M of sale proceeds; SEC fee #31); negligible at retail-scale notional but include for completeness |
| 5 | FINRA TAF (sell-side only) | NOT precommitted at PLAN | Current rate (~$0.000166/share); negligible but include |
| 6 | Cost scalar | s13-d1 used 1.5x for cost-stress S2 | Precommit at SEAL (likely 1.5x for parity with s13-d1 lineage) |
| 7 | Dividend tracking methodology | §6.2 precommits non-reinvestment | Confirm at SEAL; document P&L attribution rule |
| 8 | Split-adjustment convention | §6.1 precommits CRSP-style back-adjustment | Confirm at SEAL; verify against sealed CSV |
| 9 | DA4 (start_cash) | NOT precommitted at PLAN | Lock at SEAL after §8 reachability validation; recommended range $100k-$200k for clean DR10 v2 margin |
| 10 | Cost surface byte-equivalent reproducibility | s13-d1 P6.5 byte-reproduced S0-S4 via documented cost model | SEAL must specify the cost model formula in machine-checkable form (per `cc1817b` reproducibility standard) |

---

## 10. Phase ladder (each step requires separate operator-typed authorization)

```
PLAN (this turn)
  ↓ requires: Authorize s14-d2 cash-equity 3-name basket RSI(3) Tier-N spec DRAFT only.
DRAFT
  ↓ requires: Authorize s14-d2 cash-equity 3-name basket RSI(3) Tier-N spec SEAL only.
SEAL
  ↓ requires: Authorize s14-d2 cash-equity OHLCV fetch from <source> for {AAPL, MSFT, NVDA} only.
  ↓ + requires: Authorize s14-d2 C5-equity-corporate-action contract extension only.
[FETCH + C5 EXTENSION — operator-side data + framework prerequisites]
  ↓ requires: Authorize s14-d2 P1 plan-lock only.
P1 (plan-lock; A-gates + DA-axes precommit)
  ↓ requires: Authorize s14-d2 P2 phase-2 safety contracts only.
P2 (C1-C8 safety contracts; K-gates K1/K2/K4/K7/K8/K9/K12 declaration)
  ↓ requires: Authorize s14-d2 P3 BUILD only.
P3 BUILD (runner + IS + OOS scaffolding; OOS NEVER read until P10)
  ↓ requires: Authorize s14-d2 P4 synthetic smoke only.
P4 (synthetic smoke battery)
  ↓ requires: Authorize s14-d2 P6 IS diagnostic only.
P6 IS (in-sample diagnostic; K9 ≥100 trades evaluation)
  ↓ requires: Authorize s14-d2 P6.5 cost-stress matrix only.
P6.5 (S0-S4 cost-stress sweep; DR10 v2 AND-conjunction evaluation; DR5 cost-stress tier-flip evaluation)
  ↓ requires: Authorize s14-d2 P7 decision memo only.
P7 (decision memo: ADVANCE / REJECT_FAST / REJECT / DEFER)
  ↓ if ADVANCE only: requires: Authorize s14-d2 P10 OOS only.
P10 OOS (out-of-sample evaluation; OOS K9 ≥50/y binding)
  ↓ requires: Authorize s14-d2 P11 lifecycle memo only.
P11 (lifecycle memo: TERMINAL / PARK / ADVANCE-TO-STRATEGY-LAB)
```

**No phase advances autonomously.** Each transition requires a separate operator-typed phrase. Per `GOV-RULE-FRAMEWORK-REVISION-OPERATOR-PHRASE-V1` (from `fdf9d6e`) and `GOV-RULE-CO-PRIMARY-OPERATOR-SELECTION-PHRASE-V1` (from `7d7bb52`), parallel-session autonomous progression is preserved as PROVISIONAL but does NOT satisfy operator authorization.

---

## 11. Hard boundaries summary

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT / no SEAL / no BUILD / no fetch) | met |
| No strategy code | met |
| No backtest / simulator / signal computation | met |
| No RSI computed | met |
| No data fetch / Databento / yfinance / Polygon / Alpaca / IEX / broker | met |
| No `DATABENTO_API_KEY` access | met |
| No network IO | met |
| No live trading / no paper trading | met |
| No candidate promotion / no Strategy Lab run | met |
| No retroactive application of DR10 v2 to any existing sealed candidate | met |
| No reinterpretation of any existing sealed candidate's verdict | met |
| No modification of any existing sealed candidate artifact | met |
| **No s13-d1 / s12-d1 / s10-d2 / s10-d1 / s9 / s7-d1 / B005 / B006 / T8 revival** | met |
| **No 5376de7 (T1 micro-futures) modification or advancement** | met |
| **No T1 ratification** (T1 remains PROVISIONAL_NOT_FULLY_RATIFIED) | met |
| No DR10 v2 modification | met |
| No DR10 v2 SEAL modification (`78cd22e` byte-stable) | met |
| No governance supplement modification (`fdf9d6e` / `7d7bb52` byte-stable) | met |
| No comparison memo modification (`18bc7b0` byte-stable) | met |
| No master memo modification (`1e51680` byte-stable) | met |
| No rev2 plan modification (`ee2bfc1` byte-stable) | met |
| No phase-2 safety contract template modification | met |
| No CLAUDE.md / RUNBOOK / pipeline_manifest / `.gitignore` modification | met |
| **No `brain_memory/projects/trading_bot/lessons.md` modification or staging** | met |
| No `tmp/` helper modification | met |
| No `app.py` or Research Orchestrator file modification | met |
| No mutation of `review_queue.json` | met |
| No mutation of production `idea_memory` | met |
| No profitability claim | met |
| No live-readiness claim | met |
| No OOS-confirmation claim | met |
| Trading status | `PAUSED` |
| Live status | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` (per existing sealed candidates) | TRUE |
| K9-reachability discipline | binding (carried) |
| DR10-reachability discipline under v2 AND-conjunction | binding (carried) |
| `GOV-RULE-FRAMEWORK-REVISION-OPERATOR-PHRASE-V1` | binding (carried from `fdf9d6e`) |
| `GOV-RULE-CO-PRIMARY-OPERATOR-SELECTION-PHRASE-V1` | binding (carried from `7d7bb52`) |
| All T-FORBID-1..12 forbidden tracks | carried (T-FORBID-9/10/12 explicitly addressed in §4) |

---

## 12. Carry-forward status (UNCHANGED across this PLAN turn)

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` advisory label applies to this candidate and all descendants | TRUE |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` (per existing sealed candidates) | TRUE |
| **DR10 v2 future-only framework** | binding for s14+ NEW SEAL turns (per `78cd22e`) |
| **All existing candidate verdicts under DR10 v1** | preserved byte-equivalent and immutable |
| **S13-D1 REJECT_FAST terminal state** | preserved verbatim under DR10 v1 |
| **T1 (s14-d1) provisional status** | `PROVISIONAL_NOT_FULLY_RATIFIED` per `7d7bb52` §6; PLAN at `5376de7` preserved byte-stable; NOT advanced |
| s12-d1 lifecycle terminal | TRUE — preserved |
| s11-d1 / s10-d2 / s10-d1 / s9 / s7-d1 / B005 / B006 / T8 byte-stable | TRUE — preserved |
| `lessons.md` dirty + unstaged + uncommitted (NOT touched this turn) | TRUE |
| K9-reachability discipline | binding |
| DR10-reachability discipline under DR10 v2 AND-conjunction | binding |

---

## 13. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/s14_d2_aapl_msft_nvda_cash_equity_3_name_basket_rsi_3_bi_directional_tier_n_spec_plan.md` | This PLAN (PLAN-only; no JSON sidecar; no canonical seal sha256 since this is a planning document, not a sealed Tier-N or framework artifact — sealing happens at SEAL phase per §10) |

No other repository file is modified. The `brain_memory/projects/trading_bot/lessons.md` dirty + unstaged state from prior controller sessions remains **untouched**. The `tmp/` helpers remain untouched. The `app.py` and Research Orchestrator files remain untouched. The `5376de7` T1 PLAN remains byte-stable.

---

## 14. Next-step authorization scope

```
Authorize s14-d2 cash-equity 3-name basket RSI(3) Tier-N spec DRAFT only.
```

Authors the DRAFT artifact (DA1-DA20 axis register; F-family lock; A-gates; K-gates declaration; first-principles burden vs s9 explicit; universe-selection rationale verbatim; C1-C8 carry-over with C5 extension placeholder).

DRAFT-only; no SEAL/FETCH/BUILD until separately authorized.

---

End of s14-d2 Tier-N spec PLAN. PLAN-authoring turn only. No code. No backtest. No simulator. No signal. No data fetch. No Databento. No yfinance / Polygon / Alpaca / IEX. No `DATABENTO_API_KEY` access. No QC. No LEAN. No brokerage. No real order. No paper order. No Strategy Lab promotion. No `review_queue` mutation. No production `idea_memory` mutation. **No retroactive application of DR10 v2 to existing candidates. No s13-d1 / s12-d1 / parked-candidate revival. No T1 (5376de7) advancement or modification. No `lessons.md` modification or staging.** No live trading. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`. s13-d1 lifecycle terminal preserved verbatim under DR10 v1. T1 (s14-d1) remains `PROVISIONAL_NOT_FULLY_RATIFIED`.
