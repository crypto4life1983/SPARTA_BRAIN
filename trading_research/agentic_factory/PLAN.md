# PLAN — SPARTA Agentic Backtest Factory (frozen design record)

Status: **Phase 1 built** (docs + skeleton). Engine/loop/tests NOT built.
Approved scope so far: isolated folder structure + 6 documentation/skeleton files only.

---

## Purpose

A local-safe version of a TraderDev-style backtest loop:

```
proposer  ->  backtester (offline CSV)  ->  metrics  ->  report (json + md)  ->  decision: continue / park / kill
```

First and only strategy target: **NQ ORB** (Opening Range Breakout). No other strategy
until NQ ORB is fully proven through the loop.

---

## Full proposed folder tree (target end-state)

```
trading_research\agentic_factory\
├── README.md                     # hard safety rules + scope         [Phase 1 - DONE]
├── PLAN.md                       # this frozen design record         [Phase 1 - DONE]
├── config\
│   └── factory_config.yaml       # offline paths, NQ ORB params, thresholds   [Phase 2]
├── data_offline\
│   ├── .gitkeep                  # placeholder                       [Phase 1 - DONE]
│   └── README_DATA.md            # data rules: offline CSV only       [Phase 1 - DONE]
├── strategies\
│   └── nq_orb\
│       └── nq_orb_spec.md        # NQ ORB definition                 [Phase 1 - DONE]
├── engine\
│   ├── proposer.py               # AI proposes/parameterizes variant  [Phase 2]
│   ├── backtester.py             # offline backtest runner (pandas)   [Phase 2]
│   ├── metrics.py                # PF, win%, max DD, expectancy, etc.  [Phase 2]
│   └── decision.py               # continue / park / kill gate         [Phase 2]
├── loop\
│   └── factory_loop.py           # orchestrates the full loop          [Phase 3]
├── reports\
│   └── .gitkeep                  # generated run reports land here     [Phase 1 - DONE]
└── tests\
    ├── test_metrics.py                                                 [Phase 3]
    ├── test_decision.py                                                [Phase 3]
    └── test_safety_guards.py     # asserts no forbidden imports        [Phase 3]
```

---

## Phase 1 files (this delivery)

1. `README.md`
2. `PLAN.md`
3. `data_offline\README_DATA.md`
4. `data_offline\.gitkeep`
5. `reports\.gitkeep`
6. `strategies\nq_orb\nq_orb_spec.md`

No engine, loop, proposer, backtester, metrics, decision, or test files created.

---

## Loop contract (to be implemented in later phases)

1. **proposer** — emits a deterministic NQ ORB parameter proposal (seeded; no network).
2. **backtester** — runs the proposal over a local CSV from `data_offline\`; returns a trade list.
3. **metrics** — computes profit factor, win rate, max drawdown, expectancy, trade count, Sharpe.
4. **report** — writes a json + md summary into `reports\`.
5. **decision** — applies thresholds → `continue` (iterate params), `park` (shelve), or `kill` (discard).

---

## Safety contract (mirrors README)

- Offline-only, research-only, local-only. No network, no broker, no exchange/Databento API.
- No secrets/credentials access.
- No writes outside `trading_research\agentic_factory\`.
- No modification of obsidian-trade-logger, live trading, scheduler, review_queue, broker,
  or existing strategy-bot files.
- No staging, no committing, unless explicitly authorized later.

---

## S23-D2 addendum — Data Quality Scanner (built)

`engine\data_quality.py` + `tests\test_data_quality.py` added. The scanner
inspects any local CSV *before* a backtest result is trusted and reports row
count, first/last timestamp, required columns, duplicate timestamps, invalid
OHLC rows, timezone awareness, distinct dates, estimated bar interval, RTH
session coverage (14:30-21:00 UTC), eligible RTH sessions, and thin/holiday
warnings. It then classifies the dataset on a readiness ladder:
plumbing_test / smoke_test / serious_research / profitability_conclusion, with
a single verdict (`UNUSABLE` / `NEEDS_MORE_DATA` /
`RESEARCH_OK_NOT_PROFITABILITY_GRADE` / `PROFITABILITY_GRADE`). Offline,
stdlib-only, no optimization, no trading. The current Christmas-week NQ CSV
scores **NEEDS_MORE_DATA** (4 eligible sessions, Dec 25 closed) — good for
plumbing/smoke only.

---

## Why this does not interfere with the existing trading bot

- Disjoint, brand-new folder; touches none of `paper_trading/`, `strategy_lab/`,
  `tradingview_bridge/`, or any live module.
- No imports into or out of live code; self-contained pandas-only engine (when built).
- Reads only manually-placed CSVs in its own `data_offline\`.
- Git-inert: appears only as untracked files; leaves all existing tracked/untracked work
  (including `templates/base.html`) untouched.
