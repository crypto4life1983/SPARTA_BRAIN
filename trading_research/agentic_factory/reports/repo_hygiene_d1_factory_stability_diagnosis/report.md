# Repo-Hygiene-D1 — Factory Stability Diagnosis (DIAGNOSIS / MEMO ONLY)

**This is a DIAGNOSIS MEMO only.** No code edited, no config edited, no strategy
work, no backtest, no IS/OOS run, no data fetch, no network, no exchange API, no
broker, no paper/live. Frozen data untouched. S30/futures untouched;
JARVIS/`templates/base.html`/hydra untouched. **Not staged, not committed.**

- **Created:** 2026-05-30
- **HEAD at diagnosis:** `c02ec13` (Add JARVIS Step 49 live server restart protocol)
- **No edits made:** true · **No staging:** true · **No commit:** true

---

## 1. Current repo state

- **HEAD:** `c02ec13` — "Add JARVIS Step 49 live server restart protocol".
- **Staged files:** none (`git diff --cached` empty).
- **Factory tree:** clean — no modified/untracked files inside
  `trading_research/agentic_factory/` (other than this new report folder).
- **JARVIS files:** none modified or staged currently.
- **Repo-wide untracked:** a large pre-existing set of untracked files across the
  repo root and `data/` (unrelated to the factory; not part of this step).
- **Corrupt path observed:** `git status` emits
  `warning: could not open directory 'hydra /': No such file or directory`. The
  filesystem shows a junk directory entry repr `'hydra '` (leading U+F022
  private-use char + trailing space) at the repo root. This is the **P2 hydra
  path issue** — untracked, at repo root, outside the factory.

## 2. Config test failure diagnosis

- **Failing test:**
  `tests/test_config_wiring.py::test_load_config_includes_strategy_block`.
- **Test body:**
  `cfg = factory_loop._load_config("config/factory_config.yaml")` then
  `assert cfg["strategy"]["session_start"] == "14:30"`.
- **Committed config value:** `config/factory_config.yaml` line 23
  `session_start: "14:30"` — **CORRECT** (committed at `81a272a`; working copy
  unmodified vs HEAD; only ONE `factory_config.yaml` exists in the repo).
- **Observed test value:** `09:30`.

### Root cause — CWD-brittle test, NOT a config mismatch

The test passes a **relative** path `"config/factory_config.yaml"` to
`_load_config()`. `_load_config` (`loop/factory_loop.py` line 40) checks
`os.path.exists(config_path)` **without resolving it** (it does not call
`_resolve()`). pytest runs with **CWD = repo root `C:/SPARTA_BRAIN`**, so the
relative path resolves to `C:/SPARTA_BRAIN/config/factory_config.yaml`, which
does **not** exist. `_load_config` therefore returns the hard-coded `defaults`,
whose strategy block = `proposer.base_params()`, and `proposer.base_params()`
(`engine/proposer.py` line 23) sets `session_start = "09:30"`. Hence the test
reads `09:30` and fails.

### Why production is unaffected

`run_once()` (line 67) builds an **absolute** path
`os.path.join(_MODULE_ROOT, "config", "factory_config.yaml")` before calling
`_load_config`, so the real run always loads the correct `14:30` config. The
sibling test `test_run_once_uses_config_strategy` writes a tmp config and passes
its own path, so it also passes. **Only** `test_load_config_includes_strategy_block`
hard-codes a bare relative string and is thus CWD-dependent.

### Classification

Test brittleness (path-resolution / CWD dependency). **NOT** a committed config
mismatch, **NOT** a runtime override, **NOT** an environment secret, **NOT** an
automation flap. The expected value `14:30` is correct (09:30 ET == 14:30 UTC;
the CSV `ts_event` is UTC). Config and test expectation agree on `14:30`; the bug
is purely that the loader falls back to defaults when the path is unresolved.

### Minimal deterministic fix options

- **OPTION A (fix the test — lowest blast radius, RECOMMENDED):** in
  `test_load_config_includes_strategy_block`, resolve the path the same way
  production does, e.g.
  `factory_loop._load_config(factory_loop._resolve("config/factory_config.yaml"))`.
  Deterministic regardless of CWD; touches only the test file.
- **OPTION B (fix the loader — also safe):** make `_load_config` resolve a
  relative `config_path` against `_MODULE_ROOT` before `os.path.exists` (mirror
  `_resolve`). Safe because the only other caller, `run_once`, already passes an
  absolute path (absolute passes through `_resolve` unchanged). Slightly larger
  blast radius (production module).

**Recommended:** OPTION A (edit only the test) for P0 — surgical, no
production-code change, makes the suite deterministic. OPTION B is a reasonable
follow-up consistency improvement but is not required to make the test pass. Do
**not** change the config (already correct at 14:30); do **not** change the
proposer base default `09:30` (it is the intended ET base default).

## 3. Automation-race diagnosis

- **Symptom:** a background "automation/JARVIS" workstream repeatedly advances
  HEAD and sometimes commits artifacts between explicit approval turns (observed:
  HEAD moved `52cd272` → `8133af3` → `c02ec13` across the D14 turns).
- **Git hooks:** only `*.sample` hooks present in `.git/hooks` (none active).
- **Scheduled tasks:** no Windows scheduled task references
  sparta/jarvis/brain/agentic/commit.
- **Auto-commit tool:** `auto_brain_cycle.bat` line 16 runs
  `python tools/trading_brain_auto.py --commit`, **BUT** that tool's `commit()`
  (`tools/trading_brain_auto.py` line 406) only appends to `brain_memory` text
  files (append_decision/lesson/next_action/system_change). It does **not** run
  `git add` or `git commit`. So it is **NOT** the source of the JARVIS git commits.
- **Real git committer in repo:** the only programmatic real `git add`/`git
  commit` is `sparta_commander/research_orchestrator/safe_executor.py` (lines
  243/276) — a gated executor in the Commander lane, not the JARVIS step builder.
- **Commit metadata:** JARVIS step commits are authored AND committed by
  `ryahai <support@ryah.ai>` — the same identity as the factory commits.
- **Interleave evidence:** on `master`: 21:41 D11, 21:46 D12, 21:59 D13, 22:02
  JARVIS Step 47, 22:12 JARVIS Step 48, 22:14 D14, 22:15 JARVIS Step 49.
  Factory-research commits and JARVIS-step commits are interleaved in time on the
  **same branch**.

### Root cause

**Not** an unattended cron/hook/auto-git script inside this repo. The race is
**two concurrent workstreams** committing to the same `master` branch: (1) these
factory-research approval turns, and (2) a separate JARVIS step-builder
workstream (another interactive Claude/agent session or operator terminal) that
commits `docs/jarvis_step_NN_*` between turns. HEAD advances between approvals
because the JARVIS workstream commits in the gap.

### Why it is a risk

Shared-branch concurrency means: (a) preflight HEAD can differ from the last
factory commit even when nothing factory-related changed; (b) a `git add .` /
`git add <dir>` would sweep the other workstream's files (already avoided here via
explicit pathspec); (c) a near-miss already occurred earlier (a D9 deliverable was
committed by the other workstream before approval). The mitigation is **process
isolation**, not disabling a scheduler.

## 4. Risk assessment

| Issue | Severity | Impact |
|---|---|---|
| **Config test** | LOW-MEDIUM | A permanently-red test trains readers to ignore "1 failed", masking a future real regression; pollutes every report's test caveat. No production impact (run_once loads 14:30 correctly). Likelihood of masking a real bug: MEDIUM over time. |
| **Automation race** | MEDIUM | Shared-branch interleaving complicates every preflight and risks a wrong-files commit if pathspec discipline ever lapses; already caused one pre-approval-commit near-miss. Currently contained ONLY by strict explicit-pathspec commits + per-turn preflight — manual discipline, not an enforced guard. |
| **Hydra corrupt path** | LOW | `git status` emits a warning each run on directory `'hydra /'` (junk name with U+F022 + trailing space). Cosmetic noise + could confuse tooling that walks the tree; outside the factory. Do NOT auto-delete — confirm it is genuinely junk (likely a corrupt MoviePy temp artifact) before any removal, under separate authorization. |

## 5. Recommended fixes

- **Config test:** apply OPTION A (resolve the path in the test via
  `factory_loop._resolve`) as a P0 deterministic fix. Do NOT change the config
  (already correct at 14:30). Do NOT change the proposer base default `09:30`
  (intended ET base default).
- **Automation race:** P1 — introduce a commit guard / process isolation so
  factory-research commits are not interleaved with the JARVIS workstream.
  Preferred: run factory-research work on a dedicated branch (e.g.
  `factory-research`) and merge deliberately; OR pause the JARVIS step-builder
  during factory commit windows; OR add a lightweight advisory lock file the
  factory turns check in preflight. Decide in D3; do not change auto-commit
  behavior without approval.
- **Hydra path:** P2 — separately authorized cleanup (D4). Verify the entry is a
  corrupt temp artifact, then remove with a Windows-safe path method. Not in
  scope here.

## 6. Fix priority

- **P0:** `test_config_wiring` deterministic fix (edit the test path resolution
  only).
- **P1:** automation commit guard / branch isolation during research (pause or
  isolate the JARVIS workstream so it stops racing HEAD).
- **P2:** hydra corrupt-path (`'hydra '`) repair, only if still present,
  separately authorized.

## 7. Exact files that would need editing later

- **P0 config test:**
  `trading_research/agentic_factory/tests/test_config_wiring.py`
  (`test_load_config_includes_strategy_block`: resolve the config path via
  `factory_loop._resolve` before loading) — ONLY this file under OPTION A.
  *(OPTION B alternative, NOT recommended for P0)*
  `trading_research/agentic_factory/loop/factory_loop.py` `_load_config` — resolve
  relative `config_path` against `_MODULE_ROOT` before `os.path.exists`.
- **P1 automation guard:** process/governance change, not necessarily a factory
  file. Candidate touch points: a new factory branch (no file edit), OR a small
  preflight lock-file convention (doc + check), OR pausing
  `auto_brain_cycle.bat` / the JARVIS builder during research.
  `trading_brain_auto.py` is NOT the git committer and should not be edited for this.
- **P2 hydra:** no source file — a filesystem cleanup of the junk directory entry
  at repo root (outside the factory).

## 8. Safe next steps

- **Repo-Hygiene-D2:** apply the deterministic config-test fix ONLY (OPTION A:
  edit `test_config_wiring.py` path resolution). Run scoped suite; expect 329
  passed / 0 failed. Separately authorized.
- **Repo-Hygiene-D3:** automation commit guard / branch isolation for research.
  Separately authorized.
- **Repo-Hygiene-D4:** hydra corrupt-path repair. Separately authorized.

## 9. Forbidden actions (this step)

`no_trading_strategy_work` · `no_data_fetch` · `no_backtest` · `no_oos_use` ·
`no_paper_or_live` · `no_exchange_api` · `no_broker` · `no_optimization` ·
`no_auto_commit_changes_without_approval` · `no_edit_until_separately_authorized` ·
`no_modification_of_frozen_crypto_data` · `do_not_touch_s30_or_futures` ·
`do_not_touch_hydra_yet` · `no_staging` · `no_commit`.

---

**Final line:** Repo-Hygiene-D1 is a diagnosis memo only; no code/config was
edited, no strategy/data/paper/live work occurred. Config failure root cause =
CWD-brittle test path (config is correct at 14:30); automation race root cause =
concurrent JARVIS workstream committing to the same `master` branch (no
hook/scheduler/auto-git-script). Recommended next: Repo-Hygiene-D2 deterministic
config-test fix only.
