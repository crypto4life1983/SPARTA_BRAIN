# JARVIS Step 25 — Read-Only Conversation Layer Plan

- **Generated:** 2026-05-30
- **Type:** documentation only (no code, no UI, no endpoint, no API change)
- **Live page:** http://127.0.0.1:8765/jarvis
- **Status API:** http://127.0.0.1:8765/api/jarvis/status

This memo designs the **safest first version** of a JARVIS chat/conversation
layer so the operator can "talk to JARVIS" from the Command Center, while
JARVIS stays **read-only, non-executing, and unable to control broker/paper/live
trading**. **Documentation only** — no chat box is built here; this step adds
no capability, control, endpoint, or API change.

---

## 1. Purpose and relation to Steps 20–24

- **Step 20** polished the UI (CSS/HTML/labels only).
- **Step 21** proved the polished UI is live and safe
  (**JARVIS_POST_POLISH_SMOKE_PASS**).
- **Step 22** gave the operator runbook.
- **Step 23** set known limits and the safe, risk-tiered roadmap.
- **Step 24** added the panel glossary.
- **Step 25 (this memo)** is a forward-looking design memo only: it specifies
  what a future read-only conversation layer could safely answer, what it must
  always refuse, the read-only UX/backend shape, and the safety gates that must
  pass before any code is written.

---

## 2. Current committed baseline

| Step | Commit | What it did |
| --- | --- | --- |
| Step 20 | `4200253` | Safe UI-only polish pass (`templates/jarvis.html` only). |
| Step 21 | `4f55aae` | Post-polish live smoke memo (validation only). |
| Step 22 | `82ccf52` | Operator guide / runbook (documentation only). |
| Step 23 | `37d7dcc` | Known limits & safe roadmap (documentation only). |
| Step 24 | `9523da8` | Panel glossary (documentation only). |

---

## 3. What "talking to JARVIS" means (safe first version)

"Talking to JARVIS" means asking plain-language questions and receiving
plain-language answers derived **solely** from already-aggregated,
already-committed, read-only state. JARVIS explains what the dashboard already
shows — it is a **narrator over the same data the panels render**.

**It IS:**
- An explain-only assistant over the existing `/api/jarvis/status` payload and
  committed JARVIS docs.
- A way to ask "why is this panel yellow" and get the same answer the
  runbook/glossary already give.
- A read-only summarizer that points the operator to the right panel, field,
  or memo.

**It is NOT:**
- A command console — it issues no commands.
- A control surface — it arms nothing, refreshes nothing, writes nothing.
- A trading interface — it places no orders and toggles no paper/live/broker
  flag.
- An autonomous agent — it does not decide or act on its own.

---

## 4. What JARVIS is allowed to answer

| Question | Source | Answer style |
| --- | --- | --- |
| What is the current system status? | `commander_snapshot` + `system_core` + `online`/`read_only` | Summarize `overall_state` and contributing signals; state `read_only=true` and online status. |
| Why is commander yellow / red / green? | `commander_snapshot.warnings` + contributing checks | Name the specific driver (e.g. dirty/untracked tree for yellow); clarify yellow = needs attention, not approval. |
| What changed in the latest reports? | `health_report` + `route_smoke_report` + `cache_freshness` timestamps | Describe latest cached outcomes and freshness; note these are cached manual-tool outputs, not live runs. |
| Which panels need attention? | per-section warning/critical vs Step 24 glossary | List panels in warning/critical with the glossary's operator action; never invent a fix-from-UI. |
| What does this field mean? | Step 24 `field_glossary` | Return the plain-language definition and the must-be value. |
| What is the safest next step? | Step 23 safe improvements + recommended options | Recommend only docs-only / read-only options; defer medium/high-risk to explicit human approval. |
| What JARVIS docs exist? | committed `docs/jarvis_step_*/` memos | Enumerate the committed step memos and their purpose; point, do not execute. |
| What trading posture is shown (read-only only)? | `trading_detail` + `trading_bridge` | Report `read_only=true` and `paper_ready`/`live_ready`/`broker_control=false`; state research is candidate/visibility only, no order path. |

---

## 5. What JARVIS must refuse or block

| Request | Reason it is refused |
| --- | --- |
| Place a trade | JARVIS holds no order path; placing trades is outside its read-only mandate. |
| Enable paper / live trading | `paper_ready` / `live_ready` must always stay false; arming them is forbidden unless explicitly authorized via a separate gated channel. |
| Connect a broker | `broker_control` must always stay false; JARVIS cannot connect to or command any broker. |
| Run a strategy | JARVIS does not execute strategies, scripts, or missions. |
| Approve a strategy | Approvals that trigger downstream effects are forbidden on the JARVIS surface. |
| Modify files | The web surface never mutates the filesystem. |
| Trigger scripts | Cached-report and other scripts are manual-only and never run from the web. |
| Refresh or mutate state | GET-only; there is no refresh endpoint and no state-mutating action. |
| Write into trading systems | JARVIS never writes back to any trading, research, or downstream system. |

---

## 6. Proposed read-only UX (future, display-only)

A **future**, display-only chat panel on `/jarvis` — designed here only, not
built in Step 25:

- A **future chat panel** rendered inside the existing read-only grid.
- An **input field** for typing a question (text only; submitting fetches an
  answer-only response, never an action).
- An **answer area** that renders plain-language, read-only answers.
- A list of **suggested safe questions** the operator can click to populate the
  input (populate only — never auto-execute anything).
- A persistent, visible **"READ-ONLY ANSWERS ONLY"** warning banner.
- **No buttons that execute anything** — no run, refresh, trade, approve, or
  arm; only "ask," which returns text.

**Constraints:** no `<button>`/`<form>`/`onclick`/`method=post` that performs
any action other than requesting a text answer; no copy-and-run affordance for
any prompt/command; the panel must visibly reinforce that answers are
observations, not authorizations.

---

## 7. Proposed read-only backend shape (future implementation)

- **`GET /api/jarvis/status` remains UNCHANGED** — same 24 top-level keys, same
  fail-closed `_jarvis_safe` wrapping, GET-only.
- **A future `POST /api/jarvis/ask`** may be considered **only** if it is
  strictly **answer-only and non-mutating**: it accepts a question, returns
  text derived from already-read state, and changes nothing. It must be a
  separate, explicitly-approved step — **not** part of Step 25.
- **Hard constraints:**
  - No command execution of any kind.
  - No filesystem writes, **except** an optional **local read-only chat log**
    that may be added **only after separate explicit approval** (and even then
    it logs Q/A text only, never executes or mutates system state).
  - No broker / trading writes.
  - No refresh / cache regeneration / probe execution triggered by a question.
  - Fail-closed: if it cannot answer safely from read-only sources, it declines
    rather than acting.

---

## 8. Recommended context sources

- The current `GET /api/jarvis/status` response (already-aggregated read-only
  sections).
- Committed JARVIS docs (`docs/jarvis_step_*/` memos: runbook, known-limits,
  glossary).
- `system_map` (panels, manual-only scripts, tracked/ignored files, posture
  flags).
- `commander_snapshot` (derived top-level verdict, warnings, counts).
- `trading_detail` read-only fields (`read_only`, `paper_ready`, `live_ready`,
  `broker_control`, candidate status).
- `health_report` and `route_smoke_report` fields (cached offline outcomes).
- `cache_freshness` metadata (age vs threshold, gitignored status, timestamps).

---

## 9. Safety gates required before implementation

- Tests proving **no execution verbs** (buy/sell/run/approve/arm/connect)
  trigger any action — they must produce only text or a refusal.
- Tests proving **forbidden requests** (the §5 list) are refused with a clear
  read-only message.
- Tests proving **`GET /api/jarvis/status` shape is unchanged** (still 24
  top-level keys, `online`/`read_only` present).
- Tests proving **no broker/paper/live controls** exist or are reachable
  (`broker_control`/`paper_ready`/`live_ready` stay false).
- Tests proving **no POST endpoint mutates state** — any future
  `/api/jarvis/ask` is answer-only and changes nothing on disk or in trading
  systems.
- Tests proving the **UI exposes no execution/refresh control** (no
  `<button>`/`<form>`/`onclick`/`method=post`/refresh fetch that acts).

---

## 10. Example safe questions and expected answer style

- **"Why is the commander snapshot yellow right now?"** → It is yellow because
  the working tree is dirty/untracked — a conservative-by-design verdict
  meaning "needs attention, not fully green." The required safety checks can
  still be green. Yellow is not an error and not approval to act.
- **"Which panels need attention today?"** → Lists only panels currently in
  warning/critical, each paired with the Step 24 glossary's recommended
  (offline/observe-only) operator action. If none, says all key panels read
  healthy.
- **"What does `broker_control` mean and what should it be?"** → Defines it as
  whether JARVIS holds any broker control / order path, and states it must
  always be false; a true value is a CRITICAL safety regression to investigate.
- **"What is the safest next step after Step 25?"** → Recommends only docs-only
  or read-only options (e.g. the Step 26 plan below) and explicitly defers any
  medium/high-risk work to separate human approval.

---

## 11. Example forbidden questions and refusal style

- **"Place a long MNQ trade for me."** → JARVIS is read-only and holds no order
  path. It cannot place trades. Trade authorization happens only through a
  separate, explicitly-gated human channel — never from this surface.
- **"Turn on live trading / arm `paper_ready`."** → Refused. `paper_ready` and
  `live_ready` must always stay false on the JARVIS surface; arming them is
  forbidden unless explicitly authorized through a separate gated channel.
- **"Connect to my broker and sync positions."** → Refused. `broker_control`
  must stay false; JARVIS cannot connect to or command any broker.
- **"Run the route-smoke script now and refresh the caches."** → Refused.
  Cached-report scripts are manual-only and are never run from the web; there
  is no refresh control. JARVIS only reads already-generated cached reports.
- **"Approve and promote the S26 strategy."** → Refused. Strategy
  promotion/approval that triggers downstream effects is forbidden; JARVIS
  shows research state but never approves or executes.

---

## 12. Recommended Step 26 implementation plan (if Step 25 is approved)

If Step 25 is approved, Step 26 is a docs-or-UI-only, strictly read-only first
slice of the conversation layer, gated by the safety tests above:

- **JARVIS-CONVERSATION-UI-SHELL (display-only)** — add a display-only chat
  panel shell to `/jarvis` (input + answer area + suggested-safe-questions +
  "read-only answers only" banner) with **no backend wired yet** (renders a
  static "answer layer not yet enabled" message). UI-only, no endpoint, no
  execution.
- **JARVIS-ASK-ANSWER-ONLY-ENDPOINT (separate approval)** — only after the UI
  shell and all safety gates pass, add a strictly answer-only, non-mutating ask
  endpoint that returns text derived from read-only sources, accompanied by the
  full safety-gate test suite proving no execution, no mutation, no
  broker/paper/live, and unchanged status shape.
- **JARVIS-CONVERSATION-SAFETY-TESTS-FIRST** — author the safety-gate tests
  (refusal, no-execution, unchanged-shape) **before** any answer backend, so
  the implementation is test-gated from the start.

**Sequencing rule:** tests and the display-only shell come first; any answer
backend is a later, separately-approved step. No broker/paper/live/refresh/
execution capability is introduced at any point without explicit, separate
authorization.

---

## Safety interpretation rules

- **Green** — observation healthy.
- **Yellow** — attention needed.
- **Red** — stop and investigate.

**None of these colours, and no answer from a conversation layer, authorizes
trading or execution.**

## Never confuse this with permission

An answer from a JARVIS conversation layer is an observation about
already-known state. It is **NOT** an instruction, an approval, or
authorization to execute trades, run scripts, place orders, or arm paper/live
paths. A conversation layer that could be mistaken for permission would itself
be a safety regression. Authorization for any action comes from an explicit
human decision through the proper, separately-gated channel — never from a chat
answer on this page.

---

**Conclusion:** documentation-only read-only conversation layer plan created.
No code, UI, tool, test, endpoint, API, or trading surface was changed. No chat
box was built; this memo only designs the safe first version and the safety
gates that must pass before any implementation.
