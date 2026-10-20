# Replay of the paper bot's rules and four pre-stated variants — 2026-10-20

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

**Question asked by the operator:** "what do you suggest to fix the loss, and can you prove it with a backtest?"

**Short answer.** No. A backtest can show what a rule did on the past; it cannot prove it will work
next month, and on this history none of the four candidate changes fixes the current loss. Every
variant loses on the post-fix window just as the live rules do. What the replay does show is why
the bot is losing now, what its rules have historically been worth, and which ideas are not worth
pursuing. Those are below, with the numbers.

## Method

`tools/replay_bot_rules.py` imports the bot's own code and re-runs it bar by bar: 
`scripts.live_signals.compute_indicators`, `detect_signal_d/e/f/f2` (F2 via D2/E2),
`scripts.regime_detector.detect_regime`, `scripts.regime_control.is_signal_allowed`, and `_bar_hit`
for fills. Exits are re-implemented in `sim_de` / `sim_f` with the rules live since 2026-10-14
(half off at 1R + breakeven for D/E; ladder 40/40/20 at 1.618/2.618/4.236R with breakeven after the
first rung for F/F2; 20-day timeout; stop wins over target in the same bar; gap-honest fills).
**`tests/test_replay_bot_rules.py` feeds 360 random price paths through both the simulators and the
bot's real `manage_de` / `manage_f` and requires the same outcome and the same R to 0.002.** All pass.

Data: Binance spot daily bars, 1000 per symbol (2024-01-25 .. 2026-10-19), the current 42-symbol
universe, 290 bars warm-up, entry at the signal bar's close (what `build_trade` records), 0.1% fee per
side, risk 1R per trade. Strategies: D, E, F, F2 — the ones the allocation currently lets trade
(D2, E2, G are quarantined). Regime gate applied exactly as live.

Three ways of counting the same signals:
- **pool**: every allowed signal (consecutive breakout days overlap; measures the signal, not a book);
- **dedup**: one trade per (symbol, strategy) at a time — the fair per-trade number;
- **one slot**: the bot's reality on one exchange: one position per strategy, first signal of the
  day in config order wins.

Windows: **IS** = signals before 2026-09-15 (the partial-bar fix), **OOS** = 2026-09-15 onward, the
same window the live journal counts as admissible evidence. Four variants were fixed before the run
and none was searched: `longs_only`, `confirm` (the bot's own `_evaluate_breakout_confirmation`
gate on Donchian entries), `f_rung_1r` (first F rung at 1.0R), `timeout_40`.

**Caveats that bound every number.** Spot bars, not the bot's feed. The universe was chosen on
2026-09-16, so earlier results carry selection bias. Two and a half years is three or four regime
phases, not a sample of regimes. Entry-at-close is what the paper bot books, not what a live fill
would get. The replay matched the live journal's post-fix entries where they can be compared (XRP
short 09-15, OP long 10-13, ENJ short 10-18, CHZ E short 10-16); the journal holds slots on two
exchanges, the replay on one.

## 1. What the current rules are worth on this history (dedup)

| window | n | sum R | mean R | win | p(mean>0) |
|---|---|---|---|---|---|
| all | 2593 | +194.0 | +0.075 | 0.49 | 0.999 |
| IS | 2486 | +210.7 | +0.085 | 0.50 | 1.000 |
| OOS (post-fix) | 107 | -16.7 | -0.156 | 0.39 | 0.076 |

By half-year: +0.216 (2024-11..25-05), **-0.118** (2025-05..11), +0.103 (2025-11..26-05), +0.255
(2026-05..09), **-0.156** (post-fix). The rules have a small positive expectancy over the whole
window and swing by a tenth of an R per trade from one half-year to the next. The current phase is
the second losing phase in the window; the first lasted six months.

What the one-slot bot captures of that pool (binance only, one position per strategy AND the
coordinator's one position per symbol, see the correction in section 4): n=152 over the whole
window, +23.0R, mean +0.151R, p=0.94, about 1.1 trades a week. With three slots per strategy
(the 2026-10-20 config change) the same model takes 406 trades, +47.4R, mean +0.117R, 3.0 a
week: 2.7x the evidence at a slightly lower per-trade mean. Post-fix the one-slot model took 7
closed trades for -3.2R. **This is the realistic expectation of the bot as built: a small positive
drift with losing half-years that look exactly like now.**

## 2. Why it is losing now

| OOS, dedup | n | sum R | mean R |
|---|---|---|---|
| longs | 89 | +0.8 | +0.009 |
| shorts | 18 | -17.6 | -0.98 |

Every post-fix short lost; longs were flat. That is the whole loss. It is not the exits (every loss
closes within 0.1R of the stop) and it is not a new defect: shorts also lost for six months in
2025 (-0.197R per D short, n=256) and then made money for the next year. Shorts are the better side
over the full window (+0.084 vs +0.055 per trade).

## 3. The four variants

| variant (dedup) | all mean | IS mean | OOS mean | verdict |
|---|---|---|---|---|
| baseline | +0.075 | +0.085 | -0.156 | — |
| longs_only | +0.041 | +0.045 | +0.009 | **worse on history**; only looks good in the last 5 weeks |
| confirm | +0.112 | +0.125 | -0.139 | better in-sample, no help OOS; see below |
| f_rung_1r | +0.062 | +0.068 | -0.082 | paired on the same F signals: -0.010R/trade IS (n=3796, p=0.06), +0.066 OOS (n=162) |
| timeout_40 | paired on the same signals: **-0.015R/trade, p=0.009 against** (n=5598); OOS -0.106 | | | **worse**; keep 20 days |

`confirm` removes a set of trades whose mean is -0.058R (n=2279, p=0.005) over the whole window,
which is real in-sample. But by half-year the removed set is **positive** in the two bull phases
(+0.118, +0.226) and negative in the two others (-0.277, -0.097). It filters out losers in sideways
and bear phases and winners in bull phases. That is regime dependence, not a filter. Shadow-worthy,
not apply-worthy.

`timeout_40` is the replay's clearest negative: holding the same trades to 40 days instead of 20
costs 0.015R per trade with p=0.009 on 5598 signals. The ledger's `extend_timeout__40` is scored
forward on the bot's own timeouts and will answer on its own; this is the in-sample prior.

## 4. Two facts about the design that no parameter changes

**D, F and F2 are one entry with three exits, but the live book takes only one of them.**
F fired on the same bar as D in 1541 of 1665 F signals (93%); F2 in 1541 of 2327 (66%), and the
three exits are equivalent on history (D +0.047, F +0.080, F2 +0.064 per dedup trade). The first
version of this report said the journal holds every such entry three times; that was wrong and is
corrected here (same day). The bot's coordinator enforces one open position per symbol
(`config/trade_coordinator_config.json`, `max_open_trades_per_symbol: 1`; 119 `COORDINATOR BLOCKED
... duplicate_symbol_exposure` lines in the bot log), so when D opens XRP, F and F2 are refused on
XRP. The pool numbers above count the three strategies separately; the one-slot model now includes
the per-symbol lock. Consequence for the loop: the "free paired exit experiment" does not exist in
the live journal (tools/trade_exit_pairs.py finds no D/F pairs post-fix), only in the replay.

**One slot per strategy makes the book a near-random draw from the pool.** The slot takes the first
symbol in config order and then sits in it for up to 20 days while the pool produces 15 allowed
signals a week. The one-slot result (+0.061/trade, p=0.74) is noisier than the pool (+0.075,
p=0.999) for that reason. More slots means more of the pool; the pool's edge is still +0.075R.

## 5. The one post-hoc observation worth a shadow hypothesis later

E-based short entries (EMA20/50 cross-down below EMA200): +0.317R (n=60), +1.30R (n=12), +0.81R
(n=47) in the last three half-years, -0.33R (n=8) in the first. E longs are negative in three of
four. This is a post-hoc cut (8 base × direction cells over 5 periods, examined after the
aggregate), so it is exactly what the ledger exists to test forward and exactly what must not be
applied on sight. E is already live and fires about once a week across the universe; the operator's
"register nothing more" freeze stands, so this is noted here and nothing is registered.

## 6. What this supports, and what it does not

- **Supported:** the current rules have a small positive historical expectancy; the present loss is
  a shorts-fail phase like 2025's, not a defect; 20-day timeout beats 40; no direction block; the F
  ladder stays; the confirm gate is regime-dependent.
- **Not supported:** any rule change that "fixes the loss". None of the four candidates is positive
  on the post-fix window, and the two that look better on history (confirm, timeout) split the
  wrong way by period or by pairing.
- **Not a strategy question:** the 3× exposure from D/F/F2 and the one-slot draw. Both are about
  how much of each outcome the bot takes, not whether the outcome is good.

## 7. Cross-check against the bot-side study of the same day (added 2026-10-20, later)

A separate session working in the bot repo answered the same question on a different panel
(`reports/exit_structure_study_2026-10-11.md` Part 4: 3,656 D/E signals over six years, gross R,
uncommitted in that repo). The two studies agree on the main points without having seen each other:
no fault to fix; the loss is correlated variance across symbols (there, 22% of 12-signal windows sum
to -6.6R or worse against 1.3% if trades were independent); long-only fails out of sample; no live
change.

They disagree on one candidate. That study finds that skipping entries whose signal bar is a full
body (body >= 0.805 of range) adds +0.046R per signal with a 95% CI of [+0.011, +0.081], and that
filter is already the pre-registered shadow pair `cand_2326d78c832e` / `cand_4568eae650d3`
(2026-10-14). The same filter on this replay's 2,593 dedup trades (signal-bar body from the same
daily bars):

| 42-symbol replay, dedup | n | mean R |
|---|---|---|
| kept (body <= 0.805) | 2015 | +0.071 |
| removed (full body) | 578 | +0.088 |
| kept minus all, bootstrap 5–95% | | -0.004 [-0.059, +0.051] |

Here the filter removes trades that did slightly *better*, and the removed set is positive in three
of five half-years; full-body shorts are the single best cell in the panel (+0.183R, n=341). So the
full-body effect does not replicate on the wider, shorter panel. Both findings are in-sample on
different data, which is exactly the situation the shadow pair exists to settle. Reading: the filter
belongs in the shadow book, where it is, and this result is a reason **not** to lower its promotion
bar. A pre-registered promotion criterion for the pair is reasonable; it should be no looser than the
ledger's own (n >= 20 closed pairs, p >= 0.9 on the paired difference).

**Resolution (same day, after exchanging results with the bot-side session).** Restricted to this
replay's window (2024-01-25 onward) the other panel's kept-minus-all is +0.036R with a block-bootstrap
95% CI of [-0.020, +0.078], no longer excluding zero; its full-body shorts are -0.024R (n=168) against
+0.183R here, a sign disagreement on that cell. Its +0.046 headline rests on 2021-2023. Construction
differences named there: ungated D/E, 2R partial, gross R versus regime-gated D/E/F/F2, 1R partial,
net. Decision taken (operator delegated it): no live change; the filter stays in the shadow pair; a
**pre-registered promotion criterion** is written in that study's Part 4 and accepted as-is. It is
stricter than the bar proposed above in two ways: at least 10 closed divergence episodes on top of
20 closed baseline trades (identical trades contribute zero, so without the episode floor a handful
of skipped losers would pass), and an evidence window strictly after 2026-10-14. A pass is a
recommendation to the operator, never a switch; a fail closes the question and the pair is not
re-registered with a new threshold. Counts at the time of writing: 7 shadow trades per candidate,
0 closed, one divergence (ZIL).

Nothing in the bot was changed. Nothing was registered. Outputs: `reports/trade_learning/replay_2026-10-20/report.json`
(all tables), `progress.log`; `signals.json` (every signal with its three simulated exits) is written
there too and left uncommitted for size.
