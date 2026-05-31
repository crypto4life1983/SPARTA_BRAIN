# SPARTA Brain Knowledge Map v1

**Date:** 2026-05-31
**Scope:** Read-only whole-system module map for JARVIS. One new pure
data+rendering module, two answer call-sites, classifier pattern additions,
tests, and docs. No new routes, no storage, no execution, no broker/paper/live
trading, no YouTube upload, no content-generation job, no file mutation outside
approved docs/tests/code.
**Verdict:** `SPARTA_BRAIN_KNOWLEDGE_MAP_READY`

---

## 1. Problem

JARVIS could discuss trading, the Strategy Factory, and overall status, but it
had no structured understanding of the *rest* of SPARTA Brain. Questions like
"what does SPARTA Brain do", "what is the YouTube builder", "what is Hydra",
"what is the affiliate system", "what automation do we have", "what is the
moving company workflow", "what is brain memory", "what dashboards exist", and
"what is the roadmap" had no dedicated answer.

## 2. What changed

| File | Change |
|------|--------|
| `jarvis_knowledge_map.py` (new) | Pure data + rendering module: an 11-module inventory + roadmap, with executive / operator / product-demo registers. No side effects. |
| `app.py` | Two read-only call-sites that delegate knowledge-map intents to the new module (one in the SAFE_INFO conversational path, one in the SAFE_EXPLAIN path). |
| `jarvis_conversation_safety.py` | Added forbidden upload/publish/generate/run-builder/render patterns (checked FIRST) and SAFE module-keyword patterns. |
| `tests/test_jarvis_ask_contract.py` | 25 new tests in section "SPARTA Brain Knowledge Map v1". |

### The data source

`jarvis_knowledge_map.py` is pure: it runs no command, opens no broker/paper/
live path, uploads nothing, generates no content, writes no file, and reads no
live state. Each module carries `key, name, keywords, purpose, status, can,
cannot, safety, demo, location`. Status values are honest:
`shipped` / `shipped (partial)` / `planned`.

Modules mapped (11): JARVIS, Strategy Factory, Trading Research (partial),
YouTube Builder, Hydra / Video Engine, Affiliate System, Automation Workflows,
**Moving Company Workflow (planned — not built)**, Brain Memory, Dashboards,
Safety & Governance. Roadmap: 5 planned/not-built items (Clone Engine
importers, ElevenLabs voice, HeyGen avatar, daily auto-training scheduler,
moving company workflow).

### Gating (why the existing branches are safe)

`build_knowledge_map_answer(q, operator, demo)` engages **only** on:

- an **all-modules** question ("what does sparta brain do", "explain all the
  modules", "what can you do"),
- a **roadmap** question, or
- a **definitional / inquiry per-module** question ("what is the youtube
  builder", "what automation do we have"),

and it **excludes status frames** (`status`, `progress`, `how is`, `update on`,
`state of`). So `factory status`, `what is the trading status`, `what is sparta
brain status`, and the workflow-health phrasings still route to their existing
dedicated branches. The module is imported lazily inside a `try/except`, so any
import problem falls through harmlessly to the legacy answer.

### Classifier

Forbidden patterns were added to `_FORBIDDEN_EXECUTION` (matched FIRST), so
"upload to youtube", "publish the video", "generate a video", "run the hydra
engine", and "...then upload to youtube" all refuse before any knowledge-map
answer is produced. SAFE module-keyword patterns were added to `_SAFE_INFO`
so module questions classify read-only.

## 3. Three registers

- **Executive (default):** purpose, status, what it can/cannot do, safety,
  "authorizes no action".
- **Operator (on request):** adds module key, status, and committed file
  location.
- **Product-demo ("...to a customer / investor / friend", "in simple terms"):**
  plain-language explanation, still read-only.

## 4. Safety guarantees preserved

- **Read-only.** The data source is pure; the two call-sites read only the
  committed inventory. No command, upload, render, broker call, order, refresh,
  or write.
- **No new endpoints / no storage.** Only `/api/jarvis/ask` and
  `/api/jarvis/status` exist under `/api/jarvis/`. No file writes.
- **Forbidden still refuses.** Upload/publish/generate/run-builder/render and
  all trading commands refuse FORBIDDEN (forbidden checked first).
- **No invented capabilities.** Unbuilt modules (moving company) are reported
  as `planned`; the roadmap is reported as `not built`. No fabricated
  performance — answers avoid profit/PnL/win-rate/"ready to trade"/"validated"/
  "approved"/"earned".
- **Status branches intact.** Factory / trading / sparta-brain / workflow
  status questions keep their existing answers; the knowledge map does not
  hijack them.

## 5. Tests

25 new tests in `tests/test_jarvis_ask_contract.py` (section "SPARTA Brain
Knowledge Map v1"):

- `test_km_module_questions_return_useful_answers` (×7) — each module question
  returns a useful read-only answer with `knowledge_map` source and no banned
  performance tokens.
- `test_km_all_modules_lists_the_system` (×3) — all-modules questions name
  several distinct modules (JARVIS, Strategy Factory, YouTube, Hydra).
- `test_km_roadmap_says_planned_not_built` — roadmap reports planned/not-built.
- `test_km_unknown_module_reported_not_invented` — moving company reported as
  planned, never shipped/operational/running.
- `test_km_operator_mode_shows_module_detail` — operator detail exposes module
  key + location.
- `test_km_demo_mode_is_plain_language` — product-demo register works.
- `test_km_forbidden_command_still_refuses` (×7) — upload/publish/generate/
  run/render and trading compounds refuse.
- `test_km_module_questions_classify_safe` — module questions classify SAFE.
- `test_km_status_questions_stay_on_existing_branches` — factory/trading/brain
  status answers are not hijacked.
- `test_km_adds_no_routes_and_writes_nothing` — only the two routes; no file
  writes.
- `test_km_keeps_status_shape_and_trading_flags_locked` — status shape and
  locked trading flags unchanged.

### Results

Run with the project venv from inside `tests/` with `PYTHONPATH=..` and
`--noconftest` (a pre-existing corrupt repo-root directory `hydra ` breaks
pytest root enumeration; environment artifact, unrelated to this change).

```
test_jarvis_ask_contract.py (km_ only)                            => 25 passed
test_jarvis_ask_contract.py + safety + route (full regression)    => 618 passed, 0 failed
```

## 6. Validation

- `report.json` parses (JSON_OK).
- Module questions return useful read-only answers.
- All-modules overview lists the whole system, not just trading.
- Unbuilt module (moving company) reported as planned, not invented.
- Operator and product-demo registers work.
- Existing factory/trading/sparta-brain/workflow status branches preserved.
- Forbidden upload/publish/generate/run/render and trading commands refuse.
- No new routes; no storage; no new execution/upload/trading controls.

## 7. Commit status

Not committed — awaiting approval per the bundle's commit policy.
