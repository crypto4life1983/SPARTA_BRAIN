# JARVIS Step 29 — `/api/jarvis/ask` Endpoint Contract Tests (tests-first, no handler)

- **Generated:** 2026-05-30
- **Type:** tests + docs. No endpoint, no route, no POST handler, no `app.py`
  change, no template change.
- **Live page:** http://127.0.0.1:8765/jarvis
- **Status API:** http://127.0.0.1:8765/api/jarvis/status

This step writes the **safety/behaviour contract** for a **future**
`POST /api/jarvis/ask` endpoint **before** any handler is implemented. The tests
document the required safe behaviour while proving that no handler exists today.

---

## 1. Purpose and relation to Steps 20–28

- **Step 20** polished the UI; **21** proved it live and safe; **22** runbook;
  **23** known limits & roadmap; **24** panel glossary; **25** conversation
  layer plan; **26** display-only conversation shell; **27** answer-only backend
  safety plan; **28** the pure local safety classifier
  (`jarvis_conversation_safety.py`).
- **Step 29 (this step)** implements the second Step 27/28 recommendation —
  **JARVIS-ASK-ENDPOINT-TESTS-FIRST**: pin the endpoint contract before any
  handler is written.

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

---

## 3. Files changed (allowed files only)

- **`tests/test_jarvis_ask_contract.py`** — new contract test suite for the
  future endpoint.
- **`docs/jarvis_step_29_ask_endpoint_contract_tests/`** — this memo
  (`report.md` + `report.json`).

**Not done:** no `/api/jarvis/ask` handler, no POST route, no `app.py` change,
no `templates/jarvis.html` change, no `jarvis_conversation_safety.py` change, no
`/api/jarvis/status` shape change, no execution/refresh control, no
broker/paper/live logic.

---

## 4. Skip strategy (keeps the default suite green)

The future-contract tests are guarded by:

```python
def _ask_route_exists() -> bool:
    import app as app_module
    return any(getattr(r, "path", None) == "/api/jarvis/ask"
               for r in getattr(app_module.app, "routes", []))

_ENDPOINT_ABSENT = not _ask_route_exists()
requires_ask = pytest.mark.skipif(
    _ENDPOINT_ABSENT,
    reason="Step 29 contract test for future endpoint; implementation intentionally absent.",
)
```

- **Now:** the route does not exist, so every `@requires_ask` test is
  **skipped** — the default `pytest` run stays green.
- **Later:** when a separately-approved step registers `/api/jarvis/ask`,
  `_ask_route_exists()` returns `True` and **all** contract tests activate
  automatically — **no edit to this file is needed**. They then enforce the
  safety contract on the implementation.

The current-step assertions (endpoint absence, no app.py route, no template
fetch, unchanged status shape, classifier importable) **always run**.

---

## 5. Future endpoint contract (encoded by the skipped tests)

1. `POST /api/jarvis/ask` accepts **only** a `question` string.
2. Missing/blank question → `200` with `refused=true`, or `400/422`.
3. `command`/`action`/`execute` fields are not accepted; the response carries
   **no** `command`/`action`/`execution` field.
4. **Safe** questions → `200`, with `answer`, `safety_class`, `sources_used`,
   `refused=false`.
5. **Forbidden** questions → `200` or `400` (deterministic), `refused=true`,
   `safety_class` begins with `FORBIDDEN`, `refusal_reason` present, no
   command/action/execution field.
6. Must **not** write chat logs by default.
7. Must **not** mutate the filesystem.
8. Must **not** change `/api/jarvis/status` shape.
9. Must keep `broker_control`/`paper_ready`/`live_ready` **false**.
10. Must **not** trigger refresh.
11. The UI must still contain **no** form/button/onclick/`method=post`/ask fetch
    until a separate UI-wiring step.
12. `GET /api/jarvis/ask` must **not** be supported (`405`) unless separately
    authorized.

---

## 6. Tests in this file

**Always-run (current step):**

- `test_ask_endpoint_is_currently_absent` — route table has no ask path.
- `test_post_ask_is_not_routed_today` — `POST` returns `404/405`.
- `test_app_py_has_no_ask_route` — `app.py` has no `/api/jarvis/ask`.
- `test_template_has_no_ask_fetch` — no ask fetch / form / button / onclick /
  `method=post` in the template.
- `test_status_shape_unchanged_in_step_29` — `online`/`read_only` true, no
  `conversation`/`ask`/`chat`/`answer` key.
- `test_classifier_is_importable_for_future_endpoint` — the pure classifier the
  future handler will delegate to is importable and returns `SAFE_INFO`.

**Skipped-until-implemented (future contract):**

- `test_contract_post_accepts_only_question_string`
- `test_contract_rejects_missing_or_blank_question`
- `test_contract_rejects_command_action_execute_fields`
- `test_contract_safe_question_returns_answer` (SAFE_INFO / SAFE_EXPLAIN /
  SAFE_NEXT_REVIEW_STEP)
- `test_contract_forbidden_question_is_refused` (execution / trading / mutation
  + mixed override)
- `test_contract_does_not_write_chat_logs`
- `test_contract_does_not_mutate_filesystem`
- `test_contract_does_not_change_status_shape`
- `test_contract_keeps_broker_paper_live_locked`
- `test_contract_does_not_trigger_refresh`
- `test_contract_get_ask_not_supported`

---

## 7. Validation

- `python -m py_compile app.py jarvis_conversation_safety.py` → **PYCOMPILE_OK**
- `pytest tests/test_jarvis_route.py tests/test_jarvis_conversation_safety.py
  tests/test_jarvis_ask_contract.py --rootdir=tests -q` → **PASS** (existing +
  classifier + active contract tests; future-contract tests **skipped**)
- `python -m json.tool docs/jarvis_step_29_ask_endpoint_contract_tests/report.json`
  → **JSON_OK**

---

## 8. Recommended next safe step

**JARVIS-ASK-ANSWER-ONLY-HANDLER (Step 30, separate approval)** — implement a
strictly answer-only, non-mutating `POST /api/jarvis/ask` that delegates to
`jarvis_conversation_safety.classify_jarvis_question`, returns read-only text
derived from already-aggregated status/docs, writes nothing, triggers no
refresh, and keeps broker/paper/live false. Implementing it will turn the
skipped Step 29 contract tests **green with no test edits**. No
broker/paper/live/refresh/execution capability is introduced without explicit,
separate authorization.

---

**Conclusion:** tests-first contract for a future `/api/jarvis/ask` endpoint
added, plus Step 29 docs. The future-contract tests are skipped until the route
exists (so the default suite stays green) and encode every required safety
property; current-step tests prove the endpoint is absent. No endpoint, route,
POST handler, `app.py` change, template change, classifier change, or
status-shape change was introduced.
