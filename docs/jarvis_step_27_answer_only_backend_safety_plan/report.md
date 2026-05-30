# JARVIS Step 27 — Answer-Only Backend Safety Plan

- **Generated:** 2026-05-30
- **Type:** documentation only (no code, no UI, no endpoint, no API change)
- **Live page:** http://127.0.0.1:8765/jarvis
- **Status API:** http://127.0.0.1:8765/api/jarvis/status

This memo designs the **future** `/api/jarvis/ask` backend **before** any
implementation. The endpoint must be **answer-only, non-mutating, read-only**,
and unable to execute commands, control trading, write files, refresh state, or
trigger scripts. **Documentation only** — `/api/jarvis/ask` is **not** created
here; this step adds no endpoint, backend logic, or API change.

---

## 1. Purpose and relation to Steps 20–26

- **Step 20** polished the UI; **Step 21** proved it live and safe; **Step 22**
  gave the operator runbook; **Step 23** set known limits and the safe roadmap;
  **Step 24** added the panel glossary; **Step 25** designed the read-only
  conversation layer plan; **Step 26** shipped the display-only conversation
  shell (UI-only, no backend).
- **Step 27 (this memo)** designs the safety envelope for a future answer-only
  backend so that, if and when implemented, it stays strictly inside the
  read-only, non-executing posture proven across Steps 20–26.

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

---

## 3. What `/api/jarvis/ask` would be allowed to do (future)

- Receive a user question (a plain text string).
- Classify it as **safe** or **forbidden** using a deterministic local safety
  classifier.
- Answer **only** from already-read, read-only context.
- Explain the current system status (`overall_state`, `online`, `read_only`,
  contributing signals).
- Explain fields, panels, and committed JARVIS docs.
- Suggest the safest next **review** step (docs-only / read-only options),
  never an action.

---

## 4. What `/api/jarvis/ask` must never do

- Execute commands.
- Run scripts.
- Write files.
- Mutate state.
- Refresh status.
- Stage or commit code.
- Place trades.
- Enable paper or live trading.
- Connect brokers.
- Approve strategies.
- Modify trading systems.

---

## 5. Proposed request/response shape (future implementation)

**Request** — a question string only:

```json
{ "question": "Why is the commander snapshot yellow?" }
```

- The **only** accepted field is `question`.
- There is **no** `command` field, **no** `action` field, **no** `execute`/
  `cmd`/`shell`/`script`/`order`/`trade` field. Any such field is rejected by
  shape, not interpreted.

**Response** — pure read-only data:

```json
{
  "answer": "string — read-only answer or refusal message",
  "safety_class": "SAFE_INFO | SAFE_EXPLAIN | SAFE_NEXT_REVIEW_STEP | FORBIDDEN_EXECUTION | FORBIDDEN_TRADING | FORBIDDEN_MUTATION | UNSUPPORTED",
  "sources_used": ["commander_snapshot", "system_map"],
  "refused": false,
  "refusal_reason": "present only when refused"
}
```

**Invariants:**
- The response **never** contains a `command`, `action`, or `execution` field.
- The response is pure data derived from read-only context; producing it changes
  nothing on disk or in any trading/research system.
- If the backend cannot answer safely from read-only sources, it sets
  `refused=true` and explains, rather than acting.

---

## 6. Safety classifier design

A deterministic, local, dependency-free classifier maps each question to exactly
one label. Forbidden labels **short-circuit to a refusal before any context is
assembled**. Safe labels select which read-only sources may be consulted. The
classifier performs no I/O beyond reading the already-aggregated context.

| Label | Meaning | Handling |
| --- | --- | --- |
| `SAFE_INFO` | Answerable from current read-only status. | Answer from `commander_snapshot` / `system_core` / status meta. |
| `SAFE_EXPLAIN` | Asks what a field/panel/doc means. | Answer from committed glossary/runbook/`system_map`. |
| `SAFE_NEXT_REVIEW_STEP` | Asks for the safest next step. | Return only docs-only / read-only review options; defer risk to human approval. |
| `FORBIDDEN_EXECUTION` | Asks to run a command/script/tool, refresh, or trigger. | Refuse; `refused=true`; no context assembled. |
| `FORBIDDEN_TRADING` | Asks to place/enable trades, arm paper/live, connect broker, approve strategy. | Refuse; `refused=true`; emphasize no order path exists. |
| `FORBIDDEN_MUTATION` | Asks to write files, stage/commit, or modify any system. | Refuse; `refused=true`; emphasize read-only surface. |
| `UNSUPPORTED` | Out of scope / not answerable from read-only context. | Decline politely; `refused=true`; redirect to a safe status explanation. |

**Ordering rule (fail-closed):** if a question matches both a safe and a
forbidden pattern, it is treated as **forbidden**.

---

## 7. Refusal style

- **Short**, **clear**, explains that **JARVIS is read-only**, and **redirects
  to a safe status explanation**.
- **Template:** "JARVIS is read-only and cannot *&lt;forbidden action&gt;*. It
  only explains already-known status. I can instead tell you *&lt;safe redirect,
  e.g. why the commander snapshot is yellow or what a field means&gt;*."
- **Must not:** apologize-and-comply; provide a command to run instead; include
  any copy-and-run affordance.

---

## 8. Context sources allowed

- The current `GET /api/jarvis/status` object (already-aggregated read-only
  sections).
- Committed JARVIS docs (`docs/jarvis_step_*/` memos: runbook, known-limits,
  glossary, plans).
- The existing `system_map` (panels, manual-only scripts, tracked/ignored files,
  posture flags).
- `commander_snapshot` (derived top-level verdict, warnings, counts).
- `trading_detail` read-only fields (`read_only`, `paper_ready`, `live_ready`,
  `broker_control`, candidate status).
- `health_report` / `route_smoke_report` / `cache_freshness` fields (cached
  offline outcomes and metadata).

---

## 9. Context sources forbidden

- Broker APIs.
- Live trading state mutation.
- Paper trading control.
- Shell commands.
- Filesystem write operations.
- Git operations.
- External scripts.

---

## 10. Required tests before implementation

- **Endpoint exists only after explicit approval** — until then a test asserts
  `/api/jarvis/ask` is absent from `app.py` and the route table.
- **Forbidden execution requests are refused** (`refused=true`,
  `FORBIDDEN_EXECUTION`, no side effect).
- **Forbidden trading requests are refused** (`refused=true`,
  `FORBIDDEN_TRADING`).
- **Forbidden mutation requests are refused** (`refused=true`,
  `FORBIDDEN_MUTATION`).
- **Safe status questions are answered** (`refused=false`,
  `SAFE_INFO`/`SAFE_EXPLAIN`, `sources_used` populated).
- **`GET /api/jarvis/status` shape is unchanged** (still 24 top-level keys,
  `online`/`read_only` present).
- **No new execution buttons/forms/onclick in the UI** (template scan stays
  clean).
- **No chat logs are written** (no file writes occur during an ask call).
- **No broker/paper/live control is reachable** (`broker_control`/`paper_ready`/
  `live_ready` stay false).

---

## 11. Example safe questions and expected responses

- **"What is the current system status?"** → `SAFE_INFO`. Summarizes
  `overall_state` and contributing signals; states `online` and
  `read_only=true`. `refused=false`. `sources_used: ['commander_snapshot',
  'system_core']`.
- **"Why is the commander snapshot yellow?"** → `SAFE_INFO`. Explains yellow is
  conservative-by-design, usually a dirty/untracked tree; needs attention, not
  approval. `refused=false`. `sources_used: ['commander_snapshot']`.
- **"What does `broker_control` mean and what should it be?"** → `SAFE_EXPLAIN`.
  Defines it and states it must always be false; true is a CRITICAL regression.
  `refused=false`. `sources_used: ['trading_detail','glossary']`.
- **"What is the safest next step to review?"** → `SAFE_NEXT_REVIEW_STEP`.
  Recommends docs-only / read-only review options only; defers any
  medium/high-risk work to explicit human approval. `refused=false`.

---

## 12. Example forbidden questions and expected refusals

- **"Run the route-smoke script and refresh the caches."** →
  `FORBIDDEN_EXECUTION`. "JARVIS is read-only and cannot run scripts or refresh
  caches. It only explains already-known status. I can instead tell you what the
  cached route-smoke report currently shows."
- **"Enable live trading / arm `paper_ready`."** → `FORBIDDEN_TRADING`. "JARVIS
  is read-only and cannot enable paper or live trading; there is no order path.
  `paper_ready` and `live_ready` must stay false. I can instead explain the
  current read-only trading posture."
- **"Connect to my broker and open a position."** → `FORBIDDEN_TRADING`.
  "JARVIS is read-only and holds no broker control. It cannot connect a broker
  or open any position. I can instead explain why `broker_control` must remain
  false."
- **"Commit my staged files and write a chat log."** → `FORBIDDEN_MUTATION`.
  "JARVIS is read-only and cannot stage, commit, or write files. I can instead
  explain the current File Hygiene staged count from the cached report."
- **"Approve and promote the S26 strategy."** → `FORBIDDEN_TRADING`. "JARVIS is
  read-only and cannot approve or promote strategies. It shows research state
  only. I can instead summarize the read-only Trading Research Detail."

---

## 13. Recommended Step 28

**Tests-first, lowest-risk path.** Two options depending on risk appetite; the
safer default is the classifier / endpoint tests in isolation **before** any
route is wired:

- **JARVIS-ASK-CLASSIFIER-MODULE (local, no route)** — implement a minimal,
  deterministic, dependency-free safety-classifier module with full unit tests
  (safe vs forbidden labels, fail-closed ordering) and **no endpoint**. The
  module performs no I/O and is not wired into any route yet.
- **JARVIS-ASK-ENDPOINT-TESTS-FIRST** — author the endpoint safety tests (the
  §10 list) against a not-yet-existing `/api/jarvis/ask`, pinning the contract
  before any handler is written.

**Risk guidance:** prefer the classifier module + unit tests first (pure
function, no route, no `app.py` change). Only after the classifier and the
endpoint test contract are green should a later, separately-approved step wire a
strictly answer-only, non-mutating handler. No broker/paper/live/refresh/
execution capability is introduced at any point without explicit, separate
authorization.

---

## Safety interpretation rules

- **Green** — observation healthy.
- **Yellow** — attention needed.
- **Red** — stop and investigate.

**None of these colours, and no answer from an ask backend, authorizes trading
or execution.**

## Never confuse this with permission

An answer from `/api/jarvis/ask` would be an observation about already-known
state. It is **NOT** an instruction, an approval, or authorization to execute
trades, run scripts, place orders, or arm paper/live paths. A backend that could
be mistaken for permission — or coaxed into acting — would itself be a safety
regression, which is exactly why this plan makes the endpoint answer-only,
fail-closed, and test-gated before implementation. Authorization for any action
comes from an explicit human decision through the proper, separately-gated
channel — never from an ask answer.

---

**Conclusion:** documentation-only answer-only backend safety plan created. No
code, UI, tool, test, endpoint, API, or trading surface was changed.
`/api/jarvis/ask` was **not** created; this memo only designs its safety
envelope, request/response shape, classifier, refusal style, allowed/forbidden
context sources, and the tests that must pass before any implementation.
