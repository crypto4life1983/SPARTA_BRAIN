# Repo-Hygiene-D3 — Automation Commit Guard: Diagnosis + Guard Plan (PLAN / MEMO ONLY)

**This is a DIAGNOSIS + GUARD-PLAN MEMO only.** No automation disabled, no JARVIS
code edited, no hook/scheduler changed, no strategy run, no backtest, no IS/OOS, no
data fetch, no optimization, no paper/live. Frozen data untouched. S30/futures
untouched; hydra untouched. **Not staged, not committed.**

- **Created:** 2026-05-30
- **HEAD at diagnosis:** `102202a` (Fix deterministic config wiring test path)
- **No edits made:** true · **No staging:** true · **No commit:** true

---

## 1. Current repo state

- **HEAD:** `102202a` — "Fix deterministic config wiring test path" (Repo-Hygiene-D2).
- **Staged files:** none (`git diff --cached` empty).
- **Factory tree:** clean — nothing modified/untracked inside
  `trading_research/agentic_factory/` except this new D3 report folder.
- **JARVIS files:** none modified or staged currently.
- **Live race observed:** HEAD advanced `c02ec13` → `307d994` ("JARVIS Checkpoint
  Bundle A") **between the D2 work and this D3 preflight** — a live instance of the
  very race being diagnosed.
- **Active git hooks:** none (only `*.sample` present in `.git/hooks`).
- **Scheduled tasks doing git:** none found referencing sparta/jarvis/brain/agentic/commit.

## 2. Evidence found

- **No unattended git committer.** No active hook, no scheduled task, no daemon
  runs `git add`/`git commit`. `auto_brain_cycle.bat` runs
  `python tools/trading_brain_auto.py --commit`, but that tool's `commit()` only
  appends to `brain_memory` text files (append_decision/lesson/next_action/
  system_change) — it does **not** git-commit. `auto_start.bat` only launches the
  dashboard. `brain_brief.py` / `brain_telegram_notify.py` do not commit.
- **Only programmatic git committer in the repo** is
  `sparta_commander/research_orchestrator/safe_executor.py` (git add/commit ~lines
  243/276) — a **gated Commander-lane** executor, not the JARVIS step-builder, and
  not the source of the interleaved JARVIS step commits.
- **Real source of JARVIS commits:** a separate **interactive** workstream (another
  Claude/agent session or operator terminal) authoring `docs/jarvis_step_NN_*`
  deliverables and committing them to `master`. Same identity
  `ryahai <support@ryah.ai>` as the factory commits, which is why the two streams
  are indistinguishable by author.
- **Interleave log (master):** 20:32 crypto D9 → 20:35 JARVIS 44 → 21:29 crypto
  engine / JARVIS 45 → 21:34 JARVIS 46 → 21:41 crypto IS → 21:46 OOS protocol →
  21:59 OOS_FAIL → 22:02 JARVIS 47 → 22:12 JARVIS 48 → 22:14 crypto D14 → 22:15
  JARVIS 49 → 22:42 JARVIS Bundle A → 22:42 factory D1 → 22:47 factory D2.
- **JARVIS commit blast radius:** JARVIS commits touch `docs/jarvis_*` **and**
  repo-root code — `app.py`, `templates/jarvis.html`, `tests/test_jarvis_*`,
  `tools/jarvis_*` (verified across `307d994`, `c02ec13`, `8133af3`, `52cd272`,
  `381ad99`, `b737e4a`).
- **Critical disjointness finding:** **none** of the inspected JARVIS commits
  touched `trading_research/agentic_factory/`. The two workstreams have so far
  committed to **disjoint path subtrees** — factory turns touch only the factory
  tree; JARVIS turns touch `docs/jarvis_*`, `app.py`, `templates/jarvis.html`,
  `tools/jarvis_*`, `tests/test_jarvis_*`.

## 3. Risk model

- **What causes HEAD races:** two concurrent workstreams committing to the **same
  `master`**. HEAD advances between factory approval turns because the JARVIS
  workstream commits in the gap. This is a **coordination / branch-topology** issue,
  not a rogue script.
- **Touches the factory tree?** No — no observed JARVIS commit reached into
  `trading_research/agentic_factory/`. Subtrees are disjoint in practice.
- **Can stage unrelated files?** Only if a turn uses `git add .` / `git add <dir>`.
  Factory turns already avoid this via explicit pathspec, so a factory commit cannot
  sweep JARVIS files and vice versa. The risk is **latent**, contained only by manual
  discipline.
- **JARVIS-only or sometimes factory?** Observed JARVIS commits are JARVIS-only.
  The earlier D9 near-miss was a JARVIS-workstream commit landing a deliverable
  **before** the factory turn's approval — a timing/ordering hazard, not a
  wrong-files sweep.
- **Can it be paused safely?** Yes in principle — the JARVIS committer is an
  interactive session, not a daemon, so "pausing" means operator coordination. There
  is no cron to disable.
- **Branch workflow vs pausing:** a dedicated factory-research branch is structurally
  stronger — it removes the shared-HEAD coupling entirely (research-branch HEAD is
  stable regardless of JARVIS activity on master) and makes a deliberate merge the
  single integration point. Pausing relies on human timing every turn; branching
  relies on topology once.
- **Residual risk level:** MEDIUM — contained today purely by explicit-pathspec +
  per-turn preflight (manual discipline). Not enforced by any guard.

## 4. Guard options comparison

| Option | Benefit | Risk | Files affected | Complexity | Recommendation |
|---|---|---|---|---|---|
| **A. Pause JARVIS during factory sessions** | Zero code change; available now; eliminates interleave in the window | Relies on human timing every turn; doesn't fix shared-branch coupling; JARVIS work backs up | none (operational) | trivial | Useful stopgap, not durable |
| **B. Separate factory-research branch** | Removes shared-HEAD coupling at topology level; stable preflight ancestry; deliberate merge is the single integration point | Operator must stay on the branch; small merge ceremony | none (git branch only) | low | **RECOMMENDED primary fix** |
| **C. Commit-guard sentinel/lock file** | Lightweight lock both streams check in preflight; cheap; documents intent | Advisory unless hook-enforced (hook = D4/D5, approval-gated); stale lock if a session crashes | new sentinel/doc file; optional future hook | low / medium | Good lighter fallback; pairs with B |
| **D. Restrict automation pathspec to JARVIS-only** | JARVIS committer can never stage factory files even with `git add .` | Requires **editing JARVIS commit logic** — out of scope here; committer is interactive (no single script) | JARVIS commit path | medium-high (gated) | Defer; not plan-only actionable |
| **E. Automation stops at staged state, no commit** | Centralizes the commit decision in a human | Defeats much of automation's purpose; high friction; doesn't stop interleave alone | JARVIS commit path (edit) | medium (gated) | Not recommended — too restrictive |
| **F. Do nothing but always explicit-pathspec** | Already in force; zero new work; has prevented every sweep so far | Pure manual discipline; one `git add .` lapse re-opens sweep risk; doesn't stop HEAD races | none | none | **KEEP as permanent safety net** (necessary, not sufficient) |

## 5. Recommended guard path

- **Primary:** **B (dedicated factory-research branch)** — durable structural fix
  that removes shared-HEAD coupling **without editing any JARVIS/automation code**.
- **Permanent safety net:** **F (explicit-pathspec commits, already standing)** —
  keep on every commit regardless of branch.
- **Lighter fallback if B is rejected:** **C (advisory sentinel/lock file)** checked
  in preflight; optionally hardened into a pre-commit hook later under D4/D5 approval.
- **Stopgap:** **A (pause JARVIS during a factory commit window)** — acceptable only
  until B is adopted.
- **Deferred:** **D and E** both require editing the JARVIS/automation commit path
  and are **prohibited in this plan-only step**; route to D4/D5 with explicit
  authorization if ever pursued.

**Rationale:** the race is a branch-topology + coordination problem, not a rogue
committer. Fixing topology (B) is stronger and lower-blast-radius than editing
automation code (D/E). F already prevents file sweeps; B additionally stabilizes
HEAD ancestry. **No code/scheduler/JARVIS change is required to adopt B + F.**

## 6. Exact future implementation steps

**Adopt B (branch isolation):**
1. From a clean tree on `master` at the intended base, create the branch:
   `git switch -c factory-research`.
2. Do all factory work + decision-record commits on `factory-research` using the
   **same explicit-pathspec** method.
3. Preflight each turn checks the `factory-research` HEAD only; JARVIS commits on
   `master` no longer move it.
4. Integrate deliberately at a milestone:
   `git switch master && git merge --no-ff factory-research`, resolving only factory
   paths.
5. Never `git add .`; continue
   `cd C:/SPARTA_BRAIN && git commit -m MSG -- <explicit factory paths>`.

**Keep F (safety net):** every commit on any branch uses explicit repo-root-relative
pathspecs; never `git add .` or `git add <dir>`.

**Optional C (sentinel):** define a documented advisory lock both workstreams check
in preflight; hardening it into an enforced pre-commit hook is a D4/D5 item requiring
explicit approval (hooks change repo behavior).

## 7. Files likely to be edited in D4/D5

- **B (branch isolation):** no source edits (git branch/workflow only); possibly a
  short doc note under `trading_research/agentic_factory/` describing the protocol.
- **C (advisory sentinel):** a new advisory note/lock file under
  `trading_research/agentic_factory/` (doc only).
- **C or D enforced hook (only if ever approved):** `.git/hooks/pre-commit` — a real
  behavior change; explicit approval required; out of scope until D4/D5.
- **D or E automation edit (only if ever approved):** the JARVIS step-builder commit
  path — an interactive session, not a confirmed single script; would require
  locating and editing that committer; explicit approval required.
- **Do NOT edit:** `tools/trading_brain_auto.py` is NOT the git committer and must
  not be edited for this. Do not edit `auto_brain_cycle.bat` / `auto_start.bat` for
  the race (they do not git-commit).

## 8. Forbidden actions (this step)

`no_disabling_automation_yet` · `no_editing_jarvis_code_yet` ·
`no_changing_hooks_or_schedulers_yet` · `no_strategy_runs` · `no_backtest` ·
`no_oos_use` · `no_data_fetch` · `no_optimization` · `no_paper_or_live` ·
`no_exchange_api` · `no_broker` · `no_modification_of_frozen_crypto_data` ·
`do_not_touch_s30_or_futures` · `do_not_touch_hydra` · `no_staging` · `no_commit`.

## 9. Final line

**Repo-Hygiene-D3 is a diagnosis and guard-plan memo only; no automation, scheduler,
JARVIS, or trading behavior was changed.**
