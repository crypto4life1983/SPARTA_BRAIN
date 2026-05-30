# JARVIS Step 42 — "What Changed Since Last Check?" Read-Only Plan

- **Generated:** 2026-05-30
- **Type:** documentation / plan only. No code, no endpoint, no UI, no storage,
  no tests, no trading control.
- **Status:** PLAN ONLY — implementation deferred until separate approval.

Step 42 designs a *future* read-only change-summary capability so JARVIS can
eventually answer operator questions like *"what changed since last check?"*,
*"what new commits happened?"*, and *"what needs my attention now?"* — without
adding any execution, storage, refresh, or trading control. **Nothing is
implemented in this step.** This is a design memo only.

---

## 1. Purpose and relation to sealed JARVIS v1

Step 42 plans the first capability *after* the sealed JARVIS v1 milestone. It
builds conceptually on the committed, verified baseline:

| Step | Commit | What it sealed |
| --- | --- | --- |
| 39 | `13e43ad` | Operator acceptance smoke after app restart (live port-8765 serves committed JARVIS code; text ask, voice STT, TTS, safety refusals verified). |
| 40 | `7d80f76` | v1 milestone seal — verdict `JARVIS_V1_ACCEPTED_READ_ONLY_VOICE_COMMAND_CENTER`. |
| 41 | `e67083f` | Natural trading-status phrase coverage (casual phrasings classify SAFE_INFO, forbidden still checked first). |

Step 42 does not change any of that. It only writes a plan for a possible v1.1
change-summary feature, keeping every v1 safety invariant intact.

---

## 2. Current JARVIS v1 baseline

The sealed v1 surface that any future feature must preserve:

- **Read-only command center** — `read_only=true` always; no mutation path.
- **Text ask** — `POST /api/jarvis/ask` accepts only `{question}`.
- **Voice STT input fill** — browser SpeechRecognition fills the text box; no
  server-side audio, no auto-submit.
- **Manual TTS readback** — operator-triggered speechSynthesis of the last
  answer; no autoplay.
- **Answer-only `/api/jarvis/ask`** — returns exactly five fields
  (`answer`, `safety_class`, `sources_used`, `refused`, `refusal_reason`); no
  command/action/execution/order keys.
- **Deterministic safety classifier** — `classify_jarvis_question` labels
  questions; forbidden intent checked **first** and overrides safe wording;
  unrecognized input fails closed to UNSUPPORTED/refused.
- **No execution, no trading control, no refresh endpoint, no storage** — the
  trading flags `paper_ready`/`live_ready`/`broker_control` are locked false.

---

## 3. What "what changed since last check?" should mean

A purely **read-only comparison** of the current read-only status against a
*previously observed* read-only snapshot, summarized in plain language:

- **New commits** — commits in git HEAD/recent-log that were not in the prior
  snapshot.
- **New reports** — new entries in `trading_detail.latest_reports` (or JARVIS
  docs) since the baseline.
- **Changed warning counts** — differences in attention/warning counters
  already surfaced by status.
- **Trading posture changes** — any change in the four posture flags (expected:
  none; all locked false).
- **Cache freshness changes** — differences in `cache_freshness` timestamps/age.
- **Git cleanliness changes** — differences in clean/dirty tree state and
  untracked counts from `file_hygiene_report`.

It is a **summary of observations**, not an action.

---

## 4. What it must NOT mean

The change-summary capability must never become a side-effect channel:

- **No auto-refresh mutation** — it must not trigger a refresh of caches/status.
- **No file writes from the browser** — the browser never persists anything.
- **No trading actions** — no place/enable/connect/approve.
- **No script execution** — it must not run git, generators, or any process.
- **No broker/paper/live control.**
- **No autonomous decisions** — it only reports differences; it never decides or
  acts on them.

---

## 5. Proposed safe data sources

All already exposed by the existing read-only surface — no new fetch needed:

- **Current `/api/jarvis/status` response** — the live read-only snapshot.
- **Git HEAD / last commits** — already surfaced by status.
- **`trading_detail.latest_reports`** — already surfaced by status (read-only
  file scan).
- **`cache_freshness`** — already surfaced by status.
- **`file_hygiene_report` / cache metadata** — already surfaced by status.
- **Committed JARVIS docs** — the `docs/jarvis_step_*` memos.

No source outside the current read-only status/docs is proposed.

---

## 6. Snapshot options for a future implementation

How a "previous state" baseline could be obtained, ranked by safety:

- **Option A — No persistence:** answer "current status only"; no baseline,
  no comparison. Safest; zero storage.
- **Option B — Operator-supplied baseline:** the operator pastes a prior status
  snapshot into the question; JARVIS compares only the provided fields. No
  storage; baseline lives in the question text.
- **Option C — Manually generated read-only snapshot file:** created by an
  **offline** script run by the operator at the terminal, never from the
  browser; JARVIS only *reads* it. Storage exists but is never written by the
  web surface.
- **Option D — Local server snapshot store:** server persists snapshots, but
  **only** after a separate, explicitly approved step, and **never** triggered
  by a browser write. Highest capability, highest risk; deferred.

---

## 7. Recommended v1.1 approach

- **Start with Option A + B first** — current-status summary, plus
  operator-pasted-baseline comparison. Both are zero-storage and zero-execution.
- **Do not add automatic snapshot storage yet** — no Option C/D in v1.1.
- **Later add an offline manual snapshot report if needed** — Option C, only if
  operators find A+B insufficient, and only as a separately approved docs+offline
  step.

This keeps the first change-summary increment fully within the sealed v1 safety
envelope (no storage, no execution, no new mutation path).

---

## 8. Future answer behavior

- **No baseline present:** JARVIS says it can summarize the *current* read-only
  status but **cannot compare yet** — it does not fabricate a "before".
- **Baseline provided:** compare **only** the fields the operator supplied;
  ignore fields not given rather than guessing them.
- **Never invent changes** — if a field is absent or unverifiable, say so.
- **Clearly separate verified changes vs unknowns** — two explicit buckets:
  "changed (verified)" and "cannot determine".

---

## 9. Safe questions to support later (all read-only)

- "what changed since last check"
- "what changed since yesterday"
- "what new commits happened"
- "what new trading reports appeared"
- "what warnings changed"
- "what needs attention now"

These would classify SAFE_INFO (or a future SAFE_CHANGE_SUMMARY label) and be
answered from read-only status only.

---

## 10. Forbidden questions that must still refuse

Forbidden intent is checked first and must continue to override any safe
"what changed" wording:

- "refresh status now" → FORBIDDEN_EXECUTION
- "run git log" → FORBIDDEN_EXECUTION
- "write a snapshot" → FORBIDDEN_MUTATION
- "save this state" → FORBIDDEN_MUTATION
- "execute report generator" → FORBIDDEN_EXECUTION
- "fix the dirty tree" → FORBIDDEN_MUTATION / FORBIDDEN_EXECUTION
- "clean untracked files" → FORBIDDEN_MUTATION / FORBIDDEN_EXECUTION
- "start trading based on changes" → FORBIDDEN_TRADING

---

## 11. Test plan for a future implementation

When the feature is actually built (Step 43+), tests must pin:

- Classifier recognizes safe change-summary questions (SAFE_INFO / future
  SAFE_CHANGE_SUMMARY, refused=false).
- Forbidden mixed requests (safe wording + action) still refuse, forbidden-first.
- `/api/jarvis/status` shape unchanged (24 top-level keys; flags locked false).
- No storage by default (no file written by the web surface).
- No refresh endpoint added (`/api/jarvis/refresh` must not exist).
- Ask response carries no command/action/execute/order fields (still five keys).
- No broker/paper/live controls anywhere.

---

## 12. Recommended Step 43

Add safe **classifier coverage + static answer behavior** for "what changed"
questions, with **no persistence**: recognize the safe phrasings, answer with a
current-status summary (Option A) and operator-supplied-baseline comparison
(Option B). No snapshot storage, no refresh, no execution.

---

## 13. Recommended Step 44

Optional **offline manual snapshot plan, docs-only**: design (not build) the
Option C offline snapshot script and the read-only file format JARVIS would
*read* — never write from the browser. Plan only, separate approval required.

---

## 14. Final Step 42 verdict

- **`JARVIS_CHANGE_SUMMARY_PLAN_READY`**
- Implementation deferred until separate approval.

No code, endpoint, UI, storage, test, or trading change was made in Step 42.
This step produces only the two documentation files below.
