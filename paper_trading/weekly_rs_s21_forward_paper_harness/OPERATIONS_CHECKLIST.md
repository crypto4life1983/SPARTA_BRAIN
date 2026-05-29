# Weekly RS s21 — Broker-Free Paper Operations Checklist & Calendar

> **DIAGNOSTIC_ONLY — NOT LIVE-GRADE.** No broker. No live trading. No paper-via-broker.
> **trading_status = PAUSED · live_status = BLOCKED_AT_6_GATES · FRC = NEVER_GRANTED.**
> This is a *simulated* forward paper test of the s21 weekly RS edge against operator-supplied
> LOCAL split_only CSVs. The harness **never fetches data, holds no API keys, and connects to no broker.**
> Passing every paper gate below does **not** grant live readiness — it only keeps the diagnostic honest.

Source of truth: `manifest.py` (locked mechanic + thresholds), `cycle.py` (gated runner + stale-data guard),
`killswitch.py` (triggers). Do not edit those to "make a cycle run." If a guard fires, that is the answer.

---

## 0. Locked mechanic (never tune mid-test)
- Signal: **126-day lookback, 21-day skip** relative-strength (`L=126, S=21`), long-only.
- Rebalance cadence: **R = 5 trading days (weekly)**. Hold **top 8**, equal weight (1/8 each). Exit = relative-rank rotation only (no stop/ATR).
- Capital $100k · split_only adjustment · warmup 160 bars · cost model S1 (0.005/share, $1 min, 1 bps slippage).
- **Weekly anchor = ONE fixed weekly session, locked before week 1, never changed** (e.g. Friday-close signal). Pick it once; keep it forever.

---

## 1. Exact weekly schedule (calendar)
Run **one cycle per week**, on the same weekday every week (the locked anchor). Suggested cadence:

| When | Action |
|---|---|
| **Fri (or your locked anchor day), after session close** | Confirm a NEW weekly anchor bar exists (newer than last cycle). Run §3 only if so. |
| **Fri/Sat** | Refresh LOCAL CSVs **only when due** (see §2). Run the cycle (§3). Review kill-switch (§6). |
| **Sat/Sun** | Pre-commit checks (§5). Commit run outputs **only under a separate authorization**. |
| **Any week with no new anchor / stale data** | **Do NOT run** — log NO-TRADE (see §7). |

One cycle = one weekly rebalance. Do not run multiple cycles for the same anchor date.

---

## 2. When to refresh data
- The harness reads **operator-provided LOCAL split_only CSVs**; it does **not** fetch. Refreshing is a *separate* step.
- Default source: `refreshed_20260528` (`data/s21_weekly_rs_paper_refresh/raw`, ends **2026-05-28**).
- Refresh when the default source's `last_date` is **older than the weekly anchor you want to trade** (i.e., you need bars the current source doesn't have).
- Refreshing properly requires its **own authorization**: a RUN_BOOK + fetch workflow that (a) pulls fresh Tiingo split_only history, (b) writes a NEW dated source dir, (c) adds a new `DATA_SOURCES` entry + bumps `DEFAULT_DATA_SOURCE` in `manifest.py`. **That edits code → do not do it under this checklist alone.**
- **Never overwrite the sealed baseline** `sealed_baseline_20251230` (`read_only: True`, ends 2025-12-30). It is the immutable DR9 set and must reproduce 47/48 on overlap (BKNG re-scaled by its 25:1 2026-04-06 split).

---

## 3. When to run the cycle
Run **only** when ALL of these hold:
1. A **new weekly anchor bar** exists that is **strictly newer** than the last completed cycle's anchor (last anchor on record: **2026-05-28**, cycle 002).
2. The active data source's `last_date` **≥** the anchor you intend to trade (else stale → §7).
3. You are issuing an **explicit run authorization** this turn.

Invocation (broker-free, gated — refuses unless authorized):
```
run_weekly_paper_cycle(operator_authorized_dry_run=True, data_source="<source key>", min_last_date="<anchor date>")
```
- `operator_authorized_dry_run=True` is the gate; BUILD never sets it.
- `min_last_date` is your stale-data tripwire: if the local calendar's last bar `< min_last_date`, the run **raises `StaleDataError` (NO-TRADE)** — by design.
- Calendar misalignment across the 48 names also **raises (NO-TRADE)**.

---

## 4. Files that should be produced (per cycle)
Written under `runs/dry_cycle_NNN/` (NNN = zero-padded cycle number):
- `paper_orders.jsonl` — append-only order records for the rebalance.
- `paper_trades_closed.jsonl` — append-only closed-trade records (rotation exits).
- `killswitch_status.json` — kill-switch status + reasons for the cycle.
- `paper_weekly_report_NNN.md` — human-readable weekly report (selection, equity, costs, drawdown, gate status).

Append-only logs must only **grow**. If a prior cycle's lines change, that is a red flag — stop and investigate.

---

## 5. What to check before committing (pre-commit)
- [ ] New cycle dir `runs/dry_cycle_NNN/` contains all **four** files (§4).
- [ ] `signal_date` in the report = the intended weekly anchor; it is **newer** than the previous cycle's anchor.
- [ ] **No new anchor / stale?** Then there should be a NO-TRADE log, **not** a new cycle dir (§7).
- [ ] Selection = exactly **8** names; weights ≈ 1/8; long-only; drawn only from the locked 48 universe.
- [ ] Append-only logs grew (no edits to earlier lines); `killswitch_status.json` present and read.
- [ ] Sealed baseline untouched (`git status` clean for `data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/`).
- [ ] Mechanic unchanged vs `manifest.py` (L/S/R/top-8/equal-weight/long-only/split_only). Any drift = kill-switch (§6).
- [ ] `git status --short` shows **only** the new run files you intend to commit.
- [ ] **Commit only under a separate explicit authorization.** This checklist does not authorize commits.

---

## 6. Kill-switch review (every cycle)
Read `killswitch_status.json`. Status ladder (from `manifest.gate_thresholds`):

| Trigger | Threshold | Status |
|---|---|---|
| Drawdown warn | ≥ 15% | WARN |
| Drawdown review | ≥ 25% | REVIEW |
| **Drawdown kill** | **≥ 30%** | **TRIGGERED (halt)** |
| Annualized cost drag | > 5% / yr | TRIGGERED (halt) |
| Implementation shortfall | > 25 bps | TRIGGERED (halt) |
| Data-integrity failure | any | TRIGGERED (halt) |
| Mechanic drift from locked s21 | any | TRIGGERED (halt) |
| Trailing expectancy < 0 | persistent | REVIEW (edge divergence) |
| Manual stop | operator | TRIGGERED (halt) |

- `halt: true` → **stop the paper test.** The kill-switch **never auto-resumes**; resuming needs a deliberate operator decision and a written reason.
- REVIEW/WARN are not auto-halts but must be noted in the weekly report and watched.

---

## 7. When NOT to run (stale data / no new weekly anchor)
Do **not** create a cycle — instead log a **NO-TRADE** note — when any of these hold:
- The latest completed weekly anchor is **not newer** than the last cycle anchor (currently **2026-05-28**). No new anchor = nothing to rebalance.
- The active data source's last bar `< min_last_date` → harness raises `StaleDataError`. **Stale data is a NO-TRADE, not a reason to lower `min_last_date`.**
- Calendar misalignment across the 48 names (harness raises) → NO-TRADE / data-integrity kill.
- Any missing LOCAL CSV for a universe name (harness raises `FileNotFoundError`) → fix the data source, do not stub.

Never duplicate a cycle for an anchor already traded.

---

## 8. Evaluation milestones
Minimum sample before any milestone read (don't evaluate an under-powered sample):

| Milestone | Min closed trades | What to assess |
|---|---|---|
| **12-week** | **≥ 15** closed trades | Did the simulated edge hold? Cost drag ≤ 5%/yr? Drawdown well under kill? Any REVIEW flags recurring? Mechanic still locked? |
| **24-week** | **≥ 35** closed trades | Same, with more power. Compare realized paper behavior vs the s21 diagnostic expectation. Honest verdict only — still DIAGNOSTIC_ONLY regardless of result. |

Also honor the OOS K9 floor mindset: **≥ 50 observations/year** before leaning on any annualized read.
A "good" 12/24-week result is **not** an OOS confirmation, **not** live readiness, **not** a profitability claim, and does **not** move FRC. It is one more diagnostic data point.

---

## 9. Permanent reminders (non-negotiable)
- **No broker. No live trading. No paper-via-broker. No network/fetch by the harness. No API keys.**
- **No parameter tuning, no universe change, no cadence tuning** — the mechanic is locked.
- **FRC = NEVER_GRANTED · trading = PAUSED · live = BLOCKED_AT_6_GATES · label = DIAGNOSTIC_ONLY.**
- Sealed artifacts and the read-only baseline are never overwritten.
- Every action (run, refresh, commit, push) is its **own** explicit authorization. When a guard fires, respect it — don't engineer around it.
