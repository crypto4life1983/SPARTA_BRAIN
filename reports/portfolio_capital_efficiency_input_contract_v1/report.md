# Build Report — Portfolio Capital-Efficiency Input Contract v1 (P1)

> **Research-only. Advisory-only. Framework / specification only.** No input
> read, no metric computed, no allocation computed, no broker, no live capital,
> no orders. **No indicator results connected. Candidate #10 deferred and
> untouched.**

**Layer:** `portfolio_capital_efficiency_input_contract_v1` · **Phase:**
`P1_input_contract` · **Build date:** 2026-06-16 · **Lane status:** `WATCH` ·
**Companion (P0):** `reports/portfolio_capital_efficiency_protocol_v1/`

## What this bundle is

The **P1 Input Contract** for the Portfolio Capital-Efficiency lane. It
defines — framework-only — *which FROZEN, committed artifacts* the lane may
later read (the two registries' outputs + frozen per-strategy backtest
reports), the **required fields** each must expose, and the **admissibility /
freeze rules** (committed, checksummed, version-pinned, WATCH-ceiling
inherited, reproducible).

It **reads nothing**, **computes nothing**, and **connects to no indicator
results** in its runtime.

## Candidate #10 — deferred, NOT connected

Per the operator instruction, this contract keeps the lane **portfolio-framework
only** and does **not** connect it to C10 indicator results:

- `c10_boundary.connection_status = deferred_not_connected`,
  `must_not_touch_c10 = true`.
- C10 frozen replay outputs are listed under `deferred_inputs`, **blocked
  until** C10 finishes and freezes by itself first.
- Only once C10 has a FROZEN, committed replay output does it become an
  ordinary read-only bench input — then usable to evaluate **overlap,
  correlation, and capital efficiency** — and only in its frozen committed
  form, never the working tree.

C10's pre-existing `M` working-tree state was left exactly as found; no C10
file/test/label/replay/detector was read-for-mutation, edited, or staged.

## Files created

- `reports/portfolio_capital_efficiency_input_contract_v1/input_contract.json`
- `reports/portfolio_capital_efficiency_input_contract_v1/input_contract.md`
- `reports/portfolio_capital_efficiency_input_contract_v1/report.json`
- `reports/portfolio_capital_efficiency_input_contract_v1/report.md`
- `tools/portfolio_capital_efficiency_input_contract_check.py` (stdlib-only validator)
- `tests/test_portfolio_capital_efficiency_input_contract.py` (24 tests)

Plus append-only memory entries in `decisions.md`, `next_actions.md`, and
`logs/system_changes.md`.

## Safety posture

- **Eight flags pinned False** (data_fetch / exchange_connection /
  live_trading / broker_control / paper_order_execution /
  live_capital_allocation / position_sizing_execution / backtest).
- **Advisory-only + framework-only + frozen-committed inputs only.**
- All admissible input classes are **read-only + frozen_required**.
- **Verdict ceiling**: `max_surfaced_verdict = WATCH`; PASS/ACTIVE/STRONG
  forbidden.
- Live positions / balances and any uncommitted working tree are
  **inadmissible**.
- Shared `strategy_candidate_registry.py` intentionally **not** modified
  (additive-only).

## Verification

```
.venv/Scripts/python.exe tools/portfolio_capital_efficiency_input_contract_check.py validate
  -> validate: OK

.venv/Scripts/python.exe -m pytest \
  tests/test_portfolio_capital_efficiency_input_contract.py \
  tests/test_portfolio_capital_efficiency_protocol.py --rootdir=tests -q
  -> 49 passed in 0.51s   (24 P1 + 25 P0)
```

## Recommended next bundle (operator picks; separately authorized, spec-only)

1. **Metric Spec v1** (P2) — exact formulas + inputs per metric.
2. **Allocation Baseline Spec v1** (P3) — reference models + concentration cap.
3. **Overlap/Correlation Method v1** (P4) — redundancy estimation method.

## No-profit-claim

This contract does not imply edge and does not allocate capital. Clean, frozen
inputs do not imply profit. A capital-efficiency score does not imply future
returns. No allocation is authorized by this contract alone.
