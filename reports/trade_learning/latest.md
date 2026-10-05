# Trade Journal Learning Report — 2026-10-05

**READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER**

Sample label: **OK** (dedup closed signals 34 vs MIN_SIGNALS=30). Every conclusion below threshold is PRELIMINARY.

## Counts (closed trades)

- rows 51 · closed 45 · open 6 · distinct signals (closed) 34
- sum_R raw 6.053 · dedup best-row -0.532 · dedup mean-row -1.545
- win rate 0.422 · expectancy 0.135 R (dedup mean -0.045) · profit factor 1.175
- note: raw rows overstate the sample: the bot mirrors signals on binance and kraken and the loose '2' variants often fire on the same bar

## Evidence split (cutoff 2026-09-15 on open_date)

_partial-bar fix; trades opened before this date were generated from a still-forming candle and are retired from evidence._

| bucket | closed | signals | sum R | expectancy R | win rate | WIN | profitable TIMEOUT |
|---|---|---|---|---|---|---|---|
| valid forward evidence | 3 | 3 | -3.049 | -1.016 | 0.000 | 0 | 0 |
| retired (pre-fix) | 42 | 31 | 9.102 | 0.217 | 0.452 | 2 | 17 |

- headline counts above cover ALL closed trades, including the retired ones; read expectancy/win-rate against valid_forward
- retired share of closed rows: 0.933

## Breakdowns

### By strategy

| bucket | n | n_signals | sum_R | avg_R | win_rate |
|---|---|---|---|---|---|
| D | 7 | 7 | 5.839 | 0.834 | 0.571 |
| D2 | 11 | 9 | -9.230 | -0.839 | 0.273 |
| E | 3 | 3 | 5.857 | 1.952 | 0.667 |
| E2 | 2 | 1 | 6.367 | 3.183 | 1.000 |
| F | 4 | 4 | 6.704 | 1.676 | 0.750 |
| F2 | 11 | 8 | -2.098 | -0.191 | 0.273 |
| G | 7 | 7 | -7.386 | -1.055 | 0.286 |

### By regime x direction

| bucket | n | n_signals | sum_R | avg_R | win_rate | alignment |
|---|---|---|---|---|---|---|
| CHOP|long | 1 | 1 | -1.082 | -1.082 | 0.000 | NO_TREND_REGIME |
| CHOP|short | 1 | 1 | 2.284 | 2.284 | 1.000 | NO_TREND_REGIME |
| NONE|long | 1 | 1 | 0.338 | 0.338 | 1.000 | UNLABELED |
| NONE|short | 4 | 1 | -5.544 | -1.386 | 0.000 | UNLABELED |
| RANGE|long | 5 | 5 | -1.991 | -0.398 | 0.200 | NO_TREND_REGIME |
| RANGE|short | 5 | 4 | 8.717 | 1.743 | 0.800 | NO_TREND_REGIME |
| TREND_DOWN|long | 4 | 4 | -5.269 | -1.317 | 0.250 | COUNTER |
| TREND_DOWN|short | 19 | 12 | 3.422 | 0.180 | 0.421 | ALIGNED |
| TREND_UP|long | 5 | 5 | 5.178 | 1.036 | 0.600 | ALIGNED |

### By alignment

| bucket | n | n_signals | sum_R | avg_R | win_rate |
|---|---|---|---|---|---|
| ALIGNED | 24 | 17 | 8.600 | 0.358 | 0.458 |
| COUNTER | 4 | 4 | -5.269 | -1.317 | 0.250 |
| NO_TREND_REGIME | 12 | 11 | 7.928 | 0.661 | 0.500 |
| UNLABELED | 5 | 2 | -5.206 | -1.041 | 0.200 |

### By outcome

| bucket | n | n_signals | sum_R | avg_R | win_rate |
|---|---|---|---|---|---|
| LOSS | 23 | 17 | -32.955 | -1.433 | 0.000 |
| TIMEOUT | 20 | 15 | 32.476 | 1.624 | 0.850 |
| WIN | 2 | 2 | 6.532 | 3.266 | 1.000 |

### By exchange

| bucket | n | n_signals | sum_R | avg_R | win_rate |
|---|---|---|---|---|---|
| binance | 30 | 26 | -4.744 | -0.158 | 0.333 |
| kraken | 15 | 11 | 10.797 | 0.720 | 0.600 |

### By weekday (open_date)

| bucket | n | n_signals | sum_R | avg_R | win_rate |
|---|---|---|---|---|---|
| Fri | 9 | 6 | -1.186 | -0.132 | 0.333 |
| Mon | 6 | 2 | 14.036 | 2.339 | 0.833 |
| Sat | 5 | 5 | -1.451 | -0.290 | 0.200 |
| Sun | 1 | 1 | 0.592 | 0.592 | 1.000 |
| Thu | 7 | 7 | -2.761 | -0.394 | 0.571 |
| Tue | 8 | 5 | -6.933 | -0.867 | 0.125 |
| Wed | 9 | 8 | 3.756 | 0.417 | 0.444 |

### By month (close_date)

| bucket | n | n_signals | sum_R | avg_R | win_rate |
|---|---|---|---|---|---|
| 2026-05 | 8 | 5 | -8.743 | -1.093 | 0.125 |
| 2026-06 | 15 | 10 | 23.192 | 1.546 | 0.800 |
| 2026-07 | 6 | 3 | -3.959 | -0.660 | 0.167 |
| 2026-08 | 8 | 8 | -5.374 | -0.672 | 0.250 |
| 2026-09 | 8 | 8 | 0.937 | 0.117 | 0.375 |

## Stop discipline

- breaches (pnl_r < -1.2): 11 · total excess loss beyond -1R: 9.183 R

| id | symbol | strategy | dir | open_date | pnl_r | sl | close_price |
|---|---|---|---|---|---|---|---|
| 46 | XRPUSDT | D2 | short | 2026-08-06 | -4.627 | 1.097 | 1.287 |
| 33 | XRPUSDT | G | long | 2026-06-02 | -2.184 | 1.255 | 1.222 |
| 34 | XRPUSDT | G | long | 2026-06-04 | -2.176 | 1.167 | 1.137 |
| 47 | DOTUSDT | F2 | short | 2026-08-14 | -1.554 | 0.813 | 0.839 |
| 35 | XRPUSDT | G | long | 2026-06-06 | -1.501 | 1.038 | 1.014 |
| 15 | XRPUSDT | D2 | short | 2026-04-28 | -1.415 | 1.464 | 1.491 |
| 16 | XRPUSDT | F2 | short | 2026-04-28 | -1.415 | 1.464 | 1.491 |
| 13 | XRPUSDT | D2 | short | 2026-04-28 | -1.357 | 1.464 | 1.490 |
| 14 | XRPUSDT | F2 | short | 2026-04-28 | -1.357 | 1.464 | 1.490 |
| 44 | LINKUSDT | F2 | long | 2026-07-22 | -1.337 | 8.185 | 8.057 |
| 29 | XRPUSDT | G | long | 2026-05-23 | -1.260 | 1.308 | 1.302 |

## MFE capture (closed, excursion row, MFE >= 1R)

- n 10 · mean MFE 2.983 R · mean realized 1.724 R · mean given back 0.747 R
- capture ratio 0.578 · reached 2R but closed below 1R: 1

## Holding

- TIMEOUT share 0.444 (20 closes)
- LOSS: n 23 · mean 10.830 d · max 20.000 d
- TIMEOUT: n 20 · mean 20.050 d · max 21.000 d
- WIN: n 2 · mean 12.500 d · max 18.000 d

## Sample quality

- D: closed 7 (signals 7) vs 20 → PRELIMINARY
- D2: closed 11 (signals 9) vs 20 → PRELIMINARY
- E: closed 3 (signals 3) vs 20 → PRELIMINARY
- E2: closed 2 (signals 1) vs 20 → PRELIMINARY
- F: closed 4 (signals 4) vs 20 → PRELIMINARY
- F2: closed 11 (signals 8) vs 20 → PRELIMINARY
- G: closed 7 (signals 7) vs 20 → PRELIMINARY

## Rule suggestions (SUGGESTION_ONLY)

- **block_long_in_TREND_DOWN** [OK] — block long when regime=TREND_DOWN (counter-trend) · evidence {"avg_R": -1.317, "n": 4, "n_signals": 4, "sum_R": -5.269, "win_rate": 0.25} · observation only; not applied
- **enforce_hard_stop** [OK] — enforce hard stop / investigate fills (losses beyond planned -1R) · evidence {"n_breaches": 11, "total_excess_loss_R": 9.183, "worst_ids": [46, 33, 34, 47, 35]} · observation only; not applied
- **partial_tp_or_trail_2R** [OK] — add partial take-profit or trailing stop at 2R · evidence {"capture_ratio": 0.578, "mean_MFE_R": 2.983, "mean_realized_R": 1.724, "n": 10, "reached_2R_but_closed_below_1R": 1} · observation only; not applied
- **review_pause_D2** [PRELIMINARY] — review/pause strategy D2 (Donchian Breakout (loose)) · evidence {"avg_R": -0.839, "n": 11, "n_signals": 9, "sum_R": -9.23, "win_rate": 0.273} · observation only; not applied

_READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER_
