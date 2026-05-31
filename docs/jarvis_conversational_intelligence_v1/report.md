# JARVIS Conversational Intelligence v1

**Date:** 2026-05-31
**Scope:** JARVIS read-only `/api/jarvis/ask` answer quality + classifier
vocabulary only. No new routes, no execution, no broker/paper/live control, no
order placement, no mutation, no refresh, no storage of chat/audio/transcripts,
no Strategy Factory worktree or trading-file mutation.
**Verdict:** `JARVIS_CONVERSATIONAL_INTELLIGENCE_READY`

---

## 1. Goal

Upgrade JARVIS from terse, robotic status/refusal answers into a useful
read-only conversational assistant that handles natural questions —
greetings, "how are you", a morning briefing, a last-24h trading recap, SPARTA
Brain status, Strategy Factory status, and "what needs attention" — while
preserving every read-only / trading-safety rule.

## 2. What changed

Two files, both additive:

| File | Change |
|------|--------|
| `jarvis_conversation_safety.py` | Added SAFE_INFO regex patterns so natural conversational phrasings classify as read-only (greetings, "how are you", "brief(ing)", "strategy factory / factory status", "sparta brain / brain status", "what happened", "last/past 24h", "our/my trades"). Forbidden patterns are still matched FIRST and unchanged. |
| `app.py` | Added `_jarvis_conversational_answer(q)` — a read-only natural-language answer layer — and wired it as the first branch of the SAFE_INFO path in `_jarvis_ask_answer`. It reads only the already-aggregated read-only status (`api_jarvis_status`) and the committed report summaries that status already exposes. |

No template change was needed: voice conversation mode already posts the
spoken question to the same `POST /api/jarvis/ask` endpoint, so it inherits the
improved answers and the unchanged classifier gate automatically.

## 3. Supported natural intents (all read-only, SAFE_INFO)

| Intent | Example | Answer source |
|--------|---------|---------------|
| Greeting | "hi", "hello", "good morning" | commander_snapshot, trading_detail |
| How are you | "how are you?", "how's it going?" | commander_snapshot, trading_detail |
| Morning briefing | "brief me", "morning briefing" | commander_snapshot, trading_detail, factory_status, daily_mission |
| Trading 24h recap | "what happened in trading last 24 hours?", "what happened with our trades?" | trading_detail |
| Strategy Factory status | "what is the Strategy Factory status?", "factory status" | factory_status |
| SPARTA Brain status | "what is SPARTA Brain status?", "brain status" | system_core, ai_brains, commander_snapshot |
| General system status | "what is the current system status?" | system_core, commander_snapshot, trading_detail |

The existing structured answers (commander-yellow, trading posture, "what
changed?", docs, attention) are untouched: the conversational layer returns
`None` for anything it does not specifically recognise, so the question falls
through to the prior logic. This is why every Step 28/38/41/43/47 test still
passes unchanged.

## 4. Safety guarantees preserved

- **Read-only.** Answers come only from `api_jarvis_status` (the existing
  read-only aggregate) and the committed report summaries it already exposes.
  The layer runs no command, no backtest, no broker call; places no order;
  triggers no refresh; writes nothing.
- **No invented performance.** The trading recap explicitly states "no live or
  paper trades have been placed … so there are no fills and no realized
  performance to report" and reports the locked posture
  (`read_only=true, paper_ready=false, live_ready=false, broker_control=false`).
  Tests assert the answers never contain profit/PnL/win-rate/"ready to
  trade"/"validated"/"approved" claims.
- **Missing data → say so.** Factory/brain answers degrade to "status not
  available" rather than inventing values.
- **Classifier still gates everything.** Forbidden-first ordering is unchanged:
  a forbidden action mixed into any natural phrasing ("good morning then buy
  NQ", "brief me then place a trade", "sparta brain status and run the smoke
  script") is still refused as FORBIDDEN_*.
- **No new endpoints / no refresh / no snapshot route.** Only
  `/api/jarvis/ask` and `/api/jarvis/status` exist under `/api/jarvis/`.
- **Status shape unchanged.** `/api/jarvis/status` still has exactly 28 keys;
  `paper_ready` / `live_ready` / `broker_control` stay `false`.
- **No storage.** Conversation writes no data files and no chat/audio/transcript
  logs (asserted by filesystem-diff tests).

## 5. Tests

34 new tests added in `tests/test_jarvis_ask_contract.py`
(section "JARVIS Conversational Intelligence v1"):

- `test_ci_greetings_return_natural_response` (×5)
- `test_ci_how_are_you_is_natural_status` (×3)
- `test_ci_morning_briefing_summarizes_readonly` (×3)
- `test_ci_trading_24h_is_readonly_and_no_fake_pnl` (×4)
- `test_ci_trading_24h_keeps_broker_paper_live_locked`
- `test_ci_factory_status_summarizes_dry_run` (×3)
- `test_ci_sparta_brain_status_summarizes_system` (×3)
- `test_ci_forbidden_intent_in_conversation_still_refused` (×8)
- `test_ci_no_new_routes_or_execution_added`
- `test_ci_conversation_writes_no_files_or_chat_logs`
- `test_ci_conversation_does_not_change_status_shape`
- `test_ci_voice_conversation_mode_uses_same_ask_endpoint`

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
=> 168 passed   (was 134; +34 conversational-intelligence tests)
```

## 6. Validation

- `/jarvis` returns HTTP 200.
- `/api/jarvis/status` returns HTTP 200, 28 keys, `read_only=true`.
- `GET /api/jarvis/ask` returns 405 (POST-only, unchanged).
- `/api/jarvis/ask` answers natural questions (greeting / briefing / factory /
  brain / trading-24h / "how are you") with `refused=false`, `SAFE_INFO`.
- Forbidden phrases (and forbidden mixed into natural phrasings) still refused.
- Voice conversation mode unchanged — still posts to the same ask endpoint.
- `report.json` parses (JSON_OK).

## 7. Commit status

Not committed — awaiting approval per the bundle's commit policy. `git status`:
`app.py` and `jarvis_conversation_safety.py` modified; report files added under
`docs/jarvis_conversational_intelligence_v1/`.
