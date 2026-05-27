# S13-D1 P3 BUILD runner harness report (sealed)

**Candidate record id:** `s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history`
**Phase:** `PHASE2-S13-D1-MNQ-RSI-2-BIDIR`
**Authored (UTC):** `2026-05-27T17:38:00.237737Z`
**Lifecycle state:** P3_BUILD_RUNNER_REPORT_SEALED
**Report seal sha256:** `6c8875cb791765193f6494183614c2c78e63b1ef9a53d1375a6dc44a235eb4a6`
**Reseal verified on disk:** YES (UTF-8 explicit)

## Build scope

Runner harness package + test scaffold + synthetic fixture. **NO execution; NO P4 smoke run; NO backtest.**

## Files authored (10 files this report covers)

| File | sha256 (first 16) |
|---|---|
| `__init__.py` | `f220cc3be291245f...` |
| `main.py` | `89b5d5b9bafec733...` |
| `execution_guard.py` | `0de7fd480ae7d827...` |
| `tests/__init__.py` | `36215388b2e15796...` |
| `tests/conftest.py` | `b589298aa43f7f7f...` |
| `tests/fixtures/synthetic_mnq_daily.csv` | `265f5a08a0557706...` |
| `tests/test_smoke_t1_t15.py` | `d1a5f8807a95fbff...` |
| `tests/test_oos_driver_invariants.py` | `15dfe5237027c1b2...` |
| (in_sample_driver.py / out_of_sample_driver.py covered by separate reports) | -- |

## CONFIG locked strategy params

| Param | Value |
|---|---|
| RSI period | 2 (Connors) |
| RSI long entry / exit thresholds | **`< 10` / `> 50`** |
| RSI short entry / exit thresholds | **`> 90` / `< 50`** |
| ATR period / multiplier | 20 (Wilder) / 2.0 |
| Per-trade risk | **0.5%** (DA3=B) |
| max_units_per_market | 1 (no pyramid) |
| **START_CASH_USD** | **$200,000** (DA4=C) |
| Tick size / value | 0.25 / $0.50 |
| RTH window | 09:30-16:00 ET America/New_York |
| K9 threshold | 100 (inviolate) |

## Tests authored (NOT RUN at P3 BUILD; P4 smoke separately authorized)

17 P4 smoke tests + 12 OOS driver invariants tests = **29 tests** authored.

## C6 inherited_constraints_block (carried verbatim from P2; appears in every build report)

1. REC1-equivalent (BINDING): OOS K9 reachable at lower bound with thin margin (~50-65 trades/year vs 50/year floor). If observed IS rate falls below 25/year on RSI(2) bi-directional, OOS K9 unreachability becomes structurally probable. The s9 RSI-2 baseline observed 414 trades over long-only 4-ETF window; if MNQ.c.0 bi-directional rate falls below half that proportional rate, OOS K9 fires. If OOS K9 fires, the OOS verdict shall be OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE analogous to S10-D2 P11 PARK at 23c7164 and s12-d1 P11 park at ecbd001. The chain shall NOT relax K9 at OOS; the appropriate response is to seal the INSUFFICIENT_SAMPLE / INDETERMINATE verdict and park the candidate. Pursuing s13-d1 accepts the structural possibility of an OOS PARK outcome if the IS rate falls below the DRAFT-estimated 50-65/y band.
2. DA3=B (BINDING): per-trade risk pct = 0.005 (0.5%); REVISED at SEAL from default 1.0% for DR3 mitigation (s9 RSI lineage cost-erosion precedent)
3. DA4=C (BINDING): START_CASH_USD = 200000 ($200k); REVISED at SEAL from default $100k for DR10 mitigation (high-frequency turnover); halves per-dollar cost pressure
4. K9-reachability discipline (NEW framework standard from selection-plan revision 0e3f9d4) applied at PLAN + DRAFT + SEAL + P1 + P2; binding for all subsequent phases
5. K9_THRESHOLD_INVIOLATE: closed_trades >= 100; no relaxation at any phase
6. Mechanic family F3 RSI(2) bi-directional mean-reversion LOCKED at PLAN; no reopening at DRAFT/SEAL
7. RSI thresholds 10/50/90/50 LOCKED at PLAN; threshold modification post-SEAL FORBIDDEN per RF13
8. DR3 risk ELEVATED (RSI lineage s9 falsification precedent); mitigated via DA3=B
9. DR10 risk ELEVATED (high-frequency turnover ~50-65 trades/y); mitigated via DA4=C ($200k START_CASH)
10. Tier-N spec LOCKED byte-equivalent at 262491c (sha 2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775)
11. P1 plan-lock LOCKED byte-equivalent at 005cb8a (sha 1cac253cbbbf4cdab87e777edbe0bca00739e925de382bd1d687faae9731052c)
12. s12-d1 terminal park (PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS at ecbd001) preserved unchanged
13. All parallel-session shorter-path sealed artifacts byte-stable; not anchored by this chain
14. Expected terminal verdict if OOS K9 fires: PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED (analogous to S10-D2 P11 PARK)
15. P2 PASS does NOT imply READY_FOR_LONGER_BACKTEST; requires P6 IS diagnostic under separate authorization
16. P2 PASS NEVER implies live-readiness; 6-gate live-block applies regardless of any verdict

## Next phase requirements

P4 synthetic smoke requires separate authorization: `Authorize s13 D1 MNQ.c.0 P4 synthetic smoke only`.

## Status

trading: PAUSED · live: BLOCKED_AT_6_GATES · FRC: NEVER_GRANTED · lifecycle: P3_BUILD_RUNNER_REPORT_SEALED · REC1-equivalent binding: True
