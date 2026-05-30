# S26-D14 — Risk / Readiness Gate Design

**Defines the formal readiness-gate system for the S26 "Trend + Support/Resistance +
EMA/RSI" (long-only v1) branch BEFORE any future paper-readiness discussion. DESIGN /
REPORT ONLY — no new backtest, no new market test, no optimization, no strategy rule
change, no execution/live/paper code. Nothing here marks S26 paper-ready.**

- **Created:** 2026-05-30 · **Reference commit:** `91b6931` (S26-D13 closeout)
- **Frozen engine:** `engine/trend_sr_ema_rsi_daily.py` — UNCHANGED.
- Built from committed records (D13, D5, D6, D12) for summary only — no analysis re-run.

---

## 1. Purpose

- S26 is **research-promising but not paper-ready**.
- D14 defines **what must be true before any future paper-readiness memo can even be
  considered** — it sets the gates, blockers, and (design-only) risk limits.
- **This is NOT approval for paper trading.** It is a specification of the bar that future
  evidence must clear.

## 2. Current S26 evidence summary

| Evidence | Value |
|---|---|
| **NQ IS** | 117 trades · +7.6536R · PF 1.2016 · expectancy +0.0654R/trade · max DD 10.5943R |
| **NQ OOS** | 32 trades · +7.9990R · PF 1.7694 · expectancy +0.2500R/trade · max DD 2.1827R |
| **D6 entry significance** | ENTRY_EDGE_INCONCLUSIVE |
| **D12 multi-market** | PARTIAL_SUPPORT_WITH_CAUTION |

**Known weaknesses carried into this gate design:**
- Thin IS edge (PF 1.20, expectancy +0.0654R).
- High IS max DD (10.59R, larger than the +7.65R IS net).
- Inconclusive entry edge (no EDGE_LIKELY horizon on IS).
- ES IS high max DD (16.73R, exceeds 1.5× NQ IS DD).
- ES OOS only 27 trades and 2025-dominated (72.8% of OOS net).

## 3. Readiness levels

| Level | Meaning |
|---|---|
| **BLOCKED** | A hard blocker fired; branch parked — no promotion until resolved or a new branch is opened. |
| **RESEARCH_CANDIDATE** | Survives IS+OOS and basic robustness with caveats; cleared for deeper validation only. |
| **VALIDATION_CANDIDATE** | Passed regime (D15), walk-forward (D16) and friction (D17) gates with no hard blocker. |
| **PAPER_REVIEW_CANDIDATE** | All required gates met; eligible to be the subject of a separate paper-readiness memo (still not paper trading). |
| **PAPER_READY** | A separate paper-readiness memo has explicitly approved a constrained paper test. |
| **LIVE_READY** | Out of scope here; would require its own gate after a successful paper program. |

**Current level: `RESEARCH_CANDIDATE` only.**

## 4. Required gates before PAPER_REVIEW_CANDIDATE

All of the following must hold (none optional):

- **D15** regime breakdown does **not** reveal catastrophic regime dependency.
- **D16** rolling/walk-forward stability does **not** show the result isolated to one period.
- **D17** execution/slippage/commission stress remains **positive under conservative
  assumptions**.
- Entry significance remains **at least inconclusive, not disproven** (not NOT_SUPPORTED).
- Multi-market support remains **at least partial; ES cannot contradict NQ**.
- **No top-year / top-trade dominance problem.**
- **Drawdown assumptions are acceptable** (within predefined tolerance).
- **No unresolved data-QA issues.**

## 5. Hard blockers

Any **one** of these blocks paper readiness (forces BLOCKED / park):

- Negative OOS after realistic friction (slippage + commission).
- ES OOS fails badly or contradicts NQ.
- Regime breakdown shows profit only from one narrow regime.
- Walk-forward shows collapse outside one subperiod.
- Entry significance later becomes NOT_SUPPORTED **together with** other risk weakness.
- Monte Carlo / sequence risk becomes FRAGILE.
- Max DD or loss cluster exceeds predefined tolerance.
- Any code/data integrity issue.
- Any manual/subjective rule added after OOS.

## 6. Risk limits for a hypothetical future paper review (design only)

**This is design only, NOT authorization.** These limits would apply **only if** a separate
paper-readiness memo later approves a paper test:

- Paper only **if later approved separately**.
- **One contract / micro only** at first.
- **Fixed R-based stop required** (no discretionary stop).
- **Daily max loss limit** (predefined, in R).
- **Weekly max loss limit** (predefined, in R).
- **Max open positions = 1.**
- **No pyramiding.**
- **No discretionary override.**
- **No parameter changes** during the paper test.
- **Minimum observation period** before any upgrade is considered.
- **Kill switch** after a defined drawdown or any rule breach.

## 7. Required future validation sequence

Recommended order (each gated by Section 4 / blocked by Section 5):

1. **S26-D15** — regime breakdown.
2. **S26-D16** — rolling / walk-forward stability.
3. **S26-D17** — friction / slippage stress.
4. **S26-D18** — final research readiness review.
5. **Separate paper-readiness memo** — only if all of the above pass.

## 8. Forbidden actions

- No deployment.
- No paper trading yet.
- No live trading.
- No optimization against OOS.
- No filter additions from OOS observations.
- No mixing Donchian logic into S26.
- No marketing as a profitable bot.

## 9. Final verdict

**S26 remains a RESEARCH_CANDIDATE. It is not PAPER_REVIEW_CANDIDATE, not PAPER_READY, and
not LIVE_READY.**

---

### Notes of record
- Design only — gate specification built from the committed S26 records (D13/D5/D6/D12). No
  analysis re-run, no backtest, no market test, no optimization, no parameter/rule/source/
  engine/test change, no execution/live/paper code.
- Defines gates and (design-only) risk limits; **authorizes nothing**. Paper review remains
  conditional on a future, separately-approved memo after D15–D18 pass.
- Donchian/S23/S24/S25 untouched. `templates/base.html` not touched. Nothing staged,
  nothing committed by this step.
