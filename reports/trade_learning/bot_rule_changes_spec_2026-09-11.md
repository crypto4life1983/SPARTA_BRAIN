# Paper-bot rule changes — implementation spec (obsidian-trade-logger)

Status: **APPLIED 2026-09-11** in obsidian-trade-logger commit `c9a8f7b` (operator "ok do it all").
Tests: 12 new in `tests/test_rule_changes_2026_09.py`; suite 2867 passed, 1 pre-existing unrelated
failure. Ledger: the four matching hypotheses are marked APPLIED and tracked post-apply.
(History: first authorized 2026-09-10, blocked by the permission classifier that day.) The bot is paper-only (every trade is logged
"PAPER TRADE OPENED/CLOSED"); none of this adds broker or order code.

Evidence behind each change: `trading_learning_review_2026-09-09.md` §2 and the addendum.
Tests: repo has `tests/` (149 tests); add `tests/test_rule_changes_2026_09.py`; run
`python -m pytest tests -q -p no:cacheprovider` before and after.

## 1. Bar-aware, gap-honest stop and target checks

Files: `scripts/trade_bot.py` — `manage_de` (~L426), `manage_f` (~L454), the exit-check
block in `run_strategy` (~L750–768), and the catch-up replay `_replay_missed_bars` /
`_missed_bars` (~L640–672).

- Add optional kwargs `bar_open=None, bar_high=None, bar_low=None` to `manage_de` and
  `manage_f`. When all three are None, behaviour is unchanged (close-only), so existing
  callers and tests keep passing.
- When provided, for LONG: `sl_hit = bar_low <= sl`; fill = `bar_open` if `bar_open <= sl`
  (gap through the stop) else `sl`. Target: `tp_hit = bar_high >= tp1`; fill = `bar_open`
  if `bar_open >= tp1` else `tp1`. Mirror for SHORT with high/low swapped.
- If stop and target are both touched in the same bar, take the STOP.
- The `close_price` in the returned event and passed to `close_trade` / `calc_pnl` must be
  the fill price actually used.
- In `run_strategy`, read `last = df.iloc[-1]` and pass `bar_open=float(last["open"])`,
  `bar_high=float(last["high"])`, `bar_low=float(last["low"])`.
- Extend `_missed_bars(df, last_run_date, today)` to yield `(date, open, high, low, close)`
  when those columns exist and pass them through in the replay loop; fall back to close-only
  when they do not.
- Log `STOP-FILL {exchange} Exp {strategy} {sym} level={sl} fill={price} gap={bool}` on every
  stop fill. Keep the existing `EXIT-CHECK` line format unchanged (analytics parse it).

Why: trade 46 closed −4.63R because the 08-20 close was 0.04% short of the stop and the
next session moved 17.6%. Close-only checks have unbounded loss per trade.

## 2. Regime control fail-closed; strict-variant shorts allowed in TREND_DOWN

File: `scripts/regime_control.py` — `is_signal_allowed`, `regime_control_summary`.

- Final fallback (UNKNOWN / NO_DATA / unrecognised) returns
  `(False, f"regime={regime} unknown — blocked (fail-closed)")` instead of allowing.
- TREND_DOWN: allow shorts for strategies in `{"D","E","F","D2","E2","F2"}`; keep longs
  blocked; keep `G` blocked.
- Update the TREND_DOWN verdict text in `regime_control_summary` to
  `"shorts only (D/E/F + D2/E2/F2)"`.
- `run_strategy` (~L835) already resolves `regime = regime_map.get(sym, "UNKNOWN")`; with
  fail-closed this blocks entries when the regime map is missing. That is intended. Make sure
  the block goes through the existing `log_block(...)` and is counted in the daily summary.

Why: counter-trend and unlabeled-regime trades lost −6.8R over 9 rows; strict D/E/F shorts
made +21.5R while D2, the only breakout allowed in TREND_DOWN today, lost −9.23R.

## 3. Partial take-profit at 2R + breakeven trail for D / E / D2 / E2

File: `scripts/trade_bot.py` — `manage_de`.

- Stop distance `d = abs(entry - sl_original)`; 2R level = `entry + 2d` (long) /
  `entry - 2d` (short). Detect with bar high/low when available, else close.
- When `tp1_hit == 0` and the 2R level is reached: book a 50% partial at exactly the 2R
  level using the same fee model as `manage_f._partial`, then
  `mark_tp_hit(conn, id, 1, realized_pnl=partial)` and `update_sl(conn, id, entry)`
  (breakeven on the remainder). Return `dict(event="TP1_HIT", partial_pnl=..., trade=trade)`
  so the caller's existing TP1_HIT branch handles logging and Telegram.
- After TP1: the remainder closes on stop (now breakeven), original `tp1` target, or
  timeout, with `total_pnl = realized_pnl + remainder` and `pnl_r = total_pnl / size_usd`,
  exactly as `manage_f` does for its 0.6 remainder (here 0.5).
- Sizing: `calc_pnl` and `_partial` size units from the ORIGINAL stop distance. After the
  breakeven `update_sl`, `trade["sl"]` is the breakeven level, so read the original
  distance before any update (manage_f documents this same trap: it uses `2*atr14`).
  For D/E the original distance is `2*atr14` too; for safety compute it from
  `trade["atr14"]` rather than from the mutated `sl`.
- Keep old behaviour when 2R is never reached.

Why: winners that reached ≥1R peaked at a mean 2.98R and realized 1.79R; 3R/5R targets
were hit twice in 41 trades.

## 4. D2 on WATCH (open only with a strict twin)

File: `scripts/trade_bot.py` — run loop in `main()` and `run_strategy`.

- Add `WATCH_STRATEGIES = {"D2"}` (module constant) and an optional CLI flag
  `--watch-strategies` defaulting to `D2`.
- Strict strategies (`D`, `E`, `F`) run before loose ones in the per-exchange loop; if not,
  reorder or collect strict signals first. Record allowed strict signals in a per-run dict
  `strict_signals[(exchange, symbol, direction)] = strategy` and pass it into
  `run_strategy(..., strict_signals=...)`.
- A WATCH strategy is exit-managed normally but opens a NEW paper trade only if
  `(exchange, symbol, direction)` has a strict twin in `strict_signals`; otherwise log
  `WATCH-SKIP {exchange} Exp D2 {sym} — no strict twin signal` and count it.
- Do not change `config/strategy_status.json` (the strategy killer owns it).

Why: the in-sample what-if kept D2 only where a strict twin fired: dedup +14.6R → +16.9R.
This is a watch rule, not a kill; the killer's 20/30-trade thresholds still apply.

## Tests to add (`tests/test_rule_changes_2026_09.py`)

1. Short stop with gap-through open fills at the open and logs STOP-FILL; long stop touched
   by the low fills at `sl`; stop and target in one bar → stop; None bar args → identical to
   the old close-only result.
2. UNKNOWN regime → blocked; TREND_DOWN allows `D` short, blocks `D` long and `G`.
3. `manage_de` books a 50% partial at 2R, moves `sl` to entry, later breakeven stop-out
   returns `total ≈ partial`; a trade that never reaches 2R is unchanged.
4. D2 skipped without a strict twin, allowed with one.

Use the in-memory sqlite fixture pattern from `tests/test_trade_bot.py`.

## Non-goals

No change to sizing, symbols, timeouts, Telegram, the strategy killer, the evidence gate,
or anything under `data/`. No live/broker code. Daily scheduled command stays:
`trade_bot.py --use-regime-control --min-expected-r 0.5 --kill-switch --enable-auto-killer`.
