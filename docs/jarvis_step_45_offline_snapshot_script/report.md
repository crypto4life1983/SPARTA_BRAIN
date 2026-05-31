# JARVIS Step 45 — Offline Manual Snapshot Script + Tests

- **Generated:** 2026-05-30
- **Type:** offline operator-run script + tests + docs. No endpoint, no UI, no
  browser control, no scheduler, no refresh, no execution, no trading control.
- **Run by hand:** `python tools/jarvis_snapshot_report.py`

Step 45 implements the Step 44 plan (Option C): an **offline, operator-run**
script that captures the existing **read-only** JARVIS status into a
gitignored `storage/jarvis/snapshots/` JSON file, so a future, separately
approved step can answer *"what changed?"* with a real diff. **Nothing is wired
to the browser.** The web surface neither imports nor invokes the script and
exposes no snapshot or refresh endpoint.

---

## 1. Files created / changed (allowed files only)

- **`tools/jarvis_snapshot_report.py`** *(new)* — the offline snapshot script.
- **`tests/test_jarvis_snapshot_report.py`** *(new)* — 16 tests pinning the
  write-location, content, exclusion, status-shape, and no-UI-control
  guarantees.
- **`docs/jarvis_step_45_offline_snapshot_script/report.md` / `report.json`**
  *(new)* — this memo.

**Not changed:** `app.py` (no refactor needed — the existing read-only
`api_jarvis_status()` aggregate is imported as-is), `jarvis_conversation_safety.py`,
`templates/jarvis.html`, `templates/base.html`, any other tool, and anything
under trading / Factory / S26–S28 / Donchian / Hydra / storage (outside the
gitignored `storage/jarvis/snapshots/` runtime output). No `.gitkeep` was added:
`storage/` is already gitignored, so snapshots are never tracked and no tracked
runtime file is needed.

---

## 2. What the script does (read-only by construction)

- **Manual / offline only.** Operator runs `python tools/jarvis_snapshot_report.py`
  at the terminal. The browser cannot trigger it.
- **Reads the existing read-only status aggregate** — imports `app` and calls
  `app.api_jarvis_status()` (the same 24-key read-only payload the console shows).
  It runs no extra git/subprocess/shell, fetches nothing, calls no broker, places
  no trade, and refreshes nothing.
- **Writes exactly two files, only inside `storage/jarvis/snapshots/`** — a
  timestamped `snapshot_<ISO-with-no-colons>_<microseconds>.json` plus a
  `latest_snapshot.json` pointer. It never stages, commits, cleans, deletes, or
  writes anywhere else.
- **Whitelist capture.** Only whitelisted scalar display fields are copied out of
  each status section; anything not whitelisted is dropped, so the snapshot is a
  strict subset of the already read-only status.
- **Fail-closed.** A defense-in-depth `assert_snapshot_safe()` guard re-scans the
  serialized snapshot for forbidden whole-word tokens and raises if any appear;
  `main()` returns a nonzero exit code on any failure and writes nothing partial
  that could leak.

---

## 3. Snapshot content (all already-exposed read-only fields)

```
kind="jarvis_status_snapshot", read_only=true
generated_at, status_key_count (24), status_key_hash (sha256 of sorted keys)
git: branch, head, clean, dirty, modified_count, untracked_count
recent_commits: [{short_hash, subject}] (max 5)
commander_snapshot: overall_state, headline, warnings, trading_posture,
                    cache_status, staged_count, untracked_count
trading_detail: state, read_only(true), paper_ready(false), live_ready(false),
                broker_control(false), candidate_status
trading_latest_reports: [{name, path, modified_at, has_md}] (max 5)
cache_freshness: state, overall, generated_at
file_hygiene: state, total_untracked_count, tracked_modified_count, staged_count
```

A real run produced a 24-key snapshot with `status_key_hash` `32665ba5e92a…`,
HEAD `5d0bdf3` on `master`, `trading_posture: research_only`, and trading flags
locked `read_only=true / paper_ready=false / live_ready=false /
broker_control=false`.

---

## 4. What the snapshot must NOT contain (enforced)

The build whitelist excludes — and the fail-closed guard re-checks for — these
whole-word tokens: `secret(s)`, `api_key`/`apikey`, `broker_password`,
`password`, `credential(s)`, `token(s)`, `command`, `action`, `execute`,
`order(s)`, `trade_ticket`, `audio`, `transcript(s)`, `chat_log`, `environment`.

Word-boundary (`\b`) matching means legitimate compounds never trip the guard
(`commander_snapshot` is not `command`; an `..._audit` report name is not
`audio`; `recommended_next_actions` is deliberately **not** embedded as a
verbatim key list, so `action` never appears). The snapshot carries no secrets,
broker credentials, API keys, raw chat logs, audio, transcripts, order data,
trade instructions, command/action/execute fields, or environment variables.

---

## 5. Tests (16 new, all green)

- `write_snapshot` writes **only** the timestamped file + `latest_snapshot.json`,
  **only** inside the given dir, and never escapes it.
- `latest_snapshot.json` is valid JSON and marked `read_only`.
- snapshot includes every required read-only field (generated_at, key count/hash,
  git, commander, trading, cache, file_hygiene).
- snapshot **excludes** all forbidden tokens (`secret`, `api_key`,
  `broker_password`, `command`, `action`, `execute`, `order`, `trade_ticket`,
  `audio`, `transcript`) via word-boundary check.
- `build_snapshot` drops non-whitelisted fields (injected `secret` / `order_ticket`
  / `api_key` / `command` / `password` are stripped).
- `assert_snapshot_safe` accepts a real snapshot and rejects a planted token.
- timestamped filename has no colons (Windows-safe).
- `/api/jarvis/status` shape unchanged (24 keys; trading flags locked false).
- template has no snapshot/refresh control; no `/api/jarvis/snapshot` or
  `/api/jarvis/refresh` route exists (404); `app.py` references neither.

All temp writes use `tmp_path`, so the real storage tree is never touched.

---

## 6. Validation

- `python -m py_compile app.py jarvis_conversation_safety.py tools/jarvis_snapshot_report.py`
  → **PYCOMPILE_OK**
- `pytest tests/test_jarvis_route.py tests/test_jarvis_conversation_safety.py
  tests/test_jarvis_ask_contract.py tests/test_jarvis_snapshot_report.py
  --rootdir=tests -q` → **378 passed, 0 failed, 0 skipped** (was 362; +16)
- `python -m json.tool docs/jarvis_step_45_offline_snapshot_script/report.json`
  → **JSON_OK**
- Real run: `python tools/jarvis_snapshot_report.py` → exit 0, wrote a 24-key
  snapshot + `latest_snapshot.json`; `git status --short storage/jarvis/snapshots/`
  → empty (gitignored, never tracked).

---

## 7. Final verdict

- **`JARVIS_OFFLINE_SNAPSHOT_SCRIPT_READY`**
- Offline operator-run capture only; not wired to the browser; no endpoint, no
  UI, no scheduler, no refresh, no execution, no trading control. Runtime
  snapshots are gitignored and never staged. Nothing staged or committed.
