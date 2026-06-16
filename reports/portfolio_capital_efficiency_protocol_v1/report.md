# Build Report — Portfolio Capital-Efficiency Protocol Memo v1

> **Research-only. Advisory-only. Specification only.** No data fetch, no
> metric computed, no allocation computed, no broker, no live capital, no
> orders. Candidate #10 untouched.

**Layer:** `portfolio_capital_efficiency_protocol_v1` · **Build date:**
2026-06-16 · **Lane status (self-declared):** `WATCH`

## What this bundle is

The **P0 protocol memo** that opens a new research lane: *Portfolio Capital
Efficiency*. It specifies — on paper only — how SPARTA will later study
capital efficiency **across its bench of already-researched strategy
candidates** (diversification, overlap/redundancy, concentration limits,
capital-at-risk budgeting). The full lane's eventual output is an **advisory**
allocation memo for human review; **no capital is ever allocated, sized, or
executed** by this lane.

This is a *downstream* lane: it reads only what the per-strategy research
lanes have **frozen and committed**. It is not a new edge.

## Files created

- `reports/portfolio_capital_efficiency_protocol_v1/protocol.json`
- `reports/portfolio_capital_efficiency_protocol_v1/protocol.md`
- `reports/portfolio_capital_efficiency_protocol_v1/report.json`
- `reports/portfolio_capital_efficiency_protocol_v1/report.md`
- `tools/portfolio_capital_efficiency_protocol_check.py` (stdlib-only validator)
- `tests/test_portfolio_capital_efficiency_protocol.py` (25 tests)

Plus append-only memory entries in `decisions.md`, `lessons.md`,
`next_actions.md`, and `logs/system_changes.md`.

## Safety posture

- **Eight flags pinned False**: `data_fetch_enabled`,
  `exchange_connection_enabled`, `live_trading_enabled`,
  `broker_control_enabled`, `paper_order_execution_enabled`,
  `live_capital_allocation_enabled`, `position_sizing_execution_enabled`,
  `backtest_enabled`.
- **Advisory-only** + **frozen-committed inputs only**. Live positions, live
  balances, and any uncommitted working tree are **inadmissible**.
- **Candidate #10 boundary pinned**: the lane must not read-for-mutation,
  edit, stage, or depend on in-flight C10 files/tests/labels/replay/detector
  or working-tree state. Pre-existing C10 working-tree modifications were left
  exactly as found.
- **Verdict ceiling inherited**: never surfaces PASS / ACTIVE / STRONG; the
  lane itself is self-declared WATCH.
- **Discretionary human allocation is WATCH-only** — the lane informs, it does
  not decide.

## Registry integration — deferred

This bundle intentionally did **not** modify
`tools/strategy_candidate_registry.py` or any shared registry logic, to honor
the additive-only / surgical-change scope. The lane self-declares WATCH inside
its own `protocol.json`. Wiring a candidate seed into the shared registry is a
separate, separately-authorized step.

## Verification

```
.venv/Scripts/python.exe tools/portfolio_capital_efficiency_protocol_check.py validate
  -> validate: OK

.venv/Scripts/python.exe -m pytest tests/test_portfolio_capital_efficiency_protocol.py --rootdir=tests -q
  -> 25 passed in 0.23s
```

## Recommended next bundle (operator picks; separately authorized)

1. **Input Contract v1** (P1) — admissible frozen artifacts + freeze rules. Spec only.
2. **Metric Spec v1** (P2) — exact formulas + inputs per metric. Spec only.
3. **Allocation Baseline Spec v1** (P3) — reference models + concentration cap. Spec only.

## No-profit-claim

This protocol does not imply edge and does not allocate capital. A
capital-efficiency score does not imply future returns. An advisory allocation
memo is a human-review aid, never an execution instruction. No allocation is
authorized by this protocol alone.
