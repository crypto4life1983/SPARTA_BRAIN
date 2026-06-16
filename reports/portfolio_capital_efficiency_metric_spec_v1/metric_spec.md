# SPARTA Portfolio Capital-Efficiency Metric Spec v1

> **Research-only. Advisory-only. Metric spec / framework only.**
> No broker control. No live trading. No live capital allocation. No
> paper-order execution. No order sizing. No exchange connection. No API keys.
> No `.env`. No scheduler. **No external network calls. No metric is computed
> in this bundle. No real portfolio result is produced. No data fetch, no
> detector, no replay, no backtest.** This spec pins *how* each
> capital-efficiency metric would be computed from FROZEN admissible inputs —
> it does not compute anything.

**Metric spec id:** `portfolio_capital_efficiency_metric_spec_v1` ·
**version:** `1.0` · **phase:** `P2_efficiency_metric_spec`

**Lane status (self-declared):** `WATCH` — inherits the upstream registries'
verdict ceiling; never surfaces PASS / ACTIVE / STRONG.

**Companions:** `reports/portfolio_capital_efficiency_protocol_v1/`,
`reports/portfolio_capital_efficiency_input_contract_v1/`.

---

## 1. Objective + posture

Pin the **exact formula, required inputs, units, range, and validation rules**
for each capital-efficiency metric defined (definition-only) in the P0
protocol, plus the **schema of the future advisory report**.

This bundle is **spec/framework-only**: it defines *how* each metric *would* be
computed from FROZEN admissible inputs (per the P1 Input Contract). It computes
**no metric** and produces **no real portfolio result**.
**No metric is computed in this bundle.**
Computation is a separate, separately-authorized bundle.

## 2. Candidate #10 — still deferred, NOT connected

**Candidate #10 remains deferred and is not connected by this spec.** It is not
read, connected, or depended on here. Only once C10 has its **own FROZEN,
committed** replay artifact does it become an ordinary admissible input under
the P1 rules — never the working tree.

## 3. Shared symbols

| Symbol | Meaning |
|---|---|
| `w_i` | Proposed research weight of candidate *i* (advisory, **never** an execution size); `0 <= w_i`, `sum_i w_i = 1`. |
| `sigma_i` | `standalone_risk` of *i*, from its FROZEN per-strategy report (P1 field). |
| `rho_ij` | Pairwise correlation estimate, supplied by the **P4** method (not estimated here). |
| `sigma_p` | Portfolio aggregate: `sigma_p = sqrt( sum_i sum_j w_i w_j rho_ij sigma_i sigma_j )`. |
| `e_i` | `frozen_cost_aware_expectancy` of *i*, from its FROZEN report (P1 field). |
| `B` | Pre-declared total capital-at-risk envelope (operator scalar; never inferred). |
| `L` | Pre-declared concentration cap in `(0, 1]` (operator scalar; never inferred). |

## 4. Metrics (formula + inputs + rules; **none computed here**)

### 4.1 `capital_at_risk_budget` — budget utilisation
- **Formula:** `car_i = w_i * sigma_i`; `utilisation = ( sum_i car_i ) / B`;
  **constraint** `sum_i car_i <= B`.
- **Inputs:** operator `B`, `w_i`, `standalone_risk`.
- **Units/range:** fraction of `B`; a future allocation is FAIL if
  `utilisation > 1`.
- **Rules:** `B` operator-declared `> 0`, never inferred; missing/`<=0` → UNDEFINED+flag.

### 4.2 `candidate_overlap` — pairwise redundancy
- **Formula:** for `D in {asset, regime, direction}`,
  `jaccard_D(i,j) = |A_i^D ∩ A_j^D| / |A_i^D ∪ A_j^D|`;
  `overlap(i,j) = ( w_asset*jaccard_asset + w_regime*jaccard_regime + w_dir*jaccard_dir ) / ( w_asset + w_regime + w_dir )`,
  with pre-declared dimension weights.
- **Inputs:** `asset_exposure`, `regime_exposure`, `direction`.
- **Units/range:** dimensionless `[0, 1]` (1 = fully redundant).
- **Rules:** dimension weights pre-declared, never fit; empty union for a
  dimension → that dimension UNDEFINED and **excluded** (never 0 or 1).

### 4.3 `diversification_ratio`
- **Formula:** `DR = ( sum_i w_i sigma_i ) / sigma_p`.
- **Inputs:** `w_i`, `standalone_risk`, `rho_ij` (from P4).
- **Units/range:** dimensionless `>= 1`; higher = more diversified.
- **Rules:** `rho_ij` from P4 (not estimated here); `sigma_p == 0` → UNDEFINED+flag.

### 4.4 `concentration_limit` — breach check
- **Formula:** for grouping `G in {candidate, asset, family}`,
  `share_g = ( sum_{k in g} w_k ) / ( sum_all w )`; **BREACH** if any
  `share_g > L`.
- **Inputs:** per-candidate/asset/family weight, operator `L`.
- **Units/range:** fraction `[0, 1]`; allocation is FAIL if any `share_g > L`.
- **Rules:** `L` operator-declared in `(0, 1]`, never inferred; unmapped
  candidate flagged, never silently grouped; a breach is FAIL, not a down-weight.

### 4.5 `marginal_capital_efficiency` — **ranking only**
- **Formula:** `mrc_i = ( w_i * sum_j w_j rho_ij sigma_i sigma_j ) / sigma_p`;
  `MCE_i = e_i / mrc_i`.
- **Inputs:** `frozen_cost_aware_expectancy`, `w_i`, `standalone_risk`, `rho_ij`
  (from P4).
- **Units/range:** after-cost expectancy per unit of marginal portfolio risk;
  real-valued; used **only** to rank candidates for human review.
- **Rules:** **ranking only** — never converted into an auto-sizing or
  execution instruction; `mrc_i == 0` → UNDEFINED+flag; inputs must be FROZEN
  admissible (a bypassed PASS/ACTIVE/STRONG verdict is inadmissible).

## 5. Global metric validation rules

- **Frozen admissible inputs only** (P1); live / networked / uncommitted inputs
  inadmissible.
- **No lookahead**; **reproducible** bit-for-bit; **units declared per metric**.
- **Pre-declared constants never fit** — `B`, `L`, overlap dimension weights are
  operator constants.
- **UNDEFINED over silent default** — any division-by-zero / empty-set case is
  an explicit UNDEFINED+flag, never a silent 0 / 1 / +inf.
- **marginal_capital_efficiency is ranking-only.**
- **Verdict ceiling inherited** — every output carries WATCH; PASS/ACTIVE/STRONG
  never surfaced.
- **No real result in this bundle.**

## 6. Advisory report schema (future P5 output; **not produced here**)

- **Portfolio-level:** `report_id`, `lane`, `verdict_ceiled`,
  `pre_declared_total_risk_envelope_B`, `pre_declared_concentration_cap_L`,
  `capital_at_risk_utilisation`, `diversification_ratio`,
  `concentration_breaches`, `input_provenance`, `caveats`.
- **Per-candidate:** `candidate_id`, `verdict_ceiled`,
  `proposed_research_weight_w_i`, `standalone_risk_sigma_i`,
  `max_pairwise_overlap`, `marginal_capital_efficiency_rank`, `rationale`,
  `caveat`, `dataset_freeze_ref`, `contract_version_pin`.
- Every row requires a **rationale + caveat** and inherits the **WATCH** ceiling.

## 7. PASS / WATCH / FAIL rules

- **PASS** (for review only) — every input FROZEN + admissible; constants
  operator-supplied; units/range + UNDEFINED handling respected; marginal
  efficiency ranking-only; WATCH ceiling held; reproduces bit-for-bit. **PASS
  means "metrics fit for human review", never "allocate" or "execute".**
- **WATCH** — computable but borderline (sparse P4 correlation coverage, thin
  candidate set, an accepted UNDEFINED flag); documented + re-checked.
- **FAIL** — inadmissible/unfrozen input; a constant fit to data; a silent
  division-by-zero default; marginal efficiency used to auto-size; an ignored
  budget/concentration breach; or a bypassed WATCH ceiling.

## 8. Required future artifacts

- **Allocation Baseline Spec v1** (P3) — reference models + concentration cap.
- **Overlap/Correlation Method v1** (P4) — supplies `rho_ij`.
- **Advisory Memo Schema v1** (P5) — finalises the report schema.
- A separately-authorized **compute bundle** that actually runs these formulas
  over frozen admissible inputs.
- Lane closeout memo if the idea PARKs / RETIREs.

## 9. No-profit-claim policy

- This spec does not imply edge and does not allocate capital.
- A defined formula does not imply profit.
- A capital-efficiency score does not imply future returns.
- An advisory allocation memo is a human-review aid, never an execution
  instruction.
- No allocation is authorized by this spec alone.

## 10. Safety boundaries (pinned, non-negotiable)

- Research-only. Advisory-only. Metric spec / framework only.
- No broker control, no exchange connection, no API keys, no `.env`, no
  credential handling.
- No live trading. No live capital allocation. No paper-order execution. No
  order placement. No order sizing for execution.
- No scheduler / background daemon. No external network calls in this spec's
  runtime.
- No metric computed, no real portfolio result, no data fetch, no detector, no
  replay, no backtest in this bundle.
- Do not modify paper / live execution files. Do not read Candidate #10
  working-tree files, tests, labels, replay, or detector.
- Candidate #10 remains deferred and is not connected by this spec; C10 must
  finish and freeze by itself first.
- Consume only FROZEN, committed, admissible artifacts; never live positions or
  uncommitted working trees.
- Do not claim profitability. Do not claim live-readiness. Do not claim STRONG
  evidence from this spec alone.
- **A capital-efficiency score does not imply future returns.**
- **An advisory allocation is not an execution instruction.**
- **No allocation is authorized by this spec alone.**
