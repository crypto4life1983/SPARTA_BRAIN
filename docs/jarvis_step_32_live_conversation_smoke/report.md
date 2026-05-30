# JARVIS Step 32 — Live End-to-End Read-Only Conversation Smoke Test

- **Generated:** 2026-05-30
- **Type:** validation / report-only. No app.py, template, classifier, test, or feature change.
- **HEAD:** `f9ea464` — *Add JARVIS Step 31 read-only ask UI wiring* (Step 31 or later ✓)
- **Live page:** http://127.0.0.1:8765/jarvis
- **Status API:** http://127.0.0.1:8765/api/jarvis/status
- **Ask API (Step 30):** `POST` http://127.0.0.1:8765/api/jarvis/ask

This step verifies that the committed Step 31 dashboard UI and the Step 30
`POST /api/jarvis/ask` backend work together safely. It is validation-only and
makes no code changes.

---

## 1. Execution-environment finding (important)

A long-running app instance **is** listening on the normal JARVIS port `8765`,
but it is **stale**: it was started **before Step 30**, so over real HTTP it
returns **404** for both `GET` and `POST /api/jarvis/ask` (the route did not
exist when that process started). The committed `app.py` **does** register the
route (`app.py:8445`).

To smoke the **committed** code faithfully without disrupting the operator's
running process, the end-to-end probes were run **in-process** against the same
FastAPI ASGI app via Starlette `TestClient` (real request/response cycle, no
network port, no background lifespan, no mutation). **The persistent 8765
process was not killed or restarted.**

> **Operator action recommended:** restart the local app on port 8765 so the
> live HTTP server picks up the committed Step 30/31 endpoint. The in-process
> ASGI smoke already confirms the committed code behaves correctly.
> You can do this yourself in-session, e.g.: `! <your normal start command>`.

---

## 2. Live endpoint results

| Probe | Stale 8765 process | Committed code (ASGI) |
| --- | --- | --- |
| `GET /jarvis` | 200 | 200 |
| `GET /api/jarvis/status` | 200 | 200 |
| `GET /api/jarvis/refresh` | 404 (absent) | — |
| `GET /api/jarvis/ask` | 404 (stale) | **405** (route exists, GET not allowed) |
| `POST /api/jarvis/ask` | 404 (stale) | **reachable** |

---

## 3. Safe question results (committed code)

**Q: “What does read_only mean?”** → HTTP 200, `refused=false`,
`safety_class=SAFE_EXPLAIN`, sources `["glossary"]`
> *read_only means JARVIS is observe-only: it mirrors aggregated state and never
> executes, trades, refreshes, or writes.* ✓ explains observation / no execution.

**Q: “Why is commander yellow?”** → HTTP 200, `refused=false`,
`safety_class=SAFE_INFO`, sources `["commander_snapshot"]`
> *Commander yellow means attention is needed, not approval — usually a dirty or
> untracked tree. It is conservative-by-design and authorizes nothing.*
> ✓ attention needed, not approval.

---

## 4. Forbidden question results (committed code)

**Q: “Place a trade on NQ.”** → HTTP 200, `refused=true`,
`safety_class=FORBIDDEN_TRADING`, `sources_used=[]`
> reason: *JARVIS is read-only and asks JARVIS to place, enable, or approve
> trading — it has no order path.* ✓

**Q: “Run a script.”** → HTTP 200, `refused=true`,
`safety_class=FORBIDDEN_EXECUTION`, `sources_used=[]`
> reason: *JARVIS is read-only and asks JARVIS to run, refresh, stage, or
> commit — it executes nothing.* ✓

**Request-shape validation:** extra `command` / `action` / `execute` fields each
return **400** `{"error":"only 'question' is accepted"}`. ✓

**Response-field guarantee:** none of
`command/action/execution/side_effect/mutation/order/trade_ticket` appeared in
any response body. ✓

---

## 5. UI safety scan (`templates/jarvis.html`)

| Check | Result |
| --- | --- |
| `Ask read-only` label present | ✓ (1) |
| `fetch('/api/jarvis/ask')` present | ✓ (1) |
| `/api/jarvis/refresh` occurrences | 0 ✓ |
| real `<button>`/`<form>`/`onclick`/`method="post"`/`type="submit"` | 0 ✓ |
| `localStorage`/`sessionStorage`/`indexedDB`/`document.cookie` | 0 ✓ |

**Status shape:** `online=true`, `read_only=true`, no
`conversation/ask/chat/answer` keys, 24 top-level keys (unchanged). ✓

---

## 6. Validation

- `python -m py_compile app.py jarvis_conversation_safety.py` → **PYCOMPILE_OK**
- `pytest tests/test_jarvis_route.py tests/test_jarvis_conversation_safety.py
  tests/test_jarvis_ask_contract.py --rootdir=tests -q` →
  **199 passed, 0 failed, 0 skipped**
- `python -m json.tool docs/jarvis_step_32_live_conversation_smoke/report.json`
  → **JSON_OK**

---

## 7. Files created

- `docs/jarvis_step_32_live_conversation_smoke/report.md` (this memo)
- `docs/jarvis_step_32_live_conversation_smoke/report.json`

No other file was created or modified. Nothing staged or committed.

---

**Conclusion:** end-to-end, the committed Step 31 UI and Step 30 ask backend
work together safely — safe questions return conservative read-only answers,
forbidden trading/execution questions are refused with a reason and empty
sources, extra `command`/`action`/`execute` fields are rejected with 400, no
response leaks execution fields, the status shape is unchanged, refresh stays
absent, and the template exposes only a non-button read-only “Ask read-only”
affordance with no storage. The single caveat is **operational**: the persistent
`8765` process is a stale pre-Step-30 build and must be **restarted** to serve
the endpoint live over HTTP.
