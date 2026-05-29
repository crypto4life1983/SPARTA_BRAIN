# SPARTA Agentic Backtest Factory

A local, offline, research-only module that runs a TraderDev-style strategy loop:

```
AI proposes strategy  ->  local offline backtest  ->  metrics  ->  report  ->  decision (continue / park / kill)
```

First and only strategy target: **NQ ORB** (Nasdaq Opening Range Breakout).

This module is **inert**. It produces reports. It never trades, never connects, never
touches anything outside its own folder.

---

## HARD SAFETY RULES (non-negotiable)

1. **Research-only, local-only, offline-only.** No network calls of any kind.
2. **Never** connect to a broker, Bybit, Binance, any exchange API, or the Databento API.
3. **Never** read `local_secrets/`, `.env`, API keys, or any credential file.
4. **Never** modify `C:\Users\mahmo\obsidian-trade-logger`.
5. **Never** modify live trading files, scheduler files, `review_queue` files, broker files,
   or existing strategy-bot files.
6. **All writes are confined to** `C:\SPARTA_BRAIN\trading_research\agentic_factory\`.
   No file is created or edited outside this folder.
7. **Input data only** from `data_offline\` — CSVs you place there manually.
   No fetching, no API caching, no downloads.
8. **No order placement.** No signals are emitted to any live or paper system.
   Outputs are static report files only.
9. **No commit, no stage.** This module is left as untracked working-tree files unless
   you explicitly decide otherwise.
10. **Forbidden imports** (to be enforced by `tests/test_safety_guards.py` in a later phase):
    `requests`, `urllib`, `http`, `socket`, `ccxt`, `binance`, `bybit`, `databento`,
    and any broker/exchange SDK.

If a future requirement conflicts with any rule above, **stop and ask** before acting.

---

## Scope boundary

- This module imports **nothing** from the rest of the SPARTA_BRAIN repo.
  It is self-contained pure Python (pandas only) by design.
- It reads **only** CSVs from its own `data_offline\` folder.
- It writes **only** into its own `reports\` folder.
- It does not read `data/databento*`, broker feeds, or any live state file.

---

## Build phases

- **Phase 1 (current):** documentation + isolated folder skeleton only.
  Files: `README.md`, `PLAN.md`, `data_offline\README_DATA.md`, `data_offline\.gitkeep`,
  `reports\.gitkeep`, `strategies\nq_orb\nq_orb_spec.md`.
- **Phase 2+ (NOT built yet):** `engine\` (metrics, backtester, decision, proposer),
  `loop\factory_loop.py`, `tests\`. These require separate explicit approval.

See `PLAN.md` for the full frozen design.
