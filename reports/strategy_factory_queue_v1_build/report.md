# Strategy Factory v1 — Step 2 Build Report: Research Queue v1 schema + loader

- **Build date:** 2026-06-04
- **Official master at build time:** `9ad578c424d829e71678610176d3c4421da7992a`
- **Step:** 2 of the Strategy Factory v1 roadmap (Research Queue schema + loader/validator)
- **Scope:** schema + loader/validator ONLY. No orchestrator, no execution, no
  backtest, no dataset change, no runner change, no runner import, no dashboard
  change, no broker/exchange/order/fetch path, no paper/live, no ACTIVE/STRONG
  promotion, no Bundle 23.

---

## 1. What was implemented

A human-authored research backlog (`configs/research_queue.json`) plus a new
standard-library-only, **read-only**, **fail-closed** loader/validator
(`tools/strategy_factory_queue.py`). The queue declares which research tasks MAY
be *considered* later by an orchestrator. Listing a task is **not** authorization
to execute it — and in v1 nothing is executable at all.

Public surface:
- `load_queue_file(path) -> (obj, status)` — pure read; fail closed on
  missing/corrupt JSON.
- `validate_queue(queue_obj, load_status, source) -> report` — never raises;
  problems become `blocked_reasons` / `warnings`.
- `build(base) -> report` — loads `base/configs/research_queue.json` and returns
  the validated, normalized report. Writes nothing, runs no subprocess, makes no
  network call, imports no runner.
- `to_stable_json(report)` / `render_markdown(report)` — deterministic output.
- `write_build_report(base, report)` — **opt-in** writer that emits
  `queue.json` / `queue.md` ONLY to `reports/strategy_factory_queue_v1_build/`.
- CLI (`--base`, `--format json|md`, `--write`); default is read-only stdout.

Each queue item carries every required field: `task_id`, `strategy_id`,
`strategy_family`, `market`, `dataset_id`, `allowed_runner`, `allowed_mode`,
`priority`, `status`, `approved_for_research`, `blocked_reasons`,
`max_runtime_seconds`, `expected_outputs`, `safety_flags`, `created_at`,
`updated_at`, `next_action`. The validator additionally derives `valid`,
`eligible_for_research_listing`, and `executable` (the last is **always false**
in v1, by construction).

### Validator rules (deterministic, fail-closed)
1. **Required-field presence** — any missing item field → `blocked_reason`
   (item blocked; never executed).
2. **Runner allowlist** — only `tools/crypto_d1_backtest_runner.py`; anything
   else → blocked.
3. **Dataset allowlist** — only `CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002`; anything
   else → blocked.
4. **Mode allowlist** — only `momentum_confirmation_v1`; anything else → blocked.
5. **Safety flags** — `research_only` must be `true`; every other flag
   (including `execution_authorized`) must be present and `false`; any forbidden
   flag `true` → blocked.
6. **Execution never authorized** — `execution_authorized=true` (as a flag *or*
   a top-level field) → blocked **and** never executable.
7. **Listing ≠ execution** — `approved_for_research` must be a boolean; even when
   `true` it confers ONLY research-listing eligibility
   (`eligible_for_research_listing`), never execution.
8. **Determinism** — items ordered by `(priority, task_id)`; sorted-key JSON; no
   wall-clock dependence.
9. **Fail closed** — a missing or corrupt file yields an empty report with a
   warning, never an exception.

### Separation of approval (plan requirement 7)
`approved_for_research` (the queue-listing gate) is kept **strictly separate**
from execution. There is **no execution-authorization path** in v1:
`execution_authorized` must be false on every item, and `executable` is pinned
`false` by construction. An item can at most become *eligible to be listed for
research* — never *eligible to run*.

### Live validation (shipped config)
| task_id | mode | priority | status | valid | listing_eligible | executable |
|---|---|---|---|---|---|---|
| crypto_d1_momentum_n20_deeper_validation_v1 | momentum_confirmation_v1 | 1 | NEEDS_PLAN | true | false | false |

The one initial task — *Crypto-D1 Momentum N=20 deeper validation* — appears,
validates clean, but is **non-executable** (`approved_for_research=false`,
`executable=false`). Zero blocked items, zero warnings.

---

## 2. How it builds on the Strategy Factory v1 plan and Registry v1

- **Plan** (`reports/strategy_factory_v1_plan/`): this is **Step 2 — Research
  Queue v1**, the human-authored approved backlog. The item field set, the nine
  pinned-false safety flags, and the fail-closed posture all follow the plan's
  §9.
- **Registry v1** (Step 1, `reports/strategy_factory_registry_v1_build/`): the
  registry is the read-only single source of truth describing *existing*
  experiments. The queue is the *forward-looking* backlog of tasks that an
  orchestrator (Step 3, **not built**) may later consider. The two are
  complementary: registry = what has happened; queue = what is allowed to be
  considered next. Nothing from Step 3+ (orchestrator, runner-adapter,
  decision-memo generator, dashboard feed, scheduler) is implemented here.

---

## 3. Existing routine layer — reused vs. not reused

- **Reused (conventions):** the stdlib-only, deterministic, repo-root-relative,
  fail-closed style of `tools/strategy_report_registry.py` (Step 1) — the same
  `_repo_root()`, fail-closed JSON reads, sorted-key `to_stable_json`, and an
  opt-in `write_build_report` confined to a single build folder, plus the
  pinned-false safety flags.
- **Not reused (and why):** no runner, orchestrator, or execution code is
  imported or created. The validator is a separate, single-purpose module so the
  shipped registry scanner stays untouched. No parallel/duplicate system was
  introduced.

---

## 4. Exact files created / changed

**Created (this step):**
- `configs/research_queue.json` (human-authored research backlog; one narrow task)
- `tools/strategy_factory_queue.py` (read-only fail-closed loader/validator + opt-in build writer)
- `tests/test_strategy_factory_queue.py` (23 tests)
- `reports/strategy_factory_queue_v1_build/report.md` (this report)
- `reports/strategy_factory_queue_v1_build/report.json` (machine build report)

**Changed:** none. No existing tool, runner, test, dataset, dashboard, or
brain_memory file was modified.

---

## 5. Test results

- `tests/test_strategy_factory_queue.py` → **23 passed**
- `tests/test_strategy_report_registry.py` → **13 passed** (unchanged; confirms
  no indirect breakage of the shipped Step-1 registry)

Coverage of the required cases:
- valid queue loads → item `valid`, listed, but `executable=false`;
- missing required field → item blocked (recorded, not raised);
- unknown runner / unknown dataset / unknown mode → item blocked;
- every forbidden safety flag `true` (8 parametrized, incl.
  `execution_authorized`) → item blocked; `research_only=false` → blocked;
- `execution_authorized=true` → rejected, not executable, not listing-eligible;
- `approved_for_research=true` → listing eligible but still not executable;
- loader runs no subprocess, makes no network call, imports no runner module,
  and writes nothing on a pure read;
- deterministic ordering by `(priority, task_id)` + byte-identical JSON;
- missing / corrupt queue file fails closed with a warning (no crash);
- the **shipped** `configs/research_queue.json` validates and the N=20 task
  appears but is non-executable;
- opt-in writer confined to the build folder (nothing under `data/` or
  `templates/`).

---

## 6. Safety confirmations

- **Read-only / executes nothing:** `build` and `validate_queue` create/delete no
  file (test asserts the file set is unchanged), run no subprocess (test
  monkeypatches `subprocess.run`/`Popen` to raise), and import no runner module
  (test asserts `crypto_d1_backtest_runner` is absent from `sys.modules`).
- **Non-executable by construction:** `executable` is pinned `false` for every
  item regardless of input; there is no code path that runs a queue item.
- **Write path confined:** the only writer targets
  `reports/strategy_factory_queue_v1_build/`; never `data/`, never `templates/`,
  never datasets, never other reports.
- **Pinned-false safety flags** on the report and required on every item:
  `research_only=true`, `paper_live_authorized=false`,
  `broker_path_enabled=false`, `exchange_path_enabled=false`,
  `order_path_enabled=false`, `active_strong_promoted=false`,
  `bundle_23_started=false`, `dataset_mutation_allowed=false`,
  `execution_authorized=false`.
- **No broker/exchange/order/fetch/network code** exists in the tool (stdlib
  only).
- Crypto-D1 remains **WATCH / MIXED** and **NOT_READY_FOR_REAL_DATA**; the queue
  only declares an allowed backlog and promotes nothing.

---

## 7. What Step 3 should be

Per the roadmap: **Research Orchestrator v1 (DRY-RUN ONLY)** — a read-only
orchestrator that joins the Step-1 registry with the Step-2 queue and emits a
**dry-run execution plan** (what *would* run, in what order, against which frozen
dataset) **without running anything**. Dry-run by default; an `execute` mode must
be a **separate, explicitly approved** build behind the safety-gate contract. No
backtest, no dataset mutation, and no runner call until separately approved.

---

## 8. Non-authorization statement

This build adds a research-queue schema, a read-only fail-closed
loader/validator, and its tests only. It authorizes no paper or live trading, no
broker/exchange/order/fetch path, no ACTIVE/STRONG promotion, and no Bundle 23.
It executes no queue item, runs no backtest, imports no runner, builds no
orchestrator, and mutates no dataset. Every queue item is non-executable by
construction. Crypto-D1 remains WATCH / MIXED and NOT_READY_FOR_REAL_DATA.
