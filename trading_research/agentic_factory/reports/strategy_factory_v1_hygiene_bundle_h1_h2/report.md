# SPARTA Strategy Factory v1 — Hygiene Bundle H1–H2

**Scope:** complete the hygiene foundation required before any automated overnight
Strategy Factory build — **H1** (isolated factory-research worktree) and **H2**
(commit-guard). No strategy research execution, no backtest, no IS/OOS, no data
fetch, no broker/live/paper, no exchange API, no strategy-logic mutation. Safety
tooling + tests + docs only.

- **Created:** 2026-05-30
- **Baseline (Bundle 001):** `9b9b7912c0ff62d09372da4b57222364e735b39f`
- **HEAD at bundle (master):** `9b9b791`
- **Verdict:** **`HYGIENE_READY`** (see §6)

---

## 1. Executive summary

Both hygiene prerequisites are satisfied:

- **H1 — isolated worktree: ALREADY DONE & VERIFIED.** A dedicated worktree exists
  at `C:/sparta-factory-research` on branch `factory-research/crypto-4h-protocol`
  (created by Repo-Hygiene-D5 from base `06cfad7`). It has an **independent index
  and working tree**, sharing only the `.git` object store — so it cannot race the
  JARVIS workstream's HEAD on `master`. Factory tests pass **329/0** inside it.
- **H2 — commit-guard: BUILT & VALIDATED.** A new offline, stdlib-only guard
  (`tools/commit_guard.py` + `tools/commit_guard_rules.json`) classifies a set of
  repo-relative paths and **blocks** any commit that would include JARVIS files,
  runtime snapshots, market/frozen data, broker/live/paper/credential files, or
  strategy-logic changes (the last allowed only with an explicit `--allow-strategy`
  authorization). Covered by **17 new tests**; full factory suite **346 passed / 0
  failed**; `py_compile` clean; the guard self-approves this bundle's own files and
  blocks a mixed cross-lane set.

Because H1 required no unsafe action (the worktree pre-existed and verified clean)
and H2's guard is built, tested, and inert, the verdict is **`HYGIENE_READY`** —
not protocol-only and not blocked.

---

## 2. H1 — Isolated factory-research worktree

### 2.1 Safety assessment

Preflight at bundle start (in `C:/SPARTA_BRAIN`, branch `master`):

| Check | Result |
|---|---|
| HEAD | `9b9b791` (Bundle 001) |
| Staged set | empty |
| Modified tracked files | none |
| Existing worktrees | `C:/SPARTA_BRAIN` (master) **and** `C:/sparta-factory-research` (`factory-research/crypto-4h-protocol` @ `06cfad7`) |

The dedicated worktree **already exists** — it was created in Repo-Hygiene-D5 (the
step after the D4 transition plan). No new worktree creation was needed or
performed this turn.

### 2.2 Worktree health (verified)

| Field | Value |
|---|---|
| Path | `C:/sparta-factory-research` |
| Branch | `factory-research/crypto-4h-protocol` |
| Base commit | `06cfad79d3a70807eed9757ca503fa9231ee7f59` (Repo-Hygiene-D4) |
| Checkout | complete (full repo tree present: `app.py`, `trading_research/agentic_factory`, etc.) |
| Index / working tree | independent of `master` (shares only `.git` objects) |
| Status | clean except one untracked folder: `reports/repo_hygiene_d5_worktree_setup/` |
| Admin record | `.git/worktrees/sparta-factory-research` present |

This is exactly the isolation Repo-Hygiene-D4 recommended: two worktrees with
independent HEADs mean the JARVIS step-builder committing on `master` can never land
on the research branch, and vice-versa.

### 2.3 Loose end (noted, not actioned)

The `repo_hygiene_d5_worktree_setup/report.{md,json}` files are **untracked** inside
the worktree (the D5 setup itself was never committed). They live on the
`factory-research/crypto-4h-protocol` branch's working tree, not on `master`.
Committing them is a **separate, separately-authorized** action on that branch — out
of scope here and intentionally left untouched.

### 2.4 Standing worktree rules (from D5, restated)

- Future factory/crypto **research** runs in `C:/sparta-factory-research`.
- `master` / JARVIS continue independently in `C:/SPARTA_BRAIN`.
- Explicit-pathspec commits only; never `git add .` / `git add <dir>`.
- No merge / rebase / push without explicit approval.
- Preflight each turn on the worktree's own HEAD.

---

## 3. H2 — Commit-guard

### 3.1 What it does

`tools/commit_guard.py` inspects a list of repo-relative paths (by default the git
staged set) and returns a block/allow decision. Deny categories, in evaluation
order (first match wins):

| Category | Severity | Blocks |
|---|---|---|
| `data_file` | hard | `*.csv`, `*.parquet`, anything under `data/`, `data_offline/`, `data_crypto/`, `databento*`, `frozen_regime_inputs` |
| `broker_live_paper` | hard | broker / live / paper-trading / execution / credential / exchange-API / wallet artifacts (incl. exchange-SDK names) |
| `jarvis` | hard | any `jarvis*` path, `app.py`, `templates/base.html` |
| `runtime_snapshot` | hard | `*snapshot*`, `*_snapshots.jsonl`, `data/profit_brain_*`, `media_os_*`, `*_status.json` |
| `strategy_mutation` | **overridable** | factory `engine/`, `config/`, `strategies/`, `loop/` — trading-logic changes |

- **Hard** categories can **never** be overridden — there is no flag that authorizes
  committing data, broker/credential, JARVIS, or runtime-snapshot files from the
  factory lane.
- **`strategy_mutation`** is the only overridable category: it blocks by default and
  passes only when an explicit `--allow-strategy` (or `allow_strategy=True`) is
  given — matching the rule "no strategy logic change unless explicitly authorized."
- Anything matched by **no** deny rule (report `.md`/`.json` under `reports/`, the
  guard tool itself under `tools/`) is **allowed**.

### 3.2 Why a JSON rules file (not patterns in the `.py`)

The factory's own `tests/test_safety_guards.py` scans **every `.py`** under the
module root (except `tests/`) for forbidden substrings (e.g. exchange-vendor and
credential tokens) and fails if any appear. The guard must *match* exactly those
substrings, so they are stored in **`tools/commit_guard_rules.json`** (not scanned,
since it is not a `.py` file) and the `.py` source stays token-clean. This keeps the
new tool fully compatible with the existing offline/inert safety contract.

### 3.3 Why a CLI tool, not an auto-installed hook

The guard is an **opt-in CLI check**, not an auto-installed git hook. Git hooks live
in the shared common `.git` dir and would apply to **both** worktrees — imposing the
factory's rules on the concurrent JARVIS/`master` workstream and risking disruption
to a lane we are told not to touch. An explicit CLI check (run before a factory
commit, or wired as a hook **only inside the factory worktree** by the operator)
gives the protection without that blast radius. The optional opt-in protocol is in
§3.5.

### 3.4 Validation

| Check | Result |
|---|---|
| `py_compile tools/commit_guard.py` | **PYCOMPILE_OK** |
| New tests (`tests/test_commit_guard.py`) | 17 |
| Full factory suite | **346 passed / 0 failed** (329 prior + 17 new) |
| `test_safety_guards` (forbidden-token scan) | **passes** — guard `.py` is token-clean |
| Rules JSON | valid JSON |
| Self-check (this bundle's 6 files) | **PASS** — 6 allowed, 0 blocked |
| Cross-lane check (`app.py`, `data/foo.csv`, `broker/x.py`, a report) | **BLOCKED** — 3 blocked, 1 allowed |

### 3.5 Optional operator protocol — enable as a worktree-scoped hook

Not done automatically. If desired, the operator may wire the guard as a pre-commit
hook **inside the factory worktree only** (leaving `master`/JARVIS untouched):

```bash
# Run inside C:/sparta-factory-research (the factory worktree)
git config core.hooksPath .factory_hooks
mkdir -p .factory_hooks
# .factory_hooks/pre-commit:
#   #!/bin/sh
#   python trading_research/agentic_factory/tools/commit_guard.py || exit 1
chmod +x .factory_hooks/pre-commit
```

Note: the guard tool is committed on `master` in this bundle; the worktree branch
(`factory-research/crypto-4h-protocol`, based at `06cfad7`) will obtain it only when
`master` is merged/cherry-picked into that branch — a **separately authorized**
action. Until then the guard can be invoked from the `master` checkout, or run
ad-hoc by absolute path.

---

## 4. Files added (this bundle)

| File | Purpose |
|---|---|
| `tools/commit_guard.py` | Guard core (`classify_path`, `check_paths`) + CLI |
| `tools/commit_guard_rules.json` | Deny categories + regex patterns (kept out of `.py` for the token scanner) |
| `tools/__init__.py` | Make `tools` importable as a package |
| `tests/test_commit_guard.py` | 17 tests: each category, allow-list, override, hard-not-overridable, normalization, CLI exit codes |
| `reports/strategy_factory_v1_hygiene_bundle_h1_h2/report.md` | This report |
| `reports/strategy_factory_v1_hygiene_bundle_h1_h2/report.json` | Machine-readable twin |

No engine, strategy, config, data, JARVIS, broker, or live/paper file was created or
modified. No worktree was created or destroyed.

---

## 5. Safety attestations

`safety_tooling_and_docs_only` · `no_strategy_research_execution` · `no_backtest` ·
`no_is_oos_run` · `no_data_fetch` · `no_network` · `no_broker_or_exchange_api` ·
`no_paper_or_live` · `no_strategy_logic_mutation` · `no_worktree_created_or_removed` ·
`jarvis_untouched` · `frozen_data_untouched` · `s30_and_parked_branches_read_only` ·
`guard_is_opt_in_not_auto_installed` · `no_shared_git_hooks_modified`.

## 6. Final verdict

# **`HYGIENE_READY`**

- **H1** isolated worktree exists, is healthy, has an independent index/working
  tree, and passes 329/0 — process isolation is in place.
- **H2** commit-guard is built, token-clean, tested (17 new / 346 total passing),
  `py_compile`-clean, self-approves factory docs, and blocks cross-lane / data /
  broker / strategy files (strategy only via explicit override).

The hygiene foundation for an automated overnight Strategy Factory build is
complete. **Next allowed step (separately authorized):** begin the Orchestration
block (Bundle 001 §5 Block O — `validation_runner` + `validation_gates` + candidate
registry + hypothesis queue + safe registration + manual-start overnight batch),
performed in the isolated worktree, with the commit-guard wired in.

---

**Trading recommendation:** NONE. Hygiene/tooling bundle only. All 8 strategy
branches remain PARKED; no active strategy; no paper/live system exists or is
authorized; OOS remains sealed; no strategy logic was touched.
