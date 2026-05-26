# S10 Micro-Futures Successor Selection Plan (SEALED, PLAN-ONLY)

**Phase:** `S10_SELECTION_PLAN_SEALED_PLAN_ONLY`
**Operational status:** `SELECTION_PLAN_SEALED_AWAITING_OPERATOR_DECISION_ON_DIRECTION_AND_DATA_AVAILABILITY`
**Report date UTC:** 2026-05-26T17:47:44Z

**Selection plan seal:** `007110ff5a57dd04b184409bad64fd667374cd049155416c869a73f7af0c1f97`
**Predecessor (s8-D1 P11 lifecycle) seal:** `c79b06206c51d9b94f8d6ee2a9b78ba2d71a16eadbba18aa551319c61213849b`

> Labels: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, PLAN_AND_SPEC_ONLY, NO_FRC_GRANTED,
> S10_SELECTION_PLAN_SEALED, S8_D1_NOT_REVIVED, S7_D1_NOT_REVIVED,
> NO_TIER_N_SPEC_AUTHORED_THIS_TURN, NO_CANDIDATE_RECORD_ID_RESERVED_THIS_TURN
> Trading: PAUSED | Live: BLOCKED_AT_6_GATES | FRC: not granted
> No profitability claim. No live promotion.

---

## Motivation

- s8-D1 final status: **PARKED_SAFE_BUT_NOT_MONEY_PROVEN_OOS_SIZING_UNDERSIZED**
- s8-D1 root cause: capital-vs-contract-size sizing mismatch
- s8-D1 signal: intact, not signal failure
- s8-D1 OOS data: clean
- s8-D1 OOS K10: PASS (0.052)
- s8-D1 OOS sizing-skip pct per market: {'NQ': 100.0, 'GC': 100.0, 'ZN': 1.087, 'CL': 100.0}
- s8-D1 revived by this plan: **False**

**Purpose of S10:** Evaluate which next research direction best addresses the s8-D1 OOS sizing failure WITHOUT reviving s8-D1 and WITHOUT pre-committing to building any specific successor. This is a comparison plan; the operator decides.

---

## Scoring criteria (each 1-8, equal weight; max total = 64)

- **C1 Attacks_root_cause** (weight=1): Direction directly addresses the s8-D1 OOS failure (capital-vs-contract-size sizing mismatch).
- **C2 Signal_preservation** (weight=1): Direction preserves the s8-D1 signal logic (Donchian 55/20, no-pyramid, AMB6=NONE) so the test isolates the operational fix.
- **C3 Parameter_isolation** (weight=1): Direction changes the minimum number of parameters; outcome attributable cleanly to the change.
- **C4 Data_availability_risk** (weight=1): Probability that required data (continuous contracts in operator's Databento entitlement) is available without new vendor work. Higher score = lower risk.
- **C5 Operational_realism_at_100k** (weight=1): Direction would be practically operable at $100k starting capital (matches typical operator scale).
- **C6 Diversification_preservation** (weight=1): Direction preserves the K10 cross-asset diversification basis that motivated D1 originally.
- **C7 Predictability_of_outcome** (weight=1): Higher score for directions whose result is highly anticipated (so the test mostly confirms a hypothesis), LOWER score is also acceptable if the direction explores genuinely novel territory. Score weighted moderately because both ends of this scale have value.
- **C8 Cost_runtime_operator_burden** (weight=1): Lower SPARTA wall time + operator burden = higher score. Includes fetch cost, build cost, run cost.

Methodology: equal weighting; higher score = more favorable.

---

## Direction comparison (sorted by total score descending)

| ID | Direction | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | TOTAL | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **S10-D1** | Micro futures successor | 8 | 8 | 7 | 6 | 8 | 7 | 7 | 7 | **58** / 64 | ← **RECOMMENDED** |
| **S10-D2** | Higher-capital successor | 6 | 8 | 7 | 8 | 3 | 8 | 6 | 6 | **52** / 64 |  |
| **S10-D3** | Higher-risk successor | 5 | 7 | 7 | 8 | 6 | 8 | 5 | 6 | **52** / 64 |  |
| **S10-D5** | Hold / stop research | 1 | 1 | 8 | 8 | 8 | 1 | 1 | 8 | **36** / 64 |  |
| **S10-D4** | Pivot away from Donchian/futures trend family | 1 | 1 | 1 | 4 | 5 | 1 | 2 | 2 | **17** / 64 |  |

### S10-D1 — Micro futures successor (58/64)

- **Candidate record id pattern:** `s10-cross-asset-donchian-no-pyramid-micro-mnq-mgc-zn-mcl`
- **Universe:** ['MNQ.c.0', 'MGC.c.0', 'ZN.c.0', 'MCL.c.0']
- **Rationale:** Replace NQ/GC/CL with their micro counterparts (MNQ, MGC, MCL; each ~1/10 the dollar_per_point) while keeping ZN unchanged (no micro variant exists; ZN was already clearing the sizing floor in s8-D1 OOS). All other parameters byte-equivalent to s8-D1: Donchian 55/20, no-pyramid, AMB6 NONE, 1% risk, $100k start. Single non-strategy delta: universe substitution.
- **Expected outcome:** IS run should produce signal-comparable behavior to s8-D1 IS (same Donchian/no-pyramid logic on micros that track the same underlying price action). Per-trade dollar amounts ~1/10 of s8-D1; sharpe should be similar. OOS test is the novel evidence: does the operational fix actually unblock NQ/GC/CL-equivalent contracts at $100k?

### S10-D2 — Higher-capital successor (52/64)

- **Candidate record id pattern:** `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl`
- **Universe:** ['NQ.c.0', 'GC.c.0', 'ZN.c.0', 'CL.c.0']
- **Rationale:** Keep the s8-D1 universe but change starting_cash_mnq_equivalent from $100,000 to >= $476,000 (NQ-clearing threshold at OOS median N). All other parameters byte-equivalent. Tests whether the strategy works as-designed when capital is sufficient.
- **Expected outcome:** Highly predictable: at $500k starting capital, all 4 markets should clear the contract floor at IS and OOS; the strategy would trade approximately the same triggers as s8-D1 P9 + P9.5a found, just with non-zero contracts.

### S10-D3 — Higher-risk successor (52/64)

- **Candidate record id pattern:** `s10-cross-asset-donchian-no-pyramid-reparam-risk-nq-gc-zn-cl`
- **Universe:** ['NQ.c.0', 'GC.c.0', 'ZN.c.0', 'CL.c.0']
- **Rationale:** Increase risk_pct_per_unit from 0.01 to 0.03 (or 0.05). Some markets would then clear the floor at $100k. Tests whether the strategy survives a more-aggressive sizing rule.
- **Expected outcome:** At 3% risk, NQ requires equity >= ~$159k (still doesn't clear at $100k for NQ at OOS median N=238). At 5% risk, NQ requires equity >= ~$95k (would clear at $100k). MaxDD scales roughly with risk_pct; expect K4 to be much closer to firing at 5% risk.

### S10-D5 — Hold / stop research (36/64)

- **Candidate record id pattern:** `(none)`
- **Universe:** (none)
- **Rationale:** No new candidate. Chain pauses at s8-D1 P11 terminal park; operator focuses elsewhere (e.g., the parallel session's s9-RSI-2 work, hydra_video, youtube_growth, etc.).
- **Expected outcome:** No new evidence. s8-D1 lifecycle index stands as the canonical record. Research attention reallocates.

### S10-D4 — Pivot away from Donchian/futures trend family (17/64)

- **Candidate record id pattern:** `s10-* in a different family (e.g., mean-reversion-equities, vol-targeted-carry, etc.)`
- **Universe:** TBD per family
- **Rationale:** Move to a different research direction entirely. The parallel session is already running s9-RSI-2 mean-reversion, so an S10 in a third family would be a parallel third track. Most expensive in operator attention; potentially highest novelty per dollar.
- **Expected outcome:** Unknown by construction; depends entirely on which family is chosen. Highest expected variance in outcome.

---

## RECOMMENDATION

### Recommended: **`S10-D1` — Micro futures successor (MNQ + MGC + ZN + MCL)**

Score: **58 / 64**

### Rationale

S10-D1 is the cleanest root-cause test: it changes ONE non-strategy parameter (universe substitution to micro contracts) while preserving every s8-D1 strategy parameter (Donchian 55/20, no-pyramid, AMB6=NONE, 1% risk, $100k start). MNQ/MGC/MCL each have ~1/10 the dollar_per_point of their parent contracts, which directly addresses the floor(0.01 * $100,000 / (N * dollar_per_point)) = 0 outcome that blocked NQ/GC/CL in s8-D1 OOS. ZN is preserved at full size because it was the only s8-D1 market that cleared the floor. The result is partially predictable at the signal layer (micros track the same underlying price action; same Donchian triggers fire on the same days) and genuinely novel at the operational layer (does the strategy actually trade all 4 markets at $100k OOS?).

### Secondary recommendation (for operator consideration only)

If MNQ/MGC/MCL data availability is blocked or the historical span is too short to be useful, S10-D2 (higher-capital successor at >= $476k starting capital) is the next-best test. It changes one parameter (starting_cash) and uses the existing s8-D1 IS+OOS cache without any new fetch.

### Why other directions were not selected

- **S10-D2**: Less practical at typical $100k operator scale; high predictability of outcome reduces evidence-per-attention; doesn't help operators with smaller capital.
- **S10-D3**: Increasing risk_pct to 3-5% is aggressive; expected MaxDD growth puts K4 closer to firing; net effect is changing a sensitive sizing parameter without solving the structural problem.
- **S10-D4**: Doesn't address s8-D1 root cause; parallel session already running s9-RSI-2 mean-reversion (commits 5bd8e62, c5393ab, 1a055bd); a third concurrent research track is high operator-attention cost without obvious payoff.
- **S10-D5**: Legitimate operator choice (allocate attention elsewhere), but s8-D1's unfinished business is well-defined and cheap to resolve; not selecting this unless operator explicitly prefers it.

- No candidate_record_id reserved by this plan: **True**
- Reserving a candidate_record_id requires separate operator authorization: **True**
- s8-D1 remains terminally parked: **True**

---

## DATA AVAILABILITY GATE (mandatory before S10-D1 Tier-N spec)

**Purpose:** Before any S10-D1 Tier-N spec is authored, operator must confirm MNQ.c.0, MGC.c.0, MCL.c.0 are available in the Databento GLBX.MDP3 dataset with stype_in=continuous and ohlcv-1m schema, for the in-sample window 2013-01-01..2022-12-30 and OOS window 2023-01-01..2025-12-30.

**Operator actions required:**
- Confirm Databento entitlement covers MNQ, MGC, MCL on GLBX.MDP3
- Confirm continuous contract format (stype_in=continuous, *.c.0 suffix) is supported for these symbols
- Confirm historical coverage extends back to 2013-01-01 for IS window (MNQ/MGC/MCL launch dates may post-date IS start; in-sample window may need to be shortened if symbols don't have full 2013-2022 coverage)
- Operator runs a minimal availability test via local Python script (SPARTA does NOT execute; mirrors P8.5 pattern)
- Operator produces availability-attestation manifest before SPARTA proceeds with Tier-N spec

- **Data availability gate must be satisfied before S10-D1 Tier-N spec:** True
- **SPARTA does NOT execute the availability check:** True

**If data unavailable — implications:**
- If MNQ launched after 2013-01-01, in-sample window for S10-D1 must be shortened (e.g., 2019-01-01 onward); this CHANGES the comparability with s8-D1 IS
- If MGC has gaps, the s10 universe may need to substitute (e.g., GLD ETF in a separate paper-only research track; NOT under SPARTA execution)
- If MCL launches post-2013, similar window restriction

### Symbol historical note (INFORMATIONAL ONLY — operator must verify)

Public-record informational note about CME micro launch dates. These dates are operator-verifiable, NOT a SPARTA data claim.

- MNQ launch (public record): 2019-05-06 (MNQ launched several years AFTER s8-D1 IS start of 2013-01-01)
- MGC launch (public record): 2010-10-04 (MGC has been available since well before s8-D1 IS start)
- MCL launch (public record): 2021-07-12 (MCL launched DURING the s8-D1 OOS window; no IS-window history available)

**Implication for S10-D1:** If these launch dates are accurate per Databento entitlement, the S10-D1 in-sample window CANNOT be 2013-2022 byte-equivalent to s8-D1 IS. Practical options: (a) shorten S10-D1 in-sample to 2021-07-13..2022-12-30 (lose IS power; very thin sample, ~1.5 years); (b) shorten to 2019-05-07..2022-12-30 if dropping MCL (changes universe); (c) use ES/NQ/GC/CL full-size IS for 2013-2022 AND switch to MNQ/MGC/MCL only for OOS (heterogeneous IS-vs-OOS contract; comparability concern); (d) accept that S10-D1 cannot truly mirror s8-D1 IS and treat it as a fresh OOS-focused candidate with a different IS span. All of these are operator decisions; the data availability check gate must be satisfied BEFORE Tier-N spec authoring.

- Operator must verify launch dates via Databento entitlement: **True**

---

## Non-revival attestations

- `s8_d1_revived_by_this_plan`: False
- `s8_d1_remains_at_terminal_park_status`: PARKED_SAFE_BUT_NOT_MONEY_PROVEN_OOS_SIZING_UNDERSIZED
- `s7_d1_revived`: False
- `s7_d5_ym_only_revived`: False
- `s8_d5_zn_only_revived`: False
- `b005_001_revived`: False
- `nke_options_wheel_revived`: False
- `any_fresh_s10_candidate_requires_separate_operator_authorization_and_fresh_candidate_record_id`: True
- `any_strategy_parameter_change_must_use_fresh_candidate_record_id_per_plan_lock_threshold_lock_invariant`: True

---

## What this plan does NOT authorize

- any Tier-N spec authoring
- any candidate_record_id reservation
- any code authoring or modification
- any data fetch
- any Databento API call
- any QC API call
- any backtest or audit
- any OOS inspection
- any live trading change
- any paper trading change
- any scheduler change
- any review_queue.json mutation
- any obsidian-trade-logger touch
- any Strategy Lab promotion
- any FRC grant
- any s8-D1 file modification or revival
- any operator data-availability check execution (operator-owned)

---

## Next-step decision framework for operator

### if_operator_approves_S10_D1_micro_futures
- STEP 1: Operator runs a Databento availability check for MNQ.c.0, MGC.c.0, MCL.c.0 on GLBX.MDP3 (PRE-Tier-N gate)
- STEP 2: Operator delivers availability attestation manifest (file count + bytes + first/last date per symbol)
- STEP 3: AUTHORIZE S10-D1 Tier-N spec authoring (PLAN-ONLY; uses confirmed data availability; states final in-sample window based on actual MNQ/MGC/MCL launch dates)
- STEP 4: Subsequent steps follow the s8-D1 chain pattern (plan-lock, phase-2 plan, BUILD, smoke, IS, IS cost-stress, K10, P8, P8.5 fetch, P9, P9.5a/b, P10, P11) -- each requires separate authorization

### if_operator_chooses_S10_D2_higher_capital_instead
- AUTHORIZE S10-D2 Tier-N spec authoring (PLAN-ONLY; same s8-D1 universe; starting_cash >= $476k)
- Uses existing s8-D1 IS+OOS cache; no fresh fetch needed
- Faster path to result; less novel evidence

### if_operator_chooses_S10_D5_hold_stop
- No further SPARTA action on cross-asset Donchian track
- s8-D1 chain stands; operator focuses on parallel session work or other projects

---

## Parent chain (11 byte-stable; drift=0)

- `S8_D1_P11_lifecycle`: `c79b06206c51d9b9...`
- `S8_D1_P10_decision`: `a493931f0b812fad...`
- `S8_D1_P9_5b_sizing`: `957ede055785faf0...`
- `S8_D1_P9_5a_data`: `9d65511f83553de0...`
- `S8_D1_K10_OOS`: `ccb3609b42f92e61...`
- `S8_D1_P9_oos_s1`: `dedd8003381a8b9a...`
- `S8_D1_P6_in_sample`: `07a3fa91509f2206...`
- `S8_D1_tier_n_spec`: `8cff6babf8e4a451...`
- `S8_D1_plan_lock`: `612abbbda7235c8c...`
- `S8_selection_plan`: `6b7bdb4c350f4a77...`
- `S7_D1_PARKING`: `551fdce46c0e373e...`

---

## Negative invariants this turn (all True)

- `no_audit`: True
- `no_b005_001_revival`: True
- `no_backtest`: True
- `no_candidate_record_id_reserved`: True
- `no_code_authored`: True
- `no_d5_revival`: True
- `no_data_fetch`: True
- `no_databento_api_call`: True
- `no_db_historical_instantiated`: True
- `no_frc_granted`: True
- `no_live_promotion`: True
- `no_live_trading_change`: True
- `no_network_call`: True
- `no_nke_revival`: True
- `no_obsidian_trade_logger_mutation`: True
- `no_oos_inspection`: True
- `no_paper_trading_change`: True
- `no_profitability_claim`: True
- `no_qc_api_call`: True
- `no_review_queue_mutation`: True
- `no_s7_d1_revival`: True
- `no_s8_d1_file_modification`: True
- `no_s8_d1_revival`: True
- `no_scheduler_change`: True
- `no_tier_n_spec_authored`: True

---

*End of S10 micro-futures successor selection plan. Sealed at `007110ff5a57dd04b184409bad64fd667374cd049155416c869a73f7af0c1f97`. PLAN-ONLY. No Tier-N spec authored. No candidate_record_id reserved. No code. No backtest. No fetch.*
