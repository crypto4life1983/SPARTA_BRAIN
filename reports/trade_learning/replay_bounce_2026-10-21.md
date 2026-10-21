# Replay study: support-bounce entries the bot does not take — 2026-10-21

**READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER**

**Question (operator, 2026-10-21):** price bounced at the Donchian low and the 50 EMA and the bot took no entry. Correct by construction: D/E/F/F2 are breakout or EMA-cross rules and a bounce is a close inside the range. This replay gives the bounce idea a number on the same data and exits as the live rules (see the rule block at the top of `tools/replay_bounce_rules.py`; all rules and the headline test were fixed before the run).

**Headline (DON_T d_exit gated):** n=147, mean -0.110R per trade; minus the any-day benchmark -0.067R, p=0.182, stable across half-years: no. **Does not pass the pre-stated bar** (p >= 0.99 and same sign in every half-year with >= 10 trades).

## Benchmark: long at any bar's close, D exit, one trade per symbol at a time

| n | mean R | win | p(mean>0) | post-fix | by half-year |
|---|---|---|---|---|---|
| 2042 | -0.043 | 0.45 | 0.025 | -0.197 (n=66) | -0.03(536), +0.02(463), -0.20(558), +0.10(419), -0.20(66) · stable no |

Every number below has to be read against this line: it is what buying on a random day with the same exit returned over the window. A rule that merely matches it has found nothing.

## Long rules (support)

| rule / exit / gate | n | mean R | win | p(mean>0) | post-fix | by half-year |
|---|---|---|---|---|---|---|
| DON d exit | 1045 | -0.108 | 0.42 | 0.001 | +0.783 (n=14) | -0.27(261), +0.03(216), -0.19(344), +0.03(210), +0.78(14) · stable no |
| DON d exit gated | 153 | -0.100 | 0.39 | 0.063 | +0.667 (n=4) | -0.30(81), +0.22(49), -0.69(9), +0.15(10), +0.67(4) · stable no |
| DON s exit | 1412 | -0.130 | 0.45 | 0.000 | +0.176 (n=41) | -0.31(344), +0.09(294), -0.21(446), -0.05(287), +0.18(41) · stable no |
| DON s exit gated | 179 | -0.197 | 0.42 | 0.003 | -0.500 (n=15) | -0.41(87), +0.22(54), -0.58(11), +0.20(12), -0.50(15) · stable no |
| DON_T d exit | 173 | -0.108 | 0.40 | 0.041 | +0.457 (n=5) | -0.33(86), +0.21(60), -0.75(11), +0.26(11), +0.46(5) · stable no |
| DON_T d exit gated | 147 | -0.110 | 0.39 | 0.050 | +0.667 (n=4) | -0.32(77), +0.19(48), -0.69(9), +0.28(9), +0.67(4) · stable no |
| DON_T s exit | 212 | -0.167 | 0.44 | 0.007 | -0.466 (n=14) | -0.47(99), +0.30(71), -0.53(13), +0.26(15), -0.47(14) · stable no |
| DON_T s exit gated | 171 | -0.214 | 0.42 | 0.003 | -0.417 (n=13) | -0.46(83), +0.19(53), -0.58(11), +0.31(11), -0.42(13) · stable no |
| EMA50 d exit | 245 | -0.353 | 0.30 | 0.000 | -0.617 (n=12) | -0.48(119), -0.23(87), -0.22(12), +0.05(15), -0.62(12) · stable no |
| EMA50 d exit gated | 213 | -0.319 | 0.31 | 0.000 | -0.575 (n=11) | -0.45(98), -0.23(81), +0.04(10), +0.01(13), -0.57(11) · stable no |
| EMA50 s exit | 368 | -0.299 | 0.38 | 0.000 | -0.463 (n=22) | -0.42(165), -0.11(131), -0.40(21), -0.27(29), -0.46(22) · stable yes |
| EMA50 s exit gated | 286 | -0.288 | 0.38 | 0.000 | -0.340 (n=19) | -0.36(128), -0.21(104), -0.33(17), -0.14(18), -0.34(19) · stable yes |

| rule (d_exit) | vs any-day Δ mean R | p(rule > any-day) | 95% CI |
|---|---|---|---|
| DON d exit | -0.066 | 0.036 | [-0.133, +0.006] |
| DON d exit gated | -0.057 | 0.201 | [-0.188, +0.079] |
| DON_T d exit | -0.066 | 0.163 | [-0.193, +0.062] |
| DON_T d exit gated | -0.067 | 0.182 | [-0.197, +0.071] |
| EMA50 d exit | -0.311 | 0.0 | [-0.428, -0.187] |
| EMA50 d exit gated | -0.276 | 0.0 | [-0.405, -0.149] |

## Mirror short rules (resistance), for regime dependence only

| rule / exit / gate | n | mean R | win | p(mean>0) | post-fix | by half-year |
|---|---|---|---|---|---|---|
| DON_HI d exit | 909 | +0.016 | 0.52 | 0.689 | -0.310 (n=54) | -0.13(250), +0.03(258), +0.20(194), +0.11(153), -0.31(54) · stable no |
| DON_HI d exit gated | 434 | +0.086 | 0.56 | 0.975 | -0.650 (n=12) | -0.15(71), -0.02(109), +0.25(159), +0.22(83), -0.65(12) · stable no |
| DON_HI_T d exit | 502 | +0.076 | 0.56 | 0.965 | -0.642 (n=16) | -0.23(82), +0.06(125), +0.21(168), +0.22(111), -0.64(16) · stable no |
| DON_HI_T d exit gated | 429 | +0.091 | 0.56 | 0.975 | -0.650 (n=12) | -0.16(70), +0.01(106), +0.24(158), +0.22(83), -0.65(12) · stable no |
| EMA50_S d exit | 566 | +0.091 | 0.54 | 0.985 | -1.016 (n=9) | -0.34(54), +0.06(187), +0.18(186), +0.26(130), -1.02(9) · stable no |
| EMA50_S d exit gated | 518 | +0.083 | 0.53 | 0.972 | -1.016 (n=8) | -0.35(52), +0.03(159), +0.19(177), +0.26(122), -1.02(8) · stable no |

## What the long rules would have fired since 2026-10-01 (every signal, before dedup)

| date | symbol | rule | regime | live gate | result |
|---|---|---|---|---|---|
| 2026-10-05 | TRXUSDT | EMA50 | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 24%) | LOSS -1.09R |
| 2026-10-07 | CRVUSDT | EMA50 | TREND_UP | allowed | LOSS -1.01R |
| 2026-10-07 | TRXUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 18%) | LOSS -1.09R |
| 2026-10-07 | TRXUSDT | DON_T | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 18%) | LOSS -1.09R |
| 2026-10-09 | ARBUSDT | EMA50 | TREND_UP | allowed | open, +0.15R at last close |
| 2026-10-09 | BNBUSDT | EMA50 | TREND_UP | allowed | open, -0.01R at last close |
| 2026-10-09 | CHZUSDT | DON | TREND_DOWN | blocked: regime=TREND_DOWN blocks new longs | LOSS -1.01R |
| 2026-10-09 | CRVUSDT | DON | TREND_UP | allowed | open, +0.48R at last close |
| 2026-10-09 | CRVUSDT | DON_T | TREND_UP | allowed | open, +0.48R at last close |
| 2026-10-09 | CRVUSDT | EMA50 | TREND_UP | allowed | open, +0.48R at last close |
| 2026-10-09 | LINKUSDT | EMA50 | TREND_UP | allowed | open, -0.32R at last close |
| 2026-10-09 | POLUSDT | DON | TREND_UP | allowed | open, -0.44R at last close |
| 2026-10-09 | POLUSDT | DON_T | TREND_UP | allowed | open, -0.44R at last close |
| 2026-10-09 | THETAUSDT | DON | TREND_UP | allowed | LOSS -1.01R |
| 2026-10-09 | THETAUSDT | DON_T | TREND_UP | allowed | LOSS -1.01R |
| 2026-10-09 | UNIUSDT | DON | TREND_UP | allowed | open, +0.09R at last close |
| 2026-10-09 | UNIUSDT | DON_T | TREND_UP | allowed | open, +0.09R at last close |
| 2026-10-09 | UNIUSDT | EMA50 | TREND_UP | allowed | open, +0.09R at last close |
| 2026-10-09 | VETUSDT | EMA50 | TREND_UP | allowed | LOSS -1.01R |
| 2026-10-09 | XTZUSDT | DON | TREND_DOWN | blocked: regime=TREND_DOWN blocks new longs | WIN +0.49R |
| 2026-10-09 | ZECUSDT | EMA50 | TREND_UP | allowed | open, +0.23R at last close |
| 2026-10-10 | BNBUSDT | EMA50 | TREND_UP | allowed | open, -0.19R at last close |
| 2026-10-10 | ETHUSDT | EMA50 | TREND_UP | allowed | LOSS -1.03R |
| 2026-10-10 | LINKUSDT | EMA50 | TREND_UP | allowed | LOSS -1.02R |
| 2026-10-10 | POLUSDT | EMA50 | TREND_UP | allowed | LOSS -1.01R |
| 2026-10-10 | SOLUSDT | EMA50 | TREND_UP | allowed | LOSS -1.02R |
| 2026-10-10 | UNIUSDT | DON | TREND_UP | allowed | open, -0.11R at last close |
| 2026-10-10 | UNIUSDT | DON_T | TREND_UP | allowed | open, -0.11R at last close |
| 2026-10-10 | UNIUSDT | EMA50 | TREND_UP | allowed | open, -0.11R at last close |
| 2026-10-10 | VETUSDT | EMA50 | TREND_UP | allowed | LOSS -1.01R |
| 2026-10-10 | XRPUSDT | EMA50 | TREND_UP | allowed | LOSS -1.02R |
| 2026-10-10 | ZECUSDT | EMA50 | TREND_UP | allowed | open, +0.17R at last close |
| 2026-10-11 | CRVUSDT | EMA50 | TREND_UP | allowed | open, +0.32R at last close |
| 2026-10-11 | EGLDUSDT | DON | TREND_DOWN | blocked: regime=TREND_DOWN blocks new longs | LOSS -1.01R |
| 2026-10-11 | ETHUSDT | EMA50 | TREND_UP | allowed | LOSS -1.03R |
| 2026-10-11 | POLUSDT | EMA50 | TREND_UP | allowed | LOSS -1.02R |
| 2026-10-11 | SOLUSDT | EMA50 | TREND_UP | allowed | LOSS -1.02R |
| 2026-10-11 | UNIUSDT | EMA50 | TREND_UP | allowed | open, -0.27R at last close |
| 2026-10-11 | VETUSDT | EMA50 | TREND_UP | allowed | LOSS -1.01R |
| 2026-10-11 | XLMUSDT | EMA50 | TREND_UP | allowed | LOSS -1.02R |
| 2026-10-11 | XRPUSDT | EMA50 | TREND_UP | allowed | LOSS -1.02R |
| 2026-10-11 | ZECUSDT | EMA50 | TREND_UP | allowed | LOSS -1.01R |
| 2026-10-13 | ADAUSDT | DON | CHOP | blocked: regime=CHOP fakeout risk — all entries blocked | open, -0.34R at last close |
| 2026-10-13 | ARBUSDT | EMA50 | TREND_UP | allowed | open, -0.11R at last close |
| 2026-10-13 | AVAXUSDT | DON | TREND_UP | allowed | open, -0.32R at last close |
| 2026-10-13 | AVAXUSDT | DON_T | TREND_UP | allowed | open, -0.32R at last close |
| 2026-10-13 | AVAXUSDT | EMA50 | TREND_UP | allowed | open, -0.32R at last close |
| 2026-10-13 | BCHUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 9%) | open, +0.28R at last close |
| 2026-10-13 | BNBUSDT | DON | TREND_UP | allowed | open, -0.00R at last close |
| 2026-10-13 | BNBUSDT | DON_T | TREND_UP | allowed | open, -0.00R at last close |
| 2026-10-13 | BNBUSDT | EMA50 | TREND_UP | allowed | open, -0.00R at last close |
| 2026-10-13 | BTCUSDT | DON | TREND_UP | allowed | open, -0.03R at last close |
| 2026-10-13 | BTCUSDT | DON_T | TREND_UP | allowed | open, -0.03R at last close |
| 2026-10-13 | BTCUSDT | EMA50 | TREND_UP | allowed | open, -0.03R at last close |
| 2026-10-13 | CHZUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 7%) | open, -0.41R at last close |
| 2026-10-13 | DOGEUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 14%) | open, -0.28R at last close |
| 2026-10-13 | EGLDUSDT | DON | CHOP | blocked: regime=CHOP fakeout risk — all entries blocked | open, -0.08R at last close |
| 2026-10-13 | ETCUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 14%) | open, -0.18R at last close |
| 2026-10-13 | ETHUSDT | DON | TREND_UP | allowed | open, -0.26R at last close |
| 2026-10-13 | ETHUSDT | DON_T | TREND_UP | allowed | open, -0.26R at last close |
| 2026-10-13 | GRTUSDT | DON | TREND_UP | allowed | open, -0.33R at last close |
| 2026-10-13 | GRTUSDT | DON_T | TREND_UP | allowed | open, -0.33R at last close |
| 2026-10-13 | HBARUSDT | DON | CHOP | blocked: regime=CHOP fakeout risk — all entries blocked | open, -0.21R at last close |
| 2026-10-13 | LINKUSDT | DON | TREND_UP | allowed | open, -0.36R at last close |
| 2026-10-13 | LINKUSDT | DON_T | TREND_UP | allowed | open, -0.36R at last close |
| 2026-10-13 | LINKUSDT | EMA50 | TREND_UP | allowed | open, -0.36R at last close |
| 2026-10-13 | LTCUSDT | DON | TREND_UP | allowed | open, +0.07R at last close |
| 2026-10-13 | LTCUSDT | DON_T | TREND_UP | allowed | open, +0.07R at last close |
| 2026-10-13 | LTCUSDT | EMA50 | TREND_UP | allowed | open, +0.07R at last close |
| 2026-10-13 | POLUSDT | DON | TREND_UP | allowed | open, -0.48R at last close |
| 2026-10-13 | POLUSDT | DON_T | TREND_UP | allowed | open, -0.48R at last close |
| 2026-10-13 | RUNEUSDT | EMA50 | TREND_UP | allowed | open, +0.16R at last close |
| 2026-10-13 | SOLUSDT | DON | TREND_UP | allowed | open, -0.03R at last close |
| 2026-10-13 | SOLUSDT | DON_T | TREND_UP | allowed | open, -0.03R at last close |
| 2026-10-13 | THETAUSDT | DON | TREND_DOWN | blocked: regime=TREND_DOWN blocks new longs | open, +0.02R at last close |
| 2026-10-13 | UNIUSDT | DON | TREND_UP | allowed | open, -0.07R at last close |
| 2026-10-13 | UNIUSDT | DON_T | TREND_UP | allowed | open, -0.07R at last close |
| 2026-10-13 | UNIUSDT | EMA50 | TREND_UP | allowed | open, -0.07R at last close |
| 2026-10-13 | VETUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 3%) | open, -0.13R at last close |
| 2026-10-13 | XRPUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 14%) | open, -0.24R at last close |
| 2026-10-13 | YFIUSDT | DON | TREND_DOWN | blocked: regime=TREND_DOWN blocks new longs | open, -0.21R at last close |
| 2026-10-13 | ZECUSDT | DON | TREND_UP | allowed | open, +0.17R at last close |
| 2026-10-13 | ZECUSDT | DON_T | TREND_UP | allowed | open, +0.17R at last close |
| 2026-10-13 | ZECUSDT | EMA50 | TREND_UP | allowed | open, +0.17R at last close |
| 2026-10-14 | TRXUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 32%) | open, -0.15R at last close |
| 2026-10-14 | TRXUSDT | DON_T | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 32%) | open, -0.15R at last close |
| 2026-10-15 | AAVEUSDT | DON | TREND_UP | allowed | open, -0.14R at last close |
| 2026-10-15 | AAVEUSDT | DON_T | TREND_UP | allowed | open, -0.14R at last close |
| 2026-10-15 | AAVEUSDT | EMA50 | TREND_UP | allowed | open, -0.14R at last close |
| 2026-10-15 | ALGOUSDT | DON | TREND_UP | allowed | open, -0.23R at last close |
| 2026-10-15 | ALGOUSDT | DON_T | TREND_UP | allowed | open, -0.23R at last close |
| 2026-10-15 | ALGOUSDT | EMA50 | TREND_UP | allowed | open, -0.23R at last close |
| 2026-10-15 | ARBUSDT | DON | TREND_UP | allowed | open, -0.22R at last close |
| 2026-10-15 | ARBUSDT | DON_T | TREND_UP | allowed | open, -0.22R at last close |
| 2026-10-15 | ARBUSDT | EMA50 | TREND_UP | allowed | open, -0.22R at last close |
| 2026-10-15 | AVAXUSDT | DON | TREND_UP | allowed | open, -0.20R at last close |
| 2026-10-15 | AVAXUSDT | DON_T | TREND_UP | allowed | open, -0.20R at last close |
| 2026-10-15 | AVAXUSDT | EMA50 | TREND_UP | allowed | open, -0.20R at last close |
| 2026-10-15 | BCHUSDT | DON | TREND_DOWN | blocked: regime=TREND_DOWN blocks new longs | open, +0.15R at last close |
| 2026-10-15 | BTCUSDT | DON | TREND_UP | allowed | open, +0.17R at last close |
| 2026-10-15 | BTCUSDT | DON_T | TREND_UP | allowed | open, +0.17R at last close |
| 2026-10-15 | BTCUSDT | EMA50 | TREND_UP | allowed | open, +0.17R at last close |
| 2026-10-15 | CRVUSDT | DON | TREND_UP | allowed | open, +0.56R at last close |
| 2026-10-15 | CRVUSDT | DON_T | TREND_UP | allowed | open, +0.56R at last close |
| 2026-10-15 | CRVUSDT | EMA50 | TREND_UP | allowed | open, +0.56R at last close |
| 2026-10-15 | DOTUSDT | DON | TREND_DOWN | blocked: regime=TREND_DOWN blocks new longs | open, +0.01R at last close |
| 2026-10-15 | EGLDUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 9%) | open, +0.08R at last close |
| 2026-10-15 | ETCUSDT | DON | TREND_DOWN | blocked: regime=TREND_DOWN blocks new longs | open, -0.06R at last close |
| 2026-10-15 | ETHUSDT | DON | TREND_UP | allowed | open, +0.03R at last close |
| 2026-10-15 | ETHUSDT | DON_T | TREND_UP | allowed | open, +0.03R at last close |
| 2026-10-15 | FILUSDT | DON | TREND_UP | allowed | open, -0.48R at last close |
| 2026-10-15 | FILUSDT | DON_T | TREND_UP | allowed | open, -0.48R at last close |
| 2026-10-15 | FILUSDT | EMA50 | TREND_UP | allowed | open, -0.48R at last close |
| 2026-10-15 | HBARUSDT | DON | CHOP | blocked: regime=CHOP fakeout risk — all entries blocked | open, -0.07R at last close |
| 2026-10-15 | LINKUSDT | DON | TREND_UP | allowed | open, -0.08R at last close |
| 2026-10-15 | LINKUSDT | DON_T | TREND_UP | allowed | open, -0.08R at last close |
| 2026-10-15 | LTCUSDT | DON | TREND_UP | allowed | open, +0.09R at last close |
| 2026-10-15 | LTCUSDT | DON_T | TREND_UP | allowed | open, +0.09R at last close |
| 2026-10-15 | LTCUSDT | EMA50 | TREND_UP | allowed | open, +0.09R at last close |
| 2026-10-15 | NEARUSDT | DON | TREND_UP | allowed | open, -0.25R at last close |
| 2026-10-15 | NEARUSDT | DON_T | TREND_UP | allowed | open, -0.25R at last close |
| 2026-10-15 | POLUSDT | DON | TREND_UP | allowed | open, -0.05R at last close |
| 2026-10-15 | RUNEUSDT | DON | TREND_UP | allowed | open, +0.35R at last close |
| 2026-10-15 | RUNEUSDT | DON_T | TREND_UP | allowed | open, +0.35R at last close |
| 2026-10-15 | RUNEUSDT | EMA50 | TREND_UP | allowed | open, +0.35R at last close |
| 2026-10-15 | SOLUSDT | DON | TREND_UP | allowed | open, +0.10R at last close |
| 2026-10-15 | SOLUSDT | DON_T | TREND_UP | allowed | open, +0.10R at last close |
| 2026-10-15 | THETAUSDT | DON | CHOP | blocked: regime=CHOP fakeout risk — all entries blocked | open, +0.27R at last close |
| 2026-10-15 | UNIUSDT | DON | TREND_UP | allowed | open, +0.01R at last close |
| 2026-10-15 | UNIUSDT | DON_T | TREND_UP | allowed | open, +0.01R at last close |
| 2026-10-15 | UNIUSDT | EMA50 | TREND_UP | allowed | open, +0.01R at last close |
| 2026-10-15 | VETUSDT | DON | TREND_UP | allowed | open, +0.07R at last close |
| 2026-10-15 | XLMUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 2%) | open, -0.05R at last close |
| 2026-10-15 | XRPUSDT | DON | TREND_UP | allowed | open, +0.01R at last close |
| 2026-10-15 | XTZUSDT | DON | TREND_UP | allowed | open, +0.01R at last close |
| 2026-10-15 | XTZUSDT | DON_T | TREND_UP | allowed | open, +0.01R at last close |
| 2026-10-15 | YFIUSDT | DON | TREND_DOWN | blocked: regime=TREND_DOWN blocks new longs | open, -0.23R at last close |
| 2026-10-15 | ZECUSDT | DON | TREND_UP | allowed | open, +0.14R at last close |
| 2026-10-15 | ZECUSDT | DON_T | TREND_UP | allowed | open, +0.14R at last close |
| 2026-10-15 | ZECUSDT | EMA50 | TREND_UP | allowed | open, +0.14R at last close |
| 2026-10-16 | TRXUSDT | EMA50 | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 61%) | open, -0.55R at last close |
| 2026-10-17 | HBARUSDT | DON | CHOP | blocked: regime=CHOP fakeout risk — all entries blocked | open, -0.09R at last close |
| 2026-10-18 | AAVEUSDT | DON | TREND_UP | allowed | open, +0.12R at last close |
| 2026-10-18 | AAVEUSDT | DON_T | TREND_UP | allowed | open, +0.12R at last close |
| 2026-10-18 | AAVEUSDT | EMA50 | TREND_UP | allowed | open, +0.12R at last close |
| 2026-10-18 | ADAUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 10%) | open, +0.09R at last close |
| 2026-10-18 | ARBUSDT | EMA50 | TREND_UP | allowed | open, +0.02R at last close |
| 2026-10-18 | AVAXUSDT | DON | TREND_UP | allowed | open, -0.02R at last close |
| 2026-10-18 | AVAXUSDT | DON_T | TREND_UP | allowed | open, -0.02R at last close |
| 2026-10-18 | AVAXUSDT | EMA50 | TREND_UP | allowed | open, -0.02R at last close |
| 2026-10-18 | BCHUSDT | DON | TREND_DOWN | blocked: regime=TREND_DOWN blocks new longs | open, +0.22R at last close |
| 2026-10-18 | BNBUSDT | DON | TREND_UP | allowed | open, +0.45R at last close |
| 2026-10-18 | BNBUSDT | DON_T | TREND_UP | allowed | open, +0.45R at last close |
| 2026-10-18 | BTCUSDT | DON | TREND_UP | allowed | open, +0.22R at last close |
| 2026-10-18 | BTCUSDT | DON_T | TREND_UP | allowed | open, +0.22R at last close |
| 2026-10-18 | BTCUSDT | EMA50 | TREND_UP | allowed | open, +0.22R at last close |
| 2026-10-18 | CRVUSDT | EMA50 | TREND_UP | allowed | open, +0.64R at last close |
| 2026-10-18 | DOGEUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 11%) | open, +0.28R at last close |
| 2026-10-18 | DOTUSDT | DON | TREND_DOWN | blocked: regime=TREND_DOWN blocks new longs | open, +0.18R at last close |
| 2026-10-18 | ETHUSDT | DON | TREND_UP | allowed | open, +0.19R at last close |
| 2026-10-18 | ETHUSDT | DON_T | TREND_UP | allowed | open, +0.19R at last close |
| 2026-10-18 | HBARUSDT | DON | TREND_DOWN | blocked: regime=TREND_DOWN blocks new longs | open, -0.09R at last close |
| 2026-10-18 | LINKUSDT | DON | TREND_UP | allowed | open, +0.20R at last close |
| 2026-10-18 | LINKUSDT | DON_T | TREND_UP | allowed | open, +0.20R at last close |
| 2026-10-18 | LTCUSDT | DON | TREND_UP | allowed | open, +0.40R at last close |
| 2026-10-18 | LTCUSDT | DON_T | TREND_UP | allowed | open, +0.40R at last close |
| 2026-10-18 | RUNEUSDT | DON | TREND_UP | allowed | open, +0.17R at last close |
| 2026-10-18 | RUNEUSDT | DON_T | TREND_UP | allowed | open, +0.17R at last close |
| 2026-10-18 | RUNEUSDT | EMA50 | TREND_UP | allowed | open, +0.17R at last close |
| 2026-10-18 | SOLUSDT | DON | TREND_UP | allowed | open, +0.24R at last close |
| 2026-10-18 | SOLUSDT | DON_T | TREND_UP | allowed | open, +0.24R at last close |
| 2026-10-18 | UNIUSDT | DON | TREND_UP | allowed | open, +0.20R at last close |
| 2026-10-18 | UNIUSDT | DON_T | TREND_UP | allowed | open, +0.20R at last close |
| 2026-10-18 | VETUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 8%) | open, +0.40R at last close |
| 2026-10-18 | XLMUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 6%) | open, +0.22R at last close |
| 2026-10-18 | XRPUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 13%) | open, +0.24R at last close |
| 2026-10-18 | YFIUSDT | DON | TREND_DOWN | blocked: regime=TREND_DOWN blocks new longs | open, +0.11R at last close |
| 2026-10-18 | ZECUSDT | DON | TREND_UP | allowed | open, +0.53R at last close |
| 2026-10-18 | ZECUSDT | DON_T | TREND_UP | allowed | open, +0.53R at last close |
| 2026-10-19 | CRVUSDT | EMA50 | TREND_UP | allowed | open, +0.40R at last close |
| 2026-10-19 | GRTUSDT | DON | TREND_DOWN | blocked: regime=TREND_DOWN blocks new longs | open, +0.24R at last close |
| 2026-10-19 | LINKUSDT | DON | TREND_UP | allowed | open, +0.20R at last close |
| 2026-10-19 | LINKUSDT | DON_T | TREND_UP | allowed | open, +0.20R at last close |
| 2026-10-19 | THETAUSDT | DON | CHOP | blocked: regime=CHOP fakeout risk — all entries blocked | open, +0.70R at last close |
| 2026-10-19 | UNIUSDT | EMA50 | CHOP | blocked: regime=CHOP fakeout risk — all entries blocked | open, +0.11R at last close |
| 2026-10-20 | AAVEUSDT | DON | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | AAVEUSDT | DON_T | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | AAVEUSDT | EMA50 | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | ADAUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 18%) | open, +0.00R at last close |
| 2026-10-20 | ALGOUSDT | DON | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | ALGOUSDT | DON_T | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | ALGOUSDT | EMA50 | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | AVAXUSDT | DON | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | AVAXUSDT | DON_T | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | AVAXUSDT | EMA50 | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | BNBUSDT | EMA50 | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 34%) | open, +0.00R at last close |
| 2026-10-20 | BTCUSDT | EMA50 | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | CHZUSDT | DON | TREND_DOWN | blocked: regime=TREND_DOWN blocks new longs | open, +0.00R at last close |
| 2026-10-20 | COMPUSDT | DON | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | COMPUSDT | DON_T | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | COMPUSDT | EMA50 | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | ENJUSDT | DON | CHOP | blocked: regime=CHOP fakeout risk — all entries blocked | open, +0.00R at last close |
| 2026-10-20 | FILUSDT | DON | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | FILUSDT | DON_T | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | FILUSDT | EMA50 | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | GRTUSDT | DON | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | GRTUSDT | DON_T | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | HBARUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 14%) | open, +0.00R at last close |
| 2026-10-20 | LINKUSDT | DON | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | LINKUSDT | DON_T | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | LTCUSDT | EMA50 | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | MANAUSDT | DON | TREND_DOWN | blocked: regime=TREND_DOWN blocks new longs | open, +0.00R at last close |
| 2026-10-20 | RUNEUSDT | EMA50 | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | THETAUSDT | DON | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | THETAUSDT | DON_T | TREND_UP | allowed | open, +0.00R at last close |
| 2026-10-20 | UNIUSDT | EMA50 | CHOP | blocked: regime=CHOP fakeout risk — all entries blocked | open, +0.00R at last close |
| 2026-10-20 | VETUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 27%) | open, +0.00R at last close |
| 2026-10-20 | XLMUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 17%) | open, +0.00R at last close |
| 2026-10-20 | YFIUSDT | DON | RANGE | blocked: regime=RANGE blocks D long mid-range (pos 19%) | open, +0.00R at last close |
| 2026-10-20 | ZECUSDT | EMA50 | TREND_UP | allowed | open, +0.00R at last close |

## Reading

- Six primary long cells were pre-stated (3 rules x 2 exits); the headline is one of them. Gated and ungated are shown so the live regime gate's effect on bounce longs is visible.
- A bounce rule is a new strategy, not a tuning. Nothing here is registered, applied or shadowed; the operator's freeze on new registrations stands.
- Caveats as in the 2026-10-20 replay: spot bars, universe chosen 2026-09-16, 2.7 years = three or four regime phases, entry at the close.

_READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER_
