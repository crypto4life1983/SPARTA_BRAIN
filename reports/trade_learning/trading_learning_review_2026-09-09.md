# Trading Learning Review — 2026-09-09

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

Scope: every trading system that has produced trades or paper trades in the last year, what each one has taught, and what should change. Numbers come straight from the journal database, the paper trackers, and the research ledgers. Nothing here is applied automatically.

## 1. What is actually trading

| System | Where | Mode | Since | Result to date |
|---|---|---|---|---|
| Daily bot D/E/F/G on 11 crypto pairs | obsidian-trade-logger `trades.db` | PAPER, $20/trade, Binance + Kraken prices | 2026-04-28 | 41 closed rows, 30 distinct signals, +8.9R dedup (+$309 raw) |
| Perp funding carry, always-on monthly | `reports/paper_funding_carry` | paper $10k | 2026-05-13 | +$49.4 (+0.49%) in 120 days, costs ate 36% of funding, max DD 0.17% |
| NQ opening-range (MNQ) | `reports/nq_paper_orb` | paper $50k | 2026-05-13 | 52 trades, net −$2,172, DD −6.9% |
| GC ICT (MGC) | `reports/gc_paper_ict` | paper $50k | 2026-06-14 | 0 trades in 40 sessions, tracker PAUSE |
| Frozen stack breakout + BB snapback (BTC/ETH/XRP 1D) | `final_stack_paper_trades.csv` | backfill 2020-02 → 2025-10 | — | +39.7R / 62 and +36.8R / 70; no forward rows since 2025-10, regime COMPRESSED_DORMANT |
| s21 weekly RS rotation (equities) | `paper_trading/weekly_rs_s21_*` | paper $100k | 2025-12-30 | 2 cycles only; +73.7% is a 20-week catch-up hold mislabelled as one weekly cycle, not evidence |
| C22 Signum TrendRadar GC | SPARTA research lane | frozen data | 2026-06-20 | 81 windows; replay never built; closure recommended on feasibility |

## 2. What the real trades teach (journal, 41 closed rows)

Sample is small. 30 distinct signals, 2 to 11 closed per strategy. Everything below is PRELIMINARY.

**Regime alignment is the whole game.**

| Bucket | n | sum R | avg R | win |
|---|---|---|---|---|
| RANGE short | 4 | +9.73 | +2.43 | 100% |
| TREND_UP long | 4 | +6.29 | +1.57 | 75% |
| TREND_DOWN short | 17 | +5.45 | +0.32 | 47% |
| RANGE long | 5 | −0.44 | −0.09 | 20% |
| TREND_DOWN long (counter) | 4 | −1.35 | −0.34 | 25% |
| unlabeled (April, before regime tagging) | 5 | −5.42 | −1.08 | 20% |

Aligned trades: +11.7R over 21. Counter-trend: −1.4R over 4. Every G "Range Reversion" long on XRP in a downtrend lost. The regime control already blocks longs in TREND_DOWN, so those four came from before it was on or through the fail-open path. Keep it on, and make unknown regime block instead of allow.

**Strict variants beat loose variants, decisively.**

| Strategy | n | sum R | avg R |
|---|---|---|---|
| E (EMA cross) | 2 | +6.96 | +3.48 |
| F (Fibonacci) | 3 | +7.72 | +2.57 |
| D (Donchian) | 6 | +6.85 | +1.14 |
| E2 | 2 | +6.37 | +3.18 |
| F2 | 10 | −1.08 | −0.11 |
| G | 7 | −2.13 | −0.30 |
| D2 | 11 | −9.23 | −0.84 |

D2 is the single biggest drain and it is also the only breakout variant the regime control allows in TREND_DOWN. That rule should be inverted: allow strict D/E/F in TREND_DOWN shorts, and put D2 on watch. The strategy killer needs 20 closed trades per strategy before it acts, so on its own it will not touch D2 until roughly next spring.

**One trade broke the risk model.** Trade 46, XRP short on 2026-08-06, planned stop 1.0966, closed at 1.2871: −4.63R against a −1R plan. Six other losses closed between −1.3R and −1.6R. Excess loss beyond plan totals about 5.7R, which is two thirds of the whole dedup profit. Cause is either daily-bar stop checking with gap fills or the stop not being honoured. This is the highest-value fix in the system.

**Winners give back a third of their peak.** On the 10 closed trades with excursion data that reached 1R, mean peak was 2.98R and mean realized 1.79R. Three trades that reached 2.3R to 3.3R closed at 0.6R to 1.1R. A partial take at 2R or a trailing stop after 2R would have kept more without changing entries.

**Timeouts are the profit engine.** 20 timeout closes produced +32.3R; 19 stop losses cost −23.3R; only 2 trades ever hit target. TP1 at 3R and 5R is rarely reached on a 20-day daily-bar horizon. Targets should be nearer or replaced by trailing exits.

**Duplication inflates the sample.** Same signal on Binance and Kraken, and loose plus strict variant on the same bar, means 41 rows are 30 signals. Any statistic that does not dedup overstates confidence.

**Friday** entries: 8 trades, 0 wins, −12.9R. Sunday: 7 trades, +12.7R. Too few to act on; worth watching, not a rule.

## 3. What the paper systems teach

- **Funding carry works exactly as the research predicted: real, tiny, cost-bound.** 120 days of always-on carry earned 1.0% of capital gross and kept 0.49% after fees. That is about 1.5% a year. It is the only line that is positive, forward, and running today.
- **NQ opening range is negative forward** after 52 trades and 80 days. The tracker still says ON-TRACK because drawdown is inside its gate, but the sign is wrong. Give it its full pre-registered window, then close it honestly if the sign does not flip.
- **GC ICT never fired** in 40 sessions. The filter set (L2/mid/R3 with HTF trend EMA 50/200) is too tight for the current regime. It is not learning anything while it fires nothing.
- **The frozen breakout stack is a backtest, not forward paper.** Its last trade exited 2025-10-25. Its 0.5 to 0.6R per trade over five years is the most consistent thing in the whole ledger, but it has not been allowed to trade forward. The daily job appends zero rows because the regime detector calls the market dormant.

## 4. Is the system learning?

Honestly: it measures, it does not yet adapt.

- The journal side has a strategy killer, regime control, evidence gate, and a go/no-go evaluator. All are gated on sample sizes of 15 to 30 per strategy. With 2 to 11 closed trades per strategy after four months, none has triggered. The learning loop exists but has not closed once.
- The SPARTA side only reads the journal and writes observation snapshots. Until today nothing turned those snapshots into rule suggestions.
- The research side learned a great deal about what does not work. Twenty-six candidates were rejected honestly. That protected capital. It did not add income.

## 5. Concrete changes proposed (none applied)

1. Stop discipline first: reproduce trade 46's fill, then enforce intraday stop checks or a hard −1.5R kill on the bot. This alone recovers more R than any entry change.
2. Regime control: block on unknown regime instead of fail-open; in TREND_DOWN allow D/E/F shorts, not only D2/E2/F2; keep G longs out of TREND_DOWN.
3. Exits: partial take-profit at 2R and trail the remainder; drop 5R targets on daily bars.
4. Sizing and sample: one exchange per signal, or count the pair as one trade in every statistic.
5. Watch D2 explicitly. Lower the killer's per-strategy minimum to 12 for WATCH status only, not for KILL.
6. Keep funding carry running. It is the one positive forward line.
7. Let NQ ORB finish its window and then decide by its own gate. Loosen GC ICT filters or retire it.
8. Re-run the s21 paper harness weekly on refreshed data after the driver fixes already listed in the trading lessons file.

## 6. What "other ways for profit" looks like from this evidence

The ledger points to three things, all modest:

- Trend-aligned strict breakouts and crosses on daily crypto bars, with better exits and honoured stops. Current evidence: about +0.5R per signal on 30 signals, which is not proof.
- Funding carry as a low-volatility base, roughly 1 to 2% a year on the capital committed.
- The frozen breakout stack, if allowed to trade forward instead of sitting dormant.

Nothing in the evidence supports a fast or large edge. The realistic path is the boring one: fix the leaks in the system that already trades, let sample sizes grow, and let the gates that already exist do their job.

## Addendum 2026-09-10 — trade 46 forensic and rule what-if

**Trade 46 (XRPUSDT D2 short, opened 2026-08-06, closed −4.63R).** The bot log shows it evaluated the exit every day at 01:00 on the daily close only (`sl_hit = close >= sl` for shorts). On 2026-08-20 the close was 1.0962 against a stop of 1.0966, four hundredths of a cent short of triggering. On 2026-08-21 XRP closed at 1.2871, a 17.6% move in one session, and on 08-22 at 1.565. The stop was honoured exactly as coded; the code only looks once a day at the close. With a 2×ATR stop of about 5%, a 17% daily move produces −4.6R by construction. This is gap risk from close-only stop checks, not a fill error. It is paper, so no money was lost. The fix for any live version is a resting stop order on the exchange, or at minimum an intraday high/low check; the fix for paper accounting is to mark the stop at the first bar whose high/low crosses it.

**What-if replay of the proposed rules on the 30 dedup signals** (in-sample, post-hoc, small; direction of effect only):

| Step | signals | sum R |
|---|---|---|
| Baseline, dedup | 30 | +8.9 |
| Regime fail-closed (drop counter-trend and unlabeled) | 24 | +11.5 |
| Plus hard stop cap at −1.5R | 24 | +14.6 |
| Plus D2 on watch (keep only where a strict D/E/F twin fired) | 16 | +16.9 |

Each rule moves in the expected direction. None of these numbers is a forecast; they are the same trades re-scored, which is the definition of overfitting if taken as a result. They justify testing the rules forward on the paper bot, nothing more.
