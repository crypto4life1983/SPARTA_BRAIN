# Crypto-D3 — Crypto Data-Source + QA Provisioning (data only, no strategy)

**This is a data-source + data-QA provisioning step. No strategy code, no backtest,
no IS/OOS run, no optimization, no parameter sweep, no NEW data fetch, no exchange
API, no broker, no paper/live, no S30/futures-branch changes, no
JARVIS/templates/base.html/hydra changes, no staging, no commit.** It checks whether
clean local crypto OHLCV already exists, QAs it read-only, evaluates whether its
provenance is pinned, and issues a data-readiness verdict for a later (separately
authorized) Crypto-D4 spec. **No strategy is specified or tested here.**

- **Created:** 2026-05-30
- **HEAD at memo:** `2849279` (Crypto-D1 `c8a59fe` and Crypto-D2 `a035ab0` both
  confirmed ancestors). Factory tree: nothing staged; this `crypto_d3_...` folder is
  untracked. The S30-D4 `_run.json` was left untouched; S30 remains PARKED after
  IS_FAIL and was not touched.
- **Read-only context:** Crypto-D1 protocol (binding) and Crypto-D2 inventory +
  data-source decision (binding). Local crypto CSVs were **read** for QA only — never
  modified, moved, overwritten, or fetched.

> **Note on companion `report.json`:** an automation-written `report.json` already
> existed in this folder when this step ran, reaching the same conservative verdict
> below (`DATA_NOT_READY_FETCH_AUTH_REQUIRED`). I independently verified its central
> claim — the provenance of these exact daily files is not pinned — and aligned this
> `report.md` to that verdict. (An earlier draft of this file briefly proposed
> `DATA_READY`; that was corrected after confirming the provenance gap is real.)

---

## 1. Crypto-D1 / Crypto-D2 references (binding)

- **Crypto-D1 protocol:** `c8a59fee3e4804c416564d4673f7152e87fd3e60` — separate lane;
  spot first; BTC/ETH/SOL; daily UTC (00:00) candles; perps BLOCKED until funding
  sourced+frozen; **no exchange API execution**; IS 2020–2023 / OOS 2024–2025 proposed;
  **2026 blocked**; data-QA rules (§11); **named/pinned provenance per dataset (§5)**;
  same validation ladder as futures.
- **Crypto-D2 decision:** `a035ab079d2d76c271076ad5edeadad0e7df7086` — 5 old crypto
  items all HISTORICAL_ONLY; data-source path = spot OHLCV first, BTC/ETH/SOL, daily
  UTC, **one documented quote currency, named pinned provenance**, perps blocked; next
  step = Crypto-D3 (this).

## 2. Does local crypto data exist?

**YES (structurally) — but provenance is NOT pinned.** Daily OHLCV for BTC/ETH/SOL
exists in the repo (outside the factory tree, **gitignored**), under
`data/frozen_regime_inputs/`:

| Symbol | File | Quote | Rows | Date range |
|---|---|---|---|---|
| BTC | `btcusdt_1d_2020-01-01_2026-05-29.csv` | USDT | 2341 | 2020-01-01 → 2026-05-29 |
| ETH | `ethusdt_1d_2020-01-01_2026-05-29.csv` | USDT | 2341 | 2020-01-01 → 2026-05-29 |
| SOL | `solusdt_1d_2020-08-11_2026-05-29.csv` | USDT | 2118 | 2020-08-11 → 2026-05-29 |

This is the **regime-intelligence drop-zone** consumed by
`sparta_regime_intelligence.csv_loader` — the same data family as Crypto-D2 inventory
**item #3 (regime HMM mid-vol study), classified HISTORICAL_ONLY.** A synthetic
placeholder (`_SAMPLE_SYNTHETIC_btcusdt_1d.csv`) exists and is **excluded** (synthetic,
never usable for any edge claim).

**Provenance status — UNPINNED (the blocking gap):**
- The folder `README.md` is only a read-only drop-zone contract (required columns =
  `timestamp`/`date` + `close`). It documents **no source exchange, no spot-vs-perp,
  no retrieval method** for these files.
- A repo manifest `reports/crypto_regime_data_acquisition_manifest.json` documents a
  Binance **spot** acquisition — but at **`interval: 1h`** into a **different folder**
  (`C:\SPARTA_RESEARCH_LAB\crypto_regime_momentum_meanrev\data\raw`). It is **not** a
  1:1 provenance record for these specific `data/frozen_regime_inputs/*_1d_*.csv` daily
  files (different timeframe, different path). It is suggestive of Binance-spot lineage,
  **not proof** of it for these exact files.
- **Spot-vs-perp for these files is therefore UNDETERMINED.** The `usdt` filename and
  the manifest hint at spot, but nothing pins it. (Separately, genuine **perp
  funding** JSON for BTC/ETH/SOL exists under
  `external_repos_static/funding_rate_arbitrage_.../historicalDataJSON/` — out of
  scope; perps blocked.)

## 3. Data-source recommendation

These structurally-clean BTC/ETH/SOL daily USDT candles are a strong **candidate**
backing dataset, but cannot be promoted until provenance is closed, via **either**:

- **(A) Pin provenance retroactively** for the existing files: (a) named source
  exchange, (b) **explicit SPOT confirmation**, (c) documented retrieval method +
  date, (d) quote-currency rule (USDT, reconciled vs USD/USDC). If this can be done
  with confidence, the data is ready.
- **(B) Clean re-provision (Crypto-D3b)** — a separately authorized, provenance-
  documented spot OHLCV fetch for BTC/ETH/SOL. This is a **fetch**, so it needs its own
  explicit authorization; this memo fetches nothing.

Recommended *target* source remains **a trusted public spot daily archive (e.g.
Binance `data.binance.vision` spot daily klines), USDT quote**, with **one independent
second source (Kraken/Coinbase spot daily)** for BTC/ETH cross-check before any edge
claim.

## 4. Spot vs perp decision

- **Intended: SPOT** (Crypto-D1 §4 / Crypto-D2 §5) — no funding leg, clean accounting.
- **Status for the local files: UNDETERMINED** — a **hard gate**. If these candles
  were perp, the dataset is BLOCKED (perps require sourced+frozen funding). A frozen
  Crypto-D4 spec **cannot** be built on data whose instrument type is unconfirmed.
- **PERPS REMAIN BLOCKED** regardless until funding data + rules are frozen.

## 5. BTC / ETH / SOL coverage status

- **BTC / ETH:** 2020-01-01 → 2026-05-29, full daily, 2341 bars, identical date index.
- **SOL:** 2020-08-11 → 2026-05-29, 2118 bars — starts at SOL's exchange listing
  (mid-Aug 2020); a **justified per-symbol window** (Crypto-D1 §10), not fabricated
  pre-listing history.
- **Multi-asset alignment:** common tri-symbol index = **2118 days (2020-08-11+)**;
  BTC/ETH carry 223 extra pre-SOL days. Joint tests must use the SOL-aligned window or
  pre-registered per-symbol windows.
- **IS/OOS feasibility:** IS 2020–2023 = BTC/ETH 1461 d, SOL 1238 d; OOS 2024–2025 =
  731 d each — fully populated for all three.
- **2026 SEAL FLAG:** each series includes **149 bars of 2026** (through 2026-05-29).
  **Crypto-D1 §10 blocks 2026** — a future spec must seal it out unless separately
  authorized.

## 6. QA results (read-only; nothing modified)

| Check | BTC | ETH | SOL |
|---|---|---|---|
| Header schema (`timestamp,open,high,low,close,volume`) | ✅ | ✅ | ✅ |
| Rows | 2341 | 2341 | 2118 |
| Duplicate timestamps | 0 | 0 | 0 |
| Invalid OHLC (high<low, o/c outside hi–lo, ≤0) | 0 | 0 | 0 |
| Zero-volume bars | 0 | 0 | 0 |
| Negative-volume bars | 0 | 0 | 0 |
| Missing calendar days (24/7) | 0 | 0 | 0 |
| Date format / daily boundary (`YYYY-MM-DD`) | ✅ | ✅ | ✅ |

**Structural QA verdict: CLEAN** — no duplicates, no invalid OHLC, no zero/negative
volume, no calendar gaps (full 24/7), single consistent USDT quote, one continuous
series per symbol (no visible cross-exchange stitching). **The QA pass is about
structure only; it does not certify provenance or spot-vs-perp.**

## 7. If not ready — exact future authorization needed

To reach readiness, a separate explicit authorization for **one** of:
- **Provenance pin** of the existing files (named exchange + SPOT confirmation +
  retrieval method/date + quote rule). No fetch.
- **Crypto-D3b re-provision** — a documented spot OHLCV fetch for BTC/ETH/SOL. **This
  is a fetch and needs explicit fetch authorization.**

Plus (later, optional): second-source cross-check fetch (Kraken/Coinbase) before any
edge claim; perp/funding fetch only if perps are ever enabled (blocked until funding
frozen).

## 8. What is still blocked

- **No crypto strategy** specified, frozen, or tested (Crypto-D4 not started).
- **Provenance** of the local files unpinned → not yet a Crypto-D4 backing dataset.
- **Spot-vs-perp** undetermined for the local files (hard gate).
- **Perps** blocked until funding sourced + frozen.
- **2026 data** blocked for any IS/OOS use until separately authorized.
- **No exchange API execution / broker / paper / live** anywhere in this lane.
- **No old crypto result/parameter** reused as evidence.

## 9. Final recommendation

**DATA_NOT_READY_FETCH_AUTH_REQUIRED.** This is **not** a "no data" situation and
**not** a QA failure: clean BTC/ETH/SOL daily USDT candles exist locally and pass every
structural QA check with feasible IS/OOS windows. They are **not ready only because
provenance is unpinned** — specifically spot-vs-perp is undetermined (a hard gate) and
no source exchange / retrieval method is documented for these exact files. Readiness
requires either **(A)** retroactively pinning provenance incl. explicit SPOT
confirmation, or **(B)** a separately authorized provenance-documented re-provision
(**Crypto-D3b**). **Crypto-D4 (spec) must NOT start until the provenance gap closes.**
Crypto-D4 is **NOT authorized by this memo.**

## 10. Forbidden actions (this lane)

`no_strategy_test` · `no_exchange_api_execution` · `no_broker` · `no_paper_trading` ·
`no_live_trading` · `no_perps_until_funding_rules_frozen` · `no_new_data_fetch` ·
`no_code` · `no_backtest` · `no_optimization` · `no_parameter_sweep` ·
`no_old_crypto_strategy_rerun` · `no_using_old_results_as_proof` ·
`no_mixing_crypto_with_futures_validation_claims` · `do_not_touch_s30_or_futures_branches` ·
`jarvis_templates_base_hydra_untouched` · `no_staging` · `no_commit`.

---

**Final line:** *“Crypto-D3 is data-source + QA provisioning only; clean local
BTC/ETH/SOL daily USDT candles exist and are structurally QA-clean, but their
provenance is unpinned (spot-vs-perp undetermined), so the verdict is
DATA_NOT_READY_FETCH_AUTH_REQUIRED — no crypto strategy is specified, validated,
paper-ready, live-ready, or authorized for execution.”*

**Trading recommendation:** NONE. Data provisioning + QA only. Local BTC/ETH/SOL daily
USDT candles are structurally CLEAN but provenance-unpinned, so verdict
**DATA_NOT_READY_FETCH_AUTH_REQUIRED**. No crypto strategy is validated, paper-ready,
or live-ready; perps remain blocked; crypto stays a separate research lane; S30 and the
futures branches are untouched and S30 remains PARKED after IS_FAIL.
