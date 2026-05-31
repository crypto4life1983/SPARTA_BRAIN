# JARVIS Step 47 — Read-Only Latest-Snapshot Comparison for `/api/jarvis/ask`

- **Generated:** 2026-05-30
- **Type:** ask-answer logic + tests + docs. No endpoint, no UI, no browser
  control, no snapshot creation, no refresh, no execution, no trading control.
- **Ask API:** `POST` http://127.0.0.1:8765/api/jarvis/ask (unchanged shape)

Step 47 lets JARVIS answer *"what changed since last snapshot?"* by **reading**
the offline-generated `storage/jarvis/snapshots/latest_snapshot.json`
(display-only) and comparing it to the current read-only `/api/jarvis/status`
state. It writes nothing, creates no snapshot, adds no endpoint/UI/refresh, and
authorizes no trading. This realizes the Step 44 plan's Step 46 recommendation —
the read-only ask path *reads* the latest snapshot to compute a verified diff.

---

## 1. Files changed / created (allowed files only)

- **`app.py`** —
  - New `_JARVIS_LATEST_SNAPSHOT` path constant
    (`storage/jarvis/snapshots/latest_snapshot.json`).
  - New `_jarvis_read_latest_snapshot()` — opens the file **read-only**, returns
    `("missing"|"invalid"|"ok", data)`; fails closed on any error, never writes/
    repairs/regenerates.
  - New `_jarvis_current_comparable()` — builds an in-memory snapshot-shaped view
    of the current status via the offline tool's pure `build_snapshot`; writes
    nothing.
  - New `_jarvis_compare_snapshot(prev, curr)` — pure read-only diff over the
    whitelisted safe fields only.
  - Rewrote `_jarvis_what_changed_answer()` to branch on snapshot availability
    (missing / invalid / ok), keeping Step 43 behavior when there is no baseline.
- **`tests/test_jarvis_ask_contract.py`** — 14 Step 47 tests; the two Step 43
  content tests now `monkeypatch` the snapshot path to a missing file so they
  keep validating the no-baseline path deterministically.
- **`docs/jarvis_step_47_latest_snapshot_compare/report.md` / `report.json`** —
  this memo.

**Not changed:** `jarvis_conversation_safety.py` (the existing `changed` /
`what is new` / `change summary` SAFE_INFO patterns already route every listed
question; no classifier change needed), `templates/jarvis.html` (no UI change),
`tools/jarvis_snapshot_report.py` (imported read-only, not modified),
`tests/test_jarvis_conversation_safety.py`, `tests/test_jarvis_snapshot_report.py`,
and anything under trading / Factory / S26–S28 / Donchian / Hydra / base.html /
storage (only `latest_snapshot.json` is *read*).

---

## 2. Snapshot comparison behavior

For a safe change-summary question, the answer assembles up to three labeled
sections:

- **Verified changes since latest snapshot** *(captured `<generated_at>`)* — the
  diff, or "none — every compared read-only field matches the latest snapshot".
- **Current status** — the same read-only current-state summary as Step 43.
- **Unknown / not compared** — which fields are compared and that sensitive data
  is never compared/exposed and no trading is authorized.

Compared (safe read-only) fields only: git head/branch, latest commit subject,
commander `overall_state` + warning count, trading posture flags
(`read_only`/`paper_ready`/`live_ready`/`broker_control`/`state`/
`candidate_status`), latest trading report names, cache freshness overall,
file-hygiene counts (untracked/modified/staged), and status key count/hash.

**Never compared or exposed:** secrets, API keys, broker credentials, env vars,
chat logs, audio, transcripts, trade orders, command/action/execute fields —
none of these exist in a snapshot and none are inspected.

---

## 3. Missing-snapshot behavior (Step 43 preserved)

If `latest_snapshot.json` does not exist, JARVIS keeps the Step 43 answer: it
says no stored baseline exists, summarizes current read-only status only, and
explicitly claims no changes ("cannot compare against a previous snapshot yet").

---

## 4. Valid-snapshot comparison behavior

If the snapshot exists and is valid, JARVIS reads it display-only, builds the
current comparable, and reports **verified differences only** — e.g.:

- `git HEAD changed <old> -> <new>`
- `commander state changed <old> -> <new>`; `warning count changed N -> M`
- `trading posture paper_ready changed True -> False (reporting only; no trading
  authorized)`
- `latest trading reports changed: added X; removed Y`
- `cache freshness overall changed <old> -> <new>`; count changes; status key
  count/hash changes

It never asserts a change not backed by both snapshot and current values.

If the snapshot is **corrupt/invalid**, it fails closed: says the snapshot is
unavailable/invalid, summarizes current status only, and does not crash (HTTP
200).

---

## 5. Safety / no-write confirmation

- `/api/jarvis/ask` **writes no files** — a test records the snapshot's bytes
  and mtime before/after two asks and asserts both are unchanged, and that no
  new file appears in the snapshot's directory.
- No snapshot is created, repaired, deleted, refreshed, or regenerated.
- Response keeps exactly its five fields (`answer`, `safety_class`,
  `sources_used`, `refused`, `refusal_reason`) — no `command`/`action`/
  `execution`/`order`/`trade_ticket`/`mutation`/`side_effect`.
- Forbidden intent still refuses first: "what changed since last snapshot and
  refresh status / write a snapshot / start trading" → `FORBIDDEN_*`.
- No `/api/jarvis/snapshot` and no `/api/jarvis/refresh` endpoint exist (404);
  the template adds no snapshot/refresh control.

---

## 6. Status shape confirmation

- `/api/jarvis/status` unchanged at **24** top-level keys; `read_only=true`;
  `trading_detail` flags `paper_ready`/`live_ready`/`broker_control` locked
  `false` before and after a comparison ask.

---

## 7. Tests & validation

- `python -m py_compile app.py jarvis_conversation_safety.py
  tools/jarvis_snapshot_report.py` → **PYCOMPILE_OK**
- `pytest tests/test_jarvis_route.py tests/test_jarvis_conversation_safety.py
  tests/test_jarvis_ask_contract.py tests/test_jarvis_snapshot_report.py
  --rootdir=tests -q` → **393 passed, 0 failed, 0 skipped** (was 379; +14)
- `python -m json.tool docs/jarvis_step_47_latest_snapshot_compare/report.json`
  → **JSON_OK**
- Step 47 tests cover: missing → no-baseline answer; valid → comparison section
  appears; changed git head reported; changed commander state/warnings reported;
  changed trading posture reported without authorizing trading; changed latest
  report list reported; corrupt snapshot fails closed without crashing; ask does
  not write/modify the snapshot; response has no forbidden fields; forbidden
  mixed requests still refuse; status shape unchanged; template/endpoints have no
  snapshot/refresh control. All use temp dirs + monkeypatch, never touching the
  real runtime snapshot.

---

## 8. Verdict

- **`JARVIS_LATEST_SNAPSHOT_COMPARE_READY`**
- Read-only comparison against the offline latest snapshot, display-only, fail
  closed on missing/corrupt, no snapshot creation, no browser write, no
  endpoint/UI/refresh/execution, no trading authorization. Nothing staged or
  committed.
