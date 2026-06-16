# Build Report — Portfolio Capital-Efficiency Metric Spec v1 (P2)

> **Research-only. Advisory-only. Metric spec / framework only.** No metric
> computed, no real portfolio result, no broker, no live capital, no orders, no
> data fetch, no detector, no replay, no backtest. **C10 deferred and
> untouched.**

**Layer:** `portfolio_capital_efficiency_metric_spec_v1` · **Phase:**
`P2_efficiency_metric_spec` · **Build date:** 2026-06-16 · **Lane status:**
`WATCH` · **Companions:** P0 protocol + P1 input contract.

## What this bundle is

The **P2 Metric Spec** for the Portfolio Capital-Efficiency lane. It pins the
**exact formula, required inputs, units, range, and validation rules** for each
of the five capital-efficiency metrics, plus shared symbols, per-metric input
dependencies (referencing the P1 frozen fields), global validation rules, and
the **schema of the future advisory report**.

It **computes nothing** and produces **no real portfolio result** — every
metric carries `computed_in_this_bundle = false` and `compute_enabled = false`.

## Metrics defined (formula only; none computed)

1. **`capital_at_risk_budget`** — `utilisation = (Σ w_i·σ_i)/B`; constraint `Σ w_i·σ_i ≤ B`.
2. **`candidate_overlap`** — weighted Jaccard over `{asset, regime, direction}`; range `[0,1]`.
3. **`diversification_ratio`** — `DR = (Σ w_i·σ_i)/σ_p`; range `≥ 1`.
4. **`concentration_limit`** — `share_g` vs pre-declared cap `L`; breach ⇒ FAIL.
5. **`marginal_capital_efficiency`** — `MCE_i = e_i/mrc_i`; **ranking only**.

`σ_p`, `ρ_ij` (from the future P4 method), `B` and `L` (operator-declared
constants) are pinned in the shared-symbols table. Pre-declared constants are
**never fit to data**; every division-by-zero / empty-set case is an explicit
**UNDEFINED + flag**, never a silent default.

## Candidate #10 — still deferred, NOT connected

`c10_boundary.connection_status = deferred_not_connected`,
`must_not_touch_c10 = true`. C10 is not read, connected, or depended on. It
becomes an admissible input only once it has its **own FROZEN, committed**
replay artifact (P1 rules) — never the working tree. C10's pre-existing `M`
working-tree state was left exactly as found.

## Files created

- `reports/portfolio_capital_efficiency_metric_spec_v1/metric_spec.json`
- `reports/portfolio_capital_efficiency_metric_spec_v1/metric_spec.md`
- `reports/portfolio_capital_efficiency_metric_spec_v1/report.json`
- `reports/portfolio_capital_efficiency_metric_spec_v1/report.md`
- `tools/portfolio_capital_efficiency_metric_spec_check.py` (stdlib-only validator)
- `tests/test_portfolio_capital_efficiency_metric_spec.py` (26 tests)

Plus append-only memory entries in `decisions.md`, `next_actions.md`, and
`logs/system_changes.md`.

## Verification

```
.venv/Scripts/python.exe tools/portfolio_capital_efficiency_metric_spec_check.py validate
  -> validate: OK

.venv/Scripts/python.exe -m pytest \
  tests/test_portfolio_capital_efficiency_metric_spec.py \
  tests/test_portfolio_capital_efficiency_input_contract.py \
  tests/test_portfolio_capital_efficiency_protocol.py --rootdir=tests -q
  -> 75 passed in 0.72s   (26 P2 + 24 P1 + 25 P0)
```

## Recommended next bundle (operator picks; separately authorized, spec-only)

1. **Allocation Baseline Spec v1** (P3) — equal-weight / inverse-vol /
   capped-weight reference models + concentration cap.
2. **Overlap/Correlation Method v1** (P4) — supplies `ρ_ij` for the
   diversification ratio + marginal capital efficiency.
3. **Advisory Memo Schema v1** (P5) — finalises the advisory report schema.

A separate, separately-authorized **compute bundle** is what would actually run
these formulas over frozen admissible inputs.

## No-profit-claim

This spec does not imply edge and does not allocate capital. A defined formula
does not imply profit. A capital-efficiency score does not imply future
returns. No allocation is authorized by this spec alone.
