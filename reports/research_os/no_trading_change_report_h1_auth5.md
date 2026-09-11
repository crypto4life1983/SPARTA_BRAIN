# SPARTA Research OS — H1-Auth-5 / No-Trading-Change Report

**Generated:** 2026-09-11 (UTC)
**Mode:** `ADVISORY_ONLY` — research-only, standalone lab
**Gate:** H1-Auth-5 — the ONE PRIMARY run of the multi-symbol perpetual
funding-carry engine (BTC/ETH/SOL, Binance USD-M, delta-neutral
long-spot / short-perp, equal initial USD notional, no leverage).
**Authorization (verbatim record):** on 2026-09-10 the operator (Mahmoud)
was told "The H1 funding-carry runner still needs your verbatim
H1-Auth-5 instruction" and replied "yes please do". Treated as the
H1-Auth-5 instruction: build the runner and execute the SINGLE PRIMARY
run exactly as preregistered; no second run, no parameter changes, no
re-tuning; any failed pre-flight check = ABORT before the PRIMARY.
**Outcome:** **ABORTED at pre-flight (GI-1) — honest negative. The
PRIMARY simulation was never executed; no metric of any kind exists.**

## What this event did

Built `run_h1_auth5_simulation.py` (modelled on the G2-Auth-5 runner;
the locked engine is imported unchanged) with a fail-closed pre-flight
(P1 sha re-verification of all 15 pinned files, P2 single-run guard,
P3 engine sha, P4 `validate_inputs`, **P4b funding-row `markPrice`
numeric on every in-window stamp**, P5 reproducibility anchors, P6 the
blocking cash reconcile), the S1–S8 / tripwire / GI-GE-GR evaluation
and per-window / per-symbol × year reporting, plus 38 synthetic-fixture
runner tests (46 in `tests/` with the tools tests). Verified every pinned dataset sha256 first (15/15 match,
manifest `206a1b2c…2af6e`). Then invoked the runner.

```
C:\SPARTA_RESEARCH_LAB\h1_perp_funding\
  run_h1_auth5_simulation.py                 (runner; engine untouched)
  tests\test_run_h1_auth5_runner.py          (38 tests)
  reports\auth5\abort_record.json            (stage P4b_funding_markprice_GI1)
  reports\auth5\run_record.json              (shas, params, authorization, attempt history)
  reports\auth5\verdict.md                   (ABORTED)
  reports\auth5\no_trading_change_note.md
  reports\auth5\h1_auth5_abort_analysis.md   (diagnosis, attempt history)
  reports\auth5\preflight_attempt_00{1,2,3}_*\   (preserved earlier attempts)
NEW (SPARTA_BRAIN):
  reports\research_os\no_trading_change_report_h1_auth5.md   (this file)
```

## Result

```
ABORTED  stage=P4b_funding_markprice_GI1   (pre-flight; PRIMARY not called)
sha256   15/15 pinned datasets match; engine sha 388ecb6d…14f7 unchanged
tests    94/94 pass (48 engine + 46 runner/tools), exit 0
```

**The data fact.** In the sha-pinned H1-Auth-1 funding-rate files the
`markPrice` field is an empty string on **every row before
2023-10-31** — in the shared window that is **3,427 (BTC), 3,427 (ETH)
and 3,502 (SOL) stamps**, roughly the first 3.1 of the 5.67 years.
Accounting-model rule 7 accrues `funding_rate × q_s × markPrice_{s,t}`
from exactly this field, and the locked engine parses it
unconditionally (`_funding_by_stamp`). H1-Auth-1's integrity
validation and the engine's `validate_inputs` both checked
`fundingRate` numeric but never `markPrice`, so the gap surfaced only
at first execution. Under the locked criteria this is **GI-1
(reconcile-input series unusable)** — a pre-flight abort, an honest
negative for this PRIMARY, unrescuable in place.

## Attempt history (fully disclosed; zero metrics produced by any)

| attempt | date (UTC) | what happened | PRIMARY executed |
| --- | --- | --- | --- |
| 001 | 2026-09-10 23:18 | prior session; aborted at P5 because the runner's own window-start anchor used the pre-skip raw time (2020-09-13T16:00Z) while the engine's locked complete-triplet window starts 2020-09-14T00:00Z (6212 stamps, exactly the H1-Auth-4 record) — a runner transcription error, corrected runner-side | no |
| 002 | 2026-09-10 23:20 | prior session re-invoked; wrote only the pre-exec snapshot, then was killed by an API rate limit; no output | unknown, no output |
| 003 | 2026-09-11 13:0x | this session; P1–P5 passed, `simulate_primary` raised `ValueError(float(''))` at its first parse of the funding series, before any ledger line; bare traceback preserved | entered, zero accounting |
| 004 (record) | 2026-09-11 13:10 | runner with P4b + exception-to-abort; **ABORTED at P4b before calling the engine**; this is the record of the gate | no |

The engine is deterministic and pure (writes nothing), so no attempt
could have produced a different number from any other; nothing was
tuned, no threshold moved, no window or symbol changed.

## Honest framing (no-hype, carried forward)

This is **not** an edge result in either direction. The pre-committed
prior ("net carry thin and may well be ≤ 0; FAIL likely and
acceptable") remains untested. What is established: the pinned
snapshot cannot feed the locked accounting rule as written. Two facts
are recorded read-only for any future *separate* decision, without
recommendation: (1) the pinned `markPriceKlines-8h` series covers
every one of the 6,212 shared buckets for all three symbols; (2)
funding rows from 2023-10-31 onward do carry a numeric `markPrice`.
Using either as a mark-price source would change the locked engine
and the accounting model's rule 7 and therefore requires an explicit
re-locked amendment gate (G1-Auth-4A precedent) followed by a fresh
run authorization — it was **not** done here.

## What this event did NOT do

- Did **NOT** produce any research result, metric, v2 record, live
  signal, or paper-arena artifact; **NOT** run anti_overfit /
  regime_score / robustness_audit / lifecycle.
- Did **NOT** fetch data, touch the network, or use API keys or
  credentials; **NOT** modify any pinned data file (15/15 sha match
  after the run).
- Did **NOT** modify the locked engine or any locked H1-Auth-2 document
  (shas recorded in `run_record.json`); **NOT** soften any threshold.
- Did **NOT** touch live trading / Frozen Stack / scheduler / sizing /
  routing / promotion gates; nothing outside the h1 lab was written
  except this file. **NOT** staged, committed, or pushed in either repo.

## State

| item | state |
| --- | --- |
| H1-Auth-1 data / Auth-2 prereg / Auth-3 engine / Auth-4 tests | done (data conditional; prereg locked; engine static-valid; 48/48) |
| **H1-Auth-5 PRIMARY run** | **ABORTED at pre-flight (GI-1: funding-row markPrice empty before 2023-10-31); PRIMARY never executed; honest negative; single-run guard armed** |
| H1 line | closed at this gate; any continuation = separate amendment gate + fresh authorization |
| Trading research | PAUSED |
| Live trading | BLOCKED at 6 gates |

## Closure

H1-Auth-5 executed under the recorded authorization and **aborted at
pre-flight on a data-contract gap (GI-1), before the PRIMARY**. No
metrics, no results.json, no v2, no live change, no trading or system
change. Program remains PAUSED; live trading remains BLOCKED at 6 gates.
