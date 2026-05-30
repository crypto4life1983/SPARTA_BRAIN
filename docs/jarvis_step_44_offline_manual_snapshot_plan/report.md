# JARVIS Step 44 — Offline Manual Snapshot Plan

- **Generated:** 2026-05-30
- **Type:** documentation / plan only. No code, no endpoint, no UI, no storage,
  no snapshot script, no tests, no trading control.
- **Status:** PLAN ONLY — implementation deferred until separate approval.

Step 44 designs the safest *future* mechanism for answering *"what changed since
last check?"* with a real comparison — using **manually generated, offline,
read-only snapshots** — without adding browser writes, auto-refresh, UI storage,
execution controls, or trading control. **Nothing is implemented in this step.**
This is a design memo only.

---

## 1. Purpose and relation to prior steps

Step 43 (`316fca9`) lets JARVIS answer "what changed?" with a *current-status
summary only* — it explicitly says it cannot compare because no baseline exists.
Step 44 plans the missing piece: a safe, offline way to capture a prior
read-only snapshot that a future step could compare against.

| Step | Commit | What it established |
| --- | --- | --- |
| 40 | `7d80f76` | v1 milestone seal — `JARVIS_V1_ACCEPTED_READ_ONLY_VOICE_COMMAND_CENTER`. |
| 41 | `e67083f` | Natural trading-status phrase coverage (casual phrasings → SAFE_INFO; forbidden first). |
| 42 | `a1ac1a6` | "What changed?" plan — ranked snapshot Options A–D; verdict `JARVIS_CHANGE_SUMMARY_PLAN_READY`. |
| 43 | `316fca9` | "What changed?" static answers — current-status summary only, no baseline; verdict `JARVIS_WHAT_CHANGED_STATIC_ANSWERS_READY`. |

Step 44 is the docs-only realization of Step 42's **Option C** (offline manual
snapshot file), planned but not built.

---

## 2. Current Step 43 limitation

- **JARVIS can summarize current status** — HEAD/recent commits, commander
  state/warnings, trading posture, latest reports, cache freshness, git
  cleanliness — all read-only.
- **JARVIS cannot compare changes** — it keeps no previous baseline/snapshot, so
  it never claims a verified difference; it answers "current state only" and
  says a comparison is not possible yet.

The gap is purely the absence of a *prior* read-only snapshot to diff against.
Step 44 designs how to capture one safely.

---

## 3. Recommended safe snapshot model

- **Offline manual script only** — a small operator-run tool (e.g.
  `tools/jarvis_snapshot.py`), executed at the terminal by the operator. The web
  surface never invokes it.
- **Never triggered from the browser** — no endpoint, no button, no fetch, no
  scheduler initiates a snapshot. The browser cannot cause a write of any kind.
- **Read-only GET/status collection** — the script reads the same read-only
  status aggregate JARVIS already exposes (`/api/jarvis/status` content) and
  performs no mutation, no broker call, no trade, no refresh.
- **Writes one local JSON snapshot file only when manually run** — a single
  timestamped JSON file under a gitignored directory; nothing else is written.
- **Future JARVIS may read the snapshot file display-only** — a later,
  separately-approved step could let the read-only ask path *read* the latest
  snapshot to compute a diff. Reading only; never writing.

---

## 4. What a snapshot should contain (all already-exposed read-only fields)

- **timestamp** — when the snapshot was captured (`generated_at`).
- **git** — branch, short HEAD, recent commit subjects, clean/dirty,
  modified/untracked counts.
- **commander_snapshot** — `overall_state`, headline, warning list/count.
- **trading_detail** — posture flags (`read_only`/`paper_ready`/`live_ready`/
  `broker_control`) and `latest_reports` names/paths/modified times.
- **cache_freshness** — overall freshness state and per-cache freshness.
- **file_hygiene** — staged/untracked counts and state.
- **status key count / hash** — the 24 top-level key count and an optional
  content hash of the status payload, if useful for fast change detection.

All of these are already present in the read-only status aggregate — the
snapshot is a frozen copy, not a new data source.

---

## 5. What a snapshot must NOT contain

- secrets
- broker credentials
- API keys
- raw chat logs
- audio
- transcripts
- trade instructions
- order data
- personal / private data beyond what the existing read-only status already
  exposes

The snapshot is strictly a subset of the already-public read-only status — it
never widens exposure.

---

## 6. Storage recommendation

- **Location:** `storage/jarvis/snapshots/`.
- **Gitignored** — like the other `storage/jarvis/` runtime caches; never
  committed.
- **Timestamped files** — e.g. `snapshot_2026-05-30T20-40-00.json`.
- **Optional `latest_snapshot.json`** — a convenience pointer/copy of the most
  recent capture, also gitignored.
- **Never committed** — snapshots are local runtime artifacts only, consistent
  with the existing `_JARVIS_CACHE_FILES` convention.

---

## 7. Future comparison behavior

- **Compare current `/api/jarvis/status` to the last snapshot** — field by field,
  read-only.
- **Report verified differences only** — e.g. "HEAD changed from X to Y", "2 new
  trading reports", "warning count 2 → 3"; if a field is missing in either side,
  say it cannot be compared.
- **No invented changes** — never assert a difference that isn't backed by both
  snapshot and current values.
- **No execution recommendations** — it reports diffs; it never tells the
  operator to run, refresh, commit, or clean anything.
- **No trading authorization** — posture flags stay locked false; a change in
  research reports is never an approval to trade.

---

## 8. Safety boundaries

- **No browser write** — the UI never persists a snapshot.
- **No `/api/jarvis/snapshot` endpoint** — capture is offline-only.
- **No refresh endpoint** — `/api/jarvis/refresh` must never exist.
- **No auto-scheduled snapshot yet** — no cron/timer; operator-initiated only.
- **No action buttons** — `/jarvis` adds no `<button>`, `<form>`, `onclick`,
  submit, or `method="post"`.
- **No mutation from `/jarvis`** — the web surface stays strictly read-only.

---

## 9. Future tests required before implementation

- Snapshot script writes **only** under `storage/jarvis/snapshots/` (no writes
  elsewhere; no top-level or repo-tree mutation).
- Snapshot **excludes** secrets / storage internals / audio / transcripts /
  credentials / order data.
- Browser has **no** snapshot control (template adds no button/form/onclick/
  submit/refresh).
- `/api/jarvis/status` shape unchanged (24 top-level keys; flags locked false).
- Ask response still uses only safe read-only context (still five keys; no
  command/action/order fields).
- Forbidden mixed requests still refuse (forbidden checked first).

---

## 10. Recommended Step 45

Implement the **offline snapshot script + tests only, not wired to the web**:
add `tools/jarvis_snapshot.py` (operator-run) that captures the read-only status
into a gitignored `storage/jarvis/snapshots/` JSON file, plus tests pinning the
write-location and content-exclusion guarantees. No endpoint, no UI, no
scheduler. Separate approval required.

---

## 11. Recommended Step 46

Let the **ask endpoint read the latest snapshot display-only and compare current
vs snapshot**: the read-only ask path may *read* `latest_snapshot.json` to answer
"what changed?" with verified differences. Reading only — still no browser write,
no refresh, no execution, no trading authorization. Separate approval required.

---

## 12. Final verdict

- **`JARVIS_OFFLINE_SNAPSHOT_PLAN_READY`**
- Implementation deferred until separate approval.

No code, endpoint, UI, storage, snapshot script, test, or trading change was made
in Step 44. This step produces only the two documentation files below.
