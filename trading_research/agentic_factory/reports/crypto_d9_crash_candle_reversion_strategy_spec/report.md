# Crypto-D9 — Crypto Daily Crash-Candle Reversion v1 (FROZEN STRATEGY SPEC)

**This is a SPEC-ONLY step.** No code, no backtest, no IS/OOS run, no optimization, no
parameter sweep, no data fetch, no network, no exchange API, no broker, no paper, no live.
No OOS use, no 2024/2025/2026 rows. Frozen data untouched. S30/futures untouched;
JARVIS/`templates/base.html`/hydra untouched. **Not staged, not committed.**

- **Created:** 2026-05-30
- **HEAD at spec:** `ca4d9eb` (Crypto-D8 conservative framing) or descendant — factory
  tree clean, nothing staged, no active crypto strategy.
- **Selection basis:** Crypto-D8 (`ca4d9eb`) `SELECT_FAMILY_FOR_CRYPTO_D9_SPEC` — daily
  crash-candle / 1-day-drop reversion, POWER_OK on BTC unfiltered (81 @ −5%, 33 @ −7%,
  maxYr ≤ 0.43, regime-diverse incl. the 2022 bear).

---

## 1. Strategy name

**Crypto Daily Crash-Candle Reversion v1**

## 2. Market / timeframe

- **Instruments:** BTC / ETH / SOL **spot**
- **Data:** Binance USDT **daily UTC** frozen data
  (`data_crypto/spot_binance_usdt_1d_2020_2025/`, D3b `5b3d94c`, ratified D3c `fe5594f`)
- **Primary symbol:** **BTC**
- **Corroboration:** ETH / SOL
- **IS window:** 2020–2023
- **OOS window:** 2024–2025 **SEALED**
- **2026:** **SEALED OUT**
- **Perps:** **BLOCKED**

## 3. Core hypothesis

A large one-day spot crypto selloff may create short-horizon mean reversion due to forced
liquidation / panic selling / liquidity recovery. **D8 proved enough raw event count but
does NOT prove edge.**

## 4. Entry rule (FROZEN — exact version)

- **Long-only spot.**
- **Signal when `ret_1d ≤ −5%`.**
- **`ret_1d = close_t / close_{t-1} − 1`.**
- **No SMA200 / uptrend filter in v1** — because D8 proved that starves BTC (CODR-1's
  `close>SMA200` filter collapsed BTC to 9 events).
- **No confirmation filter in v1** — because confirmation filters risk reducing BTC below
  the event-count floor.
- **Entry at next daily open: `open_{t+1}`.**
- **One position per symbol.**
- **No pyramiding.**
- **If another signal occurs while a position is open, ignore it.**

## 5. Exit rule (FROZEN — exact version)

- **Exit at close of the 3rd bar after entry.**
- **Entry bar counts as bar 1.**
- **Therefore if entry is at `open_{t+1}`, exit is `close_{t+3}`.**
- **No stop.**
- **No profit target.**
- **No intraday assumptions.**
- **If data ends before the 3rd close, mark as `data_end`** — this is a boundary artifact
  only.

## 6. Risk / accounting

- **Gross returns first.**
- **`return_pct = exit_price / entry_price − 1`.**
- **Net returns after 0.30% round-trip friction.**
- **Stress returns after 0.45% round-trip friction.**
- **No leverage.**
- **Equal notional per trade for reporting.**
- **Report per-symbol and combined.**
- **Report gross, net base friction, and net stress friction.**

## 7. Pass / fail gates (HARD)

1. **BTC primary ≥ 30 IS events / trades.**
2. **BTC net expectancy > 0** after 0.30% friction.
3. **BTC top-3 removal remains positive** after 0.30% friction.
4. **Combined net PF > 1.3** after 0.30% friction.
5. **Stress friction 0.45% remains positive on combined.**
6. **At least 2/3 symbols positive** after 0.30% friction.
7. **No single year dominates > 60% of net.**
8. **Sequence risk not fragile** (checked later).
9. **OOS cannot be touched** unless IS passes **and** OOS protocol is committed.

## 8. Validation ladder

- **Crypto-D10:** engine + tests only
- **Crypto-D11:** IS baseline
- **Crypto-D12:** OOS protocol
- **Crypto-D13:** OOS once only if IS passes
- **then:** entry/distribution significance, sequence risk, regime, multi-asset,
  walk-forward, friction, final decision

## 9. Anti-overfit rules

- No changing the −5% threshold after results.
- No switching to −7% or −10% unless new branch.
- No adding SMA / trend filter after results.
- No confirmation filter after results.
- No changing the 3-bar exit after results.
- No OOS before protocol.
- No paper / live.
- No perps / funding.

## 10. Failure modes

- Naked falling knife.
- Edge may be negative after friction.
- Top-winner dependence.
- BTC may fail despite ETH / SOL.
- Crash events may cluster in one year.
- Daily open may gap against the entry.
- 3-day exit may miss longer recovery.
- No confirmation filter may admit low-quality signals.
- If the daily raw crash spec fails IS, the next step should be **NEEDS_4H_DATA_PROTOCOL**
  or a new branch, **not tuning**.

## 11. Final line

**“Crypto-D9 is a frozen strategy-spec step only; no crypto backtest, OOS, exchange API,
paper trading, or live trading is authorized.”**

---

**Trading recommendation:** NONE — frozen spec only. **Crypto Daily Crash-Candle Reversion
v1** is pre-registered with zero parameter freedom (−5% trigger, `open_{t+1}` entry,
`close_{t+3}` exit, no stop, no target, no filter). No backtest, no IS/OOS run, no edge
claim. Next step is **Crypto-D10 (engine + tests only)** under separate authorization. If
the daily raw crash spec later fails IS, the path is **NEEDS_4H_DATA_PROTOCOL** or a new
branch — not tuning. CODR-1 stays PARKED after IS_FAIL; OOS 2024–2025 and 2026 stay sealed;
perps remain blocked; crypto stays a separate research lane; **S30 stays PARKED and the
futures branches are untouched.**
