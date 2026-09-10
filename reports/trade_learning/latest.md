# Trade Journal Learning Report — 2026-09-09

**READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER**

Sample label: **OK** (dedup closed signals 30 vs MIN_SIGNALS=30). Every conclusion below threshold is PRELIMINARY.

## Counts (closed trades)

- rows 42 · closed 41 · open 1 · distinct signals (closed) 30
- sum_R raw 15.466 · dedup best-row 8.881 · dedup mean-row 7.868
- win rate 0.463 · expectancy 0.377 R (dedup mean 0.262) · profit factor 1.620
- note: raw rows overstate the sample: the bot mirrors signals on binance and kraken and the loose '2' variants often fire on the same bar

## Breakdowns

### By strategy

| bucket | n | n_signals | sum_R | avg_R | win_rate |
|---|---|---|---|---|---|
| D | 6 | 6 | 6.854 | 1.142 | 0.667 |
| D2 | 11 | 9 | -9.230 | -0.839 | 0.273 |
| E | 2 | 2 | 6.964 | 3.482 | 1.000 |
| E2 | 2 | 1 | 6.367 | 3.183 | 1.000 |
| F | 3 | 3 | 7.722 | 2.574 | 1.000 |
| F2 | 10 | 7 | -1.082 | -0.108 | 0.300 |
| G | 7 | 7 | -2.129 | -0.304 | 0.286 |

### By regime x direction

| bucket | n | n_signals | sum_R | avg_R | win_rate | alignment |
|---|---|---|---|---|---|---|
| CHOP|long | 1 | 1 | -1.082 | -1.082 | 0.000 | NO_TREND_REGIME |
| CHOP|short | 1 | 1 | 2.284 | 2.284 | 1.000 | NO_TREND_REGIME |
| NONE|long | 1 | 1 | 0.126 | 0.126 | 1.000 | UNLABELED |
| NONE|short | 4 | 1 | -5.544 | -1.386 | 0.000 | UNLABELED |
| RANGE|long | 5 | 5 | -0.439 | -0.088 | 0.200 | NO_TREND_REGIME |
| RANGE|short | 4 | 3 | 9.735 | 2.434 | 1.000 | NO_TREND_REGIME |
| TREND_DOWN|long | 4 | 4 | -1.352 | -0.338 | 0.250 | COUNTER |
| TREND_DOWN|short | 17 | 10 | 5.453 | 0.321 | 0.471 | ALIGNED |
| TREND_UP|long | 4 | 4 | 6.285 | 1.571 | 0.750 | ALIGNED |

### By alignment

| bucket | n | n_signals | sum_R | avg_R | win_rate |
|---|---|---|---|---|---|
| ALIGNED | 21 | 14 | 11.738 | 0.559 | 0.524 |
| COUNTER | 4 | 4 | -1.352 | -0.338 | 0.250 |
| NO_TREND_REGIME | 11 | 10 | 10.498 | 0.954 | 0.545 |
| UNLABELED | 5 | 2 | -5.418 | -1.084 | 0.200 |

### By outcome

| bucket | n | n_signals | sum_R | avg_R | win_rate |
|---|---|---|---|---|---|
| LOSS | 19 | 13 | -23.330 | -1.228 | 0.000 |
| TIMEOUT | 20 | 15 | 32.264 | 1.613 | 0.850 |
| WIN | 2 | 2 | 6.532 | 3.266 | 1.000 |

### By exchange

| bucket | n | n_signals | sum_R | avg_R | win_rate |
|---|---|---|---|---|---|
| binance | 26 | 22 | 4.669 | 0.180 | 0.385 |
| kraken | 15 | 11 | 10.797 | 0.720 | 0.600 |

### By weekday (open_date)

| bucket | n | n_signals | sum_R | avg_R | win_rate |
|---|---|---|---|---|---|
| Fri | 9 | 6 | -1.186 | -0.132 | 0.333 |
| Mon | 6 | 2 | 14.036 | 2.339 | 0.833 |
| Sat | 4 | 4 | 1.278 | 0.320 | 0.250 |
| Sun | 1 | 1 | 0.592 | 0.592 | 1.000 |
| Thu | 6 | 6 | -0.087 | -0.014 | 0.667 |
| Tue | 8 | 5 | -4.742 | -0.593 | 0.125 |
| Wed | 7 | 6 | 5.575 | 0.796 | 0.571 |

### By month (close_date)

| bucket | n | n_signals | sum_R | avg_R | win_rate |
|---|---|---|---|---|---|
| 2026-05 | 8 | 5 | -7.403 | -0.925 | 0.125 |
| 2026-06 | 15 | 10 | 27.109 | 1.807 | 0.800 |
| 2026-07 | 6 | 3 | -3.959 | -0.660 | 0.167 |
| 2026-08 | 8 | 8 | -5.374 | -0.672 | 0.250 |
| 2026-09 | 4 | 4 | 5.093 | 1.273 | 0.750 |

## Stop discipline

- breaches (pnl_r < -1.2): 7 · total excess loss beyond -1R: 6.062 R

| id | symbol | strategy | dir | open_date | pnl_r | sl | close_price |
|---|---|---|---|---|---|---|---|
| 46 | XRPUSDT | D2 | short | 2026-08-06 | -4.627 | 1.097 | 1.287 |
| 47 | DOTUSDT | F2 | short | 2026-08-14 | -1.554 | 0.813 | 0.839 |
| 15 | XRPUSDT | D2 | short | 2026-04-28 | -1.415 | 1.464 | 1.491 |
| 16 | XRPUSDT | F2 | short | 2026-04-28 | -1.415 | 1.464 | 1.491 |
| 13 | XRPUSDT | D2 | short | 2026-04-28 | -1.357 | 1.464 | 1.490 |
| 14 | XRPUSDT | F2 | short | 2026-04-28 | -1.357 | 1.464 | 1.490 |
| 44 | LINKUSDT | F2 | long | 2026-07-22 | -1.337 | 8.185 | 8.057 |

## MFE capture (closed, excursion row, MFE >= 1R)

- n 10 · mean MFE 2.983 R · mean realized 1.785 R · mean given back 0.747 R
- capture ratio 0.598 · reached 2R but closed below 1R: 1

## Holding

- TIMEOUT share 0.488 (20 closes)
- LOSS: n 19 · mean 11.470 d · max 20.000 d
- TIMEOUT: n 20 · mean 20.050 d · max 21.000 d
- WIN: n 2 · mean 12.500 d · max 18.000 d

## Sample quality

- D: closed 6 (signals 6) vs 20 → PRELIMINARY
- D2: closed 11 (signals 9) vs 20 → PRELIMINARY
- E: closed 2 (signals 2) vs 20 → PRELIMINARY
- E2: closed 2 (signals 1) vs 20 → PRELIMINARY
- F: closed 3 (signals 3) vs 20 → PRELIMINARY
- F2: closed 10 (signals 7) vs 20 → PRELIMINARY
- G: closed 7 (signals 7) vs 20 → PRELIMINARY

## Rule suggestions (SUGGESTION_ONLY)

- **block_long_in_TREND_DOWN** [OK] — block long when regime=TREND_DOWN (counter-trend) · evidence {"avg_R": -0.338, "n": 4, "n_signals": 4, "sum_R": -1.352, "win_rate": 0.25} · observation only; not applied
- **enforce_hard_stop** [OK] — enforce hard stop / investigate fills (losses beyond planned -1R) · evidence {"n_breaches": 7, "total_excess_loss_R": 6.062, "worst_ids": [46, 47, 15, 16, 13]} · observation only; not applied
- **partial_tp_or_trail_2R** [OK] — add partial take-profit or trailing stop at 2R · evidence {"capture_ratio": 0.598, "mean_MFE_R": 2.983, "mean_realized_R": 1.785, "n": 10, "reached_2R_but_closed_below_1R": 1} · observation only; not applied
- **review_pause_D2** [PRELIMINARY] — review/pause strategy D2 (Donchian Breakout (loose)) · evidence {"avg_R": -0.839, "n": 11, "n_signals": 9, "sum_R": -9.23, "win_rate": 0.273} · observation only; not applied

_READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER_
