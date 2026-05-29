# NQ ORB — Opening Range Breakout (strategy spec)

First and only strategy target for the Agentic Backtest Factory.
No other strategy (Donchian, carry, bad-regime predictor, EMA/SR, etc.) is in scope yet.

---

## Idea

Trade the breakout of the regular-session **opening range** on NQ (Nasdaq-100 futures).
The first N minutes of the session define a high/low box. A break of that box signals
directional momentum for the rest of the day.

## Definitions

- **Opening range (OR):** highest high and lowest low across the first
  `opening_range_minutes` of the session (default 15), starting at `session_start`
  (default 09:30).
- **OR high / OR low:** the box boundaries.

## Entry

- **Long:** first bar whose price breaks **above OR high** after the OR window closes.
- **Short:** first bar whose price breaks **below OR low** after the OR window closes.
- `one_trade_per_day = true`: take only the first valid breakout of the day.

## Stop

- `stop_mode = opposite_range`: stop placed at the **other** side of the opening range
  (long stop = OR low, short stop = OR high). Risk per trade `R = |entry - stop|`.

## Target

- `target_r_multiple` (default 2.0): exit at `entry + 2R` (long) or `entry - 2R` (short).

## Exit fallback

- If neither stop nor target is hit, **exit at `session_end`** (default 16:00) at the
  close of the last in-session bar.

## Parameters (searched by the proposer, offline + deterministic)

| Param                   | Default | Search set            |
|-------------------------|---------|-----------------------|
| `opening_range_minutes` | 15      | 5, 10, 15, 30         |
| `target_r_multiple`     | 2.0     | 1.5, 2.0, 3.0         |
| `stop_mode`             | opposite_range | (fixed for now) |
| `one_trade_per_day`     | true    | (fixed for now)       |

## Metrics evaluated

Profit factor, win rate, max drawdown %, expectancy (avg R), trade count, Sharpe-like ratio.

## Decision mapping

- **continue** — meets continue thresholds (PF, win rate, max DD) with enough trades → iterate params.
- **park** — profitable-ish but below continue bar → shelve for later.
- **kill** — below park bar → discard the variant.

Thresholds live in `config\factory_config.yaml` under `decision:`.

## Data

Offline intraday CSV from `data_offline\` only (see `data_offline\README_DATA.md`).
No fetching, no API, no network.
