# SPARTA Portfolio Capital-Efficiency Advisory Memo Schema v1

> **Research-only. Advisory-only. Advisory memo schema / framework only.**
> No broker control. No live trading. No live capital allocation. No capital
> deployment. No paper-order execution. No order sizing. No exchange
> connection. No API keys. No `.env`. No scheduler. **No external network
> calls. No real results are computed in this bundle. No real memo is produced.
> No data fetch, no detector, no replay, no backtest.** This schema pins the
> *structure* and *allowed verdict language* of the future advisory memo — it
> computes nothing and connects no indicator results.

**Advisory memo schema id:**
`portfolio_capital_efficiency_advisory_memo_schema_v1` · **version:** `1.0` ·
**phase:** `P5_advisory_memo_schema`

**Lane status (self-declared):** `WATCH` — inherits the upstream registries'
verdict ceiling; never surfaces PASS / ACTIVE / STRONG on any candidate or
basket.

**Companions:** P0 protocol, P1 input contract, P2 metric spec, P3 allocation
baseline spec, P4 overlap/correlation method.

---

## 1. Objective + posture

Pin the **exact structure** of the future Portfolio Capital-Efficiency advisory
memo — its required sections and the allowed verdict language — so a later,
separately-authorized **compute bundle** has a fixed, safe home for its outputs.

This bundle is **spec/framework-only**: it defines the report shape.
**No real results are computed in this bundle.**
It produces no real memo, suggests no allocation, and connects no indicator
results.

## 2. Candidate #10 — still deferred, NOT connected

**Candidate #10 remains deferred and is not connected by this schema.** In any
future memo, C10 is reported under the inadmissible/deferred-inputs summary
(classification `watch_only_inadmissible`) until it has its **own FROZEN,
committed** replay artifact admitted under P1 — never the working tree.

## 3. Required memo sections (10)

| # | Section id | Purpose |
|---|---|---|
| 1 | `admissible_frozen_inputs_summary` | Every FROZEN, committed, admissible strategy artifact used, with freeze ref + contract version. |
| 2 | `inadmissible_deferred_inputs_summary` | Every excluded / deferred strategy (incl. C10 while deferred). |
| 3 | `per_strategy_standalone_summary` | Standalone risk, frozen cost-aware expectancy, asset/regime/direction exposure. |
| 4 | `overlap_correlation_summary` | Pairwise overlap, `rho_ij`, redundancy, diversification benefit, independence class (P4). |
| 5 | `allocation_baseline_comparison` | Advisory weights under each P3 baseline + cash bucket + breaches. |
| 6 | `capital_efficiency_ranking` | Ranking-only ordering by marginal capital efficiency (never auto-sizes). |
| 7 | `basket_usefulness_classification` | Classify each candidate/basket using ONLY the allowed classifications. |
| 8 | `risk_warnings_and_limitations` | Estimation error, thin samples, regime dependence, stale frozen inputs, no-profit restatement. |
| 9 | `operator_decision_checklist` | Human-review checklist; the operator decides. |
| 10 | `no_action_recommendation` | When inputs are missing or UNDEFINED → explicit NO ACTION. |

Every candidate row requires a **rationale + caveat** and inherits the **WATCH**
ceiling.

## 4. Allowed classifications (exhaustive — the only labels permitted)

| Classification | Tier | Meaning |
|---|---|---|
| `watch_only_useful_candidate` | WATCH | Admissible candidate that looks individually useful for more research. |
| `watch_only_basket_candidate` | WATCH | Admissible candidate that adds diversification benefit to a basket (low redundancy). |
| `watch_only_redundant_candidate` | WATCH | Admissible candidate highly redundant with the bench (flagged for de-prioritisation). |
| `watch_only_inadmissible` | WATCH | Excluded / deferred (unfrozen / uncommitted / bypassed-verdict), incl. C10 while deferred; zero advisory weight. |
| `undefined_insufficient_data` | UNDEFINED | Inputs missing or a required measure UNDEFINED / insufficient → memo recommends NO ACTION. |

## 5. Forbidden verdict language (never asserted in a memo)

`PASS` · `ACTIVE` · `STRONG` · `approved for paper trading` · `approved for
live trading` · `profit guarantee` · `capital deployment instruction` ·
`broker/order/credential logic`.

**Rules:** allowed classifications are exhaustive; forbidden verdict language is
never asserted; every classification is WATCH-tier or UNDEFINED; no execution /
deployment / order / broker / credential language; missing or UNDEFINED inputs
force `undefined_insufficient_data` + NO ACTION.

## 6. PASS / WATCH / FAIL rules (schema fitness — meta, not a candidate verdict)

- **PASS** — a future memo populates every required section; uses **only** the
  allowed classifications; asserts **none** of the forbidden verdict language;
  draws solely on FROZEN admissible inputs; defaults to no-action on
  missing/UNDEFINED inputs; respects the WATCH ceiling; reproduces bit-for-bit.
  (Here PASS labels **schema fitness for human review**, never a candidate
  verdict and never "deploy" or "execute".)
- **WATCH** — populated but borderline (much weight in cash, several UNDEFINED
  measures, thin admissible set); documented + re-checked.
- **FAIL** — a required section missing; a non-allowed classification or any
  forbidden verdict language used; an inadmissible strategy given positive
  advisory weight; missing/UNDEFINED inputs not forced to no-action; or a
  bypassed WATCH ceiling.

## 7. Required future artifacts

- A separately-authorized **compute bundle** that runs the P2 metrics + P3
  baselines + P4 measures over FROZEN admissible inputs and emits a memo
  conforming to **this** schema.
- A possible **P1 amendment** admitting the FROZEN per-trade / per-period series
  the P4 measures require.
- Lane closeout memo if the idea PARKs / RETIREs.

## 8. No-profit-claim policy

- This schema does not imply edge and does not allocate or deploy capital.
- A defined memo section does not imply profit.
- A capital-efficiency score does not imply future returns.
- An advisory allocation memo is a human-review aid, never an execution
  instruction.
- No allocation is authorized by this schema alone.

## 9. Safety boundaries (pinned, non-negotiable)

- Research-only. Advisory-only. Advisory memo schema / framework only.
- No broker control, no exchange connection, no API keys, no `.env`, no
  credential handling.
- No live trading. No live capital allocation. No capital deployment. No
  paper-order execution. No order placement. No order sizing for execution.
- No scheduler / background daemon. No external network calls in this schema's
  runtime.
- No real results computed, no real memo produced, no data fetch, no detector,
  no replay, no backtest in this bundle.
- A memo may use ONLY the five allowed classifications; PASS / ACTIVE / STRONG
  and any "approved for paper/live trading", profit-guarantee,
  capital-deployment, or broker/order/credential language are forbidden.
- Do not read live strategy results. Do not read, edit, stage, or modify
  Candidate #10 files, tests, artifacts, labels, replay, detector, or
  working-tree state.
- Candidate #10 remains deferred and is not connected by this schema; C10 must
  finish and freeze by itself first.
- Consume only FROZEN, committed, admissible artifacts; never live positions or
  uncommitted working trees.
- Do not claim profitability. Do not claim live-readiness. Do not claim STRONG
  evidence from this schema alone.
- **A capital-efficiency score does not imply future returns.**
- **An advisory allocation is not an execution instruction.**
- **No allocation is authorized by this schema alone.**
