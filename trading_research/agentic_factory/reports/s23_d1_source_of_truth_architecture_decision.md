# S23-D1 — Source-of-Truth Architecture Decision

Date: 2026-05-29
Scope: SPARTA trading strategy research engine
Status: DECISION RECORDED (research-only, no live trading authorized)

---

## 1. Decision

`trading_research\agentic_factory` is the **official clean strategy research
engine** for all future SPARTA trading research.

New strategy research — proposing, backtesting, scoring, and deciding
(continue / park / kill) — happens here first. Other older strategy stacks are
treated as legacy reference until each is explicitly reviewed and either
migrated into this engine or retired.

## 2. Why This Engine Is the Source of Truth

- **Isolated.** Lives entirely inside `trading_research\agentic_factory\`.
  Writes never escape the folder. No shared mutable state with live systems.
- **Tested.** 20 passing unit tests cover metrics, decision thresholds,
  config wiring, and a safety guard that scans source for forbidden
  network/broker/secret tokens.
- **Config-wired.** Strategy params (session window, opening-range length,
  target R) flow from `config/factory_config.yaml` into the loop. The
  09:30/16:00 base-default leak was found and fixed; the rerun proved
  14:30/21:00 UTC is now honored.
- **Offline.** Backtester reads a local CSV only, using Python stdlib
  (`csv`, `datetime`). No fetch, no stream, no API, no pandas requirement.
- **Safe.** No broker, no exchange, no Databento client, no secrets, no
  scheduler, no order placement. The safety-guard test fails the build if any
  forbidden import or path string is introduced.

## 3. Commander Overlap — Treated as Legacy

`sparta_commander/` already contains an older overlapping strategy stack
(`strategy_factory_*`, `profit_brain`, `profit_candidate_factory`,
`nq_mnq_or_*`, `ai_strategy_reviewer`, `auto_research_lab`).

This overlap is **legacy until reviewed**. It is not deleted and not trusted as
the research source of truth. Each piece will be individually examined and
either folded into `agentic_factory` or explicitly parked. No new strategy
research should start in the Commander stack.

## 4. Future Role of Commander — Read-Only Dashboard

Commander's forward role is a **read-only dashboard / display layer**: it shows
evidence cards and run summaries produced by `agentic_factory`. It does not
propose, optimize, or execute strategies. Display only — the research and the
verdicts come from this engine.

## 5. Brain Memory — Human-Approved Lessons Only

`brain_memory/` stores **human-approved lessons and decisions**, not raw
machine output. A backtest result becomes a lesson only after a human reviews
it and chooses to record it. The engine produces evidence; the human decides
what is worth remembering.

## 6. obsidian-trade-logger — Isolated and Untouched

`C:\Users\mahmo\obsidian-trade-logger` is **isolated and untouched** by this
engine. It is not read, written, imported, or referenced by any research code
here. It remains the user's separate live trade journal.

## 7. No Live Trading Approved

**No live trading, order placement, broker connection, or capital deployment is
approved.** This engine is offline research only. The wall between research
output and any live system stays up. Crossing it requires a separate, explicit,
human-authorized decision — not implied by any backtest result.

## 8. Next Safe Sequence

1. Supply larger, continuous, non-holiday NQ 1-minute history (current data is
   Christmas-week only — 4 trades, below the 30-trade decision gate).
2. Rerun the NQ ORB pass on that data for a first non-trivial read (still
   research, still not profitability proof).
3. Review the Commander legacy stack piece by piece; migrate or park each.
4. Record any human-approved lesson into `brain_memory/`.
5. Only after repeated, reviewed, out-of-sample evidence — and a separate
   explicit human decision — consider anything beyond offline research.

---

*Research-only record. Nothing in this engine is staged, committed, or
connected to live capital.*
