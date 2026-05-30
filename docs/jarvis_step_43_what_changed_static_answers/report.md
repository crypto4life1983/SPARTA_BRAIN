# JARVIS Step 43 — "What Changed?" Safe Classifier Coverage + Static Answers

- **Generated:** 2026-05-30
- **Type:** classifier + route answer-quality + tests + docs. No UI change, no
  endpoint, no storage, no snapshot, no log, no refresh, no execution, no
  trading control.
- **Ask API:** `POST` http://127.0.0.1:8765/api/jarvis/ask

Step 43 makes safe operator "what changed?" questions — e.g. **"what changed
since last check?"** — classify as read-only **SAFE_INFO** and answer
**conservatively from current status only**. JARVIS keeps **no stored
snapshot/baseline**, so it explicitly says it cannot compare against a previous
check yet and claims **no verified changes**. Every safety/refusal behavior is
preserved: forbidden intent is matched **first** and overrides any safe wording.
This implements the Step 42 plan's Option A + B starting point with **no
persistence**.

---

## 1. Purpose and relation to Step 42 plan

Step 42 (`a1ac1a6`, `JARVIS_CHANGE_SUMMARY_PLAN_READY`) designed a future
read-only change-summary capability. Step 43 implements the first, safest slice:
recognize safe "what changed?" phrasings and answer with a **current-status
summary only** (Option A). Baseline comparison (Option B, operator-supplied) and
any snapshot storage (Options C/D) remain **deferred** — JARVIS never claims a
change without a provided baseline.

---

## 2. Files changed (allowed files only)

- **`jarvis_conversation_safety.py`** —
  - Added **6** read-only `_SAFE_INFO` patterns for change-summary intent:
    `\bchanged\b`, `\bchange\s+summary\b`, `\bwhat'?s\s+new\b`,
    `\bwhat\s+is\s+new\b`, `\bwhat\s+new\b`,
    `\bsummar(?:ize|ise)\s+(?:current\s+)?changes\b`.
  - Added **6** forbidden patterns so mixed action requests still refuse
    (forbidden is checked first): TRADING `\bstart\s+trading\b`; EXECUTION
    `\brun\s+git\b` and `report|generator` inside the `execute` clause; MUTATION
    `\bwrite\b.*\bsnapshot\b`, `\bsave\b.*\b(?:state|snapshot)\b`,
    `\bclean\b.*\b(?:untracked|tree|files?)\b`.
- **`app.py`** —
  - Added `_jarvis_what_changed_answer()` — READ-ONLY. Summarizes the **current**
    status from the same helpers the status endpoint already uses (`_jarvis_git`,
    `_jarvis_trading_detail`, `_jarvis_cache_freshness`, and the derived
    `_jarvis_commander_snapshot`). It runs no git/refresh/execution, fetches
    nothing, writes nothing, stores no snapshot, and never claims a verified
    change. Returns `(answer, sources_used)`.
  - Routed change-summary questions to it in `_jarvis_ask_answer`, **before** the
    trading branch, so "what new trading reports appeared" is answered as a
    change summary rather than a posture answer.
- **`tests/test_jarvis_conversation_safety.py`** — Step 43 classifier tests.
- **`tests/test_jarvis_ask_contract.py`** — Step 43 ask-endpoint tests.
- **`docs/jarvis_step_43_what_changed_static_answers/`** — this memo.

**Not done:** no `templates/jarvis.html` change; no new endpoint; no snapshot
storage; no server-side log; no browser write; no refresh/execution/broker/paper/
live control; no data fetched; no trade run/simulated; no
trading/Factory/S26-S28/Donchian/Hydra/base.html/storage file touched; the dirty
Crypto-D8 report files were **not** touched; no change to the `{question}`
payload or `/api/jarvis/status` shape; no invented performance/profit/readiness/
validation claims.

---

## 3. "What changed?" phrase coverage (all now SAFE_INFO, `refused=false`)

`what changed since last check` · `what changed since yesterday` · `what changed
today` · `what is new` · `what new commits happened` · `what new trading reports
appeared` · `what warnings changed` · `what needs attention now` · `what changed
in JARVIS` · `summarize current changes` · `give me a change summary` · `what
changed since I last checked`.

---

## 4. Example answer — "what changed since last check?"

`refused=false`, `safety_class=SAFE_INFO`,
`sources_used=["git","trading_detail","cache_freshness","commander_snapshot"]`:

> I cannot compare against a previous snapshot yet — JARVIS stores no baseline,
> so I am reporting current read-only status only and claiming no changes.
> **Verified current status:** current HEAD is `<short>` on branch master; latest
> commit subject: "…"; working tree is dirty (N modified, M untracked); most
> recent trading reports on disk: …; cache freshness overall: fresh; commander
> snapshot state: yellow; current warning count: N. **Unknown because no previous
> baseline is available:** I keep no stored snapshot, so I cannot say what changed
> since a previous check, what is new, or which warnings changed compared to
> before. Provide a previous snapshot to compare against, or treat the above as
> current state only.

The answer **separates** "Verified current status" from "Unknown because no
previous baseline is available", never asserts a change, and invents no
performance/readiness claims.

---

## 5. Safety / refusal confirmation (mixed forbidden still refused)

| Question | Class |
| --- | --- |
| what changed and refresh status | FORBIDDEN_EXECUTION |
| what changed and run git log | FORBIDDEN_EXECUTION |
| what changed and write a snapshot | FORBIDDEN_MUTATION |
| what changed and save this state | FORBIDDEN_MUTATION |
| what changed and execute report generator | FORBIDDEN_EXECUTION |
| what changed and clean untracked files | FORBIDDEN_MUTATION |
| what changed and start trading | FORBIDDEN_TRADING |
| summarize changes then place a trade | FORBIDDEN_TRADING |
| what new reports appeared then approve strategy | FORBIDDEN_TRADING |

The `/api/jarvis/ask` response keeps **exactly** its five fields (`answer`,
`safety_class`, `sources_used`, `refused`, `refusal_reason`) — **no**
`command`/`action`/`execution`/`order`/`trade_ticket`/`mutation`/`side_effect`.

---

## 6. Status shape confirmation

- **24** top-level keys (unchanged); `online=true`, `read_only=true`.
- `trading_detail` flags: `read_only=true`, `paper_ready=false`,
  `live_ready=false`, `broker_control=false`.

---

## 7. Tests & validation

- `python -m py_compile app.py jarvis_conversation_safety.py` → **PYCOMPILE_OK**
- `pytest tests/test_jarvis_route.py tests/test_jarvis_conversation_safety.py
  tests/test_jarvis_ask_contract.py --rootdir=tests -q` →
  **362 passed, 0 failed, 0 skipped** (was 319; +43 cases)
- `python -m json.tool docs/jarvis_step_43_what_changed_static_answers/report.json`
  → **JSON_OK**
- `git diff --name-only` → only `app.py`, `jarvis_conversation_safety.py`,
  `tests/test_jarvis_ask_contract.py`, `tests/test_jarvis_conversation_safety.py`
  (`templates/jarvis.html` and `tests/test_jarvis_route.py` unchanged); nothing
  staged. The Crypto-D8 report files were not touched.

---

## 8. Conclusion

JARVIS now recognizes safe "what changed?" operator questions as read-only
SAFE_INFO and answers them with a **conservative current-status summary** that
explicitly states it cannot compare against a previous baseline and claims no
verified changes — exactly the Step 42 Option A starting point, with **no
persistence, no snapshot, no storage, no log, no refresh, no execution**, and no
trading control. Forbidden intent still overrides safe wording (forbidden is
checked first), so mixed phrases like "what changed and refresh status" or
"summarize changes then place a trade" stay refused. The ask response keeps its
five fields with no command/action/order keys, and the `/api/jarvis/status`
shape is unchanged at 24 keys with trading flags locked false. **362 tests
pass.** Nothing staged or committed.
