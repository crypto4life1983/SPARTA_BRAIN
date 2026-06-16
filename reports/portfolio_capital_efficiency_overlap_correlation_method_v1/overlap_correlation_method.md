# SPARTA Portfolio Capital-Efficiency Overlap/Correlation Method v1

> **Research-only. Advisory-only. Overlap/correlation method spec / framework
> only.** No broker control. No live trading. No live capital allocation. No
> paper-order execution. No order sizing. No exchange connection. No API keys.
> No `.env`. No scheduler. **No external network calls. No real overlap or
> correlation is computed in this bundle. No real portfolio result is produced.
> No data fetch, no detector, no replay, no backtest.** This spec pins *how*
> overlap, correlation, redundancy, and independence would be measured — it
> computes nothing and reads no live strategy results.

**Method id:** `portfolio_capital_efficiency_overlap_correlation_method_v1` ·
**version:** `1.0` · **phase:** `P4_overlap_correlation_method`

**Lane status (self-declared):** `WATCH` — inherits the upstream registries'
verdict ceiling; never surfaces PASS / ACTIVE / STRONG.

**Companions:** P0 protocol, P1 input contract, P2 metric spec, P3 allocation
baseline spec.

---

## 1. Objective + posture

Pin the **exact method, inputs, units, range, and validation rules** for
measuring **overlap, correlation, redundancy, and independence** between any
two FROZEN admissible strategies — the `rho_ij` and redundancy signals consumed
by the P2 metrics and P3 baselines.

This bundle is **spec/framework-only**: it defines *how* each measure *would*
be computed from FROZEN per-trade / per-period series.
**No real overlap or correlation is computed in this bundle.**
It produces no real portfolio result and reads no live strategy results.

## 2. Candidate #10 — still deferred, NOT connected

**Candidate #10 remains deferred and is not connected by this method.** It is
not read, connected, or depended on. C10's per-trade / per-period series are
exactly the shape these measures consume — but C10 is **deferred**: it becomes
eligible only once it has its **own FROZEN, committed** replay artifact admitted
under the P1 contract, never the working tree.

## 3. Required frozen series (read-only, frozen-only)

These measures need richer FROZEN per-trade / per-period series than the P1
summary fields, supplied by a committed, checksummed **replay artifact**:
`in_position_flag_t`, `capital_at_risk_t`, `symbol_t`, `direction_t`,
`period_return_r_t`, `drawdown_flag_t`. A future P1 amendment (or the frozen
replay artifact itself) formally admits these. **No live strategy results are
ever read.**

## 4. Shared symbols

`T_common` (aligned common window) · `N_min` (pre-declared min aligned samples)
· `rho_ij` (return correlation consumed by P2 + P3) · `tau_low`, `tau_high`
(redundancy thresholds) · `rho_low` (independence correlation threshold). All
thresholds are **pre-declared operator constants**, never fit.

## 5. Methods (formula + inputs + rules; **none computed here**)

### 5.1 `trade_time_overlap_pct`
- **Formula:** Jaccard over in-position time:
  `|{t: in_i ∧ in_j}| / |{t: in_i ∨ in_j}|` over `T_common`.
- Inputs `in_position_flag_t`; range `[0,1]`; empty union → UNDEFINED+flag.

### 5.2 `simultaneous_capital_at_risk_overlap`
- **Formula:** `Σ min(car_i,car_j) / Σ max(car_i,car_j)` over `T_common`.
- Inputs `capital_at_risk_t`; range `[0,1]`; zero max-sum → UNDEFINED+flag.

### 5.3 `same_symbol_overlap`
- **Formula:** of simultaneous in-position time, fraction on the same canonical
  symbol.
- Inputs `in_position_flag_t`, `symbol_t`; range `[0,1]`; empty denom →
  UNDEFINED+flag; unmapped symbol flagged.

### 5.4 `same_direction_overlap`
- **Formula:** of simultaneous same-symbol time, fraction in the same
  direction; opposite direction surfaced as a separate **`hedging_offset`**
  flag, never netted.
- Inputs `direction_t`, `symbol_t`, `in_position_flag_t`; range `[0,1]`.

### 5.5 `return_stream_correlation` — `rho_ij`
- **Formula:** `rho_ij = cov(r_i,r_j) / (sd(r_i)·sd(r_j))` over `T_common` with
  ≥ `N_min` periods. **This is the `rho_ij` consumed by P2 + P3.**
- Inputs `period_return_r_t`; range `[-1,1]`; `sd==0` or `< N_min` →
  UNDEFINED+flag (never 0).

### 5.6 `drawdown_period_overlap`
- **Formula:** Jaccard over drawdown windows:
  `|{t: dd_i ∧ dd_j}| / |{t: dd_i ∨ dd_j}|` over `T_common`.
- Inputs `drawdown_flag_t`; range `[0,1]`; no drawdown anywhere →
  UNDEFINED+flag.

### 5.7 `redundancy_score`
- **Formula:** pre-declared-weighted blend of trade-time / car / same-symbol /
  same-direction / `max(rho_ij,0)` / drawdown overlap. UNDEFINED components are
  **excluded** (weights renormalised); all UNDEFINED → redundancy UNDEFINED.
- Range `[0,1]`; only the **positive** part of `rho_ij` feeds redundancy.

### 5.8 `diversification_benefit_score`
- **Formula:** `1 − redundancy(i,j)`; reported beside the P2
  diversification_ratio. UNDEFINED redundancy → UNDEFINED (never defaulted to 1).
- Range `[0,1]`; higher = more diversifying.

## 6. Independence classification

Map `redundancy(i,j)` (and `rho_ij`) to a class via pre-declared thresholds:

| Class | Rule |
|---|---|
| `independent` | `redundancy ≤ tau_low` AND `|rho_ij| ≤ rho_low` (both defined). |
| `partial_overlap` | `tau_low < redundancy ≤ tau_high` (defined). |
| `redundant` | `redundancy > tau_high` (defined). |
| `undefined` | redundancy/`rho_ij` UNDEFINED or fewer than `N_min` aligned periods. **Never silently coerced to another class.** |

`tau_low < tau_high`, all thresholds pre-declared, never fit; the **`undefined`
class is mandatory**.

## 7. Downstream consumers

- **P2:** `rho_ij` → `diversification_ratio` + `marginal_capital_efficiency`;
  redundancy/overlap → `candidate_overlap` context.
- **P3:** `rho_ij` + redundancy → equal-risk refinements + the
  `ranking_only_marginal_efficiency` ordering.
- (Spec dependencies only — no value is computed or passed in this bundle.)

## 8. Global method validation rules

- **Frozen admissible inputs only**; live / networked / uncommitted inputs
  inadmissible.
- **Aligned common window required** — no zero-padding or forward-fill.
- **Minimum sample size `N_min`** — below it, measure (and dependent class) is
  UNDEFINED.
- **No lookahead**; **reproducible** bit-for-bit; **pre-declared constants never
  fit**.
- **UNDEFINED over silent default**; **negative correlation is diversifying**,
  never overlap.
- **No real overlap or correlation in this bundle.**

## 9. PASS / WATCH / FAIL rules

- **PASS** (for review only) — inputs FROZEN admissible series; measures use the
  aligned `T_common` with ≥ `N_min` periods; constants operator-supplied;
  UNDEFINED handling respected; independence class ∈ {independent,
  partial_overlap, redundant, undefined}; WATCH ceiling held; reproduces
  bit-for-bit. **PASS means "measures fit for human review", never "allocate" or
  "execute".**
- **WATCH** — computable but borderline (short window near `N_min`, several
  accepted UNDEFINED components, sparse drawdown overlap); documented +
  re-checked.
- **FAIL** — inadmissible/unfrozen/live input; a zero-padded or forward-filled
  window; a constant fit to data; a zero-variance correlation silently set to 0;
  an UNDEFINED case coerced to a definite class; or a bypassed WATCH ceiling.

## 10. Required future artifacts

- **Advisory Memo Schema v1** (P5) — finalises the report schema hosting these
  measures + the independence classification.
- A possible **P1 amendment** formally admitting the FROZEN per-trade /
  per-period series.
- A separately-authorized **compute bundle** that actually runs these measures
  over frozen admissible series.
- Lane closeout memo if the idea PARKs / RETIREs.

## 11. No-profit-claim policy

- This method does not imply edge and does not allocate capital.
- A defined overlap or correlation measure does not imply profit.
- A capital-efficiency score does not imply future returns.
- An advisory allocation memo is a human-review aid, never an execution
  instruction.
- No allocation is authorized by this method alone.

## 12. Safety boundaries (pinned, non-negotiable)

- Research-only. Advisory-only. Overlap/correlation method spec / framework only.
- No broker control, no exchange connection, no API keys, no `.env`, no
  credential handling.
- No live trading. No live capital allocation. No paper-order execution. No
  order placement. No order sizing for execution.
- No scheduler / background daemon. No external network calls in this method's
  runtime.
- No real overlap or correlation computed, no real portfolio result, no data
  fetch, no detector, no replay, no backtest in this bundle.
- Do not read live strategy results. Do not read, edit, stage, or modify
  Candidate #10 files, tests, artifacts, labels, replay, detector, or
  working-tree state.
- Candidate #10 remains deferred and is not connected by this method; C10 must
  finish and freeze by itself first.
- Consume only FROZEN, committed, admissible artifacts; never live positions or
  uncommitted working trees.
- Do not claim profitability. Do not claim live-readiness. Do not claim STRONG
  evidence from this method alone.
- **A capital-efficiency score does not imply future returns.**
- **An advisory allocation is not an execution instruction.**
- **No allocation is authorized by this method alone.**
