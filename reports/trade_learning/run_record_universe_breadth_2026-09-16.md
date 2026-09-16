# Run record — paper-bot universe breadth expansion

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

Pre-registration: `reports/trade_learning/prereg_universe_breadth_2026-09-16.md`
Operator approval: 2026-09-16 ("ok do it"), after reading the pre-registration.
Change applied: `C:\Users\mahmo\obsidian-trade-logger\config\live_config.json` → `symbols` only.

## 1. Feed verification (performed before the change)

Every one of the 32 added names was fetched through the bot's own
`scripts/binance_feed.fetch(symbol, limit=250)` — the exact path the live run uses.

| check | result |
|---|---|
| Binance, 32 new names, ≥ 200 daily bars each | 32 / 32 OK, 0 failures |
| **Recency** (last completed bar ≥ 2026-09-10) | **2 failures — EOSUSDT, MKRUSDT** |
| Binance, final 42 names, recency re-checked | **42 / 42 current, 0 stale** |
| Kraken | map covers only the original 12; new names are **Binance-only** |

**A gap in my own verification, found by the bot and recorded.** The first pass only checked
that each symbol returned ≥ 200 bars. It did not check that the bars were *recent*. Two pairs
passed that check while being long delisted from Binance spot: EOSUSDT (last completed bar
2025-05-26) and MKRUSDT (2025-09-15). The bot's own `[STALE FEED]` guard caught both during the
dry run and skipped them, which is the guard working exactly as intended. Both were then
removed from the config, and every remaining symbol was re-verified for recency.

**Kraken was deliberately not extended.** `scripts/kraken_feed.SYMBOL_MAP` translates each
symbol to a Kraken pair, and adding 32 entries would mean guessing pair names. A wrong guess
trades the wrong instrument silently, so the map is left untouched. Unmapped symbols return
`None` and the bot skips them cleanly, which is existing, tested behaviour.

Consequence, recorded honestly: the added names compete for **Binance slots only** (7 strategy
slots), not the full 13. The expected speedup is therefore smaller than raw breadth suggests —
see §5 of the pre-registration, which anticipated exactly this.

## 2. Final symbol list (frozen at approval)

Before: 12 configured (11 scanning; POLUSDT configured and Kraken-mapped).
After: **42 configured** = 12 unchanged + 30 added (32 verified, 2 removed as delisted).

Unchanged 12 (both exchanges, Kraken-mapped):
```
BTCUSDT ETHUSDT XRPUSDT SOLUSDT ADAUSDT BNBUSDT AVAXUSDT LINKUSDT DOTUSDT POLUSDT ARBUSDT OPUSDT
```

Added 30 (Binance only):
```
AAVEUSDT  ALGOUSDT  ATOMUSDT  BCHUSDT   CHZUSDT   COMPUSDT  CRVUSDT   DOGEUSDT
EGLDUSDT  ENJUSDT   ETCUSDT   FILUSDT   GRTUSDT   HBARUSDT  KAVAUSDT  LTCUSDT
MANAUSDT  NEARUSDT  RUNEUSDT  SANDUSDT  SNXUSDT   THETAUSDT TRXUSDT   UNIUSDT
VETUSDT   XLMUSDT   XTZUSDT   YFIUSDT   ZECUSDT   ZILUSDT
```

Excluded, all on data rules and none on performance:

| symbol | reason |
|---|---|
| ICPUSDT | short history, flagged in the frozen `quality_report.json` |
| EOSUSDT | delisted from Binance spot; last completed bar 2025-05-26 |
| MKRUSDT | delisted from Binance spot; last completed bar 2025-09-15 |

## 3. What changed, exactly

One key in one file: `config/live_config.json` → `symbols`.

A backup of the pre-change file is at `config/live_config.json.pre_breadth_20260916.bak`, so
the change reverses by restoring one file.

`config/live_config.json` is **gitignored** in the trade-logger repo (it carries
`telegram_token` / `telegram_chat_id`), so the change is not version-controlled there and was
not force-added. **This run record and the pre-registration are the audit trail**, and the
`.bak` file is the rollback.

Nothing else. Not the 7 strategies or any parameter, not the 2×ATR stops, the 20-day timeout,
`risk_pct`, `account_size`, regime control, the minimum expected-R filter, the kill switch, the
coordinator config, the four rules applied on 2026-09-11, or any ledger threshold.

Note carried forward: **Exp G remains XRPUSDT-only** by its own code
(`if symbol != "XRPUSDT": return None` in `detect_signal_g`). Breadth does not affect it.

## 4. Baseline, frozen now (pre-change)

| measure | value |
|---|---|
| symbols scanned | 11 (of 12 configured) |
| distinct entry days | 24 |
| span | 2026-04-28 → 2026-08-22 (116 days) |
| rate | **5.0 days per entry-day** |
| closed rows / distinct signals | 42 / 31 |
| journal expectancy (dedup mean) baseline at apply time | 0.251 R |
| applied-rule forward signals at change time | 0 |

## 5. Decision rule (unchanged from the pre-registration)

- **Works:** ≤ 2.5 days per entry-day over the first 30 days, and the ledger reaches n ≥ 20.
- **Does not work:** > 4 days per entry-day after 30 days → breadth was not the constraint, the
  slot cap was; the next question is the slot model, not more symbols.
- **Invalidated:** any rule, parameter or gate changed inside the window voids it and restarts.

First read: **2026-10-16**.

This measures how fast evidence accrues. It claims nothing about profitability, and the bar for
judging the applied rules is unchanged.

## 6. Safety

Paper only. Every trade the bot books is labelled PAPER. No broker, no orders, no credentials,
no live gate touched. Live trading remains BLOCKED at the 6 gates.
