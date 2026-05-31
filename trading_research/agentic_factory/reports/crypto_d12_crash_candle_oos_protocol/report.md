# Crypto-D12 — Crash-Candle Reversion v1 OOS Protocol (PRE-REGISTRATION, protocol only)

**This is an OOS-PROTOCOL step only.** No OOS run, no 2024/2025/2026 rows read, no
backtest, no PnL simulation, no optimization, no parameter or rule change, no data
fetch, no network, no exchange API, no broker, no paper, no live. Frozen data
untouched. S30/futures untouched; JARVIS/`templates/base.html`/hydra untouched.
**Not staged, not committed.**

- **Created:** 2026-05-30
- **HEAD at protocol:** `923e786` (Crypto-D11 IS_WATCH) or descendant — factory
  tree clean, nothing staged, no active OOS run.
- **Binding context (committed):** D7 closeout `344a7e7`, D8 audit `ca4d9eb`,
  D9 frozen spec `6e0c85b`, D10 engine+tests `ce499c6`, D11 IS baseline `923e786`;
  data freeze D3b `5b3d94c`, ratified D3c `fe5594f`.

---

## 1. Purpose

Pre-register the OOS rules and the PASS/WATCH/FAIL gates **before any 2024–2025 bar
is read.** Crypto-D11 returned **IS_WATCH** (not IS_CONTINUE): the IS profile is
strong on BTC primary (69 trades, net expectancy +0.95%/trade, top-3 removal
positive on all symbols, 3/3 symbols friction-positive) but the
**single-year-dominance hard gate FAILED** — BTC 2020 = 96% of net, combined 2021
= 98%, and **every symbol lost in the 2022 bear.** This protocol fixes the OOS
judgment in advance so the OOS cannot be rationalised after the fact, and so the
OOS explicitly answers the one question D11 could not: **is any edge regime-robust,
or just another single-period artifact?**

## 2. Frozen strategy reference

| Item | Commit |
|---|---|
| Frozen spec (CCR1 v1) | `6e0c85b` (Crypto-D9) |
| Engine + tests | `ce499c6` (Crypto-D10) |
| IS baseline (IS_WATCH) | `923e786` (Crypto-D11) |

Engine module: `engine/crypto_crash_candle_reversion.py`. **No rule changes are
allowed.** The OOS run MUST use the exact frozen CCR1 v1 rules with zero parameter
freedom — no threshold change, no added filter, no exit change, no variant. Any
change is a NEW spec id and a fresh ladder, never an edit here.

## 3. OOS window

- **Window:** 2024-01-01 → 2025-12-31 **ONLY**.
- **2026:** EXCLUDED (sealed).
- **Symbols:** BTC / ETH / SOL spot — **no other symbols, no perps.**
- **Data:** the frozen `data_crypto/spot_binance_usdt_1d_2020_2025/` snapshot
  (D3b `5b3d94c`), OOS slice only.
- **Warmup:** v1 has **no** trend/SMA filter, so OOS needs **no** pre-2024 warmup;
  slice each symbol to 2024–2025 before any computation. A late-2025 entry that
  cannot complete its 3-bar horizon by 2025-12-31 exits `data_end` at the
  2025-12-31 close — **no 2026 bar is read.**
- **Boundary seal:** `rows_after_2025_used` MUST be **0**.

## 4. OOS run rules (exact frozen CCR1 v1)

- **Long-only spot.**
- **Signal:** `ret_1d ≤ −5%`, `ret_1d = close_t / close_{t-1} − 1`.
- **Entry:** next daily open `open_{t+1}`.
- **Exit:** close of the 3rd bar after entry (entry bar counts as bar 1;
  `exit_index = entry_index + 2`).
- **No stop. No profit target. No trend filter. No confirmation filter.**
- **One position per symbol; ignore overlapping signals; no pyramiding.**
- **No parameter changes. No reruns/variants** — the OOS is run **once** per
  symbol; no second look, no parameter sweep, no alternative threshold, no
  cherry-picked sub-window.
- **Friction:** per-trade additive, base 0.30% / stress 0.45% (engine returns
  GROSS).

## 5. Required OOS metrics

For **each symbol and combined**:

- trade count
- gross total return %
- net total @0.30% friction
- net total @0.45% stress friction
- expectancy (avg net trade @0.30%)
- PF-like gain/loss ratio (gross / net0.30 / net0.45)
- win rate (gross and net base)
- best / worst trade
- **year-by-year 2024 vs 2025** (trade count + net base per year)
- top-3 winner removal (net @0.30%)
- **single-year dominance** (max OOS-year share of combined net)
- **BTC primary standalone performance** (must carry its own evidence)
- **2/3-symbol corroboration** (count of symbols net-positive after 0.30%)

Plus **data QA** per symbol: rows, date range, duplicate timestamps, invalid OHLC,
zero/neg volume, `rows_after_2025_used` (must be 0).

## 6. PASS / WATCH / FAIL gates (pre-registered)

### FAIL if ANY of:

- BTC primary net @0.30% ≤ 0
- BTC trade count < 10 OOS trades
- combined net @0.45% ≤ 0
- combined net PF @0.30% < 1.10
- top-3 removal makes combined net ≤ 0
- BTC top-3 removal ≤ 0
- only one symbol positive after friction
- one OOS year contributes **>80%** of combined net **AND** the other year is ≤ 0
- any data QA defect
- 2026 contamination (any 2026 row used)
- rule mismatch (any deviation from the frozen CCR1 v1 rules)

### WATCH if:

- BTC positive but weak
- combined positive but PF < 1.30
- 2/3 symbols positive but one major symbol weak
- top-3 removal positive but thin
- one year dominates **60–80%** of combined net
- trade count low but not fail

### PASS only if ALL of:

- BTC net @0.30% > 0
- BTC trade count ≥ 10
- combined net @0.45% > 0
- combined PF @0.30% ≥ 1.30
- top-3 removal positive for **BTC AND combined**
- at least 2/3 symbols positive after friction
- both 2024 and 2025 are **not** contradictory
- no single-year dominance > 60%
- no QA defect
- exact frozen rules used

**Precedence:** FAIL triggers are checked **first** and are absolute — any single
FAIL trigger forces FAIL regardless of other metrics. PASS requires **all** PASS
conditions simultaneously. Anything that is neither a clean PASS nor a FAIL is
WATCH. **ETH/SOL strength may NOT rescue a BTC-primary FAIL.**

> Note: OOS gates are deliberately calibrated to the shorter 2-year OOS window
> (BTC ≥10 trades, combined PF ≥1.10 for FAIL / ≥1.30 for PASS) — looser than the
> 4-year IS gates, but the **regime-robustness** bar is *stricter*: per the D11
> weakness, single-year/regime dominance is a **first-class** OOS criterion
> (>80%-with-other-year-≤0 ⇒ FAIL; 60–80% ⇒ WATCH; >60% blocks PASS).

## 7. Interpretation

- **PASS is NOT paper-ready** — it means the IS edge survived a single
  pre-registered OOS test. Later ladder steps (significance, full sequence risk,
  regime, multi-asset, walk-forward, friction, final decision) still remain.
- **WATCH means continue validation only** — the family may continue down the
  ladder under separate authorization, not deploy.
- **FAIL means park** crash-candle v1 — **no OOS rerun, no second look, no
  parameter tuning.**
- **If OOS fails from single-year/single-period dominance, do NOT tune parameters
  or add filters** to chase robustness — that overfits to the OOS. Park the family
  or open a NEW pre-registered spec id.

## 8. Forbidden actions (this lane)

`no_oos_run_until_this_protocol_is_committed` · `no_parameter_changes` ·
`no_optimization` · `no_paper_or_live` · `no_exchange_api_execution` ·
`no_broker` · `no_perps` · `no_adding_confirmation_filters_after_oos` ·
`no_2026_use` · `no_data_fetch` · `no_network` · `no_modification_of_frozen_data`
· `do_not_touch_s30_or_futures` · `jarvis_templates_base_hydra_untouched` ·
`no_staging` · `no_commit`.

## 9. Final line

**“Crypto-D12 is an OOS protocol only; no OOS run, crypto backtest, exchange API,
paper trading, or live trading is authorized.”**

---

**Trading recommendation:** NONE — OOS protocol pre-registration only. The OOS run
itself is a SEPARATE, not-yet-authorized step (Crypto-D13). Crash-Candle Reversion
v1 remains **IS_WATCH**; **OOS 2024–2025 and 2026 stay SEALED** until this protocol
is committed and a D13 OOS run is separately authorized. No crypto strategy is
validated, paper-ready, or live-ready; perps remain blocked; crypto stays a
separate research lane; **S30 stays PARKED and the futures branches are untouched.**
