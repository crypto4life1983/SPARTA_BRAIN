# SPARTA Strategy Factory v1 — Research-Only Automation Backbone (PLAN ONLY)

- **Plan id:** `strategy_factory_v1_plan`
- **Plan version:** `v1`
- **Plan date:** 2026-06-03
- **Official master at plan time:** `3bd2633d0236fcc18dc30a7965c37eaf6bb4353b`
- **Status:** `PLAN_ONLY_NOT_EXECUTED`
- **This document authorizes nothing.** No code, no dashboard change, no
  backtest, no dataset change, no broker/exchange/order/fetch path, no
  paper/live trading, no ACTIVE/STRONG promotion, no Bundle 23. See the
  non-authorization statement in §14.

> Relationship to existing work: a **read-only routine layer already exists**
> (`tools/strategy_factory_routines.py` →
> `reports/strategy_factory_routines/{candidate_registry,strategy_queue,daily_state,weekly_review}/`).
> Strategy Factory v1 **builds on that layer**; it does not replace or duplicate
> it. The routine layer summarizes existing reports; the Factory adds the
> *queue → orchestrator → runner-adapter → report → decision-memo → registry →
> dashboard-feed* backbone with a hard safety-gate contract. Reuse first.

---

## 1. Current state summary

- **Official master:** `3bd2633` (read-only JARVIS Crypto-D1 Lane Monitor shipped).
- **Crypto-D1 Momentum Confirmation v1:** EXECUTED (run_id `2a3be425522a04ec`).
- **Current best candidate:** **Crypto-D1 Momentum N=20** — OOS positive and
  floor-backed on all three assets (BTC 32 / ETH 31 / SOL 23 trades, floor 20);
  N=30 positive but floor-backed on BTC only (ETH 19 / SOL 18 sample-thin).
- **Status:** **WATCH / MIXED**.
- **Readiness:** **NOT_READY_FOR_REAL_DATA**.
- **JARVIS Lane Monitor:** read-only, dynamic, committed (`3bd2633`); scans
  committed plan → executed result → decision-memo artifacts and hard-clamps the
  four authorization flags to false.
- **No paper/live authorization** anywhere. No broker, exchange, order, or fetch
  path exists in the research stack.
- **Existing assets to reuse:** `tools/crypto_d1_backtest_runner.py` (the only
  in-scope runner), the frozen `CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V002` dataset,
  the candidate registry, and the routine-layer queue.

---

## 2. Strategy Factory v1 purpose

**This is not a live trading bot.** It is a deterministic, **research-only
automation factory** that takes *already-approved* experiments off a queue,
runs them through an *allow-listed* offline runner against *frozen* data, and
emits standard reports, decision memos, and a machine-readable registry that
JARVIS can display.

The single goal is to **remove manual copy-paste** from the research loop —
turning the current "human runs the runner by hand, pastes results, updates
notes" workflow into a gated, auditable pipeline. It changes *who types the
commands*, not *what is allowed to happen*. Every existing safety property
(offline, frozen data, WATCH ceiling, no promotion) is preserved and made
machine-enforced rather than convention-enforced.

---

## 3. Proposed components

1. **Strategy Report Registry v1** — the single source of truth. A JSON file
   (plus rendered MD) listing every known research strategy with its latest
   resolved verdict, run_id, report path, decision-memo path, safety flags, and
   next action. Built by *scanning existing committed reports* (read-only) and
   updated additively after each orchestrated run.
2. **Research Queue v1** — a human-authored, version-controlled JSON backlog of
   approved research tasks. Nothing runs that is not on the queue **and** marked
   `approved_for_research: true` with zero `blocked_reasons`.
3. **Research-only Orchestrator v1** — reads the queue, validates each item
   against the Safety Gate Contract, and (only in execute mode, separately
   approved) invokes the allow-listed runner. Default mode is **dry-run**:
   validate + plan + write a manifest, run nothing.
4. **Runner Adapter layer** — a thin, explicit allow-list mapping
   `allowed_runner` → a known offline runner entry point (initially only
   `crypto_d1_backtest_runner`). Unknown runners are rejected; the adapter never
   constructs broker/exchange/order/fetch calls.
5. **Auto Decision Memo v1** — after an executed run, generate a *draft*
   decision memo (verdict echo, sample-sufficiency nuance, recommended next
   checkpoint) marked `requires_operator_signoff: true`. It records, it never
   promotes.
6. **Dashboard Registry Feed** — a read-only adapter that exposes the registry
   to JARVIS (same pattern as the shipped Lane Monitor: GET-only, hard-false
   authorization flags, forbidden verdicts clamped).
7. **Safety Gate Contract** — a single declarative config
   (`configs/strategy_factory_safety.json`) that every component loads and
   enforces; the orchestrator refuses to act if the contract is missing,
   malformed, or weakened.
8. **Failure Classifier** — deterministic mapping of run/validation outcomes to
   a small closed vocabulary (`QUEUE_REJECTED`, `SAFETY_BLOCKED`,
   `RUNNER_NOT_ALLOWED`, `RUN_ERROR`, `REPORT_MISSING`, `OK_WATCH`,
   `OK_FAIL`), never emitting PASS/ACTIVE/STRONG.
9. **Audit / Run Manifest** — every orchestrator invocation writes a manifest
   (inputs, resolved safety flags, runner, dataset hash, start/stop, outcome,
   classifier label) so any run is fully reconstructable from disk.

---

## 4. File architecture (future — NOT created by this plan)

```
tools/
  strategy_factory.py                 # orchestrator + CLI (dry-run default)
  strategy_report_registry.py         # read-only scanner + additive updater
configs/
  research_queue.json                 # human-authored approved backlog
  strategy_factory_safety.json        # declarative safety-gate contract
reports/
  strategy_factory_v1_plan/
    report.md                         # THIS plan (human)
    report.json                       # THIS plan (machine)
  strategy_factory_registry/
    registry.json / registry.md       # generated registry (future runs)
  strategy_factory_runs/<run_id>/
    manifest.json                     # generated per-run audit manifest (future)
    decision_memo.md                  # generated draft memo (future)
tests/
  test_strategy_factory_registry.py
  test_strategy_factory_queue.py
  test_strategy_factory_safety.py
  test_strategy_factory_orchestrator.py
```

Notes:
- `configs/` does **not** exist yet; it would be created by a future step.
- All new tools are **Python standard library only**, matching
  `crypto_d1_backtest_runner.py` and `strategy_factory_routines.py`.
- Nothing in this list is created by the present plan except the two plan files.

---

## 5. Data flow

```
configs/research_queue.json
        │  (human-approved, version-controlled)
        ▼
tools/strategy_factory.py  ──loads──►  configs/strategy_factory_safety.json
        │   1. validate each queue item against the safety contract
        │   2. fail closed on any violation (skip item, record reason)
        ▼
Runner Adapter (allow-list)  ──►  tools/crypto_d1_backtest_runner.py  (offline, frozen data)
        │   (execute mode only; dry-run default writes a plan + manifest, runs nothing)
        ▼
reports/crypto_d1_*/.../<report>.json   (standard runner output, WATCH ceiling)
        ▼
tools/strategy_report_registry.py  ──►  reports/strategy_factory_registry/registry.json
        │   (additive update: verdict, run_id, report_path, safety_flags, next_action)
        ▼
Auto Decision Memo (draft, requires_operator_signoff=true)
        ▼
Dashboard Registry Feed  ──►  JARVIS /api/jarvis/status (read-only, GET, clamped)
```

Every arrow is one-directional and read-or-append-only downstream of the queue.
The orchestrator never writes upstream of itself (never edits the queue or the
safety contract) and never mutates frozen datasets.

---

## 6. Safety gates

`configs/strategy_factory_safety.json` MUST pin, and every component MUST
enforce, at minimum:

```json
{
  "research_only": true,
  "data_fetch_enabled": false,
  "exchange_connection_enabled": false,
  "broker_control_enabled": false,
  "live_trading_enabled": false,
  "paper_order_execution_enabled": false,
  "order_placement_enabled": false,
  "data_mutation_enabled": false,
  "promotes_active_or_strong": false,
  "starts_bundle_23": false,
  "network_calls_enabled": false,
  "scheduler_install_enabled": false,
  "human_approval_required_for_dangerous_actions": true,
  "allowed_runners": ["crypto_d1_backtest_runner"],
  "allowed_datasets": ["CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V002"],
  "verdict_ceiling": "WATCH"
}
```

Enforcement rules:
- The orchestrator **loads the contract first**. Missing / malformed / weakened
  contract ⇒ **hard stop, run nothing**.
- Any queue item requesting a disabled capability is **rejected** and recorded
  with a `blocked_reason`; it is never silently downgraded into running.
- Dangerous actions (anything beyond offline read + frozen-data backtest)
  require **explicit human approval** and are out of scope for the automated
  path entirely in v1.
- The verdict ceiling is **WATCH**; any PASS/ACTIVE/STRONG seen in a result is
  clamped (same contract the shipped Lane Monitor already enforces).

---

## 7. First supported strategy lane

**Crypto-D1 only.** Start deliberately narrow:
- **Crypto-D1 Momentum N=20 deeper validation** (the current best candidate),
  using the existing frozen dataset and the existing offline runner.
- **Read-only registry scan** of existing Crypto-D1 reports to populate the
  registry without running anything.
- **No new live data**, no new dataset freeze, no fetch.

Explicitly **deferred** (NOT in v1): NQ/ES futures trend, crypto 4H, equities
rotation lanes, arbitrage protocol. They remain in the existing routine-layer
queue as `IDEA`/`PARKED` and are not wired into the Factory until v1 is proven.

---

## 8. Registry design

`reports/strategy_factory_registry/registry.json` — array of strategy records.
Required fields per record:

| Field | Meaning |
|---|---|
| `strategy_id` | stable id, e.g. `crypto_d1_momentum_n20` |
| `market` | e.g. `CRYPTO_SPOT_BTC_ETH_SOL` |
| `dataset_id` | frozen dataset id, e.g. `CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V002` |
| `runner_mode` | runner config used, e.g. `momentum_confirmation_v1` |
| `status` | lane status (WATCH / MIXED / PARKED / IDEA) |
| `verdict` | latest clamped verdict (WATCH ceiling; never PASS/ACTIVE/STRONG) |
| `run_id` | latest executed run_id, or null |
| `report_path` | repo-relative path to the latest report JSON, or null |
| `decision_memo_path` | repo-relative path to the decision memo, or null |
| `safety_flags` | the pinned-false safety block carried from the contract |
| `next_action` | the operator's next step |
| `created_at` | ISO-8601 UTC first-seen |
| `updated_at` | ISO-8601 UTC last update |

Construction is **read-only scan first** (derive everything from committed
reports), then **additive update** after orchestrated runs. The registry never
invents a verdict; it echoes the clamped runner output.

---

## 9. Research queue design

`configs/research_queue.json` — array of queue items. Required fields:

| Field | Meaning |
|---|---|
| `task_id` | unique id for this queued task |
| `strategy_id` | which registry strategy it targets |
| `priority` | integer; lower = sooner |
| `allowed_runner` | must be in the contract `allowed_runners` allow-list |
| `allowed_dataset` | must be in the contract `allowed_datasets` allow-list |
| `allowed_mode` | runner config mode (e.g. `momentum_confirmation_v1`) |
| `approved_for_research` | boolean; must be true to be eligible |
| `blocked_reasons` | array; must be empty to run |
| `max_runtime` | seconds; orchestrator aborts and records on overrun |
| `expected_outputs` | declared output paths for post-run verification |

A queue item runs **only if** `approved_for_research` is true, `blocked_reasons`
is empty, and `allowed_runner`/`allowed_dataset` pass the contract allow-list.
Anything else is skipped with a recorded reason.

---

## 10. Orchestrator behavior

`tools/strategy_factory.py` MUST:
1. **Read the queue** (`configs/research_queue.json`).
2. **Load + validate the Safety Gate Contract**; hard-stop if missing/weakened.
3. For each item: validate against the contract and the allow-lists.
4. **Run only approved research tasks**, and only via the Runner Adapter
   allow-list, against frozen data.
5. **Fail closed** — on any validation failure, missing input, or runner error,
   skip the item, classify the failure, and continue; never improvise a
   fallback that does more than was approved.
6. **Write an audit manifest** for every invocation (whether or not anything
   ran).
7. **Never trade, never place/route an order, never touch a broker/exchange.**
8. **Never mutate frozen data** (verify dataset checksums; refuse on mismatch).
9. **Stop on unsafe config** rather than proceeding with a degraded contract.
10. **Produce a clear operator report** (what was eligible, what ran, what was
    blocked and why, resulting verdicts, next actions).

**Default mode is dry-run:** validate + plan + manifest, execute nothing.
Execute mode is a separate, explicitly-approved invocation.

---

## 11. Dashboard integration plan

Today JARVIS has per-lane panels (e.g. the shipped Crypto-D1 Lane Monitor).
The end state is a **single registry-driven feed**:
- A read-only `_jarvis_strategy_registry_feed()` source (same pattern as the
  Lane Monitor: GET-only, hard-false authorization flags, forbidden-verdict
  clamp, fail-closed) reads `registry.json` and renders one row per strategy.
- JARVIS panels become **views over the registry** instead of bespoke per-lane
  scanners, so adding a lane is a registry entry, not new dashboard code.
- Migration is **additive and staged**: the registry feed ships alongside the
  existing Lane Monitor; the Lane Monitor is only retired once the registry feed
  demonstrably reproduces its content. No dashboard change happens in this plan.

---

## 12. Tests required before implementation

Each future build step is gated by tests (stdlib `pytest`, offline, tmp_path):

- **Queue validation** (`test_strategy_factory_queue.py`): schema/required
  fields; `approved_for_research`/`blocked_reasons` gating; allow-list
  enforcement; malformed queue fails closed.
- **Safety flags** (`test_strategy_factory_safety.py`): every flag pinned false
  as specified; missing/weakened contract ⇒ hard stop; `human_approval_required`
  cannot be toggled off via a queue item.
- **Runner allow-list** (`test_strategy_factory_orchestrator.py`): only
  allow-listed runners resolve; unknown runner ⇒ `RUNNER_NOT_ALLOWED`,
  nothing executed.
- **No broker/order paths** (orchestrator + safety tests): assert no
  broker/exchange/order/fetch/paper/live symbol is reachable; monkeypatch
  `subprocess`/network to raise and prove they are never called in dry-run.
- **Registry generation** (`test_strategy_factory_registry.py`): read-only scan
  produces correct records from seeded reports; verdict clamped to WATCH;
  additive update does not drop existing records.
- **Fail-closed behavior** (orchestrator): missing input, checksum mismatch,
  contract error all skip-and-record, never proceed.
- **Dashboard feed read-only** (future, in the dashboard test bundle): feed
  returns hard-false authorization flags, clamps PASS/ACTIVE/STRONG, and renders
  with no execution affordance.

No implementation step lands without its corresponding tests green.

---

## 13. Step-by-step implementation roadmap (small commits)

- **Step 1 — Registry scanner:** plan → build `strategy_report_registry.py`
  (read-only scan of existing Crypto-D1 reports) + `test_..._registry.py`.
- **Step 2 — Queue schema:** add `configs/research_queue.json` schema + loader
  + `test_..._queue.py` (no orchestration yet).
- **Step 3 — Safety contract:** add `configs/strategy_factory_safety.json` +
  loader/validator + `test_..._safety.py`.
- **Step 4 — Orchestrator dry-run mode:** build `strategy_factory.py` in
  validate-and-manifest-only mode + `test_..._orchestrator.py`. No execution.
- **Step 5 — Decision memo generator:** draft-memo writer with
  `requires_operator_signoff=true`.
- **Step 6 — Dashboard registry feed:** read-only JARVIS feed over the registry
  (additive, alongside the Lane Monitor).
- **Step 7 — Nightly scheduler (later, separately approved):** only after Steps
  1–6 are proven; opt-in, local, still research-only, still dry-run by default.

Each step is its own commit, gated on its tests, and separately approved before
it runs. Execute mode for the orchestrator is a distinct approval after dry-run
is trusted.

---

## 14. Non-authorization statement

This document is a **PLAN ONLY**. It writes no tool, no config, no test, no
dashboard change, no dataset change, and runs no backtest. It authorizes **no
paper or live trading, no broker/exchange/order/fetch path, no ACTIVE/STRONG
promotion, and no Bundle 23**. Crypto-D1 remains **WATCH / MIXED** and
**NOT_READY_FOR_REAL_DATA**. The current best candidate (Crypto-D1 Momentum
N=20) remains a research candidate only. Every implementation step listed here
requires **separate, explicit operator approval** before any code is written or
run.
