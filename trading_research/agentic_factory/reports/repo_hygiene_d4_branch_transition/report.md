# Repo-Hygiene-D4 — Dedicated factory-research Branch: Transition Plan / Check (PLAN / CHECK ONLY)

**This is a branch transition PLAN / CHECK only.** The dedicated branch was **NOT
created** this turn (precondition not met — see §4a). No files modified, no staging,
no commit, no merge/rebase/push. No strategy run, no backtest, no IS/OOS, no data
fetch, no paper/live. Frozen data untouched. S30/futures untouched; hydra untouched.

- **Created:** 2026-05-30
- **HEAD at check:** `9b53703` (Plan factory automation commit guard, Repo-Hygiene-D3)
- **Branch created:** **NO**

---

## 0. Preflight

- **HEAD:** `9b53703` (Repo-Hygiene-D3).
- **Current branch:** `master`.
- **Staged files:** none (`git diff --cached` empty).
- **Factory tree:** clean — nothing modified/untracked inside
  `trading_research/agentic_factory/` except this new D4 report folder.
- **Modified tracked files (repo-wide):** `app.py`, `templates/jarvis.html`,
  `tests/test_jarvis_ask_contract.py`, `tests/test_jarvis_snapshot_report.py` — **all
  four are JARVIS-workstream files**, i.e. the concurrent session's uncommitted
  in-flight work. **Not** factory files.
- **Working tree clean enough to branch?** **No** — Step 2 requires "no unrelated
  files that make checkout unsafe," and four modified tracked JARVIS files are present.

## 1. Previous branch and HEAD

- **Branch:** `master`
- **HEAD:** `9b5370331d27395d07cd935eb829b3461097dbe3` (`9b53703`)

## 2. New branch name

- **Proposed primary:** `factory-research/crypto-4h-protocol`
- **Fallback (if slash disallowed):** `factory-research-crypto-4h-protocol`
- **Existence check:** neither variant exists; the name is free.
- **Status:** branch **NOT created** this turn.

## 3. Why the branch would be created

Per D3 recommendation **B**: isolate the factory-research HEAD from JARVIS-workstream
commits on `master`, so preflight ancestry is stable and a deliberate merge becomes
the single integration point. Creation is **deferred** — see §4a.

## 4. Confirmation no files changed

Confirmed. No branch created, no tracked file modified by this step, no merge/rebase/
push, no staging, no commit. The only new files are the two D4 memo files (untracked):
`report.json` + `report.md`.

## 4a. Why the branch was NOT created + recommended mechanism

- **Blocker 1 — dirty tree:** the working tree carries 4 modified tracked JARVIS files
  (the concurrent workstream's uncommitted in-flight work). Branching while they are
  dirty would carry their changes onto the new branch.
- **Blocker 2 — shared single worktree (critical):** in **one** working directory all
  branches share **one** index and **one** working tree. `git switch -c` does **not**
  give two concurrent sessions independent branches — whichever session switches last
  sets HEAD for **both**. If the JARVIS session commits while HEAD points at
  `factory-research`, its commit lands on the research branch — exactly the
  cross-contamination D3 sought to prevent. So a plain `git switch -c` in the shared
  `C:\SPARTA_BRAIN` worktree does **not** actually isolate the two sessions.
- **Recommended mechanism — `git worktree add`:** give `factory-research` its **own
  directory + index + working tree**, sharing only the `.git` object store. Example
  (**DEFERRED — do not run without approval**):
  `git worktree add ../sparta-factory-research -b factory-research/crypto-4h-protocol 9b53703`.
  The factory session then works in `../sparta-factory-research`; the JARVIS session
  stays in `C:\SPARTA_BRAIN`. Neither races the other's HEAD and commits cannot cross
  branches.
- **Safe precondition for a plain switch (if no separate worktree):** create/switch
  only from a genuinely clean tree (no modified tracked files, no in-flight JARVIS
  edits) **and** only while the JARVIS session is paused.
- **Decision:** branch **NOT created**. Defer creation to a separately authorized
  step — preferably via `git worktree add` for true isolation, or via plain
  `git switch -c` only from a clean/paused tree.

## 5. Branch rules (once created)

- Keep **explicit-pathspec** commits:
  `cd <worktree root> && git commit -m MSG -- <explicit factory paths>`.
- **Never** use `git add .` or `git add <dir>`.
- Do **not** merge / rebase / push without explicit approval.
- JARVIS / `master` may continue separately and independently.
- The factory branch is for **crypto/factory research only** — no JARVIS files, no
  unrelated files.
- Preflight every turn on the factory branch's own HEAD (or its worktree HEAD).

## 6. Next allowed step

**Crypto-4H-D1 protocol memo only** (no data fetch, no backtest, no IS/OOS, no
paper/live). Branch creation itself remains a separately authorized action.

## 7. Forbidden actions (this step)

`no_strategy_runs` · `no_backtest` · `no_oos_use` · `no_data_fetch` ·
`no_optimization` · `no_paper_or_live` · `no_exchange_api` · `no_broker` ·
`no_modification_of_frozen_crypto_data` · `do_not_touch_s30_or_futures` ·
`do_not_touch_hydra` · `no_merge_rebase_push` · `no_staging` · `no_commit` ·
`no_file_modification_when_branching` · `no_disturbing_concurrent_jarvis_in_flight_files`.

## Final line

**Repo-Hygiene-D4 is a branch transition plan/check only; the dedicated
factory-research branch was NOT created** because the working tree carries the
concurrent JARVIS workstream's in-flight modifications and a single shared worktree
cannot isolate two sessions via a plain switch. Recommended: create via
`git worktree add` (true isolation) under separate authorization, or via plain switch
only from a clean/paused tree. No files changed, no staging, no commit, no
merge/rebase/push.
