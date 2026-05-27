# S13-D1 P6.5 cost-stress matrix result (sealed)

**Candidate record id:** `s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history`
**Phase:** `PHASE2-S13-D1-MNQ-RSI-2-BIDIR` / `P6_5_COST_STRESS`
**Backtest run_id:** `PHASE2-S13-D1-P6-5-66f6be4525fa`
**Authored (UTC):** `2026-05-27T18:44:35.847408Z`
**Lifecycle state:** P6_5_COST_STRESS_SEALED
**Report seal sha256:** `2bb04d5f8d3afbc58770ef748be9b4ce81358b6b6c7a7e892168cb7a77d53c51`
**Parent P6 IS sealed sha256:** `dc480c714c27711a542b47eccc08d74189081c58066ecbc4c27237ac2425de83` (commit 3fa479a)

## Verdict: `REJECT_FAST`

### Verdict reasons

- DR10 fires: annual_turnover=84.7851 > 0.50

### Verdict caveats (LOAD-BEARING)

- P6.5 cost-stress reading is IS-only; OOS cost-stress requires separate P10 authorization
- DR2 canonical definition is OOS-specific; the P6.5 reading is a provisional IS-only monitor, not a binding evaluation
- DR4 (oos_negative_while_is_positive_unexplained) is structurally NOT_EVALUABLE at P6.5 IS-only; deferred to P10
- K12 cost-stress DR aggregate evaluated strictly over DR3+DR5 at IS; DR2 provisional record only; DR4 deferred
- P6.5 verdict NEVER implies live-readiness; 6-gate live-block applies regardless of any verdict
- P7 decision memo NOT yet authored; this report does NOT promote to OOS
- DR10 (turnover) elevated: annual_turnover=84.7851 >> 0.50; mitigated structurally by DA4=C START_CASH $200k

## Cost-stress matrix (S0 -> S4 on IS window 2019-05-13 -> 2023-12-29)

| Tier | cost_scalar | slippage_scalar | trades | net_pnl_usd | expectancy_usd | sharpe_proxy | |maxDD%| | total_costs | cost_drag | edge_pos |
|---|---|---|---|---|---|---|---|---|---|---|
| S0 | 0.0 | 0.0 | 159 | $102,795.23 | $646.51 | 0.1237 | 15.2323% | $0.00 | 0.0000% | YES |
| S1 | 1.0 | 1.0 | 159 | $85,975.59 | $540.73 | 0.1076 | 17.6842% | $3,122.70 | 1.5614% | YES |
| S2 | 1.5 | 1.5 | 159 | $87,464.25 | $550.09 | 0.1096 | 17.1550% | $4,693.50 | 2.3467% | YES |
| S3 | 2.0 | 2.0 | 159 | $83,206.05 | $523.31 | 0.1046 | 17.6128% | $6,220.20 | 3.1101% | YES |
| S4 | 3.0 | 3.0 | 159 | $79,058.33 | $497.22 | 0.1000 | 18.5689% | $9,261.00 | 4.6305% | YES |

## DR evaluation summary

| DR | Definition (canonical) | Evaluable at P6.5 IS-only | Fires (binding) | Outcome |
|---|---|---|---|---|
| DR3 | zero_cost_only_survival (S0>0 AND all S1..S4<=0) -> REJECT_FAST | YES (binding) | False | DOES_NOT_FIRE |
| DR5 | cost_stress_turns_edge_negative tier flip -> REJECT_FAST or INCONCLUSIVE_HOLD | YES (binding) | False | DOES_NOT_FIRE |
| DR10 | annual_turnover>0.50 OR S2_cost_drag>0.05 -> REJECT_FAST | YES (binding) | True | REJECT_FAST |
| DR2 | oos_metrics_degrade_materially_under_cost_stress -> REJECT_FAST | NO (OOS-canonical); provisional IS monitor only | provisional=False | DEFERRED_TO_P10_OOS_FOR_CANONICAL_EVALUATION |
| DR4 | oos_negative_while_is_positive_unexplained -> REJECT_FAST | NO (OOS-only) | n/a | NOT_EVALUABLE_AT_P6_5_IS_ONLY; DEFERRED_TO_P10_OOS_GATE |

K12 aggregate (DR2/DR3/DR4/DR5 cost-stress firing): binding-scope evaluation over DR3+DR5 strictly → **DOES_NOT_FIRE**.

## DR10 detail

- `S1 annual_turnover` = 84.7851 > 0.50 → FIRES
- `S2 cost_drag` = 2.3467% <= 5.00% → does not fire
- Mitigation note: DA4=C ($200k START_CASH) structurally halves per-dollar cost pressure vs default $100k; observed S2 cost_drag remains below the 5% critical threshold.
- DA14=A: byte-equivalent annual_turnover threshold 0.50 inherited from s11/s12 chain (no relaxation).

## DR3 detail (zero-cost-only-survival)

- S0 expectancy positive: True (S0 expectancy = $646.51)
- All of S1..S4 expectancy <= 0: False
- Tier expectancies: 
    - S0: $646.51
    - S1: $540.73
    - S2: $550.09
    - S3: $523.31
    - S4: $497.22

## DR5 detail (cost-stress tier flip)

- Tier flip detected: False 
- Monotone-degradation check on `expectancy_per_trade_usd` across S0 -> S4: no positive-to-negative tier flip observed.

## DR2 provisional IS reading (NOT BINDING at P6.5)

- sharpe_proxy degradation S0 -> S4: 19.1593% (provisional threshold 50%)
- expectancy degradation S0 -> S4: 23.0917% (provisional threshold 50%)
- Provisional fires: False
- Canonical DR2 evaluation requires OOS; binding outcome deferred to P10.

## P6 reproduction check (S1 must match sealed P6 numbers)

| Metric | P6 sealed | P6.5 S1 fresh | Match |
|---|---|---|---|
| closed_trades_count | 159 | 159 | True |
| net_pnl_usd | $85,975.59 | $85,975.59 | True |
| expectancy_per_trade_usd | $540.73 | $540.73 | True |
| sharpe_proxy_per_trade | 0.1076 | 0.1076 | True |
| max_drawdown_pct | 0.176842 | 0.176842 | True |
| annual_turnover | 84.7851 | 84.7851 | True |
| **All match** | | | **True** |

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
| P6 IS diagnostic | `3fa479a` | `dc480c714c27711a...` |

## Status

trading: PAUSED · live: BLOCKED_AT_6_GATES · FRC: NEVER_GRANTED · lifecycle: P6_5_COST_STRESS_SEALED · REC1-equivalent binding: True · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE
