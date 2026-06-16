# Build Report — Portfolio Capital-Efficiency Allocation Baseline Spec v1 (P3)

> **Research-only. Advisory-only. Allocation baseline spec / framework only.**
> No real allocation computed, no capital deployed, no real portfolio result,
> no broker, no live/paper trading, no orders, no data fetch, no detector, no
> replay, no backtest. **C10 deferred and untouched.**

**Layer:** `portfolio_capital_efficiency_allocation_baseline_spec_v1` ·
**Phase:** `P3_allocation_baseline_spec` · **Build date:** 2026-06-16 ·
**Lane status:** `WATCH` · **Companions:** P0 + P1 + P2.

## What this bundle is

The **P3 Allocation Baseline Spec** for the Portfolio Capital-Efficiency lane.
It pins the **method, inputs, and constraints** for each allocation baseline —
the reference models a future advisory memo would compare — plus shared symbols
and the global allocation constraints.

It **computes no real allocation**, deploys no capital, and produces no real
portfolio result (`compute_enabled = false`, `capital_deployment_enabled =
false`, every baseline `computed_in_this_bundle = false`).

## Baselines defined (method only; none computed)

1. **`equal_weight`** — `w_i = 1/|S_admissible|` *(reference)*.
2. **`equal_risk`** — inverse-vol / risk parity `raw_i = 1/σ_i` *(reference)*.
3. **`capped_concentration`** — clip to `L`, redistribute excess, residual →
   cash *(reference)*.
4. **`zero_for_inadmissible`** — `S_inadmissible → w_i = 0`, absolute, overrides
   all *(hard constraint)*.
5. **`ranking_only_marginal_efficiency`** — rank by P2 `MCE_i`; **ranking
   only**, never auto-sizes *(WATCH only)*.
6. **`cash_unallocated_bucket`** — `w_cash = 1 − Σ w_i`; full cash when nothing
   qualifies *(hard constraint)*.

**Global constraints:** weights (incl. cash) sum to one; long-only;
inadmissible → 0; concentration cap `L`; capital-at-risk budget `B`; frozen
admissible inputs only; no lookahead; reproducible; **no real allocation in
this bundle**.

## Candidate #10 — still deferred, NOT connected

`c10_boundary.connection_status = deferred_not_connected`,
`must_not_touch_c10 = true`. C10 is **currently inadmissible** (deferred, not
frozen) and so would receive weight **0** under `zero_for_inadmissible`. It
becomes an ordinary admissible strategy only once it has its **own FROZEN,
committed** replay artifact (P1 rules) — never the working tree. C10's
pre-existing `M` working-tree state was left exactly as found.

## Files created

- `reports/portfolio_capital_efficiency_allocation_baseline_spec_v1/allocation_baseline_spec.json`
- `reports/portfolio_capital_efficiency_allocation_baseline_spec_v1/allocation_baseline_spec.md`
- `reports/portfolio_capital_efficiency_allocation_baseline_spec_v1/report.json`
- `reports/portfolio_capital_efficiency_allocation_baseline_spec_v1/report.md`
- `tools/portfolio_capital_efficiency_allocation_baseline_spec_check.py` (stdlib-only validator)
- `tests/test_portfolio_capital_efficiency_allocation_baseline_spec.py` (28 tests)

Plus append-only memory entries in `decisions.md`, `next_actions.md`, and
`logs/system_changes.md`.

## Verification

```
.venv/Scripts/python.exe tools/portfolio_capital_efficiency_allocation_baseline_spec_check.py validate
  -> validate: OK

.venv/Scripts/python.exe -m pytest \
  tests/test_portfolio_capital_efficiency_allocation_baseline_spec.py \
  tests/test_portfolio_capital_efficiency_metric_spec.py \
  tests/test_portfolio_capital_efficiency_input_contract.py \
  tests/test_portfolio_capital_efficiency_protocol.py --rootdir=tests -q
  -> 103 passed in 0.89s   (28 P3 + 26 P2 + 24 P1 + 25 P0)
```

## Recommended next bundle (operator picks; separately authorized, spec-only)

1. **Overlap/Correlation Method v1** (P4) — supplies `ρ_ij` for equal-risk
   refinements + the marginal-efficiency ranking.
2. **Advisory Memo Schema v1** (P5) — finalises the report schema hosting these
   baselines.
3. A separate, separately-authorized **compute bundle** that actually runs the
   baselines over frozen admissible inputs.

## No-profit-claim

This spec does not imply edge and does not allocate or deploy capital. A
defined allocation baseline does not imply profit. A capital-efficiency score
does not imply future returns. No allocation is authorized by this spec alone.
