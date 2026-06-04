# Strategy Factory v1 — Step 4 Build Report: Dry-run Research Orchestrator v1

- **Build date:** 2026-06-04
- **Official master at build time:** `3780c938720a5a23cd2e72a349df42801de7a474`
- **Step:** 4 of the Strategy Factory v1 roadmap (dry-run orchestrator that joins
  registry + queue + safety contract)
- **Scope:** DRY-RUN orchestrator ONLY. No execution, no backtest, no runner
  call, no runner import, no dataset change, no runner change, no dashboard
  change, no broker/exchange/order/fetch path, no paper/live, no ACTIVE/STRONG
  promotion, no Bundle 23.

---

## 1. What was implemented

A standard-library-only, **read-only**, **DRY-RUN** orchestrator
(`tools/strategy_factory_orchestrator.py`) that joins the three shipped read-only
layers into a single deterministic *"what would run / what is blocked / why"*
plan. It constructs no command, calls no runner, imports no runner, and pins
`executable=false` for every task. It imports only the three factory tools
(themselves read-only) — never a runner module.

Public surface:
- `build_dry_run_plan(base) -> dict` — joins registry + queue + safety; pure read.
- `to_stable_json(plan)` / `render_markdown(plan)` — deterministic output.
- `write_build_report(base, plan)` — **opt-in** writer that emits
  `dry_run_plan.json` / `dry_run_plan.md` ONLY to
  `reports/strategy_factory_orchestrator_v1_build/`.
- CLI (`--base`, `--format json|md`, `--write`); read-only stdout by default;
  exit `2` when `execution_halted` so a caller can gate on it.

### The join
- **Step 1 registry** (`strategy_report_registry.build_registry`) → per-strategy
  `current_stage` + clamped `current_verdict`, keyed by `strategy_id`.
- **Step 2 queue** (`strategy_factory_queue.build`) → normalized backlog items
  (`status`, `valid`, `blocked_reasons`, `next_action`), keyed by `task_id`.
- **Step 3 safety** (`strategy_factory_safety.build`) → `safe` flag plus the
  `queue_integration` screen of the RAW queue items against the contract.
- **Join key:** `queue.item.strategy_id → registry.strategy.strategy_id`; the
  contract screen is joined by `task_id`.

### Per-task plan fields (requirement 6)
`task_id`, `strategy_id`, `current_stage`, `current_verdict`, `queue_status`,
`contract_conformant`, `allowed_for_listing`, `executable` (**always false**),
`blocked_reasons`, `warnings`, `next_action`, `would_run_command` (**always
null**), `would_write_outputs` (**always []**), and a `disabled_preview`.

### No runnable command (requirements 7-9)
`executable` is hard-pinned `false` for every task; `would_run_command` is always
`null`; `would_write_outputs` is always `[]`. The only command-ish surface is
`disabled_preview` — an explicitly-labeled, **incomplete, non-executable** prose
note with no interpreter, no entrypoint, and no argument list. It cannot be
copied and run. Tests assert the serialized plan contains no `python `, `.venv`,
`python.exe`, `&& `, or `subprocess` tokens.

### Fail-closed rules (requirement 10)
- missing registry (no `reports/` dir) → `execution_halted`, no execution;
- missing/unreadable queue → `execution_halted`, no execution;
- missing or unsafe safety contract → `execution_halted`; every task
  `contract_conformant=false`, `allowed_for_listing=false`;
- invalid queue item → queue blocked_reasons surfaced on the task;
- unknown `strategy_id` (no registry match) → task blocked, stage/verdict null;
- `execution_authorized=true` or a forbidden broker/order/fetch/live/paper token
  in the RAW queue item → blocked by the Step-3 contract screen.

---

## 2. How it connects Steps 1, 2, and 3

Step 4 is the first component that reads all three prior layers together.
Registry answers *what has happened* (stage/verdict). Queue answers *what is
allowed to be considered* (backlog/status). The safety contract answers *may it
be considered at all* (the central gate). The orchestrator joins queue items to
registry entries by `strategy_id`, screens each RAW queue item through the
Step-3 contract, and emits a dry-run plan. It is the safety-gated, read-only
precursor to any future execute mode (Step 5+, **not built**), which would remain
behind this contract plus the three human-approval gates.

---

## 3. Existing routine layer — reused vs. not reused

- **Reused (conventions):** the stdlib-only, deterministic, repo-root-relative,
  fail-closed style of Steps 1-3 — same `_repo_root()`, sorted-key
  `to_stable_json`, opt-in `write_build_report` confined to a single build
  folder, pinned-false safety flags, and the listing-vs-execution separation.
  Reuses `strategy_factory_safety.CONTRACT_SAFETY_FLAGS` so the layers agree.
- **Not reused (and why):** no runner, execution code, subprocess, or network.
  The orchestrator delegates registry scanning, queue validation, and contract
  screening to the existing Step 1-3 modules rather than reimplementing them —
  one source of truth per concern. No parallel system was introduced.

---

## 4. Exact files created / changed

**Created (this step):**
- `tools/strategy_factory_orchestrator.py` (read-only dry-run orchestrator)
- `tests/test_strategy_factory_orchestrator.py` (13 tests)
- `reports/strategy_factory_orchestrator_v1_build/report.md` (this report)
- `reports/strategy_factory_orchestrator_v1_build/report.json` (machine report)

**Changed:** none. `configs/research_queue.json` was **not** modified — the
shipped queue item already joins cleanly to the registry and conforms to the
contract, so no config change was necessary.

---

## 5. Dry-run output summary (shipped repo)

`execution_halted=false`; registry=2 strategies, queue=1 item,
`contract_safe=true`.

| task_id | strategy_id | stage | verdict | queue_status | conformant | listing | executable | would_run_command |
|---|---|---|---|---|---|---|---|---|
| crypto_d1_momentum_n20_deeper_validation_v1 | crypto_d1_momentum_confirmation_v1 | EXECUTED | WATCH | NEEDS_PLAN | true | true | false | null |

Blocked reasons for the one task:
- *execution not authorized: dry-run orchestrator v1 never executes (executable
  is pinned false)*
- *task not approved_for_research: create the N=20 deeper-validation plan before
  any execution*

`next_action`: *Create the N=20 deeper-validation plan before any execution (no
execution in Step 2).* This matches the operator's expected initial dry-run
result exactly.

---

## 6. Test results

- `tests/test_strategy_factory_orchestrator.py` → **13 passed**
- `tests/test_strategy_factory_safety.py` → **42 passed** (unchanged)
- `tests/test_strategy_factory_queue.py` → **23 passed** (unchanged)
- `tests/test_strategy_report_registry.py` → **13 passed** (unchanged)
- **Total: 91 passed**

Coverage of the required cases:
- dry-run loads registry + queue + safety contract;
- known Crypto-D1 task appears and joins to registry EXECUTED / WATCH;
- `executable` is always false (multi-item);
- no real command emitted (`would_run_command` null; no interpreter token in the
  serialized plan);
- missing safety contract halts everything;
- unsafe safety contract halts everything;
- unknown `strategy_id` blocks the item (stage null);
- `execution_authorized=true` item blocked by the contract screen;
- forbidden broker/order path item blocked by the contract screen;
- no subprocess / no network / no runner import / no stray writes;
- deterministic ordering by `task_id` + byte-identical JSON;
- opt-in writer confined to the orchestrator build folder;
- the **shipped** repo dry-run yields the expected N=20 result.

---

## 7. Safety confirmations

- **Dry-run only / executes nothing:** `executable` pinned `false` for every
  task; `would_run_command` always `null`; `would_write_outputs` always `[]`;
  `execution_halted` gating present.
- **No copy-runnable command:** the only command surface is the labeled,
  incomplete, non-executable `disabled_preview` prose; tests assert no
  `python`/`.venv`/`subprocess`/`&&` tokens appear in the serialized plan.
- **Read-only:** runs no subprocess (test monkeypatches `subprocess.run`/`Popen`
  to raise), makes no network call, imports no runner module (test asserts
  `crypto_d1_backtest_runner` absent from `sys.modules`), and writes nothing on a
  pure read.
- **Write path confined:** the only writer targets
  `reports/strategy_factory_orchestrator_v1_build/`.
- **Pinned-false safety flags:** `research_only=true`,
  `paper_live_authorized=false`, `broker_path_enabled=false`,
  `exchange_path_enabled=false`, `order_path_enabled=false`,
  `fetch_live_data_enabled=false`, `dataset_mutation_allowed=false`,
  `active_strong_promoted=false`, `bundle_23_started=false`,
  `execution_authorized=false`.
- Crypto-D1 remains **WATCH / MIXED** and **NOT_READY_FOR_REAL_DATA**.

---

## 8. What Step 5 should be

A read-only component that turns the dry-run plan + registry into an
operator-facing artifact: either (a) a **Decision-Memo Generator v1** that drafts
a human-review memo template per EXECUTED/WATCH strategy (no promotion; operator
fills and approves), or (b) a **read-only dashboard feed** surfacing the dry-run
plan in JARVIS. Neither executes anything. An actual **execute** mode for the
orchestrator remains a **separate, explicitly-approved** build behind the Step-3
safety contract plus the three human-approval gates — not part of Step 5.

---

## 9. Non-authorization statement

This build adds a read-only dry-run orchestrator, its tests, and a build report
only. It authorizes no paper or live trading, no broker/exchange/order/fetch
path, no ACTIVE/STRONG promotion, and no Bundle 23. It executes no queue item,
runs no backtest, calls no runner, imports no runner, constructs no runnable
command, and mutates no dataset. Every task is non-executable by construction.
Crypto-D1 remains WATCH / MIXED and NOT_READY_FOR_REAL_DATA.
