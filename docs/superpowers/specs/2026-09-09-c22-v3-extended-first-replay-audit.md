# C22 V3_EXTENDED + First Deterministic Replay — Audit of Existing Work

Date: 2026-09-09 · Repo: `C:\SPARTA_BRAIN` · HEAD `5d5a3575` (master, ahead of origin by 1)
Mode: READ-ONLY AUDIT. Nothing in C22, V2, the frozen files, or strategy rules was altered.
Companion plan: `docs/superpowers/plans/2026-09-09-c22-v3-extended-first-replay-plan.md`

## 0. One-paragraph verdict

The C22 lifecycle has produced a complete, sealed *specification* stack (Phase A REV1 replay spec; B1 forward-exit + execution-data contracts; B2 short-instrument evidence request; B3 acquisition plan) and a fully parameterized V2 label contract, but **zero executable replay code**: no NAV ledger, no fills, no PnL, no cost arithmetic exists for C22. The 81-window collection (2026-06-20 → 2026-09-09) already satisfies the frozen forward-exit coverage rule (40/40 expected weekday sessions present through the second 15-day extension). The single calendar gap (2026-08-16, a Sunday) is not an expected session under B1 but **is** a hard build failure for a contiguous V3 label artifact. The decisive blockers before any fee-honest replay are unchanged since July: no short-instrument evidence (75 of 88 actionable signals are shorts), no frozen cost base case, and no execution price source for out-of-radar exits. A no-PnL deterministic dry run over the 81 windows **can** be built now from existing contracts plus one new pure ledger module.

## 1. Inventory of what exists (verified)

### 1.1 Data
| Item | State |
|---|---|
| Frozen dataset `data/external_signum_trend_radar_gc/` | 80 dated files + undated legacy 06-20 = **81 valid windows**, 50 rows each, 2026-06-20 → 2026-09-09 |
| Missing calendar day | **2026-08-16 (Sunday)** — absent from Downloads, inbox, dataset, quarantine |
| Raw top-100 `_raw_top100/` | 61 files (2026-07-11 → 09-09); reductions `_reductions/` 73 records |
| Weekend windows | 22 of 80 dated files fall on Sat/Sun (Signum exports daily) |
| Candle chain | 3900/3900 rows: `indicators.data[-1].date == runDate − 1`; 3744/3744 same-symbol overlaps byte-identical across adjacent exports (0 mismatches) |
| Top-50 dropout | 156 symbol-days of 3900 (4.0%) where a symbol present on D is absent on D+1 → **no next-bar price inside the exports** |
| Universe | 114 distinct symbols across BINANCE, BITFINEX, BITGET, BYBIT, COINBASE, GATE, KRAKEN, KUCOIN, MEXC, OKX |
| Readiness watcher | `81/20`, `HOLD_FOR_MORE_FROZEN_DATA_WINDOWS`, `label_review_decision=HOLD_FOR_MORE_C22_LABEL_EVIDENCE`, `ready=false` (expected in extension phase) |
| Local external OHLC | Binance spot 1d, 42 pairs, 2021-01-01 → **2026-06-21** (`data/broad_crypto_universe_c23_c24/`) |
| Local funding | Binance USD-M, 40 perps, → **2026-06-21** (`data/broad_crypto_funding_universe/`) |
| Local borrow rates | **None** |
| C22 asset coverage locally | OHLC+funding for 7 of 27 signal assets (AAVE, CRV, LINK, SOL, TRX, ZEC, BTC); **absent** for the other 20 |
| Short-instrument evidence dir `data/c22_short_instrument_evidence/` | **Does not exist** (B3 layout never created; `ACQUISITION_STATUS=NOT_AUTHORIZED`) |
| Tests | 190 C22 tests pass (`tests/test_c22_*.py` + 2 wiring tests). Note: `pytest` from repo root is broken by a stray directory `C:\SPARTA_BRAIN\"hydra ` (private-use char + trailing space); run from `tests/` with `PYTHONPATH=C:\SPARTA_BRAIN` |

### 1.2 Label pipeline (V1 → V2)
- Classifier: `sparta_commander/external_signum_trend_radar_gc_long_short_v1_real_candle_labels_contract.py:120-143`. Rules use ONLY fields inside the export (`indicators.data[-1]`/`[-2]`: `ohlc.o/h/l/c`, `gc.trend/upper/filter`); BTC downtrend from `BINANCE:BTCUSDT` (`:50,163-167`); `BEAR_HIGH_MULT=0.98` sourced from candidate spec `:219`.
  - `LONG_ENTRY`: `c > upper and prev_c <= prev_upper`
  - `HEDGE_SHORT`: `trend=="Red" and c < filter and prev_c >= prev_filter`
  - `BEAR_SHORT`: `btc_downtrend and trend=="Red" and h >= 0.98*filter and c < filter`
  - `SKIP` on missing indicator data; ordering `market_rank_asc, market_cap_desc, symbol_asc`.
- **No external OHLC is used anywhere**; the data-readiness contract rejects external feeds because they lack `gc.*` (`..._v1_data_readiness_contract.py:18-20,79-101`).
- V2 range contract `..._v2_range_multi_window_real_candle_labels_contract.py` is **fully parameterized**: `build_range_multi_window_manifest(window_inputs, *, start_date, end_date, expected_window_count, expected_rows_per_window, expected_total_rows)` (`:85`), `validate_range_multi_window(record)` (`:230`), `v2_artifact_filename(start, end, window_count)` (`:73`). The 26w freeze lives only in the runner constants `tools/c22_signum_trend_radar_gc_v2_range_multi_window_real_candle_labels_once.py:38-42`.
- Contract constraints that bind a V3 build:
  - `expected_dates` is a contiguous `_daterange(start,end)` (`v2:95-110`) → a range with a hole fails (`range_length_82_ne_expected_window_count_81`, `dates_not_exactly_expected_contiguous_range`).
  - Validator requires `"_v2_"` in the artifact name (`v2:289-291`); basename must stay `c22_gc_real_candle_entry_labels_multiwindow_v2`; the `{N}w_{start}_{end}` suffix prevents collision.
  - Provenance: sidecars mandatory ≥ 2026-06-28, raw ≥ 2026-07-10 (`v2:40-41`); any `MISSING_MANDATORY` rejects (`v2:274-278`). All 81 windows satisfy this today.
  - Write gate: `--execute-build` + exact token `HUMAN_DECISION_C22_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT` (`runner:81-91`); never overwrites.
- V2 artifact: `detector_labels/c22_gc_real_candle_entry_labels_multiwindow_v2_26w_2026-06-20_2026-07-15.json`, sha `b6a28a48…`, byte-identical rebuild PASS (integrity report 2026-07-20). 88 actionable (13 LONG / 72 BEAR / 3 HEDGE).

### 1.3 Phase A — replay spec REV1 (`external_signum_trend_radar_gc_long_short_v1_replay_spec_contract.py`, report 2026-07-21)
- Verdict `C22_REPLAY_SPEC_READY_FOR_SECOND_HUMAN_REVIEW`; spec sha `9bf10af3…` (pinned by B1/B2/B3).
- Frozen: entries 2026-06-20 → **2026-07-15** (`NO_NEW_ENTRY_AFTER`, `:73`); `EXCLUDED_FUTURE_DATES=(07-16,07-17,07-20)` (`:72`).
- Exits: long `close < gc.upper` or out-of-radar; short stop `close > gc.filter`, TP `close <= 0.65*entry`, out-of-radar. **No max hold** (validator fails any non-None, `:591`). Forced liquidation = non-decisive truncation diagnostic only.
- Fills: next executable session OPEN after decision date; exits before entries; ordering `date → market_rank → asset_id`; 100% NAV gross cap; **deterministic rejection, never resize**; sizing 8% (long breakout ≤25d) / 2% (long otherwise) / 3% (hedge) / 5% (bear); 1× leverage.
- Forward rule: initial 30 cal days from 07-16, then predeclared 15-day extensions until every position closes; open positions at end → `BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA`.
- Costs: 9 disaggregated components; **37 bps = sensitivity case only; base case NOT frozen**.
- Benchmarks: BTC B&H, EW passive point-in-time, zero-flat, fixed-seed matched random null, signal-off control, gross-vs-net.
- Only human token ever recorded for C22 replay: `HUMAN_DECISION_C22_REPLAY_SPEC_ACCEPT_OR_REVISE=REVISE` (→ REV1). The second review (ACCEPT) is **not recorded**.
- **No executable code**: `build_replay_spec()`, `canonical_spec_bytes()`, `validate_replay_spec()` only.

### 1.4 Phase B1 — forward-exit + execution-data contracts (2026-07-21)
- `c22_forward_exit_data_readiness_contract.py`: expected sessions = **weekdays only** (`expected_export_sessions`, `:127-133`); weekends "have NO session". Initial range 07-16 → 08-14; `extension_range(n)`; `readiness_from_coverage()`.
- Read-only re-evaluation today (contract functions, nothing written): initial horizon **COVERAGE_COMPLETE_FOR_RANGE**; 07-16 → 09-09 expected weekday sessions **40/40 present, 0 missing**; 2026-09-09 falls in extension #2 (08-30 → 09-13). 55 post-cutoff snapshots present.
- `c22_execution_data_short_instrument_feasibility_contract.py:73-92` already encodes `COST_COMPONENTS`, `COST_RESULT_LEVELS`, next-open fills, exits-before-entries, ordering, cap, rejection, `missing_next_bar_fail_closed`, `no_invented_fill`. **Contract only; nothing executes it.**
- Short instrument `UNRESOLVED_PENDING_SEPARATE_HUMAN_SELECTION`; basis review required (signal price = CMC reference `indicators.cmcRefPriceUsd`, not a venue price).

### 1.5 Phase B2 — short-instrument evidence request (2026-07-21)
22 short assets; perp/margin/funding/borrow evidence `FAIL_CLOSED`/`ABSENT` for all; 6 Binance names have partial funding ending 2026-06-21; identity risks (KRAKEN:SPXUSD collision; venue-native LEO/GT/OKB; mapping-sensitive GRAM/TEL/ASTER/VIRTUAL). Acquisition `NOT_AUTHORIZED`.

### 1.6 Phase B3 — acquisition plan (2026-07-22)
Source tiers T1–T5 (T3 minimum decisive); fail-close-early order (registry → mapping → funding/borrow → OHLC → fees → liquidity → coverage); proposed layout `data/c22_short_instrument_evidence/…` **not created**; 5 authorization tokens, none issued.

### 1.7 Reusable code elsewhere in the repo (verified by audit)
| Need | Reuse | Adaptation |
|---|---|---|
| Metrics / drawdown | `tools/c21_fee_honest_replay_once.py:141,149` (`_max_drawdown`, `_metrics`) | copy |
| SHA-pin-before-read + audit crosscheck + scope_locks summary | `c21_fee_honest_replay_once.py:78-89,266+` | copy pattern |
| Seeded matched random-entry null | `tools/c14_fee_honest_replay_once.py:61,212,245` | copy, match side mix + duration |
| Buy-and-hold benchmark | `tools/c18_h4_fee_honest_replay_once.py:187-193` | copy |
| Equal-weight passive with NAV renorm | `tools/c17_fee_honest_replay_once.py:189-204` | copy, make point-in-time |
| Seal / canonical JSON / atomic write / allowlist | `sparta_commander/strategy_factory_phase5_offline_backtest_run.py:310-346,430,439,663` | copy |
| `end_of_data` force-close convention (full round-trip charged) | `low_turnover_..._dry_run_contract.py:190`, `c21:17` | reuse as truncation diagnostic |
| Report canonicalization + atomic write | `tools/c22_forward_and_execution_data_readiness_report_once.py:149,224` | import |
| Binance OHLC/funding fetchers (REST, allowlisted, no ccxt) | `tools/fetch_binance_broad_universe_daily_frozen.py`, `tools/fetch_binance_broad_funding_frozen.py` | widen allowlist + range; **Binance only, survivorship-biased** |
| **NAV ledger with cap / ordering / rejection / next-open fills** | **nothing exists** | new pure module |

## 2. What is missing before the first replay can execute

### M1. 2026-08-16 gap
- Not an expected session under B1 (Sunday) → does **not** block forward-exit coverage.
- **Does** block a single contiguous V3 artifact (V2 contract has no gap concept).
- Fill path with precedent: on 2026-08-06 the operator fetched six historic windows via `get-trendradar-daily(runDate=…)` and admitted them through the guarded pickup chain (decision log 2026-08-06). The same operator-directed fetch with `runDate="2026-08-16"`, dropped into a clean folder and run through `tools/c22_signum_gc_download_pickup_once.py`, would yield 82 contiguous windows / 4100 rows. Requires explicit human authorization; the pickup tool itself never fetches.
- Fallback if Signum has no 08-16 run: two V3 segments (06-20 → 08-15: 57w/2850; 08-17 → 09-09: 24w/1200) using the same runner.

### M2. Entry window for the replay (spec conflict)
- Accepted-for-review spec REV1 hard-freezes entries ≤ 2026-07-15 and B1/B2/B3 are SHA-bound to it. Using V3 labels after 07-15 as **entries** contradicts the spec and would require Phase A REV2 + re-binding B1–B3 + a second review cycle.
- Recommended: first replay keeps entries = V2 26w (88 actionable); the 81/82-window collection serves as the **exit path**; V3_EXTENDED labels are entry-evidence-only / `EXIT_ONLY`-flagged diagnostics (label continuity, signal density drift) until a REV2 decision.

### M3. Weekend-session ambiguity (needs human ruling)
V2 labelled every calendar day including 8 weekend windows; B1's forward contract declares weekends non-sessions. Crypto trades 24/7 and the candle chain proves daily continuity. A Saturday LONG_ENTRY needs a defined "next executable session" (Sunday's candle open vs Monday's). Repo convention: `SPEC_AMBIGUITY_REQUIRES_HUMAN_REVIEW`. The dry run must count affected trades under both readings.

### M4. Execution price for out-of-radar exits
4.0% of symbol-days leave the top-50; on exit the next-bar open is **not** in any export. Spec: `NO_EXECUTABLE_NEXT_BAR` = fail-closed unless external OHLC exists. Local OHLC covers 7/27 assets and ends 2026-06-21. Either (a) authorize an OHLC fetch (Binance-only reach; other venues need new fetchers from the `_assert_safe_url` template), or (b) the first replay reports those trades as fail-closed and the decisive verdict is BLOCKED if any decisive trade hits this.

### M5. Short-instrument feasibility (largest blocker)
75/88 actionable signals are shorts. Evidence ABSENT for all 22 assets; acquisition NOT_AUTHORIZED; no borrow data anywhere; funding local only to 06-21. Under the spec, every short fails closed at run time → a *decisive* fee-honest replay is impossible until B3 stages 1–3 are authorized, executed, and admitted. A long-only decisive run has n=13 (non-conclusive by the spec's own power warning).

### M6. Funding / fees / slippage base case
No frozen base case; 37 bps is a labelled sensitivity only. Gate `C22_EXECUTION_COST_BASE_CASE_READY_FOR_HUMAN_REVIEW` never reached. Requires operator-supplied T1/T2 fee schedules per venue, spread/slippage evidence, and per-asset funding/borrow series for every holding day. The disaggregated component names and result levels already exist in code (`c22_execution_data_short_instrument_feasibility_contract.py:73-78`) and must be implemented against, not redesigned.

### M7. END_OF_TEST handling
No `END_OF_TEST` concept exists in C22 or the repo. Applicable rules: no max hold; open positions at end of reviewed coverage → `BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA`; forced liquidation is a non-decisive truncation diagnostic; `open_trade_count` is a required stat; repo convention elsewhere force-closes at the last bar with `exit_reason="end_of_data"` and charges the full round trip. Recommended definition (to be pinned in the dry-run spec): END_OF_TEST = last valid export date in the admitted exit path (09-09 today); positions still open are (i) counted in `open_trade_count`, (ii) valued in a separate `truncation_diagnostic` using the `end_of_data` convention at the last available candle close, (iii) excluded from all decisive metrics, and (iv) force the decisive verdict to BLOCKED until a further predeclared 15-day extension closes them.

### M8. Basis alignment
Signal/candle prices are CMC reference prices; execution would be on a venue. B1 requires a basis review with no adjustment selected. Unresolved; must be evidenced per asset before the fee-honest run.

### M9. Governance state
- Second review of Phase A REV1 (ACCEPT) not recorded; B1/B2/B3 reviews not recorded; only `REVISE` exists. The lifecycle formally sits at "awaiting human review" on four artifacts simultaneously.
- Pre-existing provenance drift: the active 2026-06-26 window is the pretty-printed file (sha `a872f356…`) quarantined twice in June, re-entered 2026-06-26 20:44, and since pinned as `source_sha256` in the frozen V2 26w artifact. Quarantine notes are stale. Not a data-content problem (50 rows, identical keys); a re-admission note is the safe fix. Not touched by this audit.

## 3. What can be built now without new data or new human tokens
1. **V3_EXTENDED runner** (new file, reuses V2 contract; dry-run default; token-gated write). Executable immediately as a dry-run; a build needs M1 resolved or the two-segment profile.
2. **Pure replay ledger module + tests** (new): sessions, next-open lookup from the following export, sizing, exits-before-entries, ordering, cap/rejection, exit rules, cost disaggregation hooks, END_OF_TEST finalization. No PnL is produced until costs are frozen; the module is contract-driven from existing constants.
3. **No-PnL dry-run runner** over V2 entries + 81/82-window exit path, reporting: trade skeleton, `open_trade_count` at 09-09, `NO_EXECUTABLE_NEXT_BAR` count, weekend-ambiguity counts under both readings, shorts fail-closed count, coverage verdict, and the truncation diagnostic. This is gate `C22_DRY_RUN_READY_FOR_HUMAN_REVIEW` from Phase A.

Everything beyond that (fee-honest PnL, decisive verdict) is blocked on M4–M6 and M8.
