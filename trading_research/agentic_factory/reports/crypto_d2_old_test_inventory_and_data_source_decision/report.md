# Crypto-D2 — Old Crypto Test Inventory + Data-Source Decision (memo only)

**This is an inventory + data-source decision memo. No crypto data fetch, no code,
no backtest, no IS/OOS run, no optimization, no parameter sweep, no strategy test,
no exchange API, no broker, no paper/live, no S30/futures-branch changes, no
JARVIS/templates/base.html/hydra changes, no staging, no commit.** It inventories
all locally-recorded historical crypto work, classifies every item as historical-
only under the new validation factory, and pins the clean data-source path for a
later (separately authorized) Crypto-D3.

- **Created:** 2026-05-30
- **HEAD at memo:** `f79dd5c` (Crypto-D1 commit `c8a59fe` is in history). Factory
  tree: nothing staged; an untracked `reports/s30_d4_overnight_drift_is_baseline/`
  folder exists from background automation and was **NOT touched, staged, or
  created by this crypto session.**
- **Read-only context:** Crypto-D1 research-lane protocol (the binding rules);
  `brain_memory/projects/trading_bot/` (project / lessons / decisions /
  next_actions); `brain_memory/knowledge/trading_lessons.md`. No data fetched.

---

## 1. Crypto-D1 reference (binding protocol)

- **Crypto-D1 commit:** `c8a59fe` (`c8a59fee3e4804c416564d4673f7152e87fd3e60`).
- **Crypto is a SEPARATE research lane** under the completed validation factory —
  **never mixed into the NQ/ES futures branches** (S30 overnight-drift, Donchian,
  S26–S29). No crypto result may be cited alongside a futures validation claim.
- **No paper/live, no exchange API execution, no broker, no auto-bot launch.**
- **Old crypto work is historical context, not evidence.** Any old idea must be
  re-entered as a NEW frozen Crypto spec and re-run through the full ladder; no
  parameter, curve, or OOS conclusion carries over.

## 2. Old crypto inventory (from local memory/reports only — nothing fetched)

All items below predate the validation-factory standard. Each is **HISTORICAL_ONLY**.

| # | Name / description | Symbols | TF | What it claimed/tested | Type | New-rules status | Re-test worth? |
|---|---|---|---|---|---|---|---|
| 1 | **Crypto trading bot + Streamlit dashboard** (scoring layers, strategy performance, trade frequency, R-leak, regime control; Binance/Kraken live feeds) | BTC/ETH + alts | mixed | A live-feed bot/analytics stack with scoring + regime control; not a single frozen hypothesis | Bot / infrastructure / execution | HISTORICAL_ONLY | Infra only — re-architect under factory; not a strategy to re-test as-is |
| 2 | **ema_pullback strategy** (trend/pullback long, drawdown context flagged) | ETH/USD (and others) | daily-ish | A trend/pullback continuation entry; flagged for ETH/USD drawdown context | Strategy / backtest | HISTORICAL_ONLY | Possibly — but it is the S26/S27 *family* (trend-continuation / pullback) that the futures factory already PARKED; re-test only as a freshly frozen spec, low priority |
| 3 | **Regime HMM "mid-vol transit" study** (regime_detection_exp; preregistered_split; K=3/K=4 hidden-Markov regime models; P(low→high)/P(high→low); cross-coin transfer M1–M4; 4000-sample aligned parametric bootstrap; label-switching diagnostics; Checkpoints A–D) | BTC, ETH, SOL | daily features | In-sample finding: rare direct low↔high regime transitions ("transit only via mid-vol") across BTC 0.004, ETH 0.002, SOL 0.000 at K=3; holdout durability left OPEN; SOL cross-coin transfer FAILED → BTC↔ETH-only boundary recorded | Regime classifier / overlay study | HISTORICAL_ONLY | As a regime/no-trade **overlay**, not a standalone entry branch (S30-D1: an overlay is not a strategy). Holdout was never closed — claim is unproven |
| 4 | **Perp funding-rate acquisition + anomaly work** (H1-Auth-1: SOL/BTC/ETH funding; FTX-collapse-week anomaly 2022-11-09..18; Binance raises funding frequency in extreme vol; REST vs data.binance.vision archive acquisition; µs-normalisation hazard; only BTC/ETH have USD-M dated chains, perp ≥3 feasible) | BTC, ETH, SOL | funding cadence | Funding-data sourcing/QA for a perp universe; diagnosed a cadence anomaly as the FTX week, not a defect | Data / funding provisioning | HISTORICAL_ONLY | Useful as **data-provisioning know-how** for a future perp lane — but **perps are BLOCKED** until funding is sourced + frozen (Crypto-D1 §4/§9) |
| 5 | **Generic bot scoring / R-leak / trade-frequency / regime-control analytics** | portfolio | mixed | Performance scoring + leakage analytics layered on the bot | Analytics / tooling | HISTORICAL_ONLY | Archive — tooling, not a hypothesis |

**Explicitly OUT OF SCOPE (not crypto — must not be pulled into this lane):** the
NQ/ES futures factory branches (Donchian S23–S25, S26–S29, S30 overnight-drift) and
the external-research-hunter cross-asset work (cross-asset Donchian, RSI2
mean-reversion via yfinance proxy, SPY vol-targeting). These are
futures/equities/cross-asset, **not** crypto, and are listed here only to prevent
mis-attribution into the crypto inventory.

## 3. Old crypto result classification

| Item | Classification |
|---|---|
| 1 — Bot + dashboard + live feeds | **REJECT_OR_ARCHIVE** (execution/infra; no exchange API to be wired; not a frozen hypothesis) |
| 2 — ema_pullback (ETH/USD) | **POSSIBLE_RETEST_CANDIDATE** but **DATA_REQUIRED_BEFORE_RETEST**; low priority (parked S26/S27 family) |
| 3 — Regime HMM mid-vol transit | **DATA_REQUIRED_BEFORE_RETEST** as an overlay/context model only; **HISTORICAL_ONLY_DO_NOT_USE** as proof (holdout never closed; SOL transfer failed) |
| 4 — Perp funding acquisition/anomaly | **DATA_REQUIRED_BEFORE_RETEST**; perps remain **BLOCKED** until funding sourced + frozen |
| 5 — Scoring / R-leak analytics | **REJECT_OR_ARCHIVE** (tooling) |

**Net:** no old crypto item is a validated candidate. Nothing carries an edge into
the new lane. The only items worth a *future* fresh-frozen retest are #2 (a
trend/pullback spec, low priority) and, as an overlay, #3 — both **gated on clean
data first**.

## 4. Data-source decision (clean path for Crypto-D3 — selection only, no fetch)

- **Spot OHLCV first** (no funding leg, cleaner accounting).
- **Symbols first:** **BTC, ETH, SOL** (XRP deferred until QA/liquidity pass).
- **Daily UTC candles first** (00:00 UTC boundary), 4H deferred, no intraday in v1.
- **Perps BLOCKED** until funding-rate data is sourced and funding rules frozen
  (Crypto-D1 §4/§9) — item #4's funding history is know-how, not authorization.
- **Quote currency:** pick ONE spot quote and document it (USDT vs USD vs USDC is a
  known QA hazard — Crypto-D1 §11); reconcile, never silently mix.

## 5. Spot vs perps decision

**Start with spot (or spot-like) OHLCV.** Do **not** test perps until funding
rates, fees, and exchange-specific mechanics are explicitly defined and frozen. The
old perp/funding work (item #4) confirms the hazard — Binance changes funding
cadence in extreme volatility (the FTX week) — which is exactly why perps must wait
for a frozen funding protocol. Spot is unaffected and goes first.

## 6. Exchange / vendor requirements

- Reliable, complete **OHLCV with volume**; no silent gaps.
- **UTC daily boundary** (00:00 UTC), documented and pinned per dataset.
- **Clear symbol convention** (e.g. `BTCUSDT` spot) and **one consistent series per
  symbol** — no ambiguous stitching across exchanges/pairs.
- **No silent exchange-outage fills** — outages flagged as explicit QA events.
- **Stable quote currency** with USD/USDT/USDC rules documented and reconciled.
- **Named, pinned provenance per dataset** (source, range, retrieval method),
  mirroring how the offline futures CSVs are documented.
- **Candidate sources (decision only, not yet fetched):** a primary archive of spot
  daily klines (e.g. an exchange's published daily-kline archive, which prior local
  notes found gave clean uniform-ms timestamps) **plus one independent second source
  for cross-checking** BTC/ETH/SOL. Final vendor pinned in Crypto-D3 — **no fetch
  here.**

## 7. QA checklist for Crypto-D3 data provisioning

- Duplicate timestamps → reject/flag.
- Missing daily candles → flag explicitly (do NOT silently forward-fill).
- Zero/negative OHLC, or high<low / close|open outside high–low → reject.
- Zero-volume bars → flag (possible outage or illiquid listing).
- Exchange-outage days → recorded as explicit events, never hidden.
- Symbol continuity → one consistent series per symbol; no cross-exchange stitching.
- Timezone consistency → all bars on the same UTC daily boundary.
- 24/7 handling → **no expected weekend/holiday gaps**; every calendar day has a bar;
  a missing day is a QA event, not a zero-return bar.
- **BTC/ETH/SOL calendar alignment** → identical date index across the three symbols
  for any multi-asset comparison.
- **Per-symbol history feasibility** → BTC/ETH have full 2020+ history; **SOL's
  exchange history starts mid-2020**, so SOL needs a **justified per-symbol window**
  (Crypto-D1 §10) rather than fabricated/stitched pre-listing history.

## 8. Proposed future sequence

| Step | Scope |
|---|---|
| Crypto-D3 | data-source / data-QA **provisioning only** (pin vendor, run QA checklist; still no strategy) |
| Crypto-D4 | choose / re-freeze ONE crypto strategy spec (pre-registered, no parameter freedom) |
| Crypto-D5 | implement engine + tests only (no run) |
| Crypto-D6 | IS baseline (hard OOS seal) |
| Crypto-D7 | OOS protocol pre-registration (committed protocol hash) |
| Crypto-D8 | OOS once (one-shot) |
| Crypto-D9+ | entry significance → sequence risk → regime → multi-asset (BTC/ETH/SOL) → walk-forward → friction → final decision gate |

## 9. Forbidden actions (this lane)

`no_live_trading` · `no_paper_trading` · `no_exchange_api_execution` ·
`no_auto_bot_launch` · `no_data_fetch` · `no_code` · `no_backtest` ·
`no_optimization` · `no_parameter_sweep` · `no_strategy_test_before_data_protocol` ·
`no_using_old_results_as_proof` · `no_mixing_crypto_with_futures_validation_claims` ·
`do_not_touch_s30_or_futures_branches` · `jarvis_templates_base_hydra_untouched` ·
`no_staging` · `no_commit`.

## 10. Final recommendation

**Crypto-D3 (spot data-source + data-QA provisioning, selection/QA only) should be
the next step.** The inventory is sufficient — old crypto work is fully catalogued
and uniformly historical-only; **no further inventory is needed before Crypto-D3.**
The blocker to any crypto strategy work is clean, QA'd spot data, so data
provisioning is the correct and only next move. **Crypto-D3 is NOT authorized by
this memo** — it requires a separate explicit instruction, and even then performs no
strategy work and (until its own authorization) no fetch.

**Final line:** *“Crypto-D2 is inventory and data-source decision only; no crypto
strategy is validated, paper-ready, live-ready, or authorized for execution.”*

---

**Trading recommendation:** NONE. Inventory + data-source decision only. No crypto
strategy is validated, paper-ready, or live-ready. All old crypto work
(BTC/ETH/SOL/XRP bots, the regime-HMM study, ema_pullback, perp/funding acquisition)
is historical context only and must be re-frozen and re-run through the validation
factory before carrying any weight. Crypto remains a separate research lane; S30 and
the futures branches are untouched.
