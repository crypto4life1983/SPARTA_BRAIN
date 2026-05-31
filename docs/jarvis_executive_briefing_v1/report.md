# JARVIS Executive Briefing Mode v1

**Date:** 2026-05-31
**Scope:** JARVIS read-only `/api/jarvis/ask` answer quality + classifier
vocabulary only. No new routes, no execution, no broker/paper/live control, no
order placement, no mutation, no refresh, no storage of chat/audio/transcripts,
no Strategy Factory worktree or trading-file mutation.
**Verdict:** `JARVIS_EXECUTIVE_BRIEFING_READY`

---

## 1. Goal

Turn JARVIS from a status responder into an executive assistant. Instead of
"Commander snapshot is yellow," a morning/overnight question now returns a
structured read-only briefing:

> Good morning Mahmoud. Here is your executive briefing. SPARTA Brain is online
> … Strategy Factory remains in research mode … No live or paper trades were
> executed … warning(s) need review … Recommended next action: …

— while preserving every read-only / trading-safety rule.

## 2. What changed

Two files, both additive:

| File | Change |
|------|--------|
| `jarvis_conversation_safety.py` | Added SAFE_INFO regex patterns for executive-briefing intents and follow-ups: `overnight`, `executive summary`, `summarize/summarise the system`, `tell me more`, `next step`, `what should we focus`, `what to focus`, `focus on today/now/next`. Forbidden patterns are still matched FIRST and unchanged. |
| `app.py` | Rebuilt the briefing branch of `_jarvis_conversational_answer` into a structured executive briefing, added "what needs attention" and "next step / focus" follow-ups, and taught the `SAFE_EXPLAIN` branch to explain the actual open commander warnings. All read-only, from the existing `api_jarvis_status` aggregate. |

No template change: voice + conversation mode already POST to
`/api/jarvis/ask`, so they inherit the new briefing automatically.

## 3. Briefing structure (all read-only)

```
Greeting            -> "Good morning Mahmoud."
System health       -> system_core + commander_snapshot (state, headline, warning count)
Strategy Factory    -> factory_status: report_count + most-recent decision (dry-run / research only)
Trading research    -> candidate_registry candidate_count + "No live or paper trades were executed"
Warnings/attention  -> commander_snapshot.warnings (count + top items)
Recommended action  -> recommended_next_actions[0]
```

### Supported intents

| Intent | Example | Answer |
|--------|---------|--------|
| Executive briefing | "good morning", "morning briefing", "what happened overnight", "overnight update", "executive summary", "summarize the system", "tell me more" | full structured briefing |
| What needs attention | "what needs attention", "anything that needs attention?" | warning list + recommended next action |
| Next step / focus | "what is the next step", "what should we focus on today", "what to focus on next" | recommended focus (read-only guidance) |
| Explain the warning | "explain the warning" | read-only explanation of the actual open commander warnings |

Existing answers (greeting for hi/hello/good evening, "how are you", trading
24h recap, Strategy Factory status, SPARTA Brain status, "what changed?",
trading posture, docs) are unchanged — the layer returns those exactly as
before, and "what warnings changed?" / "what new commits happened?" still reach
the Step 43/47 change-summary handler.

## 4. Safety guarantees preserved

- **Read-only.** Briefing reads only `api_jarvis_status` (the existing
  read-only aggregate). It runs no command, no backtest, no broker call; places
  no order; triggers no refresh; writes nothing.
- **No invented trades or performance.** The briefing explicitly says "No live
  or paper trades were executed … so there is no realized performance to
  report" and reports the locked posture
  (`read_only=true, paper_ready=false, live_ready=false, broker_control=false`).
  Tests assert no profit/PnL/win-rate/"ready to trade"/"validated"/"approved"
  claims appear.
- **Missing data → say so.** Factory/candidate answers degrade to "status not
  available" rather than inventing values.
- **Classifier still gates everything.** Forbidden-first ordering is unchanged:
  "good morning then buy NQ", "executive summary then run the smoke script",
  "summarize the system and commit the changes", "what needs attention then go
  long" all still refuse as FORBIDDEN_*.
- **No new endpoints / no refresh / no snapshot route.** Only
  `/api/jarvis/ask` and `/api/jarvis/status` exist under `/api/jarvis/`.
- **Status shape unchanged.** `/api/jarvis/status` still has exactly 28 keys;
  `paper_ready` / `live_ready` / `broker_control` stay `false`.
- **No storage.** The briefing writes no data files and no
  chat/audio/transcript logs (asserted by filesystem-diff tests).

## 5. Tests

33 new tests added in `tests/test_jarvis_ask_contract.py`
(section "JARVIS Executive Briefing Mode v1"):

- `test_eb_briefing_is_executive_structure` (×10)
- `test_eb_greeting_good_morning_becomes_briefing`
- `test_eb_overnight_update_is_readonly_no_fake_trades` (×2)
- `test_eb_briefing_keeps_trading_flags_locked`
- `test_eb_attention_lists_warnings_readonly` (×3)
- `test_eb_followups_recommend_next_action` (×3)
- `test_eb_explain_warning_is_readonly_explanation`
- `test_eb_forbidden_intent_in_briefing_still_refused` (×9)
- `test_eb_no_new_routes_or_execution_added`
- `test_eb_briefing_writes_no_files_or_chat_logs`
- `test_eb_briefing_does_not_change_status_shape`

### Results

Run with the project venv (`.venv`). Note: a pre-existing corrupt directory in
the repo root (on-disk name `hydra ` — a private-use char + trailing space)
breaks pytest's root enumeration, so the suite is run from inside `tests/` with
`PYTHONPATH=..` and `--noconftest`. Environment artifact, unrelated to this
change.

```
PYTHONPATH=.. .venv/Scripts/python -m pytest \
  test_jarvis_route.py test_jarvis_conversation_safety.py \
  --noconftest -q -p no:cacheprovider
=> 301 passed

PYTHONPATH=.. .venv/Scripts/python -m pytest \
  test_jarvis_factory_panels.py test_jarvis_ask_contract.py \
  test_jarvis_snapshot_report.py --noconftest -q -p no:cacheprovider
=> 201 passed   (was 168; +33 executive-briefing tests)
```

## 6. Validation

- `report.json` parses (JSON_OK).
- `good morning` / `morning briefing` / `overnight update` / `executive
  summary` / `summarize the system` / `tell me more` answer `refused=false`,
  `SAFE_INFO`, with the full executive structure.
- Overnight update is read-only with no fake trades or performance.
- Forbidden phrases mixed into a briefing still refused (FORBIDDEN_*).
- No new routes; `/api/jarvis/` exposes only `ask` and `status`.
- `/api/jarvis/status` shape unchanged (28 keys); trading flags locked false.

## 7. Commit status

Not committed — awaiting approval per the bundle's commit policy. `git status`:
`app.py` and `jarvis_conversation_safety.py` modified;
`tests/test_jarvis_ask_contract.py` modified; report files added under
`docs/jarvis_executive_briefing_v1/`.
