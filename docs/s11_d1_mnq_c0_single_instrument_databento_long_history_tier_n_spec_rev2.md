# S11-D1 Tier-N specification - rev2 (sealed; binding)

**Schema:** `sparta.external_research_hunter.s11_d1_mnq_c0_single_instrument_databento_long_history_tier_n_spec_rev2_sealed.v1`  
**Report kind:** S11-D1 Tier-N specification rev2 (sealed; binding; corrects v1 oos_confirmation_definition condition (e) sign/inequality typo; supersedes v1 ONLY for future S11-D1 lifecycle anchoring under separate authorization; does NOT retroactively re-anchor P1 or P2; does NOT authorize P3 or any later phase)  
**Candidate record id:** `s11-d1-mnq-c0-single-instrument-databento-long-history`  
**Algo version (UNCHANGED from v1):** `s11_d1_v0_1_0`  
**Authored at (UTC):** `2026-05-27T04:59:43Z`  
**Revision label:** `rev2`  
**Binding:** `True`  
**Report seal sha256:** `46659b4a8a73cb72fbe0153efed80aaf97b40557f8dfed51a9ba3199c243ed8d`

## Binding scope

Rev2 IS a binding Tier-N spec under the P1 clause 'any change [to Tier-N spec] requires a fresh _revN_ Tier-N spec under a separate authorization.' Rev2 is available for future P1_rev_M re-anchoring under separate operator authorization. Rev2 does NOT itself re-anchor P1 or P2; those remain anchored to v1 (sha 077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24, commit 9c63088). Authoring rev2 does NOT authorize P3 or any later phase; P3 still requires its own separate authorization which would also decide whether P3 anchors v1 or rev2.

## Predecessor seal-chain attestation (drift = 0)

- Predecessor v1 spec commit: `9c63088`
- Predecessor v1 spec seal sha256: `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`
- Predecessor v1 spec bytes on disk at rev2 authorship time: `29600`
- Non-binding clarification memo predecessor commit: `d13b56a`
- Non-binding clarification memo predecessor seal sha256: `eda08aceeb4afd7d4f985a739d6e87b3e803daff8da3f645f016b0a56a3af871`

Downstream artifacts anchored to v1 at rev2 authorship time (NOT re-anchored by rev2):

- `P1_plan_lock` at commit `7d86486` anchors v1 sha `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`
- `P2_phase_2_plan` at commit `f64f984` anchors v1 sha `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`

## Semantic diff from v1 (the ONLY substantive change)

- Exactly one substantive change: `True`
- Change location: `k9_and_oos_confirmation_rules.oos_confirmation_definition`
- Change nature: sign/inequality correction on condition (e); no threshold change; no new gate; no removed gate

**v1 condition (e) substring (broken if read in isolation):**

> `(e) OOS trade_curve_maxdd_pct <= -30%`

**rev2 condition (e) substring (corrected, magnitude-based):**

> `(e) OOS trade_curve_maxdd_pct >= -30% (equivalently |trade_curve_maxdd_pct| <= 30%; i.e., the realized OOS drawdown shall not exceed 30% in magnitude)`

**Full v1 oos_confirmation_definition (verbatim, for reference):**

> *"OOS is CONFIRMED only iff ALL of: (a) C7 verdict is READY_FOR_LONGER_BACKTEST, (b) OOS closed_trades >= 100, (c) OOS sharpe > 0, (d) OOS expectancy > 0, (e) OOS trade_curve_maxdd_pct <= -30%, (f) all safety counters zero, (g) no-pyramid invariant held, (h) starting_cash invariant held."*

**Full rev2 oos_confirmation_definition (binding):**

> *"OOS is CONFIRMED only iff ALL of: (a) C7 verdict is READY_FOR_LONGER_BACKTEST, (b) OOS closed_trades >= 100, (c) OOS sharpe > 0, (d) OOS expectancy > 0, (e) OOS trade_curve_maxdd_pct >= -30% (equivalently |trade_curve_maxdd_pct| <= 30%; i.e., the realized OOS drawdown shall not exceed 30% in magnitude), (f) all safety counters zero, (g) no-pyramid invariant held, (h) starting_cash invariant held."*

**Why v1 was broken:**

With maxdd_pct expressed as a negative number, '<= -30' evaluates True only for drawdowns DEEPER than -30% (bad outcomes). Small / shallow drawdowns (e.g., -12.96%) failed the v1 condition. The intended meaning of an acceptance gate is the inverse: drawdown not worse than -30%. Rev2's corrected form '>= -30%' (equivalently '|maxdd_pct| <= 30%') aligns with the gate's intent and with the magnitude-based convention used elsewhere in the same spec (K4 uses |maxdd_pct| > 50% notation; P1 A4 uses 'le_30' naming = magnitude <= 30%).

- No other substantive change in rev2: `True`

## Canonical byte-diff (top-level JSON keys that differ from v1)

- Diff key count: `5`
- Diff keys:
  - `authored_at_utc`
  - `k9_and_oos_confirmation_rules`
  - `report_kind`
  - `revision_metadata`
  - `schema_id`

Note: k9_and_oos_confirmation_rules differs at the nested key oos_confirmation_definition only (single string field). All other top-level keys are byte-equivalent to v1 (canonical JSON comparison).

## Header fields updated by rev2

- `authored_at_utc`
- `report_kind`
- `schema_id`

## Header fields intentionally preserved from v1

- `algo_version_for_run_id`
- `candidate_purpose`
- `candidate_record_id`
- `phase_prefix`

## Additive metadata fields introduced by rev2

- `canonical_top_level_keys_that_differ_from_v1`
- `revision_metadata`

## All other v1 content preserved BYTE-EQUIVALENT

All top-level fields NOT listed in the diff above are present in
rev2's JSON body verbatim from v1 (deep-copied at authoring time;
canonical-JSON comparison embedded in rev2's body under
`canonical_top_level_keys_that_differ_from_v1`).

Specifically preserved unchanged (canonical comparison):

- `parent_references` (S10-D1 + S10-D2 sealed chain pins)
- `data_requirements` (MNQ.c.0 CSV sha pin, IS/OOS windows, schema)
- `is_oos_split_plan` (windows, no-walk-forward, etc.)
- `minimum_trade_count_requirements` (K9 threshold = 100, inviolate)
- `entry_exit_logic_boundary_locked_at_seal` (Donchian 55/20, ATR(20), 2N stop, 1% risk)
- `cost_assumptions_locked_at_seal` (commission, fees, slippage, cost-stress tiers)
- `rejection_rules` (K-gates + DR rules)
- `promotion_rules` (live block, FRC never, etc.)
- `intentional_differences_from_s10_d2`
- `s10_d2_lessons_inherited_explicitly`
- `files_allowed_to_be_created_or_modified` (per-phase allowed-files dict)
- `files_explicitly_forbidden_from_modification_this_turn_and_all_future_s11_d1_turns` (23-item forbidden list)
- `hard_boundaries_held_this_turn` (preserved from v1)
- `labels`, `status_fields`
- All `p*_requires_separate_authorization` flags
- `no_phase_pre_approved_by_this_seal`, `exact_next_phase_authorized_by_this_seal`

The only nested change is the single string field
`k9_and_oos_confirmation_rules.oos_confirmation_definition` (condition (e) sign correction).

## Posture invariants (attested unchanged by rev2)

- Trading status: `PAUSED`
- Live status: `BLOCKED_AT_6_GATES`
- FRC granted: `False`
- Advisory label (permanent): `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- verdict_never_means_live_ready: `True`
- live_promotion_path_closed: `True`
- no_strategy_optimization_authorized: `True`
- no_profitability_claim: `True`
- no_oos_confirmation_claim: `True`

## Hard boundaries held this rev2-authoring turn

- `no_backtest`: `True`
- `no_branch_change`: `True`
- `no_broker_call`: `True`
- `no_brokerage_connection`: `True`
- `no_cache_mutation`: `True`
- `no_candidate_promoted`: `True`
- `no_clarification_memo_modification`: `True`
- `no_data_fetch`: `True`
- `no_databento_api_call`: `True`
- `no_databento_api_key_access`: `True`
- `no_external_network_call`: `True`
- `no_frc_grant`: `True`
- `no_git_push`: `True`
- `no_key_leakage`: `True`
- `no_live_readiness_claim`: `True`
- `no_live_trading`: `True`
- `no_modification_of_any_sealed_predecessor`: `True`
- `no_modification_of_app_py`: `True`
- `no_modification_of_brain_memory_projects_trading_bot_lessons_md`: `True`
- `no_modification_of_claude_md_or_runbook_or_gitignore`: `True`
- `no_modification_of_command_center_template_or_test_or_route`: `True`
- `no_modification_of_data_databento_cache_or_oos_or_is_only`: `True`
- `no_modification_of_idea_memory`: `True`
- `no_modification_of_obsidian_trade_logger`: `True`
- `no_modification_of_orb_step_30_constants`: `True`
- `no_modification_of_reports_external_research_hunter`: `True`
- `no_modification_of_review_queue`: `True`
- `no_modification_of_strategy_lab_artifacts`: `True`
- `no_modification_of_tests_directory`: `True`
- `no_oos_computation`: `True`
- `no_oos_inspection`: `True`
- `no_optimization`: `True`
- `no_p10_authorization`: `True`
- `no_p11_authorization`: `True`
- `no_p1_plan_lock_modification`: `True`
- `no_p2_phase_2_plan_modification`: `True`
- `no_p3_authorization`: `True`
- `no_p4_authorization`: `True`
- `no_p6_5_authorization`: `True`
- `no_p6_authorization`: `True`
- `no_p7_authorization`: `True`
- `no_paper_order_placed`: `True`
- `no_paper_trading`: `True`
- `no_profitability_claim`: `True`
- `no_real_order_placed`: `True`
- `no_signal_computation`: `True`
- `no_simulator_run`: `True`
- `no_strategy_lab_invoked`: `True`
- `no_v1_spec_modification_on_disk`: `True`

## P3 remains NOT authorized

- `p3_remains_not_authorized`: `True`
- `p3_anchor_choice_v1_vs_rev2_requires_separate_authorization`: `True`
- `does_not_authorize_p3`: `True`
- `does_not_authorize_any_later_phase`: `True`
- `no_lifecycle_state_change_caused_by_rev2_authorship`: `True`

Authoring rev2 does NOT advance the S11-D1 lifecycle. The current
lifecycle state remains: v1 sealed -> P1 sealed (anchored to v1) ->
P2 sealed (anchored to v1) -> P3 NOT authorized. Rev2 is available
for future P1_rev_M re-anchoring under separate operator authorization.

## Files NOT modified by this rev2 authorship

- v1 spec JSON: `reports/s11_d1_mnq_c0_single_instrument_databento_long_history_tier_n_spec_sealed.json` (byte-stable at sha `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`)
- v1 spec MD: `docs/s11_d1_mnq_c0_single_instrument_databento_long_history_tier_n_spec.md` (unchanged)
- P1 plan-lock at commit `7d86486` (unchanged)
- P2 phase-2 plan at commit `f64f984` (unchanged)
- Clarification memo at commit `d13b56a` (unchanged)
- All other sealed predecessors (S10-D2, S10-D1, B006, S7/S8/S9 chains)
- All `reports/external_research_hunter/` content
- All `data/databento_cache*` content
- `brain_memory/projects/trading_bot/lessons.md`
- `app.py`, `templates/command.html`, `tests/test_app_command_route.py`
- `CLAUDE.md`, `RUNBOOK`, `.gitignore`

