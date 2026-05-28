# s16-d1 expanded-universe (12-name cross-sector) cash-equity availability probe + DR9 audit RUN_BOOK

**NOT A SEAL** (RUN_BOOK_NOT_SEALED; no canonical seal) · **Fresh s16 path**
**Authored (UTC):** `2026-05-28T21:50:22.602842Z`
**Lifecycle:** `S16_D1_EXPANDED_CROSS_SECTOR_CASH_EQUITY_AVAILABILITY_PROBE_DR9_AUDIT_PENDING_OPERATOR_FETCH`
**Authorization:** `Authorize s16-d1 cash-equity expanded-universe availability probe + DR9 audit framework only.`

## §1. Motivation

The post-s15 selection plan (`343bdac`) found that on the 3-name AAPL/JPM/XOM daily basket only mean-reversion clears K9 — and its edge is exhausted (s14 + s15 both terminal FAIL_SAFETY). Non-mean-reversion families (trend/momentum/breakout) are K9-light on 3 names (~6-24/y << 50/y OOS floor). **Expanding to 12 names lifts basket frequency ~4×, making a NON-mean-reversion candidate K9-reachable.** Mechanic selection is deferred to the s16 Tier-N PLAN; mean-reversion re-skins are forbidden (T-FORBID-17/18 carried).

## §2. Vendor

**Tiingo split_only** (proven for 5 of these 12 names already; pure-Python requests succeeded where yfinance curl_cffi failed TLS). `TIINGO_API_KEY` from env only; never printed/logged/saved. adjClose/adjVolume ignored; dividends/distributions NOT adjusted.

## §3. Universe (12 names; 5 reusable DR9-passed, 7 fresh)

| Symbol | Sector | Exch | Data status | Splits in window |
|---|---|---|---|---|
| AAPL | Information Technology | NASDAQ | REUSE (DR9-passed) | 2020-08-31 4.0:1 |
| MSFT | Information Technology | NASDAQ | REUSE (DR9-passed) | none |
| NVDA | Information Technology | NASDAQ | REUSE (DR9-passed) | 2021-07-20 4.0:1; 2024-06-10 10.0:1 |
| JPM | Financials | NYSE | REUSE (DR9-passed) | none |
| XOM | Energy | NYSE | REUSE (DR9-passed) | none |
| UNH | Health Care | NYSE | FRESH fetch | none |
| WMT | Consumer Staples | NYSE | FRESH fetch | 2024-02-26 3.0:1 |
| KO | Consumer Staples | NYSE | FRESH fetch | none |
| META | Communication Services | NASDAQ | FRESH fetch | none |
| AMZN | Consumer Discretionary | NASDAQ | FRESH fetch | 2022-06-06 20.0:1 |
| JNJ | Health Care | NYSE | FRESH fetch | none |
| CVX | Energy | NYSE | FRESH fetch | none |

**Reusable (DR9-passed):** AAPL, MSFT, NVDA, JPM, XOM — AAPL/JPM/XOM from cross-sector `b13af03` (result_seal `a8ff9126…`); MSFT/NVDA from all-tech `214bae0` (result_seal `1c93d429…`).
**Fresh fetch + full DR9:** UNH, WMT, KO, META, AMZN, JNJ, CVX.

## §4. Output directory + manifest

- Output dir: `data/s16_d1_expanded_cross_sector_cash_equity_long_history/raw/`
- Files: `<SYM>_ohlcv_1d_20190102_20251230.csv` (×12) + `s16_d1_expanded_cross_sector_cash_equity_step02b_fetch_manifest.json`
- Manifest schema: `sparta.s16.expanded_cross_sector_cash_equity.step02b_fetch_manifest.v1` (same field structure as the s14 cross-sector manifest)
- Window: 2019-01-02 → 2025-12-30 (IS 2019-01-02..2023-12-29; OOS 2024-01-02..2025-12-30 LOCKED, not inspected)

## §5. DR9 audit framework (thresholds byte-equivalent from s14 RUN_BOOK; immutable)

gap_continuity ≥ 0.95 (NYSE calendar) · max_gap_ratio ≤ 0.30 (calendar gaps; price jumps are NOT gaps) · quality_violation_count ≤ 5 · roll_event_count NOT_APPLICABLE_CASH_EQUITY · documented_split_event_consistency PASS.

**Split-event consistency requirements:**
- **AMZN 2022-06-06 20:1** (FRESH) — most consequential; verify ratio ~1.0 under split_only across the split date.
- **WMT 2024-02-26 3:1** (FRESH; in OOS window) — verify ratio ~1.0 (data-integrity only; NOT OOS signal inspection).
- AAPL 4:1 / NVDA 4:1+10:1 — already verified PASS; re-verify only if re-fetched.
- MSFT/JPM/XOM/UNH/KO/META/CVX — no splits → trivially PASS.

**Informational (NOT a DR9 fail):** JNJ Kenvue spin-off (2023-08) appears as a ~8-10% one-day price drop under split_only (document explicitly); higher-yield names' ex-div jumps (<1%); META's 2022 drawdown is a price event.

## §6. K9-reachability logic (the point of expanding to 12 names)

OOS K9 floor = ≥50 trades/y. Expected basket round-trips/y by mechanic (12 names):
- slow trend (200d MA / Donchian-55): ~36-72/y → clears IS, borderline-clears OOS
- **medium breakout (Donchian-20/10, dual-MA 20/50): ~96-180/y → CLEARS both with margin**
- faster channel breakout (Donchian-10/5): ~144-240/y → clears comfortably
- monthly-rerank momentum: low turnover → K9-light (borderline-to-fail OOS; weekly re-rank improves)

→ A 12-name basket makes a **medium/faster breakout or trend** mechanic K9-OOS-reachable, resolving the s15-selection-plan blocker. The s16 Tier-N PLAN must still carry its own K9 table for the chosen mechanic.

## §7. DR10-v2 reachability

Cash-equity per-share commission + ~1bp slippage keep S2 cost_drag well under 5% (s14/s15 observed ~0.3-0.9%) regardless of turnover → DR10 v2 AND-conjunction does NOT fire. **CLEARS with strong margin.**

## §8. Contingency tree

- **all_12_pass_dr9 (5 reused PASS + 7 fresh PASS)** -> `Authorize s16-d1 expanded-universe cash-equity availability probe + DR9 audit RESULT SEALING only.`
- **1-4_fresh_symbols_fail_dr9** -> `Authorize s16-d1 shrunk expanded-universe DR9 RESULT SEALING only (drop failing names; basket must retain >= 8 names to preserve trend K9-reachability).`
- **5+_fresh_symbols_fail_dr9 (basket would drop below 8)** -> `Authorize s16-d1 expanded-universe revision to an alternative large-cap shortlist (RUN_BOOK rev only).`
- **a_split_event_consistency_check_fails (AMZN 20:1 or WMT 3:1 ratio off)** -> `Operator manual review of the split application; that symbol is INCONCLUSIVE_HOLD until resolved; do NOT auto-progress`
- **any_INCONCLUSIVE_HOLD** -> `Operator manual review; no auto-progression`
- **vendor_fetch_fails (TLS/network)** -> `Operator retries Tiingo later; RUN_BOOK remains reference; do NOT create repeated decline memos (brief in-chat reminder only)`

(8-name floor protects trend K9-OOS reachability; no silent symbol substitution; split-consistency failure → INCONCLUSIVE_HOLD + manual review.)

## §9. Boundaries held this RUN_BOOK turn

Framework/RUN_BOOK only · NOT a seal · no fetch / vendor API / API-key / network · no DR9 RUN / no DR9 RESULT sealed · no mechanic selection (deferred to PLAN) · no DRAFT/SEAL/BUILD/backtest/OOS · no live/broker/Strategy Lab · no revival of s15/s14/s13/s12 · no modification of reused captured data or any sealed artifact · **no `lessons.md`** · **no commit this turn**.

## §10. Next authorization

- Commit this RUN_BOOK: `Authorize commit s16-d1 expanded-universe availability probe + DR9 audit RUN_BOOK only.`
- Then operator-side fetch of the 7 fresh names → `Authorize s16-d1 expanded-universe cash-equity availability probe + DR9 audit RESULT SEALING only.`

trading `PAUSED` · live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE.
