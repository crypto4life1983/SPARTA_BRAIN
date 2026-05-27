# Next Research-Track Selection Plan -- after s10 D1 MNQ+MGC park

Status: PLAN_ONLY (no track is built or run by this plan; the next track requires its own separately authorized plan-authoring turn).
Authored: 2026-05-27
Predecessor park: s10 D1 MNQ+MGC Databento long-history, parked at `INCONCLUSIVE_HOLD` (DR9 fired on MGC.c.0 continuous-stitch; robust to holiday-aware refinement).
Predecessor park report: `reports/external_research_hunter/s10_d1_mnq_mgc_databento_long_history_park_report.json` (`report_seal_sha256 = 32c1a87146264197fd852e53ba45baf6d6d45e40355b716e5a4d41a08edf1b2f`; commit `1a9acec`)
Strict audit anchor: `reports/external_research_hunter/s10_d1_mnq_mgc_step02c_audit_report.json` (`report_seal_sha256 = fd5cd136891638d2a1338850b616d000b969c7b46ce8c12365ba9498855e5865`; commit `9bdde45`)
Holiday-aware refinement anchor: `reports/external_research_hunter/s10_d1_mnq_mgc_step02c_audit_holiday_aware_report.json` (`report_seal_sha256 = 5f0258117cf35afa17ada593d464a0fc941e87c95bc52b76d54b8d719ee34686`; commit `0e124e3`)
Sealed Tier-N spec (predecessor): `docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec.md` (commit `9040429`)
Sibling selection plan precedents: `docs/next_research_track_selection_plan_after_s7_d1_park.md`, `docs/next_research_track_selection_plan_after_s9_park.md`
T8 ETF-proxy family-level park memo: `reports/external_research_hunter/t8_spy_tlt_gld_uso_2014_2022_family_park_memo.json` (`report_seal_sha256 = 4f375af7a46d059078782ba490a91e80ef3e1329db7fc710b66b67615e2b0b65`)
S10-D1 micro availability probe memo: `reports/external_research_hunter/s10_d1_micro_availability_probe_result_memo.json` (sha256 `76dcb833f89d3044547e0e361e03f39ae325a22a5c9c06baf1ec0f2e9df213fe`)

HARD BOUNDARIES (held by this plan). Plan only. No strategy code. No backtest. No simulator. No new signal computation. No OOS inspection. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No QC / LEAN call. No network IO. No review_queue.json mutation. No production idea_memory mutation. No Strategy Lab run. No candidate promotion. No s10 D1 MNQ+MGC resurrection. No s10 D1 / s9 / s7 D1 / B006_NNN sealed-artifact modification. No ORB branch artifact mutation. No Step 30 cost constant mutation. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No `brain_memory/projects/trading_bot/lessons.md` modification or staging. No branch change. No branch creation. No commit beyond the single new plan file. No git push. No live trading. No profitability claim. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.

----

## 1. Purpose

Author a sealed selection plan for the next trading research track to follow the s10 D1 MNQ+MGC Databento long-history candidate (now terminally parked at `INCONCLUSIVE_HOLD` per commit `1a9acec`). The selection plan does NOT build any track; it surveys what is repo-available, applies the operator's selection criteria, ranks candidate directions, and produces a single recommended next track plus a recommended first step. The chosen track itself requires a fresh separately authorized plan-authoring turn before any code is written.

This selection plan inherits the cumulative findings from four parked tracks:
- s7 D1 ETF-proxy at `REJECT_FAST` (trend-following Donchian on SPY/TLT/GLD/USO; cost-stress destroys S0 edge);
- s9 RSI-2 ETF-proxy at `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` (mean-reversion on same universe; negative S0 edge);
- T8 family-level park (SPY/TLT/GLD/USO 2014-2022 falsified across two orthogonal mechanics; first-principles burden required for any third mechanic on that universe);
- s10 D1 MNQ+MGC at `INCONCLUSIVE_HOLD` (DR9 fired on MGC.c.0 continuous-stitch; MNQ.c.0 clean under both audit variants).

Plus archived single-instrument SPY vol-targeting context:
- B006_001 archived `REQUEST_FULL_PREREGISTRATION_REVIEW` (favorable verdict but no live unlock; LESSON_B006_001_002/003/004);
- B006_002 archived `REJECT_FAST` (DR11 C4-enforcement fired on the same SPY data; LESSON_B006_002_001/002).

The load-bearing forward-looking observation: **MNQ.c.0 passed both s10 D1 audit variants cleanly** -- 0 calendar gaps > 5 days; 0 consecutive abs-log-return violations; max single-day abs-log-return 0.1164; `is_pct_observed = 1.2365`. The MNQ-clean-leg finding is preserved by the s10 D1 park report (section 4.1) for any future fresh-candidate-id selection. **MGC.c.0 is not.**

## 2. Current terminal state of s10 D1 MNQ+MGC

The s10 D1 MNQ+MGC Databento long-history candidate is FORMALLY PARKED:

- `candidate_record_id`: `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history`
- terminal_verdict: `INCONCLUSIVE_HOLD`
- park_report_commit: `1a9acec`
- chain_commits: 9 commits ending at the park (`2ec9330 → 5c13821 → a95d7f0 → 9040429 → a8df18b → 0736976 → off-controller-fetch → 9bdde45 → 0e124e3 → 1a9acec`)
- driver: DR9 `mnq_mgc_data_continuity_integrity_check` fired on MGC.c.0's `missing_observations` criterion
- audit cross-evidence: strict audit and holiday-aware refinement both returned DR9 fire on MGC; 1 of 8 strict gaps reclassified as Juneteenth-explained, but 7 remaining gaps clustered in mid-August + mid-October across multiple years with one 17-day October 2022 anomaly are NOT holiday-explainable
- MNQ.c.0: clean under both variants (0 gaps; max abs-log-return 0.1164; pct_observed 1.2365)
- MGC.c.0: structural fire (8 gaps strict; 7 holiday-aware; 17-day October 2022 gap anomalous)
- OOS: never inspected; structurally blocked per sealed-spec invariant
- Strategy Lab: untouched
- review_queue.json: untouched
- broker: not connected
- live trading: BLOCKED at six gates
- advisory_label_permanent: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- `DO_NOT_RESCUE_THIS_SPEC = True`
- `NO_SUBSTITUTION_OF_MCL_OR_OTHER_SYMBOL_INTO_THIS_CANDIDATE = True` (universe was LOCKED at SEAL; any symbol swap requires a fresh candidate id, NOT a revision)
- `MNQ_C_0_CLEAN_LEG_FINDING_PRESERVED_FOR_FUTURE_FRESH_CANDIDATES = True`

## 3. Lessons inherited from s10 D1 MNQ+MGC

The next track MAY inherit (and SHOULD where applicable):

- **MNQ.c.0 daily-bar coverage on `GLBX.MDP3 ohlcv-1d stype_in=continuous` is data-quality clean over 2019-05-13 to 2025-12-30.** Anchor sha pin: `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`. 2,066 rows; 0 gaps > 5 days; max single-day abs-log-return 0.1164. A future candidate that reuses MNQ.c.0 inherits this finding without re-fetching.
- **The Step 02b Databento operator-side fetch script + runbook + patch (`a8df18b → 0736976`) are reusable byte-equivalent for any future candidate that needs a Databento fetch.** The DataFrame-normalization patch (`_normalize_dbn_dataframe`) handles the index-as-ts_event case; the deprecation fix (`datetime.now(timezone.utc)`) is in. Future fetches reuse this template.
- **The Step 02c audit framework (strict + holiday-aware variants; commits `9bdde45` and `0e124e3`) is reusable byte-equivalent for any future Databento candidate.** DR9 thresholds and the calendar-gap heuristic are encoded; the holiday list spans 2019-2023 (can be extended).
- **The Tier-N spec template (`9040429`) is reusable as a sealed-spec template.** F1 long+short bi-directional Donchian / no pyramid / ATR stop / per-trade risk = 1% / no leverage / no rate-targeting is a clean template for futures candidates.
- **The S10-D1 micro availability probe memo (`76dcb833…3fe`) is reusable for any future micro-futures universe selection.** It documents MNQ.c.0 (clean from 2019), MGC.c.0 (clean from 2019 but DR9-failing on continuous-stitch), MCL.c.0 (unreliable before 2021-07). It does NOT document M2K.c.0, MES.c.0, MNG.c.0, MHG.c.0, MBT.c.0, M6E.c.0, MYM.c.0 -- those would need fresh probes if any are candidates.
- **The 19-RUNTIME_INVARIANTS at SEAL set (7 B005_NNN + 4 B006_001 + 3 B006_002 + 5 s10-D1-specific) is reusable byte-equivalent.** The 5 s10-D1-specific invariants (`no_continuous_roll_stitch_modification_post_seal`, `no_mcl_inclusion_under_long_history_scope`, `no_intraday_schema_ingest_under_daily_only_design`, `databento_api_key_read_from_env_only_never_logged_or_saved`, `no_pyramid_per_signal`) generalize cleanly to other Databento-track candidates.

## 4. Lessons NOT inherited from s10 D1 MNQ+MGC

The next track must NOT inherit (and SHALL refuse to inherit):

- **MGC.c.0 in any 2-symbol or wider-basket candidate over the 2019-2023 IS window** on the `GLBX.MDP3 ohlcv-1d stype_in=continuous` schema. The DR9 fire is robust to refinement; the issue is structural to MGC's Databento continuous-front-month stitch. A future candidate that uses MGC requires either a different schema (`ohlcv-1m`?), a different vendor (operator-side authorization required), or a documented heuristic that the operator decides is the right post-park interpretation. None of these are pre-authorized.
- **Any rebadging of s10 D1 with relaxed DR9 thresholds.** The spec threshold-lock invariant (`no_dr_redefinition_post_seal = True`) forbids loosening `DR9_MAX_MISSING_OBSERVATIONS = 5`. A "tightened DR9" variant requires its own `_revN_` spec; a "loosened DR9" variant is forbidden outright.
- **Any silent re-introduction of MCL.c.0 into a long-history micro-futures basket**. The S10-D1 memo documented MCL as unreliable before 2021-07; reintroducing it without a fresh probe and explicit operator authorization repeats the family-level mistake.
- **The 2-symbol-futures-basket structure with MNQ + correlated-equity-micro** (e.g., MNQ + MES, MNQ + M2K, MNQ + MYM). All four micros (MNQ, MES, M2K, MYM) launched May 2019 and are highly correlated US equity indices; a basket of two equity micros provides essentially no diversification claim (`effective_independent_bets` likely below 1.5).
- **Single-asset-bears-loss outcomes.** s9 demonstrated USO carrying -$1177 of -$1335 portfolio net; s7 D1 demonstrated USO carrying +$96k of the portfolio's only positive contribution. A future 2-symbol-or-wider candidate that anticipates one-asset dominance reproduces both s7 D1 and s9 pathologies.
- **Implicit assumption that fetching more data will rescue MGC.c.0**. The audit findings are about MGC's continuous-stitch structure on `GLBX.MDP3 ohlcv-1d stype_in=continuous`, not about an insufficient ingest window.

## 5. Candidate-track selection criteria (positive)

A candidate track is acceptable iff it satisfies ALL of:

C1. **Uses existing clean data or low-friction data.** The MNQ.c.0 CSV (sha `8b7b832c…fa23e`) is already on disk and audit-clean. SPY/TLT/GLD/USO ETF CSVs are already on disk per s7 D1 (universe is family-parked; subject to T8 first-principles burden). Any additional data requires its own separately authorized fetch turn.

C2. **Has enough trade count to clear K9.** Expected `total_closed_trades >= 100` over the in-sample window. Tracks with sparse trade generation (<100 expected) require justification.

C3. **Does not rely on one asset carrying all profit or all loss.** Per-symbol contribution distribution shall be a first-class diagnostic.

C4. **Has explicit cost-stress testing from the beginning.** S0/S1/S2/S3 cost-stress matrix locked in the first IS run.

C5. **Either** (a) does NOT operate on the SPY/TLT/GLD/USO 2014-2022 universe; or (b) operates on it but explicitly satisfies the T8 family-park first-principles burden (must address BOTH s7 D1 cost-stress sensitivity AND s9 negative-S0 edge with falsifiable rationale).

C6. **First-principles rationale.** The candidate shall have a stated reason WHY it might survive where the four prior parked tracks did not. Not "it's worth trying" but a concrete falsifiable hypothesis.

C7. **One-cycle scope.** Doable in a single plan → build → seal → verdict cycle.

C8. **Inheritable safety template.** Phase 2 safety C1-C8 + the 19-RUNTIME_INVARIANTS set inheritable byte-equivalent.

## 6. Reject-fast criteria for next track (negative)

A candidate track is REJECTED FAST in this selection plan iff ANY of:

R1. Track rebadges s10 D1 MNQ+MGC, s9, s7 D1, B006_001, or B006_002.
R2. Track requires loosening any K-threshold, A-gate threshold, or DR threshold.
R3. Track requires expensive data before a cheap diagnostic could be run.
R4. Track requires live trading or brokerage connection to evaluate.
R5. Track requires Strategy Lab promotion to evaluate.
R6. Track has structural sample-size bottleneck (expected closed trades < 100).
R7. Track silently re-introduces a filter, regime gate, or selection rule that a prior parked spec locked to NONE.
R8. Track operates on the SPY/TLT/GLD/USO 2014-2022 universe without satisfying the T8 family-park first-principles burden (per family-park memo section 5).
R9. Track depends on a survivorship-cherry-pick selection rule.
R10. Track conflates diversification with edge.
R11. Track includes MGC.c.0 in any 2-symbol-or-wider basket over the 2019-2023 IS window under `GLBX.MDP3 ohlcv-1d stype_in=continuous` (the DR9 fire is structural; not retryable on the same data scope).
R12. Track includes MCL.c.0 without a fresh availability probe authorized under separate turn.
R13. Track pairs MNQ with another US equity micro (MES, M2K, MYM) and claims cross-asset diversification (R10 applies; these are all highly correlated US equity indices).

## 7. Data availability criteria

Preferred data sources (in priority order):

D1. **Sealed MNQ.c.0 daily CSV at `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv`** (sha `8b7b832c…fa23e`; 2066 rows; 2019-05-13 to 2025-12-29). Audit-clean. Zero new fetch needed. **Strongly preferred for any MNQ-only or MNQ-anchored candidate.**

D2. **Sealed s7 D1 ETF-proxy CSVs at `data/s7_d1_cross_asset_donchian/raw/*.csv`**. Audit-clean (s7 D1 Step 02c PASS). Zero new fetch needed. **Subject to T8 family-park first-principles burden** if used for any new candidate.

D3. **Separately authorized fresh Databento ingest for an alternate micro symbol** (e.g., M2K.c.0, MES.c.0, MNG.c.0, MHG.c.0, MBT.c.0, M6E.c.0, MYM.c.0). Requires fresh S10-D1-style availability probe AND fresh Step 02b operator-side fetch. Higher friction.

D4. **Separately authorized fresh yfinance ingest for expanded ETF universe** (sector / international / single-name). Requires fresh Step 02b-equivalent operator-side fetch. Higher friction.

DR_REJECTED_FOR_THIS_TRACK. Any candidate requiring expensive new data before a cheap diagnostic could be run.

## 8. Cost-stress + S0 edge pre-registration requirements

Every candidate track shall:

CS1. Define its cost model in the Tier-N spec at locking time (per-share for ETFs; per-contract for futures with tick-based slippage).
CS2. Run the full S0/S1/S2/S3 cost-stress matrix in the first IS diagnostic.
CS3. Evaluate DR2 (S2/S3 material degradation), DR3 (zero-cost-only survival), DR5 (tier flip), K1 (Sharpe<0 at S1), K2 (expectancy<=0 at S1).
CS4. Pre-register the expected S0 edge sign and magnitude at SEAL time (lesson from s9: a strategy that loses money at S0 is structurally weak; lesson from B006_002: favorable economic numbers do not override fail-closed verdicts by design).

## 9. Diversification expectations

Every candidate track shall:

DV1. Operate on at least 2 distinct asset families OR be explicitly a single-instrument diagnostic justified by first-principles.
DV2. Measure per-symbol contribution to portfolio PnL AND per-symbol contribution to portfolio loss.
DV3. Compute and report `avg_pairwise_dependence_measure` and `effective_independent_bets` if multi-symbol. For single-instrument candidates, these are trivially 0 and 1 respectively and the diagnostic instead reports the candidate's standalone risk profile.
DV4. Explicitly disclaim that diversification independence does NOT imply positive edge (lesson from s9; LESSON_B006_002_002 reinforces).

## 10. Sample-size requirements

SS1. Expected `total_closed_trades >= 100` across the IS window.
SS2. s9 (414 trades on RSI-2 high-frequency mean-reversion) and s7 D1 (37 trades on Donchian-55 low-frequency trend) bracket the trade-count spectrum; future tracks should target the upper end where possible.
SS3. Per-symbol minimum: at least 30 closed trades per symbol over IS for 2-symbol baskets (carried from s10 D1 sealed spec); >=100 for single-instrument candidates.
SS4. Tracks anticipating <100 portfolio trades require explicit justification.

## 11. OOS-locking policy (inherited unchanged from sealed-spec lineage)

OL1. OOS data shall not be inspected, computed against, simulated over, or queried during the in-sample diagnostic phase.
OL2. Post-OOS data is informational only.
OL3. OOS inspection requires a separately authorized turn after IS verdict `ELIGIBLE_FOR_OOS` plus explicit operator approval.
OL4. Loader / validator / signal / simulator / aggregator modules shall structurally enforce IS-only computation.

## 12. No-live / no-Strategy-Lab / no-brokerage policy (inherited unchanged)

NL1. No live trading authorization conferred by any IS verdict.
NL2. No Strategy Lab promotion conferred by any IS verdict.
NL3. No brokerage connection conferred by any IS verdict.
NL4. No review_queue.json mutation.
NL5. No production idea_memory mutation.
NL6. No paper-trade loop, no scheduler integration, no autopilot, no FRC gate touch.
NL7. Six live-trading gates remain BLOCKED regardless of verdict.
NL8. `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` advisory label is the default for every park-class verdict.

## 13. Candidate ranking rubric

Each candidate is scored 0-5 against 10 criteria (50 max):

- **R1_addresses_prior_failure_modes:** 5 = directly addresses the four prior parked failures (s7 D1 cost-stress, s9 negative-S0, T8 universe-falsification, s10 D1 MGC continuous-stitch); 0 = doesn't address.
- **R2_uses_existing_clean_data_or_low_friction:** 5 = reuses sealed CSV as-is with zero fetch; 3 = one targeted probe / fetch; 1 = expensive new ingest.
- **R3_clears_K9:** 5 = expected >> 100 trades; 3 = expected ~100-200; 1 = expected < 100.
- **R4_per_symbol_contribution_balance:** 5 = expected balanced or single-instrument with no asset-dominance pathology; 3 = some concentration risk; 0 = expected one-asset dominance.
- **R5_built_in_cost_stress_plus_s0_pre_registration:** 5 = full S0/S1/S2/S3 + pre-registered S0 edge sign and magnitude; 3 = cost-stress framework reusable but no pre-registration; 0 = no edge claim.
- **R6_first_principles_rationale:** 5 = strong, falsifiable, ties to ALL four prior parked tracks; 1 = ad hoc.
- **R7_different_family_or_diff_universe:** 5 = mechanic family or universe structurally different from all four parks; 3 = same family but different universe; 0 = pure rebadge.
- **R8_one_cycle_scope:** 5 = clearly doable; 1 = scope-creep risk.
- **R9_safety_template_inheritable:** 5 = inherits byte-equivalent; 1 = needs adaptation.
- **R10_explicit_oos_blocked:** 5 = OOS structurally blocked by design; 1 = needs extra plumbing.

Total >= 40 acceptable; >= 45 recommended.

## 14. Possible next tracks discovered from the repo

T1. **MNQ.c.0-only single-instrument candidate on the existing audit-clean CSV.** Universe = `{MNQ.c.0}`. Data reuse with zero fetch. Mechanic family chosen by operator at fresh Tier-N DRAFT (could be F1 trend-no-pyramid from s10 D1 carried byte-equivalent, OR vol-targeting parallel to B006_001/B006_002 lineage but on MNQ futures, OR RSI mean-reversion as the s9 analog on a non-falsified universe).

T2. **MNQ.c.0 + alternate non-equity micro futures basket.** Universe = `{MNQ.c.0, M*.c.0}` where M* is a non-equity micro NOT yet rejected by S10-D1. Candidates for the second symbol: MNG.c.0 (Micro Henry Hub natural gas), MHG.c.0 (Micro Copper), MBT.c.0 (Micro Bitcoin -- different vol profile entirely; may not fit). Requires fresh S10-D1-style availability probe under separate authorization.

T3. **Sector-ETF universe (XLE / XLF / XLK / XLV / XLU / XLI / XLB / XLP / XLY / XLRE / XLC).** Different universe from SPY/TLT/GLD/USO; T8 family-park does NOT apply. Requires fresh yfinance Step 02b ingest.

T4. **International ETF universe (EFA / EEM / EWJ / VEU / VWO).** Same comments as T3.

T5. **Mixed-asset ETF universe expansion (IWM / DBC / AGG added to SPY/TLT/GLD/USO).** Subject to T8 family-park IF retaining the SPY/TLT/GLD/USO core; would need to satisfy first-principles burden.

T6. **Single-name equity candidate** (e.g., revisit NKE under fresh spec or pick top-N S&P names). Higher data-friction; defer.

T7. **Mixed micro+equity-index futures basket** (MNQ.c.0 + ES.c.0 standard front-month). Mixes contract size scales; needs careful sizing. Defer; speculative.

T8. **Pivot to a completely different mechanic family on MNQ-only** (carry / term-structure / volatility surface). Speculative; data scope larger than ohlcv-1d.

T9. **Defer trading-bot work entirely** (operator-directed pause).

## 15. Recommended next track

**Recommendation:** **T1 -- MNQ.c.0-only single-instrument candidate on the existing audit-clean CSV.**

Proposed `candidate_record_id`: `s11-d1-mnq-c0-single-instrument-databento-long-history` (sequential to s10 D1; deliberately NOT s10-revN because s10 D1 is `DO_NOT_RESCUE_THIS_SPEC`; deliberately on MNQ.c.0 only because the audit-clean leg is preserved and reusable with zero fetch friction).

Scoring against section 13 rubric:

| Criterion | Score |
|---|---:|
| R1_addresses_prior_failure_modes | 5 (no MGC continuous-stitch issue; no T8 universe-falsification; structurally different from s7 D1 and s9 single-mechanic on ETF basket) |
| R2_uses_existing_clean_data_or_low_friction | 5 (reuses sealed MNQ.c.0 CSV byte-equivalent; zero new fetch) |
| R3_clears_K9 | 4 (depends on mechanic family chosen at Tier-N DRAFT; daily-bar trend on 1 symbol over ~6.6 years can produce 50-150 trades; daily RSI mean-reversion can produce 200+; vol-targeting monthly rebal produces ~12/year -> 80; mechanic-family choice matters here) |
| R4_per_symbol_contribution_balance | 5 (single-instrument; no asset-dominance pathology possible; per-instrument profile is the entire diagnostic) |
| R5_built_in_cost_stress_plus_s0_pre_registration | 5 (carry s10 D1 cost-stress matrix S0/S1/S2/S3 byte-equivalent; operator pre-registers S0 edge sign at SEAL) |
| R6_first_principles_rationale | 4 (MNQ.c.0 is data-clean and is a different asset class from the parked ETF-proxy universe; single-instrument scope avoids per-symbol-dominance pathology; B006_001/B006_002 lineage on SPY-only vol-targeting taught lessons that apply on the futures side too) |
| R7_different_family_or_diff_universe | 5 (different universe from s7 D1 / s9; structurally different from s10 D1 MNQ+MGC because single-instrument; not a B006_001/B006_002 revision because the underlying instrument is MNQ futures, not SPY equity ETF) |
| R8_one_cycle_scope | 5 (zero fetch friction; one Tier-N spec; one runner build; one IS run; one verdict) |
| R9_safety_template_inheritable | 5 (Phase 2 safety + 19-RUNTIME_INVARIANTS inheritable byte-equivalent with single-instrument adaptation) |
| R10_explicit_oos_blocked | 5 (OOS structurally blocked; carry s10 D1 invariant) |
| **Total** | **48 / 50** |

## 16. Why that track is next (rationale)

**The s10 D1 park preserved exactly one structurally-useful finding: MNQ.c.0 is data-clean on Databento `GLBX.MDP3 ohlcv-1d stype_in=continuous` over 2019-2025.** The CSV is already on disk with sha-pin and full audit clearance. Zero new fetch is needed. The fastest forward path that respects all four prior parks is to anchor a fresh candidate on MNQ.c.0 alone and choose a mechanic family at fresh Tier-N DRAFT.

- **It addresses the s10 D1 failure mode** because MGC is not in the universe.
- **It avoids the T8 family-park** because the universe is not SPY/TLT/GLD/USO 2014-2022.
- **It avoids the s7 D1 cost-stress sensitivity** because the operator at fresh Tier-N DRAFT can choose either (a) F1 trend-no-pyramid (different cost structure than ETF Donchian-with-pyramid; was the s10 D1 mechanic on MNQ which never reached signal phase due to MGC's DR9 fire), or (b) vol-targeting parallel to B006_001/B006_002 but on MNQ futures (different cost structure than SPY ETF; the C4 leverage-cap-bound DR11 lesson applies and may inform threshold choice).
- **It avoids the s9 negative-S0 edge** because the operator can pre-register an S0 edge sign claim at SEAL and the diagnostic falsifies it cleanly if wrong.
- **It avoids the B006_001/B006_002 SPY vol-targeting C4-binding pattern** if the operator chooses a mechanic family other than vol-targeting OR adjusts the leverage cap such that DR11 cannot be a structural verdict driver on MNQ futures.
- **Single-instrument scope eliminates per-symbol-dominance pathology** by construction. The s7 D1 (USO carries +$96k) and s9 (USO carries -$1177) pathologies cannot recur in a 1-symbol design.
- **Zero data-fetch friction** means the next cycle is short. Step 02b is essentially "no-op; reuse existing MNQ CSV" with a fresh manifest cross-link. Step 02c re-validates the existing CSV (we already know it's clean from the s10 D1 audits).

**Why NOT T2 (MNQ + alternate non-equity micro):** requires a fresh S10-D1-style availability probe for the second symbol (MNG / MHG / MBT). Probe cycle adds friction. If the second symbol fails availability or fails DR9, the candidate is parked at the audit phase with the same data-availability finding pattern as s10 D1. Defer to a future cycle after T1 produces a verdict.

**Why NOT T3 (sector ETF universe):** requires fresh yfinance Step 02b ingest (cost: time + friction). Universe size of 9-11 sector SPDRs introduces basket-management complexity. Defer.

**Why NOT T4 (international ETF universe):** same friction profile as T3; defer.

**Why NOT T5 (mixed-asset ETF expansion of SPY/TLT/GLD/USO):** subject to T8 family-park first-principles burden if retaining the parked core. Cleaner to move off entirely than to satisfy the burden.

**Why NOT T6 (single-name equity candidate):** highest data-fetch friction; per-share commission scaling differs from ETFs and futures; deferred to a future cycle.

**Why NOT T7 (mixed micro+standard-size futures basket):** speculative; contract size mismatch; defer until T1 produces a verdict.

**Why NOT T8 (pivot to carry / term-structure mechanic on MNQ-only):** requires data beyond `ohlcv-1d` (basis / next-month contract); larger data scope; defer to a future Tier-N cycle.

**Why NOT T9 (defer trading-bot work entirely):** the framework has clean forward momentum if T1 is authorized; deferral is the right move only if the operator wants to consolidate without extending.

## 17. First step of the recommended next track

The first step is to author the **Tier-N specification plan** for `s11-d1-mnq-c0-single-instrument-databento-long-history` under a separately authorized turn (mirroring how s10 D1 began with the Tier-N spec plan in `5c13821`). The first-step plan shall include:

FS1. A fresh `candidate_record_id` distinct from any parked predecessor. Proposed: `s11-d1-mnq-c0-single-instrument-databento-long-history`.

FS2. The locked universe: **`{MNQ.c.0}`** only. NO second symbol. NO substitution clause. NO universe widening at any later phase.

FS3. The locked data scope: byte-equivalent to s10 D1 -- `GLBX.MDP3` / `ohlcv-1d` / `stype_in=continuous` / IS `2019-05-13 → 2023-12-29` / OOS `2024-01-02 → 2025-12-30`. Sealed MNQ.c.0 CSV at `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` (sha `8b7b832c…fa23e`) is reused byte-equivalent; no fresh Databento call required. Step 02b for this candidate is essentially a manifest cross-link plus per-candidate audit attestation.

FS4. A locked mechanic-family selection (DRAFT-time ambiguity to be resolved by operator at SEAL): F1 long+short bi-directional Donchian-N entry / Donchian-M exit / no pyramid / ATR(P) stop (carried byte-equivalent from s10 D1), OR F2 vol-targeting (parallel to B006_002 with C4 enforcement carried byte-equivalent), OR F3 RSI mean-reversion (analog of s9 on a non-falsified universe), OR F4 other. Default at DRAFT: F1.

FS5. A locked cost model + sizing rule (futures-specific; carried byte-equivalent from s10 D1 with single-instrument adaptation): MNQ tick=0.25 / $0.50 per tick; S0/S1/S2/S3 cost-stress matrix; single contract per signal (no pyramid); per-trade risk = 1% portfolio equity sized to ATR stop.

FS6. A locked DR rule set: DR1, DR2, DR3, DR4, DR5, DR6 (post-warmup REJECT_FAST), DR7, DR8 (LiveMode refusal), DR9 (MNQ-only continuity check; thresholds carried from s10 D1; the MGC.c.0 DR9-fire is structurally absent because MGC is not in the universe), DR10. DR11 carried iff mechanic family is F2 vol-targeting; absent otherwise.

FS7. A locked acceptance gate set: A1 (>=100 trades) / A2 (S1 Sharpe > 0) / A3 (S1 expectancy > $0) / A4 (MaxDD <= 30%) / A5 (informational only for single-instrument) / A6 (upstream PASS) / A7 (NOT APPLICABLE for single-instrument; effective_independent_bets is trivially 1) / A8 (cost-stress complete) / A9 (Phase 2 safety C1-C8) / A10 (cap_binding count = 0 if not vol-targeted).

FS8. A locked K-gate set: K1, K2, K4, K6 (informational for single-instrument), K7, K8, K9, K10 (NOT APPLICABLE for single-instrument), K11 (iff vol-targeted), K12.

FS9. A locked OOS-blocking structural enforcement plan.

FS10. A planned protocol step sequence: Step 02b (operator manifest cross-link; no fresh Databento call), Step 02c (MNQ-only audit re-confirmation), Step 03 (loader; may inherit byte-equivalent from s10 D1 loader if implemented), Step 04 (validator), Step 05 (NEW signal module for the chosen mechanic family), Step 06 (simulator), Step 07 (aggregator), Step 08 (IS decision memo + park or eligibility).

The first-step plan is NOT authored by THIS selection plan; it requires a fresh operator authorization turn.

## 18. Files that may be created later (by future authorized turns; NOT this turn)

If the recommended next track is authorized in a subsequent turn, the following file paths MAY be created by future build phases (each requires its own separate authorization):

- `docs/s11_d1_mnq_c0_single_instrument_databento_long_history_tier_n_spec_plan.md` (Tier-N spec PLAN)
- `docs/s11_d1_mnq_c0_single_instrument_databento_long_history_tier_n_spec_DRAFT.md`
- `docs/s11_d1_mnq_c0_single_instrument_databento_long_history_tier_n_spec.md` (SEAL)
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_loader/`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_validator/`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_signal/`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_simulator/`
- `external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_aggregator/`
- `tests/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_*/`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_step_*_build_report.{json,md}`
- `reports/external_research_hunter/s11_d1_mnq_c0_single_instrument_databento_long_history_is_decision_memo.{json,md}` OR park report

Naming, ordering, and exact paths are determined by the first-step plan turn.

## 19. Files that must not be touched (this turn or any onward turn outside its own scope)

Permanently off-limits unless an explicitly authorized turn names the specific file as its target:

- All s10 D1 MNQ+MGC artifacts (`reports/external_research_hunter/s10_d1_*`, `tools/operator_side/s10_d1_mnq_mgc_step02b_*.py`, `tools/operator_side/s10_d1_mnq_mgc_step02c_*.py`, `docs/s10_d1_mnq_mgc_databento_long_history_*.md`, raw CSVs in `data/s10_d1_mnq_mgc_databento_long_history/raw/`).
- All s9 RSI-2 ETF-proxy artifacts.
- All s7 D1 ETF-proxy artifacts.
- All B006_001 and B006_002 sealed lifecycle artifacts.
- The T8 ETF-proxy family-level park memo.
- The S10-D1 micro availability probe memo.
- `docs/next_research_track_selection_plan_after_s7_d1_park.md`, `docs/next_research_track_selection_plan_after_s9_park.md`.
- The brain_memory lessons appended at commits `c6730d2` (s7 D1) and `efa3076` (s9). The existing entries shall NOT be modified or rewritten.
- The brain_memory unstaged dirty state of `lessons.md` from prior controller-session appends shall remain dirty in the working tree; this turn does NOT stage them. Future commit hygiene is a separate authorization.
- `review_queue.json`, production `idea_memory` directory, all Strategy Lab artifacts.
- All ORB branch artifacts and Step 30 cost constants.
- `CLAUDE.md`, `docs/decisions.md` (if exists), `RUNBOOK`, `pipeline_manifest`, `.gitignore`.

## 20. Validation gates and HALT conditions for this selection plan

Validation gates the plan-authoring turn satisfies:

V1. ASCII-only.
V2. Numbered sections in monotonic order (1..21).
V3. No execution language.
V4. No self-authorization (this plan does NOT authorize the recommended track to be built; only a separate operator turn does that).
V5. No code modification.
V6. No backtest / simulator / signal computation.
V7. No data fetch / Databento call / DATABENTO_API_KEY access.
V8. No network IO.
V9. No live trading.
V10. No prior-phase artifact modification.
V11. The committed plan file is the ONLY file changed in this turn's commit.
V12. The brain_memory dirty `lessons.md` remains UNSTAGED and UNTOUCHED.
V13. Recommended track is NOT a revision of any parked candidate.
V14. Recommended track is NOT MNQ+MGC again (per operator's explicit prohibition).

HALT conditions:

H1. If any V-gate fails, the turn HALTs.
H2. If pre-stage git index is non-empty, the turn HALTs and remediates by unstaging contaminants.
H3. If staged file count is anything other than 1 at commit time, the turn HALTs.
H4. If the staged file is anything other than `docs/next_research_track_selection_plan_after_s10_d1_park.md`, the turn HALTs.
H5. If `lessons.md` is accidentally staged, the turn HALTs and `git restore --staged brain_memory/projects/trading_bot/lessons.md` before retrying.

## 21. Next authorization language

A future operator authorization is required to proceed beyond this selection plan. That authorization shall reference this plan by exact path:

`docs/next_research_track_selection_plan_after_s10_d1_park.md`

The next operator authorization in the established controller-session pattern shall use one of these scopes:

- **"Authorize s11 D1 MNQ.c.0 single-instrument Databento long-history Tier-N specification plan only"** -- accept the T1 recommendation and begin the Tier-N spec PLAN authoring turn.
- **"Authorize alternative track selection plan revision only"** -- reject T1 and ask for a different recommendation among T2-T9.
- **"Authorize S10-D2 alternate non-equity micro availability probe only"** -- if the operator wants to pursue T2 (MNQ + alternate non-equity micro) and needs availability evidence on MNG / MHG / MBT before committing.
- **"Authorize cross-domain pivot only"** -- if the operator pivots to a different project entirely.

This selection plan is the source of truth for the four authorized next-step options after s10 D1 MNQ+MGC park. Authorizing anything else requires either a fresh selection-plan revision or an out-of-band justification.

No phase of this chain confers any standing authorization for live trading, brokerage connection, Strategy Lab promotion, OOS inspection, or production candidate registration. Each remains BLOCKED at separate plans. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.

----

End of plan. Plan-authoring turn only. No code. No backtest. No simulator. No signal. No data fetch. No yfinance. No Yahoo Finance. No Databento. No DATABENTO_API_KEY access. No QC. No LEAN. No brokerage. No real order. No paper order. No Strategy Lab promotion. No review_queue mutation. No production idea_memory mutation. No ORB branch mutation. No lessons.md modification or staging. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.
