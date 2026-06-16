# Build Report — Portfolio Capital-Efficiency Overlap/Correlation Method v1 (P4)

> **Research-only. Advisory-only. Overlap/correlation method spec / framework
> only.** No real overlap/correlation computed, no real portfolio result, no
> broker, no live/paper trading, no orders, no data fetch, no detector, no
> replay, no backtest, no live strategy results read. **C10 deferred and
> untouched.**

**Layer:** `portfolio_capital_efficiency_overlap_correlation_method_v1` ·
**Phase:** `P4_overlap_correlation_method` · **Build date:** 2026-06-16 ·
**Lane status:** `WATCH` · **Companions:** P0 + P1 + P2 + P3.

## What this bundle is

The **P4 Overlap/Correlation Method** for the Portfolio Capital-Efficiency
lane. It pins the **method, inputs, units, range, and validation rules** for
measuring overlap, correlation, redundancy, and independence between two FROZEN
admissible strategies — the `rho_ij` and redundancy signals consumed by the P2
metrics and P3 baselines.

It **computes no real overlap and no real correlation** (`compute_enabled =
false`, every method + the classification `computed_in_this_bundle = false`),
produces no real portfolio result, and reads no live strategy results.

## Methods defined (formula only; none computed)

1. **`trade_time_overlap_pct`** — Jaccard over in-position time.
2. **`simultaneous_capital_at_risk_overlap`** — `Σ min / Σ max` of car series.
3. **`same_symbol_overlap`** — same-canonical-symbol fraction of simultaneous
   in-position time.
4. **`same_direction_overlap`** — same-direction fraction; opposite →
   `hedging_offset` flag.
5. **`return_stream_correlation`** — Pearson `rho_ij` over aligned `T_common ≥
   N_min` (**consumed by P2 + P3**).
6. **`drawdown_period_overlap`** — Jaccard over drawdown windows.
7. **`redundancy_score`** — pre-declared-weighted blend; only `max(rho,0)` feeds
   it.
8. **`diversification_benefit_score`** — `1 − redundancy`.

**Independence classification:** `independent` / `partial_overlap` /
`redundant` / **`undefined`** (mandatory; insufficient data or UNDEFINED
redundancy/correlation never coerced to a definite class). Thresholds
(`tau_low`, `tau_high`, `rho_low`, `N_min`) are pre-declared operator constants,
never fit.

These consume **FROZEN per-trade / per-period series** (`in_position_flag_t`,
`capital_at_risk_t`, `symbol_t`, `direction_t`, `period_return_r_t`,
`drawdown_flag_t`) from a committed replay artifact — never live results.

## Candidate #10 — still deferred, NOT connected

`c10_boundary.connection_status = deferred_not_connected`,
`must_not_touch_c10 = true`. C10's per-trade / per-period series are exactly the
shape these measures consume, but C10 is **deferred**: eligible only once it has
its **own FROZEN, committed** replay artifact admitted under P1 — never the
working tree. C10's pre-existing `M` working-tree state was left exactly as
found; no C10 file/test/artifact/label/replay/detector was read, edited, or
staged.

## Files created

- `reports/portfolio_capital_efficiency_overlap_correlation_method_v1/overlap_correlation_method.json`
- `reports/portfolio_capital_efficiency_overlap_correlation_method_v1/overlap_correlation_method.md`
- `reports/portfolio_capital_efficiency_overlap_correlation_method_v1/report.json`
- `reports/portfolio_capital_efficiency_overlap_correlation_method_v1/report.md`
- `tools/portfolio_capital_efficiency_overlap_correlation_method_check.py` (stdlib-only validator)
- `tests/test_portfolio_capital_efficiency_overlap_correlation_method.py` (28 tests)

Plus append-only memory entries in `decisions.md`, `next_actions.md`, and
`logs/system_changes.md`.

## Verification

```
.venv/Scripts/python.exe tools/portfolio_capital_efficiency_overlap_correlation_method_check.py validate
  -> validate: OK

.venv/Scripts/python.exe -m pytest \
  tests/test_portfolio_capital_efficiency_overlap_correlation_method.py \
  tests/test_portfolio_capital_efficiency_allocation_baseline_spec.py \
  tests/test_portfolio_capital_efficiency_metric_spec.py \
  tests/test_portfolio_capital_efficiency_input_contract.py \
  tests/test_portfolio_capital_efficiency_protocol.py --rootdir=tests -q
  -> 131 passed in 1.08s   (28 P4 + 28 P3 + 26 P2 + 24 P1 + 25 P0)
```

## Recommended next bundle (operator picks; separately authorized, spec-only)

1. **Advisory Memo Schema v1** (P5) — finalises the advisory report schema
   hosting these overlap/correlation measures + the independence classification.
2. A possible **P1 amendment** that formally admits the FROZEN per-trade /
   per-period series these measures require.
3. A separate, separately-authorized **compute bundle** that actually runs these
   measures over frozen admissible series.

## No-profit-claim

This method does not imply edge and does not allocate capital. A defined
overlap or correlation measure does not imply profit. A capital-efficiency
score does not imply future returns. No allocation is authorized by this method
alone.
