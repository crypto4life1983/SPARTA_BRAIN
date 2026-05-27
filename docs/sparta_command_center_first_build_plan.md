# SPARTA Trading Command Center — First Build Plan (v1: lifecycle viewer)

**Document type:** PLANNING ONLY. No code is written by this document. No
route, template, or test is added. No file outside this one is created or
modified.

**Companion memo:** `docs/fincept_inspiration_review_for_sparta_trading_command_center.md`
(committed as `a2ca6f7 Add Fincept inspiration review memo`).

**Status this plan must preserve while it exists on disk:**
- Trading `PAUSED`
- Live `BLOCKED_AT_6_GATES`
- FRC `NEVER_GRANTED`
- `no_strategy_optimization_authorized = True`
- All sealed-artifact byte-stability invariants in force
- The operator must still type a literal `Authorize ...` phrase before any
  build step in this plan is executed.

---

## 1. Purpose

Define the **smallest possible** first implementation of the SPARTA Trading
Command Center: a single read-only HTTP route at `/command` that surfaces
the **B006_002 candidate lifecycle** state (and any sibling `B006_*`
lifecycles already on disk) in one dense panel, with sha re-verification,
no write paths, no fetch capability, no trading affordance.

This is **Module 1** of the eight-module list in the companion memo
(§3, "Sealed-Artifact Lifecycle Viewer"). The other seven modules are
out of scope for v1 and each require their own separate plan +
`Authorize ...` phrase.

The plan is intentionally tight: small surface, small test, small commit,
clean rollback. If v1 ships cleanly and survives a week of operator use
without surprises, Module 2 (`/command/gates`) is the next candidate —
under a separate plan.

---

## 2. Why this comes after commit `a2ca6f7`

Commit `a2ca6f7` (`Add Fincept inspiration review memo`) added the
review-only memo that:

- Decided **what** to absorb from Fincept (single-pane surface, dense
  read-only panels, sha-verified rendering) and **what** to reject
  (any broker connector, paper-trading panels, LLM-on-portfolio,
  auto-strategy generation, one-click deploys, runtime lock-in).
- Listed eight future modules in priority order, with Module 1
  (lifecycle viewer) as the recommended first build step.
- Locked the final recommendation: **inspiration only, not dependency.**

That memo authorized nothing — it was a thinking document. This plan is
the next thinking document: it converts the memo's "first safe build
step" paragraph into a concrete, reviewable specification *without
writing any code*. The operator's `Authorize ...` phrase to execute this
plan is a separate, future event; this document does not request it.

The two documents form a deliberate ladder:

1. `fincept_inspiration_review_for_sparta_trading_command_center.md`
   — strategic posture (committed `a2ca6f7`).
2. `sparta_command_center_first_build_plan.md` — this file, tactical
   plan for v1 only.
3. (Future, not authorized) Operator types
   `Authorize Command Center v1 lifecycle viewer build.` — implementation
   may then begin under the boundaries in §6 and §11.

---

## 3. Files allowed in the future implementation

When (and only when) the operator authorizes the v1 build, the
implementation may touch exactly the following files. Anything else
is out of scope and requires re-planning.

| Path | Action | Notes |
|------|--------|-------|
| `app.py` | additive edit | Add **one** new FastAPI route handler `GET /command`. No removal, no rename, no modification of any existing route. |
| `templates/command.html` | new file | New Jinja2 template, sibling to `templates/commander.html` / `templates/guide.html`. Pure read-only HTML; no `<form>`, no `<button>` with a POST handler, no JS that issues mutating requests. |
| `tests/test_app_command_route.py` | new file | New pytest module, sibling to `tests/test_app_shadow_validator_route.py`. Asserts the route's read-only contract (see §10). |
| `database.py` | additive edit | One call to `db.upsert_manual_entry()` registering the `/command` row for `/guide`, following the pattern documented in `CLAUDE.md` §"Other system docs". If a helper for this already exists at module scope, reuse it; do not add a new helper if not needed. |

That is the **complete** allowed-files list for v1. Four files. One
additive route, one new template, one new test module, one
documentation-row insert.

Optional, allowed only if needed for clean module structure:

| Path | Action | Notes |
|------|--------|-------|
| `command_center/__init__.py` | new file (optional) | Empty or trivial package marker if the lifecycle-scan helper grows beyond ~50 lines inside `app.py`. |
| `command_center/lifecycle_scan.py` | new file (optional) | Pure read-only function: walks `reports/external_research_hunter/`, returns a list of lifecycle rows. No network. No subprocess. No write. If used, must be covered by `tests/test_app_command_route.py` (or a sibling unit test in `tests/test_command_center_lifecycle_scan.py`). |

The optional package is **discouraged** for v1 unless code clarity
demands it. Prefer keeping v1 as small as possible inside `app.py`.

---

## 4. Files forbidden

The future implementation **must not** touch any of the following.
Forbidden means: no read-then-overwrite, no edit, no delete, no
rename, no move, no template-include of these files via a write path.

- Anything under `reports/external_research_hunter/b006_*` — sealed
  artifacts. Read-only display only; **never** written.
- Anything matching `*_compact_summary_canonical.json` anywhere on
  disk. Read-only display only.
- Anything matching `*_result_sealing_report.{md,json}` or
  `*_archival_memo.{md,json}`. Read-only display only.
- `reports/external_research_hunter/b006_002_qc_run_capture/**` —
  operator-owned capture directory; never written by controller.
- Any S10-D1 file. Concretely (non-exhaustive, planned-implementation
  must respect the spirit even for paths not listed here):
  - `data/s10_d1_mnq_mgc_databento_long_history/**`
  - `reports/s10_d1_mnq_mgc_databento_long_history_step_02b_data_ingest_success_report.{json,md}`
  - `reports/s10_d1_*` of any kind
  - `docs/s10_d1_mnq_mgc_databento_long_history_*`
  - `docs/s10_d1_mnq_mgc_step02b_operator_fetch_runbook.md`
  - The three pre-existing **unstaged** S10-D1 files that were
    `git restore --staged`-d before commit `a2ca6f7`. Their on-disk
    state must remain exactly as it is.
- Any S10-D2 file. Concretely:
  - `SPARTACUS_CLONE_ENGINE/` is unrelated and unaffected; the S10-D2
    paths are under the strategy-lab test scaffolds / synthetic
    fixtures referenced by commit `ce2920a`. Implementation must not
    edit them or import from them.
- Any sealed runner under a candidate lifecycle: `main.py`, `guard.py`,
  `execution_guard.py`, `README.md` build-pins, `RUN_BOOK.md`.
- Any sparta_commander file. Concretely: `sparta_commander/**`. The
  command center is a **sibling** to Commander (per memo §4.4), not
  a modifier of it. It reads no Commander state via Commander's
  internal write paths.
- Any `local_secrets/**`. Never opened, never imported, never
  referenced.
- Any broker, exchange, or order-related file or library. None exist
  in scope; none may be added.
- Trading strategy files of any kind: `S7_*`, `S8_*`, `S9_*`, `B005_*`,
  `B006_*` strategy code under any directory.
- The `"hydra "` ghost directory (trailing space). Not in scope.
  Implementation must not touch it, must not "fix" it, must not
  reference it.
- `brain_memory/projects/trading_bot/decisions.md` — read-only
  consumption for parsing the latest expected `Authorize ...`
  phrase; never written by `/command`. (Writes to decisions.md happen
  via the normal post-work brain-memory append flow, not via the web
  route.)
- Any file already modified-but-unstaged in the working tree as of
  commit `a2ca6f7` (the `M brain_memory/projects/trading_bot/lessons.md`
  entry). Implementation must not stage or commit them as a side
  effect.

---

## 5. Data sources allowed for read-only display

The v1 page may read (and only read) from these locations on disk:

1. `reports/external_research_hunter/` — for B006_* lifecycle artifacts.
   Specifically the following filename patterns the page will surface:
   - `b006_*_spec_draft.{md,json}`
   - `b006_*_spec_seal.{md,json}` (or whichever sealed-spec filename
     pattern is already on disk)
   - `b006_*_runner_build_report.{md,json}`
   - `b006_*_guard_build_report.{md,json}`
   - `b006_*_operator_qc_execution_acknowledgment.{md,json}`
   - `b006_*_operator_*prep*.{md,json}`
   - `b006_*_RUN_BOOK.md`
   - `b006_*_result_sealing_report.{md,json}`
   - `b006_*_archival_memo.{md,json}`
   - `b006_*_qc_run_capture/b006_*_compact_summary_canonical.json`
2. `brain_memory/projects/trading_bot/decisions.md` — last-N decision
   entries only (newest first), to extract the current expected
   `Authorize ...` phrase per lifecycle. Read-only.
3. `brain_memory/projects/trading_bot/next_actions.md` — newest entries
   only, to surface the "Operator picks one" block per lifecycle.
   Read-only.

What the page **does not** read in v1:

- Anything under `data/databento/`, `data/databento_cache/`,
  `data/frozen_regime_inputs/`. (Reserved for Module 3 `/command/data`,
  not v1.)
- Anything under `research_os/` or `reports/research_os/`. (Reserved
  for Module 4 `/command/reports` and/or future Module 8
  `/command/research`.)
- Anything under `sparta_commander/`. (Reserved for Module 6
  `/command/commander`.)
- Live broker, exchange, or wallet state. None exists in this repo
  and none will be added.

---

## 6. Security boundaries

These boundaries are non-negotiable in the future implementation.

1. **Localhost-only bind.** The `/command` route is served by the
   existing FastAPI app at `127.0.0.1:8765`. No change to bind
   interface, no new port, no remote exposure. If the existing app
   binds to a non-localhost address in any environment, that is a
   separate hardening item — out of scope for v1.
2. **Read-only HTTP verb.** `GET` only. No `POST`, no `PUT`, no
   `PATCH`, no `DELETE`. No method handler at all for non-`GET`
   verbs on `/command` (FastAPI default 405 is acceptable).
3. **No mutating side effects.** Handler must not write any file,
   must not call any subprocess, must not open any socket, must not
   touch the database except via the existing read APIs (and the
   one-time `db.upsert_manual_entry()` at startup, **not** per
   request).
4. **No credentials in scope.** Handler does not read, import, or
   reference `local_secrets/`, environment variables containing
   keys, or any provider SDK that requires keys.
5. **No external network.** Handler makes no HTTP, DNS, or socket
   call to any remote host. No vendor SDK initialization.
6. **Sha re-verification.** For every artifact rendered, the handler
   recomputes `sha256` of the on-disk file body and compares against
   the declared seal (where one exists, e.g. in the JSON sidecar's
   `report_seal_sha256`, `spec_seal_sha256`, declared
   `LOW_LOG_*_SHA256` markers). On mismatch, the row is flagged
   `SEAL_DRIFT` in the rendered output; the handler does **not**
   silently render mismatched data and does **not** modify the file.
7. **No template-injected user input.** v1 has no query params, no
   form, no input field. The route returns a static-per-request view
   of on-disk state. Future query params (e.g. `?lifecycle=b006_002`)
   are out of scope for v1.
8. **No write to `system_manual_entries` at request time.** The
   `db.upsert_manual_entry()` call lives at module-import / startup
   time, not inside the request handler.
9. **CSRF / auth posture inherits the existing dashboard.** No
   weakening. If the existing dashboard is currently un-auth'd
   (localhost-only is its security model), `/command` uses the same
   model — it does not add bypasses and does not add its own auth
   model that could weaken the umbrella.
10. **Failure mode is fail-closed.** If the handler cannot read a
    required file, cannot parse a JSON sidecar, or cannot recompute
    a sha, the rendered row shows `ERROR` / `MISSING` / `SEAL_DRIFT`
    explicitly. The handler never substitutes synthetic data,
    never falls back to stale cache, never emits a default that
    could be mistaken for a real reading.

---

## 7. What the page should show in version 1

Single dense panel, one block per B006_* lifecycle found on disk
(in v1, this will be just `b006_002`; the pattern is generalized
so future `b006_003`+ append automatically).

Per lifecycle block, in this order:

1. **Lifecycle ID** (e.g. `B006_002`).
2. **One-line description** (parsed from the spec SEAL artifact's
   title / candidate description field; literal text, no rewording).
3. **Sealed verdict** (e.g. `REJECT_FAST`) — only if the
   result-sealing report exists.
4. **Phase ladder, 0–8**, with each phase marked one of:
   `✅ COMPLETE` / `⏭ NEXT` / `⏸ PENDING` / `❌ DECLINED` /
   `— N/A`. Source: presence/absence of the lifecycle artifact files
   on disk, cross-checked against the most recent decision entry.
5. **Per-artifact row table**, with columns:
   - `Artifact name` (filename basename)
   - `Path` (clickable only as plain text; no `<a>` to mutating URL)
   - `Bytes`
   - `Declared sha` (from sidecar / pin, where applicable)
   - `Recomputed sha`
   - `Status` (`OK` / `SEAL_DRIFT` / `MISSING` / `NO_DECLARED_SHA`)
6. **Current expected `Authorize ...` phrase** — verbatim from the
   most recent decision entry's "Next authorization expected" /
   "Operator picks one" line. Rendered as plain text, with a
   leading note: "Operator types this in the controller session;
   the command center never executes it."
7. **Hard invariants strip** at top or bottom of the page (small
   monospace bar):
   `Trading PAUSED · Live BLOCKED_AT_6_GATES · FRC NEVER_GRANTED · no_strategy_optimization_authorized=True`.
   Sourced from a constant in the handler / template (these are
   posture invariants, not live state in v1).

Page-level elements:

- Title: `SPARTA Trading Command Center — Lifecycles (v1)`.
- Small footer: `Read-only · localhost · v1 lifecycle viewer ·
  Module 1 of 8 planned`.
- No nav bar items pointing to unbuilt routes
  (`/command/gates`, `/command/data`, etc.). Those links only land
  when their respective modules ship.

---

## 8. What it must not show

- No "place trade" button. No "submit order" affordance. No "go
  live" toggle. None of these exist; none may be added.
- No paper-trading control. No "simulate trade" panel. No
  fake-order panel.
- No "optimize strategy" control. No "propose new candidate"
  control. No "rerun QC" control. No "fetch data" control.
- No live P&L number. No live position. No live broker balance.
  v1 has zero live data of any kind.
- No LLM chat surface. No "ask the AI" box. No model selector.
- No edit-in-place affordance for any displayed value.
- No `<form>`, no `<input>`, no `<textarea>`, no `<button>` whose
  click handler issues a mutating request. (Buttons that scroll the
  page or expand/collapse a row purely client-side are acceptable
  but discouraged for v1 — prefer static HTML.)
- No file-upload control.
- No "share link" / "export to public" affordance.
- No path that suggests Commander-style approval can happen via
  the command center. Approvals continue to flow only through
  sparta_commander.
- No fabricated number. If a value is unknown, the cell shows
  `—` or `MISSING`, never `0`, never `N/A`-as-data.
- No profit-proof language. The page must avoid words like
  "profitable", "winning", "outperforming". `REJECT_FAST` is
  rendered as `REJECT_FAST`, not as "rejected (despite favorable
  returns)" or similar editorial.

---

## 9. Architecture sketch (no code)

The implementation, when authorized, will follow this shape:

```
GET /command (FastAPI handler in app.py)
  └─ calls lifecycle_scan() — pure function, read-only
       ├─ globs reports/external_research_hunter/b006_*
       ├─ for each lifecycle id discovered:
       │    ├─ collects artifact files matching the patterns in §5
       │    ├─ reads each artifact, recomputes sha256
       │    ├─ reads paired JSON sidecar (if any), extracts declared
       │    │   seal sha (report_seal_sha256 / spec_seal_sha256 / etc.)
       │    ├─ compares → OK / SEAL_DRIFT / MISSING / NO_DECLARED_SHA
       │    └─ infers phase 0–8 status from artifact presence + most
       │        recent decisions.md entry for that lifecycle id
       └─ returns list[LifecycleRow] (dataclass / dict; pure data)

  └─ passes rows + invariants strip to templates/command.html
       └─ renders dense read-only table; no <form>; no JS mutation
```

`lifecycle_scan` lives either inline in `app.py` (preferred for v1
if it's under ~80 lines) or in `command_center/lifecycle_scan.py`
(allowed if it grows past that). It must be pure (no globals, no
side effects beyond reading files), and synchronous (no async I/O
needed for local-disk reads at this scale).

`db.upsert_manual_entry()` is called **once at startup**, registering
the `/command` row for `/guide` per the CLAUDE.md convention. Not
inside the request handler.

---

## 10. Test plan

New test module: `tests/test_app_command_route.py`, sibling to
`tests/test_app_shadow_validator_route.py`. Uses FastAPI's
`TestClient` (existing dependency, already used by sibling tests).

Required test cases (v1 minimum):

1. **`test_command_route_returns_200`** — `GET /command` returns 200
   when at least one `B006_*` lifecycle artifact exists on disk
   (fixture or real on-disk state).
2. **`test_command_route_renders_b006_002`** — response body contains
   the literal string `B006_002` and the literal sealed verdict
   `REJECT_FAST`.
3. **`test_command_route_renders_phase_ladder`** — response body
   contains a phase-ladder cell or row for at least phases 0–8.
4. **`test_command_route_has_no_form_or_post`** — response body
   contains no `<form` substring, no `method="post"`, no
   `method="POST"`. (Substring assertion; not a full HTML parser.)
5. **`test_command_route_has_no_method_handlers`** — `POST /command`,
   `PUT /command`, `PATCH /command`, `DELETE /command` all return
   405 Method Not Allowed.
6. **`test_command_route_flags_seal_drift`** — using a tmpdir
   fixture, mutate the body of a sample artifact while keeping its
   sidecar's declared sha pinned to the original; assert the
   rendered row contains the literal token `SEAL_DRIFT` for that
   artifact.
7. **`test_command_route_does_not_write`** — wrap the handler call
   in a check that no file under `reports/external_research_hunter/`
   was modified (mtime + sha of a sample artifact before and after
   the request must be identical).
8. **`test_command_route_invariants_strip`** — response body contains
   the literal strings `Trading PAUSED`, `BLOCKED_AT_6_GATES`,
   `FRC NEVER_GRANTED`, and `no_strategy_optimization_authorized`.
9. **`test_command_route_no_fabricated_value`** — when an artifact
   is intentionally absent from the fixture, the row contains the
   literal token `MISSING` (and does **not** contain `0`, `N/A`,
   or any synthesized sha).
10. **`test_command_route_no_external_network`** *(optional but
    strongly recommended)* — monkeypatch `socket.socket` to raise
    on `connect()`, assert `GET /command` still returns 200.
    Catches accidental SDK imports that open sockets on init.

If a `command_center/lifecycle_scan.py` module is introduced, add a
separate `tests/test_command_center_lifecycle_scan.py` with at
minimum: pure-function smoke test, sha-mismatch flagging test, and
missing-file flagging test.

All tests must pass under the existing pytest invocation pattern
used by sibling tests. No new test runner. No new global fixtures
beyond those local to this module.

---

## 11. Acceptance checklist (for the future implementation, not this plan)

When the operator authorizes the v1 build, the implementation is
"done" only when every box below is checked. None of these are
checked yet; this is a future-acceptance contract.

- [ ] **Scope honored:** exactly the files listed in §3 were
  touched. `git diff --stat` shows no other paths.
- [ ] **Forbidden paths untouched:** every item in §4 verified
  unchanged (mtime + sha spot-check on a sample of each).
- [ ] **S10-D1 unstaged files unchanged:** the three S10-D1 files
  that were `git restore --staged`-d before commit `a2ca6f7` remain
  byte-identical on disk and remain unstaged.
- [ ] **S10-D2 work untouched:** no edits, no imports, no test
  reorganization affecting S10-D2 fixtures or scaffolds.
- [ ] **Strategy files untouched:** no edits to any S7/S8/S9/B005/B006
  strategy file, runner, guard, or sealed artifact.
- [ ] **Localhost-only:** route is reachable on `127.0.0.1:8765/command`
  and not reachable on any other interface (manual `curl` check from
  external IP returns connection refused, or N/A if dashboard already
  binds 127.0.0.1 only).
- [ ] **GET only:** non-`GET` verbs return 405.
- [ ] **No write:** request handling produces zero filesystem writes
  outside log lines (verified via filesystem watch or
  before/after sha of a sample artifact).
- [ ] **No external network:** request handling produces zero
  outbound network calls (verified via socket monkeypatch test
  passing, or manual `tcpdump` if available).
- [ ] **Sha re-verification works:** `SEAL_DRIFT` flag fires
  correctly in the targeted test.
- [ ] **Fail-closed rendering:** `MISSING` / `ERROR` / `SEAL_DRIFT`
  surface explicitly; no fabricated values.
- [ ] **Invariants strip present:** v1 page shows the posture line.
- [ ] **No trading affordance:** v1 page contains zero of the
  forbidden controls in §8.
- [ ] **All v1 tests pass:** the test list in §10 runs green.
- [ ] **No regression in sibling tests:** the existing test suite
  still passes (no new failures introduced).
- [ ] **`/guide` updated:** `system_manual_entries` row exists for
  `/command` and the `/guide` page renders it correctly.
- [ ] **Brain memory appended:** post-work entries added to
  `brain_memory/projects/trading_bot/decisions.md`,
  `brain_memory/projects/trading_bot/lessons.md` (if anything was
  learned), `brain_memory/projects/trading_bot/next_actions.md`, and
  `brain_memory/logs/system_changes.md`, per CLAUDE.md's required
  post-work flow.
- [ ] **Posture invariants intact:** Trading still `PAUSED`, Live
  still `BLOCKED_AT_6_GATES`, FRC still `NEVER_GRANTED`,
  `no_strategy_optimization_authorized` still `True`.

---

## 12. Commit boundary for the future implementation

When the v1 build is implemented and accepted under §11, it commits
as **exactly one commit**, with the following boundaries:

- **Subject:** `Add /command lifecycle viewer (v1, read-only)`.
- **Body (concise, why-focused):** one short paragraph noting this
  is Module 1 of the plan in
  `docs/sparta_command_center_first_build_plan.md`, references commit
  `a2ca6f7` for the inspiration memo, and explicitly states "no trade
  capability, no fetch, no broker, GET-only, localhost-only".
- **Staged files (exact set):** `app.py`, `templates/command.html`,
  `tests/test_app_command_route.py`, `database.py`. Plus the optional
  `command_center/__init__.py` + `command_center/lifecycle_scan.py`
  + `tests/test_command_center_lifecycle_scan.py` **only if** they
  were introduced. **Nothing else.** If any other file shows up in
  `git diff --cached --name-only`, the commit is aborted and the
  surprise paths are investigated (per the pattern used to land
  commit `a2ca6f7`).
- **Pre-commit verification:** `git diff --cached --name-only`
  printed and inspected before the commit lands. Any pre-staged
  surprise files from other workstreams are unstaged with
  `git restore --staged` (working tree untouched), and the operator
  is told what was unstaged.
- **Post-commit verification:** `git log -1 --oneline` and
  `git status --short -uall -- <each touched path>` printed. The
  three S10-D1 unstaged files are re-verified as still-unstaged and
  byte-identical.
- **Brain-memory post-work entries** committed in a **separate**
  follow-up commit, not bundled with the code commit. (Keeps the
  code-change commit reviewable in isolation.)

---

## 13. Rollback plan

If anything about the v1 build misbehaves after the implementation
commit lands, rollback is one of:

1. **Soft rollback — disable the route, keep the code.**
   Comment out the `@app.get("/command")` decorator line (and only
   that line) in `app.py`. Restart the dashboard. The route returns
   404; the template, test, and `system_manual_entries` row remain
   on disk but are inert. Reversible by uncommenting.

2. **Hard rollback — revert the commit.**
   `git revert <commit-hash-of-v1-build>` produces a clean inverse
   commit. No history rewrite. No `git reset --hard`. No force-push.
   The `/guide` row disappears (the upsert is reversed by the revert
   touching `database.py`), the template is removed, the test is
   removed, the route is removed. Dashboard restart picks up the
   reverted state.

3. **Targeted rollback — remove the route only, keep helper code.**
   If only the HTTP-layer behavior is bad but the `lifecycle_scan`
   helper is sound, a small follow-up commit can delete only the
   route handler, the template, and the test, while leaving the
   helper for future reuse. Use this only if `command_center/`
   modules were introduced and are independently testable.

In all three rollback paths:

- **No sealed artifact is modified, ever.** Rollback touches only
  the files this plan allowed in §3.
- **No S10-D1 or S10-D2 file is touched.**
- **No `local_secrets/` change.** No credential rotation needed
  because none were ever in scope.
- **No brain-memory rewrite.** The post-work decisions /
  lessons / next_actions entries from the original implementation
  stay on file as a historical record; a follow-up entry documents
  the rollback and the reason.

Rollback is reachable from any commit-level state without losing
operator work, because the v1 surface is intentionally tiny and
additive.

---

## 14. What this plan deliberately does **not** do

- It does **not** authorize the build. The literal phrase the
  operator types to authorize is `Authorize Command Center v1
  lifecycle viewer build.` — this plan does not request it, does
  not assume it, and does not act on it.
- It does **not** create `/command`. No route handler exists yet.
- It does **not** edit `app.py`.
- It does **not** create `templates/command.html`.
- It does **not** create `tests/test_app_command_route.py`.
- It does **not** call `db.upsert_manual_entry()`.
- It does **not** touch any S10-D1 or S10-D2 file.
- It does **not** touch the three S10-D1 unstaged files left by the
  pre-commit cleanup before `a2ca6f7`.
- It does **not** fix the `"hydra "` ghost directory (trailing
  space). That remains a separate, future cleanup item — not in
  scope here.
- It does **not** add a broker, paper-trading, optimization,
  fetch, or POST surface anywhere.

---

## 15. Final note

This plan and the companion memo (`a2ca6f7`) together form the full
review-before-build paper trail. The next on-disk artifact in this
line of work is either:

(a) the operator's `Authorize Command Center v1 lifecycle viewer
build.` phrase, after which §3–§12 govern the implementation, **or**

(b) a separate plan revising this one if the operator wants v1
scope changed before authorization.

Anything else — including any spontaneous creation of `/command`,
any edit to `app.py`, any new test, any new template — is out of
scope and out of compliance.
