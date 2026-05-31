# JARVIS Operator Phrase Polish v1

**Date:** 2026-05-31
**Scope:** Operator-mode *detection* wording only, inside the existing read-only
`/api/jarvis/ask` answer layer. No new routes, no execution, no broker/paper/live
control, no order placement, no mutation, no storage, no classifier change, no
Strategy Factory worktree or trading-file mutation.
**Verdict:** `JARVIS_OPERATOR_PHRASE_READY`

---

## 1. Problem

Operator/technical mode was reachable only when the trigger phrase appeared
*after* the intent — e.g. "trading status operator mode", "workflow status
operator mode", "show technical details", "diagnostics". A front-loaded
"operator ..." phrasing did not trigger it:

> operator trading status
> operator workflow status

These returned the **executive** wording (no posture flags) because the
`_operator` flag only matched `"operator mode"`, not the bare word `operator`.

## 2. What changed

One file, additive (no behavior removed):

| File | Change |
|------|--------|
| `app.py` | Extended the `_operator` detection in `_jarvis_conversational_answer` with one extra OR clause: `"operator" in q and ("trading" in q or "workflow" in q or "pipeline" in q or "status" in q)`. |

Why this clause is safe for the executive default: a normal executive question
("what is the trading status", "trading update", the workflow-health phrase)
never contains the word **operator**, so it still routes to executive wording.
The clause only promotes to operator mode when the user explicitly says
"operator" alongside a trading/workflow/pipeline/status intent.

No classifier change: `jarvis_conversation_safety.py` is untouched, so forbidden
commands ("place a trade", "...then place a trade", "...and buy NQ") still match
FORBIDDEN first and refuse before the answer layer runs.

## 3. Behavior after the change

- `operator trading status` / `operator trading update` → **operator** trading
  read: "observation-only" + the four posture flags
  (`read_only=true, paper_ready=false, live_ready=false, broker_control=false`),
  no invented performance.
- `operator workflow status` / `operator pipeline status` → **operator** workflow
  read: "Workflow health (read-only, operator detail)" + the four posture flags
  + commander warnings/counts.
- `what is the trading status`, `trading update`, and the full workflow-health
  phrase → still **executive** (no posture flags, no "operator detail").
- `place a trade`, `operator trading status then place a trade`,
  `operator workflow status and buy NQ` → still **FORBIDDEN**, refused.

## 4. Safety guarantees preserved

- **Read-only.** Reads only the existing `api_jarvis_status` aggregate. No
  command, backtest, broker call, order, refresh, or write.
- **No new endpoints / no storage.** Only `/api/jarvis/ask` and
  `/api/jarvis/status` exist under `/api/jarvis/`. No file writes.
- **Forbidden still refuses.** Classifier unchanged; forbidden patterns match
  first. Sell/buy/place/enable/connect-broker/approve-strategy all still refuse.
- **No invented trades or performance.** Operator answers still state
  "observation-only" and "no live or paper trades were executed"; tests assert
  no profit/PnL/win-rate/"ready to trade"/"validated"/"approved" claims.
- **Executive default intact.** Normal questions (no "operator" word) keep
  executive wording with posture flags hidden.

## 5. Tests

10 new tests added in `tests/test_jarvis_ask_contract.py` (section "JARVIS
Operator Phrase Polish v1"):

- `test_op_operator_trading_status_exposes_posture` (×2) — "operator trading
  status", "operator trading update" expose all four posture flags.
- `test_op_operator_workflow_status_exposes_technical` (×2) — "operator workflow
  status", "operator pipeline status" return "workflow health … operator detail"
  + all four posture flags.
- `test_op_normal_questions_stay_executive` (×3) — "what is the trading status",
  "trading update", and the full workflow-health phrase hide the posture flags
  and never say "operator detail".
- `test_op_forbidden_command_still_refuses` (×3) — "place a trade", "operator
  trading status then place a trade", "operator workflow status and buy NQ" all
  refuse FORBIDDEN.

### Results

Run with the project venv from inside `tests/` with `PYTHONPATH=..` and
`--noconftest` (a pre-existing corrupt repo-root directory `hydra ` breaks
pytest root enumeration; environment artifact, unrelated to this change).

```
test_jarvis_ask_contract.py (op_ only)                       => 10 passed
test_jarvis_ask_contract.py (operator/executive regression)  => 108 passed
```

(Regression selector: `operator or executive or _et_ or _tet_ or _wh_ or _op_`
— covers every executive-translation, trading-executive, workflow-health, and
operator-phrase test. 0 failures, confirming the `_operator` change did not
regress any existing executive/operator behavior.)

## 6. Validation

- `report.json` parses (JSON_OK).
- Front-loaded "operator trading status" / "operator workflow status" now
  expose the four posture flags.
- Normal trading-status / workflow-health questions stay executive.
- Forbidden commands still refuse.
- No new routes; no storage; classifier unchanged.

## 7. Commit status

Not committed — awaiting approval per the bundle's commit policy.
