# Master Reconciliation Memo after S13-D1 Terminal (sealed; binding; PLAN-only)

- **Seal SHA-256:** `e2714c8e379f0391920d890f65c9f4d525971ea5ca5261c6c9756e003aba3349`
- **Authored at UTC:** 2026-05-27T19:46:16.871415+00:00
- **Status:** `PLAN_ONLY` — no candidate authoring, no DR10 revision, no execution
- **Authorization phrase:** `Authorize master reconciliation memo before T1 / T6 / halt selection`

## 1. Eight consecutive parked / rejected Phase-2 candidates

| candidate | mechanic | universe | outcome | binding failure |
|---|---|---|---|---|
| `s7-D1` | Donchian + pyramid | 4-ETF basket (SPY/TLT/GLD/USO) | PARKED — concentration / USO dominance pathology | A7_effective_independent_bets / portfolio concentration |
| `s9` | RSI(2) long-only | 4-ETF basket (SPY/TLT/GLD/USO) | PARKED — SAFE_BUT_NOT_MONEY_PROVEN | DR2/DR3 cost-stress turned edge negative; S0 net PnL -$1,211 over 414 trades |
| `B006_001` | SPY vol-targeting (no leverage cap enforcement) | SPY | REJECTED — DR11 leverage-cap bound rate > 10% | DR11 (C4 SPY leverage-cap) |
| `B006_002` | SPY vol-targeting (with C4 enforcement) | SPY | REJECTED — verdict REJECT_FAST | C4 SPY-specific safety rule; warmup-window order pathology |
| `s10-d1` | Donchian on MNQ + MGC | MNQ.c.0 + MGC.c.0 | PARKED — INCONCLUSIVE_HOLD | DR9 MGC.c.0 continuous-stitch data integrity |
| `s10-d2` | Donchian-55/20 | 4-market futures basket | PARKED — PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED | K9 OOS (53 trades < 100) |
| `s12-d1` | Donchian-15/8 | MNQ.c.0 single | PARKED — PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS | K9 IS (48 trades < 100) |
| `s13-d1` | RSI(2) bi-directional | MNQ.c.0 single | TERMINAL REJECT_FAST | DR10 turnover branch (annual_turnover 84.79 >> 0.50); K9 had cleared at 159 trades |

**Breakdown by binding failure:**
- K9 sample-size: s10-d2, s12-d1
- DR10 turnover branch: s13-d1
- DR2/DR3 cost-stress: s9
- DR9 data integrity: s10-d1
- DR11 / C4 safety: B006_001, B006_002
- Concentration pathology: s7-D1

**Pattern:** five different failure modes across eight candidates, five mechanic families, five universes. No single mechanic or universe is the common defect — each failed for its own reason. The framework's gate set may be calibrated for a different research universe than the operator's actual intent. Section 10 surfaces this explicitly.

## 2. S13-D1 terminal result

| phase | commit | result |
|---|---|---|
| P6 IS diagnostic | `3fa479a` (seal `dc480c71…`) | **`READY_FOR_LONGER_BACKTEST`** · 159 trades / K9 PASS (1.59× margin) · net_pnl +$85,975 · |maxDD| 17.68% · sharpe 0.5503 · **`annual_turnover` 84.79** · 34.34 trades/y · real sealed CSV used + sha-verified |
| P6.5 cost-stress | `15c4fb1` (seal `2bb04d5f…`) | **`REJECT_FAST`** · DR10 turnover branch fires (84.79 >> 0.50; 169.6× over) · cost-drag branch does NOT fire (2.35% < 5%) · S0–S4 sweep: edge positive at every tier · S0→S4 sharpe degradation 13% (below 50% DR2 threshold) |
| P7 decision memo | `cc1817b` (seal `f68dd92b…`) | candidate-lifecycle **TERMINAL**; C6 verbatim; DR10 NOT modified; no P10; no Strategy Lab; lessons not written |
| P10 OOS | NOT RUN | OOS window 2024-01-02 → 2025-12-30 **preserved unread** |
| P11 standalone | NOT AUTHORED | disposition folded into P7 + T1/parallel disposition memo `cba0f47` |

**Terminal state:** `P7_DECISION_MEMO_SEALED_CANDIDATE_TERMINAL` — byte-equivalent and binding under SEAL invariant `fail_safety_outcomes_terminal_for_this_candidate_record_id=True`.

## 3+4+5+6. K9 ∧ DR10 incompatibility (the load-bearing finding)

**K9** requires ≥ 50 trades/year (binding via OOS window: 100 trades / 2 years).
**DR10** requires `annual_turnover ≤ 0.50` (turnover branch).

### Key formula

```
annual_turnover = 2 × per_trade_notional × trades_per_year / start_cash

DR10 clearance:   2 × per_trade_notional × trades_per_year  ≤  0.50 × start_cash
              ⇒  per_trade_notional  ≤  0.25 × start_cash / trades_per_year

K9 OOS floor:     trades_per_year  ≥  50

Joint constraint: per_trade_notional  ≤  0.005 × start_cash  (= 0.5% of start_cash)
```

**Max per-trade notional by start_cash:**

| start_cash | max per-trade notional | MNQ.c.0 (~$30k/contract) feasible? |
|---|---|---|
| $100k | **$500** | NO (60× over) |
| $200k | **$1,000** | NO (30× over) |
| $500k | **$2,500** | NO (12× over) |
| $1M | **$5,000** | NO (6× over) |
| $5M | **$25,000** | borderline (1.2× over) |
| $10M | **$50,000** | YES |

### Why futures structurally fail at retail

Every liquid futures contract has minimum unit notional 15–65% of $200k start_cash (MNQ $30k = 15%; ZN $110k = 55%; 6E $130k = 65%). NONE can satisfy the 0.5%-of-cash constraint at retail capital. This is contract-quantization, not a soft sizing choice. **Active trading on any liquid futures contract is structurally rejected by the K9+DR10 joint constraint at $100k–$5M.**

### Why cash-equity nano-sizing can pass but may be meaningless

Cash equities have share-level granularity → per-trade notional can be made arbitrarily small. At $200k, clearing both gates requires ~$400–$800 per position (0.005%–0.01% risk per trade ≈ $10–$20 risk per position). Position sizes this small are dominated by transaction costs (commissions, half-bid-ask, slippage). The strategy may *clear the gate* mathematically while producing zero or negative real-money edge at the sizes the gate forces. This is "satisfy the rule" research, not "discover edge" research.

## 7. Three strategic paths

| Path | Framework change required? | Produces research at realistic operational scale? | Data scope friction | Honest summary |
|---|---|---|---|---|
| **A. T1 cash-equity nano-sizing** | NO | **NO** (sub-$1k positions on $200k) | MEDIUM (new fetch + audit) | Satisfies existing gates by trading at sizes too small to be operationally relevant. Generates artifacts but the diagnostic answer doesn't translate to real money. |
| **B. T6 framework DR10 revision** | YES (heavyweight SEAL turn) | YES | NONE | Addresses root cause: DR10 calibration vs research intent. Investigation plan 28cbaea has the math + 7-option governance scoping pre-built. Preserves byte-equivalence of all prior candidates. |
| **C. Halt trading research** | NO | n/a | NONE | Acknowledges 8-PARK pattern + DR10 finding as pattern-level evidence. Stops sealed-artifact authoring on trading-bot. Reallocates operator attention to other SPARTA tracks (Hydra Video, YouTube growth, affiliate, moving company). |

## 8. T6 governance options A–G (from investigation plan 28cbaea §7)

| Option | Change | s13-d1 hypothetical | Migration cost | Framework-integrity preservation |
|---|---|---|---|---|
| **A. Status quo** | None | unchanged: REJECT_FAST | ZERO | **STRONGEST** |
| **B. Raise threshold** | 0.50 → 25/100/etc. | clears at 100 | MODERATE | MEDIUM (depends on anchor) |
| **C. Drop turnover branch** | keep S2_cost_drag only | clears (2.35% < 5%) | LOW | **ACCEPTABLE** (preserves original cost intent) |
| **D. Asset-class-specific** | per-class thresholds | depends | HIGH | MEDIUM-LOW (proliferation) |
| **E. Capital-scale-normalize** | scales with start_cash | unchanged at $200k | MODERATE | LOW (direction counter-intuitive per 28cbaea §7.5) |
| **F. OR → AND** | both branches required | clears (cost arm doesn't fire) | LOW | **WEAKENS** (loses raw-turnover signal) |
| **G. Defer** | None; revisit later | n/a | ZERO | **STRONGEST** |

**Invariant across all options:** s13-d1's terminal verdict is byte-equivalent under the OLD DR10 regardless of which option is selected. Past sealed candidates retain old verdicts; revision applies only to s14+ going forward.

## 9. Framework integrity vs operational usefulness (two different dimensions)

| | Preserve strict rules | Revise mis-calibrated rules | Avoid rule relaxation just to pass |
|---|---|---|---|
| **Approach** | Keep DR10 at 0.50 (Options A or G) | Author T6 SEAL revision with audit trail (Options B, C, D) | Operator self-check: would I have authored the SAME revision a year ago before s13-d1 fired DR10? |
| **Pros** | Strongest framework-integrity signal · No 'moving the goalposts' perception | Aligns framework with stated research intent · Empirically grounded · 28cbaea has the math | Procedural integrity guard against rationalization |
| **Cons** | Trading-bot research effectively constrained to buy-and-hold + institutional OR nano cash equity | Heavyweight turn · Requires defensible threshold anchor · Each option has its own risks | n/a — this is a check, not a path |

**The operator's strategic intent (next section) decides which dimension to weight more heavily.**

## 10. Strategic intent question (LOAD-BEARING)

> **Is the goal of the trading-bot research track to (A) discover money-strategies that the operator can actually trade at retail capital, OR (B) characterize where the SPARTA framework's discipline accepts or rejects various strategies as a research-into-research-itself exercise?**

A third legitimate answer is **(C) trading-bot is not the project's actual North Star** — other SPARTA tracks (Hydra Video, YouTube growth, affiliate, moving company operations) may produce more marginal value per unit of attention.

**Neither answer is wrong.** They are different projects. The operator may choose any of A, B, C. The trouble is having an *implicit* choice that doesn't get articulated, which leads to spending lifecycle effort on candidates that are predetermined to PARK under whichever answer is implicit.

The operator has not yet been asked this question explicitly. This memo is the moment to surface it.

## 11. Final recommendation

**`ANSWER_THE_STRATEGIC_INTENT_QUESTION_EXPLICITLY_BEFORE_CHOOSING_T1_OR_T6_OR_HALT`**

**Strength: STRONG**

### Rationale

The three paths are NOT substitutable. Each is the right answer to a different strategic intent:

- **T1 nano-sizing** is right if intent is reading B (keep framework lifecycle generating artifacts)
- **T6 SEAL revision** is right if intent is reading A (discover retail-scale operable strategies)
- **Halt** is right if intent is reading C (trading-bot not the highest-leverage track)

Choosing T1 or T6 or halt without first stating intent risks producing more predictable terminal lifecycle work (framework waste; T-FORBID-12 territory).

### Conditional recommendations

**If operator states reading A (active retail trading is the goal):**
- Recommend T6 framework DR10 revision (path B)
- Within T6, recommend **Option C (drop turnover branch, keep cost-drag)** as the most-integrity-preserving change that addresses the root cause. The original DR10 name `turnover_cost_explosion` implies cost was the load-bearing concern; the turnover branch was a structural proxy. Dropping the proxy while keeping the cost test is principled simplification.
- Alternative within T6: Option B (raise threshold) anchored to academic CTA-norm turnover (5–20× is typical for systematic CTA strategies).

**If operator states reading B (discipline-as-value is the goal):**
- Recommend T1 cash-equity nano-sizing (path A) — honestly produces sealed lifecycle artifacts at the boundary the framework allows.
- OR Option A status-quo confirmation — formally documents DR10 stays at 0.50 after explicit review.

**If operator states reading C (trading-bot not the priority):**
- Recommend halt (path C) — stop sealed-artifact authoring on the trading-bot track. Preserve all existing sealed chains as historical record. Reallocate operator attention.

### What this memo does NOT recommend

- Authoring T1 without intent statement
- Authoring T6 SEAL revision without intent statement
- Halting without intent statement
- Modifying DR10 within any existing sealed candidate (forbidden by `no_dr_redefinition_post_seal`)
- Reviving s13-d1 (forbidden by terminal state)
- Authoring another candidate that fails DR10-reachability at PLAN time (T-FORBID-12)

## 12. Posture invariants (all preserved)

- Trading **PAUSED** · Live **BLOCKED_AT_6_GATES** · FRC **NEVER_GRANTED**
- DIAGNOSTIC_ONLY_NOT_LIVE_GRADE permanent
- No profitability / live-readiness / OOS-confirmation / paper-ready / money-proven claims
- K9 not relaxed · DR10 not modified · REC1 / REC1_T1 not demoted
- All sealed artifacts byte-stable
- lessons.md / tmp helpers untouched

## Next-step authorization (operator must state intent first)

```
Strategic intent: <reading A / B / C; one sentence>
```

Then one of:

```
Authorize T1 cash-equity single-name RSI(3) bi-directional Tier-N spec PLAN only -- nano-sizing precommit
Authorize framework-level DR10 SEAL revision to Option C (drop turnover branch, keep cost-drag) only
Authorize framework-level DR10 SEAL revision to Option B (raise threshold to <value>) only
Authorize framework-level confirmation that DR10 remains at 0.50 (Option A; status quo)
Defer / Pause trading-bot track
```
