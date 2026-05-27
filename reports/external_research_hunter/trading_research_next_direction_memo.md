# Trading Research Next-Direction Memo (Advisory-Only Enumeration)

**Schema:** `sparta.trading_research.next_direction_memo.v1`
**Phase prefix:** `PHASE2-TRADING-RESEARCH-NEXT-DIRECTION`
**Controller session:** THIS SESSION ONLY
**Report kind:** Trading research next-direction advisory-only enumeration
**Report date (UTC):** 2026-05-27T20:05:00Z
**Authorization:** "Authorize trading research session synthesis and next-direction memo only."

**Scope locked:**

- Trading-bot tracks only.
- Strategy Factory Phase 1: excluded.
- Research-OS context: excluded.
- Advisory-only enumeration.
- **No recommendation. No ranking. No primary designation.**

**Companion synthesis memo:** `reports/external_research_hunter/trading_research_session_synthesis.json`

---

## 1. Framework version context

| Population | Evaluated under |
|---|---|
| Existing sealed chains (s10-D2, s12-D1, T1, parallel s13-d1) | **v1** |
| New s14+ candidates | **v2** |

| Rule | Definition |
|---|---|
| DR10 v1 | `annual_turnover > 0.50` **OR** `S2_cost_drag > 0.05` (either branch fires) |
| DR10 v2 | `annual_turnover > 0.50` **AND** `S2_cost_drag > 0.05` (both branches must fire) |

- v2 binds s14+ forward only: **TRUE**
- v2 retroactive effect on existing sealed candidates: **FALSE**
- v1 → v2 change does NOT revive s13-d1 or T1 lifecycles: **TRUE**

---

## 2. K9 / DR10 reachability baseline arithmetic

| Field | Value |
|---|---|
| K9 threshold | 100 closed_trades over IS window |
| IS window (typical) | 4.6297 years |
| K9 minimum trades/year (4.6y IS) | ~21.6 |
| DR10 v1 / v2 `annual_turnover` threshold | 0.50 |
| DR10 v1 / v2 `S2_cost_drag` threshold | 0.05 (5%) |
| START_CASH baseline | $200,000 |
| Per-trade risk baseline | 0.5% |
| MNQ.c.0 per-trade notional estimate | ~$75,000 |
| DR10 max trades/year at baseline notional | ~1.33 |
| K9 / DR10 v1 structural gap ratio | **16.2x apart** |

---

## 3. Direction options (advisory-only enumeration; A through G; not ranked)

> Each option includes K9 and DR10 reachability arithmetic under both v1 (for existing chains, informational only since terminal) and v2 (for hypothetical new s14+ candidates).

> **None of these options is authorized by this memo. All require fresh sealed operator authorization.**

### 3.1 DO-A — Lower-frequency mean-reversion (RSI-5 / RSI-7 / longer-period bands)

| Field | Value |
|---|---|
| Mechanic family | F3 RSI mean-reversion (slower than RSI(2)) |
| Universe | MNQ.c.0 (same as s12-D1 / s13-d1 / T1) |
| Trades/year estimate | 15-25 (RSI-5); 8-12 (RSI-7) |
| K9 v1 clearance at baseline | BORDERLINE-TO-FAILS (RSI-5 borderline; RSI-7 likely fails) |
| K9 v2 clearance at baseline | same (K9 unchanged by DR10 v2) |
| DR10 v1 `annual_turnover` estimate | 30-50 (much lower than RSI(2)'s 84.7851 but still 60-100x over 0.50) |
| DR10 v1 `S2_cost_drag` estimate | <2.35% (proportional to turnover) |
| DR10 v1 fires | YES on `annual_turnover` branch |
| DR10 v2 fires | NO if `S2_cost_drag` stays below 5% (likely; s13-d1's v2-equivalent S2_cost_drag at 2.35% already below threshold) |
| Net under v1 (existing chains) | Would fail DR10 v1 same as s13-d1; would likely fail K9 worse than RSI(2) |
| Net under v2 (new s14+) | Could plausibly clear DR10 v2; K9 clearance borderline; requires careful PLAN-time K9-reachability analysis |
| Constraints | K9-reachability discipline at PLAN; DR10 v2 at SEAL; standard K/DR gates |
| Fresh authorization required | **YES** |

### 3.2 DO-B — Multi-instrument futures basket (e.g., MNQ + MES + MGC)

| Field | Value |
|---|---|
| Mechanic family | F3 RSI or F1 Donchian (choose to optimize K9 + DR10 jointly) |
| Universe | Multi-instrument basket (3-5 micro-futures) |
| Trades/year estimate | ~3x single-instrument rate (RSI(2)): 3 × 34 ≈ 100/y across basket |
| K9 v1 clearance at baseline | LIKELY CLEARS (100/y × 4.6y ≈ 460 trades; well over K9=100) |
| K9 v2 clearance at baseline | same |
| DR10 v1 `annual_turnover` estimate | Per-portfolio; 3-instrument basket: could be ~3× s13-d1 = 255 (worse) OR if sized 0.5% per-position aggregated to portfolio: stays similar |
| DR10 v1 `S2_cost_drag` estimate | ~2-4% (similar to s13-d1) |
| DR10 v1 fires | YES on `annual_turnover` branch (likely) |
| DR10 v2 fires | Depends on per-portfolio `S2_cost_drag` (likely NO if similar-cost futures) |
| Net under v1 (existing chains) | Would likely fail DR10 v1 same as s13-d1 unless sizing reduced |
| Net under v2 (new s14+) | Could plausibly clear K9 with margin AND DR10 v2 if `S2_cost_drag` stays below 5% |
| Constraints | K9-reachability at PLAN; DR10 v2 at SEAL; K10 pairwise dependence (s10-D2 K10 PASS at 0.0528 supports multi-instrument); per-portfolio turnover + cost-drag methodology required at PLAN |
| Fresh authorization required | **YES** |

### 3.3 DO-C — Cash-equity sub-fractional sizing (parallel-proposed at `30c836e`)

| Field | Value |
|---|---|
| Mechanic family | F3 RSI or other; flexible |
| Universe | Cash equities (e.g., SPY/QQQ/IWM/sector ETFs); fractional shares for sub-1% notional per trade |
| Trades/year estimate | Universe-dependent; intraday or daily cash equities can produce 50-200+/year per instrument |
| K9 v1 clearance at baseline | LIKELY CLEARS (with appropriate signal density) |
| K9 v2 clearance at baseline | same |
| DR10 v1 `annual_turnover` estimate | Heavily reduced via fractional sizing. At $200k equity with 0.05% per-trade notional ($100/trade), 50 trades/year = $5k turnover = **0.025 ratio - BELOW v1 threshold 0.50** |
| DR10 v1 `S2_cost_drag` estimate | <1% (much smaller notional → much smaller per-trade cost impact in absolute terms) |
| DR10 v1 fires | NO (likely) |
| DR10 v2 fires | NO |
| Net under v1 (existing chains) | Would clear both K9 and DR10 v1 if sizing is sub-fractional and signal density adequate |
| Net under v2 (new s14+) | Would clear both K9 and DR10 v2 |
| Constraints | Fresh data layer (cash-equity OHLC; not Databento futures); K11 cap-binding check (fractional shares cap); different cost model; different brokerage/execution venue; different regulatory regime (PDT); subject to K9-reachability + DR10 v2 + all standard K/DR gates |
| Parallel alignment | `30c836e` proposes this as primary path (parallel-naming: "T1 cash-equity nano-sizing") |
| Naming collision | This session's T1 (RSI MNQ TERMINAL) is **DISTINCT** from parallel's "T1" cash-equity proposal. Any future authorization must use a fresh `candidate_record_id` without parallel-T1 naming collision. |
| Fresh authorization required | **YES** |

### 3.4 DO-D — Same RSI(2)-like mechanic on MNQ.c.0 as fresh s14+ candidate (evaluated under DR10 v2)

| Field | Value |
|---|---|
| Mechanic family | F3 RSI(2) bi-directional (same as s13-d1) |
| Universe | MNQ.c.0 (same as s13-d1) |
| Trades/year estimate | ~34 (same as s13-d1) |
| K9 v1 clearance at baseline | CLEARS (159 over 4.6y) |
| K9 v2 clearance at baseline | same |
| DR10 v1 `annual_turnover` estimate | ~84.7851 (same as s13-d1) |
| DR10 v1 `S2_cost_drag` estimate | ~2.35% (same as s13-d1) |
| DR10 v1 fires | YES on `annual_turnover` branch (same as s13-d1) |
| DR10 v2 fires | **NO** (v2 requires BOTH branches; `S2_cost_drag` 2.35% still below 5% threshold) |
| Net under v1 (existing chains) | Already TERMINAL on s13-d1 + T1 chains; lifecycle structurally closed; cannot revive |
| Net under v2 (new s14+) | Would CLEAR DR10 v2 with same observed metrics. K9 clears. But would still face: K1 sharpe (s13-d1 observed +0.1076 - barely positive); K2 expectancy (+$540.73 - positive); K4 maxdd (-17.68% - below 50% threshold); K11 cap binding; OOS gates |
| Substantive caution | Even if DR10 v2 clears, observed sharpe +0.1076 is structurally weak. Cost-stress at S2/S3/S4 kept sharpe in +0.1000-0.1096 range. **Candidate is not distinguishable from noise on this evidence; passing DR10 v2 is necessary but not sufficient for advancement.** |
| Constraints | Fresh `candidate_record_id` required (cannot reuse s13-d1 or T1 names); DR10 v2 at SEAL; all other K/DR gates; OOS K9 reachability (s13-d1's OOS proportional 68.7 below threshold 100; faces DR1 INCONCLUSIVE_HOLD); no DR10 redefinition (v2 in place); no re-running of sealed chain |
| Fresh authorization required | **YES** |
| Informational observation | This is the path that parallel's DR10 v2 SEAL revision technically enables. Whether to pursue it given weak observed sharpe is a separate strategy-merit question. |

### 3.5 DO-E — Framework-level revision beyond DR10 (e.g., K9 threshold or K9-reachability methodology)

| Field | Value |
|---|---|
| Mechanic family | N/A (framework revision, not candidate) |
| Universe | N/A |
| K9 reachability note | This option is itself a revision of K9 mechanics. Either lower K9 threshold (e.g., 50) or change K9 to a density measure (trades/year ≥ some threshold rather than absolute count). |
| DR10 reachability note | N/A (this option is about K9, not DR10; DR10 already revised to v2) |
| Net under v1 (existing chains) | Would NOT modify existing terminal verdicts (preserved byte-equivalent) |
| Net under v2 (new s14+) | Would change reachability calculus for future candidates |
| Constraints | Touches structural framework invariants; requires separate framework-level revision authorization (similar to DR10 v2 SEAL at `78cd22e`); K9 v1 thresholds + methodology preserved verbatim for existing sealed candidates |
| Parallel alignment | `28cbaea` PLAN-only investigation flagged K9 ∧ DR10 incompatibility at retail-scale; framework-level changes within parallel chain's domain |
| Fresh authorization required | **YES** |

### 3.6 DO-F — Pause trading-bot research arc

| Field | Value |
|---|---|
| Mechanic family | N/A |
| Universe | N/A |
| Net under v1 (existing chains) | All existing terminal verdicts preserved |
| Net under v2 (new s14+) | No new candidates pursued |
| Rationale for consideration | Three of four trading-bot tracks this session terminated (s10-D2 PARK, s12-D1 PARK, T1 TERMINAL). Parallel s13-d1 also TERMINAL. Cumulative evidence: single-instrument futures at retail scale faces K9/DR10 structural tension; cross-asset basket faces K9 OOS sample-size; F1 and F3 mechanic families both exposed limitations. **A pause to reassess strategy-research methodology before authoring more candidates is a legitimate option.** |
| Constraints | No further candidate authoring during pause; existing sealed artifacts preserved; framework files preserved; optional brief framework retrospective at pause start |
| Fresh authorization required | **YES** |
| This memo does NOT recommend | **TRUE** |

### 3.7 DO-G — Cross-domain pivot (Hydra/video, YouTube, affiliate)

| Field | Value |
|---|---|
| Mechanic family | N/A |
| Universe | N/A |
| Net under v1 (existing chains) | All existing terminal verdicts preserved |
| Net under v2 (new s14+) | No new trading candidates pursued |
| Rationale for consideration | CLAUDE.md project notes list trading-bot, hydra_video, youtube_growth, affiliate_system as parallel project lines. Pivoting capacity to a non-trading project is operationally available. |
| Constraints | Subject to each non-trading project's own guardrails (CLAUDE.md); trading-bot existing sealed artifacts preserved; trading-bot framework preserved |
| Fresh authorization required | **YES** |
| This memo does NOT recommend | **TRUE** |

---

## 4. Explicit non-recommendation

- This memo is **advisory only.**
- This memo does **not recommend** any option.
- This memo does **not rank** options.
- This memo does **not designate** any option as primary or secondary.
- All seven options enumerated **as peers**, each with K9/DR10 reachability arithmetic under v1 and v2.
- Operator selects direction at fresh authorization turn.

Reasoning: per operator directive at authorization — "Advisory-only enumeration; no recommendation, no ranking."

---

## 5. Posture invariants (held this next-direction turn)

- Trading status: **PAUSED**
- Live status: **BLOCKED_AT_6_GATES**
- FRC granted: **NEVER**
- Advisory label permanent: **DIAGNOSTIC_ONLY_NOT_LIVE_GRADE**
- Verdict never means live ready: **TRUE**
- Live promotion path closed: **TRUE**
- This memo authorizes any phase: **FALSE**
- This memo authorizes any option in enumeration: **FALSE**

---

## 6. Chain anchors byte-stable

- All s10-D2 sealed artifacts not modified.
- All s12-D1 sealed artifacts not modified.
- All T1 chain artifacts not modified.
- All parallel s13-d1 chain artifacts not modified.
- All parallel post-s13-d1 artifacts (`30c836e`, `28cbaea`, `78cd22e`) not modified.
- DR10 v2 SEAL not modified.
- All other sN-dN sealed artifacts not modified.
- Audit-clean CSVs not touched.
- `lessons.md` / `decisions.md` / `next_actions.md` / `system_changes.md` not touched.

---

## 7. Negative invariants

NO_BUILD. NO_SIMULATOR_RUN. NO_BACKTEST. NO_RSI_COMPUTED. NO_DONCHIAN_COMPUTED. NO_SIGNAL_COMPUTED. NO_DATA_FETCH. NO_DATABENTO_CALL. NO_DATABENTO_API_KEY_ACCESS. NO_EXTERNAL_NETWORK_CALL. NO_REVIEW_QUEUE_MUTATION. NO_IDEA_MEMORY_MUTATION. NO_STRATEGY_LAB_INVOKED. NO_CANDIDATE_PROMOTED. NO_BROKERAGE_CONNECTION. NO_ORDERS_CREATED. NO_PAPER_OR_LIVE_TRADE. NO_S10_D2_CHAIN_MODIFIED. NO_S12_D1_CHAIN_MODIFIED. NO_T1_CHAIN_MODIFIED. NO_PARALLEL_S13_D1_CHAIN_MODIFIED. NO_PARALLEL_POST_S13_D1_ARTIFACTS_MODIFIED. NO_FRAMEWORK_DR10_REVISION_FILES_MODIFIED. NO_DR10_V2_SEAL_MODIFIED. NO_K9_FRAMEWORK_REVISION_PROPOSED_AS_AUTHORIZATION. NO_CACHE_MODIFICATION. NO_DATA_MODIFICATION. NO_CSV_MODIFICATION. NO_DRIVER_MODIFICATION. NO_TEST_MODIFICATION. NO_STRATEGY_CODE_MODIFICATION. NO_RUNBOOK_MODIFICATION. NO_PIPELINE_MANIFEST_MODIFICATION. NO_DECISIONS_MD_MODIFICATION. NO_LESSONS_MD_MODIFICATION. NO_NEXT_ACTIONS_MD_MODIFICATION. NO_SYSTEM_CHANGES_LOG_MODIFICATION. NO_GITIGNORE_MODIFICATION. NO_CLAUDE_MD_MODIFICATION. NO_BRANCH_CHANGE. NO_GIT_PUSH. NO_FRC_GRANT. NO_LIVE_READINESS_CLAIM. NO_PROFITABILITY_CLAIM. NO_DR_REDEFINITION_POST_SEAL. NO_SELF_AUTHORIZATION_OF_ANY_PHASE. NO_AUTHORIZATION_EXTRACTION_FROM_PARALLEL_POST_S13_D1_ARTIFACTS. NO_SCOPE_MERGE_WITH_PARALLEL_CHAIN. NO_RECOMMENDATION_IN_MEMO. NO_RANKING_IN_MEMO. NO_KEY_LEAKAGE.

---

## 8. Validation V-gates

V1 ASCII-only. V2 keyed sections consistent. V3 no execution language. V4 no self-authorization to any phase. V5 no code modification. V6 no backtest run. V7 no simulator run. V8 no signal computation. V9 no RSI computation. V10 no data fetch. V11 no network IO. V12 no live trading. V13 all sealed chains byte-stable at HEAD. V14 lessons.md unstaged and untouched. V15 decisions.md unstaged and untouched. V16 next_actions.md unstaged and untouched. V17 parallel post-s13-d1 referenced as informational only. V18 parallel T1-T5 naming distinction from this session's T1 recorded. V19 DR10 v2 binding scope recorded as s14-forward only. V20 existing chain verdicts recorded as preserved under v1. V21 options enumerated without recommendation. V22 options not ranked. V23 each option includes K9 and DR10 reachability arithmetic. V24 each option evaluated under v1 and v2 separately.

---

## 9. Labels

`TRADING_RESEARCH_NEXT_DIRECTION_MEMO_COMPLETE`
`ADVISORY_ONLY_ENUMERATION`
`NO_RECOMMENDATION_IN_MEMO`
`NO_RANKING_IN_MEMO`
`SEVEN_OPTIONS_ENUMERATED_DO_A_THROUGH_DO_G`
`EACH_OPTION_INCLUDES_K9_DR10_REACHABILITY_ARITHMETIC`
`EACH_OPTION_EVALUATED_UNDER_V1_AND_V2`
`EXISTING_CHAIN_VERDICTS_PRESERVED_UNDER_V1`
`NEW_S14_PLUS_CANDIDATES_BIND_UNDER_V2`
`PARALLEL_T1_T5_NAMING_COLLISION_NOTED`
`DR10_V2_AND_CONJUNCTION_INFORMATIONAL_ONLY`
`DR10_V2_BINDS_S14_FORWARD_ONLY`
`FRESH_AUTHORIZATION_REQUIRED_FOR_ANY_OPTION`
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

**Companion JSON:** `trading_research_next_direction_memo.json` (carries embedded `companion_md_sha256` and canonical `report_seal_sha256`).
