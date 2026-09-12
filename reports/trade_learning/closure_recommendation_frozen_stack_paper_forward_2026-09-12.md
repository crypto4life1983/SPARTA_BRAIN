# WITHDRAWN — closure recommendation, frozen_stack_paper_forward, 2026-09-12

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

**This file was generated in error and is withdrawn. Do not act on it.**

A scorer run on 2026-09-12 briefly marked `frozen_stack_paper_forward` as REJECTED and wrote a
closure recommendation. That verdict was wrong and was corrected the same day, before any human
decision was taken. Nothing was closed, and the line remains open.

## What went wrong

The out-of-sample split had been set to 2026-09-11 on the assumption that refreshing the
external 1m cache would produce rows dated from 2026-09-12 onward. It did not: the refresh
back-filled entries from 2026-04 to 2026-08 in a single pass, because the cache had been stuck
at 2026-03-31. When the split was corrected to that real data ceiling, the scorer then treated
the 165 calendar days spanned by that back-filled history as satisfying the line's
"60-90 day clean paper run" requirement, and rejected the line on **4 executed trades**.

Both readings were wrong in the same direction: they turned a tiny, brand-new sample into a
finished verdict.

## The correction (in `tools/paper_system_scorers.py`)

- `FROZEN_STACK_FORWARD_SPLIT = "2026-03-31"` identifies which rows are out-of-sample: entries
  after the old cache ceiling were never available to the bot under its locked parameters, so
  they are genuine evidence.
- `FROZEN_STACK_OPERATION_START = "2026-09-12"` is a separate clock for the clean-run gate,
  which measures days the bot has actually been running forward — currently 0.
- The two are reported separately and labelled, so a span of back-filled history can never
  again be read as run time.

The line's current status is **SHADOW**: 4 out-of-sample executed rows (sum −1.39R, negative
but far too thin to conclude anything), 0 days of clean forward running. It needs time, not a
verdict.

Superseded by `paper_systems_scorecard.{json,md}` from 2026-09-12 onward.
