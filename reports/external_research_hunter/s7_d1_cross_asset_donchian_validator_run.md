# s7 D1 — Validator Run

**Schema:** `sparta.external_research_hunter.s7_d1_cross_asset_donchian_validator_run.v1`
**Run date (UTC):** `2026-05-25T14:58:02Z`
**Candidate:** `s7-cross-asset-donchian-no-filter-nq-gc-zn-cl`
**Predecessor seal:** `8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac`
**Verdict:** `VALIDATOR_PASS`  (21/21 pass, 0 fail)

| # | Name | Pass | Detail |
|---|---|---|---|
| `V1` | `spec_sha_matches_recorded` | ✅ | spec_md_sha256=c36588e77899f2511a429b967c0d2fab7bbf85828afae8af7cb4043f96764d4f |
| `V2` | `phase2_safety_template_inherited_byte_equivalent` | ✅ | md_match=True, json_match=True |
| `V3` | `s2_through_s6_sealed_chains_byte_stable` | ✅ | checked 13 parents, all match=True |
| `V4` | `no_d5_revival` | ✅ | matches=[] |
| `V5` | `no_b005_001_revival` | ✅ | b005_001 chain snapshot taken: ['b005_001_archival_memo_md_byte_sha', 'b005_001_archival_memo_json_byte_sha'] |
| `V6` | `no_nke_revival` | ✅ | NKE HUNTER_BRAIN_LESSONS.md snapshot recorded; mutation detection is between-turn |
| `V7` | `markets_enumerated_exactly_4_nq_gc_zn_cl` | ✅ | markets=['NQ', 'GC', 'ZN', 'CL'] |
| `V8` | `rth_only_filter_attested` | ✅ | rth_only=True |
| `V9` | `donchian_55_20_attested` | ✅ | 55/20 declared |
| `V10` | `pyramid_max_4_attested` | ✅ | max_units_per_market=4 |
| `V11` | `n_calculation_uses_entry_market_at_trigger_bar` | ✅ | n_definition recorded |
| `V12` | `portfolio_cap_uses_unit_count_not_contract_count` | ✅ | Inherits s6 portfolio_cap_bugfix_report (sha fa232ca1...) |
| `V13` | `cost_stress_matrix_S0_S1_S2_S3_S4_present` | ✅ | tiers=['S0', 'S1', 'S2', 'S3', 'S4'] |
| `V14` | `seal_roundtrip_recompute_match` | ✅ | recomputed=72602305ef8d678195f9ab91a6d4cb8e7a473ee1a641cf9e8f91b8d4e31134c3, embedded=72602305ef8d678195f9ab91a6d4cb8e7a473ee1a641cf9e8f91b8d4e31134c3 |
| `V15` | `no_oos_inspection_in_in_sample_run` | ✅ | No in-sample run executed this turn; OOS read not possible |
| `V16` | `boundaries_held_all_true` | ✅ | all_negative_invariants_True=True |
| `V17` | `spec_md_unchanged_during_seal_turn` | ✅ | start=c36588e77899f2511a429b967c0d2fab7bbf85828afae8af7cb4043f96764d4f == end=c36588e77899f2511a429b967c0d2fab7bbf85828afae8af7cb4043f96764d4f |
| `V18` | `no_d5_artifact_present_in_repo` | ✅ | matches=[] |
| `V19` | `no_b005_001_chain_mutated_during_turn` | ✅ | snapshot only; mutation detection would require between-turn baseline |
| `V20` | `no_nke_chain_mutated_during_turn` | ✅ | snapshot only; same caveat as V19 |
| `V21` | `no_obsidian_trade_logger_touched_during_turn` | ✅ | start_hash=3d8538c5e8a6e4cb..., end_hash=3d8538c5e8a6e4cb... |

