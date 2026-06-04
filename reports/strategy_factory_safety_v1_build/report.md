# Strategy Factory v1 — Step 3 Build Report: Safety Contract v1

- **Build date:** 2026-06-04
- **Official master at build time:** `f6f07ecb03d99a64eac960fe01c7e1369cdb8938`
- **Step:** 3 of the Strategy Factory v1 roadmap (central Safety Contract + validator)
- **Scope:** safety-contract schema + validator ONLY. No orchestrator, no
  execution, no backtest, no dataset change, no runner change, no runner import,
  no dashboard change, no broker/exchange/order/fetch path, no paper/live, no
  ACTIVE/STRONG promotion, no Bundle 23.

---

## 1. What was implemented

A central, machine-readable safety contract (`configs/strategy_factory_safety.json`)
plus a standard-library-only, **read-only**, **fail-closed** validator
(`tools/strategy_factory_safety.py`). The contract is the single gate every
future Strategy Factory component must pass before any research task may even be
*considered*. The validator loads and checks it, and additionally runs a
**read-only integration screen** of `configs/research_queue.json` against it.

Public surface:
- `load_safety_file(path) -> (obj, status)` — pure read; fail closed.
- `validate_contract(obj, load_status, source) -> result` — never raises.
- `screen_text(text, forbidden_terms) -> [hits]` — case-insensitive screen of a
  **candidate** value/path against the forbidden terms.
- `validate_task_against_contract(task, normalized_contract)` — per-task screen
  (allowlists + forbidden terms + flags); returns `contract_conformant`,
  `allowed_for_listing`, `executable` (always `False`).
- `validate_queue_against_contract(base, contract_result)` — read-only queue
  integration; imports no runner.
- `build(base) -> result` — loads the contract and runs the queue integration.
- `to_stable_json` / `render_markdown` / `write_build_report` (opt-in, writes
  ONLY to `reports/strategy_factory_safety_v1_build/`).
- CLI (`--base`, `--format json|md`, `--write`); exit `0` if **SAFE**, `2` if
  **UNSAFE**, so a caller can gate on it.

### The result object (requirement 10)
`{ valid, safe, blocked_reasons, warnings, normalized_contract, safety_flags }`.
`valid` = the contract loaded as an inspectable object; `safe` = it passed every
fail-closed check.

### What the contract declares
- **research_only = true.**
- **Pinned-false flags** (all blocked): `paper_live_authorized`,
  `broker_path_enabled`, `exchange_path_enabled`, `order_path_enabled`,
  `fetch_live_data_enabled`, `dataset_mutation_allowed`, `active_strong_promoted`,
  `bundle_23_started`, `execution_authorized`.
- **Allowlists:** datasets = `CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002` only; runners
  = `tools/crypto_d1_backtest_runner.py` only; modes = `momentum_confirmation_v1`
  only; markets = `crypto` only.
- **Forbidden terms:** `broker`, `exchange`, `order`, `live`, `paper`, `fetch`,
  `kraken`, `binance live`, `ACTIVE`, `STRONG`, `Bundle 23`.
- **Human approval required:** for execution, for paper/live, and for promotion.

### Fail-closed rules (requirement 6)
Missing file → UNSAFE; malformed JSON → UNSAFE; missing required key → UNSAFE;
`research_only` not true → UNSAFE; any forbidden flag true → UNSAFE; any unknown
runner/dataset/mode/market in an allowlist → UNSAFE; missing required forbidden
term → UNSAFE; any human-approval gate not true → UNSAFE. No path raises.

### Forbidden-term scope (important)
`screen_text` screens **candidate** task identifiers/paths (`task_id`,
`strategy_id`, `strategy_family`, `next_action`, runner paths) — **not** the
contract's own metadata. The contract legitimately names "broker"/"order"/etc.
inside its `forbidden_terms` list and flag names; screening those would be a
false positive, so contract-structure validation and candidate screening are
deliberately separate.

### Live validation (shipped files)
- Contract: `valid=true`, **`safe=true`**, `blocked_reasons=[]`.
- Queue integration: 1 item, 1 conformant.

| task_id | contract_conformant | allowed_for_listing | executable |
|---|---|---|---|
| crypto_d1_momentum_n20_deeper_validation_v1 | true | true | false |

The shipped queue item is **allowed for listing** under the contract but remains
**non-executable** by construction.

---

## 2. How it builds on Step 1 (registry) and Step 2 (queue)

- **Step 1 registry** = read-only single source of truth for *existing*
  experiments.
- **Step 2 queue** = human-authored approved *backlog* of considerable tasks.
- **Step 3 safety contract (this step)** = the central gate both — and every
  future component — must pass. It centralizes the pinned-false flags,
  allowlists, forbidden terms, and human-approval gates that Steps 1-2 each
  embedded locally, and provides the canonical screen the orchestrator (Step 4,
  **not built**) will be required to call before considering any task. The
  validator already proves the shipped queue item conforms for **listing** while
  staying non-executable.

Nothing from Step 4+ (orchestrator, runner-adapter, decision-memo generator,
dashboard feed, scheduler) is implemented here.

---

## 3. Exact files created / changed

**Created (this step):**
- `configs/strategy_factory_safety.json` (central safety contract)
- `tools/strategy_factory_safety.py` (read-only fail-closed validator + opt-in build writer)
- `tests/test_strategy_factory_safety.py` (42 tests)
- `reports/strategy_factory_safety_v1_build/report.md` (this report)
- `reports/strategy_factory_safety_v1_build/report.json` (machine build report)

**Changed:** none. No existing tool, runner, test, dataset, dashboard, config,
or brain_memory file was modified.

---

## 4. Test results

- `tests/test_strategy_factory_safety.py` → **42 passed**
- `tests/test_strategy_factory_queue.py` → **23 passed** (unchanged)
- `tests/test_strategy_report_registry.py` → **13 passed** (unchanged)
- **Total: 78 passed.**

Coverage of the required cases:
- valid contract is SAFE;
- missing file / malformed JSON fail closed (UNSAFE, no crash);
- every required key missing (parametrized) fails closed;
- every forbidden safety flag true (parametrized) fails closed; `research_only`
  false fails closed;
- unknown runner/dataset/mode/market (parametrized) fails closed;
- `execution_authorized=true` and `paper_live_authorized=true` each block;
- broker/exchange/order/fetch/live/kraken/ACTIVE/STRONG screened as forbidden;
- a task smuggling a forbidden token or an unlisted runner is blocked
  (not conformant, not executable);
- shipped queue item: `contract_conformant` + `allowed_for_listing`, but
  `executable=false`;
- no subprocess, no network, no runner import, no stray writes;
- deterministic normalized output (byte-identical JSON);
- opt-in writer confined to the build folder.

---

## 5. Safety confirmations

- **Read-only / executes nothing:** `build` / `validate_contract` create/delete
  no file (test asserts the file set is unchanged), run no subprocess (test
  monkeypatches `subprocess.run`/`Popen` to raise), and import no runner module
  (test asserts `crypto_d1_backtest_runner` is absent from `sys.modules`).
- **Authorizes nothing:** `research_only=true`; all nine execution / paper /
  live / broker / exchange / order / fetch / promotion / Bundle-23 flags pinned
  `false`; human approval required for execution, paper/live, and promotion.
- **Write path confined:** the only writer targets
  `reports/strategy_factory_safety_v1_build/`; never `data/`, never
  `templates/`, never datasets, never other reports.
- **No broker/exchange/order/fetch/network code** exists in the tool (stdlib
  only).
- **Integration check:** `configs/research_queue.json` validates against the
  contract — the N=20 task is `contract_conformant` and `allowed_for_listing`
  but `executable=false`.
- Crypto-D1 remains **WATCH / MIXED** and **NOT_READY_FOR_REAL_DATA**; the
  contract promotes nothing.

---

## 6. What Step 4 should be

Per the roadmap: **Research Orchestrator v1 (DRY-RUN ONLY, safety-gated)** — a
read-only orchestrator that, for each queue item, **first** calls this Step-3
safety-contract validator and refuses to consider any task unless `safe=true`
and the task is `contract_conformant`; then emits a **dry-run plan** (what
*would* run, in what order, against which frozen dataset) **without running
anything**. Dry-run by default; an `execute` mode must be a **separate,
explicitly approved** build behind this contract plus the human-approval gates.
No backtest, no dataset mutation, and no runner call until separately approved.

---

## 7. Non-authorization statement

This build adds a central safety contract, a read-only fail-closed validator,
and its tests only. It authorizes no paper or live trading, no
broker/exchange/order/fetch path, no ACTIVE/STRONG promotion, and no Bundle 23.
It executes no queue item, runs no backtest, imports no runner, builds no
orchestrator, and mutates no dataset. Crypto-D1 remains WATCH / MIXED and
NOT_READY_FOR_REAL_DATA.
