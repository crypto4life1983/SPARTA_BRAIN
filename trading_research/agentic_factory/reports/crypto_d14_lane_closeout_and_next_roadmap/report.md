# Crypto-D14 — Crypto Lane Closeout + Next-Roadmap Memo (memo only)

**This is a CLOSEOUT + ROADMAP MEMO only.** No code, no backtest, no IS/OOS run, no
data fetch, no network, no exchange API, no broker, no paper/live, no new crypto
strategy started. No 2024/2025/2026 usage beyond reading committed reports. Frozen
data untouched. S30/futures untouched; JARVIS/`templates/base.html`/hydra untouched.
**Not staged, not committed.**

- **Created:** 2026-05-30
- **HEAD at memo:** `52cd272` — descendant of D13 `b9180ea`; the only intervening
  commit is unrelated background automation ("JARVIS Step 47 snapshot"). Factory tree
  clean; nothing staged; **no active crypto strategy** (both branches PARKED).

---

## 1. Crypto lane summary

| Phase | Steps | Commit(s) | Outcome |
|---|---|---|---|
| Protocol | D1 | — | Separate crypto lane; BTC primary; spot-first (perps blocked); daily-first (4H deferred); same factory ladder; IS 2020–2023 / OOS 2024–2025 / 2026 sealed |
| Inventory | D2 | — | Old BTC/ETH/SOL/XRP bots classified **historical-only**; no curve/parameter carryover |
| Data | D3/D3a/D3b/D3c | freeze `5b3d94c`, ratified `fe5594f` | Immutable SHA256-pinned 2026-sealed BTC/ETH/SOL spot daily snapshot; QA CLEAN; `DATA_READY` |
| CODR-1 | D4/D5/D6 | spec `5552356`, engine `4614190`, IS `27b0620` | **IS_FAIL** |
| CODR-1 closeout | D7 | `344a7e7` | PARKED; recommend density audit |
| Density audit | D8 | `ca4d9eb` | Only unfiltered crash candle is ≥30 on BTC + regime-diverse; select for strict spec attempt |
| CCR1 | D9/D10/D11 | spec `6e0c85b`, engine `ce499c6`, IS `923e786` | **IS_WATCH** |
| CCR1 OOS | D12/D13 | protocol `8b14308`, result `b9180ea` | **OOS_FAIL** |

- **D1 protocol** — established the lane and standing rules (BTC primary + ETH/SOL
  corroboration; spot first; daily first; 2026 sealed; one-shot OOS vs committed hash;
  old work is context, never evidence).
- **D2 inventory** — all prior crypto work classified historical-only; any reuse must
  be re-frozen as a new spec.
- **D3/D3a/D3b/D3c data** — provenance pinned (Binance public spot daily USDT), then an
  immutable factory snapshot (BTC/ETH 2192 rows, SOL 1969 partial from 2020-08-11),
  2026 sealed out (149 rows/symbol excluded), SHA256-pinned, QA CLEAN, ratified.
- **D4/D5/D6 CODR-1 path** — `close>SMA200 AND ret≤−7%` dip-in-uptrend; spec → engine →
  IS-only run → **IS_FAIL**.
- **D7/D8/D9/D10/D11/D12/D13 CCR1 path** — closeout + density audit selected the
  **unfiltered** `ret_1d≤−5%` crash candle; spec (CCR1 v1) → engine+18 tests → IS_WATCH
  → OOS protocol → **OOS_FAIL** (run once).

## 2. Final strategy statuses

| Strategy | Status | Cause |
|---|---|---|
| **CODR-1 v1** | **PARKED after IS_FAIL** | BTC primary lost after costs (9 trades, net −4.93%), below trade-count gate, net PF<1.3, top-3 removal failed all symbols; bull-only |
| **CCR1 v1** | **PARKED after OOS_FAIL** | Top-3 removal flipped BTC (−12.21%) and combined (−13.60%) negative OOS; ETH net-negative both OOS years |
| **Any crypto strategy** | **NONE validated** | No crypto strategy is validated, paper-ready, or live-ready |

## 3. What worked

- A **separate crypto lane** was created and kept strictly isolated from futures
  validation claims.
- An **immutable, SHA256-pinned, 2026-sealed** BTC/ETH/SOL spot daily snapshot was
  built **read-only** (no fetch), QA CLEAN.
- **Provenance pinned** (vendor / endpoint-family / market / quote / interval / timezone
  / retrieval) with machine + human sidecars.
- **Factory discipline enforced** end-to-end: preflight ancestry checks,
  explicit-pathspec commits (never `git add .`), scoped tests, STOP-and-report.
- **OOS was protected** behind a committed pre-registration protocol (D12) before any
  2024–2025 bar was read.
- **OOS was run exactly once** (D13) — no reruns, no variants, no post-OOS tuning.
- **The top-3-winner-removal gate did its job** — it caught CCR1's hidden winner
  concentration OOS that the headline +45.29% combined net hid; the same gate that
  parked every futures branch.

## 4. What failed

- **CODR-1 failed** because BTC primary was **weak and too sparse**: the `close>SMA200`
  confirmation starved BTC to 9 IS events (zero in the 2022 bear), produced a negative
  after-cost BTC primary, and made it a **bull-regime-dependent** dip-buyer. Pooling
  could not rescue the primary.
- **CCR1 failed OOS** because **top-3 removal flipped BTC and combined negative**
  (−12.21% / −13.60%) and ETH was net-negative both OOS years. The unfiltered crash
  signal had the trade count D8 promised (BTC 18 OOS) but the edge was three trades wide.
- **Structural finding:** **daily-spot crash/reversion edges may be too
  top-winner-dependent.** Filtered → too sparse on BTC (CODR-1); unfiltered → enough
  count but winner-concentrated and not OOS-robust (CCR1). The daily-spot crash/reversion
  family is effectively **exhausted at v1**.

## 5. Lessons

- **BTC primary must carry its own evidence** — positive, friction-survivable,
  winner-robust; never a passenger.
- **ETH/SOL cannot rescue BTC** — read gates per-symbol first, pooled second (held
  across CODR-1 IS and CCR1 OOS).
- **Top-3 dependence is still the killer** — parked every futures branch, 2/3 of
  CODR-1's symbols, and now CCR1 OOS.
- **Daily crypto faces a density/edge squeeze** — a filter strong enough to give a
  defensible edge starves BTC below the ≥30 gate; the unfiltered signal has count but
  weak/non-robust edge. Crypto may need **better causal filters OR a more frequent
  timeframe**.
- **Confirmation filters reduce count** (SMA200 cut BTC −7% events from 30 → 9, zero in
  2022).
- **Unfiltered signals have count but weak edge proof** (CCR1: 18 BTC OOS trades, ex-top-3
  negative).
- **Perps remain blocked** until funding-rate data is sourced and funding rules frozen —
  ignoring funding manufactures an optimistic, wrong edge.

## 6. Next-roadmap options

| Option | Why it helps | Risk | Data needed | Verdict |
|---|---|---|---|---|
| **A. Crypto-4H protocol/data lane** | Addresses root cause: more bars/day → density to **afford a real filter** without starving BTC. This is the D8 `NEEDS_4H_DATA` fallback, now triggered. | Path-dependency + microstructure noise; heavyweight new freeze + full ladder; 4H winners may still concentrate. | New immutable SHA256-pinned BTC/ETH/SOL **4H** spot snapshot, governed like D3b. | **RECOMMENDED research direction (after hygiene)** |
| **B. New daily crypto hypothesis** | Cheapest — reuses frozen daily data. | D7/D8 already enumerated daily families; each is structurally defective (param-freedom / top-winner / low BTC power / friction). | None new. | **NOT recommended** — idea space picked over |
| **C. Perp protocol with funding** | Funding/basis mechanics + liquidity; funding can be signal. | Needs funding data frozen first; ignoring funding = wrong edge; perps BLOCKED until funding rules frozen. | Provenance-pinned funding-rate history, frozen. | **NOT recommended yet** — gated behind funding data |
| **D. Return to futures research** | Most mature lane/ladder. | All futures branches + S30 parked on the same gate; no fresh hypothesis queued; abandons crypto question. | None for revisits. | **NOT recommended now** — no queued edge |
| **E. Repo hygiene/config fix first** | A standing red test + automation HEAD-racing erode trust in the test/commit signal that the whole factory depends on. | Low; must stay surgical, not cover for logic change. | None. | **RECOMMENDED FIRST** |

## 7. Final recommendation

### **REPO_HYGIENE_FIRST** → then **CRYPTO_4H_PROTOCOL_NEXT**

The crypto research question is well-posed and **will not go stale**: the frozen daily
data and all lessons are committed, and the next research direction (4H) is already
identified by the D8 `NEEDS_4H_DATA` fallback now that the unfiltered daily crash family
has failed OOS. There is therefore **no urgency cost** to fixing hygiene first.

Two standing defects argue for hygiene **before** opening a heavyweight new 4H lane:

1. **A persistently-red config test** —
   `test_config_wiring.py::test_load_config_includes_strategy_block` (`session_start`
   `09:30` vs expected `14:30`) has forced a **"1 failed" caveat in every crypto report
   since D3b**. A perpetually-red suite trains readers to ignore failures — exactly how a
   real regression slips through — and erodes the test signal the factory's entire value
   rests on.
2. **Recurring background-automation / JARVIS HEAD-racing** — it advanced HEAD between
   D13 and D14, previously **committed a D9 deliverable before approval**, and staged
   JARVIS files outside the factory during D11 preflight. This complicates every preflight
   and is a governance hazard for a commit-discipline factory.

Opening a fresh multi-step 4H data + ladder lane on top of an unstable base **compounds
risk**. Fix the test signal and stabilise the commit/HEAD-race surface first, **then**
proceed to **CRYPTO_4H_PROTOCOL_NEXT** as the recommended research direction.

> **This memo authorizes nothing operational.** Neither the hygiene work nor the 4H
> protocol is started or authorized here; each needs a separate explicit instruction.

## 8. Forbidden actions (this lane)

`no_live_trading` · `no_paper_trading` · `no_exchange_api_execution` ·
`no_perps_until_funding_frozen` · `no_oos_reruns` · `no_tuning_of_failed_specs` ·
`no_mixing_crypto_with_futures_validation_claims` · `no_data_fetch` · `no_network` ·
`no_broker` · `no_optimization` · `no_modification_of_frozen_data` ·
`do_not_touch_s30_or_futures` · `jarvis_templates_base_hydra_untouched` · `no_staging` ·
`no_commit`.

## 9. Final line

**"Crypto-D14 is a closeout and roadmap memo only; no crypto strategy is validated,
paper-ready, live-ready, or authorized for execution."**

---

**Trading recommendation:** NONE — closeout + roadmap memo only. **CODR-1 is PARKED
after IS_FAIL; CCR1 is PARKED after OOS_FAIL; no crypto strategy is validated,
paper-ready, or live-ready.** The daily-spot crash/reversion family is exhausted at v1
(top-winner dependence). Recommendation is **REPO_HYGIENE_FIRST** — fix the standing
config-test failure and stabilise the automation/HEAD-race surface — **then**
**CRYPTO_4H_PROTOCOL_NEXT** as the next research direction. OOS 2024–2025 was used once
and is spent for CCR1; 2026 stays sealed; perps remain blocked; crypto stays a separate
research lane; **S30 stays PARKED and the futures branches are untouched.**
