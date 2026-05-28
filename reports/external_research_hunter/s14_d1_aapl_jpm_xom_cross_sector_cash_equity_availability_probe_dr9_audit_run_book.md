# s14-d1-cross-sector cash-equity availability probe + DR9 audit RUN_BOOK

**Document type:** RUN_BOOK (NOT a SEAL; no canonical `report_seal_sha256`)
**Authored (UTC):** `2026-05-28T17:53:09.570553Z`
**Lifecycle state:** `S14_D1_CROSS_SECTOR_CASH_EQUITY_AVAILABILITY_PROBE_DR9_AUDIT_PENDING_OPERATOR_FETCH`
**Authorization phrase:** `Authorize s14-d1-cross-sector cash-equity multi-name OHLCV availability probe + DR9 audit framework only.`
**Anchored to cross-sector PLAN at commit:** `c61860d` (sha `3acf6e3f26dfaf77773e1da05487b794ad6329f37a4fda767fa821b8157f12a2`)
**Anchored to all-tech RUN_BOOK model at commit:** `529bb6b`
**Anchored to all-tech AAPL reusable data sha:** `f6625ff1a6f8026369344bd50ca82bffcba716f1f3be9cdcfb5b905e35f893a9`

----

## 0. Scope

Cross-sector basket `{AAPL, JPM, XOM}` data acquisition framework. **NOT a SEAL.** Carries the proven Tiingo split_only approach from the all-tech basket. AAPL is already captured + DR9-PASSED (reusable); JPM + XOM require fresh fetch + DR9. No fetch executed this turn.

----

## 1. Per-symbol data status

### AAPL — Apple Inc. (Information Technology; NASDAQ)

| Field | Value |
|---|---|
| Data status | ALREADY_CAPTURED_AND_DR9_PASSED in all-tech fetch |
| Fetch required | False |
| Known splits in window | 2020-08-31 4.0:1 |
| DR9 | ALREADY_PASSED (split_only consistency verified; re-audit at cross-sector audit turn for self-contained provenance OR carry forward the all-tech DR9 PASS by sha-match) |
| Risk factors | Low (already verified) |

### JPM — JPMorgan Chase & Co. (Financials; NYSE)

| Field | Value |
|---|---|
| Data status | NOT_YET_FETCHED |
| Fetch required | True |
| Known splits in window | NONE in window |
| DR9 | FULL_DR9_AUDIT_REQUIRED after fresh fetch |
| Risk factors | Low (no splits in window; high liquidity NYSE financial; split_only = raw close; higher dividend yield ~2-3% -> small ex-div jumps under split_only, <1% of price, non-distorting to RSI(3)) |

### XOM — Exxon Mobil Corp. (Energy; NYSE)

| Field | Value |
|---|---|
| Data status | NOT_YET_FETCHED |
| Fetch required | True |
| Known splits in window | NONE in window |
| DR9 | FULL_DR9_AUDIT_REQUIRED after fresh fetch |
| Risk factors | Low (no splits in window; high liquidity NYSE energy; split_only = raw close; high dividend yield ~3-5% -> small ex-div jumps under split_only, <1% of price, non-distorting to RSI(3)) |


----

## 2. AAPL reuse policy

AAPL was captured + DR9-PASSED in the all-tech fetch (sha `f6625ff1a6f8026369344bd50ca82bffcba716f1f3be9cdcfb5b905e35f893a9`; split_only consistency verified at the 2020-08-31 4:1 split).

- **Option A (recommended; lower-friction):** copy AAPL CSV byte-equivalent into the cross-sector dir; verify sha; AAPL DR9 PASS carries by sha-match.
- **Option B:** re-fetch AAPL fresh into the cross-sector dir for fully self-contained provenance; re-run AAPL DR9.

Either way, AAPL's DR9 PASS is established. Operator decides at fetch time.

----

## 3. Vendor (carried from all-tech)

- **Vendor:** Tiingo (proven — succeeded where yfinance curl_cffi failed TLS on this machine)
- **Library:** tiingo-0.16.1 (already installed)
- **Adjustment convention:** `split_only` (Tiingo splitFactor stream; no dividend adjustment; adjClose/adjVolume ignored)
- **API key:** `TIINGO_API_KEY` from env only; never printed/logged/saved

----

## 4. Pre-authored DR9 audit framework (cash-equity adapted; thresholds carried from all-tech RUN_BOOK 529bb6b; immutable)

- `gap_continuity ≥ 0.95`
- `max_gap_ratio ≤ 0.30`
- `roll_event_count = NOT_APPLICABLE_CASH_EQUITY`
- `quality_violation_count ≤ 5`
- `documented_split_event_consistency PASS required`

**Split-event notes:**
- AAPL 2020-08-31 4:1 — already verified PASS (ratio 1.034 under split_only) in all-tech DR9
- JPM — no splits in window → trivially PASS
- XOM — no splits in window → trivially PASS

**Dividend note:** JPM + XOM have higher dividend yields than tech. Under split_only, ex-div dates show small downward jumps (<1% of price). NOT a DR9 fail condition (only split-event consistency is checked); informational.

8-step per-symbol check procedure identical to all-tech RUN_BOOK 529bb6b §5.2.

----

## 5. Operator-side fetch RUN_BOOK

- **Executor:** operator (`TIINGO_API_KEY` env only)
- **Output dir:** `data/s14_d1_aapl_jpm_xom_cross_sector_cash_equity_long_history/raw/`
- **Output files:** AAPL (reused/refetched) + JPM (fresh) + XOM (fresh) + `s14_d1_cross_sector_cash_equity_step02b_fetch_manifest.json`
- **Fetch params:** Tiingo · split_only · window 2019-01-02 to 2025-12-30 · fresh symbols JPM, XOM
- **Manifest schema:** `sparta.s14.cross_sector_cash_equity.step02b_fetch_manifest.v1` (same field structure as all-tech)
- **Post-fetch:** operator confirms all 4 files exist, then re-issues `Authorize s14-d1-cross-sector cash-equity multi-name OHLCV availability probe + DR9 audit RESULT SEALING only.`

----

## 6. Contingency tree

| Outcome | Next authorization |
|---|---|
| All 3 pass DR9 (AAPL carried + JPM/XOM fresh PASS) | `Authorize s14-d1-cross-sector cash-equity Tier-N spec DRAFT only — bound by DR10 v2.` |
| 1 symbol fails (JPM or XOM) | `Authorize s14-d1-cross-sector shrunk-basket Tier-N spec PLAN only — bound by DR10 v2.` (fresh candidate id; substitution forbidden; weakens K9 OOS) |
| 2 symbols fail | `Authorize s14-d1-cross-sector universe revision to alternative cross-sector shortlist — bound by DR10 v2.` |
| Any INCONCLUSIVE_HOLD | Operator manual review |
| Vendor fetch fails | Operator retries Tiingo later; RUN_BOOK remains reference; brief in-chat reminder only (no repeated decline memos per saved policy) |

----

## 7. Hard boundaries held this RUN_BOOK turn

No vendor API call by controller · no API-key access · no network IO · no data fetch · no DR9 audit RESULTS sealed · no DR9 audit RUN executed · no DRAFT/SEAL/BUILD/backtest/simulator/signal computation/OOS · no live/broker · no Strategy Lab · no candidate promotion · no s13-d1/s12-d1/parked revival · **no modification of the all-tech sibling DRAFT at `214bae0`** · no modification of the all-tech AAPL captured data (reused read-only) · no modification of the s14-d1-multi-instrument chain · no modification of any existing sealed artifact · no modification of the cross-sector PLAN at `c61860d` · no phase-2-safety-contract / CLAUDE.md / .gitignore modification · **no `lessons.md` modification or staging** · no review_queue / idea_memory mutation · no profitability claim · **document is NOT a SEAL**.

----

## 8. Status

trading: `PAUSED` · live: `BLOCKED_AT_6_GATES` · FRC: `NEVER_GRANTED` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · s13-d1 + s12-d1 lifecycles terminal · framework DR10 v2 binding for s14+.

**s14-d1-cross-sector lifecycle:** `S14_D1_CROSS_SECTOR_CASH_EQUITY_AVAILABILITY_PROBE_DR9_AUDIT_PENDING_OPERATOR_FETCH`
**s14-d1-cash-equity all-tech (sibling):** `S14_D1_CASH_EQUITY_TIER_N_SPEC_DRAFT_SEALED` (`214bae0`; valid)
**s14-d1-multi-instrument (sibling):** `S14_D1_AVAILABILITY_PROBE_DR9_AUDIT_PENDING_OPERATOR_FETCH` (gate-blocked at Databento)

----

## 9. Next-step authorization scope

- **Operator-side fetch (outside controller scope):** operator fetches JPM + XOM via Tiingo split_only per §5; reuses/re-fetches AAPL; writes manifest. Then:
  `Authorize s14-d1-cross-sector cash-equity multi-name OHLCV availability probe + DR9 audit RESULT SEALING only.`
- **Defer:** `Defer / Pause s14-d1-cross-sector cash-equity availability probe + DR9 audit.`
- **Advance all-tech sibling instead:** `Authorize s14-d1-cash-equity Tier-N spec SEAL only — bound by DR10 v2.`

----

End of RUN_BOOK. NOT a SEAL. No fetch executed. Tiingo split_only carried from all-tech (proven). AAPL reusable + DR9-passed; JPM + XOM fresh fetch + DR9 required. All-tech sibling DRAFT preserved byte-stable. Trading remains `PAUSED`.
