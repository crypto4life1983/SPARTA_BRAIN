# S14-D2 cash-equity 3-name basket RSI(3) bi-directional Tier-N spec DRAFT

**Status:** `DRAFT_ONLY` (PLAN accepted; SEAL/FETCH/BUILD/diagnostic NOT authorized by this DRAFT; each next step requires separate operator-typed authorization phrase per `GOV-RULE-FRAMEWORK-REVISION-OPERATOR-PHRASE-V1` and `GOV-RULE-CO-PRIMARY-OPERATOR-SELECTION-PHRASE-V1`).

**Authored:** 2026-05-27
**Authorization phrase (typed by operator this turn):**
`Authorize s14-d2 cash-equity 3-name basket RSI(3) Tier-N spec DRAFT only.`

**Candidate_record_id:** `s14-d2-aapl-msft-nvda-cash-equity-3-name-basket-rsi-3-bi-directional`

**Binding PLAN source:** commit `373eac8` (`docs/s14_d2_aapl_msft_nvda_cash_equity_3_name_basket_rsi_3_bi_directional_tier_n_spec_plan.md`).

**Bound by:** DR10 v2 AND-conjunction (per framework SEAL at `78cd22e` and governance supplement at `fdf9d6e`).

---

## 0. Parent references (pinned)

| Anchor | Commit | Sha (prefix) |
|---|---|---|
| S14-D2 PLAN (binding source) | `373eac8` | (md committed this DRAFT's parent commit) |
| DR10 v2 SEAL | `78cd22e` | report_seal `7794bb52…` |
| DR10 v2 governance supplement | `fdf9d6e` | report_seal `953ad6f3…` |
| Master reconciliation memo | `1e51680` | report_seal `e2714c8e…` |
| Rev2 next-track plan | `ee2bfc1` | md `11dffb7b…` |
| Rev2 governance supplement | `7d7bb52` | report_seal `eba24331…` |
| T1-vs-T2 comparison memo (RATIFY_T2_PRIMARY) | `18bc7b0` | report_seal `9d8d6a80…` |
| S14-D1 T1 micro-futures PLAN (PROVISIONAL) | `5376de7` | md `be53ca7e…` |
| S13-D1 SEAL (DR10 v1 canonical source) | `262491c` | report_seal `2f9d1763…` |
| S13-D1 P7 decision memo | `cc1817b` | file `ec5addcc…` |

---

## 1. HARD BOUNDARIES (held by this DRAFT turn)

DRAFT only. No SEAL. No FETCH. No BUILD. No code. No backtest. No simulator. No signal computation. No data fetch. No yfinance / Yahoo Finance / Polygon / Alpaca / IEX / Databento equities call. No `DATABENTO_API_KEY` access. No broker / exchange API call. No QC / LEAN call. No network IO. No `review_queue.json` mutation. No production `idea_memory` mutation. No Strategy Lab run. No candidate promotion. **No s13-d1 / s12-d1 / s10-d2 / s10-d1 / s9 / s7-d1 / B005 / B006 / T8 revival.** **No retroactive application of DR10 v2 to any existing sealed candidate.** **No reinterpretation of any existing sealed candidate's verdict.** **No modification of any existing sealed candidate artifact** (s11-d1 / s12-d1 / s13-d1 chain + framework_dr10_revision_seal_v2 + governance supplements + comparison memo + S14-D2 PLAN all byte-stable). **No `5376de7` modification** (T1 micro-futures PLAN remains byte-stable as `PROVISIONAL_NOT_FULLY_RATIFIED`). **No T1 advancement.** No phase-2 safety contract template modification. No CLAUDE.md modification. No `.gitignore` modification. **No `brain_memory/projects/trading_bot/lessons.md` modification or staging.** No `tmp/` helper modification. No `app.py` or Research Orchestrator file modification. No branch change. No git push. No live trading. No paper trading. No profitability claim. No live-readiness claim. No OOS-confirmation claim. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

---

## 2. Acceptance of PLAN 373eac8 as binding source

This DRAFT accepts `373eac8` (S14-D2 cash-equity Tier-N spec PLAN) as the **binding PLAN source**. Every concept, constraint, K-gate, DR-rule binding, hard boundary, phase ladder, and posture invariant declared in the PLAN is **carried by-reference into this DRAFT verbatim**. Where the PLAN defers a decision to SEAL (e.g., DA4, data source, broker fee schedule), this DRAFT does not pre-empt — the SEAL turn remains the locking point.

Where the PLAN left a definition deliberately as "PLAN-time placeholder; locked at SEAL", this DRAFT either:
- (a) **LOCKS the definition at DRAFT** when no further information is needed and SEAL would only ratify, OR
- (b) **DEFERS the definition to SEAL** when material new information is required (cost surface measurement, A7 evidence, broker selection).

Each ambiguity is explicitly labeled in §8 (DA register).

---

## 3. Candidate concept (locked from PLAN; see §8 for DRAFT-time locks and SEAL-deferred items)

| Field | Value | Lock status |
|---|---|---|
| Candidate_record_id | `s14-d2-aapl-msft-nvda-cash-equity-3-name-basket-rsi-3-bi-directional` | LOCKED at PLAN |
| Mechanic family | F3-adjacent (RSI mean-reversion; slower period than s13-d1's RSI(2); bi-directional) | LOCKED at PLAN |
| **Mechanic detail** | RSI(3) close-to-close; entry-long at RSI ≤ 15; exit-long at RSI ≥ 55; entry-short at RSI ≥ 85; exit-short at RSI ≤ 45; per-name max 1 position; portfolio-level cap K11-style | **LOCKED at DRAFT (§4)** |
| Universe (PLAN precommit) | `{AAPL, MSFT, NVDA}` frozen 3-name | LOCKED at PLAN (universe-selection rationale to be documented at SEAL per PLAN §6.6) |
| Asset class | cash equity (US large-cap) | LOCKED at PLAN |
| Sizing risk | DA3=B (0.5% per-trade risk) | LOCKED at PLAN |
| Starting cash (DA4) | DA4=A $100k OR DA4=B $200k (DRAFT recommends B $200k for cleanest DR10 v2 cost_drag margin; see §11) | **SEAL-DEFERRED with DRAFT-time recommendation** |
| Bar interval | daily OHLCV close-to-close (no intraday) | LOCKED at PLAN |
| Direction | bi-directional (long and short) | LOCKED at PLAN |
| Data source | one of: Databento equities · Polygon · Alpaca · IEX · yfinance (see §10) | SEAL-DEFERRED |
| Broker (for fee schedule) | one of: IBKR · Schwab · Alpaca · Fidelity (see §11) | SEAL-DEFERRED |
| C1-C8 phase-2 safety contracts | carry by-reference with **C5 explicit extension** (see §9) | C5 extension authorship scope is SEPARATE from this DRAFT |
| K-gates K1/K2/K4/K7/K8/K9/K12 | carry by-reference; K9 inviolate ≥ 100 closed trades; K9 OOS ≥ 50/y binding | LOCKED at framework level |
| DR rules DR1/DR2/DR3/DR4/DR5/DR6/DR7/DR9 | carry by-reference | LOCKED at framework level |
| **DR10 v2 AND-conjunction** | `(annual_turnover > 0.50 AND S2_cost_drag > 0.05) → REJECT_FAST` | LOCKED at framework level (per `78cd22e`) |
| K9-reachability discipline | binding | LOCKED at framework level |
| DR10-reachability discipline (under v2 AND-conjunction) | binding | LOCKED at framework level |
| Lifecycle expected | PLAN → DRAFT (THIS) → SEAL → C5+FETCH → P1 → P2 → P3 BUILD → P4 → P6 IS → P6.5 → P7 → P10 OOS → P11 | Phase ladder LOCKED at PLAN; each next phase requires separate operator-typed authorization |

---

## 4. DRAFT-time locks for mechanic detail

The PLAN §3 left mechanic detail as "PLAN-time placeholder; locked at SEAL". This DRAFT locks the mechanic at DRAFT time (not SEAL) because the values are precise, defensible, and require no further information to commit. SEAL will simply ratify these locks.

### 4.1 RSI period

**LOCKED at DRAFT: RSI period = 3 (daily bars)**.

Rationale:
- Rev2 plan §5.2 recommended RSI(3) as "slower than s13-d1's RSI(2); reduces signal density vs s13-d1; more selective entries with potentially higher edge per trade"
- RSI(3) provides ~50% fewer signals than RSI(2) per the rev2 plan's first-principles estimate (~17-25/y per name vs ~34/y for RSI(2) on MNQ)
- Computationally trivial; deterministic from sealed CSV close prices
- No alternative period is competitive at PLAN level (RSI(2) is T-FORBID-9-adjacent; RSI(5)/RSI(7) would reduce signal density further and likely fail K9 OOS per rev2 plan §5.3 T3 rev2 analysis)

### 4.2 Long-entry threshold

**LOCKED at DRAFT: enter long when RSI(3) ≤ 15** (close-to-close; signal computed on bar close; position entered at next bar open).

Rationale:
- Rev2 plan §5.2 placeholder was "thresholds 15/55/85/45"; this DRAFT carries that lock verbatim
- 15 is the Connors-style "oversold extreme" for RSI(3); empirically used in mean-reversion equity strategies
- Symmetric with short-entry at 85 (= 100 - 15)
- More conservative than s13-d1's RSI(2) entry at 10 (Connors-style "extreme oversold for fast RSI") — fewer false signals on cash equity which tends to mean-revert from less-extreme levels than futures

### 4.3 Long-exit threshold

**LOCKED at DRAFT: exit long when RSI(3) ≥ 55** (close-to-close; signal at bar close; position exited at next bar open).

Rationale:
- Rev2 plan §5.2 placeholder; carried verbatim
- 55 is "above neutral" but not "overbought" — captures mean-reversion-completion without waiting for full reversal
- Faster exit than wait-for-opposite-signal (which would be 85); reduces per-trade hold time and protects against trend-continuation losses
- Symmetric with short-exit at 45 (= 100 - 55)

### 4.4 Short-entry threshold

**LOCKED at DRAFT: enter short when RSI(3) ≥ 85** (close-to-close; signal at bar close; position entered at next bar open).

Rationale: symmetric counterpart of long-entry at 15; "overbought extreme" for RSI(3); admissible for cash equities (which can be shorted via margin; SEAL must precommit margin/borrow handling per §9).

### 4.5 Short-exit threshold

**LOCKED at DRAFT: exit short when RSI(3) ≤ 45** (close-to-close; signal at bar close; position exited at next bar open).

Rationale: symmetric counterpart of long-exit at 55; "below neutral" exit; mirrors long-side discipline.

### 4.6 Per-name position cap

**LOCKED at DRAFT: maximum 1 position per name at any time**.

- If a long position is open on AAPL and the long-entry signal fires again, no new position is added (no pyramiding).
- If a short-entry signal fires on AAPL while a long is open, the long position is closed FIRST (exit-long signal also fires implicitly at RSI ≥ 85 ≥ 55), then the short is entered on the next bar.
- This matches s13-d1's per-instrument single-position discipline.

### 4.7 Portfolio-level position cap (DA7-style)

**LOCKED at DRAFT: maximum 3 simultaneous positions (one per name); no portfolio leverage**.

- At any time, the portfolio holds 0, 1, 2, or 3 positions across {AAPL, MSFT, NVDA}.
- Each position is sized to 0.5% of CURRENT equity per the DA3=B sizing rule.
- No portfolio-level leverage beyond what individual positions imply.
- This is the K11-style portfolio cap. SEAL must explicitly precommit whether equity calculation uses end-of-day mark-to-market or trade-cost-basis (see §8 DA13).

### 4.8 Signal compute timing + execution timing

**LOCKED at DRAFT:**
- RSI(3) computed on close prices at bar close (T)
- Signal evaluation at bar close (T)
- Order placed at next bar open (T+1)
- Fill price = next bar open price (no intraday slippage modeling beyond §11 spread)
- This matches s13-d1's signal/execution convention.

### 4.9 Warmup

**LOCKED at DRAFT: RSI(3) warmup = 14 bars** (standard RSI smoothing convergence; >> 3-period; conservative).

- No trades during warmup window
- Sealed CSV must contain ≥14 bars before first allowed trade date

---

## 5. T2 ratified primary; T1 provisional / not advanced

**Attested at DRAFT level:**

- T2 (this candidate; `s14-d2-…`) is the **operator-ratified PRIMARY** track per:
  - Comparison memo `18bc7b0` recommendation `RATIFY_T2_PRIMARY` (T2 = 45/60 vs T1 = 32/60)
  - Operator-typed ratification phrase at S14-D2 PLAN `373eac8` authoring turn
  - Operator-typed DRAFT authorization phrase this turn
- T1 (`s14-d1-mnq-mes-mym-m2k-…` at `5376de7`) remains **`PROVISIONAL_NOT_FULLY_RATIFIED`** per:
  - Rev2 governance supplement `7d7bb52` §6 (rollback NOT authorized; treated_as_fully_operator_ratified=False)
  - S14-D2 PLAN `373eac8` §2 (T1 status under this PLAN: PROVISIONAL_NOT_FULLY_RATIFIED; preserved byte-stable; not advanced)
  - This DRAFT (hard boundary §1: "No `5376de7` modification"; "No T1 advancement")

T1's PLAN file remains byte-stable in repo for potential re-evaluation in a future selection turn. This DRAFT does NOT roll back T1, does NOT modify T1, and does NOT treat T1 as operator-selected.

---

## 6. Fresh-candidate non-revision attestation

This is a **fresh candidate_record_id**. NOT a revision of any prior candidate.

| Prior candidate | Why this is NOT a revision (DRAFT-level attestation) |
|---|---|
| **s13-d1** RSI(2) bi-directional MNQ.c.0 single-instrument | DIFFERENT asset class (cash equity vs micro-futures); DIFFERENT mechanic period (RSI(3) vs RSI(2)); DIFFERENT universe (3-name cash-equity tech basket vs single MNQ.c.0); DIFFERENT cost surface (per-share commission + half-bid-ask + SEC/FINRA fees vs per-contract commission + tick slippage); DIFFERENT direction-handling specifics (cash-equity short requires borrow + margin per §9.4 vs MNQ short is symmetric in futures). NOT T-FORBID-9 (T-FORBID-9 = "re-attempt RSI(2) bi-directional MNQ.c.0 with DA3=B + DA4=C"; T2 is a different mechanic + universe + asset class). NOT T-FORBID-10 (T-FORBID-10 prohibits `_revN_` of s13-d1; this is a fresh candidate_record_id). NOT T-FORBID-12 (s13-d1 fired DR10 v1 on turnover branch alone; T2 clears DR10 v2 by cost_drag <<5% on the load-bearing branch — different gate, different expected outcome). |
| **s12-d1** Donchian-15/8 daily MNQ.c.0 | DIFFERENT mechanic family (F3 RSI vs F1 Donchian); DIFFERENT asset class; DIFFERENT universe. |
| **s10-d2** cross-asset Donchian-no-pyramid reparam cap cost-stress | DIFFERENT mechanic family; DIFFERENT universe; DIFFERENT asset class; DIFFERENT cash scale. |
| **s9** RSI(2) cross-asset mean-reversion 4-ETF basket | Closest prior lineage. NOT a revision because: DIFFERENT mechanic period (RSI(3) vs RSI(2) — 50% slower; structurally fewer signals); DIFFERENT universe (3-name single-stock large-cap tech vs 4-ETF basket; no shared ticker); DIFFERENT cost surface (per-share commission + half-bid-ask + SEC/FINRA fees on individual stocks vs ETF expense ratios + per-share commission); s9 was long-only, T2 is bi-directional. s9 falsification was 4-ETF-basket-specific (DR2/DR3 negative-edge S0 PnL on that universe); T2 is a different test on different instruments with different mechanic period + direction. SEAL must explicitly weigh this lineage burden verbatim per S14-D2 PLAN §4 row 4. |
| **s7-d1** cross-asset Donchian no-pyramid (parked on concentration/USO dominance) | DIFFERENT mechanic family; DIFFERENT universe; concentration-risk lesson carries (informs §7 A7 warning). |
| **B005 / B006 / T8 lineage** | All futures/options lineage; different asset class. |
| **5376de7 s14-d1** T1 micro-futures basket (PROVISIONAL) | DIFFERENT asset class (cash equity vs micro-futures); DIFFERENT universe; DIFFERENT mechanic period (RSI(3) vs RSI(2)); fresh candidate_record_id (`s14-d2-` vs `s14-d1-`). |

**No revival. No reinterpretation. No reuse of any prior candidate's verdict or artifact.**

---

## 7. A7 / effective_independent_bets warning (DRAFT-level)

**AAPL/MSFT/NVDA may be highly correlated mega-cap US tech.**

### 7.1 Correlation expectations (prior-belief, NOT computed this turn)

| Pair | Expected pairwise correlation (daily returns, normal regime) | Expected (stress regime) |
|---|---|---|
| AAPL-MSFT | ~0.55-0.75 | ~0.75-0.90 |
| AAPL-NVDA | ~0.45-0.65 | ~0.70-0.85 |
| MSFT-NVDA | ~0.50-0.70 | ~0.75-0.90 |

(These are prior expectations only. No correlation has been computed by this DRAFT. SEAL-time A7 measurement is required per §7.3.)

### 7.2 Effective independent bets (A7) implications

If the average pairwise correlation is ~0.6 in normal regime:
- Naive A7 = 3 (one per name)
- Eigenvalue-decomposition A7 ≈ 1.5-2.0 (sector + market-factor concentration reduces effective independence)

If A7 ≈ 2.0:
- K9 OOS extrapolation `3 × 25/y = 75/y` becomes `~2 × 25/y = 50/y` effectively
- This is **AT the K9 OOS floor of 50/y** — borderline-clears, not strong margin
- This is the load-bearing K9 caveat for T2 (analogous to T1's correlated equity-index micros caveat, but less severe because cash-equity single names have somewhat lower correlation than equity-index micros)

### 7.3 SEAL-time A7 evidence required

Per S14-D2 PLAN §7.2 and rev2 governance supplement `7d7bb52` §8: SEAL artifact must include:
- Computed pairwise daily-return correlation matrix for {AAPL, MSFT, NVDA} over the IS window
- A7 `effective_independent_bets` via correlation eigenvalue decomposition: `A7 = (sum(eigenvalues))^2 / sum(eigenvalues^2)` (effective rank metric) OR `A7 = 1 / sum(weights * eigenvalue_fraction)` (concentration-adjusted)
- Stress-regime sub-period A7 (e.g., 2020-Q1 COVID, 2022 rate-hike cycle, 2025-Q3-Q4 if any documented stress)
- **If SEAL-measured A7 < 1.5 (highly concentrated), one of the following mitigations is required:**
  - Add a 4th name from a different sector (e.g., financials JPM, healthcare JNJ, energy XOM, consumer staples PG) to lift A7 toward ≥ 2.5
  - Substitute one tech name with a non-tech mega-cap (preserving 3-name basket size)
  - OR document explicit operator acceptance of borderline K9 OOS margin (with re-PLAN if borderline becomes unacceptable)

### 7.4 What this DRAFT does NOT compute

This DRAFT does NOT:
- Compute any correlation, eigenvalue decomposition, A7 metric, or signal
- Fetch any daily-return data
- Read any sealed CSV
- Run any historical analysis

All measurements are **SEAL-time requirements only** under separate authorization.

---

## 8. DRAFT ambiguity register (DA1-DA20)

| # | Axis | Status | Locked value (if locked) | SEAL-time requirement (if deferred) |
|---|---|---|---|---|
| DA1 | Bar interval | LOCKED at PLAN | daily OHLCV close-to-close | — |
| DA2 | Direction | LOCKED at PLAN | bi-directional (long + short) | — |
| DA3 | Risk per trade | LOCKED at PLAN | DA3=B (0.5% per-trade risk on current equity) | — |
| DA4 | Starting cash | SEAL-DEFERRED (DRAFT recommends DA4=B $200k) | — | Lock to one of DA4=A $100k or DA4=B $200k; DRAFT recommends DA4=B for cleanest DR10 v2 cost_drag margin per §11 |
| DA5 | Warmup window | LOCKED at DRAFT | 14 bars (RSI(3) smoothing convergence) | — |
| DA6 | Signal/execution timing | LOCKED at DRAFT | signal at bar close T; order at next bar open T+1 (no intraday) | — |
| DA7 | Per-name position cap | LOCKED at DRAFT | max 1 position per name; no pyramiding | — |
| DA8 | Portfolio position cap (K11-style) | LOCKED at DRAFT | max 3 simultaneous positions (one per name); no portfolio leverage | — |
| DA9 | Stop type | SEAL-DEFERRED | — | Lock to: (a) no hard stop (RSI exit only) OR (b) ATR stop (e.g., 2× ATR(14) below entry for long); DRAFT recommends (a) for parity with s13-d1 lineage and to keep mechanic mechanically simple |
| DA10 | Re-entry cooldown | LOCKED at DRAFT | none beyond per-name position cap (DA7); a new signal after exit is admissible on next bar | — |
| DA11 | Exit on opposing signal | LOCKED at DRAFT | YES (long-exit at RSI ≥ 55 fires before short-entry at RSI ≥ 85; mechanic resolves naturally) | — |
| DA12 | Time-in-force / max hold | SEAL-DEFERRED | — | Lock to: (a) hold until RSI exit signal (no time limit) OR (b) max hold N bars (e.g., 20 bars; cf. s13-d1 max hold); DRAFT recommends (a) |
| DA13 | Equity calculation for sizing | SEAL-DEFERRED | — | Lock to: (a) end-of-day mark-to-market equity OR (b) trade-cost-basis equity; DRAFT recommends (a) (industry standard) |
| DA14 | Cost-tier convention (S0-S4) | LOCKED at framework | DA14=A byte-equivalent (s11-lineage; carries to all candidates) | — |
| DA15 | Dividend handling | LOCKED at PLAN | non-reinvestment (cash account semantics); price-only series for RSI signal; dividend cash flow tracked separately in P&L | — |
| DA16 | Split handling | LOCKED at PLAN | CRSP-style backward-adjusted sealed CSV; trade-quantity tracking adjusts per split ratio (no cost) | — |
| DA17 | Universe source / eligibility | LOCKED at PLAN | frozen 3-name {AAPL, MSFT, NVDA}; close-and-do-not-replace on delisting (basket shrinks per PLAN §6.3) | — |
| DA18 | Data vendor | SEAL-DEFERRED | — | Lock to one of: Databento equities · Polygon · Alpaca · IEX · yfinance per §10 SEAL-time decision matrix |
| DA19 | Data audit methodology | SEAL-DEFERRED | — | Lock to vendor-specific DR9-equivalent audit; minimum requirements: bar count vs trading-day calendar; holiday/early-close handling; corporate-action event log cross-reference; gap detection |
| DA20 | PnL accounting convention | SEAL-DEFERRED | — | Lock to: (a) trade-by-trade closed PnL OR (b) mark-to-market daily PnL with equity curve; DRAFT recommends both tracked, daily MTM as primary for sharpe/drawdown stats |

### 8.1 Locked-at-DRAFT summary

10 of 20 axes LOCKED at DRAFT (DA1, DA2, DA3, DA5, DA6, DA7, DA8, DA10, DA11, DA14, DA15, DA16, DA17 — 13 actually). 7 remain SEAL-DEFERRED (DA4, DA9, DA12, DA13, DA18, DA19, DA20). Each SEAL-DEFERRED axis has a DRAFT-time recommendation; SEAL turn must ratify recommendation or document deliberate divergence.

---

## 9. C5 equity corporate-action contract (dedicated DRAFT section)

The C5 phase-2 safety contract (corporate-action-handling) must be **explicitly authored or extended for equities** before SEAL can proceed. This DRAFT specifies the structure of the C5 extension; the actual contract authoring is a **separate authorization scope**.

### 9.1 Splits

| Aspect | Specification |
|---|---|
| Sealed CSV convention | CRSP-style backward-adjusted (all pre-split prices divided by split ratio; volumes multiplied) |
| Trade-quantity tracking | Position size adjusts at split ex-date: e.g., 100 shares of NVDA pre-10:1 split → 1000 shares post-split at no cost; per-share risk unchanged |
| Split-event log | SEAL must precommit a manually-curated split event log for {AAPL, MSFT, NVDA} over IS+OOS window, cross-referenced against data-vendor split records |
| Historical splits (informational; SEAL must verify) | AAPL: 7:1 (2014-06-09), 4:1 (2020-08-31) — likely pre-IS; MSFT: no splits since 2003; NVDA: 4:1 (2021-07-20), 10:1 (2024-06-10) — both within plausible IS window |
| Order handling at split | No order action required (back-adjusted prices make split transparent to RSI signal) |

### 9.2 Dividends

| Aspect | Specification |
|---|---|
| Strategy precommitment (locked at PLAN) | Non-reinvestment cash account semantics |
| Dividend cash flow | Received on ex-dividend date; credited to account cash balance; tracked separately in P&L attribution |
| Price-series for signal | Price-only (not total-return); RSI signal computed on backward-adjusted close prices NOT adjusted for dividends |
| Dividend event log | SEAL must precommit a manually-curated dividend event log for {AAPL, MSFT, NVDA} over IS+OOS window (ex-date, amount, special vs regular) |
| Look-ahead bias avoidance | Dividend announcements (which precede ex-date) MUST NOT influence signal; signal uses only OHLC + close prices |
| P&L attribution | Each closed trade's P&L = price_diff + dividend_received_during_hold; aggregate P&L tracks both components separately for diagnostic transparency |

### 9.3 Symbol changes

| Aspect | Specification |
|---|---|
| AAPL/MSFT/NVDA symbol stability | All three have had stable ticker symbols since IPO; no expected symbol changes in IS+OOS window |
| Mitigation if symbol change occurs (e.g., reorganization, rebranding) | SEAL must precommit: sealed CSV is keyed by historical-ticker-at-bar-date; symbol-change events documented in event log; signal computation continues across symbol-change boundary |
| If pre-IS-window symbol change exists | Document and verify against data-vendor symbol-change log |

### 9.4 Delistings

| Aspect | Specification |
|---|---|
| Strategy precommitment (locked at PLAN §6.3) | Close-and-do-not-replace: if AAPL/MSFT/NVDA is delisted during IS or OOS window, position is closed at last-available bar; basket shrinks to 2 names; no replacement |
| Expected delistings in window | None expected for AAPL/MSFT/NVDA (all S&P 100 / Nasdaq 100 names with no delisting risk in 2019-2027 horizon) |
| SEAL verification | SEAL must verify no delisting events in IS+OOS window; if any found, candidate must be re-PLANned with different universe |
| Cash-payout-on-delisting (rare) | Cash credited to account; position closed at cash payout price |

### 9.5 Survivorship bias

| Aspect | Specification |
|---|---|
| Universe selection time | AAPL/MSFT/NVDA selected in 2026 (current); IS window 2019-2025 (planned) — selection bias acknowledged |
| Bias direction | Selecting current-thriving large-cap tech names introduces upward bias for IS-window performance (these names outperformed; failure cases like NOK/BBRY/NVDA-pre-2017 not represented) |
| NVDA specific | 2023-2025 AI-driven outperformance is regime-specific; SEAL must precommit explicit acknowledgment that NVDA results may not generalize |
| Mitigation A: rolling eligibility universe | More robust but more complex; rev2 plan §5.2 noted operator could choose; this DRAFT carries the PLAN-precommitted frozen-basket choice |
| Mitigation B: explicit operator acknowledgment | SEAL must include verbatim universe-selection-rationale section addressing: (i) sector concentration (all 3 names tech); (ii) survivorship bias (current-thriving selection); (iii) NVDA AI tailwind specificity |
| Diagnostic-value framing | "Did RSI(3) bi-directional work on these 3 specific names in 2019-2025?" is a precise diagnostic question with a precise answer, even if not maximally generalizable. P11 lifecycle memo MUST frame the diagnostic value in these terms (NOT in terms of "this strategy works on cash equities") |

### 9.6 Adjusted prices

| Aspect | Specification |
|---|---|
| Adjustment for splits | YES (CRSP-style backward-adjusted; mandatory) |
| Adjustment for dividends | NO (price-only for RSI signal; dividends tracked separately) |
| Adjustment for symbol changes | Carry historical ticker per bar date |
| Adjustment methodology source | Locked to data-vendor methodology (e.g., Databento uses CRSP convention; Polygon uses similar; yfinance uses Yahoo's split-and-dividend-adjusted "close" by default — yfinance "Close" includes dividend adjustment which would contaminate RSI signal; if yfinance is selected as data source, the UNADJUSTED close must be reconstructed from yfinance's "Adj Close" + dividend events, OR yfinance must be ruled out) |
| SEAL precommit | Document data-vendor adjustment methodology by name + URL + version |

### 9.7 Data-vendor methodology

See §10 for full data-source decision section. Methodology specifics:

- Each vendor adjusts prices differently; SEAL must precommit:
  - Adjustment formula (CRSP backward-adjust vs forward-adjust vs Yahoo-style; documented in vendor's docs)
  - Dividend treatment (included in "Close" vs separate; affects whether RSI signal contamination occurs)
  - Volume adjustment for splits
  - Corporate-action event log granularity (per-event vs aggregated)
- If chosen vendor's methodology contaminates the price-only RSI signal (e.g., yfinance default `Close` includes dividend adjustments), the SEAL artifact MUST include the de-contamination procedure verbatim and the resulting price series MUST be byte-equivalently re-derivable from the vendor source

### 9.8 C5 contract status at DRAFT

C5 equity-extension contract is **NOT YET AUTHORED**. This DRAFT specifies the requirements; the actual C5 contract document (analogous to s13-d1's C1-C8 phase-2 safety contract files) is a **separate authorization scope**. SEAL cannot proceed without the C5-equity-extension document existing as a byte-stable artifact.

**Suggested authorization phrase for C5 extension** (separate from SEAL):

```
Authorize s14-d2 C5-equity-corporate-action contract extension only.
```

---

## 10. Data-source decision section

The PLAN §5.1 listed 5 candidate data sources. This DRAFT provides full pros/cons + SEAL-time lock requirements.

### 10.1 Decision matrix

| Source | Cost | Coverage (US large-cap daily OHLCV 2019-2027) | Split/dividend adjustment | Bid-ask quote availability | Sealed-CSV-protocol adaptation cost | DR9-equivalent audit cost |
|---|---|---|---|---|---|---|
| **Databento equities** | Subscription (~$120-500/mo depending on tier) | Complete; high-quality | CRSP-style; documented | YES (TAQ-quality at higher tiers) | LOW (existing Databento integration in repo) | LOW (existing DR9 audit logic for Databento) |
| **Polygon.io** | Subscription (~$30-200/mo depending on tier) | Complete | CRSP-style; documented | YES (bid-ask at higher tiers) | MEDIUM (new integration; REST API straightforward) | MEDIUM (new audit needed) |
| **Alpaca** | Free tier available (with rate limits); paid tier ~$10-100/mo | Complete (2016+) | Split-adjusted; documented | YES (real-time bid-ask available; historical limited at free tier) | MEDIUM (new integration; REST API; well-documented Python SDK) | MEDIUM |
| **IEX Cloud** | Free tier available; paid tier ~$10-200/mo (IEX Cloud is sunset; check current status; SEAL must verify vendor still operational) | Complete | Documented | YES | MEDIUM | MEDIUM |
| **yfinance** | Free (unofficial scraper of Yahoo Finance) | Complete but with reliability caveats | Yahoo's "Close" is dividend-adjusted; UNADJUSTED close must be reconstructed (see §9.6) | NO (no bid-ask; only OHLCV) | LOW (existing yfinance gating in repo) | HIGH (Yahoo data quality issues require explicit DR9-equivalent audit with multiple cross-checks) |

### 10.2 Pros/cons summary

**Databento equities (RECOMMENDED at DRAFT):**
- **Pros:** highest data quality; existing repo integration; existing DR9 audit logic; documented CRSP adjustment; bid-ask quotes available for §11 slippage measurement
- **Cons:** subscription cost; requires `DATABENTO_API_KEY` (already gated in CLAUDE.md hard guard; SEAL+FETCH turn would require separate operator authorization for API access)

**Polygon.io:**
- **Pros:** lower cost than Databento; well-documented API; widely used in retail quant
- **Cons:** new integration cost; new DR9 audit logic; smaller community vs Databento equities

**Alpaca:**
- **Pros:** free tier admissible for diagnostic-only research; well-documented Python SDK; bid-ask available
- **Cons:** free tier rate limits may slow fetch; coverage starts 2016 (may not extend far enough into IS window if IS window > ~9 years from current date 2026)

**IEX Cloud:**
- **Pros:** historically used by retail quants
- **Cons:** IEX Cloud is being sunset (Aug 2024 announcement); status as of authoring uncertain; SEAL must verify vendor operational status before selection

**yfinance:**
- **Pros:** free; widely available; simple Python integration
- **Cons:** unofficial scraper (Yahoo Terms of Service questions); data quality issues (occasional bad bars; symbol delistings handled inconsistently); Yahoo "Close" is dividend-adjusted which contaminates RSI signal — UNADJUSTED close must be reconstructed; HIGH DR9-equivalent audit cost to certify data quality

### 10.3 DRAFT recommendation (NOT a SEAL lock)

**DRAFT-recommended source: Databento equities** (if `DATABENTO_API_KEY` operator-authorization is granted at FETCH time) **OR Polygon.io** (if Databento is operator-deferred).

Rationale:
- Highest data quality + existing infrastructure (Databento) minimizes DR9-equivalent audit cost
- Bid-ask quotes available for empirical §11 spread calibration (vs prior estimation)
- Both options have documented CRSP-style adjustments

**SEAL-time lock requirements:**
1. Lock data source by name (one of the 5 above)
2. Lock vendor pricing tier (e.g., "Databento equities daily-OHLCV tier")
3. Lock data-version pinning method (commit a `data-vendor-version.txt` with subscription tier + access date)
4. Lock split/dividend adjustment methodology by reference to vendor docs URL + version
5. Lock DR9-equivalent audit procedure (vendor-specific)

### 10.4 What this DRAFT does NOT do

- Does NOT fetch any data from any vendor
- Does NOT make any network IO call
- Does NOT select the source (only recommends)
- Does NOT precommit DATABENTO_API_KEY access
- SEAL turn + separate FETCH turn are required for data acquisition

---

## 11. Cost / DR10 v2 precommit requirements

### 11.1 Broker fee schedule lock (SEAL-deferred)

| Broker | Per-share commission | Per-trade minimum | Notes |
|---|---|---|---|
| Interactive Brokers (IBKR Pro tiered) | ~$0.0035/share (tiered: lower at higher volume) | $0.35 per order | Exchange + ECN fees often pass-through |
| Schwab | $0/trade (commission-free for equities) | $0 | SEC + FINRA pass-through |
| Alpaca | $0/trade (commission-free) | $0 | SEC + FINRA pass-through |
| Fidelity | $0/trade (commission-free) | $0 | SEC + FINRA pass-through |
| TradeStation | $0/trade or per-share (tiered) | $0-$5 | Tiered |

**DRAFT recommendation:** IBKR Pro tiered for the most-conservative cost model (commission is non-zero; matches industry stop-out scenarios). Alternative: Schwab/Alpaca/Fidelity for $0-commission realistic retail scenario.

**SEAL must lock:**
- Broker name + tier
- Per-share commission rate (with URL + version date of fee schedule)
- Per-trade minimum
- Exchange fees (often pass-through; document explicit formula)
- ECN fees if applicable

### 11.2 SEC + FINRA fees

| Fee | Rate (2026 current; SEAL must verify) | Applies to |
|---|---|---|
| SEC Section 31 fee | ~$8.00 per $1M sale proceeds (~0.0008% of sale notional) | sell side only |
| FINRA TAF (Trading Activity Fee) | ~$0.000166/share | sell side only |
| Options Regulatory Fee (ORF) | N/A (not options trading) | — |

SEAL must lock current SEC + FINRA rates (these change periodically; document version date).

### 11.3 Spread / slippage assumption

| Approach | DRAFT spec |
|---|---|
| **Spread proxy (DRAFT-recommended)** | Half-bid-ask = 1-2 basis points for large-cap names (AAPL/MSFT/NVDA typically trade 1-2 cent spreads on $200 price = 0.5-1 bp); conservative DRAFT estimate: 2 bps half-spread |
| **Empirical measurement (SEAL-required if vendor provides bid-ask)** | Average half-bid-ask across IS+OOS window; if Databento equities or Polygon high-tier is selected, measure directly |
| **Slippage on fill** | Assume fill at next bar open (already conservative); no further slippage modeled (large-cap names at retail size are inside-spread fills typically) |

**SEAL must lock:**
- Whether spread is proxied (DRAFT estimate) or empirically measured
- Half-spread value (in basis points or fraction of price)
- Whether fill at open includes slippage adjustment beyond spread

### 11.4 S2 cost_drag calculation

```
S2_cost_drag = (total_commissions + total_fees + total_spread_cost) × cost_scalar / start_cash
```

Where:
- `total_commissions` = sum over all trades of (per-share commission × shares traded × 2 for round-trip) + (per-trade minimum × 2 if applicable)
- `total_fees` = sum of SEC + FINRA on sell side only
- `total_spread_cost` = sum over all trades of (half-spread × shares × 2 for round-trip)
- `cost_scalar` = 1.5 (matches s13-d1 lineage for parity)
- `start_cash` = DA4 value ($100k or $200k per §3)

### 11.5 Worked example (DRAFT estimate; SEAL must recompute with actual values)

**Assumptions:**
- DA4 = $200k (DRAFT-recommended)
- 75 trades/year basket (3 names × ~25 trades/year per name)
- Average per-trade notional $40k (200 shares × $200 avg price)
- Average per-trade shares: 200
- Broker: IBKR Pro tiered, commission $0.0035/share, $0.35 minimum
- Half-spread: 2 bps = 0.0002 of price
- SEC fee: 0.000008 of sell notional
- FINRA TAF: $0.000166/share on sell side
- cost_scalar = 1.5

**Per-trade cost (round-trip):**
- Commission: 200 shares × $0.0035 × 2 = $1.40 (above $0.35 min, so $1.40 used)
- SEC fee (sell side): $40,000 × 0.000008 = $0.32
- FINRA TAF (sell side): 200 × $0.000166 = $0.033
- Spread cost: 200 shares × $200 × 0.0002 × 2 = $16.00
- **Total per round-trip trade**: $1.40 + $0.32 + $0.033 + $16.00 = $17.75

**Annual cost:**
- 75 trades × $17.75 = $1,331/year
- After cost_scalar 1.5: $1,997/year
- As fraction of DA4 $200k: **$1,997 / $200,000 = 0.998%**

**S2 cost_drag estimate: ~1.0%** at DA4=B $200k. **Far below 5% threshold.**

At DA4=A $100k (smaller cash):
- Same per-trade cost: $17.75 × 75 = $1,331/year × 1.5 = $1,997
- As fraction: $1,997 / $100,000 = **~2.0%**
- Still well below 5% threshold

**Both DA4 options clear DR10 v2 cost_drag branch with comfortable margin.** The PLAN's "0.3-0.5% S2 cost_drag" estimate was conservative; actual estimate at SEAL-time precision is ~1-2%.

### 11.6 DR10 v2 reachability conclusion (DRAFT-level)

**DR10 v2 status: CLEARS comfortably.** Cost_drag at both DA4=A and DA4=B is well below 5%; AND-conjunction never fires regardless of turnover branch (which fires at any active strategy). T2's structural advantage over T1 is preserved at DRAFT level.

**DR10 v2 threshold reminder (immutable per `78cd22e`):**
```
S2_cost_drag > 0.05 (one branch of AND-conjunction)
annual_turnover > 0.50 (other branch of AND-conjunction)
BOTH must fire for DR10 v2 to fire → REJECT_FAST
```
This DRAFT does NOT modify these thresholds and does NOT request any modification.

### 11.7 SEAL-time precommit checklist (carry from S14-D2 PLAN §9, expanded)

| # | Assumption | DRAFT status | SEAL action |
|---|---|---|---|
| 1 | Broker name + tier | RECOMMENDED IBKR Pro tiered | LOCK by broker name + URL of fee schedule + version date |
| 2 | Per-share commission rate | DRAFT estimate $0.0035/share | LOCK from broker fee schedule |
| 3 | Per-trade minimum | DRAFT estimate $0.35 | LOCK from broker fee schedule |
| 4 | Half-bid-ask | DRAFT estimate 2 bps | MEASURE empirically from vendor bid-ask if available; otherwise lock DRAFT estimate with conservatism multiplier |
| 5 | SEC fee rate | DRAFT estimate ~$8/$1M (2026) | VERIFY current rate at SEAL date |
| 6 | FINRA TAF rate | DRAFT estimate $0.000166/share (2026) | VERIFY current rate at SEAL date |
| 7 | cost_scalar | LOCKED at DRAFT = 1.5 (s13-d1 parity) | LOCK at SEAL with explicit reference to s13-d1 lineage |
| 8 | Dividend tracking | LOCKED at DRAFT (non-reinvestment per §9.2) | LOCK at SEAL |
| 9 | Split-adjustment | LOCKED at DRAFT (CRSP-style per §9.1) | LOCK at SEAL |
| 10 | DA4 ($100k or $200k) | DRAFT recommends $200k | LOCK at SEAL |
| 11 | Cost-model byte-equivalent reproducibility | RECOMMENDED format: documented formula + parameter table | LOCK at SEAL (must byte-reproduce S0-S4 sweep at P6.5) |

---

## 12. K9 reachability table (IS + OOS)

### 12.1 Per-name expected trade rate

| Name | RSI(3) expected trades/y (DRAFT estimate; bi-directional) | Rationale |
|---|---|---|
| AAPL | ~22-30 | Large-cap; moderate volatility; mean-reverts on 3-day window meaningfully |
| MSFT | ~20-28 | Lower vol than AAPL; slightly fewer mean-reversion events |
| NVDA | ~25-35 | Higher vol (especially 2023-2025); more mean-reversion events; bi-directional captures both long bounces and short reversions |
| Basket average | ~22-31 trades/y per name | — |

(These are DRAFT prior-beliefs based on RSI(2) baseline of ~34/y on MNQ from s13-d1 + RSI(3) being ~50% slower per rev2 plan §5.2. No backtest has been run. SEAL+P6 IS measurement required.)

### 12.2 K9 IS reachability (≥ 100 closed trades over ~5y IS window)

| Window | Length (y) | Required trades/y for K9=100 | Expected basket trades/y | K9 IS status |
|---|---:|---|---|---|
| IS | ~5 | ≥ 20.0 | 3 × 22-31 = 66-93/y | **CLEARS** (66 × 5 = 330 ≥ 100; 93 × 5 = 465; both well above 100) |

### 12.3 K9 OOS reachability (≥ 50 trades/y over ~2y OOS window — load-bearing per supplement 7d7bb52 §8)

| Window | Length (y) | Required trades/y for K9 OOS floor | Expected basket trades/y (linear) | K9 OOS status (linear) | K9 OOS status (A7-adjusted) |
|---|---:|---|---|---|---|
| OOS | ~2 | ≥ 50.0 | 3 × 22-31 = 66-93/y | **CLEARS** (66 ≥ 50; 93 ≥ 50; margin 16-43) | **CLEARS BORDERLINE-TO-COMFORTABLE** (if A7=2.0: effective ~44-62/y; clears at high end, borderline at low end; if A7=2.5: ~55-78/y; clears comfortably) |

**Margin sensitivity:**
- If actual trade rate is at low end (22/y per name) and A7 is 1.5 (highly concentrated), effective K9 OOS = 22 × 1.5 = **33/y < 50/y floor → K9 OOS FAILS**
- If actual trade rate is at low end (22/y per name) and A7 is 2.0, effective K9 OOS = 22 × 2 = **44/y < 50/y floor → BORDERLINE FAIL**
- If actual trade rate is at low end (22/y per name) and A7 is 2.5, effective K9 OOS = 22 × 2.5 = **55/y ≥ 50/y floor → CLEARS**
- If actual trade rate is at high end (31/y per name) and A7 is 1.5, effective K9 OOS = 31 × 1.5 = **46.5/y < 50/y → BORDERLINE FAIL**
- If actual trade rate is at high end (31/y per name) and A7 is 2.0, effective K9 OOS = 31 × 2 = **62/y ≥ 50/y → CLEARS**

**K9 OOS is borderline-sensitive to BOTH trade rate AND A7. SEAL-time A7 evidence + P6 IS trade-count measurement are both load-bearing.**

### 12.4 K9-reachability discipline binding

K9-reachability discipline (introduced post-s12-d1) is binding for this DRAFT. SEAL artifact must include:
- Computed (not extrapolated) trade-count expectations from actual RSI(3) thresholds + IS-window date range
- A7 evidence from §7.3
- Conservative re-derivation of K9 OOS margin under worst-case (low trade rate × low A7) scenario
- Explicit acknowledgment if K9 OOS margin is borderline; mitigation plan (4th name addition OR sector substitution) precommitted

---

## 13. Phase ladder (each step requires separate operator-typed authorization)

```
PLAN (committed at 373eac8)
  ✓ committed
DRAFT (THIS turn)
  ↓ requires: Authorize s14-d2 cash-equity 3-name basket RSI(3) Tier-N spec SEAL only.
SEAL
  ↓ requires (parallel): Authorize s14-d2 C5-equity-corporate-action contract extension only.
  ↓ requires (parallel): Authorize s14-d2 cash-equity OHLCV fetch from <vendor> for {AAPL, MSFT, NVDA} only (operator-side; DR9-equivalent audit required).
[SEAL + C5 EXTENSION + FETCH must all complete before P1]
  ↓ requires: Authorize s14-d2 P1 plan-lock only.
P1 (plan-lock; A-gates + DA-axes precommit)
  ↓ requires: Authorize s14-d2 P2 phase-2 safety contracts only.
P2 (C1-C8 + C5 safety contracts; K-gates declaration)
  ↓ requires: Authorize s14-d2 P3 BUILD only.
P3 BUILD (runner + IS + OOS scaffolding; OOS NEVER read until P10)
  ↓ requires: Authorize s14-d2 P4 synthetic smoke only.
P4 (synthetic smoke battery)
  ↓ requires: Authorize s14-d2 P6 IS diagnostic only.
P6 IS (in-sample diagnostic; K9 ≥100 trades evaluation; A7 measurement)
  ↓ requires: Authorize s14-d2 P6.5 cost-stress matrix only.
P6.5 (S0-S4 cost-stress sweep; DR10 v2 AND-conjunction evaluation; DR5 cost-stress tier-flip evaluation)
  ↓ requires: Authorize s14-d2 P7 decision memo only.
P7 (decision memo: ADVANCE / REJECT_FAST / REJECT / DEFER)
  ↓ if ADVANCE only: requires: Authorize s14-d2 P10 OOS only.
P10 OOS (out-of-sample evaluation; OOS K9 ≥ 50/y binding; A7 sensitivity check)
  ↓ requires: Authorize s14-d2 P11 lifecycle memo only.
P11 (lifecycle memo: TERMINAL / PARK / ADVANCE-TO-STRATEGY-LAB)
```

**No phase advances autonomously.** Each transition requires separate operator-typed phrase. Per `GOV-RULE-FRAMEWORK-REVISION-OPERATOR-PHRASE-V1` (from `fdf9d6e`) and `GOV-RULE-CO-PRIMARY-OPERATOR-SELECTION-PHRASE-V1` (from `7d7bb52`), parallel-session autonomous progression is preserved as PROVISIONAL but does NOT satisfy operator authorization.

---

## 14. No SEAL/BUILD/FETCH/diagnostic/execution authorized by this DRAFT

This DRAFT explicitly does NOT authorize:

- SEAL of the candidate (no `*_sealed.json` artifact created)
- C5-equity-corporate-action contract authoring (separate authorization scope; see §9.8)
- Data fetch from any vendor (no network IO; no `DATABENTO_API_KEY` access; no broker call)
- P3 BUILD of any runner/strategy/cache artifact
- P4 synthetic smoke battery execution
- P6 IS diagnostic run
- P6.5 cost-stress matrix run
- P7 decision memo authoring
- P10 OOS evaluation
- P11 lifecycle memo authoring
- Any backtest, simulator run, signal computation, RSI calculation, correlation computation, A7 measurement, or P&L calculation
- Any modification of `lessons.md`, `tmp/` helpers, `app.py`, Research Orchestrator files, sealed candidate artifacts, or governance supplements
- Any T1 ratification, advancement, or modification (5376de7 remains byte-stable and PROVISIONAL_NOT_FULLY_RATIFIED)
- Any candidate revival, OOS read, Strategy Lab promotion, live trading, paper trading, FRC grant, or live-block-gate relaxation

---

## 15. Carry-forward status (UNCHANGED across this DRAFT turn)

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` advisory label | TRUE |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` (existing sealed candidates) | TRUE |
| **DR10 v2 future-only framework** | binding for s14+ NEW SEAL turns (per `78cd22e`) |
| **All existing candidate verdicts under DR10 v1** | preserved byte-equivalent and immutable |
| **S13-D1 REJECT_FAST terminal state** | preserved verbatim under DR10 v1 |
| **T1 (s14-d1) provisional status** | `PROVISIONAL_NOT_FULLY_RATIFIED` per `7d7bb52` §6; PLAN at `5376de7` preserved byte-stable; NOT advanced |
| **T2 (s14-d2) operator-ratified PRIMARY at PLAN+DRAFT phase** | TRUE; ratification at `373eac8` PLAN commit + this DRAFT authoring |
| s12-d1 lifecycle terminal | preserved |
| s11-d1 / s10-d2 / s10-d1 / s9 / s7-d1 / B005 / B006 / T8 byte-stable | preserved |
| `lessons.md` dirty + unstaged + uncommitted (NOT touched this turn) | TRUE |
| K9-reachability discipline | binding |
| DR10-reachability discipline under DR10 v2 AND-conjunction | binding |
| `GOV-RULE-FRAMEWORK-REVISION-OPERATOR-PHRASE-V1` | binding |
| `GOV-RULE-CO-PRIMARY-OPERATOR-SELECTION-PHRASE-V1` | binding |
| All T-FORBID-1..12 forbidden tracks | carried |

---

## 16. Files written this DRAFT turn

| File | Purpose |
|---|---|
| `docs/s14_d2_aapl_msft_nvda_cash_equity_3_name_basket_rsi_3_bi_directional_tier_n_spec_draft.md` | This DRAFT (DRAFT-only; no JSON sidecar; sealing happens at SEAL phase per §13) |

No other repository file is modified. The `brain_memory/projects/trading_bot/lessons.md` dirty + unstaged state from prior controller sessions remains **untouched**. The `tmp/` helpers remain untouched. The `app.py` and Research Orchestrator files remain untouched. The `5376de7` T1 PLAN remains byte-stable. The `373eac8` S14-D2 PLAN remains byte-stable. All sealed artifacts, governance supplements, and comparison memos remain byte-stable.

---

## 17. Next-step authorization scope

```
Authorize s14-d2 cash-equity 3-name basket RSI(3) Tier-N spec SEAL only.
```

Authors the SEAL artifact (sealed JSON + companion markdown). SEAL turn must:
- Resolve all SEAL-DEFERRED DA axes (DA4, DA9, DA12, DA13, DA18, DA19, DA20) with explicit precommits
- Document universe-selection rationale verbatim (sector concentration + survivorship bias + NVDA AI tailwind specificity per §9.5)
- Lock broker fee schedule (§11.1) and data source (§10.3)
- Lock cost model with byte-equivalent reproducibility formula (§11.7 #11)
- Reference C5-equity-corporate-action contract by-version (must exist as byte-stable artifact before SEAL)
- Include sealed-CSV anchor sha256 (must exist as byte-stable artifact before SEAL via separate FETCH turn)
- Carry C1-C8 + C5 phase-2 safety contracts by-reference
- Carry K-gates + DR rules + DR10 v2 by-reference
- Generate canonical seal sha256 via LESSON_HUNTER_004 recipe
- Self-verify seal before completion

SEAL-only; no FETCH/BUILD/diagnostic until separately authorized.

---

End of s14-d2 Tier-N spec DRAFT. DRAFT-authoring turn only. No code. No backtest. No simulator. No signal. No data fetch. No Databento. No Polygon. No Alpaca. No IEX. No yfinance. No `DATABENTO_API_KEY` access. No QC. No LEAN. No brokerage. No real order. No paper order. No Strategy Lab promotion. No `review_queue` mutation. No production `idea_memory` mutation. **No retroactive application of DR10 v2 to existing candidates. No s13-d1 / s12-d1 / parked-candidate revival. No T1 (5376de7) advancement or modification. No `lessons.md` modification or staging. No C5-equity-corporate-action contract authoring (separate scope).** No live trading. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`. s13-d1 lifecycle terminal preserved verbatim under DR10 v1. T1 (s14-d1) remains `PROVISIONAL_NOT_FULLY_RATIFIED`. T2 (s14-d2) is operator-ratified PRIMARY at PLAN+DRAFT phase; SEAL turn requires separate operator-typed authorization.
