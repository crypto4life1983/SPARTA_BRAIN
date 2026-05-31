# JARVIS Trading Executive Translation v1

**Date:** 2026-05-31
**Scope:** JARVIS read-only `/api/jarvis/ask` trading/strategy answer wording +
classifier vocabulary only. No new routes, no execution, no broker/paper/live
control, no order placement, no mutation, no refresh, no storage, no Strategy
Factory worktree or trading-file mutation.
**Verdict:** `JARVIS_TRADING_EXECUTIVE_READY`

---

## 1. Problem

Trading-status phrases still returned the legacy technical posture answer
(`read_only=true, paper_ready=false, live_ready=false, broker_control=false`) by
default — a step backward from the executive translation work. Affected:

- what is the trading status
- what's happening with trading
- trading update
- how is trading going
- what happened with trading / what happened in trading
- how are our strategies doing
- what is the status of the trading bot

## 2. Desired behavior

**Executive (default):**

> Trading remains in research mode. No live or paper trades have been executed.
> Several strategy candidates are currently under evaluation. The focus remains
> validation and research rather than deployment.

**Operator (on request):** still exposes `read_only=true`, `paper_ready=false`,
`live_ready=false`, `broker_control=false`, candidate counts, and exact detail.

## 3. Audit

| Area | Finding |
|------|---------|
| Classifier | Trading-status phrases already classified `SAFE_INFO`. Missing: strategy-status phrasings ("how are our strategies doing", "strategy status"). |
| Answer layer | `_jarvis_conversational_answer` had no executive trading branch; trading phrases fell through to `_jarvis_ask_answer` → `_jarvis_trading_posture_answer()` (raw flags). "what happened … trad" hit the last-24h recap branch, which also embedded the locked posture string. |
| Tests asserting default posture | `test_step38_trading_question_is_safe_and_reports_posture`, `test_step41_natural_trading_question_reports_posture`, `test_ci_trading_24h_is_readonly_and_no_fake_pnl`. |

## 4. What changed

Two files, both additive:

| File | Change |
|------|--------|
| `jarvis_conversation_safety.py` | Appended three `SAFE_INFO` patterns for natural strategy-status phrasing. Forbidden patterns still matched FIRST and unchanged. |
| `app.py` | Added `_exec_trading_phrase` / `_operator_trading_phrase` helpers and a mode-aware "Trading Executive Translation" branch in `_jarvis_conversational_answer` (placed before the last-24h recap branch). The recap branch was also made mode-aware. |

No template change: voice + conversation mode already POST to
`/api/jarvis/ask`, so they inherit the translation automatically.

## 5. Modes

| Mode | Trading-status answer |
|------|-----------------------|
| Executive (default) | "Trading remains in research mode. No live or paper trades have been executed. [candidate phrasing]. The focus remains validation and research rather than deployment." — no posture flags, no raw counts. |
| Operator (on request: "operator mode" / "show technical details" / "diagnostics" / "exact counts") | "Trading research status (operator detail): N research candidate(s) tracked. No live or paper trades were executed — trading is observation-only (read_only=true, paper_ready=false, live_ready=false, broker_control=false) …" |

The candidate sentence is fact-driven (says "No strategy candidates are
currently under evaluation" when the count is 0), so nothing is invented.

## 6. Safety guarantees preserved

- **Read-only.** Reads only the existing `api_jarvis_status` aggregate
  (`candidate_registry`, `trading_detail`). No command, backtest, broker call,
  order, refresh, or write.
- **No invented trades or performance.** Both modes state "no live or paper
  trades … no performance to report." Tests assert no
  profit/PnL/win-rate/"ready to trade"/"validated"/"approved" claims and no
  "strategy succeeded"/"winning strategy"/"profitable"/"fills" fabrication.
- **Executive hides posture; operator exposes it.** Tests assert executive
  answers contain none of the four posture flags; operator answers contain all
  four.
- **Forbidden trading still refuses.** "…then place a trade", "…and buy NQ",
  "…then enable live trading", "…and connect to my broker", "…then approve the
  strategy", "operator mode then sell ES" all refuse as FORBIDDEN_*.
- **No new endpoints / no storage.** Only `/api/jarvis/ask` and
  `/api/jarvis/status` exist under `/api/jarvis/`.
- **Status shape unchanged.** 28 keys; `paper_ready` / `live_ready` /
  `broker_control` stay `false`.

## 7. Tests

29 new tests added in `tests/test_jarvis_ask_contract.py`
(section "JARVIS Trading Executive Translation v1"):

- `test_tet_trading_status_is_executive_by_default` (×8)
- `test_tet_trading_status_invents_no_performance` (×8)
- `test_tet_operator_mode_exposes_posture` (×4)
- `test_tet_forbidden_trading_command_still_refuses` (×6)
- `test_tet_strategy_status_classifies_safe`
- `test_tet_keeps_trading_flags_locked_and_shape`
- `test_tet_adds_no_routes_and_writes_nothing`

Three pre-existing tests were reconciled (posture flags moved from the default
answer into an operator-mode companion assertion, same pattern as Executive
Translation Mode v1):

- `test_step38_trading_question_is_safe_and_reports_posture` →
  `test_step38_trading_question_is_safe_and_translated`
- `test_step41_natural_trading_question_reports_posture` →
  `test_step41_natural_trading_question_is_translated`
- `test_ci_trading_24h_is_readonly_and_no_fake_pnl` (assertions updated)

### Results

Run with the project venv from inside `tests/` with `PYTHONPATH=..` and
`--noconftest` (a pre-existing corrupt repo-root directory `hydra ` breaks
pytest root enumeration; environment artifact, unrelated to this change).

```
test_jarvis_route.py test_jarvis_conversation_safety.py   => 301 passed
test_jarvis_ask_contract.py                               => 250 passed
test_jarvis_factory_panels.py test_jarvis_snapshot_report.py => 31 passed
```

## 8. Validation

- `report.json` parses (JSON_OK).
- Executive trading/strategy questions hide posture flags, keep "no live or
  paper trades", use research framing, and invent no performance.
- Operator-mode requests expose the four posture flags + exact counts.
- Forbidden trading commands mixed into trading-status phrasing still refuse.
- Strategy-status phrasings classify SAFE.
- No new routes; no storage; status shape unchanged (28 keys); trading flags
  locked `false`.

## 9. Commit status

Not committed — awaiting approval per the bundle's commit policy.
