# JARVIS Step 31 — Read-Only Ask UI Wiring (answers only, no execution)

- **Generated:** 2026-05-30
- **Type:** UI wiring + tests + docs. No app.py change, no new endpoint.
- **Live page:** http://127.0.0.1:8765/jarvis
- **Status API:** http://127.0.0.1:8765/api/jarvis/status
- **Ask API (existing, Step 30):** `POST` http://127.0.0.1:8765/api/jarvis/ask

This step connects the existing display-only **Talk to JARVIS** conversation
shell to the answer-only `POST /api/jarvis/ask` endpoint shipped in Step 30. The
operator can now ask read-only questions from the page. The UI stays strictly
read-only: it posts **only** `{question}`, renders answers or refusals, persists
nothing, and adds **no** execution, refresh, broker, paper, live, or mutation
control.

---

## 1. Relation to Steps 20–30

- **Step 26** shipped the display-only conversation shell (no backend).
- **Step 28** shipped the pure local safety classifier.
- **Step 29** authored the tests-first ask contract.
- **Step 30** implemented the answer-only `POST /api/jarvis/ask` handler.
- **Step 31 (this step)** wires the existing shell to that endpoint with a
  strictly read-only fetch — **no** new endpoint, **no** refresh, **no** chat
  logs.

---

## 2. Files changed (allowed files only)

- **`templates/jarvis.html`**
  - Enabled the conversation input (`id="jvAskInput"`).
  - Replaced the disabled *“Send disabled”* span with a non-button, non-form
    **`Ask read-only`** span (`id="jvAskBtn"`, `role="button"`, `tabindex="0"`).
  - Added an `aria-live` answer area (`id="jvAskOut"`).
  - Added the persistent warning **“JARVIS answers only. No execution. No
    trading control.”**
  - Changed the panel tag from `PLANNING MODE` to `READ-ONLY`.
  - Made the five suggested chips **click-to-fill** (they never auto-submit).
  - Added `wireAsk()` inside the existing render IIFE: it POSTs **only**
    `{question}` to `/api/jarvis/ask` and renders
    `answer / safety_class / refused / refusal_reason / sources_used`, all
    escaped via `esc()`.
- **`tests/test_jarvis_route.py`** — updated three obsolete Step 26 shell guards
  and added a Step 31 section (UI safety + POST integration tests).
- **`tests/test_jarvis_ask_contract.py`** — repointed the obsolete Step 29
  template ask-absence guard (renamed
  `test_template_has_no_execution_or_refresh_control`); keeps the
  button/form/onclick/submit/post/refresh-absence checks.
- **`docs/jarvis_step_31_ask_ui_wiring/`** — this memo.

**Not done:** no new endpoint, no `/api/jarvis/refresh`, no `<button>`/`<form>`/
`onclick`/`type="submit"`/`method="post"`, no chat logs, no
localStorage/sessionStorage/indexedDB/cookies, no file writes, no
execution/broker/paper/live control, no trade run, no `app.py` change, no
`jarvis_conversation_safety.py` change, no `/api/jarvis/status` shape change.

---

## 3. UI wiring summary

| Element | Behavior |
| --- | --- |
| Input `jvAskInput` | Enabled; Enter submits; placeholder “Ask a read-only question…”. |
| Submit `jvAskBtn` | `<span role="button" tabindex="0">Ask read-only</span>` — click + Enter/Space call `ask()`. **Not** a real button/submit/form. |
| Chips | Click fills the input (focus); **never** auto-submit. |
| Answer area `jvAskOut` | Renders `answer / safety_class / refused / refusal_reason / sources_used` via `esc()`. |
| Warning | Persistent “JARVIS answers only. No execution. No trading control.” |
| Refusals | Rendered as `REFUSED` with the classifier reason; never overridden or executed. |

Payload is exactly:

```js
fetch('/api/jarvis/ask', {
  method: 'POST',
  headers: {'Content-Type':'application/json','Accept':'application/json'},
  body: JSON.stringify({question: q})
})
```

`question` is the **only** field; no `command`/`action`/`execute` is ever sent.

---

## 4. Non-execution guarantees

- Template adds no `<button>`, `<form>`, `onclick`, submit, or `method="post"`.
- No refresh endpoint or wiring.
- Only `{question}` is posted.
- No client-side persistence (no localStorage/sessionStorage/indexedDB/cookie).
- `/api/jarvis/status` shape unchanged.
- `app.py` and `jarvis_conversation_safety.py` unchanged.

---

## 5. Tests

**Updated Step 26 guards (`test_jarvis_route.py`):**
`test_jarvis_conversation_shell_text_appears` (asserts the persistent warning
instead of “Planning mode only”), `..._has_no_working_controls` (drops the two
ask-route forbids; keeps button/form/onclick/submit/post/refresh),
`..._input_is_disabled` → `..._input_is_enabled_read_only_ask`.

**Repointed Step 29 guard (`test_jarvis_ask_contract.py`):**
`test_template_has_no_ask_fetch` → `test_template_has_no_execution_or_refresh_control`.

**New Step 31 tests (`test_jarvis_route.py`):** `..._page_renders_ok`,
`..._input_enabled_and_button_labeled`, `..._wires_only_answer_only_ask_endpoint`,
`..._payload_is_question_only`, `..._no_execution_or_trading_control_labels`,
`..._no_browser_storage_or_chat_persistence`, `..._no_form_or_post_method_attribute`,
`..._safe_question_returns_answer`, `..._forbidden_trading_is_refused`,
`..._ui_wiring_does_not_change_status_shape`.

---

## 6. Open conflict — awaiting your decision

`tests/test_jarvis_conversation_safety.py::test_jarvis_template_still_has_no_controls`
still asserts `/api/jarvis/ask` is **absent** from `templates/jarvis.html`.
Step 31 intentionally wires the template to that endpoint, so this absence claim
is now factually obsolete — the **same** retired-guard situation as the Step
26/28 ask-absence guards that were repointed in Step 30.

That test file is **not** in Step 31's allowed-files list. Per the Step 30
lesson (do not edit forbidden files unilaterally; do not hide the route string),
I left it **untouched** and am flagging it instead.

**Recommended resolution:** repoint it the same honest way as Step 30 — drop the
obsolete `/api/jarvis/ask` token, keep the still-valid
button/form/onclick/submit/post and `/api/jarvis/refresh` absence checks.
This needs your explicit authorization to touch one out-of-scope test file.

---

## 7. Validation

- `python -m py_compile app.py jarvis_conversation_safety.py` → **PYCOMPILE_OK**
- `pytest tests/test_jarvis_route.py tests/test_jarvis_conversation_safety.py
  tests/test_jarvis_ask_contract.py --rootdir=tests -q` →
  **198 passed, 1 failed** (the only failure is the obsolete out-of-scope
  ask-absence guard in §6).
- `python -m json.tool docs/jarvis_step_31_ask_ui_wiring/report.json` → **JSON_OK**

---

**Conclusion:** the display-only conversation shell is now wired to the
answer-only `POST /api/jarvis/ask` with a strictly read-only fetch — it posts
only `{question}`, renders answers or refusals, persists nothing, and adds no
button/form/refresh/execution/trading control. `app.py`,
`jarvis_conversation_safety.py`, and the `/api/jarvis/status` shape are
unchanged. One obsolete ask-absence guard in an out-of-scope test file is
flagged in §6 for your decision rather than edited unilaterally.
