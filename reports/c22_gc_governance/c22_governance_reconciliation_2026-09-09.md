# C22 Governance Reconciliation — 2026-09-09

Purpose: record which C22 lifecycle tokens actually exist on disk, which phases were built
without a surviving explicit human token, their current hashes / specification identities, and
what present-day human ratification would be required before a decisive replay. **No historical
token is fabricated here. No old record is altered.** Sources: `git log`, `reports/**`,
`brain_memory/**`, `reports/approvals/`, module constants (all read-only).

## 1. Tokens that actually exist (surviving explicit records)

| Token / decision | Where it survives | Effect |
|---|---|---|
| `HUMAN_DECISION_C22_REPLAY_SPEC_ACCEPT_OR_REVISE=REVISE` | `reports/c22_gc_replay_spec/c22_gc_replay_specification_phase_a.md:5` and `.json:375`; module constant `REVISE_DECISION_REF` | Produced Phase A **REV1** (spec SHA `9bf10af353521738f440c2e953af44cdd5ed093590f03a843a01972485dd9867`). The **second review (ACCEPT) is not recorded anywhere.** |
| `HUMAN_APPROVED_C22_SIGNUM_GC_FROZEN_DATA_WINDOW_REVIEW` | `brain_memory/logs/system_changes.md:5084`; `next_actions.md:3037,3039` (as the *suggested* token) | Collection-review gate reached and consumed (watcher: `collection_review_consumed=true`, decision `HOLD_FOR_MORE_C22_LABEL_EVIDENCE`). The consuming act is referenced by the watcher contract, not by a dated approval record. |
| `HUMAN_DECISION_C22_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT` (implied) | The V2 artifact exists (`b6a28a48…`, built 2026-07-15) and the V2 runner refuses to write without this exact token (`tools/…v2_range…_once.py:81-91`) | The token must have been supplied at build time; **no dated approval record of it survives** in `reports/approvals/` or `brain_memory/`. |
| 2026-08-06 operator-directed reconciliation + 6 MCP-fetched windows | `brain_memory/projects/trading_bot/decisions.md:4316`; `system_changes.md` 2026-08-06 entry | Precedent for operator-directed historic `get-trendradar-daily(runDate=…)` fetches admitted through the guarded pickup chain. |
| 2026-09-09 operator decision "candidate-family FREEZE + redirect" | `decisions.md:4320` | C22 to be driven to explicit ACCEPT/REJECT using committed research-only tooling; live trading remains BLOCKED. |
| 2026-09-09 closure recommendation | `reports/c22_gc_decision/c22_closure_recommendation_2026-09-09.md` (commit `a0449ca2`, other session) | RECOMMENDS `REJECT_KEPT_ON_RECORD` on feasibility grounds; asks the operator to record `HUMAN_DECISION_C22_REJECT_RECORDED_AT_LABELS_REVIEW` **or** `HUMAN_DECISION_C22_HOLD_PENDING_SHORT_INSTRUMENT_EVIDENCE`. **Neither has been recorded.** |
| Tokens supplied in this session (2026-09-09) | This session's operator message ("Proceed with implementation … replay infrastructure only") | `HUMAN_APPROVED_BUILD_C22_V3_EXTENDED_LABEL_EVIDENCE_ONLY` (V3 artifacts), `HUMAN_APPROVED_BUILD_C22_REPLAY_DRY_RUN_NO_PNL` (dry-run report). Both are build tokens for **diagnostic artifacts**; neither is a lifecycle ACCEPT, a replay authorization, or a profile selection. |

`reports/approvals/approvals.json` and the `phase2_manual_sim_*.json` records contain **no C22
entry**.

## 2. Phases implemented without a surviving explicit human token

| Phase / artifact | Built | Identity | Token that the module *names* | Surviving record of that token |
|---|---|---|---|---|
| Proposal → candidate spec → detector dry-run → data readiness (V1 chain) | 2026-06-20 (`b1b92795`…`33f44f2d`) | commits | proposal pinned to commit `b1b927957eb4…`; gate sequence in `..._candidate_spec_contract.py:56-61` | none dated |
| Real-candle labels + review HOLD | 2026-06-20 (`8177d7f1`, `56b8fc77`) | commits | `HUMAN_DECISION_C22_REVIEW_REAL_CANDLE_LABELS_OR_REJECT` | commit `56b8fc77` records a HOLD decision |
| V1 multi-window labels + remediation | 2026-07-09/10 (`d9f16350`, `2e0ab9ec`, `ed9cf755`) | commits | `HUMAN_DECISION_C22_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT` | none dated |
| **V2 26w label artifact** | 2026-07-15 (commit `0aa09437`, 2026-07-20) | artifact SHA `b6a28a4873d1aff17014a9d598702c67047b4ebe023b8cfddce05094f9ce9dd8`; manifest `48347e9c…`; payload `5dc9eae4…` | `HUMAN_APPROVED_BUILD_AND_VALIDATE_C22_26_WINDOW_LABEL_PIPELINE_V2_ONLY` (docstring) + runner token | none dated (artifact proves supply) |
| **Phase A REV1 replay spec** | 2026-07-21 (`a7957b79`) | spec SHA `9bf10af3…`; `PHASE_A_BUILD_TOKEN = HUMAN_APPROVED_BUILD_C22_REPLAY_SPECIFICATION_PHASE_A_SPEC_ONLY` | REVISE recorded; **ACCEPT not recorded** |
| **Phase B1** forward-exit + execution-data contracts | 2026-07-21 (`9a39b4f2`); regenerated over 81 windows 2026-09-09 (`a0449ca2`, other session) | forward SHA `f3a1029ae705bd67e4eb8cdebff144f949c2d0ff6a62f89344738fbec65e731c`; execution SHA `1a207918c7146182ab41d888d1daa14cf85fbb592d97295795701932bccf713f`; `HUMAN_APPROVED_BUILD_C22_FORWARD_AND_EXECUTION_DATA_READINESS_PHASE_B1` | none dated; review tokens `…FORWARD_EXIT_DATA_CONTRACT_ACCEPT_OR_REVISE` / `…EXECUTION_DATA_CONTRACT_ACCEPT_OR_REVISE` **not recorded** |
| **Phase B2** short-instrument evidence request | 2026-07-21 (`e7e9a2fe`) | SHA `a08a4cd58caa373cd5c9ec4f8c980a646105aa6c126fe269c33d2534e7108b40` | review token `…SHORT_INSTRUMENT_EVIDENCE_REQUEST_ACCEPT_OR_REVISE` **not recorded** |
| **Phase B3** acquisition plan | 2026-07-22 (`577101d4`) | SHA `c171fd73e7f1166c8e22946f1dfab728f14b738de6f1306c17860b52893dcc9f`; `ACQUISITION_STATUS=NOT_AUTHORIZED` | review token `…HISTORICAL_EVIDENCE_ACQUISITION_PLAN_ACCEPT_OR_REVISE` and all 5 fetch tokens **not recorded** |
| V3_EXTENDED artifacts (this session) | 2026-09-09 (`ea71033e`) | 82w `f59a0ae573bd9bf607b22dc4ea9cbafe1c6180c4507a4609fb8e80e5ed4a4547`; 57w `9528662fe05d4243d1e9645dab15803c6bbaa84e55ca01260715bab976832867`; 24w `70aa418818d6ed218f46deae9ebb25ab27d8977b528078a69b6b19dd1a39bd64` | `HUMAN_APPROVED_BUILD_C22_V3_EXTENDED_LABEL_EVIDENCE_ONLY` | this session's operator authorization (diagnostic evidence only) |
| No-P&L dry run (this session) | 2026-09-09 (`a7e79fd1`) | report SHA `f76f8330f72e454fe507b38ac76c67d5eec8a2417c7faef620330a4c620102ef` | `HUMAN_APPROVED_BUILD_C22_REPLAY_DRY_RUN_NO_PNL` | this session's operator authorization |

## 3. Frozen identities re-verified today (unchanged)

- V2 artifact: `b6a28a4873d1aff17014a9d598702c67047b4ebe023b8cfddce05094f9ce9dd8` ✔ (asserted by V3 integrity report and dry-run loader).
- 88 actionable V2 signals: 13 LONG_ENTRY / 72 BEAR_SHORT / 3 HEDGE_SHORT ✔ (V3 subset check).
- 2026-06-26 source: `a872f3568f17e95a…` ✔ (see the proposed provenance note).
- Phase A REV1 / B1 / B2 / B3 report files: untouched by this session (B1 regenerated by another session today, `a0449ca2`).

## 4. Present-day human ratification required (in order) before a decisive fee-honest replay

1. Record the outstanding **closure decision** requested by the 2026-09-09 closure recommendation
   (`HUMAN_DECISION_C22_REJECT_RECORDED_AT_LABELS_REVIEW` **or**
   `HUMAN_DECISION_C22_HOLD_PENDING_SHORT_INSTRUMENT_EVIDENCE`). If REJECT is recorded, the
   infrastructure built today remains research tooling and steps 2–9 are moot.
2. `HUMAN_DECISION_C22_REPLAY_SPEC_ACCEPT_OR_REVISE=ACCEPT` (second review of REV1) — or REVISE.
3. `HUMAN_DECISION_C22_FORWARD_EXIT_DATA_CONTRACT_ACCEPT_OR_REVISE` and
   `HUMAN_DECISION_C22_EXECUTION_DATA_CONTRACT_ACCEPT_OR_REVISE` (B1).
4. `HUMAN_DECISION_C22_WEEKEND_SESSION_RULE` — rule between `V2_CONTRACT_EXACT` and
   `CRYPTO_CALENDAR_SENSITIVITY` on governance grounds (both are reported; the dry run shows 23 of
   88 signals differ). Not selectable on performance (none exists).
5. `HUMAN_DECISION_C22_DRY_RUN_ACCEPT_OR_REJECT` on `reports/c22_gc_replay_dry_run/`.
6. B2 / B3 acceptance, then the B3 fetch authorizations
   (`…INSTRUMENT_REGISTRY_FETCH_AUTHORIZE`, `…FUNDING_AND_BORROW_FETCH_AUTHORIZE`,
   `…EXECUTION_OHLC_FETCH_AUTHORIZE`, `…FEES_AND_LIQUIDITY_FETCH_AUTHORIZE`), then
   `…HISTORICAL_INSTRUMENT_EVIDENCE_ADMIT_OR_REJECT`. The operator's 2026-09-09 message authorizes
   historical/public/read-only acquisition for evaluation; the corresponding dated approval records
   still need to be written so the precondition shell can see them.
7. `HUMAN_DECISION_C22_SHORT_INSTRUMENT_SELECT` (per asset, perp vs spot-margin).
8. `HUMAN_DECISION_C22_EXECUTION_COST_BASE_CASE_ACCEPT_OR_REVISE=ACCEPT` (component-level base
   case; 37 bps stays sensitivity-only).
9. `HUMAN_DECISION_C22_BASIS_ALIGNMENT_REVIEWED`.
10. Only then: `HUMAN_DECISION_C22_ADVANCE_TO_REPLAY_OR_REJECT=ADVANCE`.

The precondition shell `tools/c22_fee_honest_replay_once.py` looks for the exact strings above in
`reports/approvals/*.json`; writing those records is a human act.

## 5. Interpretation choices made by this session's code (flagged, not ratified)

- **Fill convention**: open of the next session strictly after the decision date, sourced only
  from an admitted export that carries that candle (no lookahead; no same-bar fill). The spec text
  ("next executable market session OPEN after decision date D") supports this; it is stricter
  than filling at the open of the decision day's own candle.
- **Weekend-dated frozen signals under V2_CONTRACT_EXACT** are still decided (they are frozen V2
  facts) and fill at the next weekday session; exits are evaluated on weekday exports only.
- **Out-of-radar exits** fail closed at the first next bar if no admitted export carries a price;
  they are never retried on a later reappearance.
- **END_OF_DATA**: boundary = last admitted export; open positions stay OPEN_AT_END_OF_DATA,
  mark-to-market is diagnostic only, performance conclusion = INCOMPLETE_FOLLOWUP.
- **Instrument verification** is reported for every record but only enforced in strict mode; the
  dry run uses lifecycle-only mode so exit evidence exists for shorts too.
