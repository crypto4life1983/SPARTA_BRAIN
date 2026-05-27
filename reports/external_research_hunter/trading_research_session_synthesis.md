# Trading Research Session Synthesis (Trading-Bot Tracks Only)

**Schema:** `sparta.trading_research.session_synthesis.v1`
**Phase prefix:** `PHASE2-TRADING-RESEARCH-SESSION-SYNTHESIS`
**Controller session:** THIS SESSION ONLY
**Report kind:** Trading research session synthesis memo for this session's trading-bot tracks only
**Report date (UTC):** 2026-05-27T20:00:00Z
**Authorization:** "Authorize trading research session synthesis and next-direction memo only."

**Scope locked:**

- Trading-bot tracks only.
- Strategy Factory Phase 1: **excluded**.
- Research-OS context: **excluded**.

**Tracks synthesized:**

1. S10-D2 closure + P10.5 OOS cost-stress.
2. S12-D1 full lifecycle + P11 PARK.
3. T1 RSI MNQ + terminal disposition.
4. Parallel s13-d1 coordination + corroborating audit.

---

## 1. Track S10-D2 (cross-asset Donchian no-pyramid reparam-cap; NQ + GC + ZN + CL)

| Field | Value |
|---|---|
| `candidate_record_id` | `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl` |
| Mechanic family | F1 Donchian trend (cross-asset basket) |
| Universe | NQ + GC + ZN + CL |
| P7 decision commit | `b466bbb` |
| P10 OOS gate commit | `15231cb` |
| P10 OOS verdict | `K9_OOS_SUB_THRESHOLD` (53 OOS trades) |
| P10.5 OOS cost-stress commit | `89ca9a7` (seal `2b268b89...`) |
| P10.5 verdict | **`OOS_COST_STRESS_SURVIVES`** |
| P10.5 scope | S0 / S2 / S3 sweep on existing 53-trade OOS sample |
| P10.5 finding | Directional consistency at S1 also holds at S0/S2/S3; does NOT address K9 sample-size finding |
| Lifecycle PARK commit | `b580aed` (seal `8d59e94a...`) |
| Terminal lesson commit | `6895012` (seal `7026b1b5...`) |
| Continuation-track selection plan commit | `c466a96` (seal `c6df16df...`) |
| Continuation selected | s11-D1 / s12-D1 single-instrument MNQ.c.0 line |
| Lifecycle terminal for this candidate id | **TRUE** |

**Key K9 lesson origin:** S10-D2 OOS exposed K9 sample-size insufficiency on a cross-asset Donchian basket. This finding informed the explicit **K9-reachability discipline** introduced later at s12-D1 PLAN.

---

## 2. Track S12-D1 (single-instrument Donchian-15/8 MNQ.c.0; pivot from cross-asset basket)

| Field | Value |
|---|---|
| `candidate_record_id` | `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history` |
| Mechanic family | F1 Donchian trend (single-instrument) |
| Universe | MNQ.c.0 (Databento long history) |
| SEAL commit | `9ce4d66` |
| P1 plan-lock | `bd7245e` |
| P2 phase-2 plan | `2b27acc` |
| P3 BUILD | `b97331a` |
| P4 SMOKE | `8cfdeb1` (15/15 PASS in 0.02s) |
| P6 IS diagnostic (this session) | `8621c32` (seal `b984b85f...`) |
| P6 IS verdict | **`INSUFFICIENT_SAMPLE`** |
| P6 IS closed trades (this session) | **33** |
| P6 IS closed trades (parallel session) | 48 |
| K9 threshold | 100 |
| IS window | 4.6297 years |
| K9 clearance ratio (this session) | 0.33 |
| K9 clearance ratio (parallel session) | 0.48 |
| Dual-implementation corroboration | Both this-session (`8621c32`) and parallel (`9241ed6`) produced sub-K9 trade counts on same audit-clean CSV. The 33 vs 48 numeric difference is implementation-detail variation (entry/exit edge cases); the substantive verdict `INSUFFICIENT_SAMPLE` is the same. |
| P11 PARK commit (this session) | `ce279cf` (seal `321b8940...`) |
| P11 PARK commit (parallel session) | `ecbd001` |
| Park status enum | `PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS` |
| Lifecycle terminal for this candidate id | **TRUE** |

**K9-reachability hypothesis falsified at IS:** PLAN-time conjecture was 80-200 IS trades over 4.6y window. Actual 33-48 trades - well below P2 lower bound of 80. Donchian-15/8 on single futures instrument over 4.6y is **structurally signal-density-limited** for K9=100 clearance.

---

## 3. Track T1 RSI MNQ (this session; substantively identical to parallel s13-d1)

| Field | Value |
|---|---|
| `candidate_record_id` | `t1-rsi-mnq-c0-mean-reversion-2-period-databento-long-history` |
| Mechanic family | F3 RSI mean-reversion (pivot from F1 Donchian after s12-D1 PARK) |
| Universe | MNQ.c.0 |
| PLAN seal | `729207f` (seal `70549a9a...`) |
| DRAFT | `fb1079a` |
| SEAL canonical | `d7fc7f5` (seal `abe9718d...`) |
| Alignment review | `c6bf9ae` (seal `bfd8d23e...`) |
| Alignment verdict | `MATERIALLY_SAME_CANDIDATE`; Option C STRONG |
| P6.5 reproducibility audit | `54873eb` (seal `ff9155f6...`) |
| Audit verdict | **`CORROBORATED (HIGH)`**; S1 byte-reproduces P6 IS sealed metrics across all 6 measured fields |
| Terminal disposition memo | `cba0f47` (seal `3696db51...`) |
| Final disposition | `TERMINAL_DEFER_TO_PARALLEL_CANONICAL_REJECT_FAST_DR10` |
| T1 chain phases executed | **0** (review/verification lane only) |
| T1 chain role | review_and_verification_lane_only |
| Lifecycle terminal for this session's T1 chain | **TRUE** |
| DA-register revisions at SEAL | DA8=B (per-trade risk 0.5%), DA9=B (START_CASH $200,000) |
| DA-register offered but not chosen | DA19=B (DR10 threshold revision to 1.00) |

---

## 4. Track parallel s13-d1 coordination (canonical execution chain for this candidate)

| Field | Value |
|---|---|
| `candidate_record_id` (parallel) | `s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history` |
| Alignment finding | `MATERIALLY_SAME_CANDIDATE` as T1; 25 of 25 substantive parameters IDENTICAL |
| SEAL commit | `262491c` (DR10 v1 canonical source; seal `dbab159f...`) |
| P1 / P2 / P3 BUILD / P4 SMOKE | `005cb8a` / `beecd87` / `24625c6` / `c44fb13` |
| P6 IS commit | `3fa479a` |
| P6 IS verdict | `READY_FOR_LONGER_BACKTEST` |
| P6 IS closed trades | **159** over 4.6297y |
| P6 IS sharpe (proxy) | +0.1076 |
| P6 IS expectancy | +$540.73 |
| P6 IS maxdd | -17.68% |
| P6.5 commit | `15c4fb1` |
| P6.5 verdict | **`REJECT_FAST`** |
| P6.5 DR10 v1 branch fired | `annual_turnover` (84.7851 vs 0.50; **169.6x over**) |
| P6.5 S2_cost_drag | 2.35% (below v1 threshold 5.00%; does NOT fire) |
| P7 decision commit | `cc1817b` (TERMINAL by DR10) |

**This session's coordination outputs** referenced above:

1. Alignment review (Option C STRONG) at `c6bf9ae`.
2. Reproducibility audit (CORROBORATED HIGH) at `54873eb`.
3. Terminal disposition memo at `cba0f47`.

**Cross-chain verdict convergence:** T1 audit (read-only methodology audit) and parallel s13-d1 (executed P6.5) converge on `REJECT_FAST` verdict on the same audit-clean CSV via independent methodologies.

---

## 5. Parallel post-s13-d1 changes (informational only; NOT authorization)

> Treated strictly as cross-chain informational context. Not executed by this session. Not anchored as authorization. Scopes not merged.

### 5.1 `30c836e` — Next-research-track selection plan after s13-d1 terminal

- Authorization phrase (parallel): "Authorize next research-track selection plan after s13-d1 terminal REJECT_FAST by DR10 only."
- Introduces: **DR10-reachability discipline** (parallel of K9-reachability discipline).
- Finding: All 5 candidate tracks T1-T5 (parallel's naming) fail DR10 reachability at PLAN time.
- Primary paths proposed by parallel: T1 cash-equity nano-sizing OR T6 framework SEAL revision.
- **PLAN only.** No execution.

**Naming-collision note:** Parallel's "T1"-"T5" naming is **SEPARATE** from this session's T1 RSI MNQ. They are distinct candidate sets. This session's T1 = `t1-rsi-mnq-c0-mean-reversion-2-period-databento-long-history` (terminal); parallel's "T1" in `30c836e` refers to a hypothetical cash-equity nano-sizing candidate.

### 5.2 `28cbaea` — Framework-level DR10 SEAL revision INVESTIGATION plan

- PLAN only; no SEAL revision performed at this commit.
- Math examples of K9 ∧ DR10 incompatibility at retail-scale.
- 7 governance options A-G with trade-offs; no recommendation.

### 5.3 `78cd22e` — Framework-level DR10 SEAL revision v2 — OR → AND

| Field | Value |
|---|---|
| Seal sha256 | `7794bb5222ed2a2cb1cd8e1ef2f43f3d1abc6f1539d71af31dda32d832b5e907` |
| Revision id | `DR10_V2_AND_CONJUNCTION` |
| DR10 v1 definition | `annual_turnover > 0.50` **OR** `S2_cost_drag > 0.05` (either branch fires) |
| DR10 v2 definition | `annual_turnover > 0.50` **AND** `S2_cost_drag > 0.05` (both branches must fire) |
| Binding scope | new candidate_record_ids authored at or after v2 SEAL |
| Binds s14+ onward only | **TRUE** |
| Retroactive effect on existing sealed candidates | **FALSE** |
| s13-d1 verdict preserved | `REJECT_FAST` under v1 (verbatim) |
| s12-d1 verdict preserved | `PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS` under v1 |
| s10-D2 verdict preserved | `PARKED_LIFECYCLE_TERMINAL` under v1 |
| T1 verdict preserved | `TERMINAL_DEFER_TO_PARALLEL_CANONICAL_REJECT_FAST_DR10` under v1 |
| Existing sealed verdicts preserved byte-equivalent under v1 | **TRUE** |
| Thresholds preserved verbatim from v1 | **TRUE** |

---

## 6. Cross-track lessons

### 6.1 K9-reachability

**Defined as:** At PLAN/SEAL turn, candidate must analyze IS+OOS trade-density and demonstrate K9 (`closed_trades >= 100` per window) is plausibly reachable given mechanic-family signal density on chosen universe.

| Stage | Status |
|---|---|
| Origin | S10-D2 P10 OOS K9 sub-threshold finding |
| Falsified at | s12-D1 P6 IS (33-48 trades vs PLAN 80-200) |
| Carried forward to | T1 + s13-d1 (conjectured 46-68/y; actual 34.4/y) |
| Framework status | discipline now baked into PLAN/SEAL practice |

### 6.2 DR10 turnover risk

| Field | Value |
|---|---|
| Defined as | `turnover_cost_explosion` DR-rule |
| v1 | `annual_turnover > 0.50` **OR** `S2_cost_drag > 0.05` |
| v2 (s14+ only) | `annual_turnover > 0.50` **AND** `S2_cost_drag > 0.05` |
| Exposed at | s13-d1 P6.5 (`annual_turnover` 84.7851 = 169.6x over) |
| Corroborated at | T1 audit `54873eb` (HIGH) |
| Status under v1 | `REJECT_FAST` on s13-d1 stands verbatim |
| Status under v2 | For NEW s14+ candidates only: same metrics would NOT fire DR10 (AND conjunction requires both branches; `S2_cost_drag` still below threshold). Forward-binding only. |

### 6.3 K9 / DR10 structural tension

**Defined as:** For single-instrument per-trade-sized strategies on multi-year windows, K9 and DR10 v1 thresholds form a structural tension.

| Threshold | Demand |
|---|---|
| K9 | MORE trades (>=22/y over 4.6y for 100 over IS) |
| DR10 v1 | LESS turnover (`annual_turnover` < 0.50) |

**Arithmetic at retail scale:**

- $200k equity, 0.5% per-trade risk, MNQ.c.0 per-trade notional ~$75k.
- Max DR10-clearing trades-per-year: **~1.33**.
- K9 minimum: **~22/y** (100 / 4.6).
- **Gap: 16-17x apart.**

**Mathematical consequence:** For single futures instrument at retail scale, K9 and DR10 v1 are **not jointly satisfiable** under conventional sizing. Either drastically reduce per-trade notional, raise DR10 threshold, or pivot universe.

**Framework response:** Parallel investigation plan `28cbaea` formalized this incompatibility; v2 SEAL at `78cd22e` changed the rule from OR to AND, **partially** relieving tension for new candidates by requiring BOTH branches to fire.

| Status | Resolution |
|---|---|
| Under v1 | tension active and documented (existing chains) |
| Under v2 | tension partially relieved for future s14+ candidates only |

### 6.4 Why Donchian variants failed trade density

**Summary:** F1 Donchian trend on liquid futures (cross-asset basket at s10-D2; single-instrument MNQ.c.0 at s12-D1) does not produce sufficient signal density to clear K9.

- **s10-D2 evidence:** Cross-asset Donchian no-pyramid reparam-cap on NQ+GC+ZN+CL produced 53 OOS trades; K9 OOS gating triggered sub-threshold disposition.
- **s12-D1 evidence:** Single-instrument Donchian-15/8 on MNQ.c.0 produced 33-48 IS trades over 4.6297y; conjectured 80-200; falsified at IS.
- **Mechanic property:** Donchian breakout requires extended price-range expansion to trigger entries. On liquid index futures this is structurally infrequent. Reparam-cap (no pyramid) further reduces re-entry opportunities.

**Conclusion:** F1 family is signal-density-limited on liquid futures at the K9=100 threshold. To clear K9, F1 must be paired with high-frequency universes or relaxed cap rules - both of which open separate risks.

### 6.5 Why RSI(2) solved trade density but failed turnover (v1)

**Summary:** F3 RSI(2) bi-directional mean-reversion solved K9 by increasing signal density 4-5x over F1 Donchian, but the same higher density drove `annual_turnover` 169.6x over DR10 v1 threshold.

| Result | Value |
|---|---|
| K9 solved (parallel s13-d1 P6 IS) | 159 closed_trades / 4.6297y = 34.4/y; K9 cleared with 1.59x margin |
| DR10 failed v1 (s13-d1 P6.5) | annual_turnover 84.7851 vs 0.50 v1 threshold = 169.6x over; `REJECT_FAST` |
| F1 vs F3 density swap | F1 Donchian-15/8 ~7-10 trades/year on MNQ.c.0 (below K9); F3 RSI(2) ~34 trades/year (clears K9 but blows past DR10 v1) |

**Load-bearing lesson:** Solving K9 by increasing signal density typically pushes turnover ratio above DR10 v1 threshold for single-instrument per-trade-sized strategies. The **22-vs-1.33 trades-per-year structural gap** means most reasonable mechanic families on single futures at retail scale will land in one of two failure modes under v1: K9 fail (too few trades) OR DR10 fail (too much turnover).

**Partial DR10 v2 relief:** Under v2 (s14+ only) the same s13-d1 metrics would NOT fire DR10 because v2 requires BOTH branches; `S2_cost_drag` 2.35% is still below threshold 5.00%. So under v2, an RSI(2)-like signal density would clear DR10 on cost-drag alone. **But this is forward-binding only**; s13-d1 verdict stands at `REJECT_FAST` under v1.

---

## 7. Posture invariants (held this synthesis turn)

- Trading status: **PAUSED**
- Live status: **BLOCKED_AT_6_GATES**
- FRC granted: **NEVER**
- Advisory label permanent: **DIAGNOSTIC_ONLY_NOT_LIVE_GRADE**
- Verdict never means live ready: **TRUE**
- Live promotion path closed: **TRUE**
- This memo authorizes any phase: **FALSE**

---

## 8. Chain anchors byte-stable

- All s10-D2 sealed artifacts not modified.
- All s12-D1 sealed artifacts not modified.
- All T1 chain artifacts not modified.
- All parallel s13-d1 chain artifacts not modified.
- All parallel post-s13-d1 artifacts (`30c836e`, `28cbaea`, `78cd22e`) not modified.
- DR10 v2 SEAL not modified.
- All other sN-dN sealed artifacts (s7 / s8-d1 / s9 / s10-d1 / s11-d1) not modified.
- Audit-clean CSVs not touched.
- `lessons.md` not touched.
- `decisions.md` not touched.
- `next_actions.md` not touched.
- `system_changes.md` log not touched.

---

## 9. Negative invariants

NO_BUILD. NO_SIMULATOR_RUN. NO_BACKTEST. NO_RSI_COMPUTED. NO_DONCHIAN_COMPUTED. NO_SIGNAL_COMPUTED. NO_DATA_FETCH. NO_DATABENTO_CALL. NO_DATABENTO_API_KEY_ACCESS. NO_EXTERNAL_NETWORK_CALL. NO_REVIEW_QUEUE_MUTATION. NO_IDEA_MEMORY_MUTATION. NO_STRATEGY_LAB_INVOKED. NO_CANDIDATE_PROMOTED. NO_BROKERAGE_CONNECTION. NO_ORDERS_CREATED. NO_PAPER_OR_LIVE_TRADE. NO_S10_D2_CHAIN_MODIFIED. NO_S12_D1_CHAIN_MODIFIED. NO_T1_CHAIN_MODIFIED. NO_PARALLEL_S13_D1_CHAIN_MODIFIED. NO_PARALLEL_POST_S13_D1_ARTIFACTS_MODIFIED. NO_FRAMEWORK_DR10_REVISION_FILES_MODIFIED. NO_CACHE_MODIFICATION. NO_DATA_MODIFICATION. NO_CSV_MODIFICATION. NO_DRIVER_MODIFICATION. NO_TEST_MODIFICATION. NO_STRATEGY_CODE_MODIFICATION. NO_RUNBOOK_MODIFICATION. NO_PIPELINE_MANIFEST_MODIFICATION. NO_DECISIONS_MD_MODIFICATION. NO_LESSONS_MD_MODIFICATION. NO_NEXT_ACTIONS_MD_MODIFICATION. NO_SYSTEM_CHANGES_LOG_MODIFICATION. NO_GITIGNORE_MODIFICATION. NO_CLAUDE_MD_MODIFICATION. NO_BRANCH_CHANGE. NO_GIT_PUSH. NO_FRC_GRANT. NO_LIVE_READINESS_CLAIM. NO_PROFITABILITY_CLAIM. NO_DR_REDEFINITION_POST_SEAL. NO_SELF_AUTHORIZATION_OF_ANY_PHASE. NO_AUTHORIZATION_EXTRACTION_FROM_PARALLEL_POST_S13_D1_ARTIFACTS. NO_SCOPE_MERGE_WITH_PARALLEL_CHAIN. NO_KEY_LEAKAGE.

---

## 10. Validation V-gates

V1 ASCII-only. V2 keyed sections consistent. V3 no execution language. V4 no self-authorization to any phase. V5 no code modification. V6 no backtest run. V7 no simulator run. V8 no signal computation. V9 no RSI computation. V10 no data fetch. V11 no network IO. V12 no live trading. V13 all sealed chains byte-stable at HEAD. V14 lessons.md unstaged and untouched. V15 decisions.md unstaged and untouched. V16 next_actions.md unstaged and untouched. V17 parallel post-s13-d1 referenced as informational only. V18 parallel T1-T5 naming distinction from this session's T1 recorded. V19 DR10 v2 binding scope recorded as s14-forward only. V20 existing chain verdicts recorded as preserved under v1.

---

## 11. Labels

`TRADING_RESEARCH_SESSION_SYNTHESIS_MEMO_COMPLETE`
`TRADING_BOT_TRACKS_SYNTHESIZED`
`S10_D2_PARKED_TERMINAL`
`S12_D1_PARKED_INSUFFICIENT_SAMPLE_TERMINAL`
`T1_TERMINAL_DEFER_TO_PARALLEL_CANONICAL`
`PARALLEL_S13_D1_TERMINAL_REJECT_FAST_DR10_V1`
`K9_REACHABILITY_DISCIPLINE_RECORDED`
`DR10_TURNOVER_RISK_RECORDED`
`K9_DR10_STRUCTURAL_TENSION_RECORDED`
`DONCHIAN_TRADE_DENSITY_INSUFFICIENT_RECORDED`
`RSI2_SOLVED_K9_FAILED_DR10_V1_RECORDED`
`DR10_V2_AND_CONJUNCTION_INFORMATIONAL_ONLY`
`DR10_V2_BINDS_S14_FORWARD_ONLY`
`NO_BUILD`
`NO_SIMULATOR_RUN`
`NO_BACKTEST`
`NO_RSI_COMPUTED`
`NO_DONCHIAN_COMPUTED`
`NO_SIGNAL_COMPUTED`
`NO_DATA_FETCH`
`NO_DATABENTO_CALL`
`NO_DATABENTO_API_KEY_ACCESS`
`NO_REVIEW_QUEUE_MUTATION`
`NO_STRATEGY_LAB_PROMOTION`
`NO_LIVE_TRADING`
`VERDICT_NEVER_MEANS_LIVE_READY`

---

**Seal method:** `sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method`

**Companion JSON:** `trading_research_session_synthesis.json` (carries embedded `companion_md_sha256` and canonical `report_seal_sha256`).
