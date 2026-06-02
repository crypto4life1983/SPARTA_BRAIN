# Build Report — Crypto-D1 Manual Dataset Intake Runbook v1 (Bundle 20)

> **Research-only. Documentation bundle.** This bundle authorizes nothing
> operational. It does not fetch data, does not create
> `data/crypto_d1_research/`, does not run QA against real data, and does not
> run a backtest.

**Layer:** `crypto_d1_manual_dataset_intake_runbook_v1` · **Bundle:** 20 ·
**Branch:** `bundle20/crypto-d1-manual-intake-runbook`

## What was built

- `reports/crypto_d1_manual_dataset_intake_runbook_v1/runbook.json` — the
  machine-readable operator runbook.
- `reports/crypto_d1_manual_dataset_intake_runbook_v1/runbook.md` — the
  human-readable runbook (sections 0–13).
- `tools/crypto_d1_manual_dataset_intake_runbook_check.py` — stdlib-only
  validator (`validate` / `show`).
- `tests/test_crypto_d1_manual_dataset_intake_runbook.py` — pytest suite.
- `reports/crypto_d1_manual_dataset_intake_runbook_v1/report.md` + `report.json`
  — this build report.

## Where it sits in the pipeline

```
B17 acquisition authorization (the gate)
   -> [Bundle 20: Manual Dataset Intake Runbook]  (operator manual phase)
   -> B19 QA runtime tool (validate the on-disk dataset)
   -> (future, separately authorized) Baseline Results Report
```

The runbook is the human-procedure layer bridging the Bundle 17 gate to the
Bundle 19 QA tool. It adds **no automation** to that bridge.

## Files edited (minimal)

- `tools/strategy_candidate_registry.py` — added `runbook.md` + `runbook.json`
  to the `crypto_d1_protocol` lane `extra_files`; `lane_status_override` stays
  **WATCH**.
- `brain_memory/projects/trading_bot/decisions.md` — one append.
- `brain_memory/projects/trading_bot/next_actions.md` — one append.

## Files NOT changed

`tools/crypto_d1_data_qa_runtime_tool.py`, `tools/crypto_d1_backtest_runner.py`,
`tools/strategy_next_bundle.py`, `app.py`, `templates/*.html`, `paper_trading/*`,
`local_secrets/*`, `brain_memory/.../lessons.md`. No prior Crypto-D1 spec docs or
arbitrage validators modified. `data/crypto_d1_research/` NOT created.

## What it authorizes

Nothing operational. It is documentation plus a validator that checks the
document's own internal consistency. It does not fetch data, does not create a
data directory, does not run QA against real data, does not run a backtest, and
does not authorize broker/live/paper trading. **QA_PASS does not authorize
automatic backtesting. QA_PASS does not authorize paper trading. QA_PASS does
not authorize live trading.** Real data may enter only through explicit
operator action and the Bundle 17 gates.

## Safety

- Validator is stdlib-only (`argparse`, `json`, `pathlib`); no network, broker,
  exchange, subprocess, `os.environ`/`getenv`, or `.env` access.
- Eleven safety flags pinned `false` in the runbook; `research_only` +
  `read_only` `true`.
- No real data files created; `data/crypto_d1_research/` not created; no QA run
  against real data; no backtest run.
- Candidate registry stays **WATCH** (never ACTIVE, never STRONG).

## Registry status

The `crypto_d1_protocol` seed `extra_files` were extended with the runbook doc
pair for traceability only. The lane stays **WATCH**; evidence does **not**
become STRONG; the candidate is **not** marked ACTIVE.

## No-profit-claim policy

A runbook is not strategy validation. Manual intake does not imply edge.
QA_PASS does not imply profitability. Clean daily OHLCV data does not imply
profit. A runbook cannot authorize backtesting, paper, or live trading by
itself. No data fetch is authorized by this runbook.
A good historical chart does not imply future returns.
