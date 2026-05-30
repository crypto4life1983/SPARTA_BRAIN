# JARVIS Step 30 — Answer-Only `/api/jarvis/ask` Handler (minimal, read-only)

- **Generated:** 2026-05-30
- **Type:** backend endpoint + tests + docs. No template change, no UI wiring.
- **Live page:** http://127.0.0.1:8765/jarvis
- **Status API:** http://127.0.0.1:8765/api/jarvis/status
- **Ask API:** `POST` http://127.0.0.1:8765/api/jarvis/ask

This step implements the smallest safe `POST /api/jarvis/ask` endpoint that
satisfies the Step 29 contract. It is **answer-only, read-only, non-mutating**,
and delegates **all** safety classification to
`jarvis_conversation_safety.classify_jarvis_question`. The UI is **not** wired
to it.

---

## 1. Purpose and relation to Steps 20–29

- **Step 28** shipped the pure local safety classifier; **Step 29** authored the
  tests-first ask contract (skipped while the route was absent).
- **Step 30 (this step)** implements the answer-only handler so the Step 29
  contract tests **activate and pass**, while keeping every read-only / no-exec
  guarantee.

---

## 2. Current committed baseline

| Step | Commit | What it did |
| --- | --- | --- |
| Step 20 | `4200253` | Safe UI-only polish pass. |
| Step 21 | `4f55aae` | Post-polish live smoke memo. |
| Step 22 | `82ccf52` | Operator guide / runbook. |
| Step 23 | `37d7dcc` | Known limits & safe roadmap. |
| Step 24 | `9523da8` | Panel glossary. |
| Step 25 | `6b88d9b` | Read-only conversation layer plan. |
| Step 26 | `f2268f3` | Read-only conversation shell (UI-only). |
| Step 27 | `e961481` | Answer-only backend safety plan. |
| Step 28 | `a5b47b4` | Conversation safety classifier (no route). |
| Step 29 | `ed8f23c` | Ask endpoint contract tests (skipped). |

---

## 3. Files changed (allowed files only)

- **`app.py`** — added `POST /api/jarvis/ask` and the `_jarvis_ask_answer`
  helper **inside** the existing JARVIS block (additive; placed between the
  `/jarvis` page route and the block's END marker).
- **`tests/test_jarvis_ask_contract.py`** — retired the three Step 29
  "endpoint absent" assertions now that the handler exists; the `@requires_ask`
  contract tests activate unchanged.
- **`tests/test_jarvis_route.py`** — repointed the obsolete Step 26 ask-absence
  guard to **refresh-only** (still asserts `/api/jarvis/refresh` is absent; all
  UI safety assertions unchanged).
- **`tests/test_jarvis_conversation_safety.py`** — repointed the obsolete
  Step 28 ask-absence guard to **refresh-only** (renamed
  `test_step_28_adds_no_refresh_or_execution_endpoint`; all classifier
  assertions unchanged).
- **`docs/jarvis_step_30_ask_answer_only_handler/`** — this memo.

> The Step 26/28 guards asserted the ask endpoint *had not been added yet*.
> Step 30 adds it by design, so those two absence checks became obsolete and
> were **repointed (not deleted)** to keep enforcing the still-valid
> refresh/execution-absence property. The route string is **not** hidden, and
> no contract or forbidden-request test was weakened.

**Not done:** no `templates/jarvis.html` change, no UI wiring / fetch, no chat
logs, no file writes, no state mutation, no subprocess/shell/git/broker call, no
refresh trigger, no broker/paper/live control, no trade run, no
`/api/jarvis/status` shape change, no `jarvis_conversation_safety.py` change.

---

## 4. Endpoint summary

```
POST /api/jarvis/ask
Request:  { "question": "<string>" }   # 'question' is the ONLY accepted field
```

**Validation (deterministic):**

- Invalid / non-object JSON body → **400**.
- Any field other than `question` (e.g. `command`/`action`/`execute`) → **400**.
- Missing `question` → **400**.
- Non-string `question` → **400**.
- Blank `question` → delegated to the classifier → `UNSUPPORTED` → **200** with
  `refused=true`.

**Response (200):**

```json
{
  "answer": "string",
  "safety_class": "SAFE_* | FORBIDDEN_* | UNSUPPORTED",
  "sources_used": ["..."],
  "refused": false,
  "refusal_reason": ""
}
```

- The response **never** contains `command`, `action`, `execution`,
  `side_effect`, `mutation`, `order`, or `trade_ticket`.
- **Safe** → `refused=false`, conservative read-only answer, `sources_used`
  populated.
- **Forbidden / unsupported** → `refused=true`, `safety_class` begins with
  `FORBIDDEN` (or `UNSUPPORTED`), short `refusal_reason`, `sources_used=[]`.
- **`GET /api/jarvis/ask`** is not registered → FastAPI returns **405**.

All safety classification is done by `classify_jarvis_question(question)`; the
handler adds only request-shape validation and conservative answer text.

---

## 5. Answer behavior (conservative, static concepts)

- `read_only` → observe-only / no execution.
- Commander **yellow** → attention needed, **not** approval.
- Trading posture → `read_only=true`, `paper_ready=false`, `live_ready=false`,
  `broker_control=false`.
- JARVIS docs → exist across Steps 20–29.
- Safest next step → review status / panels / docs; authorizes no trading.

The handler does not invent live status numbers; answers are static and
conservative.

---

## 6. Non-execution guarantees

- No `subprocess` / `os.system` / shell / `git` / broker / trading import in the
  handler.
- No file write and **no chat-log write** anywhere in the request path.
- No `/api/jarvis/refresh` path introduced.
- `broker_control` / `paper_ready` / `live_ready` remain **false** (untouched).
- `/api/jarvis/status` response shape is **unchanged**.

---

## 7. Tests

**Activated from Step 29 (now run & pass):** `..._post_accepts_only_question_string`,
`..._rejects_missing_or_blank_question`, `..._rejects_command_action_execute_fields`,
`..._safe_question_returns_answer`, `..._forbidden_question_is_refused`,
`..._does_not_write_chat_logs`, `..._does_not_mutate_filesystem`,
`..._does_not_change_status_shape`, `..._keeps_broker_paper_live_locked`,
`..._does_not_trigger_refresh`, `..._get_ask_not_supported`.

**Retired in Step 30** (obsolete now the endpoint exists):
`test_ask_endpoint_is_currently_absent`, `test_post_ask_is_not_routed_today`,
`test_app_py_has_no_ask_route`.

**Still active (current step):** `test_template_has_no_ask_fetch`,
`test_status_shape_unchanged_in_step_29`,
`test_classifier_is_importable_for_future_endpoint`.

---

## 8. Validation

- `python -m py_compile app.py jarvis_conversation_safety.py` → **PYCOMPILE_OK**
- `pytest tests/test_jarvis_route.py tests/test_jarvis_conversation_safety.py
  tests/test_jarvis_ask_contract.py --rootdir=tests -q` → **PASS**
- `python -m json.tool docs/jarvis_step_30_ask_answer_only_handler/report.json`
  → **JSON_OK**

---

## 9. Recommended next safe step

**JARVIS-ASK-UI-WIRING (Step 31, separate approval)** — only after this
answer-only handler is committed and green, wire the existing display-only
conversation shell to `POST /api/jarvis/ask` with a strictly read-only fetch (no
execution controls, no refresh, no chat-log writes), gated by its own UI safety
tests. Until then the shell stays display-only and the endpoint is backend-only.

---

**Conclusion:** a minimal answer-only `POST /api/jarvis/ask` handler was added
that delegates safety to the pure classifier, returns read-only answers or
refusals, writes nothing, mutates nothing, and triggers no refresh or trading.
The Step 29 contract tests now activate and pass. `templates/jarvis.html` is
unchanged, no UI wiring was added, no chat logs were written, and
`/api/jarvis/status` shape is preserved.
