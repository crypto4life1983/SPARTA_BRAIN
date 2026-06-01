# SPARTA Crypto-D1 Protocol Memo v1

> **Research-only. Protocol / specification only.**
> No broker control. No live trading. No paper-order execution. No exchange
> connection. No API keys. No `.env`. No credential handling. No scheduler /
> background daemon. **No external network calls. No data fetch. No
> backtest. No dataset processing in this bundle.** This memo defines how
> SPARTA will study daily crypto strategies for BTC, ETH, and SOL **before**
> any data fetch, backtest, paper trading, or live trading is allowed.

**Protocol id:** `crypto_d1_protocol_v1` · **version:** `1.0`

**Lane history note:** Earlier crypto_d* lines (CODR-1 crash-candle
reversion etc.) were closed under `crypto_d7` and `crypto_d14` closeout
memos. This v1 memo **opens a NEW daily crypto study** under a fresh
protocol; it does **not** continue, re-tune, or revive any prior parameter
set. Prior closeouts remain authoritative for prior versions.

---

## 1. Lane + scope

- **Lane:** `crypto_d1_protocol`.
- **Target assets:** **BTC** (highest liquidity, deepest history) ·
  **ETH** (second-deepest history; cross-asset robustness vs. BTC) ·
  **SOL** (intentionally different vol / drawdown profile to prevent
  BTC-only overfit).
- **Allowed market type:** `spot` only.
- **Forbidden market types** at this stage: perp futures (different
  funding / liquidation / leverage problem), dated futures, options,
  leveraged tokens, margin/borrow-facilitated spot.

Perpetual futures may be studied later under a **separate protocol** —
they change the research problem (funding, liquidation, mark-vs-index,
liquidation cascade) and must not be folded into spot at v1.

## 2. Timeframe + session

- **Primary timeframe:** daily (`1d`) only.
- Intraday timeframes are **explicitly out of scope** for this protocol.
- **Market calendar:** 24/7 (crypto). Weekday-only filters are
  **forbidden**.
- **Missing-day rules:** missing daily bars MUST be flagged in the
  dataset manifest; **never silently forward-filled**.
- **Bar-close convention:** UTC close; left-closed / right-open
  documented in the dataset manifest.
- **Timezone normalization:** all storage UTC; original timezone
  preserved as metadata if a source was local.

## 3. Candidate strategy families (define, **do not test**)

| ID | Label | Status |
|---|---|---|
| `daily_trend_following` | Daily trend following | **primary** |
| `donchian_channel_breakout` | Donchian / channel breakout | **primary** |
| `moving_average_trend_filter` | Moving-average trend filter | **primary** |
| `volatility_regime_gate` | Volatility-regime gate | **primary** |
| `momentum_continuation` | Momentum continuation | **primary** |
| `risk_on_risk_off_filter` | Simple risk-on / risk-off filter | **primary** |
| `mean_reversion` | Daily mean reversion | **WATCH only** (not primary) |

Each family carries a one-line summary + a *minimum-viable-test shape*
(pre-registered parameter grid; no in-sample optimisation beyond it). See
`protocol.json` for details.

Mean reversion is intentionally **WATCH-only**: counter-trend / pullback
entries carry higher regime-dependence risk; it is **never primary** and
**never combined** with trend-following without an explicit ensemble
protocol.

## 4. Data requirements (future, separately authorized)

- **OHLCV daily candles** required.
- **Timezone normalization** to UTC.
- **24/7 session handling**; weekday-only handling forbidden.
- **Missing-day rules:** flagged, never silently filled.
- **Exchange / source provenance:** source named in the manifest;
  row-level `source_id` required.
- **Symbol mapping:** per-venue → SPARTA canonical (BTC / ETH / SOL),
  versioned.
- **Split / rename / fork / delisting handling:** crypto rarely splits;
  renames / forks / network-changes (LUNA → LUNC, MATIC → POL) are
  first-class events with a documented adjustment method.
- **Fee assumptions:** taker-side fee per venue, dated, pre-declared.
- **Slippage assumptions:** conservative slow-day haircut on top of
  fees; depth-aware when L2 is available.
- **Stablecoin quote handling:** quote currency (USDT / USDC / USD)
  declared per series; cross-stablecoin conversion requires an explicit
  FX series + documented method.
- **Data freeze:** every dataset FROZEN with sha256 checksums before any
  IS / OOS run; manual edits invalid unless documented + re-validated
  under a new `dataset_version`.
- **No lookahead:** features and signals available at decision time
  only; IS / OOS sealed before any run.

## 5. Fee + slippage requirements

- **Default sizing:** TAKER on every leg unless a maker proof is
  pre-registered.
- **Minimum haircut per trade:** documented per venue; never best-case.
- **Fee schedule attached** to every per-dataset manifest.
- **Fees as a distinct PnL line** — never silently netted.
- **Slippage minimum:** constant-bps + 1-tick haircut OR depth-aware
  (when L2 is available).

## 6. Risk assumptions

- **No leverage** in the first test.
- **Position sizing:** equal-weight per asset OR pre-declared
  fixed-fraction sizing. No adaptive sizing at this stage.
- **Stop-loss policy:** pre-registered if any; never added post-hoc.
- **Drawdown kill:** per-asset and portfolio drawdown limits pre-declared.
- **Tail-risk disclosure:** each future backtest report must include
  worst-day / worst-week / worst-month drawdown + at least one named
  stress scenario.

## 7. Validation phases

| Phase | Purpose |
|---|---|
| **P0_protocol** | This bundle. Lock language, scope, costs, kill rules. No data, no run. |
| **P1_data_contract** | Crypto-D1 data contract + source selection. Spec only; no data pull. |
| **P2_dataset_manifest_freeze** | Acquire frozen historical data (separately authorized); produce + freeze a per-dataset manifest. |
| **P3_baseline_strategy_impl** | Implement the first candidate strategy family deterministically; no IS run yet. |
| **P4_is_oos_split** | Pre-register IS window + sealed OOS window before any run. |
| **P5_walk_forward_or_rolling** | Walk-forward / rolling validation under the pre-registered protocol. |
| **P6_robustness_sensitivity** | Parameter-perturbation sensitivity + cost stress + asset coverage. |
| **P7_paper_signal_simulation** | Paper-signal **SIMULATION ONLY** (no broker, no order execution) — and **only** if a SEPARATE future authorization grants this phase. |
| **P8_live_trading** | **EXPLICITLY OUT OF SCOPE** for this protocol stack. Live trading requires a SEPARATE far-future protocol + authorizations after evidence exists. |

## 8. PASS / WATCH / FAIL rules

- **PASS** — Future tests show: **no lookahead**; realistic fees +
  slippage; enough trades to support a verdict; **OOS survives** the IS
  pattern in sign + magnitude within a pre-registered tolerance; result
  **does not depend on a single asset**; drawdown within pre-declared
  limits; rules remain simple + explainable; no rule was changed
  mid-study.
- **WATCH** — IS shows positive expectancy after full costs but at
  least one of: OOS materially weaker than IS; one asset works, others
  do not; trade count too low; sensitive to small fee / slippage
  changes; market-regime dependent.
- **FAIL** — No OOS edge; excessive drawdown; overfit parameters; only
  works in one (bubble) regime; edge disappears with realistic costs.

## 9. Kill conditions

- Any stress scenario (vol spike / regime flip / venue outage proxy)
  eats more than N months of estimated edge.
- Backtest cannot be reproduced bit-for-bit by a second offline run.
- An assumption (no-fee, no-slippage, no-borrow, no-funding for spot)
  is silently dropped.
- OOS window is peeked before sealing.
- Parameter sweep extends beyond the pre-registered grid.
- Edge depends on data that has been manually edited without
  documentation.

## 10. Required future artifacts

- **Crypto-D1 Data Contract v1** (P1) — spec only, no data pull.
- **Crypto-D1 Dataset Manifest v1** (P2) — per-dataset manifest schema.
- **Crypto-D1 Data QA / Freeze Spec v1** (P2) — QA harness for daily
  crypto.
- **Crypto-D1 Baseline Backtest Plan v1** (P3 / P4) — pre-registration
  memo for the FIRST family + IS / OOS split.
- Per-strategy backtest report.json + report.md with PASS / WATCH /
  FAIL verdict.
- Lane closeout memo if a strategy family PARKs / RETIREs.

## 11. No-profit-claim policy

- **This protocol does not imply edge.**
- **Crypto trend ideas are not profitable until tested.**
- **A good historical chart does not imply future returns.**
- **No paper or live trading is authorized.**
- **No backtest is authorized by this protocol alone** — P3+ requires
  its own separate authorization.

## 12. Safety boundaries (pinned, non-negotiable)

- Research-only. Protocol / specification only.
- No broker control, no exchange connection, no API keys, no `.env`,
  no credential handling.
- No live trading. No paper-order execution. No order placement.
- No scheduler / background daemon. No external network calls in this
  protocol's runtime.
- **No data fetch. No backtest. No dataset processing in this bundle.**
- Do not modify paper / live execution files.
- Do not claim profitability. Do not claim live-readiness. Do not
  claim STRONG evidence from this protocol alone.
- **Crypto trend ideas are not profitable until tested with full costs.**
  **A good historical chart does not imply future returns.**
  **No backtest is authorized by this protocol alone.**
