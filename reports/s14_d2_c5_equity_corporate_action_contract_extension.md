# S14-D2 C5 Equity Corporate-Action Contract Extension

**Contract ID:** `S14_D2_C5_EQUITY_CORPORATE_ACTION_V1`
**Schema:** `sparta.candidate.s14_d2.c5_equity_corporate_action_contract_extension.v1`
**Phase:** `C5_EQUITY_CORPORATE_ACTION_CONTRACT_EXTENSION`
**Lifecycle state:** `C5_EQUITY_CORPORATE_ACTION_CONTRACT_EXTENSION_SEALED`
**Applies to:** `s14-d2-aapl-msft-nvda-cash-equity-3-name-basket-rsi-3-bi-directional`
**Universe:** {AAPL, MSFT, NVDA}
**Authored at (UTC):** `2026-05-27T22:10:00.000000+00:00`
**Sealed JSON:** `reports/s14_d2_c5_equity_corporate_action_contract_extension.json`
**Report seal sha-256:** `2b60a56472293d38356fe0b11c0fa4318c8376544839bd1fc852448b28a9e9c7`

This C5 contract extension is **INFORMATIONAL AND GOVERNANCE ONLY** for
SEAL-time reference. Does NOT fetch data. Does NOT authorize SEAL, BUILD,
P4, P6, P6.5, P7, P10, or P11. Does NOT modify any prior commit. Does NOT
ratify or advance T1 (5376de7 remains `PROVISIONAL_NOT_FULLY_RATIFIED`).

## Parent references

| Anchor | Commit |
|---|---|
| S14-D2 PLAN | `373eac8` |
| S14-D2 DRAFT | `6347dc1` |
| DR10 v2 SEAL | `78cd22e` |
| DR10 v2 governance supplement | `fdf9d6e` |
| Rev2 governance supplement | `7d7bb52` |
| T1-vs-T2 comparison memo (RATIFY_T2_PRIMARY) | `18bc7b0` |
| Rev2 next-track plan | `ee2bfc1` |
| Master reconciliation memo | `1e51680` |
| T1 provisional PLAN | `5376de7` |
| S13-D1 SEAL | `262491c` |
| S13-D1 P7 decision memo | `cc1817b` |

## 1. Scope

Extends the generic C1-C8 phase-2 safety contract framework (which was
authored for futures candidates) with equity-specific behavior for splits,
dividends, mergers, spin-offs, delistings, survivorship bias, OHLCV
adjustment, and vendor methodology. **Binds only s14-d2.** Carries by-reference
at SEAL.

## 2. Stock splits (forward)

CRSP-style backward-adjusted sealed CSV. Position size adjusts at ex-date:
e.g., 100 shares NVDA on 2024-06-09 → 1000 shares on 2024-06-10 ex-date at
no cost; per-share entry price divided by ratio. RSI(3) signal continuity
preserved (transparent to split). Split event log audit required at SEAL.

## 3. Reverse splits

ZERO expected for AAPL/MSFT/NVDA (these are not distressed/low-price names).
If unexpectedly detected: symmetric handling (multiply prices by ratio;
divide volumes). SEAL must verify ZERO reverse-split events in IS+OOS window.

## 4. Dividends (regular)

**Non-reinvestment cash account semantics** (per PLAN §6.2 + DRAFT DA15).
Cash credited to account on ex-dividend date; NOT auto-reinvested.
**Price-only RSI** (NOT total-return); ex-dividend price drop included in
signal as legitimate market event. P&L attribution tracks price_diff +
dividends_received separately. Look-ahead bias avoided (announcement metadata
not used in signal).

## 5. Special dividends

**Same treatment as regular dividends** per §4 — mechanically identical;
ad-hoc rules not principled. AAPL/MSFT/NVDA expected to have ZERO special
dividends in window (MSFT 2004 $3 special pre-IS; AAPL no specials since
2012 reinstatement; NVDA never paid special).

## 6. Symbol changes

ZERO expected (AAPL/MSFT/NVDA stable since IPO; all on NASDAQ). If detected:
historical-ticker-keyed sealed CSV preserves continuity. Audit must verify
no symbol changes in window.

## 7. Mergers / acquisitions

ZERO expected (these are S&P 100 acquirers, not targets). If detected:
**CLOSE_AND_DO_NOT_REPLACE** per PLAN §6.3 — position closed at last bar;
basket shrinks to 2 names; no replacement. Cash-buyout → cash proceeds.
Stock-merger → liquidate acquirer shares at first trading day open.

## 8. Spin-offs

ZERO expected. If detected: spun-off shares sold immediately at first open
price; parent position remains open at post-spin-off adjusted price.

## 9. Delistings

ZERO expected. If detected: CLOSE_AND_DO_NOT_REPLACE per PLAN §6.3.
K11-style portfolio cap reduces to 2 simultaneously open positions.

## 10. Survivorship bias

**ACKNOWLEDGED EXPLICITLY** — bias is present and UPWARD.

- AAPL/MSFT/NVDA selected in 2026 (current); IS window 2019-2025 captures
  their outperformance period; failure cases not represented
- **NVDA-specific bias**: 2023-2025 AI-driven outperformance = regime-specific
  tailwind; RSI behavior may reflect AI-bubble regime
- **MSFT-specific bias**: cloud + AI transformation tailwind 2019-2025
- **AAPL-specific bias**: services-growth + buyback tailwind 2019-2025

**Mitigation strategy:** verbatim acknowledgment section in SEAL artifact
(per PLAN §6.6 + DRAFT §9.5). P11 lifecycle memo MUST frame diagnostic value
as *"did RSI(3) work on THESE 3 names in 2019-2025?"* — NOT as *"this
strategy works on cash equities"* (overgeneralization).

## 11. NVDA split history risk (EXPLICIT)

**Documented historical splits within plausible IS window:**

| Ex-date | Ratio | Type | Notes |
|---|---|---|---|
| 2021-07-20 | 4:1 | forward | Announced 2021-05-21 |
| 2024-06-10 | 10:1 | forward | Announced 2024-05-22 |

**Effective NVDA back-adjustment factor: 40x** (4 × 10). Pre-2021 NVDA raw
prices ~$200-700 → post-back-adjusted equivalents ~$5-17.50.

**NVDA-specific SEAL audit requirement:** verify vendor's NVDA back-adjusted
price series includes BOTH splits. Hand-check method: NVDA 2024-06-07 close
was ~$1,209 raw / ~$120.90 post-2024-split / ~$120.90 post-all-back-adjusted.
Discrepancy of >1% on this specific bar = split-adjustment methodology issue
→ re-FETCH or vendor switch.

**RSI signal impact of NVDA splits:** ZERO if CRSP back-adjustment correctly
applied (signal operates on continuous series). If INCORRECT: artificial
extreme RSI readings at split ex-date → corrupted diagnostic.

## 12. Adjusted vs unadjusted OHLCV

**Required combination: split-adjusted (backward-CRSP) AND
dividend-UNADJUSTED.**

| Adjustment type | Status | Rationale |
|---|---|---|
| Split adjustment | **MANDATORY** (CRSP backward) | Pure mathematical adjustment; preserves signal continuity |
| Dividend adjustment | **FORBIDDEN** for RSI signal | Smooths out real ex-dividend price drop; produces non-tradable diagnostic |

**Vendor-specific notes:**

- **Databento equities**: provides both unadjusted + adjusted; use
  unadjusted + apply CRSP split adjustment via Databento split event log
- **Polygon**: provides both; use splits-only adjusted endpoint
- **Alpaca**: split-adjusted by default; verify no dividend adjustment
- **IEX Cloud**: both variants available; verify operational status (sunset
  announced Aug 2024)
- **yfinance**: HIGHEST FRICTION — `Adj Close` is split+dividend-adjusted;
  must use `Close` (unadjusted) + apply CRSP split adjustment via separately
  fetched split event log

## 13. Vendor methodology differences

Different vendors produce different back-adjusted series for the same
ticker. SEAL must lock vendor + methodology version with byte-equivalent
reproducibility from documented primary sources (vendor source + split log +
dividend log + adjustment parameters; all sha256-anchored).

## 14. Required data-vendor fields for corporate-action audit

Minimum fields: ticker_symbol (historical), bar_date, unadjusted O/H/L/C/V,
split_event_log, dividend_event_log, symbol_change_log, delisting_event,
merger_event, spin_off_event. Cross-reference at least one event of each
type against SEC EDGAR 8-K filings or company IR announcements.

## 15. Adjusted prices affecting RSI(3) signals

| Scenario | Signal behavior | Status |
|---|---|---|
| Correctly split-adjusted + dividend-unadjusted | Continuous; ex-dividend drop visible | **REQUIRED** |
| Unadjusted (no split adjustment) | Artificial RSI=0 at split ex-date → false long signal | **FORBIDDEN** |
| Dividend-adjusted (total-return) | Smooths ex-dividend drop; non-tradable diagnostic | **FORBIDDEN** |

SEAL artifact must include worked RSI(3) example across at least one NVDA
split ex-date (2021-07-20 or 2024-06-10) showing no artificial signal
extreme.

## 16. Dividend treatment specification

**SELECTED: CASH_ADJUSTMENT_NON_REINVESTED.**

| Alternative | Status | Reason |
|---|---|---|
| REINVESTED | REJECTED | Look-ahead bias; doesn't match retail reality |
| IGNORED | REJECTED | Understates total return on longs |
| **CASH_ADJUSTMENT_NON_REINVESTED** | **SELECTED** | Matches retail; no look-ahead; transparent P&L |

**Short position dividend handling:** short-seller pays dividend to lender;
DEBITED from account cash on ex-date; tracked as negative dividend P&L on
short side.

**Borrow cost for shorts:** typically ~0.25-1% per annum for AAPL/MSFT/NVDA
at retail; SEAL must verify against IBKR/Schwab borrow rate tables at SEAL
time.

## 17. Audit requirements before SEAL

12 required audits (each must produce byte-stable artifact referenced by
SEAL via sha256 anchor):

1. Split event log + cross-reference
2. Dividend event log + cross-reference
3. Verify ZERO reverse-split events
4. Verify ZERO symbol-change events
5. Verify ZERO merger/acquisition events
6. Verify ZERO spin-off events
7. Verify ZERO delisting events
8. Hand-check NVDA 2021-07-20 + 2024-06-10 splits in vendor back-adjusted series
9. Verify vendor Close is split-adjusted, NOT dividend-adjusted
10. Worked RSI(3) example across NVDA split ex-date
11. Borrow-cost rate verification for short side
12. Verbatim survivorship-bias acknowledgment section

**If any audit reveals unhandled corporate-action event, candidate must be
re-PLANned with substitute universe BEFORE SEAL.**

## 18. This contract does NOT authorize

- Data fetch from any vendor
- SEAL, BUILD, P4, P6, P6.5, P7, P10, P11
- Signal/correlation/A7/RSI computation
- Any backtest, simulator, Strategy Lab
- T1 ratification or advancement (5376de7 remains PROVISIONAL_NOT_FULLY_RATIFIED)
- Any modification of S14-D2 PLAN/DRAFT, DR10 v2, governance supplements,
  comparison memo, or any existing sealed artifact
- Modification of C1-C8 framework template (this EXTENDS C5 for equities;
  does NOT modify the template)
- Modification of lessons.md, tmp/ helpers, app.py, Research Orchestrator
- Profitability / live-readiness / OOS-confirmation claims

## 19. Posture invariants

- Trading: **PAUSED**
- Live: **BLOCKED_AT_6_GATES**
- FRC: **NEVER_GRANTED**
- Research grade: **DIAGNOSTIC_ONLY_NOT_LIVE_GRADE**
- K9 inviolacy preserved · K9-reachability binding · K9 OOS ≥ 50/y binding
- DR10-reachability binding under v2 AND-conjunction
- DR10 v1 binding existing candidates · DR10 v2 binds s14+
- s13-d1 REJECT_FAST: TERMINAL under DR10 v1
- All sealed artifacts byte-stable
- T1 (5376de7) byte-stable + PROVISIONAL_NOT_FULLY_RATIFIED
- S14-D2 PLAN (373eac8) + DRAFT (6347dc1) byte-stable
- `GOV-RULE-FRAMEWORK-REVISION-OPERATOR-PHRASE-V1` binding
- `GOV-RULE-CO-PRIMARY-OPERATOR-SELECTION-PHRASE-V1` binding
- Profitability claim: NONE · Live-readiness claim: NONE · OOS-confirmation
  claim: NONE
- Operator-typed authorization required for any next phase

## Seal

```
report_seal_sha256: 2b60a56472293d38356fe0b11c0fa4318c8376544839bd1fc852448b28a9e9c7
seal_method:        LESSON_HUNTER_004 canonical roundtrip
```
