# JARVIS Checkpoint Bundle B — Strategy Factory Read-Only Observation Layer

- **Generated:** 2026-05-30
- **Baseline commit:** `307d994` (Bundle A consolidated report)
- **HEAD at implementation:** `102202a`
- **Verdict:** **`READY_FOR_STRATEGY_FACTORY_V1`**

> **HEAD note.** The background crypto/factory process advanced HEAD from the
> Bundle A baseline `307d994` to `102202a` (commits `3d46c14`, `102202a` touched
> only `trading_research/agentic_factory/` test/diagnosis files). Bundle B was
> implemented on `102202a`; `307d994` remains in history and no factory file was
> modified by Bundle B.

Bundle B moves JARVIS from **NEAR_READY** to **READY_FOR_STRATEGY_FACTORY_V1** by
shipping **only** the CRITICAL read-only observation layer (T1–T3) plus the
freshness guard (T6). Every change is **additive and read-only**: no trading
execution, no broker controls, no strategy optimization, no crypto/futures
research execution, no trading-file mutation, no runtime snapshot committed, no
broad process kill. **Strategy Factory v1 was not opened.**

---

## 1. What shipped

### T1 — Factory Status (`factory_status`)
`_jarvis_factory_status()` lists the 10 most-recently-modified factory reports
under `trading_research/agentic_factory/reports/`, each with an extracted
decision/verdict, plus a total `report_count`. It opens **only** `report.json`
(never any `*raw*` artifact), runs no Factory job, and writes nothing.

Decision extraction (`_jarvis_report_decision`) handles the wide schema variety
in the report corpus: an exact priority list (`decision`, `verdict`,
`final_verdict`, `gate_decision`, `is_verdict`, `final_recommendation`,
`trading_recommendation`, `recommendation`), then a suffix (`*_verdict` /
`*_decision`) and numbered (`5_verdict`, `8_verdict`, …) fallback. **No match →
`UNKNOWN`** — never an invented decision. *Live:* `ready`, 58 reports.

### T2 — Pass/Fail & Survival Ledger (`survival_ledger`)
`_jarvis_survival_ledger()` reads `data/profit_brain_strategy_survival.json` and
surfaces `status`, `strategy_count`, top-5 `most_survivable`, and top-5
`weakest`. Missing → `NOT_FOUND`; corrupt → fail closed. It computes no new
score. *Live:* `ready`, status `PARTIAL`, 7 strategies, top survivor `G`
(score 17.1).

### T3 — Strategy Candidate Registry (`candidate_registry`)
`_jarvis_candidate_registry()` enumerates **research** strategy candidates from
the survival file — explicitly **distinct from the video asset registries**.
Each candidate gets a display-only `observation_tier` derived from
`survival_score` (`>=10` → `OBSERVED_SURVIVOR`, `>0` → `WEAK_CANDIDATE`, `==0` →
`NO_EDGE_YET`, else `UNKNOWN`) and `deployment_status = RESEARCH_ONLY`. The panel
pins `candidate_status = RESEARCH_CANDIDATE_ONLY` and
`paper_ready/live_ready/broker_control = false`. *Live:* `ready`, 7 candidates,
all flags false.

### T6 — Live-Server Freshness Guard (`freshness_guard`)
`_JARVIS_SERVER_BOOT_HEAD` is captured **once at import** via a read-only
`git rev-parse --short HEAD` (fail-closed to `None`). `_jarvis_freshness_guard()`
compares that booting commit to the current on-disk HEAD: equal → `fresh`;
differ → `stale` (with a "restart per the Step 49 protocol" detail); either
missing → `unknown` (fail-safe). Because uvicorn runs `reload=False`, a running
process serves its booting-commit code until a **manual** restart — this guard
makes that staleness visible without a manual probe. It **restarts nothing**.
*Live:* `fresh` (`102202a == 102202a`).

---

## 2. UI

A new **Strategy Factory Readiness** section (read-only observation · no
execution · no broker) renders five panels:

- **`pFactoryReadiness`** — a banner derived **only** from the four panels
  already fetched. Shows **READY** when factory status, survival ledger, and
  candidate registry are available **and** the live build is fresh; otherwise
  **INCOMPLETE** with a `Pending:` list. It always shows
  `Execution path: NONE — OBSERVATION ONLY`, and warns prominently when the live
  build is **STALE**.
- **`pFactoryStatus`**, **`pSurvivalLedger`**, **`pCandidateRegistry`**,
  **`pFreshness`** — the four panels above.

No control affordance was added: no `<button>`, `<form>`, `onclick`,
`method=post`, snapshot, or refresh element (asserted by template tests).

---

## 3. Status shape

`/api/jarvis/status` grows from **24 → 28** keys, adding `factory_status`,
`survival_ledger`, `candidate_registry`, `freshness_guard`. Each is wrapped by
`_jarvis_safe` (fail-closed) and reports `read_only = true`; trading flags stay
locked (`paper_ready/live_ready/broker_control = false`).

`status_key_count` in the snapshot builder is dynamic (`len(keys)`) and already
whitelisted, so snapshot-compare correctly reports the 24→28 difference against
an older baseline — no whitelist change was needed.

---

## 4. Tests & validation

- **New:** `tests/test_jarvis_factory_panels.py` — 15 tests covering 28-key
  wiring, the no-trading-enable invariant, freshness fresh/stale/unknown +
  boot-head shape, decision extraction (priority / numbered / suffix / unknown /
  non-dict), the read-only shape of all three data panels, and template
  panels-present / no-controls.
- **Updated:** `tests/test_jarvis_snapshot_report.py` (docstring + `len == 28`)
  and `tests/test_jarvis_ask_contract.py` (`len(after) == 28`).
- **`py_compile app.py`** → `PYCOMPILE_OK`.
- **Scoped pytest** (route, conversation_safety, ask_contract, snapshot_report,
  factory_panels) → **408 passed, 0 failed, 0 skipped**.
- **`report.json`** validated with `python -m json.tool` → JSON_OK.

---

## 5. Read-only / no-trading guarantees

- All four helpers read committed/local files only and run at most one
  read-only `git rev-parse`. None executes a backtest, fetches data, calls a
  broker, starts/stops a bot, optimizes a strategy, reads secrets, or writes a
  file.
- `candidate_registry` pins `paper_ready/live_ready/broker_control = false` and
  `deployment_status = RESEARCH_ONLY` for every candidate.
- No `/api/jarvis/snapshot` or `/api/jarvis/refresh` route added; the template
  has no execution/refresh/snapshot control.
- Missing/corrupt data fails closed to `UNKNOWN` / `NOT_FOUND` — never an
  invented decision or score.
- The freshness guard restarts nothing; it only reports a comparison.

## 6. Explicitly not done

- Did **not** open Strategy Factory v1.
- Did **not** modify trading execution logic or any
  `trading_research/agentic_factory` file.
- Did **not** create any broker/paper/live/execution/refresh/snapshot control or
  endpoint.
- Did **not** run, simulate, or optimize any strategy; ran no backtest and no
  crypto/futures research execution.
- Did **not** stage or commit any runtime snapshot or the untracked backlog.
- Did **not** perform any broad process kill or restart the live server.

---

## 7. Verdict

**`READY_FOR_STRATEGY_FACTORY_V1`.** The three CRITICAL observation panels
Bundle A flagged as unbuilt (T1/T2/T3) plus the T6 freshness guard are
implemented additive and read-only, wired into a 28-key fail-closed status feed,
surfaced in a dedicated readiness section with a clear READY/INCOMPLETE banner,
and covered by 15 new tests (408 total passing). JARVIS now shows Factory
readiness and candidate/pass-fail/freshness information from committed reports
only — missing data shown as `UNKNOWN`/`NOT_FOUND`, with a prominent stale-build
warning — while adding **no** trigger or execution path.

> **Operator note:** the live `:8765` process is still serving its booting
> commit (`reload=False`). To *see* these panels in the browser, restart per the
> Step 49 protocol; the new `pFreshness` panel will then read `fresh`.
