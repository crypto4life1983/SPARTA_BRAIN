# Spec — more paper slots per strategy, so the learning loop gets evidence faster

Status: **SPEC ONLY, NOT APPLIED** (written 2026-10-20 after the operator: "we need the learning
machine to keep learning and making better strategies and decisions ... we are making losses too
many"). Changes the paper bot's position cap, which is bot code in `obsidian-trade-logger`; needs an
explicit operator go. No broker, no order path, no credentials, no live trading in any state.

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

## The problem this solves

The loop cannot learn faster than the paper book closes trades.

| | value |
|---|---|
| closes per week, post-fix (2026-09-15..10-20) | 2.4 |
| allowed signals per week in the pool (42-symbol replay, dedup) | ~19 |
| share of the pool the one-slot book takes | ~6% |
| weeks to reach n = 20 for one hypothesis at 2.4 closes/week | ~8 |
| strategy E trades since the journal began | 4 |

Every pre-registered test (rollback at n >= 20, SHADOW -> CONFIRMED at n >= 20, the bot-side shadow
pair's two floors) is waiting on that 2.4. `SLOT OCCUPIED` has been logged 132 times since 10-07:
the gate allows the signal and the book has no room. The 09-23 replay already showed 389 of 414
allowed D signals skipped at one slot.

Three slots per strategy triples the evidence rate at zero real cost: the book is paper, and the
2026-10-20 replay puts the pool's expectancy at +0.075R per dedup trade over 2.7 years, so the extra
trades are drawn from the same distribution the book already trades. This is not a profit claim;
the pool also lost -0.12R/trade for six months in 2025. It is an evidence-rate claim.

## Smallest safe change (bot repo)

1. `config/live_config.json`: new key `paper_slots_per_strategy`, default **1** when absent (no
   behaviour change until the operator sets it).
2. `scripts/db.py`: add `get_open_trades(conn, exchange, strategy) -> list[dict]` (all open rows,
   oldest first). `get_open_trade` stays for callers that still want one.
3. `scripts/trade_bot.py::run_strategy` (the only place that opens positions, lines ~1091 and ~934):
   - exit management runs for **every** open position of the (exchange, strategy), each with its own
     symbol's bars, exactly as today for one;
   - the new-entry scan runs when `len(open) < K`, skipping symbols already held by this
     (exchange, strategy), and may open at most `K - len(open)` positions in one run, in config
     symbol order (today's rule);
   - `SLOT OCCUPIED` bookkeeping fires only when the book is full, excluding every held symbol.
4. Kill switch, regime gate, expected-R gate, allocation sizing, `catch_up_exits`, `last_bar_dates`,
   the watch gate and the coordinator are untouched. Per-trade risk is unchanged, so the paper book
   can carry up to K x strategies x exchanges positions at risk_pct each (K=3: up to 24 x 0.5% =
   12% of the paper account). State that number in the change note.

## Tests (added with the change)

- K absent / K=1: `run_strategy` behaviour byte-identical to today on the existing test fixtures
  (every current test keeps passing unchanged).
- K=3: three signals on three symbols in one run open three positions; a fourth is logged
  `SLOT OCCUPIED`; a symbol already held is never re-opened by the same strategy; each position
  exits on its own stop/target/timeout and frees one slot; the kill switch blocks all new entries.

## What it changes for the loop

- Rollback checks on the five applied rules reach n = 20 in ~3 weeks instead of ~8.
- `unblock__SLOT_OCCUPIED` (SHADOW, n = 4) is exactly the hypothesis this tests; its frozen
  in-sample evidence was neutral (net -1.4R over 20 resolved blocks). After the change the ledger
  should **retire** it as superseded by the config change, not score it further.
- The bot-side shadow pair's floors (20 closed baseline trades, 10 divergence episodes) arrive in
  weeks, not months.
- Three positions in D, F and F2 on the same entry remain a natural paired exit experiment; this
  spec does not collapse them. Collapsing them is a separate risk decision for a real book.

## What it does NOT do

- Does not change any signal, gate, exit, stop, partial or timeout.
- Does not make the paper book profitable. Expected per-trade result is the pool's, about +0.07R
  with half-year swings of a tenth of an R either way.
- Does not touch live trading, broker code, credentials or production uploads.

## Decision needed

One word from the operator: go / no. On go, the change is built in the bot repo with its tests;
commits and test runs there are permission-blocked in SPARTA sessions, so the operator runs one
consolidated `!` block (add with explicit pathspecs, test, commit, push) as on 2026-10-14.
