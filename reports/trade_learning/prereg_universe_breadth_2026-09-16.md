# Pre-registration — paper-bot universe breadth expansion (2026-09-16)

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER
Status: **DRAFT — awaiting operator approval. Nothing has been changed on the bot.**

## 1. The problem this addresses

The learning loop is starved, not broken. The paper bot scans 11 symbols and produces about one
entry-day every 5 days (24 distinct entry days over a 116-day span). The four rules applied on
2026-09-11 need 20 post-apply signals before the ledger can judge them, which is roughly 100
days at the current rate. Every later question queues behind that.

Signal count is the binding constraint. Nothing about the rules themselves is in question.

## 2. Hypothesis

Widening the symbol universe at **completely fixed rules** raises the rate of independent
observations, so the ledger reaches its decision thresholds sooner, without altering the edge
being measured.

This is a sample-size action, not a search. Precedent from this repo's own research:
`LESSON_S20_D1_001` and `LESSON_S21_D1_003` establish that universe breadth at fixed held-N is
a robust, non-tuning sample lever, and `LESSON_S21_D1_001` confirmed the mechanic on 48 fresh
names with zero overlap.

## 3. Universe — selected BEFORE this question was asked

To remove any chance that I picked names after seeing performance, the expansion draws from an
**already-frozen universe assembled on 2026-06-22 for a different, now-closed purpose**
(C23 low-vol / C24 illiquidity feasibility — both rejected):

`data/broad_crypto_universe_c23_c24/` — 42 Binance spot USDT pairs, 1d,
`api.binance.com/api/v3/klines`, write-once raw CSVs, **0 missing candles**, 0 exclusions.

**Correction found while drafting:** only **9** of the bot's 11 current symbols are inside
those 42. `ARBUSDT` and `OPUSDT` were added to the bot separately and are not in the frozen
universe. They are **kept**: dropping symbols the bot already trades would change the
experiment in a second way and break comparability with the frozen baseline.

**Pre-declared exclusions (data rules, never performance):**

| exclusion | reason | source |
|---|---|---|
| ICPUSDT | short history | flagged in the frozen `quality_report.json` |
| any symbol the live binance/kraken feeds cannot serve | operational, not a choice | verified and recorded before the run |

**Final universe: 43 names** = 11 current + 32 added, being the 42 frozen names minus ICPUSDT
(which is already among the 9 overlapping) plus ARBUSDT and OPUSDT.

Current 11 (unchanged): ADAUSDT ARBUSDT AVAXUSDT BNBUSDT BTCUSDT DOTUSDT ETHUSDT LINKUSDT
OPUSDT SOLUSDT XRPUSDT

The 32 added, fixed at approval, in full:

```
AAVEUSDT  ALGOUSDT  ATOMUSDT  BCHUSDT   CHZUSDT   COMPUSDT  CRVUSDT   DOGEUSDT
EGLDUSDT  ENJUSDT   EOSUSDT   ETCUSDT   FILUSDT   GRTUSDT   HBARUSDT  KAVAUSDT
LTCUSDT   MANAUSDT  MKRUSDT   NEARUSDT  RUNEUSDT  SANDUSDT  SNXUSDT   THETAUSDT
TRXUSDT   UNIUSDT   VETUSDT   XLMUSDT   XTZUSDT   YFIUSDT   ZECUSDT   ZILUSDT
```

No name is added or removed afterwards for any reason other than a feed outage, which is
logged. Breadth goes from 11 to 43, a 3.9x increase in scanned names.

## 4. What does NOT change

Everything except the symbol list. Explicitly: the 7 strategies and all their parameters, the
2×ATR stops, the 20-day timeout, `risk_pct`, the regime-control rules, the minimum expected-R
filter, the kill switch, the coordinator config, the four rules applied on 2026-09-11, and every
threshold in the hypothesis ledger (n≥20, p≥0.90 confirm, p≤0.50 reject, −0.2R rollback).

No parameter is tuned. No strategy is added or removed. Nothing is re-fitted.

## 5. Honest limits of the expected gain

Two structural facts cap the speedup, and I would rather state them now than explain them later:

1. **Position slots, not symbols, bound the rate.** The bot holds at most one open position per
   (exchange, strategy), so the ceiling is 13 concurrent positions regardless of universe size (7 strategies on
   binance, 6 on kraken since Exp G is binance-only).
   More symbols raise the probability a free slot gets filled; they do not multiply the rate
   linearly. Expect meaningfully faster, not 3.9x faster.
2. **Crypto majors are highly correlated.** 20 signals across 43 correlated names carry less
   independent information than 20 signals across 43 independent assets. This repo already has a
   contract for exactly this concern (Block 132, Cohort Independence / Correlation Penalty).
   The verdict must therefore be read with a correlation caveat, and clustered signals (same
   day, same direction, across correlated names) should be reported as such.

Neither limit invalidates the action — more samples is still strictly better than fewer at
fixed rules — but a faster verdict is not a stronger one.

## 6. Success and failure, declared now

This experiment is about **measurement rate**, not profit. It succeeds or fails on that alone.

- **Works:** post-expansion entry-day rate at least doubles (≤ 2.5 days per entry-day, from
  5.0), measured over the first 30 days, and the ledger reaches n ≥ 20 on the applied rules.
- **Does not work:** rate stays above 4 days per entry-day after 30 days. Then breadth was not
  the constraint, the slot cap was, and the honest next step is a slot-model question — not
  more symbols.
- **Invalidated:** if any rule, parameter, or gate is changed during the window, the window is
  void and restarts. Deviation voids the run.

**Nothing here is a claim about profitability.** Whether the applied rules help is decided by
the existing ledger thresholds, unchanged, and a faster clock does not lower that bar.

## 7. Evaluation

- Baseline, frozen now: 11 symbols, 5.0 days per entry-day, 24 entry-days over 116 days.
- First read: 30 days after the change lands.
- Read by: the existing loop. No new scoring code, no new thresholds.
- Recorded in: `brain_memory/projects/trading_bot/decisions.md` and the hypothesis ledger.

## 8. Safety

Paper only. No broker, no orders, no credentials, no live gates touched. The bot labels every
trade PAPER. `auto_upload_youtube` and every trading authorization remain untouched and off.
Live trading stays BLOCKED at the 6 gates.

## 9. Operator decision required

Approve, and I will: verify feed availability for each of the 43 names, write the final symbol
list into a run record, make the single symbol-list change, and record the baseline. Nothing
touches the bot before that approval.
