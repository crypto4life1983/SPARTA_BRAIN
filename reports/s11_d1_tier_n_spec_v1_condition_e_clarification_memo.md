# S11-D1 Tier-N v1 condition (e) clarification memo (sealed; non-binding)

**Schema:** `sparta.external_research_hunter.s11_d1_tier_n_spec_v1_condition_e_clarification_memo.v1`  
**Report kind:** S11-D1 non-binding clarification memo (warns future readers about an inverted-sign literal in v1 Tier-N spec oos_confirmation_definition condition (e); does NOT supersede v1, does NOT modify P1, does NOT authorize any lifecycle phase)  
**Candidate record id:** `s11-d1-mnq-c0-single-instrument-databento-long-history`  
**Authored at (UTC):** `2026-05-27T04:39:34Z`  
**Memo is binding:** `False` (documentation only; does not modify v1 or P1)  
**Report seal sha256:** `eda08aceeb4afd7d4f985a739d6e87b3e803daff8da3f645f016b0a56a3af871`

## Finding 1 - v1 condition (e) is broken if read in isolation

- v1 path: `reports/s11_d1_mnq_c0_single_instrument_databento_long_history_tier_n_spec_sealed.json`
- v1 commit: `9c63088`
- v1 seal sha256: `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`
- Broken field path: `k9_and_oos_confirmation_rules.oos_confirmation_definition (condition (e) within the 8-condition AND chain)`

**Literal text as sealed:** *"OOS is CONFIRMED only iff ALL of: (a) C7 verdict is READY_FOR_LONGER_BACKTEST, (b) OOS closed_trades >= 100, (c) OOS sharpe > 0, (d) OOS expectancy > 0, (e) OOS trade_curve_maxdd_pct <= -30%, (f) all safety counters zero, (g) no-pyramid invariant held, (h) starting_cash invariant held."*

**Why condition (e) is inverted:** With maxdd_pct expressed as a negative number (per S10-D2 convention: -12.96, -28.31, etc.), '<= -30' evaluates True only for drawdowns deeper than -30% (bad outcomes). Small / shallow drawdowns (e.g., -12.96%) fail the condition. The intended meaning of an acceptance gate is the inverse: drawdown not worse than -30% (i.e., maxdd_pct >= -30% or equivalently |maxdd_pct| <= 30%).

**Demonstration:**

| Case | v1 literal evaluates | Intuitive expected | v1 literal says |
|------|----------------------|--------------------|-----------------|
| `maxdd_pct = -12.96` (small) | `(-12.96 <= -30) is False` | PASS (small drawdown is good) | FAIL (would reject good outcomes) |
| `maxdd_pct = -35.00` (large) | `(-35.00 <= -30) is True` | FAIL (drawdown worse than threshold) | PASS (would accept bad outcomes) |

**Intended form (any one is equivalent):**

- `maxdd_pct >= -30%`
- `|maxdd_pct| <= 30%`
- `abs(maxdd_pct) <= 30%`

This memo does NOT modify v1. v1 stays byte-stable at sha `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`.

## Finding 2 - P1 plan-lock is the operationally binding evaluation grid

- P1 commit: `7d86486` (*Seal S11-D1 P1 plan-lock*)
- P1 path: `reports/s11_d1_mnq_c0_single_instrument_databento_long_history_p1_plan_lock_sealed.json`
- P1 anchors v1 by sha: `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`
- P1 introduces its own gate-evaluation grid: `True`
- P1 grid is the grid that will actually run at P6 IS / P6.5 / P10: `True`
- P1 next_phase_pre_approved: `False`

**Why v1 condition (e) is operationally dormant:** P1's rejection_rules_locked block defines the gates that the future IS driver / OOS driver / cost-stress sweep / OOS gate will evaluate. v1's oos_confirmation_definition literal text is not consumed by any planned execution path; it remains as documentation prose only. This memo flags it as a documentation hazard only, not as an active runtime defect.

**P1 lock action verbatim:** *"All Tier-N spec decisions are inherited byte-equivalent into the BUILD phase. No Tier-N spec modification is permitted; any change requires a fresh _revN_ Tier-N spec under a separate authorization."*

## Finding 3 - P1 A4 (max DD at IS) is correctly magnitude-based

- Field: `rejection_rules_locked.a_gates_evaluated_at_p6_is.A4_trade_curve_maxdd_pct_le_30`
- P1 literal: *"fail -> FAIL_SAFETY (S10-D2 used 50; S11-D1 tightens to 30 per Tier-N spec rejection-rules section, single-instrument higher concentration risk)"*
- Naming convention: 'le_30' = magnitude not exceeding 30. Pass iff |maxdd_pct| <= 30%. Fail iff |maxdd_pct| > 30% -> FAIL_SAFETY.
- Vs S10-D2: S10-D2 K4 threshold was 50% magnitude. S11-D1 A4 tightens to 30% magnitude for single-instrument concentration risk. This is correct discipline: tightening, not loosening.
- Phase evaluated at: `P6 IS diagnostic`
- Direction correct at P1: `True`

## Finding 4 - P1 K4 (max DD safety trigger) is correctly magnitude-based

- Field: `rejection_rules_locked.k_gates_evaluated.K4_trade_curve_maxdd_gt_50`
- P1 literal: *"FAIL_SAFETY trigger (|maxdd_pct| > 50%)"*
- Naming convention: 'gt_50' = magnitude greater than 50. P1 uses explicit |maxdd_pct| notation, eliminating sign ambiguity.
- Phase evaluated at: `P6 IS diagnostic + P10 OOS gate`
- Direction correct at P1: `True`
- Byte-inherited from S10-D2 K4: `True`

## Finding 5 - This memo is NON-BINDING

- `memo_does_NOT_supersede_v1_tier_n_spec`: `True`
- `memo_does_NOT_supersede_p1_plan_lock`: `True`
- `memo_does_NOT_modify_any_sealed_artifact_on_disk`: `True`
- `memo_does_NOT_introduce_a_new_evaluation_gate`: `True`
- `memo_does_NOT_alter_any_threshold`: `True`
- `memo_does_NOT_re_anchor_p1_to_a_different_seal`: `True`
- `memo_does_NOT_modify_in_sample_driver_or_out_of_sample_driver_source`: `True`
- `memo_does_NOT_modify_runner_main_source`: `True`
- `memo_does_NOT_count_as_revN_revision_under_p1_clause`: `True`
- `memo_does_NOT_fulfill_the_p1_clause_requiring_revN_for_any_tier_n_change`: True. The P1 clause says 'any change [to Tier-N spec] requires a fresh _revN_ Tier-N spec under a separate authorization.' This memo makes NO change to v1; v1 stays byte-stable. If a future operator decides a binding correction is needed, they must author an actual _revN_ Tier-N spec AND re-anchor P1 under separate fresh authorizations. This memo does neither.
- `purpose`: Documentation hazard mitigation only. Future readers of v1 in isolation will see condition (e) and may interpret it literally; this memo records that the intended interpretation is the inverse, and that the P1 plan-lock at commit 7d86486 is the operationally binding evaluation grid.

## Finding 6 - No lifecycle phase is authorized by this memo

- `p2_phase2_plan`: `requires fresh operator authorization`
- `p3_build`: `requires fresh operator authorization`
- `p4_smoke`: `requires fresh operator authorization`
- `p6_is_diagnostic`: `requires fresh operator authorization`
- `p6_5_cost_stress`: `requires fresh operator authorization`
- `p7_decision_memo`: `requires fresh operator authorization`
- `p10_oos_gate`: `requires fresh operator authorization`
- `p11_lifecycle_decision`: `requires fresh operator authorization`
- `memo_does_not_advance_any_phase_or_pre_approve_any_phase`: `True`

## Hard boundaries (all held this memo turn)

- `no_backtest`: `True`
- `no_branch_change`: `True`
- `no_brokerage_connection`: `True`
- `no_candidate_promoted`: `True`
- `no_data_fetch`: `True`
- `no_databento_api_call`: `True`
- `no_databento_api_key_access`: `True`
- `no_external_network_call`: `True`
- `no_frc_grant`: `True`
- `no_git_push`: `True`
- `no_key_leakage`: `True`
- `no_live_readiness_claim`: `True`
- `no_live_trading`: `True`
- `no_modification_of_any_b006_artifact`: `True`
- `no_modification_of_any_s10_d1_artifact`: `True`
- `no_modification_of_any_s10_d2_artifact`: `True`
- `no_modification_of_any_s7_or_s8_or_s9_artifact`: `True`
- `no_modification_of_any_sealed_predecessor`: `True`
- `no_modification_of_cache_data_databento_or_databento_oos_or_databento_is_only`: `True`
- `no_modification_of_claude_md_or_runbook_or_gitignore`: `True`
- `no_modification_of_command_center_app_py_template_test`: `True`
- `no_modification_of_idea_memory`: `True`
- `no_modification_of_in_sample_driver_source`: `True`
- `no_modification_of_lessons_md`: `True`
- `no_modification_of_obsidian_trade_logger`: `True`
- `no_modification_of_orb_step30_artifacts`: `True`
- `no_modification_of_out_of_sample_driver_source`: `True`
- `no_modification_of_p1_plan_lock`: `True`
- `no_modification_of_review_queue`: `True`
- `no_modification_of_runner_harness_source`: `True`
- `no_modification_of_strategy_lab_artifacts`: `True`
- `no_modification_of_v1_tier_n_spec`: `True`
- `no_oos_computation`: `True`
- `no_oos_inspection`: `True`
- `no_paper_order_placed`: `True`
- `no_paper_trading`: `True`
- `no_profitability_claim`: `True`
- `no_real_order_placed`: `True`
- `no_rev1_tier_n_spec_authored`: `True`
- `no_signal_computation`: `True`
- `no_simulator_run`: `True`
- `no_strategy_lab_invoked`: `True`

## Posture invariants (unchanged by this memo)

- Trading status: `PAUSED`
- Live status: `BLOCKED_AT_6_GATES`
- FRC granted: `False`
- Advisory label (permanent): `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- verdict_never_means_live_ready: `True`
- live_promotion_path_closed: `True`
- no_strategy_optimization_authorized: `True`
- no_profitability_claim: `True`
- no_oos_confirmation_claim: `True`

## Predecessor seal-chain attestation (drift = 0)

- `all_predecessor_seals_re_verifiable_from_on_disk_artifacts`: `True`
- `no_predecessor_seal_modified_by_this_memo`: `True`
- `p1_plan_lock_commit`: `7d86486`
- `s10_d2_p11_park_seal_sha256_for_reference`: `e121b82b411697c7d06bbe9ee1cc2df29c04df76712873ed0fbfd76f25fab1cb`
- `selection_plan_commit_for_reference`: `556ab3f`
- `v1_tier_n_spec_commit`: `9c63088`
- `v1_tier_n_spec_seal_sha256`: `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`

## Operator next-step options (documented only; not self-authorized)

- **`ACCEPT_AS_IS_AUTHORIZE_S11_D1_P2_PHASE_2_PLAN`**: Treat this memo as sufficient documentation hazard mitigation. The P1 plan-lock's gate grid is binding and correct; v1's dormant text is flagged here for future readers. Advance the lifecycle by authorizing P2 phase-2 plan under separate authorization.
- **`AUTHORIZE_BINDING_REVN_TIER_N_SPEC_AND_REVN_P1_PLAN_LOCK`**: If you decide the dormant-text hazard is unacceptable, author a binding _revN_ Tier-N spec correcting condition (e), AND author a _revN_ P1 plan-lock re-anchored to _revN_ Tier-N spec. Heavier correction; forks the v1+P1 chain. Requires two separate operator authorizations.
- **`HALT_S11_D1_LIFECYCLE_AND_RE_SPEC_UNDER_FRESH_CANDIDATE_ID`**: Most thorough: open a fresh candidate id (e.g., s11-d1b or s11-d2) with a clean Tier-N spec containing the correctly-signed oos_confirmation_definition. Discards the v1 + P1 work done so far.

