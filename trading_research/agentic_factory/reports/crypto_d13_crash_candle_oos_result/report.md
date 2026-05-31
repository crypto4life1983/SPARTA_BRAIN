# Crypto-D13 — Crash-Candle Reversion v1 OOS Result (BTC/ETH/SOL spot, 2024–2025)

**This is the OOS RUN step — run ONCE under the committed Crypto-D12 protocol.** The
OOS slice (2024–2025 ONLY) was read read-only; the frozen engine ran exactly once
per symbol; **no 2026 bar, no 2020–2023 IS bar** entered the engine; no rerun, no
variant, no parameter change, no optimization, no network, no exchange API, no
broker, no paper, no live. Frozen data untouched. S30/futures untouched;
JARVIS/`templates/base.html`/hydra untouched. **Not staged, not committed.**

- **Created:** 2026-05-30
- **HEAD at run:** `8b14308` (Crypto-D12 OOS protocol). Factory tree clean, nothing
  staged, one-shot runner deleted before pytest.
- **Binding context (committed):** D9 spec `6e0c85b`, D10 engine+tests `ce499c6`,
  D11 IS baseline `923e786`, D12 OOS protocol `8b14308`; data freeze D3b `5b3d94c`,
  ratified D3c `fe5594f`.

---

## 1. Protocol & engine reference

| Item | Commit |
|---|---|
| OOS protocol (gates pre-registered) | `8b14308` (Crypto-D12) |
| Frozen spec (CCR1 v1) | `6e0c85b` (Crypto-D9) |
| Engine + tests | `ce499c6` (Crypto-D10) |
| IS baseline (IS_WATCH) | `923e786` (Crypto-D11) |

Engine module: `engine/crypto_crash_candle_reversion.py`. **Exact frozen CCR1 v1
rules, zero parameter freedom:** long-only spot; signal `ret_1d ≤ −5%`; entry next
daily open `open_{t+1}`; exit close of the 3rd bar (`exit_index = entry_index + 2`);
no stop, no target, no trend filter, no confirmation filter; one position per
symbol; ignore overlapping signals; **run once per symbol, no variants.** Friction
per-trade additive: base 0.30% / stress 0.45% (engine returns GROSS).

## 2. IS baseline reference (the gate that flipped)

Crypto-D11 returned **IS_WATCH**. The IS **top-3-winner-removal gate PASSED** on BTC
(+15.76%) and combined (+314.55%); the IS failure was **single-year dominance** (BTC
2020 = 96% of net, combined 2021 = 98%; every symbol lost the 2022 bear). The OOS
test was pre-registered to answer whether any edge is regime-robust or a single-period
artifact.

## 3. Inputs & OOS seal

| Symbol | File | OOS window | Full rows | OOS rows | rows>2025 | rows<2024 |
|---|---|---|---|---|---|---|
| BTC | `BTCUSDT_1d_2020_2025.csv` | 2024-01-01..2025-12-31 | 2192 | 731 | 0 | 0 |
| ETH | `ETHUSDT_1d_2020_2025.csv` | 2024-01-01..2025-12-31 | 2192 | 731 | 0 | 0 |
| SOL | `SOLUSDT_1d_2020_2025.csv` | 2024-01-01..2025-12-31 | 1969 | 731 | 0 | 0 |

Each symbol was sliced to **2024 ≤ year ≤ 2025 BEFORE any computation.** **No 2026
bar and no 2020–2023 IS bar entered the engine** (`rows_after_2025_used = 0` and
`rows_before_2024_used = 0` for all three). All exits are `time_exit` — no
`data_end` artifact, so every OOS signal completed its full 3-bar horizon inside
2024–2025. **OOS 2026 remains SEALED.**

## 4. Data QA (OOS slice)

| Check | BTC | ETH | SOL |
|---|---|---|---|
| Rows | 731 | 731 | 731 |
| Range | 2024-01-01→2025-12-31 | 2024-01-01→2025-12-31 | 2024-01-01→2025-12-31 |
| Duplicate ts | 0 | 0 | 0 |
| Invalid OHLC | 0 | 0 | 0 |
| Zero/neg vol | 0 | 0 | 0 |
| Rows >2025 used | 0 | 0 | 0 |
| Rows <2024 used | 0 | 0 | 0 |

QA verdict: **CLEAN** — no defect, no IS contamination, no 2026 contamination.

## 5. Per-symbol OOS metrics (gross unless noted; net = per-trade additive friction)

| Metric | BTC (primary) | ETH | SOL |
|---|---|---|---|
| Trades | 18 | 40 | 55 |
| Gross total | +18.73% | −21.33% | +81.79% |
| Net total @0.30% | **+13.33%** | **−33.33%** | +65.29% |
| Net total @0.45% | +10.63% | −39.33% | +57.04% |
| Avg trade (base) | +0.74% | −0.83% | +1.19% |
| Median trade (base) | +0.87% | −0.56% | +1.27% |
| Win rate (gross) | 55.56% | 50.00% | 63.64% |
| Win rate (net base) | 50.00% | 50.00% | 61.82% |
| PF (gross) | 1.663 | 0.841 | 1.605 |
| PF (net 0.30%) | 1.434 | 0.762 | 1.462 |
| PF (net 0.45%) | 1.331 | 0.724 | 1.394 |
| Best trade | +14.19% | +18.56% | +25.69% |
| Worst trade | −12.16% | −19.07% | −15.05% |
| Exits | {time_exit: 18} | {time_exit: 40} | {time_exit: 55} |
| **Top-3 removal (net 0.30%)** | **−12.21% ❌** | −73.79% ❌ | +10.40% ✅ |
| Single-year dominance (base) | 65.4% (2025) | — (net-neg) | 67.7% (2024) |

### Year-by-year net base (by entry year)

- **BTC** — 2024: +4.61% (11t), 2025: +8.72% (7t). Both years positive.
- **ETH** — 2024: **−31.01%** (17t), 2025: **−2.32%** (23t). **Both years negative.**
- **SOL** — 2024: +44.19% (27t), 2025: +21.10% (28t). Both years positive.

## 6. Combined OOS metrics (BTC+ETH+SOL pooled)

- Trades: **113** (BTC 18, ETH 40, SOL 55)
- Gross total **+79.19%**; net @0.30% **+45.29%**; net @0.45% **+28.34%**
- Win rate gross 57.52%, net base 55.75%
- PF gross 1.266, **PF net0.30 1.145**, PF net0.45 1.089
- Avg trade base +0.40%; median base +1.11%; best +25.69%, worst −19.07%
- Year net base — 2024 +17.79% (55t), 2025 +27.50% (58t). Both years positive.
- **Top-3 removal (net 0.30%): −13.60% ❌**
- Single-year dominance (base): 60.7% (2025)
- Symbols net-positive after 0.30% friction: **2/3** (BTC, SOL); ETH net-negative

## 7. D12 gate evaluation (FAIL checked first; ETH/SOL cannot rescue BTC/combined)

### FAIL checks

| FAIL trigger | Value | Fired? |
|---|---|---|
| BTC primary net @0.30% ≤ 0 | +13.33% | no |
| BTC trade count < 10 | 18 | no |
| combined net @0.45% ≤ 0 | +28.34% | no |
| combined net PF @0.30% < 1.10 | 1.145 | no |
| **top-3 removal makes combined net ≤ 0** | **−13.60%** | **YES** |
| **BTC top-3 removal ≤ 0** | **−12.21%** | **YES** |
| only one symbol positive after friction | 2 positive | no |
| one year >80% of net AND other year ≤ 0 | 60.7%, both +ve | no |
| any data QA defect | CLEAN | no |
| 2026 contamination | 0 rows | no |
| rule mismatch | exact frozen rules | no |

**Two independent FAIL triggers fired.** Per the pre-registered precedence, a single
FAIL trigger forces FAIL regardless of other metrics, and ETH/SOL strength may not
rescue a BTC-primary or combined FAIL.

## 8. OOS verdict

### **FAIL**

The **top-3-winner-removal gate** — the universal killer that parked every futures
branch and 2/3 of CODR-1's symbols, but which CCR1 v1 **PASSED in-sample on BTC
(+15.76%) and combined (+314.55%)** — **FAILS out-of-sample on both:**

- **BTC net ex-top3 @0.30% = −12.21%** (headline BTC +13.33% is carried entirely by
  3 trades).
- **Combined net ex-top3 @0.30% = −13.60%** (headline combined +45.29% is carried
  entirely by 3 trades).

ETH is additionally net-negative OOS (−33.33% base, **both** years negative). SOL
alone is robust (top-3 pass +10.40%, both years positive), but a single robust
secondary symbol cannot rescue a BTC-primary / combined FAIL. The concentration
weakness flagged at IS (regime/winner dependence) materialized OOS as **winner
concentration**: the edge is three trades wide.

## 9. Recommendation

**PARK Crash-Candle Reversion v1 (CCR1) as OOS_FAIL.**

- **No OOS rerun, no second look, no cherry-picked sub-window.**
- **No tuning to chase the OOS:** do not change −5%, do not switch to −7%/−10%, do
  not add an SMA/trend or confirmation filter, do not change the 3-bar exit. Any such
  change is a **NEW pre-registered spec id and a fresh ladder**, never an edit here —
  tuning now would overfit to the OOS.
- **Ladder status:** CCR1 v1 is the second parked crypto branch after CODR-1
  (IS_FAIL). The crash-candle family is **OOS-falsified at v1.**
- **Scope unchanged:** OOS 2026 stays **SEALED**; perps remain **BLOCKED**; crypto
  stays a **separate research lane**, never mixed with futures validation claims; S30
  stays **PARKED**; futures branches untouched. No paper, no live, no exchange API,
  no broker authorized anywhere.

## 10. Forbidden actions (this lane)

`no_oos_rerun` · `no_second_look` · `no_parameter_tuning` ·
`no_added_filters_after_oos` · `no_optimization` · `no_2026_use` · `no_data_fetch` ·
`no_network` · `no_exchange_api_execution` · `no_broker` · `no_paper_or_live` ·
`no_perps` · `no_modification_of_frozen_data` · `do_not_touch_s30_or_futures` ·
`jarvis_templates_base_hydra_untouched`.

---

**Trading recommendation:** NONE — research OOS result only. **Crash-Candle Reversion
v1 is OOS_FAIL** on the top-3-winner-removal gate (BTC net ex-top3 −12.21%, combined
−13.60%); ETH is net-negative both OOS years; the edge is carried by three trades.
CCR1 v1 is **PARKED** — no rerun, no tuning. OOS 2026 remains **sealed**; perps remain
blocked; crypto stays a separate research lane; **S30 stays PARKED and the futures
branches are untouched.** No crypto strategy is validated, paper-ready, or live-ready.
