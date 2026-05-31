# SPARTA Strategy Factory — Routine Layer v1

A tiny, deterministic, **research-only** automation layer that reads existing
SPARTA research outputs and produces clean, JARVIS-readable status files. It
exists to cut copy-paste work — not to trade.

Tool: [`tools/strategy_factory_routines.py`](../../tools/strategy_factory_routines.py)
(Python standard library only).

## What it is

Four repeatable local routines plus a CLI runner. Each routine reads the
existing agentic validation-factory reports
(`trading_research/agentic_factory/reports/*/report.json`), summarizes the
current state, decides which research lane is next, and writes a JSON + Markdown
report a human or JARVIS/Commander can read at a glance.

| Routine | Command | Output folder | Files |
| --- | --- | --- | --- |
| Daily State | `daily-state` | `reports/strategy_factory_routines/daily_state/` | `latest_state.json` / `.md` |
| Strategy Queue | `strategy-queue` | `reports/strategy_factory_routines/strategy_queue/` | `queue.json` / `.md` |
| Weekly Review | `weekly-review` | `reports/strategy_factory_routines/weekly_review/` | `latest_weekly_review.json` / `.md` |
| JARVIS Snapshot | `jarvis-snapshot` | `storage/jarvis/strategy_factory/` | `latest_strategy_factory_snapshot.json` / `.md` |

## What it does

- **Daily State** — current research posture (GREEN / YELLOW / RED), active
  lanes, recently completed reports, blockers, what should run next, and a
  safety status block.
- **Strategy Queue** — a prioritized, research-only backlog of next lanes
  (crypto D1/4H, NQ/ES futures trend, Donchian variants, vol-confirmed
  continuation, arbitrage protocol, data QA/freeze, JARVIS checkpoints). Each
  item carries lane, priority, reason, required inputs, expected output, safety
  level, blocked flag, and a suggested next Claude/Codex bundle. Priorities and
  the hygiene-first gate are tuned from the latest roadmap memo.
- **Weekly Review** — what was tested/built, what passed/failed, what remains
  uncertain, whether we are closer to a real edge, which lanes are wasting
  time, which lane deserves the next deep bundle, and three deterministic
  scores: safety, automation readiness, research quality.
- **JARVIS Snapshot** — a compact, read-only snapshot for the dashboard /
  Commander with posture, active lane, next best action, blockers, last
  reports, the three pinned-False safety flags, and a commander color.

## What it does NOT do

- No live trading. No paper-order execution. No order placement.
- No broker control. No exchange / Alpaca API. No autonomous trade decision.
- No API keys, no `.env`, no credential handling.
- No network calls. No scheduler install. No background daemon.
- No modification of protected / live-trading / frozen-data files.
- It only **reads** research reports and **writes** its own status files inside
  `reports/strategy_factory_routines/` and `storage/jarvis/strategy_factory/`.

## How to run

```bash
cd C:\SPARTA_BRAIN
.venv\Scripts\python tools\strategy_factory_routines.py daily-state
.venv\Scripts\python tools\strategy_factory_routines.py strategy-queue
.venv\Scripts\python tools\strategy_factory_routines.py weekly-review
.venv\Scripts\python tools\strategy_factory_routines.py jarvis-snapshot
.venv\Scripts\python tools\strategy_factory_routines.py all
```

Optional `--repo-root PATH` runs the routines against a different checkout
(used by the tests to target a temp tree). If input folders are missing the
routines degrade gracefully and list what was missing under `missing_inputs`
instead of crashing.

## Safety guarantees

- Standard-library only; the test suite asserts **no** network or broker
  modules are imported (`socket`, `urllib`, `requests`, `ccxt`, `alpaca`,
  `binance`, `subprocess`, `os`, `dotenv`, …).
- The three flags `live_trading_enabled`, `broker_control_enabled`, and
  `paper_order_execution_enabled` are pinned **False** as constants and
  asserted False in every routine's output.
- Outputs are confined to the two folders above (asserted by a test that fails
  if anything is written elsewhere).
- Deterministic: same inputs → same structure; no randomness, no clocks beyond
  the `generated_at` / weekly window stamp.

## How JARVIS / Commander reads the snapshot

Read `storage/jarvis/strategy_factory/latest_strategy_factory_snapshot.json`.
It mirrors the existing JARVIS read-only snapshot conventions
(`read_only: true`, pinned-False trading flags) and adds a `commander_color`
(GREEN / YELLOW / RED) plus `next_best_action` so the panel can show factory
status without re-deriving it.

## How this reduces copy-paste work

Instead of hand-scanning dozens of `report.json` files to answer "where are we,
what's blocked, what runs next, how is the pipeline doing?", run one command
and read one short Markdown file (or let JARVIS read the JSON). The queue turns
the latest roadmap memo into an actionable, prioritized list with ready-made
next-bundle suggestions.

## Tests

`tests/test_strategy_factory_routines.py` (run with `--rootdir=tests` to avoid
a pre-existing phantom-dir at the repo root):

```bash
.venv\Scripts\python -m pytest tests\test_strategy_factory_routines.py --rootdir=tests -q
```
