# SPARTA Research OS — H1-Auth-6 / No-Trading-Change Report

**Generated:** 2026-09-12 (UTC; operator date 2026-09-11)
**Mode:** `ADVISORY_ONLY` — research-only, standalone lab
**Gate:** H1-Auth-6 — preregistration amendment (mark-price source) +
the ONE amended PRIMARY run of the multi-symbol perpetual funding-carry
engine (BTC/ETH/SOL, Binance USD-M, delta-neutral long-spot /
short-perp, equal initial USD notional, no leverage).
**Authorization (verbatim record):** on 2026-09-11 the operator
(Mahmoud) was told "Decide on H1-Auth-6, the mark-price amendment"
(open a new numbered step re-locking the mark-price source to the
mark-kline series and re-run once) and replied "ok do it all". Treated
as the H1-Auth-6 instruction: lock exactly ONE non-economic amendment,
re-lock the shas, execute the SINGLE PRIMARY run once; no second run,
no parameter changes, no re-tuning.
**Outcome:** **The PRIMARY executed exactly once. Final label
TRIPWIRE (engine label FAIL) — honest negative, closed. The +305 %
headline is a presumptive artifact (funding accrued on a fixed COIN
notional whose USD value rode a 7–25× price move, on a book the
engine's own risk flag says would have been liquidated), not an edge.**

## What this event did

1. **Amendment record** `reports/auth6/h1_auth6_amendment.{md,json}`
   (G2-Auth-7 precedent): exactly ONE non-economic amendment — rule 7's
   mark-price operand = mark-kline OPEN of the engine bucket
   `int(round(fundingTime/8h))×8h` from the pinned
   `<SYM>-markPriceKlines-8h.json` (shas `0b2664d5…`, `8d4b0a78…`,
   `5ec0b259…` at the H1-Auth-1 stamp) instead of the funding row's
   empty `markPrice`. Read-only evidence: the OPEN reproduces the
   native field exactly on 2,257 / 2,271 / 2,131 of 2,785 overlap rows
   (mean |rel diff| ~1e-6..1e-5); the CLOSE does not (~1–2 %). No
   threshold, window, parameter, symbol or cost changed.
2. **Implementation** as a runner-side input adapter in the new
   `run_h1_auth6_simulation.py` (Auth-5 runner + adapter + P3b re-lock
   + P4a; downstream functions source-identical, asserted by test);
   **engine untouched** (sha `388ecb6d…14f7` before and after). The
   H1-Auth-5 P4b guard kept verbatim now passes (raw 3,427 / 3,427 /
   3,502 empty in-window stamps → 0 / 0 / 0).
3. **Attempt 001** (r1, runner `f30d07f0…7b5f`): P1–P5 passed, then
   the engine raised at its first parse because it parses every row
   of the funding file and the r1 adapter left pre-window rows
   untouched. Zero ledger lines. Preserved under
   `reports/auth6/preflight_attempt_001_…/`; runner-side scope fix
   (r2, runner `20759ade…d27c`: same rule on every row with a mark
   bucket; NaN for the 312 / 78 / 0 rows predating the mark-kline
   history, never consumed, post-PRIMARY leak check); A1 unchanged,
   shas re-locked, r1 record preserved.
4. **The single run** (2026-09-12 01:03Z): 15/15 shas, P3b 9/9
   re-lock checks, reconcile PASSED (9.3e-10), results written.
5. Tests: **128/128** (48 engine + 8 tools + 38 Auth-5 runner + 34 new
   Auth-6 runner tests: alignment rule, refusal without mutation,
   re-lock record, P4b passing, out-of-window/NaN scope, leak check,
   downstream-verbatim).

```
C:\SPARTA_RESEARCH_LAB\h1_perp_funding\
  run_h1_auth6_simulation.py                 (NEW; engine untouched)
  tests\test_run_h1_auth6_runner.py          (NEW; 34 tests)
  reports\auth6\h1_auth6_amendment.{md,json} (amendment + re-lock, r2)
  reports\auth6\run_record.json / results.json / verdict.md / no_trading_change_note.md
  reports\auth6\h1_auth6_result_analysis.md  (artifact diagnosis)
  reports\auth6\preflight_attempt_001_CRASHED_engine_parses_out_of_window_markprice\
NEW (SPARTA_BRAIN):
  reports\research_os\no_trading_change_report_h1_auth6.md   (this file)
```

## Result

| field | value |
| --- | --- |
| final label | **TRIPWIRE** (engine label FAIL; honest negative, closed) |
| S-vector | S1✓ S2✓ **S3✗** **S4✗** S5✓ S6✓ S7✓ S8✓ |
| invalidity fired | tripwire_too_good, GR3, **GR8 liquidation (3/3 symbols)**, S3, GR2, GI2/GR6 (runner-check false positive, disclosed) |
| WA total net / annualized / Sharpe | +305.5 % / +53.9 % / 10.3 |
| WA MaxDD | 12.15 % (> 10 %) |
| W2022 | **−20.4 %** (SOL −23.0 %; FTX window −27.8 %) |
| β to BTC / basket | −0.003 / −0.001 |
| friction 1.0 / 1.5 / 2.0× | +305.5 / +304.5 / +303.6 % |
| stamps BTC / ETH / SOL | 6,212 / 6,212 / 6,287 |
| reconcile | PASSED (9.3e-10) |
| per-symbol share | BTC 0.17 / ETH 0.24 / **SOL 0.60** |
| per-year funding | 2021 +1.52, 2024 +1.40 (93 % of gross); 2022 −0.19 |

**Why it is an artifact (blunt).** `q_s` is fixed in coins, so the USD
funding base `q_s × mark_t` rose 7.5× (BTC), 5.9× (ETH), 25.5× (SOL)
while the denominator C0 stayed fixed — the G1 fake-yield mechanism in
coin-notional form; the cash reconcile passes because the arithmetic is
self-consistent, which is exactly why the tripwire exists. And the
book is infeasible as locked: 1× cash collateral (~0.17 M per symbol)
against short-perp unrealized losses of 1.09 M / 0.82 M / 4.12 M with
no cross-margin allowed → the engine's conservative-risk flag fired
for all three symbols; the funding stream belongs to a position that
would have been liquidated. Not directional (β ≈ 0), not drift. Even
inside the artifact the bear year is −20 %.

**GI2/GR6 disclosure.** The runner's post-run SOL check expects
`n_skipped == 1`, but the single incomplete triplet sits before the
complete-triplet window and is excluded by the window filter, so
`n_skipped` is 0 by construction; the off-interval count (101) and
the FTX-window stamp counts (105 SOL vs 30 BTC) confirm the locked
handling worked. False positive of the check; label unaffected;
record not edited.

## Honest framing (no-hype, carried forward)

The pre-committed prior ("thin, may well be ≤ 0; FAIL likely and
acceptable") was never reached: the locked H1 design (fixed coin
notional + fixed capital + no cross-margin) is internally inconsistent
over a 7–25× price move and produces an artifact before it can measure
a thin carry. Making it consistent (fixed USD notional with explicit
re-sizing as capital actions, or return on actual margin employed) is
a **design change = a new preregistration**, not an amendment, and is
**not** authorized or recommended here. This run is evidence neither
for nor against a thin positive funding carry.

## What this event did NOT do

- Did **NOT** produce a usable research result, v2 record, live
  signal, or paper-arena artifact; **NOT** run anti_overfit /
  regime_score / robustness_audit / lifecycle; **NOT** rerun, tune,
  rescue or re-amend after the result.
- Did **NOT** fetch data, touch the network, or use API keys or
  credentials; **NOT** modify any pinned data file (15/15 sha match
  after the run).
- Did **NOT** modify the locked engine or any locked H1-Auth-2 document
  (shas recorded); **NOT** soften any threshold.
- Did **NOT** touch live trading / Frozen Stack / scheduler / sizing /
  routing / promotion gates; nothing outside the h1 lab was written
  except this file. **NOT** staged, committed, or pushed in either
  repo. Brain-memory files were NOT appended (per the task's
  "touch nothing else in SPARTA_BRAIN").

## State

| item | state |
| --- | --- |
| H1-Auth-1..4 | done (data conditional; prereg locked; engine static-valid; 48/48) |
| H1-Auth-5 | ABORTED at pre-flight (GI-1: empty markPrice) — historical record, stands |
| **H1-Auth-6 amendment + single run** | **✓ run once → TRIPWIRE / honest negative (artifact: coin-notional inflation + liquidated book); closed; no re-amendment** |
| H1 line | CLOSED at this gate; any continuation = new preregistration (design change), separate explicit authorization |
| Trading research | PAUSED |
| Live trading | BLOCKED at 6 gates |

## Closure

H1-Auth-6 executed under the recorded authorization: one non-economic
amendment locked and re-locked, one PRIMARY run, **TRIPWIRE / honest
negative** — the preregistered design yields an implausible,
infeasible number, not a carry measurement. No metric here is an edge.
No trading or system change. Program remains PAUSED; live trading
remains BLOCKED at 6 gates.
