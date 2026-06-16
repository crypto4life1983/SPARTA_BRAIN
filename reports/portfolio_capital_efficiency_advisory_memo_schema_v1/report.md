# Build Report — Portfolio Capital-Efficiency Advisory Memo Schema v1 (P5)

> **Research-only. Advisory-only. Advisory memo schema / framework only.** No
> real results computed, no real memo produced, no capital deployed, no broker,
> no live/paper trading, no orders, no data fetch, no detector, no replay, no
> backtest. **C10 deferred and untouched.**

**Layer:** `portfolio_capital_efficiency_advisory_memo_schema_v1` · **Phase:**
`P5_advisory_memo_schema` · **Build date:** 2026-06-16 · **Lane status:**
`WATCH` · **Companions:** P0 + P1 + P2 + P3 + P4.

## What this bundle is

The **P5 Advisory Memo Schema** — the finisher of the spec ladder. It pins the
**structure** of the future advisory memo (its required sections) and the
**allowed verdict language** (WATCH/undefined classifications only), so a later,
separately-authorized **compute bundle** has a fixed, safe home for its outputs.

It **computes no real results** and produces no real memo
(`compute_enabled = false`, `capital_deployment_enabled = false`,
`memo_produced_in_this_bundle = false`, every section
`produced_in_this_bundle = false`).

## 10 required memo sections (defined; none produced)

1. `admissible_frozen_inputs_summary`
2. `inadmissible_deferred_inputs_summary`
3. `per_strategy_standalone_summary`
4. `overlap_correlation_summary`
5. `allocation_baseline_comparison`
6. `capital_efficiency_ranking`
7. `basket_usefulness_classification`
8. `risk_warnings_and_limitations`
9. `operator_decision_checklist`
10. `no_action_recommendation` (missing/UNDEFINED inputs → NO ACTION)

## Allowed verdict language (exhaustive — only labels permitted)

`watch_only_useful_candidate` · `watch_only_basket_candidate` ·
`watch_only_redundant_candidate` · `watch_only_inadmissible` ·
`undefined_insufficient_data`.

## Forbidden verdict language (enumerated, never asserted)

`PASS` · `ACTIVE` · `STRONG` · `approved for paper trading` · `approved for
live trading` · `profit guarantee` · `capital deployment instruction` ·
`broker/order/credential logic`. The validator enforces that the allowed
classifications are **exactly** the five above and that the forbidden tokens are
all enumerated; the capability-claim scan is kept separate so the schema can
legitimately *name* the forbidden tokens without tripping it.

## Candidate #10 — still deferred, NOT connected

`c10_boundary.connection_status = deferred_not_connected`,
`must_not_touch_c10 = true`. In any future memo, C10 is reported under the
inadmissible/deferred-inputs summary (`watch_only_inadmissible`) until it has
its **own FROZEN, committed** replay artifact admitted under P1 — never the
working tree. C10's pre-existing `M` working-tree state was left exactly as
found; no C10 file/test/artifact/label/replay/detector was read, edited, or
staged.

## Files created

- `reports/portfolio_capital_efficiency_advisory_memo_schema_v1/advisory_memo_schema.json`
- `reports/portfolio_capital_efficiency_advisory_memo_schema_v1/advisory_memo_schema.md`
- `reports/portfolio_capital_efficiency_advisory_memo_schema_v1/report.json`
- `reports/portfolio_capital_efficiency_advisory_memo_schema_v1/report.md`
- `tools/portfolio_capital_efficiency_advisory_memo_schema_check.py` (stdlib-only validator)
- `tests/test_portfolio_capital_efficiency_advisory_memo_schema.py` (29 tests)

Plus append-only memory entries in `decisions.md`, `next_actions.md`, and
`logs/system_changes.md`.

## Verification

```
.venv/Scripts/python.exe tools/portfolio_capital_efficiency_advisory_memo_schema_check.py validate
  -> validate: OK

.venv/Scripts/python.exe -m pytest \
  tests/test_portfolio_capital_efficiency_advisory_memo_schema.py \
  tests/test_portfolio_capital_efficiency_overlap_correlation_method.py \
  tests/test_portfolio_capital_efficiency_allocation_baseline_spec.py \
  tests/test_portfolio_capital_efficiency_metric_spec.py \
  tests/test_portfolio_capital_efficiency_input_contract.py \
  tests/test_portfolio_capital_efficiency_protocol.py --rootdir=tests -q
  -> 160 passed in 1.45s   (29 P5 + 28 P4 + 28 P3 + 26 P2 + 24 P1 + 25 P0)
```

## Spec ladder status

**P0 → P1 → P2 → P3 → P4 → P5 spec ladder is COMPLETE.** The only remaining
step is a separately-authorized **compute bundle** (plus an optional P1
amendment that admits the FROZEN per-trade / per-period series the P4 measures
require).

## No-profit-claim

This schema does not imply edge and does not allocate or deploy capital. A
defined memo section does not imply profit. A capital-efficiency score does not
imply future returns. No allocation is authorized by this schema alone.
