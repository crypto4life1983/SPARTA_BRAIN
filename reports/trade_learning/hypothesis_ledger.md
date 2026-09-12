# Trade Hypothesis Ledger — 2026-09-12

**READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER**

Every rule suggestion from the learning report is registered here as a hypothesis. Its in-sample evidence is frozen at registration; it is then scored only on PAPER trades that close strictly after that date (out-of-sample by construction), via a counterfactual delta_R = R(rule) − R(realized) per deduplicated signal. Mirrored exchange rows collapse to one signal (best-R row). Thresholds are pre-registered: CONFIRMED needs n >= 20 forward signals and bootstrap p_positive >= 0.9; REJECTED needs the same n and p_positive <= 0.5; otherwise SHADOW.

Status counts: APPLIED 4

| id | status | kind | registered | in-sample evidence (frozen) | fwd n (rows) | mean ΔR | sum ΔR | p_positive | next threshold |
|---|---|---|---|---|---|---|---|---|---|
| block_long_in_TREND_DOWN | **APPLIED** | block | 2026-09-11 | avg_R=-0.338 n=4 n_signals=4 sum_R=-1.352 win_rate=0.250 | 0 (0) | - | 0.000 | - | need 20 forward signals (have 0) |
| enforce_hard_stop | **APPLIED** | stop_cap | 2026-09-11 | n_breaches=7 total_excess_loss_R=6.062 worst_ids=[46,47,15,16,13] | 0 (0) | - | 0.000 | - | need 20 forward signals (have 0) |
| partial_tp_or_trail_2R | **APPLIED** | partial_2R | 2026-09-11 | capture_ratio=0.598 mean_MFE_R=2.983 mean_realized_R=1.785 n=10 reached_2R_but_closed_below_1R=1 | 0 (0) | - | 0.000 | - | need 20 forward signals (have 0) |
| review_pause_D2 | **APPLIED** | block | 2026-09-11 | avg_R=-0.839 n=11 n_signals=9 sum_R=-9.230 win_rate=0.273 | 0 (0) | - | 0.000 | - | need 20 forward signals (have 0) |

## Rules

- **block_long_in_TREND_DOWN** — block long when regime=TREND_DOWN (counter-trend) · params {"alignment": "COUNTER", "direction": "long", "regime": "TREND_DOWN"} · last change 2026-09-11: SHADOW -> APPLIED: applied in obsidian-trade-logger commit c9a8f7b (bar-aware stops, regime fail-closed, 2R partial, D2 watch)
- **enforce_hard_stop** — enforce hard stop / investigate fills (losses beyond planned -1R) · params {"cap_R": -1.5} · last change 2026-09-11: SHADOW -> APPLIED: applied in obsidian-trade-logger commit c9a8f7b (bar-aware stops, regime fail-closed, 2R partial, D2 watch)
- **partial_tp_or_trail_2R** — add partial take-profit or trailing stop at 2R · params {"fraction": 0.5, "trigger_R": 2.0} · last change 2026-09-11: SHADOW -> APPLIED: applied in obsidian-trade-logger commit c9a8f7b (bar-aware stops, regime fail-closed, 2R partial, D2 watch)
- **review_pause_D2** — review/pause strategy D2 (Donchian Breakout (loose)) · params {"strategy": "D2"} · last change 2026-09-11: SHADOW -> APPLIED: applied in obsidian-trade-logger commit c9a8f7b (bar-aware stops, regime fail-closed, 2R partial, D2 watch)

## What a CONFIRMED rule means

CONFIRMED means the forward counterfactual evidence crossed the pre-registered thresholds on trades that closed after the hypothesis was registered. It is a recommendation for the operator to consider applying, by hand, in the PAPER bot after reading the numbers. Nothing is applied automatically: this tool has no broker, no order path, never writes to the journal and never changes the bot. CONFIRMED is not a claim about live trading. Every hypothesis keeps being re-scored as more paper trades close and can fall back to SHADOW or move to REJECTED. Counterfactual deltas are approximations (see the partial_2R note in the module docstring) and small samples are noisy even past the thresholds.

_READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER_
