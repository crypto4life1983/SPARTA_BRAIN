"""Candidate #22 -- B3 STAGE 4A: EVIDENCE RECOVERY FROM DATED FIRST-PARTY OFFICIAL RECORDS
(supplemental to the sealed Stage Four; READ-ONLY; RESEARCH ONLY).

Stage Four failed closed under API-only evidence. Stage 4A determines how much of the unresolved
historical fee / tick-lot-minimum / spread / liquidity evidence can be recovered from DATED
official exchange records outside the live API surfaces: official announcements, dated help-center
articles, official fee pages, product/contract-change notices, API changelogs, official archived
datasets and official historical analytics endpoints. Search engines were used only to LOCATE
records; every decisive item below is an official first-party page or endpoint that this tool
re-fetches and preserves (raw HTML where the venue serves it; otherwise the rendered-text capture
taken during the sweep is embedded, hashed and labelled RENDERED_TEXT_CAPTURE_NOT_RAW_HTML).

Nothing here weakens the frozen Stage Four requirement, modifies the sealed Stage Four artifacts,
selects an assumption, or computes performance. Grades are fail-closed:
  fees:        T1_HISTORICAL_FEE_EXACT | T2_HISTORICAL_FEE_BRACKETED | T2_HISTORICAL_FEE_CHANGE_RECONSTRUCTED | CURRENT_ONLY | UNRESOLVED
  constraints: T1_HISTORICAL_CONSTRAINT_EXACT | T2_HISTORICAL_CONSTRAINT_RECONSTRUCTED | T2_BRACKETED_UNCHANGED | CURRENT_ONLY | UNRESOLVED
  spread/liq:  OBSERVED_BBO | OBSERVED_ORDERBOOK | DERIVED_SPREAD_FROM_BBO | TRADE_ACTIVITY_ONLY | DEPTH_PROXY_ONLY | UNRESOLVED
Conservative ordinary retail tier assumed (no VIP, no maker rebate, no token discount, no promotion).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import date as _date, datetime as _dt, timedelta as _td, timezone as _tz
from pathlib import Path
from typing import Callable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.c22_historical_evidence_acquisition_plan_contract as B3  # noqa: E402
import tools.c22_b3_stage1_instrument_existence_once as S1  # noqa: E402
import tools.c22_b3_stage4_fees_liquidity_once as S4  # noqa: E402

STAGE = "B3_STAGE_4A_T2_EVIDENCE_RECOVERY"
STAGE_VERSION = "c22_b3_stage4a_v1"
STAGE4_RUN_OF_RECORD = "20260911T131902Z"
STAGE4_REPORT = REPO_ROOT / "reports" / "c22_gc_b3_stage4" / ("c22_b3_stage4_fees_liquidity_%s.json" % STAGE4_RUN_OF_RECORD)
STAGE4_REPORT_SHA256 = "6c7753208b05e928aef786edb7f3741929a1cf119e09374672d233241965b9d1"
REPORT_DIR = REPO_ROOT / "reports" / "c22_gc_b3_stage4a"
RECORDS_DIR = S1.EVIDENCE_ROOT / "official_records"
_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) sparta-brain-c22-b3-stage4a-readonly/1.0"
SWEEP_DATE = "2026-09-11"
WINDOW = ("2026-06-20", "2026-09-09")

# fee grades
FEE_T1, FEE_T2_BR, FEE_T2_RC, FEE_CUR, FEE_UNRES = ("T1_HISTORICAL_FEE_EXACT", "T2_HISTORICAL_FEE_BRACKETED",
                                                    "T2_HISTORICAL_FEE_CHANGE_RECONSTRUCTED", "CURRENT_ONLY", "UNRESOLVED")
CON_T1, CON_T2_RC, CON_T2_BR, CON_CUR, CON_UNRES = ("T1_HISTORICAL_CONSTRAINT_EXACT", "T2_HISTORICAL_CONSTRAINT_RECONSTRUCTED",
                                                    "T2_BRACKETED_UNCHANGED", "CURRENT_ONLY", "UNRESOLVED")
SP_BBO, SP_OB, SP_DERIVED, SP_TRADES, SP_DEPTH, SP_UNRES = ("OBSERVED_BBO", "OBSERVED_ORDERBOOK", "DERIVED_SPREAD_FROM_BBO",
                                                            "TRADE_ACTIVITY_ONLY", "DEPTH_PROXY_ONLY", "UNRESOLVED")
RAW_HTML, RENDERED = "RAW_HTML_PRESERVED", "RENDERED_TEXT_CAPTURE_NOT_RAW_HTML"

ALLOWED_HOSTS = ("www.binance.com", "developers.binance.com", "www.bybit.com", "announcements.bybit.com", "www.okx.com",
                 "www.gate.com", "support.kraken.com", "www.kraken.com", "docs.kraken.com", "futures.kraken.com",
                 "www.bitfinex.com", "support.bitfinex.com", "blog.bitfinex.com")


class Stage4AError(RuntimeError):
    pass


# --------------------------------------------------------------------------------------------
# OFFICIAL SOURCE REGISTRY (facts captured during the 2026-09-11 sweep; every entry is re-fetched
# below for raw preservation where the venue serves raw HTML)
# --------------------------------------------------------------------------------------------
SOURCES = [
    # ---- BINANCE ----
    {"id": "BIN_TICK_20260227", "venue": "BINANCE", "url": "https://www.binance.com/en/support/announcement/detail/5f7fa3af3efa43cdae0716427defb95b",
     "title": "Updates on Tick Size for Multiple USDⓈ-M Perpetual Futures Contracts (2026-02-27)", "published": "2026-02-25", "effective": "2026-02-27T07:00Z",
     "captured": "Contracts: SOLVUSDT, FLUXUSDT, DEGENUSDT, SEIUSDT, KOMAUSDT, BRETTUSDT, NEIROUSDT, SWARMSUSDT, TRUSTUSDT, DUSDT, AVAAIUSDT, ZEREBROUSDT, XANUSDT, WALUSDT, ALTUSDT. None of the 13 C22 Binance perps named.",
     "role": "constraint_change_notice"},
    {"id": "BIN_TICK_20260406", "venue": "BINANCE", "url": "https://www.binance.com/en/support/announcement/6dbc37d4df4b42cd91b3ca768ec547dd",
     "title": "Updates on Tick Size for Multiple USDⓈ-M Perpetual Futures Contracts (2026-04-06)", "published": "2026-04-02", "effective": "2026-04-06T06:30Z",
     "captured": "Contracts: ARIAUSDT, STABLEUSDT, GWEIUSDT, PTBUSDT, HYPERUSDT. None of the 13 C22 Binance perps named.", "role": "constraint_change_notice"},
    {"id": "BIN_TICK_20260410", "venue": "BINANCE", "url": "https://www.binance.com/en/support/announcement/detail/3208154ca9544e22a999808c06f26cd7",
     "title": "Updates on Tick Size for Multiple USDⓈ-M Perpetual Futures Contracts", "published": "2026-04-10", "effective": "2026-04-13..2026-04-16",
     "captured": "Contracts: BASEDUSDT, GTCUSDT, ENAUSDT, ENAUSDC, GUAUSDT, SIRENUSDT, CHRUSDT, ALICEUSDT, DENTUSDT, OGNUSDT, DYDXUSDT. None of the 13 C22 Binance perps named.", "role": "constraint_change_notice"},
    {"id": "BIN_MINNOTIONAL_20260414", "venue": "BINANCE", "url": "https://www.binance.com/en/support/announcement/detail/10999fd17dc045de801c0c78ab29e6fc",
     "title": "Updates on Minimum Notional Value for BTCUSDT and BTCUSDC USDⓈ-M Perpetual Futures Contracts (2026-04-14)", "published": "2026-04-09", "effective": "2026-04-14T06:30Z",
     "captured": "BTCUSDT/BTCUSDC minimum notional 100 -> 50. None of the 13 C22 Binance perps named.", "role": "constraint_change_notice"},
    {"id": "BIN_TICK_20260806", "venue": "BINANCE", "url": "https://www.binance.com/en/support/announcement/be5c80d75197412b86d0faa1c5efd146",
     "title": "Updates on Tick Size for Multiple USDⓈ-M Perpetual Futures Contracts (2026-08-06)", "published": "2026-08-05", "effective": "2026-08-06T06:30Z",
     "captured": "Contracts: MOVEUSDT, COOKIEUSDT, AVNTUSDT, ZKUSDT, MAVUSDT, CKBUSDT, VANAUSDT, AXSUSDT. None of the 13 C22 Binance perps named.", "role": "constraint_change_notice"},
    {"id": "BIN_DELIST_20251205", "venue": "BINANCE", "url": "https://www.binance.com/en/support/announcement/detail/746056ce732d43dda12c1e5ae1b7a059",
     "title": "Binance Futures Will Delist Multiple Perpetual Contracts (2025-12-05)", "published": "2025-12-01", "effective": "2025-12-05",
     "captured": "SXPUSDT, MILKUSDT, OBOLUSDT, TOKENUSDT delisted. None of the 13 C22 Binance perps named.", "role": "delisting_notice"},
    {"id": "BIN_API_CHANGELOG", "venue": "BINANCE", "url": "https://developers.binance.com/docs/derivatives/change-log",
     "title": "Change Log | Binance Open Platform (USDⓈ-M Futures)", "published": None, "effective": None,
     "captured": "Entries 2026-06-02 .. 2026-09-10 (22 entries) contain no fee/commission, tick size, PRICE_FILTER, LOT_SIZE, MIN_NOTIONAL or contract-rule changes.", "role": "api_changelog"},
    {"id": "BIN_FAQ_FEE_STRUCTURE", "venue": "BINANCE", "url": "https://www.binance.com/en/support/faq/detail/360033544231",
     "title": "Binance Futures Fee Structure & Fee Calculations", "published": "2019-09-09", "effective": "updated 2026-05-01T11:51",
     "captured": "Does NOT state numeric USDⓈ-M maker/taker rates; refers to the dynamic fee page; notes 10% BNB discount; 'Fees are subject to change'.", "role": "fee_documentation_no_rates"},
    {"id": "BIN_FEE_PAGE", "venue": "BINANCE", "url": "https://www.binance.com/en/fee/futureFee",
     "title": "USDⓈ-M Futures Trading Fee Rate | Binance", "published": None, "effective": None,
     "captured": "Script-rendered table; static content shows 'No records found'; no publication/update date; no public JSON endpoint located (5 candidate bapi paths returned 404).", "role": "fee_page_dynamic_undated"},
    {"id": "BIN_FEE_SEARCH", "venue": "BINANCE", "url": "https://www.binance.com/en/support/announcement",
     "title": "Binance announcement surface search (USDⓈ-M futures fee adjustment 2026)", "published": None, "effective": None,
     "captured": "No 2026 announcement adjusting USDⓈ-M futures maker/taker fee rates located; only a 2025-07-24 new-listing maker promotion (taker unchanged, ended 2026-01-16) and legacy BUSD promotions.", "role": "search_surface_negative"},
    # ---- BYBIT ----
    {"id": "BYBIT_TICK_20260811", "venue": "BYBIT", "url": "https://announcements.bybit.com/en/article/change-tick-size-for-usdt-perpetual-contract-aug-11-2026--art4f47b6648755/",
     "title": "Change Tick Size for USDT Perpetual Contract Aug 11, 2026", "published": "2026-08-06", "effective": "2026-08-11T08:30Z",
     "captured": "GRAMUSDT current ticksize 0.0001 -> new ticksize 0.001 (also PENDLEUSDT 0.0001->0.001, IMXUSDT 0.00001->0.0001, TRXUSDT 0.00001->0.0001 on Bybit; Bybit symbols, not the C22 Binance instruments).", "role": "constraint_change_notice"},
    {"id": "BYBIT_RISKLIMIT_20260718", "venue": "BYBIT", "url": "https://announcements.bybit.com/en/article/risk-limit-adjustment-for-selected-perpetual-contracts-gramusdt-theusdt-jul-18-2026--art8081ffc35a46/",
     "title": "Risk limit adjustment for selected Perpetual Contracts GRAMUSDT,THEUSDT...(Jul 18, 2026)", "published": "2026-07-17", "effective": "2026-07-18T04:30Z",
     "captured": "Risk limit and applicable leverage adjusted for GRAMUSDT (inside window; leverage/margin, not tick/lot).", "role": "risk_parameter_notice"},
    {"id": "BYBIT_FEE_UPDATE_20260901", "venue": "BYBIT", "url": "https://announcements.bybit.com/en/article/lower-fees-simpler-structure-bybit-derivatives-fee-update--art70d07aff01f2/",
     "title": "Lower fees, simpler structure: Bybit derivatives fee update", "published": "2026-08-24", "effective": "2026-09-01T10:00Z",
     "captured": "'Rate changes affect Pro levels and the Market Maker Program. VIP retail pricing remains unchanged.' Non-VIP/VIP retail perpetual rates not changed by this notice.", "role": "fee_change_notice"},
    {"id": "BYBIT_FEE_TRADFI_20260616", "venue": "BYBIT", "url": "https://announcements.bybit.com/en/article/tradfi-perpetuals-lower-fees-across-all-tiers-bltb196506dada4be39/",
     "title": "TradFi Perpetuals: Lower Fees Across All Tiers", "published": None, "effective": "2026-06-16T10:00Z",
     "captured": "Dedicated TradFi perpetual fee schedule; not applicable to GRAMUSDT (crypto altcoin).", "role": "fee_change_notice"},
    {"id": "BYBIT_HELP_FEE_STRUCTURE", "venue": "BYBIT", "url": "https://www.bybit.com/en/help-center/article/Trading-Fee-Structure",
     "title": "Bybit Trading Fee Structure - Help Center", "published": None, "effective": "last updated 2026-09-02T01:17:46",
     "captured": "VIP 0 Perpetual & Futures Contracts: Taker 0.0550%, Maker 0.0200%.", "role": "fee_schedule_dated_post_window"},
    {"id": "BYBIT_HELP_PERP_FEES", "venue": "BYBIT", "url": "https://www.bybit.com/en/help-center/article/Perpetual-Expiry-Contract-Fees-Explained",
     "title": "Futures Contracts: Fees Explained - Help Center", "published": None, "effective": "last updated 2026-08-05T09:53:00",
     "captured": "Non-VIP USDT Perpetual: Taker 0.055%, Maker 0.02%.", "role": "fee_schedule_dated_post_window"},
    # ---- OKX ----
    {"id": "OKX_HELP_FUTURES_FEES", "venue": "OKX", "url": "https://www.okx.com/help/how-to-calculate-the-contract-transaction-fee",
     "title": "How are futures trading fees calculated on OKX?", "published": "2023-03-20", "effective": "updated 2026-08-26",
     "captured": "'if the fee level is lv1, then the taker fee rate is 0.05%, and the maker fee rate is 0.02%.' No group distinction stated.", "role": "fee_schedule_dated_post_window"},
    {"id": "OKX_FEE_GROUPING_20260115", "venue": "OKX", "url": "https://www.okx.com/help/updates-to-fee-grouping",
     "title": "Advance Notice: Updates to Fee Grouping Adjustment", "published": "2025-12-31", "effective": "2026-01-15T11:00..13:00 UTC+8",
     "captured": "Futures Group 1 'Top Pairs' / Group 2 'All other pairs'; no numeric rates; OKB-USDT-SWAP not named (OKB-USDT spot in Spot Group 2).", "role": "fee_group_notice_pre_window"},
    {"id": "OKX_FEE_GROUP_SPCX_20260615", "venue": "OKX", "url": "https://www.okx.com/en-gb/help/fee-update-for-perp-trading-pairs-spcx-usdt",
     "title": "Fee Group Update for Perpetual Futures Trading Pair: SPCXUSDT Perpetual", "published": "2026-06-14", "effective": "2026-06-15",
     "captured": "Shows per-pair group moves are announced; no rates; OKB not involved. No OKB-USDT-SWAP group or parameter notice found for 2026.", "role": "fee_group_notice_pattern"},
    {"id": "OKX_FEE_PAGE", "venue": "OKX", "url": "https://www.okx.com/fees",
     "title": "Trading Fee | Fee Rate | OKX", "published": None, "effective": None,
     "captured": "Server-rendered state carries only the spot table (Regular user maker 0.08%/taker 0.10%); perpetual table loads dynamically; no date.", "role": "fee_page_dynamic_undated"},
    # ---- GATE ----
    {"id": "GATE_FEE_20240520", "venue": "GATE", "url": "https://www.gate.com/announcements/article/36485/announcement-on-adjustment-to-usdt-m-perpetual-futures-fees",
     "title": "Announcement On Adjustment To USDT-M Perpetual Futures Fees", "published": "2024-05-09T12:30Z", "effective": "2024-05-20T08:00..12:00Z",
     "captured": "VIP0 maker 0.020% / taker 0.0500% (unchanged); 'A consistent fee rate system ... without market differentiation.'", "role": "fee_schedule_dated_pre_window"},
    {"id": "GATE_FEE_20260409", "venue": "GATE", "url": "https://www.gate.com/announcements/article/50390",
     "title": "Gate Spot and Futures Fee Structure Upgrade for an Enhanced Trading Experience", "published": "2026-03-25", "effective": "2026-04-09",
     "captured": "USDT-M perpetual VIP 0 taker 0.0500% before and after (unchanged across contract groups A/B/C, which differentiate VIP 15-16 only).", "role": "fee_schedule_dated_pre_window"},
    {"id": "GATE_FEE_20260901", "venue": "GATE", "url": "https://www.gate.com/announcements/article/101365",
     "title": "Gate USDT-M Perpetual Futures Fee Updates", "published": "2026-08-26", "effective": "2026-09-01",
     "captured": "New dedicated schedule for USDT-M TradFi perpetuals (VIP0 0.02/0.05); 'Previously, USDT-M TradFi Perpetuals and other USDT-M contracts followed the same fee structure.'", "role": "fee_schedule_dated_post_window"},
    {"id": "GATE_FEE_LISTING", "venue": "GATE", "url": "https://www.gate.com/announcements/fee",
     "title": "Fees | Gate Announcements (listing)", "published": None, "effective": None,
     "captured": "2026 fee-category notices: 03-25 structure upgrade, 08-26 TradFi update, funding-interval notices; no notice naming GT_USDT or ASTER_USDT fee changes.", "role": "search_surface"},
    {"id": "GATE_QTY_FIELD_20251218", "venue": "GATE", "url": "https://www.gate.com/announcements/article/48788",
     "title": "Gate Announcement on USDT Perpetual Contract Order Quantity Field Type Changes and Feature Rollout Plan", "published": "2025-12-18", "effective": "phases 2025-12-09 / 2025-12-30 / late-Jan-2026 onward",
     "captured": "Fractional-lot ordering rolled out gradually per contract from late January 2026; contracts and timelines 'announced separately'; no minimum-size values; no contracts named.", "role": "constraint_change_notice_unspecific"},
    {"id": "GATE_HELP_FEE_CALC", "venue": "GATE", "url": "https://www.gate.com/help/futures/futures_logic/22079",
     "title": "Futures Trading Fee Calculation | Gate Help Center", "published": None, "effective": "last updated 2022-04-11T02:51Z",
     "captured": "Rates in an image; delivery contracts fixed maker -0.015%/taker 0.016%; no perpetual VIP0 numeric in text.", "role": "fee_documentation_no_rates"},
    # ---- KRAKEN FUTURES ----
    {"id": "KR_FEES_DERIV", "venue": "KRAKEN_FUTURES", "url": "https://support.kraken.com/articles/360048917612-fee-schedule",
     "title": "Fees for Derivatives trading | Kraken", "published": None, "effective": "last updated 2026-09-05",
     "captured": "Base tier (30-day volume $0+): Maker 0.0200%, Taker 0.0500%.", "role": "fee_schedule_dated_post_window"},
    {"id": "KR_REBATE_SCHEDULE", "venue": "KRAKEN_FUTURES", "url": "https://support.kraken.com/articles/futures-maker-rebate-april-2026",
     "title": "New Listings & Incentive Rebate Fee Schedule", "published": None, "effective": "2026-02-24 (new listings) / 2026-04-01 (listed contracts); updated 2026-06-24",
     "captured": "Base tier Maker 0.0200% / Taker 0.0500%; 'All other fee rates remain unchanged'; taker fees not changed; maker rebates improved only above $250M 30-day volume.", "role": "fee_schedule_dated_pre_window"},
    {"id": "KR_CROSS_PLATFORM_20260709", "venue": "KRAKEN_FUTURES", "url": "https://support.kraken.com/articles/cross-platform-fee-tier-changes",
     "title": "Cross-platform fee tier changes (July 2026)", "published": "2026-07-09", "effective": "2026-07-09",
     "captured": "Tier QUALIFICATION methodology changed (best of spot volume / futures volume / assets on platform); no futures rate values changed.", "role": "fee_change_notice_no_rate_change"},
    {"id": "KR_SPECS", "venue": "KRAKEN_FUTURES", "url": "https://support.kraken.com/articles/4844359082772-linear-multi-collateral-derivatives-contract-specifications",
     "title": "Linear Multi-Collateral Derivatives Contract Specifications | Kraken", "published": None, "effective": "last updated 2026-09-08",
     "captured": "PF_KASUSD: tick 0.00001, min lot 1, Kaspa (KAS). PF_SPXUSD: tick 0.0001, min lot 1, base 'SPX6900 (SPX)'. Impact mid sizes 'regularly updated' (API only).", "role": "constraint_spec_dated_post_window"},
    {"id": "KR_PARAM_CHANGELOG", "venue": "KRAKEN_FUTURES", "url": "https://support.kraken.com/articles/13049711807636-derivatives-platform-parameters-changelog",
     "title": "Derivatives parameters changelog | Kraken", "published": None, "effective": None,
     "captured": "Rendered entries end 2025-09-05; no tick-size entry for PF_KASUSD/PF_SPXUSD at any date; impact mid size entries 2024-08-12/2025-02-07 (KAS), 2025-01-08 (SPX); margin class change 2025-08-08 (SPX). Entries after 2025-09-05 not rendered.", "role": "constraint_changelog_incomplete"},
    {"id": "KR_API_CHANGELOG", "venue": "KRAKEN_FUTURES", "url": "https://docs.kraken.com/api/docs/change-log/",
     "title": "Release notes - Kraken Developers", "published": None, "effective": None,
     "captured": "Search surface reports 'Effective 2026-06-22, fee calculation for Futures trades has been migrated to a centralised Kraken fee service' (calculation infrastructure); entry text not captured verbatim in this sweep.", "role": "api_changelog_partial"},
    # ---- BITFINEX ----
    {"id": "BFX_BLOG_ZERO_FEES_QA", "venue": "BITFINEX", "url": "https://blog.bitfinex.com/education/zero-fees-qa/",
     "title": "Zero Fees Q&A - Bitfinex blog", "published": "2025-12-17", "effective": "2025-12-17",
     "captured": "All maker and taker trading fees removed for spot, margin, derivatives, securities, OTC; permanent, no end date; 'Margin lending and funding fees are not changing'.", "role": "fee_schedule_dated_pre_window"},
    {"id": "BFX_HELP_WHAT_FEES", "venue": "BITFINEX", "url": "https://support.bitfinex.com/hc/en-us/articles/213919589-What-fees-does-Bitfinex-charge",
     "title": "What fees does Bitfinex charge – Bitfinex Help Center", "published": None, "effective": "updated 2026-06-01T15:01",
     "captured": "'Starting December 17th, 2025, no (Maker or Taker) fees apply for: Spot and Margin trading, Derivatives trading, Securities trading, OTC trading.' Funding providers pay 15% on funding earnings (18% hidden offers); recipients pay funding interest.", "role": "fee_schedule_dated_pre_window"},
    {"id": "BFX_HELP_FEES", "venue": "BITFINEX", "url": "https://support.bitfinex.com/hc/en-us/articles/115003433245-Bitfinex-Fees",
     "title": "Bitfinex Fees – Bitfinex Help Center", "published": None, "effective": "updated 2025-12-17T15:18",
     "captured": "Same zero maker/taker statement from 2025-12-17.", "role": "fee_schedule_dated_pre_window"},
    {"id": "BFX_ZERO_FEE_PAGE", "venue": "BITFINEX", "url": "https://www.bitfinex.com/zero-fee-trading/",
     "title": "Bitfinex | Zero Trading Fees for Every Customer", "published": None, "effective": "current (post-window capture 2026-09-11)",
     "captured": "Spot and margin trading, derivatives, securities, OTC: zero maker/taker; 'Zero is the new default'; other fees (lending) unchanged.", "role": "fee_schedule_current_post_window"},
    {"id": "BFX_FEES_PAGE", "venue": "BITFINEX", "url": "https://www.bitfinex.com/fees/",
     "title": "Bitfinex | Our Fees", "published": None, "effective": "current (post-window capture 2026-09-11)",
     "captured": "Official fee page (current).", "role": "fee_schedule_current_post_window"},
]

# instrument -> venue, and which sources apply
INSTRUMENT_SOURCES = {
    "BINANCE": ["BIN_TICK_20260227", "BIN_TICK_20260406", "BIN_TICK_20260410", "BIN_MINNOTIONAL_20260414", "BIN_TICK_20260806", "BIN_DELIST_20251205", "BIN_API_CHANGELOG", "BIN_FAQ_FEE_STRUCTURE", "BIN_FEE_PAGE", "BIN_FEE_SEARCH"],
    "BYBIT": ["BYBIT_TICK_20260811", "BYBIT_RISKLIMIT_20260718", "BYBIT_FEE_UPDATE_20260901", "BYBIT_FEE_TRADFI_20260616", "BYBIT_HELP_FEE_STRUCTURE", "BYBIT_HELP_PERP_FEES"],
    "OKX": ["OKX_HELP_FUTURES_FEES", "OKX_FEE_GROUPING_20260115", "OKX_FEE_GROUP_SPCX_20260615", "OKX_FEE_PAGE"],
    "GATE": ["GATE_FEE_20240520", "GATE_FEE_20260409", "GATE_FEE_20260901", "GATE_FEE_LISTING", "GATE_QTY_FIELD_20251218", "GATE_HELP_FEE_CALC"],
    "KRAKEN_FUTURES": ["KR_FEES_DERIV", "KR_REBATE_SCHEDULE", "KR_CROSS_PLATFORM_20260709", "KR_SPECS", "KR_PARAM_CHANGELOG", "KR_API_CHANGELOG"],
    "BITFINEX": ["BFX_BLOG_ZERO_FEES_QA", "BFX_HELP_WHAT_FEES", "BFX_HELP_FEES", "BFX_ZERO_FEE_PAGE", "BFX_FEES_PAGE"],
}


# --------------------------------------------------------------------------------------------
# fetch + preserve
# --------------------------------------------------------------------------------------------
def _assert_safe_url(url: str) -> None:
    host = re.match(r"https://([^/]+)/", url)
    if not host or host.group(1) not in ALLOWED_HOSTS:
        raise Stage4AError("refusing non-allowlisted host: %s" % url)
    low = url.lower()
    analytics_ok = "/api/charts/v1/analytics/" in low          # Kraken official public market analytics ('orderbook' type)
    for frag in ("account", "order", "userdata", "signed", "signature", "apikey", "api_key", "secret", "private", "withdraw", "wallet", "auth", "login"):
        if frag in low and not (frag == "order" and analytics_ok):
            raise Stage4AError("refusing url containing forbidden fragment %r" % frag)


def http_get(url: str, timeout: float = 60.0) -> dict:
    _assert_safe_url(url)
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT, "Accept": "text/html,application/json"}, method="GET")
    retrieved = _dt.now(_tz.utc).isoformat(timespec="seconds")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"url": url, "status": r.status, "retrieved_utc": retrieved, "raw_bytes": r.read()}
    except urllib.error.HTTPError as e:
        return {"url": url, "status": e.code, "retrieved_utc": retrieved, "raw_bytes": e.read()[:4000]}
    except Exception as e:  # noqa: BLE001
        return {"url": url, "status": None, "retrieved_utc": retrieved, "raw_bytes": repr(e)[:300].encode()}


def _title_of(b: bytes):
    m = re.search(rb"<title[^>]*>(.*?)</title>", b or b"", re.S | re.I)
    return re.sub(r"\s+", " ", m.group(1).decode("utf-8", "replace")).strip() if m else None


def preserve_source(src: dict, get: Callable, run_id: str) -> dict:
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    d = RECORDS_DIR / src["venue"]
    d.mkdir(parents=True, exist_ok=True)
    r = get(src["url"])
    raw_ok = r["status"] == 200 and len(r["raw_bytes"]) > 3000 and b"<html" in r["raw_bytes"][:2000].lower()
    stamp = r["retrieved_utc"].replace(":", "").replace("+0000", "Z")
    base = d / ("%s__%s__%s" % (src["venue"], src["id"], stamp))
    rec = dict(src)
    rec.update({"retrieved_utc": r["retrieved_utc"], "http_status": r["status"], "preservation": RAW_HTML if raw_ok else RENDERED,
                "raw_sha256": hashlib.sha256(r["raw_bytes"]).hexdigest() if raw_ok else None, "raw_path": None,
                "served_title": _title_of(r["raw_bytes"]) if raw_ok else None,
                "captured_text_sha256": hashlib.sha256(src["captured"].encode("utf-8")).hexdigest(),
                "sweep_date": SWEEP_DATE})
    if raw_ok:
        p = base.with_suffix(".html")
        if p.exists():
            raise Stage4AError("refuse_overwrite:%s" % p.name)
        p.write_bytes(r["raw_bytes"])
        p.with_suffix(".html.sha256").write_text(rec["raw_sha256"] + "\n", encoding="utf-8")
        rec["raw_path"] = S1._rel(p)
    meta = base.with_suffix(".record.json")
    meta.write_bytes(S1._canon({k: v for k, v in rec.items()}))
    rec["record_path"] = S1._rel(meta)
    return rec


# --------------------------------------------------------------------------------------------
# Kraken Futures official Market Analytics (historical orderbook / liquidity / slippage / volume)
# --------------------------------------------------------------------------------------------
def fetch_kraken_analytics(symbol: str, fill_date: str, get: Callable, run_id: str) -> dict:
    s = S1._ms(fill_date) // 1000
    out = {"symbol": symbol, "fill_date": fill_date, "window_utc": [fill_date + "T00:00:00Z", fill_date + "T01:00:00Z"], "series": {}, "metas": [], "source_ok": True}
    for typ in ("orderbook", "liquidity", "slippage", "trade-volume"):
        url = "https://futures.kraken.com/api/charts/v1/analytics/%s/%s?since=%d&to=%d&interval=60" % (symbol, typ, s, s + 3600)
        r = get(url)
        m = S1.preserve_raw("KRAKEN", symbol.replace("PF_", "").replace("USD", ""), "stage4a_analytics_%s_%s" % (typ, fill_date), r, {"symbol": symbol, "type": typ, "since_s": s, "to_s": s + 3600, "interval": 60}, run_id)
        out["metas"].append(m)
        try:
            j = json.loads(r["raw_bytes"].decode("utf-8"))["result"]
        except (ValueError, KeyError, TypeError):
            out["source_ok"] = False
            continue
        out["series"][typ] = j
    ob = out["series"].get("orderbook", {}).get("data") or {}
    liq = out["series"].get("liquidity", {}).get("data") or {}
    slp = out["series"].get("slippage", {}).get("data") or {}
    vol = out["series"].get("trade-volume", {}).get("data") or []
    ts = out["series"].get("orderbook", {}).get("timestamp") or []
    bid = [S4._f(x) for x in (ob.get("bid", {}).get("bestPrice") or [])]
    ask = [S4._f(x) for x in (ob.get("ask", {}).get("bestPrice") or [])]
    spread_bps = [((a - b) / ((a + b) / 2) * 1e4) if (a and b) else None for a, b in zip(ask, bid)]
    valid = [x for x in spread_bps if x is not None]
    out["derived"] = {
        "minutes_with_bbo": len(valid), "minutes_in_window": len(ts),
        "bbo_at_00_00": {"bid": bid[0] if bid else None, "ask": ask[0] if ask else None, "spread_bps": spread_bps[0] if spread_bps else None},
        "spread_bps_min": min(valid) if valid else None, "spread_bps_median": sorted(valid)[len(valid) // 2] if valid else None, "spread_bps_max": max(valid) if valid else None,
        "liquidity_keys": {side: sorted(liq.get(side, {}).keys()) for side in ("bid", "ask")},
        "liquidity_at_00_00": {side: {k: S4._f((liq.get(side, {}).get(k) or [None])[0]) for k in liq.get(side, {})} for side in ("bid", "ask")},
        "slippage_at_00_00": {side: {k: S4._f((slp.get(side, {}).get(k) or [None])[0]) for k in slp.get(side, {})} for side in ("bid", "ask")},
        "trade_volume_sum_first_60min": sum(S4._f(x) or 0 for x in vol) if isinstance(vol, list) else None,
        "classes": {"bbo": SP_BBO if valid else SP_UNRES, "orderbook": SP_OB if liq else SP_UNRES, "spread": SP_DERIVED if valid else SP_UNRES,
                    "trades": SP_TRADES if (isinstance(vol, list) and sum(S4._f(x) or 0 for x in vol) > 0) else "NO_TRADES_IN_WINDOW"},
        "unit_note": "bestPrice in USD; liquidity_* and slippage_* fields are the venue's own analytics units (contracts / USD as published); no unit conversion applied",
    }
    return out


# --------------------------------------------------------------------------------------------
# grading (pure)
# --------------------------------------------------------------------------------------------
def grade_fee(venue: str, dates: list) -> dict:
    lo, hi = min(dates), max(dates)
    if venue == "BINANCE":
        return {"grade": FEE_UNRES, "reconstructed_taker": None, "reconstructed_maker": None,
                "basis": "No dated official record states the regular-user USDⓈ-M maker/taker rate: the fee page is script-rendered and undated, the fee FAQ (updated 2026-05-01) gives no numbers, no public JSON endpoint exists, and the 2026 announcement surface + API changelog show no USDⓈ-M fee change. Cannot responsibly establish historical applicability.",
                "sources": INSTRUMENT_SOURCES["BINANCE"][7:], "intervening_change_found": False, "pre_window_record": None, "post_window_record": None}
    if venue == "BYBIT":
        return {"grade": FEE_CUR, "reconstructed_taker": None, "reconstructed_maker": None, "current_taker": 0.00055, "current_maker": 0.0002,
                "basis": "Post-window dated official records (help articles updated 2026-08-05 and 2026-09-02) state Non-VIP perpetual taker 0.055% / maker 0.02%; the only 2026 fee notices are TradFi-only (2026-06-16) and Pro/Market-Maker-only (2026-09-01, 'VIP retail pricing remains unchanged'). No PRE-window dated record of the retail rate was located, so bracketing is incomplete.",
                "sources": ["BYBIT_HELP_PERP_FEES", "BYBIT_HELP_FEE_STRUCTURE", "BYBIT_FEE_UPDATE_20260901", "BYBIT_FEE_TRADFI_20260616"], "intervening_change_found": False, "pre_window_record": None, "post_window_record": "BYBIT_HELP_PERP_FEES"}
    if venue == "OKX":
        return {"grade": FEE_CUR, "reconstructed_taker": None, "reconstructed_maker": None, "current_taker": 0.0005, "current_maker": 0.0002,
                "basis": "Official help article (published 2023-03-20, updated 2026-08-26) states lv1 taker 0.05% / maker 0.02% without group distinction; the 2026-01-15 fee-grouping notice created Futures Group 1/2 with no numeric rates and no OKB-USDT-SWAP assignment; the fees page is dynamic. Group applicability to OKB-USDT-SWAP for regular users on the required date is not established.",
                "sources": ["OKX_HELP_FUTURES_FEES", "OKX_FEE_GROUPING_20260115", "OKX_FEE_GROUP_SPCX_20260615", "OKX_FEE_PAGE"], "intervening_change_found": False, "pre_window_record": "OKX_FEE_GROUPING_20260115 (no rates)", "post_window_record": "OKX_HELP_FUTURES_FEES"}
    if venue == "GATE":
        return {"grade": FEE_UNRES, "reconstructed_taker": None, "reconstructed_maker": None, "schedule_level_bracket_taker": 0.0005, "schedule_level_bracket_maker": 0.0002,
                "contract_api_current_taker": 0.00075, "contract_api_current_maker": -0.0001,
                "basis": "CONFLICTING first-party records: dated schedule notices bracket VIP0 taker 0.05% / maker 0.02% (2024-05-20 effective; 2026-04-09 effective 'unchanged across contract groups'; 2026-09-01 notice says other USDT-M contracts 'followed the same fee structure'), but the official contract endpoint reports GT_USDT/ASTER_USDT taker 0.075% / maker -0.01% today and no dated notice explains a contract-level override. Fail closed.",
                "sources": ["GATE_FEE_20240520", "GATE_FEE_20260409", "GATE_FEE_20260901", "GATE_FEE_LISTING"], "intervening_change_found": False, "pre_window_record": "GATE_FEE_20260409", "post_window_record": "GATE_FEE_20260901", "conflict": True}
    if venue == "KRAKEN_FUTURES":
        return {"grade": FEE_T2_BR, "reconstructed_taker": 0.0005, "reconstructed_maker": 0.0002,
                "basis": "Pre-window dated record (rebate schedule, effective 2026-04-01, updated 2026-06-24: base tier taker 0.0500% / maker 0.0200%, 'All other fee rates remain unchanged') and post-window dated record (Fees for Derivatives trading, updated 2026-09-05: 0.0500% / 0.0200%) show the same base-tier schedule; the only intervening notice (2026-07-09) changed tier qualification, not rates; the 2026-06-22 fee-service migration is calculation infrastructure (release-note text not captured verbatim). Conservative retail tier = base tier; no rebate applied.",
                "sources": ["KR_REBATE_SCHEDULE", "KR_FEES_DERIV", "KR_CROSS_PLATFORM_20260709", "KR_API_CHANGELOG"], "intervening_change_found": False, "pre_window_record": "KR_REBATE_SCHEDULE", "post_window_record": "KR_FEES_DERIV"}
    if venue == "BITFINEX":
        return {"grade": FEE_T2_BR, "reconstructed_taker": 0.0, "reconstructed_maker": 0.0,
                "basis": "Pre-window dated records (blog 2025-12-17; help article updated 2026-06-01: 'Starting December 17th, 2025, no (Maker or Taker) fees apply for: Spot and Margin trading') and post-window current official pages (zero-fee page, fees page, captured 2026-09-11) show zero maker/taker for margin trading; official surfaces searched show no 2026 reintroduction. Margin funding interest and the 15% provider fee are borrow-cost items for a later stage, not trading fees.",
                "sources": ["BFX_HELP_WHAT_FEES", "BFX_BLOG_ZERO_FEES_QA", "BFX_HELP_FEES", "BFX_ZERO_FEE_PAGE", "BFX_FEES_PAGE"], "intervening_change_found": False, "pre_window_record": "BFX_HELP_WHAT_FEES", "post_window_record": "BFX_ZERO_FEE_PAGE"}
    raise Stage4AError("no_fee_grader:%s" % venue)


def grade_constraints(venue: str, instrument: str, dates: list, current: dict) -> dict:
    lo, hi = min(dates), max(dates)
    if venue == "BINANCE":
        return {"tick": {"grade": CON_CUR, "current": current.get("tick_size"), "historical": None}, "lot_min": {"grade": CON_CUR, "current": {k: current.get(k) for k in ("lot_step", "min_qty", "min_notional")}, "historical": None},
                "basis": "Comprehensive 2026 official tick-size notices (02-09, 02-27, 04-06, 04-10/13-16, 08-06) and the 04-14 minimum-notional notice name none of the 13 C22 perps; the derivatives API changelog 2026-06-02..09-10 records no filter changes. No dated PRE-window record of the values exists, so this is CURRENT_ONLY with no intervening change found (not T2_BRACKETED).",
                "sources": INSTRUMENT_SOURCES["BINANCE"][:7]}
    if venue == "BYBIT":
        return {"tick": {"grade": CON_T2_RC, "current": current.get("tick_size"), "historical": 0.0001,
                         "basis": "Official notice published 2026-08-06, effective 2026-08-11 08:30 UTC: GRAMUSDT tick size 0.0001 -> 0.001. All GRAM signal/fill dates (%s..%s) precede the change, so the in-window tick size was 0.0001; today's API value 0.001 would have been WRONG for the window." % (lo, hi)},
                "lot_min": {"grade": CON_CUR, "current": {k: current.get(k) for k in ("lot_step", "min_qty", "min_notional")}, "historical": None},
                "basis": "Tick reconstructed from the dated notice; lot/min-notional: no dated notice; the 2026-07-18 risk-limit/leverage adjustment (inside window) changed margin parameters, not lot/min.",
                "sources": ["BYBIT_TICK_20260811", "BYBIT_RISKLIMIT_20260718"]}
    if venue == "OKX":
        return {"tick": {"grade": CON_CUR, "current": current.get("tick_size"), "historical": None}, "lot_min": {"grade": CON_CUR, "current": {k: current.get(k) for k in ("lot_step", "min_qty", "contract_value")}, "historical": None},
                "basis": "No 2026 official parameter notice for OKB-USDT-SWAP located; listTime 2025-09-04 precedes the window; no dated pre-window value record.", "sources": ["OKX_FEE_GROUP_SPCX_20260615"]}
    if venue == "GATE":
        return {"tick": {"grade": CON_UNRES, "current": current.get("tick_size"), "historical": None}, "lot_min": {"grade": CON_UNRES, "current": {k: current.get(k) for k in ("lot_step", "min_qty", "contract_multiplier")}, "historical": None},
                "basis": "Official contract endpoint reports config_change_time INSIDE the window (%s); no dated notice describes what changed; fractional-lot rollout (notice 2025-12-18) was applied per contract on unannounced dates. Current values demonstrably post-date part of the holding period." % current.get("change_timestamp"),
                "sources": ["GATE_QTY_FIELD_20251218", "GATE_FEE_LISTING"]}
    if venue == "KRAKEN_FUTURES":
        return {"tick": {"grade": CON_CUR, "current": current.get("tick_size"), "historical": None,
                         "basis": "Spec article (updated 2026-09-08, post-window) lists the same tick as the API; the parameters changelog has no tick entry for %s at any rendered date, but its rendered entries end 2025-09-05, so absence of change through the window is not established." % instrument},
                "lot_min": {"grade": CON_CUR, "current": {"min_lot": 1, "impact_mid_size": current.get("impact_mid_size")}, "historical": None,
                            "basis": "Impact mid size in the API (%s) differs from the last rendered changelog value, proving later unrecorded changes." % current.get("impact_mid_size")},
                "basis": "Tick and min lot CURRENT_ONLY (post-window dated spec); impact mid size history incomplete.", "sources": ["KR_SPECS", "KR_PARAM_CHANGELOG"]}
    if venue == "BITFINEX":
        return {"tick": {"grade": CON_CUR, "current": None, "historical": None}, "lot_min": {"grade": CON_CUR, "current": {"min_qty": current.get("min_qty"), "max_qty": current.get("max_qty")}, "historical": None},
                "basis": "pub:info:pair carries current min/max order size only; no dated notice located.", "sources": []}
    raise Stage4AError("no_constraint_grader:%s" % venue)


def fully_historical(fee: dict, con: dict, liq_grade: str, spread_grade: str) -> bool:
    return (fee["grade"] in (FEE_T1, FEE_T2_BR, FEE_T2_RC) and con["tick"]["grade"] in (CON_T1, CON_T2_RC, CON_T2_BR)
            and con["lot_min"]["grade"] in (CON_T1, CON_T2_RC, CON_T2_BR) and liq_grade in (SP_BBO, SP_OB, SP_TRADES, SP_DEPTH)
            and spread_grade in (SP_BBO, SP_DERIVED, SP_OB))


# --------------------------------------------------------------------------------------------
def load_stage4_of_record() -> dict:
    raw = STAGE4_REPORT.read_bytes()
    if S1._sha(raw) != STAGE4_REPORT_SHA256:
        raise Stage4AError("stage4_report_sha_mismatch")
    return json.loads(raw.decode("utf-8"))


def run_stage4a(get: Callable = http_get, run_id: str | None = None, sleep_s: float = 0.3, stage4: dict | None = None, preserve: bool = True) -> dict:
    run_id = run_id or _dt.now(_tz.utc).strftime("%Y%m%dT%H%M%SZ")
    s4 = stage4 or load_stage4_of_record()
    # 1. preserve official sources
    records = {}
    if preserve:
        for src in SOURCES:
            records[src["id"]] = preserve_source(src, get, run_id)
            if sleep_s:
                time.sleep(sleep_s)
    else:
        records = {s["id"]: dict(s, preservation="NOT_FETCHED_IN_THIS_RUN") for s in SOURCES}
    # 2. Kraken official analytics for every Kraken fill window in the sealed Stage Four
    kraken_fills = sorted({(x["instrument"], x["fill_date"]) for x in s4["step6_per_fill"] if x["venue"] == "KRAKEN_FUTURES"})
    analytics = {}
    for inst, d in kraken_fills:
        analytics["%s|%s" % (inst, d)] = fetch_kraken_analytics(inst, d, get, run_id)
        if sleep_s:
            time.sleep(sleep_s)
    # 3. per-instrument grades
    step5 = s4["step5_per_instrument"]
    dates_by_asset: dict = {}
    for p in s4["per_signal"]:
        if p["fills"]:
            dates_by_asset.setdefault(p["c22_asset"], set()).add(p["decision_date"])
            for f in p["fills"]:
                if f.get("date"):
                    dates_by_asset[p["c22_asset"]].add(f["date"])
    instruments = {}
    for asset, s in step5.items():
        dates = sorted(dates_by_asset.get(asset) or [WINDOW[0]])
        fee = grade_fee(s["venue"], dates)
        con = grade_constraints(s["venue"], s["instrument"], dates, dict(s["constraints"]["current_values"] or {}, change_timestamp=s["constraints"].get("change_timestamp")))
        instruments[asset] = {"venue": s["venue"], "instrument": s["instrument"], "applicable_dates": dates, "stage4_fee_status": s["fee"]["historical_status"],
                              "stage4_constraint_status": s["constraints"]["historical_status"], "fee": fee, "constraints": con,
                              "source_records": [records[i] for i in sorted(set(fee["sources"]) | set(con["sources"])) if i in records]}
    # 4. per-fill spread / liquidity grades (Stage Four evidence + Kraken analytics)
    fills = {}
    for x in s4["step6_per_fill"]:
        key = "%s|%s" % (x["instrument"], x["fill_date"])
        if x["venue"] == "BINANCE":
            liq, spread = (SP_DEPTH if x["depth"] else SP_UNRES), (SP_DEPTH if x["depth"] else SP_UNRES)
        elif x["venue"] == "KRAKEN_FUTURES" and key in analytics and analytics[key]["source_ok"]:
            d = analytics[key]["derived"]
            liq = SP_OB if d["classes"]["orderbook"] == SP_OB else (SP_TRADES if x["trades_status"] == S4.LIQ_OBSERVED else SP_UNRES)
            spread = SP_DERIVED if d["classes"]["spread"] == SP_DERIVED else SP_UNRES
        else:
            liq, spread = (SP_TRADES if x["trades_status"] == S4.LIQ_OBSERVED else SP_UNRES), SP_UNRES
        fills[key] = {"venue": x["venue"], "instrument": x["instrument"], "fill_date": x["fill_date"], "stage4_trades_status": x["trades_status"], "stage4_spread_status": x["spread_status"],
                      "liquidity_grade": liq, "spread_grade": spread, "kraken_analytics": analytics.get(key, {}).get("derived")}
    # 5. KAS supplemental
    kas_key = "PF_KASUSD|2026-07-06"
    kas = analytics.get(kas_key, {}).get("derived")
    kas_result = {
        "stage4_verdict": S4.FAIL_LIQ, "fill_window": kas_key,
        "supplemental_evidence": kas,
        "frozen_b3_categories": ["historical_volume", "historical_spread_or_orderbook_proxy"],
        "permits_orderbook_evidence": True,
        "reasoning": "The frozen B3 plan's step-6 evidence categories explicitly include 'historical_spread_or_orderbook_proxy' alongside 'historical_volume'; the Stage Four FAIL rule ('no trades in the 30-minute window') was a tool-level rule, not a frozen-plan requirement. Official Kraken analytics show a continuous two-sided book with best bid/ask, resting liquidity and quoted slippage at every minute of the window while trade volume was zero.",
        "proposed_revised_verdict": None, "applied_to_sealed_stage4": False,
    }
    if kas and kas["classes"]["bbo"] == SP_BBO and kas["classes"]["orderbook"] == SP_OB:
        kas_result["proposed_revised_verdict"] = {"liquidity_grade": SP_OB, "spread_grade": SP_DERIVED,
                                                  "signal_stage4_verdict_if_adopted": S4.UNRES_FEE,
                                                  "note": "Liquidity requirement satisfiable from official orderbook evidence (quotes present, no trades); the signal would then stand with the other Kraken signals at UNRESOLVED_HISTORICAL_FEE -> after Stage 4A fee bracketing, at the constraint gap. Zero trades in the hour remains a recorded fact; fill at the open is still not assumed."}
    # 6. per-signal revised evidence status (75 shorts)
    per_signal = []
    for p in s4["per_signal"]:
        rec = {"signal_id": p["signal_id"], "c22_asset": p["c22_asset"], "decision_date": p["decision_date"], "stage4_verdict": p["verdict"],
               "fee_grade": None, "tick_grade": None, "lot_min_grade": None, "liquidity_grade": None, "spread_grade": None,
               "fully_historical_after_4a": False, "unresolved_fields": [], "proposed_status_after_4a": None}
        if p["verdict"] == S4.NOT_ELIGIBLE:
            rec["proposed_status_after_4a"] = S4.NOT_ELIGIBLE
            per_signal.append(rec)
            continue
        inst = instruments[p["c22_asset"]]
        rec["fee_grade"], rec["tick_grade"], rec["lot_min_grade"] = inst["fee"]["grade"], inst["constraints"]["tick"]["grade"], inst["constraints"]["lot_min"]["grade"]
        executed = [f for f in (p["fills"] or []) if f["kind"] in ("ENTRY", "EXIT") and f.get("date")]
        fkeys = ["%s|%s" % (inst["instrument"], f["date"]) for f in executed]
        lg = [fills[k]["liquidity_grade"] for k in fkeys if k in fills]
        sg = [fills[k]["spread_grade"] for k in fkeys if k in fills]
        rec["liquidity_grade"] = (min(lg, key=lambda g: [SP_OB, SP_BBO, SP_DEPTH, SP_TRADES, SP_UNRES].index(g)) if lg else "NO_EXECUTED_FILL")
        rec["spread_grade"] = (SP_UNRES if SP_UNRES in sg or not sg else (SP_DERIVED if SP_DERIVED in sg else SP_DEPTH))
        missing = []
        if inst["fee"]["grade"] not in (FEE_T1, FEE_T2_BR, FEE_T2_RC):
            missing.append("historical_fee:%s" % inst["fee"]["grade"])
        if inst["constraints"]["tick"]["grade"] not in (CON_T1, CON_T2_RC, CON_T2_BR):
            missing.append("historical_tick:%s" % inst["constraints"]["tick"]["grade"])
        if inst["constraints"]["lot_min"]["grade"] not in (CON_T1, CON_T2_RC, CON_T2_BR):
            missing.append("historical_lot_min:%s" % inst["constraints"]["lot_min"]["grade"])
        if not executed:
            missing.append("no_executed_fill_in_lifecycle")
        elif rec["liquidity_grade"] == SP_UNRES:
            missing.append("liquidity_at_fill")
        if executed and rec["spread_grade"] == SP_UNRES:
            missing.append("spread_at_fill:UNRESOLVED")
        elif executed and rec["spread_grade"] == SP_DEPTH:
            missing.append("spread_at_fill:DEPTH_PROXY_ONLY")
        rec["unresolved_fields"] = missing
        rec["fully_historical_after_4a"] = bool(executed) and fully_historical(inst["fee"], inst["constraints"], rec["liquidity_grade"], rec["spread_grade"])
        if p["signal_id"] == "2026-07-05|KRAKEN:KASUSD|BEAR_SHORT":
            rec["kas_supplemental"] = "see kas_supplemental_result; sealed Stage Four FAIL preserved"
        rec["proposed_status_after_4a"] = "PASS_STAGE_FOUR_FROM_HISTORICAL_EVIDENCE" if rec["fully_historical_after_4a"] else ("REQUIRES_CONSERVATIVE_ASSUMPTION_FOR:" + ",".join(missing))
        per_signal.append(rec)
    eligible = [r for r in per_signal if r["stage4_verdict"] != S4.NOT_ELIGIBLE]
    counts = {"fully_historical_after_4a": sum(1 for r in eligible if r["fully_historical_after_4a"]),
              "still_requiring_conservative_assumptions": sum(1 for r in eligible if not r["fully_historical_after_4a"]),
              "not_eligible": len(per_signal) - len(eligible)}
    fee_cov = {g: sum(1 for i in instruments.values() if i["fee"]["grade"] == g) for g in (FEE_T1, FEE_T2_BR, FEE_T2_RC, FEE_CUR, FEE_UNRES)}
    tick_cov = {g: sum(1 for i in instruments.values() if i["constraints"]["tick"]["grade"] == g) for g in (CON_T1, CON_T2_RC, CON_T2_BR, CON_CUR, CON_UNRES)}
    lot_cov = {g: sum(1 for i in instruments.values() if i["constraints"]["lot_min"]["grade"] == g) for g in (CON_T1, CON_T2_RC, CON_T2_BR, CON_CUR, CON_UNRES)}
    sp_cov = {g: sum(1 for f in fills.values() if f["spread_grade"] == g) for g in (SP_BBO, SP_OB, SP_DERIVED, SP_TRADES, SP_DEPTH, SP_UNRES)}
    liq_cov = {g: sum(1 for f in fills.values() if f["liquidity_grade"] == g) for g in (SP_BBO, SP_OB, SP_DERIVED, SP_TRADES, SP_DEPTH, SP_UNRES)}
    governance = {
        "frozen_b3_permits_assumptions": "NOT_AS_EVIDENCE",
        "explanation": "The frozen B3 plan grades evidence by source tier (T1..T5, T3 minimum decisive, T5 never decisive) and has no assumption class, so a conservative assumption can never be admitted as B3 evidence or raise a grade. The frozen B1 execution-data contract, however, provides a separate human-frozen COST BASE CASE gate (C22_EXECUTION_COST_BASE_CASE_READY_FOR_HUMAN_REVIEW, token HUMAN_DECISION_C22_EXECUTION_COST_BASE_CASE_ACCEPT_OR_REVISE; 37 bps is already recorded there as SENSITIVITY_CASE_NOT_BASE_CASE). Labelled FROZEN_CONSERVATIVE_ASSUMPTION values for the gaps listed here may be adopted only through that gate, frozen before any decisive performance is inspected, and reported separately from observed evidence.",
        "gate_module": "sparta_commander.c22_execution_data_short_instrument_feasibility_contract",
    }
    return {"report": "c22_b3_stage4a_t2_recovery", "stage": STAGE, "stage_version": STAGE_VERSION, "run_id": run_id, "sweep_date": SWEEP_DATE,
            "mode": "READ_ONLY_SUPPLEMENTAL_EVIDENCE_RECOVERY_FROM_DATED_OFFICIAL_RECORDS",
            "inputs": {"stage4_report": {"run": STAGE4_RUN_OF_RECORD, "sha256": STAGE4_REPORT_SHA256}, "sealed_stage4_modified": False},
            "window": list(WINDOW), "retail_tier_assumption": "conservative ordinary retail (VIP0 / non-VIP / lv1 / base tier); no maker rebate, token discount, VIP or promotional discount applied",
            "official_records": records, "kraken_analytics": {k: {kk: vv for kk, vv in v.items() if kk not in ("series", "metas")} | {"raw_sha256": [m["raw_sha256"] for m in v["metas"]]} for k, v in analytics.items()},
            "instruments": instruments, "fills": fills, "kas_supplemental_result": kas_result, "per_signal": per_signal, "counts": counts,
            "coverage": {"fee": fee_cov, "tick": tick_cov, "lot_min": lot_cov, "spread": sp_cov, "liquidity": liq_cov},
            "governance": governance, "assumptions_selected": [], "performance_computed": False, "next_stage_started": False,
            "v2_modified": False, "strategy_rules_modified": False, "stage4_artifacts_modified": False}


def render_markdown(r: dict) -> str:
    c = r["coverage"]
    L = ["# C22 — B3 Stage 4A: T2 Evidence Recovery (run %s)" % r["run_id"], "",
         "Supplemental to sealed Stage Four `%s` (sha `%s`, unmodified). Dated first-party official records only; search engines used for discovery only. No assumption selected; no performance." % (r["inputs"]["stage4_report"]["run"], r["inputs"]["stage4_report"]["sha256"]), "",
         "- Fee grades (20 instruments): %s" % json.dumps({k: v for k, v in c["fee"].items() if v}, sort_keys=True),
         "- Tick grades: %s · Lot/min grades: %s" % (json.dumps({k: v for k, v in c["tick"].items() if v}, sort_keys=True), json.dumps({k: v for k, v in c["lot_min"].items() if v}, sort_keys=True)),
         "- Spread grades (50 fills): %s · Liquidity grades: %s" % (json.dumps({k: v for k, v in c["spread"].items() if v}, sort_keys=True), json.dumps({k: v for k, v in c["liquidity"].items() if v}, sort_keys=True)),
         "- Signals fully historical after 4A: **%d** · still requiring conservative assumptions: **%d** · not eligible: %d" % (r["counts"]["fully_historical_after_4a"], r["counts"]["still_requiring_conservative_assumptions"], r["counts"]["not_eligible"]), "",
         "## Instruments", "", "| asset | instrument | dates | S4 fee | **4A fee** | reconstructed taker/maker | S4 constraint | **4A tick** | **4A lot/min** |", "|---|---|---|---|---|---|---|---|---|"]
    for a, i in r["instruments"].items():
        L.append("| %s | %s @ %s | %s..%s | %s | **%s** | %s / %s | %s | **%s** (hist %s) | **%s** |" % (a, i["instrument"], i["venue"], i["applicable_dates"][0], i["applicable_dates"][-1], i["stage4_fee_status"], i["fee"]["grade"],
                                                                                                    i["fee"].get("reconstructed_taker"), i["fee"].get("reconstructed_maker"), i["stage4_constraint_status"], i["constraints"]["tick"]["grade"], i["constraints"]["tick"].get("historical"), i["constraints"]["lot_min"]["grade"]))
    L += ["", "## Fee / constraint bases", ""]
    for a, i in r["instruments"].items():
        L.append("- **%s** fee: %s" % (a, i["fee"]["basis"]))
        L.append("  constraints: %s" % i["constraints"]["basis"])
    L += ["", "## Fill windows", "", "| instrument | fill | S4 liquidity | **4A liquidity** | **4A spread** | Kraken BBO@00:00 / spread bps / vol 60m |", "|---|---|---|---|---|---|"]
    for k, f in sorted(r["fills"].items()):
        ka = f.get("kraken_analytics") or {}
        L.append("| %s @ %s | %s | %s | **%s** | **%s** | %s |" % (f["instrument"], f["venue"], f["fill_date"], f["stage4_trades_status"], f["liquidity_grade"], f["spread_grade"],
                                                            json.dumps({"bbo": ka.get("bbo_at_00_00"), "spread_med_bps": ka.get("spread_bps_median"), "vol": ka.get("trade_volume_sum_first_60min")}, default=str) if ka else "—"))
    k = r["kas_supplemental_result"]
    L += ["", "## KAS supplemental (PF_KASUSD 2026-07-06)", "", "- Sealed Stage Four verdict: %s (preserved)" % k["stage4_verdict"], "- Frozen B3 permits orderbook evidence: %s" % k["permits_orderbook_evidence"],
          "- Evidence: %s" % json.dumps(k["supplemental_evidence"], default=str)[:900], "- Proposed revised verdict: %s" % json.dumps(k["proposed_revised_verdict"], default=str), "- Applied to sealed Stage Four: %s" % k["applied_to_sealed_stage4"], "",
          "## Per-signal revised evidence status", "", "| signal | S4 | fee | tick | lot/min | liquidity | spread | fully historical | unresolved fields |", "|---|---|---|---|---|---|---|---|---|"]
    for p in r["per_signal"]:
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (p["signal_id"], p["stage4_verdict"], p["fee_grade"], p["tick_grade"], p["lot_min_grade"], p["liquidity_grade"], p["spread_grade"], p["fully_historical_after_4a"], "; ".join(p["unresolved_fields"])))
    L += ["", "## Official records preserved", "", "| id | venue | title | published | effective/updated | preservation | sha256 |", "|---|---|---|---|---|---|---|"]
    for i, rec in r["official_records"].items():
        L.append("| %s | %s | %s | %s | %s | %s | `%s` |" % (i, rec["venue"], rec["title"], rec.get("published"), rec.get("effective"), rec.get("preservation"), (rec.get("raw_sha256") or rec.get("captured_text_sha256") or "")[:16]))
    L += ["", "## Governance", "", "- %s" % r["governance"]["frozen_b3_permits_assumptions"], "- %s" % r["governance"]["explanation"], ""]
    return "\n".join(L) + "\n"


def write_report(r: dict) -> dict:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    base = REPORT_DIR / ("c22_b3_stage4a_t2_recovery_%s" % r["run_id"])
    jp, mp = base.with_suffix(".json"), base.with_suffix(".md")
    for p in (jp, mp):
        if p.exists():
            raise Stage4AError("refuse_overwrite_report:%s" % p.name)
    blob = json.dumps(r, indent=2, sort_keys=True, default=str).encode("utf-8") + b"\n"
    tmp = jp.with_suffix(".tmp"); tmp.write_bytes(blob); os.replace(tmp, jp)
    tmp = mp.with_suffix(".tmp"); tmp.write_bytes(render_markdown(r).encode("utf-8")); os.replace(tmp, mp)
    S1.MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    man = S1.MANIFEST_DIR / ("stage4a_run_manifest__%s.json" % r["run_id"])
    man.write_bytes(S1._canon({"stage": STAGE, "run_id": r["run_id"], "report_json": S1._rel(jp), "report_sha256": S1._sha(blob),
                               "official_records": {k: {"raw_sha256": v.get("raw_sha256"), "raw_path": v.get("raw_path"), "record_path": v.get("record_path"), "preservation": v.get("preservation")} for k, v in r["official_records"].items()},
                               "kraken_analytics_raw_sha256": {k: v["raw_sha256"] for k, v in r["kraken_analytics"].items()},
                               "note": "STAGE 4A supplemental evidence; not an admission manifest; sealed Stage Four untouched; no assumption selected."}))
    return {"report_json": S1._rel(jp), "report_md": S1._rel(mp), "report_sha256": S1._sha(blob), "run_manifest": S1._rel(man)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default=None)
    a = ap.parse_args(argv)
    r = run_stage4a(run_id=a.run_id)
    w = write_report(r)
    print(json.dumps({"run_id": r["run_id"], "counts": r["counts"], "coverage": r["coverage"], "kas_proposed": r["kas_supplemental_result"]["proposed_revised_verdict"], **w}, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
