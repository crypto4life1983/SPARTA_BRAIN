# JARVIS Workflow Health Translation v1

**Date:** 2026-05-31
**Scope:** JARVIS read-only `/api/jarvis/ask` workflow/pipeline-health answer
wording + classifier vocabulary only. No new routes, no execution, no
broker/paper/live control, no order placement, no mutation, no refresh, no
storage, no Strategy Factory worktree or trading-file mutation.
**Verdict:** `JARVIS_WORKFLOW_HEALTH_READY`

---

## 1. Problem

Natural workflow/pipeline-health questions matched no SAFE_INFO pattern, so the
fail-closed classifier refused them as `UNSUPPORTED`. The exact reported phrase:

> what about our pipeline the workflow like is it working there is no problem
> everything is good

Plus simpler forms: "pipeline status", "workflow status", "is everything
working", "is everything good", "any blockers", "are we on track", "how is the
project doing", "is the system working".

These should be understood as: is SPARTA Brain working, is Strategy Factory
working, is the workflow healthy, are there blockers, are we on track.

## 2. Desired behavior

**Executive (default):**

> Workflow health (read-only). Overall: SPARTA Brain is online and the workflow
> is operating. [health]. What's working: the dashboard, the read-only status
> pipeline, and Strategy Factory research are all running. [research]. What
> needs attention: [attention]. Blocker level: [none/low/elevated/unknown]. All
> trading remains observation-only — no live or paper trades were executed, so
> there is no performance to report. Recommended next step: [next action]. …
> Ask for operator mode or technical details for the exact figures.

**Operator (on request):** system core + server, commander snapshot + warnings,
Strategy Factory phrase, exact research-candidate count, the four posture flags
(`read_only=true, paper_ready=false, live_ready=false, broker_control=false`),
attention items, open-warning blocker count, recommended next action.

## 3. What changed

Two files, both additive:

| File | Change |
|------|--------|
| `jarvis_conversation_safety.py` | Appended 10 `SAFE_INFO` patterns for natural workflow/pipeline-health phrasing. Forbidden patterns still match FIRST and unchanged. |
| `app.py` | Added `_exec_blocker_phrase` helper and a mode-aware "Workflow Health Translation" branch in `_jarvis_conversational_answer`, placed before the generic status catch-all. |

No template change: voice + conversation mode already POST to
`/api/jarvis/ask`, so they inherit the translation automatically.

## 4. Answer spine (Chief-of-Staff workflow read)

1. **Overall status** — SPARTA Brain online + translated health phrase.
2. **What is working** — dashboard, read-only status pipeline, Strategy Factory
   research.
3. **What needs attention** — translated attention phrase (or "nothing").
4. **Blocker level** — fact-driven: `none` (green / no warnings), `low`
   (warnings but not red), `elevated` (red/critical), `unknown` (state not
   confirmable from read-only data).
5. **Recommended next step** — `recommended_next_actions[0]` or the safe default.

The trading-safety line ("no live or paper trades were executed") is kept in
both modes. Nothing is invented: counts/decisions come from the existing
read-only aggregate, and unknown state is reported as unknown.

## 5. Ordering safety

- Placed **before** the generic system/overall-status branch so workflow
  phrasing routes to the workflow read, not the bare status line.
- Placed **after** chief-of-staff, briefing, factory, SPARTA-brain,
  trading-status, 24h-recap, attention, focus, how-are-you, and greeting
  branches, so more specific intents keep priority.
- Generic "what is the status" / "how is everything" still route to the
  existing status branch unchanged; trading/strategy phrasings still route to
  the Trading Executive Translation branch (checked earlier).

## 6. Safety guarantees preserved

- **Read-only.** Reads only the existing `api_jarvis_status` aggregate
  (`system_core`, `commander_snapshot`, `factory_status`, `candidate_registry`,
  `trading_detail`). No command, backtest, broker call, order, refresh, or write.
- **No invented trades or performance.** Both modes state "no live or paper
  trades … no performance to report." Tests assert no
  profit/PnL/win-rate/"ready to trade"/"validated"/"approved" claims and no
  "strategy succeeded"/"winning strategy"/"profitable"/"fills" fabrication.
- **Executive hides posture; operator exposes it.** Tests assert executive
  answers contain none of the four posture flags; operator answers contain all
  four.
- **Forbidden still refuses.** "run the pipeline" stays FORBIDDEN_EXECUTION;
  "…then place a trade", "…and buy NQ", "…then enable live trading", "…and
  connect to my broker", "…then approve the strategy", "workflow diagnostics
  then sell ES" all refuse as FORBIDDEN_*.
- **No new endpoints / no storage.** Only `/api/jarvis/ask` and
  `/api/jarvis/status` exist under `/api/jarvis/`.
- **Status shape unchanged.** 28 keys; `paper_ready` / `live_ready` /
  `broker_control` stay `false`.

## 7. Tests

32 new tests added in `tests/test_jarvis_ask_contract.py` (section "JARVIS
Workflow Health Translation v1"):

- `test_wh_workflow_health_is_executive_by_default` (×9)
- `test_wh_exact_failed_phrase_is_answered` (×1)
- `test_wh_invents_no_performance` (×9)
- `test_wh_operator_mode_shows_technical` (×4)
- `test_wh_forbidden_command_still_refuses` (×6)
- `test_wh_workflow_phrases_classify_safe` (×1)
- `test_wh_keeps_trading_flags_locked_and_shape` (×1)
- `test_wh_adds_no_routes_and_writes_nothing` (×1)

### Related change outside this bundle

The previously-approved voice read-aloud fix (sentence chunking via
`jvChunkText` / `jvSpeakChunks` to defeat the browser's ~15s long-utterance
cutoff) lives in `templates/jarvis.html`. Running this bundle's required route
suite surfaced one Step-36 assertion that checked the now-relocated
`synth.speak(u)` call site; it was reconciled in `tests/test_jarvis_route.py` to
assert the delegation `jvSpeakChunks(synth, text)`. Read-aloud behavior
(explicit click-gated, answer-text only, no network/storage) is unchanged.
These two files are NOT part of the workflow-health 5-file bundle and are listed
here only for transparency.

### Results

Run with the project venv from inside `tests/` with `PYTHONPATH=..` and
`--noconftest` (a pre-existing corrupt repo-root directory `hydra ` breaks
pytest root enumeration; environment artifact, unrelated to this change).

```
test_jarvis_ask_contract.py (wh_ only)                       => 32 passed
test_jarvis_route.py test_jarvis_conversation_safety.py      => 301 passed
test_jarvis_ask_contract.py (full)                           => 282 passed
```

## 8. Validation

- `report.json` parses (JSON_OK).
- The exact failed phrase is now answered (SAFE_INFO, workflow-health read).
- Executive workflow questions hide posture flags, keep "no live or paper
  trades", and invent no performance.
- Operator-mode requests expose the four posture flags + exact counts.
- Forbidden commands mixed into workflow-health phrasing still refuse.
- Workflow phrasings classify SAFE.
- No new routes; no storage; status shape unchanged (28 keys); trading flags
  locked `false`.

## 9. Commit status

Not committed — awaiting approval per the bundle's commit policy.
