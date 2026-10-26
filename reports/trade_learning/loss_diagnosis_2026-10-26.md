# Why the paper book is losing, and what was done about it — 2026-10-26

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

**Operator (2026-10-26, leaving for two days):** "find why, find a solution, apply it with my approval
now." This note is the answer. Short form: the loss is the system's own variance in a losing
phase, no entry rule in the bot's history separates the losers from the winners reliably, and the one
change applied is a shadow test of the single best-supported cell. Nothing in the live rules changed.

## 1. The thirteen trades (opened on or after the 2026-09-15 fix, closed by today)

| outcome | n | sum R | what happened |
|---|---|---|---|
| full stop-out (LOSS) | 7 | -7.2 | every one within 0.1R of the stop, 2 to 7 days after entry |
| 20-day TIMEOUT | 4 | -0.1 | TREND_UP longs that went nowhere; target never approached |
| WIN | 1 | +0.6 | ADA long, half banked at 1R, rest at breakeven |
| partial then stop | 1 | -0.3 | SOL long timeout at -0.33 |

Total -7.6R, mean -0.59R, 31% win rate. Split: 9 longs -3.5R, 4 shorts -4.2R; D -2.3, F -3.0, F2 -2.3;
TREND_UP -3.5 (9), RANGE -2.1 (2), TREND_DOWN -2.0 (2). No cell stands out: the loss is spread evenly
across strategy, direction, regime and exchange.

## 2. Is this inside what the system does on its own history?

On the replay of the bot's own code (42 symbols, 2024-01 to 2026-10-19, same exits), the rules make
+0.075R per trade with 42% stop-outs, 45% timeouts and 13% target wins. The edge comes from the 13%.
Thirteen trades with zero target wins happens 16% of the time at that base rate.

| 13-trade windows on the replay | share with sum <= -7.64R | share with at most one trade above +0.5R |
|---|---|---|
| dedup pool (2593 trades, chronological) | 25% | 33% |
| three-slot book model (406 trades) | 4.8% | 10% |

Worst 13-trade window in the replay: -13.4R (pool), -11.0R (book). The live run is unlucky, not
unprecedented: one in twenty for the book model, one in four for the pool. The bot-side study of
2026-10-20 found the same (22% of 12-signal windows at -6.6R or worse on its panel).

## 3. Does any entry-time cell separate losers from winners?

A pre-bounded scan of 28 cells on the 2,593 replay trades: six entry-bar feature buckets (body,
ATR expansion, volume, range position, EMA20 distance, EMA200 side) plus strategy, direction and
regime. Bar to count: the cell's mean differs from the rest with bootstrap p >= 0.9982 (Bonferroni,
28 cells) AND the same sign in every half-year with >= 20 trades.

**Nothing passes.** Every cell flips sign in at least one half-year. The post-fix half-year is the
worst for almost all of them, which is what a phase looks like and what a filter does not fix.

Closest: signal-bar volume >= 1.5x its 20-day mean. Kept trades +0.145R (n=1103) vs the rest +0.023R
(n=1490), difference +0.121R per trade, p=0.996; positive in all four full half-years (+0.29, +0.14,
+0.10, +0.04) and -0.08 post-fix (n=76). Short of the bar on both counts. Strategy E (+0.295R, n=124,
positive every period) is live and fires about once a week.

## 4. What was applied, under the operator's blanket approval

1. **Shadow hypothesis `blockwhere__volume_bucket=low|normal`** registered in the ledger with the
   replay evidence above frozen at registration (label REPLAY_PRIOR_ONLY). It is scored forward on the
   paper bot's own closes and resolves at n >= 20 with p >= 0.9, like every other hypothesis. By the
   ledger's convention the prior is -0.023R per blocked trade (those trades were roughly flat on
   history, not losers); the uplift is per-trade selection, which matters for a slot-limited book.
   A CONFIRMED result is a recommendation to the operator, not a switch.
2. **Bot-side entry-feature patch applied** (working tree, uncommitted): the bot now writes
   range_pct, atr_expansion, volume_ratio, range_position, donchian_width_pct, ema20_dist_atr and
   ema200_dist_atr into the SPARTA context log at every open. Without it the shadow test above
   cannot score. Smoke-tested; the bot repo's own pytest and the commit remain the operator's block.
3. Ledger and replay prior now accept list-valued cells ("a|b" = any of); 5 tests.

**Not applied, deliberately:** the volume filter live, any direction block, any timeout or exit
change, stopping the book. Reasons: the evidence does not meet the pre-stated bar; a live change now
would contaminate the rollback check on the five applied rules, which is 7 trades away; and the book
is paper, so the loss costs evidence, not money. The replay says the system has losing half-years of
this size and recovers from them; it does not say when.

## 5. What happens next without anyone present

- Nightly: the bot runs with three slots, writes features, the loop scores every hypothesis.
- At n >= 20 post-fix closes (about two weeks): the rollback flag on the five applied rules fires if
  the mean is still below zero, and `spec_rollback_procedure_2026-10-18.md` says what to do per rule.
- The new shadow hypothesis and the shadow pair in the bot repo accrue on their own.
- Operator on return: run the bot-repo block (features + slots commit), then read `/trade-loop`.

_READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER_
