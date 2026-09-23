# Strategy D replay: slots, direction, exits — 2026-09-23

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

**Question asked by the operator:** is there anything grounded in strategy, math and logic that can be changed to make the paper bot profitable?

**Method.** The bot's own code was replayed, not re-implemented: `scripts.live_signals.compute_indicators`,
`scripts.trade_bot.detect_signal_d`, `scripts.regime_detector.detect_regime` and
`scripts.regime_control.is_signal_allowed`, on Binance spot daily bars for the current 42-symbol universe,
2026-02-26 .. 2026-09-22 (500 bars fetched, 290 warm-up for EMA200 and the ATR percentile). Exits mirror
the bot's D rules: 2×ATR stop, half off at 2R then breakeven, 3R target, 20-bar timeout. Entry at next open,
0.1% cost per side, stop-first inside a bar (conservative). Strict D only; F/E/G not modelled. Risk 1R per
trade. Scripts live in the session scratchpad; nothing was written to the bot.

**Caveats that bound every number below.** (1) Spot data, not the bot's feed. (2) The 42-symbol universe
was chosen on 2026-09-16, so pre-September symbol results carry selection bias. (3) The direction split
was examined after seeing the aggregate: it is a post-hoc cut, not a pre-registered test. (4) Seven months
is one macro regime pair (bear into June, bull after), not a sample of regimes.

## 1. Allowed D signals

414 regime-allowed D signals: 108 long (TREND_UP) and 306 short (TREND_DOWN). Shorts are 74% of what the
gate lets through. The 09-15 dump produced the only BTC short signal in 28 bars and it was blocked
(TREND_UP); that block was correct with hindsight.

## 2. Slot policy (one position per exchange per strategy today)

| slots | trades | sum R | mean R | win | max DD (R) |
|---|---|---|---|---|---|
| 1 (today) | 18 | -1.6 | -0.091 | 0.33 | -6.7 |
| 2 | 34 | -5.6 | -0.163 | 0.32 | -8.3 |
| 3 | 47 | -7.3 | -0.155 | 0.34 | -9.9 |
| 5 | 70 | -6.9 | -0.099 | 0.37 | -13.1 |
| unlimited | 197 | +16.8 | +0.085 | 0.46 | -28.9 |

Unlimited: bootstrap p(mean R > 0) = 0.84. **No slot policy is significantly positive.** Raising the cap
does not create profit; it changes which signals are taken, and most of them are shorts.

## 3. Direction (unlimited slots)

| side | n | sum R | mean R | win | p(mean>0) |
|---|---|---|---|---|---|
| long | 57 | +19.5 | +0.342 | 0.56 | 0.98 |
| short | 140 | -2.7 | -0.019 | 0.42 | 0.43 |

Robustness of the long result: 3 symbols (ZEC, NEAR, ARB) carry 18.2 of the 19.5R; without them the
long side is +1.3R. First half of the window (bear) longs are -0.1R over 13 trades; second half (bull)
+19.6R over 44. Original 11-symbol universe only: +3.8R over 14 trades, p = 0.89.

Robustness of the short result: first half +20.4R over 88 trades (p = 0.96); second half -20.9R over 54
(p = 0.001). Without May 2026 the short side is -41.2R over 116 trades. **Shorts made money only while
the market was falling and gave it all back after.** Wanting more shorts is wanting more of that.

Long-only with the current 1 slot: -1.5R over 10 trades. Long-priority with 3 slots: -8.3R over 48.

## 4. Exits (same signals, unlimited slots)

| exit | both n / mean | long n / mean | short n / mean |
|---|---|---|---|
| A current (3R target, 2R partial, 20-bar timeout) | 178 / +0.083 | 47 / +0.330 | 133 / -0.020 |
| B 2×ATR trail, no target | 114 / +0.108 | 37 / +0.322 | 95 / +0.116 |
| C Donchian 10-day trailing exit | 114 / +0.017 | 37 / +0.394 | 95 / +0.001 |
| D 3×ATR trail | 114 / +0.029 | 37 / +0.338 | 95 / -0.005 |

No exit variant is significantly different from the current one. The tails exist (best trade +7R under
trailing exits vs +2.5R capped today) but they do not pay for the extra losers at this sample size.
Second-half shorts are negative under every exit (mean -0.34R to -0.54R, p ≤ 0.005).

## 5. What this supports, and what it does not

- **Supported:** the Donchian-20 D signal with the bot's exits has an expectancy near zero after costs
  across this window. Nothing in slot count or exit design moves it significantly. The regime gate on
  shorts is not what stands between the bot and profit.
- **Not supported:** a hand-applied "long-only D" rule. The long edge is 3 symbols in one bull phase and
  was found post hoc. It is exactly the kind of result the pre-registration framework exists to stop
  being applied on sight.
- **Registered instead (SHADOW, nothing applied):** `blockwhere__strategy=D__direction=short` in the
  hypothesis ledger with this study frozen as in-sample evidence. It is scored forward on the bot's own
  D short trades as they close; CONFIRMED at n ≥ 20 with p ≥ 0.90 would be the operator's cue to
  consider dropping D shorts in the paper bot, REJECTED closes the question.

## 6. The one structural fact that is not a strategy question

With one slot per exchange per strategy and a 42-symbol universe, the bot cannot take most of what its
own gate allows (389 of 414 signals skipped at 1 slot). Whether that matters depends on the signal having
an edge, which this window does not show. Measure it before changing it: log `SLOT_OCCUPIED` skips as
blocked-entry rows so the hindsight resolver and the unblock ledger can score them (next action).

Generated from the scratchpad scripts `slot_cap_study.py`, `slot_cap_breakdown.py`, `slot_cap_longonly.py`,
`exit_variants.py` (session 2026-09-23). Recommendation-only. It changes no gate, parameter or trade.
