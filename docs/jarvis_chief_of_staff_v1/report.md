# JARVIS Chief of Staff Mode v1

**Date:** 2026-05-31
**Scope:** JARVIS read-only `/api/jarvis/ask` answer wording + classifier
vocabulary only. No new routes, no execution, no broker/paper/live control, no
order placement, no mutation, no refresh, no storage of chat/audio/transcripts,
no Strategy Factory worktree or trading-file mutation.
**Verdict:** `JARVIS_CHIEF_OF_STAFF_READY`

---

## 1. Goal

Upgrade JARVIS from a plain executive briefing to **Chief-of-Staff quality**:
contextual, strategic, product-demo-ready, and able to recommend what matters
next — while staying strictly read-only and inventing no trades or performance.
JARVIS should sound like it understands Mahmoud, SPARTA Brain, the current
priorities, and the project journey.

The classifier still gates every question, forbidden intents still refuse first,
and all chief-of-staff recommendations are **advice only** — they authorize no
action and execute nothing.

## 2. What changed

Two files, both additive:

| File | Change |
|------|--------|
| `jarvis_conversation_safety.py` | Appended SAFE_INFO regex patterns for strategic + product-demo intents at the END of the `_SAFE_INFO` tuple. Forbidden patterns are still matched FIRST and unchanged. `\bsell\b` was **not** weakened. |
| `app.py` | Added module-level `_jarvis_chief_of_staff_answer(q)` and wired it at the top of both the `SAFE_EXPLAIN` branch of `_jarvis_ask_answer` and `_jarvis_conversational_answer`. |

No template change: voice + conversation mode already POST to
`/api/jarvis/ask`, so they inherit chief-of-staff answers automatically.

## 3. Answer styles

### Strategic chief-of-staff read

Triggered by: *what should we work on today / what is the smartest next move /
what is the priority / give me the big picture / explain where we are / why does
this matter / what should I tell someone about SPARTA Brain / are we ready to
demo*.

Structure (always read-only, framed "advice only"):

```
Current situation   -> online; commander snapshot <state> with N item(s) flagged;
                       all trading observation-only, no performance to report
What changed recently -> latest committed research checkpoint, or
                         "no recent change is confirmed from read-only state"
Why it matters      -> nothing moves toward paper/live until validation passes
Recommended focus   -> recommended_next_actions[0]
What not to do      -> do not enable paper/live, do not treat candidates as proven,
                       do not skip the validation gate
One clear next action -> recommended_next_actions[0]
```

### Product-demo overview

Triggered by a description frame (*what is / describe / pitch / tell / explain /
overview of*) on a known subject (*SPARTA Brain / JARVIS / Strategy Factory /
the system / the product / the platform*) **when it is not a status query**:

> SPARTA Brain is an **AI command center** — a local dashboard that brings the
> whole operation into one place. JARVIS is its **voice interface and chief of
> staff**. The **Strategy Factory** is the research engine that produces and
> reviews strategy candidates. **Trading stays research-only until validation
> passes** — no live or paper trades were executed, and the system places no
> orders.

## 4. Safety guarantees preserved

- **Read-only.** Reads only the existing `api_jarvis_status` aggregate. Runs no
  command, no backtest, no broker call; places no order; triggers no refresh;
  writes nothing.
- **No invented trades or performance.** Both styles state "no live or paper
  trades were executed … no performance to report." Tests assert no
  profit/PnL/win-rate/"ready to trade"/"validated"/"approved" claims appear.
- **Unknown stays unknown.** When factory state isn't `ready` or no committed
  decision exists, the "what changed recently" line says so instead of
  inventing a change.
- **Recommendations are advice only.** Every strategic answer states it
  "authorizes no action and executes nothing."
- **`sell` still refuses.** `\bsell\b` is unchanged FORBIDDEN_TRADING — "are we
  ready to sell" deliberately refuses. Product-readiness uses "ready to
  demo/ship/launch/pitch."
- **Forbidden-first ordering unchanged.** "…then buy NQ", "…then place a
  trade", "…then enable live trading", "…and connect to my broker", "…then run
  the smoke script", "…then commit the changes" all still refuse as
  FORBIDDEN_*.
- **Operator mode still works.** "operator mode" still returns the full
  technical briefing with exact counts and posture flags.
- **No new endpoints / no storage.** Only `/api/jarvis/ask` and
  `/api/jarvis/status` exist under `/api/jarvis/`.
- **Status shape unchanged.** `/api/jarvis/status` still has exactly 28 keys;
  `paper_ready` / `live_ready` / `broker_control` stay `false`.

## 5. Tests

26 new tests added in `tests/test_jarvis_ask_contract.py`
(section "JARVIS Chief of Staff Mode v1"):

- `test_cos_strategic_answer_is_structured_and_readonly` (×7)
- `test_cos_recommendation_is_advice_not_command` (×3)
- `test_cos_demo_overview_describes_product_readonly` (×4)
- `test_cos_unknown_data_is_not_invented`
- `test_cos_forbidden_intent_still_refused` (×6)
- `test_cos_sell_stays_forbidden_trading` (×2)
- `test_cos_operator_mode_still_works`
- `test_cos_adds_no_routes_and_writes_nothing`
- `test_cos_does_not_change_status_shape`

### Results

Run with the project venv (`.venv`) from inside `tests/` with `PYTHONPATH=..`
and `--noconftest` (a pre-existing corrupt repo-root directory, on-disk name
`hydra ` — a private-use char + trailing space — breaks pytest's root
enumeration; environment artifact, unrelated to this change).

```
COS + regression subset (test_jarvis_ask_contract.py -k "cos_ or et_ or eb_ or ci_")
=> 119 passed, 102 deselected
```

(Full route+safety and factory/ask/snapshot suite results recorded in
`report.json`.)

## 6. Commit status

Not committed — awaiting approval per the bundle's commit policy.
