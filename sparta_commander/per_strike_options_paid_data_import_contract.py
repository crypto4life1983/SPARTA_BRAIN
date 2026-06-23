"""PER-STRIKE OPTIONS PAID-DATA IMPORT CONTRACT (PURE, RESEARCH ONLY).

Defines the import SPEC + anti-tamper VALIDATOR for an externally-procured PAID per-strike BTC
options dataset (e.g. Tardis.dev Deribit options history) -- the PRIMARY Phase-2 VRP data path.

It BUYS NOTHING, FETCHES NOTHING, DOWNLOADS NOTHING. It is a pure schema/coverage validator the
human uses AFTER they have separately purchased + placed a paid file in the local gitignored
inbox: given an already-gathered manifest of the paid dataset (row counts, fields present, date
coverage), it confirms the data conforms to the required per-strike schema before any future
(separately-gated) backtest. It runs NO backtest / delta-hedge / straddle P&L / optimization,
activates/promotes NOTHING, and modifies NO ledger/lifecycle.
"""
from __future__ import annotations

from typing import Any

IMP_SCHEMA_VERSION = 1
IMP_MODE = "RESEARCH_ONLY"
IMP_LANE = "portfolio_sleeve_evaluation"

RECORD_ID = "PER_STRIKE_OPTIONS_PAID_DATA_IMPORT_SPEC_V1"
VERDICT = "PAID_PER_STRIKE_IMPORT_SPEC_FROZEN__AWAITS_HUMAN_PROCURED_FILE"

APPROVED_SOURCES = ("tardis.dev", "amberdata", "kaiko")  # human-procured; none fetched here
INBOX_DIR = "data/deribit_options_chain_universe/paid_inbox/"   # gitignored; human drops file
CURRENCY = "BTC"   # BTC-first

# Required per-strike fields the paid dataset MUST provide (maps to the plan's REQUIRED_FIELDS).
REQUIRED_FIELDS = (
    "instrument_name", "timestamp", "underlying_or_index_price", "expiration_timestamp",
    "strike", "option_type", "mark_price_or_settlement", "implied_vol",
    "delta", "gamma", "vega", "theta",
)
OPTIONAL_FIELDS = ("bid", "ask", "volume", "open_interest")
TARGET_DATE_RANGE = {"start": "2021-03-24", "end": "2026-06-21",
                     "stretch_start": "2020-01-01 (if the paid source supports it -> March-2020)"}


def build_paid_import_spec() -> dict[str, Any]:
    """Pure import SPEC record. No I/O; buys/fetches nothing."""
    return {
        "schema_version": IMP_SCHEMA_VERSION, "mode": IMP_MODE, "lane": IMP_LANE,
        "record_id": RECORD_ID,
        "verdict": VERDICT,
        "is_import_spec_only": True,
        "approved_sources_human_procured": list(APPROVED_SOURCES),
        "inbox_dir": INBOX_DIR,
        "inbox_is_gitignored": True,
        "currency": CURRENCY,
        "required_fields": list(REQUIRED_FIELDS),
        "optional_fields": list(OPTIONAL_FIELDS),
        "target_date_range": dict(TARGET_DATE_RANGE),
        "buys_nothing": True,
        "fetches_nothing": True,
        "downloads_nothing": True,
        "runs_no_backtest": True,
        "activates_nothing": True,
        "does_not_modify_official_ledger": True,
        "does_not_modify_lifecycle": True,
        "next_required_action": (
            "HUMAN places a procured paid BTC per-strike file in the gitignored inbox, then a "
            "SEPARATE token authorizes import-validation + (later) the gated backtest"),
        "scope_locks": {
            "no_buy": True, "no_purchase": True, "no_fetch": True, "no_download": True,
            "no_backtest": True, "no_delta_hedge_sim": True, "no_straddle_pnl": True,
            "no_optimization": True, "no_activate_candidate": True, "no_promote_candidate": True,
            "no_modify_official_ledger": True, "no_modify_lifecycle": True, "no_commit_data": True,
            "no_paper_trading": True, "no_live_trading": True, "no_broker": True,
            "no_order_logic": True,
        },
    }


def validate_paid_dataset_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator over an ALREADY-GATHERED manifest of a human-procured paid dataset
    (NOT a fetch). Valid only when: source is an approved human-procured vendor; currency is BTC;
    ALL required per-strike fields are present; row count > 0; the covered date range overlaps the
    target; and the manifest claims NO purchase/fetch happened inside SPARTA. Returns
    valid/failures + a coverage summary. Reads/buys/fetches NOTHING itself."""
    failures: list = []
    m = manifest or {}
    if m.get("currency") != CURRENCY:
        failures.append("currency_not_btc")
    src = str(m.get("source", "")).lower()
    if not any(s in src for s in APPROVED_SOURCES):
        failures.append("source_not_approved_vendor")
    fields = set(m.get("fields_present") or [])
    missing = [f for f in REQUIRED_FIELDS if f not in fields]
    if missing:
        failures.append("missing_required_fields:%s" % ",".join(missing))
    if not isinstance(m.get("row_count"), int) or m.get("row_count", 0) <= 0:
        failures.append("no_rows")
    cov = m.get("date_coverage") or {}
    first, last = cov.get("first"), cov.get("last")
    if not (isinstance(first, str) and isinstance(last, str) and first <= last):
        failures.append("bad_date_coverage")
    elif not (first <= TARGET_DATE_RANGE["end"] and last >= TARGET_DATE_RANGE["start"]):
        failures.append("coverage_outside_target_range")
    # provenance honesty: the manifest must affirm SPARTA did not buy/fetch
    if m.get("procured_externally_by_human") is not True:
        failures.append("must_be_human_procured")
    if m.get("fetched_or_bought_inside_sparta") is not False:
        failures.append("must_not_be_fetched_inside_sparta")

    covers_march_2020 = bool(isinstance(first, str) and first <= "2020-03-31")
    return {"valid": not failures, "failures": failures,
            "covers_march_2020": covers_march_2020,
            "required_fields_ok": not [f for f in REQUIRED_FIELDS if f not in fields]}
