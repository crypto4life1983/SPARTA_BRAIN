# SPARTA Strategy Factory v1 — Launch Bundle 001 (INVENTORY + MAP + BUILD PLAN · DOC ONLY)

**This is a documentation/inventory/plan bundle only.** No code written, no engine
or test changed, no backtest, no IS/OOS run, no optimization, no parameter change,
no data fetch, no network, no broker, no exchange API, no paper/live, no strategy
mutation, no staging, no commit. Every section below is synthesized from already
committed factory reports, engines, tests, configs, and the brain-memory record —
nothing was re-run.

- **Created:** 2026-05-30
- **Baseline (JARVIS Bundle B):** `e398f5afaf85d47d0c04fc8d6be24a5b9fbdbc14`
  (verdict `READY_FOR_STRATEGY_FACTORY_V1`)
- **HEAD at bundle:** `06cfad7` (Repo-Hygiene-D4 branch/worktree transition plan)
- **Scope:** Strategy Factory v1 launch as a **separate additive research lane**.
- **Verdict:** **`FACTORY_V1_NEEDS_HYGIENE_FIRST`** (see §9).

---

## 1. Executive summary

The Strategy Factory already exists as a **proven, manual, offline validation
ladder** at `trading_research/agentic_factory/`. Across two lanes (futures + crypto)
it has put **8 strategies** through the ladder and **parked all 8** — 0 promoted,
0 paper-ready, 0 live-ready, OOS protected throughout. The reusable validation core
(Factory D1–D11) is built and its test suite is **green (329 passed / 0 failed)**;
the long-standing red config test was fixed at `102202a`.

What does **not** yet exist is the thing this bundle is named for: an **automated
overnight discovery system**. Today the ladder runs **prompt-by-prompt, by hand**.
There is no autonomous orchestrator chaining the modules, no canonical candidate
registry file, no hypothesis queue, and — critically — no process isolation. The
factory still shares one `master` branch and one working tree with a concurrent
JARVIS workstream that races HEAD between turns. An unattended overnight loop that
writes and commits would be **maximally exposed** to exactly that race.

Therefore: the validation core is ready, but two structural prerequisites for
*automation* are unmet (process isolation + the orchestration layer itself). The
honest verdict is **build hygiene first, then the overnight orchestrator** —
consistent with the standing Crypto-D14 `REPO_HYGIENE_FIRST` recommendation and the
Repo-Hygiene-D4 worktree-first plan.

---

## 2. Inventory — what exists today

### 2.1 Validation core (reusable ladder · Factory D1–D11, BUILT)

| Engine file | Role | Origin |
|---|---|---|
| `engine/validation_reports.py` | Standard `make_report` / `validate_report` / refuse-before-write `write_report` → `report.json`+`report.md` | D2 |
| `engine/validation_is_runner.py` | IS-only runner; hard 2023/2024/2025 OOS seal at path **and** bar-date layers | D3 |
| `engine/validation_oos_runner.py` | OOS enforcement; refuses OOS without committed protocol hash; one-shot; blocks IS years + 2026 | D4 |
| `engine/validation_entry_significance.py` | Same-count random-entry permutation over FIXED horizons (no horizon shopping) | D5 |
| `engine/validation_sequence_risk.py` | Trade-order shuffle + bootstrap + top-winner dependence (S25 path-luck lesson) | D6 |
| `engine/validation_regime.py` | Vol/trend/year regime + concentration breakdown | D7 |
| `engine/validation_walk_forward.py` | Rolling-window stability; shared weak windows | D7 |
| `engine/validation_friction.py` | Low/moderate/high/severe R-cost; break-even friction; IS **and** OOS at each level | D7 |
| `engine/validation_decision.py` | Maps per-module verdicts → one research decision + one readiness tier; paper/live unreachable by default | D8 |
| `engine/validation_cli.py` | Safe discovery CLI: `list-modules` / `describe` / `synthetic-smoke` / `synthetic-e2e` / `version`; **no dynamic import, no real-data run, no paper/live command** | D9 |
| `engine/validation_synthetic_smoke.py` | Fake in-memory data drives the full ladder end-to-end; no real market data | D10 |

### 2.2 Strategy engines (frozen, per-branch)

- **Futures lane:** `donchian_daily.py`, `trend_sr_ema_rsi_daily.py` (S26),
  `s27_mean_reversion_bull.py`, `s28_breakout_retest.py`,
  `s29_failed_breakout_reversal.py`, `s30_overnight_drift.py`.
- **Crypto lane:** `crypto_codr1.py` (CODR-1), `crypto_crash_candle_reversion.py` (CCR1).
- **Original NQ-ORB loop primitives:** `backtester.py`, `metrics.py`, `decision.py`,
  `proposer.py`, plus `data_quality.py`, `signal_significance.py`.

### 2.3 Original orchestration (legacy, NOT wired to the ladder)

- `loop/factory_loop.py` — the first-generation single-pass loop
  (`proposer → backtester → metrics → report → decision`) for NQ ORB only. It is
  **not** connected to the validation ladder, the candidate registry, or the
  per-branch engines. It is the only orchestrator in the tree but does not perform
  multi-stage validation.

### 2.4 Config

- `config/factory_config.yaml` — NQ ORB params + decision thresholds
  (`min_trades 30`, continue `PF≥1.30 / win≥0.40 / DD≤25%`, park `PF≥1.00`,
  else kill). Session times in UTC (14:30–21:00 = RTH ET).

### 2.5 Tests

- **329 passed / 0 failed** (full factory suite, run 2026-05-30). Coverage spans
  every validation module, every strategy engine, data-quality, decision, safety
  guards, and config wiring. The previously-red
  `test_config_wiring::test_load_config_includes_strategy_block` was fixed at
  `102202a` (now resolves the config path the way production does).

### 2.6 Data inventory (offline only)

- **Futures (`data_offline/`):** NQ daily **2013–2025** (full IS+OOS), ES daily
  **2013–2025**, MNQ + MES daily **2019–2025** (micros, proxy-only), NQ 1-minute
  (2013 + a Christmas-week slice), `nq_orb_sample.csv`.
- **Crypto (`data_crypto/spot_binance_usdt_1d_2020_2025/`):** BTC/ETH/SOL daily spot
  USDT 2020–2025, SHA256-pinned, provenance-pinned, **2026 sealed out**, QA CLEAN.

### 2.7 Observation layer (read-only, outside the factory)

- JARVIS Bundle B (`e398f5a`) added 4 read-only status panels — `factory_status`,
  `survival_ledger`, `candidate_registry`, `freshness_guard` — pinning
  `paper_ready/live_ready/broker_control = false` and `deployment_status =
  RESEARCH_ONLY`. It opens only `report.json` files, runs no factory job, writes
  nothing, and did **not** open Factory v1.

---

## 3. Strategy Factory v1 map

### 3.1 Two separate lanes (must stay separate)

```
                          SPARTA STRATEGY FACTORY v1
                                     │
        ┌────────────────────────────┴────────────────────────────┐
   FUTURES LANE                                              CRYPTO LANE
   data_offline/ (NQ/ES/MNQ/MES daily)                data_crypto/ (BTC/ETH/SOL daily spot)
   IS 2013–2022 · OOS 2023–2025 · 2026 sealed         IS 2020–2023 · OOS 2024–2025 · 2026 sealed
   primary NQ; ES independent; micros proxy-only      primary BTC; ETH/SOL corroboration only
   spot-only; perps BLOCKED until funding frozen
        └────────────────────────────┬────────────────────────────┘
                                     │
                       SHARED VALIDATION LADDER (A–L)
```

### 3.2 IS/OOS protocol flow (the ladder)

| ID | Module | Hard rule |
|---|---|---|
| A | `spec_check` | Frozen spec + locked params + branch/commit recorded; blocks later modules if not frozen |
| B | `is_baseline` | IS window only; **OOS files refused** at path + bar-date layers |
| C | `oos_protocol` | Pre-register pass/watch/fail **and commit** BEFORE OOS |
| D | `oos_run` | Run OOS **once**; protocol hash must match a commit |
| E | `entry_significance` | Real entries vs same-count random-in-regime; fixed horizons |
| F | `sequence_risk` | Trade-order MC + bootstrap + top-winner dependence |
| G | `regime_breakdown` | Vol/trend/year + concentration; flag single-year/regime dominance |
| H | `multimarket` | NQ primary, ES independent, micros proxy-only (never independent) |
| I | `walk_forward` | Rolling windows; shared weak windows surfaced |
| J | `friction_stress` | Low→severe R-cost; break-even friction; IS **and** OOS |
| K | `readiness_gate` | Map evidence → readiness tier |
| L | `final_decision` | Final disposition |

### 3.3 Pass / fail / watch rules

- **IS_FAIL ⇒ full STOP / PARK** — never advance to OOS; never tune in place. Any
  change is a brand-new branch with a fresh frozen spec.
- **Top-3 / top-1% winner-removal gate** — a record carried by a few fat-tail
  winners is rejected even if headline net is positive. This single gate parked
  every futures branch and CCR1 OOS.
- **Trade-count floor** (≥30) and **PF gates** (continue ≥1.30, park ≥1.00, else
  kill).
- **OOS one-shot** vs a committed protocol hash; no reruns, no post-OOS tuning.
- **Per-symbol before pooled** — primary instrument (NQ / BTC) must carry its own
  evidence; corroborators cannot rescue it.
- **Readiness tiers (K):** `BLOCKED → RESEARCH_CANDIDATE → VALIDATION_CANDIDATE →
  PAPER_REVIEW_CANDIDATE → PAPER_READY → LIVE_READY` (paper/live unreachable on the
  default path; require a separate readiness memo with explicit override fields).
- **Final verdicts (L):** `CONTINUE · PARK · FAIL · REDESIGN_REQUIRED`.

### 3.4 Candidate registry (current known pass/fail decisions)

| Lane | Branch | Strategy | Verdict | Status |
|---|---|---|---|---|
| Futures | Donchian | Donchian System-1 daily | reference baseline only; `ENTRY_EDGE_NOT_SUPPORTED` + sequence-fragile | **PARKED** |
| Futures | S26 | Trend + S/R + EMA/RSI | `PARK_CANDIDATE` (OOS passed but thin/`FRICTION_SENSITIVE`, single-year-dominated) | **PARKED** |
| Futures | S27 | Mean-reversion in bull trend | `IS_FAIL` | **PARKED** |
| Futures | S28 | Breakout-retest + vol expansion | `IS_FAIL` | **PARKED** |
| Futures | S29 | Failed-breakout reversal | `IS_FAIL` | **PARKED** |
| Futures | S30 | Overnight drift (long) | `IS_FAIL` (data-representativeness caveat) | **PARKED** |
| Crypto | CODR-1 | Dip-in-uptrend (close>SMA200 & ret≤−7%) | `IS_FAIL` (BTC starved to 9 events) | **PARKED** |
| Crypto | CCR1 | Unfiltered crash-candle reversion | `OOS_FAIL` (top-3 removal flips negative) | **PARKED** |

**Totals: 8 tested · 0 promoted · 0 paper-ready · 0 live-ready · OOS protected on all.**
There is **no canonical candidate-registry file** in the factory tree — the registry
above is reconstructed from per-branch reports (JARVIS Bundle B reconstructs a
read-only view from `data/profit_brain_strategy_survival.json`).

### 3.5 Overnight-run design (target — NOT built)

An automated overnight discovery system would (offline, inert) loop:

```
hypothesis queue → freeze spec (A) → IS baseline (B)
   └─ IS_FAIL → auto-PARK + decision record, next hypothesis
   └─ IS pass → register+commit OOS protocol (C) → one-shot OOS (D)
        └─ run E–J → readiness gate (K) → final decision (L)
   → write uniform report.json/.md per module into an isolated worktree
   → STOP for human review at any PARK/PROMOTE boundary (never auto-promote)
```

This requires an orchestrator that does **not** exist yet (see §4).

---

## 4. Existing vs missing (gap analysis)

### 4.1 Already exists (green)

- ✅ Reusable validation ladder modules (A–L equivalents) — D2–D8.
- ✅ Hard OOS seals (path + bar-date), one-shot OOS, committed-protocol gate.
- ✅ Anti-overfit gates (top-3/top-1% winner removal, per-symbol-first, IS-fail-stops).
- ✅ Standard report schema + refuse-before-write writer.
- ✅ Safe discovery CLI + synthetic end-to-end smoke.
- ✅ Frozen, QA-clean, provenance-pinned data for both lanes.
- ✅ Green test suite (329/0) — config-test regression fixed.
- ✅ Read-only observation layer (JARVIS Bundle B).

### 4.2 Missing for an *automated overnight* system (red)

1. **Orchestrator.** `engine/validation_runner.py` + `engine/validation_gates.py`
   were proposed in Factory-D1 §9 but **never built**. Only per-module functions +
   a discovery CLI exist; nothing chains A→L automatically with gating between
   stages. `loop/factory_loop.py` is the legacy NQ-ORB single-pass and is not wired
   to the ladder.
2. **Canonical candidate registry file.** No structured factory-owned registry of
   branches/specs/verdicts/commits exists; it is reconstructed ad hoc.
3. **Hypothesis queue / proposer for structural ideas.** `proposer.py` only does NQ
   ORB parameter search. Structural hypotheses (S26–S30, CODR/CCR) were sourced by
   hand. An overnight system needs a queued, frozen-spec backlog — not a parameter
   optimizer (which is explicitly forbidden).
4. **Process isolation.** Factory still shares one `master` branch + one working
   tree with the JARVIS workstream that races HEAD between turns. The dedicated
   `factory-research` worktree is **planned (D4) but NOT created**.
5. **Automation commit-guard.** Repo-Hygiene-D3 is **plan/memo only** — explicit
   pathspec commits are still enforced by manual discipline, not an enforced guard.
6. **Safe dynamic strategy registration.** The CLI explicitly forbids dynamic import
   (D9). An overnight runner needs a vetted, allow-listed registration mechanism to
   load frozen engines without arbitrary code execution.

### 4.3 Hygiene status

- ✅ **D2 config test** — FIXED at `102202a` (suite green).
- ⚠️ **D3 commit-guard** — PLAN only; not built.
- ⚠️ **D4 worktree isolation** — PLAN only; worktree NOT created (blocked by a dirty
  shared tree carrying in-flight JARVIS files; a plain `git switch -c` cannot isolate
  two sessions in one worktree).
- ⚠️ **P2 hydra junk path** (`'hydra '` at repo root) — cosmetic `git status`
  warning; outside the factory; cleanup deferred & unauthorized.

---

## 5. Minimum build plan to reach automated overnight discovery

Smallest safe path, each step separately authorized, all offline/inert/read-only of
external systems. **Hygiene block first**, then **orchestration block**.

### Block H — Hygiene (do first)

| Step | Scope | Output |
|---|---|---|
| **H1** | Create the isolated worktree per Repo-Hygiene-D4 (`git worktree add ../sparta-factory-research -b factory-research/...`) so the overnight loop has its own index/tree and cannot race JARVIS HEAD. | Isolated worktree |
| **H2** | Land the Repo-Hygiene-D3 commit-guard (explicit-pathspec wrapper / advisory lock) so automated commits are race-proof by construction, not by manual discipline. | Commit guard |

### Block O — Orchestration (after H)

| Step | Scope (code) | Hard rule |
|---|---|---|
| **O1** | `engine/validation_runner.py` — chain A→L for ONE frozen engine, gating between stages; uniform reports. | No optimization; no auto-promote; STOP at PARK/PROMOTE |
| **O2** | `engine/validation_gates.py` — encode pass/watch/fail floors (top-3 gate, count, PF, single-year, friction) as reusable assertions. | Floors pre-registered before results |
| **O3** | `candidate_registry.json` (factory-owned) + writer — append-only branch/spec/verdict/commit ledger. | Append-only; never edits a sealed verdict |
| **O4** | `hypothesis_queue.md/json` — queued frozen-spec backlog; structural ideas only. | No parameter sweeps; specs frozen before run |
| **O5** | Safe strategy-registration allow-list (no dynamic import of arbitrary code). | Explicit registry; vetted engines only |
| **O6** | Overnight batch entrypoint (manual-start, offline) that walks the queue → runner → registry, writing into the isolated worktree. | No network/broker/scheduler-daemon; human review gate at each PARK/PROMOTE |
| **O7** | Tests for runner/gates/registry/queue + a synthetic overnight dry-run. | Suite stays green |

**Standing constraints (all steps):** offline-only, no network, no broker/exchange
API, no paper/live, no order placement, no secret access, no strategy mutation
without protocol, futures and crypto stay separate, OOS one-shot vs committed hash,
paper/live tiers unreachable without a separate readiness memo, explicit-pathspec
commits only.

---

## 6. Why NEEDS_HYGIENE_FIRST (not READY_TO_BUILD, not BLOCKED)

- **Not BLOCKED:** the validation core is built and proven, tests are green, data is
  frozen/QA-clean for both lanes, the OOS discipline held across 8 branches, and the
  config-test regression is fixed. Nothing fundamental prevents building v1.
- **Not READY_TO_BUILD (yet):** an *automated overnight* system is, by definition,
  unattended and commit-writing — the single worst exposure to the documented
  JARVIS HEAD-race. Process isolation (D4 worktree) and the commit-guard (D3) are
  **planned but not built**. Building an autonomous loop on top of a shared,
  race-prone `master` working tree compounds the exact governance hazard every
  factory report has been working around by hand.
- **Therefore NEEDS_HYGIENE_FIRST:** finish Block H (H1 worktree + H2 commit-guard),
  then proceed to Block O. This matches the standing Crypto-D14
  `REPO_HYGIENE_FIRST → next-research` ordering and the Repo-Hygiene-D4 worktree-first
  plan.

---

## 7. Safety attestations (this bundle)

`doc_only` · `no_code` · `no_engine_or_test_change` · `no_backtest` ·
`no_is_oos_run` · `no_optimization` · `no_parameter_change` · `no_data_fetch` ·
`no_network` · `no_broker_or_exchange_api` · `no_paper_or_live` ·
`no_strategy_mutation` · `futures_crypto_lanes_kept_separate` ·
`existing_reports_used_first` · `jarvis_observation_only_untouched` ·
`frozen_data_untouched` · `s30_and_all_parked_branches_read_only` · `no_staging` ·
`no_commit`.

## 8. Forbidden actions (carried into any follow-up build)

`no_live_trading` · `no_broker` · `no_paper_trading_execution` · `no_exchange_api` ·
`no_strategy_mutation_without_protocol` · `no_oos_reruns` ·
`no_tuning_of_parked_specs` · `no_auto_promotion` · `no_dynamic_arbitrary_import` ·
`no_mixing_futures_and_crypto_validation_claims` · `no_perps_until_funding_frozen` ·
`no_git_add_dot` · `explicit_pathspec_commits_only`.

## 9. Final verdict

# **`FACTORY_V1_NEEDS_HYGIENE_FIRST`**

The Strategy Factory validation core is built, proven, and test-green; data is
frozen for both lanes and OOS discipline has held across 8 parked branches. But the
**automated overnight discovery system** named by this bundle does not exist, and
its two structural prerequisites — **process isolation (D4 worktree, H1)** and the
**automation commit-guard (D3, H2)** — are still plan-only. Build the hygiene block
first, then the orchestration block (validation_runner + gates + candidate registry
+ hypothesis queue + safe registration + manual-start overnight batch).

---

**Trading recommendation:** NONE. Inventory/map/plan bundle only. All 8 branches
(Donchian, S26, S27, S28, S29, S30, CODR-1, CCR1) remain PARKED; no active strategy;
no paper/live system exists or is authorized; OOS remains sealed; the overnight
orchestrator is not built. Next allowed action: Hygiene Block H (H1 isolated
worktree, then H2 commit-guard), each separately authorized.
