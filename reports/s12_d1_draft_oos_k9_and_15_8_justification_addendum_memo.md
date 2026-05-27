# S12-D1 DRAFT OOS K9 + 15/8 justification addendum sidecar memo (sealed; non-binding)

**Schema:** `sparta.external_research_hunter.s12_d1_draft_oos_k9_and_15_8_justification_addendum_memo.v1`  
**Authored at (UTC):** `2026-05-27T14:24:55Z`  
**Memo type:** sidecar addendum / observation only  
**Authorizes execution:** `False`  
**Report seal sha256:** `10c388491f2735bbd2b16d9589ef44e3c7ab5d4c3fa89d8632ae82e3e7766add`

## Section 1 - Parallel DRAFT accepted as canonical

- Canonical S12-D1 DRAFT commit: `7e9c867` (*Add s12 D1 MNQ.c.0 Donchian-15/8 fresh-candidate Tier-N spec DRAFT (mechanic family + Donchian 15/8 LOCKED at PLAN)*)
- Canonical S12-D1 DRAFT path: `docs/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_tier_n_spec_DRAFT.md`
- Canonical S12-D1 DRAFT bytes on disk at memo authorship time: `28116`
- Canonical S12-D1 DRAFT lines on disk at memo authorship time: `397`
- DRAFT convention (MD only; no JSON seal at DRAFT time): `True`
- Follows s11-d1 DRAFT naming convention at 74e254f: `True`
- S12-D1 PLAN predecessor commit: `b4eac65`
- This session defers canonical DRAFT authorship to parallel session: `True`
- This session does NOT compete at the canonical DRAFT path: `True`

## Section 2 - This memo is observation/addendum, NOT competing DRAFT

- `memo_type`: sidecar_addendum_observation
- `memo_does_NOT_supersede_canonical_draft`: `True`
- `memo_does_NOT_re_anchor_candidate`: `True`
- `memo_does_NOT_introduce_new_evaluation_gate`: `True`
- `memo_does_NOT_alter_any_threshold`: `True`
- `memo_does_NOT_modify_canonical_draft_text_on_disk`: `True`
- `memo_does_NOT_force_any_future_seal_change`: `True`
- `memo_does_NOT_count_as_revN_revision_of_canonical_draft`: `True`
- `memo_purpose`: Documentation hazard mitigation analogous to the s11-d1 v1 condition-e clarification memo (commit d13b56a). Future readers of the s12-d1 canonical DRAFT in isolation may not see the OOS K9 reachability arithmetic or the 15/8-vs-alternatives first-principles framing. This memo records both as advisory observations to inform the future SEAL turn. Per the s11-d1 v1 P1 plan-lock 'fresh _revN_' clause applied to the DRAFT-stage analog: any binding modification to the canonical DRAFT requires a fresh _revN_ DRAFT under separate operator authorization; this memo does neither.
- `future_seal_remains_free_to_use_or_disregard_this_observation`: `True`

## Section 3 - OOS K9 reachability gap (explicit)

- **Gap severity: `HIGH`**
- Where gap lives in canonical DRAFT: The canonical DRAFT (7e9c867) §10 'Sample-size / K9 rules' documents the IS-window expected trade count (80-200 over 4.6y) and pre-commits to INCONCLUSIVE_HOLD if IS K9 fires. The DRAFT does NOT, however, perform the structural arithmetic that scales the IS rate to the OOS window.
- IS estimate from canonical DRAFT verbatim: `80-200 portfolio trades over ~4.6 years IS window`
- Implied per-year trade rate range: `17.4 to 43.5 trades per year (= [80/4.6, 200/4.6])`
- OOS window length: `2.0` years (`2024-01-02` to `2025-12-30`)
- **Implied OOS trade count estimate range: `35 to 87 trades over the 2.0-year OOS window (= [17.4*2.0, 43.5*2.0])`**
- K9 threshold (locked from s11-d1 v1, byte-equivalent): **`100`**
- K9 threshold modification: `True` (forbidden)

**Reachability analysis:**

- IS K9 central case: **REACHABLE (central estimate ~140 IS trades exceeds K9=100 with margin)**
- IS K9 lower-bound: **BORDERLINE (lower estimate 80 < K9=100)**
- OOS K9 central case: **UNREACHABLE (central OOS estimate ~63 trades is below K9=100)**
- OOS K9 upper-bound: **BORDERLINE (upper OOS estimate 87 < K9=100; even the upper end fails to reach K9)**
- OOS K9 only reaches threshold if: Actual IS signal density exceeds 50 trades/year (i.e., > 230 IS trades over 4.6y), which is at or above the upper extreme of the DRAFT's expected band. Even at IS=230 (slightly above the upper estimate), OOS at the same rate would produce ~100 trades = exactly at K9 with zero margin.

**Conclusion:** IS K9 may clear (central case); OOS K9 is expected to fail across the entire DRAFT-documented expected band. S12-D1 is therefore structurally likely to follow the same trap as S10-D2 (which cleared IS K9 with 200 trades but fired OOS K9 at 53 trades) and as S11-D1 (which was expected to fail BOTH IS K9 and OOS K9 per its own k9_risk_disclosure). S12-D1's K9-mitigation hypothesis is specifically that Donchian-15/8 raises IS density above K9; it does NOT (and structurally cannot) raise OOS density above K9 on the 2.0-year OOS window.

- This observation is arithmetic, not a strategic claim: `True`
- This observation does not force any specific SEAL decision: `True`

## Section 4 - Why OOS K9 matters

**Implication:** If S12-D1 reaches OOS with IS K9 cleared but OOS K9 fired, the terminal verdict will be analogous to S10-D2's P11 PARK at 23c7164: PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED. The cost-stress robustness, K10 (N/A for single-instrument), safety counters, no-pyramid invariant, and starting-cash invariant could all hold cleanly, and the candidate could still PARK at OOS due to insufficient OOS sample.

**Implication for research value:** S12-D1 solves the IS K9 problem (the load-bearing structural improvement that motivated the fresh candidate) but does NOT solve the OOS K9 problem because the OOS window length (2.0y) is fixed by inheritance from s11-d1 v1 sealed spec and cannot be extended without fresh Databento fetch + a further-fresh candidate id.

**Implication for lifecycle expectation:** Operator should expect S12-D1 P10 OOS gate (if eventually authorized after SEAL+BUILD+P4+P6+P6.5+P7) to land at INSUFFICIENT_SAMPLE / OOS_INDETERMINATE_BUT_DIRECTIONALLY_CONSISTENT analogous to S10-D2's P10 result. The candidate's terminal verdict, if executed, is most likely PARKED. This is not a defect in S12-D1; it is the structural OOS-window constraint inherited from the s11-d1 lineage.

**Implication for strategy validation goal:** Strategy validation (per the comparison memo at 1bf45bc section 4) requires K9 >= 100 in the relevant evaluation phase. Single-instrument daily-bar Donchian candidates on the s11-d1 lineage's 2.0y OOS window are STRUCTURALLY UNABLE to clear OOS K9 unless the strategy produces > 50 trades/year, which is at the very edge of plausibility for even the fastest Donchian variants on a single equity-index futures contract.

**Implication for methodology template value:** S12-D1 template value remains real even if terminal verdict is PARKED. A shorter-Donchian single-instrument futures runner harness does not currently exist anywhere in the repo; building it produces a reusable scaffolding pattern for future candidates regardless of S12-D1's own verdict.

- This observation does NOT imply DO_NOT_PROCEED: `True`
- This observation IMPLIES operator should know before SEAL: `True`

## Section 5 - 15/8 first-principles framing

- **Gap severity: `MEDIUM`**
- Where gap lives in canonical DRAFT: Canonical DRAFT §1 'Mechanic family + Donchian parameters LOCKED at PLAN -- DRAFT does NOT reopen' explicitly defers justification to the PLAN (b4eac65). PLAN §8 names Donchian-15/8 as the load-bearing departure but does NOT cite literature, theory, or quantitative comparison of 15/8 vs alternative faster channel lengths.

### Candidate alternatives to 15/8 considered

| Variant | Expected trades over 4.6y IS | K9 status | Why considered/rejected |
|---------|------------------------------|-----------|-------------------------|
| `donchian_55_20_s11_d1_baseline` | 25-50 over 4.6y IS (per s11-d1 v1 k9_risk_disclosure) | FAILS K9 in central case (50 < 100) | the K9 failure motivated the fresh-candidate authoring in the first place |
| `donchian_20_10` | approximately 50-110 over 4.6y IS (linear interpolation; ~1.5x s11-d1 baseline) | BORDERLINE (50 < K9 < 110) | central estimate (80) is comfortably below K9; would not reliably break the K9 trap; not enough of a structural departure to justify a fresh candidate |
| `donchian_15_8_s12_d1_chosen` | 80-200 over 4.6y IS (per PLAN §12 and canonical DRAFT §10) | REACHABLE in central case (140 > 100); borderline at lower bound (80 < 100) | central estimate exceeds K9 with margin; honest borderline-at-lower-bound disclosure; lower whipsaw risk than 10/5; recognizable short-Donchian variant |
| `donchian_10_5` | approximately 200-500 over 4.6y IS (extrapolated; very high signal density) | CLEARS K9 with significant margin | very high whipsaw rate; cost-erosion likely fatal under any non-trivial cost-stress tier (S2/S3/S4); not a recognizable trend-following channel in the trend-following literature; would push candidate into 'noise scalping' rather than 'trend following' regime |
| `donchian_5_3_or_shorter` | — | TRIVIALLY CLEARS K9 | not a trend-following mechanic at all; signal density would be dominated by intra-day-noise-on-daily-bars; cost-stress would dominate completely; would violate the F1 'trend-no-pyramid' mechanic family definition in spirit |

### Defensibility framing for 15/8

- Faster than 20/10: addresses the K9 trap that 20/10 borderline could not reliably break.
- Less hyperactive than 10/5: avoids the whipsaw / cost-erosion regime where the candidate degrades to noise-scalping.
- Within a recognizable short Donchian trend-following family: 15-bar lookbacks are documented in trend-following research as a 'fast turtle' or 'short-channel breakout' variant (e.g., shorter than the original 20/55 Turtle ruleset, but longer than pure noise-scalping channels).
- Bi-directional symmetric: both long-entry-on-N-day-high and short-entry-on-N-day-low at the same N; preserves the F1 mechanic symmetry.
- Channel-length ratio 15:8 ~ 1.875: preserves the entry-longer-than-exit asymmetry that distinguishes Donchian breakout from pure channel-touch; not too close to 1:1 (which would be a momentum-reversal mechanic instead of a trend-following one).

### What this addendum does NOT do

- Does NOT empirically validate that 15/8 produces 80-200 trades on MNQ.c.0 (that requires P6 IS execution under separate authorization).
- Does NOT cite specific peer-reviewed or industry-standard literature for 15/8 as a canonical Donchian variant (literature is mostly silent on 15/8 specifically; 20-day is more common; 55-day is the original Turtle).
- Does NOT compute the expected per-trade win rate / pay-off / sharpe at 15/8 on MNQ.c.0 (that requires running the strategy).
- Does NOT recommend a SEAL-level decision; only documents the framing for the operator to consider.

### Operator at SEAL may decide to

- Accept the canonical DRAFT's 15/8 choice as-is (default A) and let P6 IS reveal whether the band [80, 200] holds.
- Add a literature citation or quantitative simulation reference to the SEAL-time spec rationale.
- Revise to 20/10 (would require fresh candidate id per the same forbidden-revision clause; not a simple SEAL revision).
- Document at SEAL that 15/8 is provisional and may be revisited at archival memo time based on P6 evidence.

## Section 6 - Whipsaw and cost-erosion risk

**Mechanism:** Donchian-15/8 produces more breakouts than Donchian-55/20 because the prior-15-day high/low is a lower hurdle than the prior-55-day high/low. Many of those extra breakouts will trigger on noise (e.g., one-day spikes that quickly reverse), leading to entries that hit the ATR stop within a few bars. Each round-trip pays commission + fees + tick-slippage on entry, stop, and exit, eroding edge per trade. The shorter the channel, the higher the fraction of stopped-out noise trades, and the more sensitive the candidate is to cost-tier escalation.

**Canonical DRAFT acknowledges via DR10 elevation:** Canonical DRAFT §8.2 explicitly elevates DR10 prior probability: 'DR10 turnover_cost_explosion ... ELEVATED prior probability vs s11-d1 v1 because Donchian-15/8 raises annual turnover materially; this is the load-bearing trade-off accepted at PLAN'. DR10 fires REJECT_FAST if annual_turnover > 0.50 OR S2 cost drag > 0.05. This is the framework's mechanism for catching whipsaw / cost-erosion if it manifests.

**Canonical DRAFT acknowledges via DA4 cash lever:** Canonical DRAFT §16 DRAFT_AMBIGUITY register includes DA4 as a mitigation lever: DA4=A keeps START_CASH at $50k (byte-equivalent to s11-d1 v1); DA4=B raises START_CASH to $100k to halve per-dollar commission/slippage pressure by reducing contracts-per-trade for a given ATR. This is an honest engagement with the whipsaw risk that operator can resolve at SEAL turn.

**Additional observation from this addendum:** Cost-stress matrix (S0/S1/S2/S3/S4) is the binding test of whether the extra trade count from shorter Donchian is real edge or noise. If S0 (no costs) produces strong positive edge but S2/S3 collapse to near-zero or negative net PnL, that is the whipsaw signature -- the strategy captures something at zero costs but the something is smaller than realistic trading frictions. DR2/DR3/DR5 + K12 then fire REJECT_FAST. If S0 positive AND S2/S3 also positive with monotonic-decreasing-but-still-positive PnL across tiers (like S10-D2's pattern), the cost-stress is robust and whipsaw is not fatal.

**Expected outcome pattern if 15/8 is whipsaw-dominated:** Likely DR10 fire (annual turnover > 0.50 OR S2 cost drag > 0.05) -> REJECT_FAST at P6.5 cost-stress sweep. Candidate parks REJECT_FAST under DR10 rather than INCONCLUSIVE_HOLD under K9.

**Expected outcome pattern if 15/8 is genuine signal:** All cost tiers positive; DR10 below threshold; K12 not fired; verdict ladder proceeds to P6 IS RFOR_LONGER_BACKTEST analogous to S10-D2 P6 IS verdict. K9 may then fire at OOS for the reasons in section 3.

## Section 7 - Recommendations for future SEAL turn

- Recommendations are advisory only / not self-authorizing: `True`
- Future SEAL remains free to accept or decline: `True`

### `REC1_close_oos_k9_disclosure_gap_at_seal` (priority: **HIGH**)

SEAL-time Tier-N spec should add an explicit oos_k9_risk_disclosure field analogous to s11-d1 v1's k9_risk_disclosure but specifically for the OOS window. Suggested verbatim text: 'OOS K9 EXPECTED TO FIRE. Implied OOS trade count over 2.0y at IS rate is approximately 35-87 trades, below K9 = 100. If OOS K9 fires, the OOS verdict will be OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE analogous to S10-D2 P11 PARK at 23c7164. The chain shall NOT relax K9 at OOS; the appropriate response is to seal the INSUFFICIENT_SAMPLE / INDETERMINATE verdict and park the candidate. Pursuing s12-d1 accepts the structural likelihood of an OOS PARK outcome.'

### `REC2_close_15_8_justification_gap_at_seal` (priority: **MEDIUM**)

SEAL-time Tier-N spec should add a channel_length_choice_rationale field documenting the 15/8-vs-alternatives comparison (e.g., this memo's section 5 framing or equivalent). Even an honest 'no published reference for 15/8 specifically; chosen as the shortest Donchian variant that preserves trend-following character while breaking the K9 trap' is preferable to silence. This is a documentation completeness improvement, not a binding constraint.

### `REC3_resolve_da4_at_seal_with_explicit_rationale` (priority: **MEDIUM**)

SEAL-time decision: DA4=A ($50k cash; byte-equivalent to s11-d1 v1 baseline) or DA4=B ($100k cash; halves per-dollar cost pressure under Donchian-15/8's higher turnover). Operator should make this an explicit choice with rationale at SEAL. Default DA4=A preserves apples-to-apples comparison with s11-d1 v1; DA4=B mitigates the elevated DR10 risk from whipsaw / cost-erosion. Neither is mechanically wrong; the operator's research goal determines the right choice.

### `REC4_no_changes_to_canonical_draft_text` (priority: **INFORMATIONAL**)

This addendum memo does NOT request that the canonical DRAFT text be edited. The DRAFT is byte-stable on disk and remains the source of truth for SEAL inheritance. SEAL author may either incorporate REC1/REC2/REC3 directly into the SEAL JSON or include a forward reference to this addendum (commit hash to be assigned after operator commit-approval).

## Section 8 - No execution authorized

- `this_memo_authorizes_seal`: `False`
- `this_memo_authorizes_step_02b`: `False`
- `this_memo_authorizes_step_02c`: `False`
- `this_memo_authorizes_p3_build`: `False`
- `this_memo_authorizes_p4_smoke`: `False`
- `this_memo_authorizes_p6_is_diagnostic`: `False`
- `this_memo_authorizes_p6_5_cost_stress`: `False`
- `this_memo_authorizes_p7_decision_memo`: `False`
- `this_memo_authorizes_p10_oos_gate`: `False`
- `this_memo_authorizes_p11_lifecycle_decision`: `False`
- `all_subsequent_phases_require_separate_explicit_operator_authorization`: `True`
- `lifecycle_state_unchanged_by_this_memo`: `True`
- `lifecycle_state_at_memo_authorship_time`: S12-D1 PLAN sealed (b4eac65) -> S12-D1 Tier-N spec DRAFT sealed (7e9c867 canonical) -> S12-D1 SEAL NOT AUTHORIZED -> all 11 subsequent phases NOT AUTHORIZED. This memo is a DRAFT-stage sidecar addendum; it does not advance the lifecycle by any phase.

## Section 9 - All artifacts byte-stable

- `s12_d1_canonical_draft`:
  - `commit`: `7e9c867`
  - `byte_stable`: `True`
  - `file_bytes`: `28116`
  - `modified_by_this_memo`: `False`
- `s12_d1_plan`:
  - `commit`: `b4eac65`
  - `byte_stable`: `True`
  - `modified_by_this_memo`: `False`
- `comparison_memo_s10_d2_vs_s11_d1`:
  - `commit`: `1bf45bc`
  - `seal_sha256`: `d14c886416383916b7bd17f6f698d49acf3f5ba1c4c2bec8e66a0fbcd5ce1815`
  - `byte_stable`: `True`
  - `modified_by_this_memo`: `False`
- `s11_d1_v1_tier_n_spec`:
  - `commit`: `9c63088`
  - `seal_sha256`: `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`
  - `byte_stable`: `True`
  - `modified_by_this_memo`: `False`
- `s11_d1_rev2_tier_n_spec`:
  - `commit`: `c110fd4`
  - `seal_sha256`: `46659b4a8a73cb72fbe0153efed80aaf97b40557f8dfed51a9ba3199c243ed8d`
  - `byte_stable`: `True`
  - `modified_by_this_memo`: `False`
- `s10_d2_p11_park_memo`:
  - `commit`: `23c7164`
  - `seal_sha256`: `e121b82b411697c7d06bbe9ee1cc2df29c04df76712873ed0fbfd76f25fab1cb`
  - `byte_stable`: `True`
  - `modified_by_this_memo`: `False`
- `all_other_s10_d2_s11_d1_b006_s10_d1_s9_s7_s8_b005_nke_d5_artifacts_byte_stable`: `True`
- `no_sealed_predecessor_modified_by_this_memo`: `True`
- `no_driver_test_cache_data_strategy_logic_lessons_md_command_center_modified_by_this_memo`: `True`

## Hard boundaries (all held this memo turn)

- `no_authorization_of_s10_d2_continuation`: `True`
- `no_authorization_of_s11_d1_p3_build`: `True`
- `no_authorization_of_s12_d1_build_or_any_later_phase`: `True`
- `no_authorization_of_s12_d1_seal`: `True`
- `no_backtest`: `True`
- `no_branch_change`: `True`
- `no_broker_call`: `True`
- `no_brokerage_connection`: `True`
- `no_candidate_promoted`: `True`
- `no_competing_s12_d1_draft_authored`: `True`
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
- `no_modification_of_any_s7_s8_s9_b005_nke_d5_artifact`: `True`
- `no_modification_of_cache_directories`: `True`
- `no_modification_of_canonical_s12_d1_draft`: `True`
- `no_modification_of_claude_md_or_runbook_or_gitignore`: `True`
- `no_modification_of_command_center_app_py_template_test_route`: `True`
- `no_modification_of_comparison_memo`: `True`
- `no_modification_of_csv_anchors`: `True`
- `no_modification_of_data_databento_cache_or_oos_or_is_only`: `True`
- `no_modification_of_drivers`: `True`
- `no_modification_of_execution_guard`: `True`
- `no_modification_of_in_sample_driver`: `True`
- `no_modification_of_lessons_md`: `True`
- `no_modification_of_obsidian`: `True`
- `no_modification_of_orb_step_30_constants`: `True`
- `no_modification_of_out_of_sample_driver`: `True`
- `no_modification_of_review_queue_or_idea_memory`: `True`
- `no_modification_of_runner_harness`: `True`
- `no_modification_of_s11_d1_clarification_memo`: `True`
- `no_modification_of_s11_d1_p1_plan_lock`: `True`
- `no_modification_of_s11_d1_p1_rev_m_reanchor_memo`: `True`
- `no_modification_of_s11_d1_p2_phase_2_plan`: `True`
- `no_modification_of_s11_d1_p3_implementation_plan_memo`: `True`
- `no_modification_of_s11_d1_rev2_spec`: `True`
- `no_modification_of_s11_d1_v1_spec`: `True`
- `no_modification_of_s12_d1_plan`: `True`
- `no_modification_of_strategy_lab_artifacts`: `True`
- `no_modification_of_synthetic_fixtures`: `True`
- `no_modification_of_test_files`: `True`
- `no_oos_computation`: `True`
- `no_oos_confirmation_claim`: `True`
- `no_oos_inspection_beyond_constants_in_sealed_text`: `True`
- `no_paper_order_placed`: `True`
- `no_paper_trading`: `True`
- `no_parameter_change`: `True`
- `no_profitability_claim`: `True`
- `no_real_order_placed`: `True`
- `no_signal_computation`: `True`
- `no_simulator_run`: `True`
- `no_strategy_lab_invoked`: `True`
- `no_strategy_logic_modification`: `True`
- `no_threshold_loosening`: `True`

## Posture invariants (unchanged by this memo)

- `trading_status`: `PAUSED`
- `live_status`: `BLOCKED_AT_6_GATES`
- `frc_granted`: `False`
- `advisory_label_permanent`: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- `verdict_never_means_live_ready`: `True`
- `live_promotion_path_closed`: `True`
- `no_strategy_optimization_authorized`: `True`
- `no_profitability_claim`: `True`
- `no_oos_confirmation_claim`: `True`

## Predecessor seal-chain attestation (drift = 0)

- `all_predecessor_seals_re_verifiable_from_on_disk_artifacts`: `True`
- `comparison_memo_commit`: `1bf45bc`
- `comparison_memo_seal_sha256`: `d14c886416383916b7bd17f6f698d49acf3f5ba1c4c2bec8e66a0fbcd5ce1815`
- `no_predecessor_seal_modified_by_this_memo`: `True`
- `s10_d2_p11_park_commit`: `23c7164`
- `s10_d2_p11_park_seal_sha256`: `e121b82b411697c7d06bbe9ee1cc2df29c04df76712873ed0fbfd76f25fab1cb`
- `s11_d1_rev2_spec_commit`: `c110fd4`
- `s11_d1_rev2_spec_seal_sha256`: `46659b4a8a73cb72fbe0153efed80aaf97b40557f8dfed51a9ba3199c243ed8d`
- `s11_d1_v1_spec_commit`: `9c63088`
- `s11_d1_v1_spec_seal_sha256`: `077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24`
- `s12_d1_canonical_draft_commit`: `7e9c867`
- `s12_d1_plan_commit`: `b4eac65`

## Operator next-step options (documented only; not self-authorized)

- **`AUTHORIZE_S12_D1_TIER_N_SPEC_SEAL`**: Type 'Authorize s12 D1 MNQ.c.0 Tier-N spec SEAL.' to advance past DRAFT into SEAL. SEAL author should ideally incorporate REC1/REC2/REC3 from this memo; they're advisory.
- **`AUTHORIZE_S12_D1_TIER_N_SPEC_SEAL_with_specific_DA4_choice`**: Type 'Authorize s12 D1 MNQ.c.0 Tier-N spec SEAL with DA4=A' (or DA4=B) to make the cash-size decision explicit at SEAL authorization time.
- **`DEFER_S12_D1_SEAL_AND_PURSUE_OTHER_TRACK`**: Type a halt phrase. Comparison memo's option set (T2-T9, F3 RSI-2, F2 vol-targeting weekly, intraday-bar Donchian, multi-symbol low-correlation basket) remains available as alternative research directions.
- **`HALT_AND_WAIT`**: No further authorization. Preserves all sealed artifacts. Parallel session may continue S12-D1 work or open other candidates.

