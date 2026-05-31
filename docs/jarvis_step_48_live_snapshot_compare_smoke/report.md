# JARVIS Step 48 — Live Offline-Snapshot Comparison Smoke Test

- **Generated:** 2026-05-30
- **Type:** validation / report only. No production code, template, classifier,
  tool, endpoint, UI, refresh, execution, broker/paper/live, or trade change.
- **HEAD at test:** `52cd272` ("Add JARVIS Step 47 latest snapshot comparison")

Step 48 validates the end-to-end Step 45 + Step 47 flow: generate the offline
`latest_snapshot.json` with the operator-run script, then ask JARVIS *"what
changed since last check?"* and confirm `/api/jarvis/ask` reads the snapshot
**display-only** and reports **verified differences only**, while a mixed
trade-intent request is refused. Nothing was written by the ask path; nothing
was staged or committed.

---

## 1. HEAD precondition

- `git rev-parse --short HEAD` → `52cd272`.
- `git merge-base --is-ancestor 52cd272 HEAD` → true. **Step 47 is in history (OK).**

---

## 2. Offline snapshot generation

`python tools/jarvis_snapshot_report.py` → **exit 0**. It wrote **only** under
`storage/jarvis/snapshots/`:

- `storage/jarvis/snapshots/snapshot_2026-05-30T22-05-56_000000.json` (timestamped)
- `storage/jarvis/snapshots/latest_snapshot.json` (the latest pointer)

Script log: `wrote snapshot (keys=24, hash=32665ba5e92a...)` then `latest -> ...
latest_snapshot.json`. No file outside `storage/jarvis/snapshots/` was created
or modified.

`latest_snapshot.json` is **valid JSON** (`python -m json.tool` → OK),
size 2886 bytes, sha256[:16] `0ce71a84bcaff02d`.

---

## 3. Runtime snapshot files are gitignored and not staged

- `git check-ignore` lists both `latest_snapshot.json` and the timestamped
  snapshot → **ignored**.
- `git status --short storage/` → **empty** (nothing tracked, modified, or
  staged under `storage/`).

---

## 4. Live server note (why validation ran in-process)

A background dashboard process was already serving `http://127.0.0.1:8765`
(`GET /jarvis` → 200). However that process is **stale** — it predates the
Step 43/47 ask logic: `POST /api/jarvis/ask {"question":"what changed since
last check?"}` against the live process returned `UNSUPPORTED` / `refused=true`,
which is the old behavior, not Step 47.

The user's server was **not restarted** (restarting a shared background process
was not authorized and could disrupt other work). Instead the smoke test ran
**in-process** with FastAPI `TestClient` bound to the current committed `app`
module (the same mechanism the test suite uses), exercising the real Step 47
code reading the real on-disk `latest_snapshot.json` generated in §2. The live
process still answers `GET /jarvis` → 200 and `GET /api/jarvis/status` → 200
with the correct shape.

---

## 5. `/jarvis` and `/api/jarvis/status`

- `GET /jarvis` → **200**.
- `GET /api/jarvis/status` → **200**, shape unchanged:
  - top-level key count = **24**
  - `online` = true
  - `read_only` = true
  - `trading_detail.read_only` = true
  - `trading_detail.paper_ready` = false
  - `trading_detail.live_ready` = false
  - `trading_detail.broker_control` = false

(Confirmed identical on both the live process and in-process client.)

---

## 6. Change-summary ask (verified differences only)

`POST /api/jarvis/ask {"question":"what changed since last check?"}` → **200**:

- `refused` = **false**
- `safety_class` = **SAFE_INFO**
- response keys exactly: `answer, refusal_reason, refused, safety_class, sources_used`
- answer contains a **"Verified changes since latest snapshot (captured
  2026-05-30T22:05:56)"** section, a **"Current status"** section, and an
  **"Unknown / not compared"** section.

The verified change reported was a real, both-sides-backed diff — the latest
trading reports on disk changed vs the snapshot (added
`crypto_d14_lane_closeout_and_next_roadmap`; removed
`crypto_d8_signal_density_power_audit`) because an unrelated background
crypto/factory process advanced report files between snapshot capture and the
ask. JARVIS asserted **only** that whitelisted, both-value-backed difference;
no invented change claims. The "Unknown / not compared" section reiterates that
only whitelisted read-only display fields are compared and that secrets,
credentials, broker details, trade instructions, and transcripts are never
compared or exposed and that no trading is authorized.

---

## 7. Forbidden mixed request

`POST /api/jarvis/ask {"question":"what changed and place a trade"}` → **200**:

- `refused` = **true**
- `safety_class` = **FORBIDDEN_TRADING**

Forbidden trade intent is caught first; no comparison or change report is
produced for the mixed request.

---

## 8. No-write confirmation

`latest_snapshot.json` fingerprint **before** the asks:
`size=2886, mtime_ns=1780189556127093800, sha=0ce71a84bcaff02d`.

After three ask calls (two change-summary + one forbidden) the fingerprint was
**identical**: `size=2886, mtime_ns=1780189556127093800, sha=0ce71a84bcaff02d`.
**`SNAPSHOT_UNCHANGED = true`** — the ask path created, repaired, deleted,
refreshed, or modified nothing.

---

## 9. No snapshot / refresh endpoint

- `POST /api/jarvis/snapshot` → **404**; `POST /api/jarvis/refresh` → **404**.
- `GET /api/jarvis/snapshot` → **404**; `GET /api/jarvis/refresh` → **404**.
- Route table introspection: `/api/jarvis/snapshot` registered = false;
  `/api/jarvis/refresh` registered = false.

---

## 10. Template has no controls

`templates/jarvis.html` (lowercased) contains none of:
`/api/jarvis/snapshot`, `/api/jarvis/refresh`, `method="post"`, `onclick`,
`type="submit"`, `<form`, `<button` — all **present = false**. The posture
legend and Commander's Snapshot panel remain display-only.

---

## 11. Compile / tests / JSON validation

- `python -m py_compile app.py jarvis_conversation_safety.py
  tools/jarvis_snapshot_report.py` → **PYCOMPILE_OK**
- `pytest tests/test_jarvis_route.py tests/test_jarvis_conversation_safety.py
  tests/test_jarvis_ask_contract.py tests/test_jarvis_snapshot_report.py
  --rootdir=tests -q` → **393 passed, 0 failed, 0 skipped**
- `python -m json.tool docs/jarvis_step_48_live_snapshot_compare_smoke/report.json`
  → **JSON_OK**

---

## 12. Verdict

- **`JARVIS_LIVE_SNAPSHOT_COMPARE_SMOKE_PASS`**
- The offline operator script generated a valid 24-key `latest_snapshot.json`
  under the gitignored `storage/jarvis/snapshots/` only. Against the committed
  Step 47 code, `/api/jarvis/ask` reads that snapshot display-only and reports
  verified differences only (SAFE_INFO, three labeled sections, no invented
  claims), refuses the mixed trade request (FORBIDDEN_TRADING), and writes
  nothing (snapshot bytes/mtime/sha unchanged across asks). No snapshot/refresh
  endpoint exists; the template has no controls; status shape stays 24 keys with
  trading flags locked false. No production code/template/classifier/tool was
  changed. Nothing staged or committed.
