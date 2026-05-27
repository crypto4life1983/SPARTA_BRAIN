# S10-D2 vs S11-D1 next-path comparison memo (sealed; decision-support)

**Schema:** `sparta.external_research_hunter.s10_d2_vs_s11_d1_next_path_comparison_memo.v1`  
**Authored at (UTC):** `2026-05-27T13:58:25Z`  
**Authorization phrase received:** *"Authorize RUN_COMPARISON_MEMO_FIRST."*  
**Memo is binding as decision-support:** `True`  
**Memo authorizes any execution:** `False` (decision-support only)  
**Report seal sha256:** `d14c886416383916b7bd17f6f698d49acf3f5ba1c4c2bec8e66a0fbcd5ce1815`

## Binding context predecessors

| Anchor | Commit | Seal sha256 (16-char prefix) | Role |
|--------|--------|------------------------------|------|
| `p10_5_oos_cost_stress_sweep` | `89ca9a7` | `2b268b897639ec9a..` | verdict OOS_COST_STRESS_SURVIVES; candidate remains PARKED; closes S10-D2 OOS cost-stress diagnostic question |
| `s11_d1_p3_implementation_plan_memo` | `1ad8d83` | `a8a433b981846654..` | binding-as-a-plan; CONDITIONAL_GO recommendation; does not authorize execution |
| `s11_d1_rev2_tier_n_spec` | `c110fd4` | `46659b4a8a73cb72..` | binding Tier-N anchor for any future S11-D1 P3 BUILD |
| `s11_d1_p1_rev_m_reanchor_memo` | `ec503d4` | `56adfa13d2f17632..` | decision-support memo recommending rev2 anchoring for future P3 |
| `s10_d2_continuation_track_selection_plan` | `c466a96` | - | selected Option 1 as primary (= P10.5 sweep that 89ca9a7 then executed); other continuation options remain documented but unauthorized |
| `s10_d2_p11_park_memo` | `23c7164` | `e121b82b411697c7..` | terminal park record; PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED |
| `s11_d1_v1_tier_n_spec_historical_anchor_for_p1_and_p2` | `9c63088` | `077e29e62f23dbc3..` | v1 sealed; binds P1 + P2; superseded by rev2 for future anchoring only |

## Section 1 - Evidence table

Evidence-base comparison post-89ca9a7. Values are taken verbatim from sealed predecessor artifacts; no fresh computation by this memo.

| Dimension | S10-D2 (continuation) | S11-D1 (P3 BUILD expected) |
|-----------|------------------------|----------------------------|
| Universe | {NQ.c.0, GC.c.0, ZN.c.0, CL.c.0} (4 markets) | {MNQ.c.0} (1 market) |
| Starting cash | $500,000 | $50,000 |
| IS window | 2013-01-01..2022-12-30 (10.0y) | 2019-05-13..2023-12-29 (4.6y) |
| OOS window | 2023-01-01..2025-12-31 (3.0y) | 2024-01-02..2025-12-30 (2.0y) |
| IS closed trades (ACTUAL / expected) | 200 actual | 25-50 expected (per rev2 k9_risk_disclosure) |
| OOS closed trades (ACTUAL / expected) | 53 actual | ~10-22 expected |
| IS K9 (closed_trades >= 100) | PASS (200 >= 100) | EXPECTED FAIL (25-50 < 100) |
| OOS K9 (closed_trades >= 100) | FAIL (53 < 100) | EXPECTED FAIL (10-22 < 100) |
| IS cost-stress (P6.5) | PASS (READY_FOR_NEXT_PHASE; A8 PASS; K12 not fired) | NOT YET RUN |
| OOS cost-stress (P10.5) | PASS (OOS_COST_STRESS_SURVIVES, NEW from 89ca9a7; S0/S2/S3 all positive; K12 OOS not fired) | NOT YET RUN |
| K10 pairwise dependence (IS) | PASS (avg=+0.0528 vs 0.50 threshold; from this session 4ddaa84) | N/A (single instrument; trivially 1) |
| Strategy logic | Donchian 55/20 no-pyramid + Wilder ATR(20) 2N stop + 1% risk + max_units=1 + AMB6 NONE | Byte-equivalent to S10-D2 mechanic on single-instrument subset |
| Lifecycle phase | TERMINAL (P11 PARK at 23c7164; P10.5 supplemental at 89ca9a7) | P2 sealed; P3 BUILD NOT authorized |
| Expected terminal verdict if continued | Stays PARKED (K9 binding; no further diagnostic can unpark) | OOS INSUFFICIENT_SAMPLE (per rev2 k9_risk_disclosure honest admission) |
| Implementation cost from here | Low (further read-only sweeps against existing cache; ~minutes-hours per sweep) | High (P3 BUILD authoring ~30-60 min for 11 source/test files + sealed build reports; then P4 smoke; P6 IS; P6.5 cost-stress; P10 OOS; P11 park; multi-hour cumulative) |
| Methodology template value delivered | Already produced (S10-D2 chain IS the cross-asset multi-instrument template) | New single-instrument futures-Donchian template (does not currently exist anywhere) |
| K9 binding constraint | Yes (53 < 100; no further diagnostic addresses K9; only fresh-data fetch + fresh-candidate-id resolves) | Yes (more binding than S10-D2 due to shorter windows) |
| Live-block status | PERMANENT (BLOCKED_AT_6_GATES; no verdict can unblock) | PERMANENT (same as S10-D2) |

## Section 2 - Why S10-D2 survived OOS cost-stress but remains PARKED

**What P10.5 actually tested:** P10.5 evaluated whether the S10-D2 candidate's edge survives variation in the cost-tier dimension at OOS. The cost-tier axis is one specific robustness dimension (commission + fees + tick-slippage scalars applied to fills). It does NOT vary trade-count, sample-size, regime coverage, or any other robustness dimension.

**What OOS_COST_STRESS_SURVIVES means (verbatim from `89ca9a7`):** All 4 cost tiers (S0/S1/S2/S3) produced positive net PnL, positive sharpe, positive expectancy, zero safety-counter fires, and max-drawdown well under the K4 50% magnitude floor (range -12.81% to -13.49%). DR2/DR3/DR5 OOS = False. K12 OOS = False. S2 = 95.0% of S1 (slightly more robust than IS S2 = 93.9%); S3 = 88.6% of S1 (slightly more robust than IS S3 = 84.7%).

**Why park status did not change:** K9 sample-size is the binding constraint, and cost-stress does not address it BY DESIGN. From 89ca9a7's sealed text: 'cost-stress varies cost-tier but NOT closed_trades count; this sweep does not address K9 by design.' All 4 tiers had the SAME 53 closed trades. K9 OOS threshold is 100. Park_status_enum stays PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED; candidate_remains_parked=True; no_unpark=True; lifecycle_status_unchanged=True; no_oos_confirmation_claim=True.

### Diagnostic questions now CLOSED for S10-D2

- IS K9 sample sufficiency: PASS (200 trades)
- IS cost-stress robustness: PASS (P6.5)
- OOS K9 sample sufficiency: FAIL (53 trades) -- binding
- OOS cost-stress robustness: PASS (P10.5 89ca9a7)
- K10 pairwise dependence: PASS
- Safety counters across IS + 5 IS cost tiers + OOS + 4 OOS cost tiers: zero across the board
- No-pyramid invariant: held
- Starting-cash invariant: held

### Diagnostic questions STILL OPEN but cannot unpark under existing data

- Per-market PnL stratification (would diagnose concentration risk but doesn't change K9)
- Regime-stratified OOS evaluation (would test regime-conditional behavior but doesn't change K9)
- Walk-forward decomposition (would test path-dependence but doesn't change K9)
- Longer OOS window via fresh Databento fetch (WOULD address K9 but requires fresh authorization + fresh candidate id per discipline; not a continuation of the parked candidate)

- Park is terminal for this candidate id: `True`
- Any unparking requires fresh candidate id: `True`

## Section 3 - Why S11-D1 P3 BUILD is expected to hit K9 INSUFFICIENT_SAMPLE

**rev2 spec's own honest admission (verbatim):** From rev2 (byte-equivalent to v1) k9_risk_disclosure: 'IS RESULT MAY FIRE K9. If IS closed_trades < 100, the IS verdict will be INSUFFICIENT_SAMPLE (not FAIL_SAFETY). The chain shall NOT relax K9; the appropriate response is to seal the INSUFFICIENT_SAMPLE verdict and consider fresh research options under separate authorizations.' From rev2 expected_trade_count_is_window_estimate: 'Daily Donchian-55/20 on a single instrument over 4.6 years is historically sparse. S10-D2 NQ produced 54 trades over 10 years (~5.4/year); scaled to a 4.6y single-instrument IS window, the expected closed_trades is approximately 25-50 BEFORE accounting for differences in market regime, contract size, or MNQ.c.0-vs-NQ.c.0 specific behavior. THIS IS BELOW THE K9 THRESHOLD OF 100.'

**Structural arithmetic:** S10-D2's NQ leg (the closest reference) produced 54 trades over 10 years = 5.4/year. S11-D1's MNQ.c.0 leg over 4.6y IS at the same Donchian 55/20 daily breakout rate would produce approximately 4.6 * 5.4 = 25 trades, with upside variance to ~50 if MNQ has slightly higher base-rate crossings than NQ. Both endpoints are below K9 = 100. OOS over 2.0y at 5.4/year = 11 trades; upside variance to ~22 trades. Both well below K9.

**What P3 BUILD can NOT do:** P3 BUILD is source-authoring work. It does not change the structural arithmetic above. No P3 BUILD activity (source code, tests, build reports) can add trades to the historical sample; the sample is determined by the data + the strategy parameters. P3 BUILD's role is to make execution POSSIBLE under separate authorization; it does not change WHAT execution would produce.

**What P6 IS execution would produce:** Per rev2's honest disclosure, IS verdict is most likely INSUFFICIENT_SAMPLE. The chain pre-commits to seal that verdict rather than relax K9.

**What P10 OOS execution would produce:** OOS over 2.0y will produce fewer trades than IS over 4.6y. OOS verdict will almost certainly be INSUFFICIENT_SAMPLE or OOS_INDETERMINATE pattern analogous to S10-D2 P10's verdict.

**Expected terminal verdict:** `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED (analogous to S10-D2 P11 PARK at 23c7164)`

**What P3 BUILD DOES produce independent of verdict:** A single-instrument futures-Donchian template that doesn't currently exist anywhere in the repo. The runner harness + drivers + tests + sealed build reports form a reusable scaffolding pattern. Future single-instrument candidates (S11-D2, S12-D1, etc.) could reference S11-D1's runner harness as the template.

## Section 4 - Three research goals separated

### goal_1_strategy_validation

- **`definition`**: Determine whether a specific strategy specification has a real, persistent edge that survives OOS evaluation with statistically sufficient sample size.
- **`k9_role_in_this_goal`**: BINDING. Sample size < 100 -> verdict cannot be CONFIRMED.
- **`s10_d2_status_for_this_goal`**: STRUCTURALLY UNREACHABLE (OOS K9 = 53; cannot be increased without fresh data fetch + fresh candidate id)
- **`s11_d1_status_for_this_goal`**: STRUCTURALLY UNREACHABLE (OOS K9 expected 10-22)
- **`fresh_higher_density_candidate_status_for_this_goal`**: POTENTIALLY REACHABLE (depends on candidate design; mechanics with higher trade-density could clear K9)
- **`halt_and_wait_status_for_this_goal`**: NEUTRAL (no progress; no regression)

### goal_2_methodology_template_building

- **`definition`**: Build a library of reusable runner-harness scaffolding patterns covering distinct candidate-design archetypes (cross-asset multi-instrument, single-instrument, vol-targeting, mean-reversion, etc.) such that future candidate authoring is faster and more disciplined.
- **`k9_role_in_this_goal`**: NOT BINDING. Template value is independent of trade count.
- **`s10_d2_status_for_this_goal`**: ALREADY DELIVERED (cross-asset multi-instrument template; runner harness at external_research_hunter/s10_d2_..._runner_harness/)
- **`s11_d1_status_for_this_goal`**: UNIQUELY DELIVERABLE (single-instrument futures-Donchian template would be NEW; does not currently exist in repo)
- **`fresh_higher_density_candidate_status_for_this_goal`**: ALSO DELIVERS (depends on which archetype the fresh candidate exercises)
- **`halt_and_wait_status_for_this_goal`**: NEGATIVE (no template advance)

### goal_3_edge_discovery

- **`definition`**: Find a strategy class with a real economic edge that could (under separate authorization, fresh top-level approval, and full risk review) eventually be promoted out of the permanent BLOCKED_AT_6_GATES posture.
- **`k9_role_in_this_goal`**: BINDING in the sense that 'discovery' requires a sample large enough to distinguish edge from noise. Without K9 >= 100, any apparent edge is suspect.
- **`live_block_role_in_this_goal`**: PERMANENT for all current candidates. Edge discovery is a multi-month/year research program that produces evidence; it does NOT itself unblock live trading. Live trading unblocking is a fresh top-level operator authorization after full risk review per operating rules clause 7.
- **`s10_d2_status_for_this_goal`**: LOW (parked; K9 binding; cannot discover edge from insufficient sample)
- **`s11_d1_status_for_this_goal`**: LOWER (more K9-bound than S10-D2)
- **`fresh_higher_density_candidate_status_for_this_goal`**: POTENTIALLY HIGHER (e.g., F3 RSI-2 mean-reversion had 414 trades on s9 ETF-proxy -- well clear of K9, although s9 ultimately parked PARKED_SAFE_BUT_NOT_MONEY_PROVEN). Mechanics with higher trade density don't structurally fail K9, opening discovery potential subject to their own verdict ladder.
- **`halt_and_wait_status_for_this_goal`**: NEUTRAL

### Per-goal best path (documented only)

- **`strategy_validation`**: PURSUE_FRESH_HIGHER_DENSITY_CANDIDATE (only path with reachable verdict)
- **`methodology_template_building`**: START_S11_D1_P3_BUILD (unique template value) OR PURSUE_FRESH_HIGHER_DENSITY_CANDIDATE (depends on archetype)
- **`edge_discovery`**: PURSUE_FRESH_HIGHER_DENSITY_CANDIDATE (higher base-rate gives K9 headroom; subject to own K-gate / DR-rule survival)

## Section 5 - Decision matrix

Options evaluated: `CONTINUE_S10_D2`, `START_S11_D1_P3_BUILD`, `PURSUE_FRESH_HIGHER_DENSITY_CANDIDATE`, `HALT_AND_WAIT`

### `CONTINUE_S10_D2`

- **`strategy_validation_value`**: LOW (parked; cannot unpark with existing data)
- **`methodology_template_value`**: LOW (template already produced)
- **`edge_discovery_value`**: LOW (K9 trapped)
- **`time_cost`**: LOW (read-only sweeps against existing cache; minutes-hours per sweep)
- **`race_risk_with_parallel`**: MEDIUM (parallel session is the active S10-D2 author; canonical-path race possible)
- **`opportunity_cost`**: MEDIUM (time spent here is time not on a candidate that can unpark)
- **`what_it_produces`**: Marginal diagnostic refinements of an already-parked candidate; no verdict change possible
- **`best_for_which_goal`**: NONE (no goal is materially advanced)

### `START_S11_D1_P3_BUILD`

- **`strategy_validation_value`**: LOW (expected INSUFFICIENT_SAMPLE per rev2 disclosure)
- **`methodology_template_value`**: HIGH (unique single-instrument futures-Donchian template)
- **`edge_discovery_value`**: LOW (K9 trapped)
- **`time_cost`**: HIGH (multi-hour for P3 BUILD alone; plus P4 + P6 + P6.5 + P10 + P11 sequence)
- **`race_risk_with_parallel`**: HIGH (parallel session has been actively authoring S11-D1 work; multiple race patterns documented this session)
- **`opportunity_cost`**: HIGH (multi-hour committed to a candidate expected to land at INSUFFICIENT_SAMPLE)
- **`what_it_produces`**: Reusable template + sealed INSUFFICIENT_SAMPLE record + methodology lessons
- **`best_for_which_goal`**: methodology_template_building (only)

### `PURSUE_FRESH_HIGHER_DENSITY_CANDIDATE`

- **`strategy_validation_value`**: MEDIUM-HIGH (only path where K9 floor is reachable; success not guaranteed but POSSIBLE)
- **`methodology_template_value`**: MEDIUM-HIGH (depends on archetype; new mechanic family = new template)
- **`edge_discovery_value`**: MEDIUM-HIGH (higher base-rate gives K9 headroom)
- **`time_cost`**: VERY HIGH (full new candidate lifecycle: selection plan -> tier-N spec -> P1-P11; potentially weeks)
- **`race_risk_with_parallel`**: MEDIUM (depends on which candidate; parallel session has been opening S11-D1 family work; fresh candidate may be in less-contested namespace)
- **`opportunity_cost`**: VERY HIGH upfront, BUT highest expected payoff per unit of research time among the four options
- **`what_it_produces`**: A candidate with a reachable verdict ladder (assuming K-gate / DR-rule survival)
- **`best_for_which_goal`**: ALL THREE (strategy_validation, edge_discovery, and template if archetype is new)
- **`candidate_id_options_documented_only`**:
  - T2-T9 from selection plan at commit 556ab3f (S10-D1 family) for non-equity mechanic alternatives
  - F3 RSI-2 mean-reversion family applied to a non-ETF-proxy universe (closes s9 ETF-proxy failure mode; ~414 trade reference base-rate)
  - F2 vol-targeting at weekly cadence (B006_001 reference; ~50 trades/year scaled by window)
  - Intraday-bar Donchian (higher base-rate but requires new data scope; Databento intraday fetch authorization)
  - Multi-symbol diversified basket with carefully chosen low-correlation members (more careful K10 design; higher base-rate via diversification)

### `HALT_AND_WAIT`

- **`strategy_validation_value`**: NEUTRAL (no progress; no regression)
- **`methodology_template_value`**: NEUTRAL
- **`edge_discovery_value`**: NEUTRAL
- **`time_cost`**: ZERO (no controller work)
- **`race_risk_with_parallel`**: ZERO (no controller activity to race)
- **`opportunity_cost`**: LOW IF parallel session is actively working AND operator wants time to review prior decisions; MEDIUM IF parallel session is also idle
- **`what_it_produces`**: Time for operator review and parallel session to surface new work
- **`best_for_which_goal`**: NONE directly; INDIRECTLY supports better decision-making on a future authorization

## Section 6 - Opportunity cost per path

### `CONTINUE_S10_D2`

OPPORTUNITY COST = controller time spent on diagnostic refinements of a parked candidate is time NOT spent on a candidate that could clear K9. Estimate: each sweep takes minutes-to-hours; cumulative cost of running per-market stratification + regime-stratified eval + walk-forward + etc. could be ~3-6 hours over multiple turns. None changes the PARK status. The 89ca9a7 commit already closed the highest-value remaining S10-D2 diagnostic question.

### `START_S11_D1_P3_BUILD`

OPPORTUNITY COST = ~30-60 min P3 BUILD authoring + ~30 min build report sealing + ~30 min P4 smoke + ~1-2 hr P6 IS execution + ~1-2 hr P6.5 cost-stress sweep + ~1 hr P7 decision memo + ~1-2 hr P10 OOS execution + ~30 min P11 park memo = ~6-10 hours cumulative for a candidate that rev2's own honest disclosure says is expected to land at INSUFFICIENT_SAMPLE. The methodology-template value is real but is a thin justification for that much investment.

### `PURSUE_FRESH_HIGHER_DENSITY_CANDIDATE`

OPPORTUNITY COST = highest in absolute terms (full new candidate lifecycle: selection memo -> tier-N spec DRAFT -> spec SEAL -> P1 plan-lock -> P2 phase-2 plan -> P3 BUILD -> P4 smoke -> P6 IS -> P6.5 cost-stress -> P7 decision memo -> P10 OOS -> P11 lifecycle decision; potentially weeks of cumulative work), but highest EXPECTED PAYOFF per unit time among the four options because it's the only one with a reachable verdict ladder. The cost is amortized across multiple sessions; each phase is its own short authorization.

### `HALT_AND_WAIT`

OPPORTUNITY COST = lowest absolute cost (zero); but indefinitely waiting doesn't advance any goal. Justified ONLY as a temporary state to absorb context, let parallel session surface new work, or give the operator decision-making time. Not a long-term answer.

## Section 7 - Final recommendation

### Primary: **`PURSUE_FRESH_HIGHER_DENSITY_CANDIDATE`** (strength: **`MODERATE`**)

**Rationale:** Both S10-D2 continuation and S11-D1 P3 BUILD run into the same K9 sample-size wall. 89ca9a7 closed S10-D2's highest-value remaining diagnostic question; further S10-D2 work has low marginal information value. S11-D1 P3 BUILD is multi-hour work for a candidate expected to terminate at INSUFFICIENT_SAMPLE (per rev2's own disclosure). Only PURSUE_FRESH_HIGHER_DENSITY_CANDIDATE has a structurally reachable verdict ladder, and only PURSUE delivers across all three research goals (validation, template, discovery).

**Caveats:**

- Strength is MODERATE, not STRONG, because the operator's specific research priorities (strategy validation vs methodology breadth vs edge discovery) are not explicitly stated. If methodology-template-breadth is the dominant priority, START_S11_D1_P3_BUILD becomes WEAKLY recommended.
- PURSUE_FRESH_HIGHER_DENSITY_CANDIDATE requires authoring a fresh selection plan + tier-N spec + full P1-P11 lifecycle. This is a multi-week commitment.
- The fresh candidate must satisfy first-principles-burden against the parked/failed predecessors (s7-D1 + s8-D1 + s9 + s10-D1 + s10-D2 + B005 + B006 + NKE + D5); spec authoring must explicitly enumerate why the fresh candidate isn't a hidden rescue of any of those.
- Live-block (BLOCKED_AT_6_GATES) is permanent regardless of which candidate wins; this recommendation is about research-time efficiency, not about unlocking trading.

### Secondary: **`HALT_AND_WAIT`** (strength: **`WEAK`**)

**Rationale:** Defensible as a short-term holding state: parallel session has been highly active and may surface additional S10-D2 diagnostics or fresh-candidate authoring on its own. Operator can also use the idle time to review the full sealed-artifact chain accumulated this session before committing to the next multi-hour or multi-week direction.

### Not recommended as primary

- **`CONTINUE_S10_D2`**: Low marginal information value; parked candidate stays parked.
- **`START_S11_D1_P3_BUILD`**: Multi-hour investment for an expected INSUFFICIENT_SAMPLE outcome; only justified if methodology-template-breadth is the dominant priority.

- Recommendation is advisory only / not self-authorizing: `True`
- Operator decides via separate explicit authorization phrase: `True`
- This memo does not authorize any path: `True`

## Section 8 - Posture invariants (all held by this memo)

- `trading_status`: `PAUSED`
- `live_status`: `BLOCKED_AT_6_GATES`
- `frc_granted`: `False`
- `advisory_label_permanent`: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- `verdict_never_means_live_ready`: `True`
- `live_promotion_path_closed`: `True`
- `no_strategy_optimization_authorized`: `True`
- `no_profitability_claim`: `True`
- `no_oos_confirmation_claim`: `True`
- `no_oos_confirmation_claim_beyond_exact_sealed_wording_in_89ca9a7`: `True`
- `live_block_is_permanent_independent_of_any_candidate_outcome`: `True`

## Hard boundaries (all held this memo turn)

- `no_authorization_of_any_phase`: `True`
- `no_authorization_of_fresh_candidate_lifecycle`: `True`
- `no_authorization_of_s10_d2_continuation_execution`: `True`
- `no_authorization_of_s11_d1_p3_build`: `True`
- `no_backtest`: `True`
- `no_branch_change`: `True`
- `no_broker_call`: `True`
- `no_brokerage_connection`: `True`
- `no_cache_mutation`: `True`
- `no_candidate_promoted`: `True`
- `no_data_databento_cache_modification`: `True`
- `no_data_databento_cache_oos_modification`: `True`
- `no_data_fetch`: `True`
- `no_databento_api_call`: `True`
- `no_databento_api_key_access`: `True`
- `no_external_network_call`: `True`
- `no_frc_grant`: `True`
- `no_git_push`: `True`
- `no_key_leakage`: `True`
- `no_live_readiness_claim`: `True`
- `no_live_trading`: `True`
- `no_modification_of_any_runner_harness_for_any_candidate`: `True`
- `no_modification_of_any_sealed_predecessor`: `True`
- `no_modification_of_any_test_file`: `True`
- `no_modification_of_app_py`: `True`
- `no_modification_of_b006_artifacts`: `True`
- `no_modification_of_clarification_memo_on_disk`: `True`
- `no_modification_of_claude_md_or_runbook_or_gitignore`: `True`
- `no_modification_of_command_route`: `True`
- `no_modification_of_command_template`: `True`
- `no_modification_of_command_test`: `True`
- `no_modification_of_execution_guard_source`: `True`
- `no_modification_of_idea_memory`: `True`
- `no_modification_of_in_sample_driver_source`: `True`
- `no_modification_of_lessons_md`: `True`
- `no_modification_of_obsidian_trade_logger`: `True`
- `no_modification_of_orb_step_30_constants`: `True`
- `no_modification_of_out_of_sample_driver_source`: `True`
- `no_modification_of_p10_5_sweep_report_on_disk`: `True`
- `no_modification_of_p1_plan_lock_on_disk`: `True`
- `no_modification_of_p1_rev_m_reanchor_memo_on_disk`: `True`
- `no_modification_of_p2_phase_2_plan_on_disk`: `True`
- `no_modification_of_p3_implementation_plan_memo_on_disk`: `True`
- `no_modification_of_rev2_spec_on_disk`: `True`
- `no_modification_of_review_queue`: `True`
- `no_modification_of_runner_main_source`: `True`
- `no_modification_of_s10_d1_artifacts`: `True`
- `no_modification_of_s10_d2_artifacts`: `True`
- `no_modification_of_s10_d2_p11_park_memo_on_disk`: `True`
- `no_modification_of_s11_d1_artifacts`: `True`
- `no_modification_of_s7_or_s8_or_s9_or_b005_or_nke_or_d5_artifacts`: `True`
- `no_modification_of_strategy_lab_artifacts`: `True`
- `no_modification_of_v1_spec_on_disk`: `True`
- `no_oos_computation`: `True`
- `no_oos_confirmation_claim_beyond_exact_sealed_wording`: `True`
- `no_oos_inspection_beyond_sealed_text_already_on_disk`: `True`
- `no_paper_order_placed`: `True`
- `no_paper_trading`: `True`
- `no_profitability_claim`: `True`
- `no_real_order_placed`: `True`
- `no_signal_computation`: `True`
- `no_simulator_run`: `True`
- `no_strategy_lab_invoked`: `True`
- `no_strategy_test_run`: `True`

## Operator next-step options (documented only; not self-authorized)

- **`AUTHORIZE_PURSUE_FRESH_HIGHER_DENSITY_CANDIDATE`**: Type a fresh authorization phrase to start a new candidate selection memo. Recommended primary direction. Operator chooses among the documented candidate id options in the decision matrix (T2-T9 from 556ab3f, F3 RSI-2 on non-ETF universe, F2 vol-targeting weekly, intraday-bar Donchian, multi-symbol low-correlation basket).
- **`AUTHORIZE_START_S11_D1_P3_BUILD_anchored_to_rev2`**: Type 'Authorize S11-D1 P3 BUILD anchored to rev2' to begin the multi-hour S11-D1 implementation despite the expected INSUFFICIENT_SAMPLE terminal verdict. Justified if methodology-template breadth is the operator's dominant priority. The P3 implementation-plan memo at 1ad8d83 governs the build scope.
- **`AUTHORIZE_CONTINUE_S10_D2_specific_diagnostic`**: Type a specific S10-D2 continuation authorization (e.g., 'Authorize S10-D2 per-market PnL stratification' or 'Authorize S10-D2 regime-stratified OOS evaluation'). Low marginal information value; candidate stays parked.
- **`HALT_AND_WAIT`**: No further authorization this session. Defer all S10-D2 / S11-D1 / fresh-candidate decisions. Preserves all sealed artifacts as historical record.
- **`DEFER_DECISION`**: Same as HALT_AND_WAIT but explicitly revisit at a later session.

