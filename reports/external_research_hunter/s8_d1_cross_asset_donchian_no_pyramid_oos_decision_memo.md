# s8-D1 No-Pyramid - P10 OOS Decision Memo (SEALED, PLAN-ONLY)

**Phase:** `P10_OOS_DECISION_MEMO_SEALED`
**Operational status:** `OOS_DECISION_MEMO_SEALED_AWAITING_P11_LIFECYCLE_DECISION`
**Report date UTC:** 2026-05-26T03:18:13Z

**P10 decision memo seal:** `a493931f0b812fad837b9e7679710d03e445ea39d3b53cc8a3ec4ecd7309f9b3`
**Predecessor (P9.5b sizing-skip) seal:** `957ede055785faf041ccdbd13e268793076926e6547e8dad43c4edc1b38020d8`

> Labels: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, NO_FRC_GRANTED, S8_D1_P10_OOS_DECISION_MEMO_SEALED,
> OOS_SIGNAL_INTACT_BUT_CAPITAL_UNDERSIZED_FOR_2023_2025, NO_S7_D1_REVIVAL
> Trading: PAUSED | Live: BLOCKED_AT_6_GATES | FRC: not granted
> No profitability claim. No live promotion.

---

## EVIDENCE SUMMARY

### In-sample evidence (2013-2022; S1 cost tier; all preregistered gates PASS)
- C7 verdict: **READY_FOR_LONGER_BACKTEST**
- K-fires: []
- closed_trades: 111
- net_pnl_usd: $193,482.91
- sharpe_proxy_per_trade: 0.2250
- expectancy_per_trade_usd: $1,743.09
- trade_curve_maxdd_pct: -23.83%
- all 4 markets profitable: True
- no-pyramid invariant pass: True
- A8 cost-stress PASS: True; K12 fires: False
- K10 in-sample: avg_pairwise_correlation=0.065030, fires=False
- **All in-sample preregistered gates: PASS**

### Out-of-sample evidence (2023-2025; S1 cost tier)
- P9 OOS-S1 verdict: **INSUFFICIENT_SAMPLE**
- P9 OOS-S1 K-fires: ['K9']
- P9 OOS-S1 closed_trades: 15
- P9 OOS-S1 per-market trades: {'CL': 0, 'GC': 0, 'NQ': 0, 'ZN': 15}
- P9.5a OOS data integrity conclusion: **DATA_OK_TRIGGERS_EXIST_BUT_ENTRY_LOGIC_BLOCKED**
- P9.5a OOS trigger candidates per market: {'NQ': 164, 'GC': 111, 'ZN': 92, 'CL': 82}
- K10 OOS: avg_pairwise_correlation=0.051590, fires=False (PASS)
- P9.5b sizing-skip conclusion: **SIZING_SKIP_CONFIRMED**
- P9.5b per-market would_skip_pct: {'NQ': 100.0, 'GC': 100.0, 'ZN': 1.087, 'CL': 100.0}

### Consistency check

- P9.5b predicted: NQ 0 open, GC 0 open, CL 0 open, ZN 91 open (max). P9 observed: NQ 0, GC 0, CL 0, ZN 15 (less than 91 due to portfolio-cap + open-position blocks). Predictions match direction; deltas explained by expected mechanics.

---

## KEY INTERPRETIVE FINDINGS

### finding_1_signal_intact_at_OOS

**Statement:** The cross-asset Donchian-55 / Donchian-20 signal continues to produce trigger candidates at OOS scale comparable to expectation from per-market scaling.

**Evidence:** P9.5a: NQ=164, GC=111, ZN=92, CL=82 raw trigger candidates over OOS 2023-2025; per-market scaling of IS counts would yield approximately NQ:5-6, GC:8-9, ZN:14-15, CL:5-6 IF triggers fired proportionally to trade-count, but in fact OOS Donchian triggers are MORE abundant in raw count (164 NQ triggers is ~5-9x the per-market IS trigger rate). This indicates the entry CONDITION is firing more often, not less.

**Implication:** Strategy SIGNAL has not collapsed at OOS. The breakout condition is being met regularly.

### finding_2_diversification_intact_at_OOS

**Statement:** The cross-asset diversification hypothesis (K10) that motivated the D1 selection in the S8 plan continues to hold at OOS.

**Evidence:** K10 OOS: avg_pairwise_correlation = 0.051590 (vs IS 0.065030). Delta of -0.013 indicates the 4-market correlation regime is essentially unchanged. K10 OOS PASS at < 0.50 threshold.

**Implication:** Diversification basis for the candidate is preserved out-of-sample.

### finding_3_data_intact_at_OOS

**Statement:** The operator-supplied OOS Databento cache decoded cleanly into reasonable daily bars for all 4 markets.

**Evidence:** P9.5a: NQ=760, GC=680, ZN=773, CL=773 daily bars over OOS window (expected ~750 ± normal cal variations); first bar near 2023-01-03; last bar 2025-12-30 for all 4 markets; close/volume/log-return distributions are reasonable.

**Implication:** OOS zero-trade for NQ/GC/CL is NOT a data issue.

### finding_4_OOS_zero_trade_root_cause_capital_undersized

**Statement:** The OOS zero-trade outcome for NQ/GC/CL is caused by capital-vs-N-vs-contract-size mismatch: at every single Donchian trigger, floor($1,000 / (N * $/pt)) returned 0.

**Evidence:** P9.5b: NQ 164/164 (100%) would_skip; GC 111/111 (100%) would_skip; CL 82/82 (100%) would_skip. ZN 91/92 (98.9%) would_open. Median N: NQ 238.04, GC 24.07, CL 1.65, ZN 0.4832. Median contracts: NQ 0, GC 0, CL 0, ZN 2. Capital threshold to clear 1 contract at median N:   NQ requires equity >= $476k (computed: 0.01*equity >= 238*20)  GC requires equity >= $241k (computed: 0.01*equity >= 24*100)  CL requires equity >= $165k (computed: 0.01*equity >= 1.65*1000)  ZN requires equity >= $48k (computed: 0.01*equity >= 0.48*1000) -- below the $100k starting equity

**Implication:** Strategy as-locked at $100k starting equity is not tradable across all 4 markets in the OOS regime. ZN alone clears; the others require higher starting capital or smaller contract sizing (micro futures) or higher risk_pct.

### finding_5_in_sample_pass_was_capital_compatible

**Statement:** The IS S1 result that cleared all preregistered gates did so partly because IS-period (2013-2022) N values were small enough relative to $100k for all 4 markets to clear the floor early; AND IS-period equity grew over time (from $100k start to ~$293k end), so later trades operated at higher equity.

**Evidence:** IS P6: 111 closed trades; 18 NQ + 28 GC + 48 ZN + 17 CL. Per-market profitability was achieved with starting equity $100k. Equity grew net +$193k over 10 years; final ~$293k. OOS 3-year window did not give the strategy time to grow equity beyond the per-trigger floor for NQ/GC/CL.

**Implication:** The IS result was conditioned on the joint (capital, asset-vol) trajectory of 2013-2022. The OOS 2023-2025 starting state has higher vol AND higher absolute price levels (NQ ~14k-22k vs IS ~3k-15k) without commensurate starting capital. The strategy locked at $100k is structurally undersized for the OOS regime.

### finding_6_not_a_signal_failure

**Statement:** Per the OOS evidence, the s8-D1 candidate did not experience a signal failure at OOS. It experienced a capital-vs-contract-sizing mismatch that prevented the signal from being acted on for 3 of 4 markets.

**Evidence:** Findings 1-5 in combination: signal fires regularly (164/111/82/92 triggers), data decodes cleanly, diversification holds at OOS, root cause is sizing-skip cascade not signal collapse.

**Implication:** The OOS verdict INSUFFICIENT_SAMPLE per C7 closed enum is technically correct but masks the root cause. The honest interpretation is: signal intact, capital insufficient.

---

## RECOMMENDATION

### Primary: **`PARK_OOS_SIZING_UNDERSIZED_NOT_SIGNAL_FAILURE`**

### Secondary (optional only if operator chooses): `ESCALATE_REPARAMETERIZATION_TO_FRESH_SUCCESSOR_CANDIDATE_OPTIONAL_NOT_COMMITTED`

### Selected combined: **`PARK_OOS_SIZING_UNDERSIZED_NOT_SIGNAL_FAILURE + optional successor candidate`**

### Rationale synthesis

The s8-D1 candidate cleared every preregistered in-sample K-gate, A-gate, and C-contract at $100k starting equity over 2013-2022. At OOS 2023-2025 with the same locked parameters, the signal still fires (164/111/82/92 raw triggers per market), the diversification hypothesis still holds (K10 OOS PASS at 0.052), and the data decodes cleanly. However, the locked sizing rule (floor(0.01*$100,000 / (N * dollar_per_point))) returns 0 for NQ/GC/CL at every single OOS trigger, blocking the strategy from acting on its signal for 3 of 4 markets. ZN alone clears the floor. The honest park status is PARKED_SAFE_BUT_NOT_MONEY_PROVEN_OOS_SIZING_UNDERSIZED -- not a signal failure, not money-proven, but a structural parameter mismatch with the OOS regime. The chain has its decisive answer for s8-D1 as locked. The next research decision (fresh successor candidate with re-parameterized sizing, or pivot to a different family entirely) is the operator's; this memo does not preempt that. Live block remains permanent.

### Honest qualifications

- READY_FOR_LONGER_BACKTEST in C7 enum was achieved in-sample but is a research label only; not live-ready.
- PARKED_SAFE_BUT_NOT_MONEY_PROVEN_OOS_SIZING_UNDERSIZED is NOT a money-proven candidate.
- No profitability claim. No live promotion. FRC never granted. 6-gate live-block permanent.
- s8-D1 cannot be re-run under its own candidate_record_id with different parameters (plan-lock threshold-lock invariant).
- OOS DR4 was NOT directly evaluable (only S1 ran at OOS); IS-S0 vs OOS-S0 comparison not performed.
- OOS cost-stress matrix S0/S2/S3/S4 was NOT run (would be P9.5 equivalent); given the sizing-skip cascade explanation, cost-stress at OOS would also produce minimal trades for NQ/GC/CL regardless of cost tier.
- K10 OOS PASS is informative but the OOS window is 3 years; future regime shifts cannot be ruled out.
- ZN alone trading 15 times over 3 years is itself a thin OOS sample for single-market interpretation; no per-market live-readiness inference.

---

## DECISION OPTIONS EVALUATED

### PARK_OOS_SIZING_UNDERSIZED_NOT_SIGNAL_FAILURE
- preferred_per_operator_instruction: **True**
- rationale: Records s8-D1 as parked with the honest root cause finding from P9.5b: signal/diversification/data all intact at OOS; capital-vs-contract-sizing mismatch at $100k starting equity caused 3 of 4 markets to skip every trigger. This is not a signal-failure park, not a money-proven success; it is a structural parameter park that recognizes the bounded validity of the s8-D1 result. Live block remains permanent regardless.

### ESCALATE_REPARAMETERIZATION_TO_S9_OR_LATER_FRESH_CANDIDATE
- preferred_per_operator_instruction: **False**
- rationale: Would commit to a fresh successor (s9+ namespace) testing re-parameterized starting_cash, risk_pct, or contract type (e.g., micro futures MNQ/MGC/M2K). The plan-lock threshold-lock invariant forbids re-running s8-D1 with different parameters under the s8-D1 namespace, so a fresh candidate_record_id would be required. NOT selected as primary because committing to a fresh candidate is itself a separate research decision; this memo should not pre-commit to that.

### PARK_OOS_AS_INSUFFICIENT_SAMPLE_ONLY
- preferred_per_operator_instruction: **False**
- rationale: Conservative park that does not formalize the sizing-skip root cause beyond the P9.5b sealed audit. Less honest than option 1 because it masks the well-documented root cause; would create future ambiguity about why s8-D1 parked.

### Combined recommendation
- preferred_per_operator_instruction: **True**
- rationale: Park s8-D1 as locked (option 1) AND frame the fresh successor candidate as an OPTIONAL operator-decision path (option 2) WITHOUT committing to building it. The next research track (s9, s10, s11, ...) is for the operator to decide; the memo does not preempt that.

---

## SUCCESSOR-CANDIDATE FRAMING (PLAN-ONLY; NOT COMMITTED)

- Purpose: Frame the OPTIONAL operator-decision path of testing the s8-D1 signal under re-parameterized sizing. This memo does NOT commit to building any successor candidate; it only documents what a successor would entail if operator chose that path.
- Successor candidate_record_id pattern: `s9-cross-asset-donchian-no-pyramid-reparam-<param>-nq-gc-zn-cl OR pivot to a different family`
- Namespace collision note: The parallel session has started an s9-RSI-2 mean-reversion track at commit 5bd8e62. Any cross-asset Donchian reparameterization successor must use a non-colliding candidate_record_id (e.g., s10-* or s9-cross-asset-donchian-* explicitly distinct from s9-rsi2).

Parameter-change options (each requires fresh candidate_record_id):
- starting_cash_mnq_equivalent: increase from $100,000 to >=$476,000 (NQ-clearing threshold) to enable all 4 markets to trade
- risk_pct_per_unit: increase from 0.01 to e.g. 0.03 or 0.05 (more aggressive sizing per trade) -- changes the K1-K12 sensitivity profile
- contract type: pivot to micro futures (MNQ, MGC, M2K, MCL) which have 1/10 the dollar_per_point -- lowers the per-trigger capital threshold by ~10x
- universe substitution: replace NQ/GC/CL with markets where N * dollar_per_point fits the $100k floor at OOS levels -- changes the diversification hypothesis K10

What a successor would NOT do:
- Revive s8-D1 (the s8-D1 candidate parks permanently at PARKED_SAFE_BUT_NOT_MONEY_PROVEN_OOS_SIZING_UNDERSIZED)
- Re-use the s8-D1 candidate_record_id
- Claim the s8-D1 in-sample result transfers to the re-parameterized candidate (requires fresh sealed chain)
- Promote to live, paper, FRC -- all require their own separate authorizations

- operator_decision_required_before_any_successor_authoring: **True**
- no_successor_files_authored_in_p10: **True**

---

## WHAT P10 DOES NOT AUTHORIZE

- Any new backtest run (no run_in_sample invocation)
- Any audit re-run (P9, P9.5a, P9.5b are sealed; not re-run)
- OOS metric recomputation
- OOS cost-stress matrix run
- OOS K10 re-computation
- Code patch or driver modification
- Data fetch or Databento API call
- QC API call
- Network call
- Parameter change to s8-D1 (forbidden by plan-lock threshold-lock invariant)
- Fresh successor candidate authoring (requires separate operator decision)
- P11 lifecycle decision (requires separate authorization)
- Live trading change
- Paper trading change
- Scheduler change
- review_queue.json mutation
- obsidian-trade-logger touch
- Strategy Lab promotion
- FRC grant

### What P10 does authorize next:

> Operator may AUTHORIZE S8-D1 P11 lifecycle decision (PLAN-ONLY) which would formalize the park status into the sealed lifecycle record per the recommendation here.

---

## s7-D1 non-revival attestation

- `s7_d1_chain_status`: PERMANENTLY_PARKED_AT_COMMIT_f08220a
- `s7_d1_revived_by_this_memo`: False
- `s7_d1_used_as`: UPSTREAM_EVIDENCE_FOR_DELTA_CONTRAST_ONLY

---

## Parent chain (16 byte-stable; drift=0)

- `P9_5b_sizing_skip`: `957ede055785faf0...`
- `P9_5a_data_integrity`: `9d65511f83553de0...`
- `K10_oos`: `ccb3609b42f92e61...`
- `P9_oos_s1`: `dedd8003381a8b9a...`
- `P8_lifecycle`: `49b1e6a726183484...`
- `P7_5_k10_in_sample`: `221e759e09cc70b2...`
- `P7_decision_memo`: `e26d00587d39404d...`
- `P6_5_cost_stress`: `edae2e56cf16c925...`
- `P6_in_sample_diagnostic`: `07a3fa91509f2206...`
- `P4_smoke`: `1ab57a67f1a81be5...`
- `driver_build`: `d7b82d7adad62979...`
- `runner_build`: `e1f2a13cb860a629...`
- `phase2_plan`: `5e6fccd1aeb40db7...`
- `plan_lock`: `612abbbda7235c8c...`
- `tier_n_spec`: `8cff6babf8e4a451...`
- `selection_plan`: `6b7bdb4c350f4a77...`

---

## Negative invariants this turn (all True)

- `no_audit_rerun`: True
- `no_b005_001_revival`: True
- `no_broker_adapter_instantiated`: True
- `no_code_patch`: True
- `no_d5_revival_neither_s7_ym_only_nor_s8_zn_only`: True
- `no_data_fetch`: True
- `no_databento_api_call`: True
- `no_db_historical_instantiated`: True
- `no_driver_modification`: True
- `no_frc_granted`: True
- `no_fresh_successor_candidate_files_authored`: True
- `no_live_promotion`: True
- `no_live_trading_change`: True
- `no_network_call`: True
- `no_new_backtest_run`: True
- `no_nke_revival`: True
- `no_obsidian_trade_logger_mutation`: True
- `no_oos_cost_stress_run`: True
- `no_oos_k10_recomputation`: True
- `no_oos_metric_recomputation`: True
- `no_paper_trading_change`: True
- `no_parameter_change_to_s8_d1`: True
- `no_profitability_claim`: True
- `no_qc_api_call`: True
- `no_qc_cloud_submit`: True
- `no_review_queue_mutation`: True
- `no_run_in_sample_invoked`: True
- `no_s7_d1_file_modification`: True
- `no_s7_d1_revival`: True
- `no_scheduler_change`: True
- `no_strategy_lab_promotion`: True
- `no_threshold_loosening`: True

---

*End of s8-D1 P10 OOS decision memo. Sealed at `a493931f0b812fad837b9e7679710d03e445ea39d3b53cc8a3ec4ecd7309f9b3`. PLAN-ONLY. No new run. No OOS recomputation. No code patch. No fresh successor candidate authored.*
