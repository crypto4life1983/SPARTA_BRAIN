# SPARTA Portfolio Capital-Efficiency Protocol Memo v1

> **Research-only. Advisory-only. Protocol / specification only.**
> No broker control. No live trading. No live capital allocation. No
> paper-order execution. No order sizing for execution. No exchange
> connection. No API keys. No `.env`. No credential handling. No scheduler /
> background daemon. **No external network calls. No data fetch. No metric
> computed. No allocation computed in this bundle.** This memo defines how
> SPARTA will study **capital efficiency across its bench of researched
> strategy candidates** — diversification, overlap, concentration limits, and
> capital-at-risk budgeting — **before** any metric is computed, any
> allocation is suggested, or any capital is sized.

**Protocol id:** `portfolio_capital_efficiency_protocol_v1` · **version:** `1.0`

**Lane status (self-declared):** `WATCH` — this lane is never ACTIVE and
never STRONG. It inherits the upstream registry's verdict ceiling (WATCH
max) and never surfaces PASS / ACTIVE / STRONG on any candidate it reads.

**Lane history note:** This v1 memo **opens a NEW research lane** that
studies how research capital-at-risk *could* be allocated **across** SPARTA's
existing strategy bench. It does **not** propose, change, or execute any
allocation. It consumes only **FROZEN, committed** research artifacts
(read-only). It never reads live positions, broker balances, or the in-flight
working-tree state of any candidate.

---

## 1. Lane + purpose

- **Lane:** `portfolio_capital_efficiency`.
- **Purpose:** define — specification only — how SPARTA will study capital
  efficiency across its researched strategy candidates: diversification,
  overlap / redundancy, concentration limits, and capital-at-risk budgeting.
- **Final lane output (future, separately authorized):** an **ADVISORY** memo
  only — per-candidate *suggested research weight* + rationale + caveats for
  **human review**. No capital is ever allocated, sized, or executed by this
  lane.

This lane is about *using the bench efficiently*, not about discovering a new
edge. It sits **downstream** of the per-strategy research lanes (crypto-D1,
arbitrage, the detector candidates) and reads only what they have **frozen**.

## 2. Scope

**In scope**

- Read-only analysis of FROZEN, committed research artifacts (e.g.
  `strategy_report_registry` / `strategy_candidate_registry` outputs, frozen
  per-strategy backtest `report.json` verdicts).
- Defining capital-efficiency metrics on paper (formulas + inputs named, **not
  computed** in this bundle).
- Defining baseline allocation models on paper (equal-weight,
  inverse-volatility, capped-weight) as research reference points only.
- Defining the shape of a future **advisory** allocation memo.

**Out of scope**

- Live capital. Real broker / exchange balances. Real positions.
- Position sizing for execution. Order sizing. Order placement.
- Any change to live or paper trading logic or execution files.
- Computing any metric or allocation in this bundle (P0 is spec only).
- Reading, modifying, or depending on any in-flight (uncommitted) candidate
  working-tree state.

## 3. Candidate #10 boundary (pinned)

This lane **MUST NOT** read-for-mutation, edit, stage, or depend on the
in-flight **Candidate #10** (intraweek calendar seasonality) files, tests,
labels, replay, detector, or working-tree state. If C10 ever produces a
**FROZEN, committed** verdict artifact, that frozen artifact may later be
treated like any other read-only bench input — but only the committed / frozen
form, **never** the working tree.

## 4. Input sources (read-only, frozen-only)

| Source | Form | Access |
|---|---|---|
| `strategy_report_registry` | frozen committed `report.json` artifacts under `reports/` | read-only |
| `strategy_candidate_registry` | frozen committed candidate status summaries | read-only |
| `frozen_backtest_reports` | committed per-strategy `report.json` (PASS/WATCH/FAIL + cost-aware stats) | read-only |

Verdicts are **verdict-ceilinged to WATCH** upstream; this lane inherits that
ceiling and never surfaces PASS / ACTIVE / STRONG.

**Inadmissible inputs:** live broker / exchange balances or positions; any
uncommitted working-tree artifact (including in-flight C10); any dataset not
frozen with checksums upstream; any number from a live network fetch.

## 5. Capital-efficiency metrics (define, **do not compute**)

| ID | Label | Defined as |
|---|---|---|
| `capital_at_risk_budget` | Capital-at-risk budget | Pre-declared total research risk envelope any future advisory allocation must sum within. |
| `candidate_overlap` | Candidate overlap / redundancy | Pairwise similarity of two candidates' signal exposure (same asset / regime / direction) to flag redundant capital. |
| `diversification_ratio` | Diversification ratio | Weighted-average standalone risk ÷ combined portfolio risk; higher = capital spread across less-correlated edges. |
| `concentration_limit` | Concentration limit | Max share of the budget any single candidate / asset / family may hold. |
| `marginal_capital_efficiency` | Marginal capital efficiency | Advisory return-per-unit-marginal-risk a candidate adds — used only to **rank for human review**, never to auto-size. |

Each metric is **definition-only** here. Formulas and inputs are pinned in the
P2 spec; nothing is computed in this bundle.

## 6. Allocation baselines (reference only)

| ID | Label | Status |
|---|---|---|
| `equal_weight` | Equal-weight reference | reference |
| `inverse_volatility` | Inverse-volatility reference | reference |
| `capped_weight` | Capped-weight reference (subject to concentration cap) | reference |
| `discretionary_human` | Discretionary human allocation | **WATCH only** |

The discretionary-human model is intentionally **WATCH-only**: the operator
allocates by judgment using the advisory memo. **This lane informs, it does not
decide.**

## 7. Validation phases

| Phase | Purpose |
|---|---|
| **P0_protocol** | This bundle. Lock language, scope, capital boundaries, kill rules. No data, no compute, no allocation. |
| **P1_input_contract** | Define which FROZEN committed artifacts are admissible + freeze rules. Spec only. |
| **P2_efficiency_metric_spec** | Pin exact formulas + inputs per metric. Spec only; nothing computed. |
| **P3_allocation_baseline_spec** | Pin the reference models + concentration cap. Spec only. |
| **P4_overlap_correlation_spec** | Pin the overlap / correlation / redundancy estimation method. Spec only. |
| **P5_advisory_report_shape** | Pin the schema of the future advisory allocation memo. Spec only. |
| **P6_robustness_sensitivity** | Define estimation-error stress (correlation drift, expectancy decay). Compute needs separate authorization. |
| **P7_paper_allocation_simulation** | Paper allocation **SIMULATION ONLY** (no broker, no order, no live capital) — and **only** under a SEPARATE future authorization. |
| **P8_live_capital_allocation** | **EXPLICITLY OUT OF SCOPE.** Real capital requires a SEPARATE far-future protocol + authorizations after evidence exists. |

## 8. PASS / WATCH / FAIL rules

- **PASS** — A future advisory allocation is PASS-grade **for review only**
  when: it draws solely on FROZEN admissible inputs; respects the
  pre-declared capital-at-risk budget and concentration limits; is stable
  under the P6 estimation-error stress; does not concentrate the bench into a
  single asset / family / regime; every weight carries a written rationale +
  caveat; and no rule was changed mid-study. **PASS means "fit for human
  review", never "execute".**
- **WATCH** — Plausible efficiency improvement but at least one of: high
  sensitivity to estimation error; reliance on a thin candidate set;
  concentration near a limit; inputs only partially frozen. Stays advisory.
- **FAIL** — Depends on inadmissible / unfrozen inputs; breaches the budget or
  a concentration limit; collapses under estimation-error stress; or
  implicitly assumes execution. FAIL allocations are **discarded**, not
  down-weighted.

## 9. Kill conditions

- Any input sourced from live balances, live positions, a network fetch, or an
  uncommitted working tree (including in-flight C10).
- An advisory allocation is treated, described, or wired as an execution
  instruction.
- A concentration limit or the capital-at-risk budget is silently exceeded.
- A metric or weight is computed inside a spec bundle.
- The upstream verdict ceiling (WATCH max) is bypassed so PASS / ACTIVE /
  STRONG leaks into an allocation.
- Results cannot be reproduced bit-for-bit from the named frozen inputs by a
  second offline run.

## 10. Required future artifacts

- **Portfolio Capital-Efficiency Input Contract v1** (P1) — admissible frozen
  artifacts + freeze rules. Spec only.
- **Portfolio Capital-Efficiency Metric Spec v1** (P2) — exact formulas +
  inputs. Spec only.
- **Portfolio Capital-Efficiency Allocation Baseline Spec v1** (P3) —
  reference models + concentration cap. Spec only.
- **Portfolio Capital-Efficiency Overlap/Correlation Method v1** (P4) —
  redundancy estimation method. Spec only.
- **Portfolio Capital-Efficiency Advisory Memo Schema v1** (P5) — shape of the
  human-review allocation memo.
- Lane closeout memo if the capital-efficiency idea PARKs / RETIREs.

## 11. No-profit-claim policy

- This protocol does not imply edge and does not allocate capital.
- A capital-efficiency score does not imply future returns.
- An advisory allocation memo is a human-review aid, never an execution
  instruction.
- No paper or live capital allocation is authorized.
- No allocation is authorized by this protocol alone (P5+ outputs require their
  own separate authorization).

## 12. Safety boundaries (pinned, non-negotiable)

- Research-only. Advisory-only. Protocol / specification only.
- No broker control, no exchange connection, no API keys, no `.env`, no
  credential handling.
- No live trading. No live capital allocation. No paper-order execution. No
  order placement. No order sizing for execution.
- No scheduler / background daemon. No external network calls in this
  protocol's runtime.
- No data fetch, no metric computed, no allocation computed in this bundle.
- Do not modify paper / live execution files. Do not touch Candidate #10
  files, tests, labels, replay, detector, or working-tree state.
- Consume only FROZEN, committed, admissible artifacts; never live positions
  or uncommitted working trees.
- Do not claim profitability. Do not claim live-readiness. Do not claim STRONG
  evidence from this protocol alone.
- **A capital-efficiency score does not imply future returns.**
- **An advisory allocation is not an execution instruction.**
- **No allocation is authorized by this protocol alone.**
