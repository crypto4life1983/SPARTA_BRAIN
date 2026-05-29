# Weekly RS (s21) paper-trading readiness PLAN

Status: **PLAN_ONLY** (design document). This authorizes **no** execution, **no** broker connection, **no** live trade, **no** FRC grant, **no** Strategy Lab promotion, **no** data fetch, **no** code build. It defines *how* a safe, broker-free, **simulated forward paper test** of the s21 diagnostic edge would be run, and the gates that must pass before anyone may even *consider* a small live-capital test.

Authored: 2026-05-29
Source diagnostic edge: **s21-d1 weekly relative-strength rotation** — OOS_CONFIRMED_DIAGNOSTIC (clean), SEAL `ae11479`, P11 `7e12e56`, DR9 `d76c999`, line catalog `b4ee876`, master summary `6ef3dab`. Framework: DR10 v2 (`78cd22e`) + walk-forward K13 (`52a3b60`).

> **BINDING STATUS (read first):** s21 is and remains **DIAGNOSTIC_ONLY** until the paper gates below pass. This plan does **not** promote s21, does **not** connect to a broker, does **not** trade live, and does **not** grant FRC. Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · **FRC NEVER_GRANTED**. The framework's permanent 6-gate live-block stands; only a *separate, explicit human governance decision* (outside this plan) could ever change it. "Paper-validated" (if reached) is still **not** "live-ready."

----

## 0. What "paper trading" means here (and what it does NOT mean)

- **IS:** a self-contained **simulated forward test** — run the locked s21 mechanic forward in calendar time on freshly-arriving market data, with a deterministic simulated fill + cost model (same as the diagnostic), writing every decision/fill to an append-only paper ledger. No real orders, no real capital, **no broker API**.
- **IS NOT:** a brokerage paper account, a broker connection, live order routing, real capital, Strategy Lab promotion, or FRC. Those are explicitly out of scope and forbidden by this plan.

----

## 1. Exact weekly signal generation process (locked, byte-identical to s21)

**Locked mechanic (no tuning, ever):** 126-21 skip-month relative-strength signal · weekly rebalance · hold **top-8 equal-weight (1/8)** · long-only · relative-rank rotation exit · $100,000 paper notional · split_only adjustment · vendor Tiingo · warmup 160 bars. Universe = the **frozen s21 48-name basket** (no substitution/widening; any change = a different candidate requiring its own sealed lifecycle):
`AVGO, QCOM, TXN, INTC, MU, AMAT, IBM, INTU, NOW, ADI, VZ, T, CHTR, EA, SBUX, TGT, BKNG, MAR, GM, TJX, ROST, MO, CL, KMB, GIS, STZ, PFE, BMY, AMGN, GILD, CVS, CI, ISRG, SYK, C, USB, SCHW, BLK, SPGI, CB, BA, ITW, UPS, RTX, LMT, DE, PSX, VLO`

**Weekly cadence (forward calendar rule):** pick ONE fixed weekly anchor session and never change it — recommended: **signal on Friday close, execute at the next Monday open** (or, to mirror the diagnostic's same-bar convention exactly, signal-and-fill at the same session close). Whichever is chosen is **locked before week 1** and recorded in the run config; switching mid-test is a kill-switch event (§7).

**Per-week procedure (deterministic, no discretion):**
1. Ingest the latest split-adjusted daily closes for all 48 names through the signal date (reuse the s21 fetch+adjust convention; verify per-symbol SHA against the prior week's stored history for continuity).
2. **Data-integrity preconditions (else NO-TRADE this week, log + flag — never guess):** all 48 present; bar-for-bar calendar alignment; no stale bar (last date == expected session); ≥160 prior bars for the lookback.
3. Compute `trailing_return(closes, i, 126, 21)` for each name → `close[i-21] / close[i-21-126] - 1`.
4. Rank all 48 by signal descending (deterministic symbol tie-break); select **top-8**.
5. Target = equal-weight `1/8 × current_paper_equity` per selected name.
6. Determine orders: **rotation exits** (held names no longer in top-8 → full exit), **entries** (new top-8 names → buy to target), **rebalances** (held-and-still-selected → trim/add to target).
7. "Fill" at the locked reference price; apply the cost model (§4); update the paper book; append to the ledger (§3).

No parameter, cadence, universe, or rule may be changed during the test. Any change voids the run.

----

## 2. Portfolio construction rules

- **Long-only**, top-8 **equal-weight** (1/8 of equity each), **one lot per name**, **max 8 positions**, **no shorting, no leverage, no pyramiding, no derivatives, no margin.**
- Cash is held for any unfilled fraction; if fewer than 8 names produce a valid signal (should not happen on 48), hold the shortfall in cash (never concentrate).
- **Rebalance-to-target each week**: trim overweights, top up underweights within the retained set; full exit on rotation-out.
- Fractional shares permitted in the simulation only if the chosen broker model (for a future live test) would support them; otherwise round down to whole shares and hold residual cash — **decide and lock this before week 1** (it affects realism).
- No intra-week trading, no stops, no overrides — the only actions are at the weekly rebalance. (The diagnostic's exit is purely relative-rank rotation; there is no trailing/ATR stop.)

----

## 3. Paper-trade logging format (append-only; immutable per week)

Two append-only files, never edited retroactively:

**(a) `paper_orders.jsonl`** — one record per rebalance week:
```
{ "week": <int>, "signal_date": "YYYY-MM-DD", "fill_basis": "next_open|same_close",
  "equity_before": <usd>, "cash_before": <usd>,
  "signal_snapshot": { "<SYM>": <trailing_return_126_21>, ... 48 entries },
  "selected_top8": ["<SYM>", ...],
  "orders": [ { "symbol": "<SYM>", "action": "ENTER|EXIT|REBALANCE", "shares": <signed>,
               "fill_price": <usd>, "commission_usd": <usd>, "slippage_usd": <usd>,
               "cashflow_usd": <signed> }, ... ],
  "holdings_after": { "<SYM>": { "shares": <n>, "mkt_value": <usd> }, ... },
  "equity_after": <usd>, "cash_after": <usd>,
  "data_integrity": { "all_48_present": true, "calendar_aligned": true, "stale_bar": false },
  "flags": [] }
```

**(b) `paper_trades_closed.jsonl`** — one record per **closed round-trip** (a name fully exited):
```
{ "symbol": "<SYM>", "entry_week": <int>, "exit_week": <int>, "entry_date": "...", "exit_date": "...",
  "shares": <n>, "gross_pnl_usd": <usd>, "commission_total_usd": <usd>, "slippage_total_usd": <usd>,
  "net_pnl_usd": <usd>, "holding_weeks": <int> }
```
`net_pnl_usd` uses the same per-name holding-period net-cashflow accounting as the diagnostic (sells − buys incl. costs, realized on full exit). The closed-trade count drives the K9-style sample gates.

----

## 4. Slippage / commission tracking (same model as the diagnostic + realism delta)

- **Cost model (locked = diagnostic S1):** commission `max($1, $0.005/share)`; slippage `1 bp × notional` per fill. Applied to every entry/exit/rebalance leg.
- Track **per-leg** and **cumulative** commission + slippage; compute **annualized cost-drag %** = (cumulative cost / starting equity) / years_elapsed.
- **Realism delta (paper→live readiness):** also record, for each fill, the gap between the **modeled fill price** and a **reference market price** (e.g., VWAP or the opposite-side touch if available) → this is the **implementation-shortfall proxy**, the single most important paper-vs-live risk. Track its running mean/percentiles. (No broker needed — derived from the same market data.)
- Weekly and cumulative cost-drag are compared against the **DR10 v2 ceiling (S2 cost-drag < 5%/yr)**; the diagnostic ran ~1%/yr.

----

## 5. Weekly report format (`paper_weekly_report_<week>.md`)

| Field | Content |
|---|---|
| Week / signal date / fill basis | `<n>` / `YYYY-MM-DD` / locked basis |
| Equity / weekly return / cumulative return | `$` / `%` / `%` |
| Rebalances to date / closed trades this week / cumulative closed | counts |
| Turnover this week (names rotated) | count + % of book |
| Cost this week / cumulative / annualized cost-drag % | `$` / `$` / `%` |
| Implementation-shortfall (mean this week / cumulative) | bps |
| Current holdings (8) + weights | list |
| Drawdown: current / max-to-date / peak equity | `%` / `%` / `$` |
| Diagnostic-tracking check | realized expectancy/trade & win-rate vs s21 OOS (+$171, 58.5%) — within tolerance? |
| Kill-switch status | GREEN / WARN / TRIGGERED + reason |
| Data integrity | all_48 / aligned / no-stale — pass/fail |

A one-line verdict each week: `CONTINUE` / `WARN` / `HALT`.

----

## 6. Drawdown monitoring

- Track **peak paper equity**, **current drawdown** = `(peak − equity)/peak`, **max drawdown to date**.
- Thresholds (operational, tighter than the diagnostic's K4=50% fail; diagnostic s21 maxDD ≈ 19–32%):
  - **15%** → WARN (log, watch).
  - **25%** → REVIEW (mandatory operator review before continuing; auto-flag).
  - **30%** → **KILL** (halt new entries; see §7). Chosen well below the K4 FAIL_SAFETY (50%) and at the diagnostic's "concern" band so a real regime break stops the test early.
- Drawdown is computed on the paper mark-to-market book each session (not just at rebalance).

----

## 7. Kill-switch rules (any one → HALT)

Halt = **stop opening/rotating; freeze the book (or flatten to cash if operator elects); log; require explicit manual restart**. No automatic resumption.

1. **Drawdown ≥ 30%** (§6).
2. **Data/feed failure or staleness** — missing/late bar, <48 names, calendar misalignment, vendor error → NO-TRADE that week; if it persists >1 week → HALT. Never trade on guessed/stale data.
3. **Signal/▶mechanic anomaly** — <8 valid signals, NaN/None in the ranked set at a rebalance, or any deviation of the running code from the locked s21 mechanic (implementation-drift check fails) → HALT.
4. **Cost-drag breach** — annualized realized cost-drag > 5%/yr (DR10 v2 analog) → HALT for review.
5. **Edge-divergence** — realized expectancy/trade turns and *stays* negative over a trailing ≥20-trade window, or realized behavior diverges materially from the diagnostic → HALT for review.
6. **Implementation-shortfall blowout** — mean shortfall exceeds a pre-locked tolerance (e.g., > 25 bps/leg) → HALT (paper fills no longer realistic).
7. **Manual operator stop** — always available.

Kill-switch behavior itself must be **tested before week 1** (inject a synthetic stale bar / DD breach and confirm it halts).

----

## 8. 12-week and 24-week paper evaluation gates

Both are **forward** analogues of the sealed diagnostic gates (K9 sample / K1-K2 edge / K4 drawdown / DR10 cost). Expected pace from s21 OOS: ~1 rebalance/week, ≈1.6 closed trades/week, ~50 trades/yr.

### 12-week gate (interim checkpoint → `CONTINUE` or `HALT`)
- **No unresolved kill-switch trigger** during the window.
- **Sample on pace:** ≥ ~15 closed trades (≈ on track for ≥50/yr); rebalances occurred each eligible week.
- **Not catastrophic:** cumulative net P&L not deeply negative; max drawdown < 25%.
- **Cost realism:** annualized cost-drag < 5%/yr; mean implementation-shortfall within tolerance.
- **Mechanic fidelity:** running code provably matches the locked s21 mechanic (no drift).
- *12-week is a CONTINUE/HALT checkpoint only — it is NOT a pass-to-anything.*

### 24-week gate (primary paper-validation → `PAPER_VALIDATED` or `FAIL`)
ALL must hold:
- **Sample (K9 analog):** ≥ ~35–40 closed trades and on pace for ≥50/yr.
- **Edge (K1/K2 analog):** realized **expectancy/trade > 0** AND **sharpe_proxy/trade > 0** on the closed paper trades; sign consistent with the s21 diagnostic.
- **Drawdown (K4 analog):** max drawdown < 30% (never hit the 30% kill).
- **Cost (DR10 v2 analog):** annualized realized cost-drag < 5%/yr.
- **Realism:** implementation-shortfall quantified and within tolerance; paper fills credible.
- **Robustness:** no unresolved kill events; data integrity clean throughout; results not driven by 1–2 outlier trades (inspect distribution).
- Verdict `PAPER_VALIDATED` = *forward behavior is consistent with the diagnostic on a simulated basis.* **It is still DIAGNOSTIC/PAPER — not live-ready.**

If either gate fails → s21 paper test is **HALTED/parked**; no live consideration.

----

## 9. Criteria required BEFORE any small live-capital test (the highest bar — NOT granted by this plan)

A small live-capital test may only be *considered* (not started) if **all** hold, and even then it requires a separate explicit human decision:
1. **Both** 12-week and 24-week paper gates **PASSED**, ideally extended to **≥52 weeks** of clean forward paper.
2. Realized forward paper **edge sign AND rough magnitude** consistent with the s21 diagnostic (positive expectancy + sharpe; modest is expected, +$171/trade).
3. **Implementation shortfall** measured, small, and stable — the paper→live gap is the dominant risk; live fills will be worse than the model.
4. **Cost realism** validated (real commission/slippage schedule ≤ modeled, or model updated and re-tested).
5. **Capacity/liquidity** confirmed (the 48 are liquid large-caps; intended position sizes are tiny relative to ADV).
6. **Kill-switch + operational runbook** tested and functional in the forward environment.
7. **Risk capital defined as truly small and fully loss-tolerant** (size that can be lost entirely without consequence), with a hard max-loss stop on the live test itself.
8. **Governance:** a **separate, explicit, human authorization** that knowingly lifts the framework's permanent 6-gate live-block for a bounded, supervised test — i.e., **FRC would have to be deliberately granted by a human**, which it currently is **NEVER** by default. This plan does **not** grant it, does **not** request it, and does **not** create a live path; it only specifies what such a decision would need to be predicated on.

A live test is **out of scope of this plan** and remains blocked until and unless that separate human governance decision is made.

----

## 10. Explicit DIAGNOSTIC_ONLY statement

**s21 remains DIAGNOSTIC_ONLY until the paper gates pass.** Until 12-week and 24-week paper gates are passed, s21 is exactly what the sealed lifecycle says: a clean-generalization-confirmed *diagnostic* edge, not live-ready and not paper-validated. Passing the paper gates upgrades it only to **PAPER_VALIDATED (still not live-ready)**. At no point does this plan authorize broker connection, live trading, FRC, or Strategy Lab promotion. `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` · `PAUSED` · `BLOCKED_AT_6_GATES` · `FRC NEVER_GRANTED`.

----

## 11. Boundaries held by this PLAN turn

PLAN/design document only. No broker connection · no live trading · no paper-broker account · no FRC grant · no Strategy Lab promotion · no data fetch · no code build/execution · no backtest · no modification of any sealed artifact · `lessons.md` untouched · no secrets accessed. The locked s21 mechanic is referenced read-only and may not be tuned. Any future step (building the forward-paper harness, running it, or a live test) requires its own separate explicit authorization.

----

## 12. Next-step authorization scope (each separate; none pre-approved here)

- **Build the forward-paper harness (code, no run):** `Authorize weekly RS s21 paper-trading forward harness BUILD only — broker-free simulator; no run; no fetch.`
- **Run a defined paper week / backfill dry-run (no broker):** separate authorization.
- **Defer:** `Defer / Pause weekly RS paper-trading readiness at PLAN.`
- A small live-capital test is **NOT** an available next step from this plan (§9 governance bar unmet).

----

End of PLAN. Design document only. Defines a broker-free simulated forward paper test of the s21 weekly RS diagnostic edge plus 12-week/24-week gates and the (separate, human-only, currently-ungranted) bar before any small live test. **s21 remains DIAGNOSTIC_ONLY; no broker, no live trade, no FRC, no Strategy Lab promotion is authorized.** Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED`.
