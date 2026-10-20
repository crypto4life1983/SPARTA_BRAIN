# Portfolio-level rules on the 2026-10-20 replay series

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

**Question.** Both 2026-10-20 backtests found that the paper bot's losses arrive in clusters because its
signals fire in the same market state across many symbols. Can a rule that looks at the whole book,
rather than at one trade, do anything about that? Three families were fixed before the run and nothing
was searched: a cap on simultaneous same-direction positions, a cap on total positions (reference),
and an equity-curve filter on the rolling expectancy of recent closes.

**Short answer.** No. Every portfolio rule is worse than the baseline per trade or equal to it, and the
one that looks better per trade (a total cap) gets there by trading less in every phase, including the
good ones. The equity-curve filter is the clearest negative: it skips the winners after a bad stretch
and trades through the losers after a good one. Keyed to the book's own closes it locks the book shut
for good after the first bad stretch.

## Method

`tools/replay_portfolio_rules.py` reads `reports/trade_learning/replay_2026-10-20/signals.json` (the
per-signal replay of the bot's own code, see `replay_rules_variants_2026-10-20.md`) and builds the same
dedup trade series as that study: one trade per symbol+strategy at a time, 2,593 trades, 2024-11 ..
2026-10-19, fees included, 1R per trade. A chronological book model then applies each rule: a position
occupies its slot from the signal date to the exit date inclusive; signals on one date are processed
in (date, symbol) order, so an earlier signal can fill a cap for a later one.

- `same_dir_cap_N`: skip while N positions in the same direction are open (N = 3, 5, 10).
- `total_cap_N`: skip while N positions are open, any direction (N = 10, 20).
- `rolling_skip`: skip when the mean R of the last 30 closed pool signals (every allowed dedup signal,
  taken or not, closed strictly before the signal date) is below zero; inactive until 30 closes exist.
  The pool is what the paper bot can observe through its shadow and hindsight rows.
- `rolling_half`: same condition, take at half size instead of skipping (rolling mean on full-size R).
- `rolling_skip_book`: the same filter keyed to the book's own closes only; kept on the record because
  it degenerates (below).

Bootstrap p(mean>0): numpy `default_rng(7)`, 4,000 resamples, same seed per rule. Max drawdown is of
cumulative R in trade order and scales with how many positions a rule holds at once, so compare rules
on mean R and on the by-period split, not on drawdown. `tests/test_replay_portfolio_rules.py` (5 tests)
checks the book model on synthetic signals: cap enforcement by side, inclusive exit dates, the rolling
window excluding the signal day, half-size arithmetic, and the pool-vs-book refresh behaviour.

**Caveats.** Same as the parent replay: spot bars, a universe chosen on 2026-09-16, two and a half years
of history. The dedup series holds far more simultaneous positions than any real book would, so the caps
bite hard (cap 3 keeps 8% of trades); their taken sets are small and their p-values are near 0.5.

## 1. Headline (per taken trade)

| rule | n | sum R | mean R | win | p(mean>0) | OOS n | OOS sum R | OOS mean R |
|---|---|---|---|---|---|---|---|---|
| baseline | 2593 | +194.0 | +0.075 | 0.49 | 1.000 | 107 | -16.7 | -0.156 |
| same_dir_cap_3 | 207 | -0.8 | -0.004 | | 0.475 | 9 | +0.4 | +0.042 |
| same_dir_cap_5 | 321 | +6.9 | +0.021 | | 0.624 | 16 | -2.3 | -0.140 |
| same_dir_cap_10 | 570 | +17.0 | +0.030 | | 0.736 | 28 | -6.6 | -0.235 |
| total_cap_10 | 418 | +45.8 | +0.109 | | 0.972 | 20 | -0.2 | -0.008 |
| total_cap_20 | 782 | +91.0 | +0.116 | | 0.998 | 43 | -0.4 | -0.009 |
| rolling_skip (pool) | 1153 | -14.5 | -0.013 | | 0.323 | 30 | -28.1 | -0.938 |
| rolling_half (pool) | 2593 | +89.8 | +0.035 | | 0.982 | 107 | -22.4 | -0.210 |
| rolling_skip (book) | 205 | +108.7 | +0.530 | | 1.000 | 0 | — | — |

## 2. The equity-curve filter, by half-year

Taken = what the filter traded; skipped = what it refused, at full size. A filter that only refuses
winners in good phases is a regime bet, not an edge.

| period | baseline mean | rolling_skip taken n / mean | skipped n / sum R |
|---|---|---|---|
| 2024-11..2025-05 | +0.216 | 340 / +0.450 | 266 / -21.8 |
| 2025-05..2025-11 | -0.118 | 323 / **-0.239** | 507 / -20.7 |
| 2025-11..2026-05 | +0.103 | 254 / **-0.203** | 341 / **+112.7** |
| 2026-05..2026-09 | +0.255 | 206 / -0.052 | 249 / **+126.9** |
| 2026-09.. (post-fix) | -0.156 | 30 / **-0.938** | 77 / +11.4 |

It helped in the first half-year and hurt in every one since. The pattern is the lag: the window turns
negative after the losses have happened and turns positive after the recovery has happened, so the
filter is out of the market for the recovery and in it for the next drawdown. On the post-fix window it
took the 30 worst trades and refused the 77 that, together, made money. Half-sizing instead of skipping
(`rolling_half`) halves the damage and halves the gains: +0.035 per trade against +0.075.

Keyed to the book's own closes, the filter trades 205 times in the first half-year, skips once the
window turns negative in mid-2025, and never trades again: the book stops closing trades, so the window
never refreshes. Its +0.53 mean is the first half-year's bull phase alone. This is not a usable rule;
it is a property of any skip-filter fed only by what it lets through.

## 3. The caps, by half-year

| period | baseline mean | same_dir_cap_5 taken n / mean | total_cap_20 taken n / mean | total_cap_20 skipped n / mean |
|---|---|---|---|---|
| 2024-11..2025-05 | +0.216 | 69 / +0.126 | 183 / +0.290 | 423 / +0.185 |
| 2025-05..2025-11 | -0.118 | 85 / +0.180 | 225 / +0.051 | 605 / -0.181 |
| 2025-11..2026-05 | +0.103 | 70 / -0.066 | 156 / +0.183 | 439 / +0.074 |
| 2026-05..2026-09 | +0.255 | 81 / -0.126 | 175 / -0.010 | 280 / +0.421 |
| 2026-09.. (post-fix) | -0.156 | 16 / -0.140 | 43 / -0.009 | 64 / -0.255 |

The same-direction caps keep the first few signals of each cluster and those are no better than the
rest: mean R near zero, p near 0.5, worse than the baseline in three of five half-years. Clusters are
not led by their best trades.

The total caps look better per trade (+0.109 and +0.116 against +0.075) but the split shows how: they
trade a fraction of the pool in every phase, which costs nothing in the bad phases (2025-05: skipped
-0.181 per trade) and costs everything in the good ones (2026-05: taken -0.010, skipped +0.421). Total R
falls from +194 to +91. Mean per trade rises because the cap happens to be binding more often when the
pool is hot, and a hot pool is when the dedup series opens the most positions. That is an artefact of
the unlimited-position series, not a selection edge. On the post-fix window the cap gets to about zero
by taking 43 of 107 trades; it did not pick better ones (taken -0.009, skipped -0.255 is the same
"trade less" effect in a losing phase).

## 4. What this supports, and what it does not

- **Supported:** no portfolio-level rule tested here improves the per-trade result of the bot's own
  signals on this history. The cluster losses are not fixable by capping the cluster or by stepping
  aside after losses.
- **Supported:** an equity-curve filter on recent closes is harmful on this series. It lags the regime
  by one phase, and fed by the book's own closes it locks the book shut. Do not register it.
- **Not supported:** reading a total-position cap's higher mean R as an edge. It is "trade less", which
  lowers both the losses and the gains and happens to be binding most in good phases of this series.
- **Not tested:** position sizing by realised volatility, correlation-weighted sizing across symbols, or
  anything that needs intraday data. Those are different questions.

Nothing in the bot was changed. Nothing was registered. Outputs: `replay_2026-10-20/portfolio_rules.json`.
