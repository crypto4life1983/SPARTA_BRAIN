# JARVIS Step 28 — Conversation Safety Classifier (tests-first, local, no route)

- **Generated:** 2026-05-30
- **Type:** code + tests + docs. No endpoint, no route, no POST, no `app.py`
  change, no template change.
- **Live page:** http://127.0.0.1:8765/jarvis
- **Status API:** http://127.0.0.1:8765/api/jarvis/status

This step implements a small, **local, deterministic** classifier that
categorizes a future JARVIS conversation question as **safe** or **forbidden**
**before** any `/api/jarvis/ask` endpoint exists. It is **preparation only** —
no backend route is wired, no POST endpoint is added, and `app.py` is not
touched. The classifier **executes nothing**; it only inspects the text of a
string and returns a label.

---

## 1. Purpose and relation to Steps 20–27

- **Step 20** polished the UI; **Step 21** proved it live and safe; **Step 22**
  gave the operator runbook; **Step 23** set known limits and the safe roadmap;
  **Step 24** added the panel glossary; **Step 25** designed the read-only
  conversation layer plan; **Step 26** shipped the display-only conversation
  shell (UI-only); **Step 27** designed the answer-only backend safety envelope.
- **Step 28 (this step)** implements the **first** Step 27 recommendation —
  **JARVIS-ASK-CLASSIFIER-MODULE**: a pure, dependency-free safety classifier
  with full unit tests and **no endpoint**.

---

## 2. Current committed baseline

| Step | Commit | What it did |
| --- | --- | --- |
| Step 20 | `4200253` | Safe UI-only polish pass (`templates/jarvis.html` only). |
| Step 21 | `4f55aae` | Post-polish live smoke memo (validation only). |
| Step 22 | `82ccf52` | Operator guide / runbook (documentation only). |
| Step 23 | `37d7dcc` | Known limits & safe roadmap (documentation only). |
| Step 24 | `9523da8` | Panel glossary (documentation only). |
| Step 25 | `6b88d9b` | Read-only conversation layer plan (documentation only). |
| Step 26 | `f2268f3` | Read-only conversation shell (UI-only). |
| Step 27 | `e961481` | Answer-only backend safety plan (documentation only). |

---

## 3. Files changed (allowed files only)

- **`jarvis_conversation_safety.py`** — new pure classifier module (stdlib `re`
  only).
- **`tests/test_jarvis_conversation_safety.py`** — new test suite for the
  classifier and the surrounding safety gates.
- **`docs/jarvis_step_28_conversation_safety_classifier/`** — this memo
  (`report.md` + `report.json`).

**Not done:** no `/api/jarvis/ask`, no POST endpoint, no route wiring, no
`app.py` change, no `templates/jarvis.html` change, no `/api/jarvis/status`
shape change, no `read_only` behavior change, no subprocess / file write /
network / broker / trading import.

---

## 4. Classifier contract

```python
classify_jarvis_question(question) -> {
    "safety_class": "<one of the seven labels>",
    "refused": bool,                # False only for the three SAFE_* labels
    "reason": "short read-only explanation",
    "normalized_question": "stripped + whitespace-collapsed input"
}
```

**Labels:** `SAFE_INFO`, `SAFE_EXPLAIN`, `SAFE_NEXT_REVIEW_STEP`,
`FORBIDDEN_EXECUTION`, `FORBIDDEN_TRADING`, `FORBIDDEN_MUTATION`, `UNSUPPORTED`.

---

## 5. Ordering and fail-closed rules

1. **Forbidden is checked first** (`TRADING → EXECUTION → MUTATION`). If any
   forbidden pattern matches, the question is refused — **forbidden always
   overrides a co-occurring safe phrase**.
2. **Safe is checked only if no forbidden match** (`NEXT_REVIEW_STEP → EXPLAIN
   → INFO`), most-specific first.
3. **Everything else is `UNSUPPORTED` and refused**, including:
   - empty / whitespace-only input,
   - non-string input,
   - ambiguous / command-like / unrecognised input.

`refused` is `False` **only** for the three `SAFE_*` labels.

> **Note on commit phrasing:** per this step's spec, stage/commit requests are
> classified as `FORBIDDEN_EXECUTION`. (Step 27's prose example grouped commit
> under mutation; the Step 28 module follows the Step 28 spec, which lists
> "stage commit" under execution.) Either way the outcome is forbidden and
> refused.

---

## 6. Purity / non-execution guarantees

- Imports **only** the stdlib `re`.
- Runs no commands, no scripts, no trades.
- Performs no file I/O and opens no network connection.
- Imports no broker / trading / subprocess module.
- The only forbidden-action vocabulary in the module is **blocked keyword
  text** used to recognise and **refuse** dangerous questions — never to act.

A test (`test_classifier_module_imports_nothing_dangerous`) scans the module
code (docstrings/comments stripped) and asserts none of `import subprocess`,
`import os`, `import socket`, `import requests`, `import urllib`, `open(`,
`import broker`, `from broker`, `place_order`, `submit_order`, `execute_trade`
appear.

---

## 7. Example classifications

**Safe**

- "Why is commander yellow?" → `SAFE_INFO`
- "What needs attention?" → `SAFE_INFO`
- "What is the trading posture?" → `SAFE_INFO`
- "What JARVIS docs exist?" → `SAFE_INFO`
- "What does `read_only` mean?" → `SAFE_EXPLAIN`
- "Explain `pTrading`" / "Explain `cache_freshness`" → `SAFE_EXPLAIN`
- "What is the safest next review step?" → `SAFE_NEXT_REVIEW_STEP`

**Forbidden**

- "Run the route-smoke script" / "Trigger a refresh" / "Stage and commit" →
  `FORBIDDEN_EXECUTION`
- "Buy NQ" / "Enable live trading" / "Connect to my broker" / "Approve and
  promote the S26 strategy" → `FORBIDDEN_TRADING`
- "Edit `app.py`" / "Save a chat log" / "Write to disk" → `FORBIDDEN_MUTATION`

**Fail-closed**

- "" / "make me a sandwich" → `UNSUPPORTED` (refused)
- "explain the trading posture then place a trade" → `FORBIDDEN_TRADING`
  (forbidden overrides safe)

---

## 8. Tests added

- `test_classifier_returns_required_keys` — exact return keys and types.
- `test_label_vocabulary_is_complete` — label tuples match the spec.
- `test_safe_questions_are_allowed` — all eight safe examples map to the right
  `SAFE_*` label with `refused=False`.
- `test_all_safe_labels_are_reachable` — each `SAFE_*` label is produced.
- `test_forbidden_execution_is_refused` / `..._trading_...` / `..._mutation_...`
  — each forbidden category is refused with the right label.
- `test_empty_is_unsupported_refused` / `test_non_string_is_unsupported_refused`
  / `test_ambiguous_is_unsupported_refused` — fail-closed paths.
- `test_forbidden_overrides_safe` — mixed safe+forbidden questions resolve to
  the forbidden class.
- `test_normalized_question_is_whitespace_collapsed` — normalization is
  whitespace-only.
- `test_classifier_module_imports_nothing_dangerous` — purity scan.
- `test_step_28_adds_no_ask_endpoint` — `app.py` has no `/api/jarvis/ask`.
- `test_jarvis_status_shape_unchanged_after_step_28` — `online`/`read_only`
  true, no `conversation`/`ask`/`chat`/`answer` key.
- `test_jarvis_template_still_has_no_controls` — template has no
  button/form/onclick/submit/post/ask/refresh.

---

## 9. Validation

- `python -m py_compile app.py jarvis_conversation_safety.py` → **PYCOMPILE_OK**
- `pytest tests/test_jarvis_route.py tests/test_jarvis_conversation_safety.py
  --rootdir=tests -q` → **167 passed**
- `python -m json.tool docs/jarvis_step_28_conversation_safety_classifier/report.json`
  → **JSON_OK**

---

## 10. Recommended next safe step

**JARVIS-ASK-ENDPOINT-TESTS-FIRST (Step 29, separate approval)** — author the
endpoint safety tests from Step 27 §10 against a **not-yet-existing**
`/api/jarvis/ask`, pinning the contract before any handler is written. Only
after this classifier and the endpoint test contract are green should a later,
separately-approved step wire a strictly answer-only, non-mutating handler that
consumes this classifier. No broker/paper/live/refresh/execution capability is
introduced at any point without explicit, separate authorization.

---

**Conclusion:** a pure, local, deterministic JARVIS conversation safety
classifier was added with full unit tests and Step 28 docs. No endpoint, route,
POST, `app.py` change, template change, status-shape change, or
execution/trading/mutation capability was introduced. The classifier only
describes the intent of input text and **fails closed**; forbidden
classifications always override safe ones.
