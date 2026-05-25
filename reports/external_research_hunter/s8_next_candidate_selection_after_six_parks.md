# s8 Next-Candidate Selection Plan -- after SIX parks

**Schema:** `sparta.external_research_hunter.s8_next_candidate_selection_after_six_parks.v1`
**Status:** `SEALED`
**Park count at selection:** **6**
**Sealed at (UTC):** `2026-05-25T21:16:22Z`
**Direct predecessor (s7 selection plan seal):** `8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac`
**Trading status:** `PAUSED`
**Live status:** `BLOCKED_AT_6_GATES`
**FRC granted:** `False`
**Drift count at plan:** **0**

> PLAN ONLY. No code. No backtest. No Databento API. No QC. No fetch. No network.
> No live/paper trading. No s7-D1 revival. No s2-s6 revival. No profitability claim.
> All sealed parents BYTE-STABLE. Parked candidates NOT revived. Six parks documented.
> Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC never granted.

## Predecessor chain (six parks)
- `s2_NKE`
- `s3_MNQ_DRB`
- `s4_TURTLE`
- `s5_DONCHIAN_NQ`
- `s6_MULTI_MARKET_DONCHIAN_NQ_ES_YM`
- `s7_D1_CROSS_ASSET_DONCHIAN_NQ_GC_ZN_CL`

## Six parking reports inherited as evidence
### s2_NKE_options_wheel_REJECT_TIER1

- `reference`: `external_research_hunter/HUNTER_BRAIN_LESSONS.md (LESSON_HUNTER_001-008)`
- `park_status`: `REJECT_TIER1 / REJECT_FAST under DR2`
- **primary_lesson:** Single-symbol equity options is not a stable foundation; candidate-fragility-as-signal (LESSON_HUNTER_001)

### s3_MNQ_daily_range_breakout

- `parking_seal`: `1f557888e1212d6ffe0e305ac43308977f618db7473b22c90e407fe805d3f7ad`
- `park_status`: `PARKED`
- **primary_lesson:** Daily-range breakout on MNQ produced safety issues + inadequate sample. Single-market daily-breakout without trend-confirmation lacks structural edge of multi-day trend-following.

### s4_TURTLE_SYSTEM_1_NQ_C0

- `parking_seal`: `8cda3ca644524cd558cc3a1291a869d983a8c5fae9c1d0f15d6e56ba266a1cb4`
- `park_status`: `PARKED`
- **primary_lesson:** Turtle System 1 with same-direction filter on NQ.c.0 fired K-criteria (insufficient sample + negative expectancy). Filter aggressively skipped trades; only 20 closed in 10 years -- not enough evidence.

### s5_DONCHIAN_NO_FILTER_NQ_C0

- `parking_seal`: `6c308b42da6854d5dd3f8e8936fb5299666dae3158904bec65ec6458156f234c`
- `park_status`: `PARKED_SAFE_BUT_NOT_MONEY_PROVEN`
- **primary_lesson:** Removing System 1 filter cleared K9 sample bottleneck (64 trades vs s4's 20). P/L ratio 5.18 vs s4's 1.2. But single-market NQ.c.0 WR 15.62% fell 0.56pp short of P/L-implied breakeven 16.18%. Single-market sample noise hypothesis motivated s6.

### s6_MULTI_MARKET_DONCHIAN_NO_FILTER_NQ_ES_YM

- `parking_seal`: `f6953c1fb3c334d34572aa7dac29317b4ff412bf3648db62276707ef9de2894a`
- `park_status`: `PARKED_SAFE_BUT_NOT_MONEY_PROVEN`
- **primary_lesson:** Same-family 3-market diversification (NQ+ES+YM, ~0.88 avg pairwise corr) FALSIFIED as path to breakeven. WR fell (15.62 -> 14.66%), P/L fell (5.18 -> 4.68), breakeven WR rose (16.18 -> 17.62%), gap widened (-0.56pp -> -2.96pp). ES friction dominated loss; YM was only profitable market. Cross-asset hypothesis motivated s7.

### s7_D1_CROSS_ASSET_DONCHIAN_NO_FILTER_NQ_GC_ZN_CL

- `parking_seal`: `551fdce46c0e373eac03d79597d6439d740ae56f4a0ba9f2c6f2b39d25974b32`
- `park_status`: `PARKED_SAFE_BUT_NOT_MONEY_PROVEN (just committed at P8)`
- `k_fire`: `['K4']`
- `c7_verdict`: `READY_FOR_LONGER_BACKTEST (with K4 caveat)`
- **primary_lesson:** Cross-asset diversification (NQ+GC+ZN+CL, avg pairwise corr <0.5) PRODUCED genuinely positive per-trade economics: 313 closed trades, expectancy +$3,667/trade, WR 43.13% (+14.17 pp ABOVE breakeven 28.96%), Sharpe proxy +0.192, P/L ratio 2.45, 3 of 4 markets profitable (CL/NQ/ZN; only GC losing). DECISIVELY clears s6's primary lesson concern: cross-family diversification DOES lift the signal above breakeven. BUT 4-unit pyramid produced catastrophic -221.67% trade-curve MaxDD (exceeds K4 threshold -50%). Pyramid amplification at low WR (s6 lesson 3) reproduces in cross-asset universe. Signal works; pyramid mechanics need to change.
- `load_bearing_remaining_question`: `Does removing pyramid (max_units = 1) let cross-asset signal pass K4 while preserving K1/K2 (Sharpe > 0, expectancy > 0)?`

## Why s7-D1 signal worked but pyramid failed

### Signal evidence (positive)
- 313 closed trades over 10 years across 4 cross-asset markets -- adequate sample
- Expectancy +$3,667/trade: positive and meaningful
- Win rate 43.13% is +14.17 percentage points ABOVE the P/L-ratio-implied breakeven (28.96%) -- this is a LARGE margin, not noise
- 3 of 4 markets profitable independently (CL +$580k, NQ +$225k, ZN +$370k); only GC losing (-$27k)
- Sharpe proxy per-trade +0.192 (positive)
- P/L ratio 2.45 (avg winner > 2x avg loser)
- C3 safety counters all zero (no implementation issues; the strategy ran cleanly)
- Comparison to s6 (same-family NQ+ES+YM): s6 WR 14.66% with -2.96 pp gap BELOW breakeven; s7-D1 WR 43.13% with +14.17 pp gap ABOVE breakeven. The cross-family hypothesis DECISIVELY corroborated at the signal layer.

### Pyramid failure mechanism
- 4-unit pyramid with 0.5N spacing means each market can hold up to 4 positions, each 0.5N apart
- Per s7-D1: 313 trades over ~2,500 trading days -> average ~8 days between trades portfolio-wide
- Pyramid amplification: when a strong move triggers full 4-unit pyramid, a reversal causes 4 stop-losses in quick succession
- At 1% risk per unit * 4 units per market * 4 markets = 16% portfolio risk if all units stop simultaneously
- Multiple pyramid cycles per market over 10 years compound: trade-curve MaxDD = -221.67%
- s6 saw the same pattern: MaxDD -123% on 191 trades (s5 single-market: -38% on 64 trades). Pyramid amplification scales roughly with trade count even when per-trade expectancy is positive.
- Mechanism is inherent to the locked 4-unit + 0.5N spacing pyramid design: more pyramid units + smaller spacing = more aggressive scaling INTO winners AND more cumulative loss on reversals

### Interpretation
The s7-D1 result is the cleanest possible decomposition of the trend-following arc: signal layer (cross-asset diversification) is empirically validated; sizing layer (4-unit pyramid) is empirically falsified. The two are decoupled by design (cf. Tier-N spec §13 acceptance gates A1-A4 vs A8/A10). The natural follow-up is to test the same signal with reduced sizing. D1 (no-pyramid) is the direct, minimal test of that question.

## Scoring criteria
- **C1_addresses_K4_pyramid_DD_root_cause:** 5 = directly tests no-pyramid or reduced-pyramid on s7-D1 universe; 0 = doesn't address K4
- **C2_data_availability_cached:** 5 = uses existing 480-file local DBN cache; 1 = requires fresh Databento downloads
- **C3_avoids_ad_hoc_parameter_tuning:** 5 = single-parameter reduction with first-principles motivation; 1 = adds new tuning knobs without justification
- **C4_sample_size_likely_above_K9_100:** 5 = clearly >= 100 trades expected; 1 = sample bottleneck likely
- **C5_first_principles_rationale:** 5 = strong first-principles justification tied to s7-D1 K-criteria evidence; 1 = ad-hoc
- **C6_avoids_survivorship_cherry_pick_bias:** 5 = no survivorship risk; 0 = severe cherry-pick (e.g. best-of-N market selection)
- **C7_doable_in_one_candidate_cycle:** 5 = clearly doable; 1 = scope-creep risk
- **C8_safety_template_inheritable_byte_equivalent:** 5 = Phase-2 safety template C1-C8 contracts inherit byte-equivalent; 1 = requires template adaptation

## Candidate directions (6) -- scored
| ID | Direction | Total score |
|---|---|---:|
| `D1` | Cross-asset Donchian no-pyramid (max_units_per_market = 1) | **39 / 40** ← **RECOMMENDED** |
| `D2` | Cross-asset Donchian reduced pyramid (max_units_per_market = 2) | **29 / 40** |
| `D3` | Move OFF Donchian/trend-following family entirely (mean reversion / stat arb / carry / vol) | **23 / 40** |
| `D4` | Cross-asset Donchian different lengths (e.g., 100-day entry / 20-day exit) | **23 / 40** |
| `D5` | Bonds-only Donchian on ZN alone (single-market follow-up) | **25 / 40** |
| `D6` | Formal family-level park: declare trend-following falsified for this operator/universe and DEFER any further work | **28 / 40** |

### D1 -- Cross-asset Donchian no-pyramid (max_units_per_market = 1)

**id:** `s8-cross-asset-donchian-no-pyramid-nq-gc-zn-cl`

**Description:** Same locked Donchian-55 entry / Donchian-20 exit / 2N stop / 1% portfolio sizing on the same s7-D1 universe (NQ + GC + ZN + CL), with the ONE parameter REDUCTION: max_units_per_market = 1 (no pyramiding). Directly tests whether the s7-D1 K4 fire (catastrophic -221% DD) is entirely a pyramid-amplification artifact, or whether the underlying signal has DD issues even at single-unit sizing.

- **Addresses K4 root cause?** `True`
- **Data status:** `100% CACHED (480 .dbn.zst files; same s7-D1 cache)`

**Pros:**
- Most direct test of the unfixed remaining hypothesis from s7-D1: does removing pyramid amplification let the genuinely-positive cross-asset signal pass K4?
- Single-parameter knob (max_units 4 -> 1); minimal degrees of freedom for overfit
- Uses existing 480-file local DBN cache (zero new Databento downloads, zero new operator action)
- Uses well-validated helpers from main.py (PyramidManager works trivially with max_units=1; PortfolioCapTracker s6-bugfix still relevant)
- Strong first-principles motivation: K4 fired in s7-D1; the proximate cause is pyramid; reducing pyramid is the direct fix
- Honest interpretation regardless of outcome: passes -> cross-asset signal + minimal sizing works; fails K1/K2 -> Faith's alpha required pyramid amplification; fails K4 still -> signal itself has DD issues beyond pyramid
- Expected trade count similar order as s7-D1 (~150-300 trades; entries fire on same Donchian-55 breakouts) -- comfortably above K9 threshold of 100
- Reuses the patched in_sample_driver.py mechanics; minimal new code surface (only CONFIG['max_units_per_market'] differs)

**Cons:**
- REMOVES Faith's primary alpha-amplification mechanism: winners are no longer scaled into; per-trade expectancy may collapse without amplification (s5/s6 showed pyramid is part of how P/L ratio gets to ~5x)
- If expectancy collapses below zero or Sharpe goes negative, the strategy is genuinely falsified at the cross-asset universe (no further Donchian variant likely to help)
- Cannot use s7-D1's prior result for ANY parameter inheritance (rule: fresh candidate_record_id and fresh sealed chain)
- Does not address GC's losing-market problem (33.9% WR, -$27k) -- a single losing market still drags portfolio

**Scoring:**
| Criterion | Score |
|---|---:|
| C1_addresses_K4_pyramid_DD_root_cause | 5 |
| C2_data_availability_cached | 5 |
| C3_avoids_ad_hoc_parameter_tuning | 5 |
| C4_sample_size_likely_above_K9_100 | 5 |
| C5_first_principles_rationale | 5 |
| C6_avoids_survivorship_cherry_pick_bias | 4 |
| C7_doable_in_one_candidate_cycle | 5 |
| C8_safety_template_inheritable_byte_equivalent | 5 |
| **Total** | **39 / 40** |

### D2 -- Cross-asset Donchian reduced pyramid (max_units_per_market = 2)

**id:** `s8-cross-asset-donchian-2unit-pyramid-nq-gc-zn-cl`

**Description:** Same universe as D1 (NQ + GC + ZN + CL), but max_units_per_market = 2 (compromise between full Faith pyramid and no-pyramid). Empirically halves the pyramid amplification while preserving SOME of the winner-amplification mechanic Faith designed in.

- **Addresses K4 root cause?** `partial`
- **Data status:** `100% CACHED (same as D1)`

**Pros:**
- Empirical compromise between Faith's full pyramid (4) and no-pyramid (1)
- Halves max possible DD-amplification while preserving some winner-amplification
- Easy to implement (same change to CONFIG)
- Uses existing cache

**Cons:**
- Ad-hoc parameter choice -- why 2 and not 3 or 1.5? No first-principles justification for the specific number 2; pure empirical knob
- Risks overfitting to s7-D1 in-sample result: 'we saw -221% DD with max_units=4, so let's try max_units=2 because it might give acceptable DD' is exactly the kind of post-hoc tuning the Phase-2 plan C8 weak-performance rejection rule forbids
- Even at max_units=2, DD could still exceed K4 50% threshold (s5 single-market hit -38% MaxDD on 64 trades; cross-asset 4-market portfolio at 2x amplification could easily hit 100%+ on 200+ trades)
- Does NOT decisively test the load-bearing hypothesis (pyramid vs no-pyramid); creates an intermediate result with ambiguous interpretation

**Scoring:**
| Criterion | Score |
|---|---:|
| C1_addresses_K4_pyramid_DD_root_cause | 3 |
| C2_data_availability_cached | 5 |
| C3_avoids_ad_hoc_parameter_tuning | 2 |
| C4_sample_size_likely_above_K9_100 | 5 |
| C5_first_principles_rationale | 2 |
| C6_avoids_survivorship_cherry_pick_bias | 2 |
| C7_doable_in_one_candidate_cycle | 5 |
| C8_safety_template_inheritable_byte_equivalent | 5 |
| **Total** | **29 / 40** |

### D3 -- Move OFF Donchian/trend-following family entirely (mean reversion / stat arb / carry / vol)

**id:** `s8-mean-reversion-or-stat-arb-or-carry-or-vol-family-shift`

**Description:** After 6 same-family parks (s2 NKE wheel + s3 MNQ DRB + s4 Turtle + s5 Donchian NQ + s6 Multi-market Donchian + s7-D1 Cross-asset Donchian), authorize a FRESH research direction in a non-trend-following family. Candidate sub-families: (a) mean reversion (e.g., Bollinger-band reversion on indices); (b) statistical arbitrage (pairs trading); (c) calendar spread / front-back carry; (d) volatility carry (VIX futures term structure); (e) cross-sectional momentum/reversal hybrid. Sub-family choice is operator-directed.

- **Addresses K4 root cause?** `different family entirely; K4 may or may not apply`
- **Data status:** `VARIES; some require fresh Databento downloads or different vendors (VIX, options, etc.)`
- **Operator note:** D3 should be HELD as the natural s9 direction if D1 parks. Running D1 first definitively closes whether trend-following on the cross-asset universe is salvageable; D3 is the right move ONLY after that decisive answer is recorded.

**Pros:**
- Acknowledges that 6/6 parks on Donchian-cousins might indicate the trend-following FAMILY itself is unsuited to the operator/universe combination
- Opens unexplored research space
- Could find genuine alpha in a family the chain has not tested
- Survivorship/cherry-pick bias well-controlled (cross-family is genuinely different)
- Aligns with s7 selection plan's 'honest qualification for operator': 'After 6-7 parks in one family, family-level falsification becomes the prudent prior.'

**Cons:**
- VAST scope -- needs significant operator direction on which sub-family
- Requires reading new research sources not in current Tier-N spec library (the existing s3-s7 chains all reference trend-following sources)
- Different families need different safety contract templates (Phase-2 safety template C1-C8 was extracted from NKE wheel; some contracts may need adaptation for non-options/non-futures strategies)
- Could burn many candidates exploring sub-families before finding traction (each sub-family is effectively a fresh s3-equivalent first-test)
- PREMATURE without first running D1 -- D1 IS the falsification test that closes the loop on whether trend-following on cross-asset survives sizing fix

**Scoring:**
| Criterion | Score |
|---|---:|
| C1_addresses_K4_pyramid_DD_root_cause | 3 |
| C2_data_availability_cached | 2 |
| C3_avoids_ad_hoc_parameter_tuning | 3 |
| C4_sample_size_likely_above_K9_100 | 3 |
| C5_first_principles_rationale | 3 |
| C6_avoids_survivorship_cherry_pick_bias | 4 |
| C7_doable_in_one_candidate_cycle | 2 |
| C8_safety_template_inheritable_byte_equivalent | 3 |
| **Total** | **23 / 40** |

### D4 -- Cross-asset Donchian different lengths (e.g., 100-day entry / 20-day exit)

**id:** `s8-cross-asset-donchian-different-channel-lengths-100-20`

**Description:** Same universe as D1/D2; same 2N stop, same 4-unit pyramid, same 1% sizing; CHANGE the Donchian entry length from 55 -> 100 (more conservative entries, fewer breakouts) while keeping exit at 20. Tests whether reducing entry frequency alone reduces DD without touching the pyramid mechanic.

- **Addresses K4 root cause?** `False`
- **Data status:** `100% CACHED`

**Pros:**
- Uses existing cache
- Tests an orthogonal knob (entry frequency rather than position size)
- Could find that the DD problem is 'too many trades' rather than 'too much pyramid'

**Cons:**
- Ad-hoc parameter tuning of well-validated Faith parameters; Faith's 55 was deliberate (longer = miss too many trends)
- Adds a knob without first-principles justification for the specific number 100
- Does NOT address pyramid amplification (the demonstrated proximate cause of K4)
- Even with fewer entries, 4-unit pyramids on fewer-but-larger moves could still produce similar cumulative DD
- Risks running the loop multiple times tuning channel length (overfit trap)

**Scoring:**
| Criterion | Score |
|---|---:|
| C1_addresses_K4_pyramid_DD_root_cause | 1 |
| C2_data_availability_cached | 5 |
| C3_avoids_ad_hoc_parameter_tuning | 1 |
| C4_sample_size_likely_above_K9_100 | 3 |
| C5_first_principles_rationale | 1 |
| C6_avoids_survivorship_cherry_pick_bias | 2 |
| C7_doable_in_one_candidate_cycle | 5 |
| C8_safety_template_inheritable_byte_equivalent | 5 |
| **Total** | **23 / 40** |

### D5 -- Bonds-only Donchian on ZN alone (single-market follow-up)

**id:** `s8-zn-only-donchian-with-or-without-pyramid`

**Description:** ZN was the highest-trade-count market in s7-D1 (115 trades, +$370k, 34% WR). Run single-market Donchian on ZN.c.0 alone to test whether the bond-market trend-following signal is the genuine alpha source and other markets are noise / cost-drag.

- **Addresses K4 root cause?** `partial (single-market pyramid much smaller)`
- **Data status:** `100% CACHED (ZN slice of existing cache)`
- **OVERFIT FLAG:** SEVERE -- recommended AGAINST per s7 selection plan precedent

**Pros:**
- Uses existing ZN cache
- Simple single-market test
- Could clarify which markets are signal vs noise in the s7-D1 universe

**Cons:**
- SEVERE survivorship/cherry-pick bias: selecting the best-performing market of 4 from a single in-sample run is the textbook overfit trap (cf. s7 selection plan §D5 'YM-only follow-up' which was EXPLICITLY recommended AGAINST and scored 12/40)
- Sample size concern: 115 trades on ZN over 10 years is just above K9=100 threshold; not a strong sample
- Same overfit-trap reasoning that disqualified D5 in the s7 selection plan applies here verbatim with ZN substituted for YM
- Doesn't test the load-bearing cross-asset hypothesis at all -- regresses to single-market
- Even at single-market scale, 4-unit pyramid could still produce significant DD (s5 NQ-alone hit -38% on 64 trades)

**Scoring:**
| Criterion | Score |
|---|---:|
| C1_addresses_K4_pyramid_DD_root_cause | 2 |
| C2_data_availability_cached | 5 |
| C3_avoids_ad_hoc_parameter_tuning | 4 |
| C4_sample_size_likely_above_K9_100 | 3 |
| C5_first_principles_rationale | 1 |
| C6_avoids_survivorship_cherry_pick_bias | 0 |
| C7_doable_in_one_candidate_cycle | 5 |
| C8_safety_template_inheritable_byte_equivalent | 5 |
| **Total** | **25 / 40** |

### D6 -- Formal family-level park: declare trend-following falsified for this operator/universe and DEFER any further work

**id:** `s8-formal-trend-following-family-park-and-defer`

**Description:** Author a sealed s8 FAMILY-FALSIFICATION_NOTE rather than a candidate. Records that after 6 same-family parks across s2-s7-D1, the trend-following family is empirically falsified for this operator/universe combination (US futures + equity options) under the locked Phase-2 safety template. The operator commits to NO further trend-following candidates in this chain. Future work (if any) must move to a different strategy family with a fresh selection plan.

- **Addresses K4 root cause?** `n/a -- declines to test further`
- **Data status:** `n/a -- no new data needed`

**Pros:**
- Most honest if pattern continues: 6/6 parks is strong evidence of family unsuitability
- Saves operator time / cost on further trend-following tests
- Aligns with Phase-2 plan §C8 'weak performance rejection rule' applied at family level
- Forces operator to choose a different research direction explicitly

**Cons:**
- PREMATURE: s7-D1 produced a POSITIVE per-trade economics result -- the K4 fire is the only blocker. A no-pyramid test (D1) would decisively resolve whether the family is salvageable or genuinely falsified. Declaring family falsification BEFORE running D1 throws away the cheapest test of the load-bearing hypothesis.
- Loses the empirical answer to the most pointed remaining question (pyramid vs no-pyramid on cross-asset)
- Operator might regret it later if a non-trend-following sub-family also parks repeatedly

**Scoring:**
| Criterion | Score |
|---|---:|
| C1_addresses_K4_pyramid_DD_root_cause | 0 |
| C2_data_availability_cached | 5 |
| C3_avoids_ad_hoc_parameter_tuning | 5 |
| C4_sample_size_likely_above_K9_100 | n/a |
| C5_first_principles_rationale | 3 |
| C6_avoids_survivorship_cherry_pick_bias | 5 |
| C7_doable_in_one_candidate_cycle | 5 |
| C8_safety_template_inheritable_byte_equivalent | 5 |
| **Total** | **28 / 40** |

_Total excludes C4 which is n/a; treated as 0 for scoring comparability_


## Recommendation

**Recommended s8 direction:** **`D1`**
**Recommended candidate id:** `s8-cross-asset-donchian-no-pyramid-nq-gc-zn-cl`

### Rationale
D1 (cross-asset Donchian no-pyramid on s7-D1's NQ+GC+ZN+CL universe) scores 39/40 -- the highest among the 6 directions evaluated. It is the only direction that DIRECTLY tests the load-bearing remaining hypothesis from s7-D1: K4 fired at -221% DD; the proximate cause is pyramid amplification; the direct fix is removing the pyramid (max_units = 1). Every other direction either (a) doesn't address K4 (D4), (b) adds ad-hoc parameter knobs (D2), (c) is a known overfit trap (D5), (d) is premature without D1's answer (D3, D6), or some combination. D1 has zero new data needs, minimal new code surface, strong first-principles motivation, and gives an honest interpretation regardless of outcome:

### Honest interpretation of D1's possible outcomes
- **outcome_1_d1_passes_K1_K2_K4:** Cross-asset trend-following with minimal sizing genuinely works. The s7-D1 problem WAS the pyramid. This is the natural 'graduation candidate' for further research (P6.5c cost-stress matrix, then OOS authorization if operator chooses).
- **outcome_2_d1_passes_K4_but_fires_K1_or_K2:** Removing pyramid removes Faith's alpha-amplification; expectancy collapses below zero or Sharpe goes negative. This decisively falsifies the cross-asset Donchian family: it needs pyramid to be profitable, but pyramid causes catastrophic DD. The family is unsalvageable. PARK_FAMILY_FALSIFIED is the honest disposition. Operator then moves to D3 (different family) as s9.
- **outcome_3_d1_fires_K4_anyway:** Even without pyramid, the cross-asset Donchian signal produces unacceptable DD. The DD problem is intrinsic to the strategy at this universe, not the pyramid mechanic. PARK and move to D3 as s9. (Lower probability outcome; s5 single-market saw -38% DD which is below -50% threshold.)
- **outcome_4_d1_fires_K6_K7_K8_or_safety:** Implementation or chain integrity issue. Diagnose via fail report, do not patch without separate authorization (same discipline as P6 blocked / P6.5 buggy result).

- **D3 is natural s9 direction if D1 parks:** **True**
- **D6 family-level park is premature before D1:** **True**

### Recommended against
- **D5_zn_only:** SEVERE overfit trap: selecting the best-performing market of 4 from a single in-sample run is the textbook cherry-pick. s7 selection plan applied identical reasoning to YM-only and scored it 12/40 with explicit recommendation AGAINST.

## Honest qualifications for operator
- **Current state:** ZERO strategies are money-proven after s2-s7-D1. 6 candidates parked across two universes (1 NKE wheel + 5 trend-following Donchian variants).

### Honest position
After 6 candidates and ~7 months of sealed-chain research, we have produced honest provenance but no money-proven strategy. The s7-D1 result IS the strongest evidence in the chain so far for cross-asset signal viability at the per-trade economics level (the first WR-gap-positive result; the first positive Sharpe + positive expectancy + multi-market positive result). The K4 fire is a sizing-mechanic problem, not a signal problem. D1 (no-pyramid on s7-D1 universe) is the cheapest, most direct test of whether the chain can produce its first money-proven candidate. If D1 passes K1/K2/K4, the chain has its first viable candidate. If D1 fires K1 or K2, the cross-asset Donchian family is decisively falsified and D3 (different family) becomes the right s9 direction.

- **Operator owns final choice:** **True**
- **No recommendation is a profitability claim:** **True**
- **Any s8 candidate requires fresh sealed chain:** **True**
- **Live-promotion path remains closed regardless of recommendation:** **True**

## Required next step
- **Step:** Operator selects ONE direction from D1-D6 and authorizes Tier-N spec DRAFT for that candidate.

**Trigger authorization template (recommended D1):**
```
Authorize Tier-N spec DRAFT for candidate s8-cross-asset-donchian-no-pyramid-nq-gc-zn-cl. Universe: NQ.c.0 + GC.c.0 + ZN.c.0 + CL.c.0 (all CACHED locally, no fetch needed). Strategy: Faith Donchian-55 entry / Donchian-20 exit / 2N stop / 0.5N pyramid spacing / 1% PORTFOLIO equity sizing. NO same-direction filter (AMB6 structurally locked NONE). ONE parameter REDUCTION from s7-D1: max_units_per_market = 1 (NO pyramiding). PLAN ONLY at DRAFT stage; no code; no backtest; no Databento download (cache already complete).
```

**Alternative trigger (D3 path):**
```
Authorize a fresh sub-family selection memo (s9 if you choose to defer D1, or separate s8 if you choose to skip Donchian entirely): operator-specified sub-family among mean reversion / stat arb / carry / volatility carry. Acknowledges D1 is foregone in favor of family-level shift.
```

- **No authorization pre-granted by this plan:** **True**

## Negative invariants (this turn -- all True/pass)
- `selection_plan_only`: `True`
- `no_code_authored`: `True`
- `no_backtest_run`: `True`
- `no_databento_call`: `True`
- `no_data_fetch`: `True`
- `no_qc_call`: `True`
- `no_network_call`: `True`
- `no_oos_inspection`: `True`
- `no_live_trading`: `True`
- `no_paper_trading`: `True`
- `no_obsidian_trade_logger_touch`: `True`
- `no_review_queue_mutation`: `True`
- `no_d5_revived`: `True`
- `no_b005_001_revived`: `True`
- `no_nke_revived`: `True`
- `no_s7_d1_revived`: `True`
- `no_s2_through_s6_revived`: `True`
- `no_committed_file_modified`: `True`
- `no_prior_sealed_artifact_modified`: `True`
- `no_profitability_claim`: `True`
- `no_promotion_to_live`: `True`
- `no_s8_candidate_record_id_reserved`: `True`
- `no_s8_implementation_files_created`: `True`
- `no_s8_tier_n_spec_authored`: `True`
- `no_threshold_loosened`: `True`

## Operator-side state
- `obsidian_trade_logger_unchanged_through_plan`: **True**

## Authorization gates
- s8 selection plan authorizes nothing downstream: **True**
- Any s8 Tier-N spec requires separate operator authorization: **True**
- Any s8 candidate_record_id creation requires separate operator authorization: **True**

## Status fields
- `candidate_operational_status_at_plan`: `S8_SELECTION_PLAN_SEALED_NO_CANDIDATE_INSTANTIATED`
- `frc_granted`: `False`
- `live_promotion_path_closed`: `True`
- `live_status`: `BLOCKED_AT_6_GATES`
- `schema_status`: `SEALED`
- `trading_status`: `PAUSED`
- `backtest_diagnostic_only`: `True`

## Labels
- `EXTERNAL_CLAIM_ONLY`
- `NEEDS_VERIFICATION`
- `NOT_A_SIGNAL`
- `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- `NO_FRC_GRANTED`
- `S8_SELECTION_PLAN_AFTER_SIX_PARKS`
- `SIX_CANDIDATES_S2_S7_D1_DOCUMENTED`
- `SIX_DIRECTIONS_SCORED_D1_D6`
- `RECOMMENDS_D1_CROSS_ASSET_DONCHIAN_NO_PYRAMID`
- `RECOMMENDS_AGAINST_D5_ZN_ONLY_OVERFIT_TRAP`
- `D6_FAMILY_LEVEL_PARK_PREMATURE_BEFORE_D1`
- `D3_NON_DONCHIAN_FAMILY_HELD_AS_NATURAL_S9_IF_D1_PARKS`
- `PLAN_ONLY_NO_CODE_NO_BACKTEST_NO_API`
- `NO_STRATEGY_MONEY_PROVEN_YET_EXPLICITLY_STATED`
- `TRADING_REMAINS_PAUSED`
- `LIVE_REMAINS_BLOCKED_AT_6_GATES`
- `FRC_NEVER_GRANTED`
- `NO_PROFITABILITY_CLAIM`
- `ANY_S8_REQUIRES_FRESH_CANDIDATE_RECORD_ID_AND_FRESH_SEALED_CHAIN`
- `OPERATOR_OWNS_FINAL_S8_DIRECTION_CHOICE`

## Next step
- `operator_authorization_required_for_chosen_direction_among_D1_D6 OR for_alternate_path_to_park_chain`

## Seal block (canonical)
- **`report_seal_sha256`**: `6b7bdb4c350f4a779611546dcb32f6a83db2371c66d7b6ba0118121783801441`
- **`seal_method`**: `sha256 over json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False, default=str) EXCLUDING report_seal_sha256 + seal_method`
- **`schema_id`**: `sparta.external_research_hunter.s8_next_candidate_selection_after_six_parks.v1`
- **`schema_status`**: `SEALED`
- **`report_date_utc`**: `2026-05-25T21:16:22Z`

*End of s8 selection plan after six parks. PLAN ONLY. No code. No backtest. No fetch.
No live promotion. No profitability claim. FRC never granted.*
