# Crypto-D4 — Choose & Freeze ONE First Crypto Strategy Spec (memo only)

**This is a SPEC / MEMO step only.** No code, no backtest, no IS/OOS run, no
optimization, no parameter sweep, no strategy test, no data fetch, no network, no
exchange API, no broker, no paper/live. No S30/futures-branch changes, no
JARVIS/`templates/base.html`/hydra changes, no staging, no commit. Frozen data was
used **metadata/read-only only** (row counts, ranges, hashes) — **no bars were
loaded, scanned, or backtested.**

- **Created:** 2026-05-30
- **HEAD at memo:** `5b3d94c` (Crypto-D3b data freeze) — confirmed ancestor of HEAD;
  factory tree clean; nothing staged.
- **Binding context (read-only):** Crypto-D1 protocol `c8a59fe`, Crypto-D2 inventory
  `a035ab0`, Crypto-D3 data-source/QA `31ebdaf`, Crypto-D3a provenance `ae25f43`,
  Crypto-D3b freeze `5b3d94c`.

---

## 1. Crypto data readiness context

Frozen snapshot `spot_binance_usdt_1d_2020_2025` — **DATA_READY_FOR_CRYPTO_D4_SPEC**.
Binance public **spot** daily klines, **USDT**, `1d` daily-native, **UTC 00:00**.

| Symbol | Rows | Range | SHA256 (head) |
|---|---|---|---|
| BTCUSDT | 2192 | 2020-01-01 → 2025-12-31 | `d87742b8…` |
| ETHUSDT | 2192 | 2020-01-01 → 2025-12-31 | `4a4d7b08…` |
| SOLUSDT | 1969 | 2020-08-11 → 2025-12-31 | `bd8b28f1…` |

QA CLEAN (0 dup, 0 invalid OHLC, 0 zero/neg vol, 0 missing calendar days); 2026
sealed out. Perps BLOCKED until funding sourced + frozen.

## 2. Candidate comparison

| # | Candidate | Trade count | Top-winner dep. risk | Friction sens. | Multi-asset testability | Too close to rejected? | Clean entry-significance? | Verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | Trend / Donchian breakout | LOW | **HIGH** (the universal killer) | Moderate | Good | **Very close** (old crypto Donchian + parked futures trend family) | Partial | REJECT first pick |
| 2 | **Mean reversion after large down day in uptrend** | **MOD-HIGH** | **LOWER** (fixed horizon caps winners) | Mod-high (testable) | Good | Adjacent but distinct from ema_pullback continuation | **Very clean** (fixed horizon) | **SELECT** |
| 3 | Vol compression → expansion breakout | Mod-low | Mod-high | Moderate | OK | Novel | Harder (2-param entry) | REJECT first pick |
| 4 | Cross-asset momentum (BTC leads ETH/SOL) | Moderate | Moderate | Moderate | **Weak paradox** (corroboration baked into signal) | Novel-ish | Harder | REJECT first pick |
| 5 | Weekend/day-of-week seasonality | HIGH | LOW | **Very high** | OK | Novel | Trivial | REJECT first pick (likely friction-dominated FAIL) |
| 6 | Regime / no-trade overlay only | N/A | N/A | N/A | N/A standalone | Old HMM historical-only | N/A | EXCLUDE (an overlay is not a strategy) |

**Why each non-selected candidate loses as a *first* test:** (1) and (5) are
structurally likely to FAIL — (1) on top-winner concentration (the exact gate that
parked every futures branch), (5) on friction-domination/decay; (3) and (4) add
parameter freedom or undercut the multi-asset robustness gate; (6) has no entry of
its own. See `report.json` §2 for the full per-candidate hypothesis / why-edge /
why-fail / data-requirement breakdown.

## 3. Selected strategy

**SELECT candidate #2 → `CODR-1` (Crypto Oversold-Dip Reversion in Uptrend) v1.**
Verdict: **STRATEGY_SELECTED.**

Rationale: the universal killer across this factory is **top-winner dependence**.
CODR-1 minimizes it (a fixed 5-bar holding horizon caps winner size; many small
trades), delivers the **highest expected trade count** (statistical power), has the
**cleanest fixed-horizon entry-significance test**, supports strong **identical-spec
BTC/ETH/SOL corroboration**, needs only **daily spot** data, and is **distinct** from
the already-parked trend-continuation family.

## 4. Frozen spec — `CODR-1` v1 (pre-registered, no parameter freedom)

- **Direction:** LONG ONLY (spot; no shorting, no leverage).
- **Symbols:** BTCUSDT, ETHUSDT, SOLUSDT. **Primary:** BTCUSDT.
- **Timeframe:** daily, UTC 00:00. **Data:** frozen `spot_binance_usdt_1d_2020_2025` (hashes §1), read-only.
- **Windows:**
  - **IS:** BTC/ETH `2020-01-01..2023-12-31`; **SOL `2020-08-11..2023-12-31` (PARTIAL IS** — ~4.4 months short of a 2020 start; **reduced power, reported separately, never padded or stitched).**
  - **OOS:** `2024-01-01..2025-12-31` **SEALED** (one-shot after a committed protocol hash in a later step).
  - **2026:** SEALED OUT (absent from snapshot; blocked unless separately authorized).
- **Frozen parameters (single constants — NO sweep):**
  - **Trend filter:** `close_t > SMA200_t` (200-day SMA of close).
  - **Shock trigger:** daily return `ret_t = close_t/close_{t-1} − 1 ≤ −0.07` (a −7% or worse down day).
  - **Entry timing:** enter LONG at **`open_{t+1}`** when BOTH `close_t > SMA200_t` AND `ret_t ≤ −0.07` (signal uses only data through `close_t`; fill next open; **no look-ahead**).
  - **Position rule:** one open position per symbol; **no pyramiding** (ignore new triggers while in a position).
  - **Protective stop:** if a **daily close ≤ entry_fill × 0.90** (−10%), exit at that day's **close** (close-based — avoids unrealistic intrabar fills on daily data).
  - **Time stop:** otherwise exit at the **close of the 5th daily bar** after entry (fixed 5-bar horizon).
  - **Exit priority:** first of {protective stop, time stop} to trigger.
  - **Profit target:** **NONE in v1** — the fixed horizon intentionally caps winners (reduces top-winner dependence) and keeps the random-entry null clean.
- **Position accounting:** fixed notional, no leverage, no intra-test compounding (clean per-trade R); cash account; per-trade return = `exit/entry − 1 − costs`; reported in % and R.
- **Fees/slippage:** spot taker **0.10%/side** (0.20% round trip) + slippage **0.05%/side** ≈ **0.30% round-trip**, applied every trade (Crypto-D1 §8).

## 5. Validation ladder (same factory ladder as futures)

D5 engine+tests (no run) → D6 IS baseline (hard OOS seal) → D7 OOS protocol
pre-registration (committed hash) → D8 OOS once (one-shot) → D9 entry significance
(fixed-horizon random-entry) → D10 sequence risk / Monte Carlo (+ top-winner
removal) → D11 regime breakdown → D12 multi-asset robustness (BTC/ETH/SOL) → D13
walk-forward → D14 friction stress → D15 final decision gate. **PAPER/LIVE
unreachable on the default path.**

## 6. Pass / Watch / Fail gates

- **Enough trades:** ≥ 30/symbol on IS (else WATCH; SOL partial-IS expected thinner — flagged).
- **Positive expectancy:** mean per-trade R > 0 after costs.
- **Profit factor:** > 1.3 (pre-registered).
- **Top-3-winner dependence (HARD):** net stays positive after removing the top 3 winners — *the gate that parked every futures branch.*
- **Sequence risk:** Monte Carlo shuffle + bootstrap; 5th-pct terminal P&L not catastrophic.
- **Friction:** survives the ~0.30% base round-trip AND a +50% friction stress.
- **Multi-asset corroboration:** same-sign positive expectancy on ≥ 2 of 3 symbols.
- **No promotion** regardless of result.

`PASS` = survives all IS gates → proceed to OOS pre-registration (research only).
`WATCH` = mixed/thin → park. `FAIL` = stop the branch.

**Entry-significance protocol:** fixed-horizon random-entry permutation — same
symbol/trade-count/5-bar horizon/−10% stop, random eligible entry dates, build the
null mean-return distribution; real edge must beat the 95th percentile.

**Sequence-risk protocol:** trade-order shuffle + bootstrap of per-trade returns;
terminal-P&L and max-DD distributions; top-winner-removal (drop top 1/3/5).

**Multi-asset robustness:** identical frozen spec on all three; per-symbol reporting;
SOL partial-IS power stated honestly; edge not confined to one coin.

**Anti-overfit:** single pre-registered constants (no ranges/sweeps); identical spec
across symbols; one-shot OOS after a committed hash, no post-OOS tuning; no parameter
import from old crypto work; any constant change = a NEW spec id + fresh ladder.

## 7. Forbidden actions (this lane)

`no_code` · `no_backtest` · `no_is_oos_run` · `no_optimization` ·
`no_parameter_sweep` · `no_strategy_test` · `no_data_fetch` · `no_network` ·
`no_exchange_api_execution` · `no_broker` · `no_paper_or_live` ·
`no_modification_of_data_files` · `no_perps_until_funding_rules_frozen` ·
`no_using_old_results_as_proof` · `no_mixing_crypto_with_futures_validation_claims` ·
`do_not_touch_s30_or_futures_branches` · `jarvis_templates_base_hydra_untouched` ·
`no_staging` · `no_commit`.

## 8. Final line

**“Crypto-D4 is a frozen strategy-spec step only; no crypto backtest, OOS, exchange
API, paper trading, or live trading is authorized.”**

---

**Trading recommendation:** NONE. Spec/memo only. One first crypto strategy
(**CODR-1** — long-only oversold-dip reversion inside an uptrend, daily BTC/ETH/SOL
spot USDT) is now pre-registered and frozen for future testing, but it has **not**
been coded, backtested, IS/OOS-run, or validated. No crypto strategy is paper-ready
or live-ready; perps remain blocked; crypto stays a separate research lane; S30 and
the futures branches are untouched and S30 remains PARKED after IS_FAIL.
