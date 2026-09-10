# Research redirect plan — weekly RS rotation (A) + delta-neutral perp funding carry (B)

**Date:** 2026-09-09 · **Mode:** RESEARCH_ONLY / ADVISORY_ONLY · **Author:** SPARTA Research OS (read-only synthesis)
**Scope:** plan document only. Nothing here runs, fetches, commits, or authorizes anything. Every step below is a
SEPARATE future operator authorization. Live trading remains **BLOCKED at the 6 gates**; trading **PAUSED**; FRC **NEVER_GRANTED**.

## 0. Why this document exists

One year of candidate research produced 26 rejected/closed candidates and no deployable edge. Exactly two lines showed
real, replicated signal: (A) weekly relative-strength rotation on equities (s17 -> s21) and (B) BTC/ETH/SOL delta-neutral
perpetual funding carry (H1). Operator decision 2026-09-09 (`brain_memory/projects/trading_bot/decisions.md`, 2026-09-09
entry): stop opening candidate families; redirect effort to A and B. This plan restates each line's exact state and the
shortest honest path to a decision, using only gates and numbers already on record.

## 1. Line A — weekly RS rotation (s18 -> s21) + broker-free forward paper harness

### 1.1 Current exact state (dated)

| item | state | evidence |
| --- | --- | --- |
| Locked mechanic | L=126 / S=21 / R=5 / top-8 equal-weight / long-only / relative-rank exit / $100k / split_only / cost S1 | `paper_trading/weekly_rs_s21_forward_paper_harness/manifest.py` |
| s21-d1 P10 OOS gate (2026-05-29, commit f6ec7088) | **OOS_CONFIRMED_DIAGNOSTIC**; seal `003ae25285f1ed38c1610d47928cda35a2e329c27b158d65f287e16c935dcffe` | `reports/external_research_hunter/s21_d1_..._p10_oos_gate_result_sealed.md` |
| s21-d1 P11 lifecycle (2026-05-29, commit 7e12e561) | OOS_CONFIRMED_DIAGNOSTIC, NOT live-ready; seal `9aa1e14712a644b87847bee302ecf561f715414bf73941afe915a685c02dad50` | `reports/s21_d1_..._p11_lifecycle_decision_sealed.md` |
| Line catalog (2026-05-29) | **PARKED**, "real, portable, modest, DIAGNOSTIC_ONLY"; seal `b61f32ee...c845` | `reports/weekly_rs_rotation_line_catalog_s18_s21_diagnostic_only_parked_sealed.md` |
| OOS numbers (2024-01-02..2025-12-30, fresh 48-name, 0/48 ever backtested) | 171 trades (85.8/y), net **+$48,474.92**, **+$170.96/trade**, sharpe/trade 0.144, PF 1.51, win 58.48%, **max DD 19.30%**, +48.47% on $100k | P10 seal above |
| IS / cost / walk-forward | IS +$277.93/trade (310 trades); P6.5 S0-S4 all positive; P6.7 K13 5/5 (agg +$114,696) | P7 memo seal `04ee5e86...8b57` |
| Forward paper harness (built 2026-05-29, commit f73bd52d) | BUILT; broker-free; no fetch; no keys; 27/27 tests (commit 1bc6144b) | `paper_trading/weekly_rs_s21_forward_paper_harness/` |
| Paper cycles run | **2**: cycle 001 anchor 2025-12-30 (fe9bdbf4); cycle 002 anchor **2026-05-28** (b18b530f), 4 closed trades, kill-switch GREEN, verdict CONTINUE | `.../runs/dry_cycle_001`, `.../runs/dry_cycle_002` |
| Active data source | `refreshed_20260528` (Tiingo split_only, ends **2026-05-28**; RUN_BOOK 115f4f2 seal `ff8aed3d...13ce`) | `manifest.py` `DATA_SOURCES` |
| Dashboard / notifier | `/paper` route (read-only status card); Telegram notifier dry-run by default | `app.py` ~L7066; `paper_trading/weekly_rs_s21_paper_notify.py` |
| s14-d1 multi-instrument sibling (MNQ/MES/MYM/M2K) | `S14_D1_AVAILABILITY_PROBE_DR9_AUDIT_PENDING_OPERATOR_FETCH` since 2026-05-27; needs `DATABENTO_API_KEY` + paid credits; operator has no fetch capacity | decisions.md 2026-05-27 entries; memory `project_s14_d1_blocked_no_databento_fetch` |

**What is blocking (today):** the harness is stale. Last traded anchor 2026-05-28; the harness raises `StaleDataError`
(NO-TRADE by design) for any newer anchor until the local CSVs are refreshed. Roughly 14 weekly anchors (2026-06-04 ..
2026-09-04) have not been cycled. The refresh needs `TIINGO_API_KEY` (env only) and its own authorization; no committed
refresh script exists (commit 7c927da0 shipped data + manifest only). Two unresolved observations must be audited before
any read: (i) only 4 closed trades exist (far under the 15-trade floor); (ii) cycle 002 reports equity $173,749 after a
single "catch-up" rebalance from the 2025-12-30 book — that jump is unaudited and must not be interpreted as a result.

### 1.2 Success / honest negative (restated from existing gates; none invented)

Defined in `paper_trading/weekly_rs_s21_forward_paper_harness/OPERATIONS_CHECKLIST.md` §6 and §8 and `manifest.py`
`gate_thresholds`:
- **Milestones:** 12-week read requires **>= 15 closed trades**; 24-week read requires **>= 35 closed trades**. Question at
  each read: did the simulated edge hold, cost drag <= 5%/yr, drawdown well under kill, no recurring REVIEW flags, mechanic locked.
- **Honest negative:** kill-switch **TRIGGERED** (drawdown >= 30%, annualized cost drag > 5%/yr, implementation shortfall > 25 bps,
  data-integrity failure, mechanic drift, manual stop) or trailing expectancy < 0 **persistent** (REVIEW = edge divergence).
- **Success:** both milestone reads pass with kill-switch GREEN. The checklist states explicitly that a good 12/24-week result
  "is NOT an OOS confirmation, NOT live readiness, NOT a profitability claim, and does NOT move FRC."
- No numeric "edge held" threshold beyond the kill-switch ladder is on record; the plan does not add one.

### 1.3 Next steps to a decision (each a separate authorization)

| # | step | tool / path | inputs | cost / time | human token | writes |
| --- | --- | --- | --- | --- | --- | --- |
| A1 | Audit cycle 001 -> 002 catch-up jump (read-only) | **NOT BUILT** (manual read of `runs/dry_cycle_00{1,2}/*.jsonl`, `paper_book.py`, `cycle.py`) | none | ~1 h, no data | none defined (read-only) | a short audit note in `reports/research_os/` |
| A2 | Refresh data to the latest completed weekly anchor | RUN_BOOK `reports/s21_weekly_rs_paper_data_refresh_run_book_sealed.md`; fetch script **NOT BUILT** as a committed tool | Tiingo split_only FULL-history re-fetch, 48 names; `TIINGO_API_KEY` from env (not keyless); **no Databento** | Tiingo API only; minutes | exact string from the RUN_BOOK: `Authorize s21 weekly RS paper data refresh fetch + verification workflow only — Tiingo split_only, frozen 48-name universe, FULL-HISTORY re-fetch + recompute, write to data/s21_weekly_rs_paper_refresh/raw (do NOT overwrite the sealed s21 DR9 CSVs), run SHA + calendar-alignment + split-consistency + historical-overlap-reproduction checks, HALT on stale/misaligned/undocumented-divergence; TIINGO_API_KEY from env only, never printed; no paper cycle, no broker, no live, no FRC.` | new dated dir `data/s21_weekly_rs_paper_refresh/raw/<SYM>_ohlcv_1d_20190102_<ASOF>.csv` + manifest; then a separate small code edit adding a `DATA_SOURCES` entry + `DEFAULT_DATA_SOURCE` bump in `manifest.py` (tests) |
| A3 | Run the missed weekly cycles in anchor order (003..~016), one per anchor, no duplicates | `cycle.run_weekly_paper_cycle(operator_authorized_dry_run=True, data_source=<new key>, min_last_date=<anchor>, asof_index=...)` | refreshed local CSVs only | seconds each | code gate `operator_authorized_dry_run=True` + "explicit run authorization this turn" (checklist §3; no fixed phrase defined) | `runs/dry_cycle_NNN/{paper_orders.jsonl, paper_trades_closed.jsonl, killswitch_status.json, paper_weekly_report_NNN.md}` |
| A4 | Continue one cycle per week to the 12-week read (>= 15 closed) then the 24-week read (>= 35 closed) | same as A3; status via `status.paper_status()` / `/paper` | weekly refresh (A2 repeated when `last_date` < anchor) | minutes/week | as A2/A3; commits "only under a separate explicit authorization" (checklist §5) | same run files; kill-switch reviewed each cycle |
| A5 | Decision memo at the 24-week read: CONTINUE-as-diagnostic / CLOSE-honest-negative | **NOT BUILT** | run files + kill-switch history | ~1 h | none defined | `reports/research_os/weekly_rs_s21_paper_24wk_decision_<date>.md` + brain memory entries |

Deferred, not required for the Line A decision: s14-d1 multi-instrument stays PENDING_OPERATOR_FETCH (Databento). Re-open
only if fetch capacity is restored, via the recorded re-issue path (decisions.md 2026-05-27).

### 1.4 Realistic expected outcome (no hype)

The measured edge is modest: +$170.96/trade OOS on the clean fresh universe (lower than s20's +$353 and s19's +$336), with a
19.30% OOS max drawdown and ~86 trades/year on a $100k CSV simulator with proxy costs. The master summary (seal
`175d4cd3...bba4`) states all figures are paper backtests, "NOT real money, NOT live". No record supports any capital
allocation; the only thing the records support is a broker-free 24-week paper observation to see whether the diagnostic
edge persists forward. If it survives both reads, the result is still DIAGNOSTIC_ONLY by framework design; the harness
manifest's `permanent_blocks` forbid broker, live, FRC, promotion and tuning.

## 2. Line B — H1 delta-neutral perpetual funding carry (BTC/ETH/SOL, Binance USD-M)

### 2.1 Current exact state (dated)

| phase | date | state | evidence |
| --- | --- | --- | --- |
| H1-Auth-1 data acquisition + integrity | 2026-05-16 | **MET / USABLE**: 3 symbols x 5 datasets keyless, sha-pinned (`data/raw/binance/_manifest.json`, twice re-verified); shared window 2020-09-13 16:00 -> 2026-05-16 08:00 UTC (5.67 y, SOL-bound), 6,213 shared stamps (6,212 complete triplets); `symbol_count_tested >= 3` feasibility TRUE | `C:\SPARTA_RESEARCH_LAB\h1_perp_funding\h1_auth1_data_acquisition_report.md`, `h1_cross_symbol_coverage_report.md` |
| H1-Auth-2 preregistration | 2026-05-16 | **LOCKED** (6 docs: prereg, accounting model, costs, windows, criteria, gate mapping). No report_seal hash recorded; the lock is by document + the sha-pinned snapshot | `h1_auth2_preregistration_decision.md` |
| H1-Auth-3 implementation | 2026-05-16 | engine built, static validation all_pass=true, NOT executed | `h1_perp_funding_engine.py`, `_engine_static_validation.json` |
| H1-Auth-4 unit tests | 2026-05-16 | **48/48 pass**; only real-data touch is read-only `load_all`+`validate_inputs` | `h1_auth4_unit_test_report.md`, `reports/research_os/no_trading_change_report_h1_auth4.md` |
| H1-Auth-5 (the ONE PRIMARY run) | — | **NOT RUN. Runner NOT BUILT.** Engine `__main__` refuses to simulate. No H1 phase after Auth-4 exists anywhere (checked lab, `reports/research_os/`, brain memory) | `next_actions.md` "After H1-Auth-4" block |
| Related D1 candidates C20 / C21 (different mechanic, 74 bps RT) | 2026-06 | both `all_decisive_gates_pass: false` | `data/*_c20/replay_results/c20_replay_summary.json`, `..._c21/...` — context only; cannot pre-judge or rescue H1 |

**What is blocking:** only (a) building a small runner and (b) one explicit human authorization. No data fetch is needed or
permitted (the prereg binds to the sha-pinned snapshot; "no new data may be fetched"). No Databento, no API key, no credits.
Note: `tools/h1_acquire.py` aborted on a TLS-intercepting network on 2026-05-16 14:22 (`reports/h1_acquisition_ABORTED.txt`);
that is the fail-closed re-acquisition path and is irrelevant to the run, which uses the existing pinned snapshot.

### 2.2 Success / honest negative (restated from `h1_success_failure_criteria.md`, LOCKED)

- **Pre-flight abort:** blocking reconcile `|independent - ledger| <= 1e-6 * |independent|` must pass or the run ABORTS with no
  metrics = honest negative (GE-2).
- **PASS = all of S1-S8 on WA:** S1 net > 0; S2 annualized **>= 3.0%** net; S3 MaxDD **<= 10%**; S4 **W2022 net >= 0**; S5 |beta to BTC|
  and |beta to basket| **<= 0.05** and basis drift <= 25% of gross funding; S6 net > 0 at 1.0x and 1.5x friction, >= 0 at 2.0x;
  S7 all 3 symbols, full window, >= 6,000 stamps each; S8 M1 >= M2 >= M6, locked funding sign, no notional inflation, reconcile OK.
- **Too-good tripwire:** WA annualized > 25% or Sharpe > 4 => mandatory artifact investigation (CONDITIONAL at best).
- **CONDITIONAL:** reconcile OK, S1/S4/S5/S7/S8 hold, but S2 or S3 or S6 misses (or tripwire) — reported, still blocked.
- **FAIL / honest negative:** pre-flight abort, or any of S1/S4/S5/S7/S8 fails, or >= 2 of S2/S3/S6 fail, or any GI/GE/GR fires
  (incl. GR-5 single symbol > 70% of net). Anti-rescue is binding: no tuning, no window/symbol reselection, no rerun.
- A PASS grants eligibility to enter the SPARTA gate chain only (`h1_sparta_gate_mapping.md` stages 2-6); never deployment.

### 2.3 Next steps to a decision (each a separate authorization)

| # | step | tool / path | inputs | cost / time | human token | writes |
| --- | --- | --- | --- | --- | --- | --- |
| B1 | Build the H1-Auth-5 runner (runner owns persistence; independent reconcile path; expect 6,212 shared stamps) | **NOT BUILT**; templates: `C:\SPARTA_RESEARCH_LAB\g1_funding_carry\run_g1_auth5_simulation.py`, `..\g2_cash_and_carry\run_g2_auth5_simulation.py`; engine `h1_perp_funding_engine.py` unchanged | none (stdlib only) | ~1-2 h build + static validation; no data | none defined beyond "Mahmoud's explicit, verbatim H1-Auth-5 instruction" (`next_actions.md`: "H1-Auth-5 = the ONE PRIMARY run (single execution, no retry) via a SEPARATE runner script") | `run_h1_auth5_simulation.py` + static-validation JSON; no results |
| B2 | Execute the ONE PRIMARY run (single execution, no retry) | runner from B1 | sha-pinned snapshot at `h1_perp_funding\data\raw\binance\` only; keyless; no fetch; no Databento | seconds of compute | same H1-Auth-5 instruction (verbatim, explicit) | `artifacts/` JSON (per window W2020..W2026p, WA, W_SOLFTX; per symbol x year), `h1_auth5_primary_run_report.md`, `reports/research_os/no_trading_change_report_h1_auth5.md` |
| B3 | Label the outcome by the locked decision rule (PASS / CONDITIONAL / FAIL) and close | report writer **NOT BUILT** (manual) | B2 artifacts | ~1 h | none defined | closure memo; brain memory decisions/lessons/next_actions; memory file update |
| B4 | Only if PASS: stage-2 v2 evidence records, then the frozen `anti_overfit_gate` as-is (stage 3) | existing frozen SPARTA modules, unmodified | B2 artifacts | small | each stage "a distinct future Auth gate" (`h1_sparta_gate_mapping.md`); no token strings defined | v2 records, gate verdicts |
| B5 | If FAIL/CONDITIONAL: arc CLOSED as honest negative; no H1 v2/re-spec; funding-carry chain (G1, G2, C20, C21, H1) recorded complete | — | — | — | — | closure only |

### 2.4 Realistic expected outcome (no hype)

The preregistration's own prior (H1-Auth-2 decision, binding): net carry is "thin and may well be <= 0"; a FAIL is "a likely and
fully acceptable outcome". Recorded inputs: BTC funding mean +0.000108/8h (85.4% positive), ETH +0.000131 (86.4%), SOL
+0.0000015 (72.2%; ~0.16%/yr gross drag); frozen costs 13 bps per leg-turn per leg, 3%/yr collateral opportunity cost, 0.50%
re-hedge band. The success bar is >= 3%/yr net with <= 10% MaxDD and 2022 >= 0. No record states what capital this would be
worth; the engine's C0 = $1,000,000 is a fixed accounting notional, not an allocation. The honest value of B2 is a clean
answer to a question that has been prepared for four months and costs seconds to ask.

## 3. Candidate family freeze (recorded decision)

- Operator decision 2026-09-09 (`decisions.md`): **no new C-series candidate families after C22 concludes.**
- C22 state: `HOLD_FOR_MORE_FROZEN_DATA_WINDOWS`, GC collection 81/20 windows through 2026-09-09 (20260816 missing); replay
  human-gated. The collection-review token was already consumed in July (readiness watcher `COLLECTION_REVIEW_CONSUMED=True`);
  the live decision is in `reports/c22_gc_decision/c22_closure_recommendation_2026-09-09.md` (recommended: REJECT_KEPT_ON_RECORD on
  data/execution feasibility; alternative: HOLD pending short-instrument evidence). Operator records one token line in decisions.md.
- C23 (`crypto_cross_sectional_low_volatility_anomaly_beta_neutral`): stays **ON-DECK / FROZEN**. Its recorded next gate is
  `HUMAN_DECISION_OPEN_CANDIDATE_23_AFTER_C22_CONCLUDES_OR_HOLD`; under this freeze the standing answer is HOLD unless the
  operator explicitly reverses. C23+C24 are separately recorded `REJECTED_AS_PORTFOLIO_SLEEVES_KEPT_ON_RECORD` (commit ec9eef22).
- No new candidate families, no new preregistrations, no hunter-sourced candidates enter the funnel while the freeze holds.

## 4. Non-authorization statement

Nothing in this document is a live, paper-via-broker, promotion, or data-fetch authorization. Every step in §1.3 and §2.3
requires its own explicit operator authorization at the time it is taken. Live trading remains **BLOCKED at the 6 gates**
(Gate 1 anti_overfit verdicts, Gate 2 regime_score verdicts, Gate 3 Checkpoint A FAIL, Gate 4 `lifecycle.py` promotion rules,
Gate 5 `paper_arena.py`, Gate 6 Frozen Stack onboarding — `decisions.md` 2026-05-14, `live_trading_blocked_report.md`).
Trading PAUSED · FRC NEVER_GRANTED · Line A DIAGNOSTIC_ONLY · Line B research-only. No credentials, exchange keys, broker,
scheduler, sizing, routing, or Frozen Stack are touched by this plan. This file was written read-only from existing records;
no other file was modified and nothing was committed.

## 5. Recommended order

1. **B1 -> B2 -> B3** first: zero data cost, zero keys, seconds of compute, and it converts a four-month-old open question into
   a closed answer either way.
2. **A1** (audit the catch-up jump) before spending anything on A2; then **A2 -> A3 -> A4** on the weekly cadence to the
   24-week read; **A5** decides.
3. s14-d1 multi-instrument stays deferred until Databento fetch capacity exists; it is not on the critical path of either line.
