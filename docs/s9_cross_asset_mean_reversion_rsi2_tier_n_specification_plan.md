# s9 Cross-Asset Mean-Reversion RSI-2 - Tier-N Specification Plan

Status: PLAN_ONLY (specification authoring; no code, no build, no signal computation, no backtest, no simulator).
Authored: 2026-05-25
Candidate record id: `s9-cross-asset-mean-reversion-rsi2-spy-tlt-gld-uso-yfinance-proxy`
Selected by: docs/next_research_track_selection_plan_after_s7_d1_park.md (sha256 d8753155d47c36e07830750bf892743b8a1958d1ccc6d53932bee32ff76ec954, commit 530b54598fa7098eb746f2122b4002db2c984422), recommendation T1 scored 49/50.
Predecessor (parked): s7 D1 cross-asset Donchian yfinance ETF-proxy at REJECT_FAST. Park report sha256 5eb4309096a8377943799b7cc164cbbb13a86f327a813520255d0fa3b3e00263, seal e7f3fce5239d18f7cff78ddda81dde060b6842c54ddb1fdba95bfdcd584eb326, commit a5ac092.

HARD BOUNDARIES (held by this plan). Tier-N specification only. No strategy code. No RSI computation. No signal computation. No simulator. No backtest. No data fetch. No yfinance import. No Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No network IO. No s7 D1 artifact mutation. No s7 D1 resurrection or revision. No review_queue.json mutation. No production idea_memory mutation. No Strategy Lab run. No Strategy Lab promotion. No candidate promotion. No ORB branch artifact mutation. No Step 30 cost constant mutation. No existing source code modification. No tests modification. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No branch change. No branch creation. No commit beyond the single new plan file. No git push. No live trading. No profitability claim. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.

----

## 1. Purpose

Lock the Tier-N specification for the s9 cross-asset mean-reversion RSI-2 research track. This plan defines the mechanic, the data scope, the cost model, the acceptance and rejection gates, and the per-phase plan sequence for the next-step authorizations. The plan does NOT compute RSI, does NOT generate signals, does NOT run a simulator, and does NOT touch any prior phase artifact. It establishes the contract that every future plan and build phase in the s9 chain shall inherit byte-equivalently or shall require a fresh `_revN_` specification to depart from.

## 2. Why this track follows s7 D1

The s7 D1 cross-asset Donchian yfinance ETF-proxy chain parked at REJECT_FAST (commit a5ac092) because the locked no-filter Donchian-55 entry / Donchian-20 exit / 0.5N pyramid / 4-unit-max / 2N-stop mechanic on SPY/TLT/GLD/USO did NOT survive cost-stress. K12 fired via DR2 (S2/S3 materially degraded vs S1) and DR3 (S0 positive while at least one stressed tier non-positive) on the cost-stress matrix.

The validated finding from s7 D1 is the cross-asset diversification structure on this universe: `effective_independent_bets = 3.56`, `avg_pairwise_dependence = 0.041`. The four ETFs behave as four genuinely independent return series. This finding is family-agnostic: it characterizes the UNIVERSE, not the mechanic.

The s7 D1 selection plan ranked T1 (cross-asset mean-reversion on the same ETF universe) at 49/50 because mean-reversion structurally addresses both s7 D1 failure modes: (a) trade density (RSI-2 oversold-bounce fires 50-150 times/year/symbol vs Donchian-55's annual frequency), and (b) cost-stress sensitivity (mean-reversion's per-trade economics have a different cost-stress profile from low-frequency trend-following; whether the s9 edge survives is a genuine open question, not a foregone conclusion).

This plan tests the orthogonal-family hypothesis on the same universe. A pass here would confirm that the universe supports a tradeable edge under realistic costs at a structurally different mechanic. A fail here would be a strong family-level finding: TWO structurally orthogonal mechanics empirically falsified on the same universe, suggesting the universe itself is the bottleneck.

## 3. Strategy hypothesis

H1 (s9): A long-only RSI-2 oversold-bounce mean-reversion mechanic on the four-ETF universe (SPY/TLT/GLD/USO) produces a positive per-trade expectancy at S1 baseline cost-stress AND survives S2/S3 cost-stress (DR2 / DR3 / DR5 do not fire), AND clears K9 sample size (>= 100 closed trades over the in-sample window), AND produces a positive portfolio Sharpe proxy and an in-sample trade-curve max drawdown <= 50%, AND >= 2/4 markets show win-rate gap to breakeven >= 0 AND portfolio WR-gap >= +0.5pp.

H0 (s9): The mean-reversion family on this universe at canonical RSI-2 parameters also fails one or more of the above acceptance gates. If H0 holds, this universe with the available cost structure does not support either trend-following (s7 D1 falsified) or mean-reversion at canonical parameters; the universe-level conclusion strengthens to "current ETF-proxy cost structure precludes structurally simple mechanics on this universe." Further research would either: (a) move to a different cost-structure assumption (lower commission, lower slippage; would require a fresh _revN_ spec), or (b) move to a different mechanic family entirely (rotation, carry, vol-of-vol).

The hypothesis is falsifiable by the A-gates and K-criteria defined in sections 16-17.

## 4. Inherited and not-inherited lessons

INHERITED (the next track shall carry these forward):

- The cross-asset diversification finding on SPY/TLT/GLD/USO 2014-2022: `avg_pairwise_dependence = 0.041`, `effective_independent_bets = 3.56`. Section 12 below uses this in the A7 gate evaluation expectation.
- The four-symbol ETF dataset under `data/s7_d1_cross_asset_donchian/raw/` (sealed audit verdict PASS, audit_manifest sha256 794a9386abc68fdffe411e5a54534852293c8ba9c9c14fc4a2443c67a374bdcb).
- The Step 03 loader package (sealed PASS at commit d7b2a0c, loader.py sha256 e0609e404cadca1c442dbce371d766aa5e13e445362ed855509a6d9684ec6fd9). The s9 loader-reuse plan in section 18 specifies whether to reuse byte-equivalent or build a fresh s9-specific loader.
- The Step 04 validator package (sealed PASS at commit a2ec179).
- The cost-stress matrix S0/S1/S2/S3 (per s7 D1 simulator section 14) with ETF-proxy adaptation (`ETF_DOLLAR_PER_SHARE = 1.0`, `ETF_TICK_SIZE = 0.01`).
- The DR2 / DR3 / DR5 fail-fast rules with `DR2_S2_S3_DEGRADATION_THRESHOLD_FRACTION = 0.5`.
- The A1-A10 acceptance gate thresholds and K1-K11+K12 rejection criteria byte-equivalent.
- The Phase 2 safety template C1-C8 contracts.
- The IS / OOS / post-OOS window pins: in-sample = 2013-01-01 to 2022-12-30; out-of-sample = 2023-01-01 to 2025-12-30; post-OOS = 2026-01-02 to 2026-05-22.
- The IS-only structural enforcement pattern (5-layer enforcement: no override parameter, hardcoded window, eligibility-predicate exclusion, post-loop assertion, defensive scan).

NOT INHERITED (the next track shall NOT carry these forward; explicit refusal):

- The locked Donchian-55 entry / Donchian-20 exit channel mechanic.
- Wilder ATR(20) as a sizing input.
- The 0.5N pyramid step / 4-unit-max amplification design.
- The 2N hard stop.
- The Faith System 1 lifecycle convention (MOC/ONO entry timing for breakout signals; mean-reversion uses close-of-day signal evaluation but the timing convention is different and locked separately in section 9).
- Any same-direction trend filter (s7 D1 spec section 5 locked `Filter: NONE`; s9 also locks no filter, but the absence is a NEW lock not a copy).

## 5. Markets (locked)

The s9 track operates on exactly the four ETFs from the s7 D1 sealed audit:

| Symbol | Family | Inherited from | Why included |
|---|---|---|---|
| SPY | equity-index | s7 D1 audit_manifest pin `bad97abba5283694...` | Validated component of the diversification finding |
| TLT | bonds | s7 D1 audit_manifest pin `2cab9fc3d2e26c62...` | Validated component of the diversification finding |
| GLD | metals | s7 D1 audit_manifest pin `7ff41cda6214d073...` | Validated component of the diversification finding |
| USO | energy | s7 D1 audit_manifest pin `0b5b5b9472e5bdf5...` | Validated component of the diversification finding |

No symbol substitution. No universe expansion at this Tier-N spec. A future _revN_ spec may propose expanding to 6-8 ETFs (e.g., adding IWM / EFA / AGG / DBC) but that requires its own data-fetch authorization and is OUT OF SCOPE for s9.

## 6. Data source (locked)

EXACT data source:

- `data/s7_d1_cross_asset_donchian/raw/SPY_1d_2014-01-01_2026-05-25.csv` (sha256 `bad97abba52836949e4ce1ffeba2002d308286c991091c6c073283ab1e2f91eb`)
- `data/s7_d1_cross_asset_donchian/raw/TLT_1d_2014-01-01_2026-05-25.csv` (sha256 `2cab9fc3d2e26c62a08c4af64bf57d46350b3062219bf5cb7373883d04676570`)
- `data/s7_d1_cross_asset_donchian/raw/GLD_1d_2014-01-01_2026-05-25.csv` (sha256 `7ff41cda6214d0739c2143dda4b98624f4e0365db499d7cee0ff0fa37ce811b0`)
- `data/s7_d1_cross_asset_donchian/raw/USO_1d_2014-01-01_2026-05-25.csv` (sha256 `0b5b5b9472e5bdf59cbd04a3794a95bfa5e87efc9baf7837e1fca7de08530b37`)
- `data/s7_d1_cross_asset_donchian/raw/audit_manifest.json` (sha256 `794a9386abc68fdffe411e5a54534852293c8ba9c9c14fc4a2443c67a374bdcb`)
- `data/s7_d1_cross_asset_donchian/raw/fetch_run_manifest.json` (sha256 `8fe210138dedcbaa07882b704cc3c3e30ba2ca4a1d4db7f05ca4dc782005a8f7`)

Zero new data fetch. Zero new yfinance call. Zero new Yahoo Finance call. Zero new Databento call. Zero new operator-side data work. The s9 chain inherits the s7 D1 sealed dataset by reference.

The CSV bytes shall not be modified by any s9 phase. The audit_manifest.json and fetch_run_manifest.json shall not be modified. Re-running the Step 02c raw-data audit on these CSVs is OPTIONAL (audit attestation by reference to the existing s7 D1 audit report is acceptable per section 18); a fresh re-audit would not change the validated content.

## 7. Session rules (locked)

| Field | Value | Rationale |
|---|---|---|
| Reference timezone | `America/New_York` (ET) | Standard for U.S. ETF strategies |
| Trading session | RTH-only daily bars (already enforced by sealed audit) | Inherited from s7 D1 |
| Daily-bar derivation | One daily OHLCV bar per market per RTH session | Already realized in the sealed CSVs |
| Trade timezone for signal evaluation | Close-of-day signal evaluation | Mean-reversion convention |
| Trade timezone for execution | Next-bar-open fill (ONO; same as s7 D1) | Avoids look-ahead; consistent with Step 06 simulator |
| Holiday calendar | NYSE (already realized by yfinance / the audit's cross-symbol-aligned date set) | Inherited |
| Per-market trading-day count | Synchronized across the four symbols (per Step 04 validator cross-symbol alignment A3) | Inherited |
| Session boundary errors | Inherited from Step 04 validator: any IS bar that fails validator A-checks halts the load | Inherited |

## 8. Signal mechanic (RSI-2 oversold-bounce, locked)

Locked formula, locked parameters, locked thresholds:

| Parameter | Value | Source / Rationale |
|---|---|---|
| RSI period | **2** | Connors canonical 2-period RSI; not optimized |
| Series for RSI computation | **adj_close** | Removes dividend-ex-date artifacts that could artificially trigger oversold signals; TLT's monthly distributions specifically would create ~12 false signals/year if using raw close; Step 02c audit confirmed both columns are present and sealed; GLD/USO close == adj_close so the choice does not matter for them; SAME column for all four symbols for consistency |
| Oversold entry threshold | **RSI(2) < 10** | Connors canonical TPS threshold; locked at this Tier-N spec, not optimized; deviating requires a fresh `_revN_` spec |
| Exit threshold | **RSI(2) > 50** | Connors canonical TPS exit threshold; locked, not optimized |
| Direction | **LONG ONLY** | Section 9 explicitly justifies the long-only initial scope and the short-deferral |
| Filter | **NONE** | No same-direction trend filter, no MA filter, no regime filter, no volatility filter, no dependence filter; this is a structural lock (parallels s7 D1's locked `Filter: NONE`) and is the entire reason for choosing a structurally-pure mean-reversion mechanic |
| Pyramid | **NONE** | Section 12 explicitly rejects pyramid for s9 |
| Hard stop | **NONE** | Exit is signal-based (RSI(2) > 50), not price-based; section 11 documents the rationale |
| Time stop | **NONE** | No fixed-day stop; section 11 documents |

RSI formula (Wilder smoothing): standard Wilder 2-period RSI computed on the adj_close series. The future signal-spec plan (section 18) shall lock the exact computation (initial value handling, ratio rounding) byte-equivalent to a documented reference implementation. The RSI computation is OUT OF SCOPE for this Tier-N spec (no RSI is computed in this plan).

## 9. Entry rule (long-only, locked)

1. At each market's RTH close, evaluate `RSI(2)` on the closing adj_close series for that symbol.
2. If `RSI(2) < 10` AND no open position on this symbol AND the global per-symbol open-position count is 0 for this symbol: queue an `ENTRY_PENDING` LONG for the next RTH open (`ONO` timing; matches s7 D1 simulator entry convention).
3. If `RSI(2) < 10` AND a position is already open on this symbol: no new entry queued; the existing position remains open.
4. If RSI(2) >= 10: no entry queued.
5. No same-symbol opposite-direction entry. The s9 mechanic is LONG-ONLY; the SHORT side is OUT OF SCOPE at this Tier-N spec (section 9 below) and may be specified in a future `_revN_` spec under separate authorization.
6. Entries are evaluated per market independently. No cross-market gate. No correlation filter at entry time. No risk-budget rebalancing at entry time.
7. On fill (next RTH open the next trading day), record the fill price for slippage accounting.

Short-side deferral rationale: the short side requires modeling ETF share-borrow cost at S1 baseline (~25-100 bps annualized for SPY/TLT/GLD; can spike higher for USO). Adding borrow cost increases the cost-stress matrix complexity and introduces a new failure mode (high borrow during volatile periods). For the first s9 cycle, the LONG-ONLY scope is the simpler, more honest test of the mean-reversion hypothesis. A `_revN_` long/short variant may follow if the long-only s9 passes.

## 10. Exit rule (locked)

1. At each market's RTH close, for every open long position on this symbol, evaluate `RSI(2)`.
2. If `RSI(2) > 50` AND a position is open on this symbol: queue an `EXIT_PENDING` for ALL OPEN UNITS on this symbol's long position for the next RTH open.
3. On fill (next RTH open the next trading day), close the position at the fill price; record slippage; close the trade-group; reset per-symbol state.
4. The exit is bidirectional in the sense that "going through 50" is the exit trigger regardless of which direction was crossed (but since s9 is long-only, the exit always closes a long).
5. NO HARD STOP: the s9 mechanic has no fixed-distance stop. The only exit is `RSI(2) > 50`. This is intentional (RSI-2 mean-reversion typically does not use a price-distance stop; the mean-reversion is its own risk control).
6. NO TIME STOP: no fixed-day stop. Positions may stay open as long as `RSI(2) <= 50`.
7. NO TRAILING STOP. NO PROFIT TARGET. NO PARTIAL EXIT.
8. K4 CATASTROPHIC STOP (chain-level): if portfolio MaxDD > 50% on the trade-curve, K4 fires and the candidate parks immediately at end-of-day (inherited from spec section 8 K4).
9. END OF IN-SAMPLE BOUNDARY: at the last IS bar's close, any still-open positions are flat-marked at that bar's close with `exit_reason = IN_SAMPLE_END_FLAT`. No positions carry into OOS bars (inherited from Step 06 simulator pattern).

Justification for no hard stop: in RSI-2 mean-reversion the assumption is that an oversold condition will revert. A hard stop would convert short-term drawdowns into realized losses BEFORE the mean-reversion completes, which would systematically degrade the edge. The risk is bounded by (a) max concurrent positions (section 11), (b) K4 catastrophic stop, and (c) IS-end flat-mark. If the s9 IS run shows that no-hard-stop produces unacceptable MaxDD on individual trades, a `_revN_` spec may add a hard stop, but the locked s9 spec has none.

## 11. Position sizing (equal-dollar at 1% of portfolio equity per signal entry, locked)

Locked sizing convention:

| Parameter | Value | Source / Rationale |
|---|---|---|
| Capital basis | **Portfolio equity** (mark-to-market, end of prior RTH day) | Inherited from spec section 9 |
| Per-signal allocation fraction | **1.0 % of portfolio equity** | Mirrors s7 D1's per-unit risk fraction notation; conservative; allows max gross exposure of 4% across the four-symbol portfolio |
| Per-signal share count formula | `floor((0.01 * portfolio_equity) / fill_price)` | Equal-dollar allocation; shares are whole numbers; fractional shares are truncated |
| Minimum share count | If computed shares < 1, the signal is SKIPPED and logged | Matches s7 D1 minimum-size rule |
| Maximum concurrent positions per symbol | **1** | NO pyramid (section 12); a second `RSI(2) < 10` while a position is already open does not generate a new entry |
| Maximum concurrent positions portfolio-wide | **4** | One per symbol; max gross exposure = 4 * 1% = 4% of equity |
| Starting cash | **$100,000** | Inherited from s7 D1 simulator DEFAULT_STARTING_CASH |
| ETF $/share multiplier | **1.0** | ETF-proxy adaptation; inherited from s7 D1 simulator ETF_DOLLAR_PER_SHARE |
| Sizing under data outage | If adj_close is missing or non-positive at the signal bar, the signal is SKIPPED and logged | Inherited pattern |

Sizing choice rationale (equal-dollar vs ATR-based):

- ATR-based 1% risk sizing requires a fixed stop distance to define the size such that "1 ATR adverse move = 1% loss". The s9 mechanic has NO fixed stop (section 10 step 5); therefore ATR-based sizing does NOT fit the mechanic.
- Equal-dollar sizing at a fixed fraction of equity per signal is the canonical convention for Connors-style RSI-2 mean-reversion strategies; it is simple, transparent, deterministic, and does not require an ATR computation.
- Locking at 1% per signal (vs higher fractions like 5% or 10%) is conservative: max gross exposure 4% means slippage and commission represent a non-trivial fraction of per-trade P&L, making the cost-stress matrix MEANINGFUL. A 1% allocation on $100k equity = $1000 / signal; at SPY ~$400 that is ~2 shares. Slippage at S1 baseline (1 cent per share, ETF tick) = $0.02 per round trip; per-trade expected mean-reversion P&L on 2 shares is ~$2-10. Cost stress at S3 (5x slippage) = $0.10 per RT, which can flip P/L negative on small trades.
- The simulator-spec plan (section 18) may further lock additional bookkeeping (cash balance accounting, settlement convention) but the FRACTION 1% is locked here at Tier-N.

The simulator-spec plan may adjust the per-signal allocation fraction UP to 5% if the locked 1% produces no clearable signal noise; ANY upward adjustment requires explicit justification and is documented as a `_revN_` step, NOT a silent change.

## 12. Pyramid rule: NONE (explicitly rejected at Tier-N, locked)

Pyramid is EXPLICITLY REJECTED for s9. Rationale:

- The Databento-track s7 D1 (the sibling chain on NQ/GC/ZN/CL futures) parked at K4 catastrophic MaxDD -221.67% specifically due to pyramid amplification at low win rate.
- The ETF-proxy s7 D1 (this chain's predecessor) also showed cap-binding events on 16 of 37 trade groups, indicating the pyramid stack was structurally active during catastrophic periods.
- Two independent universes converge on the same lesson: 4-unit pyramid amplification is a primary failure mode for trend-following on this protocol.
- RSI-2 mean-reversion typically holds short-duration positions (1-3 days). Pyramiding a mean-reversion entry on continued weakness would CONTRADICT the mean-reversion thesis (an oversold-bounce mechanic does not benefit from doubling down on continued falling).
- Pyramid would expand the per-symbol open-position count beyond 1, which would interact non-trivially with the entry rule's "no entry if position open" condition.

`MAX_UNITS_PER_SYMBOL = 1` for s9. A `_revN_` spec may propose a pyramid variant with first-principles justification, but the locked s9 spec has no pyramid.

## 13. Cost / slippage model (locked, inherits ETF-proxy adaptation from s7 D1)

Cost-stress matrix S0/S1/S2/S3 (S4 reserved per spec section 10, OUT OF SCOPE for the simulator per Step 06 plan):

| Tier | Slippage scalar | Commission scalar | Purpose |
|---|---|---|---|
| S0 | 0x | 0x | Diagnostic floor; DR3 fires if survival is S0-only |
| S1 | 1x (baseline) | 1x (baseline) | Pre-registered baseline |
| S2 | 3x | 1.5x | Mild stress |
| S3 | 5x | 2x | Realistic adverse |
| S4 (RESERVED) | 8x | 3x | OUT OF SCOPE for the simulator |

ETF-proxy baseline (S1, 1x):

- Commission per round trip per signal: **$0.00 per share** (zero-commission ETF broker assumption); inherited from s7 D1 simulator; raising this requires a fresh `_revN_` spec.
- Slippage per entry per share: **$0.01** (one ETF penny tick); inherited from s7 D1.
- Slippage per exit per share: **$0.01** (one penny); inherited from s7 D1.
- Slippage per stop-out per share: **N/A** (s9 has no hard stop; only signal-based exit; the s7 D1 "$0.02 per share stop-out" is not applicable).
- Funding / overnight: **None** for long positions on ETFs.
- Borrow cost: **N/A** at this Tier-N spec (long-only).

DR rule evaluation (inherited byte-equivalent from s7 D1 aggregator):

- DR2: `total_net_pnl` at S2 or S3 materially degrades vs S1 (less than `DR2_S2_S3_DEGRADATION_THRESHOLD_FRACTION = 0.5` times S1, OR turns non-positive while S1 positive).
- DR3: zero-cost-only survival (S0 positive AND at least one of S1/S2/S3 non-positive).
- DR5: S0 positive AND S1 non-positive (S0->S1 edge negative).
- DR4: OOS-side check; OUT OF SCOPE for s9 IS-only Tier-N spec; deferred to the future OOS phase under separate authorization.

K12 (REJECT_FAST) fires if DR2 OR DR3 OR DR5 fires.

## 14. Data requirements (locked)

| Field | Value |
|---|---|
| Source of record | Sealed s7 D1 yfinance ETF-proxy CSVs (per section 6) |
| Schema | Daily OHLCV columns: `date,open,high,low,close,adj_close,volume` (locked column order matching the audit) |
| Symbols | SPY, TLT, GLD, USO (cross-symbol date-aligned per Step 04 validator A3) |
| In-sample window | **2013-01-01 to 2022-12-30** (inherited byte-equivalent from spec section 11) |
| OOS window | **2023-01-01 to 2025-12-30** (inherited; BLOCKED until IS verdict authorizes inspection) |
| Post-OOS window | 2026-01-02 to 2026-05-22 (informational only; never inspected during IS phase) |
| Local cache check | Sealed CSVs present at the locked path with sha256-pinned values per section 6 |
| Fresh-download budget | **ZERO** (no new fetch authorized by this plan) |
| API-key handling | N/A (no API used) |
| Data-quality gates at load time | Inherited from Step 04 validator A-checks A1-A14; the s9 loader plan in section 18 shall confirm whether the Step 03 loader is reused byte-equivalent or a fresh s9 loader is built (and if fresh, it shall verify the same sha256 pins) |
| Calendar alignment | NYSE business calendar (cross-symbol alignment validated by Step 04 A3) |
| Time zone of timestamps | All persistence in date-only YYYY-MM-DD strings (inherited) |
| Close-vs-adj_close choice | **adj_close used for RSI computation** (section 8 justification) |

## 15. Roll / contract handling

Not applicable. ETFs do not expire and do not require front-month roll handling. The s7 D1 spec section 12 (Databento roll calendar, stitch artifact attestation) does NOT apply to s9. No roll-cost component in the cost model.

## 16. Acceptance gates A1-A10 (inherited from spec section 13 byte-equivalent)

A pass at the in-sample close requires ALL of:

| Gate id | Description | Threshold | Inheritance |
|---|---|---|---|
| `A1` | Closed-trade portfolio sample size | `closed_trades_portfolio >= 100` | Inherited byte-equivalent |
| `A2` | Portfolio Sharpe proxy (per-trade) | `sharpe_proxy_per_trade > 0` | Inherited |
| `A3` | Portfolio expectancy per trade | `expectancy_per_trade > 0` (in dollars; ETF-proxy unit-of-account) | Inherited |
| `A4` | Trade-curve MaxDD | `trade_curve_maxdd_pct <= 50.0` | Inherited |
| `A5` | Per-market WR gap vs P/L-implied breakeven | At least 2/4 markets with `win_rate_gap_to_breakeven_pp >= 0` AND portfolio WR-gap `>= +0.5 pp` | Inherited |
| `A6` | Upstream validator pass | All upstream s9 phase build reports verdict PASS | Adapted (s9 chain, not s7) |
| `A7` | Effective independent bets | `effective_independent_bets >= 2.5` | Inherited; s7 D1 measured 3.56 on this universe; s9 expected to measure similarly (universe property) |
| `A8` | Cost-stress survival | All 4 tiers S0/S1/S2/S3 run; DR2/DR3/DR5 do NOT fire | Inherited |
| `A9` | Safety-template C1-C8 inheritance | All 8 Phase 2 safety contracts attestable True | Inherited |
| `A10` | Cap binding events | `cap_binding_events_count == 0` (irrelevant for no-pyramid s9; structurally zero) | Inherited; s9 trivially clears this since pyramid is rejected |

## 17. Rejection gates K1-K11 + K12 (inherited byte-equivalent)

| K | Trigger | Park status |
|---|---|---|
| `K1` | `portfolio_sharpe_proxy_per_trade < 0` | `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` |
| `K2` | `expectancy_per_trade <= 0` | `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` |
| `K3` | reserved | - |
| `K4` | `trade_curve_maxdd_pct > 50` | `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` |
| `K5` | reserved | - |
| `K6` | safety_warning_count > 0 (any non-zero in C1-C8) | `PARKED_SAFETY_FAILED` |
| `K7` | filter_silently_introduced OR dependence_gate_silently_introduced | `PARKED_SAFETY_FAILED` |
| `K8` | sealed_parent_drift > 0 (upstream sha pins mismatch) | `PARKED_PROVENANCE_BROKEN` |
| `K9` | `closed_trades_portfolio < 100` | `PARKED_FAILED_AT_INSUFFICIENT_SAMPLE` |
| `K10` | `avg_pairwise_dependence > 0.50` | `PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS` (already validated low on this universe; K10 unlikely to fire) |
| `K11` | `cap_binding_events_count > 1000` | `PARKED_CAP_BINDING` (structurally zero for no-pyramid s9) |
| `K12` | DR2 OR DR3 OR DR5 fire on the cost-stress matrix | `REJECT_FAST` |

THRESHOLD-LOCK INVARIANT (inherited from spec section 14): loosening any K threshold post-seal is forbidden. Tightening requires a fresh `_revN_` spec.

VERDICT ASSEMBLY PRIORITY (inherited from Step 07 aggregator section 16): K8 PROVENANCE > K12 REJECT_FAST > K6/K7 SAFETY > K10 DIVERSIFICATION > K9 SAMPLE > K11 CAP > K1/K2/K4 MONEY-NOT-PROVEN > A1-A10 evaluation > ELIGIBLE_FOR_OOS.

## 18. Phase sequence (future authorizations; not initiated by this plan)

The s9 chain shall proceed through phases mirroring the s7 D1 pattern, each requiring its own separate operator authorization:

P1. **Tier-N specification plan** (THIS document; sealed at commit time of this plan).

P2. **Data audit re-attestation by reference** (no new audit; the existing s7 D1 Step 02c audit at commit 1b640d1 covers these CSVs; the s9 chain attests by reference). Future P2 turn: a short sealed reference report at `reports/s9_data_audit_reference_attestation.{json,md}` pinning the s7 D1 audit report sha256 + audit_manifest sha256 as the s9 dataset provenance. NO re-fetch. NO re-compute. Optional turn; may be skipped if the loader-build plan inherits the pins directly.

P3. **Loader-reuse decision plan** (or loader build). Two options for the s9 loader:
  - Option L1 (RECOMMENDED): reuse the Step 03 s7 D1 loader byte-equivalent (`external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_loader/loader.py`, sha256 `e0609e404cadca1c442dbce371d766aa5e13e445362ed855509a6d9684ec6fd9`). The loader returns LoadedSymbol with the same fields; s9 reads adj_close from the returned tuple. No new loader package.
  - Option L2: build a fresh `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_loader/` package. Adds maintenance surface for no benefit if L1 works.
  The phase-3 plan turn shall choose between L1 and L2.

P4. **Validator-reuse decision plan** (or validator build). Two options for the s9 validator:
  - Option V1 (RECOMMENDED): reuse the Step 04 s7 D1 validator byte-equivalent. The validator confirms the loader output is fit-for-purpose for downstream s9 signal/simulator phases.
  - Option V2: build a fresh `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_validator/`. Same reasoning as P3.
  The phase-4 plan turn shall choose between V1 and V2.

P5. **Signal-module specification plan**. The signal module computes RSI(2) on adj_close and emits SignalEvent per IS-eligible bar with the entry/exit triggers (long-only). API surface, in-sample-only enforcement, forbidden-token list, V-gates, T-tests, build-script safety guardrails specified in this plan turn.

P6. **Signal-module build turn**. Writes the signal package + tests + sealed build report.

P7. **Simulator-specification plan**. The s9 simulator inherits the Step 06 s7 D1 simulator pattern with the no-pyramid configuration (MAX_UNITS_PER_SYMBOL = 1), no-hard-stop convention, equal-dollar 1%-per-signal sizing, and the signal-based exit rule (RSI > 50 exit). Two options:
  - Option S1: reuse the Step 06 s7 D1 simulator byte-equivalent and parameterize via constants override; but the Step 06 simulator has Donchian channel construction logic baked in that s9 does not use. Reusing with parameter overrides is fragile.
  - Option S2 (RECOMMENDED): build a fresh `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_simulator/` that consumes the s9 signal events (not Donchian channels) and implements the s9-specific entry/exit/sizing logic. Reuses cost-stress matrix and trade ledger schemas.

P8. **Simulator-module build turn**. Writes the simulator package + tests + sealed build report.

P9. **Aggregator-reuse decision plan** (or aggregator build). The Step 07 s7 D1 aggregator should be byte-equivalent reusable; it consumes any SimulationResult that conforms to the dataclass schema. Two options:
  - Option A1 (RECOMMENDED): reuse the Step 07 aggregator byte-equivalent. Same A1-A10, K1-K12, DR2/DR3/DR5 evaluation. Same verdict assembly.
  - Option A2: build a fresh `external_research_hunter/s9_cross_asset_mean_reversion_rsi2_yfinance_proxy_aggregator/`. Adds maintenance surface; the existing aggregator is mechanic-agnostic.

P10. **Aggregator-module build turn (if A2 chosen) OR aggregator-attestation report (if A1 chosen)**.

P11. **In-sample diagnostic run** (the first formal s9 IS verdict turn). Loads data via P3 loader, validates via P4 validator, computes signals via P6 signal module across S0/S1/S2/S3 cost tiers via P8 simulator, aggregates via P10 aggregator, produces a sealed `reports/s9_in_sample_diagnostic_result_sealed.{json,md}` with the IS verdict from the closed 8-value enum.

P12. **In-sample decision memo** (sealed memo recording the verdict + interpretation, similar to the existing `reports/external_research_hunter/s7_d1_cross_asset_donchian_in_sample_decision_memo.{json,md}` pattern).

P13. **Lifecycle action**: PARK / PROCEED-TO-OOS / REJECT_FAST sealed report.

P14. **OOS-inspection plan** (ONLY if P11 verdict is ELIGIBLE_FOR_OOS; otherwise this phase never runs). Separate operator authorization required. Includes its own structural enforcement plan (no re-fit, no OOS-parameter tuning, no winner-of-N OOS-cherry-pick, no relaxation of K-thresholds, no Strategy Lab promotion until OOS PASS plus operator review).

P15. **OOS diagnostic run + decision memo + lifecycle action** (only if P14 authorized).

No phase confers standing authorization for any subsequent phase. Each requires its own explicit fresh operator approval. No phase confers standing authorization for live trading, brokerage connection, Strategy Lab promotion, or production candidate registration; all remain BLOCKED at separate plans.

## 19. Phase 2 safety template C1-C8 inheritance

The s9 chain shall inherit the Phase 2 safety template byte-equivalent. The C1-C8 attestations are evaluated at the P11 in-sample diagnostic phase and feed into K6 / K7 / A9. Each contract:

- C1: no live trading code path in the s9 simulator or signal module.
- C2: no brokerage / paper broker / scheduler / autopilot / FRC gate import in any s9 module.
- C3: no review_queue mutation by any s9 module.
- C4: no production idea_memory mutation by any s9 module.
- C5: simulator and signal module structural OOS protection (per Step 05 / Step 06 5-layer pattern).
- C6: no candidate promotion to Strategy Lab.
- C7: no silent filter introduction (the locked `Filter: NONE` is honored; any future filter requires a fresh `_revN_` spec).
- C8: no silent threshold relaxation (the locked K1-K12 + DR2/DR3/DR5 thresholds are honored).

The exact C1-C8 attestation surface is documented at the P11 in-sample diagnostic plan turn.

## 20. Validation gates for this plan + HALT conditions + NO-ACTION attestations

V-gates the plan-authoring turn satisfies:

V1. ASCII-only.
V2. Numbered sections in monotonic order (1..21).
V3. No execution language.
V4. No self-authorization (this plan does NOT authorize any onward phase; each requires its own operator turn).
V5. No code modification.
V6. No backtest run.
V7. No simulator run.
V8. No RSI computation.
V9. No signal computation.
V10. No data fetch.
V11. No network IO.
V12. No live trading.
V13. The committed plan file is the ONLY file changed in this turn's commit.
V14. The pre-stage git index is empty.
V15. The staged file count is exactly 1 at commit time.

HALT conditions:

H1. If any V-gate fails, the plan-authoring turn HALTs.
H2. If the pre-stage git index is non-empty, the turn HALTs and remediates by unstaging contaminants before staging the plan.
H3. If the staged file count is anything other than 1 at commit time, the turn HALTs and remediates.
H4. If the integrity of any reference report (selection plan, park report, audit, loader build, validator build) shows sha mismatch against the values cited in this plan, the turn HALTs and surfaces the drift.

NO-ACTION attestations:

- This plan does NOT compute RSI (no RSI value is computed; the formula reference in section 8 is descriptive text, not an executed computation).
- This plan does NOT compute any signal.
- This plan does NOT run a simulator.
- This plan does NOT run a backtest.
- This plan does NOT fetch data.
- This plan does NOT call yfinance, Yahoo Finance, Databento, or any vendor.
- This plan does NOT access DATABENTO_API_KEY.
- This plan does NOT inspect OOS.
- This plan does NOT touch live trading, brokerage, review_queue, idea_memory, Strategy Lab, ORB artifacts, or Step 30 cost constants.
- This plan does NOT modify s7 D1 artifacts.
- This plan does NOT authorize the s9 build phases; each requires fresh operator authorization.

## 21. Next authorization required

A future operator authorization is required to proceed beyond this Tier-N spec. That authorization shall reference this plan by exact path:

`docs/s9_cross_asset_mean_reversion_rsi2_tier_n_specification_plan.md`

The next operator authorization in the established controller-session pattern shall use one of these scopes (mirroring the per-phase sequence in section 18):

- **"Authorize s9 data audit reference attestation only"** (P2; optional; may be skipped).
- **"Authorize s9 loader-reuse decision plan only"** (P3).
- **"Authorize s9 validator-reuse decision plan only"** (P4).
- **"Authorize s9 signal-module specification plan only"** (P5; the next plan-authoring step that introduces the RSI(2) computation logic at spec level).
- **"Authorize s9 Tier-N spec revision only"** (if the operator wishes to revise this Tier-N spec, e.g., to allow short-side or to adjust the locked thresholds).

This Tier-N spec is the source of truth for the s9 mechanic, sizing, costs, and gates. The build phases (P3-P12) inherit the lock from this spec byte-equivalent; departing from any locked value requires a fresh `_revN_` spec under separate authorization.

No phase of this chain confers any standing authorization for OOS inspection, Strategy Lab promotion, brokerage connection, or live trading. Each remains BLOCKED at separate plans. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.

----

End of plan. Tier-N specification authoring only. No code. No RSI computation. No signal computation. No simulator. No backtest. No data fetch. No yfinance. No Yahoo Finance. No Databento. No DATABENTO_API_KEY access. No brokerage. No real order. No paper order. No Strategy Lab promotion. No review_queue mutation. No production idea_memory mutation. No ORB branch mutation. No s7 D1 artifact modification. No s7 D1 resurrection. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.
