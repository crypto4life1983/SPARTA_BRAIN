# s17-d1 broad-universe cross-sectional momentum — P4 synthetic smoke (sealed)

**Authored (UTC):** `2026-05-29T01:00:42.352338Z` · **report_seal:** `e39e140c231b3052a856aaafd2cc9b80db1d5766ed6babc192dc8d8a4178de6c`
**Verdict: `P4_SYNTHETIC_SMOKE_PASS`** — 23 passed / 0 failed (pytest rc=0)

Synthetic fixture + invariant tests only — NO real-CSV read, NO signal computation on real data, NO backtest.
Verified: momentum primitives (126-21 / rank / top-M / equal-weight / rotation / cost), guard pass+drift detection,
**K13 fold-scheme-locked (exact DA22 boundaries, contiguous, unsearched) + verdict gate + no per-fold refit**,
driver stubs refuse execution (P6_IS / P6_7_K13 / P10_OOS NOT_AUTHORIZED), OOS isolation, end-to-end synthetic
rotation invariants (never > M held; closed trades only on rotation exit; equal-weight targets).

Anchors: P3 BUILD affbcb0 / SEAL 767d86b / P1 4484ab6 / P2 894da78. Bound by DR10 v2 + walk-forward K13.

## Status
trading PAUSED · live BLOCKED_AT_6_GATES · FRC NEVER_GRANTED · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE. lessons.md NOT touched.

## Next
`Authorize s17-d1 broad-universe cross-sectional momentum P6 IS diagnostic only.`
