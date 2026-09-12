# s21 weekly RS paper — refresh done, run BLOCKED by a corporate action

Date: 2026-09-12 · Operator instruction: run the s21 line, which the scorer reported as `NO_DATA` (harness built 2026-09-10, never run).

**Outcome: the data refresh succeeded and the cycle was NOT run. A member of the locked 48 universe has been delisted, and the harness is correct to refuse. Resolving it is a strategy-level decision for the operator, not a code fix.**

## What was done

The harness reads operator-supplied local split-only CSVs and never fetches. Its default source `refreshed_20260528` ends 2026-05-28, so a cycle today would have been 15 weeks stale and its own checklist §1 says do not run. A refresh was therefore required first.

New tool `tools/s21_tiingo_split_only_refresh_once.py` pulls the locked 48 symbols from Tiingo's official API into a new dated directory, never overwriting the read-only sealed baseline, and verifies the result against that baseline before anything downstream can use it.

Source: `data/s21_weekly_rs_paper_refresh_20260911/raw`, 48 symbols, 1,934 bars, 2019-01-02 → 2026-09-11.

### A first attempt was rejected and kept

The initial fetch wrote Tiingo's raw open/high/low/close, which are **unadjusted** traded prices. The harness needs split-only. Verification caught it: six symbols diverged from the sealed baseline, each an unapplied split (NOW 5:1 — raw 178.32 vs sealed 35.664 on 2019-01-02). The fetcher now divides every bar by the product of each split factor occurring after it. The bad fetch is retained under `data/_rejected_fetches/s21_refresh_20260911_RAW_UNADJUSTED_REJECTED/` with a rejection note, per the standing no-deletion rule.

## Verification against the sealed baseline

The checklist §2 requires the new source to reproduce `sealed_baseline_20251230` on the overlap for 47 of 48 symbols, BKNG excepted for its 25:1 split on 2026-04-06.

| Result | |
|---|---|
| Exact agreement (0.0 bps worst case) | **46** of 48 |
| Expected difference | BKNG, 25:1 split, as documented |
| **Unexpected difference** | **RTX** |
| Rule `47/48` | **not met (46)** |

**RTX** differs on 316 bars, all of them on or before 2020-04-02, by a constant factor of 1.589. That is the United Technologies / Raytheon merger conversion of April 2020. The sealed baseline applied the merger ratio; Tiingo's `splitFactor` does not encode merger conversions, so split-only history alone cannot reproduce it. Both series are internally consistent under different conventions, and every bar from 2020-04-03 onward agrees exactly. It does not affect a 2026 signal unless the RS lookback reaches back six years, but it does mean the checklist's 47/48 rule is not satisfied as written.

## The blocker: EA has been delisted

`EA` stops on **2026-08-04**, 27 trading days before every other symbol.

| EA final bars | Close | Volume |
|---|---|---|
| 2026-07-31 | 209.86 | 4,852,325 |
| 2026-08-03 | 209.91 | 4,470,382 |
| **2026-08-04** | **209.70** | **48,713,697** |

Prior 20-day average volume: 2,238,864. The final session traded **22x** normal volume with the price pinned near 209.70. That is an acquisition closing, not a data gap.

This never surfaced before because the previous source ends 2026-05-28, three months before the event.

The harness loader raises `CALENDAR_MISALIGNMENT` and halts. **That is the correct behaviour.** A locked universe with a dead member cannot be rebalanced into.

## Why this was not worked around

Three fixes were available and all were declined, because each would be a strategy change made by the wrong party:

1. **Drop EA from the universe.** The 48 names are locked in `manifest.py` as the set that earned the research verdict. Changing membership mid-test changes the strategy.
2. **Forward-fill EA after 2026-08-04.** That fabricates prices for a security that does not trade.
3. **Relax the calendar-alignment check.** That disables the guard that caught this.

The manifest was also not edited to register the new source, for the same reason: the checklist §2 says a refresh "adds a new `DATA_SOURCES` entry + bumps `DEFAULT_DATA_SOURCE`... That edits code → do not do it under this checklist alone." The new source is on disk and verified; wiring it in is a separate operator decision.

## What the operator has to decide

1. **EA.** Options: retire the name and rebalance into the remaining 47 (a universe change, needs a recorded decision and arguably invalidates comparability with the sealed research); hold EA's final cash value as a frozen position; or accept that the locked universe has expired and treat 2026-08-04 as the natural end of the s21 paper window.
2. **RTX.** Accept the split-only convention and record that the 47/48 rule now reads 46/48 for a documented merger reason, or re-derive the merger factor and apply it so the baseline reproduces.
3. **Whether a replayed window counts.** Even once the above are settled, 15 missed weekly anchors would be replayed bar-by-bar rather than lived forward. `LESSON_S21_PAPER_002` permits bar-by-bar replay and forbids the single catch-up cycle that produced the discredited "+73.7% week". Any result should be labelled a replayed out-of-sample window, not lived-forward paper.

## Status

- Refresh: **done and verified**, 46/48 exact, two differences both explained.
- Cycle run: **not attempted**. `s21_weekly_rs_paper` stays `NO_DATA` in the scorer.
- No strategy parameter, universe member, manifest entry, or guard was changed.
