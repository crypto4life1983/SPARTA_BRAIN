# JARVIS Executive Translation Mode v1

**Date:** 2026-05-31
**Scope:** JARVIS read-only `/api/jarvis/ask` answer wording + classifier
vocabulary only. No new routes, no execution, no broker/paper/live control, no
order placement, no mutation, no refresh, no storage of chat/audio/transcripts,
no Strategy Factory worktree or trading-file mutation.
**Verdict:** `JARVIS_EXECUTIVE_TRANSLATION_READY`

---

## 1. Goal

Give JARVIS two read-only ways to say the same true thing:

- **Executive Mode (default)** — customer/investor/demo-friendly. Internal
  facts are translated into business language and raw implementation detail
  (exact report counts, report names, raw warning text, posture flags) is
  hidden.
- **Operator Mode (on request)** — the full technical briefing, with exact
  counts, report names, raw warnings, and the locked posture flags.

The same safety phrasing ("observation-only", "no live or paper trades were
executed") is preserved verbatim in BOTH modes, and the classifier still gates
every question.

## 2. Translation examples (executive mode)

| Internal fact | Executive phrasing |
|---------------|--------------------|
| "62 committed reports on disk" | "Research activity is progressing normally." |
| "7 research candidates tracked" | "Several strategy candidates are currently under evaluation." |
| "Git working tree is dirty" | "Some maintenance items require attention." |
| "Large untracked backlog" | "There are project housekeeping tasks that should be reviewed." |
| commander state green/yellow/red | "All systems are operating normally." / "online and stable, with a few maintenance items under review." / "online, with several items currently needing attention." |

## 3. Executive briefing structure (all read-only)

```
Greeting          -> "Good morning Mahmoud. Here is your executive briefing."
Business status   -> "SPARTA Brain is online." + translated commander health
Research status   -> translated factory state (no counts/report names)
Trading status    -> "All trading remains observation-only — no live or paper
                      trades were executed, so there is no performance to report."
Attention items   -> translated warnings (no raw warning text / counts)
Recommendation    -> recommended_next_actions[0]
```

## 4. What changed

Two files, both additive:

| File | Change |
|------|--------|
| `jarvis_conversation_safety.py` | Added SAFE_INFO regex patterns for operator-mode triggers: `operator mode`, `show (me/the/technical) details`, `technical details`, `diagnostics`, `exact counts`. Forbidden patterns are still matched FIRST and unchanged. |
| `app.py` | Added an executive translation layer (`_exec_health_phrase`, `_exec_research_phrase`, `_exec_candidate_phrase`, `_exec_attention_phrase`) and an `_operator` mode flag to `_jarvis_conversational_answer`. The briefing, attention, and general-status branches are now mode-aware: executive (translated) by default, operator (full technical detail) when an operator trigger is present. A bare operator request ("operator mode" / "diagnostics" / "show technical details") returns the full technical briefing. |

No template change: voice + conversation mode already POST to
`/api/jarvis/ask`, so they inherit both modes automatically.

## 5. Triggers

| Mode | Example phrases |
|------|-----------------|
| Executive (default) | "good morning", "executive briefing", "morning briefing", "summarize the system", "what is the status" |
| Operator | "operator mode", "show details", "show technical details", "technical details", "diagnostics", "exact counts", "exact status" — alone or appended to a briefing/status question |

Operator triggers only change wording; both modes are equally read-only and both
keep the trading-safety phrasing.

## 6. Safety guarantees preserved

- **Read-only.** Both modes read only the existing `api_jarvis_status`
  aggregate. They run no command, no backtest, no broker call; place no order;
  trigger no refresh; write nothing.
- **No invented trades or performance.** Both modes state "no live or paper
  trades were executed … so there is no performance to report." Tests assert no
  profit/PnL/win-rate/"ready to trade"/"validated"/"approved" claims appear in
  either mode.
- **Executive hides raw detail; operator exposes it.** Tests assert executive
  mode contains none of `read_only=true`, `paper_ready=false`,
  `live_ready=false`, `broker_control=false`, `committed reports`,
  `candidate(s)`, `warning(s)`; operator mode contains all of them.
- **Classifier still gates everything.** Forbidden-first ordering is unchanged:
  "operator mode then buy NQ", "show technical details and commit the changes",
  "diagnostics then place a trade", "exact counts then enable live trading",
  "good morning, operator mode, then connect to my broker" all still refuse as
  FORBIDDEN_*.
- **No new endpoints / no refresh / no snapshot route.** Only
  `/api/jarvis/ask` and `/api/jarvis/status` exist under `/api/jarvis/`.
- **Status shape unchanged.** `/api/jarvis/status` still has exactly 28 keys;
  `paper_ready` / `live_ready` / `broker_control` stay `false`.
- **No storage.** Neither mode writes data files or chat/audio/transcript logs
  (asserted by filesystem-diff tests).

## 7. Tests

25 new tests added in `tests/test_jarvis_ask_contract.py`
(section "JARVIS Executive Translation Mode v1"):

- `test_et_executive_mode_hides_raw_details` (×5)
- `test_et_operator_mode_exposes_raw_details` (×5)
- `test_et_operator_mode_invents_no_trades_or_performance` (×2)
- `test_et_executive_status_is_translated`
- `test_et_operator_status_exposes_posture`
- `test_et_operator_triggers_classify_safe` (×5)
- `test_et_forbidden_intent_in_operator_mode_still_refused` (×5)
- `test_et_modes_add_no_routes_and_write_nothing`

Three pre-existing briefing-triggered tests were reconciled (briefings are now
executive by default, so raw posture/factory tokens moved to operator-mode
assertions): `test_ci_morning_briefing_summarizes_readonly`,
`test_eb_briefing_is_executive_structure`,
`test_eb_overnight_update_is_readonly_no_fake_trades`.

### Results

Run with the project venv (`.venv`). A pre-existing corrupt directory in the
repo root (on-disk name `hydra ` — a private-use char + trailing space) breaks
pytest's root enumeration, so the suite is run from inside `tests/` with
`PYTHONPATH=..` and `--noconftest`. Environment artifact, unrelated to this
change.

```
PYTHONPATH=.. ../.venv/Scripts/python -m pytest \
  test_jarvis_route.py test_jarvis_conversation_safety.py \
  --noconftest -q -p no:cacheprovider
=> 301 passed

PYTHONPATH=.. ../.venv/Scripts/python -m pytest \
  test_jarvis_factory_panels.py test_jarvis_ask_contract.py \
  test_jarvis_snapshot_report.py --noconftest -q -p no:cacheprovider
=> 226 passed   (was 201; +25 executive-translation tests)
```

## 8. Validation

- `report.json` parses (JSON_OK).
- Executive triggers ("good morning", "executive briefing", "morning briefing",
  "summarize the system", "what is the status") answer `refused=false`,
  `SAFE_INFO`, hide raw tokens, keep safety phrasing.
- Operator triggers ("operator mode", "show technical details", "diagnostics",
  "exact counts") answer `refused=false`, `SAFE_INFO`, expose posture flags +
  exact counts + raw factory detail.
- Neither mode invents trades or performance.
- Forbidden phrases mixed into either mode still refuse (FORBIDDEN_*).
- No new routes; `/api/jarvis/` exposes only `ask` and `status`.
- `/api/jarvis/status` shape unchanged (28 keys); trading flags locked false.

## 9. Commit status

Not committed — awaiting approval per the bundle's commit policy. `git status`:
`app.py` and `jarvis_conversation_safety.py` modified;
`tests/test_jarvis_ask_contract.py` modified; report files added under
`docs/jarvis_executive_translation_v1/`.
