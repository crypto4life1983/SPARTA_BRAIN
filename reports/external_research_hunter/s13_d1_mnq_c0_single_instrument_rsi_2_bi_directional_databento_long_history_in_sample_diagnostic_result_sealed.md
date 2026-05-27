# S13-D1 P6 IS diagnostic result (sealed)

**Candidate record id:** `s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history`
**Phase:** `PHASE2-S13-D1-MNQ-RSI-2-BIDIR` / `P6_IS_DIAGNOSTIC`
**Backtest run_id:** `PHASE2-S13-D1-IS-8cad245b4511`
**Authored (UTC):** `2026-05-27T18:26:33.038945Z`
**Lifecycle state:** P6_IS_DIAGNOSTIC_SEALED
**Report seal sha256:** `dc480c714c27711a542b47eccc08d74189081c58066ecbc4c27237ac2425de83`
**Reseal verified on disk:** YES (UTF-8 explicit)

## Verdict: `READY_FOR_LONGER_BACKTEST`

### Verdict reasons

- All gates PASS: A1 trades=159>=100, A2 sharpe_proxy=0.1076>0, A3 expectancy=$540.73>0, A4 |maxdd|=17.68%<=50%

### Verdict caveats (LOAD-BEARING)

- P6 IS verdict reflects IS-window performance only; OOS verdict requires separate P10 authorization
- REC1-equivalent (binding): OOS K9 reachable at lower bound; if observed IS rate falls below 25/year, OOS K9 unreachability becomes structurally probable
- P6 IS PASS NEVER implies live-readiness; 6-gate live-block applies regardless of any verdict
- P6.5 cost-stress not yet run; DR2/DR3/DR4/DR5/DR10 thresholds NOT YET EVALUATED at S0/S2/S3/S4 tiers
- annual_turnover=84.785 > 0.50; DR10 risk elevated

## Performance summary

| Metric | Value |
|---|---|
| `starting_cash_usd` | $200,000.00 (DA4=C) |
| `final_equity_usd` | $285,975.58 |
| `net_pnl_usd` | $85,975.59 |
| `total_costs_usd` | $3,122.70 |
| `max_drawdown_pct` (magnitude) | 17.6842% |
| `longest_drawdown_days` | 756 |
| `cagr_pct` | 8.0299% |
| `sharpe_annualized` | 0.5503 |
| `sortino_annualized` | 0.5199 |
| `sharpe_proxy_per_trade` | 0.1076 |
| `expectancy_per_trade_usd` | $540.73 |
| `profit_loss_ratio` | 0.6938 |
| `win_rate_pct_or_NA_INSUFFICIENT_SAMPLE` | 65.41 |
| `closed_trades_count` | 159 |
| `trades_per_year_observed` | 34.34 |
| `annual_turnover` | 84.7851 |
| `s2_cost_drag_fraction_estimate` | 2.3420% |

## Trade diagnostics

| Field | Value |
|---|---|
| Closed trades | 159 |
| Long / Short | 74 / 85 |
| Stop exits | 29 |
| RSI exits | 130 |
| Window-end | 0 |
| Wins / Losses | 104 / 55 |

## Scan diagnostics

| Field | Value |
|---|---|
| Bars processed | 1443 |
| Bars after warmup | 1223 |
| Warmup days | 220 |
| IS window | 2019-05-13 -> 2023-12-29 (~4.6297y) |
| CSV sha verified | True |
| OOS bars NEVER read in signal logic | True |

## C6 inherited_constraints_block (carried verbatim from P2; 16 entries)

1. REC1-equivalent (BINDING): OOS K9 reachable at lower bound with thin margin (~50-65 trades/year vs 50/year floor). If observed IS rate falls below 25/year on RSI(2) bi-directional, OOS K9 unreachability becomes structurally probable. The s9 RSI-2 baseline observed 414 trades over long-only 4-ETF window; if MNQ.c.0 bi-directional rate falls below half that proportional rate, OOS K9 fires. If OOS K9 fires, the OOS verdict shall be OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE analogous to S10-D2 P11 PARK at 23c7164 and s12-d1 P11 park at ecbd001. The chain shall NOT relax K9 at OOS; the appropriate response is to seal the INSUFFICIENT_SAMPLE / INDETERMINATE verdict and park the candidate. Pursuing s13-d1 accepts the structural possibility of an OOS PARK outcome if the IS rate falls below the DRAFT-estimated 50-65/y band.
2. DA3=B (BINDING): per-trade risk pct = 0.005 (0.5%); REVISED at SEAL from default 1.0% for DR3 mitigation
3. DA4=C (BINDING): START_CASH_USD = 200000 ($200k); REVISED at SEAL from default $100k for DR10 mitigation
4. K9-reachability discipline (NEW framework standard from 0e3f9d4) applied at PLAN+DRAFT+SEAL+P1+P2+P3+P4+P6; binding for all subsequent phases
5. K9_THRESHOLD_INVIOLATE: closed_trades >= 100; no relaxation at any phase
6. Mechanic family F3 RSI(2) bi-directional mean-reversion LOCKED at PLAN
7. RSI thresholds 10/50/90/50 LOCKED at PLAN; modification post-SEAL FORBIDDEN per RF13
8. DR3 risk ELEVATED (RSI lineage s9 falsification precedent); mitigated via DA3=B
9. DR10 risk ELEVATED (high-frequency turnover ~50-65 trades/y); mitigated via DA4=C ($200k START_CASH)
10. Tier-N spec LOCKED byte-equivalent at 262491c
11. P1 plan-lock LOCKED byte-equivalent at 005cb8a
12. s12-d1 terminal park (PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS at ecbd001) preserved unchanged
13. All parallel-session shorter-path sealed artifacts byte-stable; not anchored by this chain
14. Expected terminal verdict if OOS K9 fires: PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED
15. P6 PASS does NOT imply READY_FOR_LONGER_BACKTEST at OOS
16. P6 PASS NEVER implies live-readiness; 6-gate live-block applies regardless of any verdict

## Parent references

| Phase | Commit | Seal sha256 |
|---|---|---|
| Tier-N SEAL | `262491c` | `2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775` |
| P1 plan-lock | `005cb8a` | `1cac253cbbbf4cdab87e777edbe0bca00739e925de382bd1d687faae9731052c` |
| P2 phase-2 plan | `beecd87` | `b181ce834f5eacd2fb9f6766d6ce9404a86ecfe3d2787c7e4899d3e47ba57ec6` |
| P3 BUILD (3 reports) | `24625c6` | runner/IS/OOS sealed |
| P4 smoke | `c44fb13` | `35b803450d5dd554...` |

## Status

trading: PAUSED · live: BLOCKED_AT_6_GATES · FRC: NEVER_GRANTED · lifecycle: P6_IS_DIAGNOSTIC_SEALED · REC1-equivalent binding: True
