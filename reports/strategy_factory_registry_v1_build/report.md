# Strategy Factory v1 — Step 1 Build Report: Strategy Report Registry v1

- **Build date:** 2026-06-03
- **Official master at build time:** `ce02b2236974b276d3b56406324401afdb6f40ae`
- **Step:** 1 of the Strategy Factory v1 roadmap (Registry scanner)
- **Scope:** read-only registry scanner ONLY. No orchestrator, no queue, no
  backtest, no dataset change, no runner change, no dashboard change, no
  broker/exchange/order/fetch path, no paper/live, no ACTIVE/STRONG promotion,
  no Bundle 23.

---

## 1. What was implemented

A new standard-library-only, **read-only** tool
`tools/strategy_report_registry.py` that scans committed plan → result →
decision-memo artifacts under `reports/` and produces a normalized, deterministic
registry of known experiments.

Public surface:
- `build_registry(base) -> dict` — pure read; returns the registry. Writes
  nothing, runs no subprocess, makes no network call.
- `to_stable_json(registry) -> str` — deterministic (sorted-key) serialization.
- `render_markdown(registry) -> str` — compact human table.
- `write_build_report(base, registry) -> [paths]` — **opt-in** writer that
  emits `registry.json` / `registry.md` to the single allowed folder
  `reports/strategy_factory_registry_v1_build/` and nowhere else.
- CLI (`--format json|md`, `--write`); default is read-only stdout.

Each registry entry carries every field required by the Step-1 spec:
`strategy_id`, `strategy_family`, `market`, `dataset_id`, `runner_mode`,
`stage`, `status`, `verdict`, `run_id`, `report_path`, `plan_path`,
`decision_memo_path`, `safety_flags`, `next_action`, `created_at`,
`updated_at`. Clamped entries additionally carry `verdict_clamped_from` and
`unsafe_verdict_flagged`.

### Resolution logic (deterministic, fail-closed)
- Scan glob `crypto_d1_*plan*/report.json` (the same tree the shipped JARVIS
  Lane Monitor reads).
- Resolve the result dir by dropping a **trailing** `_plan` from the plan dir
  name. If the dir does not end with `_plan`, the result-dir convention is
  **not** applied (it would otherwise collapse onto the plan dir and misread the
  plan's own `report.json` as a result) — the entry stays `PLAN_ONLY` with a
  recorded warning.
- Stage precedence: `DECISION_RECORDED` > `EXECUTED` > `PLAN_ONLY`.
- Verdict ceiling: `ACTIVE`/`STRONG`/`PASS` → clamped to `WATCH` + warning +
  `unsafe_verdict_flagged=true`; empty/unknown → `UNKNOWN` (never `PASS`).
- Timestamps come only from the artifacts (`plan_date`, result `generated_at`);
  there is no wall-clock dependence, so repeated builds are byte-identical.

### Live scan result (current repo)
| strategy_id | stage | status | verdict | run_id |
|---|---|---|---|---|
| crypto_d1_baseline_backtest_plan_v1 | PLAN_ONLY | WATCH | — | — |
| crypto_d1_momentum_confirmation_v1 | EXECUTED | WATCH / MIXED | WATCH | 2a3be425522a04ec |

(One warning: the baseline plan dir name does not end with `_plan`, so it is
treated as plan-only — fail-closed, by design.)

---

## 2. How it builds on the Strategy Factory v1 plan

This is **Step 1** of the roadmap in
`reports/strategy_factory_v1_plan/report.json` — the *Strategy Report Registry*,
defined there as the read-only "single source of truth" built by *scanning
existing committed reports first*, before any orchestrator or queue exists. The
field list, the WATCH verdict ceiling, and the eight pinned-false safety flags
all match the plan's §6 and §8. Nothing from later steps (orchestrator, queue,
decision-memo generator, dashboard feed, scheduler) is implemented here.

---

## 3. Existing routine layer — reused vs. not reused

- **Reused (conventions):** the established stdlib-only, deterministic,
  repo-root-relative style of `tools/strategy_factory_routines.py`; and the
  plan→result→memo scan + verdict-clamp pattern already shipped in the JARVIS
  Crypto-D1 Lane Monitor (`app.py`).
- **Not reused (and why):** `strategy_factory_routines.py` reads a *different*
  input tree (`trading_research/agentic_factory/reports/`) and emits *summaries*
  (daily-state / queue / weekly-review), not a per-strategy registry keyed on
  the `reports/crypto_d1_*` plan/result artifacts with the Step-1 field schema.
  Extending it would overload a tool tuned to another tree and output shape.
  The new scanner is therefore minimal and separate, but deliberately mirrors
  its safety posture. No parallel/duplicate system was introduced beyond this
  one small, single-purpose reader.

---

## 4. Exact files created / changed

**Created (this step):**
- `tools/strategy_report_registry.py` (read-only scanner + opt-in build writer)
- `tests/test_strategy_report_registry.py` (13 tests)
- `reports/strategy_factory_registry_v1_build/report.md` (this report)
- `reports/strategy_factory_registry_v1_build/report.json` (machine build report)

**Changed:** none. No existing tool, runner, test, dataset, dashboard, or
brain_memory file was modified.

---

## 5. Test results

- `tests/test_strategy_report_registry.py` → **13 passed**
- `tests/test_jarvis_lane_monitor_source.py` → **20 passed** (unchanged;
  confirms no indirect breakage of the shipped Lane Monitor)

Coverage of the required cases:
- scans plan + executed report → `EXECUTED`, verdict `WATCH`, run_id present;
- decision memo advances stage to `DECISION_RECORDED`;
- verdict ceiling stays `WATCH`;
- `ACTIVE`/`STRONG`/`PASS` clamped to `WATCH` and flagged unsafe (+warning);
- missing result, corrupt result JSON, and missing `reports/` all fail closed;
- empty/unknown verdict → `UNKNOWN`, never `PASS`;
- deterministic ordering + byte-identical JSON across builds;
- no subprocess, no stray writes; opt-in writer confined to the build folder.

---

## 6. Safety confirmations

- **Read-only by default:** `build_registry` creates/deletes no file (test
  asserts the file set is unchanged) and runs no subprocess (test monkeypatches
  `subprocess.run`/`Popen` to raise).
- **Write path confined:** the only writer targets
  `reports/strategy_factory_registry_v1_build/`; never `data/`, never
  `templates/`, never the dashboard.
- **Pinned-false safety flags** on the registry and every entry:
  `research_only=true`, `paper_live_authorized=false`,
  `broker_path_enabled=false`, `exchange_path_enabled=false`,
  `order_path_enabled=false`, `active_strong_promoted=false`,
  `bundle_23_started=false`, `dataset_mutation_allowed=false`.
- **No broker/exchange/order/fetch/network code** exists in the tool (stdlib
  only; no socket/requests/urllib/subprocess use in the read path).
- Crypto-D1 remains **WATCH / MIXED** and **NOT_READY_FOR_REAL_DATA**; the
  registry only re-describes existing artifacts and promotes nothing.

---

## 7. What Step 2 should be

Per the roadmap: **Research Queue v1 schema + loader** — add
`configs/research_queue.json` (human-authored, approved backlog) with the field
set from the plan §9 (`task_id`, `strategy_id`, `priority`, `allowed_runner`,
`allowed_dataset`, `allowed_mode`, `approved_for_research`, `blocked_reasons`,
`max_runtime`, `expected_outputs`) plus a stdlib loader/validator and
`tests/test_strategy_factory_queue.py`. **No orchestration and no execution** in
Step 2 — schema + validation only, fail-closed, separately approved before build.

---

## 8. Non-authorization statement

This build adds a read-only scanner and its tests only. It authorizes no paper
or live trading, no broker/exchange/order/fetch path, no ACTIVE/STRONG
promotion, and no Bundle 23. It runs no backtest and mutates no dataset.
Crypto-D1 remains WATCH / MIXED and NOT_READY_FOR_REAL_DATA.
