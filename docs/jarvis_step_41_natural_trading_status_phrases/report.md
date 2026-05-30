# JARVIS Step 41 — Natural Trading-Status Phrase Coverage

- **Generated:** 2026-05-30
- **Type:** classifier + route answer-quality + tests + docs. No UI change, no endpoint, no storage, no trading control.
- **Ask API:** `POST` http://127.0.0.1:8765/api/jarvis/ask

Step 41 makes casual, natural trading-status questions — e.g. **"how is the
trading doing?"** — classify as read-only **SAFE_INFO** and answer with the
observation-only trading posture, instead of being refused as **UNSUPPORTED**.
Every safety/refusal behavior is preserved: forbidden intent is matched **first**
and overrides any safe wording.

---

## 1. Observed issue

In the live dashboard, *"how is the trading doing?"* returned **REFUSED ·
UNSUPPORTED**. It is a safe read-only status question and should answer like the
existing *"how are we doing with trading?"* path.

---

## 2. Files changed (allowed files only)

- **`jarvis_conversation_safety.py`** — added **3** read-only `_SAFE_INFO`
  patterns covering natural phrasings: `trad(e|es|ing)` co-occurring with
  `status|update|overview|doing|going` (both orders), and `with
  trad(e|es|ing)`. Patterns are **apostrophe-independent** (work for "how's" /
  "what's", straight or curly). Forbidden patterns are unchanged and still
  checked **first**.
- **`app.py`** — added `"trades"` to the SAFE_INFO trading-routing condition in
  `_jarvis_ask_answer` so *"how are trades doing?"* (no "trading" substring)
  reaches `_jarvis_trading_posture_answer()`. The posture answer and its
  read-only source are otherwise unchanged from Step 38.
- **`tests/test_jarvis_conversation_safety.py`** — Step 41 classifier tests.
- **`tests/test_jarvis_ask_contract.py`** — Step 41 ask-endpoint tests.
- **`docs/jarvis_step_41_natural_trading_status_phrases/`** — this memo.

**Not done:** no `templates/jarvis.html` change; no new endpoint; no
refresh/execution/broker/paper/live control; no storage; no trade run/simulated;
no data fetched; no broker/live/paper logic touched; no
trading/Factory/S26-S28/Donchian/Hydra/base.html/storage file touched; no change
to the `{question}` payload or `/api/jarvis/status` shape; no invented
performance/profit/readiness/validation claims.

---

## 3. Before / after — "how is the trading doing?"

| | Answer |
| --- | --- |
| **Before** | **REFUSED / UNSUPPORTED** (no safe pattern matched; fail-closed) |
| **After** | **SAFE_INFO**, `refused=false`: *"Trading is observation-only. read_only=true. paper_ready=false. live_ready=false. broker_control=false. This means JARVIS is not authorized to trade or control broker/paper/live systems."* · `sources_used=["trading_detail"]` |

---

## 4. Phrase coverage (all now SAFE_INFO, `refused=false`)

`how is the trading doing` · `how's the trading doing` · `how is trading doing` ·
`how are trades doing` · `how is our trading doing` · `how is the trading bot
doing` · `how is the trading system doing` · `how is paper trading doing` · `how
is live trading doing` · `what's going on with trading` · `give me trading
status` · `tell me trading status` · `trading update` · `trading overview` · `are
we doing good with trading` · `are we okay with trading`.

*Apostrophe note:* both straight (`how's`) and curly (`how’s`) variants classify
SAFE_INFO — the patterns do not depend on the apostrophe.

---

## 5. Safety / refusal confirmation (mixed forbidden still refused)

| Question | Class |
| --- | --- |
| how is trading doing then place a trade | FORBIDDEN_TRADING |
| trading update and buy NQ | FORBIDDEN_TRADING |
| tell me trading status and enable live trading | FORBIDDEN_TRADING |
| how is the bot doing and connect broker | FORBIDDEN_TRADING |
| trading overview then run script | FORBIDDEN_EXECUTION |
| are we okay with trading then approve strategy | FORBIDDEN_TRADING |

The `/api/jarvis/ask` response keeps **exactly** its five fields
(`answer`, `safety_class`, `sources_used`, `refused`, `refusal_reason`) — **no**
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
  **319 passed, 0 failed, 0 skipped** (was 269; +50 parametrized cases)
- `python -m json.tool docs/jarvis_step_41_natural_trading_status_phrases/report.json` → **JSON_OK**
- `git diff --name-only` → only `app.py`, `jarvis_conversation_safety.py`,
  `tests/test_jarvis_ask_contract.py`, `tests/test_jarvis_conversation_safety.py`
  (`templates/jarvis.html` and `tests/test_jarvis_route.py` unchanged); nothing staged.

---

## 8. Conclusion

JARVIS now recognizes natural, casual trading-status phrasings as read-only
SAFE_INFO questions and answers them with the observation-only posture, sourced
only from the existing read-only `trading_detail` scan. The fix is a 3-pattern
classifier extension plus a one-keyword (`trades`) routing addition in the
existing Step 38 answer path — no new endpoint, UI, storage, refresh, execution,
or trading control. Forbidden intent still overrides safe wording (forbidden is
checked first), so mixed phrases like *"trading update and buy NQ"* stay refused.
The ask response keeps its five fields with no command/action/order keys, and the
`/api/jarvis/status` shape is unchanged at 24 keys with trading flags locked
false. **319 tests pass.** Nothing staged or committed.
