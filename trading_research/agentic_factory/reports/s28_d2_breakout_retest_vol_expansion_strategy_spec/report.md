# S28-D2 — Breakout-Retest with Volatility Expansion and Mechanical Bad-Regime Gate · FROZEN Strategy Spec (Pre-Registration)

**Frozen hypothesis specification ONLY. No strategy code, no backtest, no IS/OOS
run, no optimization, no parameter sweep, no data fetch, no paper, no live. The
spec below is locked BEFORE any result is seen. If any rule changes after a
result, it opens a NEW branch — S28 is not mutated in place.**

- **Created:** 2026-05-30 · **Reference commit (S28-D1):** `c8f5a46`
- **Selected-hypothesis commit:** `c8f5a46a0cd9a3732e0a9ed9c107d52c230e31d0`
- **Donchian:** PARKED. **S26:** PARK_CANDIDATE. **S27:** PARKED (IS_FAIL).
  S28 is an **unbuilt, unvalidated** hypothesis.

---

## Design context — what S28 must NOT repeat

- **Donchian:** raw breakout entry was `ENTRY_EDGE_NOT_SUPPORTED` and
  `SEQUENCE_RISK_FRAGILE` (net flips negative without the top-3 winners). **S28
  does NOT enter the breakout** — it enters the *retest-that-holds*, and
  pre-registers a significance test that the retest must BEAT the raw breakout.
- **S26:** `FRICTION_SENSITIVE`, `REGIME_RISK_INCONCLUSIVE`, collapsed in the
  2014–2016 chop with no no-trade gate. **S28 adds an explicit mechanical
  bad-regime NO-TRADE gate** and uses wider-structure stops for friction
  headroom.
- **S27:** mean-reversion FAILED IS with only 18 trades and negative expectancy
  (capped target rarely reached, two-step confirmation too restrictive). **S28
  pre-registers explicit trade-count floors** and keeps the entry
  selective-but-not-rare; +2R target on larger structures.
- **Entry must be significance-testable:** the retest-hold is a discrete, datable
  event tested two ways — vs random-in-universe AND vs raw-breakout entry — at
  fixed horizons.

---

## 1. Strategy name

**Breakout-Retest with Volatility Expansion and Mechanical Bad-Regime Gate.**

## 2. Market and timeframe

| Item | Value |
|---|---|
| Primary | **NQ** continuous futures, **daily** bars |
| Independent confirmation (later) | **ES** daily — **D10 only**, never part of the entry |
| Intraday | none in v1 |
| 2026 data | **not used** |
| In-sample (IS) | **2013–2022** |
| Out-of-sample (OOS) | **2023–2025 — SEALED** until the OOS protocol step is committed |
| Proxy micros | MNQ/MES (from 2019) **descriptive corroboration only**, never independent |

## 3. Core hypothesis

A raw breakout alone is noisy, but a breakout that **expands volatility/
participation**, then **RETESTS and HOLDS** the prior resistance level, may
identify genuine acceptance above resistance (prior resistance becomes support).
The edge must come from the **retest-hold event after expansion** — not from raw
breakout chasing — which is exactly why entry significance is pre-registered
against **both** random-in-universe and raw-breakout entries.

## 4. Trend / background filter

Long-only context. A setup is only allowed when **all** hold:

- `close > EMA200`
- `EMA50 > EMA200`
- `EMA200[i] − EMA200[i−20] >= 0` (non-negative 20-bar change of EMA200)

**EMA200 slope IS included.** The slope gate (consistent with the S26/S27 lesson)
restricts to a genuinely rising trend, not a topping/rolling market. Fixed
mechanical binary gate — no optimization.

## 5. Resistance and breakout

| Component | Rule |
|---|---|
| Resistance | highest **HIGH** over the prior **55** bars, **excluding** the current bar |
| Breakout bar | `close > resistance` |
| Range expansion (required) | true range of breakout bar `>= 1.25 * ATR20` (ATR20 through the breakout bar) |
| Volume expansion (required) | breakout-bar volume `>= 1.20 * SMA20(volume)` (20-bar simple avg, prior+current) |
| Volume source | real daily volume column (present in the provisioned daily CSVs) |
| Captured at breakout | `resistance_level`, `ATR20_at_breakout` |

**Volume fallback:** if a future data concern made volume unusable, a
range-expansion-only variant (`TR >= 1.25*ATR20`) would be a **SEPARATE branch**,
not a silent fallback. **v1 REQUIRES volume expansion.**

## 6. Retest window

- **Window:** up to **10 bars AFTER** the breakout bar.
- **Retest rule** (candidate bar j): `low[j] <= resistance + 0.25 * ATR20_at_breakout`.
- **Hold rule:** `AND close[j] >= resistance` (the retest bar closes back above the reclaimed level).
- **Signal bar:** the **first** in-window bar satisfying **both** retest and hold = the retest-hold (signal) bar.
- **Expiry (no retest):** if no in-window bar satisfies the retest rule, the setup **EXPIRES**.
- **Expiry (failure):** if `close < resistance` on any in-window bar **before** a retest-hold occurs, the setup **FAILS/expires** (acceptance lost).
- **One active setup** is tracked at a time.

## 7. Entry timing

- **Signal bar:** the retest-hold bar.
- **Entry:** **next bar open** = open of (signal bar + 1).
- **No same-bar lookahead.** One active setup. One position at a time.

## 8. Bad-regime NO-TRADE gate

**Chosen option: A — near-mean / non-rising chop filter.**

> **NO TRADE** (setup suppressed) if
> `abs(close − EMA200) <= 1.0 * ATR20` **AND** `(EMA50[i] − EMA50[i−20]) <= 0`.

- **Evaluated on:** the retest-hold (signal) bar.
- **Why A:** directly targets the documented **2014–2016 failure regime** (price
  oscillating near the 200MA with a flat/falling intermediate trend). Genuine
  trend breakouts of 55-day highs sit well above EMA200, so this gate rarely
  blocks real trends and mainly blocks the near-mean chop that sank S26/Donchian.
  Mechanical, stdlib (EMA arrays already computed), no subjective labels.
- **Flat/negative definition:** EMA50 20-bar change `<= 0`.

## 9. Stop

- **Rule:** `stop = entry − 2.0 * ATR20` (ATR20 as of the retest-hold signal bar).
- **R unit:** `1R = 2.0 * ATR20` = the stop distance. All results in **R only**.
- **Why ATR-based:** clean, consistent R accounting and wider headroom on larger
  breakout structures — the friction headroom S26 lacked.

## 10. Exit

| Component | Rule |
|---|---|
| Target | **+2.0R** (= entry + 2×1R = entry + `4.0 * ATR20`) |
| Stop | **−1R** (= the `2.0*ATR20` stop above) |
| Time stop | exit at the **CLOSE of the 20th bar held** if neither stop nor target hit |
| Failure-exit (close below resistance) | **NOT used in v1** — deliberately omitted to keep the exit fixed and simple (S26/S27 v1 minimalism). Adding it later opens a new branch. |
| Exit precedence | **stop → target → time_stop.** If stop and target both touch on the same bar, **STOP fills first** (conservative). |
| Management begins | the bar **AFTER** the fill bar (conservative; the fill bar opens the position but is not itself an exit bar). |

## 11. Position rules

Long-only · one position at a time · no pyramiding · no compounding · R-only
accounting · one active setup at a time.

## 12. Entry significance protocol

- **Test 1 — vs random-in-universe:** retest-hold entries vs the **same count** of
  random entries drawn from the same trend/regime-allowed universe (bull filter
  true, bad-regime gate passed).
- **Test 2 — vs raw breakout:** retest-hold entries vs **raw breakout** entries
  (enter at the breakout bar's next open) — isolates the retest's marginal edge
  AND tests against the parked Donchian style.
- **Horizons (bars):** 5, 10, 20, 40.
- **Requirement:** the retest must **beat random AND beat the raw breakout** to be
  `EDGE_LIKELY`. If it does not beat raw-breakout, **PARK** — do not continue
  "inconclusive" like S26.

## 13. Validation ladder

| Step | Scope |
|---|---|
| D3 | implement engine + tests only (no results) |
| D4 | IS baseline 2013–2022 |
| D5 | OOS protocol pre-registration |
| D6 | OOS run **ONCE** (2023–2025) |
| D7 | entry significance (retest vs random AND vs raw breakout) |
| D8 | Monte Carlo / sequence risk |
| D9 | regime breakdown (incl. explicit 2014–2016 chop check) |
| D10 | ES multi-market robustness (independent confirmation) |
| D11 | walk-forward stability |
| D12 | friction stress |
| D13 | decision gate |

## 14. Pass / Watch / Fail thresholds (pre-registered BEFORE any result)

Conservative. **PASS** = all met · **WATCH** = minor misses · **FAIL** = any hard
floor breached.

| Gate | PASS | WATCH | FAIL |
|---|---|---|---|
| IS trade count | ≥30 | 20–29 | <20 |
| OOS trade count | ≥15 | 10–14 | <10 |
| Profit factor | ≥1.40 | 1.15–1.39 | <1.15 |
| Expectancy | >0 on IS **and** OOS | — | ≤0 on either |
| Max DD cap | IS max DD ≤ IS net R | — | IS max DD > 1.5× IS net R |
| Positive years | ≥6/10 IS years positive | 5/10 | <5/10 |
| Top-3 winner dependence | IS net stays **positive** after removing top 3 winners | — | IS net goes negative without top 3 (Donchian failure mode) |
| Entry significance | `EDGE_LIKELY` vs random AND beats raw-breakout | `INCONCLUSIVE` (not disproven) | `NOT_SUPPORTED`, or does not beat raw breakout |
| Sequence risk | bootstrap prob(total R≤0) < 10% | 10–20% | ≥20% (Donchian was 20.9%) |
| Friction | IS positive at 0.05R **and** OOS positive at 0.10R per trade | — | OOS negative at ≤0.05R |

## 15. Anti-overfit rules

- No changing the breakout length (**55**), ATR multipliers (**1.25** TR, **0.25**
  retest, **2.0** stop), volume multiplier (**1.20**), retest window (**10**),
  time stop (**20**), or regime-gate constants after seeing results.
- No OOS peeking before the OOS protocol is committed.
- No parameter sweeps.
- No adding or removing filters after OOS.
- If any rule changes, open a **NEW branch** (do not mutate S28 in place).
- No paper/live promotion from this spec or from IS results.

## 16. Expected failure modes

1. **Too few trades** — selective stack (55-bar high + range + volume + retest +
   regime gate); watch the IS/OOS trade floors.
2. **Retest rule too strict** — price breaks out and never returns within 10 bars;
   expiry rate may be high.
3. **Volume filter too restrictive** — kills otherwise-valid retests; watch trade count.
4. **Late entries** after the move is exhausted (retest far into the move) — watch
   win rate vs time-stop exits.
5. **Friction sensitivity** — mitigated by the wider `2.0*ATR` stop, stress-tested at D12.
6. **False breakouts in chop** — mitigated by the bad-regime no-trade gate +
   retest-hold requirement.
7. **Dependence on post-2016 trend regimes** — D9 regime breakdown checks
   2014–2016 explicitly.

## 17. Final line

**“S28-D2 is a frozen hypothesis specification only; no strategy code, backtest,
OOS, paper, or live trading is authorized.”**

---

### Guardrails

`no_code` · `no_backtest` · `no_is_oos_run` · `no_optimization` ·
`no_parameter_sweeps` · `no_data_fetch` · `no_paper_or_live` · `no_broker_or_api`
· `s26_untouched` · `s27_untouched` · `donchian_untouched` ·
`jarvis_templates_hydra_untouched`.

**Trading recommendation:** NONE. Frozen spec only. Donchian, S26, and S27 stay
PARKED; S28 is an unbuilt, unvalidated hypothesis.
