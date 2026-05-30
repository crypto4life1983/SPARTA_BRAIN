# JARVIS Step 23 — Known Limits & Safe Roadmap

- **Generated:** 2026-05-30
- **Type:** documentation only (no code, no UI, no API change)
- **Live page:** http://127.0.0.1:8765/jarvis
- **Status API:** http://127.0.0.1:8765/api/jarvis/status

This memo defines what JARVIS can and cannot do today, what is intentionally
blocked, which improvements are safe to make next, and what must remain
forbidden unless explicitly authorized later. It adds **no** capability,
control, or API change.

---

## 1. Purpose and relation to Steps 20–22

- **Step 20** polished the UI (CSS/HTML/labels only).
- **Step 21** proved the polished UI is live and safe
  (**JARVIS_POST_POLISH_SMOKE_PASS**).
- **Step 22** documented how to operate and interpret it (operator runbook).
- **Step 23 (this memo)** sets the forward-looking guardrails: JARVIS's
  identity, its deliberate limits, and a risk-tiered roadmap so every future
  step stays inside the read-only safety envelope.

---

## 2. Current committed baseline

| Step | Commit | What it did |
| --- | --- | --- |
| Step 20 | `4200253` | Safe UI-only polish pass (`templates/jarvis.html` only). |
| Step 21 | `4f55aae` | Post-polish live smoke memo (validation only). |
| Step 22 | `82ccf52` | Operator guide / runbook (documentation only). |

---

## 3. Current JARVIS identity

- A **read-only command center** — it mirrors aggregated SPARTA_BRAIN state.
- An **observer, not an executor** — it never runs commands, scripts, prompts,
  or missions.
- A **status / intelligence surface, not a trading controller** — it holds no
  order path and no broker control.

---

## 4. Known limits

- **No broker control** — JARVIS cannot connect to or command any broker.
- **No paper/live trading readiness** — `paper_ready` and `live_ready` are
  always false.
- **No execution buttons** — the UI has no `<button>` and no actionable
  control.
- **No POST/refresh actions** — GET-only; no `/api/jarvis/refresh`; data
  updates only via the page's own GET poll.
- **No autonomous decisions** — JARVIS does not decide or act on its own.
- **No strategy recommendation engine yet** — it shows research state but does
  not recommend or promote strategies.
- **No alerting automation yet** — it does not push notifications, page, or
  message.
- **No write-back to trading systems** — JARVIS never mutates any trading,
  research, or downstream system.

---

## 5. Forbidden changes unless explicitly authorized

- Broker integration of any kind.
- Live or paper trade enablement (arming `paper_ready` / `live_ready`).
- Order placement or any order path.
- Execution UI controls (buttons, forms, `onclick`, POST).
- Auto-refresh controls that **mutate** state.
- Strategy promotion / approval controls that trigger downstream effects.
- Changing `read_only` semantics — `read_only` must stay true and meaningful.

---

## 6. Safe next improvements (low risk, no new behavior)

- More documentation memos.
- Static help overlays (display-only).
- A panel glossary.
- Status-interpretation tables (green/yellow/red and per-panel states).
- Read-only historical snapshots (display of already-committed point-in-time
  data).
- A read-only archive view of committed JARVIS health reports.
- Read-only links to committed reports/memos.
- Visual clarity improvements with no new behavior (CSS/label/layout only).

---

## 7. Medium-risk improvements (require separate approval)

- **Passive auto-refresh polling** — cadence/visibility changes to the
  existing GET poll. Still read-only, but a timing/behavior change warrants
  sign-off.
- **Dashboard filters** — client-side show/hide of already-fetched data.
- **Alerting / notifications** — any outbound signal.
- **External health-report ingestion** — reading reports produced outside the
  current manual tools.
- **Stronger commander-snapshot summarization** — richer derived synthesis of
  existing fields.

---

## 8. High-risk improvements (must remain blocked)

- Broker / paper / live controls.
- Any endpoint that writes state.
- Approvals that trigger actions.
- Strategy execution workflows.

---

## 9. Recommended Step 24 / 25 / 26 options

**Step 24 (docs-only clarity):**
- **JARVIS-PANEL-GLOSSARY-MEMO** — a glossary mapping every panel and
  `api_key` to a plain-language definition and how-to-read note.
- **JARVIS-STATUS-INTERPRETATION-TABLE-MEMO** — a reference for green/yellow/red
  and each section's states.

**Step 25 (docs-only verification/index):**
- **JARVIS-DOCS-AUTO-CHECK-MEMO** — a read-only memo that re-verifies the docs
  index against the live API and tracked docs.
- **JARVIS-REPORT-ARCHIVE-INDEX-MEMO** — a docs-only index of all committed
  JARVIS step reports with commit hashes and conclusions.

**Step 26 (UI-only or recurring validation):**
- **JARVIS-CACHE-FRESHNESS-AGE-BADGES** — optional display-only age badges per
  cache row (UI-only, no controls); or
- **JARVIS-LIVE-REGRESSION-SMOKE (recurring)** — re-run the live smoke memo
  after the next JARVIS commit.

---

## 10. Operator decision rule

- **Green** — healthy observation.
- **Yellow** — attention needed.
- **Red** — stop and investigate.

**None of these colours means permission to execute trades.** JARVIS is an
observation surface; trade authorization is never granted by a dashboard
colour.

---

**Conclusion:** documentation-only known-limits and safe-roadmap memo created.
No code, UI, tool, test, API, or trading surface was changed.
