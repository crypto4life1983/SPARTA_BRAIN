# Crypto-D7 — CODR-1 Closeout + Next-Hypothesis Selection (memo only)

**This is a CLOSEOUT + IDEA-SELECTION MEMO only.** No code, no backtest, no IS/OOS
run, no optimization, no parameter change, no data fetch, no network, no exchange API,
no broker, no paper/live. No OOS use, no 2024/2025/2026 rows. Frozen crypto data
untouched. No S30/futures changes, no JARVIS/`templates/base.html`/hydra changes. **Not
staged, not committed.**

- **Created:** 2026-05-30
- **HEAD at memo:** `27b0620` (Crypto-D6 IS baseline) — factory tree clean; nothing
  staged; **no active crypto strategy** (CODR-1 v1 PARKED after IS_FAIL).

---

## 1. CODR-1 chain summary

| Step | Commit | What |
|---|---|---|
| Crypto-D4 spec | `5552356` | Froze **CODR-1 v1** (Crypto Oversold-Dip Reversion in Uptrend): long-only spot; `close_t>SMA200` AND `ret_t≤−7%` → enter `open_{t+1}`; one position/symbol, no pyramiding; −10% close stop (precedence) else time stop at close of 5th held bar; no profit target. Pre-registered, no parameter freedom. |
| Crypto-D5 engine/tests | `4614190` | Implemented the frozen engine (`engine/crypto_codr1.py`, stdlib-only, offline, **GROSS** returns, friction a separate layer) + tests. No run. |
| Crypto-D6 IS baseline | `27b0620` | Ran CODR-1 **IS-only** on frozen BTC/ETH/SOL spot daily (BTC/ETH 2020–2023; SOL partial 2020-08-11..2023). SMA200 warmed **inside** IS; **0** rows from 2024/2025/2026 used. Verdict **IS_FAIL**. |

## 2. CODR-1 final verdict

### **PARKED after IS_FAIL**

- **No OOS run.** **No Crypto-D7 OOS authorized.**
- Per the ladder, IS_FAIL stops the branch *before* any OOS pre-registration. D2's
  future-sequence had penciled D7 as "OOS protocol pre-registration," but CODR-1 never
  earned OOS — so D7 is repurposed as this closeout. **OOS 2024–2025 and 2026 remain
  SEALED and untouched.**

## 3. Main failure reasons (from D6 `27b0620`)

- **BTC primary failed hard** — 9 trades, net@0.30% total **−4.93%** (avg −0.55%/trade),
  gross PF 0.911, net PF 0.81. A strategy whose **primary** symbol loses money after
  costs cannot advance.
- **BTC trade count too low** — only **9** IS trades vs the **≥30/symbol** gate; ETH (27)
  also below 30.
- **Net PF below threshold** — after the pre-registered 0.30% round-trip friction, net PF
  was below **1.3** on BTC (0.81), ETH (1.21) and the **combined** pool (1.28); only SOL
  cleared it (1.45).
- **Top-3 gate failed under stress** — the HARD top-3-winner-removal gate failed on **all
  three** symbols at net@0.30% (BTC −25.12%, ETH −35.05%, SOL −2.86% ex-top-3). The
  combined pool passed at base friction (+6.74%) but **FAILED under +50% stress**
  (net@0.45% ex-top-3 = −2.71%).
- **Edge concentrated in 2020–2021 bull** — the `close>SMA200` filter suppresses entries
  in the 2022 bear (combined trades drop to 2 in 2022, 5 in 2023). It is effectively a
  **bull-only dip-buyer** — exactly the regime fragility the ladder is built to catch.
- **Combined pass was pooling-dependent** — the only thing the pool cleared (top-3 at base
  friction) it cleared by pooling 66 trades across three coins, diluting per-coin winner
  concentration. Not per-symbol robust; cannot rescue a primary-symbol failure.

## 4. What this teaches

- **Simple oversold-dip reversion is not enough** — a single −7% day in an uptrend is too
  weak/too rare a causal signal on daily spot: it neither fires often enough (BTC 9
  trades) nor yields an edge robust to friction and winner-removal.
- **BTC primary must carry evidence** — multi-asset corroboration is a *secondary* check,
  not a substitute. If BTC (deepest market, designated primary) cannot carry its own
  positive, friction-surviving, winner-robust edge, the hypothesis fails regardless of
  ETH/SOL.
- **Multi-asset pooling cannot hide weak symbol-level evidence** — pooling flatters trade
  count and dilutes concentration but masks per-symbol fragility. Read gates **per-symbol
  first, pooled second.**
- **The top-winner gate remains crucial** — the gate that parked every futures branch
  again exposed concentration the headline returns hid. It stays a hard, non-negotiable
  gate.
- **Crypto needs more signals OR a different mechanism** — daily-spot BTC does not generate
  enough discrete shock events to power a thin event-driven strategy to ≥30 trades with a
  friction-robust edge. The next idea must **either fire materially more often** (higher
  signal density / more frequent timeframe) **or rest on a stronger, more specific causal
  mechanism** than "a one-day dip in an uptrend."

## 5. Data readiness remains useful

- The immutable, SHA256-pinned, 2026-sealed **BTC/ETH/SOL spot daily USDT** snapshot
  (D3b `5b3d94c`, ratified D3c `fe5594f`; BTC `d87742b8`, ETH `4a4d7b08`, SOL `bd8b28f1`)
  remains **QA-CLEAN and valid** for the next separately-authorized crypto hypothesis.
  **CODR-1's failure is a strategy failure, not a data failure.**
- **Perps remain BLOCKED** until funding-rate data is sourced and funding rules frozen
  (Crypto-D1 §4/§9; D2 item #4 funding work is know-how, not authorization).
- Quote reconciliation (USDT vs USD/USDC) and an independent second-source cross-check
  (e.g. Kraken/Coinbase) remain advisable before any future edge claim (D3b).

## 6. Next-hypothesis options (≥5 compared)

| Id | Idea | May work | May fail | Trades | Top-winner risk | Friction sens. | BTC/ETH/SOL testable | New data? | Too close to CODR-1 / rejected? |
|---|---|---|---|---|---|---|---|---|---|
| A | Volatility compression → expansion breakout | coils precede expansion; fires in bull+bear | needs lookback+threshold → **parameter freedom**; expansion winners fat-tailed | mod-low | mod-high | moderate | OK | no | Novel vs CODR-1, but parameter-freedom is why D4 rejected it (cand #3) |
| B | Cross-asset momentum (BTC→ETH/SOL) | BTC often leads alts | corroboration **baked into** signal → undercuts the multi-asset gate; leaves BTC with no primary entry | moderate | moderate | moderate | **weak paradox** | no | Conflicts with the BTC-must-carry lesson; D4 rejected it (cand #4) |
| C | Trend continuation after high-volume breakout (+ winner safeguards) | volume-confirmed trend rides | **top-winner-dependent** structure; safeguards blunt the upside it relies on | low | **HIGH (killer)** | moderate | OK | no | **Too close to PARKED trend family** (D4 cand #1 / S26-S27 / D2 ema_pullback) |
| D | Mean reversion after **extreme multi-day liquidation candle**, stricter **BTC confirmation** | stronger causal flush than a routine dip; **forces BTC to carry** (fixes a D6 root cause) | extreme flushes **rarer** than −7% days → likely even **fewer BTC trades** → ≥30 gate risk | **LOW–v.low (binding risk)** | lower (fixed horizon caps winners) | mod-high (testable) | good; BTC-carry built in | daily: no; may need 4H/liquidation proxy → **yes** | Adjacent to CODR-1 but mechanistically distinct |
| E | Calendar / weekend / day-of-week seasonality | **high signal density** → easily ≥30 trades; trivial, no params | tiny per-trade edge → **friction-dominated FAIL**; 24/7 crypto weakened weekend effect | HIGH | LOW | **VERY HIGH (killer)** | OK | no | Novel vs CODR-1, but friction-domination is why D4 rejected it (cand #5) |
| F | Regime / no-trade overlay only | could protect a future entry (avoid 2022 bear) | **an overlay is not a strategy** — no entry of its own; old HMM holdout never closed, SOL transfer FAILED | N/A | N/A | N/A | N/A standalone | no | Same exclusion as D4 (cand #6) / S30-D1 / D2 item #3 |

## 7. Recommendation

### **NO_STRATEGY_SELECTED_NEED_MORE_RESEARCH**

Every option carries a structural defect the factory has already reasoned through: **A**
parameter freedom, **B** conflicts with the BTC-must-carry lesson, **C** top-winner-
dependent trend family (already parked), **E** friction-dominated, **F** an overlay is not
a strategy. The only option aligned with the D6 lessons — **D** (liquidation-cascade
reversion with BTC confirmation) — is throttled by the **same binding constraint that just
failed CODR-1**: too few discrete signal events on daily BTC to reach the ≥30-trade gate.
Picking another thin daily-spot event strategy now would most likely reproduce CODR-1's
BTC trade-count failure.

**What Crypto-D8 should be:** a **read-only signal-density / statistical-power audit**
(memo only — *counting candidate events, NOT backtesting*) on the frozen IS data. For each
surviving family (especially **D**, with **E** as a high-frequency sanity floor), count how
many candidate entry events it would produce on BTC/ETH/SOL in 2020–2023 IS, and decide
whether daily spot can **ever** yield ≥30 BTC events with a friction-survivable per-event
edge. If daily spot is structurally too sparse for event-driven mechanisms, D8 should also
scope whether a **more frequent timeframe (4H spot — deferred in D2)** or a **second data
source** is the real prerequisite. Only after that audit should a later step freeze a
single hypothesis spec.

**Conditional runner-up:** if a single idea *must* be chosen, **option D** is the least-bad
single pick (stronger mechanism + forces BTC to carry), **but it must not be frozen** until
the D8 signal-density audit confirms it can clear the BTC trade-count gate. **No full spec
is written in this memo.**

## 8. Forbidden actions (this lane)

`no_oos` · `no_strategy_testing` · `no_backtest` · `no_exchange_api_execution` ·
`no_broker` · `no_paper_or_live` · `no_perps` · `no_parameter_tweaking_of_codr1` ·
`no_data_fetch` · `no_network` · `no_optimization` · `no_modification_of_frozen_data` ·
`do_not_touch_s30_or_futures` · `jarvis_templates_base_hydra_untouched` · `no_staging` ·
`no_commit`.

## 9. Final line

**“Crypto-D7 is a closeout and idea-selection memo only; no crypto strategy is validated,
paper-ready, live-ready, or authorized for execution.”**

---

**Trading recommendation:** NONE. Closeout + idea-selection memo only. **CODR-1 v1 is
PARKED after IS_FAIL** (no OOS run, no D7 OOS authorized). No next hypothesis is frozen —
recommendation is **NO_STRATEGY_SELECTED_NEED_MORE_RESEARCH**, with Crypto-D8 proposed as a
read-only signal-density/power audit. Frozen BTC/ETH/SOL spot data stays valid for future
research; perps remain blocked; OOS 2024–2025 and 2026 stay sealed; crypto stays a separate
research lane; **S30 stays PARKED after IS_FAIL and the futures branches are untouched.**
