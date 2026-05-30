# JARVIS Step 38 — Read-Only Ask Answer-Quality Improvement

- **Generated:** 2026-05-30
- **Type:** backend answer-quality + classifier extension + tests + docs. No UI change, no endpoint, no storage, no trading control.
- **Live page:** http://127.0.0.1:8765/jarvis
- **Status API:** http://127.0.0.1:8765/api/jarvis/status
- **Ask API (Step 30):** `POST` http://127.0.0.1:8765/api/jarvis/ask

Step 38 improves the **answers** `/api/jarvis/ask` gives for common read-only
operator questions — especially **"how are we doing with trading?"** — so JARVIS
returns a useful **trading-posture summary** instead of generic safety text. The
handler still **executes nothing**: no commands, no trades, no refresh, no
writes, no storage. Trading answers are derived **only** from the existing
read-only `_jarvis_trading_detail` file scan.

---

## 1. Problem

"how are we doing with trading?" did not match any safe pattern and fell through
to **UNSUPPORTED (refused)**; the posture phrasing returned a generic read-only
shell string. Neither summarized the actual read-only posture the operator
wanted.

---

## 2. Files changed (allowed files only)

- **`jarvis_conversation_safety.py`** — extended `_SAFE_INFO` with read-only
  trading-status patterns: `how are we doing`, `ready for (paper|live) trading`,
  `(paper|live)_ready`, `broker_control`, `trading status`. These classify the
  questions as **SAFE_INFO** instead of fail-closing to UNSUPPORTED. The
  **forbidden** patterns are unchanged and still checked **first**, so no
  action-request (e.g. "enable paper trading", "connect broker") can leak
  through.
- **`app.py`** — added **`_jarvis_trading_posture_answer()`**, a read-only
  helper that reads the four posture fields from
  `_jarvis_safe(_jarvis_trading_detail)` and builds a direct summary. Any field
  not readable as a bool is reported conservatively as *"I cannot verify that
  field from the current read-only status."* Routed trading-status questions in
  the `SAFE_INFO` branch of `_jarvis_ask_answer` to this helper, replacing the
  old hardcoded `"posture"` string.
- **`tests/test_jarvis_ask_contract.py`** — added a Step 38 section.
- **`tests/test_jarvis_conversation_safety.py`** — added Step 38 classifier tests.
- **`docs/jarvis_step_38_ask_answer_quality/`** — this memo.

**Not done:** no `templates/jarvis.html` change; no new endpoint; no
refresh/execution/broker/paper/live control; no chat/audio/transcript storage;
no `localStorage`/`sessionStorage`/`IndexedDB`/cookies; no trade run or
simulated; no data fetched; no broker/live/paper logic touched; no
trading/Factory/S26-S28/Donchian/Hydra/base.html/storage file touched; no change
to the `{question}` payload shape or the `/api/jarvis/status` shape; no invented
performance/profit/readiness/validation claims.

---

## 3. Before / after — "how are we doing with trading?"

| | Answer |
| --- | --- |
| **Before** | UNSUPPORTED / generic shell: *"This is answerable from the read-only JARVIS status aggregate; it reports observed state only and authorizes no action."* (or refused fail-closed) |
| **After** | **SAFE_INFO**, `refused=false`: *"Trading is observation-only. read_only=true. paper_ready=false. live_ready=false. broker_control=false. This means JARVIS is not authorized to trade or control broker/paper/live systems."* · `sources_used=["trading_detail"]` |

---

## 4. Answer-quality summary

| Element | Detail |
| --- | --- |
| Posture answer | *"Trading is observation-only. read_only=true. paper_ready=false. live_ready=false. broker_control=false. This means JARVIS is not authorized to trade or control broker/paper/live systems."* |
| Source of truth | `_jarvis_safe(_jarvis_trading_detail)` — read-only file scan; never runs/fetches/trades/writes. |
| Fields reported | `read_only`, `paper_ready`, `live_ready`, `broker_control`. |
| Missing field | Reported as *"I cannot verify that field from the current read-only status."* — never guessed. |
| Style | Direct, useful, conservative; no hype, no trading advice, no permission language. |
| Sources | `["trading_detail"]`. |
| Other answers | "why is commander yellow?" / "what needs attention?" / "what does read_only mean?" / "what JARVIS docs exist?" answer as before. |

---

## 5. Safety / refusal confirmation (all still refused)

| Question | Class |
| --- | --- |
| place a trade on NQ | FORBIDDEN_TRADING |
| buy NQ | FORBIDDEN_TRADING |
| sell ES | FORBIDDEN_TRADING |
| go long | FORBIDDEN_TRADING |
| enable paper trading | FORBIDDEN_TRADING |
| enable live trading | FORBIDDEN_TRADING |
| connect broker | FORBIDDEN_TRADING |
| approve strategy | FORBIDDEN_TRADING |
| run script | FORBIDDEN_EXECUTION |
| refresh status | FORBIDDEN_EXECUTION |
| modify file | FORBIDDEN_MUTATION |
| explain the trading posture then place a trade | FORBIDDEN_TRADING (forbidden override) |

The `/api/jarvis/ask` response keeps **exactly** its five fields
(`answer`, `safety_class`, `sources_used`, `refused`, `refusal_reason`) — **no**
`command`/`action`/`execution`/`order`/`trade_ticket`/`mutation`/`side_effect`.

---

## 6. Status shape confirmation

- **24** top-level keys (unchanged); `online=true`, `read_only=true`.
- `trading_detail` flags: `read_only=true`, `paper_ready=false`,
  `live_ready=false`, `broker_control=false`.
- No forbidden keys present.

---

## 7. Tests & validation

- `python -m py_compile app.py jarvis_conversation_safety.py` → **PYCOMPILE_OK**
- `pytest tests/test_jarvis_route.py tests/test_jarvis_conversation_safety.py
  tests/test_jarvis_ask_contract.py --rootdir=tests -q` →
  **269 passed, 0 failed, 0 skipped** (was 239; +30 Step 38 tests)
- `python -m json.tool docs/jarvis_step_38_ask_answer_quality/report.json` → **JSON_OK**
- `git diff --name-only` → only `app.py`, `jarvis_conversation_safety.py`,
  `tests/test_jarvis_ask_contract.py`, `tests/test_jarvis_conversation_safety.py`
  (`templates/jarvis.html` and `tests/test_jarvis_route.py` unchanged); nothing staged.

---

## 8. Conclusion

JARVIS now answers common read-only operator trading-status questions with a
direct, data-derived posture summary sourced only from the existing read-only
`_jarvis_trading_detail` scan, instead of generic safety text. The classifier
was extended so "how are we doing with trading?" and "are we ready for
paper/live trading?" classify **SAFE_INFO**, while every forbidden
action-request stays **refused** because forbidden is checked first. The ask
response keeps its five fields with no command/action/order keys, the status
shape is unchanged at 24 keys with trading flags locked false, the UI/template
are untouched (still `{question}` only), and no endpoint/refresh/execution/
storage/trading control was added. **269 tests pass.** Nothing staged or
committed.
