# Crypto-D3a — Existing-Data Provenance Pin Attempt (provenance/memo only)

**This is a provenance-pin attempt over EXISTING local crypto data. No data fetch, no
network, no exchange API, no broker, no strategy code, no backtest, no IS/OOS run, no
optimization, no parameter sweep, no paper/live, no modification of any crypto CSV/data
file, no S30/futures-branch changes, no JARVIS/templates/base.html/hydra changes, no
staging, no commit.** It searches local files only to determine whether the provenance
of the existing `data/frozen_regime_inputs/` BTC/ETH/SOL daily candles can be pinned.

- **Created:** 2026-05-30
- **HEAD at finalize:** `ce62a71` (automation draft was at `2849279`; background
  automation advances HEAD continuously). Crypto-D1 `c8a59fe`, Crypto-D2 `a035ab0`,
  and Crypto-D3 `31ebdaf` all confirmed ancestors. Nothing staged; this folder is
  untracked. S30 untouched and remains PARKED after IS_FAIL.
- **Read-only:** local README/manifests/reports/tools/config only. No CSV/data file was
  modified. Nothing fetched.

---

## 1. Crypto-D3 summary (carried in)

Crypto-D3 verdict was **DATA_NOT_READY_FETCH_AUTH_REQUIRED**: clean local BTC/ETH/SOL
daily USDT candles exist in `data/frozen_regime_inputs/` (BTC/ETH 2020-01-01→2026-05-29,
2341 rows; SOL 2020-08-11→2026-05-29, 2118 rows; 0 dup / 0 invalid OHLC / 0 zero-or-neg
volume / 0 missing calendar days; one USDT quote) — but were blocked because provenance
(source exchange, spot-vs-perp, retrieval method) was unpinned. Crypto-D3a attempts to
close that gap from local evidence only.

## 2. Evidence searched (local only, no network)

- `data/frozen_regime_inputs/README.md` (drop-zone contract).
- `reports/crypto_regime_data_acquisition_manifest.json` (acquisition manifest).
- `tools/stage_frozen_regime_csv.py` (frozen-CSV staging/normalizer).
- `tools/regime_shadow_fresh_data_update.py` (Phase 5F fresh-data orchestrator).
- `tools/fetch_binance_crypto_daily_frozen.py` (Phase 3H Binance daily klines fetcher).
- Repo-wide grep for `frozen_regime_inputs`, daily aggregation/resample, `btcusdt_1d`,
  Binance/Kraken/Coinbase, spot/perp, USDT, SPARTA_RESEARCH_LAB.
- Directory listing of `data/frozen_regime_inputs/` (current files + `.superseded.*`
  backups).

## 3. Evidence found

**Producer code path identified (the sanctioned producer of these exact files):**

- **`tools/fetch_binance_crypto_daily_frozen.py` (Phase 3H)** — docstring: *"Fetches
  public **spot** daily klines for BTCUSDT / ETHUSDT / SOLUSDT from the Binance public
  market data endpoint and writes a canonical frozen CSV under
  `data/frozen_regime_inputs/`."*
  - Endpoint pinned: `BINANCE_PUBLIC_KLINES_URL = "https://api.binance.com/api/v3/klines"`
    — Binance **spot** market data API (perps would be `fapi.binance.com`). URL guard
    rejects `account/order/trade/userdata/signed/signature/apikey/secret`. No API key,
    no signed/account/trading endpoints.
  - Symbols pinned: `ALLOWED_SYMBOLS = {BTCUSDT, ETHUSDT, SOLUSDT}` (USDT-quoted).
  - Interval pinned: `ALLOWED_INTERVAL = "1d"` — **daily-native**, fetched directly at
    1d (NOT aggregated from 1h).
  - UTC boundary: kline `open_time` (ms epoch) → `datetime.fromtimestamp(.., tz=utc)
    .strftime("%Y-%m-%d")`; Binance 1d klines are anchored to **00:00 UTC**.
- **`tools/regime_shadow_fresh_data_update.py` (Phase 5F)** orchestrates the refresh:
  crypto refresh is via `fetch_binance_crypto_daily_frozen.fetch_and_stage`, gated behind
  explicit `--allow-network-for-crypto`, `CRYPTO_INTERVAL = "1d"`, whitelist
  `BTCUSDT/ETHUSDT/SOLUSDT` only, endpoint `api.binance.com/api/v3/klines` only.
- **`reports/crypto_regime_data_acquisition_manifest.json`** corroborates a Binance
  **spot** lineage (`source: data.binance.vision`) but documents a **1h** acquisition
  into a **different** folder (`SPARTA_RESEARCH_LAB\...\data\raw`) — supportive context,
  **not** the 1:1 record for these daily files.

**Live run-record sha256 linkage (INDEPENDENTLY VERIFIED — ties the exact on-disk bytes
to the Binance-spot pipeline):**

- `reports/regime_intelligence/shadow_validation/health/latest_status.json` and the
  matching run-log `reports/regime_intelligence/shadow_validation/logs/fresh_data_update_20260530T001513Z.json`
  (run finished `2026-05-30T00:15:13Z`) record, per file, the producing pipeline's
  `actions_taken=[update_crypto, merge_crypto_shards, ...]`, `args.update_crypto=true`
  with `allow_network_for_crypto=true`, `symbols=[BTCUSDT,ETHUSDT,SOLUSDT]`,
  `interval=1d`, and a per-file sha256 + last-date.
- **I recomputed the sha256 of the three on-disk daily files and they EXACTLY match the
  recorded shas:** BTC `863182c1…ffd00d`, ETH `8b987ce5…446aac`, SOL `3ee27dbe…42da6`.
  This is a **live linkage** proving the current on-disk bytes ARE the output of the
  Binance-spot `update_crypto`→`merge_crypto_shards` pipeline — confirming source
  provenance beyond inference.
- **The same record also confirms the immutability gap:** the `update_crypto` action
  fetched only the **2026-05-29 single-row shard** (`rows_written: 1`, output
  `…_2026-05-29_2026-05-29.csv`) and then merged it into the cumulative
  `…_2020-01-01_2026-05-29.csv`. The dataset is produced by **daily incremental
  append-merge**, so its bytes (and end date) change every day — exactly why no fixed
  immutable snapshot exists yet.

**Dataset-stability evidence (the remaining gap):**

- `data/frozen_regime_inputs/` is **gitignored** (not a committed frozen snapshot).
- **72 `*.csv.superseded.<timestamp>` backups** exist; filenames roll the end date
  forward over time (…2026-05-20, -21, -22, -26, -27, …-29). The "frozen" file is
  **live daily-refreshed** by the Phase 5F updater — its content and end date change
  day to day. There is **no committed, content-hashed immutable snapshot** of a specific
  retrieval for these exact files.

## 4. Provenance fields checklist

| Field | Status | Value / evidence |
|---|---|---|
| Source / exchange / vendor | **PINNED** | Binance public market data — `api.binance.com/api/v3/klines` |
| Spot vs perp | **PINNED → SPOT** | spot endpoint (perp = `fapi`); fetcher docstring "public spot daily klines"; URL guard forbids account/order/trade/signed |
| Symbol convention | **PINNED** | `BTCUSDT / ETHUSDT / SOLUSDT` (USDT majors allowlist) |
| Quote currency | **PINNED** | USDT (consistent across all three) |
| Timeframe origin (native vs aggregated) | **PINNED → daily-native** | `ALLOWED_INTERVAL="1d"`, fetched directly at 1d (not 1h→1d aggregation) |
| UTC / day boundary | **PINNED** | `open_time`→UTC date, `%Y-%m-%d`; Binance 1d anchored 00:00 UTC |
| Retrieval method / source script | **PINNED** | `tools/fetch_binance_crypto_daily_frozen.py` (`fetch_and_stage`), gated `--allow-network-for-crypto`; orchestrated by `tools/regime_shadow_fresh_data_update.py` |
| Date range | **PINNED (per file)** | BTC/ETH 2020-01-01→2026-05-29; SOL 2020-08-11→2026-05-29 |
| 2026 inclusion / seal | **PINNED** | 2026 present (149 bars/symbol) → **must be sealed** (Crypto-D1 §10) |
| Immutable frozen snapshot (content-hash pinned) | **NOT MET** | gitignored + 72 `.superseded.*` backups = **live daily-refreshed**; end date rolls forward; no committed per-file sha256 |

**9 of 10 source-provenance fields are now PINNED.** The single unmet item is dataset
**immutability** — not a source-provenance gap, but a dataset-stability gap.

## 5. Final provenance verdict

**PROVENANCE_PARTIAL_NOT_READY.**

The **source provenance is now pinned** (Binance public **spot** klines,
`api.binance.com/api/v3/klines`, USDT, **daily-native 1d**, UTC 00:00 boundary,
retrieval script identified), and **independently verified** by a live sha256 linkage
(on-disk file hashes match the producing pipeline's run-record, §3) — a clear upgrade
from Crypto-D3's "UNKNOWN". **No new fetch is required** to establish origin. **But the data is NOT yet ready** because the
on-disk dataset is a **live, daily-refreshed, gitignored copy**, not an immutable,
content-hashed frozen snapshot. A validation-factory backing dataset must be frozen and
hash-pinned (like the offline futures CSVs), so a tuned/validated result is reproducible
against fixed bytes.

## 6. If pinned — proceed conditions (partial: source pinned, freeze still needed)

Because the source is pinned but the dataset is not frozen, the data **cannot** proceed
to a Crypto-D4 spec until it is frozen into the factory. The applicable rules once
frozen:
- **2026 sealing rule:** drop all 2026 bars; IS = 2020–2023, OOS = 2024–2025 (Crypto-D1
  §10). 2026 stays blocked unless separately authorized.
- **SOL per-symbol window:** start 2020-08-11 (listing); tri-symbol joint tests align to
  the common 2020-08-11+ index (or pre-registered per-symbol windows).
- **Quote rule:** USDT, documented, reconciled vs USD/USDC (no silent mixing).

## 7. If not ready — recommendation

**Recommended next step: a factory-internal FREEZE (no fetch).** Since clean local data
with pinned source provenance already exists, the correct action is **not** a re-fetch
but a **separately authorized freeze/transcode** step that:
1. Snapshots the current `data/frozen_regime_inputs/{btcusdt,ethusdt,solusdt}_1d_*.csv`
   into the **factory's own data area** under a frozen naming convention.
2. **Seals out 2026** at freeze time (keep ≤ 2025-12-31).
3. Records a **per-file provenance sidecar**: source = Binance spot `api/v3/klines`,
   USDT, 1d-native, UTC, retrieval script + snapshot date, and the **sha256** of each
   frozen file.
4. Commits that immutable snapshot + sidecar (so the dataset is reproducible).

This is a **freeze, not a fetch** — no network. (A separate **Crypto-D3b re-provision**
with its own explicit `--allow-network-for-crypto` authorization remains the
alternative if a clean re-pull is preferred over snapshotting the live copy.) **Neither
freeze nor fetch is authorized by this memo.**

## 8. Forbidden actions (this lane)

`no_strategy_testing` · `no_exchange_api_execution` · `no_paper_or_live` · `no_broker` ·
`no_network` · `no_data_fetch` · `no_code` · `no_backtest` · `no_optimization` ·
`no_parameter_sweep` · `no_modification_of_crypto_csv_or_data_files` ·
`no_perps_until_funding_rules_frozen` · `no_using_old_results_as_proof` ·
`no_mixing_crypto_with_futures_validation_claims` · `do_not_touch_s30_or_futures_branches` ·
`jarvis_templates_base_hydra_untouched` · `no_staging` · `no_commit`.

---

**Final line:** *“Crypto-D3a pins the SOURCE provenance of the existing local crypto
data (Binance public spot daily klines, USDT, UTC) but the on-disk dataset is a live,
gitignored, daily-refreshed copy, not an immutable frozen snapshot — verdict
PROVENANCE_PARTIAL_NOT_READY; a separately authorized factory-internal freeze (no fetch)
is the next step, and no crypto strategy is specified, validated, paper-ready,
live-ready, or authorized for execution.”*

**Trading recommendation:** NONE. Provenance pin only. Source provenance is pinned
(Binance spot, USDT, daily-native, UTC) but the dataset is not yet a frozen immutable
snapshot, so verdict **PROVENANCE_PARTIAL_NOT_READY**. No crypto strategy is validated,
paper-ready, or live-ready; perps remain blocked; crypto stays a separate research lane;
S30 and the futures branches are untouched and S30 remains PARKED after IS_FAIL.
